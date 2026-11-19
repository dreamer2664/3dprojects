"""5-inch TFT dashboard graphic (Race-style layout) — system Python / PIL.
Layout follows the photographed 2026 dash (p_19 / official gallery): dark background, horizontal
rev bar across the top with green active segment, large gear indicator 'N' in a green box in the centre,
speed on the left, data fields on the right. Text uses only generic data (numbers/units), no logos."""
from PIL import Image, ImageDraw, ImageFont
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ASSETS", "textures", "tft_race.png")
W, H = 1600, 960  # 5:3

def font(sz, bold=True):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

im = Image.new("RGB", (W, H), (6, 7, 10)); d = ImageDraw.Draw(im)
# subtle vignette panel
for i in range(40):
    d.rectangle([i, i, W - i, H - i], outline=(8 + i // 6, 9 + i // 6, 13 + i // 5))
# rev bar
x0, x1, y0, y1 = 70, W - 70, 70, 150
segs = 60
for s in range(segs):
    xa = x0 + (x1 - x0) * s / segs; xb = x0 + (x1 - x0) * (s + 0.82) / segs
    if s < 9: col = (40, 220, 90)
    elif s < 48: col = (34, 36, 44)
    elif s < 55: col = (60, 30, 30)
    else: col = (90, 20, 20)
    d.rectangle([xa, y0, xb, y1], fill=col)
for k, lab in enumerate(["2", "4", "6", "8", "10", "12", "14"]):
    xx = x0 + (x1 - x0) * (k * 2 + 2) / 16
    d.text((xx - 15, y1 + 12), lab, font=font(34), fill=(160, 165, 175))
# gear box
d.rounded_rectangle([W / 2 - 150, 300, W / 2 + 150, 680], radius=30, outline=(40, 220, 90), width=10, fill=(8, 30, 14))
d.text((W / 2 - 75, 330), "N", font=font(300), fill=(60, 235, 110))
# speed
d.text((140, 330), "0", font=font(260), fill=(235, 238, 245))
d.text((150, 610), "km/h", font=font(54, False), fill=(150, 155, 165))
# right data column
rows = [("ATC", "3"), ("AWC", "2"), ("AEB", "2"), ("AEM", "1")]
for i, (k, v) in enumerate(rows):
    y = 300 + i * 95
    d.text((W - 520, y), k, font=font(56), fill=(150, 155, 165))
    d.text((W - 240, y), v, font=font(64), fill=(240, 240, 245))
# bottom bar
d.rectangle([60, H - 170, W - 60, H - 168], fill=(40, 42, 50))
d.text((80, H - 140), "RACE", font=font(70), fill=(240, 240, 245))
d.text((520, H - 140), "12:47", font=font(70), fill=(200, 205, 215))
d.text((900, H - 140), "21°C", font=font(70), fill=(200, 205, 215))
d.rectangle([W - 380, H - 132, W - 120, H - 72], outline=(200, 205, 215), width=5)
d.rectangle([W - 372, H - 124, W - 200, H - 80], fill=(200, 205, 215))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
im.save(OUT); print("saved", OUT)
