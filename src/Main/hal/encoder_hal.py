"""
Encoder Hardware Abstraction Layer
Provides a clean interface for rotary encoder readings and distance calculations.
"""

from machine import Pin
from .base_hal import BaseHAL


class EncoderHAL(BaseHAL):
    """Hardware abstraction layer for rotary encoder."""
    
    def __init__(self, pin_a=7, pin_b=6, steps_per_cm=67.28):
        """
        Initialize encoder HAL.
        
        Args:
            pin_a: Encoder A signal pin (DT)
            pin_b: Encoder B signal pin (CLK)
            steps_per_cm: Number of encoder steps per centimeter
        """
        super().__init__()
        self.pin_a_num = pin_a
        self.pin_b_num = pin_b
        self.steps_per_cm = steps_per_cm
        
        # Hardware components
        self._pin_a = None
        self._pin_b = None
        
        # Position tracking
        self._position = 0
        self._last_state = 0
        self._motor_direction = 1  # 1: forward, -1: backward
        
        # Distance calculations
        self._initial_position = 0
        self._position_history = []
        self._max_history = 10
        
    def initialize(self):
        """Initialize encoder hardware."""
        try:
            self._pin_a = Pin(self.pin_a_num, Pin.IN, Pin.PULL_UP)
            self._pin_b = Pin(self.pin_b_num, Pin.IN, Pin.PULL_UP)
            
            self._last_state = self._pin_a.value()
            
            # Set up interrupt on A signal
            self._pin_a.irq(
                trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, 
                handler=self._handle_encoder_interrupt
            )
            
            # Reset position counters
            self.reset_position()
            self._is_initialized = True
            
        except Exception as e:
            self._handle_error(f"Encoder initialization failed: {e}")
            
    def _handle_encoder_interrupt(self, pin):
        """Handle encoder interrupt."""
        try:
            a_val = self._pin_a.value()
            
            if a_val != self._last_state:
                self._position += self._motor_direction
                self._last_state = a_val
                self._update_history()
                
        except Exception as e:
            self._handle_error(f"Encoder interrupt failed: {e}")
            
    def set_motor_direction(self, direction):
        """
        Set motor direction for position calculation.
        
        Args:
            direction: 1 for forward, -1 for backward
        """
        self._motor_direction = 1 if direction >= 0 else -1
        
    def get_motor_direction(self):
        """Get current motor direction."""
        return self._motor_direction
        
    def get_position(self):
        """Get current encoder position (steps)."""
        return self._position
        
    def get_distance_cm(self):
        """Get distance traveled in centimeters."""
        return self._position / self.steps_per_cm
        
    def get_distance_mm(self):
        """Get distance traveled in millimeters."""
        return self.get_distance_cm() * 10
        
    def reset_position(self):
        """Reset position counter to zero."""
        self._position = 0
        self._initial_position = 0
        self._position_history.clear()
        
    def set_reference_position(self):
        """Set current position as reference point."""
        self._initial_position = self._position
        
    def get_relative_distance_cm(self):
        """Get distance from reference position in centimeters."""
        relative_position = self._position - self._initial_position
        return relative_position / self.steps_per_cm
        
    def get_speed_estimate(self):
        """
        Estimate current speed based on recent position changes.
        
        Returns:
            Speed in cm/s (approximate)
        """
        if len(self._position_history) < 2:
            return 0.0
            
        # Calculate position change over recent history
        recent_change = self._position_history[-1] - self._position_history[0]
        time_span = len(self._position_history) * 0.01  # Assuming 10ms intervals
        
        if time_span > 0:
            steps_per_second = recent_change / time_span
            return steps_per_second / self.steps_per_cm
        return 0.0
        
    def calibrate_steps_per_cm(self, known_distance_cm):
        """
        Calibrate steps per centimeter using a known distance.
        
        Args:
            known_distance_cm: Actual distance traveled in cm
        """
        if self._position != 0:
            self.steps_per_cm = abs(self._position) / known_distance_cm
            return True
        return False
        
    def get_calibration_info(self):
        """Get calibration information."""
        return {
            'steps_per_cm': self.steps_per_cm,
            'current_position': self._position,
            'current_distance_cm': self.get_distance_cm(),
            'motor_direction': self._motor_direction,
            'history_length': len(self._position_history)
        }
        
    def _update_history(self):
        """Update position history for speed estimation."""
        self._position_history.append(self._position)
        if len(self._position_history) > self._max_history:
            self._position_history.pop(0)
            
    def is_moving(self):
        """Check if encoder is detecting movement."""
        if len(self._position_history) < 2:
            return False
        return self._position_history[-1] != self._position_history[-2]
        
    def get_direction_from_movement(self):
        """Determine movement direction from encoder readings."""
        if len(self._position_history) < 2:
            return 0
            
        change = self._position_history[-1] - self._position_history[-2]
        if change > 0:
            return 1
        elif change < 0:
            return -1
        return 0
        
    def deinitialize(self):
        """Deinitialize encoder hardware."""
        if self._is_initialized:
            if self._pin_a:
                self._pin_a.irq(handler=None)
            self._is_initialized = False
