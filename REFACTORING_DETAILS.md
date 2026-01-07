# AirPy Code Refactoring Summary

## Overview
This document summarizes the comprehensive refactoring of the AirPy air quality data processing tool to make it more flexible, modular, and robust in handling different file formats while maintaining all cleaning and standardization functionality.

## Key Changes Made

### 1. Created FileProcessor Class (`airpy/core/file_processor.py`)
- **Purpose**: Centralized, flexible file handling and metadata extraction
- **Features**:
  - Automatic filename format detection
  - Support for multiple filename patterns:
    - `site_5112_2024.csv` (Standard site format)
    - `15min_2020_site_5111_station_name.csv` (15-minute format)
    - `raw_data_something_2020_site_5111_station_name.csv` (Raw data format)
    - `site_5111202012251200000.csv` (Live format with timestamp)
    - `5112_2024.csv` (Numeric year format)
    - `station_name_5112_2024.csv` (Name ID year format)
    - Custom position-based parsing for unusual formats
  - Fallback metadata extraction for unknown formats
  - Robust error handling and graceful degradation

### 2. Introduced PollutantProcessor Class (`airpy/core/processor.py`)
- **Purpose**: Column-by-column pollutant processing with timestamp-based cleaning
- **Features**:
  - Individual pollutant processing for PM25, PM10, Ozone
  - Specialized nitrogen compound processing (NO, NO2, NOx) with unit standardization
  - Maintains original cleaning algorithms:
    - Consecutive repeat detection and removal
    - Outlier detection using IQR and MAD methods
    - Rolling average calculations
    - Unit inconsistency correction for nitrogen compounds
  - Preserves all cleaning and standardization logic

### 3. Refactored Metadata Handling (`airpy/utils/metadata.py`)
- **Backward Compatibility**: All existing functions maintained for compatibility
- **New Implementation**: Functions now use the FileProcessor class internally
- **Improved Robustness**: Better error handling and fallback mechanisms

### 4. Removed Plot Dependencies (`airpy/utils/cleaning.py`)
- **Removed**: All matplotlib imports and plotting code
- **Preserved**: All data cleaning and processing functionality
- **Updated**: Function signatures maintained for backward compatibility
- **Focus**: Pure data processing without visualization dependencies

### 5. Enhanced Main Processing Workflow
- **Column-by-Column Processing**: Pollutants are now processed individually with proper timestamp utilization
- **Nitrogen Compound Grouping**: NO, NO2, and NOx are processed together for unit standardization
- **Flexible File Detection**: Automatically handles various filename formats
- **Better Error Handling**: Continues processing other files if one fails
- **Progress Reporting**: Enhanced logging and progress feedback

## Technical Improvements

### Flexibility Enhancements
1. **Multiple Filename Format Support**: Handles various naming conventions automatically
2. **Extensible Architecture**: Easy to add new filename patterns
3. **Custom Position Parsing**: Supports custom site ID position specification
4. **Graceful Fallbacks**: Continues processing even with unknown file formats

### Robustness Improvements
1. **Error Isolation**: File processing errors don't stop the entire workflow
2. **Memory Management**: Improved garbage collection and memory cleanup
3. **Data Validation**: Better validation of input data and parameters
4. **State Preservation**: All cleaning and standardization algorithms preserved

### Code Organization
1. **Separation of Concerns**: File processing, metadata extraction, and data cleaning are now separate modules
2. **Class-Based Design**: Object-oriented approach for better maintainability
3. **Backward Compatibility**: Existing code continues to work without changes
4. **Modular Structure**: Each component can be used independently

## Key Features Preserved

### Data Cleaning Pipeline
- ✅ Consecutive repeat detection and removal
- ✅ Outlier detection using IQR and MAD methods
- ✅ Rolling average calculations for temporal smoothing
- ✅ Negative value handling and masking
- ✅ Gap interpolation with configurable limits

### Nitrogen Compound Processing
- ✅ Unit inconsistency detection and correction
- ✅ NO/NO2/NOx relationship validation
- ✅ Multiple conversion equation support (C1, C2, C4, C6)
- ✅ CPCB standard compliance checking
- ✅ Count mismatch detection

### Data Standardization
- ✅ Column name standardization
- ✅ Timestamp formatting and processing
- ✅ Site metadata integration
- ✅ City and state information lookup
- ✅ Year and location tagging

## Usage Examples

### Basic Processing
```python
from airpy.core.processor import process_data

process_data(
    raw_dir="path/to/raw/data",
    clean_dir="path/to/clean/data",
    pollutants=['PM25', 'PM10', 'NO', 'NO2', 'NOx', 'Ozone']
)
```

### City-Specific Processing
```python
process_data(
    city="Mumbai",
    raw_dir="path/to/raw/data",
    clean_dir="path/to/clean/data"
)
```

### Custom Site ID Position
```python
process_data(
    raw_dir="path/to/raw/data",
    clean_dir="path/to/clean/data",
    siteid_position=[2, 3]  # Site ID at positions 2-3 when split by underscore
)
```

### Live Data Processing
```python
process_data(
    live=True,
    raw_dir="path/to/live/data",
    clean_dir="path/to/clean/data"
)
```

## Benefits of Refactoring

1. **Improved Flexibility**: Handles various file formats without modification
2. **Better Maintainability**: Modular, class-based design
3. **Enhanced Robustness**: Graceful error handling and fallback mechanisms
4. **Preserved Functionality**: All cleaning and standardization algorithms maintained
5. **Backward Compatibility**: Existing code continues to work
6. **Scalability**: Easy to extend with new filename patterns and processing methods
7. **Focus on Core Functionality**: Removed plotting dependencies for cleaner data processing

## Testing
The refactored code has been thoroughly tested with:
- Various filename formats
- Different pollutant combinations
- Nitrogen compound processing
- Backward compatibility verification
- Error handling scenarios

All tests pass successfully, confirming that the refactoring maintains the original functionality while adding significant improvements in flexibility and robustness.

## Future Enhancements
The new architecture makes it easy to add:
- New filename format patterns
- Additional pollutant processing methods
- Enhanced validation rules
- Custom cleaning algorithms
- Integration with different data sources

The refactored codebase provides a solid foundation for future enhancements while maintaining the high-quality data processing capabilities of the original AirPy tool.