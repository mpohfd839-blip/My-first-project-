"""Procedural flat-cartoon backgrounds. Each returns (bg RGBA 1920x1080, fg RGBA or None)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SW, SH = 1920, 1080
K = 2
OUT = (38, 28, 30, 255)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_HAND = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,))


class Cv:
    def __init__(self, w=SW, h=SH, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * K, h * K), bg)
        self.d = ImageDraw.Draw(self.img)

    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def poly(self, pts, fill, ol=True, w=3):
        pp = self._p(pts)
        self.d.polygon(pp, fill=fill)
        if ol:
            self.d.line(pp + [pp[0]], fill=OUT, width=w * K, joint="curve")

    def rect(self, x0, y0, x1, y1, fill, ol=True, w=3):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, ol, w)

    def ell(self, x0, y0, x1, y1, fill, ol=True, w=3):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=OUT if ol else None, width=w * K if ol else 0)

    def line(self, pts, fill=OUT, w=3):
        self.d.line(self._p(pts), fill=fill, width=int(w * K), joint="curve")

    def grad(self, x0, y0, x1, y1, c0, c1):
        for y in range(int(y0 * K), int(y1 * K)):
            t = (y - y0 * K) / max(1, (y1 - y0) * K)
            c = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)) + (255,)
            self.d.line([(x0 * K, y), (x1 * K, y)], fill=c)

    def text(self, xy, s, size, fill, font=FONT_B, anchor="mm", angle=0):
        f = ImageFont.truetype(font, int(size * K))
        if angle == 0:
            self.d.text((xy[0] * K, xy[1] * K), s, font=f, fill=fill, anchor=anchor)
        else:
            tmp = Image.new("RGBA", (int(size * K * len(s)), int(size * K * 2)), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((tmp.width / 2, tmp.height / 2), s, font=f, fill=fill, anchor="mm")
            tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
            self.img.alpha_composite(tmp, (int(xy[0] * K - tmp.width / 2), int(xy[1] * K - tmp.height / 2)))

    def done(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


# ------------------------------------------------------------ reusable bits
def window(c, x0, y0, x1, y1, sky=((150, 180, 210), (205, 220, 230)), night=False, curtains=(150, 60, 55), moon=False):
    c.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 14, (240, 236, 228))
    if night:
        sky = ((15, 22, 45), (35, 48, 80))
    c.grad(x0, y0, x1, y1, sky[0], sky[1])
    if moon:
        c.ell(x1 - 110, y0 + 40, x1 - 40, y0 + 110, (235, 235, 215), False)
    c.rect(x0, y0, x1, y1, None) if False else c.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], OUT, 4)
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], (240, 236, 228), 10)
    c.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], (240, 236, 228), 10)
    if curtains:
        cw = (x1 - x0) * 0.28
        c.poly([(x0 - 40, y0 - 40), (x0 + cw, y0 - 40), (x0 + cw * 0.6, y1 + 20), (x0 - 40, y1 + 30)], curtains)
        c.poly([(x1 + 40, y0 - 40), (x1 - cw, y0 - 40), (x1 - cw * 0.6, y1 + 20), (x1 + 40, y1 + 30)], curtains)
        c.rect(x0 - 70, y0 - 52, x1 + 70, y0 - 36, (90, 70, 50))


def frame(c, x0, y0, x1, y1, inner=(200, 190, 170), wood=(120, 80, 50)):
    c.rect(x0, y0, x1, y1, wood)
    c.rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10, inner)


def wallpaper(c, x0, y0, x1, y1, base, stripe, gap=60):
    c.rect(x0, y0, x1, y1, base, ol=False)
    x = x0
    while x < x1:
        c.rect(x, y0, x + gap * 0.35, y1, stripe, ol=False)
        x += gap


def floor_boards(c, y0, y1, col, vp=(960, 300)):
    c.rect(0, y0, SW, y1, col, ol=False)
    for i in range(-12, 13):
        xb = 960 + i * 170
        xt = vp[0] + (xb - vp[0]) * (y0 - vp[1]) / (y1 - vp[1])
        c.line([(xt, y0), (xb, y1)], sh(col, .8), 3)
    for k in range(1, 6):
        y = y0 + (y1 - y0) * (k / 6) ** 1.4
        c.line([(0, y), (SW, y)], sh(col, .86), 2)


def couch(c, x0, x1, y_seat, col):
    # back part (behind people)
    c.poly([(x0 + 20, y_seat - 260), (x1 - 20, y_seat - 260), (x1 - 10, y_seat), (x0 + 10, y_seat)], col)
    n = 3
    for i in range(n):
        a = x0 + 40 + (x1 - x0 - 80) * i / n
        b = x0 + 40 + (x1 - x0 - 80) * (i + 1) / n
        c.poly([(a + 6, y_seat - 240), (b - 6, y_seat - 240), (b - 4, y_seat - 30), (a + 4, y_seat - 30)], sh(col, 1.08))


def couch_front(c, x0, x1, y_seat, col, bottom=1080):
    c.poly([(x0 - 30, y_seat - 120), (x0 + 60, y_seat - 120), (x0 + 60, bottom), (x0 - 30, bottom)], sh(col, .92))
    c.poly([(x1 + 30, y_seat - 120), (x1 - 60, y_seat - 120), (x1 - 60, bottom), (x1 + 30, bottom)], sh(col, .92))
    c.poly([(x0 + 60, y_seat - 30), (x1 - 60, y_seat - 30), (x1 - 60, bottom), (x0 + 60, bottom)], sh(col, .85))
    c.line([(x0 + 60, y_seat + 20), (x1 - 60, y_seat + 20)], sh(col, .7), 4)


def lamp(c, x, y, shade=(235, 215, 160), on=True):
    c.rect(x - 8, y - 230, x + 8, y, (90, 80, 70))
    c.poly([(x - 60, y - 230), (x + 60, y - 230), (x + 40, y - 320), (x - 40, y - 320)], shade)
    c.ell(x - 70, y - 12, x + 70, y + 14, (90, 80, 70))


def corn(c, y_base, y_top, x0, x1, col=(150, 140, 70), dense=26, seed=1):
    rnd = random.Random(seed)
    c.rect(x0, y_top, x1, y_base, sh(col, .75), ol=False)
    x = x0
    while x < x1:
        hgt = rnd.uniform(0.7, 1.0) * (y_base - y_top)
        c.line([(x, y_base), (x + rnd.uniform(-6, 6), y_base - hgt)], sh(col, rnd.uniform(.8, 1.15)), 4)
        for k in range(3):
            yy = y_base - hgt * rnd.uniform(.3, .9)
            c.line([(x, yy), (x + rnd.choice([-1, 1]) * rnd.uniform(14, 30), yy - rnd.uniform(-8, 14))], sh(col, rnd.uniform(.8, 1.1)), 3)
        x += dense * rnd.uniform(.6, 1.2)


def tree_dead(c, x, y, s, col=(60, 50, 45), seed=3):
    rnd = random.Random(seed)
    def br(x0, y0, a, L, w, d):
        x1 = x0 + math.sin(a) * L
        y1 = y0 - math.cos(a) * L
        c.line([(x0, y0), (x1, y1)], col, w)
        if d > 0:
            br(x1, y1, a - rnd.uniform(.25, .6), L * .7, max(1, w * .65), d - 1)
            br(x1, y1, a + rnd.uniform(.25, .6), L * .7, max(1, w * .65), d - 1)
    br(x, y, 0, 120 * s, 14 * s, 5)


# ------------------------------------------------------------ backgrounds
def bg_apt(night=False, party=False):
    c = Cv()
    wall = (205, 180, 150) if not night else (120, 110, 115)
    c.rect(0, 0, SW, 800, wall, ol=False)
    c.rect(0, 770, SW, 800, sh(wall, .8), ol=False)
    floor_boards(c, 800, 1080, (150, 105, 70) if not night else (85, 65, 55))
    window(c, 180, 170, 560, 520, night=night, curtains=(110, 120, 90), moon=night)
    # shelf
    c.rect(1460, 200, 1760, 760, (120, 85, 55))
    for k in range(4):
        y = 230 + k * 130
        c.rect(1480, y, 1740, y + 110, (95, 65, 40))
        x = 1490
        rnd = random.Random(k)
        while x < 1720:
            w = rnd.randint(18, 34)
            c.rect(x, y + 110 - rnd.randint(60, 100), x + w, y + 110, rnd.choice([(170, 60, 60), (60, 90, 140), (200, 170, 80), (80, 120, 80), (220, 220, 210)]), w=2)
            x += w + 3
    # frames: you + emma doodles
    frame(c, 760, 160, 960, 330, (180, 210, 230))
    frame(c, 1010, 190, 1180, 330, (230, 200, 170))
    lamp(c, 1320, 770)
    if party:
        cols = [(220, 70, 80), (80, 140, 220), (250, 200, 60), (120, 200, 120)]
        for i in range(14):
            x = 120 + i * 130
            y = 90 + 40 * math.sin(i * .8)
            c.line([(x, y), (x + 130, 90 + 40 * math.sin((i + 1) * .8))], (80, 60, 50), 2)
            c.poly([(x + 20, y + 5), (x + 70, y + 5), (x + 45, y + 60)], cols[i % 4], w=2)
        for i, x in enumerate((650, 1250)):
            c.ell(x, 380, x + 90, 490, cols[i], w=3)
            c.line([(x + 45, 490), (x + 40, 640)], (80, 60, 50), 2)
        c.rect(700, 520, 1220, 600, (240, 230, 210))
        c.text((960, 560), "HAPPY BIRTHDAY", 44, (200, 60, 70, 255))
    couch(c, 360, 1360, 900, (90, 110, 120) if not night else (60, 72, 85))
    bg = c.done()
    f = Cv()
    couch_front(f, 360, 1360, 900, (90, 110, 120) if not night else (60, 72, 85))
    # coffee table
    f.poly([(560, 1000), (1160, 1000), (1200, 1080), (520, 1080)], (130, 90, 60))
    return bg, f.done()


def bg_class():
    c = Cv()
    c.rect(0, 0, SW, 760, (215, 210, 185), ol=False)
    c.rect(0, 740, SW, 760, (140, 120, 90), ol=False)
    c.rect(0, 760, SW, 1080, (175, 160, 130), ol=False)
    c.rect(330, 120, 1590, 540, (50, 85, 65), w=10)
    c.rect(330, 540, 1590, 560, (140, 110, 80))
    c.text((960, 200), "STATISTICS 101", 56, (235, 235, 225, 255))
    c.text((700, 330), "P(A|B) = P(B|A)P(A) / P(B)", 34, (230, 230, 220, 230))
    c.text((1200, 430), "σ = √Σ(x-μ)²/N", 34, (230, 230, 220, 230))
    c.ell(1660, 140, 1800, 280, (245, 245, 240))
    c.line([(1730, 210), (1730, 160)], OUT, 4)
    c.line([(1730, 210), (1765, 225)], OUT, 4)
    window(c, 40, 160, 260, 560, curtains=None)
    bg = c.done()
    f = Cv()
    for x0 in (280, 1080):
        f.poly([(x0, 920), (x0 + 560, 920), (x0 + 600, 960), (x0 - 40, 960)], (200, 160, 110))
        f.rect(x0 - 40, 960, x0 + 600, 985, (170, 130, 90))
        f.rect(x0, 985, x0 + 20, 1080, (90, 90, 95))
        f.rect(x0 + 540, 985, x0 + 560, 1080, (90, 90, 95))
    return bg, f.done()


def bg_notebook():
    c = Cv()
    c.rect(0, 0, SW, SH, (150, 110, 75), ol=False)
    c.poly([(260, 60), (1680, 40), (1720, 1040), (230, 1060)], (248, 246, 236))
    for k in range(18):
        y = 160 + k * 50
        c.line([(250, y), (1700, y - 18)], (150, 180, 220), 2)
    c.line([(470, 60), (440, 1060)], (225, 120, 120), 3)
    for k in range(14):
        y = 100 + k * 70
        c.ell(200, y, 240, y + 30, (180, 180, 185), w=2)
    c.text((1000, 220), "Lecture 4 - Probability", 40, (60, 60, 120, 255), font=FONT_HAND, angle=1)
    return c.done(), None


def farmhouse(c, x, y, s=1.0, xmas=False, night=False):
    W, H = 640 * s, 360 * s
    wall = (238, 236, 228) if not night else (150, 155, 170)
    roof = (80, 70, 75)
    c.poly([(x - W / 2 - 30 * s, y - H), (x + W / 2 + 30 * s, y - H), (x + W / 4, y - H - 220 * s), (x - W / 4, y - H - 220 * s)], roof)
    if xmas:
        c.poly([(x - W / 2 - 30 * s, y - H), (x + W / 2 + 30 * s, y - H), (x + W / 4, y - H - 220 * s), (x - W / 4, y - H - 220 * s)], (240, 245, 250))
    c.rect(x - W / 2, y - H, x + W / 2, y, wall)
    for k in range(1, 12):
        c.line([(x - W / 2, y - H + k * H / 12), (x + W / 2, y - H + k * H / 12)], sh(wall, .9), 2)
    c.rect(x + W / 4 - 20 * s, y - H - 260 * s, x + W / 4 + 30 * s, y - H - 120 * s, (120, 70, 60))
    lit = (255, 210, 120) if night or xmas else (150, 170, 190)
    for wx in (-0.36, -0.12, 0.12, 0.36):
        for wy in (-0.78, -0.38):
            X = x + W * wx
            Y = y + H * wy
            if wx == 0.12 and wy == -0.38:
                continue
            c.rect(X - 32 * s, Y - 45 * s, X + 32 * s, Y + 45 * s, lit)
            c.line([(X, Y - 45 * s), (X, Y + 45 * s)], OUT, 2)
            c.rect(X - 46 * s, Y - 45 * s, X - 32 * s, Y + 45 * s, (60, 70, 80))
            c.rect(X + 32 * s, Y - 45 * s, X + 46 * s, Y + 45 * s, (60, 70, 80))
    # door + porch
    c.rect(x + W * .12 - 34 * s, y - 150 * s, x + W * .12 + 34 * s, y, (120, 40, 40))
    c.poly([(x - W / 2 - 10 * s, y - 190 * s), (x + W / 2 + 10 * s, y - 190 * s), (x + W / 2 + 40 * s, y - 160 * s), (x - W / 2 - 40 * s, y - 160 * s)], (110, 100, 100))
    for px in range(0, 7):
        X = x - W / 2 + px * W / 6
        c.rect(X - 6 * s, y - 160 * s, X + 6 * s, y, (240, 240, 235))
    c.rect(x - W / 2 - 30 * s, y - 50 * s, x + W / 2 + 30 * s, y - 40 * s, (240, 240, 235))
    if xmas:
        cols = [(255, 80, 80), (80, 255, 120), (255, 220, 80), (100, 160, 255)]
        for k in range(30):
            X = x - W / 2 - 30 * s + k * (W + 60 * s) / 29
            c.ell(X - 6, y - H - 4 - 6 * math.sin(k), X + 6, y - H + 8 - 6 * math.sin(k), cols[k % 4], ol=False)
        c.ell(x + W * .12 - 30 * s, y - 135 * s, x + W * .12 + 30 * s, y - 75 * s, (40, 110, 60))


def bg_farm(xmas=False, car=None):
    c = Cv()
    night = xmas
    if night:
        c.grad(0, 0, SW, 620, (15, 20, 40), (50, 60, 90))
    else:
        c.grad(0, 0, SW, 620, (150, 155, 160), (200, 200, 195))
        for k in range(6):
            x = 200 + k * 330
            c.ell(x, 80 + 30 * (k % 2), x + 380, 200 + 30 * (k % 2), (175, 178, 182), ol=False)
    # tree line
    for k in range(40):
        x = k * 50
        c.ell(x - 40, 520 - (k * 37 % 50), x + 60, 640, (90, 95, 85) if not night else (30, 35, 45), ol=False)
    ground = (140, 130, 95) if not night else (215, 222, 235)
    c.rect(0, 610, SW, SH, ground, ol=False)
    if not night:
        corn(c, 760, 600, 0, 600, seed=2)
        corn(c, 760, 600, 1400, SW, seed=5)
    else:
        corn(c, 760, 610, 0, 600, col=(200, 205, 215), seed=2)
        corn(c, 760, 610, 1400, SW, col=(200, 205, 215), seed=5)
    farmhouse(c, 980, 760, 1.0, xmas=xmas, night=night)
    # barn
    c.poly([(1460, 760), (1460, 560), (1560, 480), (1660, 560), (1660, 760)], (150, 50, 45) if not night else (90, 40, 45))
    if night:
        c.poly([(1450, 565), (1560, 475), (1670, 565), (1660, 580), (1560, 500), (1460, 580)], (240, 245, 250))
    c.rect(1520, 640, 1600, 760, (110, 35, 35))
    # gravel drive
    c.poly([(1070, 760), (1180, 760), (900, 1080), (520, 1080)], (170, 165, 160) if not night else (190, 195, 210))
    rnd = random.Random(4)
    for k in range(400):
        yy = rnd.uniform(765, 1075)
        t = (yy - 760) / 320
        xa = 1070 + (520 - 1070) * t
        xb = 1180 + (900 - 1180) * t
        xx = rnd.uniform(xa, xb)
        r = 2 + 4 * t
        c.ell(xx - r, yy - r * .6, xx + r, yy + r * .6, (130, 125, 120), ol=False)
    # mailbox
    c.rect(420, 790, 432, 900, (90, 70, 50))
    c.rect(380, 750, 470, 795, (60, 70, 80))
    if car == "parked":
        draw_car(c, 760, 900, 0.9)
    return c.done(), None


def draw_car(c, x, y, s=1.0, col=(120, 30, 35), lights=False, people=None):
    # side view sedan, facing right
    body = [(x - 260 * s, y - 40 * s), (x - 250 * s, y - 110 * s), (x - 140 * s, y - 120 * s), (x - 80 * s, y - 190 * s), (x + 90 * s, y - 190 * s), (x + 160 * s, y - 120 * s), (x + 270 * s, y - 105 * s), (x + 280 * s, y - 40 * s)]
    c.poly(body, col)
    c.poly([(x - 120 * s, y - 120 * s), (x - 70 * s, y - 178 * s), (x, y - 178 * s), (x, y - 120 * s)], (150, 175, 195))
    c.poly([(x + 15 * s, y - 120 * s), (x + 15 * s, y - 178 * s), (x + 85 * s, y - 178 * s), (x + 140 * s, y - 120 * s)], (150, 175, 195))
    if people:
        for (px, colr) in people:
            c.ell(x + px * s - 22 * s, y - 175 * s, x + px * s + 22 * s, y - 128 * s, colr, ol=False)
    c.line([(x - 250 * s, y - 75 * s), (x + 275 * s, y - 75 * s)], sh(col, .7), 3)
    c.rect(x + 255 * s, y - 100 * s, x + 280 * s, y - 85 * s, (255, 240, 180) if lights else (230, 230, 220), w=2)
    c.rect(x - 262 * s, y - 100 * s, x - 248 * s, y - 85 * s, (200, 40, 40), w=2)


def wheel(c, x, y, s, ang):
    c.ell(x - 48 * s, y - 48 * s, x + 48 * s, y + 48 * s, (30, 30, 32))
    c.ell(x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s, (170, 170, 175))
    for k in range(5):
        a = ang + k * 2 * math.pi / 5
        c.line([(x, y), (x + math.cos(a) * 24 * s, y + math.sin(a) * 24 * s)], (90, 90, 95), 3)


def bg_lake(night=False, toys=False):
    c = Cv()
    if night:
        c.grad(0, 0, SW, 520, (10, 14, 28), (30, 36, 55))
    else:
        c.grad(0, 0, SW, 520, (155, 160, 165), (205, 205, 200))
    for k in range(30):
        x = k * 70
        c.ell(x - 50, 430 - (k * 23 % 40), x + 80, 560, (85, 90, 80) if not night else (20, 24, 30), ol=False)
    water = (110, 120, 125) if not night else (12, 16, 24)
    c.rect(0, 520, SW, SH, water, ol=False)
    for k in range(18):
        y = 560 + k * 30
        x = (k * 263) % 1600
        c.line([(x, y), (x + 200 + k * 10, y)], sh(water, 1.15), 2)
    # dock
    dock = (110, 85, 60) if not night else (45, 40, 38)
    c.poly([(700, 1080), (1000, 1080), (980, 640), (900, 640)], dock)
    for k in range(10):
        y = 650 + k * 45
        c.line([(900 - (k * 6), y), (980 + (k * 2), y)], sh(dock, .7), 3)
    tree_dead(c, 220, 620, 2.2, (50, 45, 42) if not night else (8, 8, 12), 3)
    tree_dead(c, 1680, 640, 2.6, (50, 45, 42) if not night else (8, 8, 12), 7)
    # reeds
    rnd = random.Random(9)
    for k in range(60):
        x = rnd.uniform(0, 600) if k < 30 else rnd.uniform(1300, SW)
        c.line([(x, 1080), (x + rnd.uniform(-20, 20), 1080 - rnd.uniform(100, 260))], (80, 90, 60) if not night else (15, 20, 15), 4)
    if toys:
        c.ell(1150, 700, 1230, 740, (230, 120, 140))
        c.poly([(1300, 760), (1360, 740), (1380, 770), (1320, 790)], (240, 220, 80))
    return c.done(), None


def bg_frontdoor(xmas=False):
    c = Cv()
    sky = (40, 50, 80) if xmas else (170, 172, 175)
    c.rect(0, 0, SW, SH, sky, ol=False)
    wall = (238, 236, 228) if not xmas else (200, 205, 220)
    c.rect(0, 0, SW, 900, wall, ol=False)
    for k in range(1, 20):
        c.line([(0, k * 45), (SW, k * 45)], sh(wall, .9), 2)
    # open doorway with warm interior
    c.rect(700, 140, 1240, 900, (255, 205, 140))
    c.rect(720, 160, 1220, 900, (250, 210, 160), ol=False)
    c.rect(720, 160, 1220, 560, (220, 175, 120), ol=False)
    c.rect(1000, 250, 1120, 370, (130, 90, 60))
    c.poly([(1220, 160), (1380, 120), (1380, 940), (1220, 900)], (130, 40, 40))
    c.rect(550, 300, 640, 560, (60, 80, 90))
    c.rect(1300, 300, 1390, 560, (60, 80, 90))
    c.rect(0, 900, SW, SH, (130, 110, 100), ol=False)
    for k in range(6):
        c.line([(0, 900 + k * 32), (SW, 900 + k * 32)], (100, 85, 78), 3)
    c.ell(640, 120, 700, 180, (255, 240, 180))
    if xmas:
        c.ell(890, 180, 1050, 340, (40, 110, 60), w=4)
        c.ell(930, 220, 1010, 300, (250, 210, 160), ol=False)
        c.poly([(950, 320), (990, 320), (1000, 360), (940, 360)], (200, 40, 40))
        cols = [(255, 80, 80), (80, 255, 120), (255, 220, 80), (100, 160, 255)]
        for k in range(24):
            X = 680 + k * 25
            c.ell(X - 6, 120 - 6 + 8 * math.sin(k), X + 6, 132 + 8 * math.sin(k), cols[k % 4], ol=False)
    return c.done(), None


def bg_dining(xmas=False, props=()):
    c = Cv()
    wallpaper(c, 0, 0, SW, 760, (180, 150, 120), (165, 135, 108), 70)
    c.rect(0, 560, SW, 760, (120, 80, 55), ol=False)
    c.line([(0, 560), (SW, 560)], OUT, 4)
    c.rect(0, 760, SW, SH, (110, 75, 50), ol=False)
    window(c, 760, 120, 1160, 470, night=True, curtains=(140, 40, 40))
    # chandelier
    c.line([(960, 0), (960, 70)], OUT, 4)
    c.poly([(880, 70), (1040, 70), (1000, 110), (920, 110)], (200, 170, 90))
    for x in (870, 930, 990, 1050):
        c.ell(x - 12, 100, x + 12, 130, (255, 230, 160))
    # hutch
    c.rect(1500, 180, 1820, 760, (110, 70, 45))
    c.rect(1530, 210, 1790, 470, (160, 190, 200))
    for x in (1560, 1640, 1720):
        c.ell(x, 260, x + 60, 320, (240, 240, 235), w=2)
        c.ell(x, 370, x + 60, 430, (240, 240, 235), w=2)
    frame(c, 160, 200, 380, 420, (200, 170, 140))
    if xmas:
        # tree
        for k in range(5):
            y = 220 + k * 100
            w = 60 + k * 50
            c.poly([(320, y - 90), (320 + w, y + 40), (320 - w, y + 40)], (30, 100, 55))
        c.rect(300, 720, 340, 770, (90, 60, 40))
        cols = [(255, 80, 80), (255, 220, 80), (100, 160, 255), (240, 240, 255)]
        rnd = random.Random(5)
        for k in range(40):
            yy = rnd.uniform(200, 700)
            ww = 60 + (yy - 220) / 100 * 50
            xx = 320 + rnd.uniform(-ww * .8, ww * .8)
            c.ell(xx - 8, yy - 8, xx + 8, yy + 8, cols[k % 4], w=1)
        c.poly([(320, 110), (340, 150), (300, 150)], (255, 220, 80))
    bg = c.done()
    # chairs backs behind people are part of bg
    f = Cv()
    f.poly([(80, 880), (1840, 880), (1920, 1080), (0, 1080)], (245, 240, 230) if not xmas else (170, 40, 45))
    f.line([(80, 880), (1840, 880)], OUT, 4)
    f.poly([(0, 1040), (1920, 1040), (1920, 1080), (0, 1080)], (225, 220, 205) if not xmas else (140, 30, 35), ol=False)
    if "turkey" in props:
        f.ell(860, 820, 1060, 940, (240, 240, 240))
        f.ell(890, 790, 1030, 900, (190, 120, 60))
        f.ell(1010, 820, 1050, 850, (240, 230, 210))
        f.ell(560, 880, 700, 930, (240, 240, 240))
        f.ell(580, 870, 680, 915, (80, 140, 70), ol=False)
        f.ell(1220, 880, 1360, 930, (240, 240, 240))
        f.ell(1240, 870, 1340, 915, (230, 200, 120), ol=False)
    if "cake" in props:
        f.ell(860, 900, 1060, 960, (240, 240, 240))
        f.rect(890, 820, 1030, 920, (245, 215, 225))
        f.ell(890, 800, 1030, 840, (250, 230, 235))
        for x in (920, 960, 1000):
            f.rect(x - 4, 770, x + 4, 815, (120, 170, 230), w=2)
            f.ell(x - 7, 750, x + 7, 772, (255, 200, 80), ol=False)
    return bg, f.done()


def bg_living(xmas=False):
    c = Cv()
    wallpaper(c, 0, 0, SW, 780, (150, 165, 130), (138, 152, 118), 80)
    c.rect(0, 760, SW, 790, (110, 80, 55), ol=False)
    c.rect(0, 790, SW, SH, (120, 95, 75), ol=False)
    # rug
    c.ell(250, 900, 1500, 1120, (140, 60, 50))
    # kitchen doorway (dark)
    c.rect(1560, 170, 1880, 790, (60, 55, 50))
    c.rect(1580, 190, 1860, 790, (30, 30, 32), ol=False)
    c.rect(1600, 450, 1840, 520, (50, 50, 55), ol=False)
    # family photos (emma only)
    frame(c, 300, 150, 470, 340, (230, 200, 170))
    frame(c, 520, 120, 700, 330, (210, 220, 200))
    frame(c, 760, 160, 900, 330, (220, 200, 210))
    # fireplace
    c.rect(1080, 380, 1460, 780, (150, 80, 65))
    c.rect(1050, 360, 1490, 395, (230, 225, 215))
    c.rect(1170, 520, 1370, 780, (35, 25, 25))
    c.rect(1180, 230, 1360, 350, (220, 225, 200))
    if xmas:
        for k, x in enumerate((1110, 1230, 1350)):
            c.poly([(x, 395), (x + 40, 395), (x + 40, 470), (x + 60, 490), (x + 20, 500), (x, 470)], (200, 40, 40) if k % 2 == 0 else (30, 110, 60), w=2)
        c.ell(1210, 680, 1330, 790, (255, 140, 40), ol=False)
        for k in range(5):
            y = 260 + k * 100
            w = 50 + k * 45
            c.poly([(130, y - 90), (130 + w, y + 40), (130 - w, y + 40)], (30, 100, 55))
        cols = [(255, 80, 80), (255, 220, 80), (100, 160, 255)]
        rnd = random.Random(2)
        for k in range(30):
            yy = rnd.uniform(220, 740)
            ww = 50 + (yy - 260) / 100 * 45
            xx = 130 + rnd.uniform(-ww * .7, ww * .7)
            c.ell(xx - 8, yy - 8, xx + 8, yy + 8, cols[k % 3], w=1)
    couch(c, 360, 1060, 920, (120, 70, 60))
    bg = c.done()
    f = Cv()
    couch_front(f, 360, 1060, 920, (120, 70, 60))
    return bg, f.done()


def bg_porch():
    c = Cv()
    c.grad(0, 0, SW, 600, (8, 12, 26), (28, 34, 52))
    c.ell(1500, 90, 1600, 190, (220, 225, 215), ol=False)
    c.rect(0, 520, SW, 760, (8, 10, 16), ol=False)
    for k in range(10):
        c.line([(100 + k * 170, 560 + k * 13), (220 + k * 170, 560 + k * 13)], (30, 36, 50), 2)
    for k in range(25):
        x = k * 80
        c.ell(x - 50, 470 - (k * 23 % 40), x + 80, 545, (12, 14, 20), ol=False)
    # porch floor + posts + rail
    c.poly([(0, 760), (SW, 760), (SW, SH), (0, SH)], (90, 80, 75))
    for k in range(8):
        c.line([(0, 760 + k * 45), (SW, 760 + k * 45)], (70, 62, 58), 3)
    for x in (120, 1800):
        c.rect(x - 22, 0, x + 22, 760, (210, 205, 195))
    c.rect(0, 600, SW, 625, (210, 205, 195))
    for k in range(30):
        x = 30 + k * 65
        c.rect(x - 6, 625, x + 6, 760, (200, 195, 185), w=2)
    # back door with warm window at left
    c.rect(0, 0, 160, 760, (120, 115, 110), ol=False)
    c.ell(880, 20, 1040, 60, (255, 230, 160), ol=False)
    return c.done(), None


def bg_guest(puddle=False):
    c = Cv()
    wall = (120, 115, 130)
    c.rect(0, 0, SW, 720, wall, ol=False)
    floor_boards(c, 720, 1080, (100, 80, 65))
    window(c, 1300, 120, 1640, 470, night=True, curtains=(80, 70, 100), moon=True)
    # moonlight patch on floor
    c.poly([(1180, 760), (1560, 760), (1760, 1000), (1300, 1000)], (150, 150, 175, 255), ol=False)
    # door
    c.rect(1720, 180, 1900, 720, (90, 70, 60))
    c.ell(1735, 450, 1755, 470, (200, 180, 100))
    # nightstand + clock
    c.rect(80, 520, 280, 720, (100, 70, 50))
    c.rect(120, 470, 240, 520, (30, 30, 30))
    c.text((180, 495), "2:47", 34, (255, 60, 50, 255))
    frame(c, 500, 140, 700, 320, (150, 160, 170))
    # bed headboard + bed
    c.rect(380, 330, 1180, 600, (110, 75, 55))
    c.rect(360, 560, 1200, 860, (220, 220, 230))
    c.ell(520, 520, 820, 640, (245, 245, 250))
    if puddle:
        c.ell(1420, 930, 1640, 990, (70, 90, 115), ol=False)
        c.ell(1440, 940, 1600, 975, (110, 130, 160), ol=False)
    bg = c.done()
    f = Cv()
    f.poly([(330, 660), (1230, 660), (1260, 900), (300, 900)], (90, 100, 140))
    f.line([(330, 700), (1230, 700)], (70, 80, 115), 6)
    f.rect(300, 900, 1260, 960, (110, 75, 55))
    return bg, f.done()


def bg_hall(door_glow=False):
    c = Cv()
    vp = (960, 480)
    wall = (150, 140, 120)
    c.rect(0, 0, SW, SH, sh(wall, .9), ol=False)
    # back wall
    bx0, by0, bx1, by1 = 780, 260, 1140, 700
    c.poly([(0, 0), (bx0, by0), (bx0, by1), (0, SH)], wall)
    c.poly([(SW, 0), (bx1, by0), (bx1, by1), (SW, SH)], sh(wall, .95))
    c.poly([(0, 0), (SW, 0), (bx1, by0), (bx0, by0)], (180, 175, 165))
    c.poly([(0, SH), (SW, SH), (bx1, by1), (bx0, by1)], (110, 80, 60))
    c.poly([(560, SH), (1360, SH), (1060, by1), (860, by1)], (120, 40, 45))
    c.rect(bx0, by0, bx1, by1, sh(wall, .85))
    # end door
    c.rect(890, 380, 1030, 700, (110, 85, 70))
    if door_glow:
        c.rect(890, 690, 1030, 700, (255, 230, 150), ol=False)
        c.poly([(880, 700), (1040, 700), (1100, 760), (820, 760)], (180, 150, 100), ol=False)
    # side doors
    for (x0, x1) in ((180, 420), (520, 660)):
        t0 = x0 / bx0
        t1 = x1 / bx0
        c.poly([(x0, 160 + (by0 - 0) * t0 * .3 + 100 * t0), (x1, 160 + 100 * t1 + (by0) * t1 * .3), (x1, SH - (SH - by1) * t1 - 40), (x0, SH - (SH - by1) * t0 - 40)], (100, 75, 60))
    for (x0, x1) in ((1500, 1740), (1260, 1400)):
        t0 = (SW - x0) / (SW - bx1)
        t1 = (SW - x1) / (SW - bx1)
        c.poly([(x0, 160 + 100 * t0 + by0 * t0 * .3), (x1, 160 + 100 * t1 + by0 * t1 * .3), (x1, SH - (SH - by1) * t1 - 40), (x0, SH - (SH - by1) * t0 - 40)], (100, 75, 60))
    frame(c, 930, 300, 990, 360, (200, 200, 190))
    c.ell(930, 40, 990, 80, (255, 240, 200))
    return c.done(), None


def bg_kitchen(empty_chair=False):
    c = Cv()
    c.rect(0, 0, SW, 780, (230, 220, 190), ol=False)
    for x in range(0, SW, 60):
        for y in range(420, 600, 60):
            c.rect(x, y, x + 60, y + 60, (240, 240, 235), w=1)
    c.rect(0, 120, 1100, 380, (150, 180, 170))
    for k in range(5):
        c.rect(k * 220 + 10, 130, k * 220 + 210, 370, (160, 190, 180), w=2)
        c.ell(k * 220 + 190, 330, k * 220 + 200, 340, (90, 90, 90), ol=False)
    c.rect(0, 600, 1100, 780, (150, 180, 170))
    c.rect(0, 590, 1100, 615, (230, 230, 225))
    c.rect(400, 520, 700, 600, (70, 70, 75))
    window(c, 1220, 140, 1600, 460, sky=((230, 200, 150), (250, 230, 190)), curtains=(220, 120, 100))
    c.rect(0, 780, SW, SH, (180, 165, 140), ol=False)
    for x in range(0, SW, 120):
        c.line([(x, 780), (x - 200, SH)], (160, 145, 120), 2)
    # table
    c.rect(1250, 760, 1900, 800, (160, 110, 70))
    c.rect(1280, 800, 1300, 1000, (120, 80, 50))
    c.rect(1850, 800, 1870, 1000, (120, 80, 50))
    if empty_chair:
        c.rect(1050, 600, 1150, 980, (130, 85, 55))
    return c.done(), None


def bg_garage():
    c = Cv()
    c.rect(0, 0, SW, 800, (140, 110, 80), ol=False)
    for x in range(0, SW, 90):
        c.line([(x, 0), (x, 800)], (115, 88, 62), 4)
    c.rect(0, 800, SW, SH, (120, 120, 118), ol=False)
    c.rect(200, 150, 900, 500, (190, 160, 120))
    for x in range(220, 890, 30):
        for y in range(170, 490, 30):
            c.ell(x - 3, y - 3, x + 3, y + 3, (90, 70, 50), ol=False)
    c.line([(300, 220), (300, 400)], (140, 145, 150), 10)
    c.rect(270, 200, 330, 230, (140, 145, 150))
    c.line([(420, 230), (520, 380)], (200, 60, 50), 12)
    c.ell(600, 230, 700, 330, (90, 90, 95), w=4)
    c.line([(780, 200), (780, 420)], (120, 90, 60), 10)
    c.rect(150, 560, 1000, 600, (130, 90, 60))
    c.rect(170, 600, 200, 800, (100, 70, 50))
    c.rect(950, 600, 980, 800, (100, 70, 50))
    # mower
    c.rect(1300, 820, 1560, 900, (60, 130, 70))
    c.line([(1520, 830), (1680, 640)], (60, 60, 60), 8)
    c.ell(1300, 880, 1370, 950, (30, 30, 30))
    c.ell(1490, 880, 1560, 950, (30, 30, 30))
    # bulb
    c.line([(1100, 0), (1100, 120)], OUT, 3)
    c.ell(1080, 115, 1120, 160, (255, 240, 180))
    c.rect(1700, 100, 1900, 700, (180, 180, 170))
    for y in range(140, 700, 80):
        c.line([(1700, y), (1900, y)], (150, 150, 140), 4)
    return c.done(), None


def bg_lake2009(swing=True):
    c = Cv()
    c.grad(0, 0, SW, 520, (130, 190, 230), (200, 230, 240))
    c.ell(1550, 80, 1700, 230, (255, 240, 170), ol=False)
    for k in range(30):
        x = k * 70
        c.ell(x - 50, 430 - (k * 23 % 40), x + 80, 560, (70, 130, 70), ol=False)
    c.rect(0, 520, SW, 700, (80, 140, 180), ol=False)
    for k in range(8):
        c.line([(100 + k * 230, 560 + k * 16), (240 + k * 230, 560 + k * 16)], (140, 190, 220), 3)
    c.rect(0, 680, SW, SH, (110, 170, 80), ol=False)
    c.poly([(0, 680), (SW, 680), (SW, 700), (0, 720)], (200, 190, 140), ol=False)
    # swing frame
    if swing:
        c.line([(420, 1000), (560, 420)], (130, 90, 55), 18)
        c.line([(700, 1000), (560, 420)], (130, 90, 55), 18)
        c.line([(1220, 1000), (1100, 420)], (130, 90, 55), 18)
        c.line([(980, 1000), (1100, 420)], (130, 90, 55), 18)
        c.line([(540, 425), (1120, 425)], (120, 80, 50), 22)
    return c.done(), None


def bg_grave():
    c = Cv()
    c.grad(0, 0, SW, 600, (120, 125, 130), (170, 172, 175))
    c.rect(0, 580, SW, SH, (90, 105, 80), ol=False)
    for k in range(9):
        x = 100 + k * 220
        y = 600 + (k % 2) * 20
        c.poly([(x, y), (x + 70, y), (x + 70, y - 90), (x + 35, y - 115), (x, y - 90)], (130, 130, 135))
    tree_dead(c, 1650, 600, 2.4, (50, 45, 42), 11)
    # headstone
    c.poly([(800, 820), (1120, 820), (1120, 560), (960, 470), (800, 560)], (190, 190, 195), w=4)
    c.text((960, 620), "OUR DAUGHTER", 38, (90, 90, 95, 255))
    c.text((960, 690), "2004 - 2009", 36, (90, 90, 95, 255))
    c.rect(840, 820, 1080, 860, (110, 90, 60))
    # little white casket
    c.poly([(640, 980), (1280, 980), (1240, 900), (680, 900)], (245, 245, 245), w=4)
    c.rect(640, 980, 1280, 1040, (230, 230, 230), w=4)
    c.ell(900, 870, 1020, 930, (230, 120, 140))
    c.ell(930, 860, 990, 900, (250, 200, 210))
    return c.done(), None


def bg_wall(col, corn_wall=False):
    c = Cv()
    if corn_wall:
        c.grad(0, 0, SW, 600, (160, 165, 170), (200, 200, 198))
        corn(c, 1080, 520, 0, SW, col=(140, 130, 80), dense=34, seed=8)
        c.rect(0, 0, 120, SH, (60, 60, 65), ol=False)
        c.rect(1800, 0, SW, SH, (60, 60, 65), ol=False)
        return c.done(), None
    c.grad(0, 0, SW, SH, sh(col, 1.08), sh(col, .82))
    rnd = random.Random(int(sum(col)))
    for k in range(40):
        x = rnd.uniform(0, SW)
        y = rnd.uniform(0, SH)
        c.ell(x - 60, y - 30, x + 60, y + 30, sh(col, rnd.uniform(.94, 1.04)) , ol=False)
    return c.done(), None


def bg_car_int():
    c = Cv()
    # rear window view (moving corn painted separately), car interior
    c.rect(0, 0, SW, SH, (70, 70, 75), ol=False)
    c.poly([(300, 120), (1620, 120), (1700, 420), (220, 420)], (170, 172, 175))
    bg = c.done()
    f = Cv()
    # seats (behind people drawn in bg? we keep seats in bg via separate func)
    # windshield frame
    f.poly([(0, 0), (SW, 0), (SW, 60), (0, 60)], (40, 40, 44), ol=False)
    f.poly([(0, 0), (140, 0), (40, SH), (0, SH)], (40, 40, 44), ol=False)
    f.poly([(SW, 0), (SW - 140, 0), (SW - 40, SH), (SW, SH)], (40, 40, 44), ol=False)
    # dashboard
    f.poly([(0, 900), (SW, 900), (SW, SH), (0, SH)], (50, 50, 55))
    f.poly([(0, 860), (SW, 860), (SW, 910), (0, 910)], (65, 65, 70))
    # steering wheel (driver on right of screen)
    f.ell(1080, 700, 1500, 1120, None, w=26) if False else None
    f.d.ellipse([1080 * K, 720 * K, 1480 * K, 1120 * K], outline=(30, 30, 32), width=34 * K)
    f.d.ellipse([1080 * K, 720 * K, 1480 * K, 1120 * K], outline=OUT, width=4 * K)
    f.line([(1280, 920), (1150, 860)], (30, 30, 32), 24)
    f.line([(1280, 920), (1410, 860)], (30, 30, 32), 24)
    f.ell(1230, 880, 1330, 960, (45, 45, 48))
    # mirror
    f.line([(960, 60), (960, 120)], (30, 30, 32), 12)
    f.rect(820, 110, 1100, 190, (35, 35, 38))
    f.rect(835, 122, 1085, 178, (150, 155, 165), ol=False)
    return bg, f.done()


def car_seats(c, empty_seat=False):
    for x in (640, 1280):
        c.poly([(x - 230, 1080), (x - 210, 430), (x - 150, 370), (x + 150, 370), (x + 210, 430), (x + 230, 1080)], (85, 80, 75))
        c.rect(x - 100, 300, x + 100, 380, (90, 85, 80))
    if empty_seat:
        c.line([(470, 430), (820, 1080)], (25, 25, 28), 22)
        c.ell(800, 1000, 860, 1060, (170, 170, 175))


def bg_fridge():
    c = Cv()
    c.rect(0, 0, SW, SH, (60, 62, 72), ol=False)
    c.rect(560, 40, 1360, 1080, (215, 220, 222), w=5)
    c.line([(560, 420), (1360, 420)], OUT, 5)
    c.rect(600, 140, 630, 360, (180, 185, 190))
    c.rect(600, 470, 630, 800, (180, 185, 190))
    # child's drawing with two girls, one scribbled
    c.poly([(800, 480), (1180, 470), (1190, 760), (810, 770)], (250, 248, 240), w=3)
    for (x, scrib) in ((900, False), (1080, True)):
        c.ell(x - 30, 540, x + 30, 600, None, w=3)
        c.line([(x, 600), (x, 670)], (60, 60, 60), 3)
        c.poly([(x - 40, 690), (x + 40, 690), (x, 620)], (250, 210, 60), w=2)
        c.line([(x - 15, 690), (x - 20, 740)], (60, 60, 60), 3)
        c.line([(x + 15, 690), (x + 20, 740)], (60, 60, 60), 3)
        if scrib:
            rnd = random.Random(3)
            pts = [(x + rnd.uniform(-60, 60), rnd.uniform(520, 720)) for _ in range(40)]
            c.line(pts, (20, 20, 25), 5)
    c.ell(780, 450, 820, 490, (220, 60, 60), ol=False)
    c.ell(1160, 450, 1200, 490, (60, 120, 220), ol=False)
    for (x, y, col) in ((700, 200, (240, 200, 60)), (1100, 250, (120, 200, 120)), (900, 160, (220, 120, 200))):
        c.ell(x, y, x + 50, y + 50, col)
    return c.done(), None


def bg_tv():
    c = Cv()
    c.rect(0, 0, SW, SH, (40, 38, 40), ol=False)
    c.rect(300, 120, 1620, 900, (25, 25, 28), w=6)
    c.rect(340, 160, 1580, 860, (60, 140, 70), ol=False)
    for k in range(11):
        x = 340 + k * 124
        c.line([(x, 160), (x - 60 + k * 12, 860)], (230, 240, 230), 3)
    c.rect(860, 900, 1060, 960, (30, 30, 32))
    c.rect(700, 960, 1220, 990, (30, 30, 32))
    return c.done(), None


def bg_table_top(plates=4):
    c = Cv()
    c.rect(0, 0, SW, SH, (110, 75, 50), ol=False)
    c.rect(140, 160, 1780, 920, (245, 240, 230), w=4)
    pos = [(420, 320), (960, 300), (1500, 320), (420, 760), (960, 780)]
    for i, (x, y) in enumerate(pos):
        if i < plates:
            c.ell(x - 140, y - 110, x + 140, y + 110, (250, 250, 250), w=3)
            c.ell(x - 100, y - 78, x + 100, y + 78, (240, 240, 240), w=2)
            c.rect(x - 200, y - 90, x - 185, y + 90, (190, 190, 195), w=2)
            c.rect(x + 185, y - 90, x + 200, y + 90, (190, 190, 195), w=2)
        else:
            pass
    c.ell(1340, 620, 1640, 860, (190, 120, 60))
    return c.done(), None


def bg_calendar(xmas=False):
    c = Cv()
    c.rect(0, 0, SW, SH, (200, 185, 160), ol=False)
    c.rect(560, 80, 1360, 1000, (250, 248, 240), w=5)
    c.rect(560, 80, 1360, 230, (180, 40, 40) if not xmas else (30, 110, 60), w=5)
    c.text((960, 155), "DECEMBER" if xmas else "NOVEMBER", 72, (255, 255, 255, 255))
    for i in range(35):
        x = 580 + (i % 7) * 110
        y = 250 + (i // 7) * 145
        c.rect(x, y, x + 105, y + 140, (250, 248, 240), w=2)
        day = i - 2
        if 0 < day <= 30:
            c.text((x + 22, y + 22), str(day), 26, (60, 60, 60, 255))
    tgt = 25 if xmas else 27
    i = tgt + 2
    x = 580 + (i % 7) * 110
    y = 250 + (i // 7) * 145
    c.d.ellipse([(x - 8) * K, (y - 6) * K, (x + 113) * K, (y + 146) * K], outline=(220, 30, 30), width=7 * K)
    return c.done(), None


def bg_photowall():
    c = Cv(2400, 1080)
    c.rect(0, 0, 2400, 1080, (205, 180, 150), ol=False)
    rnd = random.Random(12)
    for i in range(16):
        x = 80 + (i % 8) * 290 + rnd.uniform(-20, 20)
        y = 120 + (i // 8) * 420 + rnd.uniform(-30, 30)
        frame(c, x, y, x + 230, y + 300, (190 + rnd.randint(-20, 30), 200, 210 + rnd.randint(-20, 20)), wood=rnd.choice([(120, 80, 50), (40, 40, 40), (220, 210, 190)]))
    return c.done(), None


def bg_floor():
    c = Cv()
    c.rect(0, 0, SW, SH, (95, 75, 60), ol=False)
    for y in range(0, SH, 120):
        c.line([(0, y), (SW, y)], (70, 55, 45), 5)
        off = (y // 120) * 340 % 900
        for x in range(off, SW, 900):
            c.line([(x, y), (x, y + 120)], (70, 55, 45), 4)
    c.poly([(400, 0), (1500, 0), (1700, SH), (200, SH)], (125, 120, 140, 255), ol=False)
    for y in range(0, SH, 120):
        c.line([(300, y), (1600, y)], (100, 95, 110), 5)
    return c.done(), None


def bg_window_dawn():
    c = Cv()
    c.rect(0, 0, SW, SH, (130, 115, 120), ol=False)
    window(c, 560, 140, 1360, 800, sky=((250, 170, 120), (255, 220, 170)), curtains=(80, 70, 100))
    c.rect(560, 640, 1360, 800, (120, 110, 90), ol=False)
    return c.done(), None


def bg_hospital():
    c = Cv()
    c.rect(0, 0, SW, SH, (160, 175, 175), ol=False)
    c.rect(360, 140, 1560, 860, (40, 45, 50), w=8)
    c.rect(400, 180, 1520, 820, (10, 25, 20), ol=False)
    for x in range(400, 1520, 80):
        c.line([(x, 180), (x, 820)], (20, 50, 35), 1)
    for y in range(180, 820, 80):
        c.line([(400, y), (1520, y)], (20, 50, 35), 1)
    c.text((520, 230), "HR", 40, (80, 255, 120, 255))
    return c.done(), None


def bg_fire():
    c = Cv()
    c.grad(0, 0, SW, 700, (110, 110, 120), (170, 160, 150))
    c.rect(0, 700, SW, SH, (90, 85, 70), ol=False)
    c.rect(760, 560, 1160, 1000, (90, 85, 80), w=5)
    for y in (640, 760, 880):
        c.line([(760, y), (1160, y)], (60, 55, 50), 6)
    tree_dead(c, 300, 720, 2.0, (60, 55, 50), 4)
    return c.done(), None


def bg_road():
    c = Cv()
    c.grad(0, 0, SW, 600, (150, 155, 160), (200, 200, 198))
    return c.done(), None


def bg_hands():
    c = Cv()
    c.rect(0, 0, SW, SH, (55, 55, 60), ol=False)
    c.d.ellipse([200 * K, -200 * K, 1900 * K, 1500 * K], outline=(28, 28, 30), width=120 * K)
    return c.done(), None


BUILDERS = {
    "apt": lambda a: bg_apt(False, False),
    "apt_night": lambda a: bg_apt(True, False),
    "party": lambda a: bg_apt(False, True),
    "class": lambda a: bg_class(),
    "notebook": lambda a: bg_notebook(),
    "farm_ext": lambda a: bg_farm(False, a.get("car") if a.get("car") == "parked" else None),
    "farm_xmas": lambda a: bg_farm(True),
    "lake": lambda a: bg_lake(a.get("night", False) or "night" in a.get("fx", []), a.get("toys", False)),
    "frontdoor": lambda a: bg_frontdoor(a.get("xmas", False)),
    "dining": lambda a: bg_dining(False, tuple(a.get("props", []))),
    "dining_xmas": lambda a: bg_dining(True, tuple(a.get("props", []))),
    "living": lambda a: bg_living(a.get("xmas", False)),
    "porch": lambda a: bg_porch(),
    "guest": lambda a: bg_guest(a.get("puddle", False)),
    "hall": lambda a: bg_hall(a.get("door_glow", False)),
    "kitchen": lambda a: bg_kitchen(a.get("empty_chair", False)),
    "garage": lambda a: bg_garage(),
    "lake2009": lambda a: bg_lake2009(),
    "grave": lambda a: bg_grave(),
    "face": lambda a: bg_wall(tuple(a.get("wall", (120, 110, 100))), a.get("corn_wall", False)),
    "car_int": lambda a: bg_car_int(),
    "fridge": lambda a: bg_fridge(),
    "tv": lambda a: bg_tv(),
    "table_top": lambda a: bg_table_top(a.get("plates", 4)),
    "calendar": lambda a: bg_calendar(a.get("xmas", False)),
    "photowall": lambda a: bg_photowall(),
    "floor_drip": lambda a: bg_floor(),
    "window_dawn": lambda a: bg_window_dawn(),
    "hospital": lambda a: bg_hospital(),
    "fire": lambda a: bg_fire(),
    "road": lambda a: bg_road(),
    "hands": lambda a: bg_hands(),
}
