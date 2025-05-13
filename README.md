# AirPy Tool

A Python package for cleaning and processing air quality data.

## Installation

You can install AirPy from PyPI:

```bash
pip install airpy-tool
```

You can also install directly from GitHub:

```bash
pip install git+https://github.com/chandankr014/airpy-tool.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/chandankr014/airpy-tool.git
cd airpy-tool
pip install -e .
```

## Usage

### Command-line Interface

AirPy provides a command-line tool for processing air quality data:

```bash
# Process all data
airpy

# Process data for a specific city
airpy --city "Delhi"

# Process live data
airpy --live

# Specify custom directories
airpy --raw-dir /path/to/raw/data --clean-dir /path/to/output

# Process specific pollutants
airpy --pollutants PM25 PM10 NO2
```

### Python API

You can also use AirPy as a Python library:

```python
from airpy.core.processor import process_data

# Process data with default settings
process_data()

# Process data for a specific city
process_data(city="Delhi")

# Process live data
process_data(live=True)

# Specify custom directories
process_data(raw_dir="/path/to/raw/data", clean_dir="/path/to/output")

# Process specific pollutants
process_data(pollutants=["PM25", "PM10", "NO2"])
```

## Features

AirPy provides the following features for air quality data processing:

- Data cleaning and formatting
- Outlier detection and removal
- Consecutive repeat detection
- Unit inconsistency correction for nitrogen compounds
- Time series analysis and visualization

## Data Format

AirPy supports the following file formats:
- CSV files
- Excel (XLSX) files

The data should follow one of these filename formats:
- `15Min_YEAR_site_ID_STATION_CITY_ORG_15Min.csv`
- `Raw_data_15Min_YEAR_site_ID_STATION_CITY_ORG_15Min.csv`
- `site_ID_YEAR.csv`
- Live data format: `site_IDYYYYMMDDHHMMSS.xlsx`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 