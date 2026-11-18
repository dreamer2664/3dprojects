"""Exhaust: 4-2-1 headers (heat-tinted), under-engine catalyst, mid pipe,
titanium silencer with black end cap, mounted right side."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "60_EXHAUST"

def build(ctx):
    c = coll(COLL)
    # ---- primaries: front bank sweeps down and back; rear bank down and forward
    for i, (p, d) in enumerate(ctx.get('exh_front', [])):
        p = Vector(p)
        side = 1 if p[1] > 0 else -1
        tube(f"Exh_F{i}", [p, p + Vector((0.055, 0, -0.085)), (0.925, p.y * 1.15, 0.315),
                           (0.76, p.y * 1.05, 0.215), (0.66, p.y * 0.85, 0.180)],
             0.0195, mat='header_tint', res=8, bev_res=5, c=c)
    for i, (p, d) in enumerate(ctx.get('exh_rear', [])):
        p = Vector(p)
        tube(f"Exh_R{i}", [p, p + Vector((-0.06, 0, -0.12)), (p.x - 0.03, p.y * 1.3, 0.26),
                           (0.52, p.y * 1.1, 0.185), (0.60, p.y * 0.9, 0.172)],
             0.0195, mat='header_tint', res=8, bev_res=5, c=c)
    # ---- catalyst / collector box under engine (bronze tint)
    box("Exh_catalyst", (0.30, 0.20, 0.105), (0.575, 0, 0.175), rot=(0, -4, 0), mat='cat_tint', bev=0.02, c=c)
    box("Exh_cat_shield", (0.26, 0.22, 0.012), (0.575, 0, 0.118), rot=(0, -4, 0), mat='alu_black_anod', bev=0.004, c=c)
    tube("Exh_cat_in_L", [(0.68, 0.06, 0.175), (0.72, 0.04, 0.18)], 0.021, mat='header_tint', c=c)
    tube("Exh_cat_in_R", [(0.68, -0.06, 0.175), (0.72, -0.04, 0.18)], 0.021, mat='header_tint', c=c)
    # ---- mid pipe to silencer (right side, under swingarm then up)
    tube("Exh_mid", [(0.44, 0, 0.185), (0.26, -0.03, 0.20), (0.10, -0.08, 0.26), (0.11, -0.10, 0.33), (0.17, -0.105, 0.365)],
         0.0245, mat='header_tint', res=8, c=c)
    # ---- silencer: tapered titanium box, right side, rising steeply to the rear
    A = Vector((0.15, -0.105, 0.37)); B = Vector((-0.145, -0.105, 0.665))
    def prof(t):
        w = 0.105 + 0.02 * t; h = 0.085 + 0.025 * t
        return rrect(w, h, 0.025, 4)
    o = loft("Exh_silencer", sweep_sections([A, A + (B - A) * 0.15, A + (B - A) * 0.85, B], prof),
             mat='titanium_brushed')
    bevel(o, 0.005, 2); wnormal(o)
    # end cap (black) + outlet
    capdir = (B - A).normalized()
    o = loft("Exh_endcap", sweep_sections([B - capdir * 0.005, B + capdir * 0.075],
             lambda t: rrect(0.128 - 0.045 * t, 0.112 - 0.035 * t, 0.03, 4)), mat='plastic_black')
    E = B + capdir * 0.075
    cyl("Exh_outlet", 0.028, 0.030, loc=tuple(E + Vector((0, 0, 0.0))),
        rot=(0, math.degrees(math.atan2(capdir.x, capdir.z)) if True else -50, 0), mat='cat_tint', n=28, c=c)
    # silencer strap + mount
    box("Exh_strap", (0.026, 0.135, 0.115), (0.015, -0.105, 0.60), rot=(0, -38, 0), mat='alu_black_anod', bev=0.004, c=c)
    rod("Exh_mount", (0.02, -0.105, 0.68), (0.06, -0.06, 0.75), 0.008, 'bolt_zinc', c=c)
    # heat shield on mid pipe
    box("Exh_mid_shield", (0.16, 0.09, 0.004), (0.13, -0.09, 0.30), rot=(0, -55, 0), mat='titanium_brushed', bev=0.002, c=c)
    return {}
