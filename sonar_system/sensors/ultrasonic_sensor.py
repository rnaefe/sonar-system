"""
Ultrasonic Sensor - HC-SR04 sensor implementation via serial communication.

This is the real hardware sensor that communicates with an Arduino
running the sonar firmware.
"""

import time
import serial
import serial.tools.list_ports
from typing import Optional, Tuple
from PyQt5.QtCore import QThread

from .base_sensor import BaseSensor


def get_available_ports() -> list:
    """
    Get list of available serial ports.
    
    Returns:
        List of tuples: (port_name, description)
    """
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append((port.device, port.description))
    return ports


def find_arduino_port() -> Optional[str]:
    """
    Try to automatically find Arduino port.
    
    Returns:
        Port name or None if not found
    """
    keywords = ['arduino', 'ch340', 'cp210', 'usb serial', 'usb-serial', 'ft232']
    for port in serial.tools.list_ports.comports():
        desc = port.description.lower()
        if any(kw in desc for kw in keywords):
            return port.device
    return None


class UltrasonicSensor(BaseSensor):
    """
    HC-SR04 ultrasonic sensor implementation.
    
    Communicates with an Arduino over serial to receive angle and distance
    readings from an ultrasonic sensor mounted on a servo.
    
    Features:
    - Auto-reconnect on connection loss
    - Port auto-detection
    - Command queue for motor control
    """
    
    NAME = "HC-SR04 Ultrasonic"
    DESCRIPTION = "Real ultrasonic sensor via Arduino serial connection"
    
    # Auto-reconnect settings
    AUTO_RECONNECT = True
    RECONNECT_DELAY = 2.0
    MAX_RECONNECT_ATTEMPTS = 0  # 0 = infinite
    AUTO_SCAN_PORTS = True
    
    def __init__(self, port: str = None, baud_rate: int = 250000, timeout: float = 0.1):
        """
        Initialize the ultrasonic sensor.
        
        Args:
            port: Serial port name. If None, will auto-scan for Arduino.
            baud_rate: Serial baud rate (must match Arduino firmware)
            timeout: Serial read timeout in seconds
        """
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        
        self._serial = None
        self._thread = None
        self._command_queue = []
        self._latest_reading = None
        self._reconnect_count = 0
    
    def start(self) -> bool:
        """Start reading from the sensor."""
        if self._running:
            return True
        
        self._running = True
        self._thread = _SensorThread(self)
        self._thread.start()
        return True
    
    def stop(self):
        """Stop reading from the sensor."""
        self._running = False
        if self._thread:
            self._thread.wait(2000)
            self._thread = None
        
        if self._serial and self._serial.is_open:
            self._serial.close()
        
        self._connected = False
        self.connection_changed.emit(False)
    
    def get_latest_reading(self) -> Optional[Tuple[int, float]]:
        """Get the most recent sensor reading."""
        return self._latest_reading
    
    def send_command(self, command: str):
        """
        Queue a command to send to the Arduino.
        
        Args:
            command: Command string (e.g., "MODE:RADAR", "F", "S")
        """
        self._command_queue.append(command)
    
    def _connect(self) -> bool:
        """Attempt to establish serial connection."""
        current_port = self.port
        
        # Auto-scan for port if not specified
        if current_port is None and self.AUTO_SCAN_PORTS:
            current_port = find_arduino_port()
        
        if current_port is None:
            self.error_occurred.emit("No port specified and auto-scan failed")
            return False
        
        try:
            self._serial = serial.Serial(
                current_port,
                self.baud_rate,
                timeout=self.timeout
            )
            self._connected = True
            self._reconnect_count = 0
            self.connection_changed.emit(True)
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Connection failed: {e}")
            return False
    
    def _read_loop(self):
        """Main reading loop (runs in background thread)."""
        while self._running:
            try:
                # Attempt connection if not connected
                if not self._connected:
                    if not self._connect():
                        if self.AUTO_RECONNECT:
                            time.sleep(self.RECONNECT_DELAY)
                            self._reconnect_count += 1
                            continue
                        else:
                            break
                
                # Send queued commands
                while self._command_queue and self._serial and self._serial.is_open:
                    cmd = self._command_queue.pop(0)
                    self._serial.write(f"{cmd}\n".encode())
                
                # Read incoming data
                if self._serial and self._serial.in_waiting:
                    line = self._serial.readline().decode('utf-8', errors='ignore').strip()
                    self._parse_line(line)
                
            except serial.SerialException as e:
                self._connected = False
                self.connection_changed.emit(False)
                self.error_occurred.emit(f"Connection lost: {e}")
                
                if self._serial and self._serial.is_open:
                    self._serial.close()
                
            except Exception as e:
                self.error_occurred.emit(str(e))
    
    def _parse_line(self, line: str):
        """Parse a line of data from the Arduino."""
        if not line:
            return
        
        try:
            # Expected format: "angle,distance"
            if ',' in line:
                parts = line.split(',')
                if len(parts) >= 2:
                    angle = int(parts[0].strip())
                    distance = float(parts[1].strip())
                    
                    # Validate range
                    if 0 <= angle <= 180 and distance >= 0:
                        self._latest_reading = (angle, distance)
                        self.data_received.emit(angle, distance)
        except (ValueError, IndexError):
            pass  # Ignore malformed lines


class _SensorThread(QThread):
    """Background thread for sensor reading."""
    
    def __init__(self, sensor: UltrasonicSensor):
        super().__init__()
        self._sensor = sensor
    
    def run(self):
        self._sensor._read_loop()
