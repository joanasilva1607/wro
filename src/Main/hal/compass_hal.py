"""
Compass Hardware Abstraction Layer
Provides a clean interface for compass/magnetometer sensor readings.
"""

from machine import Pin, I2C
import time
import math
try:
    from .base_hal import BaseHAL
except ImportError:
    # Fallback for direct execution
    from base_hal import BaseHAL


class CompassHAL(BaseHAL):
    """Hardware abstraction layer for CMPS12 compass module."""
    
    def __init__(self, i2c_id=1, sda_pin=14, scl_pin=15, addr=None, reg=0x02):
        """
        Initialize compass HAL.
        
        Args:
            i2c_id: I2C bus ID
            sda_pin: SDA pin number
            scl_pin: SCL pin number
            addr: I2C address (auto-detected if None)
            reg: Register address for bearing data
        """
        super().__init__()
        self.i2c_id = i2c_id
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.addr = addr
        self.reg = reg
        
        # Hardware components
        self._i2c = None
        self._address = None
        
        # Calibration and filtering
        self._angle_offset = 0.0
        self._last_valid_heading = 0.0
        self._reading_history = []
        self._max_history = 5
        
    def initialize(self):
        """Initialize compass hardware."""
        try:
            self._i2c = I2C(self.i2c_id, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin))
            self._address = self.addr if self.addr is not None else self._auto_find_address()
            
            # Set initialized flag early to allow test readings
            self._is_initialized = True
            
            # Test reading to verify connection
            test_reading = self._read_raw()
            if test_reading is None:
                self._is_initialized = False
                raise Exception("Cannot read from compass")
                
            # Initialize calibration - use current heading as reference
            current_heading = self.get_heading()
            if current_heading is not None:
                self._angle_offset = current_heading + 180
            else:
                self._angle_offset = 0.0
                
        except Exception as e:
            self._is_initialized = False
            self._handle_error(f"Compass initialization failed: {e}")
            
    def _auto_find_address(self):
        """Auto-detect compass I2C address."""
        # First scan for all available I2C devices
        try:
            available_devices = self._i2c.scan()
            if not available_devices:
                raise Exception("No I2C devices found")
        except Exception:
            available_devices = []
            
        # Common compass addresses in order of priority
        candidates = [0x60, 0x1E, 0x42, 0x0C, 0x1C]
        
        # Test each candidate address that's actually present
        for addr in candidates:
            if addr in available_devices:
                try:
                    # Try to read compass data
                    data = self._i2c.readfrom_mem(addr, self.reg, 2)
                    if data and len(data) == 2:
                        # Additional validation - check if reading makes sense
                        raw_value = (data[0] << 8) | data[1]
                        heading = raw_value / 10.0
                        if 0 <= heading <= 360:
                            print(f"Found compass at address {hex(addr)} with heading {heading:.1f}°")
                            return addr
                except Exception:
                    continue
                    
        # If no candidates worked, try any other devices found
        for addr in available_devices:
            if addr not in candidates:
                try:
                    data = self._i2c.readfrom_mem(addr, self.reg, 2)
                    if data and len(data) == 2:
                        print(f"Found potential compass at address {hex(addr)}")
                        return addr
                except Exception:
                    continue
                    
        # Last resort - return default
        print("No compass found, using default address 0x60")
        return 0x60
        
    def _read_raw(self):
        """Read raw 16-bit value from compass register."""
        if not self._is_initialized:
            return None
            
        try:
            data = self._i2c.readfrom_mem(self._address, self.reg, 2)
            if len(data) != 2:
                self._handle_error(f"Compass read returned {len(data)} bytes instead of 2")
                return None
            return (data[0] << 8) | data[1]
        except OSError as e:
            # I2C communication error
            self._handle_error(f"Compass I2C communication failed: {e}")
            return None
        except Exception as e:
            self._handle_error(f"Compass raw read failed: {e}")
            return None
            
    def get_heading(self):
        """
        Get compass heading in degrees (0.0 to 359.9).
        
        Returns:
            Heading in degrees or None if reading fails
        """
        raw = self._read_raw()
        if raw is None:
            return self._last_valid_heading  # Return last valid reading
            
        # Convert raw value to degrees
        heading = raw / 10.0
        
        # Validate and filter reading
        if self._is_valid_heading(heading):
            self._update_history(heading)
            self._last_valid_heading = heading
            return heading
        else:
            return self._last_valid_heading
            
    def get_heading_radians(self):
        """Get compass heading in radians."""
        heading = self.get_heading()
        if heading is None:
            return None
        return heading * (math.pi / 180.0)
        
    def get_relative_heading(self):
        """Get heading relative to initialization offset."""
        raw_heading = self.get_heading()
        if raw_heading is None:
            return None
            
        bearing = raw_heading - (self._angle_offset % 360.0)
        
        # Normalize to 0-360 range
        if bearing >= 360.0:
            bearing -= 360.0
        elif bearing < 0:
            bearing += 360.0
            
        return bearing
        
    def set_angle_offset(self, offset):
        """Set angle offset for relative heading calculations."""
        self._angle_offset = offset
        
    def get_angle_offset(self):
        """Get current angle offset."""
        return self._angle_offset
        
    def calibrate(self):
        """Calibrate compass using current heading as reference."""
        current_heading = self.get_heading()
        if current_heading is not None:
            self._angle_offset = current_heading + 180
            return True
        return False
        
    def get_filtered_heading(self):
        """Get filtered heading using moving average."""
        if len(self._reading_history) < 2:
            return self.get_heading()
            
        return sum(self._reading_history) / len(self._reading_history)
        
    def _is_valid_heading(self, heading):
        """Validate heading reading."""
        if heading is None or heading < 0 or heading >= 360:
            return False
            
        # Check for reasonable change from last reading
        if self._last_valid_heading is not None and self._last_valid_heading != 0.0:
            diff = abs(heading - self._last_valid_heading)
            if diff > 180:  # Handle wraparound
                diff = 360 - diff
            if diff > 90:  # More tolerant threshold for magnetic interference
                # Only log as warning, don't reject unless extremely large
                if diff > 150:
                    self._handle_error(f"Compass reading jumped {diff:.1f}° (from {self._last_valid_heading:.1f}° to {heading:.1f}°)")
                    return False
                else:
                    # Accept but log for debugging
                    print(f"Compass warning: Large change {diff:.1f}° (from {self._last_valid_heading:.1f}° to {heading:.1f}°)")
                    return True
        
        # Accept first reading after initialization (when last_valid is 0.0)        
        return True
        
    def _update_history(self, heading):
        """Update reading history for filtering."""
        self._reading_history.append(heading)
        if len(self._reading_history) > self._max_history:
            self._reading_history.pop(0)
            
    def read_debug(self):
        """Return debug information."""
        raw = self._read_raw()
        heading = self.get_heading()
        return {
            'raw': raw,
            'heading': heading,
            'relative_heading': self.get_relative_heading(),
            'offset': self._angle_offset,
            'address': hex(self._address) if self._address else None,
            'i2c_config': f"I2C{self.i2c_id}(SDA={self.sda_pin}, SCL={self.scl_pin})",
            'register': hex(self.reg),
            'history_length': len(self._reading_history),
            'last_valid': self._last_valid_heading,
            'is_initialized': self._is_initialized
        }
        
    def get_diagnostic_info(self):
        """Get comprehensive diagnostic information."""
        try:
            # Try to scan I2C bus
            devices = self._i2c.scan() if self._i2c else []
        except:
            devices = "scan_failed"
            
        return {
            'config': {
                'i2c_id': self.i2c_id,
                'sda_pin': self.sda_pin, 
                'scl_pin': self.scl_pin,
                'address': hex(self.addr) if self.addr else "auto-detect",
                'register': hex(self.reg)
            },
            'status': {
                'initialized': self._is_initialized,
                'detected_address': hex(self._address) if self._address else None,
                'i2c_devices': [hex(d) for d in devices] if isinstance(devices, list) else devices
            },
            'readings': {
                'current_raw': self._read_raw(),
                'current_heading': self.get_heading(),
                'relative_heading': self.get_relative_heading(),
                'filtered_heading': self.get_filtered_heading(),
                'last_valid': self._last_valid_heading,
                'history_count': len(self._reading_history)
            },
            'calibration': {
                'angle_offset': self._angle_offset
            }
        }
        
    def reset_calibration(self):
        """Reset compass calibration."""
        self._angle_offset = 0.0
        self._reading_history.clear()
        
    def deinitialize(self):
        """Deinitialize compass hardware."""
        if self._is_initialized:
            self._i2c = None
            self._is_initialized = False
