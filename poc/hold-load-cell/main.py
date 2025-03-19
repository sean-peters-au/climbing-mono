"""Main application for the load cell monitoring system."""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from client import ArduinoClient
from gui import LoadCellGUI


def main():
    """Main application entry point."""
    app = QApplication([])
    
    # Create Arduino client
    arduino = ArduinoClient('/dev/cu.usbmodem101', 115200)
    
    # Setup state change callback
    def on_state_changed(old_state, new_state):
        pass
        # print(f"State changed: status={new_state['status']}, active_cell={new_state['active_cell']}")
    
    # Setup error callback
    def on_error(error_message):
        print(f"Error: {error_message}")
    
    # Setup health change callback
    def on_health_changed(health):
        print(f"Connection health: connected={health['is_connected']}, healthy={health['is_healthy']}, "
              f"success_rate={health['success_rate']:.2f}, latency={health['avg_latency']:.1f}ms")
    
    # Register callbacks
    arduino.on_state_changed = on_state_changed
    arduino.on_error = on_error
    arduino.on_health_changed = on_health_changed
    
    # Start the client
    if not arduino.start():
        print("Failed to connect to Arduino. Please check the connection and try again.")
        sys.exit(1)
    
    # Configuration for load cells
    cell_configs = [
        (0, 2, 3),  # Cell 0: DOUT=2, SCK=3
        (1, 4, 5),  # Cell 1: DOUT=4, SCK=5
        (2, 6, 7),  # Cell 2: DOUT=6, SCK=7
        (3, 8, 9)   # Cell 3: DOUT=8, SCK=9
    ]
    
    # Configure all load cells
    for cell_id, dout, sck in cell_configs:
        print(f"Configuring load cell {cell_id} with DOUT={dout}, SCK={sck}")
        arduino.configure_cell(cell_id, dout, sck)
    
    # Wait for all configurations to complete
    if not arduino.wait_for_idle(timeout=10.0):
        print("Warning: Timed out waiting for Arduino to become idle")
    
    # Setup callbacks for GUI
    def zero_cell(cell_id):
        print(f"Zeroing load cell {cell_id}")
        arduino.zero_cell(cell_id)
    
    def zero_all_cells():
        print("Zeroing all load cells")
        arduino.zero_all_cells()
    
    def calibrate_cell(cell_id, known_mass):
        print(f"Calibrating load cell {cell_id} with mass {known_mass}g")
        arduino.calibrate_cell(cell_id, known_mass)
    
    # Create GUI
    gui = LoadCellGUI(4, zero_cell, zero_all_cells, calibrate_cell)
    
    # Add connection health status to window title
    def update_window_title():
        health = arduino.get_connection_health()
        status = "Connected" if health['is_connected'] else "Disconnected"
        health_status = "Healthy" if health['is_healthy'] else "Unhealthy"
        success_rate = health['success_rate'] * 100
        latency = health['avg_latency']
        
        title = f"Load Cell Monitor - {status}, {health_status}, Success: {success_rate:.1f}%, Latency: {latency:.1f}ms"
        gui.setWindowTitle(title)
    
    # Update GUI with latest data periodically
    def update_gui():
        # Get current state
        state = arduino.get_state()
        
        # Update window title with connection health
        update_window_title()
        
        # Update each cell's status and reading
        for i in range(4):
            is_configured = state['cell_configured'][i]
            is_active = (state['active_cell'] == i and state['status'] != 0)  # Not IDLE
            is_faulty = False  # We could add fault detection in the future
            
            reading = state['cell_readings'][i]
            
            # Update the GUI with cell status and reading
            gui.update_cell(i, reading, is_configured, is_active, is_faulty)
        
        # Schedule the next update
        QTimer.singleShot(10, update_gui)  # 10ms = 100Hz update rate
    
    # Show the GUI
    gui.show()
    
    # Start the GUI update loop
    QTimer.singleShot(10, update_gui)
    
    # Run the application
    result = app.exec_()
    
    # Clean up
    arduino.stop()
    
    sys.exit(result)


if __name__ == "__main__":
    main()