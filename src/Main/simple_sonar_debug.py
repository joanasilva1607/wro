#!/usr/bin/env python3
"""
Simple Sonar Debug - MicroPython Compatible
Basic sonar distance display without fancy formatting.
"""

import time
from robot_controller import RobotController

def simple_sonar_display():
    """Simple sonar readings display."""
    print("=== SIMPLE SONAR DEBUG ===")
    print("Press Ctrl+C to stop")
    
    robot = RobotController()
    
    try:
        print("Initializing robot...")
        robot.initialize()
        
        if not robot._is_initialized:
            print("Robot initialization failed!")
            return
            
        print("Robot initialized. Starting readings...")
        print("Format: [Count] Front:XXcm Rear:XXcm Left:XXcm Right:XXcm")
        print("-" * 60)
        
        count = 0
        
        while True:
            count += 1
            
            # Get fresh sensor data
            fresh_data = robot.get_fresh_sensor_data()
            sensor_data = fresh_data['data']
            is_fresh = fresh_data['fresh']
            
            if sensor_data:
                front = sensor_data.get('front', 'N/A')
                rear = sensor_data.get('rear', 'N/A')
                left = sensor_data.get('left', 'N/A')
                right = sensor_data.get('right', 'N/A')
                
                freshness = "FRESH" if is_fresh else "CACHED"
                print(f"[{count:03d}] Front:{front}cm Rear:{rear}cm Left:{left}cm Right:{right}cm ({freshness})")
                
            else:
                print(f"[{count:03d}] No sensor data received")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nSonar debug stopped")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Shutting down...")
        try:
            robot.shutdown()
        except:
            pass

def test_raw_communication():
    """Test raw communication data."""
    print("\n=== RAW COMMUNICATION TEST ===")
    
    try:
        import sys
        sys.path.append('hal')
        from communication_hal import CommunicationHAL
        from config import get_config
        
        config = get_config()
        comm_config = config.get_hardware_config('communication')
        
        print(f"Config: {comm_config}")
        
        comm = CommunicationHAL(**comm_config)
        comm.initialize()
        
        if not comm.is_initialized():
            print("Communication HAL failed to initialize")
            return
            
        print("Communication HAL initialized")
        print("Checking for data...")
        
        for i in range(20):
            if comm.has_data():
                data = comm.read_data(4)
                if data:
                    print(f"Raw[{i:02d}]: {list(data)} = Front:{data[0]} Rear:{data[1]} Left:{data[2]} Right:{data[3]}")
                else:
                    print(f"Raw[{i:02d}]: Read failed")
            else:
                print(f"Raw[{i:02d}]: No data")
                
            time.sleep(0.3)
            
    except Exception as e:
        print(f"Raw test failed: {e}")
    finally:
        try:
            comm.deinitialize()
        except:
            pass

def manual_sensor_test():
    """Manual step-by-step sensor test."""
    print("\n=== MANUAL SENSOR TEST ===")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._is_initialized:
            print("Robot initialization failed")
            return
            
        print("Robot initialized")
        print("Taking 10 individual readings...")
        
        for i in range(10):
            print(f"\nReading {i+1}:")
            
            # Get sensor data
            sensor_data = robot._get_sensor_data()
            
            if sensor_data:
                print(f"  Sensor data received: {sensor_data}")
                print(f"  Front distance: {sensor_data.get('front', 'ERROR')}")
                print(f"  Rear distance:  {sensor_data.get('rear', 'ERROR')}")
                print(f"  Left distance:  {sensor_data.get('left', 'ERROR')}")
                print(f"  Right distance: {sensor_data.get('right', 'ERROR')}")
            else:
                print("  No sensor data received")
                
            # Check communication HAL status
            if robot._comm_hal.is_initialized():
                has_data = robot._comm_hal.has_data()
                print(f"  Communication HAL has data: {has_data}")
            else:
                print("  Communication HAL not initialized")
                
            time.sleep(1)
            
    except Exception as e:
        print(f"Manual test failed: {e}")
    finally:
        robot.shutdown()

def main():
    """Main function."""
    print("Choose sonar debug mode:")
    print("1. Simple real-time display")
    print("2. Raw communication test") 
    print("3. Manual step-by-step test")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            simple_sonar_display()
        elif choice == '2':
            test_raw_communication()
        elif choice == '3':
            manual_sensor_test()
        else:
            print("Invalid choice, running simple display...")
            simple_sonar_display()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

