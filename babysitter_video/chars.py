"""Procedural 2D cartoon characters with a simple skeleton (drawn with PIL, supersampled)."""
import math
from PIL import Image, ImageDraw

OUT = (38, 28, 30, 255)
SS = 2  # supersample

def C(rgb, a=255):
    return (rgb[0], rgb[1], rgb[2], a)

def shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb[:3])

CHARS = {
    "you":   dict(skin=(238, 196, 160), hair=(92, 60, 38), style="short", top=(52, 68, 108), top2=(42, 55, 90), pants=(58, 62, 72), shoes=(40, 40, 45), hoodie=True, h=1.0, w=1.0),
    "emma":  dict(skin=(244, 205, 175), hair=(158, 72, 38), style="wavy", top=(214, 160, 58), top2=(185, 132, 45), pants=(55, 65, 95), shoes=(110, 70, 50), h=.95, w=.92, lips=(200, 100, 100)),
    "lily":  dict(skin=(214, 218, 216), hair=(22, 22, 28), style="long", top=(196, 200, 206), top2=(160, 166, 175), pants=(196, 200, 206), shoes=(150, 150, 155), dress=True, h=.93, w=.88, eyebags=True, lips=(170, 150, 160), creepy=True),
    "diane": dict(skin=(240, 200, 172), hair=(205, 188, 150), style="bob", top=(140, 110, 155), top2=(115, 88, 130), pants=(95, 75, 65), shoes=(70, 50, 45), h=.93, w=1.02, apron=True, lips=(190, 95, 100), age=True),
    "frank": dict(skin=(232, 186, 150), hair=(150, 148, 145), style="cap", top=(160, 50, 45), top2=(120, 35, 32), pants=(60, 80, 115), shoes=(70, 50, 40), flannel=True, h=1.02, w=1.12, mustache=True, age=True),
    "claire": dict(skin=(244, 208, 180), hair=(236, 205, 120), style="updo", top=(38, 112, 82), top2=(28, 88, 64), pants=(38, 112, 82), shoes=(30, 30, 35), dress=True, h=.95, w=.92, lips=(200, 70, 80), earrings=True),
    "david": dict(skin=(232, 190, 158), hair=(60, 45, 35), style="short", top=(36, 40, 56), top2=(28, 30, 44), pants=(36, 40, 56), shoes=(20, 20, 22), suit=True, h=1.03, w=1.05),
    "noah":  dict(skin=(248, 212, 188), hair=(200, 95, 45), style="baby", top=(130, 175, 225), top2=(105, 150, 200), pants=(130, 175, 225), shoes=(248, 212, 188), kid=True, baby=True, h=1.0, w=1.0, bust_base=12, ducks=True),
    "fakenoah": dict(skin=(226, 214, 208), hair=(185, 90, 48), style="baby", top=(120, 160, 205), top2=(95, 135, 180), pants=(120, 160, 205), shoes=(226, 214, 208), kid=True, baby=True, h=1.0, w=1.0, bust_base=12, ducks=True, creepy=True, eyebags=True),
    "kemma": dict(skin=(244, 205, 175), hair=(158, 72, 38), style="kid", top=(245, 205, 60), top2=(220, 175, 40), pants=(245, 205, 60), shoes=(200, 80, 80), dress=True, h=1.0, w=1.0, kid=True),
    "klily": dict(skin=(242, 205, 178), hair=(30, 28, 32), style="kid", top=(245, 205, 60), top2=(220, 175, 40), pants=(245, 205, 60), shoes=(200, 80, 80), dress=True, h=1.0, w=1.0, kid=True),
}

# ---------------------------------------------------------------- geometry
def rot(p, a, o=(0, 0)):
    ca, sa = math.cos(a), math.sin(a)
    x, y = p[0] - o[0], p[1] - o[1]
    return (o[0] + x * ca - y * sa, o[1] + x * sa + y * ca)

def ellipse_pts(cx, cy, rx, ry, n=28, a0=0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + ry * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]

def capsule(p0, p1, r, n=10):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    a = math.atan2(dy, dx)
    pts = []
    for i in range(n + 1):
        t = a + math.pi / 2 + math.pi * i / n
        pts.append((p1[0] + r * math.cos(t - math.pi), p1[1] + r * math.sin(t - math.pi)))
    for i in range(n + 1):
        t = a - math.pi / 2 + math.pi * i / n
        pts.append((p0[0] + r * math.cos(t + math.pi), p0[1] + r * math.sin(t + math.pi)))
    return pts

def taper(p0, p1, r0, r1, n=8):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    a = math.atan2(dy, dx)
    pts = []
    for i in range(n + 1):
        t = a - math.pi / 2 + math.pi * i / n
        pts.append((p1[0] + r1 * math.cos(t), p1[1] + r1 * math.sin(t)))
    for i in range(n + 1):
        t = a + math.pi / 2 + math.pi * i / n
        pts.append((p0[0] + r0 * math.cos(t), p0[1] + r0 * math.sin(t)))
    return pts


class Pen:
    """Maps character units -> layer pixels, with optional global rotation (lean)."""
    def __init__(self, img, ox, oy, u, alpha=1.0):
        self.d = ImageDraw.Draw(img)
        self.ox, self.oy, self.u = ox, oy, u
        self.alpha = alpha
        self.lw = max(1, int(round(u * 0.55)))

    def P(self, pts):
        return [(self.ox + x * self.u, self.oy + y * self.u) for x, y in pts]

    def col(self, c):
        return (c[0], c[1], c[2], int((c[3] if len(c) > 3 else 255) * self.alpha))

    def poly(self, pts, fill, outline=True, w=None):
        pp = self.P(pts)
        if fill is not None:
            self.d.polygon(pp, fill=self.col(fill))
        if outline:
            ww = self.lw if w is None else max(1, int(w * self.u))
            self.d.line(pp + [pp[0]], fill=self.col(OUT), width=ww, joint="curve")

    def line(self, pts, w=0.5, col=OUT):
        pp = self.P(pts)
        self.d.line(pp, fill=self.col(col), width=max(1, int(w * self.u)), joint="curve")

    def circle(self, x, y, r, fill, outline=True, w=None):
        X, Y = self.ox + x * self.u, self.oy + y * self.u
        R = r * self.u
        ww = self.lw if w is None else max(1, int(w * self.u))
        self.d.ellipse([X - R, Y - R, X + R, Y + R], fill=self.col(fill) if fill else None,
                       outline=self.col(OUT) if outline else None, width=ww if outline else 0)


# ---------------------------------------------------------------- pose
def default_pose():
    return dict(sit=False, lean=0.0, bob=0.0, dx=0.0, head_tilt=0.0, turn=0.0, look=(0.0, 0.0),
                blink=0.0, mouth=0.0, expr="neutral", aL=(8, 0), aR=(8, 0), legL=0.0, legR=0.0,
                knee=0.0, breath=0.0, held=None, hand_face=0.0, eyes_closed=False)


def draw_character(name, pose, u, bust=False, alpha=1.0, opts=None):
    """Return (RGBA image, anchor_x, anchor_y) where anchor is feet centre (or chest for bust)."""
    cd = dict(CHARS[name])
    opts = opts or {}
    if opts.get("healthy") and name == "lily":
        cd["skin"] = (246, 208, 186)
        cd["eyebags"] = False
        cd["lips"] = (205, 110, 115)
    wet = opts.get("wet", False)
    uu = u * SS
    if bust:
        W, H = int(110 * uu), int(78 * uu)
        ox, oy = W / 2, H + cd.get("bust_base", 58) * uu   # body y=-base sits at layer bottom
    else:
        W, H = int(110 * uu), int(130 * uu)
        ox, oy = W / 2, H - 6 * uu
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pen = Pen(img, ox, oy, uu, 1.0)
    _draw(pen, cd, pose, name, wet, bust)
    out = img.resize((W // SS, H // SS), Image.LANCZOS if bust else Image.BILINEAR)
    if alpha < 0.999:
        a = out.getchannel("A").point(lambda v: int(v * alpha))
        out.putalpha(a)
    return out, ox / SS, oy / SS


def _draw(pen, cd, p, name, wet, bust):
    hs = cd.get("h", 1.0)
    ws = cd.get("w", 1.0)
    kid = cd.get("kid", False)
    skin = cd["skin"]
    sit = p["sit"]
    by = p["bob"]
    bx = p["dx"]
    # skeleton (units; y up negative)
    hip_y = (-30 if sit else -45 * hs) + by
    sh_y = hip_y - 34 * hs - p["breath"] * 0.6
    if kid:
        hip_y = -40 + by
        sh_y = hip_y - 26
    if cd.get("baby"):
        hip_y = (-11 if sit else -18) + by
        sh_y = hip_y - 17 - p["breath"] * 0.4
    lean = math.radians(p["lean"])
    hip = (bx, hip_y)
    shoulder_c = rot((bx, sh_y), lean, hip)
    torso_w = 15 * ws * (0.8 if kid else 1)
    hipw = 13 * ws * (0.8 if kid else 1)
    # ---- hair back
    head_c = rot((bx, sh_y - 19 * (0.72 if cd.get("baby") else (0.9 if kid else 1))), lean, hip)
    head_c = (head_c[0] + p.get("hx", 0), head_c[1] + p.get("hy", 0))
    tilt = math.radians(p["head_tilt"]) + lean
    hr = 13.5 if not kid else 14.5
    hair_back(pen, cd, head_c, hr, tilt, p["turn"], wet)
    # ---- legs
    if not bust:
        draw_legs(pen, cd, hip, hipw, p, sit, hs, kid)
    # ---- torso
    sl = rot((shoulder_c[0] - torso_w, shoulder_c[1] + 2), 0)
    sr = (shoulder_c[0] + torso_w, shoulder_c[1] + 2)
    hl = (hip[0] - hipw, hip[1])
    hr_ = (hip[0] + hipw, hip[1])
    top = cd["top"]
    if cd.get("dress"):
        hem = 28 if kid else (28 if not sit else 12)
        flare = 6 if kid else 5
        body = [(sl[0] + 1, sl[1] - 2), (sr[0] - 1, sr[1] - 2), (sr[0] + 1, sr[1] + 6), (hr_[0] + flare, hip[1] + hem * (0.6 if sit else 1)),
                (hl[0] - flare, hip[1] + hem * (0.6 if sit else 1)), (sl[0] - 1, sl[1] + 6)]
        if sit:
            body = [(sl[0] + 1, sl[1] - 2), (sr[0] - 1, sr[1] - 2), (sr[0] + 1, sr[1] + 6), (hr_[0] + 6, hip[1] + 6), (hl[0] - 6, hip[1] + 6), (sl[0] - 1, sl[1] + 6)]
        pen.poly(body, top)
        pen.line([(hip[0] - 4, hip[1] + 10), (hip[0] - 3, hip[1] + 22)], 0.3, C(shade(top, .8)))
        pen.line([(hip[0] + 5, hip[1] + 8), (hip[0] + 4, hip[1] + 20)], 0.3, C(shade(top, .8)))
        # collar
        pen.poly(ellipse_pts(shoulder_c[0], shoulder_c[1] + 0.5, 5.5, 3.5, 14, 0, math.pi), C(shade(top, 1.08)), True, 0.35)
    else:
        body = [(sl[0] + 1, sl[1] - 2), (sr[0] - 1, sr[1] - 2), (sr[0] + 1.5, sr[1] + 5), (hr_[0] + 1, hr_[1] + 3), (hl[0] - 1, hl[1] + 3), (sl[0] - 1.5, sl[1] + 5)]
        pen.poly(body, top)
        if cd.get("flannel"):
            for k in range(-2, 3):
                x = shoulder_c[0] + k * 6
                pen.line([(x, sh_y + 3), (x + (hip[0] - shoulder_c[0]), hip_y + 2)], 0.6, C(cd["top2"]))
            for k in range(1, 5):
                y = sh_y + k * 7
                pen.line([(shoulder_c[0] - torso_w + 1, y), (shoulder_c[0] + torso_w - 1, y)], 0.6, C(cd["top2"]))
            pen.line([(shoulder_c[0], sh_y + 1), (hip[0], hip_y + 2)], 0.35)
        if cd.get("hoodie"):
            pen.poly(ellipse_pts(shoulder_c[0], sh_y + 1, 8.5, 4.5, 16, 0, math.pi), C(cd["top2"]), True, 0.35)
            pen.line([(shoulder_c[0] - 2.5, sh_y + 3), (shoulder_c[0] - 3, sh_y + 12)], 0.35, C((230, 230, 235)))
            pen.line([(shoulder_c[0] + 2.5, sh_y + 3), (shoulder_c[0] + 3, sh_y + 12)], 0.35, C((230, 230, 235)))
            pocket = [(hip[0] - 8, hip_y - 9), (hip[0] + 8, hip_y - 9), (hip[0] + 10, hip_y - 1), (hip[0] - 10, hip_y - 1)]
            pen.poly(pocket, C(cd["top2"]), True, 0.35)
        if name == "emma":
            # knitted collar + ribs
            pen.poly(ellipse_pts(shoulder_c[0], sh_y + 1, 6.5, 3.5, 16, 0, math.pi), C(cd["top2"]), True, 0.35)
            for k in range(-3, 4):
                pen.line([(hip[0] + k * 3.5, hip_y - 3), (hip[0] + k * 3.5, hip_y + 2)], 0.25, C(cd["top2"]))
        if cd.get("apron"):
            ap = [(hip[0] - 9, sh_y + 9), (hip[0] + 9, sh_y + 9), (hip[0] + 11, hip_y + (6 if sit else 14)), (hip[0] - 11, hip_y + (6 if sit else 14))]
            pen.poly(ap, C((236, 228, 210)), True, 0.4)
            pen.line([(hip[0] - 9, sh_y + 9), (shoulder_c[0] - 4, sh_y + 1)], 0.4, C((236, 228, 210)))
            pen.line([(hip[0] + 9, sh_y + 9), (shoulder_c[0] + 4, sh_y + 1)], 0.4, C((236, 228, 210)))
            pen.line([(hip[0] - 12, hip_y - 6), (hip[0] + 12, hip_y - 6)], 0.5, C((200, 90, 80)))
    if cd.get("suit"):
        pen.poly([(shoulder_c[0] - 5, sh_y + 1), (shoulder_c[0] + 5, sh_y + 1), (shoulder_c[0], sh_y + 16)], C((240, 240, 240)), True, 0.3)
        pen.poly([(shoulder_c[0] - 1.4, sh_y + 2), (shoulder_c[0] + 1.4, sh_y + 2), (shoulder_c[0] + 2, sh_y + 14), (shoulder_c[0], sh_y + 17), (shoulder_c[0] - 2, sh_y + 14)], C((170, 30, 40)), True, 0.25)
        pen.line([(shoulder_c[0] - 5, sh_y + 1), (shoulder_c[0] - 2, sh_y + 20)], 0.4)
        pen.line([(shoulder_c[0] + 5, sh_y + 1), (shoulder_c[0] + 2, sh_y + 20)], 0.4)
    if cd.get("ducks"):
        for k, (dx_, dy_) in enumerate(((-4, 5), (3, 9), (-2, 13))):
            x0, y0 = shoulder_c[0] + dx_, sh_y + dy_
            pen.circle(x0, y0, 1.3, C((250, 215, 60)), False)
            pen.circle(x0 + 1.1, y0 - 1.2, 0.8, C((250, 215, 60)), False)
    # torso shading
    pen.line([(shoulder_c[0] - torso_w + 2.5, sh_y + 6), (hip[0] - hipw + 2, hip_y - 1)], 0.6, C(shade(top, .82), 140))
    # ---- neck
    neck = [(head_c[0] - 3.5, head_c[1] + 8), (head_c[0] + 3.5, head_c[1] + 8), (shoulder_c[0] + 4, shoulder_c[1] + 1), (shoulder_c[0] - 4, shoulder_c[1] + 1)]
    pen.poly(neck, C(shade(skin, .9)))
    # ---- arms (behind-head items drawn after torso)
    arms(pen, cd, p, shoulder_c, torso_w, hs, kid)
    # ---- head
    draw_head(pen, cd, p, head_c, hr, tilt, wet, name)


def draw_legs(pen, cd, hip, hipw, p, sit, hs, kid):
    pants = cd["pants"]
    shoes = cd["shoes"]
    L = (40 * hs) if not kid else (17 if cd.get("baby") else 38)
    if cd.get("dress"):
        pants = cd["skin"] if not kid else cd["skin"]
    for side, ang in ((-1, p["legL"]), (1, p["legR"])):
        a = math.radians(ang) * side * -1
        top = (hip[0] + side * hipw * 0.5, hip[1] - 2)
        if sit:
            knee = (top[0] + side * 3, top[1] + 4)
            foot = (knee[0] + side * 1, 0)
            pen.poly(taper(top, knee, 5.2, 5.0), C(pants))
            pen.poly(taper(knee, (foot[0], foot[1] - 3), 4.6, 4.0), C(pants))
            pen.poly(ellipse_pts(foot[0] + side * 1.5, foot[1] - 2, 5, 2.8, 16), C(shoes))
        else:
            kneebend = p.get("knee", 0) if side == -1 else p.get("knee2", 0)
            knee = rot((top[0], top[1] + L * 0.5), a, top)
            foot = rot((knee[0], knee[1] + L * 0.5 - 2), a + math.radians(kneebend) * side * -1, knee)
            w0 = 5.4 if not kid else 3.4
            pen.poly(taper(top, knee, w0, w0 * 0.92), C(pants))
            pen.poly(taper(knee, foot, w0 * 0.92, w0 * 0.78), C(pants))
            pen.poly(ellipse_pts(foot[0] + side * 1.8, foot[1] + 0.5, 5.5 if not kid else 4, 2.8, 16), C(shoes))


def arms(pen, cd, p, sc, tw, hs, kid):
    sleeve = cd["top"]
    skin = cd["skin"]
    L1 = 17 * hs if not kid else (8 if cd.get("baby") else 12)
    L2 = 16 * hs if not kid else (7 if cd.get("baby") else 11)
    r = 4.3 if not kid else (2.9 if cd.get("baby") else 3)
    for side, (a, e) in ((-1, p["aL"]), (1, p["aR"])):
        s = (sc[0] + side * (tw - 2), sc[1] + 3)
        aa = math.radians(a)
        ee = math.radians(a + e)
        el = (s[0] + side * math.sin(aa) * L1, s[1] + math.cos(aa) * L1)
        hd = (el[0] + side * math.sin(ee) * L2, el[1] + math.cos(ee) * L2)
        pen.poly(taper(s, el, r, r * 0.9), C(sleeve))
        if cd.get("dress") and not kid:
            pen.poly(taper(el, hd, r * 0.7, r * 0.62), C(skin))
        else:
            pen.poly(taper(el, hd, r * 0.88, r * 0.8), C(sleeve))
            pen.poly(ellipse_pts(hd[0], hd[1], r * 0.95, r * 0.6, 12), C(shade(sleeve, .85)), True, 0.3)
        hand = (hd[0] + side * math.sin(ee) * 2.5, hd[1] + math.cos(ee) * 2.5)
        pen.circle(hand[0], hand[1], 3.0 if not kid else 2.2, C(skin))
        held = p.get("held")
        if held and side == held[0]:
            draw_held(pen, held[1], hand, side)


def draw_held(pen, what, hand, side):
    x, y = hand
    if what == "polaroid":
        pts = [(x - 4, y - 9), (x + 4, y - 9), (x + 4, y + 1), (x - 4, y + 1)]
        pen.poly(pts, C((240, 238, 230)), True, 0.3)
        pen.poly([(x - 3, y - 8), (x + 3, y - 8), (x + 3, y - 2), (x - 3, y - 2)], C((150, 170, 150)), False)
    elif what == "album":
        pen.poly([(x - 9, y - 6), (x + 9, y - 6), (x + 9, y + 6), (x - 9, y + 6)], C((110, 60, 40)), True, 0.4)
        pen.line([(x - 7, y - 4), (x + 7, y - 4)], 0.3, C((200, 170, 90)))
    elif what == "plate_pizza" or what == "plate_cake":
        pen.poly(ellipse_pts(x, y - 1, 9, 3, 18), C((245, 245, 245)), True, 0.35)
        if what == "plate_pizza":
            pen.poly([(x - 4, y - 2), (x + 5, y - 3), (x, y - 1)], C((235, 180, 80)), True, 0.25)
        else:
            pen.poly([(x - 3, y - 6), (x + 3, y - 6), (x + 3, y - 1), (x - 3, y - 1)], C((240, 210, 220)), True, 0.25)
    elif what == "camera":
        pen.poly([(x - 6, y - 5), (x + 6, y - 5), (x + 6, y + 3), (x - 6, y + 3)], C((40, 40, 45)), True, 0.35)
        pen.circle(x, y - 1, 2.8, C((90, 110, 140)))
    elif what == "phone":
        pen.poly([(x - 2.5, y - 6), (x + 2.5, y - 6), (x + 2.5, y + 2), (x - 2.5, y + 2)], C((25, 25, 30)), True, 0.3)
        pen.poly([(x - 1.8, y - 5.2), (x + 1.8, y - 5.2), (x + 1.8, y + 1), (x - 1.8, y + 1)], C((150, 200, 255)), False)
    elif what == "monitor":
        pen.poly([(x - 4, y - 7), (x + 4, y - 7), (x + 4, y + 2), (x - 4, y + 2)], C((235, 235, 235)), True, 0.3)
        pen.poly([(x - 3, y - 6), (x + 3, y - 6), (x + 3, y - 1), (x - 3, y - 1)], C((120, 150, 120)), False)
    elif what == "bottle":
        pen.poly([(x - 1.5, y - 8), (x + 1.5, y - 8), (x + 1.5, y + 1), (x - 1.5, y + 1)], C((240, 240, 250)), True, 0.25)
        pen.poly([(x - 0.8, y - 10), (x + 0.8, y - 10), (x + 1.2, y - 8), (x - 1.2, y - 8)], C((230, 180, 120)), True, 0.2)
    elif what == "keys":
        pen.circle(x, y + 2, 1.4, None, True, 0.3)
        pen.line([(x, y + 3), (x + 1, y + 6)], 0.5, C((220, 190, 80)))
    elif what == "wrench":
        pen.line([(x, y), (x + side * 2, y + 12)], 1.0, C((150, 155, 160)))
    elif what == "spatula":
        pen.line([(x, y), (x + side * 6, y - 8)], 0.6, C((60, 60, 60)))
        pen.poly([(x + side * 5, y - 8), (x + side * 9, y - 12), (x + side * 11, y - 10), (x + side * 7, y - 6)], C((70, 70, 70)), True, 0.3)
    elif what == "popcorn":
        pen.poly([(x - 4, y - 7), (x + 4, y - 7), (x + 3, y + 2), (x - 3, y + 2)], C((230, 60, 60)), True, 0.3)
        for k in range(-2, 3):
            pen.circle(x + k * 1.6, y - 8, 1.4, C((250, 240, 200)), True, 0.15)


# ---------------------------------------------------------------- head
def hair_back(pen, cd, c, r, tilt, turn, wet):
    hair = cd["hair"]
    st = cd["style"]
    cx, cy = c
    def R(pts):
        return [rot((cx + x, cy + y), tilt, c) for x, y in pts]
    hx = turn * 1.5
    if st == "long":
        drop = 34
        pts = [(-r - 1 + hx, -2), (-r - 2 + hx, 10), (-r - 4 + hx, drop), (-r + 3 + hx, drop + 3), (-r + 8, drop - 2), (0, drop + 2),
               (r - 8, drop - 2), (r - 3 + hx, drop + 3), (r + 4 + hx, drop), (r + 2 + hx, 10), (r + 1 + hx, -2)] + ellipse_pts(hx, -1, r + 1.5, r + 2, 18, 0, -math.pi)[::-1][::-1]
        pts = [(-r - 1 + hx, 0)] + ellipse_pts(hx, -1, r + 1.6, r + 2.2, 20, math.pi, 2 * math.pi) + [(r + 1.5 + hx, 0), (r + 2 + hx, 12), (r + 4 + hx, drop), (r - 2, drop + 4), (r - 7, drop), (0, drop + 3), (-r + 7, drop), (-r + 2, drop + 4), (-r - 4 + hx, drop), (-r - 2 + hx, 12)]
        pen.poly(R(pts), C(hair))
    elif st == "wavy":
        drop = 16
        pts = [(-r - 1, 0)] + ellipse_pts(turn * 1.2, -1, r + 2, r + 2.4, 20, math.pi, 2 * math.pi) + [(r + 1.5, 0), (r + 4, 8), (r + 2.5, 12), (r + 5, drop), (r - 1, drop + 3), (r - 5, drop), (-r + 5, drop), (-r + 1, drop + 3), (-r - 5, drop), (-r - 2.5, 12), (-r - 4, 8)]
        pen.poly(R(pts), C(hair))
    elif st == "bob":
        pts = [(-r - 1, 0)] + ellipse_pts(turn * 1.2, -1, r + 2.5, r + 2.6, 20, math.pi, 2 * math.pi) + [(r + 2.5, 0), (r + 3, 9), (r - 1, 11), (-r + 1, 11), (-r - 3, 9)]
        pen.poly(R(pts), C(hair))
    elif st == "updo":
        pen.circle(*rot((cx + turn * 1.0, cy - r - 2.5), tilt, c), 5.2, C(shade(hair, .92)))
    elif st == "kid":
        pts = [(-r - 1, 0)] + ellipse_pts(turn * 1.2, -1, r + 2, r + 2.2, 20, math.pi, 2 * math.pi) + [(r + 2, 0), (r + 2, 8), (r - 1, 10), (-r + 1, 10), (-r - 2, 8)]
        pen.poly(R(pts), C(hair))


def face_shape(cx, cy, r, turn):
    pts = []
    n = 40
    for i in range(n):
        a = 2 * math.pi * i / n
        x = math.cos(a) * r
        y = math.sin(a) * r * 1.12
        if y > 0:  # jaw narrower
            x *= 1 - 0.18 * (y / (r * 1.12)) ** 2
            y *= 1.02
        pts.append((cx + x + turn * 0.6 * (1 if y > 0 else 0.3), cy + y))
    return pts


def draw_head(pen, cd, p, c, r, tilt, wet, name):
    cx, cy = c
    turn = p["turn"]
    skin = cd["skin"]
    expr = p["expr"]
    def R(pts):
        return [rot(q, tilt, c) for q in pts]
    def RP(x, y):
        return rot((x, y), tilt, c)
    # ears
    for side in (-1, 1):
        if side * turn < 0.55:
            ex = cx + side * (r - 0.5) + turn * 1.2
            pen.poly(R(ellipse_pts(ex, cy + 1, 2.6, 4, 14)), C(skin))
    pen.poly(R(face_shape(cx, cy, r, turn)), C(skin))
    if p.get("back"):
        pen.poly(R(ellipse_pts(cx, cy - 1, r + 1.4, r * 1.12 + 1, 30)), C(cd["hair"]))
        if cd["style"] == "updo":
            pen.circle(*RP(cx, cy - r - 1), 5.2, C(shade(cd["hair"], .92)))
        return
    if cd.get("earrings"):
        for side in (-1, 1):
            ex_ = cx + side * (r - 0.5) + turn * 1.2
            pen.poly(R([(ex_, cy + 4.5), (ex_ + 1.1, cy + 6), (ex_, cy + 7.6), (ex_ - 1.1, cy + 6)]), C((200, 235, 255)), True, 0.2)
    # cheek shading along jaw
    jaw = [(cx + x, cy + y) for x, y in [(-r * .85, r * .4), (-r * .4, r * 1.05), (r * .4, r * 1.05), (r * .85, r * .4)]]
    pen.line(R(jaw), 0.5, C(shade(skin, .86), 120))
    fx = cx + turn * 3.2
    # eyes
    ey = cy - 0.4
    exs = [fx - 5.2, fx + 5.2]
    lookx, looky = p["look"]
    blink = p["blink"]
    ex_open = {"scared": 1.25, "terrified": 1.4, "blank": 0.82, "creepy_smile": 1.2, "angry": 0.85, "sleep": 0, "pain": 0,
               "happy": 1.0, "sad": 0.95, "cry": 0.9, "happy_empty": 1.05, "cry_smile": 0.8}.get(expr, 1.0)
    erx, ery = 2.9, 3.4 * ex_open
    pupil = 1.45
    if expr in ("terrified", "scared"):
        pupil = 1.0
    if expr in ("blank", "creepy_smile", "smile_huge") and cd.get("creepy"):
        pupil = 1.9
    for i, ex in enumerate(exs):
        if ex_open == 0 or p.get("eyes_closed"):
            if expr == "pain":
                pen.line(R([(ex - 2.6, ey - 1.2), (ex + 0.4, ey), (ex - 2.6, ey + 1.2)] if i == 0 else [(ex + 2.6, ey - 1.2), (ex - 0.4, ey), (ex + 2.6, ey + 1.2)]), 0.6)
            else:
                pen.line(R(ellipse_pts(ex, ey - 0.5, 2.6, 1.6, 10, 0.15, math.pi - 0.15)), 0.55)
            continue
        if cd.get("eyebags"):
            pen.line(R(ellipse_pts(ex, ey + 1.2, 2.8, 2.6, 10, 0.3, math.pi - 0.3)), 0.6, C((150, 140, 160), 200))
        pen.poly(R(ellipse_pts(ex, ey, erx, ery, 24)), C((252, 250, 246)), True, 0.4)
        px = ex + lookx * 1.2
        py = ey + looky * 1.2
        if expr == "happy_empty":
            pen.circle(*RP(px, py), pupil * 1.15, C((20, 16, 18)), False)
        else:
            iris = {"emma": (90, 120, 70), "you": (80, 60, 40), "lily": (35, 35, 40), "diane": (70, 100, 140), "frank": (80, 90, 110)}.get(name, (60, 50, 40))
            pen.circle(*RP(px, py), pupil * 1.35, C(iris), False)
            pen.circle(*RP(px, py), pupil * 0.75, C((15, 12, 14)), False)
            if not (cd.get("creepy") and expr in ("blank", "creepy_smile", "smile_huge")):
                pen.circle(*RP(px - 0.5, py - 0.6), pupil * 0.35, C((255, 255, 255)), False)
        # eyelid / blink
        if blink > 0.02:
            top = ey - ery - 0.4
            bot = ey - ery + 2 * ery * blink + 0.3
            lid = [(ex - erx - 0.6, top), (ex + erx + 0.6, top), (ex + erx + 0.6, bot), (ex - erx - 0.6, bot)]
            pen.poly(R(lid), C(skin), False)
            pen.line(R([(ex - erx, bot), (ex + erx, bot)]), 0.45)
        if (expr in ("blank",) and not cd.get("baby")) or (cd.get("creepy") and expr == "neutral"):
            # heavy upper lid
            pen.poly(R([(ex - erx - .5, ey - ery - .5), (ex + erx + .5, ey - ery - .5), (ex + erx + .5, ey - ery * 0.35), (ex - erx - .5, ey - ery * 0.35)]), C(shade(skin, .97)), False)
            pen.line(R([(ex - erx, ey - ery * 0.35), (ex + erx, ey - ery * 0.35)]), 0.45)
        if cd.get("age"):
            pen.line(R([(ex + (3.8 if i else -3.8), ey + 0.4), (ex + (4.8 if i else -4.8), ey + 1.4)]), 0.25)
    # brows
    bt = {"worried": 18, "scared": 22, "terrified": 26, "sad": 20, "cry": 22, "angry": -24, "pain": -10, "cry_smile": 18}.get(expr, 0)
    blift = {"scared": -1.5, "terrified": -2.2, "creepy_smile": -1.0, "angry": 0.8}.get(expr, 0)
    hair = cd["hair"]
    browc = shade(hair, .8) if cd["style"] != "cap" else (110, 105, 100)
    for i, ex in enumerate(exs):
        s = -1 if i == 0 else 1
        a = math.radians(bt) * s
        b0 = (ex - 2.8, ey - ery - 2.2 + blift)
        b1 = (ex + 2.8, ey - ery - 2.2 + blift)
        mid = (ex, ey - ery - 2.2 + blift)
        b0 = rot(b0, a, mid)
        b1 = rot(b1, a, mid)
        pen.line(R([b0, b1]), 0.9, C(browc))
    # nose
    pen.line(R([(fx + 0.3, cy + 2.2), (fx - 0.7, cy + 4.6), (fx + 0.8, cy + 5.0)]), 0.4, C(shade(skin, .7)))
    if cd.get("mustache"):
        pen.poly(R([(fx - 5, cy + 7.6), (fx - 1, cy + 5.8), (fx, cy + 6.4), (fx + 1, cy + 5.8), (fx + 5, cy + 7.6), (fx + 3, cy + 8.4), (fx, cy + 7.4), (fx - 3, cy + 8.4)]), C((150, 145, 140)), True, 0.3)
    # cheeks
    if expr in ("happy", "smile", "laugh", "cry_smile") or (name in ("emma", "kemma", "klily", "diane")) or p.get("healthy"):
        for ex in exs:
            pen.circle(*RP(ex + (1 if ex > fx else -1) * 0.8, cy + 4.6), 1.8, C((240, 140, 130), 70), False)
    # mouth
    my = cy + 8.6
    mo = p["mouth"]
    lips = cd.get("lips", (150, 70, 70))
    dark = (90, 30, 35)
    if expr in ("creepy_smile", "smile_huge"):
        w = 7.5 if expr == "creepy_smile" else 12.5 + (p.get("grow", 0) * 3)
        pts = [(fx - w, my - 1.8)] + [(fx + x, my - 0.5 + 2.8 * (1 - (x / w) ** 2) + mo * 2) for x in [w * (i / 10 * 2 - 1) for i in range(11)]] + [(fx + w, my - 1.8)]
        pen.poly(R(pts), C(dark), True, 0.45)
        # teeth
        for k in range(-5, 6):
            x = fx + k * 1.3
            pen.line(R([(x, my - 1.4 + 0.1 * abs(k)), (x, my + 0.3)]), 0.3, C((235, 235, 220)))
        pen.line(R([(fx - w + 1, my - 1.2), (fx + w - 1, my - 1.2)]), 1.1, C((240, 238, 225)))
        return_hair_front(pen, cd, p, c, r, tilt, wet, turn)
        extras(pen, cd, p, c, r, tilt, expr, exs, ey, wet)
        return
    if mo > 0.06:
        h = 0.6 + 3.2 * mo
        w = 2.4 + 0.8 * mo
        if expr in ("scared", "terrified"):
            h += 1.0
        pen.poly(R(ellipse_pts(fx, my + h * 0.25, w, h * 0.55, 18)), C(dark), True, 0.4)
        if h > 1.6:
            pen.poly(R(ellipse_pts(fx, my + h * 0.55, w * 0.6, h * 0.22, 12)), C((200, 90, 95)), False)
    else:
        if expr in ("smile", "happy", "laugh", "smile_small", "happy_empty", "cry_smile", "smile_wide"):
            w = {"smile_small": 2.6, "happy": 4.2, "laugh": 4.4, "happy_empty": 4.6, "smile_wide": 6.2}.get(expr, 3.4)
            if expr in ("happy", "laugh", "happy_empty", "smile_wide"):
                pts = [(fx - w, my - 0.8)] + [(fx + x, my - 0.8 + 2.6 * (1 - (x / w) ** 2)) for x in [w * (i / 8 * 2 - 1) for i in range(9)]]
                pen.poly(R(pts), C(dark), True, 0.4)
                pen.line(R([(fx - w + 0.8, my - 0.5), (fx + w - 0.8, my - 0.5)]), 0.7, C((245, 245, 235)))
            else:
                pen.line(R(ellipse_pts(fx, my - 1.4, w, 1.8, 10, 0.3, math.pi - 0.3)), 0.55)
        elif expr in ("sad", "cry", "worried", "pain"):
            pen.line(R(ellipse_pts(fx, my + 1.2, 2.4, 1.2, 10, math.pi + 0.4, 2 * math.pi - 0.4)), 0.55)
        elif expr in ("scared", "terrified"):
            pen.poly(R(ellipse_pts(fx, my + 0.4, 1.6, 1.3, 12)), C(dark), True, 0.4)
        elif expr == "smile_nervous":
            pen.line(R([(fx - 3, my), (fx - 1.5, my - .6), (fx, my), (fx + 1.5, my - .6), (fx + 3, my)]), 0.5)
        elif expr == "angry":
            pen.line(R([(fx - 2.6, my + 0.6), (fx + 2.6, my + 0.6)]), 0.6)
        else:
            pen.line(R([(fx - 2.2, my), (fx + 2.2, my)]), 0.5)
    return_hair_front(pen, cd, p, c, r, tilt, wet, turn)
    extras(pen, cd, p, c, r, tilt, expr, exs, ey, wet)


def extras(pen, cd, p, c, r, tilt, expr, exs, ey, wet):
    def R(pts):
        return [rot(q, tilt, c) for q in pts]
    t = p.get("t", 0)
    if p.get("phone"):
        px_, py_ = c[0] + r + 0.5, c[1] - 1
        pen.poly(R([(px_ - 1, py_ - 5), (px_ + 3, py_ - 5), (px_ + 3, py_ + 9), (px_ - 1, py_ + 9)]), C((25, 25, 30)), True, 0.3)
        pen.circle(*rot((px_ + 2.5, py_ + 7), tilt, c), 2.8, C(cd["skin"]))
    if p.get("birthmark"):
        bx_, by_ = c[0] + r * 0.62, c[1] + r * 0.5
        pen.poly(R([(bx_, by_ + 1.2), (bx_ - 1.2, by_ - 0.2), (bx_ - 0.6, by_ - 1.0), (bx_, by_ - 0.4), (bx_ + 0.6, by_ - 1.0), (bx_ + 1.2, by_ - 0.2)]), C((140, 85, 60)), False)
    if expr in ("cry", "cry_smile"):
        for ex in exs:
            ln = 4 + 3 * ((t * 0.7) % 1.0)
            pen.line(R([(ex, ey + 3), (ex - 0.3, ey + 3 + ln)]), 0.9, C((60, 55, 70), 220) if cd.get("earrings") else C((150, 200, 240), 200))
    if expr == "terrified":
        x = c[0] + r * 0.8
        y = c[1] - r * 0.4 + 2 * ((t * 0.5) % 1.0)
        pen.poly(R([(x, y - 2), (x + 1.2, y + 0.8), (x, y + 1.6), (x - 1.2, y + 0.8)]), C((170, 215, 245)), True, 0.25)
    if wet:
        for k, ox in enumerate((-r * 0.9, r * 0.75, -r * 0.4)):
            ph = (t * 0.9 + k * 0.37) % 1.0
            y = c[1] + r * 0.6 + ph * 22
            pen.poly(R([(c[0] + ox, y - 1.6), (c[0] + ox + 0.9, y + 0.6), (c[0] + ox, y + 1.2), (c[0] + ox - 0.9, y + 0.6)]), C((150, 175, 200), int(220 * (1 - ph))), False)


def return_hair_front(pen, cd, p, c, r, tilt, wet, turn):
    hair = cd["hair"]
    st = cd["style"]
    cx, cy = c
    def R(pts):
        return [rot((cx + x, cy + y), tilt, c) for x, y in pts]
    hx = turn * 2.2
    if st == "short":
        pts = ellipse_pts(hx * .4, -1.5, r + 1.4, r + 1.4, 22, math.pi * 1.0, 2 * math.pi) + [(r + 1, -2), (r - 1, -5), (r - 4, -6.5), (hx + 3, -7.5), (hx, -6), (hx - 3, -8), (-r + 3, -6.5), (-r + 1, -3), (-r - 1, -2)]
        pen.poly(R(pts), C(hair))
        pen.line(R([(hx - 2, -r), (hx + 1, -8)]), 0.4, C(shade(hair, .7)))
    elif st == "long":
        h2 = shade(hair, 1.0)
        pts = ellipse_pts(hx * .3, -1.5, r + 1.6, r + 1.8, 22, math.pi, 2 * math.pi) + [(r + 1.6, 4), (r - 1.5, 0), (r - 3.5, -6.5), (hx + 1, -10.5), (hx - 1, -10.5), (-r + 3.5, -6.5), (-r + 1.5, 0), (-r - 1.6, 4)]
        pen.poly(R(pts), C(h2))
        # front locks over shoulders
        for s in (-1, 1):
            lock = [(s * (r - 1.0), -1), (s * (r + 1.8), 4), (s * (r + 1.5), 24), (s * (r - 2), 30), (s * (r - 3.5), 18), (s * (r - 2.5), 5)]
            pen.poly(R(lock), C(h2))
        pen.line(R([(hx, -r - 1.5), (hx + 0.2, -10)]), 0.35, C((70, 70, 80)))
        if wet:
            for s in (-1, 1):
                pen.line(R([(s * (r - 1), 8), (s * (r - 0.5), 22)]), 0.4, C((80, 95, 115), 200))
    elif st == "wavy":
        pts = ellipse_pts(hx * .3, -1.5, r + 1.8, r + 2, 22, math.pi, 2 * math.pi) + [(r + 1.8, 2), (r - 0.5, -2), (r - 3, -6), (hx + 4, -8), (hx - 2, -7.5), (-r + 4, -8.5), (-r + 1, -4), (-r - 1.8, 2)]
        pen.poly(R(pts), C(hair))
        pen.line(R([(hx - 4, -r), (hx - 1, -8)]), 0.35, C(shade(hair, .75)))
        pen.line(R([(hx + 4, -r + 1), (hx + 6, -7)]), 0.35, C(shade(hair, .75)))
    elif st == "bob":
        pts = ellipse_pts(hx * .3, -1.5, r + 2.6, r + 2.6, 22, math.pi, 2 * math.pi) + [(r + 2.6, 4), (r + 0.5, 6), (r - 1.5, -4), (hx + 2, -7), (hx - 4, -6.5), (-r + 1.5, -4), (-r - .5, 6), (-r - 2.6, 4)]
        pen.poly(R(pts), C(hair))
        for k in (-4, 0, 4):
            pen.line(R([(hx + k, -r - 1), (hx + k * 1.2 + 1, -6)]), 0.3, C(shade(hair, .8)))
    elif st == "updo":
        pts = ellipse_pts(hx * .3, -1.5, r + 1.6, r + 1.7, 22, math.pi, 2 * math.pi) + [(r + 1.6, -1), (r - 0.5, -3), (r - 3, -7), (hx + 3, -9.5), (hx - 6, -8.5), (-r + 2, -5), (-r - 0.2, -1), (-r - 1.6, -1)]
        pen.poly(R(pts), C(hair))
        for k in (-5, -1, 3):
            pen.line(R([(hx + k, -r - 1), (hx + k + 4, -7)]), 0.3, C(shade(hair, .8)))
    elif st == "baby":
        pen.poly(R([(hx - 3, -r + 0.5), (hx - 1, -r - 3.5), (hx + 1.5, -r - 1), (hx + 3.5, -r - 3), (hx + 3, -r + 1)]), C(hair), True, 0.3)
        pen.line(R(ellipse_pts(hx + 1, -r - 2.5, 1.6, 1.6, 10, 0.5, 4.5)), 0.35, C(shade(hair, .8)))
    elif st == "kid":
        pts = ellipse_pts(hx * .3, -1.5, r + 2, r + 2, 22, math.pi, 2 * math.pi) + [(r + 2, 6), (r, 7), (r - 1, -3), (r - 4, -5), (-r + 4, -5), (-r + 1, -3), (-r, 7), (-r - 2, 6)]
        pen.poly(R(pts), C(hair))
        pen.circle(*rot((cx + r - 1, cy - r + 1), tilt, c), 2.0, C((240, 90, 110)))
    elif st == "cap":
        # gray sides
        for s in (-1, 1):
            pen.poly(R([(s * (r + 0.6), -6), (s * (r + 1.2), 1), (s * (r - 1.2), 2), (s * (r - 1.6), -5)]), C(hair))
        capc = (45, 72, 52)
        pen.poly(R(ellipse_pts(hx * .3, -4, r + 1.6, r + 0.8, 22, math.pi, 2 * math.pi) + [(r + 1.6, -4), (-r - 1.6, -4)]), C(capc))
        pen.poly(R([(-r - 1.6 + hx, -4), (r + 1.6 + hx, -4), (r + 3 + hx, -1.8), (-r - 3 + hx, -1.8)]), C(shade(capc, .8)))
        pen.poly(R([(hx - 4, -r + 1), (hx + 4, -r + 1), (hx + 4, -r + 6), (hx - 4, -r + 6)]), C((235, 230, 215)), True, 0.3)


# ---------------------------------------------------------------- animation
def blink_at(t, seed):
    # blink roughly every 3-5 s, 0.15s long
    period = 3.2 + (seed % 7) * 0.31
    ph = (t + seed * 0.77) % period
    if ph < 0.16:
        return math.sin(ph / 0.16 * math.pi)
    return 0.0


def make_pose(actor, t, dur, mouth_env, seed):
    """Compute the pose for actor dict at local time t."""
    p = default_pose()
    anim = actor.get("anim", "idle")
    p["expr"] = actor.get("expr", "neutral")
    p["sit"] = actor.get("sit", False)
    look = actor.get("look", (0, 0))
    p["look"] = (look[0], look[1])
    p["turn"] = max(-1, min(1, look[0] * 0.55))
    p["t"] = t
    br = math.sin(t * 2 * math.pi / 3.6 + seed)
    p["breath"] = br
    p["bob"] = br * 0.35
    p["head_tilt"] = math.sin(t * 0.7 + seed) * 2.0
    p["hy"] = -br * 0.3
    still = anim == "still"
    if not still:
        p["blink"] = blink_at(t, seed)
        # small eye saccades
        sx = math.sin(t * 0.9 + seed * 2.1)
        if abs(sx) > 0.92:
            p["look"] = (look[0] + 0.25 * (1 if sx > 0 else -1), look[1])
    else:
        p["head_tilt"] = 3.0 + math.sin(t * 0.25) * 0.8
        p["bob"] = 0
        p["breath"] = 0
        p["hy"] = 0
    if actor.get("shake"):
        p["dx"] += math.sin(t * 47) * 0.35
        p["head_tilt"] += math.sin(t * 31) * 1.2
    talking = anim in ("talk", "whisper") or actor.get("talk")
    if talking:
        m = mouth_env
        if actor.get("whisper"):
            m *= 0.6
        p["mouth"] = m
        p["head_tilt"] += mouth_env * 2.0 * math.sin(t * 5)
        # talking gestures
        g = math.sin(t * 1.7 + seed)
        p["aR"] = (14 + 10 * max(0, g), -40 - 30 * max(0, g))
    if anim == "laugh":
        p["expr"] = "happy"
        p["mouth"] = 0.5 + 0.3 * abs(math.sin(t * 9))
        p["bob"] += abs(math.sin(t * 9)) * 0.8
        p["head_tilt"] += 4 * math.sin(t * 4)
    if p["sit"]:
        p["aL"] = (14, -55)
        p["aR"] = (14, -55)
        if talking:
            g = math.sin(t * 1.7 + seed)
            p["aR"] = (20 + 10 * max(0, g), -70 - 20 * max(0, g))
    if anim == "walk":
        x1 = actor.get("x1", actor["x"])
        sp = 2.4
        ph = t * sp * math.pi
        p["legL"] = 18 * math.sin(ph)
        p["legR"] = -18 * math.sin(ph)
        p["aL"] = (10 + 14 * math.sin(ph), -10)
        p["aR"] = (10 - 14 * math.sin(ph), -10)
        p["bob"] = -abs(math.sin(ph)) * 1.4
    if anim == "drag":
        ph = t * 2.6 * math.pi
        p["legL"] = 18 * math.sin(ph)
        p["legR"] = -18 * math.sin(ph)
        p["aL"] = (75, -5)
        p["lean"] = 6
        p["bob"] = -abs(math.sin(ph)) * 1.4
    if anim == "point":
        k = min(1, t / 0.6)
        p["aR"] = (8 + 80 * k, -5 * k)
    if anim == "hug":
        k = min(1, t / 0.8)
        p["aL"] = (8 + 40 * k, -70 * k)
        p["aR"] = (8 + 40 * k, -70 * k)
    if anim in ("handshake", "handshake_r"):
        sh = math.sin(t * 10) * 6 if t < 2 else 0
        if anim == "handshake":
            p["aL"] = (40 + sh, -30)
        else:
            p["aR"] = (40 + sh, -30)
    if anim == "give" or actor.get("polaroid"):
        k = min(1, t / 0.9)
        p["aL"] = (10 + 62 * k, -20 * k)
        p["held"] = (-1, "polaroid")
    if anim == "camera":
        p["aL"] = (35, -150)
        p["aR"] = (35, -150)
        p["held"] = (1, "camera")
    if actor.get("plate"):
        p["aL"] = (16, -70)
        p["aR"] = (16, -70)
        p["held"] = (1, "plate_" + actor["plate"])
    if actor.get("album"):
        p["aL"] = (25, -80)
        p["aR"] = (25, -80)
        p["held"] = (1, "album")
    if actor.get("offer"):
        p["aR"] = (55, -40)
        p["held"] = (1, "popcorn")
    if anim == "wave":
        p["aR"] = (150, -20 + 25 * math.sin(t * 8))
    if anim == "cook":
        p["aL"] = (35 + 5 * math.sin(t * 3), -60)
        p["held"] = (-1, "spatula")
        p["head_tilt"] += 4 * math.sin(t * 2.2)
    if anim == "wrench":
        p["aR"] = (30 + 8 * math.sin(t * 4), -40)
        p["held"] = (1, "wrench")
        p["lean"] = 8
    if anim == "sit_bucket":
        p["sit"] = True
        p["lean"] = 6
        p["aL"] = (18, -40)
        p["aR"] = (18, -40)
        p["held"] = (1, "polaroid")
    if anim == "rub_face":
        p["sit"] = True
        k = 0.5 + 0.5 * math.sin(t * 1.5)
        p["aL"] = (30, -125 - 10 * k)
        p["aR"] = (30, -125 - 10 * k)
        p["eyes_closed"] = True
        p["head_tilt"] += 6
    if anim == "flinch":
        k = max(0, 1 - t / 0.5)
        p["head_tilt"] += -10 * k
        p["dx"] += math.sin(t * 40) * 1.2 * k
    if anim == "shake":
        p["dx"] += math.sin(t * 50) * 0.6
        p["aL"] = (30, -100)
        p["aR"] = (30, -100)
    if anim == "mow":
        p["aL"] = (40, -40)
        p["aR"] = (40, -40)
        ph = t * 2 * math.pi
        p["legL"] = 12 * math.sin(ph)
        p["legR"] = -12 * math.sin(ph)
    if anim == "cpr":
        p["lean"] = 25
        p["aL"] = (60, -10)
        p["aR"] = (60, -10)
        p["bob"] = abs(math.sin(t * 9)) * 1.5
    if anim == "drive":
        p["aL"] = (25, -70 + 3 * math.sin(t * 1.1))
        p["aR"] = (25, -70 - 3 * math.sin(t * 1.1))
    if anim == "climb":
        k = min(1, t / 1.6)
        p["hy"] = (1 - k) * -14
        p["dx"] = (1 - k) * 18
    if anim == "eat":
        p["aR"] = (20, -100 - 25 * abs(math.sin(t * 2)))
        p["mouth"] = 0.25 * abs(math.sin(t * 6))
    if actor.get("hold"):
        p["aL" if actor["x"] > 0.5 else "aR"] = (25, -10)
    if anim == "sleep":
        p["eyes_closed"] = True
    if anim == "whisper":
        p["lean"] = -6 if look[0] < 0 else 6
    if p["expr"] in ("sleep",):
        p["eyes_closed"] = True
    if p["expr"] == "pain":
        p["eyes_closed"] = False
    if actor.get("healthy"):
        p["healthy"] = True
    if actor.get("back"):
        p["back"] = True
    if actor.get("eyes_shut"):
        p["eyes_closed"] = True
    if actor.get("phone"):
        p["phone"] = True
    if actor.get("birthmark"):
        p["birthmark"] = True
    if actor.get("grow"):
        p["grow"] = min(1.0, t / max(1.0, dur))
    if actor.get("held_phone"):
        p["aR"] = (30, -110); p["held"] = (1, "phone")
    if actor.get("monitor"):
        p["aR"] = (30, -80); p["held"] = (1, "monitor")
    if actor.get("keys"):
        p["aR"] = (20, -20); p["held"] = (1, "keys")
    if anim == "baby":
        p["sit"] = True
        if p["expr"] in ("happy", "smile"):
            p["aL"] = (60 + 35 * math.sin(t * 5 + seed), -30)
            p["aR"] = (60 + 35 * math.sin(t * 5.6 + seed + 1), -30)
            p["head_tilt"] += 5 * math.sin(t * 3)
            p["mouth"] = 0.3 * abs(math.sin(t * 4)) if p["expr"] == "happy" else 0
        elif p["expr"] == "cry":
            p["aL"] = (100 + 20 * math.sin(t * 9), -20)
            p["aR"] = (100 + 20 * math.sin(t * 9.5), -20)
            p["mouth"] = 0.7 + 0.3 * math.sin(t * 7)
            p["dx"] += math.sin(t * 25) * 0.3
        else:
            p["aL"] = (25, -40)
            p["aR"] = (25, -40)
        if actor["c"] == "fakenoah":
            p["blink"] = 0.0
            p["bob"] = 0.0
            p["breath"] = 0.0
            p["head_tilt"] = 4.0
        if actor.get("rock"):
            p["dx"] += math.sin(t * 2.5) * 1.5
    if anim == "lift":
        p["aL"] = (70, -60); p["aR"] = (70, -60)
    if anim == "feed":
        p["aR"] = (45, -95); p["aL"] = (35, -60); p["held"] = (1, "bottle")
    if anim == "hold":
        p["aL"] = (30, -85); p["aR"] = (30, -85)
    if anim == "lay":
        p["lean"] = 14; p["aL"] = (55, -25); p["aR"] = (55, -25)
    if anim == "touch":
        p["aR"] = (62, -8)
    if anim == "carry":
        p["aL"] = (88, 0); p["aR"] = (-60, -20); p["lean"] = -4
        p["dx"] += math.sin(t * 20) * 0.3
    if anim in ("run", "backaway"):
        sp = 4.0 if anim == "run" else 1.4
        ph = t * sp * math.pi
        p["legL"] = 22 * math.sin(ph) if anim == "run" else 12 * math.sin(ph)
        p["legR"] = -p["legL"]
        if anim == "run":
            p["aL"] = (10 + 30 * math.sin(ph), -40)
            p["aR"] = (10 - 30 * math.sin(ph), -40)
            p["lean"] = 6
        else:
            p["aL"] = (25, -30); p["aR"] = (25, -30)
        p["bob"] = -abs(math.sin(ph)) * 1.4
    if anim == "push":
        p["lean"] = -12; p["aL"] = (75, -30); p["aR"] = (75, -30)
        p["dx"] += math.sin(t * 30) * 0.4
    if anim == "tie":
        p["aL"] = (30, -140 + 6 * math.sin(t * 4)); p["aR"] = (30, -140 - 6 * math.sin(t * 4))
    if anim == "sleep_bed":
        p["eyes_closed"] = True
    return p
