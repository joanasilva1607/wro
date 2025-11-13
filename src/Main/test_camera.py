#!/usr/bin/env python3
"""
Camera Test Script
Test the camera HAL for obstacle color detection.
"""

import time
import sys
from robot_controller import RobotController

# MicroPython-compatible exception printing
def print_exception(e):
    """Print exception in a MicroPython-compatible way."""
    try:
        import traceback
        traceback.print_exc()
    except ImportError:
        # MicroPython fallback - just print error details
        print(f"Exception: {type(e).__name__}: {e}")
        # Try to get more details if available
        try:
            import sys
            if hasattr(sys, 'print_exception'):
                # In MicroPython, we need to be in an except block to use this
                # So we'll just print what we can
                pass
        except:
            pass


def test_camera_basic():
    """Basic camera test - read colors continuously."""
    print("=== Camera Basic Test ===")
    print("Reading obstacle colors from camera...")
    print("Press Ctrl+C to stop\n")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._camera_hal.is_initialized():
            print("ERROR: Camera not initialized!")
            return
        
        print("Camera initialized successfully")
        print("Waiting for color data...\n")
        
        read_count = 0
        
        while True:
            color = robot.read_camera_color()
            
            if color:
                read_count += 1
                color_name = robot.get_camera_color_name(color)
                print(f"[{read_count}] Color detected: {color} ({color_name})")
            
            time.sleep(0.1)  # Small delay
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print_exception(e)
    finally:
        robot.shutdown()


def test_camera_statistics():
    """Test camera with statistics collection."""
    print("=== Camera Statistics Test ===")
    print("Collecting color statistics for 10 seconds...\n")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._camera_hal.is_initialized():
            print("ERROR: Camera not initialized!")
            return
        
        start_time = time.time()
        duration = 10
        
        while time.time() - start_time < duration:
            robot.read_camera_color()
            time.sleep(0.05)  # Read every 50ms
        
        # Get statistics
        stats = robot.get_camera_statistics()
        
        print("\n=== Statistics ===")
        print(f"Total reads: {stats['total_reads']}")
        print(f"Last color: {stats['last_color']} ({stats['last_color_name']})")
        print(f"\nColor counts:")
        print(f"  Red:    {stats['red_count']}")
        print(f"  Green:  {stats['green_count']}")
        print(f"  Unknown: {stats['unknown_count']}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print_exception(e)
    finally:
        robot.shutdown()


def test_camera_wait():
    """Test waiting for specific colors."""
    print("=== Camera Wait Test ===")
    print("Waiting for color detection...\n")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._camera_hal.is_initialized():
            print("ERROR: Camera not initialized!")
            return
        
        print("Waiting for first color (timeout: 5 seconds)...")
        color = robot.wait_for_camera_color(timeout=5)
        
        if color:
            color_name = robot.get_camera_color_name(color)
            print(f"✓ Color detected: {color} ({color_name})")
        else:
            print("✗ No color detected within timeout")
        
    except Exception as e:
        print(f"\nError: {e}")
        print_exception(e)
    finally:
        robot.shutdown()


def test_camera_helpers():
    """Test camera helper methods."""
    print("=== Camera Helper Methods Test ===")
    print("Testing color detection helpers...\n")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._camera_hal.is_initialized():
            print("ERROR: Camera not initialized!")
            return
        
        print("Reading colors and testing helper methods...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            color = robot.read_camera_color()
            
            if color:
                print(f"Color: {robot.get_camera_color_name()}")
                print(f"  is_obstacle_red():    {robot.is_obstacle_red()}")
                print(f"  is_obstacle_green():  {robot.is_obstacle_green()}")
                print(f"  is_obstacle_unknown(): {robot.is_obstacle_unknown()}")
                print()
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print_exception(e)
    finally:
        robot.shutdown()


def main():
    """Main test menu."""
    print("=== Camera Test Menu ===")
    print("1. Basic test (continuous reading)")
    print("2. Statistics test (10 seconds)")
    print("3. Wait test (wait for color)")
    print("4. Helper methods test")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            test_camera_basic()
        elif choice == '2':
            test_camera_statistics()
        elif choice == '3':
            test_camera_wait()
        elif choice == '4':
            test_camera_helpers()
        else:
            print("Invalid choice, running basic test...")
            test_camera_basic()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        print_exception(e)


if __name__ == "__main__":
    main()

