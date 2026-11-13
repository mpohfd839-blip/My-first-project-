"""Scenes for the pictogram / spotlight style. Content canvas is CW x CH."""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from picto import draw_person, draw_dog, make_pose, WHITE, BACK, LINE, DARK

CW, CH = 1920, 860
FY = 700
K = 2
W3 = (238, 236, 230)
GRAY = (150, 148, 144)
YEL = (245, 215, 90)
RED = (215, 35, 40)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FXB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FH = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"


@functools.lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, int(size))


class Pr:
    """Prop canvas drawn at 2x."""
    def __init__(self, w=CW, h=CH):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x0, y0, x1, y1, c=W3, r=0):
        if r:
            self.d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], int(r * K), fill=c)
        else:
            self.d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=c)

    def poly(self, pts, c=W3):
        self.d.polygon([(x * K, y * K) for x, y in pts], fill=c)

    def ell(self, x0, y0, x1, y1, c=W3, outline=None, w=0):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=c, outline=outline, width=int(w * K))

    def line(self, pts, c=GRAY, w=3):
        self.d.line([(x * K, y * K) for x, y in pts], fill=c, width=int(w * K), joint="curve")

    def text(self, xy, s, size, c, f=FB, anchor="mm"):
        self.d.text((xy[0] * K, xy[1] * K), s, font=font(f, size * K), fill=c, anchor=anchor)

    def done(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


@functools.lru_cache(maxsize=16)
def glow(cx=.5, cy=.42, rx=.55, ry=.75, col=(205, 190, 155), base=(8, 7, 7)):
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    r = np.sqrt(((xx / CW - cx) / rx) ** 2 + ((yy / CH - cy) / ry) ** 2)
    k = np.clip(1 - r, 0, 1) ** 1.6
    out = np.array(base, np.float32) + (np.array(col, np.float32) - np.array(base, np.float32)) * k[..., None]
    return Image.fromarray(out.astype(np.uint8))


def cast_shadow(img_rgb, layer, lx, fy=FY, scale=1.45, alpha=0.78, blur=7, offset=(0, 0)):
    """Darken img_rgb with an enlarged blurred shadow of layer (RGBA) projected from (lx, fy)."""
    a = layer.getchannel("A")
    w, h = a.size
    nw, nh = int(w * scale), int(h * scale)
    a2 = a.resize((nw, nh), Image.BILINEAR)
    sh = Image.new("L", (CW, CH), 0)
    ox = int(lx - lx * scale + offset[0])
    oy = int(fy - fy * scale + offset[1])
    sh.paste(a2, (ox, oy))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    # only on wall (above floor)
    m = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(m).rectangle([0, 0, CW, fy], fill=255)
    sh = ImageChops.multiply(sh, m)
    dark = Image.new("RGB", (CW, CH), (14, 12, 11))
    return Image.composite(dark, img_rgb, sh)


def floorline(p, y=FY):
    p.rect(0, y, CW, y + 5, W3)


def window(p, x0, y0, x1, y1, frame=W3):
    p.rect(x0 - 12, y0 - 12, x1 + 12, y1 + 12, frame)
    p.rect(x0, y0, x1, y1, (12, 12, 16))
    p.rect((x0 + x1) / 2 - 4, y0, (x0 + x1) / 2 + 4, y1, frame)
    p.rect(x0, (y0 + y1) / 2 - 4, x1, (y0 + y1) / 2 + 4, frame)


def lamp(p, x, y, on=True):
    p.rect(x - 5, y - 150, x + 5, y, W3)
    p.ell(x - 40, y - 8, x + 40, y + 6, W3)
    p.poly([(x - 48, y - 150), (x + 48, y - 150), (x + 32, y - 215), (x - 32, y - 215)], YEL if on else W3)


def hanging_lamp(p, x, y=180):
    p.rect(x - 3, 0, x + 3, y, W3)
    p.poly([(x - 80, y + 70), (x + 80, y + 70), (x + 26, y), (x - 26, y)], W3)
    p.rect(x - 60, y + 70, x + 60, y + 76, YEL)


def corn_row(p, y_base, x0, x1, hgt, col, seed=1, step=26):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        h = hgt * rnd.uniform(.75, 1.0)
        p.line([(x, y_base), (x + rnd.uniform(-5, 5), y_base - h)], col, 4)
        for k in range(3):
            yy = y_base - h * rnd.uniform(.35, .9)
            p.line([(x, yy), (x + rnd.choice([-1, 1]) * rnd.uniform(14, 26), yy - rnd.uniform(-6, 12))], col, 3)
        x += step * rnd.uniform(.7, 1.2)


def farmhouse(p, x, y, s=1.0, lit=True, lights_off=False):
    w, h = 560 * s, 300 * s
    p.poly([(x - w / 2 - 30 * s, y - h), (x + w / 2 + 30 * s, y - h), (x + w * .28, y - h - 180 * s), (x - w * .28, y - h - 180 * s)], W3)
    p.rect(x - w / 2, y - h, x + w / 2, y, W3)
    p.rect(x + w * .2, y - h - 230 * s, x + w * .2 + 40 * s, y - h - 100 * s, W3)
    rnd = random.Random(2)
    for k in range(14):
        xx = x - w / 2 + rnd.uniform(0, w)
        yy = y - h + rnd.uniform(10, h - 30)
        p.line([(xx, yy), (xx + rnd.uniform(10, 30) * s, yy + rnd.uniform(-4, 8) * s)], (190, 188, 182), 2)
    for i, wx in enumerate((-.34, -.12, .12, .34)):
        for j, wy in enumerate((-.78, -.38)):
            X, Y = x + w * wx, y + h * wy
            if wx == .12 and wy == -.38:
                continue
            c = YEL if lit and not (lights_off and (i + j) % 3) else (25, 25, 30)
            p.rect(X - 28 * s, Y - 38 * s, X + 28 * s, Y + 38 * s, c)
            p.rect(X - 2 * s, Y - 38 * s, X + 2 * s, Y + 38 * s, W3)
    p.rect(x + w * .12 - 30 * s, y - 120 * s, x + w * .12 + 30 * s, y, (20, 20, 24))
    p.rect(x - w / 2 - 20 * s, y - 150 * s, x + w / 2 + 20 * s, y - 140 * s, W3)
    for k in range(7):
        X = x - w / 2 + k * w / 6
        p.rect(X - 4 * s, y - 140 * s, X + 4 * s, y, W3)


def car(p, x, y, s=1.0, lights=None):
    p.poly([(x - 170 * s, y - 25 * s), (x - 160 * s, y - 70 * s), (x - 80 * s, y - 78 * s), (x - 40 * s, y - 120 * s), (x + 60 * s, y - 120 * s), (x + 100 * s, y - 78 * s), (x + 170 * s, y - 68 * s), (x + 175 * s, y - 25 * s)], W3)
    p.poly([(x - 70 * s, y - 80 * s), (x - 35 * s, y - 112 * s), (x + 5 * s, y - 112 * s), (x + 5 * s, y - 80 * s)], (25, 25, 30))
    p.poly([(x + 15 * s, y - 80 * s), (x + 15 * s, y - 112 * s), (x + 55 * s, y - 112 * s), (x + 88 * s, y - 80 * s)], (25, 25, 30))
    for wx in (-100, 110):
        p.ell(x + wx * s - 30 * s, y - 55 * s, x + wx * s + 30 * s, y + 5 * s, (25, 25, 28))
        p.ell(x + wx * s - 16 * s, y - 41 * s, x + wx * s + 16 * s, y - 9 * s, W3)
    if lights == "tail":
        p.rect(x - 175 * s, y - 62 * s, x - 162 * s, y - 45 * s, RED)
    elif lights == "head":
        p.rect(x + 165 * s, y - 62 * s, x + 178 * s, y - 45 * s, YEL)


# ------------------------------------------------------------------ static scenes
def sc_house(a):
    p = Pr()
    corn_row(p, FY - 20, 0, 640, 170, (120, 118, 112), 1)
    corn_row(p, FY - 20, 1300, CW, 170, (120, 118, 112), 4)
    farmhouse(p, 960, FY, 1.0, lit=not a.get("morning"), lights_off=a.get("lights_off"))
    # mailbox (crooked)
    p.line([(470, FY), (485, FY - 110)], W3, 8)
    p.poly([(440, FY - 140), (520, FY - 128), (515, FY - 95), (436, FY - 105)], W3)
    # gravel road
    for k in range(60):
        rnd = random.Random(k)
        x = 480 + rnd.uniform(0, 520)
        y = FY + 10 + rnd.uniform(0, 140)
        p.ell(x - 4, y - 2, x + 4, y + 2, (120, 118, 112))
    floorline(p)
    if a.get("car") == "parked":
        car(p, 650, FY, 0.9)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.38, rx=.6, ry=.9, col=(196, 176, 140) if a.get("dusk") else ((160, 168, 182) if a.get("night") else (205, 190, 160))), lx=960)


def sc_photos(a):
    p = Pr()
    if a.get("grandma"):
        p.rect(760, 130, 1160, 620, W3)
        p.rect(790, 160, 1130, 590, (30, 28, 26))
        g, ox, oy = draw_person("grandma", dict(make_pose(dict(anim="smile"), 0, 5, 1)), 4.2)
        p.img.alpha_composite(g.resize((g.width * K, g.height * K)), (int((960 - ox) * K), int((640 - oy) * K)))
        p.text((960, 660), "GRANDMA  1938 - 2021", 26, GRAY)
        for x in (700, 1220):
            p.ell(x - 30, 560, x + 30, 620, W3)
            p.line([(x, 620), (x, FY)], W3, 6)
    else:
        for i, (x, lab) in enumerate(((420, "1921"), (960, "GRANDMA"), (1500, "MOM"))):
            p.rect(x - 170, 170, x + 170, 560, W3)
            p.rect(x - 150, 190, x + 150, 540, (30, 28, 26))
            p.text((x, 600), lab, 30, GRAY)
            if i == 0:
                farmhouse(p, x, 500, 0.42)
            else:
                nm = "grandma" if i == 1 else "kidmom"
                g, ox, oy = draw_person(nm, make_pose(dict(anim="smile"), 0, 5, i), 2.6 if i == 1 else 2.9)
                p.img.alpha_composite(g.resize((g.width * K, g.height * K)), (int((x - ox) * K), int((540 - oy) * K)))
    floorline(p)
    return dict(props=p.done(), glow=dict(cy=.4), lx=960)


def sc_kitchen(a):
    p = Pr()
    # window
    window(p, 300, 190, 620, 470)
    # counter + cabinets left
    p.rect(0, 520, 260, FY, W3)
    p.rect(20, 160, 250, 330, W3)
    p.line([(135, 160), (135, 330)], GRAY, 3)
    # fridge
    p.rect(1260, 170, 1500, FY, W3, r=14)
    p.line([(1260, 380), (1500, 380)], GRAY, 4)
    p.rect(1280, 220, 1292, 340, GRAY)
    p.rect(1280, 410, 1292, 560, GRAY)
    p.rect(1350, 220, 1460, 350, (250, 250, 245))
    for k in range(5):
        p.line([(1362, 250 + k * 18), (1448, 250 + k * 18)], GRAY, 3)
    p.ell(1394, 204, 1416, 228, RED)
    hanging_lamp(p, 900, 170)
    # table
    p.rect(760, 520, 1100, 540, W3)
    p.rect(780, 540, 796, FY, W3)
    p.rect(1064, 540, 1080, FY, W3)
    p.rect(1120, 470, 1132, FY, W3)
    p.rect(1120, 560, 1180, 572, W3)
    p.rect(1170, 560, 1180, FY, W3)
    if a.get("wallphone"):
        p.rect(700, 300, 760, 410, (225, 215, 190), r=8)
        p.rect(706, 300, 754, 330, (210, 200, 175), r=8)
        for k in range(10):
            p.ell(726 + (k % 2) * 6, 410 + k * 12, 738 + (k % 2) * 6, 422 + k * 12, None, (210, 200, 175), 3)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.47, cy=.36), lx=900)


def sc_living(a):
    p = Pr()
    for x in (180, 1180, 1500):
        window(p, x, 200, x + 220, 440)
    lamp(p, 330, FY)
    # couch
    p.rect(560, 470, 1040, 610, W3, r=26)
    p.rect(520, 520, 600, FY - 30, W3, r=20)
    p.rect(1000, 520, 1080, FY - 30, W3, r=20)
    p.rect(580, 600, 1020, FY - 30, W3, r=12)
    p.line([(720, 480), (720, 600)], GRAY, 3)
    p.line([(880, 480), (880, 600)], GRAY, 3)
    p.rect(560, FY - 30, 580, FY, W3)
    p.rect(1020, FY - 30, 1040, FY, W3)
    # tv
    p.rect(1260, 560, 1440, FY, W3)
    p.rect(1230, 420, 1470, 560, W3, r=8)
    p.rect(1244, 434, 1456, 546, (20, 20, 24))
    # cuckoo clock
    p.poly([(820, 250), (900, 190), (980, 250)], W3)
    p.rect(835, 250, 965, 360, W3)
    p.ell(865, 270, 935, 340, (25, 25, 28))
    # stairs edge
    for k in range(6):
        p.rect(1700 + k * 40, FY - (k + 1) * 50, CW, FY - k * 50, W3)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.45, cy=.4), lx=800)


def sc_laundry(a):
    p = Pr()
    p.rect(980, 300, 1320, 640, (12, 12, 16))
    p.rect(960, 280, 1340, 300, W3)
    p.rect(960, 640, 1340, 660, W3)
    p.rect(960, 280, 980, 660, W3)
    p.rect(1320, 280, 1340, 660, W3)
    p.rect(1150, 220, 1170, 240, W3)
    p.rect(940, 228, 1360, 236, W3)
    # washer
    p.rect(300, 460, 560, FY, W3, r=10)
    p.ell(355, 520, 505, 670, (30, 30, 34))
    p.ell(380, 545, 480, 645, (50, 50, 55))
    p.rect(320, 475, 540, 500, (220, 218, 212))
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.42), lx=700)


def sc_backdoor(a):
    p = Pr()
    if a.get("wide"):
        x0, x1, y0 = 1020, 1380, 170
    else:
        x0, x1, y0 = 700, 1220, 60
    p.rect(x0 - 24, y0 - 24, x1 + 24, FY, W3)
    p.rect(x0, y0, x1, FY, (225, 223, 217))
    wy1 = y0 + (x1 - x0) * 0.62
    p.rect(x0 + 40, y0 + 40, x1 - 40, wy1, (40, 38, 36))
    p.ell(x1 - 70, wy1 + 120, x1 - 34, wy1 + 156, GRAY)
    p.rect(x0 + 40, wy1 + 40, x1 - 40, wy1 + 46, GRAY)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.45, cy=.4), lx=700, win=(x0 + 40, y0 + 40, x1 - 40, wy1))


def sc_porch_out(a):
    p = Pr()
    p.rect(0, 120, CW, FY, (205, 203, 197))
    for k in range(14):
        p.line([(0, 140 + k * 40), (CW, 140 + k * 40)], (185, 183, 177), 2)
    for x in (380, 1100):
        p.rect(x, 220, x + 300, 470, (28, 26, 24))
        p.rect(x + 10, 230, x + 290, 460, (230, 215, 170))
    p.rect(0, FY - 10, CW, FY + 20, W3)
    for k in range(20):
        p.rect(k * 100, FY - 140, k * 100 + 10, FY, W3)
    p.rect(0, FY - 150, CW, FY - 138, W3)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.5, col=(150, 155, 170)), lx=960, noshadow=True)


def sc_house_cut(a):
    p = Pr()
    x0, x1, y0, y1 = 420, 1500, 140, FY
    mid = (y0 + y1) / 2
    p.poly([(x0 - 40, y0), (x1 + 40, y0), (960, y0 - 110)], None) if False else None
    for pts in ([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], [(x0 - 40, y0), (960, y0 - 120), (x1 + 40, y0)],
                [(x0, mid), (x1, mid)], [(780, mid), (780, y1)], [(1180, mid), (1180, y1)], [(960, y0), (960, mid)]):
        p.line(pts, W3, 8)
    for wx in (500, 900, 1300):
        p.rect(wx, mid + 60, wx + 90, mid + 150, (60, 58, 54))
    for wx in (540, 1240):
        p.rect(wx, y0 + 60, wx + 90, y0 + 150, (60, 58, 54))
    p.text((600, y1 - 20), "KITCHEN", 24, GRAY)
    p.text((980, y1 - 20), "LIVING ROOM", 24, GRAY)
    p.text((1340, y1 - 20), "LAUNDRY", 24, GRAY)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.45), lx=960, floor=y1 - 40, amul=0.6, noshadow=True)


def sc_cornfield(a):
    p = Pr()
    for r_, (yb, h, col) in enumerate(((560, 260, (70, 68, 64)), (630, 300, (110, 108, 102)), (FY, 360, (190, 188, 182)))):
        corn_row(p, yb, 0, CW, h, col, seed=r_ + 3, step=22 + r_ * 6)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.3, col=(140, 148, 165)), lx=960, noshadow=True)


def sc_stairs(a):
    p = Pr()
    n = 15
    for k in range(n):
        x = 300 + k * 85
        y = FY - k * 38
        c = W3 if k < 14 else (90, 30, 30)
        if k == 14 and not a.get("extra"):
            continue
        p.rect(x, y - 38, x + 85, y, c)
        p.rect(x, y - 38, CW if k == n - 1 else x + 85, y - 34, W3 if k < 14 else RED)
    p.rect(300 + 14 * 85, FY - 14 * 38 - 4, CW, FY - 14 * 38, W3)
    p.line([(320, FY - 140), (300 + 14 * 85, FY - 14 * 38 - 140)], W3, 6)
    for k in range(0, 15, 2):
        x = 320 + k * 85
        p.line([(x, FY - k * 38 - 38), (x, FY - k * 38 - 38 - 102)], W3, 3)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.55, cy=.4), lx=800)


def stair_pos(step):
    return 300 + step * 85 - 20, FY - step * 38


def sc_hall(a, long=True):
    p = Pr()
    vx, vy = 960, 360
    n = 18 if long else 4
    dep = 0.93 if long else 0.6
    for k in range(n):
        t0 = k / n
        t1 = (k + 1) / n
        s0 = 1 - dep * t0 ** 0.6
        s1 = 1 - dep * t1 ** 0.6
        for side in (-1, 1):
            xa, xb = vx + side * 900 * s0, vx + side * 900 * s1
            ya0, ya1 = vy - 420 * s0, vy + 340 * s0
            yb0, yb1 = vy - 420 * s1, vy + 340 * s1
            if k % 2 == 0:
                p.poly([(xa, ya0 + 140 * s0), (xb, yb0 + 140 * s1), (xb, yb1), (xa, ya1)], (205, 203, 197))
            p.line([(xa, ya1), (xb, yb1)], W3, 4 * s0 + 1)
    s = 1 - dep
    p.rect(vx - 70 * s * 3, vy - 140 * s * 3 + 30, vx + 70 * s * 3, vy + 340 * s, (30, 28, 26))
    if a.get("door_open"):
        p.rect(vx - 45 * s * 3, vy - 110 * s * 3 + 30, vx + 45 * s * 3, vy + 340 * s, (250, 225, 160))
    p.line([(0, vy + 340), (vx, vy + 340 * s)], W3, 5)
    p.line([(CW, vy + 340), (vx, vy + 340 * s)], W3, 5)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.42, rx=.7), lx=960, noshadow=True)


def sc_wallphone(a):
    p = Pr()
    p.rect(820, 120, 1100, 560, (225, 215, 190), r=30)
    p.rect(840, 110, 1080, 220, (212, 202, 178), r=40)
    for r_ in range(4):
        for c in range(3):
            p.ell(895 + c * 50, 290 + r_ * 55, 925 + c * 50, 320 + r_ * 55, (200, 190, 165))
    for k in range(16):
        p.ell(920 + (k % 2) * 14, 560 + k * 9, 950 + (k % 2) * 14, 590 + k * 9, None, (212, 202, 178), 5)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.4), lx=960, noshadow=True)


def sc_curtains(a):
    p = Pr()
    return dict(props=p.done(), glow=dict(cx=.5, cy=.45, rx=.5, ry=.7, col=(150, 145, 140)), lx=960, noshadow=True)


def sc_cuckoo(a):
    p = Pr()
    p.poly([(700, 230), (960, 60), (1220, 230)], W3)
    p.rect(740, 230, 1180, 640, W3)
    p.ell(820, 300, 1100, 580, (25, 25, 28))
    for k in range(12):
        ang = k * math.pi / 6
        p.line([(960 + math.cos(ang) * 120, 440 + math.sin(ang) * 120), (960 + math.cos(ang) * 135, 440 + math.sin(ang) * 135)], W3, 6)
    p.rect(920, 120, 1000, 200, (25, 25, 28))
    return dict(props=p.done(), glow=dict(cx=.5, cy=.4), lx=960, noshadow=True)


def sc_yard(a):
    p = Pr()
    p.rect(0, 380, CW, CH, (230, 232, 238))
    corn_row(p, 390, 0, CW, 200, (120, 110, 100), seed=6)
    farmhouse(p, 1700, 420, 0.5, lit=False)
    return dict(props=p.done(), glow=dict(cx=.5, cy=.2, rx=.8, ry=.6, col=(250, 190, 160)), lx=960, noshadow=True)


def sc_memory(a):
    p = Pr()
    p.rect(400, 470, 1000, 610, W3, r=26)
    p.rect(420, 600, 980, FY - 30, W3, r=12)
    lamp(p, 260, FY)
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.45, cy=.4, col=(215, 190, 150)), lx=700)


def sc_future(a):
    p = Pr()
    hanging_lamp(p, 900, 140)
    p.rect(560, 520, 1180, 540, W3)
    p.rect(580, 540, 596, FY, W3)
    p.rect(1144, 540, 1160, FY, W3)
    p.rect(820, 505, 900, 520, (250, 250, 245))
    floorline(p)
    return dict(props=p.done(), glow=dict(cx=.45, cy=.38, col=(210, 190, 150)), lx=900)


def sc_blank(a):
    return dict(props=Image.new("RGBA", (CW, CH), (0, 0, 0, 0)), glow=None, lx=960, noshadow=True)


BUILD = {
    "house": sc_house, "photos": sc_photos, "kitchen": sc_kitchen, "living": sc_living, "laundry": sc_laundry,
    "backdoor": sc_backdoor, "porch_out": sc_porch_out, "house_cut": sc_house_cut, "cornfield": sc_cornfield,
    "stairs": sc_stairs, "hall_long": lambda a: sc_hall(a, True), "hall_short": lambda a: sc_hall(a, False),
    "wallphone": sc_wallphone, "curtains": sc_curtains, "cuckoo": sc_cuckoo, "yard": sc_yard,
    "memory": sc_memory, "future": sc_future,
}
TEXT_SCENES = ("rulecard", "title", "endcard", "list", "oldlist", "newlist", "phone", "clockcard")


@functools.lru_cache(maxsize=24)
def base_scene(name, key):
    import json
    a = json.loads(key)
    b = BUILD[name](a)
    g = b["glow"]
    bg = glow(**g) if g else Image.new("RGB", (CW, CH), (8, 7, 7))
    props = b["props"]
    if not b.get("noshadow"):
        bg = cast_shadow(bg, props, b["lx"], b.get("floor", FY), scale=1.35, alpha=0.7, blur=10)
    bg = bg.convert("RGBA")
    bg.alpha_composite(props)
    return bg, b


# ------------------------------------------------------------------ dynamic painters
def curtain_pair(d, x0, y0, x1, y1, k, col=W3):
    """k: 0 open .. 1 closed."""
    w = (x1 - x0) / 2
    cw = 30 + (w - 30) * k
    for side in (0, 1):
        if side == 0:
            xa, xb = x0 - 20, x0 + cw
        else:
            xa, xb = x1 - cw, x1 + 20
        d.rectangle([xa, y0 - 30, xb, y1 + 30], fill=col)
        for j in range(1, 5):
            xx = xa + (xb - xa) * j / 5
            d.line([(xx, y0 - 20), (xx, y1 + 20)], fill=(205, 203, 197), width=3)
    d.rectangle([x0 - 50, y0 - 46, x1 + 50, y0 - 34], fill=W3)


def curtain_k(spec, t, dur, idx=0, total=1):
    c = spec.get("curtain")
    if c in (None, "open"):
        return 0.0
    if c == "closed":
        return 1.0
    if c == "closing":
        return min(1, t / 1.0)
    if c == "slam":
        return min(1, t / 0.2)
    if c == "opening":
        return 1 - min(1, t / 1.2)
    if c == "closing_all":
        start = dur * idx / total
        return min(1, max(0, (t - start) / 0.8))
    return 0.0


def paint_dynamic(name, img, spec, t, dur, b):
    d = ImageDraw.Draw(img)
    if name == "kitchen":
        if spec.get("outside") or spec.get("sunrise"):
            if spec.get("sunrise"):
                d.rectangle([300, 190, 620, 470], fill=(250, 170, 130))
                d.rectangle([300, 330, 620, 470], fill=(235, 238, 245))
            else:
                d.ellipse([360, 380, 560, 450], fill=(120, 105, 50))
                for k in range(8):
                    x = 310 + k * 40
                    d.line([(x, 470), (x + 3, 300 + (k * 13) % 50)], fill=(60, 58, 54), width=4)
            d.rectangle([456, 190, 464, 470], fill=W3)
            d.rectangle([300, 326, 620, 334], fill=W3)
        if spec.get("dawnedge"):
            d.rectangle([296, 180, 306, 480], fill=(240, 200, 170))
            d.rectangle([614, 180, 624, 480], fill=(240, 200, 170))
        curtain_pair(d, 300, 190, 620, 470, curtain_k(spec, t, dur))
        if spec.get("ringing") and (t % 0.8) < 0.4:
            for r in (40, 70):
                d.arc([730 - r, 355 - r, 730 + r, 355 + r], -60, 60, fill=W3, width=4)
        if spec.get("flick2"):
            if (0.6 < t < 0.8) or (1.1 < t < 1.3):
                ov = Image.new("RGBA", img.size, (0, 0, 0, 170))
                img.alpha_composite(ov)
    if name == "living":
        for i, x in enumerate((180, 1180, 1500)):
            k = curtain_k(spec, t, dur, i, 3)
            curtain_pair(d, x, 200, x + 220, 440, k)
        if spec.get("tv"):
            r = random.Random(int(t * 8))
            c = (90 + r.randint(0, 60), 110 + r.randint(0, 60), 160 + r.randint(0, 60))
            d.rectangle([1244, 434, 1456, 546], fill=c)
        if spec.get("taps"):
            for k in range(6):
                ph = (t * 1.7 + k * 0.37) % 1
                x = [290, 1290, 1610, 290, 1290, 1610][k] + (k * 37 % 60) - 30
                y = 260 + (k * 53 % 120)
                if ph < 0.3:
                    r = 10 + ph * 80
                    d.ellipse([x - r, y - r, x + r, y + r], outline=W3, width=3)
    if name == "laundry":
        refl = spec.get("refl")
        if refl:
            a = dict(anim="reach", face=-1)
            pp = make_pose(a, 5.0, 5, 3)
            if refl in ("wave", "smile"):
                pp["aR"] = (150, -15 + 25 * math.sin(t * 7))
                pp["aL"] = (20, 0)
            if refl == "smile":
                pp["smile"] = True
            im, ox, oy = draw_person("kid", pp, 3.0)
            r_ = Image.new("RGBA", img.size, (0, 0, 0, 0))
            r_.alpha_composite(im, (int(1150 - ox), int(760 - oy)))
            r_.putalpha(r_.getchannel("A").point(lambda v: int(v * 0.42)))
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).rectangle([980, 300, 1320, 640], fill=255)
            img.paste(r_, (0, 0), ImageChops.multiply(r_.getchannel("A"), mask))
            if refl == "smile":
                hx, hy = 1150, 760 - 3.0 * 100 + 30
                d.arc([hx - 40, 380, hx + 40, 440], 15, 165, fill=(250, 250, 250), width=7)
            d.rectangle([1150, 300, 1158, 640], fill=W3)
            d.rectangle([980, 466, 1320, 474], fill=W3)
        c = spec.get("curtain")
        if c:
            k = curtain_k(spec, t, dur)
            curtain_pair(d, 980, 300, 1320, 640, k)
        if spec.get("tapfx") and 0.2 < t < 0.6:
            r = 20 + (t - 0.2) * 300
            d.ellipse([1150 - r, 470 - r, 1150 + r, 470 + r], outline=W3, width=4)
    if name == "backdoor":
        wx0, wy0, wx1, wy1 = b["win"]
        shp = spec.get("dogshape")
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        cx = (wx0 + wx1) / 2
        if shp == "dog":
            wag = math.sin(t * 14) * 25 if spec.get("wag") else 0
            ld.ellipse([cx - 120, wy1 - 120, cx + 100, wy1 + 20], fill=(200, 160, 80, 255))
            ld.ellipse([cx + 40, wy1 - 210, cx + 150, wy1 - 100], fill=(200, 160, 80, 255))
            ld.line([(cx - 110, wy1 - 80), (cx - 190, wy1 - 150 + wag)], fill=(200, 160, 80, 255), width=26)
            if spec.get("scratchfx"):
                ph = (t * 6) % 1
                ld.line([(cx + 110, wy1 - 60 - ph * 60), (cx + 140, wy1 - ph * 60)], fill=(200, 160, 80, 255), width=22)
        elif shp in ("rise", "stand"):
            k = 1.0 if shp == "stand" else min(1, t / max(1.0, dur * 0.7))
            top = wy1 - 160 - (wy1 - wy0 + 300) * k
            ld.ellipse([cx - 70, top, cx + 70, top + 140], fill=(15, 12, 10, 255))
            ld.rectangle([cx - 80, top + 120, cx + 80, wy1 + 200], fill=(15, 12, 10, 255))
            ld.line([(cx - 80, top + 160), (cx - 160, top + 380)], fill=(15, 12, 10, 255), width=30)
            ld.line([(cx + 80, top + 160), (cx + 170, top + 360)], fill=(15, 12, 10, 255), width=30)
        layer = layer.filter(ImageFilter.GaussianBlur(14))
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).rectangle([wx0, wy0, wx1, wy1], fill=255)
        frost = Image.new("RGBA", img.size, (0, 0, 0, 0))
        frost.alpha_composite(layer)
        img.paste(frost, (0, 0), ImageChops.multiply(frost.getchannel("A"), mask))
        if shp in ("rise", "stand"):
            k = 1.0 if shp == "stand" else min(1, t / max(1.0, dur * 0.7))
            if k > 0.6:
                # shadow spilling over the door top / wall
                sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(sh).ellipse([cx - 90, wy0 - 260 * (k - .6) / .4 - 120, cx + 90, wy0 + 40], fill=(10, 9, 8, int(210 * (k - .6) / .4)))
                img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
        # frost texture
        fr = Image.new("RGBA", img.size, (0, 0, 0, 0))
        fd = ImageDraw.Draw(fr)
        fd.rectangle([wx0, wy0, wx1, wy1], fill=(220, 225, 235, 40))
        rnd = random.Random(3)
        for k in range(160):
            x, y = rnd.uniform(wx0, wx1), rnd.uniform(wy0, wy1)
            r = rnd.uniform(4, 14)
            fd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 22))
        img.alpha_composite(fr)
    if name == "porch_out" and spec.get("walker"):
        x = 1800 - min(1, t / max(1, dur)) * 1700
        creature(d, x, FY - 10, 1.0, t)
    if name == "house_cut":
        x0, x1, y0, y1 = 420, 1500, 140, FY
        per = [(x0, y1), (x0, y0), (x1, y0), (x1, y1)]
        if spec.get("scrape") or spec.get("tapwin"):
            L = 2 * ((x1 - x0) + (y1 - y0))
            pos = (t / max(1, dur)) * L * 0.9
            seg = [(x0 - 30, y1, x0 - 30, y0), (x0 - 30, y0 - 30, x1 + 30, y0 - 30), (x1 + 30, y0, x1 + 30, y1)]
            acc = 0
            hx = hy = None
            trail = []
            for (ax, ay, bx, by) in seg:
                sl = math.hypot(bx - ax, by - ay)
                if pos <= acc + sl:
                    k = (pos - acc) / sl
                    hx, hy = ax + (bx - ax) * k, ay + (by - ay) * k
                    trail.append(((ax, ay), (hx, hy)))
                    break
                trail.append(((ax, ay), (bx, by)))
                acc += sl
            for (pa, pb) in trail:
                for j in range(3):
                    d.line([(pa[0] + j * 8, pa[1] + j * 8), (pb[0] + j * 8, pb[1] + j * 8)], fill=(90, 30, 30), width=3)
            if hx is not None:
                creature(d, hx, hy + 140, 0.5, t, black=True)
            if spec.get("tapwin"):
                for (wx, wy) in ((500, (y0 + y1) / 2 + 60), (900, (y0 + y1) / 2 + 60), (1300, (y0 + y1) / 2 + 60)):
                    if abs(hx - wx) < 140 if hx is not None else False:
                        d.rectangle([wx, wy, wx + 90, wy + 90], fill=(245, 245, 240))
        if spec.get("alive"):
            k = 0.5 + 0.5 * math.sin(t * 9)
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle([x0, y0, x1, y1], fill=(255, 220, 120, int(60 + 80 * k)))
            img.alpha_composite(ov)
            for k2 in range(8):
                xx = x0 + (k2 * 150 + t * 400) % (x1 - x0)
                d.line([(xx, y1 + 10), (xx + 60, y1 + 10)], fill=YEL, width=6)
        if spec.get("pipes"):
            for j, (px, py) in enumerate(((700, y0 + 20), (1250, y0 + 20))):
                on = (t % 2) < 0.3 or 0.6 < (t % 2) < 0.9
                d.line([(px, py), (px, y1 - 10)], fill=YEL if on else (90, 88, 84), width=10)
    if name == "cornfield" and spec.get("walker_away"):
        k = min(1, t / max(1, dur))
        creature(d, 960 + 200 * k, FY - 40 - 180 * k, 1.0 - 0.75 * k, t, black=True)
    if name == "stairs":
        c0, c1 = spec.get("count", (0, 0))
        k = min(1, t / max(1, dur * 0.95))
        cur = int(round(c0 + (c1 - c0) * k))
        if cur > 0:
            x, y = stair_pos(min(cur, 15) - 1)
            col = RED if cur >= 15 else W3
            d.text((x + 40, y - 120), str(cur), font=font(FXB, 90), fill=col, anchor="mm")
    if name == "hall_long" and spec.get("momshadow"):
        s = 0.07 * 3
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        cx, cy = 960, 360
        sw = math.sin(t * 1.3) * 4
        sd.ellipse([cx - 16 + sw, cy - 70, cx + 16 + sw, cy - 36], fill=(20, 16, 12, 230))
        sd.polygon([(cx - 18 + sw, cy - 36), (cx + 18 + sw, cy - 36), (cx + 26, cy + 24), (cx - 26, cy + 24)], fill=(20, 16, 12, 230))
        img.alpha_composite(sh)
    if name == "wallphone":
        if spec.get("ring") and (t % 0.9) < 0.5:
            for r in (60, 110, 160):
                d.arc([960 - r * 2.5, 165 - r, 960 + r * 2.5, 165 + r], 200, 340, fill=W3, width=6)
        rings = spec.get("rings")
        if rings:
            if spec.get("countup"):
                a_, b_ = spec["countup"]
                kk = min(1, t / max(1, dur * 0.95))
                rings = int(round(a_ + (b_ - a_) * kk))
            d.text((1400, 360), f"RING {rings}", font=font(FXB, 80), fill=W3 if rings < 7 else RED, anchor="mm")
            for j in range(7):
                d.rectangle([1250 + j * 44, 430, 1284 + j * 44, 464], outline=W3, width=3, fill=W3 if j < rings else None)
        if spec.get("wave"):
            pts = []
            for i in range(0, 600, 6):
                pts.append((660 + i, 720 + math.sin(i * 0.08 + t * 10) * 20 * (0.5 + 0.5 * math.sin(i * 0.02 + t * 3))))
            d.line(pts, fill=W3, width=4)
    if name == "curtains":
        st = spec.get("shadows", 1)
        # back-lit window shapes behind curtain
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        n = {1: 3, 2: 7, 3: 7}[st]
        for i in range(n):
            x = 300 + i * 220 + math.sin(t * 0.8 + i) * 20
            alpha = 255
            if st == 3:
                alpha = int(255 * max(0, 1 - t / max(1, dur * 0.6) * (1 + i * 0.12)))
            sc = 1.0 if st == 1 else 1.25
            creature(sd, x, CH, sc * (0.9 + 0.1 * (i % 3)), t + i, black=True, alpha=alpha)
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(sh)
        # curtain fabric over
        cl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        cd.rectangle([0, 0, CW, CH], fill=(230, 226, 215, 120))
        for j in range(24):
            x = j * 80 + 40
            cd.line([(x, 0), (x, CH)], fill=(200, 195, 185, 140), width=6)
        if spec.get("bulge"):
            for i in range(n):
                x = 300 + i * 220
                r = 60 + 20 * math.sin(t * 3 + i)
                cd.ellipse([x - r, 380 - r, x + r, 380 + r], fill=(255, 250, 240, 60))
        img.alpha_composite(cl)
        d.rectangle([0, 0, CW, 24], fill=W3)
    if name == "cuckoo":
        sw = math.sin(t * 3.2) * 0.35
        d.line([(960, 640), (960 + math.sin(sw) * 160, 640 + math.cos(sw) * 160)], fill=W3, width=6)
        d.ellipse([960 + math.sin(sw) * 160 - 26, 640 + math.cos(sw) * 160 - 26, 960 + math.sin(sw) * 160 + 26, 640 + math.cos(sw) * 160 + 26], fill=W3)
        hh = (t * 0.2) % (2 * math.pi)
        d.line([(960, 440), (960 + math.cos(-1.2 + hh * 0.05) * 70, 440 + math.sin(-1.2) * 70)], fill=W3, width=10)
        d.line([(960, 440), (960 + math.cos(-1.57 + t * 0.6) * 105, 440 + math.sin(-1.57 + t * 0.6) * 105)], fill=W3, width=6)
        if spec.get("bird"):
            ph = (t % 1.2) if spec.get("birdloop") else min(t, 1.2)
            k = math.sin(min(1, ph / 0.6) * math.pi) if spec.get("birdloop") else min(1, t / 0.6)
            bx = 960
            by = 160 - 10
            d.rectangle([920, 120, 1000, 200], fill=(10, 10, 12))
            d.ellipse([bx - 30, by - 30 + 0, bx + 30 + 40 * k, by + 25], fill=W3)
            d.polygon([(bx + 28 + 40 * k, by - 6), (bx + 60 + 40 * k, by), (bx + 28 + 40 * k, by + 6)], fill=YEL)
    if name == "yard":
        st = spec.get("prints", 1)
        rnd = random.Random(7)
        n = 60 if st == 1 else 200
        for i in range(n):
            ang = i * 0.21
            rad = 480 + 60 * math.sin(i * 0.7)
            x = 1700 + math.cos(ang) * rad * 1.4 - 400
            y = 600 + math.sin(ang) * rad * 0.35
            if not (0 < x < CW and 400 < y < CH):
                x = rnd.uniform(0, CW); y = rnd.uniform(420, CH - 20)
            frac = (x / CW)
            if frac < 0.5:
                for k in range(4):
                    d.ellipse([x - 6 + k * 6 - 9, y - 10, x - 6 + k * 6 - 3, y - 4], fill=(120, 120, 130))
                d.ellipse([x - 10, y - 4, x + 10, y + 10], fill=(120, 120, 130))
            else:
                d.ellipse([x - 9, y - 22, x + 9, y + 22], fill=(110, 110, 120))
                for k in range(7):
                    d.line([(x - 12 + k * 4, y - 22), (x - 14 + k * 4.5, y - 40)], fill=(110, 110, 120), width=3)
    if name == "house":
        mode = spec.get("car")
        if mode in ("leave", "arrive"):
            ov = Pr()
            if mode == "leave":
                k = min(1, t / max(1, dur * 0.8))
                x = 650 - k * 900
                car(ov, x, FY, 0.9 * (1 - 0.4 * k), lights="tail")
            else:
                k = min(1, t / max(1, dur * 0.8))
                x = -300 + k * 950
                car(ov, x, FY, 0.9, lights="head")
            img.alpha_composite(ov.done())


def creature(d, x, y, s, t, black=True, alpha=255):
    """Tall thin shadow creature with too many joints. (x,y) = feet."""
    c = (10, 9, 8, alpha)
    h = 520 * s
    hx, hy = x, y - h
    d.ellipse([hx - 30 * s, hy - 40 * s, hx + 30 * s, hy + 30 * s], fill=c)
    d.polygon([(x - 24 * s, hy + 30 * s), (x + 24 * s, hy + 30 * s), (x + 14 * s, y - h * 0.45), (x - 14 * s, y - h * 0.45)], fill=c)
    sw = math.sin(t * 2) * 0.2
    for side in (-1, 1):
        pts = [(x + side * 20 * s, hy + 40 * s)]
        ang = side * (0.5 + sw)
        L = 70 * s
        for j in range(5):
            px, py = pts[-1]
            ang = ang + side * (0.6 if j % 2 else -0.4)
            pts.append((px + math.sin(ang) * L, py + abs(math.cos(ang)) * L))
        d.line(pts, fill=c, width=int(9 * s) + 1, joint="curve")
        for j in range(4):
            px, py = pts[-1]
            d.line([(px, py), (px + side * (10 + j * 5) * s, py + (20 + j * 6) * s)], fill=c, width=int(4 * s) + 1)
        lp = [(x + side * 10 * s, y - h * 0.45)]
        for j in range(3):
            px, py = lp[-1]
            lp.append((px + side * (25 if j % 2 == 0 else -15) * s, py + h * 0.15))
        d.line(lp, fill=c, width=int(10 * s) + 1, joint="curve")


# ------------------------------------------------------------------ text-based scenes
def hud_boxes(d, cx, cy, cur, size=34, gap=10, done_upto=None):
    n = 5
    tot = n * size + (n - 1) * gap
    x0 = cx - tot / 2
    for i in range(n):
        x = x0 + i * (size + gap)
        num = i + 1
        if num == cur:
            d.rectangle([x, cy - size / 2, x + size, cy + size / 2], fill=W3)
            d.text((x + size / 2, cy), str(num), font=font(FB, size * .6), fill=(10, 10, 10), anchor="mm")
        else:
            col = W3 if (done_upto and num < done_upto) else (110, 108, 104)
            d.rectangle([x, cy - size / 2, x + size, cy + size / 2], outline=col, width=2)
            d.text((x + size / 2, cy), str(num), font=font(FB, size * .55), fill=col, anchor="mm")


def paint_text_scene(name, img, spec, t, dur):
    d = ImageDraw.Draw(img)
    if name == "rulecard":
        n = spec.get("card", 1)
        k = min(1, t / 0.35)
        sc = 0.85 + 0.15 * k
        d.text((900, 330), "RULE", font=font(FXB, 150 * sc), fill=W3, anchor="rm")
        bx = 940
        bs = 170 * sc
        d.rounded_rectangle([bx, 330 - bs / 2, bx + bs, 330 + bs / 2], int(20 * sc), fill=W3)
        d.text((bx + bs / 2, 335), str(n), font=font(FXB, 140 * sc), fill=(10, 10, 10), anchor="mm")
        w = 520 * min(1, t / 0.6)
        d.rectangle([960 - w, 452, 960 + w, 458], fill=RED)
        d.text((960, 530), spec.get("cardtext", ""), font=font(FXB, 64), fill=W3, anchor="mm")
        hud_boxes(d, 960, 640, n, size=46, gap=14, done_upto=n)
    elif name == "title":
        d.text((960, 200), "FILE 112  //  CASE: THE HOUSE ON GRAVEL ROAD", font=font(FB, 30), fill=(140, 138, 134), anchor="mm")
        d.text((960, 340), "RULES FOR YOUR", font=font(FXB, 110), fill=W3, anchor="mm")
        d.text((960, 470), "FIRST NIGHT ALONE", font=font(FXB, 130), fill=W3, anchor="mm")
        w = 600 * min(1, t / 0.8)
        d.rectangle([960 - w, 560, 960 + w, 566], fill=RED)
        hud_boxes(d, 960, 650, 0, size=46, gap=14)
    elif name == "endcard":
        pass
    elif name in ("list", "oldlist", "newlist"):
        paper = (246, 244, 236) if name != "oldlist" else (232, 214, 160)
        ink = (40, 40, 60) if name != "oldlist" else (90, 70, 50)
        d.polygon([(470, 30), (1450, 20), (1460, CH - 20), (460, CH - 10)], fill=paper)
        if name == "list":
            d.ellipse([930, 6, 990, 66], fill=RED)
        d.text((960, 110), "Rules for your first night alone", font=font(FH, 66), fill=ink, anchor="mm")
        rules = ["At 8 PM, close every curtain in the house. Start with the kitchen.",
                 "The dog sleeps outside tonight. If he scratches at the door, do not let him in. The dog is with us.",
                 "There are fourteen stairs. If you count fifteen, go back down.",
                 "If the house phone rings after midnight, let it ring seven times. Then pick up, and say nothing.",
                 "At 6 AM, open the curtains again, and say \"Good morning, house.\""]
        hl = spec.get("hl", 0)
        wk = 1.0
        if name == "newlist" and spec.get("write") and not spec.get("lastline"):
            wk = min(1, t / max(1, dur * 0.9))
        for i, r in enumerate(rules):
            y = CH * (.32 + .12 * i) - 60
            if name == "newlist" and i / 5 > wk:
                break
            words = f"{i + 1}. {r}".split()
            lines, cur = [], ""
            for w_ in words:
                if len(cur) + len(w_) > 52 and cur:
                    lines.append(cur); cur = w_
                else:
                    cur = (cur + " " + w_).strip()
            lines.append(cur)
            if hl == i + 1:
                d.rectangle([500, y - 8, 500 + 920 * min(1, t / 0.5), y + 46 * len(lines) + 4], fill=(250, 225, 90))
            col = ink if (hl in (0, i + 1)) else (ink[0] + 110, ink[1] + 110, ink[2] + 100)
            for j, ln in enumerate(lines):
                d.text((520, y + j * 46), ln, font=font(FH, 40), fill=col)
        if name == "oldlist" and spec.get("stage") == 1:
            d.text((1300, 790), "October 1991", font=font(FH, 56), fill=(150, 40, 40), anchor="mm")
            d.ellipse([1110, 745, 1490, 835], outline=RED, width=6)
        if name == "newlist" and spec.get("lastline"):
            d.text((960, 790), "The house will take care of you.", font=font(FH, 50), fill=(150, 40, 40), anchor="mm")
    elif name == "phone":
        d.ellipse([500, 520, 900, 1100], fill=(210, 208, 202))
        d.ellipse([1020, 520, 1420, 1100], fill=(210, 208, 202))
        d.rounded_rectangle([700, 20, 1220, 900], 60, fill=W3)
        d.rounded_rectangle([724, 60, 1196, 870], 40, fill=(18, 18, 22))
        scr = spec.get("screen")
        if scr == "alarm":
            d.text((960, 300), "5:59", font=font(FXB, 150), fill=W3, anchor="mm")
            d.text((960, 410), "ALARM", font=font(FB, 40), fill=(150, 150, 150), anchor="mm")
            r = 70 + 6 * math.sin(t * 10)
            d.ellipse([960 - r, 600 - r, 960 + r, 600 + r], fill=(230, 60, 50))
        else:
            d.text((960, 110), "MOM", font=font(FB, 40), fill=W3, anchor="mm")
            d.line([(724, 150), (1196, 150)], fill=(60, 60, 66), width=2)
            y = 190
            def bub(y, txt, mine):
                lines = []
                cur = ""
                for w_ in txt.split():
                    if len(cur) + len(w_) > 18 and cur:
                        lines.append(cur); cur = w_
                    else:
                        cur = (cur + " " + w_).strip()
                lines.append(cur)
                h = 46 * len(lines) + 30
                x0, x1 = (850, 1170) if mine else (750, 1080)
                d.rounded_rectangle([x0, y, x1, y + h], 26, fill=(60, 120, 230) if mine else (60, 60, 68))
                for j, ln in enumerate(lines):
                    d.text((x0 + 22, y + 16 + j * 46), ln, font=font(FB, 34), fill=W3)
                return y + h + 20
            y = bub(y, "Is Buster with you?", True)
            if scr in ("photo", "dont"):
                if scr == "photo" and t < 1.0:
                    for j in range(3):
                        if int(t * 4) % 3 >= j:
                            d.ellipse([780 + j * 34, y + 20, 804 + j * 34, y + 44], fill=(150, 150, 150))
                else:
                    d.rounded_rectangle([750, y, 1080, y + 300], 26, fill=(40, 40, 46))
                    d.rectangle([770, y + 170, 1060, y + 280], fill=(80, 70, 60))
                    dog, ox, oy = draw_dog(dict(anim="sleep", face=1), 2.4, t)
                    img.alpha_composite(dog, (int(915 - ox), int(y + 250 - oy)))
                    y += 320
            if scr == "dont":
                y = bub(y, "Don't open the door.", False)
    elif name == "clockcard":
        hh, mm = spec.get("hands", (8, 0))
        cx, cy, R = 960, 380, 250
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=W3, width=16)
        for k in range(12):
            a = k * math.pi / 6
            d.line([(cx + math.cos(a) * (R - 40), cy + math.sin(a) * (R - 40)), (cx + math.cos(a) * (R - 18), cy + math.sin(a) * (R - 18))], fill=W3, width=8)
        am = (mm / 60) * 2 * math.pi - math.pi / 2
        ah = ((hh % 12) / 12 + mm / 720) * 2 * math.pi - math.pi / 2
        d.line([(cx, cy), (cx + math.cos(ah) * R * .5, cy + math.sin(ah) * R * .5)], fill=W3, width=18)
        d.line([(cx, cy), (cx + math.cos(am) * R * .78, cy + math.sin(am) * R * .78)], fill=W3, width=10)
        asec = t * 2 * math.pi / 6 - math.pi / 2
        d.line([(cx, cy), (cx + math.cos(asec) * R * .85, cy + math.sin(asec) * R * .85)], fill=RED, width=4)
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=W3)
        if spec.get("label"):
            d.text((cx, cy + R + 70), spec["label"], font=font(FB, 40), fill=(170, 168, 164), anchor="mm")
