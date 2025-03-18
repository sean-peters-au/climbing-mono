import cadquery as cq

# ----------------------------
# Washer Dimensions
# ----------------------------
height = 3.0  # mm (the thickness of the washer)
id_dia = 5.0  # mm (inner diameter)
od_dia = 9.0  # mm (outer diameter)

# Convert diameter to radius
id_rad = id_dia / 2.0  # 2.5 mm
od_rad = od_dia / 2.0  # 4.5 mm

# ----------------------------
# Build the Washer Geometry
# ----------------------------
washer = (
    cq.Workplane("XY")
    # Create a cylinder of outer diameter
    .circle(od_rad)
    .extrude(height)
    # Cut out the inner diameter
    .faces(">Z").workplane()
    .circle(id_rad)
    .cutBlind(-height)
)

# ----------------------------
# Export to STL
# ----------------------------
washer.val().exportStl("washer.stl", tolerance=0.01)
print("Exported 'washer.stl'.")