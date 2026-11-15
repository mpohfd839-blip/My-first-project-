"""Video timeline: year at each second, drone camera path, lighting, captions, era, population,
particles and the 2D overlay (year, era + flag, population, landmark titles)."""
import math
import random

import cairo
import numpy as np

W, H = 1280, 720
DUR = 720.0

# (video second, year)
YEAR_KEYS = [
    (0, 1600.0), (14, 1600.4), (44, 1609.50), (52, 1609.70), (72, 1609.74), (80, 1609.8), (96, 1614.0),
    (112, 1624.5), (150, 1626.6), (184, 1643.0), (214, 1653.6), (240, 1660.0), (258, 1664.55), (280, 1664.70),
    (292, 1673.50), (304, 1673.65), (316, 1674.9), (344, 1699.8), (382, 1730.0), (418, 1776.40), (432, 1776.58),
    (444, 1776.705), (462, 1776.735), (478, 1783.95), (494, 1789.33), (504, 1789.36), (528, 1811.4),
    (556, 1830.0), (584, 1850.0), (602, 1860.0), (622, 1885.0), (646, 1931.0), (668, 1975.0), (690, 2014.0),
    (704, 2026.0), (720, 2026.0),
]

# camera keys: (t, eye, target, fov)
CAM_KEYS = [
    (0, (200, 1400, 4200), (500, 0, -2600), 42),
    (14, (-100, 650, 1800), (350, 0, -1800), 44),
    (28, (700, 260, -900), (650, 0, -2150), 46),
    (42, (900, 140, -1800), (640, 10, -2190), 46),
    (52, (-350, 70, 2900), (-700, 0, 2200), 48),
    (62, (-420, 90, -600), (-800, 5, -1500), 48),
    (72, (-500, 110, -4300), (-900, 5, -5200), 48),
    (80, (600, 320, 900), (0, 0, -300), 46),
    (96, (380, 230, 420), (0, 0, -150), 44),
    (112, (250, 150, 200), (0, 0, -120), 44),
    (130, (-260, 150, 160), (0, 5, -130), 44),
    (150, (-330, 170, -420), (20, 5, -200), 44),
    (168, (650, 190, -150), (200, 0, -380), 44),
    (184, (720, 160, -520), (220, 0, -420), 44),
    (200, (900, 130, -880), (200, 0, -660), 44),
    (214, (-520, 150, -900), (0, 0, -660), 44),
    (240, (700, 520, 700), (120, 0, -380), 42),
    (258, (250, 60, 380), (250, 10, 1600), 46),
    (270, (420, 90, 560), (150, 5, 200), 46),
    (280, (500, 220, 450), (60, 0, -200), 44),
    (292, (-200, 260, 900), (100, 0, 600), 46),
    (304, (-500, 280, 500), (0, 0, -250), 44),
    (316, (-550, 180, -380), (-60, 0, -680), 44),
    (344, (-380, 140, -560), (-80, 10, -700), 44),
    (360, (1350, 240, -150), (700, 0, -800), 44),
    (382, (1450, 260, -1100), (650, 0, -1400), 44),
    (400, (1150, 380, -2200), (300, 0, -1300), 44),
    (418, (-300, 900, 3300), (0, 0, 600), 44),
    (432, (-600, 420, 1800), (-200, 0, 300), 46),
    (444, (-800, 260, -250), (-160, 0, -700), 46),
    (462, (-650, 300, -1200), (-120, 0, -650), 46),
    (478, (600, 600, 1800), (0, 0, 400), 44),
    (494, (380, 110, -480), (110, 15, -670), 44),
    (504, (320, 90, -820), (110, 15, -670), 44),
    (528, (600, 1500, 900), (700, 0, -4200), 44),
    (556, (-450, 260, -1800), (-80, 0, -3200), 46),
    (584, (300, 330, -4300), (700, 0, -5800), 46),
    (602, (2100, 700, 900), (300, 0, -2300), 44),
    (622, (1900, 500, -500), (500, 40, -1500), 44),
    (646, (900, 650, 1300), (-50, 120, -1300), 46),
    (668, (-1400, 520, 900), (100, 150, -1700), 46),
    (690, (-1500, 160, 2300), (-200, 180, -1300), 46),
    (704, (-1350, 90, 1850), (-300, 180, -1500), 46),
    (720, (-1300, 120, 1800), (-300, 200, -1600), 46),
]

# lighting presets
DAY = dict(sun_el=38, sun_az=215, sun_col=(1.05, 0.98, 0.88), sky_top=(0.36, 0.56, 0.82), sky_hor=(0.78, 0.85, 0.90),
           sky_amb=(0.42, 0.48, 0.58), ground_amb=(0.30, 0.28, 0.24), fog_col=(0.74, 0.82, 0.90), fog_den=1 / 16000,
           night=0.0, grade=(1.0, 1.0, 1.0))
MORNING = dict(DAY, sun_el=22, sun_az=120, sun_col=(1.1, 0.92, 0.75), sky_hor=(0.92, 0.84, 0.74),
               fog_col=(0.86, 0.82, 0.76), grade=(1.04, 1.0, 0.95))
GOLDEN = dict(DAY, sun_el=9, sun_az=250, sun_col=(1.25, 0.78, 0.45), sky_top=(0.30, 0.42, 0.70),
              sky_hor=(1.0, 0.72, 0.48), sky_amb=(0.42, 0.40, 0.50), fog_col=(0.95, 0.72, 0.52),
              grade=(1.08, 0.98, 0.9))
DUSK = dict(DAY, sun_el=2, sun_az=260, sun_col=(0.9, 0.42, 0.25), sky_top=(0.10, 0.14, 0.32),
            sky_hor=(0.75, 0.38, 0.30), sky_amb=(0.20, 0.20, 0.32), ground_amb=(0.12, 0.10, 0.10),
            fog_col=(0.38, 0.28, 0.32), night=0.6, grade=(1.0, 0.95, 1.0))
NIGHT = dict(DAY, sun_el=25, sun_az=200, sun_col=(0.10, 0.12, 0.20), sky_top=(0.02, 0.03, 0.09),
             sky_hor=(0.10, 0.12, 0.24), sky_amb=(0.10, 0.12, 0.22), ground_amb=(0.05, 0.05, 0.07),
             fog_col=(0.08, 0.09, 0.16), night=1.0, grade=(0.95, 0.98, 1.08))
LIGHT_KEYS = [(0, MORNING), (40, DAY), (430, DAY), (440, DUSK), (446, NIGHT), (462, NIGHT), (472, MORNING),
              (486, DAY), (650, DAY), (672, GOLDEN), (690, DUSK), (700, NIGHT), (720, NIGHT)]

ERAS = [  # (from year, name, flag)
    (-1e9, "LENAPEHOKING", "lenape"), (1624.4, "NEW NETHERLAND", "nl"), (1625.6, "NEW AMSTERDAM", "nl"),
    (1664.68, "NEW YORK  ·  ENGLISH COLONY", "en"), (1673.62, "NEW ORANGE", "nl"),
    (1674.85, "NEW YORK  ·  BRITISH COLONY", "gb"), (1776.58, "BRITISH-OCCUPIED NEW YORK", "gb"),
    (1783.9, "NEW YORK  ·  UNITED STATES", "us"), (1789.3, "NEW YORK  ·  U.S. CAPITAL", "us"),
    (1790.6, "NEW YORK CITY", "us"), (1898, "GREATER NEW YORK", "us"),
]
POP = [(1624.5, 30), (1626, 270), (1630, 300), (1640, 450), (1650, 1000), (1664, 1500), (1680, 3200), (1698, 4937),
       (1712, 5840), (1731, 8622), (1756, 13046), (1771, 21863), (1776.5, 25000), (1776.8, 5000), (1783, 12000),
       (1790, 33131), (1800, 60515), (1810, 96373), (1820, 123706), (1830, 202589), (1840, 312710),
       (1850, 515547), (1860, 813669), (1880, 1206299), (1900, 1850093), (1910, 2331542), (1950, 1960101),
       (1980, 1428285), (2000, 1537195), (2020, 1694251), (2026, 1660000)]

# landmark titles: (t0, t1, TITLE, subtitle, world point or None)
CAPTIONS = [
    (2, 13, "WHAT NEW YORK LOOKED LIKE", "400 YEARS AGO", "title"),
    (16, 30, "MANNAHATTA", "\"island of many hills\" — home of the Lenape people", None),
    (30, 44, "WERPOES", "A Lenape village beside the Collect Pond", (640, 30, -2180)),
    (53, 72, "HALVE MAEN", "Henry Hudson sails up the river that will bear his name, September 1609", None),
    (98, 112, "NEW NETHERLAND", "Dutch traders return to buy beaver furs from the Lenape", None),
    (114, 132, "FORT AMSTERDAM", "Built from 1625 at the southern tip of the island", (0, 20, -120)),
    (134, 150, "THE PURCHASE OF MANHATTAN", "1626: Peter Minuit trades goods worth 60 guilders for the island", None),
    (168, 184, "THE HEERE GRACHT", "A canal dug in the 1640s — today's Broad Street", (230, 10, -350)),
    (186, 212, "THE WALL", "1653: a timber wall against attack — the future Wall Street", (180, 20, -660)),
    (218, 240, "NEW AMSTERDAM, 1660", "About 1,500 people, 300 houses, a fort and a windmill", None),
    (258, 278, "THE ENGLISH ARRIVE", "August 1664: four warships force the Dutch to surrender", None),
    (281, 292, "NEW YORK", "The city is renamed after the Duke of York", None),
    (293, 314, "NEW ORANGE", "1673: the Dutch take the city back — for just fifteen months", None),
    (318, 340, "TRINITY CHURCH", "1698 — the wall comes down a year later", (-90, 40, -690)),
    (346, 382, "THE EAST RIVER WATERFRONT", "Wharves and landfill push the shoreline out into the river", None),
    (384, 416, "A GROWING COLONIAL PORT", "1760: over 15,000 people, the second-largest city in the colonies", None),
    (419, 438, "THE BRITISH FLEET", "Summer 1776: hundreds of warships fill New York Harbor", None),
    (445, 462, "THE GREAT FIRE", "21 September 1776: a quarter of the city burns", None),
    (466, 478, "EVACUATION DAY", "25 November 1783: the last British troops leave", None),
    (482, 504, "FEDERAL HALL", "30 April 1789: George Washington becomes the first U.S. President here",
     (110, 25, -670)),
    (510, 528, "THE GRID", "1811: the Commissioners' Plan lays streets over the whole island", None),
    (530, 556, "CITY HALL", "Completed in 1812", (80, 30, -1475)),
    (560, 584, "BROADWAY", "By 1850, half a million people live in New York", None),
    (604, 622, "THE BROOKLYN BRIDGE", "1883: the longest suspension bridge in the world", (1320, 60, -1180)),
    (626, 646, "THE SKYSCRAPERS", "1913 Woolworth · 1930 Chrysler · 1931 Empire State", None),
    (648, 668, "THE STATUE OF LIBERTY", "Dedicated in 1886", (-1150, 70, 1500)),
    (670, 690, "ONE WORLD TRADE CENTER", "541 metres — the tallest building in the Western Hemisphere",
     (-230, 560, -1250)),
    (704, 719, "NEW YORK", "400 YEARS LATER", "title"),
]


def interp_keys(keys, t):
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / max(t1 - t0, 1e-6)
            return a, b, f
    return keys[-1][1], keys[-1][1], 0.0


def year_at(t):
    a, b, f = interp_keys(YEAR_KEYS, t)
    return a + (b - a) * f


def _cr(p0, p1, p2, p3, f):
    f2, f3 = f * f, f * f * f
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f2 + (-p0 + 3 * p1 - 3 * p2 + p3) * f3)


def _hermite(p0, p1, p2, p3, f, t0, t1, tm1, t2):
    # cardinal spline with tangents scaled by segment duration to avoid overshoot
    m1 = (p2 - p0) / max(t1 - tm1, 1e-6) * (t1 - t0) * 0.5
    m2 = (p3 - p1) / max(t2 - t0, 1e-6) * (t1 - t0) * 0.5
    f2, f3 = f * f, f * f * f
    return (2 * f3 - 3 * f2 + 1) * p1 + (f3 - 2 * f2 + f) * m1 + (-2 * f3 + 3 * f2) * p2 + (f3 - f2) * m2


def camera_at(t):
    ks = CAM_KEYS
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]:
            f = (t - ks[i][0]) / (ks[i + 1][0] - ks[i][0])
            i0, i3 = max(0, i - 1), min(len(ks) - 1, i + 2)
            T = [ks[j][0] for j in (i0, i, i + 1, i3)]
            eye = _hermite(*(np.array(ks[j][1], float) for j in (i0, i, i + 1, i3)), f, T[1], T[2], T[0], T[3])
            tgt = _hermite(*(np.array(ks[j][2], float) for j in (i0, i, i + 1, i3)), f, T[1], T[2], T[0], T[3])
            eye[1] = max(eye[1], 45.0)
            fov = ks[i][3] + (ks[i + 1][3] - ks[i][3]) * f
            return eye, tgt, fov
    return np.array(ks[-1][1], float), np.array(ks[-1][2], float), ks[-1][3]


def lighting_at(t):
    a, b, f = interp_keys(LIGHT_KEYS, t)
    f = f * f * (3 - 2 * f)
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, tuple):
            out[k] = tuple(x + (y - x) * f for x, y in zip(va, vb))
        else:
            out[k] = va + (vb - va) * f
    el, az = math.radians(out["sun_el"]), math.radians(out["sun_az"])
    out["sun_dir"] = (math.cos(el) * math.sin(az), math.sin(el), -math.cos(el) * math.cos(az))
    return out


def era_at(year):
    e = ERAS[0]
    for x in ERAS:
        if year >= x[0]:
            e = x
    return e


FLAG_COLS = {"lenape": (0.6, 0.3, 0.2), "nl": (0.95, 0.5, 0.1), "en": (0.85, 0.85, 0.85), "gb": (0.8, 0.15, 0.2),
             "us": (0.85, 0.85, 0.9)}


def pop_at(year):
    if year < POP[0][0]:
        return None
    for (y0, p0), (y1, p1) in zip(POP, POP[1:]):
        if y0 <= year <= y1:
            return p0 + (p1 - p0) * (year - y0) / (y1 - y0)
    return POP[-1][1]


def state_at(t):
    eye, tgt, fov = camera_at(t)
    S = lighting_at(t)
    year = year_at(t)
    era = era_at(year)
    S.update(cam=tuple(eye), target=tuple(tgt), fov=fov, year=year, time=t, era=era,
             flag_col=FLAG_COLS[era[2]] if era[2] != "nl" else (0.95, 0.55, 0.15))
    S["fade"] = min(1.0, t / 1.5, (DUR - t) / 2.0)
    S["tilt"] = 1.0
    return S


# ------------------------------------------------------------------ particles
def particles(world, t, year, S):
    P = []
    R = random.Random(1)
    night = S["night"]

    def plume(x, y, z, seed, n=7, size=6, rise=40, col=(0.75, 0.75, 0.75), alpha=0.35, speed=0.12):
        r = random.Random(seed)
        for i in range(n):
            ph = (t * speed + i / n + r.random() * 0.1) % 1
            P.append((x + math.sin(ph * 6 + seed) * 4 * ph + ph * 12, y + ph * rise, z + ph * 6,
                      size * (0.6 + ph * 1.6), *col, alpha * (1 - ph)))

    # Lenape campfires
    if year < 1650:
        for (cx, cz), s in (((650, -2180), 1), ((-330, -3600), 2), ((1300, -3300), 3), ((1450, 250), 4)):
            plume(cx, 8, cz, s, n=8, size=5, rise=45, col=(0.8, 0.8, 0.78), alpha=0.35)
    # chimney smoke over the town (sample of houses)
    if 1630 < year < 1880:
        a = None
        for g in ("house", "row"):
            for k, d in enumerate(world.I[g][::97]):
                if d["birth"] < year < d["death"] and abs(d["pos"][2] - S["target"][2]) < 1500:
                    x, y, z = d["pos"]
                    plume(x, y + d["scale"][1] * 1.4, z, k * 13 + 7, n=4, size=2.5, rise=25,
                          col=(0.82, 0.82, 0.82), alpha=0.25)
    # 1776 fire
    if 1776.71 < year < 1776.75:
        f = (year - 1776.71) / 0.04
        for d in world.I["house"]:
            if abs(d["death"] - 1776.72) < 0.01:
                x, y, z = d["pos"]
                k = (x * 13 + z * 7) % 1
                if (-z - 180) / 970 > f * 1.6 + 0.15:
                    continue
                if R.random() < 0.35:
                    continue
                for i in range(4):
                    ph = (t * 1.1 + i / 4 + k) % 1
                    P.append((x + R.uniform(-5, 5), y + 6 + ph * 26, z + R.uniform(-5, 5), 16 * (1 - ph * 0.5),
                              1.0, 0.5 + 0.4 * (1 - ph), 0.15, 0.9 * (1 - ph)))
                P.append((x, y + 10, z, 38, 1.0, 0.45, 0.1, 0.18))
                plume(x, y + 25, z, int(k * 1000), n=4, size=22, rise=160, col=(0.12, 0.10, 0.10), alpha=0.5,
                      speed=0.2)
    # cannon smoke when the English fleet arrives / 1776
    if 1664.64 < year < 1664.70 or 1776.55 < year < 1776.70:
        for d in world.I["ship"][:60]:
            if d["birth"] < year < d["death"] and d["move"][3] > d["move"][2] and year > d["move"][3]:
                x, y, z = d["pos"]
                x += d["move"][0]
                z += d["move"][1]
                if R.random() < 0.3:
                    plume(x + 10, 8, z, int(x), n=3, size=8, rise=20, col=(0.9, 0.9, 0.9), alpha=0.4, speed=0.4)
    # steamer smoke
    if year > 1812:
        for k, d in enumerate(world.I["steamer"]):
            if d["birth"] < year < d["death"]:
                f = min(1, max(0, (year - d["move"][2]) / max(d["move"][3] - d["move"][2], 1e-6)))
                f = f * f * (3 - 2 * f)
                x = d["pos"][0] + d["move"][0] * f
                z = d["pos"][2] + d["move"][1] * f
                plume(x, 35, z, k, n=5, size=6, rise=35, col=(0.3, 0.3, 0.32), alpha=0.4)
    # fireworks finale
    if t > 704:
        for b in range(6):
            r = random.Random(b * 31 + int((t - 704) / 1.6))
            ph = ((t - 704) / 1.6 + b / 6) % 1
            cx, cy, cz = r.uniform(-900, 400), r.uniform(250, 420), r.uniform(300, 1300)
            col = r.choice([(1, 0.85, 0.4), (1, 0.4, 0.4), (0.5, 0.8, 1), (0.8, 1, 0.6)])
            for i in range(40):
                a = i * 2.39996
                e = math.acos(1 - 2 * (i + 0.5) / 40)
                rr = 90 * math.sqrt(ph)
                P.append((cx + rr * math.sin(e) * math.cos(a), cy + rr * math.cos(e) - 40 * ph * ph,
                          cz + rr * math.sin(e) * math.sin(a), 5, *col, (1 - ph) * 0.95))
    return P


# ------------------------------------------------------------------ overlay
def _flag(c, kind, x, y, w=36, h=24):
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    if kind == "lenape":
        c.set_source_rgb(0.55, 0.35, 0.2)
        c.paint()
        c.set_source_rgb(0.95, 0.88, 0.7)
        c.arc(x + w / 2, y + h / 2, h * 0.28, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgb(0.55, 0.35, 0.2)
        c.arc(x + w / 2, y + h / 2, h * 0.14, 0, 2 * math.pi)
        c.fill()
    elif kind == "nl":
        for i, col in enumerate(((0.95, 0.5, 0.1), (1, 1, 1), (0.1, 0.25, 0.6))):
            c.set_source_rgb(*col)
            c.rectangle(x, y + i * h / 3, w, h / 3 + 0.5)
            c.fill()
    elif kind == "en":
        c.set_source_rgb(1, 1, 1)
        c.paint()
        c.set_source_rgb(0.8, 0.1, 0.15)
        c.rectangle(x + w / 2 - 3, y, 6, h)
        c.rectangle(x, y + h / 2 - 3, w, 6)
        c.fill()
    elif kind == "gb":
        c.set_source_rgb(0.1, 0.17, 0.45)
        c.paint()
        c.set_line_width(5)
        c.set_source_rgb(1, 1, 1)
        c.move_to(x, y)
        c.line_to(x + w, y + h)
        c.move_to(x + w, y)
        c.line_to(x, y + h)
        c.stroke()
        c.rectangle(x + w / 2 - 4, y, 8, h)
        c.rectangle(x, y + h / 2 - 4, w, 8)
        c.fill()
        c.set_source_rgb(0.8, 0.1, 0.15)
        c.rectangle(x + w / 2 - 2, y, 4, h)
        c.rectangle(x, y + h / 2 - 2, w, 4)
        c.fill()
    elif kind == "us":
        for i in range(13):
            c.set_source_rgb(*((0.75, 0.1, 0.15) if i % 2 == 0 else (1, 1, 1)))
            c.rectangle(x, y + i * h / 13, w, h / 13 + 0.5)
            c.fill()
        c.set_source_rgb(0.1, 0.17, 0.45)
        c.rectangle(x, y, w * 0.42, h * 7 / 13)
        c.fill()
    c.restore()
    c.rectangle(x, y, w, h)
    c.set_source_rgba(0, 0, 0, 0.4)
    c.set_line_width(1)
    c.stroke()


def _text(c, txt, x, y, size, font, weight=cairo.FONT_WEIGHT_NORMAL, a=1.0, align="left", spacing=0.0,
          shadow=0.55, col=(1, 1, 1)):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, weight)
    c.set_font_size(size)
    if spacing:
        widths = [c.text_extents(ch).x_advance + spacing for ch in txt]
        tw = sum(widths) - spacing
    else:
        tw = c.text_extents(txt).x_advance
    x0 = x - tw if align == "right" else (x - tw / 2 if align == "center" else x)
    for dx, dy, cc, aa in ((1.5, 1.5, (0, 0, 0), shadow * a), (0, 0, col, a)):
        c.set_source_rgba(*cc, aa)
        if spacing:
            xx = x0 + dx
            for ch, wd in zip(txt, widths):
                c.move_to(xx, y + dy)
                c.show_text(ch)
                xx += wd
        else:
            c.move_to(x0 + dx, y + dy)
            c.show_text(txt)
    return tw


def _person(c, x, y, a):
    c.set_source_rgba(1, 1, 1, a)
    c.arc(x, y - 7, 3.2, 0, 2 * math.pi)
    c.fill()
    c.arc(x, y + 3, 6, math.pi, 2 * math.pi)
    c.fill()


def overlay(t, S, VP):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    year = S["year"]
    y_int = int(math.floor(year + 1e-6))
    ui = min(1.0, max(0.0, (t - 12.5) / 1.5))
    if ui > 0:
        _text(c, f"{y_int}", W - 34, H - 34, 64, "Barlow Condensed", cairo.FONT_WEIGHT_BOLD, ui, "right")
        era = S["era"]
        _flag(c, era[2], 34, H - 74)
        _text(c, era[1], 34, H - 34, 17, "Barlow Condensed", cairo.FONT_WEIGHT_BOLD, ui * 0.95, spacing=1.6)
        p = pop_at(year)
        if p:
            txt = f"c. {int(round(p, -1 if p < 1000 else -2)):,}" if p >= 100 else f"c. {int(p)}"
            tw = _text(c, txt, W - 30, 44, 21, "Barlow Condensed", cairo.FONT_WEIGHT_BOLD, ui * 0.95, "right")
            _person(c, W - 30 - tw - 14, 38, ui * 0.95)
    for t0, t1, title, sub, anchor in CAPTIONS:
        if t0 <= t <= t1:
            a = min(1.0, (t - t0) / 0.8, (t1 - t) / 0.8)
            if anchor == "title":
                c.set_source_rgba(0, 0, 0, 0.25 * a)
                c.paint()
                _text(c, title, W / 2, H / 2 - 10, 50, "Cinzel", cairo.FONT_WEIGHT_BOLD, a, "center", spacing=3,
                      shadow=0.8)
                _text(c, sub, W / 2, H / 2 + 48, 34, "Cinzel", cairo.FONT_WEIGHT_NORMAL, a, "center", spacing=6,
                      shadow=0.8, col=(1.0, 0.9, 0.7))
                continue
            x, y = W / 2, H * 0.80
            if anchor is not None:
                p = np.array([*anchor, 1.0]) @ VP.T
                if p[3] > 1:
                    sx = (p[0] / p[3] * 0.5 + 0.5) * W
                    sy = (1 - (p[1] / p[3] * 0.5 + 0.5)) * H
                    if 120 < sx < W - 120 and 80 < sy < H - 150:
                        x, y = sx, sy - 18
            _text(c, title, x, y, 30, "Cinzel", cairo.FONT_WEIGHT_NORMAL, a, "center", spacing=4, shadow=0.7)
            if sub:
                _text(c, sub, W / 2, H - 92 if anchor is None or y > H * 0.7 else H - 92, 21, "EB Garamond",
                      cairo.FONT_WEIGHT_NORMAL, a * 0.95, "center", shadow=0.8)
    surf.flush()
    return bytes(surf.get_data())
