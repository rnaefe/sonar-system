"""
Moving Average Filter - Smooths data by averaging recent values.

This is the simplest and most intuitive filter. It reduces high-frequency
noise but introduces some lag in response to sudden changes.

Best for: General noise reduction when response time is not critical.
"""

from collections import deque
from typing import Dict

from .base_filter import BaseFilter


class MovingAverageFilter(BaseFilter):
    """
    Moving Average Filter implementation.
    
    Maintains a sliding window of recent values for each angle
    and outputs the average.
    
    Trade-offs:
    - Larger window = smoother output, but more lag
    - Smaller window = faster response, but more noise passes through
    """
    
    NAME = "Moving Average"
    DESCRIPTION = "Averages the last N readings to smooth noise"
    
    def __init__(self, window_size: int = 5, enabled: bool = True):
        """
        Initialize the moving average filter.
        
        Args:
            window_size: Number of samples to average (default: 5)
            enabled: Whether the filter is active
        """
        super().__init__(enabled)
        self.window_size = window_size
        self._history: Dict[int, deque] = {}
    
    def _apply(self, angle: int, value: float) -> float:
        """
        Apply moving average filter.
        
        Args:
            angle: Angle in degrees
            value: Raw sensor value
            
        Returns:
            Averaged value
        """
        # Initialize history for this angle if needed
        if angle not in self._history:
            self._history[angle] = deque(maxlen=self.window_size)
        
        # Add new value
        self._history[angle].append(value)
        
        # Return average
        return sum(self._history[angle]) / len(self._history[angle])
    
    def reset(self):
        """Clear all history."""
        self._history.clear()
    
    def set_window_size(self, size: int):
        """
        Change the window size.
        
        Note: This clears existing history.
        """
        self.window_size = max(1, size)
        self.reset()
