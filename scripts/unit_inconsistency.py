import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

#conversion factors for NO, NO2 and NOx from ppb to µg/m3
#Governing Equation: NO(ppb) + NO2(ppb) = NOx(ppb)
NO2_FACTOR = 1.88 # 1 ppb = 1.88 µg/m3
NO_FACTOR = 1.23 # 1 ppb = 1.23 µg/m3
NOx_FACTOR = 1.9125 # (NO ppb + NO2 ppb) * 1.9125 = NOx µgm-3. 

'''
Conversion Equations
--------------------
C1: NO: µg/m3, NO2: µg/m3, NOx: ppb
C2: NO: ppb, NO2: ppb, NOx: ppb
C3: NO: ppb, NO2: ppb, NOx: µg/m3
C4: NO: ppb, NO2: µg/m3, NOx: ppb
C5: NO: ppb, NO2: µg/m3, NOx: µg/m3
C6: NO: µg/m3, NO2: ppb, NOx: ppb
C7: NO: µg/m3, NO2: ppb, NOx: µg/m3
C8: NO: µg/m3, NO2: µg/m3, NOx: µg/m3
'''

VALIDATE_EQUATIONS = {
    'C1' : lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2/NO2_FACTOR) - NOx,                        
    'C2' : lambda NO, NO2, NOx: (NO) + (NO2) - NOx,                                             
    'C4' : lambda NO, NO2, NOx: (NO) + (NO2/NO2_FACTOR) - (NOx),                         
    'C6' : lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2) - NOx,                                  
    # 'C3' : lambda NO, NO2, NOx: (NO) + (NO2) - (NOx/NOx_FACTOR),                      
    # 'C5' : lambda NO, NO2, NOx: (NO) + (NO2/NO2_FACTOR) - (NOx/NOx_FACTOR),                
    # 'C7' : lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2) - (NOx/NOx_FACTOR),                                 
    # 'C8' : lambda NO, NO2, NOx: (NO/NO_FACTOR) + (NO2/NO_FACTOR) - (NOx/NOx_FACTOR),                                
}

CONVERSION_EQUATIONS = {
    'C1' : lambda NO, NO2, NOx: (NO , NO2, NOx),
    'C2' : lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2 *  NO2_FACTOR, NOx),
    'C4' : lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2, NOx),
    'C6' : lambda NO, NO2, NOx: (NO , NO2 * NO2_FACTOR, NOx),
    'UNIDENTIFIABLE' : lambda NO, NO2, NOx: (np.nan, np.nan, np.nan),
    # 'C3' : lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2 * NO2_FACTOR, (NO + NO2)),
    # 'C5' : lambda NO, NO2, NOx: (NO * NO_FACTOR, NO2, (NO + NO2 / NO2_FACTOR)),
    # 'C7' : lambda NO, NO2, NOx: (NO , NO2 * NO2_FACTOR, (NO / NO_FACTOR + NO2)),
    # 'C8' : lambda NO, NO2, NOx: (NO , NO2, (NO/NO_FACTOR + NO2/NO2_FACTOR)),
}
def correct_unit_inconsistency(df,filename, get_input, plot=False):
    df['Timestamp']=pd.to_datetime(df['Timestamp'], format="%Y-%m-%d %H:%M:%S")
    temp = deepcopy(df)
    errors = {}
    
    for equation in VALIDATE_EQUATIONS:
        error = VALIDATE_EQUATIONS[equation](temp['NO_clean'], temp['NO2_clean'], temp['NOx_clean'])
        error[df['NO_clean'].isna() | df['NO2_clean'].isna() | df['NOx_clean'].isna()] = np.nan
        errors[equation] = np.mean(error**2)
        temp[equation] = error
        print(equation)

    PERCENTAGE_FACTOR = 1
    CONSTANT_FACTOR = 1
    temp['THRESHOLD'] = (temp['NOx_clean'].abs() * PERCENTAGE_FACTOR) + CONSTANT_FACTOR
    temp['unidentifiable_flag'] = temp[[*list(errors.keys())]].abs().gt(temp['THRESHOLD'], axis='index').all(axis='columns')
    temp['error'] = temp[[*list(errors.keys())]].abs().idxmin(axis=1)
    temp['error'][temp['unidentifiable_flag']] = 'UNIDENTIFIABLE'
    
    # converted_values = CONVERSION_EQUATIONS[prevalent_error](temp['NO_clean'], temp['NO2_clean'], temp['NOx_clean'])
    temp['NO_CPCB'] = np.nan
    temp['NO2_CPCB'] = np.nan
    temp['NOx_CPCB'] = np.nan
    for equation in CONVERSION_EQUATIONS:
        converted_values = CONVERSION_EQUATIONS[equation](temp['NO_clean'].loc[temp['error'] == equation], 
                                                          temp['NO2_clean'].loc[temp['error'] == equation], 
                                                          temp['NOx_clean'].loc[temp['error'] == equation])
        temp.loc[temp['error'] == equation,'NO_CPCB'] = converted_values[0]
        temp.loc[temp['error'] == equation, 'NO2_CPCB'] = converted_values[1]
        temp.loc[temp['error'] == equation, 'NOx_CPCB'] = converted_values[2]
    temp['NO_clean'] = temp['NO_outliers']
    temp['NO2_clean'] = temp['NO2_outliers']  
    temp['NOx_clean'] = temp['NOx_outliers']

    temp['NO_CPCB'][df['NO_clean'].isna()] = np.nan
    temp['NO2_CPCB'][df['NO2_clean'].isna()] = np.nan
    temp['NOx_CPCB'][df['NOx_clean'].isna()] = np.nan


    temp['NO_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan
    temp['NO2_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan
    temp['NOx_CPCB'][temp['NO_clean'].isna() | temp['NO2_clean'].isna() | temp['NOx_clean'].isna()] = np.nan



    # print(prevalent_error)
    # print(converted_values)
    df['error'] = temp['error']
    df['NO_CPCB'] = temp['NO_CPCB']
    df['NO2_CPCB'] = temp['NO2_CPCB']
    df['NOx_CPCB'] = temp['NOx_CPCB']
    df['Threshold'] = temp['THRESHOLD']
    df['Interesting'] = temp['THRESHOLD'] > temp['C1'].abs()
    for equation in VALIDATE_EQUATIONS:
        df[equation] = temp[equation]
    #Set All NO, NO2 and NOx to NaN if either one of them is NaN
    return df
        

    
