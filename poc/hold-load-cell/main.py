from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui import LoadCellGUI
import time
import threading
import sys
from arduino_protocol import ArduinoProtocol


def main():
    """Main application entry point."""
    app = QApplication([])
    
    # Create Arduino protocol handler
    arduino = ArduinoProtocol('/dev/cu.usbmodem101', 115200)
    
    # Connect to Arduino
    if not arduino.connect():
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
        arduino.configure_cell(cell_id, dout, sck)
        print(f"Configuring load cell {cell_id} with DOUT={dout}, SCK={sck}")
        time.sleep(0.5)  # Give time for configuration to complete
    
    # Wait for all configurations to complete
    arduino.wait_for_idle()
    
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
    
    # Create GUI with per-cell operations
    gui = LoadCellGUI(arduino.MAX_LOAD_CELLS, zero_cell, zero_all_cells, calibrate_cell)
    gui.show()
    
    # Update GUI with latest data periodically
    def update_gui():
        state = arduino.get_state()
        
        # Update each cell's status and reading
        for i in range(arduino.MAX_LOAD_CELLS):
            is_configured = state['cell_configured'][i]
            is_active = (state['active_cell'] == i and state['status'] != arduino.STATUS_IDLE)
            is_faulty = False  # We could add fault detection in the future
            
            reading = state['cell_readings'][i]
            
            # Update the GUI with cell status and reading
            gui.update_cell(i, reading, is_configured, is_active, is_faulty)
        
        # Schedule the next update
        QTimer.singleShot(10, update_gui)  # 10ms = 100Hz update rate
    
    # Start the GUI update loop
    QTimer.singleShot(10, update_gui)
    
    # Run the application
    result = app.exec_()
    
    # Clean up when done
    arduino.disconnect()
    
    sys.exit(result)


if __name__ == "__main__":
    main()