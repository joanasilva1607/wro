#!/usr/bin/env python3
"""
Test Robot Controller Compass
Test the robot controller compass after HAL fixes.
"""

import sys
import time

def test_robot_compass():
    """Test compass through robot controller."""
    print("=== Testing Robot Controller Compass ===")
    
    try:
        # Import robot controller
        from robot_controller import RobotController
        
        # Create robot instance
        robot = RobotController()
        
        print("Initializing robot...")
        robot.initialize()
        
        if not robot._is_initialized:
            print("✗ Robot initialization failed!")
            
            # Check HAL errors
            errors = robot.get_hal_errors()
            if errors:
                print("HAL Errors found:")
                for timestamp, error in errors:
                    print(f"  {error}")
            else:
                print("No HAL errors logged")
                
            return False
            
        print("✓ Robot initialized successfully!")
        
        # Test compass specifically
        print("\nTesting compass through robot controller...")
        
        # Test compass initialization
        if robot._compass_hal.is_initialized():
            print("✓ Compass HAL initialized")
        else:
            print("✗ Compass HAL not initialized")
            return False
            
        # Test compass readings
        print("\nTaking compass readings...")
        successful_readings = 0
        
        for i in range(10):
            heading = robot.get_compass_heading()
            relative = robot.get_relative_heading()
            
            if heading is not None:
                print(f"Reading {i+1}: {heading:.1f}° (relative: {relative:.1f}°)")
                successful_readings += 1
            else:
                print(f"Reading {i+1}: FAILED")
                
            time.sleep(0.3)
            
        success_rate = (successful_readings / 10) * 100
        print(f"\nCompass success rate: {success_rate:.0f}% ({successful_readings}/10)")
        
        # Test compass debug info
        print("\nCompass debug information:")
        try:
            debug_info = robot._compass_hal.read_debug()
            for key, value in debug_info.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  Debug info failed: {e}")
            
        # Test robot status
        print("\nRobot status:")
        status = robot.get_robot_status()
        print(f"  Compass heading: {status['compass_heading']}")
        print(f"  Relative heading: {status['relative_heading']}")
        print(f"  Initialized: {status['initialized']}")
        
        return successful_readings > 7  # 70% success rate
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this on the robot with proper Python path")
        return False
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        # Clean shutdown
        try:
            robot.shutdown()
            print("Robot shut down cleanly")
        except:
            pass

def test_compass_hal_direct():
    """Test compass HAL directly."""
    print("\n=== Testing Compass HAL Directly ===")
    
    try:
        # Import compass HAL
        import sys
        sys.path.append('hal')
        from compass_hal import CompassHAL
        from config import get_config
        
        # Get config
        config = get_config()
        compass_config = config.get_hardware_config('compass')
        print(f"Using config: {compass_config}")
        
        # Create compass
        compass = CompassHAL(**compass_config)
        
        # Initialize
        print("Initializing compass HAL...")
        compass.initialize()
        
        if not compass.is_initialized():
            print("✗ Compass HAL initialization failed")
            return False
            
        print("✓ Compass HAL initialized successfully")
        
        # Test readings
        print("Taking HAL readings...")
        for i in range(5):
            heading = compass.get_heading()
            relative = compass.get_relative_heading()
            filtered = compass.get_filtered_heading()
            
            print(f"Reading {i+1}: {heading:.1f}° (rel: {relative:.1f}°, filt: {filtered:.1f}°)")
            time.sleep(0.2)
            
        return True
        
    except Exception as e:
        print(f"HAL test failed: {e}")
        return False
    finally:
        try:
            compass.deinitialize()
        except:
            pass

def main():
    """Main test function."""
    print("Testing compass integration after fixes...\n")
    
    # Test 1: HAL direct
    hal_success = test_compass_hal_direct()
    
    # Test 2: Robot controller
    robot_success = test_robot_compass()
    
    # Results
    print("\n=== FINAL RESULTS ===")
    print(f"HAL Direct Test: {'PASS' if hal_success else 'FAIL'}")
    print(f"Robot Controller Test: {'PASS' if robot_success else 'FAIL'}")
    
    if hal_success and robot_success:
        print("\n🎉 SUCCESS! Compass is now working in both HAL and Robot Controller!")
        print("Your compass issue has been resolved.")
    elif hal_success:
        print("\n⚠️  HAL works but Robot Controller has issues")
        print("Check robot controller initialization or configuration")
    else:
        print("\n❌ Still having issues - check error messages above")

if __name__ == "__main__":
    main()
