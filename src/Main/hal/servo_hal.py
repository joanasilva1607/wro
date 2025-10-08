"""
Servo Hardware Abstraction Layer
Provides a clean interface for servo motor control with safety features.
"""

from machine import Pin, PWM
from .base_hal import BaseHAL


class ServoHAL(BaseHAL):
    """Hardware abstraction layer for servo motor control."""
    
    def __init__(self, pin=3, servo_pwm_freq=50, min_u16_duty=1802, max_u16_duty=7864,
                 center_steering=91, max_steering_offset=11):
        """
        Initialize servo HAL.
        
        Args:
            pin: GPIO pin number for servo control
            servo_pwm_freq: PWM frequency for servo control
            min_u16_duty: Minimum PWM duty cycle value
            max_u16_duty: Maximum PWM duty cycle value
            center_steering: Center position angle
            max_steering_offset: Maximum offset from center
        """
        super().__init__()
        self.pin = pin
        self.servo_pwm_freq = servo_pwm_freq
        self.min_u16_duty = min_u16_duty
        self.max_u16_duty = max_u16_duty
        self.center_steering = center_steering
        self.max_steering_offset = max_steering_offset
        
        # Calculate angle limits
        self.min_angle = center_steering - max_steering_offset
        self.max_angle = center_steering + max_steering_offset
        
        # Current state
        self._current_angle = 0.001  # Slightly off to force initial movement
        self._target_angle = center_steering
        
        # Hardware component
        self._motor = None
        self._angle_conversion_factor = 0
        
    def initialize(self):
        """Initialize servo hardware."""
        try:
            self._angle_conversion_factor = (
                (self.max_u16_duty - self.min_u16_duty) / 
                (self.max_angle - self.min_angle)
            )
            
            self._motor = PWM(Pin(self.pin))
            self._motor.freq(self.servo_pwm_freq)
            
            # Move to center position
            self.move_to_center()
            self._is_initialized = True
            
        except Exception as e:
            self._handle_error(f"Servo initialization failed: {e}")
            
    def move(self, angle):
        """
        Move servo to specified angle.
        
        Args:
            angle: Target angle in degrees
        """
        if not self._is_initialized:
            self._handle_error("Servo not initialized")
            return
            
        # Round to 2 decimal places to reduce unnecessary adjustments
        angle = round(angle, 2)
        
        # Apply safety limits
        angle = max(self.min_angle, min(self.max_angle, angle))
        
        # Check if movement is necessary
        if angle == self._current_angle:
            return
            
        try:
            # Calculate duty cycle and move
            duty_u16 = self._angle_to_u16_duty(angle)
            self._motor.duty_u16(duty_u16)
            
            # Update state
            self._current_angle = angle
            self._target_angle = angle
            
        except Exception as e:
            self._handle_error(f"Servo movement failed: {e}")
            
    def move_to_center(self):
        """Move servo to center position."""
        self.move(self.center_steering)
        
    def move_left(self, offset=None):
        """Move servo left by specified offset or maximum."""
        if offset is None:
            offset = self.max_steering_offset
        target_angle = self.center_steering - offset
        self.move(target_angle)
        
    def move_right(self, offset=None):
        """Move servo right by specified offset or maximum."""
        if offset is None:
            offset = self.max_steering_offset
        target_angle = self.center_steering + offset
        self.move(target_angle)
        
    def get_current_angle(self):
        """Get current servo angle."""
        return self._current_angle
        
    def get_target_angle(self):
        """Get target servo angle."""
        return self._target_angle
        
    def is_at_center(self):
        """Check if servo is at center position."""
        return abs(self._current_angle - self.center_steering) < 0.1
        
    def get_angle_limits(self):
        """Get servo angle limits."""
        return self.min_angle, self.max_angle
        
    def update_settings(self, servo_pwm_freq=None, min_u16_duty=None, 
                       max_u16_duty=None, min_angle=None, max_angle=None):
        """Update servo settings dynamically."""
        if servo_pwm_freq is not None:
            self.servo_pwm_freq = servo_pwm_freq
        if min_u16_duty is not None:
            self.min_u16_duty = min_u16_duty
        if max_u16_duty is not None:
            self.max_u16_duty = max_u16_duty
        if min_angle is not None:
            self.min_angle = min_angle
        if max_angle is not None:
            self.max_angle = max_angle
            
        # Recalculate conversion factor
        if self._is_initialized:
            self._angle_conversion_factor = (
                (self.max_u16_duty - self.min_u16_duty) / 
                (self.max_angle - self.min_angle)
            )
            
    def _angle_to_u16_duty(self, angle):
        """Convert angle to PWM duty cycle value."""
        return int(
            (angle - self.min_angle) * self._angle_conversion_factor
        ) + self.min_u16_duty
        
    def deinitialize(self):
        """Safely deinitialize servo hardware."""
        if self._is_initialized:
            self.move_to_center()
            if self._motor:
                self._motor.deinit()
            self._is_initialized = False
