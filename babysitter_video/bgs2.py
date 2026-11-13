"""Backgrounds for the babysitter story."""
import math, random
from PIL import Image, ImageDraw
from bgs import Cv, SW, SH, OUT, sh, window, frame, floor_boards, couch, couch_front, lamp, tree_dead, draw_car

STONE = (150, 150, 155)


def pine(c, x, y, s, col=(30, 45, 40)):
    for k in range(4):
        w = (70 - k * 14) * s
        yy = y - k * 55 * s
        c.poly([(x - w, yy), (x + w, yy), (x, yy - 110 * s)], sh(col, 1 + k * .05), w=2)
    c.rect(x - 8 * s, y, x + 8 * s, y + 30 * s, (50, 40, 35), w=2)


def mansion(c, x, y, s=1.0):
    W, H = 760 * s, 520 * s
    c.poly([(x - W / 2 - 40 * s, y - H), (x + W / 2 + 40 * s, y - H), (x + W / 3, y - H - 230 * s), (x - W / 3, y - H - 230 * s)], (55, 55, 62))
    # attic eye window
    c.ell(x - 55 * s, y - H - 170 * s, x + 55 * s, y - H - 60 * s, (25, 25, 30), w=5)
    c.ell(x - 22 * s, y - H - 138 * s, x + 22 * s, y - H - 92 * s, (60, 60, 70), ol=False)
    c.rect(x - W / 2, y - H, x + W / 2, y, STONE)
    rnd = random.Random(3)
    for r_ in range(13):
        yy = y - H + r_ * H / 13
        off = (r_ % 2) * 40 * s
        c.line([(x - W / 2, yy), (x + W / 2, yy)], sh(STONE, .85), 2)
        xx = x - W / 2 + off
        while xx < x + W / 2:
            c.line([(xx, yy), (xx, yy + H / 13)], sh(STONE, .85), 2)
            xx += 80 * s
    for wx in (-0.36, -0.12, 0.12, 0.36):
        for wy in (-0.83, -0.5):
            X, Y = x + W * wx, y + H * wy
            c.rect(X - 34 * s, Y - 50 * s, X + 34 * s, Y + 50 * s, (40, 45, 55))
            c.line([(X, Y - 50 * s), (X, Y + 50 * s)], OUT, 2)
            c.rect(X - 52 * s, Y - 50 * s, X - 34 * s, Y + 50 * s, (25, 25, 28))
            c.rect(X + 34 * s, Y - 50 * s, X + 52 * s, Y + 50 * s, (25, 25, 28))
    for wx in (-0.36, -0.12, 0.36):
        X, Y = x + W * wx, y - H * 0.17
        c.rect(X - 34 * s, Y - 50 * s, X + 34 * s, Y + 50 * s, (255, 210, 130))
        c.rect(X - 52 * s, Y - 50 * s, X - 34 * s, Y + 50 * s, (25, 25, 28))
        c.rect(X + 34 * s, Y - 50 * s, X + 52 * s, Y + 50 * s, (25, 25, 28))
    c.rect(x + W * .12 - 40 * s, y - 170 * s, x + W * .12 + 40 * s, y, (20, 20, 24))
    c.ell(x + W * .12 - 70 * s, y - 210 * s, x + W * .12 - 50 * s, y - 190 * s, (255, 230, 160), ol=False)
    c.rect(x - W / 2 - 20 * s, y - 14 * s, x + W / 2 + 20 * s, y, (120, 120, 125))


def bg_mansion(a):
    c = Cv()
    c.grad(0, 0, SW, 700, (35, 30, 50), (120, 80, 90))
    c.ell(1500, 90, 1590, 180, (230, 225, 210), ol=False)
    for k in range(34):
        x = k * 60
        pine(c, x, 700 - (k * 31 % 60), 1.3 + (k % 3) * .2, (20, 30, 28))
    c.rect(0, 690, SW, SH, (45, 55, 45), ol=False)
    mansion(c, 960, 780, 1.0)
    for x in (120, 330, 1600, 1800):
        pine(c, x, 840, 2.4, (18, 26, 24))
    c.poly([(1020, 780), (1120, 780), (1180, SH), (700, SH)], (120, 115, 110))
    return c.done(), None


def bg_porch2(a):
    c = Cv()
    c.rect(0, 0, SW, SH, STONE, ol=False)
    for r_ in range(24):
        yy = r_ * 45
        c.line([(0, yy), (SW, yy)], sh(STONE, .85), 3)
        xx = (r_ % 2) * 60
        while xx < SW:
            c.line([(xx, yy), (xx, yy + 45)], sh(STONE, .85), 3)
            xx += 120
    inside = a.get("door") in ("open", "opening", "open_inside")
    c.rect(700, 120, 1220, 900, (60, 45, 40))
    if inside:
        c.rect(720, 140, 1200, 900, (250, 205, 150), ol=False)
        c.rect(720, 140, 1200, 520, (220, 170, 120), ol=False)
        c.rect(1020, 220, 1140, 340, (130, 90, 60))
        c.poly([(1200, 140), (1360, 100), (1360, 940), (1200, 900)], (35, 30, 30))
    else:
        c.rect(720, 140, 1200, 900, (35, 30, 30))
    c.ell(600, 300, 660, 380, (255, 220, 150))
    c.rect(0, 900, SW, SH, (90, 85, 80), ol=False)
    c.rect(500, 880, 1420, 920, (110, 100, 95))
    return c.done(), None


def bouncer(c, x, y):
    c.poly([(x - 150, y), (x + 150, y), (x + 110, y - 40), (x - 110, y - 40)], (200, 200, 205))
    c.poly([(x - 120, y - 40), (x + 120, y - 40), (x + 90, y - 200), (x - 90, y - 200)], (230, 190, 200))
    c.d.arc([(x - 140) * 2, (y - 330) * 2, (x + 140) * 2, (y - 60) * 2], 200, 340, fill=(200, 200, 205), width=16)


def bg_living2(a):
    c = Cv()
    wall = (190, 170, 150)
    c.rect(0, 0, SW, 800, wall, ol=False)
    c.rect(0, 780, SW, 800, sh(wall, .8), ol=False)
    floor_boards(c, 800, 1080, (120, 85, 60))
    # stairs at right
    c.poly([(1500, 800), (1920, 800), (1920, 80), (1760, 80)], (90, 75, 65))
    for k in range(12):
        y = 800 - k * 60
        x = 1500 + k * 22
        c.rect(x, y - 60, 1920, y, (110, 85, 65), w=2)
    c.poly([(1720, 0), (1920, 0), (1920, 120), (1760, 140)], (15, 15, 20), ol=False)
    c.line([(1480, 640), (1760, 40)], (70, 50, 40), 10)
    # nursery door left
    c.rect(60, 220, 300, 800, (120, 90, 65))
    c.ell(260, 500, 280, 520, (200, 180, 100))
    window(c, 420, 180, 760, 480, night=True, curtains=(120, 70, 70))
    frame(c, 880, 200, 1060, 360, (200, 200, 190))
    lamp(c, 1380, 790)
    couch(c, 340, 1100, 940, (105, 95, 120))
    bouncer(c, 1114, 1066)
    if a.get("wet_bouncer"):
        c.ell(1050, 920, 1180, 980, (90, 110, 140), ol=False)
    bg = c.done()
    f = Cv()
    couch_front(f, 340, 1100, 940, (105, 95, 120))
    f.poly([(560, 1010), (1000, 1010), (1040, 1080), (520, 1080)], (110, 75, 50))
    if a.get("monitor_table"):
        f.rect(740, 960, 820, 1010, (235, 235, 235))
        f.rect(752, 970, 808, 1000, (150, 200, 160), ol=False)
    return bg, f.done()


def bg_nursery(a):
    c = Cv()
    wall = (170, 195, 215)
    c.rect(0, 0, SW, 780, wall, ol=False)
    for x in range(0, SW, 140):
        for y in range(40, 760, 140):
            c.ell(x + 60, y, x + 76, y + 16, (240, 240, 250), ol=False)
    floor_boards(c, 780, 1080, (150, 115, 85))
    # closet
    st = a.get("closet", "closed")
    c.rect(80, 140, 480, 790, (235, 230, 220))
    c.rect(100, 160, 460, 790, (20, 18, 20), ol=False)
    if st == "closed":
        c.rect(100, 160, 460, 790, (225, 215, 200))
    elif st == "ajar":
        c.rect(118, 160, 460, 790, (225, 215, 200))
    else:
        c.poly([(460, 160), (620, 120), (620, 830), (460, 790)], (225, 215, 200))
    if st != "closed":
        pass
    c.ell(420, 470, 440, 490, (190, 170, 100)) if st != "open" else None
    window(c, 1450, 150, 1800, 470, night=True, curtains=(240, 200, 210), moon=True)
    # dresser + nightstand camera
    c.rect(620, 560, 900, 790, (240, 235, 230))
    for y in (600, 670, 740):
        c.line([(640, y), (880, y)], OUT, 2)
    c.rect(720, 500, 800, 560, (240, 240, 240))
    c.ell(742, 512, 778, 548, (40, 40, 45))
    c.ell(752, 522, 768, 538, (200, 40, 40), ol=False)
    # crib back panel
    c.rect(980, 520, 1480, 830, (245, 240, 235))
    c.rect(1000, 540, 1460, 600, (250, 248, 240), ol=False)
    c.rect(1000, 780, 1460, 840, (230, 230, 240))
    if a.get("mobile"):
        c.line([(1230, 300), (1230, 380)], OUT, 3)
        c.line([(1150, 380), (1310, 380)], OUT, 3)
        for k, col in enumerate(((250, 200, 80), (130, 200, 230), (240, 150, 170))):
            x = 1150 + k * 80
            c.line([(x, 380), (x, 420)], OUT, 2)
            c.ell(x - 18, 420, x + 18, 456, col)
    bg = c.done()
    f = Cv()
    f.rect(960, 800, 1500, 870, (245, 240, 235))
    for x in range(990, 1480, 44):
        f.rect(x, 560, x + 12, 820, (250, 246, 240), w=2)
    f.rect(960, 540, 1500, 570, (245, 240, 235))
    f.rect(960, 520, 990, 960, (245, 240, 235))
    f.rect(1470, 520, 1500, 960, (245, 240, 235))
    return bg, f.done()


def bg_kitchen2(a):
    c = Cv()
    c.rect(0, 0, SW, 790, (225, 215, 195), ol=False)
    c.rect(0, 790, SW, SH, (190, 180, 170), ol=False)
    for x in range(0, SW, 120):
        for y in range(790, SH, 120):
            c.rect(x, y, x + 120, y + 120, (200, 190, 180) if (x // 120 + y // 120) % 2 else (180, 170, 160), w=1)
    c.rect(0, 120, 900, 380, (60, 70, 85))
    for k in range(4):
        c.rect(k * 225 + 10, 130, k * 225 + 215, 370, (70, 80, 98), w=2)
    c.rect(0, 600, 900, 790, (60, 70, 85))
    c.rect(0, 585, 920, 610, (230, 230, 230))
    # fridge
    c.rect(1060, 120, 1460, 790, (225, 228, 232), w=5)
    c.line([(1060, 400), (1460, 400)], OUT, 4)
    c.rect(1090, 180, 1110, 360, (170, 175, 180))
    c.rect(1090, 430, 1110, 650, (170, 175, 180))
    c.poly([(1190, 200), (1400, 195), (1405, 470), (1195, 475)], (252, 250, 240), w=3)
    for k in range(6):
        c.line([(1215, 230 + k * 40), (1380, 228 + k * 40)], (60, 80, 170), 3)
    c.ell(1285, 185, 1305, 205, (220, 60, 60), ol=False)
    window(c, 1560, 160, 1860, 460, night=True, curtains=(200, 180, 140))
    return c.done(), None


def bg_stairs(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (60, 55, 60), ol=False)
    vpx, vpy = 960, 120
    for k in range(16):
        t0 = k / 16
        t1 = (k + 1) / 16
        y0 = SH - t0 ** 0.8 * (SH - vpy)
        y1 = SH - t1 ** 0.8 * (SH - vpy)
        w0 = 700 * (1 - t0) + 120
        w1 = 700 * (1 - t1) + 120
        col = sh((120, 95, 75), 1 - t0 * 0.85)
        c.poly([(vpx - w0, y0), (vpx + w0, y0), (vpx + w1, y1), (vpx - w1, y1)], col, w=2)
    c.poly([(0, 0), (vpx - 120, vpy), (vpx - 820, SH), (0, SH)], (75, 70, 75))
    c.poly([(SW, 0), (vpx + 120, vpy), (vpx + 820, SH), (SW, SH)], (68, 64, 70))
    c.rect(vpx - 220, 0, vpx + 220, vpy + 4, (5, 5, 8), ol=False)
    c.line([(vpx + 830, SH), (vpx + 150, vpy)], (90, 65, 50), 14)
    for k in range(10):
        t = k / 10
        x = vpx + 830 - (680) * t
        y = SH - (SH - vpy) * t
        c.line([(x, y), (x, y - 120 * (1 - t) - 20)], (90, 65, 50), int(6 * (1 - t)) + 2)
    return c.done(), None


def bg_dogwall(a):
    c = Cv(2400, 1080)
    c.rect(0, 0, 2400, 1080, (190, 170, 150), ol=False)
    rnd = random.Random(4)
    for i in range(10):
        x = 120 + (i % 5) * 450
        y = 150 + (i // 5) * 430
        frame(c, x, y, x + 320, y + 340, (200, 215, 225), wood=(60, 45, 35))
        cx, cy = x + 160, y + 190
        c.ell(cx - 95, cy - 90, cx + 95, cy + 80, (28, 28, 32))
        c.poly([(cx - 90, cy - 70), (cx - 135, cy - 10), (cx - 115, cy + 70), (cx - 70, cy + 10)], (20, 20, 24))
        c.poly([(cx + 90, cy - 70), (cx + 135, cy - 10), (cx + 115, cy + 70), (cx + 70, cy + 10)], (20, 20, 24))
        c.ell(cx - 55, cy + 5, cx + 55, cy + 95, (45, 45, 50))
        c.ell(cx - 22, cy + 10, cx + 22, cy + 38, (8, 8, 10))
        for ex in (cx - 40, cx + 40):
            c.ell(ex - 14, cy - 40, ex + 14, cy - 12, (120, 75, 40))
            c.ell(ex - 5, cy - 32, ex + 5, cy - 20, (5, 5, 5), ol=False)
        if i % 2 == 0:
            c.poly([(cx - 16, cy + 70), (cx + 16, cy + 70), (cx + 12, cy + 120), (cx - 12, cy + 120)], (230, 100, 120))
        c.rect(cx - 70, cy + 95, cx + 70, cy + 112, (200, 40, 40), w=2)
    return c.done(), None


def bg_dorm(a):
    c = Cv()
    c.rect(0, 0, SW, 800, (175, 165, 185), ol=False)
    floor_boards(c, 800, 1080, (130, 110, 95))
    window(c, 1300, 140, 1680, 480, sky=((250, 170, 120), (255, 220, 170)), curtains=(90, 90, 130))
    c.rect(100, 200, 500, 420, (245, 240, 230))
    c.text((300, 260), "RENT DUE", 44, (200, 40, 40, 255))
    c.text((300, 340), "$850", 50, (40, 40, 40, 255))
    if a.get("bed"):
        c.rect(560, 560, 1360, 900, (220, 220, 230))
        c.rect(540, 460, 600, 920, (110, 80, 60))
    else:
        c.rect(1100, 620, 1600, 660, (130, 90, 60))
        c.rect(1120, 660, 1140, 900, (100, 70, 50))
        c.rect(1560, 660, 1580, 900, (100, 70, 50))
    bg = c.done()
    f = None
    if a.get("bed"):
        fc = Cv()
        fc.poly([(560, 720), (1360, 720), (1380, 950), (540, 950)], (80, 110, 150))
        f = fc.done()
    return bg, f


def bg_closet(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (170, 195, 215), ol=False)
    c.rect(460, 60, 1460, 1080, (235, 230, 220))
    c.rect(520, 110, 1400, 1080, (5, 4, 6), ol=False)
    c.rect(0, 960, SW, SH, (150, 115, 85), ol=False)
    c.rect(520, 960, 1400, SH, (25, 20, 18), ol=False)
    return c.done(), None


def bg_monitor_table(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (90, 65, 45), ol=False)
    for y in range(0, SH, 100):
        c.line([(0, y), (SW, y + 30)], (75, 52, 36), 6)
    c.rect(200, 140, 560, 380, (210, 200, 180))
    return c.done(), None


def bg_floor_steps(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (140, 105, 78), ol=False)
    for y in range(0, SH, 110):
        c.line([(0, y), (SW, y)], (110, 82, 60), 5)
        off = (y // 110) * 330 % 900
        for x in range(off, SW, 900):
            c.line([(x, y), (x, y + 110)], (110, 82, 60), 4)
    return c.done(), None


def bg_frontdoor_in(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (175, 160, 145), ol=False)
    floor_boards(c, 900, 1080, (110, 80, 60))
    if a.get("open_door"):
        c.rect(640, 120, 1180, 900, (230, 170, 140))
        c.grad(660, 140, 1160, 900, (250, 170, 130), (180, 150, 160))
    else:
        c.rect(640, 120, 1180, 900, (85, 55, 40))
        for (x0, y0, x1, y1) in ((690, 170, 890, 480), (930, 170, 1130, 480), (690, 540, 890, 860), (930, 540, 1130, 860)):
            c.rect(x0, y0, x1, y1, (95, 62, 45), w=3)
        c.ell(1120, 520, 1150, 550, (200, 180, 100))
    # frosted side window
    c.rect(1230, 120, 1420, 900, (60, 50, 45))
    c.rect(1250, 140, 1400, 880, (70, 80, 100), ol=False)
    c.rect(400, 130, 600, 230, (60, 50, 45))
    return c.done(), None


def bg_frost(a):
    c = Cv()
    c.grad(0, 0, SW, SH, (20, 24, 40), (40, 40, 55))
    c.ell(300, 100, 460, 260, (255, 230, 170), ol=False)
    c.rect(0, 860, SW, SH, (50, 48, 50), ol=False)
    bg = c.done()
    f = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(f)
    d.rectangle([0, 0, SW, SH], fill=(190, 200, 215, 70))
    rnd = random.Random(2)
    for k in range(900):
        x, y = rnd.uniform(0, SW), rnd.uniform(0, SH)
        r = rnd.uniform(4, 22)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 230, 240, rnd.randint(10, 45)))
    d.rectangle([0, 0, 120, SH], fill=(60, 50, 45, 255))
    d.rectangle([SW - 120, 0, SW, SH], fill=(60, 50, 45, 255))
    d.line([(120, 0), (120, SH)], fill=OUT, width=6)
    d.line([(SW - 120, 0), (SW - 120, SH)], fill=OUT, width=6)
    return bg, f


def bg_house_windows(a):
    c = Cv(2600, 1080)
    c.grad(0, 0, 2600, 600, (15, 15, 28), (40, 40, 55))
    c.rect(0, 120, 2600, 960, STONE)
    for r_ in range(19):
        yy = 120 + r_ * 45
        c.line([(0, yy), (2600, yy)], sh(STONE, .85), 3)
    for i, x in enumerate((300, 900, 1500, 2100)):
        c.rect(x, 300, x + 340, 700, (255, 205, 130))
        c.line([(x + 170, 300), (x + 170, 700)], OUT, 5)
        c.line([(x, 500), (x + 340, 500)], OUT, 5)
        c.text((x + 170, 760), ["LIVING ROOM", "KITCHEN", "NURSERY", "HALL"][i], 30, (200, 200, 205, 200))
    c.rect(0, 960, 2600, 1080, (35, 45, 35), ol=False)
    return c.done(), None


def bg_window_face(a):
    c = Cv()
    c.grad(0, 0, SW, SH, (12, 14, 24), (30, 32, 45))
    bg = c.done()
    f = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(f)
    room = a.get("room", "living")
    wallc = {"living": (190, 170, 150), "kitchen": (225, 215, 195), "nursery": (170, 195, 215)}[room]
    wallc = tuple(int(v * 0.55) for v in wallc)
    d.rectangle([0, 0, SW, SH], fill=wallc + (255,))
    d.rectangle([380, 80, 1540, 1000], fill=(0, 0, 0, 0))
    d.rectangle([360, 60, 1560, 1020], outline=(230, 225, 215), width=36)
    d.line([(960, 80), (960, 1000)], fill=(230, 225, 215), width=26)
    d.line([(380, 540), (1540, 540)], fill=(230, 225, 215), width=26)
    d.polygon([(500, 100), (650, 100), (450, 980), (400, 980)], fill=(255, 255, 255, 22))
    if room == "nursery":
        d.rectangle([340, 0, 460, 1080], fill=(240, 200, 210, 255))
        d.rectangle([1460, 0, 1580, 1080], fill=(240, 200, 210, 255))
    return bg, f


def bg_cash(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (210, 205, 200), ol=False)
    for x in range(0, SW, 160):
        c.line([(x, 0), (x - 200, SH)], (195, 190, 186), 3)
    rnd = random.Random(1)
    for k in range(12):
        x = 500 + rnd.uniform(-60, 60) + (k % 4) * 230
        y = 330 + (k // 4) * 170 + rnd.uniform(-20, 20)
        c.poly([(x, y), (x + 300, y - 10), (x + 305, y + 130), (x + 5, y + 140)], (120, 170, 120), w=3)
        c.ell(x + 120, y + 30, x + 190, y + 105, (100, 150, 100), w=2)
        c.text((x + 40, y + 30), "100", 26, (60, 100, 60, 255))
    return c.done(), None


def bg_bouncer_close(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (50, 45, 60), ol=False)
    c.poly([(500, 1080), (1420, 1080), (1300, 300), (620, 300)], (200, 170, 180))
    c.d.arc([380 * 2, -100 * 2, 1540 * 2, 700 * 2], 200, 340, fill=(180, 180, 190), width=40)
    return c.done(), None


def bg_crib_top(a):
    c = Cv()
    c.rect(0, 0, SW, SH, (150, 115, 85), ol=False)
    c.rect(260, 80, 1660, 1000, (245, 240, 235), w=6)
    c.rect(320, 140, 1600, 940, (235, 240, 250), ol=False)
    for x in range(320, 1600, 80):
        for y in range(140, 940, 80):
            c.ell(x + 30, y + 30, x + 44, y + 44, (210, 220, 240), ol=False)
    return c.done(), None


BUILDERS = {
    "mansion": bg_mansion, "porch2": bg_porch2, "living2": bg_living2, "nursery": bg_nursery,
    "kitchen2": bg_kitchen2, "stairs": bg_stairs, "dogwall": bg_dogwall, "dorm": bg_dorm,
    "closet": bg_closet, "monitor_table": bg_monitor_table, "floor_steps": bg_floor_steps,
    "frontdoor_in": bg_frontdoor_in, "frost": bg_frost, "house_windows": bg_house_windows,
    "window_face": bg_window_face, "cash": bg_cash, "bouncer_close": bg_bouncer_close, "crib_top": bg_crib_top,
}
