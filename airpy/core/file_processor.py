"""
File processing and metadata extraction utilities for AirPy.
This module provides a unified interface for handling different file formats and structures.
"""
import re
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional, Union, List

# Use importlib.resources instead of deprecated pkg_resources
try:
    from importlib.resources import files as importlib_files
    from importlib.resources import as_file
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files as importlib_files
    from importlib_resources import as_file


class FileProcessor:
    """
    A unified class for handling file processing, metadata extraction, and file format detection.
    This class provides flexible methods to handle various filename structures and formats.
    """
    
    def __init__(self):
        """Initialize the FileProcessor with sites data."""
        self.sites = self._load_sites_data()
        self.supported_extensions = ('.xlsx', '.csv', '.xls', '.txt')
        
    def _load_sites_data(self) -> pd.DataFrame:
        """
        Load the sites_master.csv file from the package.
        
        Returns:
            pd.DataFrame: DataFrame containing site metadata.
        """
        try:
            # Use importlib.resources (modern approach)
            data_ref = importlib_files('airpy').joinpath('data', 'sites_master.csv')
            with as_file(data_ref) as sites_file:
                if sites_file.exists():
                    return pd.read_csv(sites_file)
                else:
                    raise FileNotFoundError("Could not find sites_master.csv file")
        except Exception as e:
            print(f"[DEBUG] Error loading sites_master.csv: {e}")
            # Fallback: try relative path from module location
            try:
                module_dir = Path(__file__).parent.parent
                sites_file = module_dir / 'data' / 'sites_master.csv'
                if sites_file.exists():
                    return pd.read_csv(sites_file)
            except Exception:
                pass
            return pd.DataFrame()
    
    def get_state(self, city: str) -> Optional[str]:
        """
        Get the state name for a given city from the sites_master.csv file.
        
        Args:
            city (str): The name of the city (case-insensitive)
            
        Returns:
            str: The state name corresponding to the city, or None if not found
        """
        if city == "unknown" or city is None:
            return None
        
        try:
            city = city.lower()
            sites_lower = self.sites.copy()
            sites_lower['city_lower'] = sites_lower['city'].str.lower()
            
            matching_row = sites_lower[sites_lower['city_lower'] == city]
            if matching_row.empty:
                print(f"No state found for city: {city}")
                return None
            else:
                return matching_row.iloc[0]['stateID']
                
        except Exception as e:
            print(f"Error fetching state for {city}: {str(e)}")
            return None
    
    def get_all_metadata_from_sites_master(self, site_id: str = None) -> Optional[Union[str, Dict]]:
        """
        Get metadata for a specific site from sites_master.csv.
        
        Args:
            site_id (str): The site ID to look up
            
        Returns:
            Union[str, Dict]: JSON string of site data or None if not found
        """
        if site_id is None:
            return None
            
        try:
            site_data = self.sites[self.sites['site_code'] == site_id]
            if site_data.empty:
                print(f"No data found for site_id: {site_id}")
                return None
            else:
                return site_data.to_json(orient='records')
        except Exception as e:
            print(f"Error loading sites data for {site_id}: {str(e)}")
            return None
    
    def detect_filename_format(self, filename: str) -> str:
        """
        Detect the format of the filename to determine the appropriate parsing method.
        
        Args:
            filename (str): The filename to analyze
            
        Returns:
            str: The detected format type
        """
        filename_lower = filename.lower()
        
        if filename_lower.startswith("15min"):
            return "15min_format"
        elif filename_lower.startswith("raw_data"):
            return "raw_data_format"
        elif re.match(r'site_\d+\d{4}\d{2}\d{2}\d{6}', filename_lower):
            return "live_format"
        elif filename_lower.startswith("site_") and "_" in filename:
            return "site_format"
        elif re.match(r'\d+_\d{4}', filename):
            return "numeric_year_format"
        elif re.match(r'[a-zA-Z]+_\d+_\d{4}', filename):
            return "name_id_year_format"
        else:
            return "unknown_format"
    
    def parse_15min_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse 15min format: 15min_2020_site_5111_station_name.csv
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            year = int(parts[1])
            site_id = '_'.join(parts[2:4])
            site_name = '_'.join(parts[4:]).replace(".csv", "").replace(".xlsx", "")
            
            city, state = self._get_city_state_from_site_id(site_id)
            return site_id, site_name, year, city, state
        except Exception as e:
            print(f"Error parsing 15min format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_raw_data_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse raw_data format: raw_data_something_2020_site_5111_station_name.csv
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            year = int(parts[3])
            site_id = '_'.join(parts[4:6])
            site_name = '_'.join(parts[6:]).replace(".csv", "").replace(".xlsx", "")
            
            city, state = self._get_city_state_from_site_id(site_id)
            return site_id, site_name, year, city, state
        except Exception as e:
            print(f"Error parsing raw_data format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_site_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse site format: site_5112_2024.csv
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            if len(parts) >= 3:
                site_id = '_'.join(parts[0:2])
                year_part = parts[2].split('.')[0]
                year = int(year_part)
                site_name = parts[1]
                
                city, state = self._get_city_state_from_site_id(site_id)
                return site_id, site_name, year, city, state
            else:
                raise ValueError(f"Insufficient parts in filename: {filename}")
        except Exception as e:
            print(f"Error parsing site format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_live_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse live format: site_5111202012251200000.csv (site_ID + YYYYMMDDHHMMSS)
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            match = re.search(r'site_(\d+)(\d{4})(\d{2})(\d{2})(\d{6})', filename)
            if not match:
                raise ValueError("Invalid live filename format")

            site_numeric_id = match.group(1)
            year = int(match.group(2))
            month = int(match.group(3))
            day = int(match.group(4))
            time = match.group(5)

            site_id = f"site_{site_numeric_id}"
            site_name = site_numeric_id
            
            city, state = self._get_city_state_from_site_id(site_id)
            
            # print(f"[DEBUG] LIVE FORMAT - SITE ID: {site_id} - YEAR: {year} - CITY: {city}")
            return site_id, site_name, year, city, state
        except Exception as e:
            print(f"Error parsing live format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_numeric_year_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse numeric year format: 5112_2024.csv
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            site_numeric_id = parts[0]
            year = int(parts[1].split('.')[0])
            
            site_id = f"site_{site_numeric_id}"
            site_name = site_numeric_id
            
            city, state = self._get_city_state_from_site_id(site_id)
            return site_id, site_name, year, city, state
        except Exception as e:
            print(f"Error parsing numeric year format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_name_id_year_format(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Parse name ID year format: station_name_5112_2024.csv
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            if len(parts) >= 3:
                # Find the numeric site ID and year
                site_numeric_id = None
                year = None
                site_name_parts = []
                
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2100:
                        # This is likely the year
                        year = int(part)
                        if i > 0 and parts[i-1].isdigit():
                            site_numeric_id = parts[i-1]
                            site_name_parts = parts[:i-1]
                        break
                
                if site_numeric_id and year:
                    site_id = f"site_{site_numeric_id}"
                    site_name = '_'.join(site_name_parts) if site_name_parts else site_numeric_id
                    
                    city, state = self._get_city_state_from_site_id(site_id)
                    return site_id, site_name, year, city, state
                else:
                    raise ValueError("Could not extract site ID and year")
            else:
                raise ValueError(f"Insufficient parts in filename: {filename}")
        except Exception as e:
            print(f"Error parsing name ID year format '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def parse_custom_position(self, filename: str, siteid_position: List[int]) -> Tuple[str, str, int, str, str]:
        """
        Parse filename using custom site ID position specification.
        
        Args:
            filename (str): The filename to parse
            siteid_position (List[int]): [start_index, end_index] for site ID extraction
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            parts = filename.split('_')
            year = int(parts[-1].split('.')[0])
            site_id = '_'.join(parts[siteid_position[0]:siteid_position[1]+1])
            
            # Try to get metadata from sites master
            result = self.get_all_metadata_from_sites_master(site_id)
            
            if result:
                import json
                site_data = json.loads(result)[0]
                site_name = site_data.get('name', site_id)
                city = site_data.get('city', 'Unknown')
                state = site_data.get('state', self.get_state(city))
            else:
                site_name = site_id
                city, state = self._get_city_state_from_site_id(site_id)
            
            return site_id, site_name, year, city, state
        except Exception as e:
            print(f"Error parsing custom position '{filename}': {e}")
            return self._create_fallback_metadata(filename)
    
    def _get_city_state_from_site_id(self, site_id: str) -> Tuple[str, str]:
        """
        Get city and state from site ID using sites master data.
        
        Args:
            site_id (str): The site ID to look up
            
        Returns:
            Tuple: (city, state)
        """
        try:
            city_data = self.sites[self.sites['site_code'] == site_id]['city']
            if not city_data.empty:
                city = city_data.values[0].strip()
                state = self.get_state(city)
                return city, state
            else:
                return "Unknown", None
        except Exception as e:
            print(f"Error getting city/state for site_id {site_id}: {e}")
            return "Unknown", None
    
    def _create_fallback_metadata(self, filename: str) -> Tuple[str, str, int, str, str]:
        """
        Create fallback metadata when parsing fails.
        
        Args:
            filename (str): The original filename
            
        Returns:
            Tuple: (site_id, site_name, year, city, state) with fallback values
        """
        # Try to extract year from anywhere in filename
        year_match = re.search(r'(19|20)\d{2}', filename)
        year = int(year_match.group()) if year_match else 2020
        
        # Use filename without extension as site_id
        site_id = filename.split('.')[0]
        site_name = site_id
        city = "Unknown"
        state = None
        
        print(f"Using fallback metadata for {filename}: {site_id}, {site_name}, {year}, {city}, {state}")
        return site_id, site_name, year, city, state
    
    def extract_metadata(self, filename: str, siteid_position: Optional[List[int]] = None, live: bool = False) -> Tuple[str, str, int, str, str]:
        """
        Main method to extract metadata from filename using appropriate parser.
        
        Args:
            filename (str): The filename to parse
            siteid_position (Optional[List[int]]): Custom position for site ID extraction
            live (bool): Whether this is live data
            
        Returns:
            Tuple: (site_id, site_name, year, city, state)
        """
        try:
            # If custom position is provided, use it
            if siteid_position:
                return self.parse_custom_position(filename, siteid_position)
            
            # If live flag is set, try live format first
            if live:
                format_type = self.detect_filename_format(filename)
                if format_type == "live_format":
                    return self.parse_live_format(filename)
            
            # Detect format and use appropriate parser
            format_type = self.detect_filename_format(filename)
            
            parser_map = {
                "15min_format": self.parse_15min_format,
                "raw_data_format": self.parse_raw_data_format,
                "site_format": self.parse_site_format,
                "live_format": self.parse_live_format,
                "numeric_year_format": self.parse_numeric_year_format,
                "name_id_year_format": self.parse_name_id_year_format,
            }
            
            parser = parser_map.get(format_type)
            if parser:
                result = parser(filename)
                # print(f"[DEBUG] EXTRACTED: site_id={result[0]}, year={result[2]}, city={result[3]}")
                return result
            else:
                # print(f"[DEBUG] Unknown format detected for {filename}, using fallback")
                return self._create_fallback_metadata(filename)
                
        except Exception as e:
            print(f"Error extracting metadata from {filename}: {e}")
            return self._create_fallback_metadata(filename)
    
    def is_supported_file(self, filename: str) -> bool:
        """
        Check if the file has a supported extension.
        
        Args:
            filename (str): The filename to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return filename.lower().endswith(self.supported_extensions)
    
    def filter_files_by_extension(self, files: List[str]) -> List[str]:
        """
        Filter a list of files to only include supported extensions.
        
        Args:
            files (List[str]): List of filenames to filter
            
        Returns:
            List[str]: Filtered list of supported files
        """
        return [f for f in files if self.is_supported_file(f)]