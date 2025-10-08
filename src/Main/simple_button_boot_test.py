"""
Simple button boot test to isolate the issue
"""

import time
import machine
from hal.button_hal import ButtonHAL

def test_button_direct():
    """Test button directly without robot controller."""
    print("=== Direct Button Test ===")
    
    # Create button HAL directly
    button_hal = ButtonHAL(pin=22, pull_up=True, debounce_ms=50)
    
    try:
        # Initialize
        print("Initializing button HAL...")
        button_hal.initialize()
        print("Button HAL initialized!")
        
        # Test immediate state
        print("\nTesting immediate button state...")
        is_pressed = button_hal.is_pressed()
        print(f"Button currently pressed: {is_pressed}")
        
        # Test debug info
        debug_info = button_hal.debug_info()
        print(f"Debug info: {debug_info}")
        
        # Test wait_for_press with timeout
        print("\nTesting wait_for_press with 3 second timeout...")
        print("Press the button now...")
        
        start_time = time.time()
        result = button_hal.wait_for_press(timeout_ms=3000)
        elapsed = time.time() - start_time
        
        print(f"Result: {result}")
        print(f"Time elapsed: {elapsed:.2f} seconds")
        
        if result:
            print("SUCCESS: Button press detected!")
        else:
            print("FAILED: No button press detected")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        button_hal.deinitialize()
        print("Test completed.")

if __name__ == "__main__":
    test_button_direct()
