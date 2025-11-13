"""
Robot Controller - Business Logic Layer
Implements high-level robot behaviors using the Hardware Abstraction Layer.
"""

import time
import math
from hal import HALManager, MotorHAL, ServoHAL, CompassHAL, EncoderHAL, CommunicationHAL, ButtonHAL
from config import get_config


class RobotController:
    """High-level robot controller implementing navigation and movement logic."""
    
    def __init__(self, config=None):
        """Initialize robot controller with HAL components."""
        # Get configuration
        self._config = config or get_config()
        
        # Initialize HAL manager
        self._hal_manager = HALManager()
        
        # Create and register HAL components using configuration
        motor_config = self._config.get_hardware_config('motor')
        self._motor_hal = MotorHAL(**motor_config)
        
        servo_config = self._config.get_hardware_config('servo')
        self._servo_hal = ServoHAL(**servo_config)
        
        compass_config = self._config.get_hardware_config('compass')
        self._compass_hal = CompassHAL(**compass_config)
        
        encoder_config = self._config.get_hardware_config('encoder')
        self._encoder_hal = EncoderHAL(**encoder_config)
        
        comm_config = self._config.get_hardware_config('communication')
        self._comm_hal = CommunicationHAL(**comm_config)
        
        button_config = self._config.get_hardware_config('button')
        self._button_hal = ButtonHAL(**button_config)
        
        # Register components
        self._hal_manager.register_component('motor', self._motor_hal)
        self._hal_manager.register_component('servo', self._servo_hal)
        self._hal_manager.register_component('compass', self._compass_hal)
        self._hal_manager.register_component('encoder', self._encoder_hal)
        self._hal_manager.register_component('communication', self._comm_hal)
        self._hal_manager.register_component('button', self._button_hal)
        
        # Robot state
        self._is_initialized = False
        self._current_speed = 0.0
        self._current_direction = 1
        
        # Sensor data caching
        self._last_sensor_data = {
            'front': 0,
            'rear': 0,
            'right': 0,
            'left': 0
        }
        
        # Navigation parameters from configuration
        nav_config = self._config.get_navigation_config()
        self._default_max_speed = nav_config.get('default_max_speed', 0.6)
        self._default_min_speed = nav_config.get('default_min_speed', 0.22)
        self._default_slow_distance = nav_config.get('default_slow_distance', 20)
        self._default_stop_distance = nav_config.get('default_stop_distance', 5)
        
    def initialize(self):
        """Initialize all robot systems."""
        try:
            # Initialize all HAL components
            self._hal_manager.initialize_all()
            
            # Synchronize encoder with motor direction
            self._encoder_hal.set_motor_direction(self._current_direction)
            
            # Calibrate compass
            self._compass_hal.calibrate()
            
            # Center servo
            self._servo_hal.move_to_center()
            
            self._is_initialized = True
            print("Robot controller initialized successfully")
            
        except Exception as e:
            print(f"Robot initialization failed: {e}")
            self._hal_manager.deinitialize_all()
            
    def shutdown(self):
        """Safely shutdown all robot systems."""
        self.stop()
        self._hal_manager.deinitialize_all()
        self._is_initialized = False
        print("Robot controller shut down")
        
    def emergency_stop(self):
        """Emergency stop - immediately halt all movement."""
        if self._motor_hal.is_initialized():
            self._motor_hal.stop()
        if self._servo_hal.is_initialized():
            self._servo_hal.move_to_center()
        print("EMERGENCY STOP ACTIVATED")
        
    # === Basic Movement Controls ===
    
    def move_forward(self, speed=None):
        """Move robot forward at specified speed."""
        if not self._is_initialized:
            return False
            
        speed = speed if speed is not None else self._default_max_speed
        self._motor_hal.forward(speed)
        self._encoder_hal.set_motor_direction(1)
        self._current_speed = speed
        self._current_direction = 1
        return True
        
    def move_backward(self, speed=None):
        """Move robot backward at specified speed."""
        if not self._is_initialized:
            return False
            
        speed = speed if speed is not None else self._default_max_speed
        self._motor_hal.backward(speed)
        self._encoder_hal.set_motor_direction(-1)
        self._current_speed = speed
        self._current_direction = -1
        return True
        
    def stop(self):
        """Stop robot movement."""
        if self._motor_hal.is_initialized():
            self._motor_hal.stop()
        if self._servo_hal.is_initialized():
            self._servo_hal.move_to_center()
        self._current_speed = 0.0
        
    def steer(self, angle):
        """
        Steer robot to specified angle.
        
        Args:
            angle: Steering angle (servo angle)
        """
        if self._servo_hal.is_initialized():
            self._servo_hal.move(angle)
            
    def steer_left(self, offset=None):
        """Steer robot left."""
        if self._servo_hal.is_initialized():
            self._servo_hal.move_left(offset)
            
    def steer_right(self, offset=None):
        """Steer robot right."""
        if self._servo_hal.is_initialized():
            self._servo_hal.move_right(offset)
            
    def center_steering(self):
        """Center the steering."""
        if self._servo_hal.is_initialized():
            self._servo_hal.move(91)
    
    # === Advanced Movement Functions ===
    
    def move_distance(self, target_cm, relative=True, max_speed=None, min_speed=None):
        """
        Move robot a specific distance with speed control.
        
        Args:
            target_cm: Target distance in centimeters
            relative: If True, move relative to current position
            max_speed: Maximum speed (0.0 to 1.0)
            min_speed: Minimum speed (0.0 to 1.0)
        """
        if not self._is_initialized:
            return False
            
        max_speed = max_speed if max_speed is not None else self._default_max_speed
        min_speed = min_speed if min_speed is not None else self._default_min_speed
        
        # Set target distance
        if relative:
            self._encoder_hal.set_reference_position()
            target_distance = target_cm
        else:
            target_distance = target_cm
            initial_distance = self._encoder_hal.get_distance_cm()
            
        # Movement parameters
        slow_distance = self._default_slow_distance
        stop_distance = self._default_stop_distance
        slowdown_started = False
        prev_speed = 0
        
        while True:
            if relative:
                current_distance = self._encoder_hal.get_relative_distance_cm()
                diff = target_distance - current_distance
                initial_diff = current_distance
            else:
                current_distance = self._encoder_hal.get_distance_cm()
                diff = target_distance - current_distance
                initial_diff = current_distance - initial_distance
                
            reverse = diff < 0
            if reverse:
                diff = -diff
                initial_diff = -initial_diff
                
            # Calculate speed based on distance
            speed = max_speed
            
            # Acceleration phase (first few cm)
            if initial_diff < stop_distance:
                speed = min_speed
            elif initial_diff < slow_distance:
                speed_interval = max_speed - min_speed
                distance_interval = slow_distance - stop_distance
                speed = min_speed + (speed_interval * (initial_diff - stop_distance) / distance_interval)
                
            # Deceleration phase (approaching target)
            if diff < stop_distance:
                speed = min_speed
            elif diff < slow_distance:
                if not slowdown_started:
                    slowdown_started = True
                    max_speed = prev_speed
                    
                speed_interval = max_speed - min_speed
                distance_interval = slow_distance - stop_distance
                speed = min_speed + (speed_interval * (diff - stop_distance) / distance_interval)
                
            # Apply movement
            if reverse:
                self.move_backward(speed)
            else:
                self.move_forward(speed)
                
            prev_speed = speed
            
            # Check if target reached
            if diff <= 0.5:  # 5mm tolerance
                break
                
            time.sleep(0.001)  # Small delay for control loop
            
        self.stop()
        return True
        
    def rotate_angle(self, angle, reverse=False, relative=True, timeout=None):
        """
        Rotate robot to a specific compass heading.
        
        Args:
            angle: Target angle in degrees
            reverse: Use reverse direction for rotation
            relative: If True, rotate relative to current heading
            timeout: Maximum time for rotation in seconds
        """
        if not self._is_initialized:
            return False
            
        self.stop()

        offeset_bak = self._compass_hal.get_angle_offset()
        
        # Set target heading
        if relative:
            current_heading = self._compass_hal.get_heading()
            if current_heading is None:
                return False
            self._compass_hal.set_angle_offset(current_heading + 180 + angle)
        else:
            current_offset = self._compass_hal.get_angle_offset()
            self._compass_hal.set_angle_offset(current_offset + angle)
            
        # Rotation parameters
        max_offset = 45
        margin = 0.75
        angle_min_adjustment = 2.5
        speed_min = 0.2
        speed_max = 0.4
        
        start_time = time.time()
        is_first_loop = True
        
        while True:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                self.stop()
                self._servo_hal.move_to_center()
                time.sleep(0.2)
                return False
                
            current_bearing = self._compass_hal.get_relative_heading()
            if current_bearing is None:
                continue
                
            # Check if target reached
            if abs(current_bearing - 180) <= margin:
                self.stop()
                self._servo_hal.move_to_center()
                time.sleep(0.2)
                break
                
            # Calculate steering adjustment
            offset = current_bearing - 180
            
            # Clamp offset
            if abs(offset) > max_offset:
                offset = max_offset if offset > 0 else -max_offset
                
            ratio = offset / max_offset
            angle_adjustment = ratio * self._servo_hal.max_steering_offset
            
            # Apply minimum adjustment
            if abs(angle_adjustment) < angle_min_adjustment:
                angle_adjustment = angle_min_adjustment if angle_adjustment >= 0 else -angle_min_adjustment
                
            if reverse:
                angle_adjustment = -angle_adjustment
                
            # Set steering angle
            servo_angle = self._servo_hal.center_steering - angle_adjustment
            self.steer(servo_angle)
            
            # Wait for servo on first loop
            if is_first_loop:
                time.sleep(0.15)
                is_first_loop = False
                
            # Calculate speed based on error
            speed_range = speed_max - speed_min
            speed = speed_min + (abs(ratio) * speed_range)
            
            # Apply movement
            if reverse:
                self.move_backward(speed)
            else:
                self.move_forward(speed)
                
            time.sleep(1/500)  # Control loop delay
        
        self._compass_hal.set_angle_offset(offeset_bak)
        return True
        
    def move_lane(self, target_cm=None, relative=True, clockwise=True, wall_distance=50,
                  use_sonar=False, use_compass=False, until_front_distance=None, blind_distance=0,
                  lock_compass_heading=False, until_rear_distance=None,compass_multiplier=0.1):
        """
        Move along a lane with wall following and compass guidance.
        
        Args:
            target_cm: Target distance to move (use either this OR until_front_distance, not both)
            relative: Move relative to current position
            clockwise: Direction of movement
            wall_distance: Desired distance from wall (if using sonar)
            use_sonar: Enable sonar-based wall following
            use_compass: Enable compass-based heading correction
            sonar_multiplier: Weight for sonar correction
            compass_multiplier: Weight for compass correction
            until_front_distance: Stop when front sonar distance reaches this value (mutually exclusive with target_cm and until_rear_distance)
            until_rear_distance: Stop when rear sonar distance reaches this value (mutually exclusive with target_cm and until_front_distance)
            blind_distance: Distance to travel before checking front obstacle
            lock_compass_heading: If True and use_compass, lock current heading as target
        """
        if not self._is_initialized:
            return False
            
        # Validate parameters - allow only one stopping mode among distance/front/rear
        specified_modes = sum(v is not None for v in [target_cm, until_front_distance, until_rear_distance])
        if specified_modes != 1:
            raise ValueError("Specify exactly one of target_cm, until_front_distance, or until_rear_distance.")

        sonar_multiplier=0.25

        if wall_distance > 50:
            sonar_multiplier = 0.25

            
        # Optionally lock current heading as compass target
        previous_compass_offset = None
        did_lock_heading = False
        if use_compass and lock_compass_heading:
            current_heading_for_lock = self._compass_hal.get_heading()
            if current_heading_for_lock is not None:
                previous_compass_offset = self._compass_hal.get_angle_offset()
                self._compass_hal.set_angle_offset(current_heading_for_lock + 180)
                did_lock_heading = True

        # Determine movement mode
        use_distance_mode = target_cm is not None
        use_front_distance_mode = until_front_distance is not None
        use_rear_distance_mode = until_rear_distance is not None
        
        # Set target distance for distance-based mode
        if use_distance_mode:
            if relative:
                self._encoder_hal.set_reference_position()
                target_distance = target_cm
            else:
                target_distance = target_cm
                initial_distance = self._encoder_hal.get_distance_cm()
        else:
            # For front distance mode, we still need to track distance for deceleration
            if relative:
                self._encoder_hal.set_reference_position()
            initial_distance = self._encoder_hal.get_distance_cm()
            
        # Movement parameters
        max_speed = self._default_max_speed
        min_speed = self._default_min_speed
        slow_distance = self._default_slow_distance
        stop_distance = self._default_stop_distance
        slowdown_started = False
        prev_speed = 0
        
        while True:
            # Get sensor data from communication
            #sensor_data = self._get_sensor_data()
            fresh_data = self.get_fresh_sensor_data()
            sensor_data = fresh_data['data']
            
            # Calculate current distance
            if relative:
                current_distance = self._encoder_hal.get_relative_distance_cm()
            else:
                current_distance = self._encoder_hal.get_distance_cm()
                initial_diff = current_distance - initial_distance
                
            # Check for front/rear obstacle only after blind distance
            front_distance = None
            rear_distance = None
            if sensor_data and (current_distance >= blind_distance or blind_distance == 0):
                if use_front_distance_mode:
                    front_distance = sensor_data.get('front', 255)
                if use_rear_distance_mode:
                    rear_distance = sensor_data.get('rear', 255)
                
            # Handle different movement modes
            initial_diff = current_distance

            if use_distance_mode:
                # Distance-based mode
                diff = target_distance - current_distance
                
                # Check if target reached
                if abs(diff) <= 0.5:
                    break
                    
            else:
                # Front distance mode
                if use_front_distance_mode:
                    if front_distance is not None and front_distance >= until_front_distance -3 and front_distance <= until_front_distance:
                        print(f"Front obstacle detected at {front_distance}cm after {current_distance:.1f}cm travel, stopping")
                        self.move_lane(
                            relative=relative,
                            use_compass=use_compass,
                            lock_compass_heading=lock_compass_heading,
                            target_cm=front_distance - until_front_distance
                        )
                        break
                    # For front distance mode, we use front distance difference for deceleration
                    if front_distance is not None:
                        diff = front_distance - until_front_distance
                    else:
                        diff = 0  # No front sensor data, maintain current speed

                else:
                    # Rear distance mode
                    if rear_distance is not None and rear_distance >= until_rear_distance and rear_distance <= until_rear_distance +3:
                        print(f"Rear obstacle detected at {rear_distance}cm after {current_distance:.1f}cm travel, stopping")
                        self.move_lane(
                            relative=relative,
                            use_compass=use_compass,
                            lock_compass_heading=lock_compass_heading,
                            target_cm=until_rear_distance - rear_distance
                        )
                        break
                    # For rear distance mode, we use rear distance difference for deceleration
                    if rear_distance is not None:
                        diff = until_rear_distance - rear_distance
                    else:
                        diff = 0
                
            reverse = diff < 0
            if reverse:
                diff = -diff
                initial_diff = -initial_diff
                
            # Calculate steering corrections
            diff_distance = 0
            if use_sonar and sensor_data:
                # For open challenge: clockwise = follow left wall (outside), anticlockwise = follow right wall (outside)
                if clockwise:
                    side_distance = sensor_data.get('left', wall_distance)  # Outside wall is on the left
                    diff_distance = -(side_distance - wall_distance)
                else:
                    side_distance = sensor_data.get('right', wall_distance)  # Outside wall is on the right
                    diff_distance = (side_distance - wall_distance)  # Invert for right wall following
                
                if abs(diff_distance) > 10:
                    diff_distance = 0
                    
            diff_compass = 0
            if use_compass:
                current_bearing = self._compass_hal.get_relative_heading()
                if current_bearing is not None:
                    diff_compass = 180 - current_bearing
                    
            # Apply sensor fusion for steering
            if use_compass and use_sonar and abs(diff_compass) > 40:
                diff_distance = 0
                
            servo_angle = (diff_distance * sonar_multiplier) + (diff_compass * compass_multiplier)
            
            # Calculate speed based on distance
            speed = max_speed
            
            # Acceleration phase
            if initial_diff < stop_distance:
                speed = min_speed
            elif initial_diff < slow_distance:
                speed_interval = max_speed - min_speed
                distance_interval = slow_distance - stop_distance
                speed = min_speed + (speed_interval * (initial_diff - stop_distance) / distance_interval)
                
            # Deceleration phase
            if use_distance_mode or current_distance >= blind_distance or blind_distance == 0:
                # Distance-based deceleration
                if diff < stop_distance:
                    speed = min_speed
                elif diff < slow_distance:
                    if not slowdown_started:
                        slowdown_started = True
                        max_speed = prev_speed
                        
                    speed_interval = max_speed - min_speed
                    distance_interval = slow_distance - stop_distance
                    speed = min_speed + (speed_interval * (diff - stop_distance) / distance_interval)
                

                
            # Adjust steering based on speed
            servo_angle = servo_angle / speed * max_speed

            if reverse:
                servo_angle = -servo_angle
                
            servo_angle = self._servo_hal.center_steering + servo_angle


            if speed < self._default_min_speed:
                speed = self._default_min_speed
            
            # Apply movement and steering
            if reverse:
                self.move_backward(speed)
            else:
                self.move_forward(speed)

            
            self.steer(servo_angle)
                
            prev_speed = speed

            time.sleep(1/100)
            
        # Restore compass offset if we locked it for this movement
        if did_lock_heading and previous_compass_offset is not None:
            self._compass_hal.set_angle_offset(previous_compass_offset)

        self.stop()
        return True
        
    def run_open_challenge(self, target_laps=3, wall_distance=30, front_stop_distance=30):
        """
        Run the open challenge with automatic direction detection and wall following.
        
        Args:
            target_laps: Number of laps to complete (default: 3)
            wall_distance: Target distance from outside wall in cm (default: 30)
            front_stop_distance: Distance from front wall to start turning (default: 30)
        """
        print("DEBUG: run_open_challenge() function called")
        print(f"DEBUG: Robot initialization status: {self._is_initialized}")
        
        if not self._is_initialized:
            print("ERROR: Robot not initialized in run_open_challenge!")
            return False
            
        print("=== STARTING OPEN CHALLENGE ===")
        print(f"Target laps: {target_laps}")
        print(f"Wall following distance: {wall_distance}cm")
        print(f"Turn trigger distance: {front_stop_distance}cm")
        print("DEBUG: Challenge setup complete, starting main loop...")
        
        # Challenge state
        direction_detected = False
        is_clockwise = None
        current_lap = 1
        lanes_completed = 0
        
        # Set reference position and get absolute heading
        self._encoder_hal.set_reference_position()
        initial_heading = self._compass_hal.get_heading()
        if initial_heading is None:
            print("ERROR: Cannot get initial compass heading!")
            return False
            
        # Track absolute target headings for each lane
        target_heading = initial_heading
        
        print(f"Starting position set, initial heading: {initial_heading:.1f}°")
        print(f"Using absolute compass headings, target: {target_heading:.1f}°")
        
        try:
            while current_lap <= target_laps:
                print(f"\n--- LAP {current_lap} ---")
                
                # Complete 4 lanes per lap
                for lane in range(1, 5):
                    print(f"\nLane {lane}/4 (Lap {current_lap}/{target_laps})")
                    
                    if lane == 1 and not direction_detected:
                        # First lane: use compass to go straight until corner
                        print(f"First lane: Moving straight using absolute heading {target_heading:.1f}°")
                        success = self.move_lane(use_compass=True, until_front_distance=front_stop_distance, blind_distance=30)
                        
                        
                        if success:
                            # Detect direction at the corner
                            is_clockwise = self._detect_direction()
                            direction_detected = True
                            direction_str = "CLOCKWISE" if is_clockwise else "ANTICLOCKWISE"
                            print(f"Direction detected: {direction_str}")
                        else:
                            print("Failed to complete first lane")
                            return False
                            
                    else:
                        # Subsequent lanes: move 250cm, then check front and complete lane
                        wall_side = 'left' if is_clockwise else 'right'  # Corrected: clockwise follows left wall (outside)
                        print(f"Following {wall_side} wall at {wall_distance}cm distance")
                        
                        success = self.move_lane(
                            relative=True,
                            clockwise=is_clockwise,
                            use_compass=True,
                            use_sonar=True,
                            wall_distance=wall_distance,
                            until_front_distance=15,  # Front stop distance
                            blind_distance=200  # Don't check front until 250cm
                        )
                    
                    # Turn at the end of each lane (except the last lane of the last lap)
                    if not (current_lap == target_laps and lane == 4):
                        print(f"Making 90° turn ({'right' if is_clockwise else 'left'})")
                        
                        # Calculate new target heading after turn
                        if is_clockwise:
                            target_heading = (target_heading + 90) % 360  # Right turn
                        else:
                            target_heading = (target_heading - 90) % 360  # Left turn
                            
                        print(f"New target heading after turn: {target_heading:.1f}°")
                        
                        success = self._make_corner_turn_absolute(is_clockwise, target_heading)
                        
                        if not success:
                            print("Failed to make corner turn")
                            return False
                    
                    lanes_completed += 1
                    print(f"Lane {lane} completed! (Total lanes: {lanes_completed})")
                
                current_lap += 1
                
            print(f"\n🎉 OPEN CHALLENGE LAPS COMPLETED! 🎉")
            print(f"Successfully completed {target_laps} laps")
            print(f"Direction: {'CLOCKWISE' if is_clockwise else 'ANTICLOCKWISE'}")
            print(f"Total lanes completed: {lanes_completed}")
            
            # Add final corner and meter as requested
            print("\n--- FINAL CORNER AND METER ---")
            print("Making final corner turn...")
            
            # Calculate new target heading for final turn
            if is_clockwise:
                target_heading = (target_heading + 90) % 360  # Right turn
            else:
                target_heading = (target_heading - 90) % 360  # Left turn
                
            print(f"Final turn target heading: {target_heading:.1f}°")
            
            # Make the final corner turn
            success = self._make_corner_turn_absolute(is_clockwise, target_heading)
            
            if not success:
                print("Failed to make final corner turn")
                return False
                
            print("Final corner completed!")
            
            # Move one more meter (100cm) after the corner using move_lane
            print("Moving final meter (100cm) with wall following...")
            success = self.move_lane(
                target_cm=100,
                relative=True,
                clockwise=is_clockwise,
                use_compass=True,
                use_sonar=True,
                wall_distance=wall_distance,
            )
            
            if not success:
                print("Failed to move final meter")
                return False
                
            print("Final meter completed!")
            
            print(f"\n🎉 OPEN CHALLENGE FULLY COMPLETED! 🎉")
            print(f"Successfully completed {target_laps} laps + final corner + final meter")
            print(f"Direction: {'CLOCKWISE' if is_clockwise else 'ANTICLOCKWISE'}")
            print(f"Total lanes completed: {lanes_completed}")
            print("Final corner and meter: COMPLETED")
            
            return True
            
        except KeyboardInterrupt:
            print("\nOpen challenge interrupted by user")
            return False
        except Exception as e:
            print(f"Open challenge failed: {e}")
            return False
        finally:
            self.stop()
            
    def _navigate_first_lane(self, front_stop_distance):
        """
        Navigate the first lane using compass guidance until reaching the corner.
        
        Args:
            front_stop_distance: Distance from front wall to stop
            
        Returns:
            bool: Success status
        """
        print("Starting first lane navigation with compass guidance")
        
        # Get initial heading for straight line navigation
        target_heading = self._compass_hal.get_heading()
        if target_heading is None:
            print("Failed to get initial compass heading")
            return False
            
        print(f"Target heading: {target_heading:.1f}°")
        
        # Movement parameters
        base_speed = 0.4
        max_steering_adjustment = 15
        
        while True:
            # Get sensor data
            sensor_data = self._get_sensor_data()
            front_distance = sensor_data.get('front', 255)
            
            # Check if we've reached the front wall
            if front_distance <= front_stop_distance:
                print(f"Reached front wall (distance: {front_distance}cm)")
                self.stop()
                return True
                
            # Get current heading
            current_heading = self._compass_hal.get_heading()
            if current_heading is None:
                print("Lost compass reading, stopping")
                self.stop()
                return False
                
            # Calculate heading error
            heading_error = target_heading - current_heading
            
            # Handle wraparound (e.g., target=10°, current=350°)
            if heading_error > 180:
                heading_error -= 360
            elif heading_error < -180:
                heading_error += 360
                
            # Calculate steering adjustment
            steering_adjustment = heading_error * 0.5  # Proportional control
            steering_adjustment = max(-max_steering_adjustment, 
                                    min(max_steering_adjustment, steering_adjustment))
            
            # Apply movement
            servo_angle = int(self._servo_hal.center_steering + steering_adjustment)
            self.steer(servo_angle)
            self.move_forward(base_speed)
            
            # Debug output
            if abs(heading_error) > 2:
                print(f"Heading correction: error={heading_error:.1f}°, steering={steering_adjustment:.1f}")
            
            time.sleep(0.05)  # Control loop delay
            
    def _navigate_first_lane_absolute(self, front_stop_distance, target_heading):
        """
        Navigate the first lane using absolute compass heading until reaching the corner.
        
        Args:
            front_stop_distance: Distance from front wall to stop
            target_heading: Absolute compass heading to maintain
            
        Returns:
            bool: Success status
        """
        print(f"Starting first lane navigation with absolute heading {target_heading:.1f}°")
        
        # Movement parameters
        base_speed = 0.4
        max_steering_adjustment = 15
        
        while True:
            # Get sensor data
            sensor_data = self._get_sensor_data()
            front_distance = sensor_data.get('front', 255)
            
            # Check if we've reached the front wall
            if front_distance <= front_stop_distance:
                print(f"Reached front wall (distance: {front_distance}cm)")
                self.stop()
                return True
                
            # Get current heading
            current_heading = self._compass_hal.get_heading()
            if current_heading is None:
                print("Lost compass reading, stopping")
                self.stop()
                return False
                
            # Calculate heading error
            heading_error = target_heading - current_heading
            
            # Handle wraparound (e.g., target=10°, current=350°)
            if heading_error > 180:
                heading_error -= 360
            elif heading_error < -180:
                heading_error += 360
                
            # Calculate steering adjustment
            steering_adjustment = heading_error * 0.5  # Proportional control
            steering_adjustment = max(-max_steering_adjustment, 
                                    min(max_steering_adjustment, steering_adjustment))
            
            # Apply movement
            servo_angle = int(self._servo_hal.center_steering + steering_adjustment)
            self.steer(servo_angle)
            self.move_forward(base_speed)
            
            # Debug output
            if abs(heading_error) > 2:
                print(f"Heading correction: target={target_heading:.1f}°, current={current_heading:.1f}°, "
                      f"error={heading_error:.1f}°, steering={steering_adjustment:.1f}")
            
            time.sleep(0.05)  # Control loop delay
            
    def _detect_direction(self):
        """
        Detect if the track is clockwise or anticlockwise by comparing sonar readings.
        
        Returns:
            bool: True if clockwise, False if anticlockwise
        """
        print("Detecting track direction using sonar readings...")
        
        # Take multiple readings for reliability
        right_readings = []
        left_readings = []
        
        for i in range(5):
            sensor_data = self._get_sensor_data()
            right_distance = sensor_data.get('right', 0)
            left_distance = sensor_data.get('left', 0)
            
            if right_distance > 0 and left_distance > 0:
                right_readings.append(right_distance)
                left_readings.append(left_distance)
                
            time.sleep(0.1)
            
        if not right_readings or not left_readings:
            print("Warning: Could not get reliable sonar readings for direction detection")
            return True  # Default to clockwise
            
        # Calculate average distances
        avg_right = sum(right_readings) / len(right_readings)
        avg_left = sum(left_readings) / len(left_readings)
        
        print(f"Average distances - Right: {avg_right:.1f}cm, Left: {avg_left:.1f}cm")
        
        # If right distance > left distance, we're at a right corner (clockwise)
        is_clockwise = avg_right > avg_left
        
        print(f"Direction determination: {'CLOCKWISE' if is_clockwise else 'ANTICLOCKWISE'}")
        print(f"Logic: Right({avg_right:.1f}) {'>' if is_clockwise else '<='} Left({avg_left:.1f})")
        
        return is_clockwise
        
    def _navigate_lane_with_distance_check(self, wall_distance, front_stop_distance, is_clockwise, min_distance_before_check):
        """
        Navigate a lane using move_lane with minimum distance requirement.
        
        Args:
            wall_distance: Target distance from wall
            front_stop_distance: Distance from front wall to stop
            is_clockwise: True for clockwise direction (follow left wall)
            min_distance_before_check: Minimum distance to travel before checking front wall
            
        Returns:
            bool: Success status
        """
        print(f"Starting lane navigation with {min_distance_before_check}cm minimum distance")
        
        # Set reference position to track distance traveled
        self._encoder_hal.set_reference_position()
        
        # Movement parameters for move_lane
        use_sonar = True
        use_compass = True
        
        # Start moving using move_lane in a custom loop
        while True:
            # Get current distance traveled
            distance_traveled = abs(self._encoder_hal.get_relative_distance_cm())
            
            # Get sensor data
            sensor_data = self._get_sensor_data()
            front_distance = sensor_data.get('front', 255)
            
            # Only check front wall after minimum distance
            if distance_traveled >= min_distance_before_check:
                if front_distance <= front_stop_distance:
                    print(f"Reached front wall after {distance_traveled:.1f}cm (front: {front_distance}cm)")
                    self.stop()
                    return True
            
            # Use move_lane logic for a small segment (10cm at a time)
            try:
                success = self.move_lane(
                    target_cm=40,
                    relative=True,
                    clockwise=is_clockwise,
                    wall_distance=wall_distance,
                    use_sonar=use_sonar,
                    use_compass=use_compass
                )
                
                if not success:
                    print("move_lane segment failed")
                    return False
                    
            except Exception as e:
                print(f"Lane navigation error: {e}")
                return False
                
            # Debug output every 50cm
            if int(distance_traveled) % 50 == 0 and distance_traveled > 0:
                print(f"Lane progress: {distance_traveled:.1f}cm traveled, front: {front_distance}cm")
                
            time.sleep(0.1)  # Brief pause between segments
        
    def _make_corner_turn(self, clockwise):
        """
        Make a 90-degree turn at a corner.
        
        Args:
            clockwise: True for right turn, False for left turn
            
        Returns:
            bool: Success status
        """
        turn_direction = "RIGHT" if clockwise else "LEFT"
        print(f"Making 90° {turn_direction} turn")
        
        # Stop and prepare for turn
        self.stop()
        time.sleep(0.2)
        
        # Get initial heading
        initial_heading = self._compass_hal.get_heading()
        if initial_heading is None:
            print("Failed to get initial heading for turn")
            return False
            
        # Calculate target heading (90 degrees from current)
        if clockwise:
            target_heading = (initial_heading + 90) % 360
        else:
            target_heading = (initial_heading - 90) % 360
            
        print(f"Turn: {initial_heading:.1f}° → {target_heading:.1f}°")
        
        # Execute the turn using the existing rotate_angle function
        success = self.rotate_angle(90 if clockwise else -90, relative=True, timeout=15)
        
        if success:
            final_heading = self._compass_hal.get_heading()
            print(f"Turn completed. Final heading: {final_heading:.1f}°")
        else:
            print("Turn failed or timed out")
            
        return success
        
    def _make_corner_turn_absolute(self, clockwise, target_heading):
        """
        Make a 90-degree turn to reach a specific absolute heading using rotate_angle logic.
        
        Args:
            clockwise: True for right turn, False for left turn
            target_heading: Absolute target heading in degrees
            
        Returns:
            bool: Success status
        """
        turn_direction = "RIGHT" if clockwise else "LEFT"
        print(f"Making 90° {turn_direction} turn to heading {target_heading:.1f}°")
        
        if not self._is_initialized:
            return False
            
        self.stop()
        
        # Get current heading for display
        initial_heading = self._compass_hal.get_heading()
        if initial_heading is None:
            print("Failed to get initial heading for turn")
            return False
            
        print(f"Turn: {initial_heading:.1f}° → {target_heading:.1f}°")
        
        # Set compass offset to target the absolute heading
        # The rotate_angle logic expects relative heading of 180° to be the target
        # So we set offset such that when we reach target_heading, relative will be 180°
        self._compass_hal.set_angle_offset(target_heading + 180)
        
        # Rotation parameters (same as rotate_angle)
        max_offset = 50
        margin = 2  # Slightly larger margin for absolute turns
        angle_min_adjustment = 3
        speed_min = 0.22
        speed_max = 0.4
        timeout = 15  # 15 second timeout
        
        start_time = time.time()
        is_first_loop = True
        
        while True:
            # Check timeout
            if (time.time() - start_time) > timeout:
                print("Turn timed out")
                self.stop()
                return False
                
            current_bearing = self._compass_hal.get_relative_heading()
            if current_bearing is None:
                continue
                
            # Check if target reached (relative heading should be 180° when at target)
            if abs(current_bearing - 180) <= margin:
                current_heading = self._compass_hal.get_heading()
                print(f"Turn completed. Final heading: {current_heading:.1f}°")
                self.stop()
                break
                
            # Calculate steering adjustment (same logic as rotate_angle)
            offset = current_bearing - 180
            
            # Clamp offset
            if abs(offset) > max_offset:
                offset = max_offset if offset > 0 else -max_offset
                
            ratio = offset / max_offset
            angle_adjustment = ratio * self._servo_hal.max_steering_offset
            
            # Apply minimum adjustment
            if abs(angle_adjustment) < angle_min_adjustment:
                angle_adjustment = angle_min_adjustment if angle_adjustment >= 0 else -angle_min_adjustment
                
            # Always use reverse for corner turns
            reverse = True
            if reverse:
                angle_adjustment = -angle_adjustment
                
            # Set steering angle
            servo_angle = int(self._servo_hal.center_steering - angle_adjustment)
            self.steer(servo_angle)
            
            # Wait for servo on first loop
            if is_first_loop:
                time.sleep(0.15)
                is_first_loop = False
                
            # Calculate speed based on error (same as rotate_angle)
            speed_range = speed_max - speed_min
            speed = speed_min + (abs(ratio) * speed_range)
            
            # Apply movement
            if reverse:
                self.move_backward(speed)
            else:
                self.move_forward(speed)
                
            time.sleep(0.0002)  # Control loop delay (same as rotate_angle)
            
        return True
        
    # === Sensor Reading Functions ===
    
    def get_compass_heading(self):
        """Get current compass heading."""
        return self._compass_hal.get_heading()
        
    def get_relative_heading(self):
        """Get relative compass heading."""
        return self._compass_hal.get_relative_heading()
        
    def get_distance_traveled(self):
        """Get total distance traveled."""
        return self._encoder_hal.get_distance_cm()
        
    def get_relative_distance(self):
        """Get distance from reference point."""
        return self._encoder_hal.get_relative_distance_cm()
        
    def reset_distance_counter(self):
        """Reset distance counter."""
        self._encoder_hal.reset_position()
        
    def set_distance_reference(self):
        """Set current position as distance reference."""
        self._encoder_hal.set_reference_position()
        
    def _get_sensor_data(self):
        """
        Get the latest sensor data from communication interface.
        Always reads the most recent data available, caches last known values.
        """
        if not self._comm_hal.is_initialized():
            return self._last_sensor_data.copy()
            
        try:
            # Read all available data to get the most recent complete packet
            latest_data = None
            
            # Keep reading while data is available to get the freshest
            while self._comm_hal.has_data():
                # Try to read a complete 4-byte packet
                data = self._comm_hal.read_data(4)
                if data and len(data) == 4:
                    latest_data = data
                elif data and len(data) > 0:
                    # Partial packet - read remaining bytes if available
                    remaining_bytes = 4 - len(data)
                    if self._comm_hal.has_data():
                        extra_data = self._comm_hal.read_data(remaining_bytes)
                        if extra_data:
                            data += extra_data
                            if len(data) == 4:
                                latest_data = data
                
            # If we got new complete data, update cache
            if latest_data:
                self._last_sensor_data = {
                    'left': latest_data[0],
                    'rear': latest_data[1], 
                    'right': latest_data[2],
                    'front': latest_data[3]
                }
                
        except Exception as e:
            print(f"Sensor data read error: {e}")
            
        # Always return the cached data (either updated or last known)
        return self._last_sensor_data.copy()
        
    def get_fresh_sensor_data(self):
        """
        Force reading fresh sensor data and return with freshness info.
        
        Returns:
            dict: Sensor data with 'fresh' flag indicating if data was updated
        """
        old_data = self._last_sensor_data.copy()
        new_data = self._get_sensor_data()
        
        return {
            'data': new_data,
            'fresh': new_data != old_data,
            'timestamp': time.time() if hasattr(time, 'time') else 0
        }
        
    # === Status and Debug Functions ===
    
    def get_robot_status(self):
        """Get comprehensive robot status."""
        return {
            'initialized': self._is_initialized,
            'current_speed': self._current_speed,
            'current_direction': self._current_direction,
            'compass_heading': self.get_compass_heading(),
            'relative_heading': self.get_relative_heading(),
            'distance_traveled': self.get_distance_traveled(),
            'relative_distance': self.get_relative_distance(),
            'servo_angle': self._servo_hal.get_current_angle() if self._servo_hal.is_initialized() else None,
            'motor_moving': self._motor_hal.is_moving() if self._motor_hal.is_initialized() else False,
            'encoder_moving': self._encoder_hal.is_moving() if self._encoder_hal.is_initialized() else False
        }
        
    def print_status(self):
        """Print current robot status."""
        status = self.get_robot_status()
        print("=== Robot Status ===")
        for key, value in status.items():
            print(f"{key}: {value}")
        print("==================")
        
    def get_hal_errors(self):
        """Get HAL error log."""
        return self._hal_manager.get_error_log()
        
    def clear_hal_errors(self):
        """Clear HAL error log."""
        self._hal_manager.clear_error_log()
        
    def is_button_pressed(self):
        """Check if button is currently pressed."""
        if self._button_hal.is_initialized():
            return self._button_hal.is_pressed()
        return False
        
    def wait_for_button_press(self, timeout_ms=None):
        """Wait for button press with optional timeout."""
        if self._button_hal.is_initialized():
            return self._button_hal.wait_for_press(timeout_ms)
        return False
        
    def obstacle_corner(self, last_inside=False, color_inside=None, color_outside=None, 
                       is_first_lane=False, clockwise=True, next_lane=None):
        """
        Handle obstacle detection at corners for the obstacle challenge.
        
        Args:
            last_inside: Whether the previous lane ended inside
            color_inside: Color detection data for inside position
            color_outside: Color detection data for outside position
            is_first_lane: Whether this is the first lane
            clockwise: Direction of movement
            next_lane: Next lane traffic position (if known)
            
        Returns:
            LaneTraffic: Detected traffic position
        """
        from lane import LaneTraffic
        
        if next_lane is None or next_lane == LaneTraffic.Unknown:
            # Need to detect the obstacle position
            self.rotate_angle(0, reverse=True, relative=False)
            
            if last_inside:
                # Move forward to get better detection
                self.move_lane(
                    target_cm=99999,
                    relative=True,
                    use_compass=False,
                    use_sonar=False
                )
            else:
                # Move forward briefly
                self.move_lane(
                    target_cm=99999,
                    relative=True,
                    use_compass=False,
                    use_sonar=False
                )
            
            self.rotate_angle(0, relative=False)
            
            # Simulate color detection (hardcoded for now)
            # In future implementation, this would use actual camera data
            if color_inside and color_outside:
                next_obstacle_inside = (color_inside.get("detected", False) and 
                                      color_outside.get("detected", False) and
                                      color_inside.get("distance", 999) < color_outside.get("distance", 999))
            elif color_inside and color_inside.get("detected", False):
                next_obstacle_inside = True
            else:
                next_obstacle_inside = False
                
            # Make the turn to avoid the obstacle
            angle = 60 if next_obstacle_inside else -60
            if not clockwise:
                angle = -angle
                
            self.rotate_angle(angle, relative=False)
            
            # Move forward to clear the obstacle
            self.move_forward(0.4)
            
            if not next_obstacle_inside and is_first_lane:
                time.sleep(0.18)
            else:
                if next_obstacle_inside:
                    time.sleep(0.35)
                else:
                    time.sleep(0.2)
                    # Check for front obstacle
                    sensor_data = self._get_sensor_data()
                    front_distance = sensor_data.get('front', 255)
                    while front_distance > 17:
                        time.sleep(0.001)
                        sensor_data = self._get_sensor_data()
                        front_distance = sensor_data.get('front', 255)
            
            self.rotate_angle(0, relative=False)
            
            return LaneTraffic.Inside if next_obstacle_inside else LaneTraffic.Outside
            
        else:
            # Use known next lane position
            if next_lane == LaneTraffic.Inside:
                self.rotate_angle(0, relative=False, reverse=True)
            else:
                self.rotate_angle(0, relative=False, reverse=False)

            return next_lane
            
    def run_obstacle_challenge(self, hardcoded_lanes=None):
        """
        Run the obstacle challenge with hardcoded lane positions.
        
        Args:
            hardcoded_lanes: List of Lane objects with hardcoded positions (optional)
        """
        from lane import Lane, LaneTraffic
        
        print("=== STARTING OBSTACLE CHALLENGE ===")
        
        if not self._is_initialized:
            print("ERROR: Robot not initialized!")
            return False
            
        # Initialize hardcoded lane positions if not provided
        if hardcoded_lanes is None:
            # Default hardcoded lane configuration
            hardcoded_lanes = [
                Lane(LaneTraffic.Inside, LaneTraffic.Outside),   # Lane 0
                Lane(LaneTraffic.Outside, LaneTraffic.Inside),   # Lane 1
                Lane(LaneTraffic.Inside, LaneTraffic.Outside),   # Lane 2
                Lane(LaneTraffic.Outside, LaneTraffic.Inside),   # Lane 3
            ]
            
        print(f"Using {len(hardcoded_lanes)} hardcoded lane positions")
        
        # Challenge state
        current_lane = 0
        current_lap = 0
        clockwise = None
        side_sonar = None
        
        # Set reference position and get absolute heading
        self._encoder_hal.set_reference_position()
        initial_heading = self._compass_hal.get_heading()
        if initial_heading is None:
            print("ERROR: Cannot get initial compass heading!")
            return False
            
        compass_offset = initial_heading + 180
        self._compass_hal.set_angle_offset(compass_offset)
        
        # Detect direction using sonar
        print("Detecting track direction...")
        sensor_data = self._get_sensor_data()
        left_distance = sensor_data.get('left', 0)
        right_distance = sensor_data.get('right', 0)
        
        clockwise = left_distance < right_distance
        side_sonar = 'left' if clockwise else 'right'
        
        print(f"Direction detected: {'CLOCKWISE' if clockwise else 'ANTICLOCKWISE'}")
        print(f"Following {side_sonar} wall")
        
        # Simulate color detection data (hardcoded for now)
        color_outside = {"detected": True, "distance": 30}
        color_inside = {"detected": True, "distance": 50}
        
        try:
            # Exit parking area
            print("Exiting parking area...")
            self.move_lane(
                relative=True,
                clockwise=clockwise,
                use_compass=True,
                lock_compass_heading=True,
                until_rear_distance=4
            )
            self.rotate_angle(50 if clockwise else -50)
            
            # Check initial lane alignment
            previous_lane_alignment = False
            if color_inside["detected"] and color_outside["detected"]:
                previous_lane_alignment = (color_inside["distance"] < color_outside["distance"])
            elif color_inside["detected"]:
                previous_lane_alignment = True
            else:
                previous_lane_alignment = False
                
            # Exit parking based on alignment
            if previous_lane_alignment:
                self.rotate_angle(40 if clockwise else -40)
                self.move_lane(
                    relative=True,
                    clockwise=clockwise,
                    use_compass=True,
                    lock_compass_heading=True,
                    until_front_distance=25
                )

            else:
                self.move_lane(
                    relative=True,
                    clockwise=clockwise,
                    use_compass=True,
                    lock_compass_heading=True,
                    target_cm=15
                )
                    
            self.rotate_angle(0, relative=False)
            
            # Set up wall distances
            inside = 79
            outside = 17
            outside_parking = 35
            
            wall_distance = inside if previous_lane_alignment else outside_parking
            
            # Move to first lane
            print("Moving to first lane...")
            self.move_lane(
                relative=True,
                clockwise=clockwise,
                wall_distance=wall_distance,
                use_sonar=True,
                use_compass=True,
                until_front_distance=15,
                blind_distance=50
            )
            
        
            
            current_lane = 1
            number_laps = 1

            
            # Main obstacle challenge loop
            while current_lane <= number_laps*4:  # 3 laps * 4 lanes = 12 total lanes
                compass_offset += 90 if clockwise else -90
                self._compass_hal.set_angle_offset(compass_offset)
                
                lane_index = current_lane % 4
                next_lane_index = (lane_index + 1) % 4
                is_first_lane = lane_index == 0
                
                print(f"\n--- Lane {current_lane} (Lap {current_lap + 1}) ---")
                print(f"Lane position: {hardcoded_lanes[lane_index]}")
                
                if current_lane == number_laps*4:
                    print("Final lane reached!")
                    self.stop()
                    break
                    
                # Detect obstacle at corner
                previous_lane_final = (hardcoded_lanes[(lane_index + 3) % 4].final 
                                     if current_lane > 1 else LaneTraffic.Unknown)
                
                detected_position = self.obstacle_corner(
                    last_inside=(previous_lane_final == LaneTraffic.Inside),
                    color_inside=color_inside,
                    color_outside=color_outside,
                    is_first_lane=is_first_lane,
                    clockwise=clockwise,
                    next_lane=hardcoded_lanes[lane_index].initial
                )
                
                # Update lane with detected position
                hardcoded_lanes[lane_index].initial = detected_position
                
                # Set wall distance based on position
                wall_distance = (inside if hardcoded_lanes[lane_index].initial == LaneTraffic.Inside 
                               else (outside_parking if is_first_lane else outside))
                
                #get rear sensor data
                sensor_data = self._get_sensor_data()
                rear_distance = sensor_data.get('rear', 255)

                target_distance = 115 - rear_distance

                # Move along the lane
                self.move_lane(
                    target_cm=target_distance,
                    relative=True,
                    clockwise=clockwise,
                    wall_distance=wall_distance,
                    use_sonar=True,
                    use_compass=True
                )

                # Detect final position if unknown
                if hardcoded_lanes[lane_index].final == LaneTraffic.Unknown:
                    angle = -15 if hardcoded_lanes[lane_index].initial == LaneTraffic.Inside else 15
                    if not clockwise:
                        angle = -angle
                        
                    self.rotate_angle(angle, relative=False)
                    
                    # Simulate final position detection
                    if color_inside["detected"] and color_outside["detected"]:
                        hardcoded_lanes[lane_index].final = (LaneTraffic.Inside 
                                                           if (color_inside["distance"] < color_outside["distance"]) 
                                                           else LaneTraffic.Outside)
                    elif color_inside["detected"]:
                        hardcoded_lanes[lane_index].final = LaneTraffic.Inside
                    else:
                        hardcoded_lanes[lane_index].final = LaneTraffic.Outside
                        
                # Handle position change if needed
                if hardcoded_lanes[lane_index].initial != hardcoded_lanes[lane_index].final:
                    angle = 90 if hardcoded_lanes[lane_index].final == LaneTraffic.Inside else -90
                    if not clockwise:
                        angle = -angle
                        
                    self.rotate_angle(angle, relative=False)
                    

                    if (hardcoded_lanes[lane_index].final == LaneTraffic.Outside and is_first_lane):
                        self.move_lane(
                            relative=True,
                            clockwise=clockwise,
                            use_compass=True,
                            lock_compass_heading=True,
                            until_rear_distance=55
                        )

                    else:
                        self.move_lane(
                            relative=True,
                            clockwise=clockwise,
                            use_compass=True,
                            lock_compass_heading=True,
                            until_front_distance=18
                        )
                            
                    self.rotate_angle(0, relative=False)
                else:
                    self.rotate_angle(0, relative=False, reverse=True)
                    
                # Set final wall distance
                wall_distance = (inside if hardcoded_lanes[lane_index].final == LaneTraffic.Inside 
                               else (outside_parking if is_first_lane else outside))
                
                target_distance = 50
                if current_lane == (number_laps*4)-1:
                    #Last lane of the last lap
                    target_distance = 15
                elif hardcoded_lanes[next_lane_index].initial == LaneTraffic.Unknown:
                    #First lap
                    target_distance = 50
                elif hardcoded_lanes[next_lane_index].initial == LaneTraffic.Inside:
                    #Next is an Inside lane
                    target_distance = 63
                else:

                    if next_lane_index == 0:
                        #Next is an Outside lane and first lane
                        target_distance = 38
                    else:
                        #Next is an Outside lane and not first lane
                        target_distance = 15

                # Move to next corner
                print("Moving to next corner...")
                self.move_lane(
                    relative=True,
                    clockwise=clockwise,
                    wall_distance=wall_distance,
                    use_sonar=True,
                    use_compass=True,
                    until_front_distance=target_distance,
                    blind_distance=80
                )
                
                # Additional movement for first few lanes
                if False: # current_lane < 5:
                    self.move_lane(
                        relative=True,
                        clockwise=clockwise,
                        wall_distance=wall_distance,
                        use_sonar=True,
                        use_compass=True,
                        until_front_distance=40
                    )
                    
                current_lane += 1
                current_lap = int(current_lane / 4)
                
            # Final parking sequence
            print("\n--- FINAL PARKING SEQUENCE ---")
            
            
            self.rotate_angle(0, reverse=clockwise, relative=False)
            
            if clockwise:
                self.rotate_angle(90, reverse=True, relative=False)
                self.move_lane(
                    relative=True,
                    clockwise=clockwise,
                    use_compass=True,
                    lock_compass_heading=True,
                    until_rear_distance=14
                )
                self.rotate_angle(0, reverse=True, relative=False)

                
            self.move_lane(
                relative=True,
                clockwise=clockwise,
                wall_distance=10,
                use_sonar=True,
                use_compass=True,
                until_front_distance=12
            )


            self.rotate_angle(90 if clockwise else -90)
            
            self.move_lane(
                relative=True,
                clockwise=clockwise,
                use_compass=True,
                lock_compass_heading=True,
                until_rear_distance=28
            )

            self.rotate_angle(0, relative=False)

            self.move_lane(
                relative=True,
                clockwise=clockwise,
                use_compass=True,
                lock_compass_heading=True,
                target_cm=31.5,
                compass_multiplier=0.65
            )

            self.rotate_angle(90 if clockwise else -90, reverse=True)


            self.move_lane(
                relative=True,
                clockwise=clockwise,
                until_rear_distance=18,
                use_compass=True,
                lock_compass_heading=True
            )

            self.rotate_angle(0, reverse=True, relative=False)


            self.move_lane(
                relative=True,
                clockwise=clockwise,
                use_compass=True,
                until_rear_distance=4
            )
            
            print("\n🎉 OBSTACLE CHALLENGE COMPLETED! 🎉")
            return True
            
        except KeyboardInterrupt:
            print("\nObstacle challenge interrupted by user")
            return False
        except Exception as e:
            print(f"Obstacle challenge failed: {e}")
            return False
        finally:
            self.stop()