"""Wheels, tyres, brake discs, calipers, rear sprocket carrier."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from lib import *
from lib import _link, _CUR
import geom as G

# ------------------------------------------------------------------ helpers
def _rot_to_y(o):
    """Lathe objects are built around local Z; wheel axis is world Y."""
    o.rotation_euler = (math.radians(-90), 0, 0)
    return o

def tyre(name, ry, rr, rc, phi_max, bead_y, n=96, front=True):
    """Toroidal carcass: crown/shoulder ellipse, sidewall turning in to the bead at the rim flange."""
    prof = []
    steps = 32
    for i in range(steps + 1):
        phi = math.radians(-phi_max + 2 * phi_max * i / steps)
        y = ry * math.sin(phi); r = rc + rr * math.cos(phi)
        prof.append((r, y))
    lo = [(0.2235, -bead_y - 0.004), (0.2185, -bead_y - 0.001), (G.RIM_R + 0.001, -bead_y + 0.004)]
    hi = [(G.RIM_R + 0.001, bead_y - 0.004), (0.2185, bead_y + 0.001), (0.2235, bead_y + 0.004)]
    prof = lo + prof + hi
    o = lathe(name, prof, n=n, mat='tyre', closed=True)
    subsurf(o, 1, 2)
    return _rot_to_y(o)

def rim(name, W, n=96):
    h = W / 2
    prof = [(0.1985, -h + 0.006), (0.2120, -h + 0.002), (0.2150, -h - 0.004), (0.2245, -h - 0.0065), (0.2275, -h - 0.004),
            (0.2268, -h + 0.0005), (0.2165, -h + 0.006), (0.2155, -h + 0.012), (0.2050, -0.012), (0.2040, 0.012),
            (0.2155, h - 0.012), (0.2165, h - 0.006), (0.2268, h - 0.0005), (0.2275, h + 0.004), (0.2245, h + 0.0065),
            (0.2150, h + 0.004), (0.2120, h - 0.002), (0.1985, h - 0.006)]
    o = lathe(name, prof, n=n, mat='paint_black_gloss', closed=True)
    return _rot_to_y(o)

def split_spokes(name, W, hub_r, rim_r, thick, n_spokes=5, rot0=0.0):
    """Forged 5 split-spoke star: each spoke forks into two legs that meet the rim.
    Built in the wheel plane (local XY) and extruded along local Z (wheel axis)."""
    bm = bmesh.new()
    for s in range(n_spokes):
        a0 = rot0 + 2 * math.pi * s / n_spokes
        # outline of one Y-shaped spoke in polar coords (r, angle offset)
        split_r = hub_r + 0.30 * (rim_r - hub_r)
        leg_sep = math.radians(15.0)       # half angle between the legs at the rim
        w_root = 0.030; w_leg = 0.0125
        pts = []
        # root (at hub), split point, legs to rim — build closed polygon CCW
        def P(r, da): return (r * math.cos(a0 + da), r * math.sin(a0 + da))
        pts.append(P(hub_r, -w_root / hub_r / 2))
        pts.append(P(split_r, -w_root / split_r / 2 * 1.05))
        # outer edge of leg 1
        for k in range(1, 6):
            t = k / 5; r = split_r + t * (rim_r - split_r); da = -(leg_sep * t ** 0.8) - (w_leg / r / 2) * (1 + 0.6 * (1 - t))
            pts.append(P(r, da))
        r = rim_r; pts.append(P(r + 0.004, -leg_sep - w_leg / r * 0.9))
        pts.append(P(r + 0.004, -leg_sep + w_leg / r * 0.9))
        for k in range(5, 0, -1):
            t = k / 5; r = split_r + t * (rim_r - split_r); da = -(leg_sep * t ** 0.8) + (w_leg / r / 2) * (1 + 0.6 * (1 - t))
            pts.append(P(r, da))
        pts.append(P(split_r + 0.018, 0.0))
        for k in range(1, 6):
            t = k / 5; r = split_r + t * (rim_r - split_r); da = (leg_sep * t ** 0.8) - (w_leg / r / 2) * (1 + 0.6 * (1 - t))
            pts.append(P(r, da))
        r = rim_r; pts.append(P(r + 0.004, leg_sep - w_leg / r * 0.9))
        pts.append(P(r + 0.004, leg_sep + w_leg / r * 0.9))
        for k in range(5, 0, -1):
            t = k / 5; r = split_r + t * (rim_r - split_r); da = (leg_sep * t ** 0.8) + (w_leg / r / 2) * (1 + 0.6 * (1 - t))
            pts.append(P(r, da))
        pts.append(P(split_r, w_root / split_r / 2 * 1.05))
        pts.append(P(hub_r, w_root / hub_r / 2))
        vs = [bm.verts.new((x, y, -thick / 2)) for x, y in pts]
        f = bm.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=nv, vec=(0, 0, thick))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); _link(o)
    assign(o, 'paint_black_gloss')
    bevel(o, 0.0035, 3, angle=30)
    auto_smooth(o, 30)
    return o

def hub(name, W, front=True):
    if front:
        prof = [(0.012, -0.060), (0.034, -0.060), (0.036, -0.052), (0.060, -0.050), (0.062, -0.044), (0.040, -0.040),
                (0.046, -0.020), (0.046, 0.020), (0.040, 0.040), (0.062, 0.044), (0.060, 0.050), (0.036, 0.052),
                (0.034, 0.060), (0.012, 0.060)]
    else:
        prof = [(0.016, -0.075), (0.042, -0.075), (0.050, -0.066), (0.075, -0.062), (0.075, -0.050), (0.056, -0.045),
                (0.056, 0.030), (0.072, 0.040), (0.074, 0.060), (0.046, 0.066), (0.020, 0.066)]
    o = lathe(name, prof, n=48, mat='paint_black_gloss', closed=True)
    return _rot_to_y(o)

def wheel_assembly(prefix, centre, front=True):
    W = 0.089 if front else 0.152
    parts = []
    t = tyre(f"{prefix}_Tyre_Pirelli_{'120-70ZR17' if front else '200-55ZR17'}",
             ry=0.060 if front else 0.100, rr=0.052 if front else 0.072, rc=0.240 if front else 0.243,
             phi_max=112 if front else 112, bead_y=W / 2 + 0.006, front=front)
    r = rim(f"{prefix}_Rim_forged_{'3.5x17' if front else '6.0x17'}", W)
    s = split_spokes(f"{prefix}_Spokes_5split", W, hub_r=0.048 if front else 0.070, rim_r=0.201, thick=0.024 if front else 0.030)
    s.rotation_euler = (math.radians(-90), 0, 0)
    h = hub(f"{prefix}_Hub", W, front)
    # machined edge highlight ring on rim lip (Factory wheels are fully machined)
    lip = torus(f"{prefix}_Rim_machined_lip_L", 0.2272, 0.0012, rot=(90, 0, 0), mat='alu_machined', n=96, m=6)
    lip.location = (0, W / 2 + 0.004, 0)
    lip2 = torus(f"{prefix}_Rim_machined_lip_R", 0.2272, 0.0012, rot=(90, 0, 0), mat='alu_machined', n=96, m=6)
    lip2.location = (0, -W / 2 - 0.004, 0)
    valve = cyl(f"{prefix}_Valve_stem", 0.004, 0.03, loc=(0.0, 0.0, 0.198), rot=(0, 0, 0), mat='alu_black_anod', n=12)
    valve.location = (0.0, -0.02, 0.196); valve.rotation_euler = (0, 0, 0)
    root = empty(f"{prefix}_WHEEL", centre)
    for o in (t, r, s, h, lip, lip2, valve):
        o.location = Vector(o.location) + centre
        parent(o, root)
    # axle + nuts
    ax = cyl(f"{prefix}_Axle", 0.0125 if front else 0.0125, 0.25 if front else 0.30, loc=centre, rot=(90, 0, 0), mat='steel_stainless', n=24)
    parent(ax, root)
    nut = bolt(f"{prefix}_Axle_nut", d=0.016 if not front else 0.012, L=0.01, loc=centre + Vector((0, -0.125 if front else -0.15, 0)),
               rot=(90, 0, 0), head='hex', mat='alu_black_anod')
    parent(nut, root)
    return root

# ------------------------------------------------------------------ brakes
def drilled_disc(name, r_out, r_in, thick, rows=3, holes_per_row=30, hole_r=0.0026):
    """Stainless floating rotor with T-drive style inner tabs and drilled pattern."""
    bm = bmesh.new()
    n = 120
    prof = [(r_in, -thick / 2), (r_out, -thick / 2), (r_out, thick / 2), (r_in, thick / 2)]
    bmesh.ops.create_circle(bm, cap_ends=False, radius=r_out, segments=n)
    bm.free()
    o = lathe(name, prof, n=n, mat='disc_steel', closed=True)
    # holes cutter (single joined object for one EXACT boolean)
    cbm = bmesh.new()
    for row in range(rows):
        rr = r_in + (r_out - r_in) * (0.28 + 0.24 * row)
        for k in range(holes_per_row):
            a = 2 * math.pi * (k + 0.33 * row) / holes_per_row
            m = Matrix.Translation((rr * math.cos(a), rr * math.sin(a), 0))
            bmesh.ops.create_cone(cbm, cap_ends=True, cap_tris=False, segments=10, radius1=hole_r, radius2=hole_r, depth=thick * 3, matrix=m)
    cme = bpy.data.meshes.new(name + "_holes"); cbm.to_mesh(cme); cbm.free()
    cut = bpy.data.objects.new(name + "_holes_cutter", cme); bpy.context.scene.collection.objects.link(cut)
    boolean(o, cut, apply=True)
    bpy.data.objects.remove(cut)
    auto_smooth(o, 30)
    return o

def disc_carrier(name, r_hub, r_pins, n_arms=6, thick=0.006):
    bm = bmesh.new()
    pts = []
    N = n_arms * 16
    for i in range(N):
        a = 2 * math.pi * i / N
        ph = (i % 16) / 16.0
        # arms: radius bulges to pin radius at arm centre
        bump = math.exp(-((ph - 0.5) / 0.14) ** 2)
        r = r_hub + 0.018 + (r_pins + 0.010 - r_hub - 0.018) * bump
        pts.append((r * math.cos(a), r * math.sin(a)))
    inner = [(r_hub * math.cos(2 * math.pi * i / N), r_hub * math.sin(2 * math.pi * i / N)) for i in range(N)]
    vo = [bm.verts.new((x, y, -thick / 2)) for x, y in pts]
    vi = [bm.verts.new((x, y, -thick / 2)) for x, y in inner]
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((vi[i], vi[j], vo[j], vo[i]))
    ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, 0, thick))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); _link(o)
    assign(o, 'disc_carrier'); bevel(o, 0.0012, 2, angle=30); auto_smooth(o, 30)
    return o

def front_disc(prefix, centre, side):
    y = side * 0.0775
    root = empty(f"{prefix}_DISC_330", centre + Vector((0, y, 0)))
    d = drilled_disc(f"{prefix}_Disc_rotor_330x5.5", 0.165, 0.124, 0.0055)
    c = disc_carrier(f"{prefix}_Disc_carrier_alu", 0.034, 0.118, n_arms=6)
    pins = []
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6 + math.pi / 6 * 0
        a = 2 * math.pi * k / 6
        p = cyl(f"{prefix}_Disc_float_pin_{k}", 0.0055, 0.0085, loc=(0.1225 * math.cos(a), 0.1225 * math.sin(a), 0), mat='steel_stainless', n=16)
        pins.append(p)
    bolts = []
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        b = bolt(f"{prefix}_Disc_bolt_{k}", d=0.004, L=0.008, loc=(0.040 * math.cos(a), 0.040 * math.sin(a), 0.003), head='allen', mat='bolt_zinc')
        if side < 0: b.rotation_euler = (math.pi, 0, 0); b.location.z = -0.003
        bolts.append(b)
    for o in [d, c] + pins + bolts:
        o.location = Matrix.Rotation(math.radians(-90), 4, 'X') @ Vector(o.location)
        o.rotation_euler.rotate(Euler((math.radians(-90), 0, 0)))
        o.location += root.location
        parent(o, root)
    return root

def hypure_caliper(prefix, centre, side, angle_deg):
    """Brembo HYPURE: asymmetric cast monobloc, 4x30 mm pistons, 100 mm radial mount, 3 bridges.
    Natural grey anodised (OE). Built in a local frame: X = tangent, Z = radial outward, Y = axle direction."""
    root = empty(f"{prefix}_CALIPER_Hypure", centre)
    yd = side * 0.0775
    parts = []
    L = 0.118; H = 0.050; T = 0.021; gap = 0.0135
    # outer half (away from wheel) and inner half
    for nm, yy in (("outer", yd + side * (gap / 2 + T / 2)), ("inner", yd - side * (gap / 2 + T / 2))):
        sec = []
        # lofted body with asymmetric (wedge) profile along tangent
        for i, t in enumerate([-0.5, -0.42, -0.25, 0.0, 0.25, 0.42, 0.5]):
            x = t * L
            hh = H * (0.70 + 0.30 * math.cos(t * math.pi)) * (1.0 + 0.10 * t)
            ww = T * (0.85 + 0.15 * math.cos(t * math.pi))
            pts = rrect(ww, hh, min(ww, hh) * 0.42, 3)
            sec.append([(x, yy + u, 0.143 + v) for (u, v) in pts])
        o = loft(f"{prefix}_Caliper_half_{nm}", sec, mat='alu_grey_anod')
        subsurf(o, 1, 2); auto_smooth(o, 60)
        parts.append(o)
        # piston bosses (visible as round domes on the outer face)
        if nm == "outer":
            for px in (-0.026, 0.026):
                b = cyl(f"{prefix}_Caliper_piston_boss_{'A' if px < 0 else 'B'}", 0.0185, 0.008, loc=(px, yy + side * T * 0.45, 0.143),
                        rot=(90, 0, 0), mat='alu_grey_anod', n=32, bev=0.002)
                parts.append(b)
    # three bridges over the disc
    for bx in (-0.040, 0.0, 0.040):
        b = box(f"{prefix}_Caliper_bridge_{int(bx*1000)}", (0.016, gap + 0.004, 0.012), loc=(bx, yd, 0.143 + H * 0.36), mat='alu_grey_anod', bev=0.003)
        parts.append(b)
    # pads
    for nm, yy in (("o", yd + side * 0.0045), ("i", yd - side * 0.0045)):
        p = box(f"{prefix}_Brake_pad_{nm}", (0.092, 0.0038, 0.034), loc=(0, yy, 0.145), mat='brake_pad', bev=0.001)
        parts.append(p)
    # pad pin + spring
    pin = cyl(f"{prefix}_Caliper_pad_pin", 0.0025, gap + 2 * T + 0.004, loc=(0, yd, 0.143 + H * 0.15), rot=(90, 0, 0), mat='steel_stainless', n=12)
    parts.append(pin)
    spr = box(f"{prefix}_Caliper_pad_spring", (0.05, gap + 0.004, 0.0012), loc=(0, yd, 0.143 + H * 0.42 + 0.006), mat='steel_stainless')
    parts.append(spr)
    # radial mounting ears + bolts (100 mm centres) on the inner half, pointing to the fork foot
    for mx in (-0.050, 0.050):
        e = box(f"{prefix}_Caliper_mount_ear_{'F' if mx>0 else 'R'}", (0.020, 0.016, 0.022), loc=(mx, yd + side * (gap / 2 + T * 0.6), 0.124), mat='alu_grey_anod', bev=0.004)
        parts.append(e)
        b = bolt(f"{prefix}_Caliper_radial_bolt_{'F' if mx>0 else 'R'}", d=0.010, L=0.035, loc=(mx, yd + side * (gap / 2 + T * 0.6), 0.10), rot=(180, 0, 0), head='allen', mat='bolt_black')
        parts.append(b)
    # bleed nipple + banjo
    bn = cyl(f"{prefix}_Caliper_bleeder", 0.003, 0.014, loc=(0.040, yd - side * (gap / 2 + T * 0.5), 0.143 + H * 0.5), mat='steel_stainless', n=10)
    parts.append(bn)
    bj = cyl(f"{prefix}_Caliper_banjo", 0.0075, 0.012, loc=(-0.035, yd - side * (gap / 2 + T * 0.5), 0.143 + H * 0.52), rot=(0, 0, 0), mat='steel_stainless', n=6)
    parts.append(bj)
    # place: local frame rotated about Y by angle around axle centre
    a = math.radians(angle_deg)
    R = Matrix.Rotation(-(a - math.pi / 2), 4, 'Y')
    for o in parts:
        o.location = R @ Vector(o.location)
        o.rotation_euler.rotate(R.to_euler())
        o.location += root.location
        parent(o, root)
    return root

def rear_disc_and_caliper(centre):
    side = -1
    root = empty("R_DISC_220", centre + Vector((0, side * 0.083, 0)))
    d = drilled_disc("R_Disc_rotor_220", 0.110, 0.078, 0.005, rows=2, holes_per_row=22, hole_r=0.0024)
    d.location = Matrix.Rotation(math.radians(-90), 4, 'X') @ Vector(d.location)
    d.rotation_euler = (math.radians(-90), 0, 0); d.location += root.location; parent(d, root)
    for k in range(5):
        a = 2 * math.pi * k / 5
        b = bolt(f"R_Disc_bolt_{k}", d=0.004, L=0.008, loc=(0, 0, 0), head='allen', mat='bolt_zinc')
        b.location = root.location + Vector((0.068 * math.cos(a), -0.004, 0.068 * math.sin(a)))
        b.rotation_euler = (math.radians(90), 0, 0); parent(b, root)
    # 2-piston Brembo rear caliper on carrier, below/forward of axle
    cr = empty("R_CALIPER_Brembo_2p", centre)
    a = math.radians(-58)
    cx, cz = 0.093 * math.cos(a), 0.093 * math.sin(a)
    cal = box("R_Caliper_body", (0.068, 0.040, 0.034), loc=(cx, side * 0.083, cz), rot=(0, math.degrees(-a) - 90, 0), mat='alu_black_anod', bev=0.006)
    cal.location += centre; parent(cal, cr)
    carrier = box("R_Caliper_carrier_plate", (0.13, 0.008, 0.05), loc=(0.05, side * 0.110, -0.035), rot=(0, 30, 0), mat='alu_cast', bev=0.003)
    carrier.location += centre; parent(carrier, cr)
    return root, cr

def rear_sprocket(centre, chain_y=0.112, teeth=41):
    """41T sprocket (525 pitch 15.875 mm) on cush-drive carrier, left side."""
    pitch = 0.015875
    rp = pitch / (2 * math.sin(math.pi / teeth))
    bm = bmesh.new()
    pts = []
    for k in range(teeth):
        for j, (dr, da) in enumerate([(-0.0055, -0.36), (0.0045, -0.14), (0.0062, 0.0), (0.0045, 0.14), (-0.0055, 0.36)]):
            a = 2 * math.pi * (k + 0.5 + da) / teeth
            pts.append(((rp + dr) * math.cos(a), (rp + dr) * math.sin(a)))
    inner_r = rp - 0.022
    vo = [bm.verts.new((x, y, -0.003)) for x, y in pts]
    vi = [bm.verts.new((inner_r * math.cos(2 * math.pi * i / len(pts)), inner_r * math.sin(2 * math.pi * i / len(pts)), -0.003)) for i in range(len(pts))]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((vi[i], vi[j], vo[j], vo[i]))
    ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, 0, 0.006))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("R_Sprocket_41T"); bm.to_mesh(me); bm.free()
    sp = bpy.data.objects.new("R_Sprocket_41T", me); _link(sp); assign(sp, 'sprocket_alu'); bevel(sp, 0.0006, 1, angle=30)
    sp.rotation_euler = (math.radians(-90), 0, 0); sp.location = centre + Vector((0, chain_y, 0))
    # spider with 5 lightening windows
    web = lathe("R_Sprocket_web", [(0.050, -0.003), (inner_r + 0.001, -0.003), (inner_r + 0.001, 0.003), (0.050, 0.003)], n=60, mat='sprocket_alu', closed=True)
    web.rotation_euler = (math.radians(-90), 0, 0); web.location = sp.location
    cbm = bmesh.new()
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        m = Matrix.Translation(((0.050 + inner_r) / 2 * math.cos(a), (0.050 + inner_r) / 2 * math.sin(a), 0))
        bmesh.ops.create_cone(cbm, cap_ends=True, segments=24, radius1=(inner_r - 0.050) * 0.36, radius2=(inner_r - 0.050) * 0.36, depth=0.02, matrix=m)
    cme = bpy.data.meshes.new("spw"); cbm.to_mesh(cme); cbm.free()
    cut = bpy.data.objects.new("spw_cut", cme); bpy.context.scene.collection.objects.link(cut)
    cut.rotation_euler = web.rotation_euler; cut.location = web.location
    boolean(web, cut, apply=True); bpy.data.objects.remove(cut)
    carrier = lathe("R_Cush_drive_carrier", [(0.020, 0.0), (0.072, 0.0), (0.074, 0.008), (0.060, 0.028), (0.020, 0.028)], n=48, mat='alu_cast', closed=True)
    carrier.rotation_euler = (math.radians(90), 0, 0); carrier.location = centre + Vector((0, chain_y - 0.002, 0))
    nuts = []
    for k in range(5):
        a = 2 * math.pi * k / 5
        n = bolt(f"R_Sprocket_nut_{k}", d=0.006, L=0.004, head='hex', mat='bolt_zinc')
        n.rotation_euler = (math.radians(-90), 0, 0)
        n.location = centre + Vector((0.058 * math.cos(a), chain_y + 0.003, 0.058 * math.sin(a)))
        nuts.append(n)
    return [sp, web, carrier] + nuts, rp

def build(cal=None):
    c = coll("10_WHEELS_BRAKES"); set_coll(c)
    fw = wheel_assembly("F", G.FRONT_AXLE, True)
    rw = wheel_assembly("R", G.REAR_AXLE, False)
    fdl = front_disc("F_L", G.FRONT_AXLE, +1)
    fdr = front_disc("F_R", G.FRONT_AXLE, -1)
    cl = hypure_caliper("F_L", G.FRONT_AXLE, +1, 130)
    cr = hypure_caliper("F_R", G.FRONT_AXLE, -1, 130)
    rd, rc = rear_disc_and_caliper(G.REAR_AXLE)
    spr, rp = rear_sprocket(G.REAR_AXLE)
    return dict(sprocket_rp=rp)
