"""Stick-figure history-cartoon toolkit (pycairo): characters with thin limbs, simple scenes,
typewriter handwriting text, year tags and a textured 'satellite' map."""
import math
import os
import random
import shutil

import cairo
import numpy as np

W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))
HAND = "Patrick Hand"


def ensure_fonts():
    dst = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(dst, exist_ok=True)
    src = os.path.join(HERE, "fonts")
    changed = False
    for f in os.listdir(src):
        if not os.path.exists(os.path.join(dst, f)):
            shutil.copy(os.path.join(src, f), dst)
            changed = True
    if changed:
        os.system("fc-cache -f >/dev/null 2>&1")


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


OUT = hexc("#2B2420")
SKIN = hexc("#F5D3B3")


def ellipse(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(max(rx, 0.01), max(ry, 0.01))
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def fill_ol(c, col, w=2.2, ol=OUT):
    c.set_source_rgba(*col)
    c.fill_preserve()
    c.set_source_rgba(*ol)
    c.set_line_width(w)
    c.stroke()


def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def line(c, a, b, w, col=OUT):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(w)
    c.move_to(*a)
    c.line_to(*b)
    c.set_source_rgba(*col)
    c.stroke()


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


# ---------------------------------------------------------------- characters
CHARS = {
    "nicholas": dict(top="tunic", col="#3E5A3A", legs="#2A2A2A", hair="#6B4A2E", beard="#6B4A2E",
                     hat="peaked", hatcol="#3E5A3A", epaulettes=True, sash="#7FB0D8"),
    "alexandra": dict(top="dress", col="#C9B6DA", hair="#9A4A2A", bun=True, pearls=True),
    "alexei": dict(top="tunic", col="#F4F4F0", legs="#F4F4F0", hair="#8A6A4A", sailor=True, kid=True),
    "daughter": dict(top="dress", col="#F7F5EF", hair="#7A5A3A", bow=True),
    "doctor": dict(top="tunic", col="#3A3A44", legs="#3A3A44", hair="#AAAAAA", beard="#AAAAAA", glasses=True),
    "maid": dict(top="dress", col="#7A7A86", hair="#5A3A2A", apron=True, bun=True),
    "guard": dict(top="tunic", col="#26221F", legs="#26221F", hair="#3A2A1E", hat="peaked", hatcol="#26221F",
                  moustache="#3A2A1E"),
    "peasant": dict(top="tunic", col="#D9CBA8", legs="#6A5A44", hair="#7A5A3A", beard="#7A5A3A", belt="#7A3A2A"),
    "host": dict(top="tunic", col="#3E6E9C", legs="#3A3A44", hair="#4A3222", hat="flatcap", hatcol="#7A5232",
                 glasses=True, scarf="#C8322F"),
}


def stick(c, x, y, s, who, t=0.0, face=1, walk=None, arm_f=15, arm_b=-10, talk=False, look=0.0, mood="neutral",
          extra=None, eyes_closed=False):
    spec = dict(CHARS[who])
    if extra:
        spec.update(extra)
    skin = hexc(spec["skin"]) if spec.get("skin") else SKIN
    kid = spec.get("kid", False)
    c.save()
    c.translate(x, y)
    k = s * (0.7 if kid else 1.0)
    c.scale(k * face, k)
    bob = 0
    sw = 0
    if walk is not None:
        sw = math.sin(walk) * 22
        bob = -abs(math.cos(walk)) * 3
    # ground shadow
    ellipse(c, 0, 2, 26, 5)
    c.set_source_rgba(0, 0, 0, 0.13)
    c.fill()
    c.translate(0, bob)
    hip = -70
    legcol = hexc(spec.get("legs", "#2A2A2A"))

    def leg(dx, ang):
        a = math.radians(ang)
        fx = dx + math.sin(a) * 70
        fy = hip + math.cos(a) * 70
        line(c, (dx, hip), (fx, fy), 5.5, legcol)
        ellipse(c, fx + 5, fy, 8, 4)
        c.set_source_rgba(*OUT)
        c.fill()

    def arm(ang, front):
        a = math.radians(ang)
        sx, sy = (10 if front else -6), -128
        hx = sx + math.sin(a) * 56
        hy = sy + math.cos(a) * 56
        line(c, (sx, sy), (hx, hy), 5, OUT)
        ellipse(c, hx, hy, 5, 5)
        c.set_source_rgba(*skin)
        c.fill_preserve()
        c.set_source_rgba(*OUT)
        c.set_line_width(1.6)
        c.stroke()
        return hx, hy

    arm(arm_b - (sw * 0.6 if walk is not None else 0), False)
    dress = spec["top"] == "dress"
    if not dress:
        leg(-5, -sw)
    # body
    col = hexc(spec["col"])
    if dress:
        poly(c, [(-15, -140), (15, -140), (34, -6), (-34, -6)])
        fill_ol(c, col)
        if spec.get("apron"):
            poly(c, [(-11, -110), (11, -110), (18, -20), (-18, -20)])
            fill_ol(c, hexc("#F4F2EC"), 1.6)
        for dx in (-9, 9):
            line(c, (dx, -6), (dx + sw * 0.15, 0), 4.5, OUT)
    else:
        poly(c, [(-16, -142), (16, -142), (19, -66), (-19, -66)])
        fill_ol(c, col)
        if spec.get("belt"):
            line(c, (-19, -74), (19, -74), 4, hexc(spec["belt"]))
        if spec.get("sailor"):
            poly(c, [(-16, -142), (16, -142), (0, -118)])
            fill_ol(c, hexc("#2B4C9B"), 1.4)
        if spec.get("sash"):
            line(c, (-14, -138), (16, -78), 6, hexc(spec["sash"]))
        if spec.get("epaulettes"):
            for dx in (-16, 16):
                ellipse(c, dx, -141, 8, 3.5)
                c.set_source_rgba(*hexc("#E2B53B"))
                c.fill()
        if spec.get("scarf"):
            poly(c, [(-14, -144), (14, -144), (10, -132), (-10, -132)])
            fill_ol(c, hexc(spec["scarf"]), 1.4)
            line(c, (8, -134), (12, -112), 6, hexc(spec["scarf"]))
        leg(5, sw)
    if spec.get("pearls"):
        for i in range(7):
            ellipse(c, -9 + i * 3, -136 + abs(i - 3) * -0.8, 1.8, 1.8)
            c.set_source_rgba(1, 1, 1, 1)
            c.fill()
    hand = arm(arm_f + (sw * 0.6 if walk is not None else 0), True)
    # head
    hy = -170
    line(c, (0, -142), (0, -150), 5, skin)
    hair = hexc(spec.get("hair", "#3A2A1E"))
    if spec.get("bun"):
        ellipse(c, -14, hy - 22, 11, 10)
        fill_ol(c, hair, 1.6)
    ellipse(c, 0, hy, 24, 25)
    fill_ol(c, skin, 2)
    c.save()
    ellipse(c, 0, hy, 24, 25)
    c.clip()
    ellipse(c, -4, hy - 24, 30, 14)
    c.set_source_rgba(*hair)
    c.fill()
    c.restore()
    if spec.get("bow"):
        for dx in (-9, 9):
            ellipse(c, -16 + dx * 0.6, hy - 22, 7, 5)
            fill_ol(c, hexc("#FFFFFF"), 1.4)
    if spec.get("beard"):
        c.move_to(-16, hy + 4)
        c.curve_to(-14, hy + 34, 20, hy + 34, 22, hy + 4)
        c.line_to(16, hy + 12)
        c.curve_to(8, hy + 18, -2, hy + 18, -10, hy + 10)
        c.close_path()
        c.set_source_rgba(*hexc(spec["beard"]))
        c.fill()
    ex = 6 + look * 3
    for dx in (ex - 7, ex + 7):
        if eyes_closed:
            line(c, (dx - 3, hy - 3), (dx + 3, hy - 3), 2, OUT)
        else:
            ellipse(c, dx, hy - 3, 2.6, 3.2)
            c.set_source_rgba(*OUT)
            c.fill()
    if spec.get("glasses"):
        for dx in (ex - 7, ex + 7):
            ellipse(c, dx, hy - 3, 6, 5.5)
            c.set_line_width(1.5)
            c.set_source_rgba(*OUT)
            c.stroke()
    if spec.get("moustache"):
        line(c, (ex - 6, hy + 8), (ex + 7, hy + 8), 3.5, hexc(spec["moustache"]))
    mopen = talk and (t * 9) % 1 < 0.5
    if mopen:
        ellipse(c, ex + 1, hy + 12, 3.5, 3.5)
        c.set_source_rgba(*hexc("#7A2E2E"))
        c.fill()
    elif not spec.get("beard"):
        if mood == "worried":
            c.arc(ex + 1, hy + 16, 4, 1.2 * math.pi, 1.8 * math.pi)
        elif mood == "happy":
            c.arc(ex + 1, hy + 8, 5, 0.2 * math.pi, 0.8 * math.pi)
        else:
            c.move_to(ex - 3, hy + 11)
            c.line_to(ex + 5, hy + 11)
        c.set_line_width(2)
        c.set_source_rgba(*OUT)
        c.stroke()
    hat = spec.get("hat")
    if hat == "peaked":
        hc = hexc(spec.get("hatcol", "#26221F"))
        ellipse(c, 0, hy - 22, 25, 7)
        fill_ol(c, hc, 1.6)
        rrect(c, -17, hy - 30, 34, 10, 3)
        fill_ol(c, hc, 1.6)
        line(c, (4, hy - 17), (26, hy - 16), 4, OUT)
    elif hat == "flatcap":
        hc = hexc(spec.get("hatcol", "#7A5232"))
        c.move_to(-24, hy - 12)
        c.curve_to(-24, hy - 34, 14, hy - 34, 22, hy - 18)
        c.line_to(32, hy - 14)
        c.line_to(20, hy - 10)
        c.close_path()
        fill_ol(c, hc, 1.6)
    elif hat == "crown":
        poly(c, [(-16, hy - 20), (-18, hy - 40), (-8, hy - 30), (0, hy - 44), (8, hy - 30), (18, hy - 40),
                 (16, hy - 20)])
        fill_ol(c, hexc("#E9B93A"), 1.6)
    c.restore()
    # return hand position in world coords (for props)
    hxw = x + face * hand[0] * k
    hyw = y + (hand[1] + bob) * k
    return hxw, hyw


def lantern(c, x, y, t, glow=True):
    if glow:
        g = cairo.RadialGradient(x, y, 5, x, y, 260)
        g.add_color_stop_rgba(0, 1, 0.82, 0.45, 0.45 + 0.05 * math.sin(t * 12))
        g.add_color_stop_rgba(1, 1, 0.82, 0.45, 0)
        c.set_source(g)
        c.arc(x, y, 260, 0, 2 * math.pi)
        c.fill()
    line(c, (x, y - 6), (x, y - 16), 2, OUT)
    rrect(c, x - 9, y - 6, 18, 24, 4)
    fill_ol(c, hexc("#FFD27A"), 1.8)


# ---------------------------------------------------------------- backgrounds
def sky_bg(c, t, night=False, ground="#7FB55A", horizon=470):
    g = cairo.LinearGradient(0, 0, 0, horizon)
    if night:
        g.add_color_stop_rgba(0, *hexc("#0E1530"))
        g.add_color_stop_rgba(1, *hexc("#2A3560"))
    else:
        g.add_color_stop_rgba(0, *hexc("#8EC6EA"))
        g.add_color_stop_rgba(1, *hexc("#DDEFF8"))
    c.set_source(g)
    c.rectangle(0, 0, W, horizon)
    c.fill()
    if night:
        r = random.Random(3)
        for i in range(70):
            c.set_source_rgba(1, 1, 0.9, 0.4 + 0.5 * abs(math.sin(t + i)))
            c.arc(r.uniform(0, W), r.uniform(0, horizon - 60), r.uniform(0.8, 2), 0, 2 * math.pi)
            c.fill()
        ellipse(c, 1080, 110, 34, 34)
        c.set_source_rgba(*hexc("#F4F1E0"))
        c.fill()
    else:
        clouds(c, t)
    # hills
    for k, (yy, col) in enumerate(((horizon - 40, "#8FB88A"), (horizon - 10, "#7AA874"))):
        cc = hexc(col) if not night else tuple(v * 0.35 for v in hexc(col)[:3]) + (1,)
        c.move_to(0, H)
        for x in range(0, W + 41, 40):
            c.line_to(x, yy + 18 * math.sin(x / 170 + k * 2))
        c.line_to(W, H)
        c.close_path()
        c.set_source_rgba(*cc)
        c.fill()
    gc = hexc(ground) if not night else tuple(v * 0.35 for v in hexc(ground)[:3]) + (1,)
    c.rectangle(0, horizon + 20, W, H)
    c.set_source_rgba(*gc)
    c.fill()


def clouds(c, t, n=4, seed=2):
    r = random.Random(seed)
    for i in range(n):
        x = (r.uniform(0, W + 300) + t * 10) % (W + 300) - 150
        y = r.uniform(50, 180)
        s = r.uniform(0.7, 1.2)
        for dx, dy, rr in ((0, 0, 26), (30, -12, 30), (62, 0, 24), (32, 6, 26)):
            ellipse(c, x + dx * s, y + dy * s, rr * s * 1.15, rr * s * 0.8)
            c.set_source_rgba(1, 1, 1, 0.97)
            c.fill()


def room_bg(c, t, wall="#D9C9A6", stripe="#CDBB95", floor="#8A6A48", night=False, dim=0.0):
    c.set_source_rgba(*hexc(wall))
    c.rectangle(0, 0, W, 560)
    c.fill()
    for x in range(0, W, 60):
        c.rectangle(x, 0, 28, 560)
        c.set_source_rgba(*hexc(stripe))
        c.fill()
    line(c, (0, 560), (W, 560), 10, hexc("#6A4A30"))
    c.rectangle(0, 565, W, H)
    c.set_source_rgba(*hexc(floor))
    c.fill()
    for x in range(-200, W, 90):
        line(c, (x, 565), (x + 120, H), 2, (0, 0, 0, 0.15))
    if night or dim:
        c.set_source_rgba(0.02, 0.03, 0.1, 0.55 if night else dim)
        c.paint()


def grey_bg(c):
    c.set_source_rgba(*hexc("#D6D3D0"))
    c.paint()


# ---------------------------------------------------------------- satellite-style map
_MAP = {}


def _noise(h, w, seed, octaves=5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, tot = 1.0, 0
    for o in range(octaves):
        sh = max(2, h // (2 ** (octaves - o + 1)))
        sw = max(2, w // (2 ** (octaves - o + 1)))
        small = rng.random((sh, sw))
        from PIL import Image
        big = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)) / 255.0
        out += big * amp
        tot += amp
        amp *= 0.55
    return out / tot


LAND = [
    # simplified northern Eurasia (Europe on the left, Siberia to the right), 1280x720 frame
    [(0, 300), (60, 250), (140, 270), (170, 330), (230, 300), (250, 240), (300, 200), (260, 150), (300, 70),
     (380, 40), (430, 110), (400, 190), (440, 230), (480, 170), (540, 130), (640, 120), (700, 90), (800, 110),
     (900, 70), (1000, 90), (1120, 60), (1280, 80), (1280, 720), (900, 720), (860, 620), (800, 640), (760, 560),
     (700, 540), (620, 580), (560, 560), (500, 600), (430, 560), (380, 600), (300, 560), (260, 610), (200, 560),
     (120, 600), (60, 560), (0, 560)],
]
SEAS = [  # cut back out of the land
    ("black", (500, 610), (110, 48)),
    ("caspian", (770, 590), (38, 90)),
    ("baltic", (330, 260), (40, 70)),
]
PLACES = {"petrograd": (420, 250), "moscow": (520, 330), "yekaterinburg": (790, 300)}
EMPIRE = [(300, 200), (380, 40), (1280, 40), (1280, 720), (900, 720), (860, 620), (560, 560), (430, 560), (300, 470),
          (330, 330)]


def map_surface():
    if "s" in _MAP:
        return _MAP["s"]
    h, w = H, W
    n = _noise(h, w, 4)
    n2 = _noise(h, w, 9, 6)
    ocean = np.zeros((h, w, 3))
    ocean[..., 0] = 0.05 + 0.08 * n
    ocean[..., 1] = 0.20 + 0.12 * n
    ocean[..., 2] = 0.45 + 0.25 * n
    land = np.zeros((h, w, 3))
    yy = np.linspace(0, 1, h)[:, None]
    green = np.stack([0.30 + 0.15 * n2, 0.45 + 0.15 * n2, 0.20 + 0.08 * n2], -1)
    brown = np.stack([0.55 + 0.15 * n2, 0.45 + 0.12 * n2, 0.28 + 0.08 * n2], -1)
    tundra = np.stack([0.72 + 0.1 * n2, 0.74 + 0.1 * n2, 0.66 + 0.1 * n2], -1)
    mix = np.clip((n2 - 0.45) * 3, 0, 1)[..., None]
    land = green * (1 - mix) + brown * mix
    tmix = np.clip((0.3 - yy) * 4, 0, 1)[..., None]
    land = land * (1 - tmix) + tundra * tmix
    # Ural ridge
    xs = np.arange(w)[None, :]
    ridge = np.exp(-((xs - (700 + 30 * np.sin(np.arange(h)[:, None] / 60))) ** 2) / 400.0)
    land = land * (1 - 0.35 * ridge[..., None]) + np.array([0.45, 0.35, 0.25]) * 0.35 * ridge[..., None]
    # mask via cairo
    ms = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
    mc = cairo.Context(ms)
    for p in LAND:
        poly(mc, p)
        mc.fill()
    mc.set_operator(cairo.OPERATOR_CLEAR)
    for _, (x, y), (rx, ry) in SEAS:
        ellipse(mc, x, y, rx, ry)
        mc.fill()
    ms.flush()
    stride = ms.get_stride()
    m = np.frombuffer(ms.get_data(), np.uint8).reshape(h, stride)[:, :w] / 255.0
    from PIL import Image, ImageFilter
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255.0
    img = ocean * (1 - m[..., None]) + land * m[..., None]
    # coastline darkening
    edge = np.clip(np.abs(np.gradient(m)[0]) + np.abs(np.gradient(m)[1]), 0, 1)
    img = img * (1 - 0.6 * edge[..., None])
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    buf = np.zeros((h, w, 4), np.uint8)
    buf[..., 0], buf[..., 1], buf[..., 2], buf[..., 3] = img[..., 2], img[..., 1], img[..., 0], 255
    s = cairo.ImageSurface.create_for_data(memoryview(buf).cast("B"), cairo.FORMAT_ARGB32, w, h, w * 4)
    _MAP["s"] = (s, buf)
    return _MAP["s"]


def map_bg(c):
    s, _ = map_surface()
    c.set_source_surface(s, 0, 0)
    c.paint()


def pin(c, x, y, t, col="#E8443A", appear=1.0):
    if appear <= 0:
        return
    k = smooth(appear)
    for i in range(2):
        ph = (t * 0.9 + i / 2) % 1
        ellipse(c, x, y, 8 + 30 * ph, (8 + 30 * ph) * 0.45)
        c.set_source_rgba(*hexc(col)[:3], (1 - ph) * 0.7 * k)
        c.set_line_width(2)
        c.stroke()
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.move_to(0, 0)
    c.curve_to(-14, -18, -12, -34, 0, -34)
    c.curve_to(12, -34, 14, -18, 0, 0)
    fill_ol(c, hexc(col), 2, hexc("#FFFFFF"))
    ellipse(c, 0, -23, 4.5, 4.5)
    c.set_source_rgba(1, 1, 1, 1)
    c.fill()
    c.restore()


# ---------------------------------------------------------------- text
def hand_text(c, txt, x, y, size, t_since, cps=16, col=(1, 1, 1, 1), shadow=True, align="center", font=HAND,
              outline=False):
    n = int(clamp(t_since * cps / max(1, len(txt))) * len(txt)) if t_since >= 0 else 0
    if n <= 0:
        return
    sub = txt[:n]
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    full = c.text_extents(txt)
    x0 = x - full.x_advance / 2 if align == "center" else x
    if shadow:
        c.move_to(x0 + 2, y + 2)
        c.set_source_rgba(0, 0, 0, 0.35)
        c.show_text(sub)
    if outline:
        c.move_to(x0, y)
        c.text_path(sub)
        c.set_line_width(size / 7)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_source_rgba(0.1, 0.06, 0.05, 0.9)
        c.stroke()
    c.move_to(x0, y)
    c.set_source_rgba(*col)
    c.show_text(sub)


def year_tag(c, txt, a=1.0):
    c.select_font_face(HAND, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(24)
    e = c.text_extents(txt)
    rrect(c, 22, 20, e.x_advance + 24, 36, 7)
    c.set_source_rgba(0.25, 0.25, 0.28, 0.75 * a)
    c.fill()
    c.move_to(34, 46)
    c.set_source_rgba(1, 1, 1, a)
    c.show_text(txt)


def hand_arrow(c, x0, y0, x1, y1, prog, col=(1, 1, 1, 1)):
    if prog <= 0:
        return
    x = lerp(x0, x1, clamp(prog))
    y = lerp(y0, y1, clamp(prog))
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(3)
    c.set_source_rgba(*col)
    c.move_to(x0, y0)
    c.curve_to(lerp(x0, x, 0.3), lerp(y0, y, 0.1) - 10, lerp(x0, x, 0.7), lerp(y0, y, 0.9) - 6, x, y)
    c.stroke()
    if prog >= 1:
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            c.move_to(x1, y1)
            c.line_to(x1 + 14 * math.cos(a + da), y1 + 14 * math.sin(a + da))
        c.stroke()
