"""Details: brake/clutch hoses (braided), plate holder with light + indicators,
wiring looms, rear reflector."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "95_DETAILS"

def build(ctx):
    c = coll(COLL)
    # ---- front brake hose: right master cyl -> splitter -> both Hypure calipers
    tube("Hose_brake_F", [(1.155, -0.185, 0.955), (1.22, -0.16, 0.80), (1.275, -0.115, 0.62), (1.315, -0.085, 0.50)],
         0.0055, mat='braided', res=6, c=c)
    box("Brake_splitter", (0.02, 0.03, 0.03), (1.315, -0.085, 0.49), mat='alu_black_anod', bev=0.004, c=c)
    for side, yy in ((1, 0.115), (-1, -0.10)):
        tube(f"Hose_brake_F_{side}", [(1.315, -0.085, 0.50), (1.33, yy * 0.8, 0.46), (1.375, yy, 0.475)],
             0.005, mat='braided', res=6, c=c)
    # ---- rear brake hose: rear master -> along swingarm right -> rear caliper
    tube("Hose_brake_R", [(0.475, -0.15, 0.415), (0.40, -0.10, 0.42), (0.25, -0.095, 0.42), (0.10, -0.10, 0.44)],
         0.0045, mat='braided', res=6, c=c)
    # ---- wiring looms
    tube("Loom_main", [(1.10, 0.05, 0.88), (0.95, 0.08, 0.78), (0.75, 0.10, 0.70)], 0.008, mat='hose_rubber', c=c)
    tube("Loom_front", [(1.12, -0.03, 0.90), (1.18, -0.06, 0.80), (1.16, -0.08, 0.68)], 0.006, mat='hose_rubber', c=c)
    # ---- plate holder: arm, plate, light, indicators, reflector
    rod("Plate_arm", (-0.06, 0, 0.815), (-0.235, 0, 0.645), 0.014, 'plastic_black', n=10, c=c)
    box("Plate_bracket", (0.05, 0.115, 0.02), (-0.145, 0, 0.735), rot=(0, 33, 0), mat='plastic_black', bev=0.004, c=c)
    box("Plate", (0.014, 0.175, 0.175), (-0.252, 0, 0.615), rot=(0, 33, 0), mat='ground_white', bev=0.004, c=c)
    box("Plate_light", (0.03, 0.05, 0.015), (-0.205, 0, 0.70), rot=(0, 33, 0), mat='led_white', bev=0.003, c=c)
    box("Tail_light", (0.035, 0.085, 0.018), (-0.155, 0, 0.935), rot=(0, 12, 0), mat='led_red', bev=0.004, c=c)
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        rod(f"Indicator_stalk_{s}", (-0.115, side * 0.055, 0.895), (-0.12, side * 0.135, 0.885), 0.006,
            'plastic_black', n=8, c=c)
        box(f"Indicator_{s}", (0.045, 0.022, 0.018), (-0.12, side * 0.145, 0.885), rot=(0, 10, 0),
            mat='reflector_amber', bev=0.006, c=c)
    box("Rear_reflector", (0.02, 0.045, 0.015), (-0.20, 0, 0.665), rot=(0, 33, 0), mat='led_red', bev=0.004, c=c)
    return {}
