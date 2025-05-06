import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gc
from pathlib import Path
import warnings
import argparse
import sys

# SUPPRESS WARNINGS
warnings.filterwarnings("ignore")

# IMPORT CUSTOM MODULES
from scripts.formatting import *
from scripts.NO_Count_Mismatch import *
from scripts.unit_inconsistency import *
from scripts.data_cleaning import *
from scripts.functions import *


def process_data(city=None, live=False, raw_dir=None, clean_dir=None, pollutants=None):
    """
    Process air quality data.
    
    Parameters:
    -----------
    city : str, optional
        City name to process
    live : bool, default=False
        Whether to process live data
    raw_dir : str, optional
        Path to raw data directory
    clean_dir : str, optional
        Path to save cleaned data
    pollutants : list, optional
        List of pollutants to process
    """
    # SETUP DIRECTORIES
    if raw_dir:
        data_dir = Path(raw_dir)
    else:
        data_dir = Path(f'data/raw/')
    
    if clean_dir:
        save_dir = Path(clean_dir)
    else:
        save_dir = Path(f'data/clean/')
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # LOAD SITE INFORMATION
    sites = pd.read_csv('files/sites_master.csv')
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
                fn = str(save_dir) + '/' + str(site_id) + '_' + str(year) + ".csv"
                local_df.to_csv(fn, index=False)
                
            if file.endswith('.xlsx'):
                fn = str(save_dir) + '/' + str(site_id) + '_' + str(year) + ".xlsx"
                local_df.drop(columns=['To Date', 'Timestamp'], inplace=True)
                local_df.rename(columns={'From Date': 'Timestamp'}, inplace=True)
                local_df.to_excel(fn, index=False)
            
            print(f'\033[92mSaved successfully for: {site_id}_{year}\033[0m')
            plt.close('all')
            print("----------------------------------------------------------")
            
        except Exception as e:
            print(f"Error occurred in [airpy processing] - {e}")
            print("----------------------------------------------------------")


def main():
    """Main entry point for AirPy command line usage."""
    # PARSE COMMAND LINE ARGUMENTS
    parser = argparse.ArgumentParser(description="AirPy - Air Quality Data Processing Tool")
    parser.add_argument("--city", type=str, help="City name to process")
    parser.add_argument("--live", action="store_true", help="Process live data")
    parser.add_argument("--raw-dir", type=str, help="Path to raw data directory")
    parser.add_argument("--clean-dir", type=str, help="Path to save cleaned data")
    parser.add_argument("--pollutants", type=str, nargs="+", 
                        help="List of pollutants to process (default: PM25 PM10 NO NO2 NOx)")
    
    args = parser.parse_args()
    
    # ENSURE DEFAULT DIRECTORIES EXIST
    if not os.path.exists('data/raw'):
        os.makedirs('data/raw')
    
    if not os.path.exists('data/clean'):
        os.makedirs('data/clean')
        
    # PROCESS DATA
    process_data(
        city=args.city,
        live=args.live,
        raw_dir=args.raw_dir,
        clean_dir=args.clean_dir,
        pollutants=args.pollutants
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
