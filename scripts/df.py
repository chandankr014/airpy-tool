"""
For all functions required in cleaning and preprocessing of dataframe.
"""

import pandas as pd

""" clean from df """
def clean_dataframe(df: pd.DataFrame):
    col_dict = {}
    for col in df.columns:
        if " (" in col:
            new_col = col.split(" (")[0]
            col_dict[col] = new_col
        else:
            col_dict[col] = col
    df.rename(columns=col_dict, inplace=True)
    print("LOG: DATAFRAME CLEANED")
    return df


""" clean from filepath """
def clean_dataframe_filepath(filepath: str):
    df = pd.read_csv(filepath)
    col_dict = {}
    for col in df.columns:
        if " (" in col:
            new_col = col.split(" (")[0]
            col_dict[col] = new_col
        else:
            col_dict[col] = col
    df.rename(columns=col_dict, inplace=True)
    print("LOG: DATAFRAME CLEANED")
    return df



# df = clean_dataframe_filepath("../Raw_data_15Min_2023_site_103_CRRI_Mathura_Road_Delhi_IMD_15Min.csv")
# print(df.columns)