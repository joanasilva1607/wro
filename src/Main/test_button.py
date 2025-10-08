"""
Test script for button functionality
Tests the button on pin GP22 with internal pull-up resistor
"""

import time
from robot_controller import RobotController

def test_button():
    """Test button functionality."""
    print("Button Test Starting...")
    
    # Create robot controller
    robot = RobotController()
    
    try:
        # Initialize robot (this will also initialize the button)
        print("Initializing robot...")
        if not robot.initialize():
            print("Failed to initialize robot!")
            return
            
        print("Robot initialized successfully!")
        print("Button is on pin GP22 with internal pull-up resistor")
        print("Press the button to test, or Ctrl+C to exit")
        
        # Test button for 30 seconds
        start_time = time.time()
        button_press_count = 0
        
        while time.time() - start_time < 30:
            if robot.is_button_pressed():
                button_press_count += 1
                print(f"Button pressed! (Press #{button_press_count})")
                
                # Wait for button release to avoid multiple counts
                while robot.is_button_pressed():
                    time.sleep(0.01)
                    
            time.sleep(0.01)  # Small delay to prevent busy waiting
            
        print(f"\nTest completed! Button was pressed {button_press_count} times.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        robot.shutdown()
        print("Button test ended.")

if __name__ == "__main__":
    test_button()

