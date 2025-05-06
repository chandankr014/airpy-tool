# AirPy - Air Quality Data Processing Tool

## What is this?
AirPy is a tool that helps process and clean air quality data from monitoring stations. It takes raw air quality measurements and makes them more reliable and easier to understand.

## What does it do?
- Cleans and organizes air quality data from monitoring stations
- Checks for and fixes common data problems
- Creates helpful visualizations and reports
- Processes multiple air pollutants including:
  - PM2.5 and PM10 (particulate matter)
  - NOx, NO2, NO (nitrogen compounds)
  - Ozone
  - And more

## How to Use AirPy

### Method 1: Direct Run (Python Script)
```bash
# Run directly as a Python script
python airpy.py --city mumbai
python airpy.py --pollutants PM25 PM10 NO2
python airpy.py --raw-dir /path/to/data --clean-dir /path/to/output
```

### Method 2: After Installation
```bash
# Install the package
pip install -e .

# Run as a command-line tool
airpy --city pune
airpy --pollutants PM25 PM10 NO2
```

### Method 3: Python Import
```python
# Import into your own Python script
from airpy import process_data

# Process data for a specific city
process_data(city="mumbai")

# Process specific pollutants
process_data(pollutants=["PM25", "PM10", "NO2"])
```

## Command Line Options
- `--city`: Specify city name to process (e.g., "mumbai", "pune")
- `--pollutants`: List of pollutants to process (default: PM25 PM10 NO NO2 NOx)
- `--raw-dir`: Path to raw data directory (default: "data/raw")
- `--clean-dir`: Path to output clean data (default: "data/clean")
- `--live`: Process live data (flag, no value needed)

## Project Structure
- `airpy.py` - Main processing script
- `data/` - Contains raw and processed data
- `files/` - Configuration and reference files
- `scripts/` - Processing tools and utilities

## Requirements
- Python 3.6+
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - and others

## Support
If you encounter any issues or need help while using AirPy, please check the error logs in `data_processing.log`. 