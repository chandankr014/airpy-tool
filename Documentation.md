# AirPy Data Cleaning Documentation

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
09:00: NO2 = 25 ppb    →  NO2_clean = 25 (outliers removed, but units not yet corrected)
09:15: NO2 = 47.6 μg/m³  →  NO2_clean = 47.6 (outliers removed, but units not yet corrected)

Step 2: Clean → Unit Corrected
09:00: NO2_clean = 25      →  NO2_CPCB = 47 μg/m³ (converted from ppb)
09:15: NO2_clean = 47.6      →  NO2_CPCB = 47.6 μg/m³ (already in correct units)
```

### 5. **Data Gap Interpolation**

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

**How it works:**
- Scans for common missing data indicators
- Converts all to a standard format (NaN - "Not a Number")
- Flags negative pollution values as invalid
- Identifies impossible combinations (e.g., PM2.5 higher than PM10)

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

---

This documentation ensures that users understand not just what the data cleaning process does, but why each step is necessary for producing reliable air quality information that can be safely used for public health protection and policy decisions.
