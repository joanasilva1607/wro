"""
Main Robot Application using Hardware Abstraction Layer
Clean separation between business logic and hardware control.
"""

import time
from machine import Pin
from robot_controller import RobotController

# Initialize status LED
led = Pin(25, Pin.OUT)
led.on()  # Turn on LED at boot


class RobotApplication:
    """Main robot application class."""
    
    def __init__(self):
        """Initialize robot application."""
        self.robot = RobotController()
        self.running = False
        
    def initialize(self):
        """Initialize robot systems."""
        print("Initializing robot systems...")
        self.robot.initialize()
        
        if not self.robot._is_initialized:
            print("Robot initialization failed!")
            print("LED will remain ON - check hardware connections")
            return False
            
        print("Robot initialization complete!")
        print("LED turned OFF - initialization successful")
        led.off()  # Turn off LED when initialization is successful
        return True
        
    def shutdown(self):
        """Shutdown robot systems."""
        print("Shutting down robot...")
        self.running = False
        self.robot.shutdown()
        led.on()  # Turn LED back on during shutdown
        print("Robot shutdown complete.")
        
    def emergency_stop(self):
        """Emergency stop procedure."""
        print("EMERGENCY STOP!")
        self.robot.emergency_stop()
        led.on()  # Turn LED on during emergency stop
        self.running = False
        
    def run_demo_sequence(self):
        """Run a demonstration sequence."""
        print("Starting demo sequence...")
        
        try:
            # Demo 1: Basic movement
            print("Demo 1: Moving forward 50cm")
            self.robot.move_distance(50, relative=True)
            time.sleep(1)
            
            # Demo 2: Rotation
            print("Demo 2: Rotating 90 degrees")
            self.robot.rotate_angle(90, relative=True)
            time.sleep(1)
            
            # Demo 3: Move backward
            print("Demo 3: Moving backward 25cm") 
            self.robot.move_distance(-25, relative=True)
            time.sleep(1)
            
            # Demo 4: Return to center
            print("Demo 4: Rotating back to start")
            self.robot.rotate_angle(-90, relative=True)
            time.sleep(1)
            
            print("Demo sequence complete!")
            
        except Exception as e:
            print(f"Demo sequence error: {e}")
            self.robot.stop()
            
    def run_sensor_test(self):
        """Run sensor testing loop."""
        print("Starting sensor test loop...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                # Get and display sensor readings
                status = self.robot.get_robot_status()
                
                print(f"Compass: {status['compass_heading']:.1f}°, "
                      f"Distance: {status['distance_traveled']:.1f}cm, "
                      f"Servo: {status['servo_angle']:.1f}°")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nSensor test stopped by user")
        except Exception as e:
            print(f"Sensor test error: {e}")
            
    def run_navigation_test(self):
        """Run navigation testing with wall following."""
        print("Starting navigation test...")
        
        try:
            # Test 1: Lane following with compass
            print("Test 1: Lane following with compass guidance")
            self.robot.move_lane(
                target_cm=100,
                relative=True,
                clockwise=True,
                use_compass=True,
                use_sonar=False
            )
            time.sleep(1)
            
            # Test 2: Lane following with sensor fusion
            print("Test 2: Lane following with sensor fusion")
            self.robot.move_lane(
                target_cm=100,
                relative=True,
                clockwise=True,
                use_compass=True,
                use_sonar=True,
                wall_distance=30
            )
            time.sleep(1)
            
            print("Navigation test complete!")
            
        except Exception as e:
            print(f"Navigation test error: {e}")
            self.robot.stop()
            
    def run_calibration_sequence(self):
        """Run calibration sequence for sensors."""
        print("Starting calibration sequence...")
        
        try:
            # Compass calibration
            print("Calibrating compass...")
            if self.robot._compass_hal.calibrate():
                print("Compass calibration successful")
            else:
                print("Compass calibration failed")
                
            # Encoder calibration (optional)
            print("Testing encoder...")
            initial_distance = self.robot.get_distance_traveled()
            self.robot.move_distance(50, relative=True)  # Move 50cm
            final_distance = self.robot.get_distance_traveled()
            actual_distance = final_distance - initial_distance
            
            print(f"Encoder test: Target=50cm, Actual={actual_distance:.1f}cm")
            
            # Servo calibration
            print("Testing servo range...")
            self.robot.center_steering()
            time.sleep(0.5)
            self.robot.steer_left()
            time.sleep(0.5)
            self.robot.steer_right()
            time.sleep(0.5)
            self.robot.center_steering()
            
            print("Calibration sequence complete!")
            
        except Exception as e:
            print(f"Calibration error: {e}")
            self.robot.stop()
            
    def run_open_challenge(self):
        """Run the open challenge sequence."""
        print("Starting Open Challenge...")
        print("This will run 3 laps with automatic direction detection")
        print("Press Ctrl+C to stop at any time")
        
        try:
            print("\nStarting challenge execution...")
            
            # Check if robot is initialized
            if not self.robot._is_initialized:
                print("ERROR: Robot is not initialized!")
                print("Please run option 6 (Show Robot Status) to check initialization")
                return
                
            print("Robot is initialized, proceeding with challenge...")
            
            # Run the challenge
            success = self.robot.run_open_challenge(
                target_laps=3,
                wall_distance=30,
                front_stop_distance=15
            )
            
            if success:
                print("\n🎉 OPEN CHALLENGE COMPLETED SUCCESSFULLY! 🎉")
            else:
                print("\n❌ Open challenge failed or was interrupted")
                
        except KeyboardInterrupt:
            print("\n\nOpen challenge interrupted by user")
            self.robot.emergency_stop()
        except Exception as e:
            print(f"\nOpen challenge error: {e}")
            self.robot.stop()
            
    def run_main_loop(self):
        """Run main robot operation loop."""
        print("Starting main operation loop...")
        self.running = True
        
        try:
            while self.running:
                # Get current status
                status = self.robot.get_robot_status()
                
                # Display key information
                print(f"Distance: {status['distance_traveled']:.1f}cm, "
                      f"Heading: {status['compass_heading']:.1f}°")
                
                # Add your main robot logic here
                # For now, just monitor sensors
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            print("\nMain loop stopped by user")
        except Exception as e:
            print(f"Main loop error: {e}")
        finally:
            self.running = False
            
    def show_menu(self):
        """Show interactive menu."""
        while True:
            print("\n=== Robot Control Menu ===")
            print("1. Run Demo Sequence")
            print("2. Sensor Test Loop")
            print("3. Navigation Test")
            print("4. Calibration Sequence")
            print("5. Main Operation Loop")
            print("6. Open Challenge (3 Laps)")
            print("7. Show Robot Status")
            print("8. Emergency Stop")
            print("9. Exit")
            print("========================")
            
            try:
                choice = input("Enter choice (1-9): ").strip()
                
                if choice == '1':
                    self.run_demo_sequence()
                elif choice == '2':
                    self.running = True
                    self.run_sensor_test()
                elif choice == '3':
                    self.run_navigation_test()
                elif choice == '4':
                    self.run_calibration_sequence()
                elif choice == '5':
                    self.run_main_loop()
                elif choice == '6':
                    self.run_open_challenge()
                elif choice == '7':
                    self.robot.print_status()
                elif choice == '8':
                    self.emergency_stop()
                elif choice == '9':
                    break
                else:
                    print("Invalid choice, please try again.")
                    
            except KeyboardInterrupt:
                print("\nOperation interrupted by user")
                self.robot.stop()
            except Exception as e:
                print(f"Menu error: {e}")


def main():
    """Main application entry point."""
    print("Robot Application Starting...")
    print("LED Status: ON (initialization in progress)")
    
    # Create robot application
    app = RobotApplication()
    
    try:
        # Initialize robot
        if not app.initialize():
            print("Failed to initialize robot, exiting.")
            print("LED Status: ON (initialization failed)")
            return
        
        # Check for button press at startup
        print("\nChecking for button press on pin GP22...")
        print("Press and hold the button to run Open Challenge directly, or wait 3 seconds for menu...")
        print("LED Status: OFF (initialization successful)")
        
        # Debug: Check button state before waiting
        print(f"DEBUG: Button currently pressed: {app.robot.is_button_pressed()}")
        print("DEBUG: Starting 3-second button wait...")
        
        # Wait for button press with 3 second timeout
        if app.robot.wait_for_button_press(timeout_ms=3000):
            print("\nButton pressed! Starting Open Challenge immediately...")
            print("Challenge will begin in 2 seconds...")
            time.sleep(2)  # Give user time to see the message
            app.run_open_challenge()
        else:
            print("\nNo button press detected. Showing menu...")
            # Show interactive menu
            app.show_menu()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        print("LED Status: ON (shutdown)")
    except Exception as e:
        print(f"Application error: {e}")
        print("LED Status: ON (error state)")
    finally:
        # Ensure clean shutdown
        app.shutdown()
        
    print("Robot Application Ended.")


# Alternative: Direct execution examples
def run_simple_test():
    """Simple test without menu system."""
    robot = RobotController()
    
    try:
        # Initialize
        robot.initialize()
        
        # Simple movement test
        print("Moving forward...")
        robot.move_forward(0.5)
        time.sleep(2)
        
        print("Stopping...")
        robot.stop()
        time.sleep(1)
        
        print("Rotating...")
        robot.rotate_angle(90, relative=True)
        time.sleep(1)
        
        print("Test complete!")
        
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        robot.shutdown()


if __name__ == "__main__":
    # Run the full application with menu
    main()
    
    # Alternative: Run simple test
    # run_simple_test()
