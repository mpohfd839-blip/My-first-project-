"""Tesla-specific motion graphics."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from core import W, H, PAL, font, ease, ease_out, stroke, circle, arc_pts, glow_layer, polyline_partial, CINZEL9, CINZEL7, GARAI, MONO
import arts as A
from arts import layer, finish, col, person, draw_map, proj_eq, BYNAME, WORLD


# ------------------------------------------------------------------ lightning
def bolt_pts(x0, y0, x1, y1, rnd, gen=6, disp=0.28):
    pts = [(x0, y0), (x1, y1)]
    d = math.hypot(x1 - x0, y1 - y0) * disp
    for g in range(gen):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            nx, ny = -(b[1] - a[1]), (b[0] - a[0])
            nl = math.hypot(nx, ny) or 1
            off = rnd.uniform(-d, d)
            new += [(mx + nx / nl * off, my + ny / nl * off), b]
        pts = new
        d *= 0.55
    return pts


def bolt(d, x0, y0, x1, y1, rnd, core=(255, 255, 255, 255), outer=(140, 210, 255, 200), w=5, branches=3):
    pts = bolt_pts(x0, y0, x1, y1, rnd)
    d.line(pts, fill=outer, width=int(w * 3), joint="curve")
    d.line(pts, fill=core, width=int(w), joint="curve")
    for k in range(branches):
        i = rnd.randint(len(pts) // 5, len(pts) - 2)
        bx, by = pts[i]
        ang = math.atan2(y1 - y0, x1 - x0) + rnd.uniform(-1.0, 1.0)
        L = math.hypot(x1 - x0, y1 - y0) * rnd.uniform(0.15, 0.35)
        bp = bolt_pts(bx, by, bx + math.cos(ang) * L, by + math.sin(ang) * L, rnd, 4)
        d.line(bp, fill=outer[:3] + (140,), width=int(w * 1.6), joint="curve")
        d.line(bp, fill=core[:3] + (200,), width=max(1, int(w * 0.5)), joint="curve")


def bolt_burst(d, cx, cy, t, n=5, R=420, seed=0, outer=(140, 210, 255, 200), rate=8):
    rnd = random.Random(int(t * rate) * 31 + seed)
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = R * rnd.uniform(0.5, 1.0)
        bolt(d, cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8, rnd, outer=outer, w=4, branches=2)


def flash(img, t, period=1.7, strength=90):
    ph = (t % period)
    if ph < 0.12:
        ov = Image.new("RGBA", (W, H), (220, 230, 255, int(strength * (1 - ph / 0.12))))
        img.alpha_composite(ov)


# ------------------------------------------------------------------ props
def mountains(d, c, y=820):
    pts = [(900, y), (1000, y - 160), (1080, y - 90), (1200, y - 280), (1320, y - 150), (1420, y - 240), (1560, y - 120), (1680, y - 300), (1800, y - 160), (1920, y - 220), (1920, y)]
    d.line(pts, fill=c, width=4, joint="curve")


def coil(d, cx, base, s, c, acc):
    w = 70 * s
    hgt = 360 * s
    d.rectangle([cx - w, base - hgt, cx + w, base], outline=c, width=4)
    for k in range(int(hgt / (9 * s))):
        y = base - hgt + 6 * s + k * 9 * s
        d.line([(cx - w, y), (cx + w, y + 4 * s)], fill=c[:3] + (150,), width=2)
    d.rectangle([cx - w * 1.8, base - 20 * s, cx + w * 1.8, base], outline=c, width=4)
    ty = base - hgt - 40 * s
    d.ellipse([cx - 150 * s, ty - 50 * s, cx + 150 * s, ty + 50 * s], outline=c, width=5)
    d.ellipse([cx - 90 * s, ty - 25 * s, cx + 90 * s, ty + 25 * s], outline=c[:3] + (150,), width=3)
    return cx, ty


def art_coil_big(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    s = 1.25 if b.get("big") else 1.0
    cx, ty = coil(d, 1380, 900, s, col(b, "ink"), col(b, "acc"))
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    bolt_burst(d2, cx, ty, t, 6, 520 * s, outer=col(b, "acc", 210))
    glow_layer(img, L2, 22, 1.6)
    flash(img, t, 1.3, 50)


def art_colorado(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    mountains(d, col(b, "faint"))
    # barn + tower
    bx, by = 1300, 860
    d.rectangle([bx - 200, by - 160, bx + 200, by], outline=c, width=4)
    d.polygon([(bx - 220, by - 160), (bx + 220, by - 160), (bx, by - 260)], outline=c)
    d.line([(bx - 220, by - 160), (bx, by - 260), (bx + 220, by - 160)], fill=c, width=4)
    d.line([(bx, by - 260), (bx, by - 560)], fill=c, width=6)
    for k in range(6):
        y = by - 280 - k * 45
        d.line([(bx - 30 + k * 4, y), (bx + 30 - k * 4, y - 20)], fill=c, width=2)
    circle(d, bx, by - 590, 34, c, w=5)
    d.line([(820, by), (W, by)], fill=c, width=3)
    if b.get("fire"):
        rnd = random.Random(int(t * 10))
        for k in range(10):
            x = 1680 + k * 18
            h = 60 + rnd.uniform(0, 90)
            d.polygon([(x - 14, by), (x + 14, by), (x + rnd.uniform(-6, 6), by - h)], fill=(255, 140, 50, 220))
        d.rectangle([1660, by - 80, 1860, by], outline=c, width=3)
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    if b.get("bolts") or b["art"] == "colorado":
        rnd = random.Random(int(t * 6))
        n = 4 if b.get("bolts") else 1
        if b.get("bolts") or (t % 2.5) < 0.25:
            for k in range(n):
                a = rnd.uniform(-2.6, -0.5)
                r = rnd.uniform(250, 520)
                bolt(d2, bx, by - 590, bx + math.cos(a) * r, by - 590 + math.sin(a) * r * .7, rnd, outer=col(b, "acc", 210), w=5)
            if b.get("bolts"):
                bolt(d2, bx, by - 590, bx + rnd.uniform(-300, 300), by, rnd, outer=col(b, "acc", 210), w=4)
    glow_layer(img, L2, 22, 1.6)
    if b.get("bolts"):
        flash(img, t, 0.9, 70)


def art_switch(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    d.rectangle([1200, 300, 1560, 860], outline=c, width=6)
    for y in (420, 740):
        circle(d, 1380, y, 26, c, w=5)
    k = ease((t - 0.8) / 0.4)
    a = math.radians(-60 + 120 * k)
    hx, hy = 1380 + math.sin(a) * 300, 580 - math.cos(a) * 300
    d.line([(1380, 580), (hx, hy)], fill=c, width=22)
    circle(d, hx, hy, 34, fill=col(b, "acc"))
    circle(d, 1380, 580, 30, fill=c)
    finish(img, b, L)
    if k >= 1:
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        bolt_burst(d2, 1380, 740, t, 3, 200, outer=col(b, "acc", 220), rate=14)
        glow_layer(img, L2, 16, 1.5)


def art_portrait(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    # stylised profile facing left
    pts = [(1500, 900), (1500, 760), (1460, 700), (1440, 640), (1410, 610), (1395, 580), (1380, 560), (1388, 545), (1372, 530),
           (1390, 512), (1384, 490), (1395, 470), (1380, 440), (1386, 400), (1400, 360), (1430, 320), (1480, 290), (1540, 282),
           (1600, 296), (1650, 330), (1680, 380), (1690, 440), (1680, 500), (1660, 560), (1640, 620), (1640, 700), (1700, 760),
           (1820, 820), (1880, 900)]
    stroke(d, pts, col(b, "ink"), 5, ease(t / 2.0))
    stroke(d, [(1392, 548), (1420, 556), (1440, 548)], col(b, "ink"), 6, ease((t - 1.5) / .4))
    stroke(d, [(1470, 300), (1500, 360), (1560, 330)], col(b, "faint"), 3, ease((t - 1.2) / .5))
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    if (t % 1.8) < 0.3:
        rnd = random.Random(int(t * 10))
        bolt(d2, 1520, 220, 1700 + rnd.uniform(-60, 60), 80, rnd, outer=col(b, "acc", 200), w=4)
    glow_layer(img, L2, 18, 1.5)


ICON = {}


def icon(d, name, cx, cy, c, acc, t):
    if name == "bulb":
        circle(d, cx, cy - 20, 55, c, w=5)
        d.rectangle([cx - 25, cy + 30, cx + 25, cy + 60], outline=c, width=4)
        d.line([(cx - 15, cy - 10), (cx, cy - 35), (cx + 15, cy - 10)], fill=acc, width=4)
    elif name == "wave":
        pts = [(cx - 80 + i * 4, cy + math.sin(i * 0.3 + t * 5) * 30) for i in range(41)]
        d.line(pts, fill=c, width=5)
    elif name in ("boat",):
        d.polygon([(cx - 70, cy), (cx + 70, cy), (cx + 50, cy + 30), (cx - 50, cy + 30)], outline=c)
        d.line([(cx - 70, cy), (cx + 70, cy), (cx + 50, cy + 30), (cx - 50, cy + 30), (cx - 70, cy)], fill=c, width=4)
        d.line([(cx, cy), (cx, cy - 60)], fill=c, width=4)
        for r in (15, 30):
            d.arc([cx - r, cy - 60 - r, cx + r, cy - 60 + r], 200, 340, fill=acc, width=3)
    elif name == "globe":
        circle(d, cx, cy, 60, c, w=4)
        d.ellipse([cx - 25, cy - 60, cx + 25, cy + 60], outline=c, width=3)
        d.line([(cx - 60, cy), (cx + 60, cy)], fill=c, width=3)
        d.line([(cx - 40, cy - 70), (cx + 40, cy + 70)], fill=acc, width=5)
    elif name == "drone":
        d.rectangle([cx - 30, cy - 12, cx + 30, cy + 12], outline=c, width=4)
        for sx in (-1, 1):
            d.line([(cx + sx * 30, cy), (cx + sx * 70, cy - 20)], fill=c, width=4)
            d.ellipse([cx + sx * 70 - 30, cy - 26, cx + sx * 70 + 30, cy - 14], outline=acc, width=3)
    elif name == "remote":
        d.rounded_rectangle([cx - 30, cy - 70, cx + 30, cy + 70], 14, outline=c, width=4)
        for k in range(3):
            circle(d, cx, cy - 30 + k * 30, 9, fill=acc if k == 0 else c)
    elif name == "robot":
        d.rectangle([cx - 40, cy - 60, cx + 40, cy], outline=c, width=4)
        d.rectangle([cx - 50, cy + 5, cx + 50, cy + 65], outline=c, width=4)
        circle(d, cx - 18, cy - 30, 8, fill=acc); circle(d, cx + 18, cy - 30, 8, fill=acc)
    elif name == "outlet":
        d.rounded_rectangle([cx - 50, cy - 70, cx + 50, cy + 70], 10, outline=c, width=4)
        for y in (-30, 30):
            d.rectangle([cx - 20, cy + y - 12, cx - 12, cy + y + 12], fill=c)
            d.rectangle([cx + 12, cy + y - 12, cx + 20, cy + y + 12], fill=c)
    elif name == "radio":
        d.rounded_rectangle([cx - 70, cy - 40, cx + 70, cy + 50], 10, outline=c, width=4)
        circle(d, cx - 30, cy + 5, 22, c, w=4)
        d.line([(cx + 40, cy - 40), (cx + 70, cy - 90)], fill=c, width=4)
        for r in (15, 30):
            d.arc([cx + 70 - r, cy - 90 - r, cx + 70 + r, cy - 90 + r], 200, 340, fill=acc, width=3)
    elif name == "motor":
        circle(d, cx, cy, 60, c, w=5)
        a = t * 6
        for k in range(3):
            an = a + k * 2.094
            d.line([(cx, cy), (cx + math.cos(an) * 45, cy + math.sin(an) * 45)], fill=acc, width=6)


def art_four(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    icons = b.get("icons", ["bulb", "wave", "boat", "globe"])
    labels = b.get("labels", icons)
    for i in range(4):
        k = ease((t - 0.3 - i * 0.5) / 0.5)
        if k <= 0:
            continue
        cx = 1000 + (i % 2) * 400
        cy = 330 + (i // 2) * 350
        a = int(255 * k)
        circle(d, cx, cy, 120, col(b, "faint", a), w=3)
        icon(d, icons[i], cx, cy, col(b, "ink", a), col(b, "acc", a), t)
        d.text((cx, cy + 150), labels[i], font=font(CINZEL7, 28), fill=col(b, "ink", a), anchor="mm")
    finish(img, b, L)


def art_question(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease(t / 0.8)
    d.text((1380, 520), "?", font=font(CINZEL9, 520), fill=col(b, "acc", int(255 * k)), anchor="mm")
    finish(img, b, L, 24)
    if (t % 2.0) < 0.25:
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        bolt_burst(d2, 1380, 300, t, 2, 260, outer=col(b, "acc", 180), rate=12)
        glow_layer(img, L2, 16, 1.3)


def art_title(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, ty = coil(d, W / 2, 380, 0.55, col(b, "ink"), col(b, "acc"))
    finish(img, b, L, 16)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    bolt_burst(d2, cx, ty, t, 5, 330, outer=col(b, "acc", 220))
    glow_layer(img, L2, 20, 1.6)
    flash(img, t, 1.1, 40)


def art_birthmap(img, b, t, dur):
    box = (960, 140, 1840, 960, 5, 30, 52, 38)
    L = layer(); d = ImageDraw.Draw(L)
    for c in WORLD:
        for ring in c["rings"]:
            if not any(0 <= p[0] <= 35 and 35 <= p[1] <= 55 for p in ring[:10]):
                continue
            pts = [proj_eq(x, y, box) for x, y in ring]
            if c["name"] == "Croatia":
                d.polygon(pts, fill=col(b, "acc", 120))
            stroke(d, pts, col(b, "ink", 200), 2, ease(t / 1.6), closed=True)
    x, y = proj_eq(15.3, 44.6, box)
    r = 10 + 5 * math.sin(t * 5)
    circle(d, x, y, r + 12, col(b, "acc"), w=3)
    circle(d, x, y, 8, fill=col(b, "acc"))
    d.text((x + 26, y), "SMILJAN", font=font(CINZEL7, 32), fill=col(b, "ink"), anchor="lm")
    # midnight clock
    cx, cy = 1700, 300
    circle(d, cx, cy, 80, col(b, "ink"), w=4)
    d.line([(cx, cy), (cx, cy - 60)], fill=col(b, "ink"), width=6)
    d.line([(cx, cy), (cx + 2, cy - 45)], fill=col(b, "acc"), width=8)
    d.text((cx, cy + 110), "00:00", font=font(MONO, 26), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def art_village_storm(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    base = 860
    d.line([(900, base), (W, base)], fill=c, width=3)
    for k, x in enumerate((1000, 1200, 1430, 1650)):
        w_, h_ = 140 + k * 10, 110 + (k % 2) * 30
        d.rectangle([x, base - h_, x + w_, base], outline=c, width=4)
        d.polygon([(x - 15, base - h_), (x + w_ + 15, base - h_), (x + w_ / 2, base - h_ - 90)], outline=c)
        d.line([(x - 15, base - h_), (x + w_ / 2, base - h_ - 90), (x + w_ + 15, base - h_)], fill=c, width=4)
        lit = (k == 2)
        d.rectangle([x + 30, base - 70, x + 70, base - 30], fill=col(b, "acc" if lit else "faint", 220 if lit else 120))
    for k in range(120):
        x = (k * 97 + t * 200) % W
        y = (k * 53 + t * 900) % H
        d.line([(x, y), (x - 8, y + 26)], fill=col(b, "faint", 150), width=2)
    finish(img, b, L)
    if (t % 2.2) < 0.3:
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        rnd = random.Random(int(t / 2.2))
        bolt(d2, 1200 + rnd.uniform(0, 400), 0, 1300 + rnd.uniform(0, 300), base - 200, rnd, outer=col(b, "acc", 220), w=5)
        glow_layer(img, L2, 20, 1.6)
        flash(img, t, 2.2, 90)


def art_candle(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, base = 1380, 880
    d.rectangle([cx - 50, base - 320, cx + 50, base], outline=col(b, "ink"), width=5)
    d.ellipse([cx - 160, base - 20, cx + 160, base + 30], outline=col(b, "ink"), width=4)
    out = b.get("out") and t > dur * 0.5
    if not out:
        fl = 1 + 0.08 * math.sin(t * 13) + 0.05 * math.sin(t * 7)
        for r, a in ((160, 40), (90, 90), (45, 200)):
            d.ellipse([cx - r * .6, base - 400 - r * fl, cx + r * .6, base - 400 + r * .5], fill=(255, 200, 110, a))
        d.polygon([(cx - 22, base - 360), (cx + 22, base - 360), (cx, base - 470 * fl)], fill=(255, 240, 200, 255))
    else:
        for k in range(6):
            ph = ((t - dur * .5) * .5 + k * .15) % 1
            d.ellipse([cx - 6 + math.sin(ph * 6 + k) * 30, base - 360 - ph * 300 - 6, cx + 6 + math.sin(ph * 6 + k) * 30, base - 360 - ph * 300 + 6], fill=col(b, "faint", int(160 * (1 - ph))))
    d.line([(cx, base - 320), (cx, base - 360)], fill=col(b, "ink"), width=4)
    finish(img, b, L, 30)


def art_mind(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    head = [(1150, 920), (1160, 760), (1110, 700), (1090, 640), (1060, 610), (1080, 590), (1062, 560), (1080, 540), (1070, 500),
            (1080, 420), (1120, 330), (1200, 260), (1320, 220), (1450, 230), (1560, 290), (1620, 380), (1640, 480), (1620, 580),
            (1580, 660), (1570, 760), (1600, 920)]
    stroke(d, head, col(b, "ink"), 5, ease(t / 1.8))
    rot = t * (1.2 if b.get("gears") else 0.6)
    for (gx, gy, r, sp) in ((1360, 430, 90, 1), (1490, 520, 60, -1.5), (1260, 560, 55, -1.6)):
        for k in range(10):
            a = rot * sp + k * math.pi / 5
            d.line([(gx + math.cos(a) * r * .75, gy + math.sin(a) * r * .75), (gx + math.cos(a) * r * 1.05, gy + math.sin(a) * r * 1.05)], fill=col(b, "acc"), width=12)
        circle(d, gx, gy, r * .8, col(b, "acc"), w=6)
        circle(d, gx, gy, r * .25, col(b, "acc"), w=4)
    finish(img, b, L)


def art_dynamo(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    cx, cy = 1380, 560
    d.rectangle([cx - 300, cy + 160, cx + 300, cy + 200], outline=c, width=4)
    for s in (-1, 1):
        d.arc([cx - 250, cy - 250, cx + 250, cy + 250], 90 + s * 90 - 60, 90 + s * 90 + 60, fill=c, width=40)
    rot = t * 6
    circle(d, cx, cy, 140, c, w=5)
    for k in range(12):
        a = rot + k * math.pi / 6
        d.line([(cx + math.cos(a) * 40, cy + math.sin(a) * 40), (cx + math.cos(a) * 135, cy + math.sin(a) * 135)], fill=c, width=3)
    circle(d, cx, cy, 40, fill=c)
    finish(img, b, L)
    if not b.get("nospark"):
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        rnd = random.Random(int(t * 16))
        for k in range(6):
            a = rnd.uniform(0, 6.28)
            x0, y0 = cx + math.cos(a) * 140, cy + math.sin(a) * 140
            bolt(d2, x0, y0, x0 + math.cos(a) * rnd.uniform(40, 120), y0 + math.sin(a) * rnd.uniform(40, 120), rnd, outer=(255, 200, 100, 220), w=3, branches=1)
        glow_layer(img, L2, 12, 1.5)
    else:
        d3 = ImageDraw.Draw(img)
        k = ease((t - .5) / .5)
        d3.line([(cx + 200, cy - 280), (cx + 240, cy - 240), (cx + 320, cy - 340)], fill=col(b, "acc", int(255 * k)), width=14)


def art_laugh(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    words = ["HA", "HA", "HA", "HA", "HA"] if not b.get("quiet") else ["HA"]
    for i, w_ in enumerate(words):
        k = ease((t - i * .25) / .3)
        x = 1050 + (i % 3) * 260 + (i // 3) * 130
        y = 350 + (i // 3) * 260 + math.sin(t * 8 + i) * 12
        a = int(255 * k * (0.4 if b.get("quiet") else 1))
        d.text((x, y), w_, font=font(CINZEL9, 200 if not b.get("quiet") else 260), fill=col(b, "acc" if i % 2 else "ink", a), anchor="mm")
    finish(img, b, L)


def art_park(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 860
    for r in range(260, 100, -20):
        circle(d, 1500, 620, r, fill=(255, 160 + (260 - r) // 3, 80, 24))
    circle(d, 1500, 620, 100, fill=(255, 190, 110, 255))
    d.rectangle([900, base, W, H], fill=PAL[b["pal"]]["bg"] + (255,))
    d.line([(900, base), (W, base)], fill=col(b, "ink"), width=3)
    for x in (1000, 1780):
        d.line([(x, base), (x, base - 260)], fill=col(b, "ink"), width=10)
        circle(d, x, base - 330, 110, col(b, "ink"), w=5)
    k = min(1.0, t / max(1, dur * .6))
    for j, off in enumerate((0, 70)):
        x = 1100 + k * 300 + off
        person(d, x, base - 40, 3.2 if j == 0 else 3.0, col(b, "ink"))
    finish(img, b, L)


def art_rmf(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy, R = 1380, 540, 300
    circle(d, cx, cy, R, col(b, "faint"), w=3)
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
        amp = math.cos(t * 4 - k * 2 * math.pi / 3)
        cc = col(b, "acc", int(120 + 135 * max(0, amp)))
        for j in range(5):
            d.ellipse([x - 40 + j * 4, y - 40 + j * 4, x + 40 - j * 4, y + 40 - j * 4], outline=cc, width=3)
        d.text((cx + math.cos(a) * (R + 80), cy + math.sin(a) * (R + 80)), ["A", "B", "C"][k], font=font(CINZEL9, 40), fill=col(b, "ink"), anchor="mm")
    a = t * 4 - math.pi / 2
    tip = (cx + math.cos(a) * (R - 60), cy + math.sin(a) * (R - 60))
    d.line([(cx, cy), tip], fill=col(b, "ink"), width=10)
    d.polygon([(tip[0] + math.cos(a) * 30, tip[1] + math.sin(a) * 30), (tip[0] + math.cos(a + 2.4) * 30, tip[1] + math.sin(a + 2.4) * 30), (tip[0] + math.cos(a - 2.4) * 30, tip[1] + math.sin(a - 2.4) * 30)], fill=col(b, "ink"))
    # trailing arc
    stroke(d, arc_pts(cx, cy, R - 60, R - 60, a - 1.4, a, 30), col(b, "acc", 160), 6)
    rot = t * 3.6
    for k in range(6):
        an = rot + k * math.pi / 3
        d.line([(cx, cy), (cx + math.cos(an) * 90, cy + math.sin(an) * 90)], fill=col(b, "faint"), width=6)
    circle(d, cx, cy, 95, col(b, "faint"), w=4)
    finish(img, b, L)


def art_sand(img, b, t, dur):
    d0 = ImageDraw.Draw(img)
    d0.rectangle([900, 640, W, H], fill=(150, 110, 80, 255))
    L = layer(); d = ImageDraw.Draw(L)
    c = (70, 40, 30, 255)
    prog = ease(t / max(1, dur * .8))
    stroke(d, arc_pts(1380, 820, 160, 80, 0, 2 * math.pi, 60), c, 6, prog * 2)
    for k in range(3):
        a = k * 2.094
        stroke(d, [(1380, 820), (1380 + math.cos(a) * 160, 820 + math.sin(a) * 80)], c, 5, prog * 2 - 1 - k * .2)
    tip = polyline_partial(arc_pts(1380, 820, 160, 80, 0, 2 * math.pi, 60), min(1, prog * 2))[-1]
    d.line([tip, (tip[0] + 160, tip[1] - 420)], fill=(110, 70, 40, 255), width=12)
    img.alpha_composite(L)


def art_acwave(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    x0, x1, cy = 960, 1820, 540
    d.line([(x0, cy), (x1, cy)], fill=col(b, "faint"), width=2)
    f = 0.06 if b.get("fast") else 0.018
    pts = [(x, cy + math.sin((x - x0) * f - t * 6) * 180) for x in range(x0, x1, 4)]
    pp = polyline_partial(pts, ease(t / 1.5))
    if len(pp) > 1:
        d.line(pp, fill=col(b, "acc"), width=7, joint="curve")
    d.text((x0, cy - 260), "AC", font=font(CINZEL9, 60), fill=col(b, "acc"), anchor="lm")
    if b.get("win"):
        yy = cy + 260
        d.line([(x0, yy), (x1, yy)], fill=col(b, "faint"), width=6)
        d.text((x0, yy - 50), "DC", font=font(CINZEL9, 50), fill=col(b, "faint"), anchor="lm")
        k = ease((t - .8) / .4)
        d.line([(x0 + 100, yy - 60), (x0 + 100 + 120 * k, yy + 40 * k)], fill=(255, 80, 70, 255), width=10)
    finish(img, b, L)


def art_skyline(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 760
    rnd = random.Random(2)
    x = 900
    while x < W:
        w_ = rnd.randint(50, 110); h_ = rnd.randint(80, 300)
        d.rectangle([x, base - h_, x + w_, base], outline=col(b, "ink"), width=3)
        if rnd.random() < .3:
            d.polygon([(x, base - h_), (x + w_, base - h_), (x + w_ / 2, base - h_ - 60)], outline=col(b, "ink"))
        for wy in range(base - h_ + 20, base - 10, 34):
            if rnd.random() < .5:
                d.rectangle([x + 12, wy, x + 24, wy + 14], fill=col(b, "acc", 180))
        x += w_ + 8
    d.line([(900, base), (W, base)], fill=col(b, "ink"), width=3)
    A.waves(d, col(b, "ink"), t, base + 40, 3, 6)
    sx = 900 + ease(t / max(1, dur)) * 400
    A.draw_ship(d, sx, base + 100, 0.4, col(b, "ink"), t, 1.0, math.sin(t) * 2)
    finish(img, b, L)


def art_bulb(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 460
    k = 0.6 + 0.4 * math.sin(t * 2) ** 2
    for r, a in ((300, 30), (220, 50), (160, 80)):
        circle(d, cx, cy, r, fill=col(b, "acc", int(a * k)))
    circle(d, cx, cy, 160, col(b, "ink"), w=6)
    d.rectangle([cx - 70, cy + 150, cx + 70, cy + 260], outline=col(b, "ink"), width=5)
    for y in range(cy + 170, cy + 260, 24):
        d.line([(cx - 70, y), (cx + 70, y + 8)], fill=col(b, "ink"), width=3)
    pts = [(cx - 40, cy + 150), (cx - 30, cy - 10)] + [(cx - 30 + i * 10, cy - 10 + (20 if i % 2 else -20)) for i in range(7)] + [(cx + 40, cy + 150)]
    d.line(pts, fill=(255, 240, 200, 255), width=5, joint="curve")
    finish(img, b, L, 28)


def art_door(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 1220, 220, 1560, 900
    d.rectangle([x0 - 20, y0 - 20, x1 + 20, y1], outline=col(b, "ink"), width=6)
    k = 1 - ease(t / 0.35)
    w_ = (x1 - x0) * (0.2 + 0.8 * (1 - k))
    d.rectangle([x0, y0, x0 + w_, y1], fill=col(b, "faint", 200), outline=col(b, "ink"), width=4)
    if k < 0.2:
        circle(d, x0 + w_ - 40, (y0 + y1) / 2, 14, fill=col(b, "ink"))
        for j in range(4):
            d.line([(x1 + 40, 400 + j * 70), (x1 + 120, 380 + j * 70)], fill=col(b, "acc", int(255 * max(0, 1 - (t - .35) * 2))), width=6)
    finish(img, b, L)


def art_ditch(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    base = 820
    d.line([(900, base), (1300, base)], fill=c, width=5)
    d.line([(1300, base), (1340, base + 120), (1640, base + 120), (1680, base)], fill=c, width=5)
    d.line([(1680, base), (W, base)], fill=c, width=5)
    ph = (t * 1.2) % 1
    a = math.sin(ph * math.pi * 2) * 0.6
    px, py = 1480, base + 40
    d.ellipse([px - 26, py - 220, px + 26, py - 168], fill=c)
    d.line([(px, py - 168), (px + 10, py - 70)], fill=c, width=22)
    d.line([(px + 10, py - 70), (px - 20, py + 70)], fill=c, width=18)
    d.line([(px + 10, py - 70), (px + 40, py + 70)], fill=c, width=18)
    hx, hy = px + 60 * math.cos(a), py - 140 + 60 * math.sin(a)
    d.line([(px + 5, py - 150), (hx, hy)], fill=c, width=14)
    d.line([(hx - 120 * math.cos(a + 1.2), hy - 120 * math.sin(a + 1.2)), (hx + 140 * math.cos(a + 1.2), hy + 140 * math.sin(a + 1.2))], fill=c, width=8)
    if ph > 0.5:
        for k in range(8):
            r = (ph - .5) * 2
            d.ellipse([1300 + k * 20 - 8 - r * 60, base - r * 120 - 8 + k * 6, 1300 + k * 20 + 8 - r * 60, base - r * 120 + 8 + k * 6], fill=col(b, "faint"))
    d.text((1150, 400), "$2", font=font(CINZEL9, 150), fill=col(b, "acc"), anchor="mm")
    d.text((1150, 500), "PER DAY", font=font(CINZEL7, 36), fill=c, anchor="mm")
    finish(img, b, L)


def art_motor(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 540
    circle(d, cx, cy, 320, col(b, "ink"), w=8)
    for k in range(12):
        a = k * math.pi / 6
        ph = math.cos(t * 5 - k * math.pi / 6 * 2)
        x, y = cx + math.cos(a) * 270, cy + math.sin(a) * 270
        d.ellipse([x - 32, y - 32, x + 32, y + 32], outline=col(b, "acc", int(100 + 155 * max(0, ph))), width=8)
    rot = t * 4.5
    circle(d, cx, cy, 170, col(b, "ink"), w=5)
    for k in range(16):
        an = rot + k * math.pi / 8
        d.line([(cx + math.cos(an) * 40, cy + math.sin(an) * 40), (cx + math.cos(an) * 160, cy + math.sin(an) * 160)], fill=col(b, "ink"), width=4)
    circle(d, cx, cy, 36, fill=col(b, "acc"))
    finish(img, b, L)


def art_versus(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease(t / .8)
    d.rectangle([900, 160, 1360, 920], fill=(255, 170, 60, int(50 * k)))
    d.rectangle([1400, 160, 1860, 920], fill=(80, 200, 255, int(50 * k)))
    d.text((1130, 300), "DC", font=font(CINZEL9, 150), fill=(255, 190, 90, int(255 * k)), anchor="mm")
    d.text((1130, 420), "EDISON", font=font(CINZEL7, 40), fill=col(b, "ink", int(255 * k)), anchor="mm")
    d.text((1630, 300), "AC", font=font(CINZEL9, 150), fill=(120, 220, 255, int(255 * k)), anchor="mm")
    d.text((1630, 420), "TESLA & WESTINGHOUSE", font=font(CINZEL7, 32), fill=col(b, "ink", int(255 * k)), anchor="mm")
    d.line([(940, 700), (1320, 700)], fill=(255, 190, 90, 255), width=8)
    pts = [(x, 700 + math.sin(x * .03 - t * 6) * 80) for x in range(1440, 1820, 4)]
    d.line(pts, fill=(120, 220, 255, 255), width=8)
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    rnd = random.Random(int(t * 8))
    bolt(d2, 1380, 140, 1380, 940, rnd, outer=col(b, "acc", 220), w=5, branches=4)
    glow_layer(img, L2, 16, 1.5)


def art_distance(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    y1, y2 = 420, 720
    d.text((960, y1 - 70), "DC", font=font(CINZEL9, 50), fill=(255, 190, 90, 255), anchor="lm")
    d.text((960, y2 - 70), "AC", font=font(CINZEL9, 50), fill=col(b, "acc"), anchor="lm")
    k = ease((t - .3) / 2.0)
    xe = 960 + 860 * k
    for x in range(960, int(min(xe, 1160)), 6):
        a = max(0, 1 - (x - 960) / 200)
        d.line([(x, y1), (x + 6, y1)], fill=(255, 190, 90, int(255 * a)), width=10)
    d.text((1180, y1 + 40), "1 MILE", font=font(MONO, 24), fill=col(b, "faint"), anchor="mm")
    d.line([(960, y2), (xe, y2)], fill=col(b, "acc"), width=10)
    for k2 in range(6):
        px = 1040 + k2 * 150
        if px < xe:
            d.line([(px, y2), (px, y2 - 90)], fill=col(b, "ink"), width=4)
            d.line([(px - 30, y2 - 80), (px + 30, y2 - 80)], fill=col(b, "ink"), width=4)
    ph = (t * 0.6) % 1
    circle(d, 960 + 860 * ph * k, y2, 12, fill=(255, 255, 255, 255))
    d.text((1820, y2 + 50), "100s OF MILES", font=font(MONO, 24), fill=col(b, "faint"), anchor="rm")
    finish(img, b, L)


def art_danger(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 540
    on = (t % 1.0) < 0.6
    tri = [(cx, cy - 300), (cx + 320, cy + 240), (cx - 320, cy + 240)]
    d.polygon(tri, fill=(255, 200, 40, 255 if on else 140))
    d.line(tri + [tri[0]], fill=(20, 20, 20, 255), width=16, joint="curve")
    d.polygon([(cx + 20, cy - 170), (cx - 70, cy + 40), (cx, cy + 30), (cx - 30, cy + 190), (cx + 80, cy - 20), (cx + 10, cy - 10)], fill=(20, 20, 20, 255))
    d.text((cx, cy + 320), "HIGH VOLTAGE", font=font(CINZEL9, 50), fill=col(b, "acc"), anchor="mm")
    finish(img, b, L)


def art_worldsfair(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 800
    c = col(b, "ink")
    for k, (x, w_, h_) in enumerate(((960, 160, 200), (1140, 220, 260), (1380, 260, 360), (1660, 180, 220))):
        d.rectangle([x, base - h_, x + w_, base], outline=c, width=4)
        d.arc([x + w_ * .2, base - h_ - w_ * .3, x + w_ * .8, base - h_ + w_ * .3], 180, 360, fill=c, width=4)
        for col_ in range(int(w_ / 30)):
            d.line([(x + 15 + col_ * 30, base - h_ + 20), (x + 15 + col_ * 30, base)], fill=c[:3] + (90,), width=2)
    rnd = random.Random(1)
    k = ease((t - .2) / 2.5)
    for i in range(700):
        if i / 700 > k:
            break
        x = rnd.uniform(940, 1860); y = rnd.uniform(380, base)
        tw = 0.5 + 0.5 * math.sin(t * 6 + i)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 230, 150, int(140 + 115 * tw)))
    d.line([(900, base), (W, base)], fill=c, width=4)
    for i in range(int(k * 40)):
        x = 940 + i * 23
        d.line([(x, base + 10), (x, base + 40 + (i % 3) * 12)], fill=(255, 230, 150, 120), width=2)
    finish(img, b, L, 16)


def art_niagara(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    d.line([(920, 360), (1180, 360)], fill=c, width=5)
    d.line([(1180, 360), (1180, 820)], fill=c, width=5)
    for k in range(24):
        x = 1000 + k * 8
        off = (t * 600 + k * 37) % 120
        for y in range(360 + int(off), 820, 120):
            d.line([(x, y), (x, y + 60)], fill=(200, 230, 255, 200), width=3)
    for k in range(10):
        ph = (t * .8 + k * .1) % 1
        d.ellipse([980 + k * 20 - ph * 40, 800 - ph * 60, 1020 + k * 20 + ph * 40, 840 - ph * 20], fill=(220, 240, 255, int(120 * (1 - ph))))
    d.rectangle([1220, 680, 1340, 820], outline=c, width=4)
    d.text((1280, 860), "POWER HOUSE", font=font(MONO, 18), fill=col(b, "faint"), anchor="mm")
    poles = [(1400 + k * 90, 820) for k in range(5)]
    for x, y in poles:
        d.line([(x, y), (x, y - 220)], fill=c, width=4)
        d.line([(x - 30, y - 200), (x + 30, y - 200)], fill=c, width=4)
    wire = [(1340, 700)] + [(x, 620 + 20 * (i % 2)) for i, (x, y) in enumerate(poles)] + [(1820, 640)]
    d.line(wire, fill=col(b, "faint"), width=3)
    for k in range(4):
        ph = (t * .5 + k * .25) % 1
        q = polyline_partial(wire, ph)[-1]
        circle(d, q[0], q[1], 10, fill=col(b, "acc"))
    d.rectangle([1760, 560, 1860, 820], outline=c, width=4)
    for wy in range(590, 800, 40):
        d.rectangle([1780, wy, 1800, wy + 20], fill=col(b, "acc", 220)); d.rectangle([1820, wy, 1840, wy + 20], fill=col(b, "acc", 220))
    d.text((1810, 860), "BUFFALO", font=font(CINZEL7, 26), fill=c, anchor="mm")
    d.text((1580, 560), "26 MILES", font=font(CINZEL9, 34), fill=col(b, "acc"), anchor="mm")
    finish(img, b, L)


def art_contract(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease((t - 0.6) / 1.2) if b.get("tear") else 0
    for half in (0, 1):
        x0 = 1080 + half * 300 + (k * 140 * (1 if half else -1))
        rot = (k * 10 * (1 if half else -1))
        pg = Image.new("RGBA", (300, 720), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pg)
        pd.rectangle([0, 0, 300, 720], fill=(240, 230, 205, 255))
        if half == 0:
            pd.text((300, 70), "ROYAL", font=font(CINZEL9, 44), fill=(60, 40, 30, 255), anchor="rm")
        else:
            pd.text((0, 70), "TIES", font=font(CINZEL9, 44), fill=(60, 40, 30, 255), anchor="lm")
        for j in range(14):
            y = 150 + j * 36
            pd.line([(30 if half == 0 else 0, y), (300 if half == 0 else 260, y)], fill=(120, 100, 80, 255), width=3)
        edge = [(300 if half == 0 else 0, y) for y in range(0, 721, 30)]
        pg = pg.rotate(rot, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(pg, (int(x0 - pg.width / 2 + 150), int(540 - pg.height / 2)))
    img.alpha_composite(L)


def art_tubes(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    for s, x in ((-1, 1240), (1, 1520)):
        fl = 0.7 + 0.3 * random.Random(int(t * 12) + s).random()
        g = ease((t - .6) / .6) * fl
        for r, a in ((60, 40), (40, 80)):
            d.rounded_rectangle([x - r, 260 - r, x + r, 760 + r], 40, fill=col(b, "acc", int(a * g)))
        d.rounded_rectangle([x - 22, 260, x + 22, 760], 20, fill=(240, 220, 255, int(60 + 195 * g)), outline=col(b, "ink"), width=3)
        d.rounded_rectangle([x - 70, 700, x + 70, 860], 50, fill=col(b, "faint"))
    finish(img, b, L, 26)


def art_body(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, base = 1380, 900
    c = col(b, "ink")
    d.ellipse([cx - 50, base - 600, cx + 50, base - 500], fill=c)
    d.rounded_rectangle([cx - 70, base - 490, cx + 70, base - 230], 30, fill=c)
    d.line([(cx - 40, base - 230), (cx - 50, base)], fill=c, width=40)
    d.line([(cx + 40, base - 230), (cx + 50, base)], fill=c, width=40)
    d.line([(cx - 70, base - 470), (cx - 240, base - 560)], fill=c, width=30)
    d.line([(cx + 70, base - 470), (cx + 240, base - 560)], fill=c, width=30)
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    k = 0.7 + 0.3 * math.sin(t * 9)
    if b.get("skin"):
        stroke(d2, [(cx - 70, base - 490), (cx - 70, base - 230), (cx - 50, base), (cx + 50, base), (cx + 70, base - 230), (cx + 70, base - 490)], col(b, "acc"), 8)
        circle(d2, cx, base - 550, 60, col(b, "acc"), w=8)
    else:
        d2.ellipse([cx - 320, base - 760, cx + 320, base + 40], outline=col(b, "acc", int(180 * k)), width=10)
    rnd = random.Random(int(t * 12))
    for s in (-1, 1):
        fx, fy = cx + s * 250, base - 566
        for kk in range(3):
            bolt(d2, fx, fy, fx + s * rnd.uniform(80, 220), fy + rnd.uniform(-150, 80), rnd, outer=col(b, "acc", 220), w=3, branches=1)
    glow_layer(img, L2, 20, 1.6)


def art_xray(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "acc")
    if b.get("skull"):
        cx, cy = 1380, 500
        stroke(d, arc_pts(cx, cy, 200, 230, math.pi * .9, math.pi * 2.1, 60), c, 8, ease(t / 1.4))
        stroke(d, [(cx - 190, cy + 80), (cx - 120, cy + 260), (cx + 120, cy + 260), (cx + 190, cy + 80)], c, 8, ease(t / 1.4))
        for s in (-1, 1):
            d.ellipse([cx + s * 80 - 50, cy - 10, cx + s * 80 + 50, cy + 80], outline=c, width=8)
        d.polygon([(cx, cy + 100), (cx - 25, cy + 160), (cx + 25, cy + 160)], outline=c)
        for k in range(8):
            d.line([(cx - 110 + k * 30, cy + 220), (cx - 110 + k * 30, cy + 260)], fill=c, width=6)
    else:
        cx, base = 1380, 920
        d.ellipse([cx - 150, base - 300, cx + 150, base - 80], outline=col(b, "faint", 120), width=4)
        for k, (dx, L_) in enumerate(((-110, 300), (-55, 380), (0, 410), (55, 380), (110, 300))):
            prog = ease((t - k * .15) / 1.0)
            x0, y0 = cx + dx * .6, base - 160
            pts = [(x0, y0)]
            for j in range(3):
                pts.append((x0 + dx * (0.25 + j * .2), y0 - L_ * (0.4 + j * .2)))
            stroke(d, pts, c, 12, prog)
            for p in pts[1:]:
                if prog >= 1:
                    circle(d, p[0], p[1], 9, fill=c)
        d.line([(cx - 60, base - 160), (cx + 60, base - 160)], fill=c, width=10)
        d.line([(cx - 40, base - 160), (cx - 50, base)], fill=c, width=12)
        d.line([(cx + 40, base - 160), (cx + 50, base)], fill=c, width=12)
    finish(img, b, L, 20)
    sy = 150 + ((t * 300) % 800)
    ImageDraw.Draw(img).line([(900, sy), (W, sy)], fill=col(b, "acc", 60), width=4)


def art_boat(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    d.rectangle([1000, 620, 1840, 900], outline=c, width=5)
    for k in range(5):
        y = 660 + k * 50
        d.line([(1010 + ((t * 40 + k * 30) % 60), y), (1830, y)], fill=col(b, "faint", 120), width=2)
    bx = 1420 + (math.sin(t * 0.9) * 250 if b.get("moving") else 0)
    by = 700
    d.polygon([(bx - 110, by), (bx + 110, by), (bx + 80, by + 50), (bx - 80, by + 50)], fill=PAL[b["pal"]]["bg"] + (255,))
    d.line([(bx - 110, by), (bx + 110, by), (bx + 80, by + 50), (bx - 80, by + 50), (bx - 110, by)], fill=c, width=5)
    d.rectangle([bx - 40, by - 50, bx + 40, by], outline=c, width=4)
    d.line([(bx, by - 50), (bx, by - 140)], fill=c, width=4)
    if (t % 1.2) < 0.6:
        circle(d, bx, by - 150, 14, fill=col(b, "acc"))
    d.rounded_rectangle([960, 300, 1100, 420], 12, outline=c, width=5)
    d.line([(1080, 300), (1120, 200)], fill=c, width=4)
    if b.get("waves") or b.get("moving"):
        for k in range(4):
            r = ((t * 200 + k * 100) % 400)
            d.arc([1120 - r, 200 - r, 1120 + r, 200 + r], -40, 40, fill=col(b, "acc", int(255 * (1 - r / 400))), width=4)
    if b.get("question"):
        for k, (qx, qy) in enumerate(((1250, 300), (1600, 260), (1750, 420))):
            d.text((qx, qy + math.sin(t * 3 + k) * 10), "?", font=font(CINZEL9, 90), fill=col(b, "acc", 220), anchor="mm")
    finish(img, b, L)


def art_oscillator(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    d.rectangle([1340, 160, 1420, 900], outline=c, width=5)
    off = math.sin(t * 30) * 6
    d.rectangle([1420 + off, 440, 1600 + off, 580], outline=c, width=5)
    circle(d, 1510 + off, 510, 40, c, w=4)
    for k in range(5):
        r = 60 + ((t * 120 + k * 50) % 250)
        d.arc([1510 - r, 510 - r, 1510 + r, 510 + r], -60, 60, fill=col(b, "acc", int(255 * (1 - (r - 60) / 250))), width=4)
    d.text((1510, 680), f"{4 + int(t * 3) % 6} Hz", font=font(MONO, 36), fill=col(b, "acc"), anchor="mm")
    finish(img, b, L)


def art_shaking(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    stop = b.get("stop") and t > 0.6
    amp = 0 if stop else 8 + 6 * math.sin(t * 2)
    base = 880
    for k, (x, w_, h_) in enumerate(((960, 180, 420), (1160, 220, 520), (1400, 200, 380), (1620, 220, 480))):
        dx = math.sin(t * 40 + k) * amp
        d.rectangle([x + dx, base - h_, x + w_ + dx, base], outline=c, width=4)
        for wy in range(base - h_ + 30, base - 40, 60):
            for wx in range(x + 25, x + w_ - 30, 55):
                d.rectangle([wx + dx, wy, wx + 25 + dx, wy + 30], outline=c, width=2)
        if not stop and t > 1.5:
            rnd = random.Random(k)
            pts = [(x + w_ / 2 + dx, base - h_)]
            for j in range(6):
                pts.append((pts[-1][0] + rnd.uniform(-20, 20), pts[-1][1] + h_ / 7))
            d.line(pts, fill=col(b, "acc"), width=3)
    d.line([(900, base), (W, base)], fill=c, width=5)
    if b.get("stop"):
        k = ease(t / 0.3)
        d.text((1380, 300), "!", font=font(CINZEL9, 200), fill=col(b, "acc", int(255 * k)), anchor="mm")
    finish(img, b, L)


def art_earth_split(img, b, t, dur):
    b2 = dict(b); b2["stage"] = "NONE"
    A.SCR = type("S", (), {"NONE": []})
    A.art_globe(img, b2, t, dur, cx=1380, cy=540, R=360)
    L = layer(); d = ImageDraw.Draw(L)
    rnd = random.Random(4)
    pts = [(1380, 180)]
    for k in range(14):
        pts.append((1380 + rnd.uniform(-40, 40), 180 + (k + 1) * 52))
    stroke(d, pts, col(b, "acc"), 10, ease((t - .5) / 1.5))
    glow_layer(img, L, 20, 1.6)


def art_blackout(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "ink")
    base = 860
    off = t > 0.8
    rnd = random.Random(3)
    x = 940
    while x < 1820:
        w_ = rnd.randint(60, 120); h_ = rnd.randint(80, 200)
        d.rectangle([x, base - h_, x + w_, base], outline=c, width=3)
        for wy in range(base - h_ + 20, base - 20, 34):
            on = (not off) or rnd.random() < 0.0
            d.rectangle([x + 14, wy, x + 30, wy + 16], fill=col(b, "acc", 230) if on else col(b, "faint", 60))
        x += w_ + 10
    d.line([(900, base), (W, base)], fill=c, width=3)
    d.rectangle([1500, 380, 1700, 560], outline=c, width=4)
    d.text((1600, 600), "POWER STATION", font=font(MONO, 20), fill=col(b, "faint"), anchor="mm")
    finish(img, b, L)
    if 0.5 < t < 1.2:
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        bolt_burst(d2, 1600, 470, t, 4, 180, outer=(255, 180, 80, 220), rate=16)
        glow_layer(img, L2, 16, 1.5)
    if off:
        ImageDraw.Draw(img).rectangle([0, 0, W, H], fill=(0, 0, 0, int(80 * ease((t - .8) / .3))))


def art_earth_power(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    gy = 560
    d.line([(900, gy), (W, gy)], fill=col(b, "ink"), width=5)
    for k in range(6):
        y = gy + 40 + k * 60
        d.line([(900, y), (W, y)], fill=col(b, "faint", 100 - k * 12), width=2)
    d.line([(1000, gy), (1000, gy - 300)], fill=col(b, "ink"), width=6)
    circle(d, 1000, gy - 320, 30, col(b, "ink"), w=5)
    for k in range(5):
        r = ((t * 260 + k * 160) % 800)
        d.arc([1000 - r, gy - r * .4, 1000 + r, gy + r * .4], 0, 180, fill=col(b, "acc", int(255 * (1 - r / 800))), width=5)
    for k, x in enumerate((1450, 1650, 1820)):
        lit = ((t * 260) % 800) > (x - 1000) * 0.9 or t > 3
        d.line([(x, gy), (x, gy - 120)], fill=col(b, "ink"), width=4)
        circle(d, x, gy - 150, 30, col(b, "ink"), w=4)
        if lit:
            circle(d, x, gy - 150, 26, fill=col(b, "acc", 230))
    finish(img, b, L)


def art_lamps(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease((t - .3) / 2.5)
    n = 0
    for r in range(10):
        for c_ in range(20):
            x = 960 + c_ * 44 + (r % 2) * 22
            y = 320 + r * 58
            n += 1
            lit = n / 200 <= k
            d.line([(x, y + 14), (x, y + 30)], fill=col(b, "faint"), width=2)
            circle(d, x, y, 12, col(b, "ink"), fill=col(b, "acc", 240) if lit else None, w=2)
    d.text((1380, 980), f"{int(200 * k)} / 200", font=font(MONO, 30), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L, 16)


def art_mars(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    if b.get("planet"):
        circle(d, 1600, 380, 170, fill=(190, 80, 50, 255))
        for k in range(5):
            d.ellipse([1500 + k * 30, 300 + k * 30, 1560 + k * 30, 330 + k * 30], fill=(150, 60, 40, 255))
        for k in range(5):
            r = ((t * 150 + k * 90) % 450)
            d.arc([1600 - 170 - r, 380 - 170 - r, 1600 + 170 + r, 380 + 170 + r], 120, 220, fill=col(b, "ink", int(255 * (1 - r / 450))), width=3)
        rnd = random.Random(5)
        for k in range(120):
            d.point((rnd.uniform(900, W), rnd.uniform(100, 1000)), fill=(255, 255, 255, 200))
    x0, x1, cy = 960, 1500 if b.get("planet") else 1820, 700 if b.get("planet") else 560
    d.rectangle([x0, cy - 150, x1, cy + 150], outline=col(b, "ink"), width=4)
    pts = []
    for x in range(x0 + 10, x1 - 10, 3):
        u = (x - x0) / (x1 - x0)
        v = math.sin(x * 0.4 + t * 30) * 4
        for j, c0 in enumerate((0.25, 0.5, 0.75)):
            if abs(u - c0) < 0.02:
                v -= 100 * math.cos((u - c0) / 0.02 * math.pi / 2)
        pts.append((x, cy + v))
    d.line(pts, fill=col(b, "acc"), width=4)
    for j, c0 in enumerate((0.25, 0.5, 0.75)):
        if t > 0.6 + j * 0.6:
            d.text((x0 + (x1 - x0) * c0, cy - 190), str(j + 1), font=font(CINZEL9, 60), fill=col(b, "acc"), anchor="mm")
    finish(img, b, L)


def wardenclyffe(d, cx, base, s, c):
    for sx in (-1, 1):
        d.line([(cx + sx * 70 * s, base), (cx + sx * 30 * s, base - 520 * s)], fill=c, width=5)
    for k in range(10):
        y = base - k * 52 * s
        w_ = 70 * s - k * 4 * s
        d.line([(cx - w_, y), (cx + w_, y - 52 * s)], fill=c, width=2)
        d.line([(cx + w_, y), (cx - w_, y - 52 * s)], fill=c, width=2)
    d.chord([cx - 140 * s, base - 600 * s, cx + 140 * s, base - 460 * s], 180, 360, outline=c, width=5)
    d.line([(cx - 140 * s, base - 530 * s), (cx + 140 * s, base - 530 * s)], fill=c, width=5)
    d.rectangle([cx - 260 * s, base - 90 * s, cx - 120 * s, base], outline=c, width=4)
    return cx, base - 560 * s


def art_tower(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    c = col(b, "faint" if b.get("dark_tower") else "ink")
    cx, ty = wardenclyffe(d, 1380, 900, 1.25, c)
    d.line([(900, 900), (W, 900)], fill=c, width=3)
    if b.get("rings") or not b.get("dark_tower"):
        for k in range(5):
            r = ((t * 160 + k * 120) % 600)
            d.ellipse([cx - r * 1.6, ty - r * .5, cx + r * 1.6, ty + r * .5], outline=col(b, "acc", int(220 * (1 - r / 600))), width=4)
    finish(img, b, L)


def art_atlantic(img, b, t, dur):
    box = (900, 160, 1840, 940, -75, 10, 62, 30)
    L = layer(); d = ImageDraw.Draw(L)
    for c in WORLD:
        for ring in c["rings"]:
            if not any(-80 <= p[0] <= 15 and 25 <= p[1] <= 70 for p in ring[:10]):
                continue
            pts = [proj_eq(x, y, box) for x, y in ring]
            d.line(pts + [pts[0]], fill=col(b, "faint", 200), width=2)
    a = proj_eq(-5.2, 50.0, box)
    bb = proj_eq(-52.7, 47.6, box)
    arc = [(a[0] + (bb[0] - a[0]) * u, a[1] + (bb[1] - a[1]) * u - math.sin(u * math.pi) * 220) for u in [i / 40 for i in range(41)]]
    stroke(d, arc, col(b, "acc"), 5, ease((t - .3) / 2.0))
    for p, lab in ((a, "POLDHU"), (bb, "SIGNAL HILL")):
        circle(d, p[0], p[1], 10, fill=col(b, "acc"))
        d.text((p[0], p[1] + 34), lab, font=font(CINZEL7, 24), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def art_meter(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 540
    d.rounded_rectangle([cx - 230, cy - 320, cx + 230, cy + 320], 40, outline=col(b, "ink"), width=6)
    for k in range(4):
        dx = cx - 150 + k * 100
        circle(d, dx, cy - 150, 40, col(b, "ink"), w=4)
        a = t * (1 + k) * 0.8
        d.line([(dx, cy - 150), (dx + math.cos(a) * 32, cy - 150 + math.sin(a) * 32)], fill=col(b, "acc"), width=4)
    d.ellipse([cx - 160, cy + 60, cx + 160, cy + 110], outline=col(b, "ink"), width=4)
    ph = t * 4
    d.line([(cx + math.cos(ph) * 150, cy + 85), (cx + math.cos(ph) * 150, cy + 85)], fill=col(b, "acc"), width=8)
    d.text((cx + 330, cy - 200), "?", font=font(CINZEL9, 220), fill=col(b, "acc"), anchor="mm")
    finish(img, b, L)


def art_demolish(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease((t - 0.8) / 1.5)
    tw = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    wardenclyffe(ImageDraw.Draw(tw), 450, 880, 1.25, col(b, "ink"))
    tw = tw.rotate(-k * 40, center=(450, 880), resample=Image.BICUBIC)
    L.alpha_composite(tw, (930, 20))
    if t > 0.6:
        rnd = random.Random(2)
        ph = min(1, (t - .6) / 1.2)
        for j in range(30):
            a = rnd.uniform(-3.0, -0.1); sp = rnd.uniform(100, 500)
            x = 1380 + math.cos(a) * sp * ph; y = 880 + math.sin(a) * sp * ph + 300 * ph * ph
            d.rectangle([x - 8, y - 8, x + 8, y + 8], fill=col(b, "faint"))
        r = 80 + ph * 300
        d.ellipse([1380 - r, 880 - r * .7, 1380 + r, 880 + r * .3], fill=(255, 150, 60, int(200 * (1 - ph))))
    d.line([(900, 900), (W, 900)], fill=col(b, "ink"), width=3)
    finish(img, b, L)


def art_turbine(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 540
    for k in range(9):
        x = cx - 200 + k * 50
        d.ellipse([x - 30, cy - 260, x + 30, cy + 260], outline=col(b, "ink"), width=4)
        a = t * 8 + k * .4
        d.line([(x, cy), (x + math.cos(a) * 20, cy + math.sin(a) * 240)], fill=col(b, "acc"), width=3)
    d.line([(cx - 340, cy), (cx + 340, cy)], fill=col(b, "ink"), width=10)
    for k in range(8):
        ph = (t * .8 + k * .125) % 1
        y = cy - 220 + k * 60
        d.line([(1000 + ph * 200, y), (1100 + ph * 200, y)], fill=col(b, "acc", int(255 * (1 - ph))), width=4)
    finish(img, b, L)


def art_deathbeam(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, ty = wardenclyffe(d, 1000, 900, 0.9, col(b, "ink"))
    finish(img, b, L)
    L2 = layer(); d2 = ImageDraw.Draw(L2)
    k = ease((t - .5) / .5)
    ex = cx + 900 * k
    d2.line([(cx, ty), (ex, ty - 200 * k)], fill=col(b, "acc"), width=14)
    d2.line([(cx, ty), (ex, ty - 200 * k)], fill=(255, 255, 255, 255), width=4)
    for j in range(4):
        px = 1500 + j * 90
        py = 220 + j * 40 + (max(0, t - 1.2 - j * .3) ** 2) * 200
        d2.polygon([(px - 40, py), (px + 40, py), (px + 50, py - 8), (px - 30, py - 8)], fill=col(b, "ink"))
        d2.line([(px - 10, py - 4), (px + 10, py - 30)], fill=col(b, "ink"), width=6)
    glow_layer(img, L2, 20, 1.6)


def art_pigeons(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    d.rectangle([1000, 220, 1760, 860], outline=col(b, "ink"), width=8)
    d.line([(1380, 220), (1380, 860)], fill=col(b, "ink"), width=6)
    d.line([(1000, 540), (1760, 540)], fill=col(b, "ink"), width=6)
    d.text((1380, 180), "3327", font=font(MONO, 34), fill=col(b, "faint"), anchor="mm")
    for k in range(9):
        ph = (t * .12 + k * .11) % 1
        x = 940 + ph * 900
        y = 360 + math.sin(ph * 6 + k) * 120 + (k % 3) * 80
        f = math.sin(t * 10 + k) * 14
        c = (255, 255, 255, 255) if k == 4 else col(b, "faint")
        d.line([(x - 26, y - f), (x, y), (x + 26, y - f)], fill=c, width=5 if k == 4 else 3)
    finish(img, b, L)


def art_papers(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    for k in range(5):
        x0 = 1100 + k * 30; y0 = 260 + k * 24
        d.rectangle([x0, y0, x0 + 420, y0 + 560], fill=(232, 224, 200, 255), outline=(90, 80, 60, 255), width=3)
        for j in range(10):
            d.line([(x0 + 40, y0 + 80 + j * 40), (x0 + 380, y0 + 80 + j * 40)], fill=(150, 140, 120, 255), width=3)
    for j, (txt_, y) in enumerate((("CONFIDENTIAL", 420), ("SEIZED", 640))):
        k = ease_out((t - 0.5 - j * 0.5) / 0.25)
        if k > 0:
            s = 1.5 - 0.5 * k
            st = Image.new("RGBA", (520, 120), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            sd.rectangle([4, 4, 516, 116], outline=(180, 30, 30, 230), width=8)
            sd.text((260, 60), txt_, font=font(CINZEL9, 56), fill=(180, 30, 30, 230), anchor="mm")
            st = st.resize((int(520 * s * .8), int(120 * s * .8))).rotate(-8 + j * 10, expand=True)
            L.alpha_composite(st, (int(1370 - st.width / 2), int(y - st.height / 2)))
    img.alpha_composite(L)


def art_court(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    d.rectangle([1000, 220, 1500, 880], fill=(238, 228, 204, 255), outline=(90, 80, 60, 255), width=4)
    d.text((1250, 290), "PATENT No. 645,576", font=font(CINZEL7, 30), fill=(60, 40, 30, 255), anchor="mm")
    for j in range(10):
        d.line([(1040, 360 + j * 40), (1460, 360 + j * 40)], fill=(150, 140, 120, 255), width=3)
    k = ease_out((t - .9) / .25)
    if k > 0:
        d.text((1250, 780), "UPHELD", font=font(CINZEL9, 70), fill=(30, 110, 60, int(255 * k)), anchor="mm")
    a = -0.9 + 0.4 * ease(t / .9)
    hx, hy = 1680, 520
    gl = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rectangle([260, 60, 340, 380], fill=col(b, "ink"))
    gd.rounded_rectangle([160, 20, 440, 120], 30, fill=col(b, "ink"))
    gl = gl.rotate(math.degrees(a), center=(300, 380), resample=Image.BICUBIC)
    L.alpha_composite(gl, (hx - 300, hy - 200))
    img.alpha_composite(L)


def art_unit(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 540
    for k in range(6):
        rx = 180 + k * 60
        d.ellipse([cx - rx, cy - rx * .55, cx + rx, cy + rx * .55], outline=col(b, "acc", 200 - k * 25), width=3)
    ph = t * 2
    for k in range(6):
        rx = 180 + k * 60
        a = ph + k
        circle(d, cx + math.cos(a) * rx, cy + math.sin(a) * rx * .55, 7, fill=col(b, "ink"))
    d.text((cx, cy), "1 T", font=font(CINZEL9, 170), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L, 20)


def art_finale(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease(t / max(1, dur * .7))
    cx, cy = W / 2, 560
    for r in range(600, 50, -40):
        circle(d, cx, cy, r * (0.4 + 0.6 * k), fill=(255, 220, 140, int(14 + (600 - r) / 30)))
    for j in range(24):
        a = j * math.pi / 12 + t * 0.15
        d.line([(cx + math.cos(a) * 140, cy + math.sin(a) * 140), (cx + math.cos(a) * (300 + 400 * k), cy + math.sin(a) * (300 + 400 * k))], fill=(255, 230, 160, 90), width=4)
    finish(img, b, L, 26)
    if (t % 1.6) < 0.25:
        L2 = layer(); d2 = ImageDraw.Draw(L2)
        bolt_burst(d2, cx, cy - 300, t, 3, 400, outer=(255, 220, 140, 200), rate=10)
        glow_layer(img, L2, 18, 1.5)


TESLA_ARTS = {
    "colorado": art_colorado, "switch": art_switch, "coil_big": art_coil_big, "portrait": art_portrait, "four": art_four,
    "question": art_question, "title": art_title, "birthmap": art_birthmap, "village_storm": art_village_storm, "candle": art_candle,
    "mind": art_mind, "dynamo": art_dynamo, "laugh": art_laugh, "park": art_park, "rmf": art_rmf, "sand": art_sand,
    "acwave": art_acwave, "skyline": art_skyline, "bulb": art_bulb, "door": art_door, "ditch": art_ditch, "motor": art_motor,
    "versus": art_versus, "distance": art_distance, "danger": art_danger, "worldsfair": art_worldsfair, "niagara": art_niagara,
    "contract": art_contract, "tubes": art_tubes, "body": art_body, "labfire": A.art_fire, "xray": art_xray, "boat": art_boat,
    "oscillator": art_oscillator, "shaking": art_shaking, "earth_split": art_earth_split, "blackout": art_blackout,
    "earth_power": art_earth_power, "lamps": art_lamps, "mars": art_mars, "tower": art_tower, "atlantic": art_atlantic,
    "meter": art_meter, "demolish": art_demolish, "turbine": art_turbine, "deathbeam": art_deathbeam, "pigeons": art_pigeons,
    "papers": art_papers, "court": art_court, "unit": art_unit, "finale": art_finale,
    "chapter": A.art_chapter, "counter": A.art_counter,
}
LAYOUT = {
    "counter": ("center", W / 2, 200, 78), "title": ("center", W / 2, 620, 92), "chapter": ("none", 0, 0, 0),
    "finale": ("center", W / 2, 140, 92), "portrait": ("left", 110, 380, 120), "endcard": ("none", 0, 0, 0),
}
