"""Frame: aluminium twin-spar (cast + pressed, welded), headstock, swingarm pivot
plates, engine mounts, subframe, fuel cell, rearsets, sidestand."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "30_FRAME"

def _spar(side):
    s = 'L' if side > 0 else 'R'
    y = 0.070 * side
    path = [(1.062, y, 0.862), (0.93, y, 0.848), (0.78, y, 0.805), (0.665, y, 0.715),
            (0.575, y, 0.605), (0.535, y, 0.505)]
    def prof(t):
        h = 0.105 - 0.030 * t
        return rrect(0.034, h, 0.012, 3)
    o = loft(f"Frame_spar_{s}", sweep_sections(path, prof), mat='frame_black')
    bevel(o, 0.004, 2); wnormal(o)
    return o

def build(ctx):
    c = coll(COLL)
    # headstock along steering axis
    rod("Frame_headstock", G.steer_point(0.795), G.steer_point(0.985), 0.0475, 'frame_black', n=32, c=c)
    rod("Frame_headstock_gusset", G.steer_point(0.80), (1.03, 0, 0.84), 0.028, 'frame_black', n=20, c=c)
    for side in (1, -1):
        _spar(side)
    # cross beam under front of tank
    rod("Frame_cross_front", (0.985, -0.062, 0.795), (0.985, 0.062, 0.795), 0.020, 'frame_black', n=20, c=c)
    # swingarm pivot plates (cast) + bosses
    plate_pts = [(0.655, 0.615), (0.585, 0.635), (0.490, 0.600), (0.430, 0.505), (0.425, 0.375),
                 (0.470, 0.275), (0.575, 0.270), (0.645, 0.360), (0.665, 0.480)]
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        extrude_xz(f"Frame_pivotplate_{s}", plate_pts, side * 0.052, side * 0.104, mat='frame_black', bev=0.006, coll=c)
        cyl(f"Frame_pivot_boss_{s}", 0.036, 0.012, loc=(0.520, side * 0.107, 0.465), rot=(90, 0, 0),
            mat='frame_black', n=28, bev=0.003, c=c)
    cyl("Frame_pivot_nut", 0.0275, 0.016, loc=(0.520, -0.122, 0.465), rot=(90, 0, 0), mat='bolt_zinc', n=6, c=c)
    cyl("Frame_pivot_capL", 0.024, 0.008, loc=(0.520, 0.120, 0.465), rot=(90, 0, 0), mat='alu_machined', n=28, c=c)
    rod("Frame_pivot_shaft", (0.520, -0.12, 0.465), (0.520, 0.12, 0.465), 0.0145, 'steel_stainless', c=c)
    # engine mount bosses + through bolts (front head, mid case, rear on pivot plates)
    for i, (x, z, hy) in enumerate([(0.925, 0.400, 0.150), (0.940, 0.545, 0.140),
                                    (0.470, 0.555, 0.108), (0.575, 0.330, 0.108)]):
        cyl(f"Frame_engmount_{i}", 0.014, 2 * hy + 0.02, loc=(x, 0, z), rot=(90, 0, 0), mat='bolt_zinc', n=16, c=c)
        for side in (1, -1):
            cyl(f"Frame_engmount_boss_{i}_{side}", 0.023, 0.010, loc=(x, side * (hy + 0.008), z), rot=(90, 0, 0),
                mat='frame_black', n=20, c=c)
    # ---- subframe (cast aluminium, black)
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        y = 0.058 * side
        path = [(0.635, y, 0.730), (0.42, 0.068 * side, 0.790), (0.20, 0.072 * side, 0.838), (0.115, 0.066 * side, 0.862)]
        def prof(t):
            return rrect(0.030, 0.040 - 0.012 * t, 0.010, 3)
        o = loft(f"Subframe_beam_{s}", sweep_sections(path, prof), mat='frame_black')
        bevel(o, 0.004, 2); wnormal(o)
    rod("Subframe_cross", (0.135, -0.062, 0.855), (0.135, 0.062, 0.855), 0.015, 'frame_black', n=16, c=c)
    box("Subframe_tray", (0.30, 0.165, 0.012), (0.36, 0, 0.755), mat='plastic_black', bev=0.004, c=c)
    box("Subframe_ecu", (0.10, 0.12, 0.030), (0.33, 0, 0.775), mat='alu_black_anod', bev=0.004, c=c)   # ECU
    cyl("Battery", 0.065, 0.14, loc=(0.475, 0, 0.745), rot=(0, 90, 0), mat='plastic_black', n=4, bev=0.006, c=c)
    # ---- fuel cell (mostly under seat) + filler
    fuel = loft("Fuel_cell", sweep_sections(
        [(0.53, 0, 0.62), (0.44, 0, 0.60), (0.28, 0, 0.63), (0.20, 0, 0.70)],
        lambda t: rrect(0.19 - 0.03 * t, 0.15, 0.05, 4)), mat='plastic_black')
    rod("Fuel_filler_neck", (0.75, 0, 0.72), (0.835, 0, 0.905), 0.040, 'plastic_black', n=24, c=c)
    lathe("Fuel_cap", [(0.0, 0.0), (0.042, 0.0), (0.045, 0.006), (0.042, 0.012), (0.030, 0.016), (0.0, 0.016)],
          n=40, loc=(0.847, 0, 0.918), mat='alu_black_anod', closed=True, c=c)
    # ---- rearsets
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        y0, y1 = side * 0.158, side * 0.172
        pts = [(0.660, 0.395), (0.540, 0.425), (0.505, 0.360), (0.530, 0.270), (0.600, 0.250),
               (0.655, 0.300), (0.670, 0.360)]
        pl = extrude_xz(f"Rearset_plate_{s}", pts, min(y0, y1), max(y0, y1), mat='alu_cast', bev=0.003, coll=c)
        for i, (hx, hz) in enumerate([(0.585, 0.395), (0.555, 0.355), (0.575, 0.310), (0.620, 0.290), (0.635, 0.345)]):
            cyl(f"Rearset_hole_{s}_{i}", 0.011, 0.02, loc=(hx, side * 0.165, hz), rot=(90, 0, 0), mat='engine_black', n=16, c=c)
        # footpeg
        fp = Vector((G.FOOTPEG.x, side * G.FOOTPEG.y, G.FOOTPEG.z))
        rod(f"Rearset_peg_{s}", fp, fp + Vector((0, side * 0.075, 0)), 0.0115, 'alu_machined', n=20, c=c)
        rod(f"Rearset_peg_tip_{s}", fp + Vector((0, side * 0.070, 0)), fp + Vector((0, side * 0.080, 0)),
            0.0135, 'alu_black_anod', n=16, c=c)
        box(f"Rearset_heel_{s}", (0.09, 0.006, 0.05), (0.615, side * 0.175, 0.365), rot=(0, -25, 0),
            mat='alu_black_anod', bev=0.003, c=c)
        if side < 0:  # brake pedal (right side)
            rod("Rearset_brakelever", (0.620, -0.185, 0.300), (0.700, -0.195, 0.282), 0.007, 'alu_machined', n=12, c=c)
            rod("Rearset_brake_tip", (0.700, -0.195, 0.282), (0.716, -0.195, 0.278), 0.010, 'alu_black_anod', n=12, c=c)
            cyl("Rearset_master", 0.016, 0.085, loc=(0.520, -0.150, 0.415), rot=(0, 90, 0), mat='alu_black_anod', n=20, c=c)
            rod("Rearset_master_rod", (0.555, -0.155, 0.415), (0.625, -0.180, 0.310), 0.004, 'steel_stainless', n=10, c=c)
        else:        # shift lever (left side)
            rod("Rearset_shiftlever", (0.620, 0.185, 0.300), (0.700, 0.195, 0.285), 0.007, 'alu_machined', n=12, c=c)
            rod("Rearset_shift_tip", (0.700, 0.195, 0.285), (0.716, 0.195, 0.282), 0.010, 'rubber', n=12, c=c)
            rod("Rearset_shift_link", (0.615, 0.180, 0.305), (0.700, 0.155, 0.415), 0.0035, 'steel_stainless', n=10, c=c)
    # sidestand (retracted) on left
    rod("Sidestand_leg", (0.655, 0.125, 0.290), (0.515, 0.185, 0.225), 0.013, 'frame_black', n=16, c=c)
    cyl("Sidestand_pivotbolt", 0.012, 0.03, loc=(0.655, 0.135, 0.290), rot=(90,0,0), mat='bolt_zinc', n=12, c=c)
    cyl("Sidestand_pivot", 0.014, 0.030, loc=(0.585, 0.140, 0.285), rot=(90, 0, 0), mat='bolt_zinc', n=16, c=c)
    return {}
