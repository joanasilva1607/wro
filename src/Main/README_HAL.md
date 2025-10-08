# Hardware Abstraction Layer (HAL) Architecture

This directory contains a complete Hardware Abstraction Layer implementation that separates business logic from hardware control, making the robot code more maintainable, testable, and portable.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  (main_with_hal.py, robot_controller.py)                   │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
│  (Navigation algorithms, Movement control, Sensors)        │
├─────────────────────────────────────────────────────────────┤
│                Hardware Abstraction Layer                  │
│  (motor_hal.py, servo_hal.py, compass_hal.py, etc.)       │
├─────────────────────────────────────────────────────────────┤
│                    Hardware Layer                          │
│  (MicroPython machine module, GPIO, I2C, UART)            │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/Main/
├── hal/                          # Hardware Abstraction Layer
│   ├── __init__.py              # HAL package initialization
│   ├── base_hal.py              # Base classes and HAL manager
│   ├── motor_hal.py             # Motor control HAL
│   ├── servo_hal.py             # Servo control HAL
│   ├── compass_hal.py           # Compass sensor HAL
│   ├── encoder_hal.py           # Encoder HAL
│   └── communication_hal.py     # UART communication HAL
├── robot_controller.py          # High-level robot control logic
├── main_with_hal.py            # New main application using HAL
├── config.py                   # Configuration management
├── main.py                     # Original monolithic implementation
└── README_HAL.md              # This file
```

## Key Benefits

### 1. **Separation of Concerns**
- Hardware control logic isolated from business logic
- Easy to modify hardware without changing algorithms
- Clear interfaces between components

### 2. **Maintainability**
- Modular design with single responsibility principle
- Standardized error handling across all components
- Consistent API design patterns

### 3. **Testability**
- HAL components can be mocked for unit testing
- Business logic can be tested independently
- Hardware-in-the-loop testing capabilities

### 4. **Portability**
- Easy migration to different hardware platforms
- Hardware-specific code contained in HAL layer
- Business logic remains unchanged across platforms

### 5. **Robustness**
- Comprehensive error handling and recovery
- Hardware health monitoring
- Graceful degradation on component failures

## HAL Components

### Motor HAL (`motor_hal.py`)
```python
# Example usage
motor = MotorHAL(pwm_pin=0, dir_pin1=1, dir_pin2=2)
motor.initialize()
motor.forward(0.8)  # 80% speed forward
motor.stop()
```

**Features:**
- Speed control with direction
- Safety limits and validation
- Current state tracking
- Error handling and recovery

### Servo HAL (`servo_hal.py`)
```python
# Example usage
servo = ServoHAL(pin=3, center_steering=91)
servo.initialize()
servo.move_to_center()
servo.move_left(offset=10)
servo.move_right()
```

**Features:**
- Angle-based control with safety limits
- Center, left, right positioning
- Smooth movement with validation
- Dynamic settings update

### Compass HAL (`compass_hal.py`)
```python
# Example usage
compass = CompassHAL(i2c_id=1, sda_pin=14, scl_pin=15)
compass.initialize()
heading = compass.get_heading()
relative_heading = compass.get_relative_heading()
compass.calibrate()
```

**Features:**
- Auto I2C address detection
- Heading filtering and validation
- Relative heading calculations
- Calibration support

### Encoder HAL (`encoder_hal.py`)
```python
# Example usage
encoder = EncoderHAL(pin_a=7, pin_b=6, steps_per_cm=67.28)
encoder.initialize()
distance = encoder.get_distance_cm()
encoder.reset_position()
```

**Features:**
- Interrupt-driven position tracking
- Distance calculations in cm/mm
- Speed estimation
- Calibration support

### Communication HAL (`communication_hal.py`)
```python
# Example usage
comm = CommunicationHAL(uart_id=0, tx_pin=16, rx_pin=17)
comm.initialize()
comm.send_message("Hello")
data = comm.read_data(4)
```

**Features:**
- UART message handling
- Queue management
- Statistics tracking
- Robust data transfer

## Robot Controller

The `RobotController` class provides high-level robot behaviors:

```python
from robot_controller import RobotController

robot = RobotController()
robot.initialize()

# High-level movement commands
robot.move_distance(50, relative=True)  # Move 50cm forward
robot.rotate_angle(90, relative=True)   # Rotate 90 degrees
robot.move_lane(100, use_compass=True)  # Lane following

# Sensor access
heading = robot.get_compass_heading()
distance = robot.get_distance_traveled()
status = robot.get_robot_status()

robot.shutdown()
```

## Configuration Management

The configuration system provides centralized parameter management:

```python
from config import get_config

config = get_config()

# Get configuration values
max_speed = config.get("navigation.default_max_speed")
motor_pin = config.get("hardware.motor.pwm_pin")

# Set configuration values
config.set("navigation.default_max_speed", 0.9)

# Save/load configuration
config.save_to_file("robot_config.json")
config.load_from_file("robot_config.json")
```

## Migration from Original Code

### Step 1: Run Both Versions
- Keep `main.py` as fallback
- Test `main_with_hal.py` thoroughly
- Compare behavior and performance

### Step 2: Gradual Migration
- Start with simple movements
- Add sensor integration
- Implement advanced navigation
- Test each component individually

### Step 3: Configuration Tuning
- Adjust parameters in `config.py`
- Calibrate sensors using HAL methods
- Optimize performance settings

### Step 4: Full Transition
- Replace `main.py` with HAL version
- Update documentation
- Train team on new architecture

## Usage Examples

### Basic Robot Control
```python
from robot_controller import RobotController

def basic_demo():
    robot = RobotController()
    robot.initialize()
    
    try:
        # Move in a square pattern
        for _ in range(4):
            robot.move_distance(50)      # Forward 50cm
            robot.rotate_angle(90)       # Turn 90 degrees
            
    finally:
        robot.shutdown()
```

### Sensor Monitoring
```python
def sensor_monitor():
    robot = RobotController()
    robot.initialize()
    
    try:
        while True:
            status = robot.get_robot_status()
            print(f"Heading: {status['compass_heading']:.1f}°")
            print(f"Distance: {status['distance_traveled']:.1f}cm")
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        robot.shutdown()
```

### Advanced Navigation
```python
def navigation_demo():
    robot = RobotController()
    robot.initialize()
    
    try:
        # Wall following with sensor fusion
        robot.move_lane(
            target_cm=200,
            clockwise=True,
            use_compass=True,
            use_sonar=True,
            wall_distance=30
        )
        
    finally:
        robot.shutdown()
```

## Testing and Debugging

### Component Testing
```python
# Test individual HAL components
from hal import MotorHAL

motor = MotorHAL()
motor.initialize()
motor.forward(0.5)
time.sleep(2)
motor.stop()
motor.deinitialize()
```

### Error Monitoring
```python
robot = RobotController()
robot.initialize()

# Get HAL errors
errors = robot.get_hal_errors()
for timestamp, error in errors:
    print(f"{timestamp}: {error}")
```

### Status Monitoring
```python
# Comprehensive status check
robot.print_status()

# Individual component status
status = robot.get_robot_status()
print(f"Initialized: {status['initialized']}")
print(f"Moving: {status['motor_moving']}")
```

## Performance Considerations

### Optimization Tips
1. **Minimize HAL calls in tight loops**
2. **Use bulk operations where possible**
3. **Cache frequently accessed values**
4. **Monitor error logs for issues**

### Memory Management
- HAL components have minimal memory overhead
- Configuration system uses efficient data structures
- Error logs have automatic size limits

### Real-time Performance
- Interrupt-driven encoder processing
- Minimal latency in motor/servo control
- Efficient sensor data processing

## Extension Points

### Adding New Hardware
1. Create new HAL class inheriting from `BaseHAL`
2. Implement required methods
3. Register with `HALManager`
4. Add configuration parameters
5. Update `RobotController` as needed

### Custom Behaviors
1. Extend `RobotController` class
2. Use existing HAL components
3. Add new high-level methods
4. Maintain abstraction principles

## Troubleshooting

### Common Issues
1. **Initialization Failures**: Check pin configurations and hardware connections
2. **Communication Errors**: Verify UART settings and connections
3. **Sensor Readings**: Check I2C addresses and calibration
4. **Movement Issues**: Verify motor directions and encoder settings

### Debug Tools
- HAL error logging system
- Component status monitoring
- Configuration validation
- Interactive testing menu

This HAL architecture provides a solid foundation for complex robot behaviors while maintaining clean, maintainable code.
