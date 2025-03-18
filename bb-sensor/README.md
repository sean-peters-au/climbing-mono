# BetaBoard Sensor

- Load Cell Housing STL(`sensor_housing.py`)
- Sensor PCB (`sensor_pcb_footprint.py`)

## Environment Setup

### 1. Install Miniforge (conda for Apple Silicon)

```bash
    brew install miniforge
```

### 2. Create and activate environment

```bash
    # Create environment
    conda create -n bb-sensor python=3.10

    # Activate environment
    conda activate bb-sensor
```

### 3. Install dependencies

```bash
    # Install CAD and PCB design tools
    conda install --file conda-requirements.txt
    pip install -r requirements.txt

    # Install KiCad
    brew install --cask kicad

    # Configure KiCad environment (run after activating conda environment)
    conda env config vars set KICAD_SYMBOL_DIR="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
    conda env config vars set KICAD8_SYMBOL_DIR="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"

    # Reactivate environment for changes to take effect
    conda deactivate
    conda activate bb-sensor
```

## Usage

### Generate 3D Housing

```bash
    python scripts/sensor_housing.py
```

This will create `housing_unit.stl` in the current directory.

### Generate PCB Netlist

```bash
    python scripts/sensor_pcb_footprint.py
```

This will create `climbing_hold_sensors.net` which can be imported into KiCad for schematic and PCB layout.
```

/Applications/Kicad/Kicad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 scripts/pcb_test.py