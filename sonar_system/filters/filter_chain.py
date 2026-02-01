"""
Filter Chain - Compose multiple filters into a processing pipeline.

Filters are applied in order, with each filter receiving the output
of the previous one. This allows combining the strengths of different
filters (e.g., median for spike removal + moving average for smoothing).
"""

from typing import List, Optional

from .base_filter import BaseFilter


class FilterChain(BaseFilter):
    """
    A chain of filters applied in sequence.
    
    Example usage:
        chain = FilterChain([
            MedianFilter(window_size=3),      # Remove spikes first
            MovingAverageFilter(window_size=5) # Then smooth
        ])
        filtered_value = chain.process(angle, raw_value)
    
    The chain itself can be enabled/disabled, which affects all filters.
    Individual filters can also be toggled independently.
    """
    
    NAME = "Filter Chain"
    DESCRIPTION = "Pipeline of multiple filters applied in sequence"
    
    def __init__(self, filters: Optional[List[BaseFilter]] = None, enabled: bool = True):
        """
        Initialize the filter chain.
        
        Args:
            filters: List of filters to chain (in order of application)
            enabled: Whether the entire chain is active
        """
        super().__init__(enabled)
        self._filters: List[BaseFilter] = filters or []
    
    def add_filter(self, filter_: BaseFilter):
        """
        Add a filter to the end of the chain.
        
        Args:
            filter_: Filter to add
        """
        self._filters.append(filter_)
    
    def remove_filter(self, index: int) -> Optional[BaseFilter]:
        """
        Remove a filter from the chain.
        
        Args:
            index: Index of filter to remove
            
        Returns:
            Removed filter, or None if index invalid
        """
        if 0 <= index < len(self._filters):
            return self._filters.pop(index)
        return None
    
    def get_filters(self) -> List[BaseFilter]:
        """Get list of filters in the chain."""
        return self._filters.copy()
    
    def _apply(self, angle: int, value: float) -> float:
        """
        Apply all filters in sequence.
        
        Args:
            angle: Angle in degrees
            value: Raw sensor value
            
        Returns:
            Fully filtered value
        """
        result = value
        for filter_ in self._filters:
            result = filter_.process(angle, result)
        return result
    
    def reset(self):
        """Reset all filters in the chain."""
        for filter_ in self._filters:
            filter_.reset()
    
    def get_info(self) -> dict:
        """Get chain information including all filters."""
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "enabled": self._enabled,
            "filters": [f.get_info() for f in self._filters],
        }


# Pre-configured filter chains for common use cases
class FilterPresets:
    """Factory for common filter configurations."""
    
    @staticmethod
    def none() -> FilterChain:
        """No filtering - pass through raw data."""
        return FilterChain([])
    
    @staticmethod
    def light() -> FilterChain:
        """Light filtering - minimal lag, some noise reduction."""
        from .moving_average import MovingAverageFilter
        return FilterChain([
            MovingAverageFilter(window_size=3)
        ])
    
    @staticmethod
    def standard() -> FilterChain:
        """Standard filtering - good balance of smoothing and response."""
        from .median_filter import MedianFilter
        from .moving_average import MovingAverageFilter
        return FilterChain([
            MedianFilter(window_size=3),
            MovingAverageFilter(window_size=3)
        ])
    
    @staticmethod
    def heavy() -> FilterChain:
        """Heavy filtering - very smooth but with noticeable lag."""
        from .median_filter import MedianFilter
        from .moving_average import MovingAverageFilter
        return FilterChain([
            MedianFilter(window_size=5),
            MovingAverageFilter(window_size=7)
        ])
    
    @staticmethod
    def kalman() -> FilterChain:
        """Kalman-based filtering - optimal estimation."""
        from .median_filter import MedianFilter
        from .kalman_filter import SimpleKalmanFilter
        return FilterChain([
            MedianFilter(window_size=3),  # Remove spikes first
            SimpleKalmanFilter(process_noise=1.0, measurement_noise=10.0)
        ])
