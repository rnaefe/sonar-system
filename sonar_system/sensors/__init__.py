"""
Sensor abstraction layer for the Sonar System.

This module provides a clean abstraction over different sensor types,
allowing the visualization layer to work with any sensor that implements
the BaseSensor interface.
"""

from .base_sensor import BaseSensor
from .ultrasonic_sensor import UltrasonicSensor
from .mock_sensor import MockSensor, ScenarioPresets

__all__ = ["BaseSensor", "UltrasonicSensor", "MockSensor", "ScenarioPresets"]
