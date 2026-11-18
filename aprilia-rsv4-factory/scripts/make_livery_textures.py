"""
Livery tracing for the Shakedown Indigo graphics.

Runs with the *system* Python (PIL + numpy + OpenCV), not inside Blender.

Method (documented in DECISIONS.md D-008):
  The official Aprilia studio photographs (research/photos/p_17, p_18, p_15, p_19)
  are classified pixel-by-pixel into the livery's flat paint classes
  (matte black, gloss black, violet, white, light grey, red). Classification
  is restricted to model-space zones where each class legitimately occurs,
  so that reflections on black paint are not mistaken for white decals.
  The result is a clean, lighting-free "decal map" in the photo's own pixel
  space; calibration constants below map model coordinates -> photo pixels
  inside the Blender shader (projection mapping).

Outputs (ASSETS/textures/):
  livery_<view>_albedo.png   flat colours
  livery_<view>_rough.png    roughness (gloss vs matte areas)
"""
import os, json
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = os.path.join(ROOT, "research", "photos")
OUT = os.path.join(ROOT, "ASSETS", "textures")
os.makedirs(OUT, exist_ok=True)

UP = 2  # upsampling factor for smoother decal edges

# Calibration: model (X fwd, Z up) <-> photo pixels.  px = ax + bx*X ; py = az + bz*Z
# p_18 (left side, +Y):  X = (1553 - px)*0.0011816 ; Z = (1137 - py)*0.001143
# p_17 (right side, -Y): X = (px - 384)*0.0012286  ; Z = (1145 - py)*0.001188
# p_15 (front):          Y = (px - 493)*0.00096    ; Z = (1323 - py)*0.00096
# p_19 (top):            X = 1.10 - (py-600)*0.001014 ; Y = (461 - px)*0.00101
CAL = {
    "left":  dict(photo="p_18.jpg", u=("X", 1553.0, -1/0.0011816), v=("Z", 1137.0, -1/0.001143)),
    "right": dict(photo="p_17.jpg", u=("X", 384.0, 1/0.0012286),   v=("Z", 1145.0, -1/0.001188)),
    "front": dict(photo="p_15.jpg", u=("Y", 493.0, 1/0.00096),     v=("Z", 1323.0, -1/0.00096)),
    "top":   dict(photo="p_19.jpg", u=("Y", 461.0, -1/0.00101),    v=("X", 600.0 + 1.10/0.001014, -1/0.001014)),
}

# Model-space zones (X,Z) where white/grey decals are allowed on the side views
SIDE_ZONES = [
    ("side_stripes", (0.66, 1.42), (0.20, 0.70)),
    ("tail",         (-0.26, 0.50), (0.69, 1.06)),
    ("tank_logo",    (0.70, 0.88), (0.900, 0.968)),
    ("rsv4_logo",    (1.13, 1.29), (0.695, 0.775)),
]

PALETTE = {  # sRGB albedo (picked from median of class pixels, then normalised)
    "black":  (16, 16, 18),
    "gblack": (10, 10, 12),
    "violet": (84, 30, 196),
    "white":  (232, 232, 230),
    "lgrey":  (158, 160, 162),
    "red":    (226, 38, 22),
}
ROUGH = {"black": 0.42, "gblack": 0.12, "violet": 0.16, "white": 0.20, "lgrey": 0.22, "red": 0.20}


def to_px(view, axis_val_u, axis_val_v):
    c = CAL[view]
    return c["u"][1] + c["u"][2] * axis_val_u, c["v"][1] + c["v"][2] * axis_val_v


def zone_mask(view, shape):
    m = np.zeros(shape[:2], np.uint8)
    if view in ("left", "right"):
        for _, (x0, x1), (z0, z1) in SIDE_ZONES:
            pa = to_px(view, x0, z0); pb = to_px(view, x1, z1)
            xa, xb = sorted([pa[0], pb[0]]); ya, yb = sorted([pa[1], pb[1]])
            cv2.rectangle(m, (int(xa * UP), int(ya * UP)), (int(xb * UP), int(yb * UP)), 255, -1)
    elif view == "front":
        # nose logo + wing chequer zones
        cv2.rectangle(m, (int(380 * UP), int(470 * UP)), (int(600 * UP), int(560 * UP)), 255, -1)
        cv2.rectangle(m, (0, int(560 * UP)), (int(960 * UP), int(900 * UP)), 255, -1)
    elif view == "top":
        cv2.rectangle(m, (int(180 * UP), int(720 * UP)), (int(330 * UP), int(900 * UP)), 255, -1)
        cv2.rectangle(m, (int(600 * UP), int(720 * UP)), (int(760 * UP), int(900 * UP)), 255, -1)
    return m > 0


def classify(view):
    c = CAL[view]
    bgr = cv2.imread(os.path.join(PH, c["photo"]))
    bgr = cv2.resize(bgr, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    bgr = cv2.bilateralFilter(bgr, 7, 40, 7)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    H = hsv[..., 0] * 2.0; S = hsv[..., 1] / 255.0; V = hsv[..., 2] / 255.0
    zones = zone_mask(view, bgr.shape)
    # studio background: bright, unsaturated and connected to the image border -> excluded
    bg = ((V > 0.86) & (S < 0.10)).astype(np.uint8)
    n, labels = cv2.connectedComponents(bg)
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    bgmask = np.isin(labels, list(border))
    zones = zones & ~bgmask

    cls = np.full(H.shape, "black", dtype=object)
    violet = (H > 245) & (H < 300) & (S > 0.30) & (V > 0.25)
    red = ((H < 18) | (H > 345)) & (S > 0.55) & (V > 0.35)
    white = (S < 0.16) & (V > 0.80) & zones
    lgrey = (S < 0.16) & (V > 0.50) & (V <= 0.80) & zones
    gblack = (S < 0.20) & (V > 0.17) & (V <= 0.50) & zones
    cls[gblack] = "gblack"; cls[lgrey] = "lgrey"; cls[white] = "white"
    cls[violet] = "violet"; cls[red] = "red"

    # integer label image -> mode filter for clean edges
    names = list(PALETTE.keys())
    lab = np.zeros(H.shape, np.uint8)
    for i, n in enumerate(names):
        lab[cls == n] = i
    lab = cv2.medianBlur(lab, 5)

    alb = np.zeros(bgr.shape, np.uint8); rough = np.zeros(H.shape, np.uint8)
    for i, n in enumerate(names):
        m = lab == i
        alb[m] = PALETTE[n][::-1]  # to BGR
        rough[m] = int(ROUGH[n] * 255)
    alb = cv2.GaussianBlur(alb, (3, 3), 0)
    cv2.imwrite(os.path.join(OUT, f"livery_{view}_albedo.png"), alb)
    cv2.imwrite(os.path.join(OUT, f"livery_{view}_rough.png"), rough)
    stats = {n: float((lab == i).mean()) for i, n in enumerate(names)}
    return bgr.shape, stats


if __name__ == "__main__":
    meta = {}
    for v in CAL:
        shp, st = classify(v)
        c = CAL[v]
        meta[v] = dict(photo=c["photo"], width=shp[1] // UP, height=shp[0] // UP, u=c["u"], v=c["v"], stats=st)
        print(v, shp, {k: round(x, 3) for k, x in st.items()})
    json.dump(meta, open(os.path.join(OUT, "livery_calibration.json"), "w"), indent=1)
