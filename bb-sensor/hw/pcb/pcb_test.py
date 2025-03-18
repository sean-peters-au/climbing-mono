from skidl import *

# Nets
vin_5v = Net("VIN_5V")
gnd = Net("GND")
v3v3 = Net("3V3")

# 1) Barrel jack symbol & footprint
barrel_jack = Part(
    "Connector",
    "Barrel_Jack",  
    footprint="Connector_BarrelJack:BarrelJack_Horizontal",
)

# Pin connections (assuming barrel jack pin 1 = +5 V, pin 2 = GND)
vin_5v += barrel_jack[1]
gnd += barrel_jack[2]

# 2) LDO symbol: pick an LDO from Regulator_Linear
# Example: "LD1117S33" is a common 3.3 V linear regulator
ldo = Part(
    "Regulator_Linear",      # Library
    "LD1117S33TR_SOT223",             # Symbol name (check in KiCad)
    footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"  # Adjust if your symbol expects another pin arrangement
)

# Connect pins:
# - input pin of LDO = VIN_5V
# - output pin of LDO = 3V3
# - ground pin of LDO = GND
vin_5v += ldo["VI"]
v3v3 += ldo["VO"]
gnd += ldo["GND"]

# 3) Decoupling caps
c_in = Part("Device", "C", value="10uF", footprint="Capacitor_SMD:C_0805_2012Metric")
c_out = Part("Device", "C", value="10uF", footprint="Capacitor_SMD:C_0805_2012Metric")

# Connect them:
vin_5v += c_in[1]
gnd    += c_in[2]

v3v3   += c_out[1]
gnd    += c_out[2]

# Generate files
generate_netlist(tool=KICAD8)
generate_pcb(
    pcb_file="board_step3.kicad_pcb",
    fp_libs=[
        # Add your existing libraries for barrel jack & resistors ...
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_BarrelJack.pretty',
        # Add the library for the SOT-223 package:
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_TO_SOT_SMD.pretty',
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_SMD.pretty',
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_SMD.pretty',
        # ... add any others as needed
    ],
)
