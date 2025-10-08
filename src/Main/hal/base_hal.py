"""
Base Hardware Abstraction Layer
Provides common functionality for all HAL components.
"""


class BaseHAL:
    """Base class for all hardware abstraction layer components."""
    
    def __init__(self):
        self._is_initialized = False
        self._error_callback = None
        
    def initialize(self):
        """Initialize hardware component. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement initialize()")
        
    def deinitialize(self):
        """Deinitialize hardware component. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement deinitialize()")
        
    def is_initialized(self):
        """Check if hardware component is initialized."""
        return self._is_initialized
        
    def set_error_callback(self, callback):
        """Set error callback function."""
        self._error_callback = callback
        
    def _handle_error(self, error_message):
        """Handle errors consistently across all HAL components."""
        print(f"HAL Error: {error_message}")
        if self._error_callback:
            self._error_callback(error_message)


class HALManager:
    """Manager for all HAL components."""
    
    def __init__(self):
        self._components = {}
        self._error_log = []
        
    def register_component(self, name, hal_component):
        """Register a HAL component."""
        if not isinstance(hal_component, BaseHAL):
            raise ValueError("Component must inherit from BaseHAL")
            
        hal_component.set_error_callback(self._log_error)
        self._components[name] = hal_component
        
    def initialize_all(self):
        """Initialize all registered components."""
        for name, component in self._components.items():
            try:
                component.initialize()
                print(f"Initialized {name}")
            except Exception as e:
                self._log_error(f"Failed to initialize {name}: {e}")
                
    def deinitialize_all(self):
        """Deinitialize all registered components."""
        for name, component in self._components.items():
            try:
                component.deinitialize()
                print(f"Deinitialized {name}")
            except Exception as e:
                self._log_error(f"Failed to deinitialize {name}: {e}")
                
    def get_component(self, name):
        """Get a specific HAL component."""
        return self._components.get(name)
        
    def _log_error(self, error_message):
        """Log errors from HAL components."""
        import time
        timestamp = time.time()
        self._error_log.append((timestamp, error_message))
        print(f"HAL Manager Error: {error_message}")
        
    def get_error_log(self):
        """Get the error log."""
        return self._error_log.copy()
        
    def clear_error_log(self):
        """Clear the error log."""
        self._error_log.clear()
