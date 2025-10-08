"""
Simple button test to identify the issue
"""

import time
import machine

def test_button_simple():
    """Simple button test with direct pin access."""
    print("Simple Button Test")
    print("=================")
    print("This test will help identify the button issue.")
    print("Button should be connected: GP22 to GND when pressed")
    print()
    
    try:
        # Configure pin 22 with pull-up
        print("Configuring pin 22 with internal pull-up resistor...")
        button_pin = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
        print("Pin configured successfully!")
        print()
        
        print("Testing for 10 seconds...")
        print("Expected behavior:")
        print("- Raw value should be 1 when button NOT pressed")
        print("- Raw value should be 0 when button IS pressed")
        print()
        print("Press the button now and watch the values...")
        print()
        
        start_time = time.time()
        last_value = None
        change_count = 0
        
        while time.time() - start_time < 10:
            current_value = button_pin.value()
            
            if current_value != last_value:
                change_count += 1
                status = "PRESSED" if current_value == 0 else "NOT PRESSED"
                print(f"Change #{change_count}: Raw value = {current_value} ({status})")
                last_value = current_value
                
            time.sleep(0.1)
            
        print()
        print(f"Test completed! {change_count} changes detected.")
        
        if change_count == 0:
            print("WARNING: No changes detected!")
            print("Possible issues:")
            print("1. Button not connected properly")
            print("2. Button not making good contact")
            print("3. Wrong pin number")
            print("4. Hardware issue")
        else:
            print("Button appears to be working!")
            
    except Exception as e:
        print(f"Error during test: {e}")
        print("This might indicate a hardware or configuration issue.")

if __name__ == "__main__":
    test_button_simple()
