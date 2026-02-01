"""
Mock Sensor - Simulated sensor for testing and demonstration.

This sensor generates realistic test data including:
- Static walls (stable distance readings)
- Moving obstacles (temporary distance changes)
- Random noise (jitter typical of HC-SR04)
- Outlier spikes (sensor errors)

Use this to test the filtering pipeline without hardware.
"""

import math
import random
import time
from typing import Optional, Tuple, List
from PyQt5.QtCore import QThread, QTimer

from .base_sensor import BaseSensor


class MockSensor(BaseSensor):
    """
    Simulated ultrasonic sensor for testing and demonstration.
    
    Generates realistic noisy data that mimics real HC-SR04 behavior,
    perfect for demonstrating why filtering is necessary.
    """
    
    NAME = "Mock Sensor"
    DESCRIPTION = "Simulated sensor with configurable noise and scenarios"
    
    def __init__(
        self,
        scan_speed: float = 0.02,
        noise_level: float = 5.0,
        outlier_probability: float = 0.05,
        scenario: str = "realistic"
    ):
        """
        Initialize the mock sensor.
        
        Args:
            scan_speed: Time in seconds between readings
            noise_level: Standard deviation of Gaussian noise (in cm)
            outlier_probability: Probability of generating an outlier spike
            scenario: Scenario to simulate ("realistic", "wall", "moving_object")
        """
        super().__init__()
        self.scan_speed = scan_speed
        self.noise_level = noise_level
        self.outlier_probability = outlier_probability
        self.scenario = scenario
        
        self._thread = None
        self._latest_reading = None
        self._current_angle = 0
        self._direction = 1  # 1 = forward sweep, -1 = reverse
        
        # Scenario state
        self._moving_object_angle = 90
        self._moving_object_direction = 1
        self._time_counter = 0
    
    def start(self) -> bool:
        """Start generating simulated data."""
        if self._running:
            return True
        
        self._running = True
        self._connected = True
        self.connection_changed.emit(True)
        
        self._thread = _MockThread(self)
        self._thread.start()
        return True
    
    def stop(self):
        """Stop generating data."""
        self._running = False
        if self._thread:
            self._thread.wait(2000)
            self._thread = None
        
        self._connected = False
        self.connection_changed.emit(False)
    
    def get_latest_reading(self) -> Optional[Tuple[int, float]]:
        """Get the most recent reading."""
        return self._latest_reading
    
    def _generate_reading(self) -> Tuple[int, float]:
        """
        Generate a single simulated reading.
        
        Returns:
            Tuple of (angle, distance) with realistic noise
        """
        angle = self._current_angle
        
        # Get base distance from scenario
        base_distance = self._get_scenario_distance(angle)
        
        # Add Gaussian noise (typical HC-SR04 jitter)
        noise = random.gauss(0, self.noise_level)
        distance = base_distance + noise
        
        # Occasionally generate outlier spikes (sensor errors)
        if random.random() < self.outlier_probability:
            # Outliers can be either very close or very far
            if random.random() < 0.5:
                distance = random.uniform(2, 15)  # Sudden close spike
            else:
                distance = random.uniform(180, 200)  # Sudden far spike
        
        # Clamp to valid range
        distance = max(2.0, min(200.0, distance))
        
        # Update angle for next reading (sweep pattern)
        self._current_angle += self._direction
        if self._current_angle >= 180:
            self._direction = -1
        elif self._current_angle <= 0:
            self._direction = 1
        
        self._time_counter += 1
        
        return (angle, distance)
    
    def _get_scenario_distance(self, angle: int) -> float:
        """
        Get base distance for the current scenario.
        
        Args:
            angle: Current scan angle
            
        Returns:
            Base distance before noise is applied
        """
        if self.scenario == "wall":
            # Simple flat wall at constant distance
            return 100.0
        
        elif self.scenario == "moving_object":
            # Wall with a moving object in front
            wall_distance = 150.0
            
            # Update moving object position
            self._moving_object_angle += self._moving_object_direction * 0.5
            if self._moving_object_angle > 140:
                self._moving_object_direction = -1
            elif self._moving_object_angle < 40:
                self._moving_object_direction = 1
            
            # Check if current angle sees the object
            object_width = 20  # degrees
            if abs(angle - self._moving_object_angle) < object_width / 2:
                return 50.0  # Object is closer than wall
            return wall_distance
        
        else:  # "realistic" - complex room scenario
            return self._get_realistic_distance(angle)
    
    def _get_realistic_distance(self, angle: int) -> float:
        """
        Generate a realistic room-like distance profile.
        
        Simulates:
        - Left wall (angled)
        - Right wall (angled)
        - Back wall (flat)
        - A stationary obstacle
        - A periodically appearing moving object
        """
        # Base room shape - trapezoidal room
        if angle < 30:
            # Left wall - close and angled
            base = 40 + angle * 2
        elif angle > 150:
            # Right wall - close and angled
            base = 40 + (180 - angle) * 2
        else:
            # Back wall with some variation
            base = 100 + 20 * math.sin(math.radians(angle * 2))
        
        # Stationary obstacle (pillar) around 60-70 degrees
        if 55 <= angle <= 75:
            base = min(base, 45 + abs(angle - 65) * 2)
        
        # Moving object that appears periodically
        cycle = (self._time_counter // 100) % 3
        if cycle == 0:  # Object present
            object_center = 90 + 30 * math.sin(self._time_counter * 0.05)
            if abs(angle - object_center) < 15:
                object_dist = 35 + abs(angle - object_center) * 2
                base = min(base, object_dist)
        
        return base
    
    def _run_loop(self):
        """Main simulation loop."""
        while self._running:
            angle, distance = self._generate_reading()
            self._latest_reading = (angle, distance)
            self.data_received.emit(angle, distance)
            time.sleep(self.scan_speed)


class _MockThread(QThread):
    """Background thread for mock sensor."""
    
    def __init__(self, sensor: MockSensor):
        super().__init__()
        self._sensor = sensor
    
    def run(self):
        self._sensor._run_loop()


# Pre-configured scenarios for easy testing
class ScenarioPresets:
    """Factory for common test scenarios."""
    
    @staticmethod
    def clean_wall() -> MockSensor:
        """Wall with minimal noise - shows baseline behavior."""
        return MockSensor(
            noise_level=1.0,
            outlier_probability=0.0,
            scenario="wall"
        )
    
    @staticmethod
    def noisy_wall() -> MockSensor:
        """Wall with realistic HC-SR04 noise."""
        return MockSensor(
            noise_level=5.0,
            outlier_probability=0.03,
            scenario="wall"
        )
    
    @staticmethod
    def very_noisy() -> MockSensor:
        """Extremely noisy sensor - stress test for filters."""
        return MockSensor(
            noise_level=15.0,
            outlier_probability=0.1,
            scenario="wall"
        )
    
    @staticmethod
    def moving_obstacle() -> MockSensor:
        """Moving object scenario."""
        return MockSensor(
            noise_level=5.0,
            outlier_probability=0.03,
            scenario="moving_object"
        )
    
    @staticmethod
    def realistic_room() -> MockSensor:
        """Full realistic room simulation."""
        return MockSensor(
            noise_level=5.0,
            outlier_probability=0.05,
            scenario="realistic"
        )
