"""Chroma-key the green-screen character images into RGBA cut-outs (cut/*.png)."""
import glob, os
import numpy as np
from PIL import Image, ImageFilter
for f in glob.glob("assets/CHAR_*.jpg") + glob.glob("assets/MASCOT_*.jpg"):
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spill = g - np.maximum(r, b)                      # how "green" a pixel is
    if "virus" in f:   # the virus itself is partly green: key only colours close to pure screen green
        dist = np.sqrt(r ** 2 + (1 - g) ** 2 + b ** 2)
        alpha = np.clip((dist - 0.30) / 0.18, 0, 1)
    else:
        alpha = np.clip(1 - (spill - 0.12) / 0.25, 0, 1)
    # despill: pull green down to the max of red/blue
    g2 = g if "virus" in f else np.minimum(g, np.maximum(r, b) + 0.04)
    rgb = np.stack([r, g2, b], -1)
    al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    # keep only the biggest blob region: remove tiny floating glow dots by opening
    am = np.asarray(al).astype(np.float32) / 255
    big = Image.fromarray((am * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(6))
    am = am * np.clip(np.asarray(big).astype(np.float32) / 255 * 1.6, 0, 1)
    out = np.dstack([rgb * 255, am * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    im = im.crop(im.getbbox())
    name = os.path.basename(f)[:-4]
    im.save(f"cut/{name}.png")
    print(name, im.size)
