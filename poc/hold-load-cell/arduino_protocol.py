import serial
import struct
import time
import threading
import queue
import math
from typing import List, Dict, Any, Optional, Tuple


class ArduinoProtocol:
    """
    Protocol for communicating with Arduino load cell controller.
    Uses a master-initiated polling approach with fixed command/response structs.
    """
    
    # System constants
    MAX_LOAD_CELLS = 4
    
    # Status codes
    STATUS_IDLE = 0
    STATUS_ZEROING = 1
    STATUS_CALIBRATING = 2
    STATUS_STREAMING = 3
    STATUS_ERROR = 255
    
    # Error codes
    ERR_NONE = 0
    ERR_INVALID_COMMAND = 1
    ERR_INVALID_CELL_ID = 2
    ERR_CELL_NOT_CONFIGURED = 3
    ERR_CALIBRATION_FAILED = 4
    
    # Command masks (bit positions in the command byte)
    CMD_CONFIGURE = 0b00000001
    CMD_ZERO = 0b00000010
    CMD_CALIBRATE = 0b00000100
    CMD_RESET = 0b00001000
    
    def __init__(self, port: str, baud_rate: int, poll_interval: float = 0.05):
        """
        Initialize the Arduino protocol handler.
        
        Args:
            port: Serial port name
            baud_rate: Serial baud rate
            poll_interval: Polling interval in seconds (default: 50ms)
        """
        # Serial configuration
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.poll_interval = poll_interval
        
        # Thread control
        self.running = False
        self.io_thread = None
        self.lock = threading.Lock()  # Lock for thread-safe access to shared resources
        
        # Command queue
        self.command_queue = queue.Queue()
        
        # Current state
        self.state = {
            'status': self.STATUS_IDLE,
            'error': self.ERR_NONE,
            'active_cell': 255,  # No active cell
            'cell_configured': [False] * self.MAX_LOAD_CELLS,
            'cell_readings': [0.0] * self.MAX_LOAD_CELLS,
            'calibration_factors': [0.0] * self.MAX_LOAD_CELLS
        }
        
        # Struct formats
        # CommandStruct: command_flags(B), cell_id(B), dout_pin(B), sck_pin(B), calibration_mass(f), reserved(4B)
        self.command_struct_format = '<BBBBf4B'
        self.command_struct_size = struct.calcsize(self.command_struct_format)
        
        # ResponseStruct: status(B), error(B), active_cell(B), 
        #                 cell_configured(4B), cell_readings(4f), calibration_factors(4f)
        self.response_struct_format = '<BBB4B4f4f'
        self.response_struct_size = struct.calcsize(self.response_struct_format)
    
    def connect(self) -> bool:
        """
        Connect to the Arduino.
        
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=0.5)
            time.sleep(0.5)  # Allow time for Arduino to reset
            
            # Start IO thread
            self.running = True
            self.io_thread = threading.Thread(target=self._io_loop)
            self.io_thread.daemon = True
            self.io_thread.start()
            
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Arduino and stop the IO thread."""
        self.running = False
        if self.io_thread:
            self.io_thread.join(timeout=1.0)
        
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state (thread-safe).
        
        Returns:
            Copy of the current state dictionary
        """
        with self.lock:
            return self.state.copy()
    
    def get_readings(self) -> List[float]:
        """
        Get the current load cell readings (thread-safe).
        
        Returns:
            List of load cell readings
        """
        with self.lock:
            return self.state['cell_readings'].copy()
    
    def configure_cell(self, cell_id: int, dout_pin: int, sck_pin: int) -> None:
        """
        Configure a load cell.
        
        Args:
            cell_id: Cell ID (0-3)
            dout_pin: DOUT pin number
            sck_pin: SCK pin number
        """
        command = {
            'flags': self.CMD_CONFIGURE,
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
            cell_id: Cell ID (0-3), or 255 for all cells
        """
        command = {
            'flags': self.CMD_ZERO,
            'cell_id': cell_id,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': 0.0
        }
        self.command_queue.put(command)
    
    def zero_all_cells(self) -> None:
        """Zero all configured load cells."""
        self.zero_cell(255)  # 255 means all cells
    
    def calibrate_cell(self, cell_id: int, known_mass: float) -> None:
        """
        Calibrate a load cell with a known mass.
        
        Args:
            cell_id: Cell ID (0-3)
            known_mass: Known mass in grams
        """
        command = {
            'flags': self.CMD_CALIBRATE,
            'cell_id': cell_id,
            'dout_pin': 0,
            'sck_pin': 0,
            'calibration_mass': known_mass
        }
        self.command_queue.put(command)
    
    def reset_system(self) -> None:
        """Reset the Arduino system."""
        command = {
            'flags': self.CMD_RESET,
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
            with self.lock:
                if self.state['status'] == self.STATUS_IDLE:
                    return True
            time.sleep(0.1)
        return False
    
    def _io_loop(self) -> None:
        """Main IO thread loop for communicating with Arduino."""
        last_poll_time = 0.0
        
        while self.running:
            current_time = time.time()
            
            # Poll at the specified interval
            if current_time - last_poll_time >= self.poll_interval:
                last_poll_time = current_time
                
                try:
                    # Prepare command to send
                    command = self._prepare_command()
                    
                    # Send command to Arduino
                    self._send_command(command)
                    
                    # Read response from Arduino
                    self._read_response()
                except Exception as e:
                    print(f"Error in IO loop: {e}")
                    time.sleep(0.1)  # Wait a bit before trying again
            
            # Small sleep to prevent CPU hogging
            time.sleep(0.001)
    
    def _prepare_command(self) -> Dict[str, Any]:
        """
        Prepare command struct to send to Arduino.
        
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
            pass  # No command to process
        
        return command
    
    def _send_command(self, command: Dict[str, Any]) -> None:
        """
        Send a command struct to the Arduino.
        
        Args:
            command: Command dictionary
        """
        if not self.serial or not self.serial.is_open:
            return
        
        # Pack command struct
        command_data = struct.pack(
            self.command_struct_format,
            command['flags'],
            command['cell_id'],
            command['dout_pin'],
            command['sck_pin'],
            command['calibration_mass'],
            0, 0, 0, 0  # Reserved bytes
        )
        
        # Send to Arduino
        self.serial.write(command_data)
        self.serial.flush()
    
    def _read_response(self) -> None:
        """Read and process response struct from Arduino."""
        if not self.serial or not self.serial.is_open:
            return
        
        # Read expected number of bytes
        response_data = self.serial.read(self.response_struct_size)
        
        if len(response_data) == self.response_struct_size:
            # Unpack response struct
            unpacked = struct.unpack(self.response_struct_format, response_data)
            
            # Extract fields
            status = unpacked[0]
            error = unpacked[1]
            active_cell = unpacked[2]
            cell_configured = list(unpacked[3:7])
            cell_readings = list(unpacked[7:11])
            calibration_factors = list(unpacked[11:15])
            
            # Convert cell_configured from bytes to booleans
            cell_configured = [bool(x) for x in cell_configured]
            
            # Update state (thread-safe)
            with self.lock:
                self.state['status'] = status
                self.state['error'] = error
                self.state['active_cell'] = active_cell
                self.state['cell_configured'] = cell_configured
                self.state['cell_readings'] = cell_readings
                self.state['calibration_factors'] = calibration_factors 