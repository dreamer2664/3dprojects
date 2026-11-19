"""Hard points (see DECISIONS.md D-003 and research/TECHNICAL_NOTES.md §2).
Metres; +X forward, +Y rider's left, Z up; origin on the ground under the rear axle."""
import math
from mathutils import Vector

WHEELBASE = 1.435
R_FRONT = 0.292          # Pirelli Diablo Supercorsa 120/70 ZR17 measured OD ~583 mm
R_REAR = 0.315           # 200/55 ZR17 OD ~630 mm
RIM_R = 0.2159           # 17" bead seat radius
FRONT_AXLE = Vector((WHEELBASE, 0.0, R_FRONT))
REAR_AXLE = Vector((0.0, 0.0, R_REAR))

RAKE = math.radians(24.6)
TRAIL = 0.1045
X_GROUND_STEER = WHEELBASE + TRAIL
STEER_DIR = Vector((-math.sin(RAKE), 0.0, math.cos(RAKE)))   # up along steering axis
STEER_FWD = Vector((math.cos(RAKE), 0.0, math.sin(RAKE)))     # perpendicular, forward
FORK_HALF_SPACING = 0.1025
FORK_TOP_DIST = 0.700    # axle -> top of fork tube along axis (cap)
TOP_CLAMP_DIST = 0.668   # axle -> top clamp mid-plane along axis
LOW_CLAMP_DIST = 0.505

def steer_point(z):
    """Point on the steering axis at height z."""
    return Vector((X_GROUND_STEER - z * math.tan(RAKE), 0.0, z))

def fork_point(d, side=1):
    """Point on a fork tube axis at distance d (along axis) from the axle."""
    return FRONT_AXLE + STEER_DIR * d + Vector((0, side * FORK_HALF_SPACING, 0))

SWINGARM_PIVOT = Vector((0.520, 0.0, 0.465))
CRANK = Vector((0.640, 0.0, 0.455))
BANK_FRONT_DEG = 39.0
BANK_REAR_DEG = 104.0
SEAT_Z = 0.842
FOOTPEG = Vector((0.583, 0.170, 0.334))

def bank_dir(front=True):
    a = math.radians(BANK_FRONT_DEG if front else BANK_REAR_DEG)
    return Vector((math.cos(a), 0.0, math.sin(a)))
