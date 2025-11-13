#!/usr/bin/env python3
"""
Serial Read Debug for GPIO9
Display real-time serial data from GPIO9 (RX pin).
"""

import time
import sys
from machine import Pin, UART


class GPIO9SerialDebug:
    """Debug utility for serial reading on GPIO9."""
    
    def __init__(self, baudrate=115200, uart_id=1, tx_pin=None):
        """
        Initialize serial debug on GPIO9.
        
        Args:
            baudrate: Serial baud rate (default: 115200)
            uart_id: UART interface ID (default: 1, to avoid conflict with main UART)
            tx_pin: TX pin number (optional, for full duplex)
        """
        self.baudrate = baudrate
        self.uart_id = uart_id
        self.rx_pin = 9  # GPIO9
        self.tx_pin = tx_pin
        
        self._uart = None
        self._bytes_received = 0
        self._packets_received = 0
        self._start_time = None
        
    def initialize(self):
        """Initialize UART on GPIO9."""
        try:
            print(f"Initializing UART{self.uart_id} on GPIO9 (RX)...")
            print(f"Baudrate: {self.baudrate}")
            
            if self.tx_pin is not None:
                self._uart = UART(
                    self.uart_id,
                    baudrate=self.baudrate,
                    tx=Pin(self.tx_pin),
                    rx=Pin(self.rx_pin)
                )
                print(f"TX pin: GPIO{self.tx_pin}")
            else:
                # RX only mode
                self._uart = UART(
                    self.uart_id,
                    baudrate=self.baudrate,
                    rx=Pin(self.rx_pin)
                )
                print("TX pin: Not configured (RX only mode)")
            
            # Clear any existing data (read all available)
            if self._uart.any():
                self._uart.read(self._uart.any())
            
            print("✓ UART initialized successfully")
            return True
            
        except Exception as e:
            print(f"✗ UART initialization failed: {e}")
            return False
    
    def deinitialize(self):
        """Deinitialize UART."""
        if self._uart:
            try:
                self._uart.deinit()
                print("UART deinitialized")
            except:
                pass
    
    def has_data(self):
        """Check if data is available."""
        if not self._uart:
            return False
        return self._uart.any() > 0
    
    def read_data(self, num_bytes=1):
        """
        Read data from UART.
        
        Args:
            num_bytes: Number of bytes to read (default: 1)
            
        Returns:
            Bytes data or None
        """
        if not self._uart:
            return None
        
        try:
            if not self.has_data():
                return None
            
            # Always read exactly num_bytes (default 1)
            data = self._uart.read(num_bytes)
            
            if data:
                self._bytes_received += len(data)
                self._packets_received += 1
            
            return data
            
        except Exception as e:
            print(f"Read error: {e}")
            return None
    
    def get_statistics(self):
        """Get read statistics."""
        elapsed = time.time() - self._start_time if self._start_time else 0
        bytes_per_sec = self._bytes_received / elapsed if elapsed > 0 else 0
        
        return {
            'bytes_received': self._bytes_received,
            'packets_received': self._packets_received,
            'elapsed_time': elapsed,
            'bytes_per_second': bytes_per_sec
        }
    
    def format_data_hex(self, data):
        """Format data as hexadecimal string."""
        return ' '.join([f'{b:02X}' for b in data])
    
    def format_data_decimal(self, data):
        """Format data as decimal values."""
        return ' '.join([f'{b:3d}' for b in data])
    
    def format_data_ascii(self, data):
        """Format data as ASCII characters (with escape for non-printable)."""
        result = []
        for b in data:
            if 32 <= b <= 126:  # Printable ASCII
                result.append(chr(b))
            else:
                result.append('.')
        return ''.join(result)
    
    def display_realtime(self, display_format='all', update_interval=0.1):
        """
        Display real-time serial data.
        
        Args:
            display_format: 'hex', 'decimal', 'ascii', or 'all'
            update_interval: Update interval in seconds
        """
        print("\n=== GPIO9 SERIAL READ DEBUG (REAL-TIME) ===")
        print(f"RX Pin: GPIO{self.rx_pin}")
        print(f"Baudrate: {self.baudrate}")
        print(f"Display format: {display_format}")
        print("Press Ctrl+C to stop\n")
        
        self._start_time = time.time()
        
        # Display header
        if display_format == 'all':
            print("┌─────────┬──────────────┬─────────────────────────────────────────────────────────┬──────────────────┐")
            print("│  Time   │    Bytes     │                        HEX                                │      ASCII       │")
            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┼──────────────────┤")
        elif display_format == 'hex':
            print("┌─────────┬──────────────┬─────────────────────────────────────────────────────────┐")
            print("│  Time   │    Bytes     │                        HEX                                │")
            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┤")
        elif display_format == 'decimal':
            print("┌─────────┬──────────────┬─────────────────────────────────────────────────────────┐")
            print("│  Time   │    Bytes     │                      DECIMAL                              │")
            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┤")
        elif display_format == 'ascii':
            print("┌─────────┬──────────────┬─────────────────────────────────────────────────────────┐")
            print("│  Time   │    Bytes     │                        ASCII                              │")
            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┤")
        
        reading_count = 0
        
        try:
            while True:
                data = self.read_data()
                
                if data:
                    # Get current time
                    try:
                        current_time = time.strftime("%H:%M:%S")
                    except AttributeError:
                        # MicroPython fallback
                        elapsed = time.time() - self._start_time
                        current_time = f"{elapsed:06.2f}"
                    
                    num_bytes = len(data)
                    hex_str = self.format_data_hex(data)
                    decimal_str = self.format_data_decimal(data)
                    ascii_str = self.format_data_ascii(data)
                    
                    # Truncate long strings for display
                    max_hex_len = 60
                    max_ascii_len = 16
                    
                    if len(hex_str) > max_hex_len:
                        hex_str = hex_str[:max_hex_len] + "..."
                    if len(ascii_str) > max_ascii_len:
                        ascii_str = ascii_str[:max_ascii_len]
                    
                    # Display based on format
                    if display_format == 'all':
                        print(f"│{current_time}│ {num_bytes:>4} bytes │ {hex_str:<60} │ {ascii_str:<16} │")
                    elif display_format == 'hex':
                        print(f"│{current_time}│ {num_bytes:>4} bytes │ {hex_str:<60} │")
                    elif display_format == 'decimal':
                        print(f"│{current_time}│ {num_bytes:>4} bytes │ {decimal_str:<60} │")
                    elif display_format == 'ascii':
                        print(f"│{current_time}│ {num_bytes:>4} bytes │ {ascii_str:<60} │")
                    
                    reading_count += 1
                    
                    # Add separator every 10 readings
                    if reading_count % 10 == 0:
                        if display_format == 'all':
                            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┼──────────────────┤")
                        else:
                            print("├─────────┼──────────────┼─────────────────────────────────────────────────────────┤")
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            if display_format == 'all':
                print("└─────────┴──────────────┴─────────────────────────────────────────────────────────┴──────────────────┘")
            else:
                print("└─────────┴──────────────┴─────────────────────────────────────────────────────────┘")
            print("\nReal-time display stopped by user")
        except Exception as e:
            print(f"\nError during real-time display: {e}")
    
    def collect_statistics(self, duration=10, sample_interval=0.1):
        """
        Collect statistics over a period of time.
        
        Args:
            duration: Duration in seconds
            sample_interval: Sampling interval in seconds
        """
        print(f"\n=== GPIO9 SERIAL STATISTICS COLLECTION ===")
        print(f"Collecting data for {duration} seconds...")
        print(f"Sample interval: {sample_interval}s\n")
        
        self._start_time = time.time()
        samples = []
        end_time = time.time() + duration
        
        try:
            while time.time() < end_time:
                data = self.read_data()
                if data:
                    samples.append({
                        'timestamp': time.time(),
                        'data': data,
                        'length': len(data)
                    })
                time.sleep(sample_interval)
        
        except KeyboardInterrupt:
            print("Collection interrupted by user")
        
        # Display statistics
        print("\n=== STATISTICS SUMMARY ===")
        print(f"Total samples: {len(samples)}")
        
        if samples:
            total_bytes = sum(s['length'] for s in samples)
            avg_bytes = total_bytes / len(samples) if samples else 0
            max_bytes = max(s['length'] for s in samples)
            min_bytes = min(s['length'] for s in samples)
            
            stats = self.get_statistics()
            
            print(f"Total bytes received: {stats['bytes_received']}")
            print(f"Total packets: {stats['packets_received']}")
            print(f"Average bytes per packet: {avg_bytes:.2f}")
            print(f"Max packet size: {max_bytes} bytes")
            print(f"Min packet size: {min_bytes} bytes")
            print(f"Average rate: {stats['bytes_per_second']:.2f} bytes/sec")
            
            # Show first few samples
            print("\n=== FIRST 5 SAMPLES ===")
            for i, sample in enumerate(samples[:5]):
                print(f"\nSample {i+1}:")
                print(f"  Length: {sample['length']} bytes")
                print(f"  HEX: {self.format_data_hex(sample['data'])}")
                print(f"  ASCII: {self.format_data_ascii(sample['data'])}")
        else:
            print("No data received during collection period")
    
    def test_connection(self, timeout=5):
        """
        Test serial connection and display first received data.
        
        Args:
            timeout: Timeout in seconds
        """
        print("\n=== GPIO9 SERIAL CONNECTION TEST ===")
        print(f"Waiting for data (timeout: {timeout}s)...")
        
        start_time = time.time()
        data_received = False
        
        while (time.time() - start_time) < timeout:
            if self.has_data():
                data = self.read_data()
                if data:
                    data_received = True
                    print(f"✓ Data received!")
                    print(f"  Length: {len(data)} bytes")
                    print(f"  HEX: {self.format_data_hex(data)}")
                    print(f"  Decimal: {self.format_data_decimal(data)}")
                    print(f"  ASCII: {self.format_data_ascii(data)}")
                    break
            time.sleep(0.1)
        
        if not data_received:
            print("✗ No data received within timeout period")
            print("  Check:")
            print("  - GPIO9 is connected to the TX pin of the sending device")
            print("  - Baudrate matches the sending device")
            print("  - Ground is connected between devices")
            print("  - Device is actually transmitting data")
        
        return data_received


def main():
    """Main debug function."""
    print("=== GPIO9 SERIAL READ DEBUG UTILITY ===")
    print("Choose debug mode:")
    print("1. Real-time display (all formats)")
    print("2. Real-time display (hex only)")
    print("3. Real-time display (decimal only)")
    print("4. Real-time display (ASCII only)")
    print("5. Connection test")
    print("6. Statistics collection")
    
    try:
        choice = input("\nEnter choice (1-6): ").strip()
        
        # Get baudrate if needed
        baudrate_input = input("Enter baudrate (default 115200): ").strip()
        baudrate = int(baudrate_input) if baudrate_input else 115200
        
        # Get UART ID
        uart_id_input = input("Enter UART ID (default 1): ").strip()
        uart_id = int(uart_id_input) if uart_id_input else 1
        
        # Create debug instance
        debug = GPIO9SerialDebug(baudrate=baudrate, uart_id=uart_id)
        
        if not debug.initialize():
            print("Failed to initialize UART")
            return
        
        try:
            if choice == '1':
                debug.display_realtime(display_format='all')
            elif choice == '2':
                debug.display_realtime(display_format='hex')
            elif choice == '3':
                debug.display_realtime(display_format='decimal')
            elif choice == '4':
                debug.display_realtime(display_format='ascii')
            elif choice == '5':
                debug.test_connection()
            elif choice == '6':
                duration_input = input("Enter collection duration in seconds (default 10): ").strip()
                duration = int(duration_input) if duration_input else 10
                debug.collect_statistics(duration=duration)
            else:
                print("Invalid choice, running connection test...")
                debug.test_connection()
        
        finally:
            debug.deinitialize()
            
    except KeyboardInterrupt:
        print("\nDebug utility interrupted by user")
    except Exception as e:
        print(f"Debug utility error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


