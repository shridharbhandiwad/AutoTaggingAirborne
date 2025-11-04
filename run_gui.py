#!/usr/bin/env python3
"""
Quick launch script for GUI

Launches the GUI directly without command-line arguments.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from radar_analyzer.gui import launch_gui

if __name__ == '__main__':
    launch_gui()
