"""
Motor Hardware Abstraction Layer
Provides a clean interface for motor control, abstracting hardware-specific implementations.
"""

from machine import Pin, PWM
from .base_hal import BaseHAL


class MotorHAL(BaseHAL):
    """Hardware abstraction layer for motor control."""
    
    def __init__(self, pwm_pin=0, dir_pin1=1, dir_pin2=2, pwm_freq=1000):
        """
        Initialize motor HAL.
        
        Args:
            pwm_pin: PWM pin number for speed control
            dir_pin1: Direction control pin 1
            dir_pin2: Direction control pin 2
            pwm_freq: PWM frequency in Hz
        """
        super().__init__()
        self.pwm_pin = pwm_pin
        self.dir_pin1 = dir_pin1
        self.dir_pin2 = dir_pin2
        self.pwm_freq = pwm_freq
        
        # Motor state
        self._current_speed = 0.0
        self._current_direction = 0  # 1: forward, -1: backward, 0: stopped
        
        # Hardware components
        self._m1 = None
        self._m2 = None
        self._m_pwm = None
        
    def initialize(self):
        """Initialize motor hardware components."""
        try:
            self._m1 = Pin(self.dir_pin1, Pin.OUT)
            self._m2 = Pin(self.dir_pin2, Pin.OUT)
            self._m_pwm = PWM(Pin(self.pwm_pin))
            self._m_pwm.freq(self.pwm_freq)
            
            # Ensure motor is stopped on initialization
            self.stop()
            self._is_initialized = True
            
        except Exception as e:
            self._handle_error(f"Motor initialization failed: {e}")
            
    def set_speed(self, speed, direction=1):
        """
        Set motor speed and direction.
        
        Args:
            speed: Speed value between 0.0 and 1.0
            direction: 1 for forward, -1 for backward
        """
        if not self._is_initialized:
            self._handle_error("Motor not initialized")
            return
            
        # Validate inputs
        speed = max(0.0, min(1.0, abs(speed)))
        direction = 1 if direction >= 0 else -1
        
        try:
            if speed == 0:
                self.stop()
                return
                
            # Set direction pins
            if direction == 1:  # Forward
                self._m1.value(0)
                self._m2.value(1)
            else:  # Backward
                self._m1.value(1)
                self._m2.value(0)
                
            # Set PWM duty cycle
            duty_cycle = int(speed * 65535)
            self._m_pwm.duty_u16(duty_cycle)
            
            # Update state
            self._current_speed = speed
            self._current_direction = direction
            
        except Exception as e:
            self._handle_error(f"Motor speed setting failed: {e}")
            
    def forward(self, speed):
        """Move motor forward at specified speed."""
        self.set_speed(speed, 1)
        
    def backward(self, speed):
        """Move motor backward at specified speed."""
        self.set_speed(speed, -1)
        
    def stop(self):
        """Stop the motor."""
        if not self._is_initialized:
            return
            
        try:
            self._m1.value(0)
            self._m2.value(0)
            self._m_pwm.duty_u16(0)
            
            self._current_speed = 0.0
            self._current_direction = 0
            
        except Exception as e:
            self._handle_error(f"Motor stop failed: {e}")
            
    def get_current_speed(self):
        """Get current motor speed."""
        return self._current_speed
        
    def get_current_direction(self):
        """Get current motor direction."""
        return self._current_direction
        
    def is_moving(self):
        """Check if motor is currently moving."""
        return self._current_speed > 0
        
    def deinitialize(self):
        """Safely deinitialize motor hardware."""
        if self._is_initialized:
            self.stop()
            if self._m_pwm:
                self._m_pwm.deinit()
            self._is_initialized = False
