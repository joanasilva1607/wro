#!/usr/bin/env python3
"""
GPIO9 Pulse Detector
Monitor GPIO9 for digital pulses and state changes.
Detects rising edges, falling edges, and measures pulse characteristics.
"""

import time
import machine
from machine import Pin


class GPIO9PulseDetector:
    """Detect and analyze pulses on GPIO9."""
    
    def __init__(self, pin=9, pull=None):
        """
        Initialize pulse detector.
        
        Args:
            pin: GPIO pin number (default: 9)
            pull: Pull resistor mode - None, Pin.PULL_UP, or Pin.PULL_DOWN
        """
        self.pin_num = pin
        self.pull = pull
        self.pin = None
        
        # Pulse statistics
        self.rising_edge_count = 0
        self.falling_edge_count = 0
        self.total_pulses = 0
        
        # Timing data
        self.last_rising_time = None
        self.last_falling_time = None
        self.last_state_change_time = None
        self.pulse_widths = []  # Store recent pulse widths
        self.periods = []  # Store recent periods (time between rising edges)
        self.max_history = 100  # Keep last 100 measurements
        
        # Current state
        self.current_state = None
        self.last_state = None
        
        # Interrupt handler
        self._interrupt_enabled = False
        
    def initialize(self):
        """Initialize GPIO9 pin."""
        try:
            print(f"Initializing GPIO{self.pin_num} for pulse detection...")
            
            # Configure pin based on pull resistor setting
            if self.pull is None:
                self.pin = Pin(self.pin_num, Pin.IN)
                print("  Pull resistor: None (floating)")
            elif self.pull == Pin.PULL_UP:
                self.pin = Pin(self.pin_num, Pin.IN, Pin.PULL_UP)
                print("  Pull resistor: PULL_UP")
            elif self.pull == Pin.PULL_DOWN:
                self.pin = Pin(self.pin_num, Pin.IN, Pin.PULL_DOWN)
                print("  Pull resistor: PULL_DOWN")
            else:
                self.pin = Pin(self.pin_num, Pin.IN)
                print("  Pull resistor: None (invalid option, using floating)")
            
            # Read initial state
            self.current_state = self.pin.value()
            self.last_state = self.current_state
            
            print(f"  Initial state: {self.current_state} ({'HIGH' if self.current_state else 'LOW'})")
            print("✓ GPIO initialized successfully")
            return True
            
        except Exception as e:
            print(f"✗ GPIO initialization failed: {e}")
            return False
    
    def _handle_interrupt(self, pin):
        """Handle pin interrupt for pulse detection."""
        current_time = time.ticks_us()  # Use microseconds for better precision
        new_state = pin.value()
        
        # Detect rising edge (LOW -> HIGH)
        if new_state == 1 and self.last_state == 0:
            self.rising_edge_count += 1
            self.total_pulses += 1
            
            if self.last_rising_time is not None:
                # Calculate period (time between rising edges)
                period = time.ticks_diff(current_time, self.last_rising_time)
                self.periods.append(period)
                if len(self.periods) > self.max_history:
                    self.periods.pop(0)
            
            self.last_rising_time = current_time
            
        # Detect falling edge (HIGH -> LOW)
        elif new_state == 0 and self.last_state == 1:
            self.falling_edge_count += 1
            
            if self.last_rising_time is not None:
                # Calculate pulse width (HIGH duration)
                pulse_width = time.ticks_diff(current_time, self.last_rising_time)
                self.pulse_widths.append(pulse_width)
                if len(self.pulse_widths) > self.max_history:
                    self.pulse_widths.pop(0)
            
            self.last_falling_time = current_time
        
        self.last_state = new_state
        self.current_state = new_state
        self.last_state_change_time = current_time
    
    def enable_interrupts(self):
        """Enable interrupt-based pulse detection."""
        if not self.pin:
            print("Error: Pin not initialized")
            return False
        
        try:
            # Set up interrupt on both rising and falling edges
            self.pin.irq(
                trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                handler=self._handle_interrupt
            )
            self._interrupt_enabled = True
            print("✓ Interrupts enabled (RISING and FALLING edges)")
            return True
        except Exception as e:
            print(f"✗ Failed to enable interrupts: {e}")
            return False
    
    def disable_interrupts(self):
        """Disable interrupt-based pulse detection."""
        if self.pin:
            self.pin.irq(handler=None)
            self._interrupt_enabled = False
            print("Interrupts disabled")
    
    def get_current_state(self):
        """Get current pin state."""
        if self.pin:
            self.current_state = self.pin.value()
        return self.current_state
    
    def get_statistics(self):
        """Get pulse detection statistics."""
        stats = {
            'rising_edges': self.rising_edge_count,
            'falling_edges': self.falling_edge_count,
            'total_pulses': self.total_pulses,
            'current_state': self.get_current_state(),
            'interrupt_enabled': self._interrupt_enabled
        }
        
        # Calculate average pulse width
        if self.pulse_widths:
            avg_width_us = sum(self.pulse_widths) / len(self.pulse_widths)
            min_width_us = min(self.pulse_widths)
            max_width_us = max(self.pulse_widths)
            stats['pulse_width'] = {
                'avg_us': avg_width_us,
                'min_us': min_width_us,
                'max_us': max_width_us,
                'avg_ms': avg_width_us / 1000.0,
                'min_ms': min_width_us / 1000.0,
                'max_ms': max_width_us / 1000.0
            }
        else:
            stats['pulse_width'] = None
        
        # Calculate average period and frequency
        if self.periods:
            avg_period_us = sum(self.periods) / len(self.periods)
            min_period_us = min(self.periods)
            max_period_us = max(self.periods)
            avg_freq_hz = 1000000.0 / avg_period_us if avg_period_us > 0 else 0
            stats['period'] = {
                'avg_us': avg_period_us,
                'min_us': min_period_us,
                'max_us': max_period_us,
                'avg_ms': avg_period_us / 1000.0,
                'min_ms': min_period_us / 1000.0,
                'max_ms': max_period_us / 1000.0
            }
            stats['frequency'] = {
                'avg_hz': avg_freq_hz,
                'min_hz': 1000000.0 / max_period_us if max_period_us > 0 else 0,
                'max_hz': 1000000.0 / min_period_us if min_period_us > 0 else 0
            }
        else:
            stats['period'] = None
            stats['frequency'] = None
        
        return stats
    
    def reset_statistics(self):
        """Reset all pulse statistics."""
        self.rising_edge_count = 0
        self.falling_edge_count = 0
        self.total_pulses = 0
        self.last_rising_time = None
        self.last_falling_time = None
        self.pulse_widths.clear()
        self.periods.clear()
        print("Statistics reset")
    
    def monitor_realtime(self, duration=None, update_interval=0.5):
        """
        Monitor GPIO9 in real-time and display pulse statistics.
        
        Args:
            duration: Monitoring duration in seconds (None for infinite)
            update_interval: Update display interval in seconds
        """
        print("\n=== GPIO9 PULSE DETECTION (REAL-TIME) ===")
        print(f"Pin: GPIO{self.pin_num}")
        print(f"Update interval: {update_interval}s")
        if duration:
            print(f"Duration: {duration}s")
        else:
            print("Duration: Infinite (Press Ctrl+C to stop)")
        print()
        
        start_time = time.time()
        last_display_time = start_time
        
        try:
            while True:
                current_time = time.time()
                
                # Check duration
                if duration and (current_time - start_time) >= duration:
                    break
                
                # Update display at specified interval
                if (current_time - last_display_time) >= update_interval:
                    self._display_statistics()
                    last_display_time = current_time
                
                time.sleep(0.01)  # Small sleep to prevent busy waiting
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            print("\n=== FINAL STATISTICS ===")
            self._display_statistics(detailed=True)
    
    def _display_statistics(self, detailed=False):
        """Display current statistics."""
        stats = self.get_statistics()
        
        # Get timestamp (MicroPython compatible)
        try:
            timestamp = time.strftime('%H:%M:%S')
        except (AttributeError, OSError):
            timestamp = '---'
        
        print(f"\n[{timestamp}] GPIO9 Status:")
        print(f"  Current State: {stats['current_state']} ({'HIGH' if stats['current_state'] else 'LOW'})")
        print(f"  Rising Edges:  {stats['rising_edges']}")
        print(f"  Falling Edges: {stats['falling_edges']}")
        print(f"  Total Pulses:  {stats['total_pulses']}")
        print(f"  Interrupts:    {'Enabled' if stats['interrupt_enabled'] else 'Disabled'}")
        
        if stats['pulse_width']:
            pw = stats['pulse_width']
            print(f"  Pulse Width:   Avg={pw['avg_ms']:.3f}ms (Min={pw['min_ms']:.3f}ms, Max={pw['max_ms']:.3f}ms)")
        
        if stats['period']:
            p = stats['period']
            f = stats['frequency']
            print(f"  Period:        Avg={p['avg_ms']:.3f}ms (Min={p['min_ms']:.3f}ms, Max={p['max_ms']:.3f}ms)")
            print(f"  Frequency:     Avg={f['avg_hz']:.2f}Hz (Min={f['min_hz']:.2f}Hz, Max={f['max_hz']:.2f}Hz)")
        
        if not stats['pulse_width'] and not stats['period']:
            print("  No pulses detected yet...")
    
    def poll_mode(self, duration=10, sample_interval=0.01):
        """
        Monitor GPIO9 using polling (no interrupts).
        Useful for testing or when interrupts aren't available.
        
        Args:
            duration: Monitoring duration in seconds
            sample_interval: Sampling interval in seconds
        """
        print(f"\n=== GPIO9 PULSE DETECTION (POLLING MODE) ===")
        print(f"Pin: GPIO{self.pin_num}")
        print(f"Duration: {duration}s")
        print(f"Sample interval: {sample_interval*1000:.1f}ms")
        print()
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time:
                current_state = self.get_current_state()
                
                # Detect state changes
                if current_state != self.last_state:
                    current_time_us = time.ticks_us()
                    
                    # Rising edge
                    if current_state == 1 and self.last_state == 0:
                        self.rising_edge_count += 1
                        self.total_pulses += 1
                        
                        if self.last_rising_time is not None:
                            period = time.ticks_diff(current_time_us, self.last_rising_time)
                            self.periods.append(period)
                            if len(self.periods) > self.max_history:
                                self.periods.pop(0)
                        
                        self.last_rising_time = current_time_us
                        print(f"[{time.time() - start_time:.3f}s] RISING EDGE detected")
                    
                    # Falling edge
                    elif current_state == 0 and self.last_state == 1:
                        self.falling_edge_count += 1
                        
                        if self.last_rising_time is not None:
                            pulse_width = time.ticks_diff(current_time_us, self.last_rising_time)
                            self.pulse_widths.append(pulse_width)
                            if len(self.pulse_widths) > self.max_history:
                                self.pulse_widths.pop(0)
                        
                        self.last_falling_time = current_time_us
                        print(f"[{time.time() - start_time:.3f}s] FALLING EDGE detected")
                    
                    self.last_state = current_state
                
                time.sleep(sample_interval)
                
        except KeyboardInterrupt:
            print("\nPolling stopped by user")
        finally:
            print("\n=== FINAL STATISTICS ===")
            self._display_statistics(detailed=True)


def main():
    """Main function."""
    print("=== GPIO9 PULSE DETECTOR ===")
    print()
    print("Choose detection mode:")
    print("1. Interrupt mode (real-time, recommended)")
    print("2. Polling mode (for testing)")
    print("3. Quick test (5 seconds)")
    
    try:
        choice = input("\nEnter choice (1-3, default=1): ").strip() or "1"
        
        # Get pull resistor setting
        print("\nPull resistor setting:")
        print("1. None (floating)")
        print("2. PULL_UP")
        print("3. PULL_DOWN")
        pull_choice = input("Enter choice (1-3, default=1): ").strip() or "1"
        
        pull_map = {
            "1": None,
            "2": Pin.PULL_UP,
            "3": Pin.PULL_DOWN
        }
        pull = pull_map.get(pull_choice, None)
        
        # Create detector
        detector = GPIO9PulseDetector(pin=9, pull=pull)
        
        if not detector.initialize():
            print("Failed to initialize GPIO9")
            return
        
        try:
            if choice == "1":
                # Interrupt mode
                detector.enable_interrupts()
                detector.monitor_realtime(duration=None)
            elif choice == "2":
                # Polling mode
                duration_input = input("Enter duration in seconds (default 10): ").strip()
                duration = int(duration_input) if duration_input else 10
                detector.poll_mode(duration=duration)
            elif choice == "3":
                # Quick test
                detector.enable_interrupts()
                detector.monitor_realtime(duration=5)
            else:
                print("Invalid choice, using interrupt mode...")
                detector.enable_interrupts()
                detector.monitor_realtime(duration=None)
        
        finally:
            detector.disable_interrupts()
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

