"""
Comprehensive button test to diagnose boot sequence issues
"""

import time
from robot_controller import RobotController

def test_button_comprehensive():
    """Comprehensive test of button functionality."""
    print("=== Comprehensive Button Test ===")
    print("This test will help diagnose the button boot sequence issue")
    print()
    
    # Create robot controller
    robot = RobotController()
    
    try:
        # Step 1: Initialize robot
        print("Step 1: Initializing robot...")
        if not robot.initialize():
            print("FAILED: Robot initialization failed!")
            return
        print("SUCCESS: Robot initialized!")
        print()
        
        # Step 2: Check button HAL initialization
        print("Step 2: Checking button HAL...")
        button_hal = robot._button_hal
        print(f"Button HAL initialized: {button_hal.is_initialized()}")
        if button_hal.is_initialized():
            debug_info = button_hal.debug_info()
            print(f"Button debug info: {debug_info}")
        print()
        
        # Step 3: Test immediate button state
        print("Step 3: Testing immediate button state...")
        is_pressed = robot.is_button_pressed()
        print(f"Button currently pressed: {is_pressed}")
        print()
        
        # Step 4: Test button state changes
        print("Step 4: Testing button state changes for 5 seconds...")
        print("Press and release the button during this test...")
        
        start_time = time.time()
        last_state = None
        change_count = 0
        
        while time.time() - start_time < 5:
            current_state = robot.is_button_pressed()
            if current_state != last_state:
                change_count += 1
                status = "PRESSED" if current_state else "NOT PRESSED"
                print(f"Change #{change_count}: Button {status}")
                last_state = current_state
            time.sleep(0.1)
            
        print(f"Detected {change_count} state changes in 5 seconds")
        print()
        
        # Step 5: Test wait_for_button_press with short timeout
        print("Step 5: Testing wait_for_button_press with 3 second timeout...")
        print("Press the button now (or hold it if already pressed)...")
        
        start_time = time.time()
        result = robot.wait_for_button_press(timeout_ms=3000)
        elapsed = time.time() - start_time
        
        print(f"Result: {result}")
        print(f"Time elapsed: {elapsed:.2f} seconds")
        
        if result:
            print("SUCCESS: Button press detected!")
        else:
            print("FAILED: No button press detected")
            print()
            print("Debugging information:")
            debug_info = robot._button_hal.debug_info()
            print(f"Final button debug info: {debug_info}")
            
            # Test raw pin reading
            if robot._button_hal.button:
                raw_value = robot._button_hal.button.value()
                print(f"Raw pin value: {raw_value}")
                print("Expected: 0 for pressed (with pull-up), 1 for not pressed")
        
        print()
        
        # Step 6: Test the exact boot sequence
        print("Step 6: Testing exact boot sequence...")
        print("This simulates the exact code from main.py")
        
        # Check for button press at startup (exact code from main.py)
        print("\nChecking for button press on pin GP22...")
        print("Press and hold the button to run Open Challenge directly, or wait 3 seconds for menu...")
        
        # Debug: Check button state before waiting
        print(f"DEBUG: Button currently pressed: {robot.is_button_pressed()}")
        print("DEBUG: Starting 3-second button wait...")
        
        # Wait for button press with 3 second timeout
        if robot.wait_for_button_press(timeout_ms=3000):
            print("\nButton pressed! Starting Open Challenge immediately...")
            print("SUCCESS: Boot sequence would start Open Challenge")
        else:
            print("\nNo button press detected. Would show menu...")
            print("FAILED: Boot sequence would show menu instead of starting challenge")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        robot.shutdown()
        print("\nTest completed.")

if __name__ == "__main__":
    test_button_comprehensive()
