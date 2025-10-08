"""
Button troubleshooting script
Tests different configurations to identify the issue
"""

import time
import machine

def test_pin_configurations():
    """Test different pin configurations."""
    print("Button Troubleshooting")
    print("=====================")
    print("Testing different pin configurations...")
    print()
    
    # Test different pins to see if the issue is pin-specific
    test_pins = [22, 21, 20, 19, 18]  # Common GPIO pins
    
    for pin_num in test_pins:
        print(f"Testing pin {pin_num}...")
        try:
            # Test with pull-up
            pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
            initial_value = pin.value()
            print(f"  Pin {pin_num} with pull-up: {initial_value}")
            
            # Test without pull-up
            pin_no_pull = machine.Pin(pin_num, machine.Pin.IN)
            initial_value_no_pull = pin_no_pull.value()
            print(f"  Pin {pin_num} without pull-up: {initial_value_no_pull}")
            
        except Exception as e:
            print(f"  Pin {pin_num} error: {e}")
        print()

def test_button_with_different_configs():
    """Test button with different configurations."""
    print("Testing button with different configurations...")
    print()
    
    configs = [
        {"pin": 22, "pull_up": True, "name": "GP22 with pull-up"},
        {"pin": 22, "pull_up": False, "name": "GP22 without pull-up"},
        {"pin": 21, "pull_up": True, "name": "GP21 with pull-up"},
    ]
    
    for config in configs:
        print(f"Testing: {config['name']}")
        try:
            if config["pull_up"]:
                pin = machine.Pin(config["pin"], machine.Pin.IN, machine.Pin.PULL_UP)
            else:
                pin = machine.Pin(config["pin"], machine.Pin.IN)
                
            print(f"  Initial value: {pin.value()}")
            print("  Press button now (if connected to this pin)...")
            
            # Test for 3 seconds
            start_time = time.time()
            changes = 0
            last_value = pin.value()
            
            while time.time() - start_time < 3:
                current_value = pin.value()
                if current_value != last_value:
                    changes += 1
                    status = "PRESSED" if (config["pull_up"] and current_value == 0) or (not config["pull_up"] and current_value == 1) else "NOT PRESSED"
                    print(f"    Change #{changes}: {current_value} ({status})")
                    last_value = current_value
                time.sleep(0.1)
                
            print(f"  Result: {changes} changes detected")
            
        except Exception as e:
            print(f"  Error: {e}")
        print()

def test_robot_button_hal():
    """Test the robot's button HAL specifically."""
    print("Testing Robot Button HAL...")
    print()
    
    try:
        from robot_controller import RobotController
        
        robot = RobotController()
        
        print("Initializing robot...")
        if not robot.initialize():
            print("Failed to initialize robot!")
            return
            
        print("Robot initialized successfully!")
        print("Testing button HAL...")
        
        # Get debug info
        debug_info = robot._button_hal.debug_info()
        print("Button HAL Debug Info:")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        print()
        
        print("Testing for 5 seconds...")
        start_time = time.time()
        changes = 0
        
        while time.time() - start_time < 5:
            is_pressed = robot.is_button_pressed()
            was_pressed = robot._button_hal.was_pressed()
            
            if was_pressed:
                changes += 1
                print(f"Button press detected! (#{changes})")
                
            time.sleep(0.1)
            
        print(f"Result: {changes} button presses detected")
        
        robot.shutdown()
        
    except Exception as e:
        print(f"Robot HAL test error: {e}")

if __name__ == "__main__":
    print("=== Button Troubleshooting Suite ===")
    print()
    
    # Test 1: Different pin configurations
    test_pin_configurations()
    
    # Test 2: Button with different configs
    test_button_with_different_configs()
    
    # Test 3: Robot button HAL
    test_robot_button_hal()
    
    print("=== Troubleshooting Complete ===")
    print("Check the results above to identify the issue.")
