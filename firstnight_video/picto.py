"""White pictogram (stickman) characters with a simple skeleton + animation poses."""
import math
from PIL import Image, ImageDraw

SS = 2
WHITE = (238, 236, 230, 255)
BACK = (196, 194, 188, 255)
LINE = (150, 148, 144, 255)
DARK = (30, 28, 26, 255)

# per character proportions (units: kid standing height ~100)
CH = {
    "kid":     dict(h=1.0, head=11.0, hair="messy", hood=True),
    "adult":   dict(h=1.25, head=10.5, hair="messy"),
    "mom":     dict(h=1.22, head=10.0, hair="ponytail", dress=True),
    "kidmom":  dict(h=1.0, head=11.0, hair="ponytail", dress=True),
    "dad":     dict(h=1.3, head=10.0, hair="short", glasses=True),
    "grandma": dict(h=1.15, head=10.0, hair="bun", glasses=True, dress=True, cardigan=True),
}


def rot(p, a, o):
    c, s = math.cos(a), math.sin(a)
    x, y = p[0] - o[0], p[1] - o[1]
    return (o[0] + x * c - y * s, o[1] + x * s + y * c)


def capsule(d, p0, p1, r, col):
    d.line([p0, p1], fill=col, width=int(2 * r))
    for p in (p0, p1):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def default_pose():
    return dict(lean=0.0, bob=0.0, dx=0.0, tilt=0.0, aL=(10, 0), aR=(10, 0), legL=0.0, legR=0.0,
                kneeL=0.0, kneeR=0.0, crouch=0.0, sit=False, kneel=False, lie=False, held=None, face=1,
                smile=False, phone=False)


def draw_person(name, p, u):
    """Render a pictogram person. Returns (RGBA, anchor_x, anchor_y) with anchor at feet centre."""
    cd = CH[name]
    hs = cd["h"]
    W, H = int(90 * hs * u * SS), int(130 * hs * u * SS)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    U = u * SS
    ox, oy = W / 2, H - 8 * U
    def P(x, y):
        return (ox + x * U, oy + y * U)
    f = p["face"]
    # skeleton
    leg = 42 * hs if name != "kid" else 42
    if name in ("kidmom",):
        leg = 42
    torso = 30 * hs
    hip_y = -leg + p["bob"] + p["crouch"] * leg * 0.35
    if p["sit"]:
        hip_y = -leg * 0.52 + p["bob"]
    if p["kneel"]:
        hip_y = -leg * 0.55 + p["bob"]
    hip = (p["dx"], hip_y)
    lean = math.radians(p["lean"]) * f
    sh = rot((hip[0], hip[1] - torso), lean, hip)
    head_r = cd["head"]
    neck = rot((hip[0], hip[1] - torso - 3), lean, hip)
    head = rot((hip[0], hip[1] - torso - 4 - head_r), lean, hip)
    head = (head[0] + p.get("hx", 0), head[1] + p.get("hy", 0))
    limb_r = 4.0 if name in ("kid", "kidmom") else 3.7
    arm_r = 3.3 if name in ("kid", "kidmom") else 3.1

    def legs(col, which):
        for side, ang, kn in ((-1, p["legL"], p["kneeL"]), (1, p["legR"], p["kneeR"])):
            if (side == -f) != (which == "back"):
                continue
            top = (hip[0] + side * 4.5, hip[1])
            if p["sit"]:
                knee = (top[0] + f * leg * 0.48, top[1])
                foot = (knee[0] + f * 2, knee[1] + leg * 0.5)
            elif p["kneel"]:
                knee = (top[0] + f * leg * 0.2, top[1] + leg * 0.45)
                foot = (knee[0] - f * leg * 0.48, knee[1] + 1)
            else:
                a = math.radians(ang)
                knee = (top[0] + math.sin(a) * leg * 0.5, top[1] + math.cos(a) * leg * 0.5)
                b = a - math.radians(kn) * f
                foot = (knee[0] + math.sin(b) * leg * 0.5, knee[1] + math.cos(b) * leg * 0.5)
            capsule(d, P(*top), P(*knee), limb_r * U, col)
            capsule(d, P(*knee), P(*foot), limb_r * U, col)
            fx = foot[0] + f * 3
            capsule(d, P(foot[0] - f * 1, foot[1] + 0.5), P(fx, foot[1] + 0.5), limb_r * 0.9 * U, col)

    def arms(col, which):
        for side, (a, e) in ((-1, p["aL"]), (1, p["aR"])):
            if (side == -f) != (which == "back"):
                continue
            s = (sh[0] + side * 7.5, sh[1] + 3)
            aa = math.radians(a)
            ee = math.radians(a + e)
            L1, L2 = 15 * hs, 14 * hs
            el = (s[0] + side * math.sin(aa) * L1, s[1] + math.cos(aa) * L1)
            hd = (el[0] + side * math.sin(ee) * L2, el[1] + math.cos(ee) * L2)
            capsule(d, P(*s), P(*el), arm_r * U, col)
            capsule(d, P(*el), P(*hd), arm_r * U, col)
            d.ellipse([P(*hd)[0] - 3.6 * U, P(*hd)[1] - 3.6 * U, P(*hd)[0] + 3.6 * U, P(*hd)[1] + 3.6 * U], fill=col)
            if p.get("held") and p["held"][0] == side:
                held(d, p["held"][1], P(*hd), U, side)

    arms(BACK, "back")
    legs(BACK, "back")
    # torso
    tw, bw = 9.5, 8.0
    if cd.get("dress"):
        hem = 14 if not p["sit"] else 4
        pts = [rot((hip[0] - tw, hip[1] - torso + 2), lean, hip), rot((hip[0] + tw, hip[1] - torso + 2), lean, hip),
               (hip[0] + bw + 6, hip[1] + hem), (hip[0] - bw - 6, hip[1] + hem)]
    else:
        pts = [rot((hip[0] - tw, hip[1] - torso + 2), lean, hip), rot((hip[0] + tw, hip[1] - torso + 2), lean, hip),
               (hip[0] + bw, hip[1] + 2), (hip[0] - bw, hip[1] + 2)]
    legs(WHITE, "front")
    d.polygon([P(*q) for q in pts], fill=WHITE)
    for q in pts[:2]:
        d.ellipse([P(*q)[0] - 4 * U, P(*q)[1] - 4 * U, P(*q)[0] + 4 * U, P(*q)[1] + 4 * U], fill=WHITE)
    # details
    if cd.get("hood"):
        c = rot((hip[0], hip[1] - torso + 2), lean, hip)
        d.arc([P(c[0] - 7, c[1] - 4)[0], P(c[0] - 7, c[1] - 4)[1], P(c[0] + 7, c[1] + 6)[0], P(c[0] + 7, c[1] + 6)[1]], 0, 180, fill=LINE, width=int(1.4 * U))
        pk = (hip[0], hip[1] - 7)
        d.line([P(pk[0] - 6, pk[1]), P(pk[0] + 6, pk[1])], fill=LINE, width=int(1.2 * U))
    if cd.get("cardigan"):
        a0 = rot((hip[0], hip[1] - torso + 3), lean, hip)
        d.line([P(*a0), P(hip[0], hip[1] + 10)], fill=LINE, width=int(1.2 * U))
    # neck + head
    capsule(d, P(*neck), P(*rot((neck[0], neck[1] - 4), lean, neck)), 3 * U, WHITE)
    hx, hy = P(*head)
    R = head_r * U
    hair = cd.get("hair")
    if hair == "ponytail":
        tx = hx - f * R * 1.05
        d.ellipse([tx - R * .45, hy - R * .3, tx + R * .45, hy + R * .9], fill=WHITE)
    if hair == "bun":
        d.ellipse([hx - f * R * .2 - R * .45, hy - R * 1.45, hx - f * R * .2 + R * .45, hy - R * .6], fill=WHITE)
    d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=WHITE)
    if hair == "messy":
        for k in range(-2, 3):
            a = math.radians(-90 + k * 22)
            bx, by = hx + math.cos(a) * R * 0.92, hy + math.sin(a) * R * 0.92
            d.polygon([(bx - 2.2 * U, by), (bx + 2.2 * U, by), (bx + math.cos(a) * 4.5 * U + f * 1.5 * U, by + math.sin(a) * 4.5 * U)], fill=WHITE)
        d.arc([hx - R * .9, hy - R * .9, hx + R * .9, hy + R * .9], 200, 340, fill=LINE, width=int(1.2 * U))
    if hair == "ponytail" or hair == "bun":
        d.arc([hx - R * .9, hy - R * .95, hx + R * .9, hy + R * .85], 190, 350, fill=LINE, width=int(1.2 * U))
    if hair == "short":
        d.arc([hx - R * .92, hy - R * .92, hx + R * .92, hy + R * .92], 195, 345, fill=LINE, width=int(1.6 * U))
    if cd.get("glasses"):
        gx = hx + f * R * .35
        d.ellipse([gx - R * .3, hy - R * .2, gx + R * .3, hy + R * .2], outline=LINE, width=int(1.3 * U))
        d.line([(gx - f * R * .3, hy), (hx - f * R * .9, hy - R * .1)], fill=LINE, width=int(1.1 * U))
    if p.get("smile"):
        d.arc([hx + f * R * .1 - R * .4, hy - R * .1, hx + f * R * .1 + R * .4, hy + R * .55], 20, 160, fill=LINE, width=int(1.5 * U))
    if p.get("phone"):
        px = hx + f * R * .95
        d.rounded_rectangle([px - 2 * U, hy - 5 * U, px + 2 * U, hy + 6 * U], int(U), fill=LINE)
    arms(WHITE, "front")
    out = img.resize((W // SS, H // SS), Image.LANCZOS)
    return out, ox / SS, oy / SS


def held(d, what, h, U, side):
    x, y = h
    if what == "paper":
        d.rectangle([x - 5 * U, y - 12 * U, x + 5 * U, y + 1 * U], fill=(250, 250, 245, 255))
        for k in range(3):
            d.line([(x - 3.5 * U, y - 9 * U + k * 3 * U), (x + 3.5 * U, y - 9 * U + k * 3 * U)], fill=LINE, width=int(U))
    elif what == "phone":
        d.rounded_rectangle([x - 2.5 * U, y - 7 * U, x + 2.5 * U, y + 2 * U], int(U), fill=LINE)
        d.rectangle([x - 1.6 * U, y - 6 * U, x + 1.6 * U, y + 1 * U], fill=(150, 200, 255, 255))
    elif what == "book":
        d.polygon([(x - 9 * U, y - 6 * U), (x, y - 3 * U), (x + 9 * U, y - 6 * U), (x + 9 * U, y + 3 * U), (x, y + 5 * U), (x - 9 * U, y + 3 * U)], fill=(250, 250, 245, 255))
        d.line([(x, y - 3 * U), (x, y + 5 * U)], fill=LINE, width=int(U))
    elif what == "pen":
        d.line([(x, y), (x + side * 4 * U, y - 7 * U)], fill=LINE, width=int(1.3 * U))
    elif what == "bag":
        d.rounded_rectangle([x - 6 * U, y, x + 6 * U, y + 12 * U], int(2 * U), fill=(238, 236, 230, 255))


def draw_dog(p, u, t):
    """Side-view pictogram dog. p: dict(anim, face). Anchor at feet centre."""
    U = u * SS
    W, H = int(120 * U), int(90 * U)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = p.get("face", 1)
    ox, oy = W / 2, H - 6 * U
    def P(x, y):
        return (ox + x * f * U, oy + y * U)
    anim = p.get("anim", "idle")
    run = anim in ("run", "jump")
    ph = t * (14 if run else 0)
    by = -abs(math.sin(ph)) * 4 if run else 0
    if anim == "jump":
        by -= 10 * abs(math.sin(t * 3))
    if anim == "sleep":
        d.ellipse([ox - 30 * U, oy - 24 * U, ox + 30 * U, oy], fill=WHITE)
        hx, hy = ox + f * 28 * U, oy - 14 * U
        d.ellipse([hx - 11 * U, hy - 10 * U, hx + 11 * U, hy + 10 * U], fill=WHITE)
        d.ellipse([hx - f * 4 * U - 4 * U, hy - 8 * U, hx - f * 4 * U + 4 * U, hy + 8 * U], fill=BACK)
        capsule(d, (ox - f * 28 * U, oy - 8 * U), (ox - f * 10 * U, oy - 2 * U), 3 * U, BACK)
        out = img.resize((W // SS, H // SS), Image.LANCZOS)
        return out, ox / SS, oy / SS
    # legs
    for k, (lx, ph0) in enumerate(((-18, 0), (-12, math.pi), (16, math.pi), (22, 0))):
        sw = math.sin(ph + ph0) * 9 if run else 0
        col = BACK if k in (1, 3) else WHITE
        capsule(d, P(lx, -24 + by), P(lx + sw, -1), 3.4 * U, col)
    # body
    b0, b1 = P(-26, -38 + by), P(26, -18 + by)
    d.rounded_rectangle([min(b0[0], b1[0]), b0[1], max(b0[0], b1[0]), b1[1]], int(10 * U), fill=WHITE)
    # tail
    wag = math.sin(t * 16) * 14 if anim in ("idle", "run", "jump", "wag") else 0
    capsule(d, P(-26, -34 + by), P(-40, -48 + by + wag * 0.4), 2.6 * U, WHITE)
    # head
    capsule(d, P(22, -36 + by), P(30, -46 + by), 6 * U, WHITE)
    hx, hy = P(32, -50 + by)
    d.ellipse([hx - 10 * U, hy - 10 * U, hx + 10 * U, hy + 10 * U], fill=WHITE)
    sx, sy = P(44, -46 + by)
    d.rounded_rectangle([min(hx, sx), sy - 5 * U, max(hx, sx) + 4 * U, sy + 5 * U], int(5 * U), fill=WHITE)
    ex, ey = P(28, -58 + by)
    d.ellipse([ex - 4.5 * U, ey, ex + 4.5 * U, ey + 15 * U], fill=BACK)
    nx, ny = P(48, -47 + by)
    d.ellipse([nx - 2.2 * U, ny - 2 * U, nx + 2.2 * U, ny + 2 * U], fill=DARK)
    if anim == "jump":
        tx, ty = P(46, -40 + by)
        d.ellipse([tx - 2 * U, ty, tx + 2 * U, ty + 6 * U], fill=(230, 110, 120, 255))
    out = img.resize((W // SS, H // SS), Image.LANCZOS)
    return out, ox / SS, oy / SS


def make_pose(a, t, dur, seed):
    p = default_pose()
    anim = a.get("anim", "idle")
    p["face"] = a.get("face", 1)
    br = math.sin(t * 2 * math.pi / 3.4 + seed)
    p["bob"] = br * 0.4
    p["tilt"] = 0
    if anim in ("walk", "phone_pace", "carry"):
        sp = 2.2
        ph = t * sp * math.pi
        p["legL"] = 22 * math.sin(ph); p["legR"] = -22 * math.sin(ph)
        p["kneeL"] = 18 * max(0, math.sin(ph)); p["kneeR"] = 18 * max(0, -math.sin(ph))
        p["aL"] = (12 - 18 * math.sin(ph), -10); p["aR"] = (12 + 18 * math.sin(ph), -10)
        p["bob"] = -abs(math.sin(ph)) * 1.6
        if anim == "phone_pace":
            p["aR"] = (40, -150); p["phone"] = True
            p["face"] = 1 if math.sin(t * 0.5) > 0 else -1
        if anim == "carry":
            p["aL"] = (20, -60); p["aR"] = (20, -60); p["held"] = (1, "bag")
    elif anim == "talk":
        g = math.sin(t * 2.0 + seed)
        p["aR"] = (25 + 15 * max(0, g), -50 - 20 * max(0, g))
        p["hy"] = math.sin(t * 6) * 0.4 * (0.5 + 0.5 * math.sin(t * 1.3))
    elif anim == "worry":
        p["aL"] = (35, -140); p["aR"] = (35, -140)
        p["hy"] = 1.0; p["lean"] = 5
    elif anim == "stick_note":
        k = min(1, t / 1.2)
        p["aR"] = (20 + 70 * k, -20); p["held"] = (1, "paper")
    elif anim == "laugh":
        p["bob"] += abs(math.sin(t * 9)) * 1.2
        p["aL"] = (20, -40); p["aR"] = (20, -40); p["smile"] = True
    elif anim == "kneel_hold":
        p["kneel"] = True
        p["aL"] = (55, -40); p["aR"] = (55, -40)
    elif anim == "held":
        p["aL"] = (45, -20); p["aR"] = (45, -20)
    elif anim == "wave":
        p["aR"] = (150, -15 + 25 * math.sin(t * 7))
    elif anim == "read":
        p["aR"] = (30, -110); p["aL"] = (20, -20); p["hy"] = -0.6
    elif anim in ("sit_couch", "sit_hug", "yawn"):
        p["sit"] = True
        p["aL"] = (20, -50); p["aR"] = (20, -50)
        if anim == "sit_hug":
            p["aL"] = (45, -100); p["aR"] = (45, -100); p["dx"] = math.sin(t * 30) * 0.3
        if anim == "yawn":
            k = max(0, math.sin(t * 1.2))
            p["aR"] = (30 + 120 * k, -30 - 40 * k)
    elif anim == "lie_couch":
        p["sit"] = True; p["lie"] = True
    elif anim in ("reach", "reach_frozen"):
        k = min(1, t / 0.7) if anim == "reach" else 1
        p["aR"] = (20 + 140 * k, -10 * k)
    elif anim == "yank":
        k = min(1, t / 0.25)
        p["aR"] = (160 - 120 * k, -20); p["lean"] = -10 * k
    elif anim in ("breathe", "exhale"):
        p["bob"] = math.sin(t * 6) * 1.2
        p["aL"] = (25, -60); p["aR"] = (25, -60); p["lean"] = 8
    elif anim in ("shake", "phone_ear_shake", "turn_follow"):
        p["dx"] = math.sin(t * 45) * 0.5
        p["aL"] = (35, -120); p["aR"] = (35, -120)
        if anim == "phone_ear_shake":
            p["aR"] = (40, -150); p["phone"] = True; p["aL"] = (20, -20)
        if anim == "turn_follow":
            p["face"] = 1 if (t % 4) < 2 else -1
    elif anim == "whisper":
        p["aR"] = (30, -100); p["lean"] = 6
    elif anim == "knob":
        p["aR"] = (70, -15); p["lean"] = 4
    elif anim == "back_off":
        k = min(1, t / 0.6)
        p["aR"] = (70 - 50 * k, -15); p["dx"] = -6 * k
    elif anim == "phone_ear":
        p["aR"] = (40, -150); p["phone"] = True
    elif anim in ("climb", "descend", "look_up"):
        p["aL"] = (20, -20); p["aR"] = (20, -20)
        if anim != "look_up":
            ph = t * 2.6 * math.pi
            p["legL"] = 18 * math.sin(ph); p["legR"] = -18 * math.sin(ph)
            p["kneeL"] = 40 * max(0, math.sin(ph)); p["kneeR"] = 40 * max(0, -math.sin(ph))
        else:
            p["hy"] = -1.5; p["lean"] = -6
    elif anim == "sit_floor":
        p["sit"] = True; p["aL"] = (20, -50); p["aR"] = (20, -50)
    elif anim == "read_story":
        p["sit"] = True; p["aL"] = (50, -60); p["aR"] = (50, -60); p["held"] = (1, "book")
    elif anim == "sit_wall":
        p["sit"] = True; p["aL"] = (30, -80); p["aR"] = (30, -80); p["hx"] = 2; p["hy"] = 1.5
    elif anim == "stretch":
        k = 0.5 + 0.5 * math.sin(t * 1.5)
        p["aL"] = (150 + 15 * k, 0); p["aR"] = (150 + 15 * k, 0)
    elif anim == "speak_up":
        p["aL"] = (20, -30); p["aR"] = (20, -30); p["hy"] = -1; p["smile"] = True
    elif anim == "smile":
        p["smile"] = True; p["aL"] = (25, -60); p["aR"] = (25, -60)
    elif anim == "fall_back":
        k = min(1, t / 0.6)
        p["lean"] = -60 * k; p["crouch"] = 0.6 * k; p["aL"] = (120, 0); p["aR"] = (120, 0); p["smile"] = True
    elif anim == "hug":
        p["aL"] = (60, -80); p["aR"] = (60, -80); p["lean"] = 6
    elif anim == "hugged":
        p["aL"] = (55, -70); p["aR"] = (55, -70); p["smile"] = True
    elif anim == "nod":
        p["hy"] = abs(math.sin(t * 4)) * 1.6 if t < 2.5 else 0
    elif anim == "frozen":
        p["bob"] = 0
        p["aR"] = (35, -100); p["held"] = (1, "paper")
    elif anim == "look_phone":
        p["face"] = -1
    elif anim == "hand_wall":
        p["aR"] = (85, -5); p["lean"] = 4
    elif anim == "write":
        p["sit"] = True
        p["aR"] = (55, -60 + 6 * math.sin(t * 9)); p["held"] = (1, "pen")
        p["aL"] = (50, -50)
    return p
