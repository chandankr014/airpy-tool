# AirPy Tool - User Guide for Non-Technical Users

## What is AirPy?

AirPy is a specialized tool designed to clean and process air quality data from the Central Pollution Control Board (CPCB) in India. Think of it as a "data janitor" that takes messy, raw air quality measurements and transforms them into clean, reliable data that researchers and policymakers can trust.

## Why Do We Need Data Cleaning?

Air quality monitoring stations collect data continuously, but this raw data often contains errors, inconsistencies, and missing information. Without proper cleaning, this data could lead to:

- **Incorrect conclusions** about air quality trends
- **Misleading policy decisions** based on faulty data
- **Wasted resources** on analysis of unreliable information
- **Public confusion** about actual air quality conditions

## Data Cleaning Techniques Used in AirPy

### 1. **Outlier Detection and Removal**
**What it does:** Identifies and removes unusually high or low air quality readings that are likely errors.

**Why it's necessary:** Air quality sensors sometimes malfunction and record impossible values (like negative pollution levels or extremely high readings). These outliers can skew analysis and give false impressions of air quality.

**How it works:** 
- Uses statistical methods to identify readings that are too far from normal patterns
- Compares each reading to the typical range for that location and time
- Removes readings that are statistically impossible or highly unlikely

### 2. **Consecutive Repeat Detection**
**What it does:** Identifies and removes data points where the same value is recorded repeatedly for suspiciously long periods.

**Why it's necessary:** When sensors get stuck or malfunction, they may record the same value for hours or days. This doesn't represent real air quality changes and needs to be cleaned.

**How it works:**
- Looks for patterns where the same value appears many times in a row
- Uses statistical analysis to determine if the pattern is natural or indicates a sensor problem
- Removes suspicious repeated values while keeping legitimate stable readings

### 3. **Unit Inconsistency Correction**
**What it does:** Fixes problems where different air quality measurements use different units of measurement.

**Why it's necessary:** Different monitoring stations might report nitrogen compounds (NO, NO2, NOx) in different units (parts per billion vs. micrograms per cubic meter). This makes it impossible to compare data across stations without correction.

**How it works:**
- Automatically detects which units each station is using
- Converts all measurements to a standard unit (micrograms per cubic meter)
- Ensures mathematical relationships between NO, NO2, and NOx are consistent

### 4. **Data Formatting and Standardization**
**What it does:** Converts data from various file formats and structures into a consistent, usable format.

**Why it's necessary:** CPCB provides data in different file formats (CSV, Excel) with varying structures. Without standardization, it's impossible to analyze data from multiple sources together.

**How it works:**
- Reads data from different file types (CSV, Excel)
- Standardizes column names and data types
- Ensures all timestamps are in the same format
- Removes unnecessary columns and formatting

### 5. **Missing Data Handling**
**What it does:** Intelligently fills small gaps in the data where readings are missing.

**Why it's necessary:** Short gaps in data collection are common due to brief sensor issues or maintenance. Small gaps can be filled to create continuous datasets for analysis.

**How it works:**
- Identifies small gaps (up to 2 consecutive missing readings)
- Uses surrounding data to estimate reasonable values for missing points
- Leaves larger gaps unfilled to avoid creating false data

### 6. **Data Validation and Quality Checks**
**What it does:** Performs mathematical checks to ensure data makes logical sense.

**Why it's necessary:** Air quality measurements have known relationships (e.g., NO + NO2 should equal NOx). When these relationships don't hold, it indicates data quality issues.

**How it works:**
- Checks mathematical relationships between related pollutants
- Flags data points where relationships are impossible
- Provides quality indicators for each data point

## How to Use AirPy

### Simple Command Line Usage

1. **Process all available data:**
   ```bash
   airpy
   ```

2. **Process data for a specific city:**
   ```bash
   airpy --city "Delhi"
   ```

3. **Process live (real-time) data:**
   ```bash
   airpy --live
   ```

4. **Process specific pollutants only:**
   ```bash
   airpy --pollutants PM25 PM10 NO2
   ```

### What You Need to Get Started

1. **Raw Data Directory:** A folder containing your air quality data files
2. **Output Directory:** A folder where cleaned data will be saved
3. **Data Files:** Air quality data in CSV or Excel format

### Supported File Formats

AirPy can work with data files that follow these naming patterns:
- `15Min_YEAR_site_ID_STATION_CITY_ORG_15Min.csv`
- `Raw_data_15Min_YEAR_site_ID_STATION_CITY_ORG_15Min.csv`
- `site_ID_YEAR.csv`
- Live data: `site_IDYYYYMMDDHHMMSS.xlsx`

## What You Get After Processing

After running AirPy, you'll receive:

1. **Cleaned Data Files:** Processed data saved in CSV or Excel format
2. **Quality Reports:** Information about what was cleaned and why
3. **Standardized Format:** All data in consistent units and structure
4. **Ready for Analysis:** Data that can be used for research, policy-making, or public reporting

## Benefits of Using AirPy

- **Saves Time:** Automated cleaning instead of manual data review
- **Improves Accuracy:** Removes errors that could affect analysis
- **Ensures Consistency:** Standardizes data from multiple sources
- **Enables Comparison:** Makes it possible to compare data across different stations and time periods
- **Builds Trust:** Provides reliable data for decision-making

## Getting Help

If you encounter issues or have questions:
1. Check the error messages for guidance
2. Ensure your data files are in the correct format
3. Verify that your directories exist and are accessible
4. Contact technical support if problems persist

## Important Notes

- **Backup Your Data:** Always keep copies of your original raw data
- **Review Results:** Check the cleaned data to ensure it looks reasonable
- **Understand Limitations:** No automated tool is perfect - use your judgment
- **Document Changes:** Keep records of what cleaning was applied to your data

---

*This tool helps ensure that air quality data is reliable, consistent, and ready for meaningful analysis that can inform environmental policy and public health decisions.*