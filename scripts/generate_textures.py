#!/usr/bin/env python3
"""Memory-safe authoring of PBR texture sources for the Blüthner rebuild.

The sandbox has 1.9 GB RAM, so all synthesis happens at 2K and is upscaled to
4K/8K with Pillow; the final 8K pore pass is written row-block by row-block.
"""
import gc
import os
import numpy as np
from PIL import Image

OUT = "/home/user/3dprojects/assets/1899-bluthner-grand-piano/textures"
os.makedirs(OUT, exist_ok=True)


def save_rgb(name, arr):
    Image.fromarray(arr.astype(np.uint8), "RGB").save(os.path.join(OUT, name), optimize=True)
    print("saved", name, arr.shape, flush=True)


def save_gray(name, arr):
    Image.fromarray(arr.astype(np.uint8), "L").save(os.path.join(OUT, name), optimize=True)
    print("saved", name, arr.shape, flush=True)


def noise_field(h, w, cell, seed, size=None):
    gh, gw = max(2, h // cell), max(2, w // cell)
    g = np.random.default_rng(seed).random((gh, gw), dtype=np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8), "L")
    target = size or (w, h)
    return np.asarray(im.resize(target, Image.Resampling.BICUBIC), dtype=np.float32) / 255.0


def upscale_rgb(arr, size):
    return np.asarray(Image.fromarray(arr.astype(np.uint8), "RGB").resize(
        size, Image.Resampling.LANCZOS), dtype=np.uint8)


def upscale_gray(arr, size):
    return np.asarray(Image.fromarray(arr.astype(np.uint8), "L").resize(
        size, Image.Resampling.LANCZOS), dtype=np.uint8)


def rosewood():
    h = w = 2048
    warp = noise_field(h, w, 90, 11) - 0.5
    streak = noise_field(h, w, 12, 12) - 0.5
    fine = noise_field(h, w, 3, 13) - 0.5
    yy = np.arange(h, dtype=np.float32)[:, None]
    phase = yy / 18.0 + warp * 9.0
    bands = 0.5 + 0.5 * np.sin(phase * 2 * np.pi)
    bands = np.clip(bands * 0.74 + streak * 0.34 + fine * 0.10, 0, 1)
    pore = fine * 14.0
    col = np.empty((h, w, 3), dtype=np.uint8)
    col[..., 0] = np.clip(48 + bands * 76 + pore, 0, 255)
    col[..., 1] = np.clip(20 + bands * 34 + pore * 0.6, 0, 255)
    col[..., 2] = np.clip(16 + bands * 23 + pore * 0.5, 0, 255)
    save_rgb("_rosewood_color_2k_tmp.png", col)
    del phase, warp, streak, bands
    gc.collect()
    height = (fine * 0.25 + pore / 40.0).astype(np.float32)
    gy, gx = np.gradient(height)
    del height, fine, pore
    gc.collect()
    nx, ny, nz = -gx * 7.0, -gy * 7.0, np.ones_like(gx)
    inv = 1.0 / np.sqrt(nx*nx + ny*ny + nz*nz)
    nrm = np.empty((h, w, 3), dtype=np.uint8)
    nrm[..., 0] = (nx*inv*0.5+0.5)*255
    nrm[..., 1] = (ny*inv*0.5+0.5)*255
    nrm[..., 2] = (nz*inv*0.5+0.5)*255
    save_rgb("rosewood_normal_4k.png", upscale_rgb(nrm, (4096, 4096)))
    del nx, ny, nz, inv, nrm, gx, gy
    gc.collect()
    rough = np.clip(66 + (1.0 - (col[..., 0].astype(np.float32)/130.0)) * 58, 0, 255)
    save_gray("rosewood_rough_4k.png", upscale_gray(rough, (4096, 4096)))
    del rough, yy
    gc.collect()
    save_rgb("rosewood_color_4k.png", upscale_rgb(col, (4096, 4096)))
    del col
    gc.collect()
    # 8K source, written in 256-row blocks to stay inside RAM.
    src = Image.open(os.path.join(OUT, "rosewood_color_4k.png")).convert("RGB")
    big = src.resize((8192, 8192), Image.Resampling.LANCZOS)
    out = Image.new("RGB", (8192, 8192))
    for y0 in range(0, 8192, 256):
        block = np.asarray(big.crop((0, y0, 8192, min(8192, y0+256))), dtype=np.float32)
        n = (np.random.default_rng(15000+y0).random(block.shape[:2], dtype=np.float32)-0.5)*16
        block[..., 0] += n; block[..., 1] += n*0.7; block[..., 2] += n*0.6
        out.paste(Image.fromarray(block.astype(np.uint8), "RGB"), (0, y0))
    out.save(os.path.join(OUT, "rosewood_color_8k_source.png"), optimize=True)
    print("saved rosewood_color_8k_source.png (8192, 8192, 3)", flush=True)
    del src, big, out
    gc.collect()
    os.remove(os.path.join(OUT, "_rosewood_color_2k_tmp.png"))


def spruce():
    h = w = 2048
    warp = noise_field(h, w, 90, 21) - 0.5
    xx = np.arange(w, dtype=np.float32)[None, :]
    lines = 0.5 + 0.5 * np.sin((xx / 9.0 + warp * 8.0) * 2 * np.pi)
    early = np.clip(lines ** 6, 0, 1)
    micro = noise_field(h, w, 3, 22) - 0.5
    col = np.empty((h, w, 3), dtype=np.uint8)
    for c, base in enumerate((186, 154, 108)):
        col[..., c] = np.clip(base + early * (28+2*c) + micro*12, 0, 255)
    save_rgb("spruce_soundboard_color_4k.png", upscale_rgb(col, (4096, 4096)))


def gilt():
    h = w = 1024
    n = noise_field(h, w, 6, 31)
    micro = noise_field(h, w, 2, 32)
    cast = n*0.6 + micro*0.4
    col = np.empty((h, w, 3), dtype=np.uint8)
    col[..., 0] = 148 + cast*74; col[..., 1] = 108 + cast*62; col[..., 2] = 46 + cast*34
    save_rgb("gilt_bronze_color_2k.png", upscale_rgb(col, (2048, 2048)))
    save_gray("gilt_bronze_rough_2k.png", upscale_gray((60+(1-cast)*90).astype(np.uint8), (2048, 2048)))


def simple_maps():
    h = w = 512
    for name, base in [("ivory_key", (218,207,183)), ("ebony_sharp", (24,20,18)),
                       ("felt_hammer", (176,146,104)), ("leather", (72,42,28))]:
        n = noise_field(h, w, 5, 41+len(name)) - 0.5
        m = noise_field(h, w, 2, 61+len(name)) - 0.5
        v = n*18 + m*8
        col = np.empty((h, w, 3), dtype=np.uint8)
        for c, b in enumerate(base): col[..., c] = np.clip(b+v, 0, 255)
        save_rgb(name+"_color_1k.png", upscale_rgb(col, (1024, 1024)))


if __name__ == "__main__":
    rosewood()
    spruce()
    gilt()
    simple_maps()
    print("TEXTURES_DONE", flush=True)
