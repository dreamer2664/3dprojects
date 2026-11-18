"""Front end: Öhlins NIX30 Smart EC 2.0 USD fork (43 mm TiN), triple clamps,
steering damper, clip-on handlebars.  (Tech notes §2, §5)"""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "20_FORK"

def build(ctx):
    c = coll(COLL)
    rake = -math.degrees(G.RAKE)
    # steering stem
    rod("F_Steering_stem", G.FRONT_AXLE + G.STEER_DIR * 0.46, G.FRONT_AXLE + G.STEER_DIR * 0.70,
        0.0135, 'steel_stainless', c=c)
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        fp = lambda d: G.fork_point(d, side)
        rod(f"F_Fork_{s}_stanchion", fp(0.285), fp(0.700), 0.0215, 'ohlins_gold', n=28, c=c)
        rod(f"F_Fork_{s}_topcap", fp(0.698), fp(0.713), 0.0228, 'alu_black_anod', n=28, c=c)
        rod(f"F_Fork_{s}_adjuster", fp(0.713), fp(0.720), 0.0075, 'ohlins_gold', n=12, c=c)
        rod(f"F_Fork_{s}_slider", fp(0.045), fp(0.305), 0.0275, 'fork_black', n=28, r2=0.0255, c=c)
        box(f"F_Fork_{s}_axleboss", (0.050, 0.046, 0.085), tuple(fp(0.032)), rot=(0, rake, 0),
            mat='fork_black', bev=0.008, c=c)
        for dz in (-0.022, 0.022):
            bolt(f"F_Fork_{s}_pinch", d=0.008, L=0.05, head='allen', mat='bolt_zinc', c=c,
                 loc=tuple(fp(0.032) + G.STEER_FWD * 0.026 + Vector((0, 0, dz))), rot=(0, 90, 0))
        # radial caliper bosses (100 mm spacing) on trailing face of slider
        for d in (0.118, 0.218):
            bp = fp(d) - G.STEER_FWD * 0.0265
            rod(f"F_Fork_{s}_calboss_{int(d*1000)}", bp, bp - G.STEER_FWD * 0.013, 0.0102, 'fork_black', n=16, c=c)
        # amber fork reflector
        box(f"F_Fork_{s}_reflector", (0.005, 0.0035, 0.095),
            tuple(fp(0.26) + Vector((0, side * 0.0282, 0))), rot=(0, rake, 0), mat='reflector_amber', bev=0.0015, c=c)
        # fender mount bosses
        for sgn in (1, -1):
            mp = fp(0.335) + G.STEER_FWD * 0.028 * sgn
            rod(f"F_Fork_{s}_fendboss_{sgn}", mp, mp + Vector((0, side * 0.012, 0)), 0.008, 'fork_black', n=12, c=c)
    # triple clamps (2025+: lighter aluminium upper)
    mid_low = G.FRONT_AXLE + G.STEER_DIR * G.LOW_CLAMP_DIST
    box("F_Triple_lower", (0.105, 0.232, 0.056), tuple(mid_low), rot=(0, rake, 0), mat='fork_black', bev=0.008, c=c)
    mid_up = G.FRONT_AXLE + G.STEER_DIR * G.TOP_CLAMP_DIST
    box("F_Triple_upper", (0.095, 0.226, 0.030), tuple(mid_up), rot=(0, rake, 0), mat='alu_black_anod', bev=0.006, c=c)
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        rod(f"F_Triple_lower_collar_{s}", G.fork_point(0.505 - 0.031, side), G.fork_point(0.505 + 0.031, side),
            0.0245, 'fork_black', n=24, c=c)
        rod(f"F_Triple_upper_collar_{s}", G.fork_point(0.668 - 0.018, side), G.fork_point(0.668 + 0.018, side),
            0.0240, 'alu_black_anod', n=24, c=c)
        for dx in (-0.035, 0.035):
            bolt(f"F_Triple_upper_pinch_{s}", d=0.007, L=0.026, head='allen', mat='bolt_ti', c=c,
                 loc=tuple(G.fork_point(0.668, side) + G.STEER_FWD * dx + G.STEER_DIR * 0.016), rot=(0, rake, 0))
    # stem nut
    cyl("F_Stem_nut", 0.0205, 0.018, loc=tuple(G.FRONT_AXLE + G.STEER_DIR * 0.690), rot=(0, rake, 0),
        mat='alu_machined', n=6, c=c)
    cyl("F_Stem_nut_cap", 0.012, 0.004, loc=tuple(G.FRONT_AXLE + G.STEER_DIR * 0.700), rot=(0, rake, 0),
        mat='plastic_black', n=24, c=c)
    # clip-on handlebars
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        base = G.fork_point(0.672, side) + G.STEER_FWD * 0.012 + Vector((0, side * 0.012, 0))
        dirv = Vector((-0.58, side * 0.74, -0.20)).normalized()
        end = base + dirv * 0.185
        rod(f"F_Clipon_{s}_bar", base, end, 0.0111, 'alu_black_anod', n=20, c=c)
        rod(f"F_Clipon_{s}_grip", base + dirv * 0.062, end + dirv * 0.002, 0.0162, 'rubber', n=20, c=c)
        rod(f"F_Clipon_{s}_barweight", end, end + dirv * 0.016, 0.0135, 'steel_stainless', n=16, c=c)
        bolt(f"F_Clipon_{s}_clampbolt", d=0.007, L=0.028, loc=tuple(base), rot=(90, 0, 0), head='allen', mat='bolt_ti', c=c)
    # Öhlins Smart EC steering damper (transverse above headstock)
    dp = Vector((1.104, 0.0, 0.918))
    rod("F_SteerDamper_body", dp + Vector((0, -0.072, 0)), dp + Vector((0, 0.018, 0)), 0.0165, 'ohlins_gold', n=24, c=c)
    rod("F_SteerDamper_rod", dp + Vector((0, 0.018, 0)), dp + Vector((0, 0.082, 0)), 0.006, 'steel_stainless', n=12, c=c)
    box("F_SteerDamper_clamp", (0.030, 0.020, 0.022), tuple(dp + Vector((0, 0.085, 0))), mat='alu_black_anod', bev=0.004, c=c)
    box("F_SteerDamper_bracket", (0.05, 0.03, 0.02), tuple(dp + Vector((0.005, -0.02, -0.035))), rot=(0, 20, 0),
        mat='frame_black', bev=0.004, c=c)
    rod("F_SteerDamper_ecwire", dp + Vector((-0.005, -0.072, 0)), (1.02, -0.10, 0.83), 0.004, 'hose_rubber', n=8, c=c)
    # ignition switch on upper clamp
    cyl("F_Ignition", 0.0125, 0.020, loc=tuple(mid_up + G.STEER_FWD * 0.043 + G.STEER_DIR * 0.010),
        rot=(0, rake, 0), mat='plastic_black', n=24, bev=0.002, c=c)
    return {}
