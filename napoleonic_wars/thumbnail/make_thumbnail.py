"""YouTube thumbnail: 'I AM NAPOLEON - THE NIGHTMARE OF EUROPE'.

Usage: python3 make_thumbnail.py background.jpg out.png
"""
import math
import os
import random
import sys

import cairo
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video"))
import gfx  # noqa: E402
from gfx import (INK, arrow, ellipse, explosion, fill, flag, flames, hexc, mounted, napoleon, poly,  # noqa: E402
                 rrect, smoke, soldier)

W, H = 1920, 1080


def load_bg(path):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x0 = (im.width - W) // 2 + 120  # shift a little so Europe sits left of centre
    x0 = max(0, min(x0, im.width - W))
    im = im.crop((x0, 0, x0 + W, H))
    a = np.asarray(im)
    buf = np.zeros((H, W, 4), dtype=np.uint8)
    buf[..., 0], buf[..., 1], buf[..., 2], buf[..., 3] = a[..., 2], a[..., 1], a[..., 0], 255
    return cairo.ImageSurface.create_for_data(memoryview(buf).cast("B"), cairo.FORMAT_ARGB32, W, H, W * 4), buf, x0, s


def glow_text(c, txt, x, y, size, fill_col, stroke=14, glow=(0.9, 0.05, 0.05), glow_r=26, font="DejaVu Sans"):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    for k in range(glow_r, 0, -3):
        c.move_to(x, y)
        c.text_path(txt)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_line_width(stroke + k * 2)
        c.set_source_rgba(*glow, 0.05)
        c.stroke()
    c.move_to(x + 8, y + 10)
    c.text_path(txt)
    c.set_source_rgba(0, 0, 0, 0.6)
    c.fill()
    c.move_to(x, y)
    c.text_path(txt)
    c.set_line_width(stroke)
    c.set_source_rgba(0.05, 0.03, 0.02, 1)
    c.stroke_preserve()
    if isinstance(fill_col, cairo.Pattern):
        c.set_source(fill_col)
    else:
        c.set_source_rgba(*fill_col)
    c.fill()


def main():
    bg_path, out = sys.argv[1:3]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    bg, _keep, x0, s = load_bg(bg_path)

    # ---- background map, darkened toward the edges
    c.set_source_surface(bg, 0, 0)
    c.paint()
    c.set_source_rgba(0.05, 0.0, 0.0, 0.18)
    c.paint()
    g = cairo.RadialGradient(780, 520, 300, 780, 520, 1350)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.75)
    c.set_source(g)
    c.paint()

    def P(x, y):  # map coords of the source image -> thumbnail
        return x * s - x0, y * s

    paris = P(560, 470)
    # ---- burning cities and battle smoke across Europe
    targets = {"madrid": P(470, 600), "rome": P(690, 590), "vienna": P(780, 470), "berlin": P(740, 400),
               "moscow": P(1080, 330), "warsaw": P(860, 410), "cairo": P(1060, 760)}
    for i, (name, (x, y)) in enumerate(targets.items()):
        smoke(c, x, y - 40, 3.0 + i, n=6, s=1.2, col=(0.15, 0.12, 0.12), rise=110, seed=i, a=0.9)
        flames(c, x, y, 90, 110, 1.3 + i * 0.7, seed=i)
        explosion(c, x, y - 30, 0.25, 0.7)

    # ---- invasion arrows from Paris
    for name, col in (("madrid", "#FFD43B"), ("rome", "#FFD43B"), ("vienna", "#FFD43B"), ("berlin", "#FFD43B"),
                      ("moscow", "#FFD43B"), ("cairo", "#FFD43B")):
        tx, ty = targets[name]
        mx, my = (paris[0] + tx) / 2, (paris[1] + ty) / 2 - 60
        arrow(c, [paris, (mx, my), (tx, ty)], 1.0, col, w=22, head=46)

    # ---- marching army over Europe
    r = random.Random(4)
    cols = [(P(590, 430), P(800, 390)), (P(610, 500), P(820, 470)), (P(600, 560), P(760, 560))]
    for ci, ((ax, ay), (bx, by)) in enumerate(cols):
        n = 8
        for k in range(n):
            u = k / (n - 1)
            x, y = ax + (bx - ax) * u, ay + (by - ay) * u
            for row in range(2):
                soldier(c, x + r.uniform(-5, 5), y + row * 26 + 40, 0.5, "fr", t=0.4 + k, walk=k * 1.3 + row,
                        face=1, arms="musket")
        flag(c, bx + 30, by + 60, 0.3 + ci, "fr", pole=120, w=80, h=52, eagle=True)
    for i, (x, y) in enumerate((P(840, 430), P(860, 520))):
        mounted(c, x, y + 70, 0.55, 1, 1.2 + i, who="cuir", col=("#3A2A22", "#7A5232")[i], gallop=True)

    # ---- red glow behind Napoleon
    g = cairo.RadialGradient(1520, 560, 60, 1520, 560, 620)
    g.add_color_stop_rgba(0, 1, 0.35, 0.1, 0.85)
    g.add_color_stop_rgba(0.5, 0.8, 0.1, 0.05, 0.45)
    g.add_color_stop_rgba(1, 0.5, 0, 0, 0)
    c.set_source(g)
    c.arc(1520, 560, 620, 0, 2 * math.pi)
    c.fill()
    flames(c, 1520, 1100, 900, 300, 2.0, seed=7, a=0.85)

    # ---- giant Napoleon pointing at Europe
    NX, NY, NS = 1530, 1420, 6.6
    napoleon(c, NX, NY, NS, face=-1, arms="point", expr="angry", t=0.5, blink=False, look=1)
    # menacing face: hat shadow, glinting eyes and a sly grin (drawn in the same local frame)
    c.save()
    c.translate(NX, NY)
    c.scale(-NS, NS)
    hy, ex = -138, 10
    # cover the default brows and mouth with skin
    for dx in (ex - 8, ex + 8):
        ellipse(c, dx, hy - 10, 8, 3.6)
        fill(c, gfx.SKIN)
    ellipse(c, ex + 1, hy + 13, 9, 4)
    fill(c, gfx.SKIN)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    # angry brows: inner ends low
    for dx, side in ((ex - 8, 1), (ex + 8, -1)):
        c.move_to(dx - side * 6.5, hy - 15)
        c.line_to(dx + side * 5.5, hy - 7.5)
        c.set_line_width(3.6)
        c.set_source_rgba(*INK)
        c.stroke()
    # sly one-sided smirk
    c.move_to(ex - 5, hy + 15)
    c.curve_to(ex, hy + 16.5, ex + 6, hy + 15, ex + 10, hy + 9.5)
    c.set_line_width(2.6)
    c.stroke()
    # hat shadow over the upper face
    c.save()
    ellipse(c, 0, hy, 28.5, 28.5)
    c.clip()
    sh = cairo.LinearGradient(0, hy - 30, 0, hy + 2)
    sh.add_color_stop_rgba(0, 0, 0, 0, 0.6)
    sh.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(sh)
    c.paint()
    c.restore()
    # glinting red eyes
    for dx in (ex - 8, ex + 8):
        ellipse(c, dx + 1.2, hy - 3.2, 1.3, 1.3)
        fill(c, (1, 0.25, 0.15, 0.95))
    c.restore()

    # ---- titles
    tg = cairo.LinearGradient(0, 90, 0, 230)
    tg.add_color_stop_rgba(0, 1, 0.93, 0.45, 1)
    tg.add_color_stop_rgba(1, 1, 0.68, 0.05, 1)
    glow_text(c, "I AM", 70, 175, 120, tg, stroke=16)
    glow_text(c, "NAPOLEON", 70, 345, 190, tg, stroke=20)

    # banner
    c.save()
    c.translate(40, 860)
    c.rotate(-0.025)
    poly(c, [(0, 0), (1180, 0), (1140, 150), (0, 150)])
    bgrad = cairo.LinearGradient(0, 0, 0, 150)
    bgrad.add_color_stop_rgba(0, 0.85, 0.07, 0.07, 1)
    bgrad.add_color_stop_rgba(1, 0.5, 0.02, 0.02, 1)
    c.set_source(bgrad)
    c.fill_preserve()
    c.set_line_width(8)
    c.set_source_rgba(0.05, 0.02, 0.02, 1)
    c.stroke()
    glow_text(c, "THE NIGHTMARE OF EUROPE", 34, 108, 84, (1, 1, 1, 1), stroke=10, glow=(0, 0, 0), glow_r=8)
    c.restore()

    # ---- embers + grain-free final vignette
    r = random.Random(9)
    for i in range(160):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = r.uniform(1.5, 4.5)
        ellipse(c, x, y, rr, rr)
        c.set_source_rgba(1, r.uniform(0.4, 0.75), 0.15, r.uniform(0.4, 0.9))
        c.fill()
    surf.write_to_png(out)
    Image.open(out).convert("RGB").save(out.rsplit(".", 1)[0] + ".jpg", quality=92)
    print("wrote", out)


if __name__ == "__main__":
    main()
