#!/usr/bin/env python3
"""
SKiDL script for a Wi-Fi load-sensor PCB with:
  - ESP32 (inline-defined)
  - 4x HX711 amplifiers (inline-defined)
  - 4 SEN-10245 half-bridge load cells, w/ bridging resistors from "Device" library
  - A barrel jack for 5 V input (inline)
  - A 3.3 V linear regulator (inline)
  - Passives (R, C) from standard "Device" library
  - A 3-pin connector from "Connector" library if available

All pin 'func' assignments are omitted so it doesn't conflict with older SKiDL versions.
"""

from skidl import SKIDL, Pin, Part, Net, generate_netlist

NUM_SENSORS = 4
SENSOR_BRIDGE_RES_VAL = "1k"

#
# Footprint references (edit to match your KiCad library footprints)
#
ESP32_FOOTPRINT       = "Module:ESP32-WROOM-32"
HX711_FOOTPRINT       = "Package_SOIC:SOIC-16_3.9x9.9mm_P1.27mm"
REGULATOR_FOOTPRINT   = "Package_TO_SOT_SMD:SOT-223"
BARREL_JACK_FOOTPRINT = "Connector:Barrel_Jack"
CONNECT_3P_FOOTPRINT  = "Connector:Conn_01x03"
RES_0603              = "Resistor_SMD:R_0603"
CAP_0603              = "Capacitor_SMD:C_0603"

#
# Define nets
#
net_5v  = Net("5V")
net_3v3 = Net("3V3")
net_gnd = Net("GND")

#
# Barrel Jack (inline part)
#
barrel_jack = Part(
    tool=SKIDL,
    name="BarrelJack",
    ref="J1",
    footprint=BARREL_JACK_FOOTPRINT,
    pins=[
        Pin(num="1", name="VIN"),
        Pin(num="2", name="GND"),
    ]
)
net_5v  += barrel_jack["VIN"]
net_gnd += barrel_jack["GND"]

#
# 3.3 V Regulator (inline)
#
reg_3v3 = Part(
    tool=SKIDL,
    name="REG_3V3",
    ref="U1",
    footprint=REGULATOR_FOOTPRINT,
    pins=[
        Pin(num="1", name="VIN"),
        Pin(num="2", name="VOUT"),
        Pin(num="3", name="GND"),
    ]
)
net_5v  += reg_3v3["VIN"]
net_3v3 += reg_3v3["VOUT"]
net_gnd += reg_3v3["GND"]

#
# Decoupling caps from Device library
#
c_in = Part("Device", "C", ref="C1", value="10uF", footprint=CAP_0603)
c_out = Part("Device", "C", ref="C2", value="10uF", footprint=CAP_0603)

net_5v  += c_in[1]
net_gnd += c_in[2]
net_3v3 += c_out[1]
net_gnd += c_out[2]

#
# ESP32 Module (inline)
#
esp32 = Part(
    tool=SKIDL,
    name="ESP32_WROOM",
    ref="U2",
    footprint=ESP32_FOOTPRINT,
    pins=[
        Pin(num="1",  name="3V3"),
        Pin(num="2",  name="GND"),
        Pin(num="3",  name="EN"),
        Pin(num="6",  name="GPIO12"),
        Pin(num="7",  name="GPIO13"),
        Pin(num="8",  name="GPIO14"),
        Pin(num="9",  name="GPIO15"),
        Pin(num="10", name="GPIO16"),
        Pin(num="11", name="GPIO17"),
        Pin(num="12", name="GPIO18"),
        Pin(num="13", name="GPIO19"),
    ]
)
net_3v3 += esp32["3V3"]
net_gnd += esp32["GND"]

# Additional bypass near ESP32
for c_idx in range(3, 6):
    cdec = Part("Device", "C", ref=f"C{c_idx}", value="0.1uF", footprint=CAP_0603)
    net_3v3 += cdec[1]
    net_gnd += cdec[2]

#
# HX711 Amplifiers (inline)
#
hx711_list = []
for i in range(NUM_SENSORS):
    amp = Part(
        tool=SKIDL,
        name="HX711",
        ref=f"U{i+3}",
        footprint=HX711_FOOTPRINT,
        pins=[
            Pin(num="1",  name="VDD"),
            Pin(num="2",  name="VFB"),
            Pin(num="3",  name="BASE"),
            Pin(num="4",  name="VBG"),
            Pin(num="5",  name="AVDD"),
            Pin(num="6",  name="AGND"),
            Pin(num="7",  name="BP"),
            Pin(num="8",  name="BM"),
            Pin(num="9",  name="Rate"),
            Pin(num="10", name="VLC"),
            Pin(num="11", name="DGND"),
            Pin(num="12", name="DOUT"),
            Pin(num="13", name="PD_SCK"),
            Pin(num="14", name="DVDD"),
            Pin(num="15", name="AVCAP"),
            Pin(num="16", name="VCC"),
        ]
    )
    hx711_list.append(amp)

    # Tie power
    net_3v3 += amp["VDD"], amp["DVDD"], amp["VCC"], amp["AVDD"]
    net_gnd += amp["DGND"], amp["AGND"]

    # Bypass
    c_amp = Part("Device", "C", ref=f"CAMP{i+1}", value="0.1uF", footprint=CAP_0603)
    net_3v3 += c_amp[1]
    net_gnd += c_amp[2]

    # Data lines
    sck_net  = Net(f"HX{i+1}_SCK")
    dout_net = Net(f"HX{i+1}_DOUT")
    sck_net  += amp["PD_SCK"]
    dout_net += amp["DOUT"]

    # Assign them to ESP32 pins
    sck_net  += esp32[f"GPIO{12 + i}"]
    dout_net += esp32[f"GPIO{16 + i}"]

#
# 3-pin connectors + bridging resistors for half-bridge sensors
#
for i in range(NUM_SENSORS):
    conn = Part(
        "Connector", "Conn_01x03_Pin",
        ref=f"J{i+2}",
        footprint=CONNECT_3P_FOOTPRINT
    )

    r_up = Part("Device", "R", ref=f"R{i+1}A", value=SENSOR_BRIDGE_RES_VAL, footprint=RES_0603)
    r_dn = Part("Device", "R", ref=f"R{i+1}B", value=SENSOR_BRIDGE_RES_VAL, footprint=RES_0603)

    mid_net   = Net(f"SENS{i+1}_MID")
    eplus_net = Net(f"SENS{i+1}_EPLUS")
    eminus_net= Net(f"SENS{i+1}_EMINUS")
    sig_net   = Net(f"SENS{i+1}_SIG")

    eplus_net   += conn[1]
    eminus_net  += conn[2]
    sig_net     += conn[3]

    # bridging
    eplus_net += r_up[1]
    mid_net   += r_up[2]
    eminus_net += r_dn[1]
    mid_net    += r_dn[2]

    hx = hx711_list[i]
    hx["BP"] += sig_net
    hx["BM"] += mid_net

    # E+ = 3.3V, E- = GND
    net_3v3 += eplus_net
    net_gnd += eminus_net

#
# Generate netlist
#
if __name__ == "__main__":
    generate_netlist("climbing_hold_sensors.net")