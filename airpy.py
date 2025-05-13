#!/usr/bin/env python3
"""
AirPy - A tool for cleaning and processing air quality data.
This file is a wrapper around the airpy package for backward compatibility.
"""

import sys
from airpy.cli import main

if __name__ == "__main__":
    sys.exit(main())
