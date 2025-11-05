"""
Robot Configuration Management
Centralized configuration for all robot parameters.
"""

import json


class RobotConfig:
    """Configuration manager for robot parameters."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "hardware": {
            "motor": {
                "pwm_pin": 0,
                "dir_pin1": 1,
                "dir_pin2": 2,
                "pwm_freq": 1000
            },
            "servo": {
                "pin": 3,
                "servo_pwm_freq": 50,
                "min_u16_duty": 1802,
                "max_u16_duty": 7864,
                "center_steering": 91,
                "max_steering_offset": 11
            },
            "compass": {
                "i2c_id": 1,
                "sda_pin": 14,
                "scl_pin": 15,
                "addr": 0x60,
                "reg": 0x02
            },
            "encoder": {
                "pin_a": 7,
                "pin_b": 6,
                "steps_per_cm": 67.28
            },
            "communication": {
                "uart_id": 0,
                "baudrate": 115200,
                "tx_pin": 16,
                "rx_pin": 17
            },
            "button": {
                "pin": 22,
                "pull_up": True,
                "debounce_ms": 50
            }
        },
        "navigation": {
            "default_max_speed": 0.70,
            "default_min_speed": 0.25,
            "default_slow_distance": 20,
            "default_stop_distance": 5,
            "wall_distance": 50,
            "sonar_multiplier": 0.25,
            "compass_multiplier": 0.1
        },
        "safety": {
            "max_speed_limit": 1.0,
            "emergency_stop_enabled": True,
            "sensor_timeout": 1.0,
            "max_rotation_time": 10.0
        },
        "calibration": {
            "compass_auto_calibrate": True,
            "encoder_auto_calibrate": False,
            "servo_center_on_init": True
        }
    }
    
    def __init__(self, config_file=None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
            
    def get(self, key_path, default=None):
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Path to config value (e.g., "hardware.motor.pwm_pin")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path, value):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Path to config value (e.g., "hardware.motor.pwm_pin")
            value: Value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
            
        # Set the value
        config_ref[keys[-1]] = value
        
    def load_from_file(self, filename):
        """Load configuration from JSON file."""
        try:
            with open(filename, 'r') as f:
                file_config = json.load(f)
                self._merge_configs(self.config, file_config)
            print(f"Configuration loaded from {filename}")
        except Exception as e:
            print(f"Failed to load config from {filename}: {e}")
            
    def save_to_file(self, filename=None):
        """Save configuration to JSON file."""
        filename = filename or self.config_file
        if not filename:
            raise ValueError("No filename provided for saving config")
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Failed to save config to {filename}: {e}")
            
    def _merge_configs(self, base, override):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
                
    def get_hardware_config(self, component):
        """Get hardware configuration for specific component."""
        return self.get(f"hardware.{component}", {})
        
    def get_navigation_config(self):
        """Get navigation configuration."""
        return self.get("navigation", {})
        
    def get_safety_config(self):
        """Get safety configuration."""
        return self.get("safety", {})
        
    def get_calibration_config(self):
        """Get calibration configuration."""
        return self.get("calibration", {})
        
    def validate_config(self):
        """Validate configuration values."""
        errors = []
        
        # Validate hardware pins
        used_pins = []
        hardware_config = self.get("hardware", {})
        
        for component, config in hardware_config.items():
            for param, value in config.items():
                if "pin" in param and isinstance(value, int):
                    if value in used_pins:
                        errors.append(f"Pin {value} used multiple times")
                    else:
                        used_pins.append(value)
                        
        # Validate speed limits
        max_speed = self.get("navigation.default_max_speed", 1.0)
        min_speed = self.get("navigation.default_min_speed", 0.0)
        speed_limit = self.get("safety.max_speed_limit", 1.0)
        
        if max_speed > speed_limit:
            errors.append(f"Max speed {max_speed} exceeds safety limit {speed_limit}")
        if min_speed >= max_speed:
            errors.append(f"Min speed {min_speed} >= max speed {max_speed}")
            
        # Validate distances
        slow_dist = self.get("navigation.default_slow_distance", 20)
        stop_dist = self.get("navigation.default_stop_distance", 5)
        
        if stop_dist >= slow_dist:
            errors.append(f"Stop distance {stop_dist} >= slow distance {slow_dist}")
            
        return errors
        
    def print_config(self):
        """Print current configuration."""
        print("=== Robot Configuration ===")
        self._print_dict(self.config, indent=0)
        print("============================")
        
    def _print_dict(self, d, indent=0):
        """Recursively print dictionary with indentation."""
        for key, value in d.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                self._print_dict(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")


# Global configuration instance
robot_config = RobotConfig()


def get_config():
    """Get global configuration instance."""
    return robot_config


def load_config(filename):
    """Load configuration from file."""
    global robot_config
    robot_config.load_from_file(filename)


def save_config(filename=None):
    """Save configuration to file."""
    global robot_config
    robot_config.save_to_file(filename)
