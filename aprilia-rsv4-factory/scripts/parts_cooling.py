"""Cooling: curved radiator + twin extraction fans, oil cooler, hoses, overflow."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "70_COOLING"

def build(ctx):
    c = coll(COLL)
    # radiator: 3 vertical slats approximating the curve, tilted ~25°
    cx, cz, tilt = 1.200, 0.462, math.radians(25)
    dx, dz = math.sin(tilt), math.cos(tilt)
    H = 0.145   # half height
    for i in range(9):
        t = i / 8 - 0.5                      # -0.5..0.5 across width
        y = t * 0.30
        bow = 0.018 * (1 - (2 * t) ** 2)     # curved: centre further forward
        p0 = Vector((cx - bow - H * dx, y, cz - H * dz))
        p1 = Vector((cx - bow + H * dx, y, cz + H * dz))
        rod(f"Rad_core_{i}", p0, p1, 0.0165, 'radiator_core', n=4, c=c)
    # end tanks
    for y in (-0.163, 0.163):
        rod(f"Rad_tank_{y:+.2f}", (cx - H * dx, y, cz - H * dz), (cx + H * dx, y, cz + H * dz),
            0.021, 'plastic_black', n=12, c=c)
    # top/bottom rails
    rod("Rad_rail_top", (cx + H * dx, -0.16, cz + H * dz), (cx + H * dx, 0.16, cz + H * dz), 0.012, 'paint_black_gloss', n=10, c=c)
    rod("Rad_rail_bot", (cx - H * dx, -0.16, cz - H * dz), (cx - H * dx, 0.16, cz - H * dz), 0.012, 'paint_black_gloss', n=10, c=c)
    # twin extraction fans behind core
    for i, yy in enumerate((-0.075, 0.075)):
        zz = cz + 0.03 - 0.02 * i
        cyl(f"Rad_fan_{i}", 0.072, 0.025, loc=(cx + 0.045, yy, zz), rot=(0, 65, 0), mat='plastic_black', n=24, c=c)
        cyl(f"Rad_fan_hub_{i}", 0.022, 0.032, loc=(cx + 0.045, yy, zz), rot=(0, 65, 0), mat='engine_black', n=16, c=c)
    # hoses: pump -> rad bottom right ; rad top left -> cylinder head
    tube("Hose_rad_in", [(0.795, -0.10, 0.40), (0.95, -0.12, 0.33), (1.10, -0.13, 0.35), (1.155, -0.15, 0.38)],
         0.016, mat='hose_rubber', res=6, c=c)
    tube("Hose_rad_out", [(1.235, 0.15, 0.55), (1.10, 0.14, 0.60), (0.95, 0.13, 0.60), (0.87, 0.12, 0.57)],
         0.016, mat='hose_rubber', res=6, c=c)
    # overflow tank near swingarm pivot
    box("Coolant_overflow", (0.05, 0.07, 0.12), (0.47, 0.13, 0.33), mat='reservoir_smoke', bev=0.01, c=c)
    # oil cooler (small, in front of engine low)
    box("Oilcooler", (0.03, 0.20, 0.07), (1.06, 0, 0.30), rot=(0, -15, 0), mat='radiator_core', bev=0.005, c=c)
    return {}
