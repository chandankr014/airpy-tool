"""
Data cleaning and processing utilities for AirPy.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy


# -----------------------------------------------------------------------------
# Outlier detection and treatment functions
# -----------------------------------------------------------------------------

def outlier_treatment(datacolumn):
    """
    Function gives IQR outlier threshold.
    
    Args:
        datacolumn: Pandas column with annual 15 mins pollutant data
        
    Returns:
        Tuple of (lower_range, upper_range) - thresholds for outlier detection
    """
    # Get the 1st and 3rd quartile of the series
    Q1, Q3 = np.nanpercentile(datacolumn, [25, 75])
    
    # Calculate the Interquartile range (IQR)
    IQR = Q3 - Q1
    
    # Calculate upper and lower outlier threshold  
    lower_range = Q1 - (1.5 * IQR)
    upper_range = Q3 + (1.5 * IQR)
    return lower_range, upper_range


def find_local_outliers(local_df, col):
    """
    Function removes abnormally high values within a local timeseries.
    
    Args:
        local_df: Pandas DataFrame containing pollutant data and timestamp
        col: Pollutant header name (e.g., 'PM25', 'NO2')
        
    Returns:
        DataFrame with outliers removed
    """
    # Create a deep copy of local df as unchanged
    unchanged = local_df.copy(deep=True)
    
    # Create a copy of cleaned data
    local_df[col + '_outliers'] = local_df[col+'_consecutives']
    
    # Interpolate the raw data while will be used to create flags
    local_df[col+'_int'] = interpolate_gaps(local_df[col].to_numpy(), limit=2)
    
    # Group the values by site_id and get median value from the interpolated data
    local_df["med"] = local_df.groupby("site_id")[col+'_int'].rolling(window=4*3, min_periods=4*3).median().values
    
    # Get the absolute difference between the actual value and median on running 3 hr window only if all 12 values where present
    local_df["med_2"] = (local_df[col+'_int'] - local_df["med"]).abs()
    
    # Get the median of med_2
    local_df["mad"] = local_df.groupby("site_id")["med_2"].rolling(window=4*3, min_periods=4*3).median().values

    # Calculate the MAD outlier threshold
    local_df["t"] = ((local_df[col]-local_df["med"]) / local_df["mad"]).abs()
    
    # Mask all values which have t above 3.5 as np.nan
    local_df[col+'_outliers'].mask(local_df['t'] > 3.5, np.nan, inplace=True)
    
    # Mask all values which are below the IQR lower boundary
    local_df[col + '_outliers'].mask(local_df[col] < outlier_treatment(local_df[col])[0], np.nan, inplace=True)
    
    # Return the "_outliers" column to unchanged dataframe
    unchanged[col + '_outliers'] = local_df[col + '_outliers']
    return unchanged


def find_repeats(local_df, col):
    """
    Function removes consecutive repeats within a local timeseries.
    
    Args:
        local_df: Pandas DataFrame containing pollutant data and timestamp
        col: Pollutant header name (e.g., 'PM25', 'NO2')
        
    Returns:
        DataFrame with consecutive repeats removed
    """
    # Create a deep copy of working file as unchanged
    unchanged = local_df.copy(deep=True)
    
    # Create a copy of raw data as "_consecutives"
    local_df[col+'consecutives'] = local_df[col]
    
    # Try to forward interpolate the data
    try:
        local_df[col+'_int'] = interpolate_gaps(local_df[col].to_numpy(), limit=0)
    except:
        local_df[col+'_int'] = local_df[col]
        pass
    
    # Increment the local copy of raw value by 1
    local_df[col+'_int'] = local_df[col+'_int'] + 1
    
    # Calculate the mean, standard deviation of maniputed data in the rolling window of 1 day
    local_df["med"] = local_df.groupby("site_id")[col+'_int'].rolling(window=4*24*2, min_periods=1).mean().values
    local_df["std"] = local_df.groupby("site_id")[col+'_int'].rolling(window=4*24*2, min_periods=1).std().values
    
    # Calculate co-variance
    local_df["t"] = (local_df["std"]/local_df['med'])
    
    # Mask all consecutive repeats with t < 0.1 as np.nan
    local_df[col+'consecutives'].mask(local_df['t'] < 0.1, np.nan, inplace=True)

    # Create a local copy of data cleaned for consecutives in unchanged
    unchanged[col+'_consecutives'] = local_df[col+'consecutives']

    return unchanged


def interpolate_gaps(values, limit=None):
    """
    Interpolate gaps in time series.
    
    Args:
        values: Array of values
        limit: Maximum number of consecutive NaN values to fill
        
    Returns:
        Array with interpolated values
    """
    values = np.asarray(values)
    i = np.arange(values.size)
    valid = np.isfinite(values)
    filled = np.interp(i, i[valid], values[valid])
    
    if limit is not None:
        invalid_runs = find_runs(~valid)
        for run in invalid_runs:
            if len(run) > limit:
                filled[run] = np.nan
    
    return filled


def find_runs(x):
    """
    Find runs of consecutive items in an array.
    """
    # Create an array with the same shape as x
    n = x.shape[0]
    # Add start and endpoints
    y = np.zeros(n + 2, dtype=bool)
    y[1:-1] = x
    y[0] = False
    y[-1] = False
    # Get indices where there are changes
    pos = np.flatnonzero(y[:-1] != y[1:])
    # Get the indices of the runs
    return [np.arange(pos[i], pos[i+1]) for i in range(0, len(pos), 2)]


def group_plot(local_df, col, label, station_name, filename, plot=False, year=''):
    """
    Process a pollutant column with consecutive and outlier detection.
    
    Args:
        local_df: DataFrame containing the data
        col: Pollutant column name
        label: Label for plots
        station_name: Name of the station
        filename: Filename for saving plots
        plot: Whether to generate plots
        year: Year of the data
        
    Returns:
        Processed DataFrame
    """
    # Check if column exists
    if col not in local_df.columns:
        print(f"Error: Column {col} not found")
        local_df[col+'_consecutives'] = np.nan
        local_df[col+'_outliers'] = np.nan
        return local_df
    
    # Find consecutive repeats
    local_df = find_repeats(local_df, col)
    
    # Find outliers
    local_df = find_local_outliers(local_df, col)
    
    # Generate plots if requested
    if plot:
        plt.figure(figsize=(12, 8))
        plt.plot(local_df['Timestamp'], local_df[col], 'b.', alpha=0.2, label='Raw')
        plt.plot(local_df['Timestamp'], local_df[col+'_consecutives'], 'g.', alpha=0.5, label='Cleaned Consecutive')
        plt.plot(local_df['Timestamp'], local_df[col+'_outliers'], 'r.', alpha=0.5, label='Cleaned Outlier')
        plt.title(f"{label} at {station_name} - {year}")
        plt.ylabel(f"{label} (μg/m³)")
        plt.xlabel("Time")
        plt.legend()
        plt.savefig(f"{filename}_{col}_cleaning.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    return local_df


# -----------------------------------------------------------------------------
# Nitrogen compound processing functions
# -----------------------------------------------------------------------------

def NO_count_mismatch(df: pd.DataFrame):
    """
    Mark observation as mismatch if either NO or NO2 do not exist, but NOx is not NaN and > 0.
    
    Args:
        df: DataFrame containing NO, NO2, NOx columns
        
    Returns:
        DataFrame with mismatch flag added
    """
    df['mismatch'] = np.where(((df['NOx'].notna() & df['NOx'] > 0) & (df['NO'].isna() | df['NO2'].isna())), 1, 0)
    return df


# Conversion factors for NO, NO2 and NOx from ppb to µg/m3
# Governing Equation: NO(ppb) + NO2(ppb) = NOx(ppb)
NO2_FACTOR = 1.88  # 1 ppb = 1.88 µg/m3
NO_FACTOR = 1.23   # 1 ppb = 1.23 µg/m3
NOx_FACTOR = 1.9125  # (NO ppb + NO2 ppb) * 1.9125 = NOx µgm-3

# Validation equations for different unit combinations
VALIDATE_EQUATIONS = {
    'C1': lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2/NO2_FACTOR) - NOx,                        
    'C2': lambda NO, NO2, NOx: (NO) + (NO2) - NOx,                                             
    'C4': lambda NO, NO2, NOx: (NO) + (NO2/NO2_FACTOR) - (NOx),                         
    'C6': lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2) - NOx,                                  
}

# Conversion equations for different unit combinations
CONVERSION_EQUATIONS = {
    'C1': lambda NO, NO2, NOx: (NO, NO2, NOx),
    'C2': lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2 * NO2_FACTOR, NOx),
    'C4': lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2, NOx),
    'C6': lambda NO, NO2, NOx: (NO, NO2 * NO2_FACTOR, NOx),
    'UNIDENTIFIABLE': lambda NO, NO2, NOx: (np.nan, np.nan, np.nan),
}


def correct_unit_inconsistency(df, filename, get_input, plot=False):
    """
    Correct unit inconsistencies in NO, NO2, and NOx measurements.
    
    Args:
        df: DataFrame containing the data
        filename: Filename for saving plots
        get_input: Flag for mixed unit identification
        plot: Whether to generate plots
        
    Returns:
        DataFrame with corrected units
    """
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%Y-%m-%d %H:%M:%S")
    temp = deepcopy(df)
    errors = {}
    
    # Calculate errors for each equation
    for equation in VALIDATE_EQUATIONS:
        error = VALIDATE_EQUATIONS[equation](temp['NO_clean'], temp['NO2_clean'], temp['NOx_clean'])
        error[df['NO_clean'].isna() | df['NO2_clean'].isna() | df['NOx_clean'].isna()] = np.nan
        errors[equation] = np.mean(error**2)
        temp[equation] = error
        print(equation)

    # Set thresholds for error identification
    PERCENTAGE_FACTOR = 1
    CONSTANT_FACTOR = 1
    temp['THRESHOLD'] = (temp['NOx_clean'].abs() * PERCENTAGE_FACTOR) + CONSTANT_FACTOR
    
    # Flag points with errors above threshold
    temp['unidentifiable_flag'] = temp[[*list(errors.keys())]].abs().gt(temp['THRESHOLD'], axis='index').all(axis='columns')
    
    # Find the best equation for each point
    temp['error'] = temp[[*list(errors.keys())]].abs().idxmin(axis=1)
    temp['error'][temp['unidentifiable_flag']] = 'UNIDENTIFIABLE'
    
    # Apply unit conversions based on identified equations
    temp['NO_CPCB'] = np.nan
    temp['NO2_CPCB'] = np.nan
    temp['NOx_CPCB'] = np.nan
    
    for equation in CONVERSION_EQUATIONS:
        converted_values = CONVERSION_EQUATIONS[equation](
            temp['NO_clean'].loc[temp['error'] == equation], 
            temp['NO2_clean'].loc[temp['error'] == equation], 
            temp['NOx_clean'].loc[temp['error'] == equation]
        )
        temp.loc[temp['error'] == equation, 'NO_CPCB'] = converted_values[0]
        temp.loc[temp['error'] == equation, 'NO2_CPCB'] = converted_values[1]
        temp.loc[temp['error'] == equation, 'NOx_CPCB'] = converted_values[2]
    
    # Restore original cleaned values
    temp['NO_clean'] = temp['NO_outliers']
    temp['NO2_clean'] = temp['NO2_outliers']  
    temp['NOx_clean'] = temp['NOx_outliers']

    # Handle missing values
    temp['NO_CPCB'][df['NO_clean'].isna()] = np.nan
    temp['NO2_CPCB'][df['NO2_clean'].isna()] = np.nan
    temp['NOx_CPCB'][df['NOx_clean'].isna()] = np.nan

    temp['NO_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan
    temp['NO2_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan
    temp['NOx_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan

    # Copy results to original dataframe
    df['error'] = temp['error']
    df['NO_CPCB'] = temp['NO_CPCB']
    df['NO2_CPCB'] = temp['NO2_CPCB']
    df['NOx_CPCB'] = temp['NOx_CPCB']
    df['Threshold'] = temp['THRESHOLD']
    df['Interesting'] = temp['THRESHOLD'] > temp['C1'].abs()
    
    for equation in VALIDATE_EQUATIONS:
        df[equation] = temp[equation]
        
    return df 