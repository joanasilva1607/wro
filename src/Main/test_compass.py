#!/usr/bin/env python3
"""
Quick Compass Test Script
Simple test to verify compass functionality.
"""

import time
import sys
from robot_controller import RobotController

def test_compass_quick():
    """Quick compass test using robot controller."""
    print("=== Quick Compass Test ===")
    
    robot = RobotController()
    
    try:
        print("Initializing robot...")
        robot.initialize()
        
        if not robot._is_initialized:
            print("✗ Robot initialization failed!")
            return False
            
        print("✓ Robot initialized successfully")
        
        # Test compass readings
        print("\nTesting compass readings...")
        for i in range(10):
            heading = robot.get_compass_heading()
            relative = robot.get_relative_heading()
            
            if heading is not None:
                print(f"Reading {i+1}: {heading:.1f}° (relative: {relative:.1f}°)")
            else:
                print(f"Reading {i+1}: FAILED")
                
            time.sleep(0.5)
            
        # Get compass diagnostic info
        print("\nCompass diagnostic info:")
        try:
            debug_info = robot._compass_hal.read_debug()
            for key, value in debug_info.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  Debug info failed: {e}")
            
        # Test compass diagnostic
        print("\nFull compass diagnostic:")
        try:
            diag_info = robot._compass_hal.get_diagnostic_info()
            for section, data in diag_info.items():
                print(f"  {section}:")
                for key, value in data.items():
                    print(f"    {key}: {value}")
        except Exception as e:
            print(f"  Diagnostic failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
        
    finally:
        print("\nShutting down...")
        robot.shutdown()

def test_compass_direct():
    """Test compass HAL directly."""
    print("\n=== Direct Compass HAL Test ===")
    
    from hal.compass_hal import CompassHAL
    from config import get_config
    
    config = get_config()
    compass_config = config.get_hardware_config('compass')
    
    compass = CompassHAL(**compass_config)
    
    try:
        print(f"Testing with config: {compass_config}")
        compass.initialize()
        
        if compass.is_initialized():
            print("✓ Compass initialized successfully")
            
            # Test readings
            print("\nTaking readings...")
            for i in range(5):
                heading = compass.get_heading()
                print(f"Reading {i+1}: {heading:.1f}°" if heading is not None else f"Reading {i+1}: FAILED")
                time.sleep(0.2)
                
            return True
        else:
            print("✗ Compass initialization failed")
            return False
            
    except Exception as e:
        print(f"Direct test failed: {e}")
        return False
        
    finally:
        try:
            compass.deinitialize()
        except:
            pass

def main():
    """Main test function."""
    print("Starting compass tests...")
    
    # Test 1: Using robot controller
    success1 = test_compass_quick()
    
    # Test 2: Direct HAL test
    success2 = test_compass_direct()
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    print(f"Robot Controller Test: {'PASS' if success1 else 'FAIL'}")
    print(f"Direct HAL Test: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("✓ All tests passed - compass is working!")
    elif success2:
        print("⚠ Direct HAL works but robot controller has issues")
    else:
        print("✗ Compass hardware/configuration problem detected")
        print("\nNext steps:")
        print("1. Run compass_debug.py for detailed diagnostics")
        print("2. Check hardware connections (I2C wiring)")
        print("3. Verify compass module power supply")
        print("4. Check config.py settings")

if __name__ == "__main__":
    main()
