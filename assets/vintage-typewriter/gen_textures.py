#!/usr/bin/env python3
"""Generate procedural textures for the Remington MODEL 56 typewriter."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
os.makedirs(TD, exist_ok=True)
random.seed(561956); np.random.seed(561956)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def noise(w, h, lo, hi, blur=0):
    a = np.random.randint(lo, hi + 1, (h, w), dtype=np.uint8)
    img = Image.fromarray(a, 'L')
    if blur: img = img.filter(ImageFilter.GaussianBlur(blur))
    return img

def save(img, name):
    p = os.path.join(TD, name)
    img.save(p)
    print("tex:", name, img.size)

# ---------- 1. enamel roughness (subtle orange-peel) ----------
base = noise(512, 512, 100, 138, blur=2.5)
warr = np.array(base, dtype=np.int16)
warr += np.random.randint(-8, 9, warr.shape, dtype=np.int16)
save(Image.fromarray(np.clip(warr, 70, 165).astype(np.uint8), 'L'), "enamel_rough.png")

# ---------- 2. keycap (Bakelite) roughness: fine scratches ----------
img = Image.new('L', (256, 256), 72)
d = ImageDraw.Draw(img)
for _ in range(260):
    x, y = random.uniform(0, 256), random.uniform(0, 256)
    ln = random.uniform(20, 120); ang = random.uniform(0, math.pi)
    g = random.randint(95, 165)
    d.line([x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln], fill=g, width=1)
img = img.filter(ImageFilter.GaussianBlur(0.6))
save(img, "keycap_rough.png")

# ---------- 3. brushed chrome roughness (horizontal streaks) ----------
a = np.full((512, 512), 30, dtype=np.float32)
for _ in range(2400):
    y = random.randint(0, 511); x0 = random.randint(-80, 512); ln = random.randint(40, 320)
    v = random.uniform(-16, 34)
    a[y, max(0, x0):min(512, x0 + ln)] += v
a = np.clip(a, 8, 110).astype(np.uint8)
save(Image.fromarray(a, 'L'), "chrome_rough.png")

# ---------- 4. rubber roughness ----------
r = noise(256, 256, 190, 224, blur=1.2)
save(r, "rubber_rough.png")

# ---------- 5. ribbon: black/red woven bicolor ----------
W, H = 512, 128
img = Image.new('RGB', (W, H))
px = img.load()
for y in range(H):
    for x in range(W):
        band = y < H // 2  # top black, bottom red
        weave = int(((x * 7 + y * 3) % 9) / 9.0 * 18 + ((x + y) % 4) * 3)
        n = int(np.random.randint(0, 26))
        if band: px[x, y] = (18 + n + weave // 3, 16 + n + weave // 4, 15 + n)
        else:    px[x, y] = (78 + n + weave // 2, 18 + n // 3, 16 + n // 3)
img = img.filter(ImageFilter.GaussianBlur(0.4))
save(img, "ribbon.png")

# ---------- 6. scale ruler (carriage) ----------
W, H = 1024, 96
img = Image.new('RGB', (W, H), (233, 227, 207))
d = ImageDraw.Draw(img)
inc = random.Random(77)
for i in range(W):  # subtle wear speckle
    if inc.random() < 0.10:
        d.point((i, inc.randrange(H)), fill=(198, 192, 172))
for cm in range(0, 27):
    x = 24 + cm * 36
    h = 58 if cm % 5 == 0 else (38 if cm % 1 == 0 else 0)
    d.line([x, 8, x, 8 + h], fill=(40, 34, 26), width=3 if cm % 5 == 0 else 2)
    if cm % 5 == 0:
        f = ImageFont.truetype(MONO_B, 26)
        d.text((x - 9, 62), str(cm), font=f, fill=(40, 34, 26))
    elif cm % 1 == 0:
        for k in (1, 2, 3):
            x2 = x + k * 9
            d.line([x2, 8, x2, 8 + 18], fill=(60, 54, 44), width=1)
d.line([24, 8, 24 + 26 * 36, 8], fill=(40, 34, 26), width=2)
save(img, "scale.png")

# ---------- 7. paper: warm off-white, fibers + typed text ----------
W, H = 1240, 1754
img = Image.new('RGB', (W, H), (239, 233, 216))
# fiber noise
carb = np.asarray(img).astype(np.int16)
for _ in range(5200):
    x, y = random.randint(0, W - 1), random.randint(0, H - 1)
    ln = random.randint(3, 26); ang = random.uniform(0, math.pi)
    g = random.choice([-14, -9, 12, 16])
    for s in range(ln):
        xx, yy = int(x + math.cos(ang) * s), int(y + math.sin(ang) * s)
        if 0 <= xx < W and 0 <= yy < H:
            carb[yy, xx] = np.clip(carb[yy, xx] + g, 0, 255)
# faint vertical chain lines
carb[:, :: 137] -= 5
img = Image.fromarray(np.clip(carb, 0, 255).astype(np.uint8), 'RGB')
# soft edge vignette
vig = Image.new('L', (W, H), 0)
dv = ImageDraw.Draw(vig)
dv.rectangle([0, 0, W, H], fill=26)
dv.rectangle([26, 26, W - 26, H - 26], fill=10)
dv.rectangle([70, 70, W - 70, H - 70], fill=0)
vig = vig.filter(ImageFilter.GaussianBlur(48))
img = Image.composite(Image.new('RGB', (W, H), (196, 188, 168)), img, vig)
d = ImageDraw.Draw(img)

def type_line(text, cx, y, font, ink=(26, 24, 22), alpha=0.92, track=0, blot=True):
    widths = [d.textlength(ch, font=font) for ch in text]
    tot = sum(widths) + track * (len(text) - 1)
    x = cx - tot / 2
    for ch, w in zip(text, widths):
        a = alpha * random.uniform(0.62, 1.0)
        jx, jy = random.uniform(-1.1, 1.1), random.uniform(-1.4, 1.4)
        if ch != ' ':
            lyr = Image.new('RGBA', (int(w) + 26, font.size + 26), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lyr)
            dl.text((13 + jx, 10 + jy), ch, font=font, fill=ink + (int(255 * a),))
            img.paste(lyr, (int(x - 13), int(y - 10)), lyr)
            if blot and random.random() < 0.05:
                d.ellipse([x + w / 2 - 2, y + font.size / 2 + 6, x + w / 2 + 2, y + font.size / 2 + 9],
                          fill=(20, 18, 16, 90))
        x += w + track

type_line("No. 01856", W * 0.78, H * 0.105, ImageFont.truetype(MONO, 34), alpha=0.8)
type_line("REMINGTON MODEL 56", W / 2, H * 0.295, ImageFont.truetype(MONO_B, 63), track=6)
type_line("PORTABLE MANUAL TYPEWRITER", W / 2, H * 0.372, ImageFont.truetype(MONO, 29), alpha=0.85, track=3)
type_line("-  -  -  -  -  -  -  -  -  -  -  -", W / 2, H * 0.435, ImageFont.truetype(MONO, 30), alpha=0.55)
type_line("THE ART OF PRECISION", W / 2, H * 0.525, ImageFont.truetype(MONO_B, 55), track=4)
type_line("ESTABLISHED  MCMLVI", W / 2, H * 0.612, ImageFont.truetype(MONO, 27), ink=(96, 26, 22), alpha=0.9, track=2)
save(img, "paper.png")

# ---------- 8. brass badge: engraved MODEL 56 ----------
W, H = 640, 384
img = Image.new('RGB', (W, H))
d = ImageDraw.Draw(img)
top = np.array([196, 158, 92], dtype=np.float32); bot = np.array([122, 88, 44], dtype=np.float32)
t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
grad = (top[None, None, :] * (1 - t) + bot[None, None, :] * t)
img = Image.fromarray(np.repeat(grad, W, axis=1).astype(np.uint8), 'RGB')
arr = np.asarray(img).astype(np.float32)
for y in range(H):
    for _ in range(28):
        x = random.randint(0, W - 30)
        arr[y, x:x + random.randint(8, 60)] += random.uniform(-9, 9)
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')
d = ImageDraw.Draw(img)
# borders: engraved double line
for off, col, wd in ((16, (64, 44, 20), 4), (26, (235, 205, 140), 2), (30, (64, 44, 20), 2)):
    d.rectangle([off, off, W - off, H - off], outline=col, width=wd)

def eng_text(text, cx, y, font, track=0):
    widths = [d.textlength(c, font=font) for c in text]
    tot = sum(widths) + track * (len(text) - 1)
    x = cx - tot / 2
    for c, w in zip(text, widths):
        if c != ' ':
            d.text((x, y + 2), c, font=font, fill=(238, 210, 150))  # lower highlight
            d.text((x, y), c, font=font, fill=(46, 32, 14))          # engraved dark
        x += w + track

# four-point star (drawn, not font glyph)
def star(cx, cy, r_out, r_in=None):
    r_in = r_in or r_out * 0.38
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    d.polygon(pts, fill=(46, 32, 14))
    d.polygon([(x, y - 1.5) for x, y in pts], outline=(238, 210, 150))

star(W / 2, 55, 15)
eng_text("REMINGTON", W / 2, 116, ImageFont.truetype(SERIF_B, 60), track=5)
eng_text("MODEL 56", W / 2, 238, ImageFont.truetype(SERIF_B, 50), track=13)
save(img, "badge.png")

# ---------- 9. key legends ----------
def legend(name, text, wide=False):
    W, H = (512, 256) if wide else (256, 256)
    img = Image.new('RGB', (W, H), (16, 15, 14))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(SERIF_B, 150 if not wide else 88)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((W - tw) / 2 - bb[0], (H - th) / 2 - bb[1]), text, font=f, fill=(238, 231, 210))
    save(img, f"legend_{name}.png")

for ch in "1234567890-":
    legend("MINUS" if ch == "-" else ch, ch)
legend("BACK", "←")
legend("TAB", "TAB")
for ch in list("QWERTYUIOP") + list("ASDFGHJKL") + list("ZXCVBNM"):
    legend(ch, ch)
legend("LBRACKET", "["); legend("RBRACKET", "]")
legend("SEMI", ";"); legend("QUOTE", "'")
legend("COMMA", ","); legend("PERIOD", "."); legend("SLASH", "/")
legend("RETURN", "RETURN", wide=True)
legend("SHIFT", "SHIFT", wide=True)
legend("TABW", "TAB", wide=True)
legend("BACKW", "←", wide=True)
print("done")
