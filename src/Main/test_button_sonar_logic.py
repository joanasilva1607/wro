#!/usr/bin/env python3
"""
Test script for button press with sonar distance logic
Tests the new button behavior that checks front + rear sonar distances
"""

import time
from robot_controller import RobotController

def test_sonar_distance_logic():
    """Test the sonar distance logic for challenge selection."""
    print("=== TESTING BUTTON SONAR LOGIC ===")
    print("This test simulates the new button press behavior")
    print("that checks front + rear sonar distances to choose challenge")
    print()
    
    robot = RobotController()
    
    try:
        print("Initializing robot...")
        robot.initialize()
        
        if not robot._is_initialized:
            print("✗ Robot initialization failed!")
            return
            
        print("✓ Robot initialized successfully")
        print()
        
        # Test the sonar distance logic
        print("Testing sonar distance logic...")
        print("Getting fresh sensor data...")
        
        fresh_data = robot.get_fresh_sensor_data()
        sensor_data = fresh_data['data']
        
        if sensor_data:
            front_distance = sensor_data.get('front', 0)
            rear_distance = sensor_data.get('rear', 0)
            total_distance = front_distance + rear_distance
            
            print(f"Sonar readings:")
            print(f"  Front: {front_distance}cm")
            print(f"  Rear:  {rear_distance}cm")
            print(f"  Total: {total_distance}cm")
            print()
            
            # Test the decision logic
            if total_distance > 100:  # More than 1 meter
                print("✓ Decision: Total distance > 100cm")
                print("  → Would start OPEN CHALLENGE")
            else:
                print("✓ Decision: Total distance <= 100cm")
                print("  → Would start OBSTACLE CHALLENGE")
                
            print()
            print("Logic test completed successfully!")
            
        else:
            print("✗ Could not read sonar data")
            print("  → Would default to OPEN CHALLENGE")
            
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nShutting down...")
        robot.shutdown()
        print("Test completed.")

def test_multiple_readings():
    """Test multiple sonar readings to see variation."""
    print("\n=== TESTING MULTIPLE SONAR READINGS ===")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._is_initialized:
            print("Robot initialization failed!")
            return
            
        print("Taking 5 sonar readings to check consistency...")
        print("Format: [Reading] Front:XXcm + Rear:XXcm = Total:XXcm → Decision")
        print("-" * 60)
        
        for i in range(5):
            fresh_data = robot.get_fresh_sensor_data()
            sensor_data = fresh_data['data']
            
            if sensor_data:
                front = sensor_data.get('front', 0)
                rear = sensor_data.get('rear', 0)
                total = front + rear
                decision = "OPEN" if total > 100 else "OBSTACLE"
                
                print(f"[{i+1:2d}] Front:{front:3d}cm + Rear:{rear:3d}cm = Total:{total:3d}cm → {decision}")
            else:
                print(f"[{i+1:2d}] No sensor data")
                
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Multiple readings test error: {e}")
    finally:
        robot.shutdown()

if __name__ == "__main__":
    test_sonar_distance_logic()
    test_multiple_readings()









