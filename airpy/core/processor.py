"""
Core data processing functionality for AirPy.
"""
import os 
import pandas as pd
import numpy as np
import gc
from pathlib import Path
from typing import List, Optional, Union
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

# IMPORT CUSTOM MODULES
from airpy.utils.formatting import get_formatted_df
from airpy.utils.cleaning import group_plot, NO_count_mismatch, correct_unit_inconsistency
from airpy.core.file_processor import FileProcessor


# -----------------------------------------------------------------------------
# Debug/Verbose logging helper
# -----------------------------------------------------------------------------
class Logger:
    """Simple logger with verbose control for debug-friendly output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def info(self, message: str):
        """Always print info messages."""
        print(f"[INFO] {message}")
    
    def debug(self, message: str):
        """Print debug messages only when verbose is True."""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def success(self, message: str):
        """Print success messages in green."""
        print(f'\033[92m[SUCCESS] {message}\033[0m')
    
    def warning(self, message: str):
        """Print warning messages in yellow."""
        print(f'\033[93m[WARNING] {message}\033[0m')
    
    def error(self, message: str):
        """Print error messages in red."""
        print(f'\033[91m[ERROR] {message}\033[0m')


# Global logger instance (can be configured)
_logger = Logger(verbose=False)

class PollutantProcessor:
    """
    A class to handle column-by-column processing of pollutants with timestamp-based cleaning.
    """
    
    def __init__(self):
        self.nitrogen_compounds = ['NO', 'NO2', 'NOx']
        self.individual_pollutants = ['PM25', 'PM10', 'Ozone']
    
    def process_individual_pollutant(self, df: pd.DataFrame, pollutant: str, site_name: str, year: str) -> pd.DataFrame:
        """
        Process a single pollutant column with cleaning and standardization.
        
        Args:
            df: DataFrame containing the pollutant data
            pollutant: Name of the pollutant column
            site_name: Name of the monitoring site
            year: Year of the data
            
        Returns:
            DataFrame with processed pollutant data
        """
        if pollutant not in df.columns:
            _logger.debug(f"Pollutant {pollutant} not found in data")
            return df
            
        if len(df[pollutant].value_counts()) == 0:
            _logger.debug(f"No available {pollutant} data")
            return df
        
        _logger.debug(f"Processing {pollutant} for {site_name}")
        
        # STEP 1: GROUP AND CLEAN DATA (CONSECUTIVE AND OUTLIERS)
        df = group_plot(df, pollutant, pollutant, site_name, f"{site_name}_{year}")
        
        # STEP 2: CALCULATE ROLLING AVERAGE
        df[pollutant + '_hourly'] = df.groupby("site_id")[pollutant].rolling(
            window=4, min_periods=1).mean().values

        # STEP 3: CLEAN OUTLIERS BASED ON ROLLING AVERAGE
        df[pollutant + '_clean'] = df[pollutant + '_outliers']
        mask = df[pollutant + '_hourly'] < 0
        df.loc[mask, pollutant + '_clean'] = np.nan

        # STEP 4: REMOVE TEMPORARY COLUMNS
        df.drop(columns=[f"{pollutant}_hourly"], inplace=True)
        
        _logger.debug(f"Successfully cleaned {pollutant} for {site_name}")
        return df
    
    def process_nitrogen_compounds(self, df: pd.DataFrame, site_name: str, year: str) -> pd.DataFrame:
        """
        Process NO, NO2, and NOx together for unit standardization and cleaning.
        
        Args:
            df: DataFrame containing nitrogen compound data
            site_name: Name of the monitoring site
            year: Year of the data
            
        Returns:
            DataFrame with processed nitrogen compound data
        """
        # Check if we have any nitrogen compound data
        has_nitrogen_data = any(
            pollutant in df.columns and not df[pollutant].isnull().all() 
            for pollutant in self.nitrogen_compounds
        )
        
        if not has_nitrogen_data:
            _logger.debug("No available nitrogen compound data (NOx, NO2, NO)")
            return df
        
        _logger.debug(f"Processing nitrogen compounds for {site_name}")
        
        # Process each nitrogen compound individually first
        for pollutant in self.nitrogen_compounds:
            if pollutant in df.columns and not df[pollutant].isnull().all():
                df = self.process_individual_pollutant(df, pollutant, site_name, year)
        
        # CHECK AND FIX UNIT INCONSISTENCIES FOR NITROGEN COMPOUNDS
        if (df['NOx'].isnull().all() or df['NO2'].isnull().all() or df['NO'].isnull().all()):
            _logger.debug("Insufficient nitrogen compound data for unit consistency check")
        else:
            _logger.debug(f"Checking unit inconsistencies for nitrogen compounds at {site_name}")
            df = correct_unit_inconsistency(df, f"{site_name}_{year}", False)
        
        # CHECK FOR NO/NOx/NO2 COUNT MISMATCHES
        df = NO_count_mismatch(df)
        
        return df
    
    def process_all_pollutants(self, df: pd.DataFrame, pollutants: List[str], site_name: str, year: str) -> pd.DataFrame:
        """
        Process all pollutants in a column-by-column manner.
        
        Args:
            df: DataFrame containing pollutant data
            pollutants: List of pollutants to process
            site_name: Name of the monitoring site
            year: Year of the data
            
        Returns:
            DataFrame with all processed pollutants
        """
        # Separate nitrogen compounds from other pollutants
        nitrogen_pollutants = [p for p in pollutants if p in self.nitrogen_compounds]
        other_pollutants = [p for p in pollutants if p not in self.nitrogen_compounds]
        
        # Process individual pollutants first
        for pollutant in other_pollutants:
            df = self.process_individual_pollutant(df, pollutant, site_name, year)
        
        # Process nitrogen compounds together if any are present
        if nitrogen_pollutants:
            df = self.process_nitrogen_compounds(df, site_name, year)
        
        return df


def process_data(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    city: Optional[str] = None,
    live: bool = False,
    raw_dir: Optional[str] = None,
    clean_dir: Optional[str] = None,
    pollutants: Optional[List[str]] = None,
    siteid_position: Optional[List[int]] = None,
    verbose: bool = False,
    overwrite: bool = False
) -> Optional[pd.DataFrame]:
    """
    Processes air quality data by reading raw data files, cleaning them, and saving the results.
    
    Supports both single file and folder (batch) processing modes.

    Parameters:
    -----------
    input_path : str, optional
        Path to a single input file OR a directory containing raw data files.
        This is the preferred parameter - use this instead of raw_dir.
    output_path : str, optional
        Path to output file (for single file mode) OR directory (for batch mode).
        This is the preferred parameter - use this instead of clean_dir.
    city : str, optional
        The name of the city for which the air quality data should be processed.
        If not specified, data for all available cities will be processed.
    live : bool, default=False
        A flag indicating whether to process live data format filenames.
    raw_dir : str, optional
        [DEPRECATED] Use input_path instead. Directory containing raw data files.
    clean_dir : str, optional
        [DEPRECATED] Use output_path instead. Directory to save cleaned data.
    pollutants : list, optional
        A list of pollutants to process. Default: ['PM25', 'PM10', 'NO', 'NO2', 'NOx', 'Ozone']
    siteid_position : list, optional
        [start_index, end_index] for custom site ID position in filename when split by '_'.
    verbose : bool, default=False
        Enable verbose/debug output for troubleshooting.
    overwrite : bool, default=False
        If True, overwrite existing output files. If False, skip files that already exist.

    Returns:
    --------
    pd.DataFrame or None
        Returns the cleaned DataFrame when processing a single file.
        Returns None when processing a folder (files are saved to disk).

    Examples:
    ---------
    # Process a single file
    df = process_data(input_path="data/raw/site_5112_2024.csv", output_path="data/clean/")
    
    # Process a folder
    process_data(input_path="data/raw/", output_path="data/clean/")
    
    # Process with verbose output
    process_data(input_path="data/raw/", output_path="data/clean/", verbose=True)
    
    # Process specific pollutants only
    process_data(input_path="data/raw/", output_path="data/clean/", pollutants=['PM25', 'PM10'])
    """
    global _logger
    _logger = Logger(verbose=verbose)
    
    # Handle backward compatibility: raw_dir/clean_dir -> input_path/output_path
    if input_path is None and raw_dir is not None:
        input_path = raw_dir
        _logger.debug("Using raw_dir parameter (deprecated, use input_path instead)")
    if output_path is None and clean_dir is not None:
        output_path = clean_dir
        _logger.debug("Using clean_dir parameter (deprecated, use output_path instead)")
    
    # Validate required parameters
    if input_path is None:
        raise ValueError("input_path (or raw_dir) must be specified. Example: input_path='data/raw/'")
    if output_path is None:
        raise ValueError("output_path (or clean_dir) must be specified. Example: output_path='data/clean/'")
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Determine if single file or folder mode
    is_single_file = input_path.is_file()
    
    if is_single_file:
        _logger.info(f"Single file mode: {input_path.name}")
        return _process_single_file(
            input_file=input_path,
            output_path=output_path,
            pollutants=pollutants,
            siteid_position=siteid_position,
            live=live,
            overwrite=overwrite
        )
    else:
        _logger.info(f"Batch mode: Processing folder {input_path}")
        return _process_folder(
            input_dir=input_path,
            output_dir=output_path,
            city=city,
            pollutants=pollutants,
            siteid_position=siteid_position,
            live=live,
            overwrite=overwrite
        )
def _process_single_file(
    input_file: Path,
    output_path: Path,
    pollutants: Optional[List[str]] = None,
    siteid_position: Optional[List[int]] = None,
    live: bool = False,
    overwrite: bool = False
) -> pd.DataFrame:
    """
    Process a single air quality data file.
    
    Args:
        input_file: Path to the input file
        output_path: Path to output file or directory
        pollutants: List of pollutants to process
        siteid_position: Custom site ID position in filename
        live: Whether this is live data format
        overwrite: Whether to overwrite existing output
        
    Returns:
        pd.DataFrame: The cleaned DataFrame
    """
    file_processor = FileProcessor()
    pollutant_processor = PollutantProcessor()
    
    # Set default pollutants
    if pollutants is None:
        pollutants = ['PM25', 'PM10', 'NO', 'NO2', 'NOx', 'Ozone']
    
    _logger.debug(f"Processing file: {input_file}")
    _logger.debug(f"Pollutants to process: {pollutants}")
    
    # Validate input file
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not file_processor.is_supported_file(input_file.name):
        raise ValueError(f"Unsupported file format: {input_file.suffix}. Supported: .csv, .xlsx, .xls, .txt")
    
    # Extract metadata from filename
    try:
        site_id, site_name, year, city_name, state = file_processor.extract_metadata(
            input_file.name, siteid_position=siteid_position, live=live
        )
        _logger.debug(f"Extracted: site_id={site_id}, year={year}, city={city_name}, state={state}")
    except Exception as e:
        _logger.error(f"Failed to extract metadata from filename: {e}")
        raise
    
    # Determine output file path
    if output_path.is_dir() or not output_path.suffix:
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{site_id}_{year}{input_file.suffix}"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_file = output_path
    
    # Check if output exists
    if output_file.exists() and not overwrite:
        _logger.warning(f"Output file exists, skipping (use overwrite=True to replace): {output_file}")
        return pd.read_csv(output_file) if output_file.suffix == '.csv' else pd.read_excel(output_file)
    
    # Read and format the dataframe
    try:
        df = get_formatted_df(str(input_file))
        _logger.debug(f"Loaded dataframe with shape: {df.shape}")
    except Exception as e:
        _logger.error(f"Failed to read file: {e}")
        raise
    
    # Remove duplicate indices
    df = df.loc[~df.index.duplicated(keep='first')]
    
    # Prepare dataframe for processing
    local_df = df.copy()
    local_df['date'] = pd.to_datetime(local_df['Timestamp']).dt.date
    local_df['site_id'] = site_id
    local_df['site_name'] = site_name
    local_df['city'] = city_name
    local_df['state'] = state
    
    # Process all pollutants
    _logger.info(f"Processing pollutants for {site_name} ({year})")
    local_df = pollutant_processor.process_all_pollutants(local_df, pollutants, site_name, str(year))
    
    # Cleanup dataframe
    local_df = _cleanup_dataframe(local_df, year)
    
    # Save the processed data
    _save_dataframe(local_df, output_file, input_file.suffix)
    _logger.success(f"Saved: {output_file.name}")
    
    return local_df


def _process_folder(
    input_dir: Path,
    output_dir: Path,
    city: Optional[str] = None,
    pollutants: Optional[List[str]] = None,
    siteid_position: Optional[List[int]] = None,
    live: bool = False,
    overwrite: bool = False
) -> None:
    """
    Process all air quality data files in a folder.
    
    Args:
        input_dir: Path to the input directory
        output_dir: Path to the output directory
        city: Filter by city name (optional)
        pollutants: List of pollutants to process
        siteid_position: Custom site ID position in filename
        live: Whether this is live data format
        overwrite: Whether to overwrite existing output files
    """
    file_processor = FileProcessor()
    pollutant_processor = PollutantProcessor()
    
    # Validate input directory
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set default pollutants
    if pollutants is None:
        pollutants = ['PM25', 'PM10', 'NO', 'NO2', 'NOx', 'Ozone']
    
    _logger.debug(f"Input directory: {input_dir}")
    _logger.debug(f"Output directory: {output_dir}")
    _logger.debug(f"Pollutants: {pollutants}")
    
    # Get all supported files
    files = [f for f in os.listdir(input_dir) if file_processor.is_supported_file(f)]
    
    if not files:
        _logger.warning(f"No supported files found in {input_dir}")
        _logger.info("Supported formats: .csv, .xlsx, .xls, .txt")
        return
    
    _logger.info(f"Found {len(files)} files to process")
    
    # Normalize city filter
    city_filter = city.lower() if city else None
    if city_filter:
        _logger.info(f"Filtering by city: {city}")
    
    # Track statistics
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Process each file
    for idx, file in enumerate(files, 1):
        try:
            gc.collect()  # Memory cleanup
            
            filepath = input_dir / file
            _logger.info(f"[{idx}/{len(files)}] Processing: {file}")
            
            # Extract metadata
            try:
                site_id, site_name, year, city_name, state = file_processor.extract_metadata(
                    file, siteid_position=siteid_position, live=live
                )
            except Exception as e:
                _logger.error(f"Failed to extract metadata from {file}: {e}")
                error_count += 1
                continue
            
            # Apply city filter
            if city_filter and city_name.lower() != city_filter:
                _logger.debug(f"Skipping {file} - city '{city_name}' doesn't match filter '{city}'")
                skipped_count += 1
                continue
            
            # Determine output file
            output_file = output_dir / f"{site_id}_{year}{filepath.suffix}"
            
            # Check if output exists
            if output_file.exists() and not overwrite:
                _logger.debug(f"Output exists, skipping: {output_file.name}")
                skipped_count += 1
                continue
            
            # Read and process the file
            try:
                df = get_formatted_df(str(filepath))
            except Exception as e:
                _logger.error(f"Failed to read {file}: {e}")
                error_count += 1
                continue
            
            # Remove duplicate indices
            df = df.loc[~df.index.duplicated(keep='first')]
            
            # Prepare dataframe
            local_df = df.copy()
            local_df['date'] = pd.to_datetime(local_df['Timestamp']).dt.date
            local_df['site_id'] = site_id
            local_df['site_name'] = site_name
            local_df['city'] = city_name
            local_df['state'] = state
            
            # Process pollutants
            local_df = pollutant_processor.process_all_pollutants(local_df, pollutants, site_name, str(year))
            
            # Cleanup and save
            local_df = _cleanup_dataframe(local_df, year)
            _save_dataframe(local_df, output_file, filepath.suffix)
            
            _logger.success(f"Saved: {site_id}_{year}")
            processed_count += 1
            
        except Exception as e:
            _logger.error(f"Error processing {file}: {e}")
            error_count += 1
            continue
    
    # Print summary
    _logger.info("=" * 50)
    _logger.info(f"Processing complete!")
    _logger.info(f"  Processed: {processed_count}")
    _logger.info(f"  Skipped: {skipped_count}")
    _logger.info(f"  Errors: {error_count}")
    _logger.info(f"  Total: {len(files)}")


def _cleanup_dataframe(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Clean up the processed dataframe by removing temporary columns and reordering.
    
    Args:
        df: DataFrame to clean up
        year: Year to add as column
        
    Returns:
        Cleaned DataFrame
    """
    # Remove intermediate processing columns
    df = df[df.columns.drop(list(df.filter(regex='_int')))]
    df = df[df.columns.drop(list(df.filter(regex='(?<!_)consecutives')))]
    
    # Drop unused columns
    columns_to_drop = [
        't', 'std', 'med', 'med_2', 'mad', 'date', 'ratio',
        'Benzene', 'Toluene', 'Xylene', 'O Xylene', 'Eth-Benzene', 'MP-Xylene',
        'AT', 'RH', 'WS', 'WD', 'RF', 'TOT-RF', 'SR', 'BP', 'VWS'
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    # Reorder columns: basic info first
    basic_columns = ['Timestamp', 'site_id', 'city', 'state']
    other_columns = [col for col in df.columns if col not in basic_columns + ['dates', 'year']]
    df = df[basic_columns + other_columns]
    
    # Add year column
    df['year'] = year
    
    return df


def _save_dataframe(df: pd.DataFrame, output_file: Path, suffix: str) -> None:
    """
    Save the dataframe to the specified file.
    
    Args:
        df: DataFrame to save
        output_file: Path to output file
        suffix: File extension (.csv or .xlsx)
    """
    if suffix.lower() == '.csv':
        df.to_csv(output_file, index=False)
    elif suffix.lower() in ('.xlsx', '.xls'):
        # Handle Excel-specific column cleanup
        df_excel = df.copy()
        df_excel.drop(columns=['To Date', 'Timestamp'], inplace=True, errors='ignore')
        df_excel.rename(columns={'From Date': 'Timestamp'}, inplace=True)
        df_excel.to_excel(output_file, index=False)
    else:
        # Default to CSV
        df.to_csv(output_file.with_suffix('.csv'), index=False) 