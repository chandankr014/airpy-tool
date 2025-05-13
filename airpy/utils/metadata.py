"""
Utilities for extracting metadata from filenames and handling site information.
"""
import re
import pandas as pd


def get_siteId_Name_Year_City(file: str, sites: list):
    """
    Extracts site_id, site_name, year, and city from the filename based on its format.
    
    Args:
    - file (str): The filename to extract information from.
    - sites (list): A list or DataFrame containing site details, including 'site_code' and 'city'.

    Returns:
    - tuple: (site_id, site_name, year, city)
    """
    
    if file.lower().startswith("15min"):
        parts = file.split('_')
        year = int(parts[1])                 # Year is the second part
        site_id = '_'.join(parts[2:4])       # Site ID is the third and fourth parts
        site_name = '_'.join(parts[4:-1]).replace(".csv", "")  # Site name is between the 5th element and the end minus .csv
        
    elif file.lower().startswith("raw_data"):
        parts = file.split('_')
        year = int(parts[3])                 # Year is the fourth part
        site_id = '_'.join(parts[4:6])       # Site ID is the fifth and sixth parts
        site_name = '_'.join(parts[6:-1]).replace(".csv", "")  # Site name starts from the seventh part

    elif file.lower().startswith("site_"):
        # Simple format: site_5112_2024.csv
        parts = file.split('_')
        if len(parts) >= 3:
            site_id = '_'.join(parts[0:2])   # Site ID is "site_5112"
            year_part = parts[2].split('.')[0]  # Extract "2024" from "2024.csv"
            try:
                year = int(year_part)
                site_name = parts[1]  # Use site numeric ID as site name if no better name available
            except ValueError:
                # If the year part isn't a number, handle the error
                raise ValueError(f"Could not extract year from filename: {file}")
        else:
            raise ValueError(f"Filename doesn't have enough parts: {file}")

    else:
        raise ValueError("Filename format is not recognized")

    city_data = sites[sites['site_code'] == site_id]['city']
    if not city_data.empty:
        city = city_data.values[0].strip()  # Extract and strip whitespace from city name
    else:
        city = "Unknown"  # Handle cases where site_id is not found in the sites DataFrame

    print(f"SITE ID: {site_id} - SITENAME: {site_name} - YEAR: {year} - CITY: {city}")
    return site_id, site_name, year, city


def get_siteId_Name_Year_City_LIVE(file, sites):
    """
    Extracts site_id, site_name, year, and city from a live data filename.
    
    Args:
    - file (str): The filename to extract information from.
    - sites (list): A list or DataFrame containing site details.
    
    Returns:
    - tuple: (site_id, site_name, year, city)
    """
    try:
        # Extract the numerical part after "site_"
        match = re.search(r'site_(\d+)(\d{4})(\d{2})(\d{2})(\d{6})', file)
        if not match:
            raise ValueError("Invalid filename format")

        site_id = match.group(1)    # Extract variable-length site ID
        year = int(match.group(2))  # Extract 4-digit year
        month = int(match.group(3)) # Extract 2-digit month
        day = int(match.group(4))   # Extract 2-digit day
        time = match.group(5)       # Extract HHMMSS time

        # Fetch city based on site_id
        city = sites[sites['site_code'] == 'site_'+site_id]['city'].values
        city = city[0].strip() if len(city) > 0 else "Unknown"

        print(f"SITE ID: {site_id} - YEAR: {year} - MONTH: {month} - DAY: {day} - TIME: {time} - CITY: {city}")
        return site_id, site_id, year, city

    except Exception as e:
        print(f"Error parsing filename '{file}': {e}")
        return None 