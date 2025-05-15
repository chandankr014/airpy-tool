"""
Core data processing functionality for AirPy.
"""
import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gc
from pathlib import Path
# import warnings
# import importlib.resources
import pkg_resources

# IMPORT CUSTOM MODULES
from airpy.utils.formatting import get_formatted_df
from airpy.utils.cleaning import group_plot, NO_count_mismatch, correct_unit_inconsistency
from airpy.utils.metadata import get_siteId_Name_Year_City, get_siteId_Name_Year_City_LIVE


def process_data(city=None, live=False, raw_dir=None, clean_dir=None, pollutants=None):
    """
    Processes air quality data by reading raw data files, cleaning them, and saving the results.

    This function is designed to handle air quality data for a specified city and can process either 
    historical or live data. It requires directories for both raw input data and cleaned output data. 
    Additionally, it allows for the specification of pollutants to be processed.

    Parameters:
    -----------
    city : str, optional
        The name of the city for which the air quality data should be processed. If not specified, 
        data for all available cities will be processed.
    live : bool, default=False
        A flag indicating whether to process live data. If set to True, the function will handle 
        live data; otherwise, it will process historical data.
    raw_dir : str, optional
        The file path to the directory containing raw air quality data files. This directory must 
        exist and contain the necessary data files for processing.
    clean_dir : str, optional
        The file path to the directory where cleaned data will be saved. If the directory does not 
        exist, the function will attempt to create it.
    pollutants : list, optional
        A list of pollutants to be processed. If not provided, the function will default to processing 
        a standard set of pollutants, including 'PM25', 'PM10', 'NO', 'NO2', and 'NOx'.
    """
    # SETUP DIRECTORIES
    if raw_dir:
        data_dir = Path(raw_dir)
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Raw data directory '{raw_dir}' does not exist")
    else:
        raise ValueError("Raw data directory must be specified")
    
    if clean_dir:
        save_dir = Path(clean_dir)
        if not os.path.exists(save_dir):
            # Create the directory if it doesn't exist
            try:
                os.makedirs(save_dir)
            except Exception as e:
                raise FileNotFoundError(f"Could not create clean data directory '{clean_dir}': {e}")
    else:
        raise ValueError("Clean data directory must be specified")
    
    # LOAD SITE INFORMATION
    try:
        # Try to get the sites_master.csv file from the installed package
        sites_file = pkg_resources.resource_filename('airpy', 'data/sites_master.csv')
        if os.path.exists(sites_file):
            sites = pd.read_csv(sites_file)
        else:
            raise FileNotFoundError("Could not find sites_master.csv file")
    except Exception as e:
        print(f"Error loading sites_master.csv: {e}")
        return
        
    files = os.listdir(data_dir)
    
    # CONFIGURATION
    LIVE = live
    
    # SET DEFAULT POLLUTANTS IF NOT SPECIFIED
    if pollutants is None:
        pollutants = ['PM25', 'PM10', 'NO', 'NO2', 'NOx']
    
    # FILTER FILES BY CITY IF SPECIFIED
    if city:
        # Filter files by city if needed
        city = city.lower()
        print(f"Processing data for city: {city}")
    
    # PROCESS EACH FILE IN THE RAW DATA DIRECTORY
    for idx, file in enumerate(files):
        try:
            # MEMORY CLEANUP
            gc.collect()
            
            # SETUP FILE INFORMATION
            filepath = os.path.join(data_dir, file)
            mixed_unit_identification = False
            
            # GET SITE INFORMATION FROM FILENAME
            if LIVE:
                site_id, site_name, year, city_name = get_siteId_Name_Year_City_LIVE(file, sites)
            else:
                site_id, site_name, year, city_name = get_siteId_Name_Year_City(file, sites)
            
            # SKIP IF CITY FILTER IS APPLIED AND DOESN'T MATCH
            if city and city_name.lower() != city:
                continue
            
            # GET FORMATTED DATAFRAME FROM RAW FILE
            true_df, station_name, city_name, state = get_formatted_df(filepath, site_name, city_name, city_name)
            
            # REMOVE DUPLICATE INDICES
            true_df = true_df.loc[~true_df.index.duplicated(keep='first')]
            
            # CREATE A COPY OF THE DATAFRAME
            df = true_df.copy()
            filename = station_name + "_" + str(year) 
            
            # PREPARE LOCAL DATAFRAME FOR PROCESSING
            local_df = df.copy()
            local_df['date'] = pd.to_datetime(local_df['Timestamp']).dt.date
            local_df['site_id'] = site_id
            local_df['site_name'] = site_name
            local_df['city'] = city_name
            local_df['state'] = state
            
            # PROCESS EACH POLLUTANT
            for pollutant in pollutants:
                if len(df[pollutant].value_counts()) == 0:
                    print(f"Not available {pollutant} data")
                    continue
                else:
                    # DATA CLEANING PROCESS FOR EACH POLLUTANT
                    # STEP 1: GROUP AND PLOT DATA
                    local_df = group_plot(local_df, pollutant, pollutant, station_name, filename, year=year)
                    
                    # STEP 2: CALCULATE ROLLING AVERAGE
                    local_df[pollutant + '_hourly'] = local_df.groupby("site_id")[pollutant].rolling(
                        window=4, min_periods=1).mean().values
                    
                    # STEP 3: CLEAN OUTLIERS
                    local_df[pollutant + '_clean'] = local_df[pollutant + '_outliers']
                    local_df[pollutant + '_clean'].mask(local_df[pollutant + '_hourly'] < 0, np.nan, inplace=True)
                    
                    # STEP 4: REMOVE TEMPORARY COLUMNS
                    local_df.drop(columns=[f"{pollutant}_hourly"], inplace=True)
                    
                    print(f"Successfully cleaned {pollutant} for {station_name}")
            
            # CHECK AND FIX UNIT INCONSISTENCIES FOR NITROGEN COMPOUNDS
            if df['NOx'].isnull().all() or df['NO2'].isnull().all() or df['NO'].isnull().all():
                print("No available NOx, NO2, NO data | Not checking for unit inconsistency")
            else:
                print(f"Finding unit inconsistencies for {station_name}")
                local_df = correct_unit_inconsistency(local_df, filename, mixed_unit_identification, plot=True)
            
            # ADDITIONAL DATA PROCESSING
            # CHECK FOR NO/NOx/NO2 COUNT MISMATCHES
            local_df = NO_count_mismatch(local_df)
            
            # FINAL DATAFRAME CLEANUP
            local_df = local_df.reindex()
            
            # REMOVE UNNECESSARY COLUMNS
            local_df = local_df[local_df.columns.drop(list(local_df.filter(regex='_int')))]
            local_df = local_df[local_df.columns.drop(list(local_df.filter(regex='(?<!_)consecutives')))]
            
            # DROP UNUSED COLUMNS
            local_df = local_df.drop(columns=[
                't', 'std', 'med', 'date', 'ratio', 
                'Benzene', 'Toluene', 'Xylene', 'O Xylene', 'Eth-Benzene', 'MP-Xylene', 
                'AT', 'RH', 'WS', 'WD', 'RF', 'TOT-RF', 'SR', 'BP', 'VWS'
            ], errors='ignore')
            
            # REORDER COLUMNS
            local_df = local_df[['Timestamp', 'site_id', 'city', 'state'] + 
                              [col for col in local_df.columns if col not in 
                                ['dates', 'Timestamp', 'site_id', 'city', 'state']]]
            
            # ADD YEAR COLUMN
            local_df['year'] = year
            print("LOG: DONE LOCAL DF")
            
            # SAVE PROCESSED DATA
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            if file.endswith('.csv'):
                fn = os.path.join(str(save_dir), f"{site_id}_{year}.csv")
                local_df.to_csv(fn, index=False)
                
            if file.endswith('.xlsx'):
                fn = os.path.join(str(save_dir), f"{site_id}_{year}.xlsx")
                local_df.drop(columns=['To Date', 'Timestamp'], inplace=True, errors='ignore')
                local_df.rename(columns={'From Date': 'Timestamp'}, inplace=True, errors='ignore')
                local_df.to_excel(fn, index=False)
            
            print(f'\033[92mSaved successfully for: {site_id}_{year}\033[0m')
            plt.close('all')
            print("----------------------------------------------------------")
            
        except Exception as e:
            print(f"Error occurred in [airpy processing] - {e}")
            print("----------------------------------------------------------") 