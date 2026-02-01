"""
Data Processor - Central hub for sensor data processing.

This component sits between sensors and visualization, handling:
- Raw data from sensors
- Filtering pipeline
- Data distribution to visualizers
- Comparison mode (raw vs filtered)

Architecture:
    Sensor -> DataProcessor -> Filter Chain -> Visualization
                           └-> Raw Data -----> Comparison View
"""

from typing import Optional, Dict, Tuple, Callable
from PyQt5.QtCore import QObject, pyqtSignal

from .sensors import BaseSensor
from .filters import FilterChain, FilterPresets


class DataProcessor(QObject):
    """
    Central data processing hub.
    
    Receives raw data from sensors, applies filtering, and emits
    both raw and filtered data for visualization comparison.
    
    Signals:
        raw_data(angle: int, distance: float): Unfiltered sensor data
        filtered_data(angle: int, distance: float): Data after filter chain
        data_quality_warning(message: str): Quality issue detected
    """
    
    raw_data = pyqtSignal(int, float)       # angle, raw_distance
    filtered_data = pyqtSignal(int, float)   # angle, filtered_distance
    data_quality_warning = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self._sensor: Optional[BaseSensor] = None
        self._filter_chain: FilterChain = FilterPresets.standard()
        
        # Data storage for comparison
        self._raw_data: Dict[int, float] = {}
        self._filtered_data: Dict[int, float] = {}
        
        # Quality detection thresholds
        self._spike_threshold = 50.0  # cm change to consider a spike
        self._last_readings: Dict[int, float] = {}
        
        # Statistics
        self._stats = {
            "readings_processed": 0,
            "spikes_detected": 0,
            "noise_filtered": 0.0,
        }
    
    def set_sensor(self, sensor: BaseSensor):
        """
        Attach a sensor to the processor.
        
        Args:
            sensor: Any sensor implementing BaseSensor interface
        """
        # Disconnect previous sensor if any
        if self._sensor:
            try:
                self._sensor.data_received.disconnect(self._on_sensor_data)
            except TypeError:
                pass
        
        self._sensor = sensor
        self._sensor.data_received.connect(self._on_sensor_data)
    
    def set_filter_chain(self, chain: FilterChain):
        """
        Set the filter chain.
        
        Args:
            chain: Configured filter chain
        """
        self._filter_chain = chain
    
    def enable_filtering(self, enabled: bool):
        """Enable or disable the filter chain."""
        self._filter_chain.enabled = enabled
    
    def reset(self):
        """Reset all data and filter states."""
        self._raw_data.clear()
        self._filtered_data.clear()
        self._last_readings.clear()
        self._filter_chain.reset()
        self._stats = {
            "readings_processed": 0,
            "spikes_detected": 0,
            "noise_filtered": 0.0,
        }
    
    def get_raw_data(self) -> Dict[int, float]:
        """Get current raw data (angle -> distance)."""
        return self._raw_data.copy()
    
    def get_filtered_data(self) -> Dict[int, float]:
        """Get current filtered data (angle -> distance)."""
        return self._filtered_data.copy()
    
    def get_stats(self) -> dict:
        """Get processing statistics."""
        return self._stats.copy()
    
    def _on_sensor_data(self, angle: int, distance: float):
        """
        Handle incoming sensor data.
        
        Args:
            angle: Angle in degrees
            distance: Raw distance reading
        """
        self._stats["readings_processed"] += 1
        
        # Check for data quality issues
        self._check_data_quality(angle, distance)
        
        # Store and emit raw data
        self._raw_data[angle] = distance
        self.raw_data.emit(angle, distance)
        
        # Apply filtering
        filtered = self._filter_chain.process(angle, distance)
        self._filtered_data[angle] = filtered
        self.filtered_data.emit(angle, filtered)
        
        # Track noise reduction
        self._stats["noise_filtered"] += abs(distance - filtered)
        
        # Update last reading for this angle
        self._last_readings[angle] = distance
    
    def _check_data_quality(self, angle: int, distance: float):
        """
        Check for data quality issues like spikes.
        
        Args:
            angle: Angle in degrees
            distance: Raw distance reading
        """
        if angle in self._last_readings:
            delta = abs(distance - self._last_readings[angle])
            if delta > self._spike_threshold:
                self._stats["spikes_detected"] += 1
                self.data_quality_warning.emit(
                    f"Spike detected at {angle}°: {delta:.1f}cm change"
                )


class ComparisonDataProvider:
    """
    Provides synchronized raw and filtered data for comparison visualization.
    
    This class is a convenience wrapper that maintains both data streams
    and provides them in a format suitable for side-by-side visualization.
    """
    
    def __init__(self, processor: DataProcessor):
        """
        Initialize with a data processor.
        
        Args:
            processor: Configured DataProcessor instance
        """
        self._processor = processor
        self._comparison_mode = False
    
    def set_comparison_mode(self, enabled: bool):
        """Enable or disable comparison mode."""
        self._comparison_mode = enabled
    
    @property
    def comparison_mode(self) -> bool:
        """Check if comparison mode is enabled."""
        return self._comparison_mode
    
    def get_comparison_data(self) -> Tuple[Dict[int, float], Dict[int, float]]:
        """
        Get both raw and filtered data for comparison.
        
        Returns:
            Tuple of (raw_data, filtered_data) dictionaries
        """
        return (
            self._processor.get_raw_data(),
            self._processor.get_filtered_data()
        )
    
    def get_noise_reduction_stats(self) -> dict:
        """
        Calculate noise reduction statistics.
        
        Returns:
            Dict with noise reduction metrics
        """
        raw = self._processor.get_raw_data()
        filtered = self._processor.get_filtered_data()
        stats = self._processor.get_stats()
        
        if not raw:
            return {"average_reduction": 0, "readings": 0, "spikes": 0}
        
        total_diff = 0
        count = 0
        for angle in raw:
            if angle in filtered:
                total_diff += abs(raw[angle] - filtered[angle])
                count += 1
        
        avg_reduction = total_diff / count if count > 0 else 0
        
        return {
            "average_reduction": avg_reduction,
            "readings": stats["readings_processed"],
            "spikes": stats["spikes_detected"],
        }
