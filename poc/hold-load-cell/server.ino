#include <HX711_ADC.h>
#include <EEPROM.h>

// System parameters
#define MAX_LOAD_CELLS 4

// Status codes
#define STATUS_IDLE 0
#define STATUS_ZEROING 1
#define STATUS_CALIBRATING 2
#define STATUS_STREAMING 3
#define STATUS_ERROR 255

// Error codes
#define ERR_NONE 0
#define ERR_INVALID_COMMAND 1
#define ERR_INVALID_CELL_ID 2
#define ERR_CELL_NOT_CONFIGURED 3
#define ERR_CALIBRATION_FAILED 4

// Command flags (bit positions in the command byte)
#define CMD_CONFIGURE_MASK 0b00000001
#define CMD_ZERO_MASK      0b00000010
#define CMD_CALIBRATE_MASK 0b00000100
#define CMD_RESET_MASK     0b00001000

// Communication protocol structs (must match Python side)
struct CommandStruct {
  // Command flags (bitfield)
  uint8_t command_flags;
  
  // Target cell ID (255 = all cells)
  uint8_t cell_id;
  
  // Configuration parameters
  uint8_t dout_pin;
  uint8_t sck_pin;
  
  // Calibration mass
  float calibration_mass;
  
  // Reserved for future use
  uint8_t reserved[4];
};

struct ResponseStruct {
  // Global status
  uint8_t status;
  
  // Error code
  uint8_t error;
  
  // Currently active cell (255 = none)
  uint8_t active_cell;
  
  // Cell configuration status
  uint8_t cell_configured[MAX_LOAD_CELLS];
  
  // Cell readings
  float cell_readings[MAX_LOAD_CELLS];
  
  // Cell calibration factors
  float calibration_factors[MAX_LOAD_CELLS];
};

// Global variables
HX711_ADC* loadCells[MAX_LOAD_CELLS];
bool cellConfigured[MAX_LOAD_CELLS] = {false};
int doutPins[MAX_LOAD_CELLS];
int sckPins[MAX_LOAD_CELLS];
float calibrationFactors[MAX_LOAD_CELLS] = {0};

// Current system state
uint8_t currentStatus = STATUS_IDLE;
uint8_t lastError = ERR_NONE;
uint8_t activeCell = 255; // 255 = no active cell

// Response data
ResponseStruct responseData;

void setup() {
  Serial.begin(115200);
  delay(100);
  
  // Initialize all load cell pointers to NULL
  for (int i = 0; i < MAX_LOAD_CELLS; i++) {
    loadCells[i] = NULL;
    responseData.cell_configured[i] = 0;
    responseData.cell_readings[i] = 0;
    responseData.calibration_factors[i] = 0;
  }
  
  // Initialize response struct
  responseData.status = STATUS_IDLE;
  responseData.error = ERR_NONE;
  responseData.active_cell = 255;
}

void loop() {
  // Check if a command packet is available
  if (Serial.available() >= sizeof(CommandStruct)) {
    // Read the command packet
    CommandStruct commandData;
    Serial.readBytes((uint8_t*)&commandData, sizeof(CommandStruct));
    
    // Process the command
    processCommand(commandData);
    
    // Update all readings before sending response
    updateAllReadings();
    
    // Send the response
    sendResponse();
  }
  
  // Always update the active load cell (if any)
  if (activeCell < MAX_LOAD_CELLS && loadCells[activeCell] != NULL) {
    loadCells[activeCell]->update();
  }
}

// Process a command struct
void processCommand(CommandStruct& cmd) {
  // Reset error
  lastError = ERR_NONE;
  responseData.error = ERR_NONE;
  
  // Process configuration command
  if (cmd.command_flags & CMD_CONFIGURE_MASK) {
    if (cmd.cell_id < MAX_LOAD_CELLS) {
      configureCell(cmd.cell_id, cmd.dout_pin, cmd.sck_pin);
    } else {
      lastError = ERR_INVALID_CELL_ID;
    }
  }
  
  // Process zero command
  if (cmd.command_flags & CMD_ZERO_MASK) {
    if (cmd.cell_id == 255) {
      // Zero all cells
      zeroAllCells();
    } else if (cmd.cell_id < MAX_LOAD_CELLS) {
      // Zero specific cell
      zeroCell(cmd.cell_id);
    } else {
      lastError = ERR_INVALID_CELL_ID;
    }
  }
  
  // Process calibration command
  if (cmd.command_flags & CMD_CALIBRATE_MASK) {
    if (cmd.cell_id < MAX_LOAD_CELLS) {
      calibrateCell(cmd.cell_id, cmd.calibration_mass);
    } else {
      lastError = ERR_INVALID_CELL_ID;
    }
  }
  
  // Process reset command
  if (cmd.command_flags & CMD_RESET_MASK) {
    resetSystem();
  }
  
  // Update error code in response
  responseData.error = lastError;
}

// Configure a load cell
void configureCell(uint8_t cellId, uint8_t doutPin, uint8_t sckPin) {
  currentStatus = STATUS_IDLE;
  activeCell = cellId;
  
  // If cell was previously configured, delete old instance
  if (loadCells[cellId] != NULL) {
    delete loadCells[cellId];
    loadCells[cellId] = NULL;
    cellConfigured[cellId] = false;
    responseData.cell_configured[cellId] = 0;
  }
  
  // Store pin configuration
  doutPins[cellId] = doutPin;
  sckPins[cellId] = sckPin;
  
  // Create and initialize load cell
  loadCells[cellId] = new HX711_ADC(doutPin, sckPin);
  
  if (loadCells[cellId] == NULL) {
    lastError = ERR_CELL_NOT_CONFIGURED;
    return;
  }
  
  // Initialize the HX711
  loadCells[cellId]->begin();
  loadCells[cellId]->start(2000, true);
  loadCells[cellId]->setReverseOutput();
  
  // Mark as configured
  cellConfigured[cellId] = true;
  responseData.cell_configured[cellId] = 1;
  
  // Update response data
  responseData.status = currentStatus;
  responseData.active_cell = activeCell;
  responseData.calibration_factors[cellId] = calibrationFactors[cellId];
}

// Zero a specific load cell
void zeroCell(uint8_t cellId) {
  if (!cellConfigured[cellId] || loadCells[cellId] == NULL) {
    lastError = ERR_CELL_NOT_CONFIGURED;
    return;
  }
  
  // Set status
  currentStatus = STATUS_ZEROING;
  activeCell = cellId;
  
  // Update response data
  responseData.status = currentStatus;
  responseData.active_cell = activeCell;
  
  // Zero the load cell
  loadCells[cellId]->tare();
  
  // Reset status
  currentStatus = STATUS_IDLE;
  
  // Update response data
  responseData.status = currentStatus;
}

// Zero all configured load cells
void zeroAllCells() {
  // Set status
  currentStatus = STATUS_ZEROING;
  
  // Update response data
  responseData.status = currentStatus;
  
  // Zero all configured cells
  for (uint8_t i = 0; i < MAX_LOAD_CELLS; i++) {
    if (cellConfigured[i] && loadCells[i] != NULL) {
      activeCell = i;
      responseData.active_cell = activeCell;
      loadCells[i]->tare();
    }
  }
  
  // Reset status
  currentStatus = STATUS_IDLE;
  activeCell = 255;
  
  // Update response data
  responseData.status = currentStatus;
  responseData.active_cell = activeCell;
}

// Calibrate a specific load cell with known mass
void calibrateCell(uint8_t cellId, float knownMass) {
  if (!cellConfigured[cellId] || loadCells[cellId] == NULL) {
    lastError = ERR_CELL_NOT_CONFIGURED;
    return;
  }
  
  // Set status
  currentStatus = STATUS_CALIBRATING;
  activeCell = cellId;
  
  // Update response data
  responseData.status = currentStatus;
  responseData.active_cell = activeCell;
  
  // Refresh dataset
  loadCells[cellId]->refreshDataSet();
  
  // Get calibration value
  float newCalibrationValue = loadCells[cellId]->getNewCalibration(knownMass);
  
  // Store calibration factor
  calibrationFactors[cellId] = newCalibrationValue;
  responseData.calibration_factors[cellId] = newCalibrationValue;
  
  // Reset status
  currentStatus = STATUS_IDLE;
  
  // Update response data
  responseData.status = currentStatus;
}

// Reset the system
void resetSystem() {
  // Stop all load cells
  for (uint8_t i = 0; i < MAX_LOAD_CELLS; i++) {
    if (loadCells[i] != NULL) {
      delete loadCells[i];
      loadCells[i] = NULL;
      cellConfigured[i] = false;
      responseData.cell_configured[i] = 0;
      responseData.cell_readings[i] = 0;
      responseData.calibration_factors[i] = 0;
    }
  }
  
  // Reset status
  currentStatus = STATUS_IDLE;
  lastError = ERR_NONE;
  activeCell = 255;
  
  // Update response data
  responseData.status = currentStatus;
  responseData.error = lastError;
  responseData.active_cell = activeCell;
}

// Update all load cell readings
void updateAllReadings() {
  for (uint8_t i = 0; i < MAX_LOAD_CELLS; i++) {
    if (cellConfigured[i] && loadCells[i] != NULL) {
      // Only update if not currently busy with the active cell
      if (i != activeCell || currentStatus == STATUS_IDLE) {
        loadCells[i]->update();
      }
      
      // Get value
      float value = loadCells[i]->getData();
      
      // Update response data
      responseData.cell_readings[i] = value;
    } else {
      responseData.cell_readings[i] = 0;
    }
  }
}

// Send response struct to master
void sendResponse() {
  // Update the status and active cell
  responseData.status = currentStatus;
  responseData.active_cell = activeCell;
  
  // Send the entire struct
  Serial.write((uint8_t*)&responseData, sizeof(ResponseStruct));
  Serial.flush();
}