import numpy as np
import matplotlib.pyplot as plt


def outlier_treatment(datacolumn):
    """
    function gives IQR outlier threshold 
    
    Parameter
    ---------
    datacolumn: pandas column
        annual 15 mins pollutant data 
        
        
    return
    ------
    lower_range: int
        
    
    upper_range: int
    
    
    This function takes up the annual 15 mins data for each pollutant and calculates the outlier threshold.
    Provides IQR range to remove the outliers closer to the minimum value of the dataset
    
    Reference
    ---------
    .. [1] Chaudhary, S. (2021, December 12). Why “1.5” in IQR Method of Outlier Detection? - Towards Data Science. 
    Medium. https://towardsdatascience.com/why-1-5-in-iqr-method-of-outlier-detection-5d07fdc82097
    
    """
    
    #get the 1st and 3rd quartile of the series
    Q1,Q3 = np.nanpercentile(datacolumn , [25,75])
    
    #calculate the Interquartile range (IQR)
    IQR = Q3 - Q1
    
    #calculate upper and lower outlier threshold  
    lower_range = Q1 - (1.5 * IQR)
    upper_range = Q3 + (1.5 * IQR)
    return lower_range,upper_range


def find_local_outliers(local_df, col):
    
    """
    function removes abnormaly high values within a local timeseries 
    
    Parameter
    ---------
    local_df: pandas dataframe
        contains pollutant data and timestamp 
    col: pollutant header name
        could be PM25(PM2.5), PM10, NO, NO2, NOX, O3
        
        
    return
    ------
    unchanged: pandas dataframe
        contains data column with suffix "_outliers" which is cleaned for extreme outliers
        
    
    Finds outlier by running a 3 hour window (3*4 15 mins data)
    Median Absolute Deviation (MAD) = (value - rolling window median)

    t = |(value - rolling window median) / MAD|

    t > 3.5 --> removed as outliers
    
    
    Reference
    ---------
    .. [1] Iglewicz, B., & Hoaglin, D. C. How to Detect and Handle Outliers (Vol. 16). 
    Amsterdam University Press. 1993. https://books.google.nl/books?id=siInAQAAIAAJ. ISBN: 978-82-425-3091-2
    
    .. [2] Leys, C.; Ley, C.; Klein, O.; Bernard, P.; Licata, L. Detecting Outliers: 
    Do Not Use Standard Deviation around the Mean, Use Absolute Deviation around the Median. 
    J. Exp. Soc. Psychol. 2013, 49 (4), 764–766. 
    
    .. [3] Mahajan, M., Kumar, S., Pant, B., & Tiwari, U. K. (2020). Incremental Outlier Detection in Air Quality 
    Data Using Statistical Methods. 2020 International Conference on Data Analytics for Business and Industry: Way 
    Towards a Sustainable Economy, ICDABI 2020. https://doi.org/10.1109/ICDABI51230.2020.9325683
   


    """
    
    #Create a deep copy of local df as unchanged
    unchanged = local_df.copy(deep = True)
    
    #create a copy of cleaned data
    local_df[col + '_outliers'] = local_df[col+'_consecutives']
    
    #interpolate the raw data while will be used to create flags
    local_df[col+'_int'] = interpolate_gaps(local_df[col].to_numpy(), limit= 2)
    
    #group the values by site_id and get median value from the interpolated data
    local_df["med"] = local_df.groupby("site_id")[col+'_int'].rolling(window = 4*3, min_periods = 4*3).median().values
    
    #get the absolute difference between the actual value and median on running 3 hr window only if all 12 values where present
    local_df["med_2"] = (local_df[col+'_int'] - local_df["med"]).abs()
    
    #get the median of med_2
    local_df["mad"] = local_df.groupby("site_id")["med_2"].rolling(window = 4*3, min_periods = 4*3).median().values

    #calculate the MAD outlier threshold
    local_df["t"] = ((local_df[col]-local_df["med"]) / local_df["mad"]).abs()
    
    #mask all values which have t above 3.5 as np.nan
    local_df[col+'_outliers'].mask(local_df['t'] > 3.5, np.nan, inplace=True)
    
    #mask all values which are below the IQR lower boundary
    local_df[col + '_outliers'].mask(local_df[col] < outlier_treatment(local_df[col])[0], np.nan, inplace=True)
    
    #return the "_outliers" column to unchanged dataframe
    unchanged[col + '_outliers']= local_df[col + '_outliers']
    return unchanged


def find_repeats(local_df, col):
    """
    function removes consecutive repeats within a local timeseries 
    
    Parameter
    ---------
    local_df: pandas dataframe
        contains pollutant data and timestamp 
    col: pollutant header name
        could be PM25(PM2.5), PM10, NO, NO2, NOX, O3
        
        
    return
    ------
    unchanged: pandas dataframe
        contains data column with suffix "_consecutive" which is cleaned for consecutive repeats within a local timeseries 
        
    
    Finds repeats by running a 24 hour window (24*4 15 mins data)
    Co-efficient of Variance = Standard deviation / Mean

    t > 0.1 --> removed as repeats
    
    
    Reference
    ---------
    .. [1] Singh, V.; Singh, S.; Biswal, A.; Kesarkar, A. P.; Mor, S.; Ravindra, K. Diurnal and Temporal Changes 
    in Air Pollution during COVID-19 Strict Lockdown over Different Regions of India. Environ. Pollut. 2020, 266, 
    115368. https://doi.org/10.1016/j.envpol.2020.115368.

    """
    #create a deep copy of working file as unchanged
    unchanged = local_df.copy(deep = True)
    
    #create a copy of raw data as "_consecutives"
    local_df[col+'consecutives'] = local_df[col]
    
    #try to forward interpolate the data
    try:
        local_df[col+'_int'] = interpolate_gaps(local_df[col].to_numpy(), limit = 0)
    except:
        local_df[col+'_int'] = local_df[col]
        pass
    
    #increment the local copy of raw value by 1
    local_df[col+'_int'] = local_df[col+'_int'] +1
    
    #calculate the mean, standard deviation of maniputed data in the rolling window of 1 day
    local_df["med"] = local_df.groupby("site_id")[col+'_int'].rolling(window = 4*24*2, min_periods = 1).mean().values
    local_df["std"] = local_df.groupby("site_id")[col+'_int'].rolling(window = 4*24*2, min_periods = 1).std().values
    
    #calculate co-variance
    local_df["t"] = (local_df["std"]/local_df['med'])
    
    #mask all consecutive repeats with t < 0.1 as np.nan
    local_df[col+'consecutives'].mask(local_df['t'] < 0.1, np.nan, inplace=True)

    #create a local copy of data cleaned for consecutives in unchanged
    unchanged[col+'_consecutives'] = local_df[col+'consecutives']

    return unchanged


def interpolate_gaps(values, limit=None):
    
    """
    function removes interpolates a copy of raw data, only with limit of two and fills the missing value between two valid values.
    
    Parameter
    ---------
    values: pollutant column
        could be PM25(PM2.5), PM10, NO, NO2, NOX, O3
        
        
    return
    ------
    filled: numpy array
        contains forward interpolated data
        
        
    Fill gaps using linear interpolation, optionally only fill gaps up to a
    size of `limit`
    
    ----------
    Code credits: Joe Kington, Software engineer at Planet, Houston, Texas, United States
  
    .. [1] How to plot and work with NaN values in matplotlib. (n.d.). Stack Overflow. 
    https://stackoverflow.com/questions/36455083/how-to-plot-and-work-with-nan-values-in-matplotlib

    """

    values = np.asarray(values)
    i = np.arange(values.size)
    valid = np.isfinite(values)
    filled = np.interp(i, i[valid], values[valid])

    if limit is not None:
        invalid = ~valid
        for n in range(1, limit+1):
            invalid[:-n] &= invalid[n:]
        filled[invalid] = np.nan

    return filled


def find_abs_rep(local_df, col, filename):
    
    """
    function identifies absolutely repeating values within the timeseries
    
    Parameter
    ---------
    local_df: pandas dataframe
        contains pollutant data and timestamp 
    col: pollutant header name
        could be PM25(PM2.5), PM10, NO, NO2, NOX, O3
    filename: string
        contains station name + year + '.html'

    return
    ------
    unchanged: pandas dataframe
        contains pollutant data removed for absolute repeats
    """
    
    unchanged = local_df.copy(deep = True)
    ar1 = interpolate_gaps(local_df[col].to_numpy(), limit=2)
    local_df[col + '_ab_rep'] = ar1
    local_df['hint'] = local_df[col + '_ab_rep'].loc[(local_df[col + '_ab_rep'].shift() != local_df[col + '_ab_rep']) & 
                                    (local_df[col + '_ab_rep'].shift(2) != local_df[col + '_ab_rep']) &
                                    (local_df[col + '_ab_rep'].shift(3) != local_df[col + '_ab_rep']) &
                                    (local_df[col + '_ab_rep'].shift(4) != local_df[col + '_ab_rep'])]
    local_df[col + '_ab_rep'] = np.where(local_df['hint'] == True, np.nan, local_df[col + '_ab_rep'])
    unchanged[col + '_ab_rep'] = local_df[col + '_ab_rep']
    return unchanged


def group_plot(local_df, col, label, station_name, filename, plot=False, year=''):

    """
    function removes consecutive repeats within a local timeseries 
    
    Parameter
    ---------
    only_plots: pandas dataframe
        contains raw data and timestamp 
    local_df: pandas dataframe
        contains pollutant data and timestamp that are being cleaned
    col: string
        could be PM25(for PM2.5), PM10, NO, NO2, NOX, O3
    label: string
        string for corresponding pollutants with proper sub and super scripts
    station_name: string
        station name
    filename: string
        station name + year + ".html
    st_no: int
        unique identifier for the station
    return
    ------
    true_df: pandas dataframe
        contains data column with suffix "_consecutive" and "_outliers" which is cleaned for consecutive repeats and outliers within a local timeseries 
    """
    
    df_temp = find_repeats(local_df, col)
    df_temp = find_abs_rep(df_temp, col, filename)
    df = find_local_outliers(df_temp, col)

    
    if (col == 'PM25')or(col == 'PM10') or (col == 'SO2') or (col == 'Ozone'):
        yaxis_title= str(label) + " concentration in µg/m³"
        # fig.update_layout(xaxis_title="Date", yaxis_title= str(label) + " concentration in µg/m³")
    else:
        yaxis_title= str(label) + " concentration in reported units"

    # true_df = df.copy(deep=True)
    # true_df[col+'_consecutives'] = df[col+'_consecutives']
    # true_df[col+'_outliers'] = df[col+'_outliers']
    true_df = local_df.copy(deep=True)
    true_df[col+'_consecutives'] = df_temp[col+'_consecutives']
    true_df[col+'_outliers'] = df[col+'_outliers']
    
    # # Plots the diurnal curve before and after cleaning
    # if plot:
    #     print("PLOTTING....")
    #     fig, ax = plt.subplots()
    #     df = true_df
    #     get_diurnal(df, col+'_consecutives', 'blue', 'title', ax)
    #     get_diurnal(df, col+'_outliers', 'cyan', 'title', ax)
    #     get_diurnal(df, col, 'red', 'title', ax)
    #     plt.title(str(station_name))
    #     plt.xticks(np.arange(0,24, 1.0))
    #     plt.grid(color = '#F5F5F5')
    #     ax.axvspan(16, 20, alpha=0.1, color='red', label = 'Peak traffic hours')
    #     ax.axvspan(7, 11, alpha=0.1, color='red')
    #     ax.legend(loc='upper right')
    #     plt.xlabel("Hours")
    #     plt.ylabel(str(yaxis_title))
    #     # plt.show(block=False)
    #     plt.savefig('plots/diurnal/' + str(station_name) + '_' + str(year) + '_' + str(col) +'.png')
    return true_df