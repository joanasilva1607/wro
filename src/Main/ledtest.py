#!/usr/bin/env python3
"""
LED Test Script
Tests the status LED functionality.
"""

from machine import Pin
import time

def test_led():
    """Test LED functionality."""
    print("LED Test Starting...")
    
    # Initialize LED
    led = Pin(25, Pin.OUT)
    
    print("LED initialized on pin 25")
    
    # Test sequence
    print("\nTesting LED sequence:")
    print("1. LED ON (boot state)")
    led.on()
    time.sleep(1)
    
    print("2. LED OFF (initialization successful)")
    led.off()
    time.sleep(1)
    
    print("3. LED ON (shutdown/error state)")
    led.on()
    time.sleep(1)
    
    print("4. LED OFF (final state)")
    led.off()
    time.sleep(0.5)
    
    print("\nLED test complete!")
    print("LED Status: OFF")

if __name__ == "__main__":
    test_led()

