"""
Camera Hardware Abstraction Layer
Reads obstacle color detection from camera via GPIO9 UART at 50 baud.
Output: '1' = Red, '2' = Green, '3' = Unknown
"""

from machine import Pin, UART
import time
from .base_hal import BaseHAL


class CameraHAL(BaseHAL):
    """Hardware abstraction layer for camera color detection."""
    
    # Color constants
    COLOR_RED = '1'
    COLOR_GREEN = '2'
    COLOR_UNKNOWN = '3'
    
    COLOR_NAMES = {
        COLOR_RED: 'Red',
        COLOR_GREEN: 'Green',
        COLOR_UNKNOWN: 'Unknown'
    }
    
    def __init__(self, uart_id=1, baudrate=50, rx_pin=9):
        """
        Initialize camera HAL.
        
        Args:
            uart_id: UART interface ID (default: 1, to avoid conflict with main UART)
            baudrate: Serial baud rate (default: 50)
            rx_pin: RX pin number (default: 9, GPIO9)
        """
        super().__init__()
        self.uart_id = uart_id
        self.baudrate = baudrate
        self.rx_pin = rx_pin
        
        # Hardware component
        self._uart = None
        
        # Current color state
        self._last_color = None
        self._last_color_time = None
        
        # Statistics
        self._color_reads = 0
        self._color_counts = {
            self.COLOR_RED: 0,
            self.COLOR_GREEN: 0,
            self.COLOR_UNKNOWN: 0
        }
        
    def initialize(self):
        """Initialize camera UART communication."""
        try:
            self._uart = UART(
                self.uart_id,
                baudrate=self.baudrate,
                rx=Pin(self.rx_pin)
            )
            
            # Clear any existing data (read all available)
            if self._uart.any():
                self._uart.read(self._uart.any())
            
            self._is_initialized = True
            print(f"Camera initialized on GPIO{self.rx_pin} (UART{self.uart_id}, {self.baudrate} baud)")
            
        except Exception as e:
            self._handle_error(f"Camera initialization failed: {e}")
            
    def deinitialize(self):
        """Deinitialize camera hardware."""
        if self._is_initialized:
            if self._uart:
                try:
                    self._uart.deinit()
                except:
                    pass
            self._is_initialized = False
            print("Camera deinitialized")
    
    def read_color(self):
        """
        Read the current obstacle color from camera.
        Reads one byte at a time.
        
        Returns:
            str: Color code ('1'=Red, '2'=Green, '3'=Unknown) or None if no data
        """
        if not self._is_initialized:
            return None
        
        try:
            available = self._uart.any()
            if not available:
                return None
            
            # Read all available bytes to ensure we capture the most recent value
            data = self._uart.read(available)
            if not data:
                return None
            
            # Iterate from latest byte backwards to find the most recent valid color
            for byte in reversed(data):
                color_code = chr(byte)
                if color_code in [self.COLOR_RED, self.COLOR_GREEN, self.COLOR_UNKNOWN]:
                    self._last_color = color_code
                    self._last_color_time = time.time()
                    self._color_reads += 1
                    self._color_counts[color_code] = self._color_counts.get(color_code, 0) + 1
                    return color_code
                else:
                    # Invalid color code received, continue searching older bytes
                    self._handle_error(f"Invalid color code received: {color_code} (byte: {byte})")
            
            return None
            
        except Exception as e:
            self._handle_error(f"Color read failed: {e}")
            return None
    
    def get_color(self):
        """
        Get the last detected color.
        
        Returns:
            str: Last color code or None if never read
        """
        return self._last_color
    
    def get_color_name(self, color_code=None):
        """
        Get human-readable color name.
        
        Args:
            color_code: Color code (default: uses last detected color)
            
        Returns:
            str: Color name or None
        """
        if color_code is None:
            color_code = self._last_color
        
        if color_code is None:
            return None
        
        return self.COLOR_NAMES.get(color_code, 'Invalid')
    
    def is_red(self):
        """
        Check if last detected color is red.
        
        Returns:
            bool: True if red, False otherwise
        """
        return self._last_color == self.COLOR_RED
    
    def is_green(self):
        """
        Check if last detected color is green.
        
        Returns:
            bool: True if green, False otherwise
        """
        return self._last_color == self.COLOR_GREEN
    
    def is_unknown(self):
        """
        Check if last detected color is unknown.
        
        Returns:
            bool: True if unknown, False otherwise
        """
        return self._last_color == self.COLOR_UNKNOWN
    
    def has_data(self):
        """Check if color data is available to read."""
        if not self._is_initialized:
            return False
        return self._uart.any() > 0
    
    def wait_for_color(self, timeout=None):
        """
        Wait for a color reading with optional timeout.
        
        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            str: Color code or None if timeout
        """
        start_time = time.time()
        
        while True:
            color = self.read_color()
            if color is not None:
                return color
            
            if timeout is not None:
                if time.time() - start_time >= timeout:
                    return None
            
            time.sleep(0.01)  # Small delay to prevent busy waiting
    
    def get_statistics(self):
        """Get camera statistics."""
        return {
            'total_reads': self._color_reads,
            'last_color': self._last_color,
            'last_color_name': self.get_color_name(),
            'last_color_time': self._last_color_time,
            'color_counts': self._color_counts.copy(),
            'red_count': self._color_counts.get(self.COLOR_RED, 0),
            'green_count': self._color_counts.get(self.COLOR_GREEN, 0),
            'unknown_count': self._color_counts.get(self.COLOR_UNKNOWN, 0)
        }
    
    def reset_statistics(self):
        """Reset camera statistics."""
        self._color_reads = 0
        self._color_counts = {
            self.COLOR_RED: 0,
            self.COLOR_GREEN: 0,
            self.COLOR_UNKNOWN: 0
        }
        print("Camera statistics reset")
    
    def flush_input(self):
        """Flush input buffer."""
        if self._is_initialized and self._uart.any():
            self._uart.read(self._uart.any())



