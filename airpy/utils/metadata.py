"""
Utilities for extracting metadata from filenames and handling site information.
This module provides backward compatibility while using the new FileProcessor class.
"""
from airpy.core.file_processor import FileProcessor

# Create a global instance of FileProcessor for backward compatibility
_file_processor = FileProcessor()


def get_all_metadata_from_sites_master(sites=None, site_id=None):
    """
    Load the sites_master.csv file and return its contents as a DataFrame.
    
    Args:
        sites: Deprecated parameter, kept for backward compatibility
        site_id: Site ID to look up
    
    Returns:
        str: JSON string containing site metadata
    """
    return _file_processor.get_all_metadata_from_sites_master(site_id)


def get_state(city: str):
    """
    Get the state name for a given city from the sites_master.csv file.
    
    Args:
        city (str): The name of the city (case-insensitive)
        
    Returns:
        str: The state name corresponding to the city, or None if not found
    """
    return _file_processor.get_state(city)


def get_siteId_Name_Year_City(file: str, sites=None):
    """
    Extracts site_id, site_name, year, and city from the filename based on its format.
    
    Args:
        file (str): The filename to extract information from.
        sites: Deprecated parameter, kept for backward compatibility

    Returns:
        tuple: (site_id, site_name, year, city, state)
    """
    return _file_processor.extract_metadata(file, live=False)


def get_siteId_Name_Year_City_LIVE(file: str, sites=None):
    """
    Extracts site_id, site_name, year, and city from a live data filename.
    
    Args:
        file (str): The filename to extract information from.
        sites: Deprecated parameter, kept for backward compatibility
    
    Returns:
        tuple: (site_id, site_name, year, city, state)
    """
    return _file_processor.extract_metadata(file, live=True) 