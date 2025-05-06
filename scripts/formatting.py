import pandas as pd
import numpy as np
from scripts.df import clean_dataframe_filepath, clean_dataframe


def read_df(df):
    # Check if 'Timestamp' or similar column exists and rename it to 'Timestamp'
    dd = ['Timestamp']
    for d in dd:
        if d in df.columns:
            df[d] = pd.to_datetime(df[d], errors='coerce', format='%Y-%m-%d %H:%M:%S')

    #cleans all data for null entries and replaces with np.nan
    try:
        df['PM10'] =  pd.to_numeric(df.PM10, errors='coerce')
    except:
        print("NO PM10 data")
        df['PM10'] = np.nan
    
    try:
        df['NO'] =  pd.to_numeric(df.NO, errors='coerce')
    except:
        print("No NO data")
        df['NO'] = np.nan
    
    try:
        df['NO2'] =  pd.to_numeric(df.NO2, errors='coerce')
    except:
        print("No NO2 data")
        df['NO2'] = np.nan
    
    try:
        df['NOx'] =  pd.to_numeric(df.NOx, errors='coerce')
    except:
        print("NO NOx data")
        df['NOx'] = np.nan
    
    try:
        df['Ozone'] =  pd.to_numeric(df.Ozone, errors='coerce')
    except:
        print("NO Ozone data")
        df['Ozone'] = np.nan
    
    try:
        df.rename(columns = {'PM2.5':'PM25'}, inplace = True)
        df['PM25'] =  pd.to_numeric(df.PM25, errors='coerce')
    except:
        df['PM25'] = np.nan
        print("NO PM data")
    return df
        

def get_formatted_df(path, station_name=None, city=None, state=None):
    
    """
    function removes null entries and formats the date column
    
    Parameter
    ---------
    df: pandas dataframe
        contains raw data and timestamp 
    col: string
        could be PM25(for PM2.5), PM10, NO, NO2, NOX, O3
    return
    ------
    df: pandas dataframe
        cleaned for null values and formatted
    station_name, city_name, state: string
        station name, city name, state
    filename: string
        station name + year + ".html
    st_no: int
        unique identifier for the station

    Raw_data_15Min_2022_site_103_CRRI_Mathura_Road_Delhi_IMD_15Min.csv
    """ 
    if path.endswith('.csv'):
        df = pd.read_csv(path)
        df = clean_dataframe(df)
        df = read_df(df=df)
        df.drop(df.filter(regex="Unname"),axis=1, inplace=True)

    elif path.endswith('.xlsx'):
        df = pd.read_excel(path)
        df = df.iloc[16:].reset_index(drop=True)
        end_index = df[df.iloc[:, 0] == "Prescribed Standards"].index[0]
        df = df.iloc[:end_index-1].reset_index(drop=True)
        df.columns = ['From Date', 'To Date', 'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'SO2', 'CO',
                        'Ozone', 'Benzene', 'Toluene', 'Eth-Benzene', 'MP-Xylene', 'RH', 'WS', 'WD', 'SR',
                        'BP', 'Xylene', 'AT']
        # df.rename(columns={'From Date': 'Timestamp'}, inplace=True)
        df['Timestamp'] = df['From Date']
        print("Before cleaning: ", df.shape)
        # df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        # df.sort_values(by='Timestamp', inplace=True)
        # df.drop_duplicates(subset=['Timestamp'], keep='first', inplace=True)
        print(df)
        df = clean_dataframe(df)
        df = read_df(df=df)
        df.drop(df.filter(regex="Unname"),axis=1, inplace=True)

    return df, station_name, city, state


def get_multiple_df_linerized(df1):
    
    """
    function specific for CPCB outputs without any human intervention,
    removes null entries and formats the date column. 
    
    Parameter
    ---------
    df: pandas dataframe
        contains raw data and timestamp 
    col: string
        could be PM25(for PM2.5), PM10, NO, NO2, NOX, O3
 
        
        
    return
    ------
    df: pandas dataframe
        cleaned for null values and formatted
    station_name, city_name, state: string
        station name, city name, state
    filename: string
        station name + year + ".html
    st_no: int
        unique identifier for the station

    """    

    from_year = df1['Unnamed: 1'][8][6:10]
    to_year = df1['Unnamed: 1'][9][6:10]
    station_name = df1['CENTRAL POLLUTION CONTROL BOARD'][11]
    lst = df1.index[df1['CENTRAL POLLUTION CONTROL BOARD'] == "From Date"].tolist()
    city = df1['Unnamed: 1'][4]
    state = df1['Unnamed: 1'][3]

    print("get_multiple_df_linerized")
    print(from_year, to_year, station_name, lst, city, state)

    count = 1
    for i in range(len(lst)):
        
        if (i+1 == len(lst)):
            df_temp = df1[lst[i]:].reset_index(drop=True)
        else:
            df_temp = df1[lst[i]:lst[i+1]-1].reset_index(drop=True)
        df_temp = df_temp.rename(columns=df_temp.iloc[0]).drop(df_temp.index[0])
        df_temp = df_temp.loc[:, df_temp.columns.notna()]
        
        if count != 1:
            del df_temp['From Date'],  df_temp['To Date']
            df_concat = pd.concat([df_concat, df_temp], axis=1)
        else:
            df_concat = df_temp
        count = count + 1

    df_concat = df_concat.rename(columns = {'PM2.5':'PM25', 'From Date':'dates'})
    del df_concat['To Date']
    
    if(len(lst)>1):
        df_concat = df_concat[:len(df1[lst[0]:df1.index[df1['CENTRAL POLLUTION CONTROL BOARD'] == "Prescribed Standards"].tolist()[1]-1].reset_index(drop=True))-1]

    return df_concat, station_name, city, state

