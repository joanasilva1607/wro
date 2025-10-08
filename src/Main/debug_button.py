"""
Debug script for button functionality
Tests the button on pin GP22 with detailed debugging information
"""

import time
import machine
from robot_controller import RobotController

def debug_button_raw():
    """Debug button with raw pin reading."""
    print("Raw Button Debug Starting...")
    print("Testing pin GP22 directly...")
    
    try:
        # Test raw pin configuration
        print("Configuring pin 22 with pull-up...")
        button_pin = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
        
        print("Pin configured. Testing for 10 seconds...")
        print("Press the button (connect to GND) to test...")
        print("Raw values: 1=not pressed, 0=pressed")
        
        start_time = time.time()
        last_value = None
        
        while time.time() - start_time < 10:
            current_value = button_pin.value()
            
            if current_value != last_value:
                print(f"Pin value changed: {current_value} ({'PRESSED' if current_value == 0 else 'NOT PRESSED'})")
                last_value = current_value
                
            time.sleep(0.1)
            
        print("Raw test completed!")
        
    except Exception as e:
        print(f"Raw test error: {e}")

def debug_button_hal():
    """Debug button using HAL."""
    print("\nHAL Button Debug Starting...")
    
    # Create robot controller
    robot = RobotController()
    
    try:
        # Initialize robot (this will also initialize the button)
        print("Initializing robot...")
        if not robot.initialize():
            print("Failed to initialize robot!")
            return
            
        print("Robot initialized successfully!")
        print("Testing button HAL for 10 seconds...")
        print("Press the button to test...")
        
        start_time = time.time()
        last_pressed = False
        press_count = 0
        
        while time.time() - start_time < 10:
            current_pressed = robot.is_button_pressed()
            
            if current_pressed != last_pressed:
                if current_pressed:
                    press_count += 1
                    print(f"Button PRESSED! (Press #{press_count})")
                else:
                    print("Button RELEASED!")
                last_pressed = current_pressed
                
            time.sleep(0.1)
            
        print(f"\nHAL test completed! Button was pressed {press_count} times.")
        
    except Exception as e:
        print(f"HAL test error: {e}")
    finally:
        robot.shutdown()
        print("HAL test ended.")

def debug_button_detailed():
    """Detailed button debugging with state tracking."""
    print("\nDetailed Button Debug Starting...")
    
    # Create robot controller
    robot = RobotController()
    
    try:
        # Initialize robot
        print("Initializing robot...")
        if not robot.initialize():
            print("Failed to initialize robot!")
            return
            
        print("Robot initialized successfully!")
        print("Detailed button testing for 15 seconds...")
        print("Watch for state changes...")
        
        start_time = time.time()
        last_state = None
        state_changes = 0
        
        while time.time() - start_time < 15:
            # Get raw pin value
            raw_value = robot._button_hal.button.value() if robot._button_hal.button else None
            is_pressed = robot.is_button_pressed()
            was_pressed = robot._button_hal.was_pressed()
            
            current_state = (raw_value, is_pressed, was_pressed)
            
            if current_state != last_state:
                state_changes += 1
                print(f"State change #{state_changes}:")
                print(f"  Raw pin value: {raw_value}")
                print(f"  is_pressed(): {is_pressed}")
                print(f"  was_pressed(): {was_pressed}")
                print(f"  Time: {time.time() - start_time:.1f}s")
                print()
                last_state = current_state
                
            time.sleep(0.05)
            
        print(f"Detailed test completed! {state_changes} state changes detected.")
        
    except Exception as e:
        print(f"Detailed test error: {e}")
    finally:
        robot.shutdown()
        print("Detailed test ended.")

if __name__ == "__main__":
    print("=== Button Debug Suite ===")
    print("This will test the button in multiple ways to identify the issue.")
    print()
    
    # Test 1: Raw pin reading
    debug_button_raw()
    
    # Test 2: HAL testing
    debug_button_hal()
    
    # Test 3: Detailed debugging
    debug_button_detailed()
    
    print("\n=== Debug Complete ===")
    print("Check the output above to identify the button issue.")
