"""
Simple 1D Kalman Filter - Optimal state estimation under noise.

The Kalman filter provides theoretically optimal noise reduction
when the noise characteristics are known. This simplified 1D version
is suitable for single-variable distance measurements.

Best for: Smooth tracking when you know your sensor's noise characteristics.
"""

from typing import Dict

from .base_filter import BaseFilter


class SimpleKalmanFilter(BaseFilter):
    """
    Simplified 1D Kalman Filter implementation.
    
    This is a scalar Kalman filter optimized for distance measurements.
    It balances between trusting the sensor reading and trusting the
    predicted state based on the noise parameters.
    
    Parameters:
    - process_noise (Q): How much we expect the true value to change
    - measurement_noise (R): How noisy we expect the sensor to be
    
    Higher R = trust sensor less, smoother output
    Higher Q = trust predictions less, faster response
    """
    
    NAME = "Kalman Filter"
    DESCRIPTION = "Optimal state estimation balancing prediction and measurement"
    
    def __init__(
        self,
        process_noise: float = 1.0,
        measurement_noise: float = 10.0,
        enabled: bool = True
    ):
        """
        Initialize the Kalman filter.
        
        Args:
            process_noise: Process noise covariance (Q)
            measurement_noise: Measurement noise covariance (R)
            enabled: Whether the filter is active
        """
        super().__init__(enabled)
        self.Q = process_noise       # Process noise
        self.R = measurement_noise   # Measurement noise
        
        # State for each angle: (estimate, error_covariance)
        self._state: Dict[int, tuple] = {}
    
    def _apply(self, angle: int, measurement: float) -> float:
        """
        Apply Kalman filter.
        
        Args:
            angle: Angle in degrees
            measurement: Raw sensor value
            
        Returns:
            Filtered estimate
        """
        if angle not in self._state:
            # Initialize with first measurement
            self._state[angle] = (measurement, 1.0)
            return measurement
        
        # Get previous state
        x_prev, p_prev = self._state[angle]
        
        # Prediction step (assuming constant model)
        x_pred = x_prev
        p_pred = p_prev + self.Q
        
        # Update step
        K = p_pred / (p_pred + self.R)  # Kalman gain
        x_new = x_pred + K * (measurement - x_pred)
        p_new = (1 - K) * p_pred
        
        # Save state
        self._state[angle] = (x_new, p_new)
        
        return x_new
    
    def reset(self):
        """Reset filter state."""
        self._state.clear()
    
    def set_noise_parameters(self, process_noise: float, measurement_noise: float):
        """
        Adjust noise parameters.
        
        Args:
            process_noise: New Q value
            measurement_noise: New R value
        """
        self.Q = max(0.001, process_noise)
        self.R = max(0.001, measurement_noise)
        # Don't reset state - parameters can be tuned on the fly
