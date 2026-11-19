"""Post-render QC: composite ortho side renders over the calibrated photos.
Render camera (render.py ortho_left/right): centre (0.72, 0.575), ortho_scale 2.35 across width.
Photo p_18: px = 1553 - X/0.0011816 ; py = 1137 - Z/0.001143.
Derived: px_photo = -50.4 + 1.2430*px_render ; py_photo = -8.1 + 1.2850*py_render."""
from PIL import Image
import glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REND = os.path.join(ROOT, 'RENDERS')
OUT = os.path.expanduser('~/work/qc_final'); os.makedirs(OUT, exist_ok=True)

def newest(pat):
    fs = sorted(glob.glob(os.path.join(REND, pat)))
    return fs[-1] if fs else None

def overlay(render_pat, photo_path, out):
    r = newest(render_pat)
    if not r:
        print('missing', render_pat); return
    ph = Image.open(photo_path).convert('RGB')
    im = Image.open(r).convert('RGB')
    W, H = im.size
    im2 = im.resize((int(W * 1.2430), int(H * 1.2850)), Image.LANCZOS)
    ov = Image.new('RGB', ph.size, (255, 255, 255))
    ov.paste(im2, (-50, -8))
    Image.blend(ph, ov, 0.5).save(out)
    print('wrote', out)

overlay('*left-orthographic*', os.path.join(ROOT, 'research', 'photos', 'p_18.jpg'),
        os.path.join(OUT, 'qc_left_overlay.png'))
