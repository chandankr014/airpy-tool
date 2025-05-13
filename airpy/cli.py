"""
Command Line Interface for AirPy.
"""
import sys
import argparse
import warnings
warnings.filterwarnings("ignore")
from airpy.core.processor import process_data


def main():
    # PARSE COMMAND LINE ARGUMENTS
    parser = argparse.ArgumentParser(description="AirPy - Air Quality Data Processing Tool")
    parser.add_argument("--city", type=str, help="City name to process")
    parser.add_argument("--live", action="store_true", help="Process live data")
    parser.add_argument("--raw-dir", type=str, help="Path to raw data directory")
    parser.add_argument("--clean-dir", type=str, help="Path to save cleaned data")
    parser.add_argument("--pollutants", type=str, nargs="+", help="List of pollutants to process (default: PM25 PM10 NO NO2 NOx)")
    
    args = parser.parse_args()
    
    # PROCESS DATA
    process_data(
        city=args.city,
        live=args.live,
        raw_dir=args.raw_dir,
        clean_dir=args.clean_dir,
        pollutants=args.pollutants
    )
    return 0

if __name__ == "__main__":
    sys.exit(main()) 