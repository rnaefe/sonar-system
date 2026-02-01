#!/usr/bin/env python3
"""
Sonar System - Command Line Entry Point

Usage:
    python run.py          # Run the new v2 control center (with filtering)
    python run.py --legacy # Run the original control center
"""

import sys

def main():
    if "--legacy" in sys.argv:
        # Run original control center
        from sonar_system.control_center import run
    else:
        # Run new v2 control center with filtering
        from sonar_system.control_center_v2 import run
    
    run()

if __name__ == "__main__":
    main()
