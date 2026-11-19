"""Drive: 525 chain (link mesh, 110 links), front sprocket 16T, alignment with
rear 41T from parts_wheels."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "90_DRIVE"
PITCH = 0.015875            # 525
RF = PITCH / (2 * math.sin(math.pi / 16))   # 16T front
Y = 0.112                    # chain plane (matches rear sprocket in parts_wheels)

def build(ctx):
    c = coll(COLL)
    F = Vector((0.508, Y, 0.408))            # front sprocket centre (output shaft)
    R = Vector((0.0, Y, G.REAR_AXLE.z))
    rr = ctx.get('sprocket_rp', PITCH / (2 * math.sin(math.pi / 41)))
    # front sprocket + nut
    cyl("FrontSprocket", RF + 0.004, 0.0065, loc=tuple(F), rot=(90, 0, 0), mat='chain_steel', n=24, c=c)
    cyl("FrontSprocket_nut", 0.014, 0.012, loc=(F.x, F.y + 0.008, F.z), rot=(90, 0, 0), mat='bolt_zinc', n=6, c=c)
    # chain path: top run, arc over rear, bottom run (slight sag), arc over front
    top_a = Vector((F.x, Y, F.z + RF)); top_b = Vector((R.x, Y, R.z + rr))
    bot_a = Vector((R.x, Y, R.z - rr)); bot_b = Vector((F.x, Y, F.z - RF))
    pts = []
    n_top = 30
    for i in range(n_top):
        pts.append(top_a + (top_b - top_a) * (i / n_top))
    for i in range(22):                                    # rear wrap (top -> back -> bottom)
        a = math.radians(90 - 180 * i / 21)
        pts.append(R + Vector((math.cos(a), 0, math.sin(a))) * rr)
    n_bot = 30
    for i in range(n_bot):
        t = i / n_bot
        p = bot_a + (bot_b - bot_a) * t
        pts.append(Vector((p.x, Y, p.z - 0.010 * math.sin(math.pi * t))))   # sag
    for i in range(14):                                    # front wrap bottom -> front -> top
        a = math.radians(270 - 180 * i / 13)
        pts.append(F + Vector((math.cos(a), 0, math.sin(a))) * RF)
    # build link mesh (outer plates boxes oriented along path)
    vs = []; fs = []; n = len(pts)
    for i in range(n):
        p = pts[i]; q = pts[(i + 1) % n]
        d = (q - p); L = d.length
        if L < 1e-6: continue
        d = d.normalized()
        side = Vector((0, 1, 0)); up = d.cross(side)
        hx = d * (L * 0.55); hy = side * 0.0095; hz = up * 0.0042
        base = len(vs)
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    vs.append(tuple(p + hx * sx + hy * sy + hz * sz))
        fs.extend([(base + 0, base + 1, base + 3, base + 2), (base + 4, base + 6, base + 7, base + 5),
                   (base + 0, base + 4, base + 5, base + 1), (base + 2, base + 3, base + 7, base + 6),
                   (base + 0, base + 2, base + 6, base + 4), (base + 1, base + 5, base + 7, base + 3)])
    o = mesh_obj("Chain", vs, fs, mat='chain_steel', smooth=False, c=c)
    # gold-ish lube sheen skipped; master link rivet
    cyl("Chain_rivet", 0.003, 0.026, loc=tuple(pts[0]), rot=(90, 0, 0), mat='bolt_zinc', n=8, c=c)
    return {}
