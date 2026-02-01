"""
Serial Manager - Thread-safe serial communication handler with auto-reconnect
"""

import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal


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


def find_arduino_port() -> str:
    """
    Try to automatically find Arduino port.
    
    Returns:
        Port name or None if not found
    """
    for port in serial.tools.list_ports.comports():
        desc = port.description.lower()
        if any(x in desc for x in ['arduino', 'ch340', 'cp210', 'usb serial', 'usb-serial']):
            return port.device
    return None


class SerialManager(QThread):
    """
    Background thread for reading serial data from Arduino.
    Features auto-reconnect and port scanning.
    
    Signals:
        data_received(angle: int, distance: int): Emitted when valid data is received
        connection_changed(connected: bool): Emitted when connection status changes
        error_occurred(message: str): Emitted when an error occurs
        port_found(port: str): Emitted when a port is found during auto-scan
    """
    
    data_received = pyqtSignal(int, int)  # angle, distance
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    port_found = pyqtSignal(str)  # port name
    reconnect_attempt = pyqtSignal(int)  # attempt number
    
    # Auto-reconnect settings
    AUTO_RECONNECT = True
    RECONNECT_DELAY = 2.0  # seconds between reconnect attempts
    MAX_RECONNECT_ATTEMPTS = 0  # 0 = infinite
    AUTO_SCAN_PORTS = True  # Try to find Arduino automatically
    
    def __init__(self, port: str = None, baud: int = 250000, timeout: float = 0.1):
        """
        Initialize the serial manager.
        
        Args:
            port: Serial port name (e.g., "COM5"). If None, will auto-scan.
            baud: Baud rate
            timeout: Read timeout in seconds
        """
        super().__init__()
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.running = True
        self.connected = False
        self.ser = None
        self.command_queue = []
        self.reconnect_count = 0
    
    def run(self):
        """Main thread loop - connects, reads data, and auto-reconnects"""
        while self.running:
            try:
                # Auto-scan for port if not specified
                current_port = self.port
                if current_port is None and self.AUTO_SCAN_PORTS:
                    current_port = find_arduino_port()
                    if current_port:
                        self.port_found.emit(current_port)
                
                if current_port is None:
                    self.error_occurred.emit("No port specified and auto-scan failed")
                    if self.AUTO_RECONNECT:
                        time.sleep(self.RECONNECT_DELAY)
                        continue
                    else:
                        break
                
                # Try to connect
                self.ser = serial.Serial(current_port, self.baud, timeout=self.timeout)
                self.connected = True
                self.reconnect_count = 0
                self.connection_changed.emit(True)
                
                # Main read loop
                while self.running and self.connected:
                    try:
                        # Send queued commands
                        while self.command_queue:
                            cmd = self.command_queue.pop(0)
                            if self.ser and self.ser.is_open:
                                self.ser.write(f"{cmd}\n".encode())
                        
                        # Read incoming data
                        if self.ser and self.ser.in_waiting:
                            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                            self._parse_line(line)
                            
                    except serial.SerialException as e:
                        # Connection lost
                        self.connected = False
                        self.connection_changed.emit(False)
                        self.error_occurred.emit(f"Connection lost: {e}")
                        break
                    except Exception as e:
                        pass
                
                # Cleanup
                if self.ser and self.ser.is_open:
                    self.ser.close()
                    
            except serial.SerialException as e:
                self.connected = False
                self.connection_changed.emit(False)
                self.error_occurred.emit(f"Connection failed: {e}")
                
            except Exception as e:
                self.connected = False
                self.connection_changed.emit(False)
                self.error_occurred.emit(str(e))
            
            # Auto-reconnect logic
            if self.running and self.AUTO_RECONNECT:
                self.reconnect_count += 1
                
                # Check max attempts
                if self.MAX_RECONNECT_ATTEMPTS > 0 and self.reconnect_count >= self.MAX_RECONNECT_ATTEMPTS:
                    self.error_occurred.emit("Max reconnect attempts reached")
                    break
                
                self.reconnect_attempt.emit(self.reconnect_count)
                time.sleep(self.RECONNECT_DELAY)
            else:
                break
    
    def _parse_line(self, line: str):
        """Parse a line of data from Arduino"""
        if ',' in line:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    angle = int(parts[0])
                    distance = int(parts[1])
                    if 0 <= angle <= 180:
                        self.data_received.emit(angle, distance)
                except ValueError:
                    pass
    
    def send_command(self, cmd: str):
        """Queue a command to send to Arduino"""
        self.command_queue.append(cmd)
    
    def set_port(self, port: str):
        """Change the port (will reconnect)"""
        self.port = port
        if self.connected and self.ser:
            self.ser.close()
            self.connected = False
    
    def stop(self):
        """Stop the serial thread"""
        self.running = False
        self.connected = False
        if self.ser and self.ser.is_open:
            self.ser.close()
    
    def is_connected(self) -> bool:
        """Check if connected to serial port"""
        return self.connected
