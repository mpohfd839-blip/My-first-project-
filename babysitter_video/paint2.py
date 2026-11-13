"""Dynamic painters for the babysitter story."""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bgs import Cv, SW, SH, OUT, draw_car, wheel
from chars import draw_character, make_pose

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FH = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"

RULES = ["Do not go upstairs after 10 PM, even if the baby cries.",
         "The baby does not have a twin. If you see two, put the one in the crib back in the closet.",
         "If we call, ask us our dog's name before you answer anything.",
         "Never look at the baby monitor screen between 2 and 3 AM. Only listen.",
         "If we come home early, do not open the door."]


@functools.lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines


# ------------------------------------------------------------------ fridge note
@functools.lru_cache(maxsize=8)
def note_base():
    img = Image.new("RGBA", (SW, SH), (205, 210, 215, 255))
    d = ImageDraw.Draw(img)
    for x in range(0, SW, 6):
        d.line([(x, 0), (x, SH)], fill=(200 + (x * 7 % 9), 205, 212))
    # magnets
    d.polygon([(330, 150), (1590, 135), (1610, 1050), (320, 1065)], fill=(252, 250, 238), outline=OUT, width=4)
    for k in range(20):
        y = 220 + k * 44
        d.line([(340, y), (1600, y - 10)], fill=(200, 215, 235), width=2)
    d.ellipse([920, 105, 1000, 185], fill=(220, 50, 50), outline=OUT, width=4)
    d.ellipse([420, 980, 480, 1040], fill=(60, 140, 220), outline=OUT, width=4)
    return img


def paint_note(scene, spec, t, dur):
    scene.paste(note_base(), (0, 0))
    d = ImageDraw.Draw(scene)
    blue = (35, 55, 160)
    d.text((960, 230), "RULES FOR TONIGHT", font=font(FH, 84), fill=blue, anchor="mm")
    k = 1.0
    if spec.get("pen"):
        k = ease(t / max(0.5, dur * 0.8))
    d.line([(620, 285), (620 + 680 * k, 282)], fill=blue, width=5)
    d.line([(630, 300), (630 + 670 * k, 297)], fill=blue, width=5)
    hl = spec.get("hl", 0)
    for i, rule in enumerate(RULES):
        y = SH * (.33 + .12 * i) + 10
        lines = wrap(f"{i + 1}. {rule}", 54)
        dim = hl >= 1 and hl != i + 1
        col = (35, 55, 160, 90) if dim else (35, 55, 160, 255)
        if hl == i + 1:
            w = ease(t / 0.5)
            d.rectangle([380, y - 50, 380 + 1180 * w, y - 50 + 50 * len(lines) + 12], fill=(255, 240, 90))
        for j, ln in enumerate(lines):
            d.text((400, y - 44 + j * 50), ln, font=font(FH, 44), fill=col)
        lw = min(1160, 19 * len(lines[-1]) + 30)
        yy = y + 6 + (len(lines) - 1) * 50
        d.line([(400, yy), (400 + lw, yy - 2)], fill=col, width=3)
        d.line([(400, yy + 8), (400 + lw, yy + 6)], fill=col, width=3)


# ------------------------------------------------------------------ phone
def phone_frame(scene):
    d = ImageDraw.Draw(scene)
    scene.paste((22, 20, 26, 255), [0, 0, SW, SH])
    d.ellipse([200, 600, 760, 1300], fill=(238, 196, 160), outline=OUT, width=6)
    d.ellipse([1160, 600, 1720, 1300], fill=(238, 196, 160), outline=OUT, width=6)
    d.rounded_rectangle([640, 30, 1280, 1060], 70, fill=(15, 15, 18), outline=OUT, width=8)
    d.rounded_rectangle([665, 60, 1255, 1030], 50, fill=(245, 245, 248))
    d.rounded_rectangle([900, 72, 1020, 100], 14, fill=(15, 15, 18))
    return d


def bubble(d, y, text, mine=False, alpha=255, red=False):
    lines = wrap(text, 26)
    h = 50 * len(lines) + 30
    x0, x1 = (700, 1150) if not mine else (770, 1220)
    col = (230, 230, 235, alpha) if not red else (250, 205, 205, alpha)
    d.rounded_rectangle([x0, y, x1, y + h], 30, fill=col)
    for j, ln in enumerate(lines):
        d.text((x0 + 25, y + 18 + j * 50), ln, font=font(FR, 36), fill=(20, 20, 25, alpha))
    return y + h + 24


def paint_phone(scene, spec, t, dur):
    d = phone_frame(scene)
    scr = spec.get("screen")
    d.text((700, 120), "9:41" if scr in ("app",) else ("12:5" + ("0" if scr.startswith("call") else "1") if scr.startswith(("call", "ended", "text1")) else ("2:41" if scr == "text2" else "5:34")), font=font(FB, 30), fill=(20, 20, 20))
    if scr == "app":
        d.rectangle([665, 160, 1255, 260], fill=(110, 60, 200))
        d.text((960, 210), "SitterNow", font=font(FB, 44), fill=(255, 255, 255), anchor="mm")
        k = ease(t / 0.6)
        y = 300 - (1 - k) * 200
        d.rounded_rectangle([690, y, 1230, y + 520], 30, fill=(255, 255, 255), outline=(200, 200, 210), width=3)
        d.text((720, y + 30), "NEW REQUEST", font=font(FB, 34), fill=(110, 60, 200))
        d.text((720, y + 90), "The Whitmore Family", font=font(FB, 38), fill=(20, 20, 20))
        for j, ln in enumerate(["Friday, 7:30 PM", "1 night  -  1 baby (9 mo)", "Dead End Rd."]):
            d.text((720, y + 150 + j * 50), ln, font=font(FR, 32), fill=(80, 80, 90))
        d.text((960, y + 360), "$400", font=font(FB, 96), fill=(30, 160, 80), anchor="mm")
        pulse = 1 + 0.05 * math.sin(t * 6)
        d.rounded_rectangle([760, y + 430, 1160, y + 500], 35, fill=(110, 60, 200))
        d.text((960, y + 465), "ACCEPT", font=font(FB, 36), fill=(255, 255, 255), anchor="mm")
    elif scr in ("call", "call_active", "ended"):
        d.rounded_rectangle([665, 60, 1255, 1030], 50, fill=(30, 35, 50))
        d.ellipse([860, 260, 1060, 460], fill=(236, 205, 120), outline=OUT, width=4)
        d.text((960, 360), "C", font=font(FB, 100), fill=(255, 255, 255), anchor="mm")
        d.text((960, 530), "Claire Whitmore", font=font(FB, 48), fill=(255, 255, 255), anchor="mm")
        sub = {"call": "incoming call...", "call_active": f"00:{int(14 + t):02d}", "ended": "Call Ended"}[scr]
        d.text((960, 600), sub, font=font(FR, 36), fill=(180, 180, 190), anchor="mm")
        if scr == "call":
            r = 70 + 8 * math.sin(t * 8)
            d.ellipse([760 - r, 880 - r, 760 + r, 880 + r], fill=(220, 50, 50))
            d.ellipse([1160 - r, 880 - r, 1160 + r, 880 + r], fill=(50, 190, 90))
        elif scr == "call_active":
            d.ellipse([890, 810, 1030, 950], fill=(220, 50, 50))
    elif scr in ("text1", "text2"):
        d.rectangle([665, 160, 1255, 250], fill=(240, 240, 245))
        d.text((960, 205), "Claire Whitmore", font=font(FB, 38), fill=(20, 20, 20), anchor="mm")
        msg = ["Pepper. Her name is Pepper. Whatever just called you, it knows you're there now.",
               "There's an accident on the bridge. We're stuck. We won't be home until 4.",
               "FOLLOW THE RULES. Don't let anything in."]
        y = 280
        if scr == "text1":
            n = 3 if not spec.get("type_text") else min(3, 1 + int(t / max(1, dur / 3.2)))
            for i in range(n):
                y = bubble(d, y, msg[i])
        else:
            for i in range(3):
                y = bubble(d, y, msg[i], alpha=110)
            if t > 0.4:
                bubble(d, y, "Still on the bridge. 40 more minutes. Is everything okay?")
    elif scr.startswith("booking"):
        d.rectangle([665, 160, 1255, 260], fill=(110, 60, 200))
        d.text((960, 210), "SitterNow", font=font(FB, 44), fill=(255, 255, 255), anchor="mm")
        d.rounded_rectangle([690, 300, 1230, 620], 30, fill=(255, 255, 255), outline=(200, 200, 210), width=3)
        d.text((720, 330), "NEW BOOKING REQUEST", font=font(FB, 32), fill=(110, 60, 200))
        d.text((720, 390), "The Whitmores", font=font(FB, 40), fill=(20, 20, 20))
        d.text((720, 450), "Next Friday  -  7:30 PM", font=font(FR, 34), fill=(80, 80, 90))
        d.text((720, 510), "Note from parent:", font=font(FB, 30), fill=(80, 80, 90))
        y = 650
        if scr in ("booking_note1", "booking_note2"):
            y = bubble(d, y, "Noah loved you.")
        if scr == "booking_note2" and t > 0.5:
            bubble(d, y, "So did the other one. It's been asking for you.", red=True)


# ------------------------------------------------------------------ baby monitor
def monitor_screen(kind, t, w=880, h=600):
    c = Cv(w, h)
    c.rect(0, 0, w, h, (60, 70, 62), ol=False)
    c.rect(0, h * .72, w, h, (70, 80, 70), ol=False)
    if kind == "standing_closet":
        c.rect(30, 40, 230, h * .8, (25, 28, 25))
        c.rect(150, 40, 230, h * .8, (75, 85, 75))
        c.ell(60, 180, 90, 205, (220, 230, 220), ol=False)
        c.ell(110, 180, 140, 205, (220, 230, 220), ol=False)
    # crib
    cx0, cx1 = 300, 820
    c.rect(cx0, 180, cx1, 520, (130, 140, 130))
    c.rect(cx0 + 20, 380, cx1 - 20, 470, (165, 175, 165), ol=False)
    img = c.done()
    if kind in ("sleep",):
        p = make_pose(dict(c="noah", anim="baby", expr="sleep"), t, 5, 0, 1)
        bi, ox, oy = draw_character("noah", p, 2.6)
        bi = bi.rotate(90, expand=True, resample=Image.BICUBIC)
        breath = 1 + 0.03 * math.sin(t * 3)
        bi = bi.resize((int(bi.width * breath), bi.height))
        img.alpha_composite(bi, (int(560 - bi.width / 2), int(440 - bi.height / 2)))
    elif kind.startswith("standing"):
        p = make_pose(dict(c="noah", anim="baby", expr="cry"), t, 5, 0, 1)
        p["sit"] = False
        p["aL"] = (150, -10); p["aR"] = (150, -10)
        bi, ox, oy = draw_character("noah", p, 3.6)
        img.alpha_composite(bi, (int(560 - ox), int(470 - oy)))
    d = ImageDraw.Draw(img)
    for x in range(cx0 + 10, cx1, 36):
        d.rectangle([x, 230, x + 10, 520], fill=(150, 160, 150), outline=OUT, width=2)
    d.rectangle([cx0, 220, cx1, 240], fill=(150, 160, 150), outline=OUT, width=2)
    # night vision grade
    a = np.asarray(img.convert("L")).astype(np.float32)
    a = a * 0.9 + np.random.RandomState(int(t * 24)).randn(h, w) * 14
    a[::3] *= 0.85
    g = np.clip(a, 0, 255).astype(np.uint8)
    out = Image.merge("RGB", (Image.fromarray((g * 0.75).astype(np.uint8)), Image.fromarray(g), Image.fromarray((g * 0.75).astype(np.uint8))))
    d = ImageDraw.Draw(out)
    d.text((20, 15), "CAM 1", font=font(FB, 30), fill=(200, 255, 200))
    if (t % 1) < 0.6:
        d.ellipse([w - 150, 22, w - 128, 44], fill=(255, 40, 40))
    d.text((w - 120, 15), "REC", font=font(FB, 30), fill=(200, 255, 200))
    tm = {"sleep": "08:52", "standing": "03:01", "standing_closet": "03:01"}.get(kind, "02:00")
    d.text((20, h - 50), f"{tm}:{int(t) % 60:02d}", font=font(FB, 28), fill=(200, 255, 200))
    return out


def paint_monitor(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    scene.paste((40, 35, 40, 255), [0, 0, SW, SH])
    d.ellipse([150, 650, 700, 1350], fill=(238, 196, 160), outline=OUT, width=6)
    d.rounded_rectangle([420, 90, 1500, 1010], 80, fill=(240, 240, 242), outline=OUT, width=8)
    scr = monitor_screen(spec.get("screen", "sleep"), t)
    scene.paste(scr, (520, 170))
    d.rectangle([520, 170, 1400, 770], outline=OUT, width=6)
    for k in range(5):
        d.ellipse([700 + k * 110, 830, 760 + k * 110, 890], fill=(200, 200, 205), outline=OUT, width=3)
    d.ellipse([1300, 840, 1340, 880], fill=(60, 220, 90) if (t % 1) < .5 else (30, 120, 50))


def paint_monitor_table(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    cx, cy = 960, 600
    if spec.get("flip"):
        k = ease((t - 0.3) / 0.6)
    elif spec.get("pickup"):
        k = 1 - ease((t - 0.2) / 0.8)
    else:
        k = 1.0 if spec.get("flipped") else 0.0
    sy = abs(math.cos(k * math.pi))
    w, h = 760, int(560 * max(0.08, sy))
    lift = 0
    if spec.get("pickup"):
        lift = -120 * ease(t / 1.0)
    face_up = k < 0.5
    box = [cx - w / 2, cy - h / 2 + lift, cx + w / 2, cy + h / 2 + lift]
    d.rounded_rectangle([box[0] + 20, box[1] + 30, box[2] + 20, box[3] + 30], 50, fill=(40, 28, 20))
    d.rounded_rectangle(box, 50, fill=(240, 240, 242), outline=OUT, width=6)
    if face_up and h > 100:
        scr = monitor_screen("standing" if spec.get("pickup") else "sleep", t, 600, 400).resize((600, max(10, int(400 * sy))))
        scene.paste(scr, (int(cx - 300), int(cy - scr.height / 2 + lift - 30)))
    elif not face_up and h > 100:
        for r in range(6):
            for q in range(10):
                x = cx - 250 + q * 55
                y = cy - 150 * sy + r * 55 * sy + lift
                d.ellipse([x - 8, y - 8 * sy, x + 8, y + 8 * sy], fill=(90, 90, 95))
        if spec.get("speaker"):
            for r in range(3):
                rr = 60 + ((t * 120 + r * 80) % 240)
                a = int(200 * (1 - rr / 300))
                d.ellipse([cx - rr * 1.6, cy - rr * .8, cx + rr * 1.6, cy + rr * .8], outline=(255, 80, 80, a) if spec.get("glow") else (200, 220, 255, a), width=6)
        if spec.get("glow"):
            g = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
            ImageDraw.Draw(g).rectangle([box[0] - 30, box[3] - 10, box[2] + 30, box[3] + 40], fill=(255, 255, 255, 140))
            scene.alpha_composite(g.filter(ImageFilter.GaussianBlur(25)))


# ------------------------------------------------------------------ clock
def paint_clock(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    scene.paste((10, 10, 16, 255), [0, 0, SW, SH])
    d.rounded_rectangle([300, 300, 1620, 800], 60, fill=(25, 25, 28), outline=(60, 60, 65), width=8)
    d.rounded_rectangle([360, 360, 1560, 740], 30, fill=(8, 6, 6))
    tm = spec.get("time", "2:47")
    txt = tm if (t % 1.0) < 0.6 else tm.replace(":", " ")
    glow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((930, 560), txt, font=font(FB, 290), fill=(255, 40, 30, 255), anchor="mm")
    scene.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    scene.alpha_composite(glow)
    d.text((1480, 690), "PM" if spec.get("pm") else "AM", font=font(FB, 50), fill=(255, 40, 30), anchor="mm")


# ------------------------------------------------------------------ closet
def paint_closet_over(spec, t, dur):
    ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    door = spec.get("door", 1.0)
    if door == "closing":
        k = ease(t / 0.7)
    elif door == "opening_slow":
        k = 1 - 0.25 * ease(t / max(1, dur))
    else:
        k = float(door)
    jolt = 0
    if spec.get("knockfx"):
        for tt in (0.25, 0.85, 1.45, 2.3, 2.9, 3.5):
            if tt <= t < tt + 0.25:
                jolt = 10 * (1 - (t - tt) / 0.25)
    x0, x1 = 520, 1400
    w = (x1 - x0) * k
    if k > 0.02:
        d.polygon([(x0 + jolt, 110 - 20 * (1 - k)), (x0 + w + jolt, 110), (x0 + w + jolt, 1080), (x0 + jolt, 1080)], fill=(225, 215, 200), outline=OUT)
        d.line([(x0 + jolt, 110), (x0 + w + jolt, 110), (x0 + w + jolt, 1080)], fill=OUT, width=6)
        if k > 0.5:
            d.rectangle([x0 + 60 + jolt, 180, x0 + w - 60 + jolt, 560], outline=(200, 190, 175), width=6)
            d.rectangle([x0 + 60 + jolt, 620, x0 + w - 60 + jolt, 1040], outline=(200, 190, 175), width=6)
            d.ellipse([x0 + w - 70 + jolt, 600, x0 + w - 40 + jolt, 630], fill=(190, 170, 100), outline=OUT, width=3)
    if spec.get("hands") and k < 0.98:
        ex = x0 + w
        for j in range(4):
            y = 520 + j * 34
            ln = 40 + 25 * ease(t / 1.5)
            d.line([(ex - 10, y), (ex + ln, y + 6)], fill=(150, 155, 160), width=16)
            d.line([(ex - 10, y), (ex + ln, y + 6)], fill=OUT, width=3)
    if spec.get("eyes_crack"):
        d.rectangle([x0, 1050, x1, 1080], fill=(5, 5, 5))
        if (t % 2.2) > 0.15:
            for ex in (900, 1000):
                d.ellipse([ex - 14, 1056, ex + 14, 1072], fill=(240, 240, 230))
                d.ellipse([ex - 4, 1058, ex + 4, 1070], fill=(0, 0, 0))
    return ov


# ------------------------------------------------------------------ others
def paint_floor_steps(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    n = min(10, int(t / 0.35) + 1)
    for i in range(n):
        side = -1 if i % 2 else 1
        x = 960 + side * 60 + math.sin(i) * 20
        y = 120 + i * 95
        s = 0.6 + i * 0.07
        d.ellipse([x - 26 * s, y - 40 * s, x + 26 * s, y + 40 * s], fill=(85, 70, 60), outline=(170, 190, 210), width=2)
        for k in range(5):
            tx = x - 22 * s + k * 11 * s
            d.ellipse([tx - 6 * s, y - 62 * s, tx + 6 * s, y - 48 * s], fill=(85, 70, 60))


def paint_house_windows(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    for j, off in enumerate((0, -180)):
        x = 100 + (t / max(1, dur)) * 2300 + off
        y = 820 + abs(math.sin(t * 5 + j)) * 6
        d.ellipse([x - 38, y - 300, x + 38, y - 222], fill=(10, 10, 14))
        d.polygon([(x - 55, y - 222), (x + 55, y - 222), (x + 70, y + 120), (x - 70, y + 120)], fill=(10, 10, 14))
        d.line([(x + 50, y - 190), (x + 100, y - 280 + 25 * math.sin(t * 9))], fill=(10, 10, 14), width=18)


def paint_mansion_car(scene, spec, t, dur):
    mode = spec.get("car")
    if not mode:
        return
    c = Cv()
    if mode in ("arrive", "arrive_lights"):
        k = ease(t / max(1, dur * 0.8))
        x = -300 + k * 1300
    elif mode == "leave":
        k = ease(t / max(1, dur * 0.9))
        x = 1000 - k * 1500
    else:
        x = 1000
    y = 1000
    draw_car(c, x, y, 0.9, col=(40, 40, 48), lights=mode in ("arrive_lights", "parked_lights"))
    wheel(c, x - 150, y - 12, 0.9, x / 40)
    wheel(c, x + 130, y - 12, 0.9, x / 40)
    scene.alpha_composite(c.done())
    if mode in ("arrive_lights", "parked_lights", "leave"):
        g = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        if mode == "leave":
            gd.ellipse([x - 280, y - 110, x - 220, y - 70], fill=(255, 40, 40, 200))
        else:
            gd.polygon([(x + 255, y - 95), (x + 900, y - 220), (x + 900, y + 60)], fill=(255, 245, 200, 90))
        scene.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))


def paint_living_lights(scene, spec, t, dur):
    if not spec.get("headlights"):
        return
    g = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    x = -400 + ease(t / max(1, dur)) * 2600
    ImageDraw.Draw(g).polygon([(x - 150, 0), (x + 250, 0), (x + 150, 800), (x - 250, 800)], fill=(255, 250, 220, 120))
    scene.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))


def paint_frontdoor_silh(scene, spec, t, dur):
    if not spec.get("silh"):
        return
    g = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    sw = math.sin(t * 1.5) * 6
    gd.ellipse([1270 + sw, 300, 1350 + sw, 400], fill=(15, 15, 20, 220))
    gd.polygon([(1255 + sw, 400), (1370 + sw, 400), (1400, 880), (1250, 880)], fill=(15, 15, 20, 220))
    gd.ellipse([1330 - sw, 260, 1400 - sw, 350], fill=(10, 10, 14, 160))
    scene.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
    if spec.get("knockfx"):
        d = ImageDraw.Draw(scene)
        for tt in (0.2, 0.8, 1.4):
            if tt <= t < tt + 0.3:
                r = 40 + (t - tt) * 300
                d.ellipse([910 - r, 480 - r, 910 + r, 480 + r], outline=(255, 255, 255, 120), width=5)


def paint_stairs_shape(scene, spec, t, dur):
    if not spec.get("shape"):
        return
    d = ImageDraw.Draw(scene)
    x, y = 960, 200
    d.ellipse([x - 26, y - 70, x + 26, y - 20], fill=(3, 3, 5))
    d.polygon([(x - 30, y - 22), (x + 30, y - 22), (x + 40, y + 60), (x - 40, y + 60)], fill=(3, 3, 5))
    if spec.get("eyes") and (t % 2.5) > 0.12:
        for ex in (x - 11, x + 11):
            d.ellipse([ex - 5, y - 52, ex + 5, y - 44], fill=(235, 235, 220))


def paint_crib_top(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    if spec.get("twins"):
        for i, (nm, x) in enumerate((("noah", 640), ("fakenoah", 1280))):
            p = make_pose(dict(c=nm, anim="baby", expr="sleep"), t, 5, 0, i)
            if nm == "noah":
                p["breath"] = math.sin(t * 3)
            bi, ox, oy = draw_character(nm, p, 7.2)
            scene.alpha_composite(bi, (int(x - ox), int(900 - oy)))
        d.line([(960, 100), (960, 1000)], fill=OUT, width=8)
        d.text((640, 140), "BOUNCER", font=font(FB, 40), fill=(80, 80, 100), anchor="mm")
        d.text((1280, 140), "CRIB", font=font(FB, 40), fill=(80, 80, 100), anchor="mm")
    else:
        p = make_pose(dict(c="fakenoah", anim="baby", expr="sleep"), t, 5, 0, 1)
        bi, ox, oy = draw_character("fakenoah", p, 9.0)
        scene.alpha_composite(bi, (int(960 - ox), int(980 - oy)))


def paint_bouncer_hand(spec, t, dur):
    if not spec.get("hand"):
        return None
    ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([-100, 940, 520, 1120], 60, fill=(52, 68, 108), outline=OUT, width=6)
    d.rounded_rectangle([440, 920, 720, 1100], 80, fill=(238, 196, 160), outline=OUT, width=6)
    for k in range(3):
        d.rounded_rectangle([680, 930 + k * 46, 800, 970 + k * 46], 20, fill=(238, 196, 160), outline=OUT, width=5)
    return ov


def paint_title(scene, t, dur):
    scene.paste((10, 8, 10, 255), [0, 0, SW, SH])
    nb = note_base().resize((640, 360))
    nb.putalpha(150)
    nb = nb.rotate(-6, expand=True)
    scene.alpha_composite(nb, (1220, 520))
    d = ImageDraw.Draw(scene)
    jit = (random.Random(int(t * 24)).uniform(-6, 6) if t < 0.8 or (t % 2.3) < 0.1 else 0)
    for dx, col in ((-6 + jit, (255, 0, 40, 160)), (6 - jit, (0, 220, 255, 120)), (0, (240, 235, 225, 255))):
        d.text((760 + dx, 330), "THE PARENTS", font=font(FT, 110), fill=col, anchor="mm")
        d.text((760 + dx, 460), "LEFT ME", font=font(FT, 110), fill=col, anchor="mm")
    d.text((760, 640), "5 RULES", font=font(FT, 190), fill=(200, 20, 30), anchor="mm")
    d.line([(330, 760), (1190, 760)], fill=(200, 20, 30), width=6)
    d.text((760, 820), "A BABYSITTING HORROR STORY", font=font(FB, 40), fill=(200, 195, 190), anchor="mm")


def paint_endcard_text(d, t):
    blink = (t % 3.0) < 0.12
    if not blink:
        for x in (900, 1020):
            d.ellipse([x - 22, 230, x + 22, 250], fill=(230, 230, 220))
            d.ellipse([x - 6, 232, x + 6, 248], fill=(0, 0, 0))
    d.text((960, 410), "IT'S STILL ASKING FOR YOU...", font=font(FT, 66), fill=(200, 20, 30), anchor="mm")
    d.text((960, 520), "THANKS FOR WATCHING", font=font(FB, 44), fill=(220, 215, 210), anchor="mm")
    d.text((960, 950), "Would YOU take the job next Friday? Tell us in the comments.", font=font(FB, 34), fill=(170, 165, 160), anchor="mm")
