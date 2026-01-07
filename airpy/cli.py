"""
Command Line Interface for AirPy.
"""
import sys
import argparse
import warnings
warnings.filterwarnings("ignore")
from airpy.core.processor import process_data


def main():
    """Main entry point for the AirPy CLI."""
    
    parser = argparse.ArgumentParser(
        description="AirPy - CPCB Air Quality Data Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  airpy --input data/raw/site_5112_2024.csv --output data/clean/
  
  # Process all files in a folder
  airpy --input data/raw/ --output data/clean/
  
  # Process with verbose output for debugging
  airpy --input data/raw/ --output data/clean/ --verbose
  
  # Process specific pollutants only
  airpy --input data/raw/ --output data/clean/ --pollutants PM25 PM10
  
  # Process files for a specific city
  airpy --input data/raw/ --output data/clean/ --city Delhi
  
  # Process live data format files
  airpy --input data/raw/ --output data/clean/ --live
  
  # Overwrite existing output files
  airpy --input data/raw/ --output data/clean/ --overwrite

For more information, visit: https://github.com/chandankr014/airpy-tool
"""
    )
    
    # Input/Output arguments (primary)
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        dest="input_path",
        help="Path to input file or directory containing raw data"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        dest="output_path",
        help="Path to output file or directory for cleaned data"
    )
    
    # Legacy arguments (backward compatibility)
    parser.add_argument(
        "--raw-dir", 
        type=str, 
        help="[Deprecated] Use --input instead. Path to raw data directory"
    )
    parser.add_argument(
        "--clean-dir", 
        type=str, 
        help="[Deprecated] Use --output instead. Path to save cleaned data"
    )
    
    # Processing options
    parser.add_argument(
        "--city", 
        type=str, 
        help="Filter processing to a specific city name"
    )
    parser.add_argument(
        "--live", 
        action="store_true", 
        help="Process live data format (site_IDYYYYMMDDHHMMSS.xlsx)"
    )
    parser.add_argument(
        "--pollutants", 
        type=str, 
        nargs="+",
        default=None,
        help="List of pollutants to process (default: PM25 PM10 NO NO2 NOx Ozone)"
    )
    parser.add_argument(
        "--siteid-position", 
        type=int, 
        nargs=2,
        metavar=("START", "END"),
        help="Custom site ID position in filename [start_index, end_index] when split by '_'"
    )
    
    # Output control
    parser.add_argument(
        "--overwrite", 
        action="store_true", 
        help="Overwrite existing output files (default: skip existing)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose/debug output"
    )
    
    # Version
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.1.0"
    )
    
    args = parser.parse_args()
    
    # Handle backward compatibility
    input_path = args.input_path or args.raw_dir
    output_path = args.output_path or args.clean_dir
    
    # Validate required arguments
    if not input_path:
        parser.error("--input (or --raw-dir) is required. Example: --input data/raw/")
    if not output_path:
        parser.error("--output (or --clean-dir) is required. Example: --output data/clean/")
    
    try:
        # Process data with all arguments
        process_data(
            input_path=input_path,
            output_path=output_path,
            city=args.city,
            live=args.live,
            pollutants=args.pollutants,
            siteid_position=args.siteid_position,
            verbose=args.verbose,
            overwrite=args.overwrite
        )
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 