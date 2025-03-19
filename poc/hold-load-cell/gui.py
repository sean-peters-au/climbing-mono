from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, 
                            QInputDialog, QMessageBox, QGroupBox, QFrame)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QSize

import numpy as np
import matplotlib.pyplot as plt
import math
import time

class CellStatusWidget(QFrame):
    """Widget to display a single load cell's status and controls."""
    
    def __init__(self, cell_id, zero_callback, calibrate_callback, parent=None):
        super().__init__(parent)
        self.cell_id = cell_id
        self.zero_callback = zero_callback
        self.calibrate_callback = calibrate_callback
        
        # Set frame style
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)
        
        # Status indicators
        self.configured = False
        self.active = False
        self.faulty = False
        self.value = 0.0
        
        # Create layout
        layout = QVBoxLayout()
        
        # Cell title
        self.title_label = QLabel(f"Load Cell {cell_id}")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Status indicators
        status_layout = QHBoxLayout()
        
        self.config_label = QLabel("○ Not Configured")
        self.config_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.config_label)
        
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.status_label)
        
        layout.addLayout(status_layout)
        
        # Reading value
        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.zero_button = QPushButton("Zero")
        self.zero_button.clicked.connect(self.on_zero)
        self.zero_button.setEnabled(False)
        button_layout.addWidget(self.zero_button)
        
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.on_calibrate)
        self.calibrate_button.setEnabled(False)
        button_layout.addWidget(self.calibrate_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_zero(self):
        self.zero_callback(self.cell_id)
    
    def on_calibrate(self):
        mass, ok = QInputDialog.getDouble(self, "Calibration", 
                                          f"Enter known mass for Load Cell {self.cell_id} (in grams):",
                                          value=100.0, min=0.1, max=10000.0)
        if ok:
            self.calibrate_callback(self.cell_id, mass)
    
    def update_status(self, value, configured, active, faulty):
        self.value = value
        self.configured = configured
        self.active = active
        self.faulty = faulty
        
        # Update value display
        if faulty:
            self.value_label.setText("FAULTY")
            self.value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: red;")
        else:
            self.value_label.setText(f"{value:.2f}")
            self.value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Update configuration status
        if configured:
            self.config_label.setText("● Configured")
            self.config_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.config_label.setText("○ Not Configured")
            self.config_label.setStyleSheet("color: gray;")
        
        # Update operational status
        if active:
            self.status_label.setText("Active")
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        elif faulty:
            self.status_label.setText("Faulty")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.status_label.setText("Idle")
            self.status_label.setStyleSheet("color: black;")
        
        # Update button states
        self.zero_button.setEnabled(configured and not active)
        self.calibrate_button.setEnabled(configured and not active)


class LoadCellVisualizer(QWidget):
    """Visual representation of all load cells."""
    
    def __init__(self, num_cells, parent=None):
        super().__init__(parent)
        self.num_cells = num_cells
        self.cell_values = [0.0] * num_cells
        self.cell_configured = [False] * num_cells
        self.cell_active = [False] * num_cells
        self.cell_faulty = [False] * num_cells
        
        self.max_value = 10000
        self.min_value = -10000
        
        self.setMinimumSize(400, 200)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        bar_width = width / (self.num_cells * 2)
        spacing = width / (self.num_cells + 1)
        x_start = spacing - bar_width / 2
        
        # Draw zero line
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1, Qt.DashLine))
        painter.drawLine(0, height//2, width, height//2)
        
        # Draw each cell
        for i in range(self.num_cells):
            x_pos = x_start + i * spacing
            
            # Don't draw unconfigured cells
            if not self.cell_configured[i]:
                continue
            
            # Handle faulty cells
            if self.cell_faulty[i]:
                pen = QPen(QColor(255, 0, 0), bar_width)
                painter.setPen(pen)
                cross_size = 20
                painter.drawLine(x_pos - cross_size, height//2 - cross_size, 
                               x_pos + cross_size, height//2 + cross_size)
                painter.drawLine(x_pos - cross_size, height//2 + cross_size, 
                               x_pos + cross_size, height//2 - cross_size)
                continue
                
            # Draw active indicator
            if self.cell_active[i]:
                # Draw pulsing circle around the bar
                painter.setPen(QPen(QColor(0, 100, 255, 100), 2))
                painter.setBrush(QColor(0, 100, 255, 50))
                pulse_size = 30 + (int(time.time() * 5) % 10)
                painter.drawEllipse(int(x_pos - pulse_size/2), int(height//2 - pulse_size/2), 
                                   pulse_size, pulse_size)
            
            # Calculate bar height based on value
            value = self.cell_values[i]
            if value > 0:
                bar_height = min(int((value / self.max_value) * height / 2), height//2)
                bar_y = height//2 - bar_height
            else:
                bar_height = min(int((abs(value) / abs(self.min_value)) * height / 2), height//2)
                bar_y = height//2
            
            # Normalize and get color
            norm_value = (value - self.min_value) / (self.max_value - self.min_value)
            color = self.get_color(norm_value)
            
            # Draw the bar
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(int(x_pos - bar_width/2), bar_y, int(bar_width), bar_height)
            
            # Draw cell ID
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(int(x_pos - 5), height - 10, str(i))
    
    def get_color(self, value):
        # Use a colormap similar to matplotlib's coolwarm
        if value < 0.5:
            # Blue to white
            intensity = value * 2
            return QColor(int(intensity * 255), int(intensity * 255), 255)
        else:
            # White to red
            intensity = (value - 0.5) * 2
            return QColor(255, int((1 - intensity) * 255), int((1 - intensity) * 255))
    
    def update_cell(self, cell_id, value, configured, active, faulty):
        if 0 <= cell_id < self.num_cells:
            self.cell_values[cell_id] = value
            self.cell_configured[cell_id] = configured
            self.cell_active[cell_id] = active
            self.cell_faulty[cell_id] = faulty
            self.update()


class LoadCellGUI(QMainWindow):
    """Main window for the load cell application."""
    
    def __init__(self, num_cells, zero_cell_callback, zero_all_callback, calibrate_callback):
        super().__init__()
        self.setWindowTitle("Load Cell Monitor")
        self.resize(800, 600)
        
        self.num_cells = num_cells
        self.zero_cell_callback = zero_cell_callback
        self.zero_all_callback = zero_all_callback
        self.calibrate_callback = calibrate_callback
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Visualizer section
        visual_group = QGroupBox("Load Cell Visualization")
        visual_layout = QVBoxLayout()
        
        self.visualizer = LoadCellVisualizer(num_cells)
        visual_layout.addWidget(self.visualizer)
        
        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)
        
        # Individual cell controls
        cells_group = QGroupBox("Individual Cell Controls")
        cells_layout = QGridLayout()
        
        self.cell_widgets = []
        for i in range(num_cells):
            cell_widget = CellStatusWidget(
                i, 
                self.zero_cell_callback,
                self.calibrate_callback
            )
            self.cell_widgets.append(cell_widget)
            
            row = i // 2
            col = i % 2
            cells_layout.addWidget(cell_widget, row, col)
        
        cells_group.setLayout(cells_layout)
        main_layout.addWidget(cells_group)
        
        # Global controls
        control_layout = QHBoxLayout()
        
        self.zero_all_button = QPushButton("Zero All Cells")
        self.zero_all_button.clicked.connect(self.zero_all_callback)
        control_layout.addWidget(self.zero_all_button)
        
        main_layout.addLayout(control_layout)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def update_cell(self, cell_id, value, configured, active, faulty):
        """Update the status and reading for a specific cell."""
        if 0 <= cell_id < self.num_cells:
            # Update the cell's widget
            self.cell_widgets[cell_id].update_status(value, configured, active, faulty)
            
            # Update the visualizer
            self.visualizer.update_cell(cell_id, value, configured, active, faulty)
    
    def show_message(self, title, message):
        """Show a message dialog."""
        QMessageBox.information(self, title, message)


if __name__ == "__main__":
    import sys
    import time
    
    app = QApplication(sys.argv)
    
    def zero_callback(cell_id):
        print(f"Zero cell {cell_id}")
    
    def zero_all_callback():
        print("Zero all cells")
    
    def calibrate_callback(cell_id, mass):
        print(f"Calibrate cell {cell_id} with mass {mass}g")
    
    gui = LoadCellGUI(4, zero_callback, zero_all_callback, calibrate_callback)
    gui.show()
    
    # For testing, update cells with simulated values
    def update_test():
        for i in range(4):
            value = math.sin(time.time() + i) * 5000
            configured = i < 3  # First 3 cells configured
            active = i == int(time.time()) % 4  # Activate cells in sequence
            faulty = i == 3  # Last cell is faulty
            gui.update_cell(i, value, configured, active, faulty)
        
        QTimer.singleShot(100, update_test)
    
    QTimer.singleShot(100, update_test)
    
    sys.exit(app.exec_())