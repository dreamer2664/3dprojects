#!/usr/bin/env python3
"""Contact sheet of the final Cycles render set for quick review."""
import glob
import os
from PIL import Image, ImageDraw

D = "/home/user/3dprojects/renders/1899-bluthner-grand-piano"
paths = sorted(p for p in glob.glob(os.path.join(D, "[0-9]*.png")))
cols, tw, th = 3, 420, 260
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), (28, 28, 28))
for i, p in enumerate(paths):
    im = Image.open(p).convert("RGB")
    im.thumbnail((tw - 10, th - 26))
    x = (i % cols) * tw + (tw - im.width) // 2
    y = (i // cols) * th + 22
    sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text(((i % cols) * tw + 6, (i // cols) * th + 5),
                               os.path.basename(p), fill="white")
out = os.path.join(D, "CONTACT_SHEET.jpg")
sheet.save(out, quality=88)
print("CONTACT_SHEET", out, len(paths), sheet.size)
