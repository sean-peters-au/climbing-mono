"""High-level client for interacting with the Arduino load cell controller."""

import threading
import queue
import time
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

from protocol import (
    CommandPacket, ResponsePacket, Command, Status, Error, MAX_LOAD_CELLS,
    cell_configured_to_bool
)
from connection import ConnectionManager


# Type aliases
StateCallbackType = Callable[[Dict[str, Any], Dict[str, Any]], None]
ErrorCallbackType = Callable[[str], None]
HealthCallbackType = Callable[[Dict[str, Any]], None]


class ArduinoClient:
    """High-level client for interacting with the Arduino load cell controller."""
    
    def __init__(self, port: str, baud_rate: int, poll_interval: float = 0.05):
        """
        Initialize the Arduino client.
        
        Args:
            port: Serial port name
            baud_rate: Serial baud rate
            poll_interval: Polling interval in seconds (default: 50ms)
        """
        self.connection = ConnectionManager(port, baud_rate)
        self.poll_interval = poll_interval
        
        # Thread management
        self.running = False
        self.io_thread = None
        self.state_lock = threading.Lock()
        
        # Command queue
        self.command_queue = queue.Queue()
        
        # Sequence ID counter
        self.seq_id = 0
        self.seq_id_lock = threading.Lock()
        
        # State data
        self.state = {
            'status': Status.IDLE,
            'error': Error.NONE,
            'active_cell': 255,  # No active cell
            'cell_configured': [False] * MAX_LOAD_CELLS,
            'cell_readings': [0.0] * MAX_LOAD_CELLS,
            'calibration_factors': [0.0] * MAX_LOAD_CELLS
        }
        
        # Health data
        self.connection_health = {
            'is_connected': False,
            'is_healthy': True,
            'success_rate': 1.0,
            'avg_latency': 0.0,
            'consecutive_failures': 0
        }
        
        # Event callbacks
        self.on_state_changed: Optional[StateCallbackType] = None
        self.on_error: Optional[ErrorCallbackType] = None
        self.on_health_changed: Optional[HealthCallbackType] = None
        
    def start(self) -> bool:
        """
        Start the client and IO thread.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.connection.connect():
            return False
            
        self.running = True
        self.io_thread = threading.Thread(target=self._io_loop)
        self.io_thread.daemon = True
        self.io_thread.start()
        return True
        
    def stop(self) -> None:
        """Stop the client and IO thread."""
        self.running = False
        if self.io_thread:
            self.io_thread.join(timeout=1.0)
        self.connection.disconnect()
        
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state (thread-safe).
        
        Returns:
            Copy of the current state dictionary
        """
        with self.state_lock:
            return self.state.copy()
            
    def get_readings(self) -> List[float]:
        """
        Get the current load cell readings (thread-safe).
        
        Returns:
            List of load cell readings
        """
        with self.state_lock:
            return self.state['cell_readings'].copy()
    
    def get_cell_status(self, cell_id: int) -> Dict[str, Any]:
        """
        Get status information for a specific cell.
        
        Args:
            cell_id: Cell ID (0-3)
            
        Returns:
            Dictionary with cell status information
        """
        if not 0 <= cell_id < MAX_LOAD_CELLS:
            raise ValueError(f"Cell ID must be between 0 and {MAX_LOAD_CELLS-1}")
            
        with self.state_lock:
            return {
                'configured': self.state['cell_configured'][cell_id],
                'reading': self.state['cell_readings'][cell_id],
                'calibration_factor': self.state['calibration_factors'][cell_id],
                'active': self.state['active_cell'] == cell_id
            }
    
    def get_connection_health(self) -> Dict[str, Any]:
        """
        Get the connection health status.
        
        Returns:
            Dictionary with connection health information
        """
        return self.connection_health.copy()
            
    def configure_cell(self, cell_id: int, dout_pin: int, sck_pin: int) -> None:
        """
        Configure a load cell.
        
        Args:
            cell_id: Cell ID (0-3)
            dout_pin: DOUT pin number
            sck_pin: SCK pin number
        """
        if not 0 <= cell_id < MAX_LOAD_CELLS:
            raise ValueError(f"Cell ID must be between 0 and {MAX_LOAD_CELLS-1}")
            
        command = {
            'flags': Command.CONFIGURE,
            'cell_id': cell_id,
            'dout_pin': dout_pin,
            'sck_pin': sck_pin,
            'calibration_mass': 0.0
        }
        self.command_queue.put(command)
        
    def zero_cell(self, cell_id: int) -> None:
        """
        Zero a specific load cell.
        
        Args:
            cell_id: Cell ID (0-3)
        """
        if not 0 <= cell_id < MAX_LOAD_CELLS:
            raise ValueError(f"Cell ID must be between 0 and {MAX_LOAD_CELLS-1}")
            
        command = {
            'flags': Command.ZERO,
            'cell_id': cell_id,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': 0.0
        }
        self.command_queue.put(command)
        
    def zero_all_cells(self) -> None:
        """Zero all configured load cells."""
        command = {
            'flags': Command.ZERO,
            'cell_id': 255,  # 255 means all cells
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': 0.0
        }
        self.command_queue.put(command)
        
    def calibrate_cell(self, cell_id: int, known_mass: float) -> None:
        """
        Calibrate a load cell with a known mass.
        
        Args:
            cell_id: Cell ID (0-3)
            known_mass: Known mass in grams
        """
        if not 0 <= cell_id < MAX_LOAD_CELLS:
            raise ValueError(f"Cell ID must be between 0 and {MAX_LOAD_CELLS-1}")
            
        command = {
            'flags': Command.CALIBRATE,
            'cell_id': cell_id,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': known_mass
        }
        self.command_queue.put(command)
        
    def reset_system(self) -> None:
        """Reset the Arduino system."""
        command = {
            'flags': Command.RESET,
            'cell_id': 0,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': 0.0
        }
        self.command_queue.put(command)
    
    def wait_for_idle(self, timeout: float = 5.0) -> bool:
        """
        Wait until the Arduino is in IDLE state.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if Arduino became IDLE within timeout, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.state_lock:
                if self.state['status'] == Status.IDLE:
                    return True
            time.sleep(0.1)
        return False
    
    def get_next_seq_id(self) -> int:
        """
        Get the next sequence ID (thread-safe).
        
        Returns:
            Next sequence ID
        """
        with self.seq_id_lock:
            seq_id = self.seq_id
            self.seq_id = (self.seq_id + 1) % 256  # Keep within byte range
            return seq_id
            
    def _io_loop(self) -> None:
        """Main IO thread loop for communicating with Arduino."""
        last_poll_time = 0.0
        
        while self.running:
            current_time = time.time()
            
            # Poll at the specified interval
            if current_time - last_poll_time >= self.poll_interval:
                last_poll_time = current_time
                
                try:
                    # Prepare command
                    command = self._prepare_command()
                    
                    # Create command packet
                    seq_id = self.get_next_seq_id()
                    cmd_packet = CommandPacket.create(
                        seq_id=seq_id,
                        flags=command['flags'],
                        cell_id=command['cell_id'],
                        dout_pin=command['dout_pin'],
                        sck_pin=command['sck_pin'],
                        calibration_mass=command['calibration_mass']
                    )
                    
                    # Send command and get response
                    response = self.connection.send_receive(cmd_packet)
                    
                    # Update connection health
                    new_health = self.connection.get_health()
                    health_changed = self._update_connection_health(new_health)
                    
                    if response:
                        # Update state from response
                        self._update_state_from_response(response)
                    elif self.connection_health['consecutive_failures'] > 0:
                        if self.on_error:
                            self.on_error("Failed to get response from Arduino")
                    
                    # Notify health change if needed
                    if health_changed and self.on_health_changed:
                        self.on_health_changed(self.connection_health)
                except Exception as e:
                    print(f"Error in IO loop: {e}")
                    if self.on_error:
                        self.on_error(f"Client error: {e}")
                    
            # Small sleep to prevent CPU hogging
            time.sleep(0.001)
            
    def _prepare_command(self) -> Dict[str, Any]:
        """
        Prepare command to send to Arduino.
        
        Returns:
            Command dictionary
        """
        # Default empty command
        command = {
            'flags': 0,
            'cell_id': 0,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': 0.0
        }
        
        # Check if there's a command in the queue
        try:
            new_command = self.command_queue.get_nowait()
            command.update(new_command)
        except queue.Empty:
            pass
            
        return command
        
    def _update_state_from_response(self, response: ResponsePacket) -> None:
        """
        Update state from response packet.
        
        Args:
            response: Response packet from Arduino
        """
        old_state = None
        
        with self.state_lock:
            # Save old state for comparison
            old_state = self.state.copy()
            
            # Update state
            self.state['status'] = response.status
            self.state['error'] = response.error
            self.state['active_cell'] = response.active_cell
            
            # Convert cell_configured bytes to bool list
            self.state['cell_configured'] = cell_configured_to_bool(response.cell_configured)
            
            # Update readings and calibration factors
            self.state['cell_readings'] = list(response.cell_readings)
            self.state['calibration_factors'] = list(response.calibration_factors)
        
        # Notify state changed if callback is set
        if self.on_state_changed:
            self.on_state_changed(old_state, self.state.copy())
            
        # Notify error if set
        if response.error != Error.NONE and self.on_error:
            try:
                error_name = Error(response.error).name
                self.on_error(f"Arduino error: {error_name}")
            except ValueError:
                self.on_error(f"Arduino error code: {response.error}")
    
    def _update_connection_health(self, new_health: Dict[str, Any]) -> bool:
        """
        Update connection health status.
        
        Args:
            new_health: New health data from connection manager
            
        Returns:
            True if health status changed, False otherwise
        """
        changed = False
        
        # Check for changes in important metrics
        if (self.connection_health['is_connected'] != new_health['is_connected'] or
            self.connection_health['is_healthy'] != new_health['is_healthy'] or
            abs(self.connection_health['success_rate'] - new_health['success_rate']) > 0.05 or
            self.connection_health['consecutive_failures'] != new_health['consecutive_failures']):
            changed = True
        
        # Update health data
        self.connection_health = new_health
        
        return changed 