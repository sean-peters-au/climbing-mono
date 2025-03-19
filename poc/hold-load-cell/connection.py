"""Serial connection manager with health monitoring and robust error handling."""

import serial
import time
import threading
import collections
from typing import Optional, List, Deque, Dict, Any, Tuple

from protocol import CommandPacket, ResponsePacket


class ConnectionHealth:
    """Tracks connection health metrics."""
    
    def __init__(self, window_size: int = 20):
        """
        Initialize the connection health tracker.
        
        Args:
            window_size: Size of the sliding window for metrics
        """
        self.window_size = window_size
        self.success_history: Deque[bool] = collections.deque(maxlen=window_size)
        self.latency_history: Deque[float] = collections.deque(maxlen=window_size)
        self.last_error_time = 0.0
        self.last_error_message = ""
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0
        
    def record_success(self, latency: float) -> None:
        """
        Record a successful communication.
        
        Args:
            latency: Round-trip latency in seconds
        """
        self.success_history.append(True)
        self.latency_history.append(latency)
        self.consecutive_failures = 0
        self.total_requests += 1
        self.successful_requests += 1
        
    def record_failure(self, error_message: str) -> None:
        """
        Record a failed communication.
        
        Args:
            error_message: Description of the error
        """
        self.success_history.append(False)
        self.consecutive_failures += 1
        self.total_requests += 1
        self.last_error_time = time.time()
        self.last_error_message = error_message
        
    def get_success_rate(self) -> float:
        """
        Get the success rate over the sliding window.
        
        Returns:
            Success rate as a value between 0.0 and 1.0
        """
        if not self.success_history:
            return 1.0
        return sum(self.success_history) / len(self.success_history)
    
    def get_average_latency(self) -> float:
        """
        Get the average latency over the sliding window.
        
        Returns:
            Average latency in seconds, or 0.0 if no data
        """
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)
    
    def get_overall_success_rate(self) -> float:
        """
        Get the overall success rate since initialization.
        
        Returns:
            Overall success rate as a value between 0.0 and 1.0
        """
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    def is_healthy(self) -> bool:
        """
        Check if the connection is currently healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        # Connection is unhealthy if there have been 3+ consecutive failures
        if self.consecutive_failures >= 3:
            return False
        
        # Connection is unhealthy if success rate is below 70%
        if self.success_history and self.get_success_rate() < 0.7:
            return False
            
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current connection health status.
        
        Returns:
            Dictionary with health metrics
        """
        return {
            'is_healthy': self.is_healthy(),
            'success_rate': self.get_success_rate(),
            'avg_latency': self.get_average_latency() * 1000,  # Convert to ms
            'consecutive_failures': self.consecutive_failures,
            'total_requests': self.total_requests,
            'overall_success_rate': self.get_overall_success_rate(),
            'last_error_time': self.last_error_time,
            'last_error_message': self.last_error_message
        }


class ConnectionManager:
    """Manages serial communication with Arduino with robust error handling."""
    
    def __init__(self, port: str, baud_rate: int, timeout: float = 0.5):
        """
        Initialize the connection manager.
        
        Args:
            port: Serial port name
            baud_rate: Serial baud rate
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.lock = threading.Lock()
        self.is_connected = False
        
        # Reconnection parameters
        self.reconnect_delay = 1.0
        self.max_reconnect_attempts = 5
        self.current_reconnect_attempts = 0
        
        # Health monitoring
        self.health = ConnectionHealth()
        
    def connect(self) -> bool:
        """
        Connect to the Arduino with retry logic.
        
        Returns:
            True if connection was successful, False otherwise
        """
        with self.lock:
            if self.is_connected:
                return True
                
            for attempt in range(self.max_reconnect_attempts):
                try:
                    print(f"Connecting to {self.port} at {self.baud_rate} baud (attempt {attempt+1})...")
                    self.serial = serial.Serial(
                        self.port, self.baud_rate, timeout=self.timeout)
                    time.sleep(0.5)  # Allow Arduino to reset
                    self.is_connected = True
                    self.current_reconnect_attempts = 0
                    print(f"Successfully connected to {self.port}")
                    return True
                except serial.SerialException as e:
                    error_msg = f"Connection attempt {attempt+1} failed: {e}"
                    print(error_msg)
                    self.health.record_failure(error_msg)
                    time.sleep(self.reconnect_delay)  # Wait before retry
            
            self.current_reconnect_attempts += 1
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Arduino."""
        with self.lock:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.is_connected = False
    
    def send_receive(self, command: CommandPacket) -> Optional[ResponsePacket]:
        """
        Send a command and receive response with retry logic.
        
        Args:
            command: CommandPacket to send
            
        Returns:
            ResponsePacket if successful, None otherwise
        """
        max_attempts = 3
        
        for attempt in range(max_attempts):
            if not self.is_connected and not self.connect():
                continue
                
            start_time = time.time()
            
            try:
                with self.lock:
                    # Clear input buffer
                    self.serial.reset_input_buffer()
                    
                    # Send command
                    cmd_data = command.pack()
                    self.serial.write(cmd_data)
                    self.serial.flush()
                    
                    # Read response
                    response_data = self.serial.read(ResponsePacket.size())
                    
                    # Calculate latency
                    latency = time.time() - start_time
                    
                    if len(response_data) == ResponsePacket.size():
                        # Successfully received response
                        response = ResponsePacket.unpack(response_data)
                        
                        # Check if sequence ID matches
                        if response.seq_id == command.seq_id:
                            # Record success
                            self.health.record_success(latency)
                            return response
                        else:
                            error_msg = f"Sequence ID mismatch: sent {command.seq_id}, received {response.seq_id}"
                            print(error_msg)
                            self.health.record_failure(error_msg)
                    else:
                        error_msg = f"Incomplete response (attempt {attempt+1}): got {len(response_data)} bytes, expected {ResponsePacket.size()}"
                        print(error_msg)
                        self.health.record_failure(error_msg)
            except serial.SerialException as e:
                error_msg = f"Communication error (attempt {attempt+1}): {e}"
                print(error_msg)
                self.health.record_failure(error_msg)
                self.is_connected = False
                
            # Wait before retry with exponential backoff
            retry_delay = self.reconnect_delay * (2 ** attempt)
            time.sleep(retry_delay)
            
        return None
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the current connection health status.
        
        Returns:
            Dictionary with health metrics
        """
        status = self.health.get_status()
        status['is_connected'] = self.is_connected
        return status 