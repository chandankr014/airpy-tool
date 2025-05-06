'''
Mark observation as mismatch if either NO or NO2 do not exist, but NOx is not NaN and > 0.
'''
import pandas as pd
import numpy as np


def NO_count_mismatch(df: pd.DataFrame):
    df['mismatch'] = np.where(((df['NOx'].notna() & df['NOx'] > 0) & (df['NO'].isna() | df['NO2'].isna())), 1, 0)
    return df
    
