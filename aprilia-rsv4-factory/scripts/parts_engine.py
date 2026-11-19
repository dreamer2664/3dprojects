"""65° V4 engine: monobloc crankcase, banks, heads/cam covers (magnesium),
throttle bodies, airbox, clutch/alternator covers, water pump, starter.
Internals unverifiable -> plausible construction (documented in DECISIONS)."""
import math
from mathutils import Vector
from lib import *
import geom as G

COLL = "50_ENGINE"
CR = G.CRANK

def _bank(front, c):
    s = 'F' if front else 'R'
    d = G.bank_dir(front)
    side = Vector((d.z, 0, -d.x))            # across the bank (horizontal-ish)
    def P(t): return CR + d * t
    # crankcase mouth
    # cylinder block
    def prof(t):
        w = 0.360; h = 0.125 - 0.015 * t
        return rrect(w, h, 0.02, 3)
    secs = sweep_sections([P(0.10), P(0.175), P(0.235)], prof, up=Vector((0, 0, 1)) if front else Vector((0, 0, 1)))
    o = loft(f"Eng_block_{s}", secs, mat='engine_black'); bevel(o, 0.004, 2); wnormal(o)
    # head + cam cover
    def profh(t):
        return rrect(0.352, 0.105, 0.022, 3)
    secs = sweep_sections([P(0.235), P(0.30)], profh)
    o = loft(f"Eng_head_{s}", secs, mat='engine_black'); bevel(o, 0.004, 2); wnormal(o)
    def profc(t):
        return rrect(0.320, 0.085 - 0.02 * t, 0.028, 4)
    secs = sweep_sections([P(0.30), P(0.345)], profc)
    o = loft(f"Eng_camcover_{s}", secs, mat='magnesium'); bevel(o, 0.006, 2); wnormal(o)
    # cooling grooves on block
    for i in range(3):
        t = 0.13 + i * 0.033
        o = loft(f"Eng_block_fin_{s}_{i}", sweep_sections([P(t), P(t + 0.004)], lambda u: rrect(0.366, 0.118, 0.02, 2)), mat='engine_black')
    # cam cover bolts
    up = P(0.346)
    for yy in (-0.13, 0, 0.13):
        cyl(f"Eng_cambolt_{s}", 0.005, 0.008, loc=tuple(up + Vector((0, yy, 0)) + d * 0.002), mat='bolt_zinc', n=10, c=c)
    # spark plug / coil sticks on cam cover
    for yy in (-0.132, -0.044, 0.044, 0.132):
        cyl(f"Eng_coil_{s}", 0.011, 0.03, loc=tuple(P(0.348) + Vector((0, yy, 0))), rot=(0, 0, 0), mat='plastic_black', n=12, c=c)
    # exhaust port stubs on the outer face of the head
    ports = []
    for yy in (-0.132, -0.044, 0.044, 0.132):
        base = P(0.27) + Vector((0, yy, 0)) + side * 0.055
        tip = base + (side * 0.9 + Vector((0, 0, -0.45))).normalized() * 0.05
        rod(f"Eng_port_{s}", base, tip, 0.0205, 'header_tint', n=14, c=c)
        ports.append((tuple(tip), tuple((side * 0.85 + Vector((0, 0, -0.6))).normalized())))
    return ports

def build(ctx):
    c = coll(COLL)
    # ---- crankcase (monobloc): upper + lower + sump
    box("Eng_case_upper", (0.30, 0.31, 0.16), (0.655, 0, 0.50), mat='engine_black', bev=0.02, c=c)
    box("Eng_case_lower", (0.34, 0.33, 0.14), (0.645, 0, 0.385), mat='engine_black', bev=0.02, c=c)
    lathe("Eng_sump", [(0.10, 0.0), (0.19, 0.0), (0.20, 0.05), (0.185, 0.09), (0.10, 0.09)], n=24,
          loc=(0.63, 0, 0.225), rot=(0, 90, 0), mat='magnesium', closed=True, c=c)
    # parting ribs
    box("Eng_case_rib", (0.345, 0.335, 0.012), (0.645, 0, 0.445), mat='engine_black', bev=0.004, c=c)
    # crank ends
    cyl("Eng_crank_L", 0.045, 0.012, loc=(CR.x, 0.166, CR.z), rot=(90, 0, 0), mat='engine_black', n=28, c=c)
    cyl("Eng_crank_R", 0.045, 0.012, loc=(CR.x, -0.166, CR.z), rot=(90, 0, 0), mat='engine_black', n=28, c=c)
    # clutch cover (right) - big magnesium casting with bolt ring
    lathe("Eng_clutch_cover", [(0.055, -0.014), (0.115, -0.012), (0.125, -0.002), (0.125, 0.010), (0.10, 0.016), (0.055, 0.016)],
          n=40, loc=(0.585, -0.170, 0.435), rot=(90, 0, 0), mat='engine_black', closed=True, c=c)
    for i in range(10):
        a = 2 * math.pi * i / 10
        bolt(f"Eng_clutch_bolt_{i}", d=0.006, L=0.012, head='allen', mat='bolt_ti', c=c,
             loc=(0.585 + 0.115 * math.cos(a), -0.186, 0.435 + 0.115 * math.sin(a)), rot=(90, 0, 0))
    cyl("Eng_clutch_slave", 0.026, 0.030, loc=(0.545, -0.183, 0.475), rot=(90, 0, 0), mat='alu_black_anod', n=24, c=c)
    # alternator cover (left)
    lathe("Eng_alt_cover", [(0.05, -0.010), (0.095, -0.008), (0.102, 0.0), (0.095, 0.008), (0.05, 0.010)],
          n=36, loc=(0.665, 0.168, 0.45), rot=(90, 0, 0), mat='engine_black', closed=True, c=c)
    # front sprocket cover (left)
    box("Eng_sprocket_cover", (0.15, 0.025, 0.17), (0.505, 0.150, 0.405), rot=(0, -15, 0), mat='engine_black', bev=0.02, c=c)
    # banks
    ctx['exh_front'] = _bank(True, c)
    ctx['exh_rear'] = _bank(False, c)
    # gearbox output shaft (for chain module)
    ctx['front_sprocket'] = (0.508, 0.0, 0.408)
    cyl("Eng_output_shaft", 0.016, 0.05, loc=(0.508, 0.15, 0.408), rot=(90, 0, 0), mat='steel_stainless', n=18, c=c)
    # starter motor
    cyl("Eng_starter", 0.032, 0.11, loc=(0.615, -0.02, 0.545), rot=(0, 90, 0), mat='engine_black', n=20, c=c)
    # ---- throttle bodies (52 mm) in the V + injectors
    for i, yy in enumerate((-0.132, -0.044, 0.044, 0.132)):
        p0 = Vector((0.700, yy, 0.615)); p1 = Vector((0.735, yy, 0.735))
        rod(f"Eng_throttle_{i}", p0, p1, 0.026, 'alu_black_anod', n=20, c=c)
        rod(f"Eng_trumpet_{i}", p1, p1 + Vector((0.02, 0, 0.075)), 0.024, 'plastic_black', n=18, r2=0.028, c=c)
    box("Eng_throttle_rail", (0.03, 0.33, 0.03), (0.72, 0, 0.70), mat='alu_black_anod', bev=0.005, c=c)
    # ---- airbox above
    box("Airbox", (0.36, 0.24, 0.15), (0.815, 0, 0.795), mat='plastic_black', bev=0.03, c=c)
    rod("Airbox_snorkel", (0.955, 0, 0.83), (1.10, 0, 0.87), 0.052, 'plastic_black', n=24, c=c)
    # ---- water pump + oil filter
    cyl("Eng_waterpump", 0.038, 0.045, loc=(0.795, -0.10, 0.40), rot=(90, 0, 0), mat='engine_black', n=24, c=c)
    cyl("Eng_oilfilter", 0.030, 0.07, loc=(0.80, 0.06, 0.335), rot=(0, 0, 0), mat='paint_black_gloss', n=20, c=c)
    # oil cooler lines stub
    rod("Eng_oil_line1", (0.72, 0.10, 0.33), (0.95, 0.09, 0.35), 0.009, 'hose_rubber', n=10, c=c)
    return {}
