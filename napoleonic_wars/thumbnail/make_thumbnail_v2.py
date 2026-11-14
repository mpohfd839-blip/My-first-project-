"""Thumbnail v2: '1 MAN vs ALL OF EUROPE' - Napoleon on a rearing horse facing Europe's panicking kings.

Usage: python3 make_thumbnail_v2.py background.jpg out.png
"""
import math
import os
import random
import sys

import cairo
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_thumbnail import H, W, glow_text, load_bg  # noqa: E402
import gfx  # noqa: E402
from gfx import (INK, draw_crown, ellipse, explosion, fill, flag, flames, hexc, horse, king, napoleon,  # noqa: E402
                 poly, smoke)


def main():
    bg_path, out = sys.argv[1:3]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    bg, _keep, x0, s = load_bg(bg_path)
    c.set_source_surface(bg, 0, 0)
    c.paint()
    c.set_source_rgba(0.05, 0, 0, 0.25)
    c.paint()
    g = cairo.RadialGradient(800, 560, 280, 800, 560, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.8)
    c.set_source(g)
    c.paint()

    # ---- battle haze behind the kings
    for i, (x, y) in enumerate(((260, 640), (520, 560), (760, 650), (420, 760))):
        smoke(c, x, y, 2 + i, n=6, s=1.5, col=(0.12, 0.1, 0.1), rise=120, seed=i, a=0.75)
        explosion(c, x, y, 0.3, 0.9)
    flames(c, 520, 1090, 1100, 230, 1.7, seed=3, a=0.9)

    # ---- the kings of Europe, panicking, crowns flying off
    kings = [(240, 980, "#EEEDE6", "au"), (480, 1000, "#1F2A44", "pr"), (720, 985, "#2F5A35", "ru"),
             (960, 1005, "#C8322F", "uk")]
    for i, (x, y, robe, fk) in enumerate(kings):
        flag(c, x - 70, y - 300, 1.0 + i, fk, pole=200, w=110, h=72)
    for i, (x, y, robe, fk) in enumerate(kings):
        king(c, x, y, 2.05, robe=robe, coat=robe, hat="none", hair="wig", expr="shock", arms="up", t=0.3 + i,
             blink=False, face=1, look=1)
        c.save()
        c.translate(x + 30 + 18 * i, y - 2.05 * 175 - 70 - 25 * (i % 2))
        c.rotate(0.5 - 0.3 * i)
        draw_crown(c, 0, 0, 2.3)
        c.restore()
        # sweat drops
        for k in range(2):
            ellipse(c, x - 70 + k * 18, y - 2.05 * 150 + k * 22, 7, 11)
            fill(c, (0.6, 0.85, 1, 0.9))

    # ---- glow + Napoleon on a rearing white horse
    g = cairo.RadialGradient(1520, 520, 60, 1520, 520, 700)
    g.add_color_stop_rgba(0, 1, 0.8, 0.3, 0.75)
    g.add_color_stop_rgba(0.45, 0.95, 0.25, 0.05, 0.45)
    g.add_color_stop_rgba(1, 0.5, 0, 0, 0)
    c.set_source(g)
    c.arc(1520, 520, 700, 0, 2 * math.pi)
    c.fill()
    # sun rays behind him
    c.save()
    c.translate(1520, 520)
    for k in range(18):
        a = k * math.pi / 9
        poly(c, [(0, 0), (1400 * math.cos(a - 0.05), 1400 * math.sin(a - 0.05)),
                 (1400 * math.cos(a + 0.05), 1400 * math.sin(a + 0.05))])
        c.set_source_rgba(1, 0.85, 0.4, 0.10)
        c.fill()
    c.restore()

    def rider(cc, rx, ry):
        cc.save()
        cc.translate(rx, ry)
        cc.scale(-1, 1)  # mirror so he faces (and points his sword at) the kings
        napoleon(cc, 0, 0, 1.05, face=1, seated=True, arms="point", item="sword", expr="angry", t=0.5,
                 blink=False, look=1)
        cc.restore()

    horse(c, 1520, 1070, 3.05, -1, "#F4F0E8", 0.0, gallop=False, rider_fn=rider, rear=0.45)

    # ---- titles
    tg = cairo.LinearGradient(0, 40, 0, 300)
    tg.add_color_stop_rgba(0, 1, 0.95, 0.5, 1)
    tg.add_color_stop_rgba(1, 1, 0.66, 0.05, 1)
    glow_text(c, "1 MAN", 60, 270, 250, tg, stroke=22)
    # VS badge
    c.save()
    c.translate(1040, 165)
    c.rotate(-0.12)
    pts = []
    for k in range(16):
        r = 120 if k % 2 == 0 else 88
        a = k * math.pi / 8
        pts.append((r * math.cos(a), r * math.sin(a)))
    poly(c, pts)
    c.set_source_rgba(*hexc("#D62A2A")[:3], 1)
    c.fill_preserve()
    c.set_line_width(8)
    c.set_source_rgba(0.05, 0.02, 0.02, 1)
    c.stroke()
    glow_text(c, "VS", -68, 34, 96, (1, 1, 1, 1), stroke=10, glow=(0, 0, 0), glow_r=4)
    c.restore()

    c.save()
    c.translate(36, 330)
    c.rotate(-0.02)
    poly(c, [(0, 0), (1060, 0), (1020, 140), (0, 140)])
    bgrad = cairo.LinearGradient(0, 0, 0, 140)
    bgrad.add_color_stop_rgba(0, 0.12, 0.12, 0.14, 0.92)
    bgrad.add_color_stop_rgba(1, 0.02, 0.02, 0.03, 0.92)
    c.set_source(bgrad)
    c.fill_preserve()
    c.set_line_width(6)
    c.set_source_rgba(1, 0.75, 0.1, 1)
    c.stroke()
    glow_text(c, "ALL OF EUROPE", 30, 108, 100, (1, 1, 1, 1), stroke=10, glow=(0.9, 0.05, 0.05), glow_r=10)
    c.restore()

    # embers
    r = random.Random(11)
    for i in range(170):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = r.uniform(1.5, 4.5)
        ellipse(c, x, y, rr, rr)
        c.set_source_rgba(1, r.uniform(0.4, 0.8), 0.15, r.uniform(0.4, 0.9))
        c.fill()
    surf.write_to_png(out)
    Image.open(out).convert("RGB").save(out.rsplit(".", 1)[0] + ".jpg", quality=92)
    print("wrote", out)


if __name__ == "__main__":
    main()
