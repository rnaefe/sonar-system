"""
Signal filtering module for the Sonar System.

Provides a collection of filters to clean noisy sensor data.
Filters are designed to be chainable and toggleable.
"""

from .base_filter import BaseFilter
from .moving_average import MovingAverageFilter
from .median_filter import MedianFilter
from .kalman_filter import SimpleKalmanFilter
from .filter_chain import FilterChain, FilterPresets

__all__ = [
    "BaseFilter",
    "MovingAverageFilter",
    "MedianFilter",
    "SimpleKalmanFilter",
    "FilterChain",
    "FilterPresets",
]
