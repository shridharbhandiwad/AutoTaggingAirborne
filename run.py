#!/usr/bin/env python3
"""
Quick launch script for Radar Target Analyzer

This script provides a convenient way to run the application without installation.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from radar_analyzer.main import main

if __name__ == '__main__':
    main()
