"""
Hardware Abstraction Layer Package
Provides clean interfaces for all hardware components.
"""

from .base_hal import BaseHAL, HALManager
from .motor_hal import MotorHAL
from .servo_hal import ServoHAL
from .compass_hal import CompassHAL
from .encoder_hal import EncoderHAL
from .communication_hal import CommunicationHAL
from .button_hal import ButtonHAL
from .camera_hal import CameraHAL

__all__ = [
    'BaseHAL',
    'HALManager', 
    'MotorHAL',
    'ServoHAL',
    'CompassHAL',
    'EncoderHAL',
    'CommunicationHAL',
    'ButtonHAL',
    'CameraHAL'
]
