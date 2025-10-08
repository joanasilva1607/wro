"""
Test button functionality specifically for boot scenarios
"""

import time
from robot_controller import RobotController

def test_button_boot():
    """Test button functionality during boot sequence simulation."""
    print("=== Button Boot Test ===")
    print("This simulates the boot sequence button check")
    print()
    
    # Create robot controller
    robot = RobotController()
    
    try:
        # Initialize robot
        print("Initializing robot...")
        if not robot.initialize():
            print("Failed to initialize robot!")
            return
        print("Robot initialized successfully!")
        print()
        
        # Test button state immediately after initialization
        print("Testing button state immediately after init...")
        is_pressed = robot.is_button_pressed()
        print(f"Button currently pressed: {is_pressed}")
        print()
        
        # Test wait_for_button_press with short timeout (like in main.py)
        print("Testing wait_for_button_press with 3 second timeout...")
        print("Press the button now (or hold it if already pressed)...")
        
        start_time = time.time()
        button_detected = robot.wait_for_button_press(timeout_ms=3000)
        elapsed_time = time.time() - start_time
        
        print(f"Button detection result: {button_detected}")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        
        if button_detected:
            print("SUCCESS: Button press detected!")
        else:
            print("FAILED: No button press detected within timeout")
            print()
            print("Debugging information:")
            debug_info = robot._button_hal.debug_info()
            print(f"Button HAL debug info: {debug_info}")
            
            # Test raw button reading
            if robot._button_hal.button:
                raw_value = robot._button_hal.button.value()
                print(f"Raw button value: {raw_value}")
                print(f"Expected: 0 for pressed (with pull-up), 1 for not pressed")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        robot.shutdown()
        print("Test completed.")

if __name__ == "__main__":
    test_button_boot()
