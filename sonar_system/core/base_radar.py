"""
Base Radar - Abstract base class for all radar visualizations
"""

from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget


class BaseRadar(ABC):
    """
    Abstract base class for radar visualization plugins.
    
    All radar types must inherit from this class and implement
    the required methods.
    """
    
    # Radar metadata - override in subclasses
    NAME = "Base Radar"
    DESCRIPTION = "Abstract base radar"
    ICON = "📡"
    
    def __init__(self):
        """Initialize the radar"""
        self.radar_data = {}  # {angle: distance}
        self.widget = None
    
    @abstractmethod
    def create_widget(self) -> QWidget:
        """
        Create and return the radar visualization widget.
        
        Returns:
            QWidget: The visualization widget
        """
        pass
    
    @abstractmethod
    def update_data(self, angle: int, distance: int):
        """
        Update radar with new data point.
        
        Args:
            angle: Angle in degrees (0-180)
            distance: Distance in cm
        """
        pass
    
    @abstractmethod
    def clear(self):
        """Clear all radar data and reset visualization"""
        pass
    
    def get_info(self) -> dict:
        """
        Get radar information.
        
        Returns:
            dict: Radar metadata including name, description, icon
        """
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "icon": self.ICON,
        }
