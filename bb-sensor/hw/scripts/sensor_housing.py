import cadquery as cq

#
# ======= PARAMETERS =======
#
# Overall housing
HOUSING_WIDTH  = 40.0   # total X dimension
HOUSING_HEIGHT = 40.0   # total Y dimension
HOUSING_THICK  = 7.0    # total Z thickness

# Sensor region (square)
SENSOR_SIZE    = 34.0   # 34×34 sensor footprint
SENSOR_DEPTH   = 1.0    # inset depth from the top for the sensor

# Mounting holes
MOUNT_HOLE_DIA  = 3.1
CENTER_HOLE_DIA = 8.0
MOUNT_SPACING   = 28.0  # distance between mounting holes, center to center

# U-cut geometry
CORNER_NO_CUT   = 8.0  # 10 mm of top corner remains uncut (forming a triangle)
U_CUT_DEPTH     = 1.0   # how deep the U region is cut from the pocket floor
U_CUT_WIDTH     = 26.0  # width of the U-cutout
U_CUT_HALF_WIDTH = U_CUT_WIDTH / 2.0
U_CUT_HEIGHT_BELOW = 10
U_CUT_HEIGHT_ABOVE = U_CUT_HALF_WIDTH
#
# ======= DERIVED CONSTANTS =======
#
TOP_Z          = HOUSING_THICK / 2.0         # Z-coordinate of top face
POCKET_FLOOR_Z = TOP_Z - SENSOR_DEPTH        # Z of sensor pocket floor
BOTTOM_Z       = -HOUSING_THICK / 2.0        # Z of bottom face

SENSOR_HALF    = SENSOR_SIZE / 2.0           # e.g. 17 if 34
NO_CUT_SHIFT   = SENSOR_HALF - CORNER_NO_CUT # e.g. 17 - 10 = 7

#
# ======= CREATE HOUSING BLOCK (centered at origin) =======
#
housing = (
    cq.Workplane("XY")
    .box(HOUSING_WIDTH, HOUSING_HEIGHT, HOUSING_THICK)
)

#
# ======= DRILL MOUNTING & CENTER HOLES =======
# All from the top face
#
top_wp = housing.workplane(offset=TOP_Z)

# 4 mounting holes at ±(MOUNT_SPACING/2)
offset = MOUNT_SPACING / 2.0  # 14 if 28
hole_positions = [
    ( offset,  offset),
    ( offset, -offset),
    (-offset,  offset),
    (-offset, -offset),
]
housing = top_wp.pushPoints(hole_positions).hole(MOUNT_HOLE_DIA)

# Center hole
housing = housing.workplane(offset=TOP_Z).hole(CENTER_HOLE_DIA)

#
# ======= SENSOR POCKET (34×34, 1 mm deep) =======
# We'll center it in X and Y
#
housing = (
    housing
    .workplane(offset=TOP_Z)
    .rect(SENSOR_SIZE, SENSOR_SIZE)
    .cutBlind(-SENSOR_DEPTH)
)

# Now the pocket floor is at POCKET_FLOOR_Z.

#
# ======= U-CUT BENEATH THE SENSOR POCKET =======
# Polygon: entire 34×34 minus two top 10×10 triangular corners.
#
# In local coordinates (with the sensor pocket centered at (0,0)):
#  - The full rectangle would be from (-17,-17) to (+17,+17).
#  - We skip the top-left corner from (-17,17) to (-17,7) & (-7,17).
#  - We skip the top-right corner from (17,17) to (17,7) & (7,17).
#
cut_polygon = [
    # Start bottom-left
    (-U_CUT_HALF_WIDTH, -U_CUT_HEIGHT_BELOW),
    # Go bottom-right
    ( U_CUT_HALF_WIDTH, -U_CUT_HEIGHT_BELOW),
    # Move up right interior corner
    ( U_CUT_HALF_WIDTH,  NO_CUT_SHIFT),
    # Diagonal to skip top-right corner
    ( NO_CUT_SHIFT,  U_CUT_HEIGHT_ABOVE),
    # Straight line to top-left
    (-NO_CUT_SHIFT,  U_CUT_HEIGHT_ABOVE),
    # Diagonal to skip top-left corner
    (-U_CUT_HALF_WIDTH,  NO_CUT_SHIFT),
    # Move down left exterior corner
    (-U_CUT_HALF_WIDTH, -U_CUT_HALF_WIDTH),
    # Close the polygon
]

# Workplane at the pocket floor
pocket_floor_wp = housing.workplane(offset=TOP_Z)

# Cut polygon downward by U_CUT_DEPTH
housing = (
    pocket_floor_wp
    .polyline(cut_polygon)
    .close()
    .cutBlind(-U_CUT_DEPTH)
)

#
# ======= EXPORT =======
#
cq.exporters.export(housing, "housing_unit.stl")