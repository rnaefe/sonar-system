"""
Base Filter - Abstract base class for all signal filters.

Design Philosophy:
- Filters are stateless functions over a sliding window
- Each filter maintains its own history
- Filters can be chained together
- Filters can be enabled/disabled at runtime
"""

from abc import ABC, abstractmethod
from typing import Optional
from collections import deque


class BaseFilter(ABC):
    """
    Abstract base class for signal filters.
    
    All filters operate on a per-angle basis, meaning each angle
    has its own history. This is important for radar-style data
    where readings at different angles are independent.
    """
    
    NAME = "Base Filter"
    DESCRIPTION = "Abstract filter interface"
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the filter.
        
        Args:
            enabled: Whether the filter is active
        """
        self._enabled = enabled
    
    @property
    def enabled(self) -> bool:
        """Check if filter is enabled."""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable the filter."""
        self._enabled = value
    
    def process(self, angle: int, value: float) -> float:
        """
        Process a single value through the filter.
        
        Args:
            angle: Angle in degrees (for per-angle filtering)
            value: Raw sensor value
            
        Returns:
            Filtered value (or original if filter is disabled)
        """
        if not self._enabled:
            return value
        return self._apply(angle, value)
    
    @abstractmethod
    def _apply(self, angle: int, value: float) -> float:
        """
        Apply the filter algorithm.
        
        Args:
            angle: Angle in degrees
            value: Raw sensor value
            
        Returns:
            Filtered value
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset the filter state (clear all history)."""
        pass
    
    def get_info(self) -> dict:
        """Get filter information."""
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "enabled": self._enabled,
        }
