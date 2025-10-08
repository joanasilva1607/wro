"""
Communication Hardware Abstraction Layer
Provides a clean interface for UART and other communication protocols.
"""

from machine import Pin, UART
import time
from .base_hal import BaseHAL


class CommunicationHAL(BaseHAL):
    """Hardware abstraction layer for UART communication."""
    
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=16, rx_pin=17):
        """
        Initialize communication HAL.
        
        Args:
            uart_id: UART interface ID
            baudrate: Communication baud rate
            tx_pin: TX pin number
            rx_pin: RX pin number
        """
        super().__init__()
        self.uart_id = uart_id
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        
        # Hardware component
        self._uart = None
        
        # Message handling
        self._message_buffer = ""
        self._message_queue = []
        self._max_queue_size = 10
        
        # Statistics
        self._bytes_sent = 0
        self._bytes_received = 0
        self._messages_sent = 0
        self._messages_received = 0
        
    def initialize(self):
        """Initialize UART communication."""
        try:
            self._uart = UART(
                self.uart_id, 
                baudrate=self.baudrate, 
                tx=Pin(self.tx_pin), 
                rx=Pin(self.rx_pin)
            )
            
            # Clear any existing data
            self._uart.read()
            self._is_initialized = True
            
        except Exception as e:
            self._handle_error(f"Communication initialization failed: {e}")
            
    def send_message(self, message):
        """
        Send a message via UART.
        
        Args:
            message: String message to send
        """
        if not self._is_initialized:
            self._handle_error("Communication not initialized")
            return False
            
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
                
            bytes_written = self._uart.write(message)
            self._bytes_sent += bytes_written
            self._messages_sent += 1
            return True
            
        except Exception as e:
            self._handle_error(f"Message send failed: {e}")
            return False
            
    def send_data(self, data):
        """
        Send raw data via UART.
        
        Args:
            data: Bytes or list of bytes to send
        """
        if not self._is_initialized:
            self._handle_error("Communication not initialized")
            return False
            
        try:
            if isinstance(data, list):
                data = bytes(data)
                
            bytes_written = self._uart.write(data)
            self._bytes_sent += bytes_written
            return True
            
        except Exception as e:
            self._handle_error(f"Data send failed: {e}")
            return False
            
    def read_data(self, num_bytes=None):
        """
        Read raw data from UART.
        
        Args:
            num_bytes: Number of bytes to read (None for all available)
            
        Returns:
            Bytes data or None if no data available
        """
        if not self._is_initialized:
            return None
            
        try:
            if not self._uart.any():
                return None
                
            if num_bytes is None:
                data = self._uart.read()
            else:
                data = self._uart.read(num_bytes)
                
            if data:
                self._bytes_received += len(data)
                
            return data
            
        except Exception as e:
            self._handle_error(f"Data read failed: {e}")
            return None
            
    def read_message(self, delimiter='\n'):
        """
        Read a complete message terminated by delimiter.
        
        Args:
            delimiter: Message delimiter character
            
        Returns:
            Complete message string or None
        """
        data = self.read_data()
        if not data:
            return None
            
        try:
            self._message_buffer += data.decode('utf-8')
            
            if delimiter in self._message_buffer:
                parts = self._message_buffer.split(delimiter, 1)
                message = parts[0]
                self._message_buffer = parts[1] if len(parts) > 1 else ""
                
                self._messages_received += 1
                return message
                
        except Exception as e:
            self._handle_error(f"Message read failed: {e}")
            
        return None
        
    def has_data(self):
        """Check if data is available to read."""
        if not self._is_initialized:
            return False
        return self._uart.any() > 0
        
    def flush_input(self):
        """Flush input buffer."""
        if self._is_initialized and self._uart.any():
            self._uart.read()
            self._message_buffer = ""
            
    def flush_output(self):
        """Flush output buffer (wait for transmission to complete)."""
        if self._is_initialized:
            # On most platforms, write() is blocking, so this is usually not needed
            # But we can add a small delay to ensure transmission
            time.sleep(0.001)
            
    def get_statistics(self):
        """Get communication statistics."""
        return {
            'bytes_sent': self._bytes_sent,
            'bytes_received': self._bytes_received,
            'messages_sent': self._messages_sent,
            'messages_received': self._messages_received,
            'buffer_size': len(self._message_buffer),
            'queue_size': len(self._message_queue)
        }
        
    def reset_statistics(self):
        """Reset communication statistics."""
        self._bytes_sent = 0
        self._bytes_received = 0
        self._messages_sent = 0
        self._messages_received = 0
        
    def queue_message(self, message):
        """
        Queue a message for later sending.
        
        Args:
            message: Message to queue
        """
        if len(self._message_queue) < self._max_queue_size:
            self._message_queue.append(message)
            return True
        return False
        
    def send_queued_messages(self):
        """Send all queued messages."""
        sent_count = 0
        while self._message_queue:
            message = self._message_queue.pop(0)
            if self.send_message(message):
                sent_count += 1
            else:
                # Put message back at front of queue if send failed
                self._message_queue.insert(0, message)
                break
        return sent_count
        
    def clear_queue(self):
        """Clear message queue."""
        self._message_queue.clear()
        
    def deinitialize(self):
        """Deinitialize communication hardware."""
        if self._is_initialized:
            self.flush_output()
            if self._uart:
                self._uart.deinit()
            self._is_initialized = False
