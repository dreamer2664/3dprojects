"""Bodywork: nose, side fairings, belly pan, tank cover, tail, seats, fenders,
dual winglets, screen, headlights/DRL, mirrors. Painted panels use the
projection-mapped 'paint_livery' material (photo-traced textures)."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "80_BODY"
COLLL = "85_LIGHTS"

def _sec(x, z0, z1, w, n=20, sq=0.5):
    pts = ellipse(2 * w, z1 - z0, n=n, squareness=sq)
    return [(x, px, (z0 + z1) / 2 + py) for (px, py) in pts]

def panel(name, secs, mat='paint_livery', bev=0.005, sq=0.5, c=None):
    o = loft(name, [_sec(*s, sq=sq) for s in secs], mat=mat, c=c)
    if bev: bevel(o, bev, 2); wnormal(o)
    return o

def build(ctx):
    c = coll(COLL); cl = coll(COLLL)
    # ---------------- nose / front fairing
    panel("Nose", [(1.685, 0.700, 0.790, 0.030), (1.610, 0.630, 0.870, 0.075),
                   (1.510, 0.600, 0.955, 0.115), (1.410, 0.620, 1.020, 0.152),
                   (1.310, 0.680, 1.020, 0.168), (1.210, 0.760, 1.020, 0.176),
                   (1.135, 0.830, 0.990, 0.155)], c=c)
    # ---------------- side fairings (one volume spanning both sides)
    panel("Fairing_side", [(1.360, 0.600, 0.825, 0.190), (1.270, 0.545, 0.852, 0.201), (1.160, 0.330, 0.868, 0.206),
                           (1.040, 0.278, 0.862, 0.203), (0.920, 0.250, 0.850, 0.196), (0.760, 0.222, 0.822, 0.184),
                           (0.640, 0.245, 0.775, 0.168), (0.520, 0.320, 0.718, 0.140),
                           (0.400, 0.420, 0.715, 0.106)], bev=0.004, c=c)
    # ---------------- belly pan (matte black)
    panel("Bellypan", [(1.300, 0.205, 0.335, 0.148), (1.060, 0.160, 0.305, 0.188),
                       (0.810, 0.155, 0.290, 0.198), (0.630, 0.185, 0.305, 0.172)],
          mat='paint_black_matte', c=c)
    # ---------------- tank cover
    panel("Tank_cover", [(1.085, 0.820, 0.898, 0.098), (0.960, 0.790, 0.938, 0.160),
                         (0.825, 0.785, 0.946, 0.170), (0.690, 0.800, 0.932, 0.140),
                         (0.585, 0.830, 0.895, 0.098)], c=c)
    # ---------------- tail unit
    panel("Tail", [(0.560, 0.770, 0.875, 0.125), (0.360, 0.795, 0.955, 0.152),
                   (0.160, 0.835, 1.008, 0.118), (-0.015, 0.875, 1.008, 0.070),
                   (-0.145, 0.930, 1.005, 0.038), (-0.205, 0.965, 1.012, 0.014)], c=c)
    # silencer top shroud (black blade over the silencer, seen in photos)
    box("Tail_silencer_shroud", (0.46, 0.105, 0.012), (-0.005, -0.105, 0.575), rot=(0, 134, 0),
        mat='paint_black_matte', bev=0.004, c=c)
    # ---------------- seats
    panel("Seat_rider", [(0.605, 0.825, 0.872, 0.110), (0.455, 0.810, 0.862, 0.140),
                         (0.310, 0.822, 0.878, 0.135), (0.195, 0.845, 0.900, 0.100)],
          mat='seat_vinyl', bev=0.008, sq=0.9, c=c)
    panel("Seat_pillion", [(0.145, 0.988, 1.016, 0.085), (0.005, 0.984, 1.010, 0.080),
                           (-0.095, 0.966, 0.988, 0.042)], mat='seat_vinyl', bev=0.006, c=c)
    # ---------------- front fender + rear hugger
    A = G.FRONT_AXLE
    path = [A + Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a)))) * 0.312
            for a in [28, 50, 70, 90, 110, 130, 152]]
    o = loft("F_Fender", sweep_sections(path, lambda t: rrect(0.150 - 0.04 * abs(t - 0.5), 0.018, 0.007, 3),
                                        up=Vector((0, 1, 0))), mat='paint_black_gloss', c=c)
    bevel(o, 0.003, 2)
    R = G.REAR_AXLE
    path = [R + Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a)))) * 0.340
            for a in [52, 75, 95, 115, 135]]
    o = loft("R_Hugger", sweep_sections(path, lambda t: rrect(0.155, 0.010, 0.004, 2),
                                        up=Vector((0, 1, 0))), mat='plastic_black', c=c)
    # ---------------- winglets (dual element) + endplates
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        for k, (zp, ch) in enumerate(((0.845, 0.185), (0.575, 0.205))):
            y0 = 0.150 * side
            path = [(1.285 - 0.02 * k, y0, zp), (1.375 - 0.01 * k, y0 + side * 0.085, zp - 0.015),
                    (1.450 - 0.01 * k, y0 + side * 0.150, zp - 0.025)]
            o = loft(f"Wing_{s}_{k}", sweep_sections(path, lambda t: rrect(ch * (1 - 0.35 * t), 0.009, 0.004, 2),
                                                     up=Vector((0, 0, 1))), mat='paint_livery', c=c)
            bevel(o, 0.002, 2)
            tip = path[-1]
            box(f"Wing_endplate_{s}_{k}", (ch * 0.7, 0.004, 0.055), (tip[0] - 0.02, tip[1] + side * 0.004, tip[2] - 0.01),
                rot=(0, 8, side * -6), mat='paint_livery', bev=0.002, c=c)
    # ---------------- inner radiator shrouds
    for side in (1, -1):
        box(f"Shroud_{side}", (0.30, 0.008, 0.32), (1.10, side * 0.172, 0.56), rot=(0, 12, 0),
            mat='plastic_black', bev=0.003, c=c)
    # ---------------- heat extraction vents (side fairing, 3 slots each side)
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        for i in range(3):
            box(f"Vent_{s}_{i}", (0.115, 0.006, 0.016), (1.075 - 0.012 * i, side * 0.206, 0.565 + 0.045 * i),
                rot=(0, 22, 0), mat='engine_black', bev=0.004, c=c)
    # ---------------- ram intake
    box("Ram_intake", (0.045, 0.110, 0.058), (1.652, 0, 0.700), rot=(0, -18, 0), mat='engine_black', bev=0.008, c=c)
    # ---------------- windscreen (smoked)
    def scr(t):
        return rrect(0.155 * (1 - 0.45 * t), 0.005, 0.0025, 2)
    def scrw(t):
        return rrect(0.115 * (1 - 0.40 * t), 0.004, 0.002, 2)
    o = loft("Screen", sweep_sections([(1.330, 0, 0.955), (1.272, 0, 1.040), (1.208, 0, 1.108), (1.152, 0, 1.150)],
                                      scrw, up=Vector((0, 0, 1))), mat='screen_smoke', c=cl)
    # ---------------- headlights: 3 LED projectors + DRL brow per side
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        box(f"Headlamp_housing_{s}", (0.090, 0.098, 0.052), (1.525, side * 0.068, 0.770),
            rot=(0, -30, side * -16), mat='engine_black', bev=0.012, c=cl)
        d = Vector((1, side * 0.30, -0.06)).normalized()
        for i, yy in enumerate((0.062, 0.094, 0.124)):
            p = Vector((1.552, side * (yy * 0.72), 0.775 - 0.004 * abs(i - 1)))
            rod(f"Headlamp_proj_{s}_{i}", p - d * 0.02, p + d * 0.024, 0.0152, 'engine_black', n=16, c=cl)
            rod(f"Headlamp_lens_{s}_{i}", p + d * 0.022, p + d * 0.026, 0.0138, 'led_white', n=16, c=cl)
        box(f"Headlamp_drl_{s}", (0.065, 0.090, 0.007), (1.512, side * 0.078, 0.803),
            rot=(0, -30, side * -16), mat='led_white', bev=0.003, c=cl)
    # ---------------- mirrors with integrated indicators
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        rod(f"Mirror_stalk_{s}", (1.345, side * 0.165, 0.985), (1.310, side * 0.330, 1.052), 0.0075,
            'plastic_black', n=12, c=cl)
        box(f"Mirror_housing_{s}", (0.060, 0.115, 0.040), (1.305, side * 0.345, 1.058), rot=(0, -14, side * 8),
            mat='paint_black_gloss', bev=0.012, c=cl)
        box(f"Mirror_glass_{s}", (0.006, 0.100, 0.030), (1.272, side * 0.347, 1.055), rot=(0, -14, side * 8),
            mat='mirror_glass', bev=0.008, c=cl)
        box(f"Mirror_indicator_{s}", (0.030, 0.006, 0.010), (1.330, side * 0.405, 1.062), rot=(0, -14, side * 8),
            mat='reflector_amber', bev=0.002, c=cl)
    # ---------------- fasteners along panel edges
    for i, (x, z, y) in enumerate([(1.28, 0.72, 0.198), (1.06, 0.80, 0.205), (0.82, 0.79, 0.192),
                                   (0.63, 0.69, 0.165), (0.56, 0.55, 0.148), (1.22, 0.44, 0.196)]):
        for side in (1, -1):
            bolt(f"Body_fast_{i}_{side}", d=0.005, L=0.010, loc=(x, side * y, z), rot=(90, 0, 0),
                 head='allen', mat='bolt_zinc', c=c)
    return {}
