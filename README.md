# AirPy Tool

A Python package for cleaning and processing CPCB (Central Pollution Control Board) air quality data for official government and research use.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Flexible Input**: Process single files or entire directories
- **Multiple Formats**: Supports CSV and Excel (XLSX/XLS) files
- **Auto-detection**: Automatically detects filename format and extracts metadata
- **Data Cleaning**: Removes outliers, consecutive repeats, and corrects unit inconsistencies
- **Unit Standardization**: Converts all nitrogen compounds to µg/m³
- **Debug-friendly**: Verbose mode for troubleshooting

## Installation

### From PyPI
```bash
pip install airpy-tool
```

### From GitHub
```bash
pip install git+https://github.com/chandankr014/airpy-tool.git
```

### Local Development
```bash
git clone https://github.com/chandankr014/airpy-tool.git
cd airpy-tool
pip install -e .
```

## Quick Start

### Command Line (CLI)

```bash
# Process a single file
airpy --input data/raw/site_5112_2024.csv --output data/clean/

# Process all files in a folder
airpy --input data/raw/ --output data/clean/

# With verbose output for debugging
airpy --input data/raw/ --output data/clean/ --verbose

# Process specific pollutants only
airpy --input data/raw/ --output data/clean/ --pollutants PM25 PM10

# Filter by city
airpy --input data/raw/ --output data/clean/ --city Delhi

# Overwrite existing files
airpy --input data/raw/ --output data/clean/ --overwrite
```

### Python API

```python
from airpy.core.processor import process_data

# Process a single file
df = process_data(
    input_path="data/raw/site_5112_2024.csv",
    output_path="data/clean/"
)

# Process all files in a folder
process_data(
    input_path="data/raw/",
    output_path="data/clean/"
)

# With all options
process_data(
    input_path="data/raw/",
    output_path="data/clean/",
    city="Delhi",                          # Filter by city
    pollutants=["PM25", "PM10", "NO2"],     # Specific pollutants
    verbose=True,                           # Debug output
    overwrite=True                          # Replace existing files
)
```

## CLI Arguments Reference

| Argument | Short | Description |
|----------|-------|-------------|
| `--input` | `-i` | Path to input file or directory (required) |
| `--output` | `-o` | Path to output file or directory (required) |
| `--city` | | Filter processing to a specific city |
| `--live` | | Process live data format filenames |
| `--pollutants` | | List of pollutants to process |
| `--siteid-position` | | Custom site ID position [start, end] |
| `--overwrite` | | Overwrite existing output files |
| `--verbose` | `-v` | Enable verbose/debug output |
| `--version` | | Show version number |

## Supported File Formats

AirPy automatically detects these filename formats:

| Format | Example |
|--------|---------|
| Site format | `site_5112_2024.csv` |
| Numeric format | `5112_2024.csv` |
| 15min format | `15Min_2020_site_5111_station_name.csv` |
| Raw data format | `Raw_data_15Min_2020_site_5111_name.csv` |
| Live format | `site_5111202012251200000.xlsx` |

## Output Columns

After processing, the cleaned data includes:

### Standard Cleaned Columns
- `PM25_clean` - PM2.5 concentrations (µg/m³)
- `PM10_clean` - PM10 concentrations (µg/m³)
- `Ozone_clean` - Ozone concentrations (µg/m³)

### Unit-Corrected Nitrogen Compounds
- `NO_CPCB` - Nitric oxide (µg/m³)
- `NO2_CPCB` - Nitrogen dioxide (µg/m³)
- `NOx_CPCB` - Total nitrogen oxides (µg/m³)

## Data Cleaning Process

1. **Data Formatting**: Standardizes column names and timestamps
2. **Consecutive Repeat Detection**: Removes stuck sensor readings
3. **Outlier Detection**: Uses IQR and MAD methods
4. **Unit Correction**: Standardizes NO/NO2/NOx to µg/m³
5. **Gap Interpolation**: Fills small gaps in data

For detailed documentation, see [Documentation.md](Documentation.md).

## CPCB Data Access

Download CPCB state and city-wise air quality data:
[CPCB Data Repository](https://iitbacin-my.sharepoint.com/:f:/g/personal/30006023_iitb_ac_in/EjiZ_EVBacNKknIN7jIJK3YBm8EssUld0C6kAHBcvGcUGA?e=0vsLeM)

## Troubleshooting

### Common Issues

**No files found**
```bash
# Check if your files have supported extensions (.csv, .xlsx, .xls, .txt)
# Use verbose mode to see what's happening
airpy --input data/raw/ --output data/clean/ --verbose
```

**Metadata extraction fails**
```bash
# Use custom site ID position if your filename format is non-standard
airpy --input data/raw/ --output data/clean/ --siteid-position 1 2
```

**Missing pollutant data**
```bash
# Check which pollutants exist in your data
# Process specific available pollutants only
airpy --input data/raw/ --output data/clean/ --pollutants PM25 PM10
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:
```
AirPy - CPCB Air Quality Data Processing Tool
https://github.com/chandankr014/airpy-tool
``` 