"""Render a 5-minute animated video about cat behaviour (1280x720, 24 fps).

The cat is drawn procedurally with pycairo; frames are piped into ffmpeg and
muxed with the background soundtrack produced by make_audio.py (no voice).

Usage: python3 make_video.py background.wav out.mp4 [--preview SECONDS_LIST]
"""
import math
import subprocess
import sys

import cairo

W, H, FPS, DUR = 1280, 720, 24, 300
FLOOR = 600


# ------------------------------------------------------------------ helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between."""
    return smooth((t - a) / (b - a)) if b > a else float(t >= a)


def window(t, a, b, f=0.5):
    return ramp(t, a, a + f) * (1 - ramp(t, b - f, b))


def hexc(h, a=1.0):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (a,)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


FUR = hexc("#E9974C")
FUR_FAR = hexc("#C97835")
STRIPE = hexc("#B65E22")
CREAM = hexc("#F7E1C3")
PINK = hexc("#F1A1A9")
IRIS = hexc("#8DBF4A")
INK = hexc("#3A2A20")


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def fill(ctx, c):
    ctx.set_source_rgba(*c)
    ctx.fill()


def seg(ctx, p0, p1, w, c):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(w)
    ctx.move_to(*p0)
    ctx.line_to(*p1)
    ctx.set_source_rgba(*c)
    ctx.stroke()


def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


# ------------------------------------------------------------------ the cat
def pose(**kw):
    p = dict(x=640, y=FLOOR, face=1, s=1.0, mode="stand", crouch=0.0,
             stretch=0.0, head_dx=0.0, head_dy=0.0, tilt=0.0, eye=1.0,
             look=(0.0, 0.0), pupil=0.45, tail_up=0.6, tail_wave=0.2,
             tail_speed=2.0, legs=None, mouth=0.0, tongue=0.0, paw_up=0.0,
             paw_x=0.0, ears=0.0, jump=0.0, butt=0.0, breath=0.0, purr=0.0,
             puff=0.0)
    p.update(kw)
    return p


def gait(phase, amp, stride=26, lift=18, bound=False):
    """(forward, lift) for legs: far-front, far-back, near-front, near-back."""
    offs = (0, math.pi * 0.9, 0.25, math.pi * 1.15) if bound else (math.pi, 0, 0, math.pi)
    out = []
    for o in offs:
        a = phase + o
        out.append((amp * stride * math.sin(a), amp * lift * max(0.0, math.cos(a))))
    return out


def draw_head(ctx, cx, cy, p, t):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(p["tilt"])
    ear = p["ears"]  # 0 = upright, 1 = flattened back
    for sx in (-1, 1):
        ctx.save()
        ctx.translate(sx * 30, -32)
        ctx.rotate(sx * (0.15 + 0.9 * ear))
        ctx.move_to(-20, 8)
        ctx.line_to(sx * 4, -44 + 14 * ear)
        ctx.line_to(20, 8)
        ctx.close_path()
        fill(ctx, FUR)
        ctx.move_to(-11, 4)
        ctx.line_to(sx * 3, -30 + 10 * ear)
        ctx.line_to(11, 4)
        ctx.close_path()
        fill(ctx, PINK)
        ctx.restore()
    # head + cheek fluff
    ellipse(ctx, 0, 0, 60, 51)
    fill(ctx, FUR)
    for sx in (-1, 1):
        ctx.move_to(sx * 52, 4)
        ctx.line_to(sx * 68, 16)
        ctx.line_to(sx * 54, 22)
        ctx.line_to(sx * 64, 32)
        ctx.line_to(sx * 40, 34)
        ctx.close_path()
        fill(ctx, FUR)
    for i, dx in enumerate((-12, 0, 12)):
        seg(ctx, (dx, -48), (dx * 0.8, -32 + (6 if i == 1 else 0)), 6, STRIPE)
    ellipse(ctx, 0, 21, 28, 19)
    fill(ctx, CREAM)
    # eyes
    e = clamp(p["eye"])
    lx, ly = p["look"]
    for sx in (-1, 1):
        ex, ey = sx * 23, -6
        if e > 0.12:
            ellipse(ctx, ex, ey, 13, 14 * e)
            fill(ctx, IRIS)
            ellipse(ctx, ex + lx * 4, ey + ly * 4 * e, 13 * p["pupil"], 12.5 * e)
            fill(ctx, INK)
            ellipse(ctx, ex + lx * 4 + 4, ey - 5 * e, 3.2, 3.2 * min(1, e * 1.5))
            fill(ctx, (1, 1, 1, 0.95))
            ellipse(ctx, ex, ey, 13, 14 * e)
            ctx.set_line_width(2.5)
            ctx.set_source_rgba(*INK)
            ctx.stroke()
        else:  # closed, content eyes
            ctx.set_line_width(3.5)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.arc(ex, ey - 4, 11, 0.2 * math.pi, 0.8 * math.pi)
            ctx.set_source_rgba(*INK)
            ctx.stroke()
    # nose + mouth
    ctx.move_to(-7, 10)
    ctx.line_to(7, 10)
    ctx.line_to(0, 17)
    ctx.close_path()
    fill(ctx, PINK)
    m = p["mouth"]
    if m > 0.05:
        ellipse(ctx, 0, 27 + 4 * m, 9 + 5 * m, 3 + 10 * m)
        fill(ctx, hexc("#7A2E35"))
        ellipse(ctx, 0, 31 + 9 * m, 6 + 3 * m, 2 + 4 * m)
        fill(ctx, PINK)
    else:
        ctx.set_line_width(2.5)
        ctx.set_source_rgba(*INK)
        ctx.move_to(0, 17)
        ctx.line_to(0, 22)
        ctx.stroke()
        for sx in (-1, 1):
            ctx.arc(sx * 6, 22, 6, 0, math.pi)
            ctx.stroke()
    if p["tongue"] > 0.05:
        ellipse(ctx, 0, 30 + 7 * p["tongue"], 7, 5 + 6 * p["tongue"])
        fill(ctx, hexc("#E7808D"))
    # whiskers
    ctx.set_line_width(1.8)
    ctx.set_source_rgba(0.35, 0.25, 0.2, 0.8)
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            ctx.move_to(sx * 22, 20 + k * 4)
            ctx.line_to(sx * 72, 14 + k * 10)
            ctx.stroke()
    ctx.restore()


def draw_tail(ctx, base, p, t, length=150, width=19):
    u = p["tail_up"]
    a = lerp(-0.7, 1.55, u)
    dx, dy = -math.cos(a), -math.sin(a)
    nx, ny = -dy, dx
    w = p["tail_wave"] * 42
    s = math.sin(t * p["tail_speed"] * 2 * math.pi)
    s2 = math.sin(t * p["tail_speed"] * 2 * math.pi - 0.9)
    x0, y0 = base
    p1 = (x0 + dx * 50, y0 + dy * 50)
    p2 = (x0 + dx * 105 + nx * w * s * 0.6, y0 + dy * 105 + ny * w * s * 0.6)
    p3 = (x0 + dx * length + nx * w * s2 + 30 * u * u, y0 + dy * length + ny * w * s2 + 8 * u)
    wd = width * (1 + 0.8 * p["puff"])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(wd)
    ctx.move_to(x0, y0)
    ctx.curve_to(*p1, *p2, *p3)
    ctx.set_source_rgba(*FUR)
    ctx.stroke()
    ellipse(ctx, p3[0], p3[1], wd * 0.5, wd * 0.5)
    fill(ctx, STRIPE)


def leg(ctx, top, foot, c, w=24):
    seg(ctx, top, foot, w, c)
    ellipse(ctx, foot[0] + 3, foot[1] - 4, 15, 9)
    fill(ctx, CREAM if c == FUR else mix(CREAM, FUR_FAR, 0.4))


def draw_stand(ctx, p, t):
    cr, st = p["crouch"], p["stretch"]
    by = -118 + cr * 50
    sxs, hxs = 80, -85 + p["butt"]
    fy = by + st * 45
    ry = by - st * 32
    legs = p["legs"] or [(0, 0)] * 4
    # tail
    draw_tail(ctx, (hxs - 40, ry - 15), p, t)
    # far legs
    leg(ctx, (sxs - 14, fy + 10), (sxs - 14 + legs[0][0], -legs[0][1]), FUR_FAR)
    leg(ctx, (hxs + 14, ry + 10), (hxs + 14 + legs[1][0], -legs[1][1]), FUR_FAR)
    # body capsule
    bw = 108 - cr * 8 + p["breath"] * 6
    seg(ctx, (hxs, ry), (sxs, fy), bw, FUR)
    seg(ctx, (hxs + 15, ry + 24), (sxs - 5, fy + 24), 48, CREAM)
    ang = math.atan2(fy - ry, sxs - hxs)
    nx, ny = math.sin(ang), -math.cos(ang)
    for i in range(4):
        u = 0.15 + 0.2 * i
        px, py = lerp(hxs, sxs, u), lerp(ry, fy, u)
        seg(ctx, (px + nx * 48, py + ny * 48), (px + nx * 26 - 5, py + ny * 26), 9, STRIPE)
    # near legs
    ellipse(ctx, hxs + 5, ry + 8, 44, 46)
    fill(ctx, FUR)
    seg(ctx, (hxs - 25, ry - 20), (hxs - 5, ry - 6), 8, STRIPE)
    leg(ctx, (hxs - 8, ry + 22), (hxs - 8 + legs[3][0], -legs[3][1]), FUR, 26)
    leg(ctx, (sxs + 6, fy + 10), (sxs + 6 + legs[2][0], -legs[2][1]), FUR)
    hc = (sxs + 48 + p["head_dx"], fy - 62 + p["head_dy"] + cr * 8)
    draw_head(ctx, *hc, p, t)
    return hc


def draw_sit(ctx, p, t):
    b = p["breath"]
    # tail along the floor behind
    q = dict(p)
    draw_tail_floor(ctx, q, t)
    # far front leg
    leg(ctx, (18, -120), (22, 0), FUR_FAR)
    # haunch + chest
    ellipse(ctx, -32, -58, 64, 58 + 2 * b)
    fill(ctx, FUR)
    seg(ctx, (-22, -60), (22, -150 - 3 * b), 104 + 4 * b, FUR)
    seg(ctx, (16, -72), (32, -140), 44, CREAM)
    for i in range(3):
        seg(ctx, (-78 + i * 6, -82 + i * 26), (-52 + i * 6, -72 + i * 26), 9, STRIPE)
    seg(ctx, (-88, -40), (-62, -40), 9, STRIPE)
    # near front leg / grooming paw
    pu = p["paw_up"]
    foot = (lerp(46, 70 + p["paw_x"], pu), lerp(0, -178, pu))
    seg(ctx, (38, -118), foot, 26, FUR)
    ellipse(ctx, foot[0] + 3, foot[1] - 4, 15, 10)
    fill(ctx, CREAM)
    # hind paw peeking out
    ellipse(ctx, -2, -6, 22, 10)
    fill(ctx, CREAM)
    hc = (30 + p["head_dx"], -205 + p["head_dy"] - 3 * b)
    draw_head(ctx, *hc, p, t)
    if pu > 0.5:  # paw drawn over face when washing
        ellipse(ctx, foot[0] + 3, foot[1] - 4, 15, 10)
        fill(ctx, CREAM)
    return hc


def draw_tail_floor(ctx, p, t):
    w = p["tail_wave"]
    s = math.sin(t * p["tail_speed"] * 2 * math.pi)
    tip_y = -30 - 45 * p["tail_up"] + 30 * w * s
    tip_x = -205 + 14 * w * math.cos(t * p["tail_speed"] * 2 * math.pi)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(19 * (1 + 0.8 * p["puff"]))
    ctx.move_to(-80, -18)
    ctx.curve_to(-140, -2, -185, -4, -200, -18)
    ctx.curve_to(-212, -28, tip_x - 4, tip_y + 12, tip_x, tip_y)
    ctx.set_source_rgba(*FUR)
    ctx.stroke()
    ellipse(ctx, tip_x, tip_y, 9.5, 9.5)
    fill(ctx, STRIPE)


def draw_curl(ctx, p, t):
    b = p["breath"]
    ellipse(ctx, 0, -58 - 3 * b, 140, 60 + 5 * b)
    fill(ctx, FUR)
    for i in range(5):
        x = -90 + i * 38
        seg(ctx, (x, -112 - 4 * b), (x + 6, -92 - 3 * b), 9, STRIPE)
    ellipse(ctx, -70, -50, 55, 45 + 2 * b)
    fill(ctx, FUR)
    seg(ctx, (-95, -78), (-70, -70), 8, STRIPE)
    ellipse(ctx, 62, -12, 20, 10)
    fill(ctx, CREAM)
    hc = (95 + p["head_dx"], -62 + p["head_dy"])
    q = dict(p)
    q["tilt"] = p["tilt"] + 0.22
    draw_head(ctx, *hc, q, t)
    # tail wraps around the front, over the chin
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(20)
    ctx.move_to(-128, -40)
    ctx.curve_to(-150, 8, 40, 20, 120 + 6 * math.sin(t * 0.7), -8)
    ctx.set_source_rgba(*FUR)
    ctx.stroke()
    ellipse(ctx, 120 + 6 * math.sin(t * 0.7), -8, 10, 10)
    fill(ctx, STRIPE)
    return hc


def draw_cat(ctx, p, t):
    ctx.save()
    # ground shadow
    sh = 1 - clamp(p["jump"] / 160) * 0.6
    ellipse(ctx, p["x"], p["y"] + 2, 150 * p["s"] * sh, 13 * p["s"] * sh)
    ctx.set_source_rgba(0.2, 0.12, 0.05, 0.18)
    ctx.fill()
    ctx.translate(p["x"], p["y"] - p["jump"])
    ctx.scale(p["face"] * p["s"], p["s"])
    hc = {"stand": draw_stand, "sit": draw_sit, "curl": draw_curl}[p["mode"]](ctx, p, t)
    m = ctx.get_matrix()
    ctx.restore()
    hx, hy = m.transform_point(*hc)
    if p["purr"] > 0.02:
        draw_purr(ctx, hx, hy + 70 * p["s"], p["purr"] * p["s"], t)
    return hx, hy


def draw_cat_blend(ctx, p1, p2, a, t):
    if a <= 0.001:
        return draw_cat(ctx, p1, t)
    if a >= 0.999:
        return draw_cat(ctx, p2, t)
    ctx.push_group()
    draw_cat(ctx, p1, t)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(1 - a)
    ctx.push_group()
    r = draw_cat(ctx, p2, t)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    return r


def draw_purr(ctx, x, y, k, t):
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(3):
        ph = (t * 1.6 + i / 3) % 1
        r = 20 + 45 * ph
        ctx.set_source_rgba(1, 1, 1, 0.55 * (1 - ph) * k)
        for sx in (-1, 1):
            c = 0 if sx > 0 else math.pi
            ctx.arc(x, y, r, c - 0.45, c + 0.45)
            ctx.stroke()


# ------------------------------------------------------------------ scenery
def sky_colors(t):
    keys = [(0, "#BFE3F7", "#FFF4D6"), (120, "#8CCBF0", "#D8EEFA"),
            (215, "#7FC0EA", "#CFE9F7"), (255, "#F3A86B", "#FBD9A0"),
            (275, "#6C5B9E", "#E39A84"), (300, "#22284F", "#4C4A7E")]
    for (t0, a0, b0), (t1, a1, b1) in zip(keys, keys[1:]):
        if t <= t1:
            u = smooth((t - t0) / (t1 - t0))
            return mix(hexc(a0), hexc(a1), u), mix(hexc(b0), hexc(b1), u)
    return hexc(keys[-1][1]), hexc(keys[-1][2])


def night_amount(t):
    return ramp(t, 262, 290)


WIN = (170, 100, 300, 270)  # x, y, w, h


def draw_bird(ctx, x, y, s, flap, face=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    ellipse(ctx, 0, 0, 14, 10)
    fill(ctx, hexc("#5B6E8C"))
    ellipse(ctx, 10, -7, 8, 7)
    fill(ctx, hexc("#5B6E8C"))
    ellipse(ctx, 2, 3, 9, 6)
    fill(ctx, hexc("#E98A5A"))
    ctx.move_to(17, -8)
    ctx.line_to(23, -6)
    ctx.line_to(17, -4)
    fill(ctx, hexc("#F2C14E"))
    ellipse(ctx, 12, -8, 1.6, 1.6)
    fill(ctx, INK)
    ctx.move_to(-4, -4)
    ctx.line_to(-14, -4 - 16 * flap)
    ctx.line_to(4, -2)
    fill(ctx, hexc("#45566F"))
    ctx.move_to(-13, 0)
    ctx.line_to(-24, -4)
    ctx.line_to(-22, 4)
    fill(ctx, hexc("#45566F"))
    ctx.restore()


def draw_window(ctx, t, birds=()):
    x, y, w, h = WIN
    top, bot = sky_colors(t)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, *top)
    g.add_color_stop_rgba(1, *bot)
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    ctx.set_source(g)
    ctx.paint()
    # sun / moon
    na = night_amount(t)
    sx = lerp(x + 60, x + 250, t / DUR)
    sy = y + 60 + 120 * ramp(t, 230, 285)
    ellipse(ctx, sx, sy, 26, 26)
    fill(ctx, mix(hexc("#FFE9A8", 0.95), hexc("#F4F1E0", 0.9), na))
    if na > 0.3:
        for i, (a, b) in enumerate(((40, 40), (120, 70), (200, 30), (260, 90), (90, 120))):
            ctx.set_source_rgba(1, 1, 0.9, (na - 0.3) * (0.6 + 0.4 * math.sin(t * 3 + i)))
            ctx.arc(x + a, y + b, 1.8, 0, 2 * math.pi)
            ctx.fill()
    # drifting clouds
    for i, (cy, sp, sz) in enumerate(((50, 4, 1.0), (110, 2.6, 0.7), (170, 3.3, 0.85))):
        cx = x - 120 + ((t * sp + i * 160) % (w + 240))
        for dx, dy, r in ((0, 0, 22), (24, -10, 26), (50, 0, 20), (26, 6, 22)):
            ellipse(ctx, cx + dx * sz, y + cy + dy * sz, r * sz, r * sz * 0.8)
            ctx.set_source_rgba(1, 1, 1, 0.75 * (1 - 0.6 * na))
            ctx.fill()
    # tree branch
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(12)
    ctx.set_source_rgba(*mix(hexc("#6B4A32"), hexc("#2B2235"), na))
    ctx.move_to(x + w + 10, y + 150)
    ctx.curve_to(x + 220, y + 160, x + 140, y + 175, x + 70, y + 168)
    ctx.stroke()
    for lx, ly in ((x + 250, y + 140), (x + 180, y + 150), (x + 120, y + 160), (x + 90, y + 182), (x + 210, y + 172)):
        ellipse(ctx, lx, ly, 16, 9)
        fill(ctx, mix(hexc("#6FAE5A"), hexc("#283A3A"), na))
    for b in birds:
        draw_bird(ctx, *b)
    ctx.restore()
    # frame
    ctx.set_source_rgba(*hexc("#FBF7F0"))
    ctx.set_line_width(14)
    ctx.rectangle(x, y, w, h)
    ctx.stroke()
    ctx.set_line_width(8)
    ctx.move_to(x + w / 2, y)
    ctx.line_to(x + w / 2, y + h)
    ctx.move_to(x, y + h * 0.45)
    ctx.line_to(x + w, y + h * 0.45)
    ctx.stroke()
    rrect(ctx, x - 22, y + h + 4, w + 44, 16, 4)
    fill(ctx, hexc("#EDE5D8"))
    # curtains
    for cx, d in ((x - 26, -1), (x + w + 26, 1)):
        ctx.move_to(cx, y - 24)
        ctx.curve_to(cx + d * 28, y + 90, cx - d * 6, y + 200, cx + d * 26, y + h + 40)
        ctx.line_to(cx + d * 70, y + h + 40)
        ctx.line_to(cx + d * 50, y - 24)
        ctx.close_path()
        fill(ctx, hexc("#C9665B"))
    seg(ctx, (x - 90, y - 26), (x + w + 90, y - 26), 7, hexc("#8C6A4E"))


def draw_room(ctx, t, birds=()):
    g = cairo.LinearGradient(0, 0, 0, 470)
    g.add_color_stop_rgba(0, *hexc("#F3E3CC"))
    g.add_color_stop_rgba(1, *hexc("#E9D2B2"))
    ctx.set_source(g)
    ctx.paint()
    # wallpaper dots
    ctx.set_source_rgba(1, 1, 1, 0.25)
    for i in range(0, W, 64):
        for j in range(32, 460, 64):
            ctx.arc(i + (32 if (j // 64) % 2 else 0), j, 3, 0, 2 * math.pi)
            ctx.fill()
    draw_window(ctx, t, birds)
    # picture frame + shelf
    rrect(ctx, 820, 120, 150, 110, 6)
    fill(ctx, hexc("#7A5A43"))
    rrect(ctx, 832, 132, 126, 86, 3)
    fill(ctx, hexc("#9CC6C0"))
    ctx.move_to(832, 218)
    ctx.line_to(880, 160)
    ctx.line_to(915, 200)
    ctx.line_to(935, 180)
    ctx.line_to(958, 218)
    ctx.close_path()
    fill(ctx, hexc("#5E8C6A"))
    ellipse(ctx, 930, 152, 10, 10)
    fill(ctx, hexc("#F7D774"))
    rrect(ctx, 1010, 300, 200, 12, 3)
    fill(ctx, hexc("#8C6A4E"))
    for i, (c, hh) in enumerate((("#5C7FA3", 60), ("#C9665B", 48), ("#E3B04B", 66), ("#6B9A6B", 54))):
        rrect(ctx, 1030 + i * 24, 300 - hh, 20, hh, 2)
        fill(ctx, hexc(c))
    # lamp (glows at night)
    na = night_amount(t)
    seg(ctx, (1110, 470), (1110, 330 + 40), 6, hexc("#5A4636"))
    ctx.move_to(1075, 370)
    ctx.line_to(1145, 370)
    ctx.line_to(1130, 325)
    ctx.line_to(1090, 325)
    ctx.close_path()
    fill(ctx, mix(hexc("#EADBC0"), hexc("#FFE6A3"), na))
    # floor
    g = cairo.LinearGradient(0, 470, 0, H)
    g.add_color_stop_rgba(0, *hexc("#B98A5E"))
    g.add_color_stop_rgba(1, *hexc("#A0714A"))
    ctx.rectangle(0, 470, W, H - 470)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.35, 0.2, 0.1, 0.18)
    ctx.set_line_width(2)
    for i, yy in enumerate((500, 535, 578, 630, 690)):
        ctx.move_to(0, yy)
        ctx.line_to(W, yy)
        ctx.stroke()
        for k in range(6):
            xx = (k * 260 + i * 130) % W
            ctx.move_to(xx, yy)
            ctx.line_to(xx, yy - (yy - [470, 500, 535, 578, 630][i]))
            ctx.stroke()
    rrect(ctx, 0, 458, W, 16, 2)
    fill(ctx, hexc("#F8F1E6"))
    # sunbeam from the window
    sb = 0.16 * (1 - na)
    if sb > 0.01:
        x, y, w, h = WIN
        off = lerp(-60, 260, t / DUR)
        ctx.move_to(x + 10 + off, 476)
        ctx.line_to(x + w + off, 476)
        ctx.line_to(x + w + 260 + off, H)
        ctx.line_to(x + 140 + off, H)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.95, 0.75, sb)
        ctx.fill()
    # rug
    ellipse(ctx, 660, 630, 400, 62)
    fill(ctx, hexc("#7D9C9A"))
    ellipse(ctx, 660, 630, 360, 50)
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(4)
    ctx.stroke()
    # plant
    for a in (-0.9, -0.5, -0.15, 0.2, 0.55, 0.95):
        sway = 0.04 * math.sin(t * 0.8 + a * 3)
        ctx.save()
        ctx.translate(70, 470)
        ctx.rotate(a * 0.8 + sway)
        ellipse(ctx, 0, -75, 18, 60)
        fill(ctx, hexc("#5E9C5A"))
        ctx.restore()
    ctx.move_to(35, 460)
    ctx.line_to(105, 460)
    ctx.line_to(95, 530)
    ctx.line_to(45, 530)
    ctx.close_path()
    fill(ctx, hexc("#C77B52"))


def finish_lighting(ctx, t):
    na = night_amount(t)
    if na > 0.01:
        ctx.set_source_rgba(0.12, 0.1, 0.28, 0.38 * na)
        ctx.paint()
        g = cairo.RadialGradient(1110, 360, 10, 1110, 360, 520)
        g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.35 * na)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.paint()


# ------------------------------------------------------------------ props
def draw_yarn(ctx, x, y, r, rot, trail):
    ctx.set_line_width(3)
    ctx.set_source_rgba(*hexc("#B9425C"))
    ctx.move_to(x, y)
    ctx.curve_to(x - 60, y + r + 4, x - 110 - trail, y + r - 2, x - 170 - trail, y + r + 2)
    ctx.stroke()
    ellipse(ctx, x, y + r - 2, r * 1.05, 6)
    ctx.set_source_rgba(0.2, 0.12, 0.05, 0.18)
    ctx.fill()
    ellipse(ctx, x, y, r, r)
    fill(ctx, hexc("#D9577A"))
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgba(*hexc("#A93A57"))
    ctx.set_line_width(2.5)
    for k in range(5):
        a = rot + k * math.pi / 5
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(a)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, r * 0.95, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()
    ctx.restore()


def draw_mouse_toy(ctx, x, y, face=1, wiggle=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(face, 1)
    ellipse(ctx, 0, 4, 34, 6)
    ctx.set_source_rgba(0.2, 0.12, 0.05, 0.18)
    ctx.fill()
    ctx.set_line_width(3)
    ctx.set_source_rgba(*hexc("#8D8D96"))
    ctx.move_to(-28, -6)
    ctx.curve_to(-50, -4 + wiggle * 8, -60, -16, -75, -10 - wiggle * 6)
    ctx.stroke()
    ctx.move_to(-30, 0)
    ctx.curve_to(-28, -30, 16, -28, 30, -4)
    ctx.line_to(30, 0)
    ctx.close_path()
    fill(ctx, hexc("#A9A9B3"))
    ellipse(ctx, 6, -22, 9, 9)
    fill(ctx, hexc("#C6C6CE"))
    ellipse(ctx, 6, -22, 5, 5)
    fill(ctx, PINK)
    ellipse(ctx, 20, -12, 2.4, 2.4)
    fill(ctx, INK)
    ellipse(ctx, 31, -3, 3, 3)
    fill(ctx, PINK)
    ctx.restore()


def draw_cushion(ctx, x, y):
    ellipse(ctx, x, y - 10, 175, 30)
    fill(ctx, hexc("#E9C46A"))
    ellipse(ctx, x, y - 16, 160, 24)
    fill(ctx, hexc("#F2D58A"))
    ctx.set_source_rgba(*hexc("#D9A441"))
    ctx.set_line_width(3)
    for k in range(-3, 4):
        ctx.arc(x + k * 42, y - 16, 6, 0, 2 * math.pi)
        ctx.stroke()


def draw_zzz(ctx, x, y, t):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    for i in range(3):
        ph = (t * 0.35 + i / 3) % 1
        ctx.set_font_size(18 + 18 * ph)
        ctx.move_to(x + 30 * ph + 10 * math.sin(ph * 6), y - 110 * ph)
        ctx.set_source_rgba(1, 1, 1, 0.9 * math.sin(math.pi * ph))
        ctx.show_text("z")


def draw_heart(ctx, x, y, s, a):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 6)
    ctx.curve_to(-14, -4, -8, -16, 0, -8)
    ctx.curve_to(8, -16, 14, -4, 0, 6)
    ctx.set_source_rgba(0.93, 0.36, 0.45, a)
    ctx.fill()
    ctx.restore()


def draw_hearts(ctx, x, y, t, k=1.0):
    for i in range(3):
        ph = (t * 0.3 + i / 3) % 1
        draw_heart(ctx, x + 40 * math.sin(i * 2.1 + ph * 3), y - 140 * ph, 1.2 + ph, k * math.sin(math.pi * ph) * 0.85)


def speed_lines(ctx, x, y, d, k):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(4)
    for i, (dy, ln) in enumerate(((-150, 70), (-110, 110), (-70, 80), (-30, 60))):
        ctx.set_source_rgba(1, 1, 1, 0.6 * k)
        x0 = x - d * (180 + 20 * i)
        ctx.move_to(x0, y + dy)
        ctx.line_to(x0 - d * ln, y + dy)
        ctx.stroke()


# ------------------------------------------------------------------ captions
def caption(ctx, text, a, sub=None):
    if a <= 0.01:
        return
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(26)
    ext = ctx.text_extents(text)
    wd = ext.x_advance
    if sub:
        ctx.set_font_size(18)
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        wd = max(wd, ctx.text_extents(sub).x_advance)
    hh = 78 if sub else 54
    y = 40
    rrect(ctx, 36, y, wd + 44, hh, 16)
    ctx.set_source_rgba(0.16, 0.12, 0.1, 0.62 * a)
    ctx.fill()
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(26)
    ctx.set_source_rgba(1, 0.97, 0.9, a)
    ctx.move_to(58, y + 36)
    ctx.show_text(text)
    if sub:
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(18)
        ctx.set_source_rgba(1, 0.92, 0.8, a)
        ctx.move_to(58, y + 62)
        ctx.show_text(sub)


def centered(ctx, text, y, size, a, bold=True, c=(1, 0.97, 0.9)):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(text)
    ctx.move_to(W / 2 - e.x_advance / 2, y)
    ctx.set_source_rgba(*c, a)
    ctx.show_text(text)


def title_card(ctx, a, title, sub):
    if a <= 0.01:
        return
    rrect(ctx, W / 2 - 360, 170, 720, 150, 24)
    ctx.set_source_rgba(0.16, 0.12, 0.1, 0.6 * a)
    ctx.fill()
    centered(ctx, title, 245, 52, a)
    centered(ctx, sub, 290, 22, a, bold=False, c=(1, 0.9, 0.75))


def captions(ctx, lt, items):
    """items: list of (start, end, text, sub)."""
    for a, b, text, sub in items:
        if a <= lt < b:
            caption(ctx, text, window(lt, a, b, 0.6), sub)


# ------------------------------------------------------------------ scenes
def scene_wake(ctx, lt, t):
    draw_room(ctx, t, birds=[(WIN[0] + 230, WIN[1] + 142, 1.0, 0.0)])
    breath = math.sin(t * 2 * math.pi / 3.6)
    eye = ramp(lt, 6.5, 8.0) * 0.5 + 0.5 * ramp(lt, 9, 9.6) if lt < 10 else 1
    curl = pose(mode="curl", x=640, breath=breath, eye=eye if lt > 6.5 else 0)
    stretch = window(lt, 11, 19, 1.5)
    yawn = window(lt, 13.5, 16.5, 0.7)
    walk = ramp(lt, 22, 23) * (1 - ramp(lt, 28, 28.5))
    x = 640 + 140 * smooth((lt - 22) / 6.5)
    ph = (x - 640) / 14
    stand = pose(x=x, stretch=stretch, eye=1 - 0.85 * stretch, mouth=yawn * 1.2,
                 ears=0.3 * yawn, tail_up=lerp(0.6, 0.95, stretch), tail_wave=0.1,
                 head_dy=stretch * 25, tilt=-0.15 * stretch,
                 legs=[(f + s, l) for (f, l), s in zip(gait(ph, walk),
                                                      (32 * stretch, -10 * stretch, 32 * stretch, -10 * stretch))])
    draw_cat_blend(ctx, curl, stand, ramp(lt, 9.6, 10.4), t)
    if lt < 8:
        draw_zzz(ctx, 760, 520, t)
    title_card(ctx, window(lt, 0.8, 6.5, 0.8), "Cat Behaviour", "Five minutes in the life of a house cat")
    captions(ctx, lt, [(7, 11, "Waking up", "Cats sleep 12-16 hours a day"),
                       (11, 20, "The big stretch & yawn", "Front paws forward, back arched up"),
                       (21, 29.5, "Ready to start the day", None)])


def scene_groom(ctx, lt, t):
    draw_room(ctx, t)
    # cycle: lick paw (0-3), wash face (3-6), lick chest (6-8), pause (8-10)
    c = lt % 10
    paw = window(c, 0, 6.2, 0.6)
    wash = window(c, 3, 6.2, 0.4)
    chest = window(c, 6.4, 8.6, 0.5)
    lick = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 3.2)
    p = pose(mode="sit", x=640, s=1.25, paw_up=paw * (0.85 + 0.15 * wash),
             paw_x=wash * 18 * math.sin(t * 2 * math.pi * 1.4),
             tilt=-0.12 * paw + wash * 0.18 * math.sin(t * 2 * math.pi * 1.4) + 0.35 * chest,
             head_dy=chest * 30, head_dx=-10 * chest,
             tongue=(paw * (1 - wash) + chest) * lick, eye=lerp(1, 0.08, max(paw, chest)),
             tail_up=0.2, tail_wave=0.15, tail_speed=0.5, breath=math.sin(t * 1.8))
    draw_cat(ctx, p, t)
    captions(ctx, lt, [(0.5, 10, "Grooming", "Licking the paws first..."),
                       (10, 20, "Grooming", "...then washing the face with a damp paw"),
                       (20, 29.5, "Grooming", "Up to half of a cat's waking time is spent grooming")])


def scene_tail(ctx, lt, t):
    draw_room(ctx, t)
    if lt < 15:
        # walk across, tail held high in a question mark
        u = lt / 15
        x = lerp(-150, 1430, u) if lt < 7.5 else lerp(1430, 640, smooth((lt - 7.5) / 7))
        face = 1 if lt < 7.5 else -1
        moving = 1 if lt < 7.5 else 1 - ramp(lt, 13.5, 14.5)
        ph = x / 13 * face
        p = pose(x=x, face=face, tail_up=1.0, tail_wave=0.12, tail_speed=0.8,
                 legs=gait(ph, moving), head_dy=3 * math.sin(ph * 2))
        if lt > 14:
            p2 = pose(mode="sit", x=640, face=-1, tail_up=0.5, tail_wave=0.1)
            draw_cat_blend(ctx, p, p2, ramp(lt, 14.3, 15), t)
        else:
            draw_cat(ctx, p, t)
    else:
        k = ramp(lt, 19, 20)
        p = pose(mode="sit", x=640, face=-1, tail_up=0.5 + 0.2 * k,
                 tail_wave=lerp(0.1, 0.9, k), tail_speed=lerp(0.4, 2.6, k),
                 ears=0.35 * k, eye=lerp(1, 0.7, k), look=(-0.8 * k, 0), pupil=lerp(0.45, 0.25, k),
                 tilt=-0.08 * k)
        draw_cat(ctx, p, t)
    captions(ctx, lt, [(0.5, 15, "Tail talk: held high", "A raised tail with a curled tip = happy & friendly"),
                       (15.5, 29.5, "Tail talk: twitching tip", "A flicking, thumping tail = focused or annoyed")])


def ball_x(lt, hits):
    x = 430
    for k in hits:
        if lt > k:
            x += 52 * (1 - math.exp(-(lt - k) * 3))
    return x


def scene_yarn(ctx, lt, t):
    draw_room(ctx, t)
    hits = [2 + 2.6 * i for i in range(11)]
    bx = ball_x(lt, hits)
    cx = ball_x(lt - 0.7, hits) - 165
    v = (ball_x(lt - 0.6, hits) - ball_x(lt - 0.8, hits)) / 0.2
    amp = clamp(abs(v) / 40)
    ph = cx / 11
    legs = gait(ph, amp)
    # paw swat before each hit
    swat = 0.0
    for k in hits:
        if k - 0.5 < lt < k + 0.25:
            swat = math.sin(math.pi * (lt - (k - 0.5)) / 0.75)
    fl = legs[2]
    legs[2] = (fl[0] + 70 * swat, fl[1] + 55 * swat)
    p = pose(x=cx, crouch=0.45, legs=legs, tail_up=0.55, tail_wave=0.35, tail_speed=1.4,
             pupil=0.7, head_dy=10, tilt=0.08, butt=4 * math.sin(t * 9) * (1 - amp))
    draw_cat(ctx, p, t)
    draw_yarn(ctx, bx, FLOOR - 26, 26, bx / 26, 10 * math.sin(lt))
    captions(ctx, lt, [(0.5, 15, "Playtime", "Batting a ball of yarn practises hunting skills"),
                       (15, 29.5, "Playtime", "Wide pupils = excited & engaged")])


def scene_hunt(ctx, lt, t):
    draw_room(ctx, t)
    mx = 960
    pounce = ramp(lt, 14, 15.1)
    if lt < 8:
        x = lerp(220, 520, lt / 8)
        legs = gait(x / 6, 0.55, stride=20, lift=10)
        p = pose(x=x, crouch=1.0, legs=legs, pupil=0.75, ears=0.15, head_dy=18,
                 tail_up=0.1, tail_wave=0.1, tail_speed=0.6)
        draw_cat(ctx, p, t)
    elif lt < 14:
        w = window(lt, 9.5, 14, 0.4)
        p = pose(x=520, crouch=1.0, pupil=0.85, ears=0.15, head_dy=18,
                 butt=w * 9 * math.sin(t * 2 * math.pi * 3.5),
                 tail_up=0.15, tail_wave=0.35 * w + 0.05, tail_speed=3.5)
        draw_cat(ctx, p, t)
    elif lt < 15.1:
        u = pounce
        x = lerp(520, mx - 150, u)
        p = pose(x=x, jump=170 * math.sin(math.pi * u), stretch=-0.0, crouch=0.2 * (1 - math.sin(math.pi * u)),
                 legs=[(40, 30), (-40, 10), (55, 40), (-45, 10)], pupil=0.85, tail_up=0.4,
                 tail_wave=0.0, ears=0.2, tilt=0.1)
        draw_cat(ctx, p, t)
    else:
        hold = pose(x=mx - 150, crouch=0.6, legs=[(30, 0), (0, 0), (40, 0), (0, 0)], pupil=0.6,
                    head_dy=20, tilt=0.15, tail_wave=0.3, tail_up=0.4)
        proud = pose(mode="sit", x=mx - 170, tail_up=0.6, tail_wave=0.12, eye=0.6, tail_speed=0.5,
                     tilt=-0.1, head_dy=-5)
        draw_cat_blend(ctx, hold, proud, ramp(lt, 20, 21), t)
    draw_mouse_toy(ctx, mx + (0 if lt > 15 else 0), FLOOR - 2, face=-1,
                   wiggle=math.sin(t * 6) if lt < 14 else 0)
    if 14.9 < lt < 16:
        k = 1 - (lt - 14.9) / 1.1
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            ctx.set_source_rgba(1, 1, 1, 0.7 * k)
            ctx.arc(mx + math.cos(a) * 70 * (2 - k), FLOOR - 30 + math.sin(a) * 30 * (2 - k), 7 * k, 0, 2 * math.pi)
            ctx.fill()
    captions(ctx, lt, [(0.5, 8.5, "Stalking", "Body low, eyes locked on the target"),
                       (8.5, 14, "The butt wiggle", "Getting the back legs ready to launch"),
                       (14, 20, "Pounce!", None),
                       (20.5, 29.5, "Proud hunter", "Gotcha, little mouse toy")])


def scene_knead(ctx, lt, t):
    draw_room(ctx, t)
    draw_cushion(ctx, 640, FLOOR + 14)
    ph = t * 2 * math.pi * 1.4
    a = max(0, math.sin(ph)) * 22
    b = max(0, math.sin(ph + math.pi)) * 22
    legs = [(14, b), (0, 0), (18, a), (0, 0)]
    p = pose(x=610, y=FLOOR - 4, crouch=0.55, legs=legs, eye=0.35 if (lt % 9) < 7 else 0.05,
             tail_up=0.45, tail_wave=0.1, tail_speed=0.4, purr=0.8, breath=math.sin(t * 2.6),
             head_dy=8 + 2 * math.sin(ph), tilt=0.05)
    draw_cat(ctx, p, t)
    captions(ctx, lt, [(0.5, 15, "Kneading (\"making biscuits\")", "A comforting habit left over from kittenhood"),
                       (15, 29.5, "Kneading", "Often paired with purring and half-closed eyes")])


def scene_blink(ctx, lt, t):
    draw_room(ctx, t)
    c = lt % 5.5
    blink = 1 - window(c, 2.0, 4.4, 0.9)
    p = pose(mode="sit", x=640, y=FLOOR + 40, s=1.65, eye=0.08 + 0.85 * blink, tail_up=0.35,
             tail_wave=0.08, tail_speed=0.3, purr=1.0, breath=math.sin(t * 2.6), tilt=0.06 * math.sin(t * 0.5))
    hx, hy = draw_cat(ctx, p, t)
    if lt > 12:
        draw_hearts(ctx, hx + 160, hy + 20, t, ramp(lt, 12, 13.5) * (1 - ramp(lt, 28, 29.5)))
    captions(ctx, lt, [(0.5, 15, "The slow blink", "A cat's way of saying \"I trust you\" - try blinking back!"),
                       (15, 29.5, "Purring", "Usually means contentment and relaxation")])


def scene_window(ctx, lt, t):
    # birds visit the branch outside the window
    x0, y0 = WIN[0], WIN[1]
    birds = []
    land1 = ramp(lt, 3, 6)
    bx = lerp(x0 + 340, x0 + 160, land1)
    by = lerp(y0 + 40, y0 + 140, land1) - 3 * abs(math.sin(t * 9)) * (1 - land1)
    hop = 4 * max(0, math.sin(t * 5)) if land1 >= 1 else 0
    flap = (0.5 + 0.5 * math.sin(t * 30)) if land1 < 1 or lt > 24 else 0.0
    if lt > 24:
        u = ramp(lt, 24, 27)
        bx, by = lerp(bx, x0 - 60, u), lerp(by, y0 + 20, u)
    birds.append((bx, by - hop, 1.0, flap, -1))
    if 12 < lt < 22:
        u = (lt - 12) / 10
        birds.append((lerp(x0 + 360, x0 - 60, u), y0 + 60 + 20 * math.sin(u * 9),
                      0.8, 0.5 + 0.5 * math.sin(t * 34), -1))
    draw_room(ctx, t, birds)
    chat = (window(lt, 8, 13, 0.3) + window(lt, 17, 21, 0.3)) * (0.5 + 0.5 * math.sin(t * 2 * math.pi * 7))
    focus = ramp(lt, 2, 4)
    p = pose(mode="sit", x=560, face=-1, head_dy=-6 * focus, tilt=0.28 * focus, look=(0.6, -0.9 * focus),
             pupil=lerp(0.45, 0.8, focus), mouth=0.8 * chat, ears=0.05,
             tail_up=0.3, tail_wave=0.25 + 0.4 * focus, tail_speed=2.2)
    draw_cat(ctx, p, t)
    captions(ctx, lt, [(0.5, 8, "Bird watching", "Windows are cat television"),
                       (8, 22, "Chattering", "Rapid jaw movements when prey is out of reach"),
                       (22, 29.5, "Bird watching", "Ears forward, eyes wide, tail twitching")])


def scene_zoom(ctx, lt, t):
    draw_room(ctx, t)
    puff_k = 0.0
    if lt < 12 or lt >= 16:
        L = lt if lt < 12 else lt - 4  # pause between 12 and 16
        period = 3.0
        u = (L % period) / period
        d = 1 if int(L // period) % 2 == 0 else -1
        x = lerp(-200, 1480, u) if d > 0 else lerp(1480, -200, u)
        hop = 60 * max(0, math.sin(L * 2 * math.pi / 0.9)) if int(L // period) % 3 == 1 else 0
        ph = L * 2 * math.pi * 3.2
        p = pose(x=x, face=d, legs=gait(ph, 1.0, stride=48, lift=32, bound=True),
                 jump=hop + 8 * abs(math.sin(ph)), ears=0.75, pupil=0.85, tail_up=0.45,
                 tail_wave=0.25, tail_speed=3, stretch=0.15 * math.sin(ph), puff=0.3)
        draw_cat(ctx, p, t)
        speed_lines(ctx, x, FLOOR, d, 1.0)
    else:
        puff_k = window(lt, 12, 16, 0.4)
        p = pose(x=640, face=1, ears=0.5, pupil=0.95, tail_up=0.95, tail_wave=0.05,
                 crouch=-0.15 * puff_k, puff=puff_k, look=(-0.6, 0.2))
        draw_cat(ctx, p, t)
    captions(ctx, lt, [(0.5, 12, "The zoomies!", "Sudden bursts of energy (a.k.a. FRAPs)"),
                       (12, 16, "...and a dramatic pause", "Puffed-up tail, huge pupils"),
                       (16, 29.5, "The zoomies!", "Burning off pent-up hunting energy")])


def scene_sleep(ctx, lt, t):
    draw_room(ctx, t)
    if lt < 4:
        x = lerp(1050, 640, smooth(lt / 4))
        p = pose(x=x, face=-1, legs=gait(x / 13, 1 - ramp(lt, 3.5, 4)), tail_up=0.7, tail_wave=0.1)
        draw_cat(ctx, p, t)
    elif lt < 10:
        # circling: turn back and forth on the spot
        c = lt - 4
        face = -1 if int(c / 1.5) % 2 == 0 else 1
        k = (c % 1.5) / 1.5
        squash = 1 - 0.25 * math.sin(math.pi * k)
        p = pose(x=640, face=face * squash, legs=gait(c * 9, 0.7), crouch=0.2, tail_up=0.5,
                 tail_wave=0.1, eye=0.6)
        if lt > 9:
            draw_cat_blend(ctx, p, pose(mode="curl", x=640, eye=0.5), ramp(lt, 9.2, 10), t)
        else:
            draw_cat(ctx, p, t)
    else:
        e = 0.5 * (1 - ramp(lt, 10, 13))
        if 15 < lt < 16.5:
            e = 0.3 * window(lt, 15, 16.5, 0.5)  # one sleepy peek
        p = pose(mode="curl", x=640, eye=e, breath=math.sin(t * 2 * math.pi / 3.8), purr=0.35 * ramp(lt, 13, 15))
        draw_cat(ctx, p, t)
        if lt > 16.5:
            draw_zzz(ctx, 760, 520, t)
    captions(ctx, lt, [(0.5, 10, "Circling before lying down", "An instinct to make a safe, comfy nest"),
                       (10.5, 22, "Curled up asleep", "Nose tucked in, tail wrapped round to keep warm")])
    title_card(ctx, window(lt, 22.5, 30.5, 1.2), "Sweet dreams", "Thanks for watching")


SCENES = [scene_wake, scene_groom, scene_tail, scene_yarn, scene_hunt,
          scene_knead, scene_blink, scene_window, scene_zoom, scene_sleep]
SCENE_LEN = 30.0


def render(ctx, t):
    i = min(int(t // SCENE_LEN), len(SCENES) - 1)
    lt = t - i * SCENE_LEN
    ctx.save()
    SCENES[i](ctx, lt, t)
    ctx.restore()
    finish_lighting(ctx, t)
    # fade through black between scenes (and at start/end)
    f = 0.45
    a = 0.0
    if lt < f:
        a = 1 - lt / f
    elif lt > SCENE_LEN - f:
        a = (lt - (SCENE_LEN - f)) / f
    if i == len(SCENES) - 1 and lt > SCENE_LEN - f:
        a = max(a, 1.0 if lt > SCENE_LEN - 0.2 else a)
    if a > 0:
        ctx.set_source_rgba(0, 0, 0, smooth(a))
        ctx.paint()


def main():
    audio, out = sys.argv[1], sys.argv[2]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    if "--preview" in sys.argv:
        times = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for tt in times:
            ctx.set_source_rgb(0, 0, 0)
            ctx.paint()
            render(ctx, tt)
            surf.write_to_png(f"{out}_{tt:06.2f}.png")
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = DUR * FPS
    for f in range(n):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        render(ctx, f / FPS)
        surf.flush()
        proc.stdin.write(surf.get_data())
        if f % (FPS * 15) == 0:
            print(f"{f / FPS:5.0f}s / {DUR}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
