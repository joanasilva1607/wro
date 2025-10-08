#!/usr/bin/env python3
"""
Sonar Debug Script
Display real-time sonar distance readings from all sensors.
"""

import time
import sys
from robot_controller import RobotController

def display_sonar_readings():
    """Display real-time sonar readings."""
    print("=== SONAR DEBUG DISPLAY ===")
    print("Showing real-time sonar distance readings")
    print("Press Ctrl+C to stop\n")
    
    robot = RobotController()
    
    try:
        print("Initializing robot...")
        robot.initialize()
        
        if not robot._is_initialized:
            print("✗ Robot initialization failed!")
            return
            
        print("✓ Robot initialized successfully")
        print("Starting sonar readings...\n")
        
        # Display header
        print("┌─────────┬─────────┬─────────┬─────────┬─────────┐")
        print("│  Time   │  Front  │  Rear   │  Left   │  Right  │")
        print("├─────────┼─────────┼─────────┼─────────┼─────────┤")
        
        reading_count = 0
        
        while True:
            # Get sensor data
            sensor_data = robot._get_sensor_data()
            
            # Get current time (MicroPython compatible)
            try:
                current_time = time.strftime("%H:%M:%S")
            except AttributeError:
                # MicroPython fallback
                current_time = f"{reading_count:03d}"
            
            if sensor_data:
                front = sensor_data.get('front', 'N/A')
                rear = sensor_data.get('rear', 'N/A')
                left = sensor_data.get('left', 'N/A')
                right = sensor_data.get('right', 'N/A')
                
                # Format distances (assume they're in cm)
                front_str = f"{front:3d}cm" if isinstance(front, int) else str(front)
                rear_str = f"{rear:3d}cm" if isinstance(rear, int) else str(rear)
                left_str = f"{left:3d}cm" if isinstance(left, int) else str(left)
                right_str = f"{right:3d}cm" if isinstance(right, int) else str(right)
                
                print(f"│{current_time}│ {front_str:>6} │ {rear_str:>6} │ {left_str:>6} │ {right_str:>6} │")
                
            else:
                print(f"│{current_time}│   N/A   │   N/A   │   N/A   │   N/A   │")
            
            reading_count += 1
            
            # Add separator line every 10 readings for clarity
            if reading_count % 10 == 0:
                print("├─────────┼─────────┼─────────┼─────────┼─────────┤")
                
            time.sleep(0.5)  # Update every 500ms
            
    except KeyboardInterrupt:
        print("\n└─────────┴─────────┴─────────┴─────────┴─────────┘")
        print("Sonar debug stopped by user")
    except Exception as e:
        print(f"\nError during sonar debug: {e}")
    finally:
        print("Shutting down robot...")
        robot.shutdown()

def test_communication_hal():
    """Test the communication HAL directly."""
    print("\n=== COMMUNICATION HAL TEST ===")
    
    try:
        from hal.communication_hal import CommunicationHAL
        from config import get_config
        
        config = get_config()
        comm_config = config.get_hardware_config('communication')
        print(f"Communication config: {comm_config}")
        
        comm_hal = CommunicationHAL(**comm_config)
        comm_hal.initialize()
        
        if not comm_hal.is_initialized():
            print("✗ Communication HAL initialization failed")
            return
            
        print("✓ Communication HAL initialized")
        print("Testing data reception...")
        
        for i in range(10):
            if comm_hal.has_data():
                data = comm_hal.read_data(4)
                if data:
                    print(f"Raw data {i+1}: {[hex(b) for b in data]} = {list(data)}")
                else:
                    print(f"Data {i+1}: Read failed")
            else:
                print(f"Data {i+1}: No data available")
                
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Communication HAL test failed: {e}")
    finally:
        try:
            comm_hal.deinitialize()
        except:
            pass

def show_sensor_statistics():
    """Show sensor statistics over time."""
    print("\n=== SENSOR STATISTICS ===")
    
    robot = RobotController()
    
    try:
        robot.initialize()
        
        if not robot._is_initialized:
            print("Robot initialization failed")
            return
            
        stats = {
            'front': {'min': float('inf'), 'max': 0, 'readings': []},
            'rear': {'min': float('inf'), 'max': 0, 'readings': []},
            'left': {'min': float('inf'), 'max': 0, 'readings': []},
            'right': {'min': float('inf'), 'max': 0, 'readings': []}
        }
        
        print("Collecting 20 readings for statistics...")
        
        for i in range(20):
            sensor_data = robot._get_sensor_data()
            
            if sensor_data:
                for sensor_name in ['front', 'rear', 'left', 'right']:
                    value = sensor_data.get(sensor_name)
                    if isinstance(value, (int, float)) and value > 0:
                        stats[sensor_name]['readings'].append(value)
                        stats[sensor_name]['min'] = min(stats[sensor_name]['min'], value)
                        stats[sensor_name]['max'] = max(stats[sensor_name]['max'], value)
                        
                print(f"Reading {i+1}/20 collected")
            else:
                print(f"Reading {i+1}/20 failed")
                
            time.sleep(0.2)
            
        # Display statistics
        print("\n=== STATISTICS SUMMARY ===")
        print("┌─────────┬─────────┬─────────┬─────────┬─────────┐")
        print("│ Sensor  │   Min   │   Max   │ Average │ Samples │")
        print("├─────────┼─────────┼─────────┼─────────┼─────────┤")
        
        for sensor_name in ['front', 'rear', 'left', 'right']:
            readings = stats[sensor_name]['readings']
            if readings:
                min_val = stats[sensor_name]['min']
                max_val = stats[sensor_name]['max']
                avg_val = sum(readings) / len(readings)
                count = len(readings)
                
                print(f"│ {sensor_name:>6} │ {min_val:>5.0f}cm │ {max_val:>5.0f}cm │ {avg_val:>5.1f}cm │ {count:>6} │")
            else:
                print(f"│ {sensor_name:>6} │   N/A   │   N/A   │   N/A   │    0   │")
                
        print("└─────────┴─────────┴─────────┴─────────┴─────────┘")
        
    except Exception as e:
        print(f"Statistics collection failed: {e}")
    finally:
        robot.shutdown()

def main():
    """Main debug function."""
    print("=== SONAR DISTANCE DEBUG UTILITY ===")
    print("Choose debug mode:")
    print("1. Real-time sonar display")
    print("2. Communication HAL test")
    print("3. Sensor statistics")
    print("4. All tests")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            display_sonar_readings()
        elif choice == '2':
            test_communication_hal()
        elif choice == '3':
            show_sensor_statistics()
        elif choice == '4':
            test_communication_hal()
            show_sensor_statistics()
            display_sonar_readings()
        else:
            print("Invalid choice, running real-time display...")
            display_sonar_readings()
            
    except KeyboardInterrupt:
        print("\nDebug utility interrupted by user")
    except Exception as e:
        print(f"Debug utility error: {e}")

if __name__ == "__main__":
    main()
