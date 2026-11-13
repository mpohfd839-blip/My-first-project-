"""Illustrations (line-art, maps, charts) for each beat. Each art(img, b, t, dur) draws onto RGBA 1920x1080."""
import math, random, json, functools
from PIL import Image, ImageDraw, ImageFilter
from core import (W, H, PAL, font, ease, ease_out, stroke, circle, arc_pts, glow_layer, polyline_partial,
                  CINZEL9, CINZEL7, CINZEL4, PLAYI, GARA, GARAI, MONO)
SCR = None

WORLD = json.load(open("world.json"))
BYNAME = {c["name"]: c for c in WORLD}


def col(b, k="ink", a=255):
    return PAL[b["pal"]][k] + (a,)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def finish(img, b, L, glow=12):
    if PAL[b["pal"]]["glow"]:
        glow_layer(img, L, glow, 1.2)
    else:
        img.alpha_composite(L)


# ------------------------------------------------------------------ maps
def proj_eq(lon, lat, box):
    x0, y0, x1, y1, lon0, lon1, lat0, lat1 = box
    return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0), y0 + (lat0 - lat) / (lat0 - lat1) * (y1 - y0))


WORLD_BOX = (60, 150, 1860, 930, -180, 180, 84, -58)


def draw_map(img, b, t, dur, box=WORLD_BOX, fill_set=(), fill_k=None, outline_prog=1.0, fillcol=None, names_alpha=None, exclude=("Antarctica",)):
    L = layer()
    d = ImageDraw.Draw(L)
    ink = col(b, "faint", 220)
    fc = fillcol or col(b, "acc", 235)
    for c in WORLD:
        if c["name"] in exclude:
            continue
        k = 0.0
        if c["name"] in fill_set:
            k = 1.0 if fill_k is None else fill_k(c["name"])
        for ring in c["rings"]:
            pts = [proj_eq(x, y, box) for x, y in ring]
            if k > 0.01:
                d.polygon(pts, fill=fc[:3] + (int(fc[3] * k),))
            if outline_prog >= 1:
                d.line(pts + [pts[0]], fill=ink, width=2)
            else:
                stroke(d, pts, ink, 2, outline_prog, closed=True)
    finish(img, b, L, 8)
    return L


@functools.lru_cache(maxsize=None)
def centroid(name):
    c = BYNAME[name]
    best = max(c["rings"], key=len)
    xs = [p[0] for p in best]; ys = [p[1] for p in best]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def stage(name):
    return getattr(SCR, name)


def art_map(img, b, t, dur):
    st = stage(b.get("stage", "S1920"))
    if b.get("add"):
        st = st + b["add"]
    if b.get("grow_from"):
        ux, uy = centroid("United Kingdom")
        def fk(n):
            cx, cy = centroid(n)
            dist = math.hypot(cx - ux, cy - uy) / 200
            return ease((t - 0.3 - dist * 3.0) / 0.5)
        draw_map(img, b, t, dur, fill_set=st, fill_k=fk)
    elif b.get("shrink_from"):
        st0 = stage(b["shrink_from"])
        gone = [c for c in st0 if c not in st]
        def fk(n):
            if n in gone:
                i = gone.index(n)
                return 1 - ease((t - 0.4 - i * (dur * 0.7 / max(1, len(gone)))) / 0.4)
            return 1.0
        draw_map(img, b, t, dur, fill_set=st0, fill_k=fk)
    else:
        def fk(n):
            if b.get("add") and n in b["add"]:
                return 0.55 + 0.45 * math.sin(t * 4)
            return ease((t - 0.2) / 1.0)
        draw_map(img, b, t, dur, fill_set=st, fill_k=fk)
    # pin on London
    d = ImageDraw.Draw(img)
    x, y = proj_eq(-0.1, 51.5, WORLD_BOX)
    r = 8 + 4 * math.sin(t * 5)
    circle(d, x, y, r + 8, col(b, "ink", 180), w=2)
    circle(d, x, y, 6, fill=col(b, "ink"))


def art_routes(img, b, t, dur, cables=False):
    st = stage(b.get("stage", "S1860"))
    draw_map(img, b, t, dur, fill_set=st, fillcol=col(b, "acc", 120))
    L = layer()
    d = ImageDraw.Draw(L)
    P = lambda lo, la: proj_eq(lo, la, WORLD_BOX)
    london = (-0.1, 51.5)
    if not cables:
        routes = [[london, (-10, 45), (-20, 20), (-15, 0), (10, -30), (20, -36), (45, -25), (60, 5), (72.8, 19)],
                  [london, (-10, 45), (-40, 30), (-62, 18), (-77, 18)],
                  [(72.8, 19), (80, 6), (95, 5), (104, 1.3), (114, 22.3)],
                  [(20, -36), (60, -40), (115, -35), (151, -34)],
                  [london, (-30, 50), (-60, 46), (-74, 40.7)]]
    else:
        routes = [[london, (-9, 38.7), (-5.4, 36), (14.5, 35.9), (29.9, 31.2), (32.5, 30), (32.5, 29.9), (43, 12.8), (45, 12.8), (60, 18), (72.8, 19)]]
        if b.get("full"):
            routes += [[(72.8, 19), (80, 7), (96, 3), (104, 1.3), (115, -8), (130, -12), (151, -34), (174.8, -41.3), (184, -25)], [(-178, -20), (-150, 5), (-123, 49), (-80, 44), (-60, 46), (-30, 50), london],
                       [london, (-15, 15), (-17, 14.7), (-10, -15), (18.4, -33.9)]]
    for ri, r in enumerate(routes):
        pts = [P(*q) for q in r]
        prog = ease((t - 0.4 - ri * 0.35) / 2.2)
        pp = polyline_partial(pts, prog)
        if len(pp) > 1:
            if cables:
                d.line(pp, fill=(220, 40, 40, 255) if PAL[b["pal"]]["glow"] else col(b, "acc"), width=5, joint="curve")
            else:
                # dashed
                for i in range(len(pp) - 1):
                    a, c_ = pp[i], pp[i + 1]
                    segL = math.hypot(c_[0] - a[0], c_[1] - a[1])
                    n = max(1, int(segL / 16))
                    for k in range(0, n, 2):
                        u0, u1 = k / n, min(1, (k + 1) / n)
                        d.line([(a[0] + (c_[0] - a[0]) * u0, a[1] + (c_[1] - a[1]) * u0), (a[0] + (c_[0] - a[0]) * u1, a[1] + (c_[1] - a[1]) * u1)], fill=col(b, "ink"), width=4)
            if prog >= 1:
                ph = ((t * 0.25 + ri * 0.3) % 1)
                q = polyline_partial(pts, ph)[-1]
                if cables:
                    circle(d, q[0], q[1], 7, fill=(255, 240, 200, 255))
                else:
                    d.polygon([(q[0] - 10, q[1] + 6), (q[0] + 10, q[1] + 6), (q[0] + 6, q[1] + 12), (q[0] - 6, q[1] + 12)], fill=col(b, "ink"))
                    d.line([(q[0], q[1] + 6), (q[0], q[1] - 12)], fill=col(b, "ink"), width=2)
                    d.polygon([(q[0], q[1] - 12), (q[0] + 9, q[1] + 2), (q[0], q[1] + 2)], fill=col(b, "ink"))
    finish(img, b, L)


def art_cables(img, b, t, dur):
    art_routes(img, b, t, dur, cables=True)


INDIA_BOX = (980, 140, 1820, 980, 60, 100, 38, 4)


def art_map_india(img, b, t, dur):
    st = b.get("stage_india", 0)
    names = ["India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "Bhutan", "Myanmar", "Afghanistan", "China", "Iran"]
    L = layer()
    d = ImageDraw.Draw(L)
    for n in names:
        c = BYNAME[n]
        sub = n in ("India", "Pakistan", "Bangladesh", "Sri Lanka")
        for ring in c["rings"]:
            pts = [proj_eq(x, y, INDIA_BOX) for x, y in ring]
            if st >= 1 and sub:
                if st == 1:
                    # Bengal only: clip by longitude > 84
                    pts2 = [proj_eq(max(x, 84), y, INDIA_BOX) for x, y in ring if True]
                    k = ease((t - 0.3) / 1.2)
                    d.polygon(pts2, fill=col(b, "acc", int(200 * k)))
                else:
                    k = ease((t - 0.3 - (0 if n == "India" else 0.8)) / 1.5)
                    d.polygon(pts, fill=col(b, "acc", int(210 * k)))
            stroke(d, pts, col(b, "ink" if sub else "faint"), 3 if sub else 2, ease(t / 1.6), closed=True)
    if st == 0:
        x, y = proj_eq(72.8, 21.2, INDIA_BOX)
        r = 10 + 5 * math.sin(t * 5)
        circle(d, x, y, r + 10, col(b, "acc"), w=3)
        circle(d, x, y, 8, fill=col(b, "acc"))
        d.text((x - 24, y), "SURAT", font=font(CINZEL7, 30), fill=col(b, "ink"), anchor="rm")
    finish(img, b, L)


def art_africa(img, b, t, dur):
    box = (900, 110, 1800, 1000, -20, 55, 38, -36)
    colonizer = {}
    for n in ["Egypt", "Sudan", "S. Sudan", "Uganda", "Kenya", "Tanzania", "Zambia", "Zimbabwe", "Malawi", "Botswana", "South Africa", "Nigeria", "Ghana", "Sierra Leone", "Gambia", "Somaliland", "Lesotho", "eSwatini", "Namibia"]:
        colonizer[n] = "GB"
    for n in ["Algeria", "Morocco", "Tunisia", "Mali", "Niger", "Chad", "Mauritania", "Senegal", "Guinea", "Côte d'Ivoire", "Burkina Faso", "Benin", "Gabon", "Congo", "Central African Rep.", "Madagascar", "Cameroon", "Togo", "Djibouti"]:
        colonizer[n] = "FR"
    for n in ["Angola", "Mozambique", "Guinea-Bissau"]:
        colonizer[n] = "PT"
    for n in ["Dem. Rep. Congo", "Rwanda", "Burundi"]:
        colonizer[n] = "BE"
    for n in ["Libya", "Eritrea", "Somalia"]:
        colonizer[n] = "IT"
    cols = {"GB": col(b, "acc", 220), "FR": (70, 110, 170, 200), "PT": (90, 140, 90, 200), "BE": (200, 160, 60, 200), "IT": (150, 110, 160, 200)}
    L = layer()
    d = ImageDraw.Draw(L)
    afr = [c for c in WORLD if any(-20 <= p[0] <= 55 and -36 <= p[1] <= 38 for r in c["rings"] for p in r[:1])]
    for c in afr:
        cz = colonizer.get(c["name"])
        for ring in c["rings"]:
            pts = [proj_eq(x, y, box) for x, y in ring]
            if cz:
                k = ease((t - 0.5 - (hash(c["name"]) % 10) * 0.12) / 0.6)
                d.polygon(pts, fill=cols[cz][:3] + (int(cols[cz][3] * k),))
            d.line(pts + [pts[0]], fill=col(b, "ink", 200), width=2)
    if b.get("lines"):
        rnd = random.Random(3)
        for i in range(9):
            y = 300 + i * 70
            x0 = 950 + rnd.uniform(0, 300)
            prog = ease((t - 0.3 - i * 0.25) / 0.6)
            stroke(d, [(x0, y), (x0 + 500 + rnd.uniform(-100, 100), y + rnd.uniform(-60, 60))], col(b, "ink"), 4, prog)
        # ruler
        rx = 900 + 900 * ease(t / max(1, dur))
        d.rectangle([rx - 20, 150, rx + 20, 980], outline=col(b, "ink"), width=3)
        for k in range(0, 830, 30):
            d.line([(rx - 20, 150 + k), (rx - 8, 150 + k)], fill=col(b, "ink"), width=2)
    lx = 120
    for i, (k, nm) in enumerate((("GB", "BRITAIN"), ("FR", "FRANCE"), ("PT", "PORTUGAL"), ("BE", "BELGIUM"), ("IT", "ITALY"))):
        y = 760 + i * 40
        d.rectangle([lx, y, lx + 26, y + 26], fill=cols[k])
        d.text((lx + 40, y + 13), nm, font=font(CINZEL7, 24), fill=col(b, "ink"), anchor="lm")
    finish(img, b, L)


def art_island(img, b, t, dur):
    box = (1000, 120, 1700, 1000, -11, 2.5, 59.5, 49.5)
    L = layer()
    d = ImageDraw.Draw(L)
    for n in ("United Kingdom", "Ireland"):
        for ring in BYNAME[n]["rings"]:
            pts = [proj_eq(x, y, box) for x, y in ring]
            stroke(d, pts, col(b, "ink"), 4, ease(t / 2.0), closed=True)
            for k in range(1, 4):
                cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
                off = [(cx + (x - cx) * (1 + .08 * k), cy + (y - cy) * (1 + .06 * k)) for x, y in pts]
                stroke(d, off, col(b, "faint", 120 - 30 * k), 2, ease((t - 0.4 * k) / 2.0), closed=True)
    x, y = proj_eq(-0.1, 51.5, box)
    circle(d, x, y, 9, fill=col(b, "acc"))
    d.text((x + 18, y), "LONDON", font=font(CINZEL7, 26), fill=col(b, "ink"), anchor="lm")
    # compass
    cx, cy = 1760, 260
    circle(d, cx, cy, 60, col(b, "faint"), w=2)
    d.polygon([(cx, cy - 70), (cx + 10, cy), (cx, cy + 70), (cx - 10, cy)], fill=col(b, "ink"))
    d.text((cx, cy - 90), "N", font=font(CINZEL7, 24), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


# ------------------------------------------------------------------ globe
def ortho(lon, lat, lon0, lat0, cx, cy, R):
    lam, phi = math.radians(lon), math.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    cosc = math.sin(p0) * math.sin(phi) + math.cos(p0) * math.cos(phi) * math.cos(lam - l0)
    x = R * math.cos(phi) * math.sin(lam - l0)
    y = R * (math.cos(p0) * math.sin(phi) - math.sin(p0) * math.cos(phi) * math.cos(lam - l0))
    return cx + x, cy - y, cosc


def art_globe(img, b, t, dur, cx=1380, cy=560, R=380):
    st = stage(b.get("stage", "S1920"))
    lon0 = -40 + t * 9
    lat0 = 20
    L = layer()
    d = ImageDraw.Draw(L)
    circle(d, cx, cy, R, col(b, "ink"), fill=PAL[b["pal"]]["bg"] + (255,), w=3)
    for lat in range(-60, 90, 30):
        pts = [ortho(lo, lat, lon0, lat0, cx, cy, R) for lo in range(-180, 181, 6)]
        seg = []
        for x, y, c in pts:
            if c > 0:
                seg.append((x, y))
            else:
                if len(seg) > 1:
                    d.line(seg, fill=col(b, "faint", 140), width=1)
                seg = []
        if len(seg) > 1:
            d.line(seg, fill=col(b, "faint", 140), width=1)
    for lo in range(-180, 180, 30):
        pts = [ortho(lo, la, lon0, lat0, cx, cy, R) for la in range(-90, 91, 6)]
        seg = []
        for x, y, c in pts:
            if c > 0:
                seg.append((x, y))
            else:
                if len(seg) > 1:
                    d.line(seg, fill=col(b, "faint", 140), width=1)
                seg = []
        if len(seg) > 1:
            d.line(seg, fill=col(b, "faint", 140), width=1)
    for c in WORLD:
        if c["name"] == "Antarctica":
            continue
        emp = c["name"] in st
        for ring in c["rings"]:
            pp = [ortho(x, y, lon0, lat0, cx, cy, R) for x, y in ring]
            vis = [p[2] > 0.02 for p in pp]
            if all(vis):
                pts = [(p[0], p[1]) for p in pp]
                if emp:
                    d.polygon(pts, fill=col(b, "acc", 230))
                d.line(pts + [pts[0]], fill=col(b, "ink", 230), width=2)
            elif any(vis):
                seg = []
                for p, v in zip(pp, vis):
                    if v:
                        seg.append((p[0], p[1]))
                    elif len(seg) > 1:
                        d.line(seg, fill=col(b, "ink", 230), width=2); seg = []
                    else:
                        seg = []
                if len(seg) > 1:
                    d.line(seg, fill=col(b, "ink", 230), width=2)
    if b.get("sun"):
        a = t * 0.6
        sx, sy = cx + math.cos(a) * (R + 160), cy - 120 + math.sin(a) * 60
        for k in range(12):
            ang = k * math.pi / 6 + t
            d.line([(sx + math.cos(ang) * 50, sy + math.sin(ang) * 50), (sx + math.cos(ang) * 75, sy + math.sin(ang) * 75)], fill=(255, 200, 90, 255), width=5)
        circle(d, sx, sy, 40, fill=(255, 210, 110, 255))
    finish(img, b, L, 14)


# ------------------------------------------------------------------ icons / scenes
def ship_pts(x, y, s, rock=0.0):
    def R(px, py):
        a = math.radians(rock)
        dx, dy = px * s, py * s
        return (x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a))
    hull = [R(-170, -20), R(170, -40), R(140, 30), R(-130, 30)]
    masts = [[R(-80, -20), R(-80, -260)], [R(10, -26), R(10, -320)], [R(100, -32), R(100, -240)]]
    sails = []
    for mx, top, h in ((-80, -250, 200), (10, -310, 260), (100, -230, 180)):
        for k in range(3):
            y0 = top + k * h / 3
            sails.append([R(mx - 60 + k * 6, y0 + 10), R(mx + 60 - k * 6, y0 + 10), R(mx + 52 - k * 6, y0 + h / 3 - 6), R(mx - 52 + k * 6, y0 + h / 3 - 6)])
    bow = [R(170, -40), R(260, -110)]
    return hull, masts, sails, bow


def draw_ship(d, x, y, s, c, t, prog=1.0, rock=0.0, guns=False, fill=None):
    hull, masts, sails, bow = ship_pts(x, y, s, rock)
    if fill:
        d.polygon(hull, fill=fill)
    stroke(d, hull, c, 4, prog, closed=True)
    for m in masts:
        stroke(d, m, c, 4, prog)
    stroke(d, bow, c, 3, prog)
    for i, sl in enumerate(sails):
        stroke(d, sl, c, 3, ease((prog - 0.3 - i * 0.03) / 0.5), closed=True)
    if guns:
        for k in range(10):
            gx = x + (-120 + k * 26) * s
            gy = y + (-4 - k * 1.5) * s
            d.rectangle([gx - 7 * s, gy - 6 * s, gx + 7 * s, gy + 6 * s], fill=c)


def waves(d, c, t, y0=820, n=4, amp=10):
    for k in range(n):
        y = y0 + k * 34
        pts = [(x, y + math.sin(x * 0.012 + t * 1.6 + k) * amp) for x in range(820, W, 12)]
        d.line(pts, fill=c[:3] + (max(60, 220 - k * 45),), width=3)


def art_ship(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    rock = math.sin(t * 1.2) * 3
    bob = math.sin(t * 1.4) * 8
    draw_ship(d, 1350, 760 + bob, 1.35, col(b, "ink"), t, ease(t / 2.2), rock, guns=b["art"] == "ship_guns")
    waves(d, col(b, "ink"), t)
    if b["art"] == "ship_guns":
        n = int(100 * ease((t - 1.0) / 2.0))
        d.text((1350, 220), f"{n}", font=font(CINZEL9, 120), fill=col(b, "acc"), anchor="mm")
        d.text((1350, 300), "GUNS", font=font(CINZEL7, 32), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def art_fleet(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    for i in range(5):
        x = 920 + i * 200
        draw_ship(d, x, 520 + (i % 2) * 20 + math.sin(t + i) * 5, 0.45, col(b, "faint"), t, ease((t - i * .1) / 1.5), math.sin(t + i) * 2)
    for i in range(4):
        x = 1050 + i * 190 + (0 if b.get("calm") else t * 12)
        draw_ship(d, x, 800 + math.sin(t + i) * 6, 0.55, col(b, "ink"), t, ease((t - .5 - i * .1) / 1.5), math.sin(t * 1.2 + i) * 2)
    waves(d, col(b, "ink"), t, 860, 3, 8)
    if not b.get("calm"):
        rnd = random.Random(int(t * 3))
        for k in range(8):
            ph = (t * 0.8 + k * 0.37) % 1.4
            if ph < 1.0:
                x = 980 + (k * 137) % 800
                y = 640 + (k * 53) % 160
                r = 20 + ph * 70
                d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(230, 225, 215, int(160 * (1 - ph))))
                if ph < 0.12:
                    d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=(255, 210, 120, 255))
    finish(img, b, L)


def art_compass(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy, R = 1380, 560, 300
    circle(d, cx, cy, R, col(b, "ink"), w=4)
    circle(d, cx, cy, R - 30, col(b, "faint"), w=2)
    for k in range(60):
        a = k * math.pi / 30
        r0 = R - (40 if k % 5 == 0 else 28)
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (R - 18), cy + math.sin(a) * (R - 18))], fill=col(b, "ink"), width=3 if k % 5 == 0 else 1)
    rot = math.sin(t * 0.8) * 0.15
    for k in range(8):
        a = k * math.pi / 4 + rot - math.pi / 2
        Lr = R - 60 if k % 2 == 0 else R - 150
        tip = (cx + math.cos(a) * Lr, cy + math.sin(a) * Lr)
        l1 = (cx + math.cos(a + .25) * 40, cy + math.sin(a + .25) * 40)
        l2 = (cx + math.cos(a - .25) * 40, cy + math.sin(a - .25) * 40)
        d.polygon([tip, l1, (cx, cy), l2], fill=col(b, "acc" if k == 0 else "ink", 255 if k % 2 == 0 else 160))
    for k, s in enumerate("NESW"):
        a = k * math.pi / 2 - math.pi / 2 + rot
        d.text((cx + math.cos(a) * (R + 40), cy + math.sin(a) * (R + 40)), s, font=font(CINZEL9, 40), fill=col(b, "ink"), anchor="mm")
    # chronometer second hand
    a = (t % 60) / 60 * 2 * math.pi - math.pi / 2
    d.line([(cx, cy), (cx + math.cos(a) * (R - 50), cy + math.sin(a) * (R - 50))], fill=col(b, "acc"), width=3)
    finish(img, b, L)


def art_counter(img, b, t, dur):
    d = ImageDraw.Draw(img)
    a0, a1 = b.get("count", (0, 100))
    k = ease_out(t / max(1.0, dur * 0.6))
    v = int(a0 + (a1 - a0) * k)
    L = layer(); dl = ImageDraw.Draw(L)
    dl.text((W / 2, 470), b.get("prefix", "") + f"{v:,}", font=font(CINZEL9, 190), fill=col(b, "acc"), anchor="mm")
    # people row
    n = 40
    for i in range(n):
        if i / n > k:
            break
        x = W / 2 - 780 + i * 40
        y = 700
        dl.ellipse([x - 8, y - 30, x + 8, y - 14], fill=col(b, "ink", 220))
        dl.rounded_rectangle([x - 11, y - 12, x + 11, y + 20], 6, fill=col(b, "ink", 220))
    finish(img, b, L, 18)


def art_four(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    labels = ["SHIPS", "MONEY", "MACHINES", "DIVISION"] if not b.get("flags") else ["ENGLAND", "DUTCH", "PORTUGAL", "FRANCE"]
    for i in range(4):
        k = ease((t - 0.3 - i * 0.45) / 0.5)
        if k <= 0:
            continue
        cx = 1000 + (i % 2) * 400
        cy = 330 + (i // 2) * 350
        a = int(255 * k)
        c = col(b, "ink", a)
        circle(d, cx, cy, 120, col(b, "faint", a), w=3)
        if b.get("flags"):
            fl = [((255, 255, 255), (200, 30, 40)), ((200, 60, 40), (255, 255, 255), (40, 70, 160)), ((0, 120, 60), (210, 30, 40)), ((40, 70, 160), (255, 255, 255), (210, 30, 40))][i]
            x0, y0 = cx - 80, cy - 52
            if i == 0:
                d.rectangle([x0, y0, x0 + 160, y0 + 104], fill=(255, 255, 255, a))
                d.rectangle([x0 + 66, y0, x0 + 94, y0 + 104], fill=(200, 30, 40, a))
                d.rectangle([x0, y0 + 40, x0 + 160, y0 + 64], fill=(200, 30, 40, a))
            elif i in (1,):
                for j, cc in enumerate(fl):
                    d.rectangle([x0, y0 + j * 35, x0 + 160, y0 + j * 35 + 35], fill=cc + (a,))
            else:
                for j, cc in enumerate(fl):
                    w_ = 160 / len(fl)
                    d.rectangle([x0 + j * w_, y0, x0 + (j + 1) * w_, y0 + 104], fill=cc + (a,))
        else:
            if i == 0:
                draw_ship(d, cx - 10, cy + 40, 0.28, c, t, 1.0)
            elif i == 1:
                for j in range(4):
                    d.ellipse([cx - 50, cy + 40 - j * 22 - 14, cx + 50, cy + 40 - j * 22 + 14], outline=c, width=4, fill=PAL[b["pal"]]["bg"] + (a,))
                d.text((cx, cy - 50), "£", font=font(CINZEL9, 60), fill=c, anchor="mm")
            elif i == 2:
                rot = t * 1.5
                for j in range(10):
                    an = rot + j * math.pi / 5
                    d.line([(cx + math.cos(an) * 45, cy + math.sin(an) * 45), (cx + math.cos(an) * 75, cy + math.sin(an) * 75)], fill=c, width=16)
                circle(d, cx, cy, 55, c, w=10)
            else:
                d.line([(cx - 70, cy), (cx - 10, cy)], fill=c, width=6)
                d.line([(cx + 10, cy), (cx + 70, cy)], fill=c, width=6)
                d.line([(cx, cy - 80), (cx, cy + 80)], fill=col(b, "acc", a), width=6)
                for s in (-1, 1):
                    d.polygon([(cx + s * 70, cy - 14), (cx + s * 92, cy), (cx + s * 70, cy + 14)], fill=c)
        d.text((cx, cy + 150), labels[i], font=font(CINZEL7, 30), fill=c, anchor="mm")
    finish(img, b, L)


def art_title(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    crown(d, W / 2, 300, 1.0, col(b, "acc"), ease(t / 1.5))
    for s in (-1, 1):
        stroke(d, [(W / 2 + s * 140, 420), (W / 2 + s * 700, 420)], col(b, "faint"), 2, ease((t - .3) / 1.0))
    finish(img, b, L, 20)
    rnd = random.Random(1)
    d2 = ImageDraw.Draw(img)
    for k in range(70):
        x = rnd.uniform(200, W - 200)
        y = (rnd.uniform(0, H) - t * rnd.uniform(20, 60)) % H
        r = rnd.uniform(1, 3)
        d2.ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 120, int(120 + 100 * math.sin(t * 3 + k))))


def crown(d, cx, cy, s, c, prog=1.0):
    pts = [(cx - 150 * s, cy + 60 * s), (cx - 170 * s, cy - 60 * s), (cx - 85 * s, cy), (cx, cy - 110 * s), (cx + 85 * s, cy), (cx + 170 * s, cy - 60 * s), (cx + 150 * s, cy + 60 * s)]
    stroke(d, pts, c, 6, prog, closed=True)
    stroke(d, [(cx - 155 * s, cy + 90 * s), (cx + 155 * s, cy + 90 * s)], c, 6, prog)
    if prog >= 0.9:
        for x, y in pts[1:6:2] + [pts[3]]:
            circle(d, x, y - 18 * s, 14 * s, fill=c)
        d.line([(cx, cy - 150 * s), (cx, cy - 200 * s)], fill=c, width=int(8 * s))
        d.line([(cx - 22 * s, cy - 178 * s), (cx + 22 * s, cy - 178 * s)], fill=c, width=int(8 * s))


def art_crown(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    crown(d, 1380, 560, 1.6, col(b, "acc"), ease(t / 1.8))
    rnd = random.Random(2)
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        r = 330 + rnd.uniform(0, 60)
        ph = (t * 0.7 + k * .3) % 1
        x, y = 1380 + math.cos(a) * r, 560 + math.sin(a) * r * .6
        s = 10 * math.sin(ph * math.pi)
        d.line([(x - s, y), (x + s, y)], fill=col(b, "ink"), width=3)
        d.line([(x, y - s), (x, y + s)], fill=col(b, "ink"), width=3)
    finish(img, b, L, 20)


def art_chapter(img, b, t, dur):
    p = PAL[b["pal"]]
    L = layer(); d = ImageDraw.Draw(L)
    k = ease(t / 0.8)
    d.text((W / 2, 300), b.get("num", "I"), font=font(CINZEL9, 220), fill=p["faint"] + (int(160 * k),), anchor="mm")
    d.text((W / 2, 470), "CHAPTER", font=font(CINZEL7, 30), fill=p["acc"] + (int(255 * k),), anchor="mm")
    d.text((W / 2, 560), b.get("chtitle", ""), font=font(CINZEL9, 104), fill=p["ink"] + (int(255 * ease((t - .3) / .7)),), anchor="mm")
    wl = 520 * ease((t - .4) / .8)
    d.line([(W / 2 - wl, 640), (W / 2 + wl, 640)], fill=p["acc"] + (255,), width=4)
    d.ellipse([W / 2 - 9, 631, W / 2 + 9, 649], fill=p["acc"] + (255,))
    finish(img, b, L, 18)


def art_charter(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 1000, 160, 1720, 940
    k = ease(t / 0.9)
    d.rectangle([x0, y0 + (1 - k) * 300, x1, y1 - (1 - k) * 300], fill=(240, 228, 198, 255), outline=(120, 96, 66, 255), width=4)
    for yy in (y0, y1):
        d.ellipse([x0 - 30, yy - 30 + (1 - k) * (300 if yy == y0 else -300), x1 + 30, yy + 30 + (1 - k) * (300 if yy == y0 else -300)], outline=(120, 96, 66, 255), width=4)
    if k >= 1:
        d.text(((x0 + x1) / 2, y0 + 90), "By the Queen", font=font(GARAI, 52), fill=(60, 40, 30, 255), anchor="mm")
        rnd = random.Random(4)
        n = 14
        for i in range(n):
            y = y0 + 170 + i * 40
            prog = ease((t - 0.8 - i * 0.12) / 0.5)
            pts = [(x0 + 60 + j * 12, y + math.sin(j * 1.7 + i) * 6) for j in range(int(48 * (0.7 + 0.3 * rnd.random())))]
            stroke(d, pts, (70, 52, 36, 255), 2, prog)
        sp = ease((t - 2.4) / 1.4)
        if sp > 0:
            sig = [(1280 + j * 9, 860 + math.sin(j * .5) * 22 - j * 0.6) for j in range(40)]
            stroke(d, sig, (30, 30, 60, 255), 4, sp)
            d.text((1460, 880), "Elizabeth R", font=font(GARAI, 46), fill=(30, 30, 60, int(255 * sp)), anchor="lm")
        if b.get("seal"):
            s = ease_out((t - 1.0) / 0.4)
            r = 70 * (1.4 - 0.4 * s) if s > 0 else 0
            if s > 0:
                d.ellipse([1110 - r, 840 - r, 1110 + r, 840 + r], fill=(160, 30, 30, int(255 * s)))
                d.ellipse([1110 - r * .7, 840 - r * .7, 1110 + r * .7, 840 + r * .7], outline=(110, 18, 18, 255), width=4)
                d.text((1110, 840), "EIC", font=font(CINZEL9, 36), fill=(110, 18, 18, 255), anchor="mm")
    img.alpha_composite(L)


def art_spices(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 380
    tilt = math.sin(min(1, t / 2.0) * math.pi / 2) * 0.22
    d.line([(cx, cy), (cx, 820)], fill=col(b, "ink"), width=8)
    d.polygon([(cx - 120, 840), (cx + 120, 840), (cx + 60, 800), (cx - 60, 800)], fill=col(b, "ink"))
    lx, ly = cx - 280 * math.cos(tilt), cy + 280 * math.sin(tilt)
    rx, ry = cx + 280 * math.cos(tilt), cy - 280 * math.sin(tilt)
    d.line([(lx, ly), (rx, ry)], fill=col(b, "ink"), width=8)
    circle(d, cx, cy, 14, fill=col(b, "acc"))
    for (px, py), kind in (((lx, ly), "spice"), ((rx, ry), "silver")):
        d.line([(px, py), (px - 90, py + 180)], fill=col(b, "ink"), width=3)
        d.line([(px, py), (px + 90, py + 180)], fill=col(b, "ink"), width=3)
        d.arc([px - 110, py + 120, px + 110, py + 240], 0, 180, fill=col(b, "ink"), width=5)
        if kind == "spice":
            d.ellipse([px - 80, py + 110, px + 80, py + 190], fill=col(b, "acc"))
            d.text((px, py + 270), "SPICE", font=font(CINZEL7, 28), fill=col(b, "ink"), anchor="mm")
        else:
            for j in range(4):
                d.ellipse([px - 50, py + 165 - j * 16 - 10, px + 50, py + 165 - j * 16 + 10], outline=col(b, "ink"), width=3, fill=PAL[b["pal"]]["bg"] + (255,))
            d.text((px, py + 270), "SILVER", font=font(CINZEL7, 28), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def chart(img, b, t, dur, series, labels, ymax, unit="", title="", bars=False, colors=None):
    L = layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 980, 220, 1800, 860
    d.line([(x0, y1), (x1, y1)], fill=col(b, "ink"), width=3)
    d.line([(x0, y0), (x0, y1)], fill=col(b, "ink"), width=3)
    for k in range(1, 5):
        y = y1 - (y1 - y0) * k / 4
        d.line([(x0, y), (x1, y)], fill=col(b, "faint", 90), width=1)
        d.text((x0 - 14, y), f"{ymax * k / 4:g}{unit}", font=font(MONO, 18), fill=col(b, "faint"), anchor="rm")
    for i, lb in enumerate(labels):
        x = x0 + (x1 - x0) * (i + 0.5) / len(labels)
        d.text((x, y1 + 26), lb, font=font(MONO, 18), fill=col(b, "faint"), anchor="mm")
    prog = ease((t - 0.3) / 2.2)
    for si, s in enumerate(series):
        c = (colors[si] if colors else col(b, "acc")) if si == 0 else col(b, "ink")
        if colors:
            c = colors[si]
        pts = [(x0 + (x1 - x0) * (i + 0.5) / len(labels), y1 - (y1 - y0) * v / ymax) for i, v in enumerate(s)]
        if bars:
            n = len(series)
            for i, (x, y) in enumerate(pts):
                bw = 70 / n
                k = ease((t - 0.3 - i * 0.2) / 0.8)
                yy = y1 - (y1 - y) * k
                d.rectangle([x - 40 + si * bw * 1.1, yy, x - 40 + si * bw * 1.1 + bw, y1], fill=c)
        else:
            pp = polyline_partial(pts, prog)
            if len(pp) > 1:
                d.line(pp, fill=c, width=6, joint="curve")
            circle(d, pp[-1][0], pp[-1][1], 9, fill=c)
    if title:
        d.text((x0, y0 - 50), title, font=font(CINZEL7, 26), fill=col(b, "ink"))
    finish(img, b, L)


def art_chart_shares(img, b, t, dur):
    chart(img, b, t, dur, [[1, 3, 7, 12, 20, 32]], ["1600", "1620", "1640", "1660", "1680", "1700"], 40, "", "COMPANY CAPITAL (RELATIVE)")


def art_chart_navy(img, b, t, dur):
    chart(img, b, t, dur, [[38, 0, 0], [0, 23, 0], [0, 0, 16]], ["BRITAIN", "FRANCE", "RUSSIA"], 40, "", "BATTLESHIPS · 1889", bars=True,
          colors=[col(b, "acc"), col(b, "ink", 200), col(b, "faint")])


def art_chart_gdp(img, b, t, dur):
    chart(img, b, t, dur, [[24.4, 16, 8.6, 4.2], [2.9, 5.2, 9, 18.5]], ["1700", "1820", "1870", "1913"], 30, "%", "SHARE OF WORLD GDP  ·  INDIA vs BRITAIN",
          colors=[col(b, "acc"), col(b, "ink")])


def art_chart_cloth(img, b, t, dur):
    chart(img, b, t, dur, [[24.5, 19.7, 8.6, 2.8, 1.7], [1.9, 4.3, 9.5, 19.9, 22.9]], ["1750", "1800", "1830", "1860", "1880"], 25, "%", "SHARE OF WORLD MANUFACTURING  ·  INDIA vs UK",
          colors=[col(b, "acc"), col(b, "ink")])


def art_chart_debt(img, b, t, dur):
    chart(img, b, t, dur, [[25, 130, 180, 110, 250]], ["1900", "1919", "1923", "1938", "1946"], 260, "%", "UK NATIONAL DEBT  ·  % OF GDP")


def soldier(d, x, y, s, c, ph=0):
    d.ellipse([x - 9 * s, y - 70 * s, x + 9 * s, y - 52 * s], fill=c)
    d.rectangle([x - 11 * s, y - 52 * s, x + 11 * s, y - 20 * s], fill=c)
    d.line([(x - 6 * s, y - 20 * s), (x - 6 * s + math.sin(ph) * 8 * s, y)], fill=c, width=int(7 * s))
    d.line([(x + 6 * s, y - 20 * s), (x + 6 * s - math.sin(ph) * 8 * s, y)], fill=c, width=int(7 * s))
    d.line([(x + 12 * s, y - 50 * s), (x + 20 * s, y - 95 * s)], fill=c, width=int(3 * s))
    d.rectangle([x - 8 * s, y - 82 * s, x + 8 * s, y - 68 * s], fill=c)


def art_soldiers(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    rows, cols_ = 6, 12
    for r in range(rows):
        for c_ in range(cols_):
            k = ease((t - 0.2 - (r * cols_ + c_) * 0.02) / 0.5)
            if k <= 0:
                continue
            x = 960 + c_ * 70 + r * 12 + (1 - k) * 200 + (t * 6 % 70 if b.get("more") else 0)
            y = 380 + r * 90
            cc = col(b, "acc" if (r + c_) % 9 == 0 else "ink", int(255 * k))
            soldier(d, x, y, 1.0, cc, t * 6 + c_)
    finish(img, b, L)


def art_crack(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, base = 1380, 820
    d.line([(cx - 330, base), (cx + 330, base)], fill=col(b, "ink"), width=5)
    d.rectangle([cx - 300, base - 260, cx + 300, base], outline=col(b, "ink"), width=4)
    for k in range(5):
        x = cx - 240 + k * 120
        d.arc([x - 40, base - 180, x + 40, base - 60], 180, 360, fill=col(b, "ink"), width=4)
        d.line([(x - 40, base - 120), (x - 40, base)], fill=col(b, "ink"), width=3)
        d.line([(x + 40, base - 120), (x + 40, base)], fill=col(b, "ink"), width=3)
    dome = arc_pts(cx, base - 260, 200, 220, math.pi, 2 * math.pi, 50)
    stroke(d, dome, col(b, "ink"), 5, ease(t / 1.4))
    d.line([(cx, base - 480), (cx, base - 540)], fill=col(b, "ink"), width=5)
    for s in (-1, 1):
        mx = cx + s * 340
        d.rectangle([mx - 22, base - 420, mx + 22, base], outline=col(b, "ink"), width=4)
        d.polygon([(mx - 30, base - 420), (mx + 30, base - 420), (mx, base - 470)], outline=col(b, "ink"), fill=None)
    rnd = random.Random(7)
    prog = ease((t - 1.0) / 2.0)
    pts = [(cx, base - 480)]
    for k in range(10):
        pts.append((pts[-1][0] + rnd.uniform(-40, 40), pts[-1][1] + 48))
    stroke(d, pts, col(b, "acc"), 6, prog)
    for k in range(3):
        sp = pts[3 + k * 2]
        stroke(d, [sp, (sp[0] + rnd.choice([-1, 1]) * 90, sp[1] + 60)], col(b, "acc"), 4, ease((t - 1.6 - k * .3) / 1.0))
    finish(img, b, L)


def cannon(d, x, y, s, c, t, fire=False, face=1):
    d.ellipse([x - 40 * s, y - 40 * s, x + 40 * s, y + 40 * s], outline=c, width=int(6 * s))
    d.polygon([(x - 20 * s * face, y - 40 * s), (x + 160 * s * face, y - 70 * s), (x + 165 * s * face, y - 40 * s), (x - 10 * s * face, y - 10 * s)], fill=c)
    if fire:
        ph = (t % 1.6)
        if ph < 0.15:
            mx, my = x + 170 * s * face, y - 56 * s
            d.ellipse([mx - 30, my - 30, mx + 30, my + 30], fill=(255, 210, 120, 255))
        r = 30 + ph * 90
        mx, my = x + (190 + ph * 120) * s * face, y - 60 * s - ph * 40
        d.ellipse([mx - r, my - r * .6, mx + r, my + r * .6], fill=(225, 220, 210, int(150 * max(0, 1 - ph / 1.6))))


def art_battle(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    for i in range(30):
        x = 1000 + (i % 6) * 22; y = 420 + (i // 6) * 26
        if i / 30 < ease(t / 1.2):
            d.rectangle([x, y, x + 14, y + 14], fill=col(b, "acc"))
    d.text((1060, 380), "3,000", font=font(CINZEL9, 40), fill=col(b, "acc"), anchor="mm")
    n = 300
    for i in range(n):
        if i / n > ease((t - .4) / 1.6):
            break
        x = 1380 + (i % 20) * 20; y = 420 + (i // 20) * 22
        d.rectangle([x, y, x + 12, y + 12], fill=col(b, "ink", 210))
    d.text((1570, 380), "50,000", font=font(CINZEL9, 40), fill=col(b, "ink"), anchor="mm")
    cannon(d, 1040, 860, 0.9, col(b, "ink"), t, True, 1)
    cannon(d, 1720, 860, 0.9, col(b, "ink"), t + .8, True, -1)
    finish(img, b, L)


def art_coins_hand(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    # bag
    k = ease(t / 1.2)
    bx = 1100 + 300 * ease((t - .4) / 1.6)
    d.ellipse([bx - 110, 500, bx + 110, 740], fill=col(b, "ink"))
    d.polygon([(bx - 40, 510), (bx + 40, 510), (bx + 60, 450), (bx - 60, 450)], fill=col(b, "ink"))
    d.text((bx, 640), "£", font=font(CINZEL9, 110), fill=PAL[b["pal"]]["bg"] + (255,), anchor="mm")
    # coins falling
    for i in range(14):
        ph = (t * 0.9 + i * 0.13) % 1.2
        x = 1100 + (i * 61) % 600
        y = 200 + ph * 700
        if y < 880:
            d.ellipse([x - 26, y - 10, x + 26, y + 10], fill=col(b, "acc"), outline=col(b, "ink"), width=2)
    for j in range(6):
        d.ellipse([1500 - 60, 860 - j * 18 - 14, 1500 + 60, 860 - j * 18 + 14], fill=col(b, "acc"), outline=col(b, "ink"), width=2)
    finish(img, b, L)


def art_fire(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 860
    d.rectangle([1060, base - 260, 1700, base], outline=col(b, "ink"), width=5)
    for k in range(9):
        x = 1060 + k * 80
        d.rectangle([x, base - 300, x + 40, base - 260], outline=col(b, "ink"), width=4)
    rnd = random.Random(int(t * 10))
    for k in range(26):
        x = 1080 + k * 24 + rnd.uniform(-8, 8)
        h = 120 + rnd.uniform(0, 260) * (0.6 + 0.4 * math.sin(t * 5 + k))
        c = rnd.choice([(255, 120, 40), (255, 180, 60), (255, 80, 30)])
        d.polygon([(x - 26, base - 250), (x + 26, base - 250), (x + rnd.uniform(-10, 10), base - 250 - h)], fill=c + (230,))
    for k in range(20):
        ph = (t * 0.6 + k * 0.11) % 1
        x = 1100 + (k * 47) % 600 + math.sin(t + k) * 30
        y = base - 300 - ph * 500
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 200, 120, int(255 * (1 - ph))))
    finish(img, b, L, 24)


def art_factory(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 860
    d.line([(940, base), (1840, base)], fill=col(b, "ink"), width=4)
    for k in range(4):
        x = 980 + k * 200
        d.polygon([(x, base), (x, base - 200), (x + 100, base - 280), (x + 200, base - 200), (x + 200, base)], outline=col(b, "ink"))
        stroke(d, [(x, base), (x, base - 200), (x + 100, base - 280), (x + 200, base - 200), (x + 200, base)], col(b, "ink"), 4, ease((t - k * .2) / 1.0))
        for wy in (base - 150, base - 80):
            for wx in (x + 30, x + 120):
                d.rectangle([wx, wy, wx + 45, wy + 40], fill=col(b, "acc", int(200 * (0.6 + 0.4 * math.sin(t * 3 + k)))))
    for k, cxp in enumerate((1100, 1500, 1720)):
        d.rectangle([cxp - 22, base - 520, cxp + 22, base - 200], outline=col(b, "ink"), width=4)
        for j in range(7):
            ph = (t * 0.5 + j * 0.15 + k * .2) % 1
            r = 20 + ph * 70
            x = cxp + ph * 140 + math.sin(t + j) * 10
            y = base - 540 - ph * 280
            d.ellipse([x - r, y - r, x + r, y + r], fill=col(b, "faint", int(150 * (1 - ph))))
    # gear
    cx, cy = 1700, 330
    for j in range(12):
        an = t * 1.2 + j * math.pi / 6
        d.line([(cx + math.cos(an) * 50, cy + math.sin(an) * 50), (cx + math.cos(an) * 78, cy + math.sin(an) * 78)], fill=col(b, "ink"), width=16)
    circle(d, cx, cy, 58, col(b, "ink"), w=10)
    finish(img, b, L)


def art_cycle(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy, R = 1380, 560, 280
    nodes = [("COTTON", -90), ("MILLS", 30), ("MARKETS", 150)]
    for i, (lab, ang) in enumerate(nodes):
        a = math.radians(ang)
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
        k = ease((t - i * .4) / .6)
        circle(d, x, y, 90, col(b, "ink", int(255 * k)), w=4)
        d.text((x, y), lab, font=font(CINZEL7, 28), fill=col(b, "ink", int(255 * k)), anchor="mm")
        a2 = math.radians(nodes[(i + 1) % 3][1])
        pts = arc_pts(cx, cy, R, R, a + 0.42, a2 - 0.42 + (2 * math.pi if a2 < a else 0), 30)
        prog = ease((t - 0.6 - i * .5) / .8)
        stroke(d, pts, col(b, "acc"), 6, prog)
        if prog >= 1:
            ex, ey = pts[-1]; px_, py_ = pts[-3]
            an = math.atan2(ey - py_, ex - px_)
            d.polygon([(ex + math.cos(an) * 18, ey + math.sin(an) * 18), (ex + math.cos(an + 2.4) * 18, ey + math.sin(an + 2.4) * 18), (ex + math.cos(an - 2.4) * 18, ey + math.sin(an - 2.4) * 18)], fill=col(b, "acc"))
    ph = (t * 0.3) % 1
    a = -math.pi / 2 + ph * 2 * math.pi
    circle(d, cx + math.cos(a) * R, cy + math.sin(a) * R, 12, fill=col(b, "acc"))
    finish(img, b, L)


def art_train(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    base = 820
    sp = 500 if b.get("fast") else 260
    off = (t * sp) % 80
    d.line([(900, base), (W, base)], fill=col(b, "ink"), width=4)
    for x in range(900 - int(off), W, 80):
        d.line([(x, base + 4), (x + 40, base + 4)], fill=col(b, "faint"), width=8)
    x0 = 1180 + math.sin(t * 3) * 4
    c = col(b, "ink")
    d.rectangle([x0, base - 220, x0 + 300, base - 60], outline=c, width=5)
    d.rectangle([x0 + 300, base - 300, x0 + 440, base - 60], outline=c, width=5)
    d.rectangle([x0 + 320, base - 280, x0 + 420, base - 200], fill=col(b, "acc", 200))
    d.rectangle([x0 + 40, base - 300, x0 + 90, base - 220], outline=c, width=5)
    d.polygon([(x0 - 60, base - 60), (x0, base - 60), (x0, base - 130)], outline=c)
    for k, wx in enumerate((x0 + 60, x0 + 200, x0 + 360)):
        r = 55 if k < 2 else 45
        circle(d, wx, base - r, r, c, w=5)
        an = t * (sp / 40)
        d.line([(wx, base - r), (wx + math.cos(an) * r, base - r + math.sin(an) * r)], fill=c, width=4)
    d.line([(x0 + 60 + math.cos(t * sp / 40) * 30, base - 55), (x0 + 200 + math.cos(t * sp / 40) * 30, base - 55)], fill=c, width=6)
    for j in range(8):
        ph = (t * 0.8 + j * 0.13) % 1
        r = 20 + ph * 80
        x = x0 + 65 - ph * 500
        y = base - 330 - ph * 120
        d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=col(b, "faint", int(170 * (1 - ph))))
    if b.get("fast"):
        for k in range(10):
            y = 300 + k * 50
            x = (W - ((t * 900 + k * 230) % 1000))
            d.line([(x, y), (x + 160, y)], fill=col(b, "faint", 160), width=3)
    finish(img, b, L)


def art_suez(img, b, t, dur):
    box = (900, 150, 1840, 960, -15, 80, 55, -38)
    L = layer(); d = ImageDraw.Draw(L)
    for c in WORLD:
        for ring in c["rings"]:
            if not any(-30 <= p[0] <= 95 and -45 <= p[1] <= 60 for p in ring[:5]):
                continue
            pts = [proj_eq(x, y, box) for x, y in ring]
            fillc = col(b, "acc", 160) if c["name"] == "Egypt" else None
            if fillc:
                d.polygon(pts, fill=fillc)
            d.line(pts + [pts[0]], fill=col(b, "faint", 200), width=2)
    P = lambda lo, la: proj_eq(lo, la, box)
    longr = [P(-0.1, 51.5), P(-12, 40), P(-20, 15), P(-10, -10), P(10, -30), P(20, -36), P(40, -28), P(55, -5), P(65, 10), P(72.8, 19)]
    short = [P(-0.1, 51.5), P(-10, 40), P(-5, 36), P(15, 36), P(32.3, 31.2), P(32.5, 29.9), P(38, 21), P(43.5, 12.5), P(55, 14), P(72.8, 19)]
    p1 = ease((t - .3) / 2.0)
    pp = polyline_partial(longr, p1)
    for i in range(len(pp) - 1):
        a, c_ = pp[i], pp[i + 1]
        n = max(1, int(math.hypot(c_[0] - a[0], c_[1] - a[1]) / 14))
        for k in range(0, n, 2):
            u0, u1 = k / n, (k + 1) / n
            d.line([(a[0] + (c_[0] - a[0]) * u0, a[1] + (c_[1] - a[1]) * u0), (a[0] + (c_[0] - a[0]) * u1, a[1] + (c_[1] - a[1]) * u1)], fill=col(b, "ink", 200), width=3)
    stroke(d, short, col(b, "acc"), 6, ease((t - 1.5) / 1.6))
    d.text(P(0, -20), "19,800 KM", font=font(CINZEL7, 28), fill=col(b, "ink"), anchor="mm")
    d.text(P(45, 32), "11,600 KM", font=font(CINZEL7, 28), fill=col(b, "acc"), anchor="mm")
    if b.get("crisis"):
        x, y = P(32.4, 30.5)
        k = ease((t - 2) / 0.5)
        if k > 0:
            d.line([(x - 60 * k, y - 60 * k), (x + 60 * k, y + 60 * k)], fill=(230, 40, 40, 255), width=12)
            d.line([(x - 60 * k, y + 60 * k), (x + 60 * k, y - 60 * k)], fill=(230, 40, 40, 255), width=12)
    finish(img, b, L)


def person(d, x, y, s, c):
    d.ellipse([x - 7 * s, y - 26 * s, x + 7 * s, y - 12 * s], fill=c)
    d.rounded_rectangle([x - 9 * s, y - 10 * s, x + 9 * s, y + 16 * s], int(5 * s), fill=c)


def art_people(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    n = 0
    for r in range(16):
        for c_ in range(34):
            k = ease((t - 0.6 - (r + c_) * 0.02) / 0.4)
            if k <= 0:
                continue
            person(d, 960 + c_ * 25, 260 + r * 40, 0.8, col(b, "faint", int(220 * k)))
    k = ease(t / 0.5)
    person(d, 960 + 17 * 25, 260 + 8 * 40, 1.4, col(b, "acc", int(255 * k)))
    circle(d, 960 + 17 * 25, 260 + 8 * 40 - 4, 34, col(b, "acc", int(255 * k)), w=3)
    d.text((1380, 960), "EACH DOT ≈ 550,000 PEOPLE", font=font(MONO, 20), fill=col(b, "faint"), anchor="mm")
    finish(img, b, L)


def art_pyramid(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    labels = ["THE CROWN", "BRITISH OFFICIALS", "PRINCES & CHIEFS", "LOCAL ELITES", "300 MILLION PEOPLE"]
    for i, lab in enumerate(labels):
        k = ease((t - i * 0.35) / 0.5)
        y0 = 220 + i * 140
        w0 = 120 + i * 150
        w1 = w0 + 150
        c = col(b, "acc" if i == 0 else "ink", int(255 * k))
        d.polygon([(1380 - w0 / 2, y0), (1380 + w0 / 2, y0), (1380 + w1 / 2, y0 + 120), (1380 - w1 / 2, y0 + 120)], outline=c, fill=col(b, "acc", int(60 * k)) if i == 0 else None)
        d.line([(1380 - w0 / 2, y0), (1380 + w0 / 2, y0), (1380 + w1 / 2, y0 + 120), (1380 - w1 / 2, y0 + 120), (1380 - w0 / 2, y0)], fill=c, width=4)
        d.text((1380, y0 + 60), lab, font=font(CINZEL7, 26 if i else 30), fill=c, anchor="mm")
    finish(img, b, L)


def art_census(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 1000, 180, 1760, 940
    d.rectangle([x0, y0, x1, y1], fill=(238, 228, 204, 255), outline=col(b, "ink"), width=4)
    d.text(((x0 + x1) / 2, y0 + 50), "CENSUS OF INDIA", font=font(CINZEL9, 40), fill=(40, 34, 30, 255), anchor="mm")
    cats = ["HINDU", "MUSLIM", "SIKH", "CHRISTIAN", "BRAHMIN", "KSHATRIYA"]
    for i, c_ in enumerate(cats):
        y = y0 + 130 + i * 120
        d.line([(x0 + 40, y + 70), (x1 - 40, y + 70)], fill=(140, 120, 100, 255), width=2)
        for j in range(3):
            d.rectangle([x0 + 60 + j * 120, y + 10, x0 + 140 + j * 120, y + 50], outline=(120, 100, 80, 255), width=2)
        k = ease_out((t - 0.4 - i * 0.35) / 0.25)
        if k > 0:
            s = 1.6 - 0.6 * k
            stamp = Image.new("RGBA", (360, 90), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rectangle([4, 4, 356, 86], outline=(170, 30, 30, 230), width=6)
            sd.text((180, 45), c_, font=font(CINZEL9, 44), fill=(170, 30, 30, 230), anchor="mm")
            stamp = stamp.resize((int(360 * s * .8), int(90 * s * .8))).rotate(-6 + i * 3, expand=True)
            L.alpha_composite(stamp, (int(x0 + 470 - stamp.width / 2), int(y + 30 - stamp.height / 2)))
    img.alpha_composite(L)


def art_split(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    k = ease((t - 0.8) / 1.5)
    rnd = random.Random(5)
    for i in range(120):
        gx = rnd.uniform(-1, 1); gy = rnd.uniform(-1, 1)
        side = -1 if gx < 0 else 1
        x = 1380 + gx * 330 + side * k * 160
        y = 560 + gy * 300
        cc = col(b, "acc" if side < 0 else "ink", 230) if k > 0.2 else col(b, "ink", 230)
        person(d, x, y, 1.0, cc)
    pts = [(1380 + math.sin(y * 0.03) * 12, y) for y in range(200, 940, 10)]
    stroke(d, pts, col(b, "acc"), 5, ease((t - 0.4) / 1.0))
    finish(img, b, L)


def art_chains(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    brk = b.get("broken")
    for i in range(9):
        cx = 980 + i * 95
        cy = 560 + math.sin(t * 1.5 + i * .6) * 10
        if brk:
            gap = ease((t - 1.0) / 1.0) * (60 if i >= 5 else -60) if i in (4, 5) else ease((t - 1.0) / 1.0) * (40 if i > 4 else -40)
            cx += gap
        horiz = i % 2 == 0
        if horiz:
            d.rounded_rectangle([cx - 60, cy - 30, cx + 60, cy + 30], 30, outline=col(b, "ink"), width=12)
        else:
            d.rounded_rectangle([cx - 22, cy - 50, cx + 22, cy + 50], 22, outline=col(b, "ink"), width=12)
    if brk:
        k = ease((t - 1.0) / 0.5)
        for j in range(10):
            a = j * 0.63
            d.line([(1400 + math.cos(a) * 40 * k, 560 + math.sin(a) * 40 * k), (1400 + math.cos(a) * 90 * k, 560 + math.sin(a) * 90 * k)], fill=col(b, "acc", int(255 * k)), width=4)
    finish(img, b, L)


def art_opium(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1180, 520
    d.line([(cx, cy), (cx - 20, 900)], fill=col(b, "ink"), width=6)
    k = ease(t / 1.2)
    for j in range(5):
        a = j * 2 * math.pi / 5 + t * 0.2
        px, py = cx + math.cos(a) * 80 * k, cy + math.sin(a) * 80 * k
        d.ellipse([px - 70 * k, py - 50 * k, px + 70 * k, py + 50 * k], fill=(200, 40, 40, 200))
    circle(d, cx, cy, 34 * k, fill=(40, 30, 30, 255))
    draw_ship(d, 1580, 720 + math.sin(t) * 6, 0.6, col(b, "ink"), t, ease((t - .5) / 1.5), math.sin(t) * 2)
    cannon(d, 1520, 900, 0.6, col(b, "ink"), t, True, -1)
    finish(img, b, L)


def art_famine(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1180, 650
    d.arc([cx - 180, cy - 140, cx + 180, cy + 140], 0, 180, fill=col(b, "ink"), width=8)
    d.line([(cx - 180, cy), (cx + 180, cy)], fill=col(b, "ink"), width=6)
    rnd = random.Random(3)
    for k in range(8):
        x = 980 + k * 60
        stroke(d, [(x, 900), (x + rnd.uniform(-30, 30), 940), (x + rnd.uniform(-40, 40), 990)], col(b, "faint"), 3, ease((t - k * .1) / 1.0))
    # sacks leaving on ship
    sx = 1450 + ease((t - 0.6) / max(1, dur * .7)) * 400
    draw_ship(d, sx, 760, 0.45, col(b, "ink"), t, 1.0)
    for j in range(4):
        d.rounded_rectangle([sx - 60 + j * 30, 640 - j % 2 * 30, sx - 30 + j * 30, 690 - j % 2 * 30], 8, fill=col(b, "faint"))
    d.text((1650, 560), "GRAIN EXPORTS", font=font(CINZEL7, 26), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def art_garden(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 1000, 220, 1760, 900
    stroke(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col(b, "ink"), 10, ease(t / 1.4), closed=True)
    d.rectangle([x0 - 6, 520, x0 + 6, 600], fill=PAL[b["pal"]]["bg"] + (255,))
    circle(d, 1550, 380, 40, col(b, "ink"), w=6)
    d.text((1550, 450), "WELL", font=font(CINZEL7, 22), fill=col(b, "ink"), anchor="mm")
    rnd = random.Random(1)
    for i in range(380):
        x = rnd.uniform(x0 + 30, x1 - 30); y = rnd.uniform(y0 + 30, y1 - 30)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=col(b, "faint", 220))
    if not b.get("calm"):
        for k in range(10):
            ph = (t * 2 + k * 0.27) % 1
            if ph < 0.25:
                y = 540 + (k % 5) * 14
                d.line([(x0 + 10, y), (x0 + 10 + 260 * ph * 4, y + (k - 5) * 12 * ph * 4)], fill=(255, 220, 140, int(255 * (1 - ph * 4))), width=3)
        for k in range(5):
            d.ellipse([x0 - 60, 520 + k * 18, x0 - 36, 544 + k * 18], fill=col(b, "acc"))
    d.text((x0, y1 + 40), "ONE NARROW EXIT", font=font(CINZEL7, 24), fill=col(b, "ink"))
    finish(img, b, L)


def art_march_salt(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    pts = [(960, 860), (1150, 760), (1300, 800), (1460, 680), (1640, 640), (1780, 520)]
    stroke(d, pts, col(b, "faint"), 4, 1.0)
    for i in range(18):
        ph = ((t * 0.06) + i * 0.05) % 1
        q = polyline_partial(pts, ph)[-1]
        person(d, q[0], q[1] - 12, 1.2, col(b, "ink"))
    d.text((1780, 470), "THE SEA · DANDI", font=font(CINZEL7, 26), fill=col(b, "acc"), anchor="mm")
    waves(d, col(b, "acc"), t, 560, 2, 6)
    finish(img, b, L)


def art_partition(img, b, t, dur):
    box = (980, 140, 1820, 980, 60, 100, 38, 4)
    L = layer(); d = ImageDraw.Draw(L)
    for n in ("India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "Myanmar"):
        for ring in BYNAME[n]["rings"]:
            pts = [proj_eq(x, y, box) for x, y in ring]
            if n in ("Pakistan", "Bangladesh"):
                d.polygon(pts, fill=col(b, "faint", 120))
            d.line(pts + [pts[0]], fill=col(b, "ink", 200), width=2)
    for n in ("Pakistan", "Bangladesh"):
        for ring in BYNAME[n]["rings"]:
            pts = [proj_eq(x, y, box) for x, y in ring]
            stroke(d, pts, (230, 50, 40, 255), 6, ease((t - 0.5) / 2.0), closed=True)
    d.text(proj_eq(69, 29, box), "PAKISTAN", font=font(CINZEL7, 26), fill=col(b, "ink"), anchor="mm")
    d.text(proj_eq(79, 22, box), "INDIA", font=font(CINZEL9, 40), fill=col(b, "ink"), anchor="mm")
    finish(img, b, L)


def art_people_move(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    d.line([(1380, 160), (1380, 960)], fill=(230, 50, 40, 255), width=6)
    for i in range(60):
        lane = i % 12
        y = 200 + lane * 62
        sp = 60 + (i * 13) % 40
        if i % 2 == 0:
            x = 960 + ((t * sp + i * 70) % 840)
        else:
            x = 1800 - ((t * sp + i * 70) % 840)
        person(d, x, y + 24, 1.1, col(b, "ink" if i % 2 else "acc", 220))
    finish(img, b, L)


def union_jack(d, x, y, w, h, a=255):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 110, a))
    for s in (1, -1):
        d.line([(x, y if s > 0 else y + h), (x + w, y + h if s > 0 else y)], fill=(255, 255, 255, a), width=int(h * .2))
        d.line([(x, y if s > 0 else y + h), (x + w, y + h if s > 0 else y)], fill=(200, 30, 40, a), width=int(h * .07))
    d.rectangle([x + w * .42, y, x + w * .58, y + h], fill=(255, 255, 255, a))
    d.rectangle([x, y + h * .36, x + w, y + h * .64], fill=(255, 255, 255, a))
    d.rectangle([x + w * .45, y, x + w * .55, y + h], fill=(200, 30, 40, a))
    d.rectangle([x, y + h * .41, x + w, y + h * .59], fill=(200, 30, 40, a))


def art_flag(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    for px, down in ((1200, True), (1560, False)):
        d.line([(px, 960), (px, 200)], fill=col(b, "ink"), width=8)
        k = ease((t - 0.5) / max(1, dur * .8))
        fy = 210 + (k * 520 if down else (1 - k) * 520)
        if down:
            union_jack(d, px + 4, fy, 260, 150)
        else:
            d.rectangle([px + 4, fy, px + 264, fy + 150], fill=(200, 30, 40, 255))
            for j in range(5):
                a = j * 2 * math.pi / 5 - math.pi / 2
                d.ellipse([px + 60 + math.cos(a) * 20 - 6, fy + 50 + math.sin(a) * 20 - 6, px + 60 + math.cos(a) * 20 + 6, fy + 50 + math.sin(a) * 20 + 6], fill=(255, 220, 60, 255))
    for k in range(80):
        x = (k * 97 + t * 60) % W
        y = (k * 53 + t * 700) % H
        d.line([(x, y), (x - 6, y + 22)], fill=col(b, "faint", 120), width=2)
    finish(img, b, L)


def art_book(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    cx, cy = 1380, 640
    k = ease(t / 1.0)
    d.polygon([(cx, cy - 20), (cx - 360 * k, cy - 80), (cx - 360 * k, cy + 200), (cx, cy + 250)], outline=col(b, "ink"), fill=col(b, "ink", 30))
    d.polygon([(cx, cy - 20), (cx + 360 * k, cy - 80), (cx + 360 * k, cy + 200), (cx, cy + 250)], outline=col(b, "ink"), fill=col(b, "ink", 30))
    d.line([(cx, cy - 20), (cx, cy + 250)], fill=col(b, "ink"), width=4)
    words = ["HELLO", "TEA", "SHAMPOO", "BUNGALOW", "JUNGLE", "PYJAMAS", "LOOT", "THUG", "CRICKET", "PARLIAMENT"]
    for i, w_ in enumerate(words):
        ph = ((t * 0.25) + i * 0.1) % 1
        x = cx + math.sin(i * 1.7) * 420 * ph
        y = cy - 60 - ph * 420
        d.text((x, y), w_, font=font(CINZEL7, 30), fill=col(b, "acc" if i % 3 == 0 else "ink", int(255 * math.sin(ph * math.pi))), anchor="mm")
    finish(img, b, L)


def art_legacy(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    items = ["PARLIAMENT", "RAILWAYS", "CRICKET", "BORDERS"]
    for i, lab in enumerate(items):
        k = ease((t - 0.3 - i * 0.45) / 0.5)
        if k <= 0:
            continue
        cx = 1020 + i * 240
        cy = 520
        c = col(b, "ink", int(255 * k))
        if i == 0:
            d.rectangle([cx - 30, cy - 120, cx + 30, cy + 120], outline=c, width=4)
            circle(d, cx, cy - 70, 24, c, w=4)
            d.polygon([(cx - 36, cy - 120), (cx + 36, cy - 120), (cx, cy - 200)], outline=c)
            d.line([(cx - 36, cy - 120), (cx, cy - 200), (cx + 36, cy - 120)], fill=c, width=4)
        elif i == 1:
            d.line([(cx - 70, cy + 120), (cx - 20, cy - 120)], fill=c, width=4)
            d.line([(cx + 70, cy + 120), (cx + 20, cy - 120)], fill=c, width=4)
            for j in range(6):
                y = cy + 100 - j * 40
                ww = 60 - j * 7
                d.line([(cx - ww, y), (cx + ww, y)], fill=c, width=4)
        elif i == 2:
            d.line([(cx - 40, cy + 120), (cx + 20, cy - 100)], fill=c, width=14)
            circle(d, cx + 40, cy + 80, 22, fill=col(b, "acc", int(255 * k)))
        else:
            stroke(d, [(cx - 80, cy - 100), (cx + 80, cy - 100), (cx + 80, cy + 20), (cx - 20, cy + 20), (cx - 20, cy + 120)], col(b, "acc", int(255 * k)), 6, k)
        d.text((cx, cy + 190), lab, font=font(CINZEL7, 24), fill=c, anchor="mm")
    finish(img, b, L)


def art_sunset(img, b, t, dur):
    L = layer(); d = ImageDraw.Draw(L)
    hy = 760
    k = ease(t / max(1.0, dur * 0.9))
    sy = 360 + k * 520
    for r in range(260, 120, -20):
        circle(d, W / 2, sy, r, fill=(255, 150 + (260 - r) // 3, 60, int(30 + (260 - r) / 4)))
    circle(d, W / 2, sy, 120, fill=(255, 190, 90, 255))
    d.rectangle([0, hy, W, H], fill=PAL[b["pal"]]["bg"] + (255,))
    pts = arc_pts(W / 2, hy + 2200, 2400, 2200, math.pi * 1.25, math.pi * 1.75, 120)
    d.line(pts, fill=col(b, "ink"), width=4)
    for k2 in range(5):
        y = hy + 30 + k2 * 40
        d.line([(W / 2 - 600 + k2 * 60, y), (W / 2 + 600 - k2 * 60, y)], fill=(255, 170, 70, 120 - k2 * 20), width=3)
    finish(img, b, L, 30)


ARTS = {
    "island": art_island, "map": art_map, "counter": art_counter, "globe": art_globe, "four": art_four, "title": art_title,
    "chapter": art_chapter, "charter": art_charter, "spices": art_spices, "chart_shares": art_chart_shares,
    "soldiers": art_soldiers, "ship": art_ship, "ship_guns": art_ship, "compass": art_compass, "fleet": art_fleet,
    "chart_navy": art_chart_navy, "routes": art_routes, "chart_gdp": art_chart_gdp, "crack": art_crack,
    "battle": art_battle, "coins_hand": art_coins_hand, "map_india": art_map_india, "fire": art_fire, "crown": art_crown,
    "factory": art_factory, "cycle": art_cycle, "chart_cloth": art_chart_cloth, "train": art_train, "cables": art_cables,
    "suez": art_suez, "people": art_people, "pyramid": art_pyramid, "census": art_census, "split": art_split,
    "africa": art_africa, "chains": art_chains, "opium": art_opium, "famine": art_famine, "garden": art_garden,
    "chart_debt": art_chart_debt, "march_salt": art_march_salt, "partition": art_partition, "people_move": art_people_move,
    "flag": art_flag, "book": art_book, "legacy": art_legacy, "sunset": art_sunset,
}
# layout: (mode, x, y, size)  mode left|center|top
LAYOUT = {
    "map": ("top", 90, 70, 72), "routes": ("top", 90, 70, 72), "cables": ("top", 90, 70, 72),
    "counter": ("center", W / 2, 200, 78), "title": ("center", W / 2, 520, 92), "chapter": ("none", 0, 0, 0),
    "sunset": ("center", W / 2, 180, 96), "four": ("left", 110, 400, 84),
}
