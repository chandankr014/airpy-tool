import pandas as pd

count_df =  pd.read_csv(r"Summary\summary_count_final.csv")
mean_df = pd.read_csv(r'Summary\summary_mean_final.csv')
final_site_list = pd.read_csv(r'files/list_of_sites.csv')

# print(final_site_list.drop_duplicates(subset=['site_id']))
final_site_list = final_site_list[final_site_list['pollutant'] == 'NO2']
count_df = count_df[count_df['site_id'].isin(final_site_list['site_id'])]


'''
    +---------+--------+-------+-------+   
    |         |   NO   |  NO2  |  NOx  |
    +---------+--------+-------+-------+
    |   red   |  ppb   |  ppb  |  ppb  |
    |   blue  | µg m-3 | µg m-3|  ppb  |
    |  violet | µg m-3 |  ppb  |µg m-3 |
    |  green  |  both  |µg m-3 |  both |
    +---------+--------+-------+-------+   
    | otherwise (yellow)               |
    | (retained without any changes)   |
    +---------+--------+-------+-------+    


print('Unit Inconsistency type 1: NO: ppb, NO2: ppb, NOx: ppb')
print('Unit Inconsistency type 2: NO: µg m-3, NO2: µg m-3, NOx: ppb')
print('Unit Inconsistency type 3: NO: µg m-3, NO2: ppb, NOx: µg m-3')
print('Unit Inconsistency type 4: NO: both, NO2: µg m-3, NOx: both')
'''

final_site_list = mean_df[mean_df['site_id'].isin(final_site_list['site_id'][final_site_list['pollutant'] == 'NO2'])]
final_site_list = final_site_list[final_site_list['score'].str.contains('red|blue|violet|green', regex=True, case=False, na=False)]

new_df = pd.DataFrame()
new_df['site_id'] = final_site_list['site_id']
new_df['site_name'] = final_site_list['site_name']
new_df['year'] = final_site_list['year']
new_df['Consistent Units'] = final_site_list['score'].str.contains('blue', regex=True, case=False)
new_df['Unit Inconsistency Type 1'] = final_site_list['score'].str.contains('red', regex=True, case=False)
new_df['Unit Inconsistency Type 3'] = final_site_list['score'].str.contains('violet', regex=True, case=False)
new_df['Unit Inconsistency Type 4'] = final_site_list['score'].str.contains('green', regex=True, case=False)

new_df['Consistent Units'] = new_df['Consistent Units'].replace({True:'✔', False:'✘'})
new_df['Unit Inconsistency Type 1'] = new_df['Unit Inconsistency Type 1'].replace({True:'✘', False:'✔'})
new_df['Unit Inconsistency Type 3'] = new_df['Unit Inconsistency Type 3'].replace({True:'✘', False:'✔'})
new_df['Unit Inconsistency Type 4'] = new_df['Unit Inconsistency Type 4'].replace({True:'✘', False:'✔'})

new_df.to_csv('Summary/summary_unit_inconsistency.csv', index=False)
