"""
Median Filter - Robust outlier rejection.

The median filter is excellent at removing impulse noise (spikes)
while preserving edges. Unlike the moving average, it's not fooled
by extreme outlier values.

Best for: Removing sudden spikes from HC-SR04 misreadings.
"""

from collections import deque
from typing import Dict
import statistics

from .base_filter import BaseFilter


class MedianFilter(BaseFilter):
    """
    Median Filter implementation.
    
    Returns the median of the last N values, effectively ignoring
    outliers that would skew an average.
    
    Trade-offs:
    - Excellent at removing spikes
    - Preserves edges better than moving average
    - Requires sorting, slightly more computational cost
    """
    
    NAME = "Median Filter"
    DESCRIPTION = "Returns median of last N readings, ignoring outliers"
    
    def __init__(self, window_size: int = 5, enabled: bool = True):
        """
        Initialize the median filter.
        
        Args:
            window_size: Number of samples to consider (should be odd for true median)
            enabled: Whether the filter is active
        """
        super().__init__(enabled)
        # Ensure odd window size for true median
        self.window_size = window_size if window_size % 2 == 1 else window_size + 1
        self._history: Dict[int, deque] = {}
    
    def _apply(self, angle: int, value: float) -> float:
        """
        Apply median filter.
        
        Args:
            angle: Angle in degrees
            value: Raw sensor value
            
        Returns:
            Median value
        """
        # Initialize history for this angle if needed
        if angle not in self._history:
            self._history[angle] = deque(maxlen=self.window_size)
        
        # Add new value
        self._history[angle].append(value)
        
        # Return median
        return statistics.median(self._history[angle])
    
    def reset(self):
        """Clear all history."""
        self._history.clear()
    
    def set_window_size(self, size: int):
        """
        Change the window size.
        
        Args:
            size: New window size (will be made odd if even)
        """
        self.window_size = size if size % 2 == 1 else size + 1
        self.reset()
