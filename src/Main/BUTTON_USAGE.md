# Button Usage Guide

## Overview
A button has been added to pin GP22 with an internal pull-up resistor. When pressed during startup, the robot will run the Open Challenge directly instead of showing the menu.

## Hardware Setup
- **Pin**: GP22
- **Pull-up Resistor**: Internal (enabled by default)
- **Button Type**: Normally open (NO) - connects to ground when pressed
- **Wiring**: Connect one terminal of the button to GP22, the other to GND

## Software Configuration
The button is configured in `config.py`:
```python
"button": {
    "pin": 22,
    "pull_up": True,
    "debounce_ms": 50
}
```

## Usage

### Startup Behavior
1. When the robot starts, it will check for button press for 3 seconds
2. If button is pressed during this time, it will:
   - Read front and rear sonar distances
   - Calculate the sum of both distances
   - If sum > 100cm (1 meter): Start Open Challenge
   - If sum ≤ 100cm: Start Obstacle Challenge
   - If sonar data unavailable: Default to Open Challenge
3. If no button press is detected, it shows the normal menu

### Testing
Run the test scripts to verify button functionality:

**Basic button test:**
```bash
python test_button.py
```

**Sonar distance logic test:**
```bash
python test_button_sonar_logic.py
```

### Manual Testing
You can also test the button in the main application:
1. Run `python main.py`
2. Press and hold the button during the 3-second startup check
3. The robot will:
   - Read sonar distances and display them
   - Automatically choose the appropriate challenge based on the distance sum
   - Start the selected challenge without any keyboard input required

## Technical Details

### Button HAL
The button is implemented in `hal/button_hal.py` with the following features:
- Internal pull-up resistor enabled
- 50ms debounce time
- Methods for checking current state and detecting presses
- Timeout support for waiting for presses

### Integration
The button is integrated into the robot controller and main application:
- Added to HAL manager in `robot_controller.py`
- Configuration added to `config.py`
- Startup logic modified in `main.py`

## Troubleshooting

### Button Not Working
1. Check wiring - button should connect GP22 to GND when pressed
2. Verify pin number in configuration
3. Check if pull-up resistor is enabled
4. Test with multimeter to ensure button makes good contact

### False Triggers
1. Check for loose connections
2. Increase debounce time in configuration
3. Verify button is normally open type

### Button Always Pressed
1. Check for short circuit between GP22 and GND
2. Verify button is not stuck in pressed position
3. Check if pull-up resistor is properly enabled

