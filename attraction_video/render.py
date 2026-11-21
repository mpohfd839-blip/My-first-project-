"""Renderer for 'Why Are Men Attracted to Women?'
Animates the AI illustrations: camera moves, twinkling glow, depth blur, pulsing focal points,
particles, chroma-keyed characters, labels, call-outs, chapter cards, karaoke subtitles.
usage: render.py a b out.mp4 | --still t1,t2,... | --info
"""
import functools, json, math, os, random, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from story import SHOTS

W, H, FPS = 1920, 1080, 24
BG = (28, 16, 58)
FRED = "fonts/fredoka-latin-700-normal.woff"
FRED6 = "fonts/fredoka-latin-600-normal.woff"
NUN9 = "fonts/nunito-latin-900-normal.woff"
NUN8 = "fonts/nunito-latin-800-normal.woff"
YEL, CYA, MAG, ORA = (255, 214, 80), (70, 230, 240), (255, 90, 190), (255, 140, 90)
PALETTE = [YEL, CYA, MAG, ORA, (180, 120, 255), (255, 255, 255)]

TL = json.load(open("timeline.json"))
AUD = TL["duration"]
SPECS = [sp for sp, _ in SHOTS]
SEG = []
for i, (sp, lines) in enumerate(SHOTS):
    ss = TL["timeline"][i]["sentences"]
    if ss:
        t0 = 0.0 if i == 0 else max(0.0, ss[0]["start"] - 0.3)
    else:
        t0 = SEG[-1]["sents"][-1]["end"] + 0.8
    SEG.append(dict(i=i, start=t0, sents=ss))
TOTAL = SEG[-1]["start"] + 12.0
for i, s_ in enumerate(SEG):
    s_["end"] = SEG[i + 1]["start"] if i + 1 < len(SEG) else TOTAL
NF = int(TOTAL * FPS)
ALL_SENTS = [se for s in SEG for se in s["sents"]]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def back(x):
    x = min(1.0, max(0.0, x))
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


@functools.lru_cache(maxsize=64)
def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ assets
@functools.lru_cache(maxsize=12)
def src(name):
    return Image.open(f"assets/{name}.jpg").convert("RGB")


@functools.lru_cache(maxsize=12)
def glowmap(name):
    """Half-resolution map of the bright, saturated parts of the picture (what should twinkle)."""
    im = src(name)
    im = im.resize((im.width // 2, im.height // 2), Image.BILINEAR)
    a = np.asarray(im).astype(np.float32)
    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(10))).astype(np.float32)
    hp = np.clip(a - bl, 0, 255).max(-1, keepdims=True)          # only small local highlights (dots, sparkles)
    g = np.clip(a * (hp / 60.0) ** 1.2, 0, 255).astype(np.uint8)
    return Image.fromarray(g).filter(ImageFilter.GaussianBlur(3))


@functools.lru_cache(maxsize=4)
def blurred(name):
    im = src(name).resize((960, 540), Image.BILINEAR).filter(ImageFilter.GaussianBlur(14))
    return Image.blend(im, Image.new("RGB", im.size, BG), 0.45)


@functools.lru_cache(maxsize=32)
def cutout(name, h):
    im = Image.open(f"cut/{name}.png")
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def _vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    v = 1 - 0.38 * np.clip(d - 0.45, 0, 1) ** 1.5 / 0.6
    v = (np.clip(v, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([v, v, v]))


VIG = _vignette()


# ------------------------------------------------------------------ sprites
@functools.lru_cache(maxsize=64)
def disc(col, r, hard=0.0):
    s = r * 2 + 2
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((x - s / 2) ** 2 + (y - s / 2) ** 2) / r
    a = np.clip(1 - d, 0, 1)
    a = a ** 1.6 if not hard else np.clip((1 - d) / max(hard, 1e-3), 0, 1)
    arr = np.zeros((s, s, 4), np.uint8)
    arr[..., :3] = col
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


@functools.lru_cache(maxsize=32)
def star(col, r):
    s = r * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    pts = []
    for k in range(8):
        ang = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.22
        pts.append((c + rr * math.cos(ang), c + rr * math.sin(ang)))
    d.polygon(pts, fill=col + (255,))
    g = im.filter(ImageFilter.GaussianBlur(r * 0.35))
    g.alpha_composite(im)
    d2 = ImageDraw.Draw(g)
    d2.ellipse([c - r * .18, c - r * .18, c + r * .18, c + r * .18], fill=(255, 255, 255, 255))
    return g


@functools.lru_cache(maxsize=32)
def heart(col, r):
    s = r * 3
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(60):
        t = k / 60 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((s / 2 + x * r / 17, s / 2 - y * r / 17))
    d.polygon(pts, fill=col + (255,))
    g = im.filter(ImageFilter.GaussianBlur(r * 0.3))
    g.alpha_composite(im)
    return g


@functools.lru_cache(maxsize=256)
def text_sprite(txt, path, size, col, glow=(0, 0, 0), glow_r=0, stroke=0, track=0):
    f = font(path, size)
    dd = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    if track:
        wds = [dd.textlength(ch, font=f) + track for ch in txt]
        tw = int(sum(wds) - track)
    else:
        tw = int(dd.textlength(txt, font=f))
    pad = glow_r * 3 + stroke + 10
    im = Image.new("RGBA", (tw + pad * 2, int(size * 1.35) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch, wd in zip(txt, wds):
            d.text((x, pad), ch, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=(20, 10, 40, 255))
            x += wd
    else:
        d.text((pad, pad), txt, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=(20, 10, 40, 255))
    if glow_r:
        g = Image.new("RGBA", im.size, glow + (0,))
        g.putalpha(im.getchannel("A"))
        g = g.filter(ImageFilter.GaussianBlur(glow_r))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
        return out
    return im


@functools.lru_cache(maxsize=128)
def pill(txt, col, size=46):
    f = font(NUN9, size)
    dd = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    tw = int(dd.textlength(txt, font=f))
    pw, ph = tw + size * 1.2, int(size * 1.6)
    pad = 26
    im = Image.new("RGBA", (int(pw) + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], ph // 2, fill=col + (255,))
    g = im.filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(im)
    d = ImageDraw.Draw(out)
    d.text((pad + pw / 2, pad + ph / 2 + 2), txt, font=f, fill=(24, 12, 48, 255), anchor="mm")
    return out


def fade(im, a):
    if a >= 0.999:
        return im
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0.0, a))))
    return im


def put(layer, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot:
        im = im.rotate(rot, Image.BILINEAR, expand=True)
    im = fade(im, alpha)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if x > W or y > H or x + im.width < 0 or y + im.height < 0:
        return
    layer.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


# ------------------------------------------------------------------ camera
class Cam:
    def __init__(self, name, spec, t, dur, gt, seg=None):
        im = src(name)
        self.iw, self.ih = im.size
        z0, z1, cx0, cy0, cx1, cy1 = spec["cam"]
        sp = split_point(spec, seg, dur) if seg else None
        if sp is None:
            p = ease(t / max(dur, 0.1))
            z = z0 + (z1 - z0) * p
            cx = (cx0 + (cx1 - cx0) * p) * self.iw
            cy = (cy0 + (cy1 - cy0) * p) * self.ih
        else:
            # long shot: first move until the split, then a quick camera push to a new framing
            zm, cxm, cym = z1, cx1, cy1
            if t < sp:
                p = ease(t / sp)
                z = z0 + (zm - z0) * p; cx = cx0 + (cxm - cx0) * p; cy = cy0 + (cym - cy0) * p
            else:
                dx = 0.1 if cxm <= 0.5 else -0.1
                zt, cxt, cyt = zm * 1.3, cxm + dx, cym
                k = ease_out((t - sp) / 0.7)
                drift = (t - sp) / max(dur - sp, 0.1)
                z = zm + (zt - zm) * k + zm * 0.08 * drift
                cx = cxm + (cxt - cxm) * k; cy = cym
            cx *= self.iw; cy *= self.ih
        vw0 = min(self.iw, self.ih * 16 / 9)
        vw = vw0 / z
        vh = vw * 9 / 16
        # gentle hand-held drift
        cx += math.sin(gt * 0.31) * vw * 0.006 + math.sin(gt * 0.83) * vw * 0.002
        cy += math.cos(gt * 0.27) * vh * 0.006
        sh = spec.get("shake", 0)
        if sh:
            cx += math.sin(gt * 41) * vw * 0.004 * sh * 3
            cy += math.cos(gt * 37) * vh * 0.004 * sh * 3
        cx = min(max(cx, vw / 2), self.iw - vw / 2)
        cy = min(max(cy, vh / 2), self.ih - vh / 2)
        self.cx, self.cy, self.vw, self.vh = cx, cy, vw, vh
        self.rot = 0.0
        if spec.get("spin"):
            self.rot = 0.05 * math.sin(gt * 0.35) + 0.012 * t

    def coeffs(self, scale=1.0):
        s = self.vw / W
        c, sn = math.cos(self.rot), math.sin(self.rot)
        a, b = s * c, -s * sn
        d, e = s * sn, s * c
        cc = self.cx - (a * W / 2 + b * H / 2)
        f = self.cy - (d * W / 2 + e * H / 2)
        return (a, b, cc * scale, d, e, f * scale)

    def to_screen(self, x, y):
        px, py = x * self.iw - self.cx, y * self.ih - self.cy
        c, sn = math.cos(-self.rot), math.sin(-self.rot)
        px, py = c * px - sn * py, sn * px + c * py
        s = W / self.vw
        return W / 2 + px * s, H / 2 + py * s


def s_of(gt, t):
    return SEG[shot_at(gt - 0.0001) if t >= 0 else 0]


def split_point(spec, s, dur):
    """For shots longer than 9 s, the local time of the sentence boundary closest to the middle."""
    if dur < 9 or spec.get("chapter") or spec.get("endcard") or spec.get("quad") or len(s["sents"]) < 2:
        return None
    cands = [se["start"] - s["start"] for se in s["sents"][1:]]
    best = min(cands, key=lambda c: abs(c - dur / 2))
    return best if 3 < best < dur - 3 else None


RNG = np.random.RandomState(5)
TW_PH = RNG.rand(27, 48).astype(np.float32) * 6.283
TW_FR = (0.25 + RNG.rand(27, 48) * 0.6).astype(np.float32)


def twinkle(name, cam, gt, amt=0.7):
    g = glowmap(name).transform((W // 2, H // 2), Image.AFFINE, cam.coeffs(0.5), Image.BILINEAR)
    m = (0.5 + 0.5 * np.sin(TW_FR * gt * 6.283 + TW_PH)) ** 2 * 255 * amt
    mi = Image.fromarray(m.astype(np.uint8)).resize((W // 2, H // 2), Image.BICUBIC)
    g = ImageChops.multiply(g, Image.merge("RGB", (mi, mi, mi)))
    return g.resize((W, H), Image.BILINEAR)


def radial_mask(cx, cy, r, w=W, h=H, soft=0.6, q=4):
    sw, sh_ = w // q, h // q
    y, x = np.mgrid[0:sh_, 0:sw].astype(np.float32)
    d = np.sqrt((x - cx / q) ** 2 + (y - cy / q) ** 2) / (r / q)
    m = np.clip((d - 1) / soft, 0, 1)
    return Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)


def pulse_region(img, cx, cy, r, s):
    r = int(r)
    if r < 8:
        return img
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    reg = img.crop(box)
    nr = int(2 * r * s)
    reg = reg.resize((nr, nr), Image.BICUBIC)
    m = Image.radial_gradient("L").resize((nr, nr), Image.BILINEAR).point(lambda v: 255 if v < 150 else max(0, int(255 - (v - 150) * 2.4)))
    img.paste(reg, (int(cx - nr / 2), int(cy - nr / 2)), m)
    return img


# ------------------------------------------------------------------ particle helpers
def particles(layer, seed, t, n, origin, spread, vel, life, kind, cols, size, gravity=0.0, rate=None):
    rs = random.Random(seed)
    rate = rate or n / life
    first = int(max(0, (t - life) * rate))
    last = int(t * rate) + 1
    for k in range(first, min(last, first + n * 3)):
        rk = random.Random(seed * 1000 + k)
        tb = k / rate
        age = t - tb
        if age < 0 or age > life:
            continue
        u = age / life
        ox = origin[0] + (rk.random() - .5) * spread[0]
        oy = origin[1] + (rk.random() - .5) * spread[1]
        vx = vel[0] * (0.5 + rk.random()) + (rk.random() - .5) * abs(vel[0] + vel[1]) * 0.4
        vy = vel[1] * (0.5 + rk.random())
        x = ox + vx * age + math.sin(age * 2 + k) * 12
        y = oy + vy * age + gravity * age * age
        a = math.sin(math.pi * u) ** 0.7
        col = cols[k % len(cols)]
        sz = int(size * (0.6 + rk.random() * 0.8))
        if kind == "disc":
            put(layer, disc(col, sz), x, y, 1, a * 0.9)
        elif kind == "star":
            put(layer, star(col, sz), x, y, 0.6 + 0.5 * abs(math.sin(age * 5 + k)), a)
        elif kind == "heart":
            put(layer, heart(col, sz), x, y, 1, a, rot=math.sin(age * 2 + k) * 15)
        elif kind == "ring":
            d = ImageDraw.Draw(layer)
            rr = sz + age * 60
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=col + (int(200 * (1 - u)),), width=4)
        else:
            put(layer, text_sprite(kind, FRED, sz * 2, col, col, 6), x, y, 1, a, rot=math.sin(age + k) * 20)


def bokeh(layer, gt, seed=3, n=10, alpha=0.22):
    for k in range(n):
        rk = random.Random(seed * 77 + k)
        r = rk.randint(18, 60)
        x = (rk.random() * (W + 200) + gt * (8 + rk.random() * 18) * (1 if k % 2 else -1)) % (W + 200) - 100
        y = (rk.random() * (H + 200) - gt * (6 + rk.random() * 10)) % (H + 200) - 100
        a = alpha * (0.5 + 0.5 * math.sin(gt * (0.4 + rk.random()) + k))
        put(layer, disc(PALETTE[k % 5], r), x, y, 1, a)


# ------------------------------------------------------------------ shot effects
def sent_t(s, idx):
    ss = s["sents"]
    if not ss:
        return s["start"]
    return ss[min(idx, len(ss) - 1)]["start"]


def word_t(s, idx, text):
    """Time the narrator says the first word of `text` inside sentence idx (falls back to the sentence start)."""
    ss = s["sents"]
    if not ss:
        return s["start"]
    se = ss[min(idx, len(ss) - 1)]
    toks = [w for w in re.sub(r"[^a-z ]", " ", text.lower()).split() if len(w) > 2]
    for w, tw in se.get("words", []):
        for tk in toks:
            if w.startswith(tk[:5]) or tk.startswith(w[:5]) and len(w) > 3:
                return tw
    return se["start"]


def draw_effects(layer, img, spec, cam, s, t, gt, dur):
    sc = cam.to_screen
    seed = s["i"] + 11
    if "sparks" in spec:
        x, y = sc(*spec["sparks"])
        particles(layer, seed, t, 18, (x, y), (500, 380), (0, -25), 2.2, "star", [YEL, (255, 255, 255), CYA, MAG], 16)
    if "fire" in spec:
        x, y = sc(*spec["fire"])
        particles(layer, seed + 1, t, 22, (x, y), (160, 40), (0, -140), 2.0, "disc", [ORA, YEL, (255, 100, 60)], 9)
    if "embers" in spec:
        x, y = sc(*spec["embers"])
        particles(layer, seed + 2, t, 30, (x, y + 100), (500, 200), (30, -220), 2.4, "disc", [YEL, ORA, MAG], 7)
    if spec.get("hearts"):
        particles(layer, seed + 3, t, 14, (W / 2, H + 40), (W * 0.8, 20), (0, -120), 7, "heart", [MAG, (255, 130, 170), ORA, YEL], 22)
    if spec.get("rain"):
        particles(layer, seed + 4, t, 40, (W / 2, -40), (W, 20), (0, 260), 4.5, "disc", [YEL, (255, 240, 150)], 9, gravity=10)
    if spec.get("confetti"):
        particles(layer, seed + 5, t, 60, (W / 2, H * 0.45), (200, 100), (0, -300), 2.5, "star", [YEL, CYA, MAG, ORA], 14, gravity=180, rate=60)
    if spec.get("qmarks"):
        particles(layer, seed + 6, t, 10, (W / 2, H * 0.55), (W * 0.7, 300), (0, -60), 4.0, "?", [YEL, CYA, MAG], 34)
    if "zzz" in spec:
        x, y = sc(*spec["zzz"])
        particles(layer, seed + 7, t, 5, (x, y), (20, 10), (40, -70), 3.0, "z", [CYA, (200, 200, 255)], 26)
    if "bubbles" in spec:
        x, y = sc(*spec["bubbles"])
        particles(layer, seed + 8, t, 10, (x, y), (350, 120), (0, -50), 3.5, "heart", [MAG, ORA, CYA], 18)
    if "phone" in spec:
        x, y = sc(*spec["phone"])
        particles(layer, seed + 9, t, 6, (x, y), (10, 10), (0, 0), 1.6, "ring", [MAG], 20, rate=1.3)
    if "scanpulse" in spec:
        x, y = sc(*spec["scanpulse"])
        particles(layer, seed + 10, t, 6, (x, y), (4, 4), (0, 0), 2.4, "ring", [CYA, (255, 160, 90)], 30, rate=1.2)
    if spec.get("shield") or spec.get("spinglobe") or spec.get("snap"):
        x, y = sc(.5, .5)
        particles(layer, seed + 11, t, 4, (x, y), (4, 4), (0, 0), 3.0, "ring", [YEL], 200, rate=0.6)
    if spec.get("smoke") or spec.get("blink") or spec.get("citylights") or spec.get("screens") or spec.get("swirl") or spec.get("pathglow") or spec.get("sunrays"):
        particles(layer, seed + 12, t, 16, (W / 2, H / 2), (W * 0.9, H * 0.8), (0, -18), 2.6, "star", [YEL, CYA, MAG, (255, 255, 255)], 12)
    if "wave" in spec:
        x, y = sc(*spec["wave"])
        particles(layer, seed + 13, t, 5, (x, y), (4, 4), (0, 0), 1.8, "ring", [CYA], 60, rate=1.5)
    if "waves" in spec:
        d = ImageDraw.Draw(layer)
        x0, y0 = sc(*spec["waves"])
        for k in range(3):
            pts = []
            for xx in range(0, 600, 12):
                amp = 40 * math.sin(math.pi * xx / 600) * (0.6 + 0.4 * math.sin(gt * 3 + k))
                pts.append((x0 - 300 + xx, y0 + (k - 1) * 30 + amp * math.sin(xx / 40 - gt * 8 + k * 2)))
            d.line(pts, fill=[CYA, MAG, YEL][k] + (150,), width=5, joint="curve")
    if spec.get("scan"):
        d = ImageDraw.Draw(layer)
        y = (0.5 + 0.45 * math.sin(gt * 1.3)) * H
        for k in range(14):
            d.line([(0, y + k * 3), (W, y + k * 3)], fill=CYA + (int(90 * (1 - k / 14)),), width=3)
        for (bx, by) in [(150, 130), (W - 150, 130), (150, H - 130), (W - 150, H - 130)]:
            sx, sy = (1 if bx < W / 2 else -1), (1 if by < H / 2 else -1)
            d.line([(bx, by), (bx + 90 * sx, by)], fill=CYA + (220,), width=6)
            d.line([(bx, by), (bx, by + 90 * sy)], fill=CYA + (220,), width=6)
    if "mirror" in spec:
        d = ImageDraw.Draw(layer)
        x, _ = sc(spec["mirror"], .5)
        a = int(140 + 100 * math.sin(gt * 4))
        for k in range(0, H, 36):
            d.line([(x, k), (x, k + 20)], fill=(255, 255, 255, a), width=5)
    if spec.get("ekg"):
        d = ImageDraw.Draw(layer)
        pts = []
        for xx in range(0, W + 1, 8):
            ph = ((xx / W) * 3 - gt * 1.4) % 1
            yv = 0
            if 0.40 < ph < 0.44:
                yv = -120 * math.sin((ph - 0.40) / 0.04 * math.pi)
            elif 0.44 < ph < 0.47:
                yv = 60 * math.sin((ph - 0.44) / 0.03 * math.pi)
            pts.append((xx, H * 0.82 + yv))
        d.line(pts, fill=(255, 90, 120, 210), width=6, joint="curve")
    if "spinring" in spec:
        d = ImageDraw.Draw(layer)
        x, y = sc(*spec["spinring"])
        r = 330 * W / cam.vw * cam.iw / 1920
        for k in range(12):
            a0 = gt * 40 + k * 30
            d.arc([x - r, y - r, x + r, y + r], a0, a0 + 14, fill=YEL + (200,), width=8)
    if spec.get("flow"):
        srcs = [(.1, .12), (.1, .48), (.1, .9)]
        tx, ty = sc(.72, .45)
        for j, (ax, ay) in enumerate(srcs):
            sx_, sy_ = sc(ax, ay)
            for k in range(7):
                u = ((gt * 0.45 + k / 7 + j * 0.13) % 1)
                x = sx_ + (tx - sx_) * u
                y = sy_ + (ty - sy_) * u + math.sin(u * math.pi * 2 + j) * 60
                put(layer, disc([CYA, MAG, YEL][j], 16), x, y, 1, math.sin(math.pi * u))
    if "hilite" in spec:
        for j, (hx, hy, _) in enumerate(spec["hilite"]):
            ss = s["sents"]
            ta = (ss[1]["start"] + j * (ss[1]["end"] - ss[1]["start"]) / 3.2) if len(ss) > 1 else s["start"]
            k = gt - ta
            if k > 0:
                x, y = sc(hx, hy)
                a = math.exp(-k * 0.9) * 0.9 + 0.15
                put(layer, disc(YEL, 260), x, y, 1 + 0.1 * math.sin(k * 6), a * 0.55)
    if spec.get("grid"):
        d = ImageDraw.Draw(layer)
        a = 40
        for k in range(0, W, 80):
            d.line([(k, 0), (k, H)], fill=CYA + (a,), width=1)
        for k in range(0, H, 80):
            d.line([(0, k), (W, k)], fill=CYA + (a,), width=1)


def draw_chars(layer, spec, s, t, gt, dur):
    for (name, x, y, h, si, dl, anim) in spec.get("chars", []):
        ta = sent_t(s, si) - s["start"] + dl if si else dl
        k = t - ta
        if k < 0:
            continue
        cx, cy = x * W, y * H
        sc, al, rot = 1.0, 1.0, 0.0
        if anim == "left":
            cx -= (1 - back(k / 0.7)) * 900
        elif anim == "right":
            cx += (1 - back(k / 0.7)) * 900
        elif anim == "pop":
            sc = back(k / 0.5)
        elif anim == "sweep":
            cx = -300 + (W + 600) * (k / max(dur - ta, 1)) ** 0.9
            rot = math.sin(gt * 3) * 8
        cy += math.sin(gt * 2.2 + x * 7) * 14
        sq = 1 + 0.02 * math.sin(gt * 4.4 + x * 5)
        im = cutout(name, int(h * sq))
        out_k = (dur - t)
        if out_k < 0.35:
            al = max(0, out_k / 0.35)
        put(layer, im, cx, cy, sc, al, rot)


def draw_labels(layer, spec, cam, s, t, gt, dur):
    d = ImageDraw.Draw(layer)
    for (txt, x, y, si, dl, col) in spec.get("labels", []):
        ta = word_t(s, si, txt) - s["start"] + dl
        k = t - ta
        if k < 0:
            continue
        al = min(1, k / 0.2) * min(1, (dur - t) / 0.3)
        sc = back(k / 0.45)
        px, py = cam.to_screen(x, y)
        if spec.get("nopoint"):
            put(layer, pill(txt, col), px, py + math.sin(gt * 2 + x * 9) * 5, sc, al)
        else:
            lx, ly = px, py - 150
            if ly < 120:
                ly = py + 150
            lx = min(max(lx, 260), W - 260)
            ly = min(max(ly, 90), H - 260)
            dl_ = ease_out(k / 0.4)
            d.line([(px, py), (px + (lx - px) * dl_, py + (ly - py) * dl_)], fill=col + (int(230 * al),), width=5)
            rr = 14 + 3 * math.sin(gt * 5)
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col + (int(255 * al),))
            d.ellipse([px - rr * 2, py - rr * 2, px + rr * 2, py + rr * 2], outline=col + (int(120 * al),), width=4)
            put(layer, pill(txt, col), lx, ly, sc, al)


def fmt_count(v):
    return f"{int(v):,}"


def draw_callouts(layer, spec, s, t, gt, dur):
    if "big" in spec:
        txt, sub, si = spec["big"]
        ta = word_t(s, si, txt) - s["start"]
        k = t - ta
        if k >= 0:
            al = min(1, k / 0.25) * min(1, (dur - t) / 0.35)
            if spec.get("count"):
                txt = fmt_count(spec["count"] * ease_out(k / 1.6))
            size = 150 if len(txt) < 14 else 104
            sp = text_sprite(txt, FRED, size, (255, 255, 255), YEL, 16, stroke=4)
            put(layer, sp, W / 2, H * 0.3, back(k / 0.5) if not spec.get("count") else 1, al)
            if sub:
                put(layer, text_sprite(sub, NUN9, 54, YEL, (0, 0, 0), 8, stroke=3, track=6), W / 2, H * 0.3 + size * 0.85, 1, al * min(1, max(0, k - .3) / .3))
    if "num" in spec:
        n, word = spec["num"]
        k = t - 0.15
        if k >= 0:
            al = min(1, (dur - t) / 0.3)
            sc = back(k / 0.5)
            put(layer, disc(YEL, 95, hard=0.08), 300, 230, sc, al)
            put(layer, text_sprite(n, FRED, 120, (30, 16, 60)), 300, 238, sc, al)
            put(layer, text_sprite(word, FRED, 110, (255, 255, 255), YEL, 14, stroke=3), 300 + 150 + 260, 232, sc, al)
    if "badge" in spec:
        txt, si, col = spec["badge"]
        ta = sent_t(s, si) - s["start"]
        k = t - ta
        if k >= 0:
            al = min(1, k / 0.1) * min(1, (dur - t) / 0.3)
            sc = 1 + 1.4 * (1 - ease_out(k / 0.22))
            sp = _badge(txt, col)
            put(layer, sp, W * 0.74, H * 0.24, sc, al, rot=8)


@functools.lru_cache(maxsize=8)
def _badge(txt, col):
    f = font(FRED, 92)
    dd = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    tw = int(dd.textlength(txt, font=f))
    im = Image.new("RGBA", (tw + 120, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, tw + 100, 170], 26, outline=col + (255,), width=12, fill=(30, 10, 40, 170))
    d.text(((tw + 120) / 2, 97), txt, font=f, fill=col + (255,), anchor="mm")
    return im


def draw_quad(layer, spec, s, t, gt, dur):
    tiles = spec["quad"]
    ss = s["sents"]
    t0, t1 = (ss[0]["start"], ss[0]["end"]) if ss else (s["start"], s["end"])
    for j, (name, lab, col) in enumerate(tiles):
        ta = (t0 - s["start"]) + 1.2 + j * (t1 - t0 - 1.6) / 4
        k = t - ta
        if k < 0:
            continue
        cx = W / 2 + (-1 if j % 2 == 0 else 1) * 390
        cy = H / 2 + (-1 if j < 2 else 1) * 205 - 75
        tw_, th_ = 700, 350
        im = _tile(name, tw_, th_, col)
        put(layer, im, cx, cy + math.sin(gt * 1.5 + j) * 6, back(k / 0.5), min(1, k / 0.2) * min(1, (dur - t) / 0.3))
        put(layer, pill(lab, col, 40), cx, cy + th_ / 2 - 12, back((k - 0.2) / 0.4), min(1, max(0, k - .2) / .2))


@functools.lru_cache(maxsize=8)
def _tile(name, tw_, th_, col):
    im = src(name)
    vw0 = min(im.width, im.height * 16 / 9)
    box = ((im.width - vw0) / 2, (im.height - vw0 * th_ / tw_) / 2, (im.width + vw0) / 2, (im.height + vw0 * th_ / tw_) / 2)
    im = im.resize((tw_, th_), Image.BICUBIC, box=box).convert("RGBA")
    m = Image.new("L", (tw_, th_), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tw_, th_], 36, fill=255)
    im.putalpha(m)
    pad = 30
    out = Image.new("RGBA", (tw_ + pad * 2, th_ + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([pad - 6, pad - 6, pad + tw_ + 6, pad + th_ + 6], 40, fill=col + (255,))
    g = out.filter(ImageFilter.GaussianBlur(16))
    g.alpha_composite(out)
    g.alpha_composite(im, (pad, pad))
    return g


NUMW = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX", 7: "SEVEN"}


def chapter_frame(spec, s, t, gt, dur):
    n, title = spec["chapter"]
    base = blurred(spec["img"])
    z = 1.08 + 0.06 * t / max(dur, 1)
    bw, bh = base.width / z, base.height / z
    img = base.resize((W, H), Image.BICUBIC, box=((base.width - bw) / 2, (base.height - bh) / 2, (base.width + bw) / 2, (base.height + bh) / 2)).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bokeh(layer, gt, seed=n + 40, n=16, alpha=0.35)
    al = min(1, (dur - t) / 0.3)
    k1 = t - 0.15
    head = "EPILOGUE" if n == 8 else f"PART {NUMW[n]}"
    put(layer, text_sprite(head, NUN9, 60, YEL, (8, 2, 24), 12, stroke=4, track=14), W / 2, H * 0.36, 1, min(1, max(0, k1) / 0.3) * al)
    if n != 8:
        k2 = t - 0.55
        if k2 > 0:
            put(layer, text_sprite(title, FRED, 118, (255, 255, 255), MAG, 18, stroke=3), W / 2, H * 0.5, 0.9 + 0.1 * back(k2 / 0.5), min(1, k2 / 0.3) * al)
            d = ImageDraw.Draw(layer)
            lw = 520 * ease_out((k2 - 0.2) / 0.6)
            d.rounded_rectangle([W / 2 - lw, H * 0.6, W / 2 + lw, H * 0.6 + 8], 4, fill=YEL + (int(255 * al),))
    else:
        put(layer, text_sprite("SO LET US GO BACK...", FRED, 96, (255, 255, 255), MAG, 18, stroke=3), W / 2, H * 0.52, 1, min(1, max(0, t - .5) / .4) * al)
    lumi = cutout("MASCOT_lumi", 260)
    k3 = t - 0.4
    if k3 > 0:
        put(layer, lumi, W * 0.86, H * 0.78 + math.sin(gt * 2.4) * 16, back(k3 / 0.5), al, rot=math.sin(gt * 1.7) * 6)
    # light sweep
    sw = (t / 1.4) % 3
    if sw < 1:
        d = ImageDraw.Draw(layer)
        x = -400 + sw * (W + 800)
        d.polygon([(x, 0), (x + 160, 0), (x - 140, H), (x - 300, H)], fill=(255, 255, 255, 22))
    img.alpha_composite(layer)
    return img.convert("RGB")


def title_layer(layer, t, gt, dur):
    al = min(1, (dur - t) / 0.4)
    l1, l2 = "WHY ARE MEN", "ATTRACTED TO WOMEN?"
    k = t - 0.3
    if k > 0:
        put(layer, text_sprite("THE SCIENCE OF ATTRACTION", NUN9, 50, (255, 255, 255), (8, 2, 24), 12, stroke=4, track=12), W / 2, H * 0.22, 1, min(1, k / .4) * al)
    k = t - 0.7
    if k > 0:
        put(layer, text_sprite(l1, FRED, 140, (255, 255, 255), MAG, 20, stroke=4), W / 2, H * 0.37, back(k / 0.5), min(1, k / .2) * al)
    k = t - 1.2
    if k > 0:
        put(layer, text_sprite(l2, FRED, 140, YEL, ORA, 20, stroke=4), W / 2, H * 0.52, back(k / 0.5), min(1, k / .2) * al)


def like_sub(layer, tt, x, y, scale=1.0):
    """Animated LIKE + SUBSCRIBE + bell, with a pointer that clicks them."""
    d = ImageDraw.Draw(layer)
    liked, subd = tt > 1.3, tt > 2.4
    bw, bh = 250 * scale, 96 * scale
    d.rounded_rectangle([x, y, x + bw, y + bh], bh / 2, fill=(255, 255, 255, 245) if not liked else (60, 120, 255, 255))
    f = font(NUN9, int(40 * scale))
    d.text((x + bw / 2 + 18 * scale, y + bh / 2), "LIKE", font=f, fill=(30, 20, 50) if not liked else (255, 255, 255), anchor="mm")
    tx, ty = x + 48 * scale, y + bh / 2
    d.polygon([(tx - 18 * scale, ty + 2), (tx - 6 * scale, ty - 22 * scale), (tx + 4 * scale, ty - 22 * scale), (tx, ty - 4), (tx + 16 * scale, ty - 4), (tx + 14 * scale, ty + 20 * scale), (tx - 18 * scale, ty + 20 * scale)],
              fill=(30, 20, 50) if not liked else (255, 255, 255))
    sx = x + bw + 24 * scale
    sw = 380 * scale
    d.rounded_rectangle([sx, y, sx + sw, y + bh], bh / 2 if subd else 18 * scale, fill=(230, 30, 50, 255) if not subd else (90, 80, 110, 255))
    d.text((sx + sw / 2, y + bh / 2), "SUBSCRIBED" if subd else "SUBSCRIBE", font=f, fill=(255, 255, 255), anchor="mm")
    bx = sx + sw + 24 * scale
    d.ellipse([bx, y, bx + bh, y + bh], fill=(255, 255, 255, 235) if tt < 3.3 else YEL + (255,))
    bc = (bx + bh / 2, y + bh / 2)
    wig = math.sin(tt * 25) * 0.35 if 3.3 < tt < 4.2 else 0
    pts = []
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.33 + wig
        pts.append((bc[0] + 26 * scale * math.cos(a) * (1 if k not in (0, 8) else 1.3), bc[1] - 4 + 26 * scale * math.sin(a) * (1 if k not in (0, 8) else .2)))
    d.polygon(pts, fill=(40, 30, 60))
    d.ellipse([bc[0] - 7 * scale, bc[1] + 14 * scale, bc[0] + 7 * scale, bc[1] + 26 * scale], fill=(40, 30, 60))
    # pointer
    if tt < 4.2:
        if tt < 1.3:
            k = ease(tt / 1.2); px, py = x + bw + 300 * scale - (300 * scale) * k, y + bh + 140 * scale - 100 * scale * k
        elif tt < 2.4:
            k = ease((tt - 1.3) / 1.0); px, py = x + bw + (sw / 2 + 24 * scale) * k, y + bh / 2 + 40 * scale
        else:
            k = ease((tt - 2.4) / 0.9); px, py = x + bw + sw / 2 + 24 * scale + (sw / 2 + 24 * scale + bh / 2) * k, y + bh / 2 + 40 * scale
        s_ = scale * 1.2
        d.polygon([(px, py), (px, py + 46 * s_), (px + 12 * s_, py + 36 * s_), (px + 22 * s_, py + 56 * s_), (px + 30 * s_, py + 52 * s_), (px + 20 * s_, py + 32 * s_), (px + 36 * s_, py + 32 * s_)],
                  fill=(255, 255, 255), outline=(20, 10, 40), width=3)


def endcard_frame(spec, s, t, gt, dur):
    img = src("S54_endcard_bg").resize((W, H), Image.BICUBIC).convert("RGBA")
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bokeh(layer, gt, 90, 14, 0.3)
    put(layer, text_sprite("THANKS FOR WATCHING!", FRED, 104, (255, 255, 255), MAG, 18, stroke=4), W / 2, H * 0.17, back(t / .5), min(1, t / .3))
    put(layer, text_sprite("What should we explain next? Tell us in the comments!", NUN9, 44, (255, 255, 255), (8, 2, 24), 12, stroke=4), W / 2, H * 0.27, 1, min(1, max(0, t - .5) / .4))
    d = ImageDraw.Draw(layer)
    for j, x in enumerate((W * 0.3, W * 0.7)):
        k = ease_out((t - 0.8 - j * 0.2) / 0.5)
        if k > 0:
            bw, bh = 640 * k, 360 * k
            d.rounded_rectangle([x - bw / 2, H * 0.55 - bh / 2, x + bw / 2, H * 0.55 + bh / 2], 30, outline=[YEL, CYA][j] + (230,), width=6, fill=(20, 10, 45, 150))
            if k > 0.95:
                d.text((x, H * 0.55), "WATCH NEXT" if j == 0 else "BEST FOR YOU", font=font(NUN9, 44), fill=(255, 255, 255, 230), anchor="mm", stroke_width=3, stroke_fill=(10, 4, 30))
    like_sub(layer, max(0, t - 1.5), W / 2 - 400, H * 0.83, 1.0)
    put(layer, cutout("MASCOT_lumi", 230), W * 0.92, H * 0.8 + math.sin(gt * 2.4) * 14, back((t - 1) / .5), 1, rot=math.sin(gt * 3) * 10)
    img.alpha_composite(layer)
    return img.convert("RGB")


# ------------------------------------------------------------------ shot renderer
def shot_frame(i, t, gt):
    s = SEG[i]
    spec = SPECS[i]
    dur = s["end"] - s["start"]
    if spec.get("chapter"):
        return chapter_frame(spec, s, t, gt, dur)
    if spec.get("endcard"):
        return endcard_frame(spec, s, t, gt, dur)
    name = spec["img"]
    if not os.path.exists(f"assets/{name}.jpg"):
        name = spec.get("fb", "S54_endcard_bg")      # image not delivered yet
    cam = Cam(name, spec, t, dur, gt, s)
    img = src(name).transform((W, H), Image.AFFINE, cam.coeffs(), Image.BICUBIC, fillcolor=BG)
    img = ImageChops.add(img, twinkle(name, cam, gt))
    if "pulse" in spec:
        x, y, r, hz = spec["pulse"]
        px, py = cam.to_screen(x, y)
        pr = r * cam.ih * W / cam.vw
        ph = (gt * hz) % 1
        beat = math.exp(-ph * 7) if hz > 0.95 else 0.5 + 0.5 * math.sin(gt * hz * 6.283)
        img = pulse_region(img, px, py, pr, 1 + 0.06 * beat)
    if "dof" in spec:
        x, y, r = spec["dof"]
        px, py = cam.to_screen(x, y)
        bl = img.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
        k = ease(t / 1.5)
        m = radial_mask(px, py, r * W * (1.6 - 0.6 * k), soft=0.8)
        if k < 1:
            m = m.point(lambda v: int(v * k))
        img = Image.composite(bl, img, m)
    if "tint" in spec:
        k = ease((t - 0.5) / 2)
        img = Image.blend(img, ImageChops.multiply(img, Image.new("RGB", (W, H), spec["tint"])), 0.45 * k)
    if spec.get("dim"):
        img = Image.blend(img, Image.new("RGB", (W, H), BG), spec["dim"])
    img = img.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bokeh(layer, gt, seed=i, n=9, alpha=0.18)
    draw_effects(layer, img, spec, cam, s, t, gt, dur)
    if "quad" in spec:
        draw_quad(layer, spec, s, t, gt, dur)
    draw_chars(layer, spec, s, t, gt, dur)
    draw_labels(layer, spec, cam, s, t, gt, dur)
    draw_callouts(layer, spec, s, t, gt, dur)
    if spec.get("title"):
        title_layer(layer, t, gt, dur)
    if spec.get("subscribe") and 1.0 < t < 7.5:
        like_sub(layer, t - 1.0, W - 860, 70, 0.9)
    img.alpha_composite(layer)
    return img.convert("RGB")


# ------------------------------------------------------------------ subtitles
@functools.lru_cache(maxsize=512)
def sub_layout(text, kws):
    f = font(NUN8, 46)
    dd = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    words = text.split()
    low = [re.sub(r"[^a-z0-9']", "", w.lower()) for w in words]
    hot = [False] * len(words)
    for kw in kws:
        kt = [re.sub(r"[^a-z0-9']", "", w.lower()) for w in kw.split()]
        for a in range(len(words) - len(kt) + 1):
            if low[a:a + len(kt)] == kt:
                for b in range(a, a + len(kt)):
                    hot[b] = True
    sp = dd.textlength(" ", font=f)
    lines, cur, cw = [], [], 0
    for j, w in enumerate(words):
        wl = dd.textlength(w, font=f)
        if cur and cw + sp + wl > 1500:
            lines.append((cur, cw)); cur, cw = [], 0
        cur.append((j, w, wl)); cw += (sp if cw else 0) + wl
    lines.append((cur, cw))
    # character offsets for timing
    tot = sum(len(w) + 1 for w in words)
    acc, pos = 0, []
    for w in words:
        pos.append(acc / tot); acc += len(w) + 1
    return lines, tuple(hot), tuple(pos), sp


def draw_subs(img, gt, i):
    cur = None
    for se in SEG[i]["sents"]:
        if se["start"] - 0.15 <= gt < se["end"] + 0.4:
            cur = se
    if i > 0 and cur is None:
        for se in SEG[i - 1]["sents"][-1:]:
            if se["start"] - 0.15 <= gt < se["end"] + 0.4:
                cur = se
    if not cur or SPECS[i].get("chapter"):
        return img
    kws = tuple(SPECS[i].get("kw", ()))
    lines, hot, pos, sp = sub_layout(cur["text"], kws)
    f = font(NUN8, 46)
    u = (gt - cur["start"]) / max(0.3, cur["end"] - cur["start"])
    al = min(1, (gt - cur["start"] + 0.15) / 0.2) * min(1, (cur["end"] + 0.4 - gt) / 0.2)
    lh = 62
    y0 = H - 70 - len(lines) * lh
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mw = max(cw for _, cw in lines)
    d.rounded_rectangle([W / 2 - mw / 2 - 34, y0 - 16, W / 2 + mw / 2 + 34, y0 + len(lines) * lh + 10], 28, fill=(18, 8, 40, int(150 * al)))
    for li, (ws, cw) in enumerate(lines):
        x = W / 2 - cw / 2
        y = y0 + li * lh
        for j, w, wl in ws:
            spoken = u >= pos[j] - 0.02
            if hot[j]:
                col = YEL if spoken else (190, 165, 90)
            else:
                col = (255, 255, 255) if spoken else (170, 160, 200)
            d.text((x, y), w, font=f, fill=col + (int(255 * al),), stroke_width=2, stroke_fill=(15, 5, 35, int(200 * al)))
            x += wl + sp
    im = img.convert("RGBA")
    im.alpha_composite(layer)
    return im.convert("RGB")


def shot_at(gt):
    for s in SEG:
        if gt < s["end"]:
            return s["i"]
    return len(SEG) - 1


def render_frame(fi):
    gt = fi / FPS
    i = shot_at(gt)
    s = SEG[i]
    t = gt - s["start"]
    img = shot_frame(i, t, gt)
    # transition from previous shot
    if i > 0:
        chap = SPECS[i].get("chapter") or SPECS[i - 1].get("chapter") or SPECS[i].get("endcard")
        tr = 0.55 if chap else 0.4
        if t < tr:
            p = SEG[i - 1]
            prev = shot_frame(i - 1, gt - p["start"], gt)
            k = ease(t / tr)
            if chap:
                z = 1 + 0.12 * k
                prev = prev.resize((W, H), Image.BILINEAR, box=(W * (1 - 1 / z) / 2, H * (1 - 1 / z) / 2, W * (1 + 1 / z) / 2, H * (1 + 1 / z) / 2))
                img = Image.blend(prev, img, k)
                fl = math.sin(math.pi * k) * 0.35
                img = Image.blend(img, Image.new("RGB", (W, H), (255, 240, 255)), fl)
            else:
                img = Image.blend(prev, img, k)
    img = ImageChops.multiply(img, VIG)
    # subtitles disabled on request: only key labels and call-outs are shown
    if gt < 0.8:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, ease(gt / 0.8))
    if TOTAL - gt < 1.5:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0, (TOTAL - gt) / 1.5))
    return img


if __name__ == "__main__":
    if sys.argv[1] == "--still":
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[2].split(","):
            render_frame(int(float(ts) * FPS)).save(f"stills/s_{float(ts):07.2f}.jpg", quality=88)
        sys.exit()
    if sys.argv[1] == "--info":
        print("frames", NF, "total", TOTAL)
        for s in SEG:
            print(s["i"], round(s["start"], 2), round(s["end"] - s["start"], 2), SPECS[s["i"]].get("img"))
        sys.exit()
    a, b_, outp = int(sys.argv[1]), min(int(sys.argv[2]), NF), sys.argv[3]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "2600k", "-bufsize", "5200k",
                          "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(a, b_):
        p.stdin.write(render_frame(fi).tobytes())
        if (fi - a) % 240 == 0:
            print(f"[{a}-{b_}] frame {fi} {(fi - a + 1) / (time.time() - t0 + 1e-6):.1f} fps", flush=True)
    p.stdin.close(); p.wait()
