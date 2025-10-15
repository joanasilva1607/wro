# Obstacle Challenge Implementation

This document describes the implementation of the Obstacle Challenge for the WRO robot.

## Overview

The Obstacle Challenge is implemented as an extension to the existing robot controller, providing hardcoded lane positions for obstacle detection and avoidance. The implementation is designed to be compatible with future camera-based detection during the first lap.

## Files Added/Modified

### New Files
- `lane.py` - Contains `Lane` and `LaneTraffic` classes for obstacle position tracking
- `test_obstacle_challenge.py` - Test script for the obstacle challenge implementation
- `OBSTACLE_CHALLENGE.md` - This documentation file

### Modified Files
- `robot_controller.py` - Added `obstacle_corner()` and `run_obstacle_challenge()` methods
- `main.py` - Added obstacle challenge menu option and runner function

## Key Components

### LaneTraffic Class
```python
class LaneTraffic:
    Inside = "inside"      # Obstacle on the inside of the track
    Outside = "outside"    # Obstacle on the outside of the track
    Unknown = "unknown"    # Obstacle position not yet determined
```

### Lane Class
```python
class Lane:
    def __init__(self, initial=LaneTraffic.Unknown, final=LaneTraffic.Unknown):
        self.initial = initial  # Position when entering the lane
        self.final = final      # Position when exiting the lane
```

### Obstacle Challenge Features

1. **Hardcoded Lane Positions**: Predefined obstacle positions for 4 lanes that repeat for 3 laps
2. **Direction Detection**: Automatic detection of track direction (clockwise/anticlockwise)
3. **Obstacle Avoidance**: Smart corner navigation based on obstacle positions
4. **Wall Following**: Dynamic wall distance adjustment based on obstacle positions
5. **Timeout Management**: Adaptive timeouts based on lane conditions

## Usage

### Running the Obstacle Challenge

1. **Via Menu**:
   - Run `main.py`
   - Select option 7 "Obstacle Challenge (3 Laps)"
   - The robot will execute the obstacle challenge

2. **Programmatically**:
   ```python
   from robot_controller import RobotController
   from lane import Lane, LaneTraffic
   
   robot = RobotController()
   robot.initialize()
   
   # Use default hardcoded positions
   success = robot.run_obstacle_challenge()
   
   # Or provide custom lane positions
   custom_lanes = [
       Lane(LaneTraffic.Inside, LaneTraffic.Outside),
       Lane(LaneTraffic.Outside, LaneTraffic.Inside),
       Lane(LaneTraffic.Inside, LaneTraffic.Outside),
       Lane(LaneTraffic.Outside, LaneTraffic.Inside),
   ]
   success = robot.run_obstacle_challenge(custom_lanes)
   ```

## Challenge Flow

1. **Initialization**: Set up compass, detect direction, initialize lane positions
2. **Parking Exit**: Navigate out of parking area based on initial alignment
3. **Lane Navigation**: For each of 12 lanes (3 laps × 4 lanes):
   - Detect obstacle position at corner
   - Adjust wall following distance
   - Navigate along lane with appropriate timeout
   - Handle position changes if needed
4. **Final Parking**: Execute final parking sequence

## Configuration

### Default Lane Positions
```python
hardcoded_lanes = [
    Lane(LaneTraffic.Inside, LaneTraffic.Outside),   # Lane 0
    Lane(LaneTraffic.Outside, LaneTraffic.Inside),   # Lane 1
    Lane(LaneTraffic.Inside, LaneTraffic.Outside),   # Lane 2
    Lane(LaneTraffic.Outside, LaneTraffic.Inside),   # Lane 3
]
```

### Wall Distances
- **Inside**: 75cm (when obstacle is on inside)
- **Outside**: 25cm (when obstacle is on outside)
- **Outside Parking**: 35cm (special case for first lane)

### Speed Settings
- **Normal Speed**: 0.4-0.5
- **Corner Speed**: 0.3-0.4
- **Parking Speed**: 0.3

## Future Camera Integration

The implementation is designed to be compatible with future camera-based detection:

1. **Color Detection Simulation**: Currently uses hardcoded color detection data
2. **Obstacle Detection**: The `obstacle_corner()` method can be extended to use real camera data
3. **Position Updates**: Lane positions can be updated dynamically based on camera input

## Testing

Run the test script to verify the implementation:

```bash
python test_obstacle_challenge.py
```

The test script validates:
- Lane class functionality
- Obstacle challenge configuration
- Color detection simulation
- Direction detection logic
- Wall distance calculations
- Timeout calculations

## Error Handling

The implementation includes comprehensive error handling:
- Robot initialization checks
- Sensor data validation
- Timeout management
- Emergency stop capability
- Graceful shutdown on interruption

## Integration with Existing Code

The obstacle challenge integrates seamlessly with the existing robot controller:
- Uses existing HAL components (motor, servo, compass, encoder, communication)
- Follows the same initialization and shutdown patterns
- Compatible with existing menu system
- Maintains the same error handling approach
