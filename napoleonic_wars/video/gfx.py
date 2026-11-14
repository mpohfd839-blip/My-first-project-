"""Cartoon drawing library (pycairo) for the Napoleonic Wars video."""
import math
import random

import cairo

W, H = 1280, 720


# ------------------------------------------------------------------ basics
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def mixc(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def shade(c, k):
    """k<0 darker, k>0 lighter."""
    if k < 0:
        return tuple(v * (1 + k) for v in c[:3]) + (c[3],)
    return tuple(v + (1 - v) * k for v in c[:3]) + (c[3],)


def ellipse(c, x, y, rx, ry, rot=0.0):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(max(rx, 0.01), max(ry, 0.01))
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def fill(c, col):
    c.set_source_rgba(*col)
    c.fill()


def fill_ol(c, col, ol=None, w=2.5):
    c.set_source_rgba(*col)
    c.fill_preserve()
    c.set_source_rgba(*(ol or shade(col, -0.45)))
    c.set_line_width(w)
    c.stroke()


def seg(c, p0, p1, w, col, cap=cairo.LINE_CAP_ROUND):
    c.set_line_cap(cap)
    c.set_line_width(w)
    c.move_to(*p0)
    c.line_to(*p1)
    c.set_source_rgba(*col)
    c.stroke()


def poly(c, pts, close=True):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    if close:
        c.close_path()


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def vgrad(c, y0, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *c0)
    g.add_color_stop_rgba(1, *c1)
    return g


INK = hexc("#2A211C")
SKIN = hexc("#F4C9A0")
WHITE = hexc("#F7F4EC")
GOLD = hexc("#E9B93A")
BLACK = hexc("#22201F")
RED = hexc("#C8322F")
BLUE = hexc("#2B4C9B")
BROWN = hexc("#7A5232")
GREY = hexc("#6C6F78")

FLAGS = {
    "fr": [("v", ["#24418F", "#F4F1EA", "#D2333A"])],
    "uk": [("uk", None)],
    "au": [("h", ["#E8E4D8", "#E8E4D8"]), ("eagle", "#222")],
    "pr": [("h", ["#F2F2F2", "#1C1C1C"])],
    "ru": [("h", ["#F4F4F4", "#2B4FA0", "#D0343A"])],
    "es": [("h", ["#C8302C", "#F2C230", "#F2C230", "#C8302C"])],
    "white": [("h", ["#F7F4EC"])],
    "sw": [("sw", None)],
    "red": [("h", ["#C8322F"])],
    "us": [("h", ["#F3F3F3"])],
    "de": [("h", ["#1C1C1C", "#F2F2F2", "#C8302C"])],
    "ah": [("h", ["#C8302C", "#F2F2F2", "#C8302C"])],
    "rs": [("h", ["#C8302C", "#2B4FA0", "#F2F2F2"])],
    "be": [("v", ["#1C1C1C", "#F2C230", "#C8302C"])],
    "it": [("v", ["#2E8B4A", "#F2F2F2", "#C8302C"])],
    "usa": [("h", ["#B22234", "#F2F2F2"] * 6 + ["#B22234"]), ("canton", "#3C3B6E")],
    "tr": [("h", ["#C8302C"]), ("crescent", "#F2F2F2")],
    "ot": [("h", ["#C8302C"]), ("crescent", "#F2F2F2")],
    "mx": [("v", ["#2E8B4A", "#F2F2F2", "#C8302C"])],
}


# ------------------------------------------------------------------ flags
def flag(c, x, y, t, kind="fr", w=70, h=46, pole=120, face=1, eagle=False, wave=1.0):
    """Pole base at (x, y); flag at top, waving."""
    seg(c, (x, y), (x, y - pole), 5, BROWN)
    if eagle:
        ellipse(c, x, y - pole - 6, 9, 7)
        fill(c, GOLD)
        poly(c, [(x - 14, y - pole - 10), (x, y - pole - 4), (x + 14, y - pole - 10), (x, y - pole + 2)])
        fill(c, GOLD)
    top = y - pole + 4

    def pt(u, v):
        X = x + face * u * w
        Y = top + v * h + wave * 5 * math.sin(t * 6 + u * 5) * u
        return X, Y

    c.save()
    n = 12
    c.move_to(*pt(0, 0))
    for i in range(1, n + 1):
        c.line_to(*pt(i / n, 0))
    for i in range(n, -1, -1):
        c.line_to(*pt(i / n, 1))
    c.close_path()
    c.clip_preserve()
    c.set_source_rgba(*WHITE)
    c.fill()
    for typ, cols in FLAGS.get(kind, FLAGS["fr"]):
        if typ == "v":
            k = len(cols)
            for i, col in enumerate(cols):
                c.move_to(*pt(i / k, -0.1))
                for j in range(1, 5):
                    c.line_to(*pt(i / k + j / (4 * k), -0.1))
                c.line_to(*pt((i + 1) / k, 1.1))
                for j in range(3, -1, -1):
                    c.line_to(*pt(i / k + j / (4 * k), 1.1))
                c.close_path()
                fill(c, hexc(col))
        elif typ == "h":
            k = len(cols)
            for i, col in enumerate(cols):
                c.move_to(*pt(0, i / k))
                for j in range(1, n + 1):
                    c.line_to(*pt(j / n, i / k))
                for j in range(n, -1, -1):
                    c.line_to(*pt(j / n, (i + 1) / k))
                c.close_path()
                fill(c, hexc(col))
        elif typ == "eagle":
            cx, cy = pt(0.5, 0.5)
            ellipse(c, cx, cy, 8, 10)
            fill(c, hexc(cols))
            poly(c, [(cx - 16, cy - 6), (cx, cy), (cx + 16, cy - 6), (cx, cy + 6)])
            fill(c, hexc(cols))
        elif typ == "uk":
            c.set_source_rgba(*hexc("#1F3A7A"))
            c.paint()
            for (a, b), (cc, ww) in [(((0, 0), (1, 1)), ("#F4F4F4", 9)), (((0, 1), (1, 0)), ("#F4F4F4", 9)),
                                     (((0, 0), (1, 1)), ("#C8302C", 3.5)), (((0, 1), (1, 0)), ("#C8302C", 3.5)),
                                     (((0.5, 0), (0.5, 1)), ("#F4F4F4", 14)), (((0, 0.5), (1, 0.5)), ("#F4F4F4", 14)),
                                     (((0.5, 0), (0.5, 1)), ("#C8302C", 8)), (((0, 0.5), (1, 0.5)), ("#C8302C", 8))]:
                c.set_line_width(ww)
                c.move_to(*pt(*a))
                for j in range(1, 9):
                    c.line_to(*pt(lerp(a[0], b[0], j / 8), lerp(a[1], b[1], j / 8)))
                c.set_source_rgba(*hexc(cc))
                c.stroke()
        elif typ == "canton":
            c.move_to(*pt(0, 0))
            for j in range(1, 6):
                c.line_to(*pt(0.4 * j / 5, 0))
            c.line_to(*pt(0.4, 0.54))
            for j in range(5, -1, -1):
                c.line_to(*pt(0.4 * j / 5, 0.54))
            c.close_path()
            fill(c, hexc(cols))
        elif typ == "crescent":
            cx, cy = pt(0.42, 0.5)
            ellipse(c, cx, cy, h * 0.28, h * 0.28)
            fill(c, hexc(cols))
            cx2, cy2 = pt(0.47, 0.5)
            ellipse(c, cx2, cy2, h * 0.23, h * 0.23)
            fill(c, hexc("#C8302C"))
        elif typ == "sw":
            c.set_source_rgba(*hexc("#2D63B0"))
            c.paint()
            for a, b in (((0, 0.5), (1, 0.5)), ((0.33, 0), (0.33, 1))):
                c.set_line_width(9)
                c.move_to(*pt(*a))
                c.line_to(*pt(*b))
                c.set_source_rgba(*hexc("#F2C230"))
                c.stroke()
    c.restore()
    c.move_to(*pt(0, 0))
    for i in range(1, n + 1):
        c.line_to(*pt(i / n, 0))
    for i in range(n, -1, -1):
        c.line_to(*pt(i / n, 1))
    c.close_path()
    c.set_line_width(2)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.stroke()


# ------------------------------------------------------------------ people
UNIFORMS = {
    "fr": dict(coat="#2B4C9B", trou="#F1EEE6", hat="shako", plume="#D2333A", belts=True, facing="#F1EEE6"),
    "br": dict(coat="#C8322F", trou="#4A4F66", hat="shako", plume="#F1EEE6", belts=True, facing="#F1EEE6"),
    "au": dict(coat="#EEEDE6", trou="#EEEDE6", hat="shako", plume="#222222", belts=True, facing="#B83A3A"),
    "pr": dict(coat="#1F2A44", trou="#8A8E98", hat="shako", plume="#222222", belts=True, facing="#C8322F"),
    "ru": dict(coat="#2F5A35", trou="#EEEDE6", hat="shako", plume="#222222", belts=True, facing="#C8322F"),
    "guard": dict(coat="#22408A", trou="#F1EEE6", hat="bearskin", plume="#D2333A", belts=True, facing="#C8322F"),
    "cuir": dict(coat="#22408A", trou="#F1EEE6", hat="helmet", plume="#C8322F", belts=False, cuirass=True),
    "conscript": dict(coat="#3A5AA8", trou="#E9E3D2", hat="shako", plume="#D2333A", belts=True, young=True),
    "sp": dict(coat="#6B4A2E", trou="#3B3530", hat="brimmed", plume=None, sash="#C8302C"),
    "mam": dict(coat="#C9473B", trou="#F2D27A", hat="turban", plume="#3FA3A0", sash="#2E7D7A"),
    "sailor": dict(coat="#2A3550", trou="#F1EEE6", hat="cap_round", plume=None),
    "cossack": dict(coat="#3A3A55", trou="#A33A3A", hat="fur", plume=None),
    "fr_rag": dict(coat="#3A5490", trou="#C9BFA6", hat="bicorne_bare", plume=None, belts=False, ragged=True),
}

CIV_COATS = ["#8C5A3C", "#5C7FA3", "#B04A3A", "#6B8E4E", "#9C7A4E", "#4E5B6E", "#B38A3C", "#7A4E7A"]


def person(c, x, y, s=1.0, face=1, coat="#2B4C9B", trou="#F1EEE6", hat="none", plume=None,
           skin=None, expr="neutral", arms="down", walk=None, hair=None, hair_col="#4A3222",
           dress=None, robe=None, epaulettes=False, belts=False, facing=None, cuirass=False,
           sash=None, item=None, t=0.0, look=0, young=False, ragged=False, moust=False,
           seated=False, empty_sleeve=False, waist=None, coat_long=False, barefoot=False, blink=True):
    skin = skin or SKIN
    coat_c = hexc(coat) if isinstance(coat, str) else coat
    trou_c = hexc(trou) if isinstance(trou, str) else trou
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    bob = 0
    a = 0
    if walk is not None:
        a = math.sin(walk) * 11
        bob = -abs(math.cos(walk)) * 3
    # ---- robe behind
    if robe:
        poly(c, [(-22, -104), (22, -104), (40, 0), (-46, 0)])
        fill(c, hexc(robe))
        seg(c, (-46, -2), (40, -2), 7, WHITE)
    c.translate(0, bob)
    # ---- legs
    if dress:
        poly(c, [(-20, -70), (20, -70), (40, 0), (-40, 0)])
        fill_ol(c, hexc(dress))
    elif seated:
        seg(c, (4, -52), (26, -50), 15, trou_c)
        seg(c, (26, -50), (26, -18), 14, trou_c)
        seg(c, (26, -24), (26, -4), 15, BLACK)
    else:
        for sx, sw in ((-1, a), (1, -a)):
            fx = sx * 9 + sw
            seg(c, (sx * 9, -56), (fx, -6), 15, trou_c)
            if not barefoot:
                seg(c, (fx * 0.98, -20), (fx, -4), 15.5, BLACK)
                ellipse(c, fx + 5, -3, 10, 5)
                fill(c, BLACK)
            else:
                ellipse(c, fx + 4, -3, 9, 4)
                fill(c, skin)
    if coat_long:
        poly(c, [(-24, -100), (24, -100), (28, -38), (-28, -38)])
        fill(c, shade(coat_c, -0.08))
    # ---- arms behind (far arm)
    far = {"down": (-20, -62), "point": (-22, -64), "up": (-30, -152), "musket": (-20, -62),
           "flag": (-22, -64), "crown": (-26, -158), "hand_in": (-20, -62), "hold": (-24, -66),
           "write": (-20, -62), "cheer": (-34, -150), "shrug": (-36, -96), "fist": (-20, -62),
           "aim": (36, -98), "hug": (30, -84), "cradle": (32, -110)}.get(arms, (-20, -62))
    if not empty_sleeve:
        seg(c, (-16, -98), far, 13, shade(coat_c, -0.15))
        ellipse(c, far[0], far[1], 6.5, 6.5)
        fill(c, skin)
    # ---- torso
    rrect(c, -24, -110, 48, 62, 15)
    fill_ol(c, coat_c, w=2)
    if waist:
        poly(c, [(-8, -108), (8, -108), (12, -50), (-12, -50)])
        fill(c, hexc(waist))
    if facing and not cuirass:
        poly(c, [(-6, -108), (6, -108), (0, -86)])
        fill(c, hexc(facing))
        for k in range(3):
            ellipse(c, 0, -80 + k * 10, 2.2, 2.2)
            fill(c, GOLD)
    if cuirass:
        rrect(c, -22, -106, 44, 46, 12)
        g = vgrad(c, -106, -60, hexc("#E6E9EE"), hexc("#9AA2AE"))
        c.set_source(g)
        c.fill()
    if belts:
        seg(c, (-18, -104), (16, -56), 5, WHITE)
        seg(c, (18, -104), (-16, -56), 5, WHITE)
    if sash:
        seg(c, (-24, -60), (24, -60), 9, hexc(sash))
    if ragged:
        for k in range(3):
            poly(c, [(-20 + k * 14, -50), (-14 + k * 14, -42), (-8 + k * 14, -50)])
            fill(c, coat_c)
    seg(c, (-24, -50), (24, -50), 3, shade(coat_c, -0.3))
    if epaulettes:
        for sx in (-1, 1):
            ellipse(c, sx * 21, -106, 11, 5)
            fill(c, GOLD)
            for k in range(4):
                seg(c, (sx * 21 - 8 + k * 5, -103), (sx * 21 - 8 + k * 5, -96), 2, GOLD)
    # ---- head
    hy = -138
    if hair == "long":
        rrect(c, -27, hy - 22, 54, 52, 16)
        fill(c, hexc(hair_col))
    if hair == "curls":
        for k in range(6):
            ellipse(c, -24 + k * 9.5, hy - 18 + (k % 2) * 4, 11, 11)
            fill(c, hexc(hair_col))
        for sx in (-1, 1):
            for k in range(3):
                ellipse(c, sx * 26, hy - 4 + k * 10, 9, 9)
                fill(c, hexc(hair_col))
    if hair == "bun":
        ellipse(c, -16, hy - 24, 14, 13)
        fill(c, hexc(hair_col))
    ellipse(c, -24, hy + 2, 6, 8)
    fill(c, shade(skin, -0.08))
    ellipse(c, 0, hy, 28, 28 if not young else 27)
    fill_ol(c, skin, w=1.6)
    if hair in ("short", "long", "bald", "wig", "curls", "bun", "pig"):
        if hair == "bald":
            ellipse(c, -22, hy - 4, 8, 11)
            fill(c, hexc(hair_col))
        elif hair == "wig":
            for k in range(3):
                ellipse(c, -24, hy - 8 + k * 9, 8, 6)
                fill(c, hexc("#ECE8DF"))
            ellipse(c, 0, hy - 18, 26, 14)
            fill(c, hexc("#ECE8DF"))
        else:
            c.save()
            ellipse(c, 0, hy, 28.5, 28.5)
            c.clip()
            ellipse(c, -6, hy - 26, 34, 18)
            fill(c, hexc(hair_col))
            if hair == "short":
                poly(c, [(4, hy - 14), (14, hy - 22), (18, hy - 10), (24, hy - 20), (30, hy - 30), (-10, hy - 30)])
                fill(c, hexc(hair_col))
            c.restore()
            if hair == "pig":
                seg(c, (-26, hy), (-36, hy + 18), 6, hexc(hair_col))
    # face
    ex = 7 + look * 3
    blinking = blink and (t * 0.7 + x * 0.013) % 3.1 < 0.12
    for k, dx in enumerate((ex - 8, ex + 8)):
        if blinking or expr in ("sleep", "sad_closed"):
            seg(c, (dx - 4, hy - 1), (dx + 4, hy - 1), 2.4, INK)
        else:
            ellipse(c, dx, hy - 2, 3.4, 4.2)
            fill(c, INK)
            ellipse(c, dx + 1, hy - 3.5, 1.1, 1.1)
            fill(c, (1, 1, 1, 0.9))
    br = {"stern": (3, -3), "angry": (5, -5), "worried": (-4, 3), "sad": (-4, 3), "shock": (-2, -2),
          "happy": (0, 0), "smirk": (2, -3), "neutral": (0, 0), "sleep": (0, 0), "proud": (1, -1),
          "shout": (4, -4)}.get(expr, (0, 0))
    for dx, d in ((ex - 8, 1), (ex + 8, -1)):
        y0 = hy - 10 + (br[0] if d > 0 else br[1]) * 0.5
        y1 = hy - 10 + (br[1] if d > 0 else br[0]) * 0.5
        seg(c, (dx - 5, y0 - (2 if expr == "shock" else 0)), (dx + 5, y1 - (2 if expr == "shock" else 0)), 2.2, INK)
    ellipse(c, ex + 13, hy + 4, 4, 3.4)
    fill(c, shade(skin, -0.15))
    my = hy + 13
    c.set_line_width(2.4)
    c.set_source_rgba(*INK)
    if expr in ("happy", "proud"):
        c.arc(ex, my - 4, 7, 0.15 * math.pi, 0.85 * math.pi)
        c.stroke()
    elif expr == "smirk":
        c.move_to(ex - 5, my)
        c.curve_to(ex, my + 2, ex + 5, my, ex + 8, my - 4)
        c.stroke()
    elif expr in ("worried", "sad"):
        c.arc(ex, my + 6, 6, 1.2 * math.pi, 1.8 * math.pi)
        c.stroke()
    elif expr in ("shock", "shout"):
        ellipse(c, ex, my + 1, 4.5, 6 if expr == "shock" else 5)
        fill(c, hexc("#6E2B2B"))
    elif expr == "angry" or expr == "stern":
        seg(c, (ex - 5, my + 1), (ex + 5, my + 1), 2.4, INK)
    else:
        seg(c, (ex - 4, my), (ex + 4, my), 2.2, INK)
    if moust:
        seg(c, (ex - 6, my - 4), (ex + 7, my - 4), 4.5, hexc(hair_col if hair_col != "#4A3222" else "#5A3A22"))
    if expr not in ("sleep",) and expr in ("happy", "proud", "neutral", "smirk"):
        ellipse(c, ex - 12, hy + 8, 4, 2.4)
        c.set_source_rgba(0.95, 0.5, 0.5, 0.35)
        c.fill()
    # hat
    draw_hat(c, hat, hy, plume, t)
    # ---- near arm + item
    near = {"down": (22, -62), "point": (56, -116), "up": (30, -152), "musket": (22, -70),
            "flag": (30, -118), "crown": (26, -158), "hand_in": (6, -84), "hold": (40, -82),
            "write": (40, -70), "cheer": (34, -150), "shrug": (36, -96), "fist": (44, -118),
            "aim": (42, -96), "hug": (34, -88), "cradle": (36, -112)}.get(arms, (22, -62))
    seg(c, (16, -98), near, 13, coat_c)
    ellipse(c, near[0], near[1], 6.5, 6.5)
    fill(c, skin)
    if arms == "musket":
        seg(c, (22, -10), (26, -178), 5, BROWN)
        seg(c, (26, -178), (27, -205), 2, hexc("#C9CED6"))
    if arms == "aim":
        seg(c, (-6, -96), (80, -100), 5, BROWN)
        seg(c, (80, -100), (102, -101), 2, hexc("#C9CED6"))
    if arms == "flag":
        flag(c, near[0], -20, t, kind=item or "fr", pole=200, w=74, h=48)
    if arms == "crown" and item != "none":
        draw_crown(c, 0, -172, 1.0, laurel=(item == "laurel"))
    if arms in ("hold", "write") and item == "paper":
        poly(c, [(36, -90), (66, -96), (70, -60), (40, -56)])
        fill_ol(c, hexc("#F3EAD3"))
    if arms == "cradle":
        ellipse(c, 2, -118, 22, 14)
        fill_ol(c, WHITE)
        ellipse(c, 18, -124, 10, 10)
        fill(c, skin)
    if item == "sword" and arms in ("point", "up", "fist"):
        seg(c, near, (near[0] + 26, near[1] - 52), 4, hexc("#D5DAE2"))
    c.restore()


def draw_crown(c, x, y, s=1.0, laurel=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if laurel:
        for sx in (-1, 1):
            for k in range(5):
                a = math.pi * (0.15 + k * 0.15)
                ellipse(c, sx * 20 * math.cos(a), 10 - 16 * math.sin(a), 7, 3.5, rot=sx * (a + 0.5))
                fill(c, GOLD)
    else:
        poly(c, [(-22, 10), (-24, -14), (-12, -2), (0, -20), (12, -2), (24, -14), (22, 10)])
        fill_ol(c, GOLD, hexc("#9A7414"))
        for dx in (-12, 0, 12):
            ellipse(c, dx, 4, 3, 3)
            fill(c, RED)
    c.restore()


def draw_hat(c, hat, hy, plume, t):
    top = hy - 26
    if hat == "shako":
        poly(c, [(-18, top + 6), (18, top + 6), (20, top - 26), (-20, top - 26)])
        fill(c, BLACK)
        seg(c, (-22, top + 6), (8, top + 7), 4, BLACK)
        ellipse(c, 10, top - 8, 5, 6)
        fill(c, GOLD)
        if plume:
            ellipse(c, 2, top - 36, 5, 11)
            fill(c, hexc(plume))
    elif hat == "bicorne_side":
        c.move_to(-46, top + 8)
        c.curve_to(-40, top - 30, 40, top - 30, 46, top + 8)
        c.curve_to(20, top, -20, top, -46, top + 8)
        fill(c, BLACK)
        ellipse(c, 14, top - 5, 6, 6)
        fill(c, hexc("#24418F"))
        ellipse(c, 14, top - 5, 4, 4)
        fill(c, WHITE)
        ellipse(c, 14, top - 5, 2, 2)
        fill(c, RED)
    elif hat in ("bicorne_front", "bicorne_bare"):
        c.move_to(-30, top + 6)
        c.curve_to(-26, top - 6, -10, top - 34, 4, top - 34)
        c.curve_to(18, top - 34, 30, top - 6, 34, top + 6)
        c.close_path()
        fill(c, BLACK)
        if hat == "bicorne_front" and plume:
            ellipse(c, 0, top - 36, 12, 6)
            fill(c, hexc(plume))
    elif hat == "bearskin":
        rrect(c, -24, top - 56, 48, 66, 20)
        fill(c, hexc("#1B1A1A"))
        ellipse(c, -6, top - 50, 10, 8)
        fill(c, hexc("#C8322F"))
        if plume:
            ellipse(c, 14, top - 46, 4, 12)
            fill(c, hexc(plume))
    elif hat == "helmet":
        ellipse(c, 0, top + 2, 24, 22)
        fill(c, hexc("#C9CED6"))
        seg(c, (-20, top - 16), (20, top - 16), 6, GOLD)
        c.move_to(-4, top - 20)
        c.curve_to(-30, top - 20, -40, top + 10, -34, top + 30)
        c.set_line_width(7)
        c.set_source_rgba(*BLACK)
        c.stroke()
        if plume:
            ellipse(c, 10, top - 24, 4, 12)
            fill(c, hexc(plume))
    elif hat == "turban":
        ellipse(c, 0, top + 2, 30, 16)
        fill(c, WHITE)
        ellipse(c, 0, top - 6, 24, 14)
        fill(c, hexc("#E7D9B8"))
        if plume:
            ellipse(c, 8, top - 22, 4, 12)
            fill(c, hexc(plume))
    elif hat == "crown":
        draw_crown(c, 0, top - 4, 0.9)
    elif hat == "mitre":
        poly(c, [(-18, top + 6), (18, top + 6), (12, top - 34), (0, top - 46), (-12, top - 34)])
        fill_ol(c, WHITE, GOLD)
        seg(c, (0, top + 4), (0, top - 40), 4, GOLD)
    elif hat == "tricorne":
        poly(c, [(-34, top + 6), (34, top + 6), (22, top - 14), (-22, top - 14)])
        fill(c, BLACK)
    elif hat == "cap":
        c.move_to(-24, top + 8)
        c.curve_to(-26, top - 20, 10, top - 26, 26, top - 2)
        c.line_to(24, top + 8)
        fill(c, hexc("#C8322F"))
    elif hat == "cap_round":
        ellipse(c, 0, top + 4, 26, 9)
        fill(c, BLACK)
        rrect(c, -18, top - 8, 36, 12, 5)
        fill(c, BLACK)
    elif hat == "brimmed":
        ellipse(c, 0, top + 6, 40, 8)
        fill(c, hexc("#3A2C22"))
        rrect(c, -18, top - 16, 36, 22, 9)
        fill(c, hexc("#3A2C22"))
    elif hat == "fur":
        rrect(c, -24, top - 22, 48, 30, 12)
        fill(c, hexc("#4A3828"))
    elif hat == "bonnet":
        ellipse(c, 0, top + 4, 30, 18)
        fill(c, hexc("#F3E7D3"))


# ---- named characters
def napoleon(c, x, y, s=1.0, **kw):
    d = dict(coat="#22408A", trou="#F1EEE6", hat="bicorne_side", epaulettes=True, waist="#F1EEE6",
             hair="short", hair_col="#3A2A1E", expr="stern", facing=None)
    d.update(kw)
    person(c, x, y, s, **d)


def young_nap(c, x, y, s=1.0, **kw):
    d = dict(coat="#26437F", trou="#F1EEE6", hat="none", hair="long", hair_col="#3A2A1E", expr="stern",
             waist="#F1EEE6", young=True)
    d.update(kw)
    person(c, x, y, s, **d)


def old_nap(c, x, y, s=1.0, **kw):
    d = dict(coat="#2F5A3A", trou="#F1EEE6", hat="none", hair="bald", hair_col="#4A3828", expr="sad",
             waist="#F1EEE6")
    d.update(kw)
    person(c, x, y, s * 1.04, **d)


def wellington(c, x, y, s=1.0, **kw):
    d = dict(coat="#26304A", trou="#E9E3D2", hat="bicorne_front", hair="short", hair_col="#6A5038",
             expr="stern", coat_long=True)
    d.update(kw)
    person(c, x, y, s * 1.08, **d)


def nelson(c, x, y, s=1.0, **kw):
    d = dict(coat="#1E2A4A", trou="#F1EEE6", hat="bicorne_front", hair="short", hair_col="#9A8C7A",
             expr="stern", epaulettes=True, empty_sleeve=True, waist="#F1EEE6")
    d.update(kw)
    person(c, x, y, s, **d)


def tsar(c, x, y, s=1.0, **kw):
    d = dict(coat="#2F5A35", trou="#F1EEE6", hat="none", hair="bald", hair_col="#D8B66A", epaulettes=True,
             expr="stern", moust=False)
    d.update(kw)
    person(c, x, y, s * 1.06, **d)


def king(c, x, y, s=1.0, robe="#9C2A3A", **kw):
    d = dict(coat="#6A2A6A", trou="#F1EEE6", hat="crown", hair="wig", robe=robe, expr="neutral")
    d.update(kw)
    person(c, x, y, s, **d)


def lady(c, x, y, s=1.0, dress="#F4EFE6", hair_col="#3A2A1E", **kw):
    d = dict(coat=dress, dress=dress, hair="curls", hair_col=hair_col, expr="neutral")
    d.update(kw)
    person(c, x, y, s, **d)


def civilian(c, x, y, s, i, t, **kw):
    r = random.Random(i)
    d = dict(coat=r.choice(CIV_COATS), trou=r.choice(["#4A3F35", "#6E6250", "#3E4A5A", "#E3DACA"]),
             hat=r.choice(["cap", "none", "tricorne", "none", "bonnet"]), hair=r.choice(["short", "bun", "short"]),
             hair_col=r.choice(["#3A2A1E", "#6A4A2A", "#A8803A", "#222222"]),
             skin=r.choice([SKIN, hexc("#E8B98E"), hexc("#D9A577"), hexc("#F6D2B0")]))
    d.update(kw)
    person(c, x, y, s, t=t, **d)


def soldier(c, x, y, s, uni="fr", t=0.0, face=1, walk=None, arms="musket", expr="stern", **kw):
    d = dict(UNIFORMS[uni])
    young = d.pop("young", False)
    d.update(kw)
    person(c, x, y, s, face=face, walk=walk, arms=arms, expr=expr, t=t, young=young, hair="short", **d)


def army(c, x0, x1, y, rows=3, s=0.55, uni="fr", t=0.0, face=1, march=False, spacing=34, depth=26,
         expr="stern", flags=None, arms="musket", seed=0, speed=4.0, run=False, **kw):
    """Formation of soldiers between x0..x1 with feet line at y (front row)."""
    r = random.Random(seed)
    for row in range(rows - 1, -1, -1):
        k = 1 - row * 0.12
        yy = y - row * depth
        ss = s * k
        sp = spacing * k
        n = int((x1 - x0) / sp)
        off = (row % 2) * sp / 2
        for i in range(n + 1):
            xx = x0 + off + i * sp + r.uniform(-2, 2)
            w = (t * speed * (1.6 if run else 1) + i * 0.7 + row) if (march or run) else None
            soldier(c, xx, yy, ss, uni=uni, t=t, face=face, walk=w, arms=arms, expr=expr, **kw)
        if flags and row == 1:
            fx = lerp(x0, x1, 0.5)
            flag(c, fx, yy - 4, t, kind=flags, pole=150 * ss / 0.55, w=70 * ss / 0.55, h=46 * ss / 0.55,
                 face=face, eagle=(flags == "fr"))


def crowd(c, x0, x1, y, rows=3, s=0.55, t=0.0, cheer=True, seed=3, face=1, flags=None, spacing=30,
          expr="happy", arms=None, walk=False):
    r = random.Random(seed)
    for row in range(rows - 1, -1, -1):
        k = 1 - row * 0.1
        yy = y - row * 24
        n = int((x1 - x0) / (spacing * k))
        for i in range(n + 1):
            xx = x0 + i * spacing * k + r.uniform(-6, 6) + (row % 2) * 12
            hop = abs(math.sin(t * 6 + i * 1.3 + row)) * 6 if cheer else 0
            a = arms or (r.choice(["cheer", "up", "down", "fist"]) if cheer else "down")
            civilian(c, xx, yy - hop, s * k, i * 7 + row * 101 + seed, t, face=face if r.random() > 0.15 else -face,
                     arms=a, expr=expr, walk=(t * 5 + i) if walk else None)
        if flags and row == 1:
            for j, fk in enumerate(flags):
                flag(c, lerp(x0, x1, (j + 1) / (len(flags) + 1)), yy, t, kind=fk, pole=170 * s / 0.55, w=60, h=40)


# ------------------------------------------------------------------ horse
def horse(c, x, y, s=1.0, face=1, col="#F2EEE6", t=0.0, gallop=False, rider=None, rider_fn=None, rear=0.0):
    hc = hexc(col)
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ph = t * (9 if gallop else 0)
    c.save()
    c.translate(0, -70)
    c.rotate(-rear * 0.35)
    c.translate(0, 70)
    # tail
    c.move_to(-62, -100)
    c.curve_to(-90, -90, -88, -50, -80, -40)
    c.set_line_width(12)
    c.set_source_rgba(*shade(hc, -0.4))
    c.stroke()
    # legs
    for i, (lx, o) in enumerate(((-44, 0), (-30, 1.6), (34, 3.1), (48, 4.7))):
        sw = math.sin(ph + o) * (18 if gallop else 0)
        col = shade(hc, -0.15) if i % 2 == 0 else hc
        seg(c, (lx, -78), (lx + sw, -8), 13, col)
        seg(c, (lx + sw, -12), (lx + sw, -2), 14, INK)
    ellipse(c, 0, -94, 70, 34)
    fill_ol(c, hc, w=2)
    # neck + head
    poly(c, [(36, -116), (60, -168), (84, -160), (72, -104)])
    fill(c, hc)
    ellipse(c, 84, -160, 24, 14, rot=0.5)
    fill_ol(c, hc, w=2)
    poly(c, [(58, -176), (62, -194), (70, -178)])
    fill(c, hc)
    ellipse(c, 76, -166, 2.8, 2.8)
    fill(c, INK)
    c.move_to(54, -176)
    c.curve_to(40, -150, 36, -126, 36, -112)
    c.set_line_width(9)
    c.set_source_rgba(*shade(hc, -0.4))
    c.stroke()
    # saddle cloth
    rrect(c, -22, -126, 42, 34, 6)
    fill(c, hexc("#B5293A"))
    seg(c, (-22, -96), (20, -96), 3, GOLD)
    if rider_fn:
        c.save()
        c.translate(-2, -102)
        c.scale(face, 1)
        rider_fn(c, 0, 0)
        c.restore()
    c.restore()
    c.restore()


def mounted(c, x, y, s, face, t, who="napoleon", col="#F2EEE6", gallop=False, rear=0.0, **kw):
    fn = {"napoleon": napoleon, "wellington": wellington, "ynap": young_nap}.get(who)

    def rider(cc, rx, ry):
        if fn:
            fn(cc, rx, ry, 0.82, face=face, seated=True, t=t, **kw)
        else:
            d = dict(UNIFORMS[who])
            d.pop("young", None)
            d.update(kw)
            person(cc, rx, ry, 0.82, face=face, seated=True, t=t, hair="short", **d)
    horse(c, x, y, s, face, col, t, gallop, rider_fn=rider, rear=rear)


def cavalry(c, x0, x1, y, t, uni="cuir", face=1, s=0.5, rows=2, seed=1, cols=("#7A5232", "#3A2A22", "#A87A4A"),
            gallop=True, speed=0):
    r = random.Random(seed)
    for row in range(rows - 1, -1, -1):
        k = 1 - row * 0.12
        n = int((x1 - x0) / (95 * s * k))
        for i in range(n + 1):
            xx = x0 + i * 95 * s * k + r.uniform(-8, 8) + (row % 2) * 30 * s + face * speed * t
            mounted(c, xx, y - row * 30, s * k, face, t + i * 0.3 + row, who=uni, col=r.choice(cols), gallop=gallop)


# ------------------------------------------------------------------ backgrounds
SKIES = {
    "day": ("#7EC4EC", "#D7EEF8"), "dawn": ("#8FA6C9", "#F6D6B2"), "storm": ("#5E6A78", "#9AA5AE"),
    "sunset": ("#F08A5D", "#FBD58C"), "night": ("#141A3A", "#3A3F6E"), "fire": ("#3A1A1A", "#D0582A"),
    "dusk": ("#5E4E8A", "#E59A84"), "winter": ("#AFC3D6", "#E8EEF3"), "desert": ("#8CC6EA", "#F6E3B8"),
    "grey": ("#8D97A3", "#C9CFD5"), "gold": ("#E9A55A", "#FBE3A6"),
}
GROUNDS = {
    "grass": ("#7FBF5A", "#5E9E45"), "mud": ("#7A6A48", "#5A4A33"), "snow": ("#F4F7FA", "#D7E1EA"),
    "sand": ("#EBCB8B", "#D8AE68"), "road": ("#B9A27A", "#9C845E"), "dark": ("#3B4A3A", "#2A3528"),
    "dry": ("#C9B27A", "#AE9358"), "stone": ("#B8B2A6", "#9A9488"), "autumn": ("#A6B45A", "#8A9445"),
}


def sky(c, kind="day", y1=H):
    a, b = SKIES[kind]
    c.set_source(vgrad(c, 0, y1, hexc(a), hexc(b)))
    c.rectangle(0, 0, W, y1)
    c.fill()


def sun(c, x, y, r=46, col="#FFE9A8", t=0.0, rays=False):
    if rays:
        c.save()
        c.translate(x, y)
        c.rotate(t * 0.1)
        for k in range(14):
            a = k * math.pi / 7
            poly(c, [(0, 0), (900 * math.cos(a - 0.06), 900 * math.sin(a - 0.06)),
                     (900 * math.cos(a + 0.06), 900 * math.sin(a + 0.06))])
            c.set_source_rgba(1, 0.95, 0.7, 0.13)
            c.fill()
        c.restore()
    g = cairo.RadialGradient(x, y, r * 0.5, x, y, r * 2.4)
    g.add_color_stop_rgba(0, 1, 0.97, 0.8, 0.5)
    g.add_color_stop_rgba(1, 1, 0.97, 0.8, 0)
    c.set_source(g)
    c.arc(x, y, r * 2.4, 0, 2 * math.pi)
    c.fill()
    ellipse(c, x, y, r, r)
    fill(c, hexc(col))


def moon(c, x, y, r=30):
    ellipse(c, x, y, r, r)
    fill(c, hexc("#F4F1E0"))
    ellipse(c, x + 10, y - 6, r * 0.25, r * 0.25)
    fill(c, hexc("#DCD8C4"))


def stars(c, t, n=50, seed=4, ymax=380):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(0, ymax)
        c.set_source_rgba(1, 1, 0.9, 0.5 + 0.4 * math.sin(t * 2 + i))
        c.arc(x, y, r.uniform(1, 2.2), 0, 2 * math.pi)
        c.fill()


def clouds(c, t, n=4, y0=60, y1=200, col=(1, 1, 1, 0.9), seed=1, speed=8, scale=1.0):
    r = random.Random(seed)
    for i in range(n):
        x = (r.uniform(0, W + 300) + t * speed * r.uniform(0.6, 1.4)) % (W + 300) - 150
        y = r.uniform(y0, y1)
        s = r.uniform(0.7, 1.3) * scale
        for dx, dy, rr in ((0, 0, 30), (34, -14, 36), (70, 0, 28), (36, 8, 32), (-26, 6, 22)):
            ellipse(c, x + dx * s, y + dy * s, rr * s * 1.2, rr * s * 0.85)
            c.set_source_rgba(*col)
            c.fill()


def hills(c, y, cols=("#8FCB68", "#74B356"), seed=2, amp=30, layers=2):
    r = random.Random(seed)
    for L in range(layers):
        col = hexc(cols[min(L, len(cols) - 1)])
        yy = y - (layers - 1 - L) * 40
        ph = r.uniform(0, 6)
        c.move_to(0, H)
        for i in range(0, W + 41, 40):
            c.line_to(i, yy + amp * math.sin(i / 180 + ph) * (0.6 + 0.4 * math.sin(i / 70 + ph)))
        c.line_to(W, H)
        c.close_path()
        fill(c, shade(col, -0.05 * (layers - 1 - L)))


def tree(c, x, y, s=1.0, col="#4E9A4A", snow=False, dead=False, kind="pine"):
    seg(c, (x, y), (x, y - 30 * s), 8 * s, hexc("#6B4A32"))
    if dead:
        for k in range(3):
            seg(c, (x, y - 20 * s - k * 10 * s), (x + (-1) ** k * 18 * s, y - 34 * s - k * 12 * s), 4 * s, hexc("#5A4030"))
        return
    if kind == "pine":
        for k in range(3):
            w = (36 - k * 9) * s
            yy = y - 22 * s - k * 22 * s
            poly(c, [(x - w, yy), (x + w, yy), (x, yy - 38 * s)])
            fill(c, shade(hexc(col), -0.08 * k) if not snow else hexc("#E9F0F5"))
            if snow:
                poly(c, [(x - w * 0.6, yy - 6 * s), (x + w * 0.6, yy - 6 * s), (x, yy - 30 * s)])
                fill(c, hexc("#5E8A6A"))
    else:
        ellipse(c, x, y - 52 * s, 34 * s, 32 * s)
        fill(c, hexc(col))
        ellipse(c, x - 14 * s, y - 62 * s, 18 * s, 16 * s)
        fill(c, shade(hexc(col), 0.12))


def landscape(c, t, skyk="day", ground="grass", horizon=420, trees=True, hill=True, cloud=True,
              sunpos=None, seed=5, tree_col="#4E9A4A", snow=False, mountains=False, sunrays=False):
    sky(c, skyk, horizon + 60)
    if skyk == "night":
        stars(c, t)
    if sunpos:
        sun(c, *sunpos, t=t, rays=sunrays)
    if mountains:
        mount(c, horizon + 20, snow=True, seed=seed)
    if cloud and skyk not in ("night",):
        cc = (1, 1, 1, 0.85) if skyk in ("day", "desert", "winter", "dawn") else (0.85, 0.85, 0.9, 0.6)
        if skyk == "storm":
            cc = (0.45, 0.48, 0.55, 0.9)
        clouds(c, t, n=5, col=cc, seed=seed)
    g0, g1 = GROUNDS[ground]
    if hill:
        hills(c, horizon, cols=(g0, g1), seed=seed, amp=22)
    c.set_source(vgrad(c, horizon + 30, H, hexc(g0), hexc(g1)))
    c.rectangle(0, horizon + 30, W, H)
    c.fill()
    if trees:
        r = random.Random(seed)
        for i in range(9):
            x = r.uniform(0, W)
            tree(c, x, horizon + 18 + r.uniform(-8, 8), r.uniform(0.5, 0.8), col=tree_col, snow=snow,
                 kind=r.choice(["pine", "round"]))


def mount(c, y, snow=True, seed=1, col="#8A96A8"):
    r = random.Random(seed)
    x = -100
    while x < W + 100:
        w = r.uniform(160, 300)
        h = r.uniform(160, 300)
        poly(c, [(x, y), (x + w / 2, y - h), (x + w, y)])
        fill(c, shade(hexc(col), r.uniform(-0.1, 0.1)))
        if snow:
            poly(c, [(x + w / 2 - w * 0.16, y - h * 0.68), (x + w / 2, y - h), (x + w / 2 + w * 0.16, y - h * 0.68),
                     (x + w / 2 + 4, y - h * 0.74), (x + w / 2 - 6, y - h * 0.66)])
            fill(c, hexc("#F6F8FB"))
        x += w * 0.6


def sea(c, t, y=380, col0="#3E8FC4", col1="#1F5E8C", night=False):
    if night:
        col0, col1 = "#1E2E5A", "#0E1834"
    c.set_source(vgrad(c, y, H, hexc(col0), hexc(col1)))
    c.rectangle(0, y, W, H - y)
    c.fill()
    c.set_line_width(3)
    for k in range(14):
        yy = y + 12 + k * k * 2.2
        c.set_source_rgba(1, 1, 1, 0.18 + 0.02 * k)
        off = (t * (14 + k * 3) + k * 50) % 120
        for x in range(-120, W + 120, 120):
            c.move_to(x + off, yy)
            c.curve_to(x + off + 20, yy - 4, x + off + 40, yy - 4, x + off + 60, yy)
        c.stroke()


def rain(c, t, n=160, heavy=False, seed=9):
    r = random.Random(seed)
    c.set_line_width(2)
    c.set_source_rgba(0.85, 0.9, 1.0, 0.45 if heavy else 0.32)
    for i in range(n * (2 if heavy else 1)):
        x0 = r.uniform(0, W + 200)
        sp = r.uniform(600, 900)
        y = (r.uniform(0, H) + t * sp) % (H + 40) - 20
        x = (x0 - t * 120 - y * 0.25) % (W + 100)
        c.move_to(x, y)
        c.line_to(x - 6, y + 22)
    c.stroke()


def snowfall(c, t, n=150, heavy=False, seed=7):
    r = random.Random(seed)
    for i in range(n * (3 if heavy else 1)):
        x0 = r.uniform(0, W)
        sp = r.uniform(40, 110) * (2.4 if heavy else 1)
        y = (r.uniform(0, H) + t * sp) % (H + 20) - 10
        x = (x0 + math.sin(t + i) * 12 - (t * 220 if heavy else 0) * r.uniform(0.6, 1)) % W
        c.set_source_rgba(1, 1, 1, 0.85)
        c.arc(x, y, r.uniform(1.5, 4), 0, 2 * math.pi)
        c.fill()


def fog(c, amount=0.5, y0=250, y1=H, t=0.0):
    for k in range(5):
        y = lerp(y0, y1, k / 4)
        off = math.sin(t * 0.3 + k) * 60
        ellipse(c, W / 2 + off, y, W * 0.75, 70)
        c.set_source_rgba(1, 1, 1, amount * 0.35)
        c.fill()


def tint(c, col, a):
    c.set_source_rgba(*col[:3], a)
    c.paint()


def vignette(c, a=0.45):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, a)
    c.set_source(g)
    c.paint()


def smoke(c, x, y, t, n=6, s=1.0, col=(0.92, 0.92, 0.9), seed=1, rise=40, a=0.8):
    r = random.Random(seed)
    for i in range(n):
        ph = (t * 0.35 + i / n) % 1
        xx = x + r.uniform(-40, 40) * s + ph * r.uniform(-30, 30) * s
        yy = y - ph * rise * s
        rr = (24 + 40 * ph) * s * r.uniform(0.7, 1.2)
        ellipse(c, xx, yy, rr, rr * 0.8)
        c.set_source_rgba(*col, a * (1 - ph) * 0.8)
        c.fill()


def smoke_bank(c, y, t, a=0.6, seed=3, n=10, col=(0.93, 0.93, 0.9)):
    r = random.Random(seed)
    for i in range(n):
        x = (r.uniform(0, W) + t * r.uniform(5, 15)) % (W + 200) - 100
        rr = r.uniform(50, 110)
        ellipse(c, x, y + r.uniform(-30, 30), rr * 1.4, rr * 0.7)
        c.set_source_rgba(*col, a * r.uniform(0.5, 1))
        c.fill()


def flames(c, x, y, w, h, t, seed=1, a=1.0):
    r = random.Random(seed)
    for layer, col in enumerate(("#D9361E", "#F07A1E", "#FFC93C")):
        k = 1 - layer * 0.28
        n = max(3, int(w / 26))
        for i in range(n):
            fx = x - w / 2 + (i + 0.5) * w / n + r.uniform(-6, 6)
            fh = h * k * (0.7 + 0.3 * math.sin(t * 9 + i * 1.7 + layer)) * r.uniform(0.7, 1.1)
            fw = w / n * 0.9 * k
            c.move_to(fx - fw, y)
            c.curve_to(fx - fw, y - fh * 0.5, fx - fw * 0.2, y - fh * 0.7, fx + math.sin(t * 7 + i) * 6, y - fh)
            c.curve_to(fx + fw * 0.2, y - fh * 0.7, fx + fw, y - fh * 0.5, fx + fw, y)
            c.close_path()
            c.set_source_rgba(*hexc(col)[:3], a * 0.95)
            c.fill()


def explosion(c, x, y, u, s=1.0):
    if u <= 0 or u >= 1:
        return
    r = (40 + 260 * smooth(u)) * s
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 0.85, 1 - u)
    g.add_color_stop_rgba(0.4, 1, 0.7, 0.2, (1 - u) * 0.9)
    g.add_color_stop_rgba(1, 0.8, 0.2, 0.1, 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()


def muzzle(c, x, y, t, period=1.6, phase=0.0, s=1.0, face=1):
    ph = ((t + phase) % period) / period
    if ph < 0.12:
        k = 1 - ph / 0.12
        ellipse(c, x + face * 14 * s, y, 26 * s * k + 6, 16 * s * k + 4)
        fill(c, (1, 0.85, 0.3, 0.9 * k))
    smoke(c, x + face * 30 * s, y, t + phase, n=3, s=0.5 * s, seed=int(x), rise=50)


def cannon(c, x, y, s=1.0, face=1, t=0.0, fire=True, phase=0.0, period=2.2):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ph = ((t + phase) % period) / period
    rec = -10 * math.exp(-ph * 20) if fire else 0
    poly(c, [(-44 + rec, -8), (-40 + rec, -26), (20, -16), (20, -8)])
    fill(c, hexc("#7A5232"))
    c.save()
    c.translate(rec, 0)
    c.rotate(-0.12)
    rrect(c, -34, -42, 92, 22, 10)
    fill_ol(c, hexc("#3B3B40"), w=2)
    seg(c, (52, -38), (52, -24), 6, hexc("#2A2A2E"))
    c.restore()
    ellipse(c, -6 + rec, -16, 18, 18)
    fill_ol(c, hexc("#8A5E36"), w=3)
    ellipse(c, -6 + rec, -16, 4, 4)
    fill(c, INK)
    c.restore()
    if fire:
        if ph < 0.12:
            k = 1 - ph / 0.12
            ellipse(c, x + face * (66 * s), y - 44 * s, 30 * s * k + 6, 18 * s * k + 4)
            fill(c, (1, 0.85, 0.3, 0.95 * k))
        for i in range(4):
            q = ((t + phase) / period - i * 0.25) % 1
            q2 = ((t + phase) % period) / period + i * 0.6
            rr = (20 + 50 * q2) * s
            ellipse(c, x + face * (70 + 60 * q2) * s, y - (44 + 30 * q2) * s, rr, rr * 0.75)
            c.set_source_rgba(0.93, 0.93, 0.9, max(0, 0.75 - 0.45 * q2))
            c.fill()


def ship(c, x, y, s=1.0, face=1, t=0.0, flagk="uk", hull="#6B4A2E", stripe="#E2B53B", masts=3,
         burning=False, fire_side=False, sink=0.0, sails_col="#F4EFE2", phase=0.0):
    c.save()
    c.translate(x, y + 4 * math.sin(t * 1.5 + x * 0.01) + sink * 140)
    c.rotate(0.02 * math.sin(t * 1.2 + x * 0.02) + sink * 0.25 * face)
    c.scale(s * face, s)
    # masts + sails
    mx = [-80, 0, 80][:masts] if masts == 3 else [-40, 40][:masts]
    for i, m in enumerate(mx):
        hgt = 230 if i == 1 else 200
        seg(c, (m, -30), (m, -hgt - 20), 7, hexc("#5A3A22"))
        for k in range(3):
            yy = -60 - k * 62
            w = 54 - k * 10
            c.move_to(m - w, yy - 48)
            c.line_to(m + w, yy - 48)
            c.curve_to(m + w + 10, yy - 20, m + w + 6, yy, m + w, yy)
            c.line_to(m - w, yy)
            c.curve_to(m - w + 8, yy - 20, m - w + 4, yy - 40, m - w, yy - 48)
            fill_ol(c, hexc(sails_col), w=1.5)
    # flag at stern
    flag(c, -118, -60, t, kind=flagk, pole=90, w=46, h=30, face=-1)
    # hull
    c.move_to(-140, -50)
    c.line_to(150, -50)
    c.curve_to(150, -20, 130, 10, 100, 14)
    c.line_to(-112, 14)
    c.curve_to(-130, 0, -140, -30, -140, -50)
    fill_ol(c, hexc(hull), w=2.5)
    seg(c, (-136, -30), (146, -30), 10, hexc(stripe))
    for k in range(9):
        rrect(c, -108 + k * 27, -35, 12, 10, 2)
        fill(c, INK)
    seg(c, (150, -50), (196, -64), 5, hexc("#5A3A22"))
    c.restore()
    if burning:
        flames(c, x, y - 30 * s, 220 * s, 160 * s, t, seed=int(x))
        smoke(c, x, y - 200 * s, t, n=7, s=1.4 * s, col=(0.25, 0.22, 0.22), rise=120, seed=int(x) + 1)
    if fire_side:
        for k in range(5):
            muzzle(c, x + face * (-80 + k * 40) * s, y - 32 * s, t, period=1.3, phase=k * 0.27 + phase, s=s * 1.4,
                   face=1 if face > 0 else -1)


def boat(c, x, y, s=1.0, t=0.0, face=1):
    c.save()
    c.translate(x, y + 3 * math.sin(t * 2))
    c.scale(s * face, s)
    seg(c, (0, -20), (0, -150), 5, hexc("#5A3A22"))
    poly(c, [(4, -150), (70, -40), (4, -40)])
    fill_ol(c, hexc("#EDE5D3"), w=1.5)
    c.move_to(-70, -20)
    c.line_to(80, -20)
    c.curve_to(70, 0, 60, 8, 40, 8)
    c.line_to(-50, 8)
    c.curve_to(-64, 4, -70, -10, -70, -20)
    fill_ol(c, hexc("#7A5232"), w=2)
    c.restore()


# ------------------------------------------------------------------ buildings / props
def building_row(c, y, t, seed=1, h0=150, h1=260, night=False, cols=("#EDE2CF", "#E3D3BA", "#F2E8D8", "#D9C8AA")):
    r = random.Random(seed)
    x = -20
    while x < W + 20:
        w = r.uniform(110, 170)
        h = r.uniform(h0, h1)
        col = hexc(r.choice(cols))
        if night:
            col = shade(col, -0.55)
        rrect(c, x, y - h, w, h, 3)
        fill_ol(c, col, w=2)
        poly(c, [(x - 6, y - h), (x + w + 6, y - h), (x + w - 10, y - h - 34), (x + 10, y - h - 34)])
        fill(c, hexc("#6E7A8E") if not night else hexc("#2E3446"))
        for row in range(int((h - 30) / 46)):
            for col_i in range(int((w - 20) / 34)):
                wx = x + 16 + col_i * 34
                wy = y - h + 20 + row * 46
                rrect(c, wx, wy, 18, 28, 3)
                lit = night and r.random() < 0.4
                fill(c, hexc("#F7D774") if lit else hexc("#4A5A72" if not night else "#1A1E2C"))
        x += w + r.uniform(0, 10)


def bastille(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    stone = hexc("#9C958A")
    rrect(c, -230, -230, 460, 230, 4)
    fill_ol(c, stone, w=3)
    for tx in (-230, -80, 80, 230):
        rrect(c, tx - 48, -300, 96, 300, 10)
        fill_ol(c, shade(stone, -0.05), w=3)
        for k in range(5):
            rrect(c, tx - 44 + k * 19, -318, 12, 20, 2)
            fill(c, shade(stone, -0.05))
        rrect(c, tx - 8, -230, 16, 30, 6)
        fill(c, INK)
    rrect(c, -40, -110, 80, 110, 38)
    fill(c, hexc("#3A2E26"))
    c.restore()


def palace(c, x, y, s=1.0, col="#EFE6D4", night=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    cc = hexc(col) if not night else shade(hexc(col), -0.5)
    rrect(c, -330, -230, 660, 230, 2)
    fill_ol(c, cc, w=2)
    poly(c, [(-120, -230), (120, -230), (0, -310)])
    fill_ol(c, shade(cc, -0.05), w=2)
    for k in range(-5, 6):
        seg(c, (k * 56, -220), (k * 56, -10), 14, shade(cc, 0.3))
    for k in range(-5, 5):
        rrect(c, k * 56 + 14, -170, 28, 60, 12)
        fill(c, hexc("#F7D774") if night else hexc("#566A86"))
    rrect(c, -360, -14, 720, 14, 2)
    fill(c, shade(cc, -0.15))
    c.restore()


def cathedral_in(c, t):
    c.set_source(vgrad(c, 0, H, hexc("#5A4A6A"), hexc("#2E2438")))
    c.paint()
    for k in range(5):
        x = 140 + k * 250
        c.move_to(x - 70, H)
        c.line_to(x - 70, 260)
        c.curve_to(x - 70, 120, x, 60, x, 40)
        c.curve_to(x, 60, x + 70, 120, x + 70, 260)
        c.line_to(x + 70, H)
        c.set_line_width(26)
        c.set_source_rgba(*hexc("#8A7A6A"))
        c.stroke()
    for k, colr in enumerate(("#D24A4A", "#3A6AC0", "#E7B93A", "#4AA06A")):
        x = 265 + k * 250
        rrect(c, x - 34, 120, 68, 170, 34)
        fill(c, hexc(colr, 0.8))
        seg(c, (x, 120), (x, 290), 3, INK)
        seg(c, (x - 34, 200), (x + 34, 200), 3, INK)
    g = cairo.RadialGradient(W / 2, 200, 10, W / 2, 200, 600)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35)
    g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    c.set_source(g)
    c.paint()
    c.set_source(vgrad(c, 520, H, hexc("#8C7A62"), hexc("#5E4E3A")))
    c.rectangle(0, 520, W, H - 520)
    c.fill()
    for k in range(8):
        x = 80 + k * 160
        seg(c, (x, 520), (x, 470), 6, WHITE)
        ellipse(c, x, 462 + math.sin(t * 8 + k) * 1.5, 4, 8)
        fill(c, hexc("#FFC93C"))


def hall(c, t, wall="#E9DCC6", floor=("#B8936A", "#8C6A48"), chandelier=True, red=False, night=False):
    wl = hexc("#8C2A3A") if red else hexc(wall)
    if night:
        wl = shade(wl, -0.5)
    c.set_source(vgrad(c, 0, 470, shade(wl, 0.1), wl))
    c.rectangle(0, 0, W, 470)
    c.fill()
    for k in range(6):
        x = 60 + k * 232
        rrect(c, x, 40, 40, 430, 6)
        fill(c, shade(wl, 0.25))
        rrect(c, x - 8, 30, 56, 20, 4)
        fill(c, GOLD)
    for k in range(5):
        x = 140 + k * 232
        rrect(c, x, 110, 140, 230, 70)
        fill(c, hexc("#7AA6C8") if not night else hexc("#1A2244"))
        seg(c, (x + 70, 110), (x + 70, 340), 4, WHITE)
    c.set_source(vgrad(c, 470, H, hexc(floor[0]), hexc(floor[1])))
    c.rectangle(0, 470, W, H - 470)
    c.fill()
    for k in range(0, W, 80):
        seg(c, (k, 470), (k * 1.3 - 190, H), 2, (0, 0, 0, 0.12))
    if chandelier:
        for cx in (360, 920):
            seg(c, (cx, 0), (cx, 70), 3, GOLD)
            ellipse(c, cx, 80, 60, 16)
            fill(c, GOLD)
            for k in range(7):
                ellipse(c, cx - 54 + k * 18, 66, 4, 7)
                fill(c, hexc("#FFE08A"))


def interior(c, t, wall="#D9C7A8", floor=("#8C6A48", "#6E5236"), window=True, night=False, sky_k="day"):
    wl = hexc(wall) if not night else shade(hexc(wall), -0.45)
    c.set_source(vgrad(c, 0, 470, shade(wl, 0.08), wl))
    c.rectangle(0, 0, W, 470)
    c.fill()
    if window:
        rrect(c, 820, 90, 300, 260, 6)
        a, b = SKIES["night" if night else sky_k]
        c.set_source(vgrad(c, 90, 350, hexc(a), hexc(b)))
        c.fill()
        if night:
            moon(c, 1040, 160, 24)
        seg(c, (970, 90), (970, 350), 10, hexc("#F3EDE0"))
        seg(c, (820, 210), (1120, 210), 10, hexc("#F3EDE0"))
        rrect(c, 820, 90, 300, 260, 6)
        c.set_line_width(14)
        c.set_source_rgba(*hexc("#F3EDE0"))
        c.stroke()
    c.set_source(vgrad(c, 470, H, hexc(floor[0]), hexc(floor[1])))
    c.rectangle(0, 470, W, H - 470)
    c.fill()
    seg(c, (0, 470), (W, 470), 10, shade(wl, -0.25))


def tent_in(c, t):
    c.set_source(vgrad(c, 0, H, hexc("#E6CF9E"), hexc("#B99A64")))
    c.paint()
    for k in range(-3, 4):
        seg(c, (W / 2, -40), (W / 2 + k * 300, H), 3, (0.5, 0.35, 0.2, 0.3))
    c.set_source(vgrad(c, 520, H, hexc("#C9A86E"), hexc("#A88A52")))
    c.rectangle(0, 520, W, H - 520)
    c.fill()


def table(c, x, y, w=420, h=110, col="#7A5232", cloth=None):
    rrect(c, x - w / 2, y - h, w, 22, 4)
    fill_ol(c, hexc(cloth or col), w=2)
    for dx in (-w / 2 + 20, w / 2 - 34):
        rrect(c, x + dx, y - h + 20, 14, h - 20, 3)
        fill(c, shade(hexc(col), -0.2))


def candle(c, x, y, t, s=1.0):
    rrect(c, x - 6 * s, y - 40 * s, 12 * s, 40 * s, 3)
    fill(c, hexc("#F3EBD9"))
    g = cairo.RadialGradient(x, y - 50 * s, 2, x, y - 50 * s, 120 * s)
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.45)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    c.set_source(g)
    c.arc(x, y - 50 * s, 120 * s, 0, 2 * math.pi)
    c.fill()
    ellipse(c, x + math.sin(t * 9) * 1.5, y - 50 * s, 5 * s, 10 * s)
    fill(c, hexc("#FFC93C"))


def throne(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -70, -260, 140, 200, 30)
    fill_ol(c, GOLD, hexc("#9A7414"), 3)
    rrect(c, -54, -240, 108, 170, 24)
    fill(c, hexc("#9C2A3A"))
    for k in range(3):
        for j in range(2):
            ellipse(c, -24 + k * 24, -200 + j * 50, 5, 6)
            fill(c, GOLD)
    rrect(c, -80, -80, 160, 30, 8)
    fill_ol(c, GOLD, hexc("#9A7414"), 3)
    for dx in (-70, 56):
        rrect(c, dx, -60, 14, 60, 3)
        fill(c, hexc("#B88A1A"))
    c.restore()


def chair(c, x, y, s=1.0, col="#9C2A3A"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -50, -170, 100, 110, 22)
    fill_ol(c, hexc(col), w=3)
    rrect(c, -58, -70, 116, 28, 8)
    fill_ol(c, shade(hexc(col), -0.1), w=3)
    for dx in (-50, 38):
        rrect(c, dx, -44, 12, 44, 3)
        fill(c, BROWN)
    c.restore()


def book(c, x, y, s=1.0, glow=0.0, t=0.0):
    if glow:
        g = cairo.RadialGradient(x, y - 40 * s, 10, x, y - 40 * s, 260 * s)
        g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.6 * glow)
        g.add_color_stop_rgba(1, 1, 0.9, 0.5, 0)
        c.set_source(g)
        c.arc(x, y - 40 * s, 260 * s, 0, 2 * math.pi)
        c.fill()
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -90, -36, 180, 36, 6)
    fill(c, hexc("#F3EAD3"))
    rrect(c, -96, -44, 192, 16, 5)
    fill_ol(c, hexc("#7A2E2E"), w=2)
    rrect(c, -96, -8, 192, 12, 5)
    fill_ol(c, hexc("#7A2E2E"), w=2)
    for k in range(4):
        seg(c, (-80, -30 + k * 6), (80, -30 + k * 6), 1.2, (0.6, 0.5, 0.4, 0.6))
    ellipse(c, 0, -36, 14, 6)
    fill(c, GOLD)
    c.restore()


def globe(c, x, y, r, t):
    ellipse(c, x, y, r, r)
    fill_ol(c, hexc("#4A8AC8"), w=3)
    c.save()
    ellipse(c, x, y, r, r)
    c.clip()
    off = (t * 20) % (r * 4)
    for k in range(-2, 3):
        bx = x - r * 2 + off + k * r * 2
        ellipse(c, bx, y - r * 0.2, r * 0.5, r * 0.6)
        fill(c, hexc("#7FBF5A"))
        ellipse(c, bx + r * 0.9, y + r * 0.3, r * 0.3, r * 0.5)
        fill(c, hexc("#7FBF5A"))
    c.restore()
    seg(c, (x, y + r), (x, y + r + 30), 8, GOLD)
    ellipse(c, x, y + r + 34, 40, 8)
    fill(c, GOLD)


def pyramids(c, y, t):
    for (x, w, h) in ((260, 340, 240), (620, 280, 190), (900, 200, 130)):
        poly(c, [(x - w / 2, y), (x, y - h), (x + w / 2, y)])
        fill(c, hexc("#E2B86E"))
        poly(c, [(x, y - h), (x + w / 2, y), (x + w * 0.1, y)])
        fill(c, hexc("#C99A52"))


def village(c, y, t, x0=200, n=6, seed=2, night=False, windmill=True, church=True):
    r = random.Random(seed)
    for i in range(n):
        x = x0 + i * 120 + r.uniform(-20, 20)
        w, h = r.uniform(70, 100), r.uniform(50, 70)
        col = hexc(r.choice(["#F0E6D2", "#E8D6B8", "#F3EEE2"]))
        if night:
            col = shade(col, -0.5)
        rrect(c, x, y - h, w, h, 3)
        fill_ol(c, col, w=2)
        poly(c, [(x - 8, y - h), (x + w + 8, y - h), (x + w / 2, y - h - 40)])
        fill(c, hexc("#B5523A"))
        rrect(c, x + w / 2 - 8, y - 26, 16, 26, 2)
        fill(c, BROWN)
    if church:
        cx = x0 + n * 60
        rrect(c, cx - 30, y - 150, 60, 150, 2)
        fill_ol(c, hexc("#E9E2D2"), w=2)
        poly(c, [(cx - 36, y - 150), (cx + 36, y - 150), (cx, y - 240)])
        fill(c, hexc("#5A6A7E"))
        seg(c, (cx, y - 240), (cx, y - 266), 3, INK)
        seg(c, (cx - 8, y - 256), (cx + 8, y - 256), 3, INK)
    if windmill:
        wx = x0 + n * 120 + 60
        poly(c, [(wx - 30, y), (wx + 30, y), (wx + 18, y - 130), (wx - 18, y - 130)])
        fill_ol(c, hexc("#E6DCCB"), w=2)
        c.save()
        c.translate(wx, y - 120)
        c.rotate(t * 0.6)
        for k in range(4):
            c.rotate(math.pi / 2)
            rrect(c, -6, 0, 24, 90, 2)
            fill_ol(c, hexc("#F2EDE2"), w=1.5)
        c.restore()


def onion_city(c, y, t, night=False, burning=False):
    r = random.Random(11)
    for i in range(10):
        x = 40 + i * 130 + r.uniform(-20, 20)
        h = r.uniform(130, 260)
        w = r.uniform(50, 80)
        col = hexc(r.choice(["#F0E2C8", "#E9C9A0", "#D9E2EA", "#F2D6C6"]))
        if night:
            col = shade(col, -0.35)
        rrect(c, x - w / 2, y - h, w, h, 3)
        fill_ol(c, col, w=2)
        dc = hexc(r.choice(["#3E8E5A", "#2F6FB0", "#D9A23A", "#C0453A", "#7A4AA0"]))
        c.move_to(x - w / 2 - 6, y - h)
        c.curve_to(x - w / 2 - 20, y - h - 50, x - 4, y - h - 60, x, y - h - 96)
        c.curve_to(x + 4, y - h - 60, x + w / 2 + 20, y - h - 50, x + w / 2 + 6, y - h)
        c.close_path()
        fill_ol(c, dc, w=2)
        seg(c, (x, y - h - 96), (x, y - h - 120), 3, GOLD)
        if burning and i % 2 == 0:
            flames(c, x, y - h * 0.4, w * 1.6, h * 0.9, t, seed=i)


def brandenburg(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    stone = hexc("#E6DCC6")
    rrect(c, -260, -330, 520, 60, 4)
    fill_ol(c, stone, w=2)
    rrect(c, -230, -370, 460, 44, 4)
    fill_ol(c, stone, w=2)
    for k in range(6):
        rrect(c, -230 + k * 88, -270, 34, 270, 6)
        fill_ol(c, shade(stone, 0.2), w=2)
    # quadriga hint
    for k in range(4):
        ellipse(c, -40 + k * 26, -390, 14, 20)
        fill(c, hexc("#4E7E6A"))
    seg(c, (0, -420), (0, -380), 5, hexc("#4E7E6A"))
    c.restore()


def farmhouse(c, x, y, s=1.0, burning=False, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -300, -90, 600, 90, 2)
    fill_ol(c, hexc("#C9B79A"), w=3)
    rrect(c, -160, -220, 320, 140, 2)
    fill_ol(c, hexc("#E8DCC6"), w=3)
    poly(c, [(-176, -220), (176, -220), (120, -290), (-120, -290)])
    fill(c, hexc("#A84A32"))
    rrect(c, -40, -80, 80, 80, 36)
    fill(c, hexc("#4A3426"))
    for k in range(4):
        rrect(c, -130 + k * 75, -190, 30, 40, 3)
        fill(c, INK)
    c.restore()
    if burning:
        flames(c, x + 40 * s, y - 200 * s, 260 * s, 180 * s, t, seed=4)
        smoke(c, x + 40 * s, y - 360 * s, t, n=8, s=1.6 * s, col=(0.3, 0.28, 0.28), rise=160)


def campfire(c, x, y, t, s=1.0):
    for k in range(3):
        seg(c, (x - 30 * s, y - k * 3), (x + 30 * s, y - 10 * s + k * 3), 9 * s, BROWN)
    flames(c, x, y - 6 * s, 60 * s, 70 * s, t, seed=3)
    smoke(c, x, y - 90 * s, t, n=5, s=0.8 * s, col=(0.55, 0.55, 0.58), rise=120)


def tent(c, x, y, s=1.0, col="#EDE3CC"):
    poly(c, [(x - 70 * s, y), (x, y - 100 * s), (x + 70 * s, y)])
    fill_ol(c, hexc(col), w=2)
    poly(c, [(x - 16 * s, y), (x, y - 60 * s), (x + 16 * s, y)])
    fill(c, shade(hexc(col), -0.4))


def bridge(c, x0, x1, y, col="#8A6A48", stone=False, broken=None):
    rrect(c, x0, y - 18, x1 - x0, 18, 3)
    fill_ol(c, hexc("#9A948A" if stone else col), w=2)
    n = int((x1 - x0) / 60)
    for k in range(n + 1):
        px = x0 + k * (x1 - x0) / n
        if broken and broken[0] < px < broken[1]:
            continue
        seg(c, (px, y), (px, y + 70), 8 if not stone else 18, hexc("#6A4A32" if not stone else "#8A847A"))


def river(c, y0, y1, t, col0="#5FA6D4", col1="#3E7FB2", icy=False):
    if icy:
        col0, col1 = "#A8C8DC", "#7FA6C0"
    c.set_source(vgrad(c, y0, y1, hexc(col0), hexc(col1)))
    c.rectangle(0, y0, W, y1 - y0)
    c.fill()
    c.set_line_width(2.5)
    for k in range(6):
        yy = lerp(y0 + 8, y1 - 8, k / 5)
        off = (t * 30 + k * 40) % 100
        c.set_source_rgba(1, 1, 1, 0.3)
        for x in range(-100, W + 100, 100):
            c.move_to(x + off, yy)
            c.line_to(x + off + 40, yy)
        c.stroke()
    if icy:
        r = random.Random(5)
        for i in range(14):
            x = (r.uniform(0, W) + t * 12) % W
            ellipse(c, x, r.uniform(y0 + 10, y1 - 10), r.uniform(20, 50), r.uniform(6, 12))
            fill(c, (0.95, 0.97, 1, 0.85))


def crosses(c, y, t, n=7, rows=4):
    for row in range(rows):
        k = 1 - row * 0.15
        for i in range(n + row):
            x = 100 + (i + 0.5 * (row % 2)) * (1080 / (n + row))
            yy = y - row * 40
            seg(c, (x, yy), (x, yy - 60 * k), 8 * k, hexc("#EDE6D6"))
            seg(c, (x - 18 * k, yy - 42 * k), (x + 18 * k, yy - 42 * k), 8 * k, hexc("#EDE6D6"))


def scale_balance(c, x, y, t, tilt=0.0, flags_l=("uk", "au"), flags_r=("pr", "ru")):
    seg(c, (x, y), (x, y - 260), 12, GOLD)
    ellipse(c, x, y, 80, 14)
    fill(c, GOLD)
    a = tilt + 0.04 * math.sin(t)
    c.save()
    c.translate(x, y - 260)
    c.rotate(a)
    seg(c, (-220, 0), (220, 0), 10, GOLD)
    c.restore()
    for sx, fl in ((-1, flags_l), (1, flags_r)):
        px = x + sx * 220 * math.cos(a)
        py = y - 260 + sx * 220 * math.sin(a)
        seg(c, (px, py), (px - 50, py + 110), 2, GOLD)
        seg(c, (px, py), (px + 50, py + 110), 2, GOLD)
        ellipse(c, px, py + 116, 70, 14)
        fill(c, GOLD)
        for j, fk in enumerate(fl):
            flag(c, px - 30 + j * 40, py + 108, t + j, kind=fk, pole=60, w=34, h=22)


def statue_broken(c, x, y, t):
    poly(c, [(x - 90, y), (x + 90, y), (x + 70, y - 60), (x - 70, y - 60)])
    fill_ol(c, hexc("#9A948A"), w=2)
    c.save()
    c.translate(x - 40, y - 60)
    c.rotate(-1.2)
    napoleon(c, 0, 0, 0.9, coat="#8A6A3A", trou="#8A6A3A", waist="#8A6A3A", skin=hexc("#9A7A44"),
             hair_col="#7A5A2A", expr="sad", t=0, blink=False)
    c.restore()
    poly(c, [(x + 30, y - 80), (x + 46, y - 120), (x + 60, y - 70)])
    fill(c, hexc("#8A6A3A"))


def rosetta(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    poly(c, [(-60, 0), (-66, -150), (-30, -180), (40, -176), (64, -120), (60, 0)])
    fill_ol(c, hexc("#2E2E36"), w=3)
    for k in range(10):
        y0 = -160 + k * 15
        for j in range(8):
            seg(c, (-50 + j * 13, y0), (-44 + j * 13, y0), 2, hexc("#8A8A96"))
    c.restore()


def sleigh(c, x, y, s, t, who=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(-120, -10)
    c.line_to(120, -10)
    c.curve_to(150, -10, 160, -40, 140, -50)
    c.set_line_width(6)
    c.set_source_rgba(*GOLD)
    c.stroke()
    rrect(c, -110, -80, 200, 64, 20)
    fill_ol(c, hexc("#8C2A3A"), w=3)
    c.restore()
    if who:
        napoleon(c, x - 10 * s, y - 40 * s, 0.8 * s, coat="#5A4232", t=t, expr="worried", seated=True)
    for k in range(2):
        horse(c, x + (230 + k * 110) * s, y, 0.75 * s, 1, "#3A2A22" if k else "#5A3A2A", t + k, gallop=True)


def raft(c, x, y, t, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -280, -20, 560, 30, 4)
    fill_ol(c, hexc("#A07A4E"), w=2)
    rrect(c, -150, -170, 300, 150, 6)
    fill_ol(c, hexc("#F1E6D2"), w=3)
    poly(c, [(-170, -170), (170, -170), (0, -240)])
    fill_ol(c, hexc("#C8322F"), w=3)
    rrect(c, -40, -120, 80, 100, 36)
    fill(c, hexc("#7A2E2E"))
    c.restore()


def arrow(c, pts, prog, col="#2B4C9B", w=16, head=34):
    """Polyline arrow drawn up to prog (0..1)."""
    if prog <= 0:
        return
    # resample as quadratic smooth
    path = []
    for i in range(len(pts) - 1):
        for k in range(20):
            u = k / 20
            path.append((lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u)))
    path.append(pts[-1])
    # smooth
    sm = path[:]
    for _ in range(6):
        sm = [sm[0]] + [((a[0] + 2 * b[0] + d[0]) / 4, (a[1] + 2 * b[1] + d[1]) / 4)
                        for a, b, d in zip(sm, sm[1:], sm[2:])] + [sm[-1]]
    n = max(2, int(len(sm) * clamp(prog)))
    p = sm[:n]
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_width(w + 6)
    c.move_to(*p[0])
    for q in p[1:]:
        c.line_to(*q)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.stroke()
    c.set_line_width(w)
    c.move_to(*p[0])
    for q in p[1:]:
        c.line_to(*q)
    c.set_source_rgba(*hexc(col))
    c.stroke()
    (x0, y0), (x1, y1) = p[-2], p[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    poly(c, [(x1 + math.cos(a) * head, y1 + math.sin(a) * head),
             (x1 + math.cos(a + 2.4) * head * 0.8, y1 + math.sin(a + 2.4) * head * 0.8),
             (x1 + math.cos(a - 2.4) * head * 0.8, y1 + math.sin(a - 2.4) * head * 0.8)])
    fill_ol(c, hexc(col), (0, 0, 0, 0.4), 3)


# ------------------------------------------------------------------ map of Europe
LAND = {
    "britain": [(355, 170), (385, 140), (405, 190), (398, 240), (425, 282), (400, 304), (350, 308), (372, 270), (348, 238), (366, 205)],
    "ireland": [(298, 215), (332, 202), (338, 246), (305, 258)],
    "france": [(392, 330), (442, 308), (500, 318), (532, 350), (522, 410), (544, 452), (500, 482), (452, 482), (402, 472), (412, 430), (372, 382)],
    "lowlands": [(468, 278), (522, 268), (532, 312), (500, 318), (462, 306)],
    "iberia": [(258, 470), (330, 462), (402, 478), (452, 488), (432, 532), (402, 592), (330, 612), (282, 602), (250, 562), (255, 500)],
    "italy": [(532, 442), (572, 430), (612, 452), (602, 482), (642, 542), (692, 582), (672, 604), (642, 572), (602, 522), (562, 482)],
    "germany": [(522, 300), (622, 282), (642, 370), (560, 372), (530, 352)],
    "prussia": [(622, 262), (782, 250), (792, 322), (702, 334), (642, 332)],
    "austria": [(602, 372), (722, 352), (822, 382), (802, 432), (702, 442), (622, 422)],
    "poland": [(792, 250), (882, 250), (892, 332), (802, 342)],
    "russia": [(882, 118), (1262, 78), (1272, 522), (1002, 522), (902, 452), (892, 332), (882, 250), (822, 200)],
    "scandinavia": [(602, 62), (722, 42), (822, 152), (762, 232), (682, 182), (642, 242), (602, 182)],
    "balkans": [(722, 442), (852, 422), (902, 482), (862, 542), (782, 562), (742, 502)],
    "africa": [(230, 660), (520, 650), (800, 662), (1280, 640), (1280, 720), (230, 720)],
}
LABELS = {"britain": "BRITAIN", "france": "FRANCE", "iberia": "SPAIN", "italy": "ITALY", "prussia": "PRUSSIA",
          "austria": "AUSTRIA", "russia": "RUSSIA", "poland": "POLAND", "germany": "GERMAN\nSTATES",
          "africa": "EGYPT  ·  NORTH AFRICA"}
LAND_COL = "#EAD9B0"


def europe(c, t, colors=None, labels=True, glow=None):
    c.set_source(vgrad(c, 0, H, hexc("#A9CFD8"), hexc("#8DBAC6")))
    c.paint()
    c.set_line_width(1)
    c.set_source_rgba(1, 1, 1, 0.15)
    for k in range(0, W, 80):
        c.move_to(k, 0)
        c.line_to(k, H)
    for k in range(0, H, 80):
        c.move_to(0, k)
        c.line_to(W, k)
    c.stroke()
    colors = colors or {}
    for name, pts in LAND.items():
        col = hexc(colors.get(name, LAND_COL))
        poly(c, pts)
        c.set_source_rgba(0, 0, 0, 0.15)
        c.save()
        c.translate(4, 6)
        poly(c, pts)
        c.fill()
        c.restore()
        poly(c, pts)
        fill_ol(c, col, hexc("#7A6A4A"), 2.5)
    if glow:
        name, col, a = glow
        poly(c, LAND[name])
        c.set_source_rgba(*hexc(col)[:3], a)
        c.fill()
    if labels:
        c.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(17)
        for name, lab in LABELS.items():
            pts = LAND[name]
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            if name == "africa":
                cx, cy = 900, 690
            for li, line in enumerate(lab.split("\n")):
                e = c.text_extents(line)
                c.move_to(cx - e.x_advance / 2, cy + li * 20)
                c.set_source_rgba(0.25, 0.2, 0.15, 0.75)
                c.show_text(line)
    # parchment edge
    c.set_line_width(24)
    c.rectangle(0, 0, W, H)
    c.set_source_rgba(0.45, 0.35, 0.2, 0.35)
    c.stroke()


def centroid(name):
    pts = LAND[name]
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def map_piece(c, x, y, s, col="#2B4C9B", t=0.0):
    """small toy soldier marker on map."""
    soldier(c, x, y, s, uni={"#2B4C9B": "fr", "#C8322F": "br"}.get(col, "fr"), t=t)
