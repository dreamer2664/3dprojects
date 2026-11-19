"""Cockpit: TFT dash (photo-real race screen texture, emissive), switchgear,
master cylinders + levers, reservoirs, throttle. Mirrors/lights in parts_body."""
import math, os
from mathutils import Vector
from lib import *
import geom as G

COLL = "82_COCKPIT"

def _bar_end(side):
    base = G.fork_point(0.672, side) + G.STEER_FWD * 0.012 + Vector((0, side * 0.012, 0))
    dirv = Vector((-0.58, side * 0.74, -0.20)).normalized()
    return base, dirv

def build(ctx):
    c = coll(COLL)
    # ---- TFT: 5" screen, housing tilted toward rider
    loc = Vector((1.086, 0.0, 0.988)); tilt = 38.0
    box("TFT_housing", (0.028, 0.132, 0.082), tuple(loc), rot=(0, tilt, 0), mat='plastic_black', bev=0.006, c=c)
    box("TFT_hood", (0.05, 0.135, 0.02), tuple(loc + Vector((0.015, 0, 0.048))), rot=(0, tilt, 0),
        mat='plastic_black', bev=0.005, c=c)
    # screen quad with real UVs, emissive texture
    w, h = 0.0585, 0.0335
    vs = [(-0.001, -w, -h), (-0.001, w, -h), (-0.001, w, h), (-0.001, -w, h)]   # local plane facing -X (rider)
    o = mesh_obj("TFT_screen", vs, [(0, 1, 2, 3)], mat=None, smooth=False, c=c)
    uv = o.data.uv_layers.new(name="UVMap")
    for li, (u, v) in enumerate([(1, 0), (0, 0), (0, 1), (1, 1)]):
        uv.data[li].uv = (u, v)
    m = mat_image('tft', os.path.join(TEX, 'tft_race.png'), rough=0.25, emit=1.6)
    assign(o, m)
    xform(o, tuple(loc + Vector((-0.0148, 0, 0.004))), rot=(0, tilt, 0))
    # support bracket to frame
    box("TFT_bracket", (0.02, 0.05, 0.09), (1.10, 0, 0.945), rot=(0, 20, 0), mat='alu_black_anod', bev=0.003, c=c)
    # ---- controls on clip-ons
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        base, dirv = _bar_end(side)
        grip_in = base + dirv * 0.062
        # switchgear
        sw = grip_in - dirv * 0.020
        box(f"Switch_{s}", (0.038, 0.030, 0.034), tuple(sw + Vector((0, 0, 0.004))),
            rot=(0, 0, math.degrees(math.atan2(dirv.y, dirv.x))), mat='plastic_black', bev=0.006, c=c)
        for i in range(2 if side > 0 else 3):
            cyl(f"Switch_btn_{s}_{i}", 0.004, 0.006, loc=tuple(sw + Vector((0, side * 0.016, 0.008 - i * 0.009))),
                rot=(90, 0, 0), mat='plastic_black', n=10, c=c)
        # master cylinder + lever (brake right, clutch left)
        mc = grip_in - dirv * 0.045 + Vector((0, 0, 0.025))
        rod(f"MasterCyl_{s}", mc - Vector((0.035, 0, 0)), mc + Vector((0.035, 0, 0)), 0.014, 'alu_black_anod', n=16, c=c)
        lv0 = mc + Vector((0.0, side * 0.012, 0.0))
        rod(f"Lever_{s}_pivot", lv0, lv0 + Vector((-0.045, side * 0.022, 0.012)), 0.006, 'alu_machined', n=10, c=c)
        rod(f"Lever_{s}_blade", lv0 + Vector((-0.045, side * 0.022, 0.012)),
            lv0 + Vector((-0.150, side * 0.062, 0.022)), 0.0055, 'alu_machined', n=10, r2=0.0038, c=c)
        # fluid reservoir (smoked) with cap + sight window
        rp = mc + Vector((-0.01, 0, 0.045))
        cyl(f"Reservoir_{s}", 0.021, 0.042, loc=tuple(rp), mat='reservoir_smoke', n=20, c=c)
        cyl(f"Reservoir_cap_{s}", 0.0225, 0.008, loc=tuple(rp + Vector((0, 0, 0.024))), mat='alu_black_anod', n=20, bev=0.002, c=c)
    # throttle tube (right)
    base, dirv = _bar_end(-1)
    rod("Throttle_tube", base + dirv * 0.058, base + dirv * 0.075, 0.0175, 'plastic_black', n=18, c=c)
    # cables down from controls
    tube("Cable_throttle", [tuple(base + dirv * 0.06), (1.10, -0.16, 0.86), (1.00, -0.13, 0.74), (0.80, -0.10, 0.68)],
         0.0035, mat='hose_rubber', c=c)
    tube("Cable_clutch", [(1.14, 0.17, 0.90), (1.06, 0.15, 0.78), (0.86, 0.13, 0.60), (0.545, 0.185, 0.48)],
         0.0045, mat='braided', c=c)
    return {}
