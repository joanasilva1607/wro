"""
Button Hardware Abstraction Layer
Handles button input with internal pull-up resistor.
"""

import machine
from .base_hal import BaseHAL


class ButtonHAL(BaseHAL):
    """Button input HAL with internal pull-up resistor."""
    
    def __init__(self, pin=22, pull_up=True, debounce_ms=50):
        """
        Initialize button HAL.
        
        Args:
            pin: GPIO pin number for button (default: 22)
            pull_up: Enable internal pull-up resistor (default: True)
            debounce_ms: Debounce time in milliseconds (default: 50)
        """
        super().__init__()
        self.pin = pin
        self.pull_up = pull_up
        self.debounce_ms = debounce_ms
        self.button = None
        self.last_press_time = 0
        self.last_state = True  # Default to high (not pressed) with pull-up
        
    def initialize(self):
        """Initialize button hardware."""
        try:
            # Configure button pin with internal pull-up resistor
            if self.pull_up:
                self.button = machine.Pin(self.pin, machine.Pin.IN, machine.Pin.PULL_UP)
            else:
                self.button = machine.Pin(self.pin, machine.Pin.IN)
                
            self._is_initialized = True
            print(f"Button initialized on pin {self.pin} (pull-up: {self.pull_up})")
            
        except Exception as e:
            self._handle_error(f"Failed to initialize button: {e}")
            raise
            
    def deinitialize(self):
        """Deinitialize button hardware."""
        self.button = None
        self._is_initialized = False
        print("Button deinitialized")
        
    def is_pressed(self):
        """
        Check if button is currently pressed.
        
        Returns:
            bool: True if button is pressed, False otherwise
        """
        if not self._is_initialized or not self.button:
            return False
            
        # With pull-up resistor, button press = LOW (0)
        # Without pull-up resistor, button press = HIGH (1)
        raw_value = self.button.value()
        if self.pull_up:
            return raw_value == 0
        else:
            return raw_value == 1
            
    def was_pressed(self):
        """
        Check if button was pressed since last call (with debouncing).
        
        Returns:
            bool: True if button was pressed, False otherwise
        """
        if not self._is_initialized or not self.button:
            return False
            
        import time
        current_time = time.ticks_ms()
        current_state = self.is_pressed()
        
        # Check for button press (transition from not pressed to pressed)
        if current_state and not self.last_state:
            # Check debounce time
            if current_time - self.last_press_time > self.debounce_ms:
                self.last_press_time = current_time
                self.last_state = current_state
                return True
                
        # Update last_state even if not pressed to track transitions
        self.last_state = current_state
        return False
        
    def wait_for_press(self, timeout_ms=None):
        """
        Wait for button press with optional timeout.
        
        Args:
            timeout_ms: Maximum time to wait in milliseconds (None for no timeout)
            
        Returns:
            bool: True if button was pressed, False if timeout
        """
        if not self._is_initialized:
            return False
            
        import time
        start_time = time.ticks_ms()
        
        while True:
            if self.was_pressed():
                return True
                
            if timeout_ms is not None:
                if time.ticks_diff(time.ticks_ms(), start_time) >= timeout_ms:
                    return False
                    
            time.sleep_ms(10)  # Small delay to prevent busy waiting
            
    def get_state(self):
        """
        Get current button state.
        
        Returns:
            bool: Current button state (True = pressed, False = not pressed)
        """
        return self.is_pressed()
        
    def debug_info(self):
        """
        Get debug information about button state.
        
        Returns:
            dict: Debug information including raw pin value and states
        """
        if not self._is_initialized or not self.button:
            return {
                'initialized': False,
                'raw_value': None,
                'is_pressed': False,
                'last_state': self.last_state,
                'pull_up': self.pull_up
            }
            
        return {
            'initialized': True,
            'raw_value': self.button.value(),
            'is_pressed': self.is_pressed(),
            'last_state': self.last_state,
            'pull_up': self.pull_up,
            'pin': self.pin
        }

