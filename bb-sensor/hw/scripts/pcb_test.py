from skidl import *

# Reuse existing nets for power and ground.
vin_5v = Net("VIN_5V")
gnd = Net("GND")
v3v3 = Net("3V3")

# ----- Existing Parts -----
barrel_jack = Part(
    "Connector",
    "Barrel_Jack",  
    footprint="Connector_BarrelJack:Barrel_Jack",
)
vin_5v += barrel_jack[1]
gnd += barrel_jack[2]

ldo = Part(
    "Regulator_Linear",
    "LD1117S33TR_SOT223",
    footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
)
vin_5v += ldo["VI"]
v3v3 += ldo["VO"]
gnd += ldo["GND"]

c_in = Part("Device", "C", value="10uF", footprint="Capacitor_SMD:C_0805_2012Metric")
c_out = Part("Device", "C", value="10uF", footprint="Capacitor_SMD:C_0805_2012Metric")
vin_5v += c_in[1]
gnd    += c_in[2]
v3v3   += c_out[1]
gnd    += c_out[2]

# ----- 4) HX711 -----
# Define two new nets for communication lines. Later, you'll connect these to an MCU (ESP32, etc.).
hx711_sck  = Net("HX711_SCK")
hx711_dout = Net("HX711_DOUT")

# Let's assume your symbol is "HX711" in the "Sensor" library, with a SOIC-16 footprint:
hx711 = Part(
    "Analog_ADC",
    "HX711",
    footprint="Package_SO:SOP-16_3.9x9.9mm_P1.27mm"
)

# Hook up the HX711 pins to 3.3 V, GND, and net signals.
# Make sure these pin names match exactly what your symbol uses!
v3v3 += hx711["AVDD"], hx711["DVDD"]   # Both analog & digital supply pins = 3.3 V
gnd  += hx711["AVSS"], hx711["DGND"]   # Analog & digital grounds
hx711_sck  += hx711["SCK"]
hx711_dout += hx711["DOUT"]

# Optional: PDWN / RST / RATE pins might need to tie to GND or 3.3 V per datasheet.
# hx711["PDWN"] += gnd
# hx711["RATE"] += gnd  # Or whatever you need.

# Add a small decoupling cap for the HX711 close to the power pins:
c_hx711 = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0805_2012Metric")
v3v3 += c_hx711[1]
gnd  += c_hx711[2]

# Generate files
generate_netlist(tool=KICAD8)
generate_pcb(
    pcb_file="board_step4.kicad_pcb",
    fp_libs=[
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_BarrelJack.pretty',
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_TO_SOT_SMD.pretty',
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_SMD.pretty',
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_SMD.pretty',
        # For the HX711 footprint (if you need it):
        '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_SO.pretty',
    ],
)
