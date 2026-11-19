"""Rear: inverted-brace aluminium swingarm, Öhlins TTX36 EC shock with
progressive linkage, chain slider/adjusters."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "40_SWINGARM"

def _helix(name, a, b, R, turns, wire, mat, c):
    a, b = Vector(a), Vector(b)
    d = b - a; L = d.length; axis = d.normalized()
    u = axis.cross(Vector((0, 1, 0)))
    if u.length < 1e-6: u = axis.cross(Vector((1, 0, 0)))
    u.normalize(); v = axis.cross(u).normalized()
    pts = []
    n = int(turns * 16)
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t
        pts.append(a + d * t + (u * math.cos(ang) + v * math.sin(ang)) * R)
    return tube(name, pts, wire, mat=mat, res=2, bev_res=3, c=c, smooth_curve=False)

def build(ctx):
    c = coll(COLL)
    piv, axl = G.SWINGARM_PIVOT, G.REAR_AXLE
    # main arms
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        y = side
        path = [(piv.x + 0.01, 0.088 * y, piv.z - 0.01), (0.30, 0.094 * y, 0.400),
                (0.10, 0.088 * y, 0.340), (axl.x + 0.01, 0.082 * y, axl.z)]
        def prof(t):
            return rrect(0.042 - 0.008 * t, 0.105 - 0.048 * t, 0.014, 3)
        o = loft(f"Swarm_arm_{s}", sweep_sections(path, prof), mat='alu_cast')
        bevel(o, 0.005, 2); wnormal(o)
    # upper triangulated brace (black) visible above the silver arm
    for side in (1, -1):
        s2 = 'L' if side > 0 else 'R'
        path = [(piv.x + 0.02, 0.075 * side, piv.z + 0.055), (0.28, 0.080 * side, 0.475), (0.05, 0.075 * side, 0.385)]
        def prof2(t):
            return rrect(0.030, 0.052 - 0.020 * t, 0.010, 2)
        o = loft(f"Swarm_truss_{s2}", sweep_sections(path, prof2), mat='frame_black')
        bevel(o, 0.004, 2); wnormal(o)
    # inverted braces (under-slung) + bridges
    rod("Swarm_brace_1", (0.30, -0.085, 0.355), (0.30, 0.085, 0.355), 0.021, 'alu_cast', n=20, c=c)
    rod("Swarm_brace_2", (0.16, -0.082, 0.325), (0.16, 0.082, 0.325), 0.019, 'alu_cast', n=20, c=c)
    rod("Swarm_bridge_pivot", (0.46, -0.09, 0.43), (0.46, 0.09, 0.43), 0.024, 'alu_cast', n=20, c=c)
    # axle blocks, adjusters, axle
    for side in (1, -1):
        s = 'L' if side > 0 else 'R'
        box(f"Swarm_axleblock_{s}", (0.075, 0.034, 0.052), (0.030, side * 0.082, 0.315), mat='alu_machined', bev=0.006, c=c)
        rod(f"Swarm_adjuster_{s}", (-0.010, side * 0.082, 0.328), (-0.045, side * 0.082, 0.332), 0.005, 'bolt_zinc', n=10, c=c)
    cyl("Swarm_axle_nut", 0.030, 0.020, loc=(0.0, -0.115, 0.315), rot=(90, 0, 0), mat='bolt_zinc', n=6, c=c)
    cyl("Swarm_axle_capL", 0.026, 0.010, loc=(0.0, 0.118, 0.315), rot=(90, 0, 0), mat='alu_black_anod', n=6, c=c)
    # chain slider + guard
    box("Swarm_chain_slider", (0.26, 0.055, 0.014), (0.315, 0.096, 0.418), rot=(0, -8, 0), mat='plastic_black', bev=0.004, c=c)
    box("Swarm_chain_guard", (0.10, 0.006, 0.05), (0.475, 0.105, 0.42), rot=(0, -25, 0), mat='plastic_black', bev=0.002, c=c)
    # hugger mount tab
    box("Swarm_hugger_tab", (0.05, 0.10, 0.008), (0.30, 0, 0.36), rot=(0, -10, 0), mat='alu_cast', bev=0.002, c=c)
    # ---- Öhlins TTX36 EC shock
    top = Vector((0.640, 0.0, 0.700)); bot = Vector((0.680, 0.0, 0.415))   # behind swingarm pivot
    axis = (top - bot)
    rod("Shock_body", bot + axis * 0.06, bot + axis * 0.55, 0.0215, 'alu_black_anod', n=24, c=c)
    rod("Shock_rod", bot + axis * 0.55, top - axis * 0.02, 0.0085, 'steel_stainless', n=14, c=c)
    _helix("Shock_spring", bot + axis * 0.13, top - axis * 0.06, 0.0475, 7.5, 0.0078, 'ohlins_yellow', c)
    lathe("Shock_spring_seatB", [(0.030, -0.004), (0.052, -0.002), (0.052, 0.004), (0.030, 0.006)],
          loc=tuple(bot + axis * 0.13), rot=(0, 90, 0), mat='alu_black_anod', closed=True, c=c)
    # piggyback reservoir + EC valve
    rod("Shock_reservoir", top - axis * 0.05 + Vector((-0.035, 0, 0)), top - axis * 0.05 + Vector((-0.035, 0, -0.10)),
        0.019, 'ohlins_gold', n=22, c=c)
    box("Shock_ecvalve", (0.035, 0.025, 0.025), tuple(top - axis * 0.02 + Vector((0.01, 0.0, 0.02))), mat='alu_black_anod', bev=0.004, c=c)
    rod("Shock_eye_top", top, top + axis.normalized() * 0.02, 0.0135, 'alu_black_anod', n=16, c=c)
    # frame bracket
    box("Shock_topbracket", (0.05, 0.10, 0.02), (0.585, 0, 0.715), mat='frame_black', bev=0.004, c=c)
    # ---- progressive linkage
    extrude_xz("Link_rocker", [(0.545, 0.490), (0.508, 0.415), (0.585, 0.410)], -0.020, 0.020,
               mat='alu_machined', bev=0.003, coll=c)
    cyl("Link_rocker_pivot", 0.011, 0.09, loc=(0.545, 0, 0.490), rot=(90, 0, 0), mat='bolt_zinc', n=14, c=c)
    for side in (1, -1):
        rod(f"Link_pullrod_{side}", (0.508, side * 0.022, 0.412), (0.365, side * 0.030, 0.368), 0.009, 'alu_machined', n=14, c=c)
    cyl("Link_shock_bolt", 0.010, 0.06, loc=(0.562, 0, 0.413), rot=(90, 0, 0), mat='bolt_zinc', n=12, c=c)
    return {}
