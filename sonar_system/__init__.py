"""
Sonar System - Professional Sensor Visualization Framework

A modular Python framework for real-time sensor visualization with:
- Sensor abstraction layer (hardware-agnostic design)
- Signal filtering pipeline (noise reduction, outlier rejection)
- Multiple visualization modes with comparison capability
- Robot control integration

Author: Sonar System Contributors
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Sonar System Contributors"

# Public API
from .sensors import BaseSensor, UltrasonicSensor, MockSensor
from .filters import FilterChain, FilterPresets, MovingAverageFilter, MedianFilter, SimpleKalmanFilter
from .data_processor import DataProcessor, ComparisonDataProvider
from .radars import AVAILABLE_RADARS, get_radar_by_name

__all__ = [
    # Sensors
    "BaseSensor",
    "UltrasonicSensor", 
    "MockSensor",
    # Filters
    "FilterChain",
    "FilterPresets",
    "MovingAverageFilter",
    "MedianFilter",
    "SimpleKalmanFilter",
    # Data Processing
    "DataProcessor",
    "ComparisonDataProvider",
    # Visualization
    "AVAILABLE_RADARS",
    "get_radar_by_name",
]
