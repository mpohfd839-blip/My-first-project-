"""WWI additions to the cartoon library: uniforms, hats, vehicles, trenches, maps, photo presentation."""
import math
import os
import random
import sys

import cairo
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "napoleonic_wars", "video"))
import gfx  # noqa: E402
from gfx import *  # noqa: E402,F401,F403

KHAKI = hexc("#8A7D52")
FELD = hexc("#6E7563")

# ------------------------------------------------------------------ hats & facial hair
_orig_hat = gfx.draw_hat


def _hat_part(c, part, hy, plume, t):
    top = hy - 26
    ex = 7
    if part == "brodie":
        ellipse(c, 0, top + 8, 38, 8)
        fill(c, hexc("#5E5A3A"))
        ellipse(c, 0, top + 2, 22, 13)
        fill(c, hexc("#6A6644"))
    elif part == "pickel":
        ellipse(c, 0, top + 4, 26, 18)
        fill(c, hexc("#1E1C1A"))
        seg(c, (-26, top + 10), (26, top + 10), 4, hexc("#1E1C1A"))
        poly(c, [(-5, top - 12), (5, top - 12), (0, top - 36)])
        fill(c, GOLD if plume == "gold" else hexc("#B8B8B8"))
        ellipse(c, 12, top + 2, 6, 7)
        fill(c, GOLD)
    elif part == "stahl":
        c.move_to(-30, top + 18)
        c.curve_to(-32, top - 22, 30, top - 22, 30, top + 6)
        c.line_to(22, top + 10)
        c.line_to(-22, top + 20)
        c.close_path()
        fill(c, hexc("#5C6050"))
        ellipse(c, 22, top - 2, 3, 3)
        fill(c, hexc("#3A3E32"))
    elif part == "adrian":
        ellipse(c, 0, top + 8, 34, 7)
        fill(c, hexc("#62738A"))
        ellipse(c, 0, top + 1, 24, 15)
        fill(c, hexc("#6E7F96"))
        seg(c, (-10, top - 12), (12, top - 12), 5, hexc("#56677E"))
    elif part == "kepi":
        poly(c, [(-18, top + 8), (18, top + 8), (22, top - 18), (-14, top - 14)])
        fill(c, hexc("#C8322F"))
        seg(c, (-18, top + 4), (18, top + 4), 7, hexc("#24346E"))
        seg(c, (6, top + 9), (30, top + 12), 4, BLACK)
    elif part == "peaked":
        col = hexc(plume) if plume and plume.startswith("#") else hexc("#7E7A55")
        ellipse(c, 0, top - 4, 30, 9)
        fill(c, col)
        rrect(c, -20, top - 4, 40, 12, 3)
        fill(c, shade(col, -0.15))
        seg(c, (-20, top + 4), (20, top + 4), 3, hexc("#C8322F") if plume == "#3A3A3A" else shade(col, -0.35))
        seg(c, (6, top + 10), (30, top + 12), 4, BLACK)
    elif part == "slouch":
        ellipse(c, 0, top + 6, 40, 8)
        fill(c, hexc("#8A7A58"))
        rrect(c, -18, top - 16, 36, 22, 9)
        fill(c, hexc("#8A7A58"))
        seg(c, (-18, top + 2), (18, top + 2), 4, hexc("#5A4A32"))
        poly(c, [(-40, top + 6), (-22, top - 22), (-16, top + 4)])
        fill(c, hexc("#7A6A48"))
    elif part == "pagri":
        for k in range(3):
            ellipse(c, 0, top + 4 - k * 9, 28 - k * 3, 12)
            fill(c, shade(hexc("#B8A878"), -0.06 * k))
        poly(c, [(8, top - 10), (16, top - 30), (20, top - 8)])
        fill(c, hexc("#A89868"))
    elif part == "alpine":
        ellipse(c, 0, top + 6, 32, 7)
        fill(c, hexc("#5E6650"))
        rrect(c, -16, top - 14, 32, 22, 8)
        fill(c, hexc("#5E6650"))
        c.move_to(-14, top - 6)
        c.curve_to(-30, top - 40, -36, top - 50, -50, top - 56)
        c.set_line_width(4)
        c.set_source_rgba(0.15, 0.15, 0.15, 1)
        c.stroke()
    elif part == "kalpak":
        rrect(c, -22, top - 24, 44, 34, 10)
        fill(c, hexc("#2A2420"))
    elif part == "flycap":
        ellipse(c, 0, top + 8, 30, 24)
        fill(c, hexc("#5A3A22"))
        seg(c, (-26, hy - 12), (26, hy - 12), 6, hexc("#3A2A1A"))
        for dx in (-2, 18):
            ellipse(c, dx, hy - 18, 8, 6)
            fill(c, hexc("#9AC0D0"))
    elif part == "arab":
        c.move_to(-34, hy + 36)
        c.curve_to(-40, hy - 10, -30, top - 18, 0, top - 18)
        c.curve_to(30, top - 18, 34, hy - 30, 30, hy - 26)
        c.line_to(22, hy - 20)
        c.curve_to(20, top - 6, -20, top - 6, -22, hy)
        c.line_to(-22, hy + 40)
        c.close_path()
        fill(c, hexc("#F2EEE6"))
        seg(c, (-28, top - 4), (28, top - 4), 6, GOLD)
    elif part == "plumehelm":
        ellipse(c, 0, top + 2, 24, 18)
        fill(c, hexc("#2A2A2A"))
        for k in range(7):
            ellipse(c, -6 + k * 3, top - 20 - (k % 3) * 4, 5, 14, rot=-0.4 + k * 0.12)
            fill(c, hexc("#3E8A4A"))
    elif part == "widehat":
        ellipse(c, 0, top + 4, 46, 10)
        fill(c, hexc("#F4EFE6"))
        ellipse(c, 0, top - 6, 24, 14)
        fill(c, hexc("#F4EFE6"))
        for k in range(3):
            ellipse(c, -14 + k * 12, top - 14, 7, 7)
            fill(c, hexc("#E8A0B0"))
    elif part == "bowler":
        ellipse(c, 0, top + 6, 30, 6)
        fill(c, BLACK)
        ellipse(c, 0, top - 4, 20, 16)
        fill(c, BLACK)
    elif part == "gasmask":
        ellipse(c, 0, hy, 32, 34)
        fill(c, hexc("#8A8468"))
        for dx in (ex - 8, ex + 9):
            ellipse(c, dx, hy - 4, 8, 8)
            fill_ol(c, hexc("#C8D6CC"), INK, 2.5)
        seg(c, (ex + 2, hy + 14), (ex + 6, hy + 34), 7, hexc("#5A5644"))
    elif part == "mup":
        for sx in (-1, 1):
            c.move_to(ex, hy + 9)
            c.curve_to(ex + sx * 8, hy + 14, ex + sx * 16, hy + 10, ex + sx * 18, hy + 1)
            c.set_line_width(4)
            c.set_source_rgba(*hexc("#3A2A1A"))
            c.stroke()
    elif part == "mous":
        seg(c, (ex - 8, hy + 9), (ex + 9, hy + 9), 5, hexc("#4A3828"))
    elif part == "wmous":
        ellipse(c, ex, hy + 10, 14, 5)
        fill(c, hexc("#EDEDED"))
    elif part == "bigmous":
        for sx in (-1, 1):
            ellipse(c, ex + sx * 9, hy + 10, 11, 5, rot=sx * 0.2)
            fill(c, hexc("#4A3828"))
    elif part == "beard":
        c.move_to(-14, hy + 4)
        c.curve_to(-12, hy + 34, 26, hy + 34, 28, hy + 4)
        c.line_to(22, hy + 14)
        c.curve_to(12, hy + 18, 0, hy + 18, -6, hy + 12)
        c.close_path()
        fill(c, hexc("#6A4A2E"))
        seg(c, (ex - 7, hy + 9), (ex + 8, hy + 9), 4, hexc("#6A4A2E"))
    elif part == "goatee":
        poly(c, [(ex - 6, hy + 17), (ex + 8, hy + 17), (ex + 1, hy + 32)])
        fill(c, hexc("#8A5A32"))
        seg(c, (ex - 6, hy + 9), (ex + 8, hy + 9), 3.5, hexc("#8A5A32"))
    elif part == "glasses":
        for dx in (ex - 8, ex + 8):
            ellipse(c, dx, hy - 2, 7, 6)
            c.set_line_width(1.6)
            c.set_source_rgba(*INK)
            c.stroke()
    elif part == "bowtie":
        poly(c, [(-8, hy + 30), (8, hy + 36), (8, hy + 24)])
        fill(c, INK)
        poly(c, [(8, hy + 30), (24, hy + 36), (24, hy + 24)])
        fill(c, INK)
    else:
        _orig_hat(c, part, hy, plume, t)


def draw_hat(c, hat, hy, plume, t):
    if not hat:
        return
    for part in str(hat).split("+"):
        _hat_part(c, part, hy, plume, t)


gfx.draw_hat = draw_hat

gfx.UNIFORMS.update({
    "tommy": dict(coat="#8A7D52", trou="#7E7248", hat="brodie", belts=False, sash=None),
    "hun14": dict(coat="#7A806A", trou="#5E6352", hat="pickel", belts=False),
    "hun": dict(coat="#6E7563", trou="#5E6352", hat="stahl", belts=False),
    "poilu14": dict(coat="#2D3E7A", trou="#C8322F", hat="kepi", belts=False),
    "poilu": dict(coat="#7D93A8", trou="#6E849A", hat="adrian", belts=False),
    "ivan": dict(coat="#7E7A55", trou="#6A6648", hat="peaked", plume="#7E7A55", belts=False),
    "sepoy": dict(coat="#9A8A5A", trou="#9A8A5A", hat="pagri+mous", belts=False, skin=hexc("#C99470")),
    "doughboy": dict(coat="#6B6A44", trou="#6B6A44", hat="brodie", belts=False),
    "anzac": dict(coat="#8A7D52", trou="#7E7248", hat="slouch", belts=False),
    "ott": dict(coat="#8E8458", trou="#7E7448", hat="pagri", belts=False),
    "alpini": dict(coat="#7A7E6A", trou="#6A6E5A", hat="alpine", belts=False),
    "gasman": dict(coat="#8A7D52", trou="#7E7248", hat="gasmask+brodie", belts=False),
    "hungas": dict(coat="#6E7563", trou="#5E6352", hat="gasmask+stahl", belts=False),
    "arabf": dict(coat="#E9E1D0", trou="#E9E1D0", hat="arab", belts=False, sash="#8A3A2A",
                  skin=hexc("#C99470")),
})


# ------------------------------------------------------------------ named characters
def char(c, who, x, y, s=1.0, **kw):
    P = {
        "ff": dict(coat="#8FB4D8", trou="#1E2A3A", hat="plumehelm+mup", epaulettes=True, hair="short",
                   expr="proud"),
        "princip": dict(coat="#2A2A2E", trou="#2A2A2E", hat="none", hair="short", hair_col="#1E1612",
                        expr="stern", waist="#F2EEE6"),
        "kaiser": dict(coat="#5E6A5A", trou="#3A3E36", hat="pickel+mup", plume="gold", epaulettes=True,
                       expr="stern"),
        "tsar": dict(coat="#7E7A55", trou="#3A3A3A", hat="none+beard", hair="short", hair_col="#6A4A2E",
                     epaulettes=True, expr="sad"),
        "franzj": dict(coat="#EEEDE6", trou="#C8322F", hat="none+wmous", hair="bald", hair_col="#DDD",
                       epaulettes=True, expr="stern"),
        "churchill": dict(coat="#2A2A33", trou="#2A2A33", hat="none+bowtie", hair="bald", hair_col="#C08A5A",
                          waist="#2A2A33", expr="smirk"),
        "lenin": dict(coat="#3A3A3A", trou="#2A2A2A", hat="none+goatee", hair="bald", hair_col="#8A5A32",
                      expr="shout"),
        "wilson": dict(coat="#2A2A33", trou="#2A2A33", hat="none+glasses", hair="short", hair_col="#8A8A8A",
                       waist="#F2EEE6", expr="stern"),
        "lawrence": dict(coat="#F2EEE6", trou="#F2EEE6", hat="arab", robe="#F2EEE6", expr="proud",
                         sash="#C9A23A"),
        "redbaron": dict(coat="#4A3A2A", trou="#4A3A2A", hat="flycap", expr="smirk"),
        "hindenburg": dict(coat="#6E7563", trou="#3A3E36", hat="peaked+wmous", plume="#6E7563", epaulettes=True,
                           expr="stern"),
        "ludendorff": dict(coat="#6E7563", trou="#3A3E36", hat="peaked+mous", plume="#6E7563", epaulettes=True,
                           expr="angry"),
        "kemal": dict(coat="#8E8458", trou="#7E7448", hat="kalpak+mous", epaulettes=True, expr="stern"),
        "kitchener": dict(coat="#8A7D52", trou="#7E7248", hat="peaked+bigmous", plume="#8A7D52",
                          epaulettes=True, expr="stern"),
        "brusilov": dict(coat="#7E7A55", trou="#3A3A3A", hat="peaked+wmous", plume="#7E7A55", epaulettes=True,
                         expr="proud"),
        "falkenhayn": dict(coat="#6E7563", trou="#3A3E36", hat="pickel+mous", epaulettes=True, expr="smirk"),
        "khudadad": dict(coat="#9A8A5A", trou="#9A8A5A", hat="pagri+mous", skin=hexc("#C99470"), expr="proud"),
        "gunther": dict(coat="#6B6A44", trou="#6B6A44", hat="brodie", expr="stern"),
        "mccrae": dict(coat="#8A7D52", trou="#7E7248", hat="peaked+mous", plume="#8A7D52", expr="sad"),
        "nurse": dict(coat="#F4F2EC", dress="#F4F2EC", hat="bonnet", hair="bun", expr="neutral"),
        "worker": dict(coat="#7A5A3A", dress="#6A4A3A", hat="bonnet", hair="bun", expr="neutral"),
        "sophie": dict(coat="#F4EFE6", dress="#F4EFE6", hat="widehat", hair="bun", expr="happy"),
        "pilot": dict(coat="#4A3A2A", trou="#4A3A2A", hat="flycap", expr="stern"),
        "gentleman": dict(coat="#2A2A33", trou="#2A2A33", hat="bowler", hair="short", waist="#F2EEE6",
                          expr="neutral"),
        "officer": dict(coat="#8A7D52", trou="#7E7248", hat="peaked+mous", plume="#8A7D52", expr="stern",
                        epaulettes=True),
    }[who]
    d = dict(P)
    d.update(kw)
    person(c, x, y, s, **d)


# ------------------------------------------------------------------ battlefield pieces
def barbed_wire(c, x0, x1, y, s=1.0, col=(0.25, 0.22, 0.2, 0.9)):
    n = int((x1 - x0) / (90 * s)) + 1
    for i in range(n + 1):
        x = x0 + i * 90 * s
        seg(c, (x, y), (x + 4 * s, y - 44 * s), 4 * s, hexc("#5A4030"))
    c.set_line_width(1.6 * s)
    c.set_source_rgba(*col)
    for row in range(3):
        c.move_to(x0, y - 12 * s - row * 12 * s)
        for i in range(int((x1 - x0) / (15 * s))):
            c.line_to(x0 + i * 15 * s, y - 12 * s - row * 12 * s + (5 if i % 2 else -5) * s)
        c.stroke()


def crater(c, x, y, rx, water=True):
    ellipse(c, x, y, rx, rx * 0.28)
    fill(c, hexc("#4E3E2A"))
    ellipse(c, x, y + rx * 0.04, rx * 0.8, rx * 0.2)
    fill(c, hexc("#6E7E86") if water else hexc("#3E2E1E"))


def stump(c, x, y, s=1.0):
    poly(c, [(x - 8 * s, y), (x - 5 * s, y - 70 * s), (x - 12 * s, y - 92 * s), (x + 2 * s, y - 80 * s),
             (x + 6 * s, y - 104 * s), (x + 8 * s, y)])
    fill(c, hexc("#3E3226"))


def nomansland(c, t, skyk="grey", horizon=400, seed=3, wire=True, wet=True):
    sky(c, skyk, horizon + 60)
    if skyk == "night":
        stars(c, t, 30)
    clouds(c, t, n=5, col=(0.55, 0.55, 0.58, 0.7) if skyk != "night" else (0.2, 0.2, 0.3, 0.6), seed=seed)
    c.set_source(vgrad(c, horizon, H, hexc("#7A6448"), hexc("#4E3E2A")))
    c.rectangle(0, horizon, W, H)
    c.fill()
    r = random.Random(seed)
    for i in range(16):
        y = r.uniform(horizon + 15, H - 20)
        crater(c, r.uniform(0, W), y, r.uniform(30, 90) * (0.4 + (y - horizon) / (H - horizon)), wet)
    for i in range(7):
        y = r.uniform(horizon + 5, horizon + 120)
        stump(c, r.uniform(0, W), y, r.uniform(0.5, 1.0))
    if wire:
        barbed_wire(c, -20, W + 20, horizon + 90, 0.8)


def trench(c, t, skyk="grey", wet=True, night=False, ladders=0, snow=False, seed=2):
    nomansland(c, t, "night" if night else skyk, horizon=250, seed=seed)
    if snow:
        c.set_source_rgba(1, 1, 1, 0.75)
        c.rectangle(0, 250, W, 200)
        c.fill()
    # back wall with plank revetment
    c.set_source(vgrad(c, 400, 680, hexc("#6A5236"), hexc("#4A3826")))
    c.rectangle(0, 400, W, 290)
    c.fill()
    for k in range(9):
        y = 430 + k * 28
        seg(c, (0, y), (W, y), 3, (0.25, 0.17, 0.1, 0.5))
    for k in range(0, W, 160):
        seg(c, (k, 410), (k, 680), 10, hexc("#5A4028"))
    # sandbag parapet
    r = random.Random(seed)
    for row in range(3):
        for k in range(-1, 18):
            x = k * 76 + (row % 2) * 38 + r.uniform(-4, 4)
            rrect(c, x, 360 + row * 22, 74, 26, 11)
            fill_ol(c, hexc("#B8A27A" if not snow else "#E8EAEC"), hexc("#7A6A48"), 1.5)
    for i in range(ladders):
        x = 200 + i * 360
        seg(c, (x, 690), (x + 50, 360), 7, hexc("#7A5A3A"))
        seg(c, (x + 40, 690), (x + 90, 360), 7, hexc("#7A5A3A"))
        for k in range(8):
            yy = 660 - k * 40
            seg(c, (x + 5 + k * 6.3, yy), (x + 45 + k * 6.3, yy), 5, hexc("#7A5A3A"))
    # duckboards + water
    rrect(c, 0, 680, W, 40, 0)
    fill(c, hexc("#3E3226"))
    if wet:
        c.set_source_rgba(0.45, 0.5, 0.52, 0.7)
        c.rectangle(0, 690, W, 30)
        c.fill()
    for k in range(0, W, 46):
        rrect(c, k, 682, 38, 10, 2)
        fill(c, hexc("#8A6A48"))


def shell_burst(c, x, y, t, period=3.0, phase=0.0, s=1.0):
    ph = ((t + phase) % period) / period
    if ph < 0.35:
        k = ph / 0.35
        if ph < 0.06:
            ellipse(c, x, y - 20 * s, 70 * s, 40 * s)
            fill(c, (1, 0.85, 0.4, 0.9 * (1 - ph / 0.06)))
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * 0.22
            r = 160 * s * smooth(k)
            ellipse(c, x + math.cos(a) * r * 0.6, y + math.sin(a) * r, 18 * s * (1 + k), 18 * s * (1 + k))
            c.set_source_rgba(0.3, 0.24, 0.18, 0.85 * (1 - k))
            c.fill()
    smoke(c, x, y - 60 * s, t + phase, n=4, s=0.9 * s, col=(0.45, 0.42, 0.4), rise=80, seed=int(x) % 97)


def gas_cloud(c, t, x_front, y=560, a=0.6):
    r = random.Random(7)
    for i in range(40):
        x = x_front - r.uniform(0, 1200) + math.sin(t * 0.5 + i) * 20
        yy = y + r.uniform(-140, 140)
        rr = r.uniform(70, 150)
        ellipse(c, x, yy, rr * 1.4, rr * 0.6)
        c.set_source_rgba(0.72, 0.78, 0.32, a * r.uniform(0.3, 0.6))
        c.fill()


def machine_gun(c, x, y, s=1.0, face=1, t=0.0, fire=True):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    for dx in (-40, 0, 30):
        seg(c, (0, -40), (dx, 0), 5, hexc("#3A3A3A"))
    rrect(c, -30, -62, 110, 22, 8)
    fill_ol(c, hexc("#4A4E44"), w=2)
    seg(c, (80, -51), (110, -51), 6, hexc("#2A2A2A"))
    rrect(c, -10, -40, 22, 30, 4)
    fill(c, hexc("#7A5A32"))
    c.restore()
    if fire and (t * 12) % 1 < 0.5:
        ellipse(c, x + face * 118 * s, y - 51 * s, 14 * s, 9 * s)
        fill(c, (1, 0.85, 0.3, 0.95))


def tank(c, x, y, s=1.0, face=1, t=0.0, col="#7A7650"):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    hull = [(-170, -10), (-150, -120), (90, -120), (180, -10), (150, 0), (-150, 0)]
    poly(c, hull)
    fill_ol(c, hexc("#3A3626"), w=3)
    # moving treads
    off = (t * 40) % 24
    c.save()
    poly(c, hull)
    c.clip()
    for k in range(-10, 20):
        seg(c, (-180 + k * 24 + off, -130), (-180 + k * 24 + off, 10), 4, hexc("#55503A"))
    c.restore()
    rrect(c, -120, -100, 220, 80, 10)
    fill_ol(c, hexc(col), w=2)
    rrect(c, -40, -80, 70, 50, 8)
    fill_ol(c, shade(hexc(col), -0.15), w=2)
    seg(c, (20, -56), (80, -62), 9, hexc("#2A2A22"))
    for k in range(8):
        ellipse(c, -110 + k * 28, -92, 2.5, 2.5)
        fill(c, hexc("#4A4630"))
    for k in range(6):
        ellipse(c, -120 + k * 48, -6, 13, 13)
        fill_ol(c, hexc("#2A2620"), w=2)
    c.restore()
    smoke(c, x - face * 150 * s, y - 120 * s, t, n=3, s=0.5 * s, col=(0.3, 0.3, 0.3), rise=60, seed=5)


def biplane(c, x, y, s=1.0, face=1, t=0.0, col="#C8322F", tri=False, mark="cross"):
    c.save()
    c.translate(x, y + 6 * math.sin(t * 1.3))
    c.scale(s * face, s)
    wing = shade(hexc(col), -0.08)
    rows = (-46, -18, 10) if tri else (-40, 6)
    for wy in rows[:-1]:
        rrect(c, -70, wy, 150, 12, 5)
        fill_ol(c, wing, w=1.5)
    for wx in (-50, 50):
        seg(c, (wx, rows[0] + 6), (wx, rows[-1] + 6), 2.5, INK)
    # fuselage
    c.move_to(-130, -2)
    c.curve_to(-60, -24, 60, -26, 92, -10)
    c.line_to(92, 12)
    c.curve_to(40, 18, -60, 14, -130, 6)
    c.close_path()
    fill_ol(c, hexc(col), w=2)
    poly(c, [(-130, -2), (-150, -30), (-118, -6)])
    fill_ol(c, hexc(col), w=1.5)
    rrect(c, -70, rows[-1], 150, 12, 5)
    fill_ol(c, wing, w=1.5)
    ellipse(c, 10, -14, 14, 9)
    fill(c, INK)
    # markings
    if mark == "cross":
        poly(c, [(-112, -6), (-98, -6), (-98, -18), (-90, -18), (-90, -6), (-76, -6), (-76, 2), (-90, 2), (-90, 14),
                 (-98, 14), (-98, 2), (-112, 2)])
        fill_ol(c, BLACK, WHITE, 2)
    else:
        for r, cc in ((10, "#24418F"), (6.5, "#F4F1EA"), (3, "#C8322F")):
            ellipse(c, -94, -2, r, r)
            fill(c, hexc(cc))
    # propeller
    ellipse(c, 98, 0, 5, 34 * abs(math.sin(t * 40)) + 4)
    fill(c, (0.2, 0.2, 0.2, 0.5))
    ellipse(c, 98, 0, 6, 6)
    fill(c, INK)
    for wx in (0, 30):
        seg(c, (wx + 10, 14), (wx, 34), 2.5, INK)
    ellipse(c, 10, 36, 7, 7)
    fill(c, INK)
    ellipse(c, 34, 36, 7, 7)
    fill(c, INK)
    c.restore()


def zeppelin(c, x, y, s=1.0, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    ellipse(c, 0, 0, 280, 60)
    c.set_source(vgrad(c, -60, 60, hexc("#C9CCCF"), hexc("#7A7E84")))
    c.fill()
    for k in range(-6, 7):
        seg(c, (k * 40, -56 + abs(k) * 1.5), (k * 40, 56 - abs(k) * 1.5), 1.5, (0.3, 0.3, 0.35, 0.4))
    poly(c, [(-250, -10), (-300, -60), (-270, -6)])
    fill(c, hexc("#8A8E94"))
    poly(c, [(-250, 10), (-300, 60), (-270, 6)])
    fill(c, hexc("#8A8E94"))
    rrect(c, -40, 56, 80, 20, 6)
    fill_ol(c, hexc("#5A5E64"), w=2)
    c.restore()


def uboat(c, x, y, s=1.0, face=1, t=0.0):
    c.save()
    c.translate(x, y + 3 * math.sin(t * 1.4))
    c.scale(s * face, s)
    c.move_to(-260, 0)
    c.curve_to(-200, -30, 200, -30, 280, -4)
    c.line_to(260, 14)
    c.curve_to(150, 24, -200, 24, -260, 0)
    fill_ol(c, hexc("#5E6670"), w=2)
    poly(c, [(-40, -22), (-30, -80), (50, -80), (70, -22)])
    fill_ol(c, hexc("#6A727C"), w=2)
    seg(c, (10, -80), (14, -140), 4, hexc("#3A3E44"))
    seg(c, (14, -140), (28, -140), 4, hexc("#3A3E44"))
    seg(c, (120, -26), (170, -40), 6, hexc("#3A3E44"))
    c.restore()


def liner(c, x, y, s=1.0, t=0.0, sink=0.0, funnels=4):
    c.save()
    c.translate(x, y + sink * 120)
    c.rotate(sink * 0.22)
    c.scale(s, s)
    c.move_to(-340, -60)
    c.line_to(360, -60)
    c.curve_to(350, -20, 330, 10, 300, 14)
    c.line_to(-300, 14)
    c.curve_to(-330, 0, -340, -30, -340, -60)
    fill_ol(c, hexc("#1E1E22"), w=2)
    rrect(c, -280, -100, 560, 42, 4)
    fill_ol(c, hexc("#F2EEE6"), w=2)
    for k in range(18):
        ellipse(c, -260 + k * 30, -80, 5, 5)
        fill(c, hexc("#4A5A72"))
    for k in range(funnels):
        fx = -170 + k * 110
        rrect(c, fx, -200, 46, 104, 4)
        fill_ol(c, hexc("#B8442E"), w=2)
        rrect(c, fx, -200, 46, 22, 4)
        fill(c, BLACK)
    c.restore()
    for k in range(funnels):
        fx = x + (-147 + k * 110) * s
        smoke(c, fx, y - 220 * s + sink * 120, t + k, n=4, s=0.8 * s, col=(0.3, 0.3, 0.32), rise=90, seed=k)


def dreadnought(c, x, y, s=1.0, face=1, t=0.0, fire=False, phase=0.0):
    c.save()
    c.translate(x, y + 3 * math.sin(t + x * 0.01))
    c.scale(s * face, s)
    c.move_to(-320, -40)
    c.line_to(330, -40)
    c.line_to(380, -54)
    c.curve_to(360, -10, 340, 10, 300, 14)
    c.line_to(-300, 14)
    c.curve_to(-330, 0, -330, -20, -320, -40)
    fill_ol(c, hexc("#6E747A"), w=2)
    rrect(c, -120, -110, 240, 70, 4)
    fill_ol(c, hexc("#7E848A"), w=2)
    rrect(c, -30, -170, 60, 60, 4)
    fill_ol(c, hexc("#868C92"), w=2)
    for fx in (-80, 60):
        rrect(c, fx, -190, 36, 82, 4)
        fill_ol(c, hexc("#5E646A"), w=2)
    for tx in (-250, -170, 170, 250):
        rrect(c, tx - 30, -70, 60, 30, 10)
        fill_ol(c, hexc("#5E646A"), w=2)
        seg(c, (tx, -58), (tx + 70 * (1 if tx > 0 else -1), -64), 7, hexc("#3A3E44"))
    seg(c, (0, -170), (0, -260), 5, hexc("#4A4E54"))
    c.restore()
    smoke(c, x - 62 * s * face, y - 200 * s, t, n=4, s=0.9 * s, col=(0.25, 0.25, 0.27), rise=100, seed=3)
    if fire:
        for k, tx in enumerate((-250, -170, 170, 250)):
            muzzle(c, x + face * (tx + 80 * (1 if tx > 0 else -1)) * s, y - 64 * s, t, period=2.4,
                   phase=k * 0.3 + phase, s=s * 2, face=face if tx > 0 else -face)


def old_car(c, x, y, s=1.0, face=1, t=0.0, col="#2A2A2E", riders=None, moving=True):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    if riders:
        riders(c)
    poly(c, [(-150, -40), (-140, -96), (-40, -96), (-20, -60), (110, -60), (150, -40), (150, -12), (-150, -12)])
    fill_ol(c, hexc(col), w=2)
    seg(c, (-148, -60), (150, -52), 3, GOLD)
    ellipse(c, 150, -48, 9, 9)
    fill(c, hexc("#F7E8A8"))
    for wx in (-90, 90):
        ellipse(c, wx, -10, 32, 32)
        fill(c, BLACK)
        ellipse(c, wx, -10, 20, 20)
        fill(c, hexc("#8A8A8A"))
        c.save()
        c.translate(wx, -10)
        c.rotate(t * 6 if moving else 0)
        for k in range(6):
            c.rotate(math.pi / 3)
            seg(c, (0, 0), (0, 18), 2.5, INK)
        c.restore()
    c.restore()


def train(c, x, y, s=1.0, face=1, t=0.0, cars=3, heads=True, col="#2A3A2E"):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    rrect(c, 0, -120, 200, 90, 10)
    fill_ol(c, hexc("#1E1E1E"), w=2)
    rrect(c, -60, -150, 80, 120, 6)
    fill_ol(c, hexc("#2A2A2A"), w=2)
    rrect(c, 160, -170, 26, 50, 4)
    fill(c, hexc("#1E1E1E"))
    poly(c, [(200, -40), (240, -10), (200, -10)])
    fill(c, hexc("#5A5A5A"))
    for wx in (30, 90, 150):
        ellipse(c, wx, -18, 22, 22)
        fill_ol(c, hexc("#B8442E"), INK, 3)
    for k in range(cars):
        cx = -80 - (k + 1) * 230
        rrect(c, cx, -140, 220, 110, 6)
        fill_ol(c, hexc(col), w=2)
        for j in range(5):
            rrect(c, cx + 14 + j * 42, -124, 28, 30, 3)
            fill(c, hexc("#F2E2B0"))
            if heads:
                ellipse(c, cx + 28 + j * 42, -104, 8, 8)
                fill(c, SKIN)
        for wx in (cx + 40, cx + 180):
            ellipse(c, wx, -20, 18, 18)
            fill(c, INK)
    c.restore()
    smoke(c, x + face * 173 * s, y - 190 * s, t, n=6, s=1.2 * s, col=(0.85, 0.85, 0.85), rise=140, seed=8)


def big_gun(c, x, y, s=1.0, face=1, t=0.0, fire=True, period=3.0, rail=False):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ph = (t % period) / period
    rec = -16 * math.exp(-ph * 18) if fire else 0
    if rail:
        rrect(c, -220, -60, 380, 50, 6)
        fill_ol(c, hexc("#4A4E44"), w=2)
        for wx in range(-200, 160, 50):
            ellipse(c, wx, -6, 16, 16)
            fill(c, INK)
    c.save()
    c.translate(rec, 0)
    c.rotate(-0.55 if not rail else -0.45)
    rrect(c, -60, -70, 340 if rail else 240, 34, 12)
    fill_ol(c, hexc("#4E5244"), w=2)
    c.restore()
    if not rail:
        for wx in (-30, 50):
            ellipse(c, wx + rec, -30, 34, 34)
            fill_ol(c, hexc("#6A4A2E"), INK, 3)
    c.restore()
    if fire and ph < 0.1:
        k = 1 - ph / 0.1
        tip = (x + face * (math.cos(-0.55) * 230 * s), y - 50 * s + math.sin(-0.55) * 230 * s)
        ellipse(c, tip[0], tip[1], 70 * s * k + 10, 40 * s * k + 6)
        fill(c, (1, 0.85, 0.4, 0.95 * k))
    smoke(c, x + face * 180 * s, y - 220 * s, t, n=5, s=1.4 * s, col=(0.8, 0.8, 0.78), rise=120, seed=4)


def poppies(c, y0, y1, t, n=140, seed=3):
    r = random.Random(seed)
    for i in range(n):
        y = r.uniform(y0, y1)
        k = 0.4 + (y - y0) / (y1 - y0)
        x = r.uniform(0, W)
        sw = math.sin(t * 1.5 + i) * 3 * k
        seg(c, (x, y + 30 * k), (x + sw, y), 2.5 * k, hexc("#3E7A3E"))
        for a in range(4):
            ang = a * math.pi / 2 + i
            ellipse(c, x + sw + math.cos(ang) * 6 * k, y + math.sin(ang) * 6 * k, 8 * k, 6 * k, rot=ang)
            fill(c, hexc("#D62A2A"))
        ellipse(c, x + sw, y, 3 * k, 3 * k)
        fill(c, INK)


def clock_face(c, x, y, r, hh, mm):
    ellipse(c, x, y, r + 10, r + 10)
    fill(c, hexc("#5A3A22"))
    ellipse(c, x, y, r, r)
    fill_ol(c, hexc("#F4EEDC"), INK, 3)
    for k in range(12):
        a = k * math.pi / 6
        seg(c, (x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82),
            (x + math.sin(a) * r * 0.94, y - math.cos(a) * r * 0.94), 5 if k % 3 == 0 else 2.5, INK)
    am = mm / 60 * 2 * math.pi
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    seg(c, (x, y), (x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5), 8, INK)
    seg(c, (x, y), (x + math.sin(am) * r * 0.8, y - math.cos(am) * r * 0.8), 5, INK)
    ellipse(c, x, y, 7, 7)
    fill(c, RED)


def domino(c, x, y, ang, kind, s=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    rrect(c, -22, -150, 44, 150, 6)
    fill_ol(c, hexc("#F2EEE6"), INK, 3)
    flag(c, -16, -40, 0, kind, pole=1, w=32, h=22, wave=0)
    for k in range(3):
        ellipse(c, 0, -120 + k * 18, 4, 4)
        fill(c, INK)
    c.restore()


def camel(c, x, y, s=1.0, face=1, t=0.0, rider=True):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ph = t * 7
    for i, lx in enumerate((-50, -34, 34, 50)):
        sw = math.sin(ph + i * 1.6) * 16
        seg(c, (lx, -90), (lx + sw, -4), 10, hexc("#B88A52") if i % 2 else hexc("#A87A42"))
    ellipse(c, 0, -110, 70, 30)
    fill(c, hexc("#C99A5E"))
    ellipse(c, -10, -140, 30, 26)
    fill(c, hexc("#C99A5E"))
    poly(c, [(50, -120), (86, -190), (100, -180), (70, -104)])
    fill(c, hexc("#C99A5E"))
    ellipse(c, 104, -188, 22, 11)
    fill(c, hexc("#C99A5E"))
    ellipse(c, 104, -192, 2.5, 2.5)
    fill(c, INK)
    if rider:
        person(c, -6, -150, 0.7, coat="#E9E1D0", trou="#E9E1D0", hat="arab", seated=True, t=t, arms="aim",
               sash="#8A3A2A", skin=hexc("#C99470"))
    c.restore()


def pigeon(c, x, y, s=1.0, face=1, t=0.0, flying=True):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ellipse(c, 0, 0, 34, 20)
    fill(c, hexc("#8A929C"))
    ellipse(c, 30, -16, 14, 13)
    fill(c, hexc("#7A828C"))
    ellipse(c, 24, -4, 10, 7)
    fill(c, hexc("#6A9A8A"))
    poly(c, [(42, -16), (54, -12), (42, -10)])
    fill(c, hexc("#E8C46A"))
    ellipse(c, 34, -19, 2.5, 2.5)
    fill(c, INK)
    poly(c, [(-30, -4), (-56, -14), (-56, 8)])
    fill(c, hexc("#5E666E"))
    fl = math.sin(t * 18) if flying else -0.3
    poly(c, [(-10, -10), (-30, -10 - 50 * fl), (16, -12)])
    fill(c, hexc("#6E7680"))
    rrect(c, 2, 16, 8, 12, 3)
    fill(c, hexc("#C9CED6"))
    c.restore()


def hospital(c, t, n=6, night=False):
    interior(c, t, wall="#E6DFCF", floor=("#B8AE98", "#9A907A"), window=True, night=night)
    for k in range(n):
        x = 120 + k * 200
        rrect(c, x, 560, 160, 40, 6)
        fill_ol(c, hexc("#F4F2EC"), hexc("#8A8A8A"), 2)
        seg(c, (x, 600), (x, 650), 5, hexc("#6A6A6A"))
        seg(c, (x + 160, 600), (x + 160, 650), 5, hexc("#6A6A6A"))
        ellipse(c, x + 30, 552, 18, 14)
        fill(c, SKIN)
        ellipse(c, x + 26, 540, 18, 8)
        fill(c, hexc("#F4F2EC"))


# ------------------------------------------------------------------ WWI map
WLAND = dict(gfx.LAND)
WLAND["ottoman"] = [(902, 482), (1060, 462), (1150, 520), (1080, 590), (900, 580), (872, 540)]
WLAND["serbia"] = [(742, 448), (790, 440), (800, 480), (760, 494)]
WLABELS = {"britain": "BRITAIN", "france": "FRANCE", "iberia": "SPAIN", "italy": "ITALY", "germany": "GERMANY",
           "austria": "AUSTRIA-HUNGARY", "russia": "RUSSIA", "ottoman": "OTTOMAN\nEMPIRE", "lowlands": "BELGIUM",
           "serbia": "SERBIA", "africa": "NORTH AFRICA · MIDDLE EAST"}
ENTENTE = "#9CC48A"
CENTRAL = "#C9A06A"


def ww1map(c, t, colors=None, labels=True, glow=None, base=None):
    old_land, old_labels = gfx.LAND, gfx.LABELS
    gfx.LAND, gfx.LABELS = WLAND, WLABELS
    cols = {"germany": "#EAD9B0", "prussia": "#EAD9B0", "poland": "#EAD9B0"}
    if base == "blocs":
        cols.update({"britain": ENTENTE, "ireland": ENTENTE, "france": ENTENTE, "russia": ENTENTE,
                     "poland": ENTENTE, "germany": CENTRAL, "prussia": CENTRAL, "austria": CENTRAL})
    cols.update(colors or {})
    if "germany" in cols:
        cols.setdefault("prussia", cols["germany"])
    try:
        europe(c, t, colors=cols, labels=labels, glow=glow)
    finally:
        gfx.LAND, gfx.LABELS = old_land, old_labels


def wcentroid(name):
    pts = WLAND[name]
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def pulse_dot(c, x, y, t, col="#C8322F"):
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        ellipse(c, x, y, 10 + 50 * ph, 10 + 50 * ph)
        c.set_line_width(3)
        c.set_source_rgba(*hexc(col)[:3], 1 - ph)
        c.stroke()
    ellipse(c, x, y, 9, 9)
    fill_ol(c, hexc(col), WHITE, 2.5)


# ------------------------------------------------------------------ photos
_IMG = {}
IMG_DIR = None


def load_img(n):
    if n not in _IMG:
        from PIL import Image
        im = Image.open(os.path.join(IMG_DIR, f"{n:02d}.jpg")).convert("RGB")
        # keep enough resolution for zooming at 1280x720
        im.thumbnail((2000, 2000))
        a = np.asarray(im)
        h, w, _ = a.shape
        buf = np.zeros((h, w, 4), dtype=np.uint8)
        buf[..., 0] = a[..., 2]
        buf[..., 1] = a[..., 1]
        buf[..., 2] = a[..., 0]
        buf[..., 3] = 255
        surf = cairo.ImageSurface.create_for_data(memoryview(buf).cast("B"), cairo.FORMAT_ARGB32, w, h, w * 4)
        _IMG[n] = (surf, buf, w, h)
        if len(_IMG) > 12:
            _IMG.pop(next(iter(_IMG)))
    s, _, w, h = _IMG[n]
    return s, w, h


def paint_img(c, n, x, y, w, h, zoom=1.0, fx=0.5, fy=0.5, alpha=1.0):
    """Cover-fit image n into rect (x,y,w,h); zoom>1 crops in around (fx,fy)."""
    surf, iw, ih = load_img(n)
    sc = max(w / iw, h / ih) * zoom
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    cx = x + w / 2 - (fx - 0.5) * (iw * sc - w)
    cy = y + h / 2 - (fy - 0.5) * (ih * sc - h)
    c.translate(cx - iw * sc / 2, cy - ih * sc / 2)
    c.scale(sc, sc)
    c.set_source_surface(surf, 0, 0)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(alpha)
    c.restore()


def photo_overlay(c, kind, t, u):
    if not kind:
        return
    for k in kind.split("+"):
        if k == "smoke":
            smoke_bank(c, 520, t, a=0.28, seed=5, col=(0.85, 0.83, 0.8))
            smoke_bank(c, 200, t * 0.7, a=0.12, seed=9, col=(0.85, 0.83, 0.8))
        elif k == "rain":
            rain(c, t, n=140)
        elif k == "snow":
            snowfall(c, t, n=180)
        elif k == "gas":
            gas_cloud(c, t, 300 + 900 * u, 560, a=0.45)
        elif k == "fog":
            fog(c, 0.5, 300, 720, t)
        elif k == "flash":
            ph = (t % 2.7) / 2.7
            if ph < 0.08:
                tint(c, (1, 0.9, 0.6), 0.35 * (1 - ph / 0.08))
        elif k == "embers":
            r = random.Random(4)
            for i in range(50):
                ph = (t * r.uniform(0.1, 0.3) + r.random()) % 1
                x = r.uniform(0, W) + math.sin(t + i) * 20
                ellipse(c, x, H - ph * H, 2.2, 2.2)
                c.set_source_rgba(1, 0.6, 0.2, (1 - ph) * 0.8)
                c.fill()
        elif k == "search":
            for i, base in enumerate((300, 640, 1000)):
                a = -math.pi / 2 + 0.5 * math.sin(t * 0.5 + i * 2)
                poly(c, [(base, H), (base + math.cos(a - 0.05) * 1200, H + math.sin(a - 0.05) * 1200),
                         (base + math.cos(a + 0.05) * 1200, H + math.sin(a + 0.05) * 1200)])
                c.set_source_rgba(1, 1, 0.9, 0.12)
                c.fill()
        elif k == "sea":
            for i in range(6):
                y = 500 + i * 36 + math.sin(t + i) * 4
                c.set_source_rgba(1, 1, 1, 0.05)
                c.rectangle(0, y, W, 6)
                c.fill()
        elif k == "light":
            g = cairo.RadialGradient(W * 0.75, 100, 20, W * 0.75, 100, 700)
            g.add_color_stop_rgba(0, 1, 0.9, 0.7, 0.18 + 0.05 * math.sin(t * 2))
            g.add_color_stop_rgba(1, 1, 0.9, 0.7, 0)
            c.set_source(g)
            c.paint()


def specks(c, t, amount=1.0, seed=0):
    r = random.Random(int(t * 24) * 7 + seed)
    for i in range(int(10 * amount)):
        ellipse(c, r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 2.2), r.uniform(0.6, 2.2))
        c.set_source_rgba(0.1, 0.08, 0.05, r.uniform(0.2, 0.6))
        c.fill()
    if r.random() < 0.25 * amount:
        x = r.uniform(0, W)
        c.set_line_width(1.2)
        c.set_source_rgba(0.95, 0.92, 0.85, 0.25)
        c.move_to(x, 0)
        c.line_to(x + r.uniform(-6, 6), H)
        c.stroke()


def desk_bg(c, t):
    c.set_source(vgrad(c, 0, H, hexc("#6A4A30"), hexc("#4A3220")))
    c.paint()
    for k in range(0, H, 60):
        seg(c, (0, k + 30), (W, k + 26), 2, (0.25, 0.15, 0.08, 0.35))
    # props: compass, map corner, pen
    poly(c, [(900, 470), (1280, 430), (1280, 720), (960, 720)])
    fill(c, hexc("#E6D6AE"))
    c.set_line_width(2)
    c.set_source_rgba(0.5, 0.4, 0.3, 0.5)
    for k in range(6):
        c.move_to(920 + k * 50, 470 - k * 6)
        c.line_to(970 + k * 52, 720)
    c.stroke()
    ellipse(c, 150, 600, 60, 60)
    fill_ol(c, hexc("#C9A23A"), hexc("#7A5A1A"), 4)
    ellipse(c, 150, 600, 46, 46)
    fill(c, hexc("#F4EEDC"))
    seg(c, (150, 600), (150 + 30 * math.cos(t * 0.3), 600 - 30 * math.sin(t * 0.3)), 4, RED)
    seg(c, (40, 200), (240, 120), 10, hexc("#2A2A2A"))
    seg(c, (240, 120), (262, 112), 4, GOLD)


def board_bg(c, t):
    c.set_source(vgrad(c, 0, H, hexc("#B8875A"), hexc("#9A6E46")))
    c.paint()
    r = random.Random(3)
    for i in range(400):
        ellipse(c, r.uniform(0, W), r.uniform(0, H), 2, 2)
        c.set_source_rgba(0.4, 0.25, 0.12, 0.3)
        c.fill()
    for (x, y) in ((120, 120), (1150, 140), (160, 600), (1120, 600)):
        rrect(c, x - 60, y - 40, 120, 80, 2)
        fill_ol(c, hexc("#F2E8D0"), w=1)
        ellipse(c, x, y - 34, 7, 7)
        fill(c, RED)
    c.set_line_width(2.5)
    c.set_source_rgba(0.75, 0.1, 0.1, 0.8)
    c.move_to(120, 86)
    c.line_to(640, 360)
    c.line_to(1150, 106)
    c.stroke()


def photo_print(c, n, x, y, w, h, rot, u, t, zoom=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    rrect(c, -w / 2 + 10, -h / 2 + 14, w + 28, h + 70, 4)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.fill()
    rrect(c, -w / 2 - 14, -h / 2 - 14, w + 28, h + 70, 3)
    fill(c, hexc("#F4EFE2"))
    paint_img(c, n, -w / 2, -h / 2, w, h, zoom=zoom + 0.06 * u)
    for tx, ta in ((-w / 2 + 20, -0.6), (w / 2 - 20, 0.6)):
        c.save()
        c.translate(tx, -h / 2 - 10)
        c.rotate(ta)
        rrect(c, -36, -12, 72, 24, 2)
        c.set_source_rgba(0.95, 0.9, 0.7, 0.75)
        c.fill()
        c.restore()
    c.restore()


def gold_frame(c, n, x, y, w, h, u, nameplate=None):
    rrect(c, x - 30, y - 30, w + 60, h + 60, 6)
    c.set_source(vgrad(c, y - 30, y + h + 30, hexc("#E9C46A"), hexc("#9A7414")))
    c.fill()
    rrect(c, x - 14, y - 14, w + 28, h + 28, 4)
    fill(c, hexc("#7A5A14"))
    paint_img(c, n, x, y, w, h, zoom=1.05 + 0.08 * u, fy=0.35)
    if nameplate:
        c.select_font_face("DejaVu Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(22)
        e = c.text_extents(nameplate)
        bw = e.x_advance + 40
        rrect(c, x + w / 2 - bw / 2, y + h + 44, bw, 40, 4)
        c.set_source(vgrad(c, y + h + 44, y + h + 84, hexc("#E9C46A"), hexc("#B8901E")))
        c.fill()
        c.move_to(x + w / 2 - e.x_advance / 2, y + h + 71)
        c.set_source_rgba(0.2, 0.14, 0.05, 1)
        c.show_text(nameplate)


def map_legend(c, items, u):
    a = smooth(u * 4)
    if a <= 0:
        return
    c.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(22)
    wd = max(c.text_extents(lbl).x_advance for lbl, _ in items) + 80
    hh = 20 + 40 * len(items)
    x, y = W - wd - 40, 120
    rrect(c, x, y, wd, hh, 12)
    c.set_source_rgba(0.12, 0.09, 0.06, 0.72 * a)
    c.fill()
    for i, (lbl, col) in enumerate(items):
        rrect(c, x + 18, y + 18 + i * 40, 28, 24, 4)
        c.set_source_rgba(*hexc(col)[:3], a)
        c.fill()
        c.move_to(x + 58, y + 38 + i * 40)
        c.set_source_rgba(1, 0.96, 0.88, a)
        c.show_text(lbl)
