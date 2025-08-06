# AirPy Data Cleaning Documentation
## A Guide for Non-Technical Users

### Overview
AirPy is a tool that cleans and processes air quality data from India's Central Pollution Control Board (CPCB). Raw air quality data often contains errors, inconsistencies, and unreliable measurements that need to be cleaned before analysis. This document explains the data cleaning techniques used and why they are necessary.

### **Final Cleaned Columns to Use**
After AirPy completes all cleaning processes, use these columns for analysis:
- **PM25_clean** - PM2.5 concentrations in μg/m³
- **PM10_clean** - PM10 concentrations in μg/m³  
- **Ozone_clean** - Ozone concentrations in μg/m³
- **NO_CPCB** - Nitric oxide concentrations in μg/m³ (unit-corrected)
- **NO2_CPCB** - Nitrogen dioxide concentrations in μg/m³ (unit-corrected)
- **NOx_CPCB** - Total nitrogen oxides concentrations in μg/m³ (unit-corrected)

**All measurements are standardized to μg/m³ (micrograms per cubic meter)**

---

## Why Data Cleaning is Essential

Air quality monitoring stations collect data every 15 minutes, 24 hours a day. However, this raw data often contains:
- **Sensor malfunctions** that produce impossible readings
- **Dust or debris** on sensors causing incorrect measurements
- **Calibration errors** in different monitoring stations
- **Data transmission errors** during collection
- **Human errors** in data entry or unit reporting

Without proper cleaning, these errors would lead to:
- Incorrect health advisories
- Poor policy decisions
- Misleading pollution trends
- Unreliable scientific research

---

## Data Cleaning Techniques Used in AirPy

### 1. **Data Formatting and Standardization**

**What it does:**
- Converts dates and times to a standard format
- Removes measurement units from column names (e.g., "PM2.5 (μg/m³)" becomes "PM25")
- Ensures all pollution measurements are stored as numbers
- Standardizes column names across different data sources

**Why it's necessary:**
Different monitoring stations may report data in various formats. Some might use "PM2.5" while others use "PM25". Some might include units in the data itself. Standardization ensures all data follows the same format, making analysis possible across different stations and time periods.

**Example:**
```
Before: "PM2.5 (μg/m³)", "NO2 (ppb)", "2023-01-15 10:30"
After: "PM25", "NO2", "2023-01-15 10:30:00"
```

### 2. **Outlier Detection and Removal**

**What it does:**
- Identifies unusually high or low readings that don't match normal patterns
- Uses statistical methods to find measurements that are far from typical values
- Removes these suspicious readings from the dataset

**Why it's necessary:**
Sensors can malfunction and produce impossible readings (like negative pollution levels or extremely high values). These outliers can skew averages and give false impressions of air quality. For example, a malfunctioning PM2.5 sensor might report 5000 μg/m³ when typical values are 20-100 μg/m³.

**How it works:**
- **IQR Method**: Calculates the range where 75% of normal measurements fall and removes values far outside this range
- **Local Analysis**: Compares each measurement to nearby readings in time to spot sudden unrealistic jumps
- **Median Comparison**: Uses the middle value of surrounding measurements to identify outliers

**Example:**
```
Time    | Raw PM2.5 | Cleaned PM2.5 | Action
10:00   | 45        | 45           | Keep (normal)
10:15   | 2500      | [removed]    | Remove (outlier)
10:30   | 52        | 52           | Keep (normal)
```

### 3. **Consecutive Repeat Detection**

**What it does:**
- Identifies when a sensor reports the exact same value many times in a row
- Removes these suspicious repeated measurements
- Recognizes that real air quality rarely stays exactly the same

**Why it's necessary:**
When sensors get stuck or malfunction, they often report the same value repeatedly. Real air pollution levels naturally fluctuate, so identical readings for hours suggest equipment problems rather than actual conditions.

**How it works:**
- Analyzes variation in measurements over time
- Calculates if the data shows natural fluctuation or artificial repetition
- Removes periods where measurements are suspiciously constant

**Example:**
```
Time    | Raw PM2.5 | Cleaned PM2.5 | Action
09:00   | 45        | 45           | Keep
09:15   | 45        | 45           | Keep
09:30   | 45        | [removed]    | Remove (too repetitive)
09:45   | 45        | [removed]    | Remove (too repetitive)
10:00   | 48        | 48           | Keep (natural variation)
```

### 4. **Unit Inconsistency Correction**

**What it does:**
- First applies all standard cleaning methods (outlier removal, repeat detection, etc.) to create "_clean" versions of all pollutants
- Then specifically handles nitrogen compounds (NO, NO2, NOx) for unit consistency correction
- Automatically detects when different stations report nitrogen compounds in different units
- Converts all measurements to a standard unit (μg/m³)
- Creates "_CPCB" suffixed columns for unit-corrected nitrogen compounds

**Why it's necessary:**
Different monitoring stations sometimes report the same pollutant in different units. For example, some stations might report NO2 in "parts per billion" (ppb) while others use "micrograms per cubic meter" (μg/m³). Without conversion, comparing data between stations would be meaningless.

**How it works:**
This is a **two-step process**:

**Step 1: General Cleaning**
- Raw data is cleaned using outlier detection, repeat removal, and other methods
- Results are saved with "_clean" suffix (PM25_clean, PM10_clean, Ozone_clean)

**Step 2: Unit Correction (Nitrogen Compounds Only)**
- Uses chemical equations to validate unit consistency
- For nitrogen compounds: NO + NO2 = NOx (this relationship must hold true)
- Tests different unit combinations to find the correct one
- Automatically converts all measurements to the standard unit
- Results are saved with "_CPCB" suffix (NO_CPCB, NO2_CPCB, NOx_CPCB)

**Example:**
```
Step 1: Raw → Clean
Station A: NO2_raw = 25 ppb    →  NO2_clean = 25 (outliers removed, but units not yet corrected)
Station B: NO2_raw = 47 μg/m³  →  NO2_clean = 47 (outliers removed, but units not yet corrected)

Step 2: Clean → Unit Corrected
Station A: NO2_clean = 25      →  NO2_CPCB = 47 μg/m³ (converted from ppb)
Station B: NO2_clean = 47      →  NO2_CPCB = 47 μg/m³ (already in correct units)
```

### 5. **Data Gap Interpolation**

**What it does:**
- Fills small gaps in data where measurements are missing
- Estimates missing values based on nearby measurements
- Only fills short gaps (typically 2-3 readings)

**Why it's necessary:**
Monitoring stations occasionally miss readings due to temporary communication issues or brief maintenance. For short gaps, the pollution level likely changes gradually, so we can reasonably estimate missing values from surrounding data.

**How it works:**
- Identifies gaps in the time series
- Uses linear interpolation to estimate missing values
- Only fills gaps shorter than a specified limit
- Leaves longer gaps unfilled (marked as missing)

**Example:**
```
Time    | Raw PM2.5 | Cleaned PM2.5 | Action
10:00   | 45        | 45           | Keep
10:15   | [missing] | 46.5         | Estimate (interpolate)
10:30   | 48        | 48           | Keep
```

### 6. **Missing Data Handling**

**What it does:**
- Identifies different types of missing or invalid data
- Converts problematic entries to a standard "missing" format
- Handles cases where data exists but is unreliable

**Why it's necessary:**
Raw data files often contain various indicators for missing data: empty cells, "N/A", "Error", negative values, or text in numeric fields. Standardizing how missing data is represented ensures consistent analysis.

**How it works:**
- Scans for common missing data indicators
- Converts all to a standard format (NaN - "Not a Number")
- Flags negative pollution values as invalid
- Identifies impossible combinations (e.g., PM2.5 higher than PM10)

---

## Quality Assurance Features

### Validation Checks
- **Cross-pollutant validation**: Ensures related pollutants have logical relationships
- **Temporal consistency**: Checks that changes over time are realistic
- **Geographical validation**: Compares readings with nearby stations

### Reporting
- **Cleaning statistics**: Shows how much data was removed or corrected
- **Quality flags**: Marks data points that required significant cleaning
- **Uncertainty indicators**: Identifies periods where data quality may be lower

---

## Benefits of This Cleaning Process

### For Public Health
- **Accurate air quality advisories** based on reliable data
- **Proper health warnings** during pollution episodes
- **Reliable exposure assessments** for health studies

### For Policy Making
- **Trustworthy pollution trends** for regulatory decisions
- **Accurate compliance monitoring** for emission standards
- **Reliable data for environmental impact assessments**

### For Research
- **Clean datasets** for scientific studies
- **Consistent time series** for trend analysis
- **Standardized data** for multi-city comparisons

---

## What the Cleaned Data Provides

After cleaning, the processed data includes:

### Original Measurements
- Raw pollutant readings (PM2.5, PM10, NO2, NO, NOx, Ozone)
- Timestamp and location information

### Cleaned Data
**Standard cleaned columns (with "_clean" suffix):**
- PM25_clean, PM10_clean, Ozone_clean - All pollutants with outliers removed, repeats filtered, and gaps interpolated

**Unit-corrected columns (with "_CPCB" suffix):**
- NO_CPCB, NO2_CPCB, NOx_CPCB - Nitrogen compounds with unit standardization applied

**All measurements standardized to μg/m³**

### Quality Information
- Flags indicating data quality issues
- Statistics about cleaning performed
- Uncertainty estimates

---

## Usage Guidelines

### When to Use Cleaned Data
- **Policy analysis and reporting**
- **Health impact assessments**
- **Scientific research**
- **Public information dissemination**

### When to Exercise Caution
- **Periods with extensive cleaning** (check quality flags)
- **Stations with frequent sensor issues**
- **Extreme weather events** (may affect sensor performance)

### Best Practices
1. **Always check quality flags** before using cleaned data
2. **Review cleaning statistics** to understand data reliability
3. **Consider uncertainty estimates** in analysis
4. **Use multiple stations** for regional assessments
5. **Document data sources and cleaning methods** in reports

---

## Technical Support

For questions about data cleaning methods or to report data quality issues:
- Review the cleaning logs for specific stations
- Check quality flags for problematic periods
- Consult domain experts for interpretation
- Report systematic issues to monitoring agencies

---

This documentation ensures that users understand not just what the data cleaning process does, but why each step is necessary for producing reliable air quality information that can be safely used for public health protection and policy decisions.