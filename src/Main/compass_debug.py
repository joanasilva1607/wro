#!/usr/bin/env python3
"""
Compass Debug Script
Comprehensive testing and diagnostics for compass issues.
"""

import time
import sys
from hal.compass_hal import CompassHAL
from config import get_config

def test_i2c_scan():
    """Scan I2C bus for devices."""
    print("=== I2C Bus Scan ===")
    try:
        from machine import Pin, I2C
        
        # Try different I2C configurations
        i2c_configs = [
            {"id": 1, "scl": 15, "sda": 14},  # Default from config
            {"id": 0, "scl": 5, "sda": 4},   # Alternative bus
            {"id": 1, "scl": 7, "sda": 6},   # Alternative pins
        ]
        
        for config in i2c_configs:
            try:
                print(f"\nTrying I2C{config['id']} (SCL={config['scl']}, SDA={config['sda']})...")
                i2c = I2C(config['id'], scl=Pin(config['scl']), sda=Pin(config['sda']))
                devices = i2c.scan()
                
                if devices:
                    print(f"  Found devices: {[hex(addr) for addr in devices]}")
                    return config, devices
                else:
                    print("  No devices found")
                    
            except Exception as e:
                print(f"  Error: {e}")
                
    except ImportError:
        print("Cannot import machine module - running on non-MicroPython platform")
        return None, []
        
    print("No I2C devices found on any configuration")
    return None, []

def test_compass_addresses(i2c_config, found_devices):
    """Test specific compass addresses."""
    print("\n=== Compass Address Testing ===")
    
    if not i2c_config:
        print("No working I2C configuration found")
        return None
        
    try:
        from machine import Pin, I2C
        i2c = I2C(i2c_config['id'], scl=Pin(i2c_config['scl']), sda=Pin(i2c_config['sda']))
        
        # Common compass addresses and their typical registers
        compass_addresses = {
            0x60: {"name": "CMPS12", "reg": 0x02, "description": "CMPS12 Tilt Compensated Compass"},
            0x1E: {"name": "HMC5883L", "reg": 0x03, "description": "HMC5883L 3-Axis Magnetometer"},
            0x42: {"name": "CMPS11", "reg": 0x02, "description": "CMPS11 Tilt Compensated Compass"},
            0x0C: {"name": "AK8975", "reg": 0x03, "description": "AK8975 3-axis Magnetometer"},
            0x1C: {"name": "LSM303", "reg": 0x28, "description": "LSM303 Accelerometer/Magnetometer"},
        }
        
        working_addresses = []
        
        for addr in found_devices:
            if addr in compass_addresses:
                info = compass_addresses[addr]
                print(f"\nTesting {info['name']} at address {hex(addr)}...")
                print(f"  Description: {info['description']}")
                
                try:
                    # Try to read from the typical register
                    data = i2c.readfrom_mem(addr, info['reg'], 2)
                    if data and len(data) == 2:
                        raw_value = (data[0] << 8) | data[1]
                        heading = raw_value / 10.0 if addr in [0x60, 0x42] else raw_value
                        print(f"  SUCCESS: Read data={data}, raw={raw_value}, heading={heading:.1f}°")
                        working_addresses.append((addr, info))
                    else:
                        print(f"  FAILED: Invalid data length: {len(data) if data else 'None'}")
                        
                except Exception as e:
                    print(f"  FAILED: {e}")
            else:
                print(f"\nUnknown device at {hex(addr)} - testing as generic compass...")
                # Try common compass registers
                for reg in [0x02, 0x03, 0x28]:
                    try:
                        data = i2c.readfrom_mem(addr, reg, 2)
                        if data and len(data) == 2:
                            raw_value = (data[0] << 8) | data[1]
                            print(f"  Register {hex(reg)}: data={data}, raw={raw_value}")
                    except:
                        pass
        
        return working_addresses
        
    except Exception as e:
        print(f"Error during address testing: {e}")
        return None

def test_compass_initialization():
    """Test compass initialization with different configurations."""
    print("\n=== Compass Initialization Test ===")
    
    # Get default configuration
    config = get_config()
    compass_config = config.get_hardware_config('compass')
    print(f"Default config: {compass_config}")
    
    # Test configurations to try
    test_configs = [
        compass_config,  # Default from config
        {"i2c_id": 1, "sda_pin": 14, "scl_pin": 15, "addr": None, "reg": 0x02},  # Auto-detect
        {"i2c_id": 1, "sda_pin": 14, "scl_pin": 15, "addr": 0x60, "reg": 0x02},  # CMPS12
        {"i2c_id": 1, "sda_pin": 14, "scl_pin": 15, "addr": 0x1E, "reg": 0x03},  # HMC5883L
        {"i2c_id": 0, "sda_pin": 4, "scl_pin": 5, "addr": None, "reg": 0x02},    # Different bus
    ]
    
    for i, test_config in enumerate(test_configs):
        print(f"\n--- Test Configuration {i+1} ---")
        print(f"Config: {test_config}")
        
        try:
            compass = CompassHAL(**test_config)
            compass.initialize()
            
            if compass.is_initialized():
                print("✓ Initialization SUCCESS")
                
                # Test basic reading
                heading = compass.get_heading()
                if heading is not None:
                    print(f"✓ Reading SUCCESS: {heading:.1f}°")
                    
                    # Test multiple readings
                    print("Taking 5 readings...")
                    for j in range(5):
                        h = compass.get_heading()
                        time.sleep(0.1)
                        print(f"  Reading {j+1}: {h:.1f}°" if h is not None else f"  Reading {j+1}: FAILED")
                        
                    return compass  # Return working compass
                else:
                    print("✗ Reading FAILED")
            else:
                print("✗ Initialization FAILED")
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            
        # Clean up
        try:
            compass.deinitialize()
        except:
            pass
            
    return None

def test_compass_debug_info(compass):
    """Test compass debug functions."""
    print("\n=== Compass Debug Information ===")
    
    if not compass or not compass.is_initialized():
        print("No working compass available")
        return
        
    try:
        debug_info = compass.read_debug()
        print("Debug info:")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
            
        # Test calibration
        print("\nTesting calibration...")
        old_offset = compass.get_angle_offset()
        result = compass.calibrate()
        new_offset = compass.get_angle_offset()
        print(f"Calibration {'SUCCESS' if result else 'FAILED'}")
        print(f"Offset changed from {old_offset:.1f}° to {new_offset:.1f}°")
        
        # Test relative heading
        print("\nTesting relative heading...")
        for i in range(3):
            abs_heading = compass.get_heading()
            rel_heading = compass.get_relative_heading()
            filtered_heading = compass.get_filtered_heading()
            
            print(f"  Reading {i+1}: Absolute={abs_heading:.1f}°, Relative={rel_heading:.1f}°, Filtered={filtered_heading:.1f}°")
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Debug test failed: {e}")

def main():
    """Main compass debugging function."""
    print("=== COMPASS DEBUGGING SCRIPT ===")
    print("This script will systematically test your compass hardware\n")
    
    # Step 1: Scan I2C bus
    i2c_config, found_devices = test_i2c_scan()
    
    # Step 2: Test compass addresses
    working_addresses = test_compass_addresses(i2c_config, found_devices)
    
    # Step 3: Test compass initialization
    working_compass = test_compass_initialization()
    
    # Step 4: Test debug functions
    test_compass_debug_info(working_compass)
    
    # Summary
    print("\n=== SUMMARY ===")
    if working_compass:
        print("✓ Compass is working!")
        print("✓ Issue may be in robot controller or main application")
        print("\nRecommendations:")
        print("1. Check robot controller compass integration")
        print("2. Verify compass configuration in config.py")
        print("3. Check for interference from other hardware")
    else:
        print("✗ Compass is not working")
        print("\nPossible causes:")
        print("1. Hardware connection issues (check I2C wiring)")
        print("2. Wrong I2C configuration (pins, bus ID)")
        print("3. Faulty compass module")
        print("4. Power supply issues")
        print("5. I2C bus conflicts with other devices")
        
        if found_devices:
            print(f"\nFound I2C devices: {[hex(addr) for addr in found_devices]}")
            print("Check if any of these could be your compass with wrong address/register")
        else:
            print("\nNo I2C devices found - check wiring and power")
    
    # Cleanup
    if working_compass:
        try:
            working_compass.deinitialize()
        except:
            pass

if __name__ == "__main__":
    main()
