"""Core drawing helpers, palettes, backgrounds, HUD and headline typography."""
import math, random, functools, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FD = "fonts/"
CINZEL9 = FD + "cinzel-latin-900-normal.woff"
CINZEL7 = FD + "cinzel-latin-700-normal.woff"
CINZEL4 = FD + "cinzel-latin-400-normal.woff"
PLAY9 = FD + "playfair-display-latin-900-normal.woff"
PLAYI = FD + "playfair-display-latin-400-italic.woff"
GARA = FD + "eb-garamond-latin-400-normal.woff"
GARAI = FD + "eb-garamond-latin-400-italic.woff"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

PAL = {
    "storm":  dict(bg=(18, 22, 36), edge=(4, 5, 10), ink=(214, 224, 245), acc=(120, 200, 255), faint=(80, 96, 130), glow=True, tex="dark"),
    "volt":   dict(bg=(14, 12, 34), edge=(3, 3, 10), ink=(220, 230, 255), acc=(110, 220, 255), faint=(90, 90, 150), glow=True, tex="grid"),
    "blue":   dict(bg=(12, 30, 58), edge=(4, 10, 24), ink=(210, 228, 248), acc=(250, 210, 90), faint=(80, 110, 150), glow=False, tex="grid"),
    "sunset": dict(bg=(64, 30, 26), edge=(20, 8, 8), ink=(250, 226, 196), acc=(255, 170, 80), faint=(160, 110, 90), glow=True, tex="dark"),
    "amber":  dict(bg=(40, 26, 12), edge=(10, 6, 2), ink=(246, 222, 170), acc=(255, 190, 80), faint=(140, 110, 70), glow=True, tex="dark"),
    "dust":   dict(bg=(196, 180, 150), edge=(130, 110, 84), ink=(48, 38, 28), acc=(150, 60, 30), faint=(130, 112, 90), glow=False, tex="parch"),
    "blood":  dict(bg=(40, 8, 12), edge=(12, 2, 4), ink=(240, 220, 210), acc=(255, 70, 60), faint=(130, 70, 70), glow=True, tex="dark"),
    "purple": dict(bg=(30, 12, 48), edge=(8, 3, 14), ink=(236, 222, 255), acc=(200, 120, 255), faint=(120, 90, 160), glow=True, tex="dark"),
    "fire":   dict(bg=(30, 12, 6), edge=(8, 3, 1), ink=(255, 226, 190), acc=(255, 130, 40), faint=(140, 90, 60), glow=True, tex="dark"),
    "xray":   dict(bg=(4, 18, 30), edge=(1, 4, 8), ink=(190, 235, 255), acc=(120, 255, 230), faint=(60, 110, 130), glow=True, tex="grid"),
    "teal":   dict(bg=(8, 40, 44), edge=(2, 12, 14), ink=(214, 244, 240), acc=(255, 200, 90), faint=(70, 130, 130), glow=False, tex="grid"),
    "stone":  dict(bg=(58, 56, 54), edge=(18, 18, 18), ink=(232, 228, 220), acc=(255, 160, 60), faint=(130, 126, 120), glow=False, tex="dark"),
    "dark":   dict(bg=(10, 10, 12), edge=(2, 2, 3), ink=(220, 220, 225), acc=(255, 210, 120), faint=(90, 90, 100), glow=True, tex="dark"),
    "space":  dict(bg=(6, 6, 16), edge=(1, 1, 4), ink=(220, 225, 255), acc=(255, 100, 70), faint=(80, 80, 120), glow=True, tex="dark"),
    "night":  dict(bg=(10, 16, 30), edge=(2, 4, 10), ink=(214, 222, 240), acc=(120, 220, 255), faint=(70, 86, 120), glow=True, tex="grid"),
    "dusk":   dict(bg=(36, 30, 40), edge=(10, 8, 12), ink=(232, 222, 214), acc=(240, 180, 120), faint=(120, 104, 110), glow=True, tex="dark"),
    "copper": dict(bg=(36, 22, 14), edge=(10, 6, 4), ink=(240, 200, 160), acc=(110, 220, 255), faint=(140, 100, 70), glow=True, tex="dark"),
    # bg0, bg1 (vignette), ink, accent, faint, glow(bool)
    "parch":   dict(bg=(226, 212, 182), edge=(170, 150, 118), ink=(46, 36, 26), acc=(166, 32, 30), faint=(150, 132, 104), glow=False, tex="parch"),
    "parch2":  dict(bg=(214, 200, 170), edge=(150, 128, 98), ink=(40, 34, 30), acc=(30, 74, 120), faint=(140, 124, 100), glow=False, tex="parch"),
    "ink":     dict(bg=(16, 14, 12), edge=(4, 3, 3), ink=(232, 214, 170), acc=(236, 172, 72), faint=(110, 96, 72), glow=True, tex="dark"),
    "gold":    dict(bg=(22, 17, 10), edge=(6, 4, 2), ink=(240, 210, 140), acc=(255, 150, 60), faint=(120, 96, 60), glow=True, tex="dark"),
    "navy":    dict(bg=(16, 34, 62), edge=(6, 14, 30), ink=(205, 222, 240), acc=(240, 192, 90), faint=(80, 112, 150), glow=False, tex="grid"),
    "navy2":   dict(bg=(12, 22, 40), edge=(4, 8, 16), ink=(200, 214, 232), acc=(232, 90, 70), faint=(70, 96, 130), glow=True, tex="grid"),
    "green":   dict(bg=(18, 44, 34), edge=(6, 18, 12), ink=(226, 220, 186), acc=(232, 186, 80), faint=(90, 120, 100), glow=False, tex="damask"),
    "crimson": dict(bg=(44, 10, 12), edge=(14, 3, 4), ink=(238, 222, 206), acc=(255, 255, 255), faint=(130, 70, 70), glow=True, tex="dark"),
}


@functools.lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, int(size))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


@functools.lru_cache(maxsize=16)
def background(pal):
    p = PAL[pal]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    k = np.clip(r, 0, 1) ** 1.8
    bg = np.array(p["bg"], np.float32) * (1 - k[..., None]) + np.array(p["edge"], np.float32) * k[..., None]
    rs = np.random.RandomState(4)
    if p["tex"] == "parch":
        low = rs.rand(H // 40, W // 40).astype(np.float32)
        low = np.array(Image.fromarray((low * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
        mid = rs.rand(H // 8, W // 8).astype(np.float32)
        mid = np.array(Image.fromarray((mid * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
        bg *= (0.9 + 0.1 * low[..., None]) * (0.97 + 0.03 * mid[..., None])
    elif p["tex"] == "dark":
        low = rs.rand(H // 60, W // 60).astype(np.float32)
        low = np.array(Image.fromarray((low * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
        bg *= (0.85 + 0.3 * low[..., None])
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    if p["tex"] == "grid":
        c = tuple(int(v * 1.25) for v in p["bg"])
        for x in range(0, W, 60):
            d.line([(x, 0), (x, H)], fill=c, width=1)
        for y in range(0, H, 60):
            d.line([(0, y), (W, y)], fill=c, width=1)
    if p["tex"] == "damask":
        c = tuple(int(v * 1.18) for v in p["bg"])
        for y in range(0, H + 120, 120):
            for x in range(0, W + 120, 120):
                ox = 60 if (y // 120) % 2 else 0
                d.ellipse([x + ox - 18, y - 30, x + ox + 18, y + 30], outline=c, width=2)
                d.ellipse([x + ox - 30, y - 18, x + ox + 30, y + 18], outline=c, width=2)
    return img


# ------------------------------------------------------------------ strokes
def polyline_partial(pts, prog):
    if prog >= 1 or len(pts) < 2:
        return pts
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tgt = L[-1] * max(0, prog)
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tgt:
            out.append(pts[i])
        else:
            seg = L[i] - L[i - 1]
            k = (tgt - L[i - 1]) / seg if seg else 0
            a, b = pts[i - 1], pts[i]
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            break
    return out


def stroke(d, pts, col, w=3, prog=1.0, closed=False):
    if closed:
        pts = list(pts) + [pts[0]]
    pp = polyline_partial(pts, prog)
    if len(pp) >= 2:
        d.line(pp, fill=col, width=int(w), joint="curve")


def circle(d, cx, cy, r, col=None, fill=None, w=3):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, fill=fill, width=int(w))


def arc_pts(cx, cy, rx, ry, a0, a1, n=60):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + ry * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def glow_layer(img, layer, radius=18, strength=1.0):
    q = 4
    g = layer.resize((layer.width // q, layer.height // q), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(1, radius / q)))
    g = g.resize(layer.size, Image.BILINEAR)
    if strength != 1.0:
        g.putalpha(g.getchannel("A").point(lambda v: int(min(255, v * strength))))
    img.alpha_composite(g)
    img.alpha_composite(layer)


# ------------------------------------------------------------------ headline
def parse_head(head):
    lines = []
    for ln in head.split("|"):
        words = []
        acc = False
        for tok in ln.split(" "):
            if not tok:
                continue
            a0 = tok.startswith("[")
            if a0:
                acc = True
            word = tok.replace("[", "").replace("]", "")
            words.append((word, acc))
            if tok.endswith("]") or tok.endswith("].") or tok.endswith("]?") or tok.endswith("],"):
                acc = False
        lines.append(words)
    return lines


def draw_headline(img, head, pal, t, x, y, size=96, align="left", cap="", cap_t=0.6, maxw=None):
    p = PAL[pal]
    lines = parse_head(head)
    f = font(CINZEL9, size)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    wi = 0
    lh = size * 1.12
    widths = []
    for ln in lines:
        wsum = sum(d.textlength(w + " ", font=f) for w, _ in ln) - d.textlength(" ", font=f)
        widths.append(wsum)
    total_h = lh * len(lines)
    for li, ln in enumerate(lines):
        if align == "center":
            cx = x - widths[li] / 2
        else:
            cx = x
        cy = y + li * lh
        for w, acc in ln:
            k = ease_out((t - 0.12 * wi) / 0.45)
            if k > 0:
                col = p["acc"] if acc else p["ink"]
                a = int(255 * k)
                dy = (1 - k) * size * 0.35
                d.text((cx, cy + dy), w, font=f, fill=col + (a,))
            cx += d.textlength(w + " ", font=f)
            wi += 1
    if p["glow"]:
        glow_layer(img, layer, 14, 1.3)
    else:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(layer.getchannel("A").point(lambda v: v // 5))
        img.alpha_composite(sh, (3, 4))
        img.alpha_composite(layer)
    if cap:
        k = ease((t - cap_t) / 0.6)
        if k > 0:
            d2 = ImageDraw.Draw(img)
            fc = font(CINZEL7, 24)
            cy = y + total_h + 18
            txt = "   ".join(cap.split(" · "))
            col = p["faint"] + (int(255 * k),)
            if align == "center":
                d2.text((x, cy), cap, font=fc, fill=col, anchor="ma")
            else:
                d2.line([(x, cy - 6), (x + 90 * k, cy - 6)], fill=p["acc"] + (int(255 * k),), width=3)
                d2.text((x, cy + 8), cap, font=fc, fill=col)
    return total_h


# ------------------------------------------------------------------ HUD
HUD_TITLE = "NIKOLA TESLA  ·  1856 - 1943"
TL0, TL1, TLSTEP = 1856, 1943, 10


def hud(img, pal, chap, year, metric, t, gprog):
    p = PAL[pal]
    d = ImageDraw.Draw(img)
    c = p["faint"]
    fm = font(MONO, 20)
    d.text((70, 52), chap or "", font=fm, fill=c)
    d.text((W - 70, 52), HUD_TITLE, font=fm, fill=c, anchor="ra")
    d.text((70, H - 72), year, font=font(MONO, 24), fill=p["ink"])
    # timeline bar 1600..1997
    x0, x1, yb = 420, W - 420, H - 60
    d.line([(x0, yb), (x1, yb)], fill=c, width=2)
    for yr in range(1860, TL1 + 1, TLSTEP):
        xx = x0 + (x1 - x0) * (yr - TL0) / (TL1 - TL0)
        d.line([(xx, yb - 6), (xx, yb + 6)], fill=c, width=2)
        d.text((xx, yb + 12), str(yr), font=font(MONO, 13), fill=c, anchor="ma")
    yr = None
    for tok in year.replace("AD", "").split():
        if tok.isdigit():
            yr = int(tok)
    if yr:
        xx = x0 + (x1 - x0) * min(1, max(0, (yr - TL0) / (TL1 - TL0)))
        d.line([(x0, yb), (xx, yb)], fill=p["acc"], width=4)
        d.ellipse([xx - 7, yb - 7, xx + 7, yb + 7], fill=p["acc"])
    if metric is not None:
        d.text((W - 70, H - 90), "PATENTS", font=font(MONO, 14), fill=c, anchor="ra")
        d.text((W - 70, H - 72), f"{int(metric):03d}", font=font(MONO, 26), fill=p["ink"], anchor="ra")
    # global progress hairline
    d.line([(0, H - 3), (W * gprog, H - 3)], fill=p["acc"], width=3)
