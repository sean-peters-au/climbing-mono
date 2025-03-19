import serial
import time
import threading
import queue
import math
import struct
import collections

class LoadCellManager:
    # Command constants
    COMMAND_ZERO = 'z'
    COMMAND_CALIBRATE = 'c'
    COMMAND_STREAM = 's'
    COMMAND_NEW_CELL = 'n'
    COMMAND_STOP = 'q'
    COMMAND_BINARY = 'b'
    COMMAND_TEXT = 't'
    COMMAND_DEBUG = 'd'
    
    # Binary protocol constants
    PACKET_HEADER = 0xAA
    PACKET_FOOTER = 0x55
    
    def __init__(self, port, baud_rate):
        """Initialize the LoadCellManager with the given serial port and baud rate.
        
        Args:
            port: Serial port to connect to
            baud_rate: Baud rate for serial communication
        """
        print(f"Initializing LoadCellManager on port {port} at {baud_rate} baud")
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=0.01)  # Shorter timeout for more responsive reads
            time.sleep(0.5)  # Shorter sleep time
            print("Serial connection established")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise
            
        self.data_queues = []
        self.faulty_cells = []
        self.stop_event = threading.Event()
        self.stream_thread = None
        self.use_binary_protocol = False  # Default to text protocol
        
        # Circular buffer for binary data
        self.buffer = bytearray(1024)  # 1KB buffer
        self.buffer_pos = 0
        
        # Timing statistics for performance monitoring
        self.latency_stats = collections.deque(maxlen=100)
        
        # Debug flags
        self.debug = True
        
        # Clear any pending data
        self.flush_buffers()

    def flush_buffers(self):
        """Flush both input and output buffers."""
        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            # Read any leftover data
            while self.ser.in_waiting > 0:
                self.ser.read(self.ser.in_waiting)
            print("Serial buffers flushed")
        except Exception as e:
            print(f"Error flushing buffers: {e}")

    def send_command(self, command):
        """Send a command to the Arduino.
        
        Args:
            command: Command character to send
        """
        if self.debug:
            print(f"Sending command: '{command}'")
        try:
            self.ser.write(command.encode())
            self.ser.flush()  # Ensure the command is sent immediately
        except Exception as e:
            print(f"Error sending command: {e}")

    def read_response(self):
        """Read text response from Arduino and print it."""
        try:
            while self.ser.in_waiting > 0:
                response = self.ser.readline().decode().strip()
                print(f"Arduino: {response}")
        except Exception as e:
            print(f"Error reading response: {e}")

    def configure_load_cell(self, dout_pin, sck_pin):
        """Configure a new load cell on the Arduino.
        
        Args:
            dout_pin: Data out pin number
            sck_pin: Clock pin number
        """
        print(f"Configuring load cell with DOUT={dout_pin}, SCK={sck_pin}")
        self.send_command(self.COMMAND_NEW_CELL)
        time.sleep(0.5)
        
        # Send DOUT pin with newline terminator
        try:
            cmd = f"{dout_pin}\n"
            if self.debug:
                print(f"Sending DOUT pin: '{cmd.strip()}'")
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(0.5)
            
            # Send SCK pin with newline terminator
            cmd = f"{sck_pin}\n"
            if self.debug:
                print(f"Sending SCK pin: '{cmd.strip()}'")
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(0.5)
            
            self.listen_responses()
            self.data_queues.append(queue.Queue())
            self.faulty_cells.append(False)
            print(f"Load cell configured successfully. Total cells: {len(self.data_queues)}")
        except Exception as e:
            print(f"Error configuring load cell: {e}")

    def listen_responses(self, duration=5):
        """Listen for text responses from the Arduino for a specified duration.
        
        Args:
            duration: Duration in seconds to listen for
        """
        print(f'Listening for {duration} seconds')
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.ser.in_waiting > 0:
                try:
                    response = self.ser.readline().decode().strip()
                    print(f"Arduino: {response}")
                except Exception as e:
                    print(f"Error reading response: {e}")
            time.sleep(0.1)  # Shorter sleep time
        print('Listening complete')

    def zero(self):
        """Zero all load cells."""
        print("Zeroing load cells")
        self.send_command(self.COMMAND_ZERO)
        self.listen_responses()

    def calibrate(self, gui):
        """Calibrate all load cells with user input.
        
        Args:
            gui: GUI object to display prompts and get user input
        """
        for i in range(len(self.data_queues)):
            print(f"Calibrating load cell {i}")
            self.send_command(self.COMMAND_CALIBRATE)
            time.sleep(0.2)  # Shorter sleep time
            self.read_response()
            gui.show_message(f"Load Cell {i}: Place a known mass on the load cell.")
            known_mass = gui.prompt_known_mass()
            if known_mass is not None:
                mass_cmd = f"{known_mass}\n"
                print(f"Sending calibration mass: {mass_cmd.strip()}")
                self.ser.write(mass_cmd.encode())
                self.ser.flush()  # Ensure data is sent immediately
                self.listen_responses()
            else:
                gui.show_message(f"Load Cell {i}: Calibration canceled.")
        
        # After calibration is complete, make sure to flush buffers
        print("Calibration complete, flushing buffers")
        time.sleep(0.5)  # Wait for any remaining messages
        self.flush_buffers()
    
    def toggle_debug(self):
        """Toggle debug mode on the Arduino."""
        print("Toggling debug mode")
        self.send_command(self.COMMAND_DEBUG)
        time.sleep(0.1)
        self.read_response()
    
    def enable_binary_protocol(self):
        """Switch to binary protocol for more efficient communication."""
        print("Switching to binary protocol")
        self.use_binary_protocol = True
        self.send_command(self.COMMAND_BINARY)
        time.sleep(0.1)
        self.read_response()
    
    def enable_text_protocol(self):
        """Switch back to text protocol."""
        print("Switching to text protocol")
        self.use_binary_protocol = False
        self.send_command(self.COMMAND_TEXT)
        time.sleep(0.1)
        self.read_response()

    def process_binary_packet(self, data):
        """Process a binary data packet from the Arduino.
        
        Binary packet format:
        - Header (1 byte): 0xAA
        - Timestamp (4 bytes): milliseconds
        - Number of cells (1 byte): n
        - Cell readings (n*4 bytes): floats
        - Footer (1 byte): 0x55
        
        Args:
            data: Binary data buffer
        
        Returns:
            List of load cell readings or None if packet is invalid
        """
        if len(data) < 7:  # Minimum packet size (header + timestamp + count + footer)
            if self.debug:
                print(f"Packet too small: {len(data)} bytes")
            return None
            
        if data[0] != self.PACKET_HEADER or data[-1] != self.PACKET_FOOTER:
            if self.debug:
                print(f"Invalid packet markers: header={data[0]:02x}, footer={data[-1]:02x}")
            return None
            
        # Extract timestamp (4 bytes)
        timestamp = data[1] | (data[2] << 8) | (data[3] << 16) | (data[4] << 24)
        
        # Calculate latency
        latency = time.time() * 1000 - timestamp
        self.latency_stats.append(latency)
        
        # Number of cells
        cell_count = data[5]
        
        # Expected packet size
        expected_size = 7 + (cell_count * 4)  # header + timestamp + count + cells + footer
        if len(data) != expected_size:
            if self.debug:
                print(f"Unexpected packet size: got {len(data)}, expected {expected_size}")
            return None
            
        # Parse float values
        readings = []
        for i in range(cell_count):
            offset = 6 + (i * 4)
            value_bytes = bytes(data[offset:offset+4])
            value = struct.unpack('f', value_bytes)[0]
            readings.append(value)
            
        return readings

    def stream_readings(self):
        """Stream readings from the Arduino continuously."""
        print(f"Starting streaming with protocol: {'binary' if self.use_binary_protocol else 'text'}")
        
        try:
            # Flush any pending data
            self.flush_buffers()
            
            if self.use_binary_protocol:
                self.send_command(self.COMMAND_STREAM)
                time.sleep(0.1)
                self.read_response()  # Clear any initial responses
                
                # Reset buffer
                self.buffer_pos = 0
                
                print("Entering binary stream mode...")
                while not self.stop_event.is_set():
                    # Read available data
                    if self.ser.in_waiting > 0:
                        bytes_read = self.ser.read(self.ser.in_waiting)
                        if self.debug and len(bytes_read) > 0:
                            print(f"Read {len(bytes_read)} bytes")
                        
                        # Add to buffer
                        for b in bytes_read:
                            self.buffer[self.buffer_pos] = b
                            self.buffer_pos += 1
                            
                            # Look for packet footer to process complete packet
                            if b == self.PACKET_FOOTER and self.buffer_pos > 6:
                                # Search backward for header
                                for i in range(self.buffer_pos - 2, -1, -1):
                                    if self.buffer[i] == self.PACKET_HEADER:
                                        # Process this packet
                                        packet_data = self.buffer[i:self.buffer_pos+1]
                                        readings = self.process_binary_packet(packet_data)
                                        
                                        if readings:
                                            if self.debug:
                                                print(f"Processed readings: {readings}")
                                            for i, value in enumerate(readings):
                                                if i < len(self.data_queues):
                                                    # Check for NaN or Inf values
                                                    if math.isnan(value) or math.isinf(value):
                                                        self.faulty_cells[i] = True
                                                        self.data_queues[i].put(0.0)
                                                    else:
                                                        self.faulty_cells[i] = False
                                                        self.data_queues[i].put(value)
                                        
                                        # Reset buffer position to start fresh
                                        self.buffer_pos = 0
                                        break
                                
                                # If buffer gets too full without finding a valid packet, reset it
                                if self.buffer_pos > 900:
                                    if self.debug:
                                        print("Buffer overflow, resetting")
                                    self.buffer_pos = 0
                    time.sleep(0.001)  # Minimal sleep to prevent CPU hogging
            else:
                # Text protocol (original implementation)
                print("Entering text stream mode...")
                
                # Before starting the stream, send a dummy command to clear any lingering text
                print("Sending dummy command to clear buffers")
                self.send_command(' ')  # Space as a dummy command
                time.sleep(0.1)
                self.flush_buffers()
                
                # Now start streaming
                self.send_command(self.COMMAND_STREAM)
                time.sleep(0.2)  # Give more time for initial response
                
                # Wait for stream to start
                stream_started = False
                start_time = time.time()
                while not stream_started and time.time() - start_time < 2.0:
                    if self.ser.in_waiting > 0:
                        response = self.ser.readline().decode().strip()
                        print(f"Setup response: {response}")
                        if "STREAM_START" in response:
                            stream_started = True
                            print("Stream initialization confirmed")
                
                if not stream_started:
                    print("Warning: Did not receive stream start confirmation")
                
                self.flush_buffers()  # Flush any initial response
                
                print("Stream mode active")
                last_valid_data_time = time.time()
                data_received = False
                
                while not self.stop_event.is_set():
                    if self.ser.in_waiting > 0:
                        try:
                            response = self.ser.readline().decode().strip()
                            if response:
                                # Check for data marker at the beginning
                                if response.startswith("DATA:"):
                                    data = response[5:]  # Skip "DATA:" prefix
                                    if self.debug:
                                        print(f"Load values: {data}")
                                    
                                    try:
                                        load_values = [float(val) for val in data.split(',')]
                                        last_valid_data_time = time.time()
                                        data_received = True
                                        
                                        for i in range(len(load_values)):
                                            if i < len(self.data_queues):
                                                # Check for NaN or Inf values
                                                if math.isnan(load_values[i]) or math.isinf(load_values[i]):
                                                    self.faulty_cells[i] = True
                                                    self.data_queues[i].put(0.0)  # Put a safe value
                                                else:
                                                    self.faulty_cells[i] = False
                                                    self.data_queues[i].put(load_values[i])
                                    except ValueError as e:
                                        if self.debug:
                                            print(f"Error parsing values: {e}")
                                elif response.startswith("DEBUG:"):
                                    # Just print debug messages
                                    print(f"Arduino debug: {response}")
                                else:
                                    print(f"Ignoring non-data response: {response}")
                                
                                # If we haven't received valid data for a while, restart streaming
                                if time.time() - last_valid_data_time > 3.0:
                                    print("No valid data received for 3 seconds, restarting stream")
                                    self.flush_buffers()
                                    self.send_command(self.COMMAND_STOP)
                                    time.sleep(0.2)
                                    self.flush_buffers()
                                    self.send_command(self.COMMAND_STREAM)
                                    time.sleep(0.2)
                                    self.flush_buffers()
                                    last_valid_data_time = time.time()
                        except Exception as e:
                            print(f"Error reading stream: {e}")
                    time.sleep(0.01)  # Slight sleep to allow other threads to run
                
                print(f"Data received during streaming: {data_received}")
            
            print("Exiting stream loop")
            self.send_command(self.COMMAND_STOP)
            time.sleep(0.1)
            self.read_response()
        except Exception as e:
            print(f"Streaming thread error: {e}")

    def start_streaming(self):
        """Start streaming data from the Arduino."""
        if self.stream_thread and self.stream_thread.is_alive():
            print("Already streaming. Stop current stream first.")
            return
            
        print("Starting data streaming")
        
        # Make sure buffers are clear before starting
        self.flush_buffers()
        
        self.stop_event.clear()
        # Reset faulty status when starting new stream
        self.faulty_cells = [False] * len(self.faulty_cells)
        
        # Start with text protocol for compatibility
        self.use_binary_protocol = False
        
        self.stream_thread = threading.Thread(target=self.stream_readings)
        self.stream_thread.daemon = True  # Daemon thread will exit when main program exits
        self.stream_thread.start()
        
        # Reset latency stats
        self.latency_stats.clear()
        print("Streaming started")

    def stop_streaming(self):
        """Stop streaming data from the Arduino."""
        print("Stopping data streaming")
        for queue in self.data_queues:
            queue.queue.clear()
        if self.stream_thread and self.stream_thread.is_alive():
            self.stop_event.set()
            self.stream_thread.join(timeout=1.0)  # Wait for thread to exit with timeout
            print("Streaming thread stopped")
        else:
            print("No active streaming thread")
            
        # Flush buffers after stopping stream
        self.flush_buffers()
            
        # Print latency stats if available
        if self.latency_stats:
            avg_latency = sum(self.latency_stats) / len(self.latency_stats)
            print(f"Average communication latency: {avg_latency:.2f} ms")

    def close(self):
        """Close the serial connection."""
        print("Closing serial connection")
        self.stop_streaming()
        self.ser.close()
        print("Connection closed")