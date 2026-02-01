"""
Base Sensor - Abstract base class for all sensor types.

This abstraction ensures that the visualization layer never depends
on concrete sensor implementations, making the system extensible
and testable.
"""

from abc import ABC, ABCMeta, abstractmethod
from typing import Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal


# Combine QObject's metaclass with ABCMeta to allow abstract Qt classes
class QABCMeta(type(QObject), ABCMeta):
    """Combined metaclass for QObject + ABC compatibility."""
    pass


class BaseSensor(QObject, ABC, metaclass=QABCMeta):
    """
    Abstract base class for all sensors.
    
    All sensor implementations must inherit from this class and implement
    the required methods. This allows the GUI to work with any sensor type
    without knowing the concrete implementation.
    
    Signals:
        data_received(angle: int, distance: float): Raw sensor reading
        connection_changed(connected: bool): Connection status change
        error_occurred(message: str): Error notification
    """
    
    # Qt signals for sensor events
    data_received = pyqtSignal(int, float)  # angle, distance
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    # Sensor metadata - override in subclasses
    NAME = "Base Sensor"
    DESCRIPTION = "Abstract sensor interface"
    
    def __init__(self):
        super().__init__()
        self._connected = False
        self._running = False
    
    @property
    def is_connected(self) -> bool:
        """Check if sensor is currently connected."""
        return self._connected
    
    @property
    def is_running(self) -> bool:
        """Check if sensor is actively reading data."""
        return self._running
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the sensor data acquisition.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the sensor data acquisition."""
        pass
    
    @abstractmethod
    def get_latest_reading(self) -> Optional[Tuple[int, float]]:
        """
        Get the most recent sensor reading.
        
        Returns:
            Tuple of (angle, distance) or None if no reading available
        """
        pass
    
    def send_command(self, command: str):
        """
        Send a command to the sensor (if supported).
        
        Args:
            command: Command string to send
        """
        pass  # Default: no-op for sensors that don't support commands
    
    def get_info(self) -> dict:
        """
        Get sensor information.
        
        Returns:
            dict: Sensor metadata
        """
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "connected": self._connected,
            "running": self._running,
        }
