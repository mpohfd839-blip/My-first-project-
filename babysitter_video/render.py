"""Frame renderer. Usage: python3 render.py <start_frame> <end_frame> <out.mp4>  |  python3 render.py --still t1,t2,..."""
import json, math, random, sys, subprocess, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from story import SHOTS
import bgs, bgs2, paint2
bgs.BUILDERS.update(bgs2.BUILDERS)
from bgs import Cv, SW, SH, OUT
from chars import draw_character, make_pose

FPS = 24
OW, OH = 1280, 720
END_EXTRA = 9.0
FONT_SUB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_TITLE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_HAND = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"

TL = json.load(open("timeline.json"))
AUDIO_DUR = TL["duration"]

# ------------------------------------------------------------------ timing
shots = []
for i, (spec, lines) in enumerate(SHOTS):
    ss = TL["timeline"][i]["sentences"]
    shots.append(dict(spec=spec, sents=ss, idx=i))
for i, s in enumerate(shots):
    if s["sents"]:
        s["t0"] = max(0.0, s["sents"][0]["start"] - 0.25)
    else:
        s["t0"] = (shots[i - 1]["sents"][-1]["end"] + 0.6 if shots[i - 1]["sents"] else shots[i - 1]["t0"] + 3.0)
shots[0]["t0"] = 0.0
TOTAL = AUDIO_DUR + END_EXTRA
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL
NFRAMES = int(TOTAL * FPS)

# subtitle cues (split long sentences)
CUES = []
for s in shots:
    for se in s["sents"]:
        txt = se["text"].upper()
        a, b = se["start"], se["end"]
        parts = [txt]
        if len(txt) > 70:
            words = txt.split(" ")
            parts, cur = [], ""
            for w in words:
                if len(cur) + len(w) > 52 and cur:
                    parts.append(cur.strip()); cur = ""
                cur += w + " "
                if cur.rstrip().endswith((",", ";", ":")) and len(cur) > 28:
                    parts.append(cur.strip()); cur = ""
            if cur.strip():
                parts.append(cur.strip())
        L = sum(len(p) for p in parts)
        t = a
        for p in parts:
            d = (b - a) * len(p) / L
            CUES.append((t, t + d + (0.35 if p is parts[-1] else 0.0), p))
            t += d

# mouth envelope from narration
def load_env():
    if os.path.exists("env.npy"):
        return np.load("env.npy")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "narration.mp3", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 8000 // FPS
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    env = np.clip((rms - 0.015) / 0.09, 0, 1)
    np.save("env.npy", env)
    return env
ENV = load_env()
def env_at(t):
    i = int(t * FPS)
    if 0 <= i < len(ENV):
        # quantize for snappy cartoon mouth
        v = ENV[i]
        return 0.0 if v < 0.12 else (0.45 if v < 0.45 else 0.85)
    return 0.0

# ------------------------------------------------------------------ caches
@functools.lru_cache(maxsize=40)
def get_bg(key):
    name, args = key
    a = json.loads(args)
    bg, fg = bgs.BUILDERS[name](a)
    fgbb = fg.getbbox() if fg is not None else None
    return bg, fg, fgbb

def bg_key(spec):
    a = {k: spec.get(k) for k in ("car", "night", "toys", "xmas", "props", "puddle", "door_glow", "empty_chair", "wall", "corn_wall", "plates", "fx", "closet", "mobile", "wet_bouncer", "monitor_table", "bed", "room", "open_door", "door") if spec.get(k) is not None}
    return (spec["bg"], json.dumps(a, sort_keys=True))

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ actor rendering
def place_actor(scene, box, actor, t, dur, gt, seed):
    pose = make_pose(actor, t, dur, env_at(gt), seed)
    opts = {"wet": actor.get("wet"), "healthy": actor.get("healthy")}
    alpha = actor.get("alpha", 1.0)
    bust = actor.get("bust", False)
    x, y, s = actor["x"], actor["y"], actor["s"]
    anim = actor.get("anim")
    if anim in ("walk", "drag", "run", "backaway") and "x1" in actor:
        k = min(1.0, t / max(1.0, dur * 0.9))
        x = x + (actor["x1"] - x) * k
    if bust:
        u = s * SH / 56.0
    else:
        u = s * SH / 112.0
    if anim in ("sleep", "wake"):
        u = 9.5
        bust = True
    if anim == "sleep_bed":
        u = 9.5
        bust = True
    img, ox, oy = draw_character(actor["c"], pose, u, bust=bust, alpha=alpha, opts=opts)
    X, Y = x * SW, y * SH
    if actor.get("lying"):
        img = img.rotate(90, expand=True, resample=Image.BICUBIC)
        px, py = X - img.width / 2, Y - img.height * 0.6
    elif anim == "sleep_bed":
        px, py = 960 - img.width / 2, 900 - img.height
    elif anim == "sleep":
        px, py = 670 - img.width / 2, 965 - img.height
    elif anim == "wake":
        px, py = 670 - img.width / 2, 870 - img.height + math.sin(t * 30) * 2
    elif bust:
        px, py = X - img.width / 2, Y - img.height
    else:
        px, py = X - ox, Y - oy
    scene.alpha_composite(img, (int(px - box[0]), int(py - box[1])))
    # breath vapour
    if False and actor.get("breath"):
        ph = (t * 0.45 + seed * 0.1) % 1.0
        if ph < 0.6:
            mx = X + (actor.get("look", (0, 0))[0]) * u * 4
            my = (Y - img.height + (78 - 31) * u) if bust else (Y - 89 * u)
            d = ImageDraw.Draw(scene)
            for k in range(3):
                r = u * (2 + ph * 10 + k * 2)
                a = int(70 * (1 - ph / 0.6))
                sd = (1 if actor.get("look", (0, 0))[0] >= 0 else -1)
                cx = mx + sd * u * (9 + ph * 16) + k * u * 2 * sd
                cy = my - ph * u * 6 + u * 3
                d.ellipse([cx - r - box[0], cy - r * .6 - box[1], cx + r - box[0], cy + r * .6 - box[1]], fill=(235, 240, 250, a))

# ------------------------------------------------------------------ special scene painters
def kid_img(name, expr="smile", u=3.0, sit=False, seed=1, t=0.0):
    a = dict(c=name, anim="idle", expr=expr, sit=sit)
    p = make_pose(a, t, 5, 0, seed)
    return draw_character(name, p, u)

@functools.lru_cache(maxsize=16)
def album_page(kid, page):
    c = Cv()
    c.rect(0, 0, SW, SH, (90, 50, 40), ol=False)
    c.poly([(120, 80), (950, 110), (950, 1040), (100, 1000)], (245, 238, 220), w=4)
    c.poly([(970, 110), (1800, 80), (1820, 1000), (970, 1040)], (245, 238, 220), w=4)
    c.line([(960, 100), (960, 1050)], (150, 130, 110), 8)
    img = c.done()
    d = ImageDraw.Draw(img)
    rnd = random.Random(page * 7 + len(kid))
    slots = [(180, 170), (520, 220), (250, 600), (1040, 160), (1380, 210), (1100, 610)]
    scenes = [((250, 230, 210), "cake"), ((150, 200, 240), "ears"), ((200, 220, 180), "school"), ((160, 210, 160), "swing"), ((230, 200, 200), "xmas"), ((200, 200, 230), "plain")]
    font = ImageFont.truetype(FONT_HAND, 30)
    for i, (x, y) in enumerate(slots):
        w, h = 330, 330
        ang = rnd.uniform(-5, 5)
        ph = Image.new("RGBA", (w, h + 60), (250, 250, 248, 255))
        pd = ImageDraw.Draw(ph)
        col, kind = scenes[(i + page) % len(scenes)]
        pd.rectangle([18, 18, w - 18, h - 18], fill=col)
        if kid:
            age_u = 2.3 + 0.25 * ((i + page) % 3)
            ki, ox, oy = kid_img(kid, "happy" if i % 2 == 0 else "smile", age_u, seed=i)
            ph.alpha_composite(ki, (int(w / 2 - ox), int(h - 18 - oy + 20)))
            if kind == "ears":
                pd.ellipse([w / 2 - 70, 60, w / 2 - 20, 110], fill=(20, 20, 20))
                pd.ellipse([w / 2 + 20, 60, w / 2 + 70, 110], fill=(20, 20, 20))
            if kind == "cake":
                pd.rectangle([w / 2 - 60, h - 90, w / 2 + 60, h - 30], fill=(250, 210, 225), outline=OUT, width=3)
            if kind == "swing":
                pd.line([(60, 20), (60, h - 20)], fill=(130, 90, 55), width=8)
                pd.line([(w - 60, 20), (w - 60, h - 20)], fill=(130, 90, 55), width=8)
        pd.rectangle([18, 18, w - 18, h - 18], outline=(40, 40, 40), width=2)
        if page == 6 and i % 2 == 1:
            # cut-out hole where a sibling was removed
            pd.polygon([(w * .55, 30), (w - 25, 40), (w - 30, h - 30), (w * .6, h - 25)], fill=(90, 50, 40))
        label = {0: "1st birthday", 1: "Disney World!", 2: "Kindergarten", 3: "the swing set", 4: "Christmas", 5: "Summer"}[(i + page) % 6]
        nm = "Lily" if kid == "klily" else "Emma"
        pd.text((w / 2, h + 20), f"{nm} - {label}", font=font, fill=(50, 50, 110), anchor="mm")
        ph = ph.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(ph, (x, y))
    return img

def paint_album(scene, spec, t, dur):
    img = album_page(spec.get("kid", "kemma"), spec.get("page", 0))
    scene.paste(img, (0, 0))
    if spec.get("flip"):
        # rapid page flipping
        ph = (t * 1.6) % 1.0
        d = ImageDraw.Draw(scene)
        x = 1800 - ph * 1660
        d.polygon([(960, 100), (x, 80 + 60 * math.sin(ph * math.pi)), (x, 1000 + 40 * math.sin(ph * math.pi)), (960, 1040)], fill=(238, 230, 210), outline=OUT, width=4)

@functools.lru_cache(maxsize=8)
def polaroid_img(side, scratched, back_text):
    W, H = 900, 1040
    im = Image.new("RGBA", (W, H), (244, 241, 230, 255))
    d = ImageDraw.Draw(im)
    if side == "front":
        ph = Image.new("RGBA", (800, 780), (0, 0, 0, 255))
        c = Cv(800, 780)
        c.grad(0, 0, 800, 360, (150, 190, 215), (210, 225, 220))
        c.rect(0, 340, 800, 780, (130, 170, 90), ol=False)
        c.rect(0, 330, 800, 380, (90, 140, 170), ol=False)
        c.line([(120, 780), (220, 120)], (130, 90, 55), 22)
        c.line([(680, 780), (580, 120)], (130, 90, 55), 22)
        c.line([(200, 125), (600, 125)], (120, 80, 50), 26)
        for x in (290, 510):
            c.line([(x - 50, 125), (x - 50, 560)], (90, 80, 70), 4)
            c.line([(x + 50, 125), (x + 50, 560)], (90, 80, 70), 4)
            c.rect(x - 70, 555, x + 70, 575, (120, 80, 50))
        ph = c.done()
        left, right = ("kemma", "klily")
        for x, nm in ((290, left), (510, right)):
            p = make_pose(dict(c=nm, anim="idle", expr="happy", sit=True), 0.3, 5, 0, 2)
            p["aL"] = (150, -10); p["aR"] = (150, -10)
            ki, ox, oy = draw_character(nm, p, 4.4)
            ph.alpha_composite(ki, (int(x - ox), int(600 - oy)))
        # scratches
        sx = 290 if scratched == "left" else 510
        dd = ImageDraw.Draw(ph)
        rnd = random.Random(5 if scratched == "right" else 9)
        for k in range(70):
            y0 = rnd.uniform(240, 420)
            x0 = sx + rnd.uniform(-75, 75)
            dd.line([(x0, y0), (x0 + rnd.uniform(-60, 60), y0 + rnd.uniform(-50, 50))], fill=rnd.choice([(250, 250, 245), (200, 195, 190), (60, 50, 50)]), width=rnd.randint(3, 8))
        # aged tone
        arr = np.asarray(ph.convert("RGB")).astype(np.float32)
        arr = arr * np.array([1.05, 0.97, 0.82]) + 12
        ph = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        im.paste(ph, (50, 50))
        d.rectangle([50, 50, 850, 830], outline=(150, 145, 130), width=3)
    else:
        f = ImageFont.truetype(FONT_HAND, 110)
        d.multiline_text((W / 2, H / 2 - 40), back_text, font=f, fill=(60, 80, 170), anchor="mm", align="center", spacing=30)
        rnd = random.Random(3)
        for k in range(300):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            d.point((x, y), fill=(200, 195, 180))
    # curled worn edges
    d.rectangle([0, 0, W - 1, H - 1], outline=(180, 175, 160), width=6)
    return im

def paint_polaroid(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    scene.paste((95, 62, 40, 255), [0, 0, SW, SH])
    for y in range(0, SH, 90):
        d.line([(0, y), (SW, y + 20)], fill=(80, 52, 34), width=6)
    if spec.get("wallet"):
        d.rounded_rectangle([300, 200, 1620, 1000], 40, fill=(70, 40, 25), outline=OUT, width=6)
    pim = polaroid_img(spec.get("side", "front"), spec.get("scratched", "right") if not spec.get("swap") else "left", spec.get("back_text", ""))
    ang = -4 + math.sin(t * 0.8) * 0.8
    r = pim.rotate(ang, expand=True, resample=Image.BICUBIC)
    sc = 0.95
    r = r.resize((int(r.width * sc), int(r.height * sc)), Image.BILINEAR)
    # shadow
    shd = Image.new("RGBA", r.size, (0, 0, 0, 0))
    shd.putalpha(r.getchannel("A").point(lambda v: v * 0.5))
    scene.alpha_composite(shd.filter(ImageFilter.GaussianBlur(12)) if False else shd, (int(SW / 2 - r.width / 2 + 25), int(SH / 2 - r.height / 2 + 30)))
    scene.alpha_composite(r, (int(SW / 2 - r.width / 2), int(SH / 2 - r.height / 2)))
    # fingers holding
    d.ellipse([SW / 2 - r.width / 2 - 40, SH / 2 + 220, SW / 2 - r.width / 2 + 90, SH / 2 + 330], fill=(232, 190, 155), outline=OUT, width=5)
    d.ellipse([SW / 2 + r.width / 2 - 90, SH / 2 + 200, SW / 2 + r.width / 2 + 40, SH / 2 + 310], fill=(232, 190, 155), outline=OUT, width=5)

def paint_clock(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    scene.paste((12, 12, 18, 255), [0, 0, SW, SH])
    d.rounded_rectangle([360, 300, 1560, 800], 60, fill=(25, 25, 28), outline=(60, 60, 65), width=8)
    d.rounded_rectangle([420, 360, 1500, 740], 30, fill=(8, 6, 6))
    f = ImageFont.truetype(FONT_SUB, 300)
    glow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    txt = "2:47" if (t % 1.0) < 0.6 else "2 47"
    gd.text((960, 560), txt, font=f, fill=(255, 40, 30, 255), anchor="mm")
    blur = glow.filter(ImageFilter.GaussianBlur(18))
    scene.alpha_composite(blur)
    scene.alpha_composite(glow)
    d.text((1430, 690), "AM", font=ImageFont.truetype(FONT_SUB, 50), fill=(255, 40, 30), anchor="mm")

def paint_tv(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    rnd = random.Random(int(t * 4))
    for k in range(14):
        x = 400 + ((k * 97 + t * (60 + k * 7)) % 1100)
        y = 220 + (k * 53 % 560)
        col = (230, 60, 50) if k % 2 else (240, 240, 240)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=col, outline=OUT, width=3)
    d.rectangle([340, 780, 1580, 860], fill=(20, 20, 60))
    d.text((380, 820), "OSU 14  -  MICH 10   3RD QTR", font=ImageFont.truetype(FONT_SUB, 40), fill=(255, 255, 255), anchor="lm")
    vol = int(20 + 80 * min(1, t / max(1, dur * 0.85)))
    d.rectangle([420, 220, 1200, 270], fill=(0, 0, 0, 200))
    d.rectangle([430, 230, 430 + 760 * vol / 100, 260], fill=(60, 220, 90))
    d.text((1240, 245), f"VOL {vol}", font=ImageFont.truetype(FONT_SUB, 42), fill=(60, 220, 90), anchor="lm")

def paint_notebook(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    fade = 1.0
    if spec.get("fading"):
        fade = max(0.0, 1 - t / max(1, dur))
    k = min(1, t / max(0.5, dur * 0.7)) if not spec.get("fading") else 1.0
    pts_all = []
    for j, (cx, cy) in enumerate(((340, 260), (360, 520), (330, 780))):
        pts = []
        n = 160
        for i in range(int(n * min(1, k * 3 - j) if k * 3 - j > 0 else 0)):
            a = i / n * 6 * math.pi
            r = 6 + i * 0.45
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        if len(pts) > 1:
            d.line(pts, fill=(60, 60, 70, int(255 * fade)), width=4)
            if not spec.get("fading") and len(pts) < n:
                px, py = pts[-1]
                d.line([(px, py), (px + 220, py - 300)], fill=(230, 190, 60), width=26)
                d.line([(px, py), (px + 30, py - 40)], fill=(240, 210, 170), width=26)

def paint_floor(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    if spec.get("puddle_only"):
        R = 260
    else:
        R = 60 + 200 * min(1, t / max(1, dur))
    d.ellipse([960 - R * 1.6, 620 - R * .6, 960 + R * 1.6, 620 + R * .6], fill=(55, 70, 95), outline=(140, 160, 190), width=3)
    if not spec.get("puddle_only"):
        for k in range(3):
            ph = (t * 1.1 + k / 3) % 1.0
            y = -50 + ph * 650
            d.ellipse([950, y - 22, 970, y + 22], fill=(170, 200, 230), outline=OUT, width=3)
            if ph > 0.9:
                rr = (ph - 0.9) * 10 * 120
                d.ellipse([960 - rr * 1.6, 620 - rr * .5, 960 + rr * 1.6, 620 + rr * .5], outline=(190, 210, 235), width=4)

def paint_road(scene, spec, t, dur, interior=False):
    d = ImageDraw.Draw(scene)
    speed = 900 if spec.get("car") != "parked" else 0
    off = (t * speed) % 400
    # far trees
    for k in range(-1, 30):
        x = k * 90 - (t * speed * 0.15) % 90
        d.ellipse([x - 70, 470, x + 70, 620], fill=(95, 100, 85))
    d.rectangle([0, 580, SW, 760], fill=(140, 130, 85))
    rnd = random.Random(1)
    for k in range(-1, 70):
        x = k * 30 - (t * speed * 0.6) % 30
        h = 130 + (k * 37 % 50)
        d.line([(x, 760), (x + 4, 760 - h)], fill=(160, 150, 80), width=6)
        d.line([(x, 760 - h * .6), (x + 22, 760 - h * .7)], fill=(150, 140, 70), width=4)
    d.rectangle([0, 760, SW, 960], fill=(70, 70, 75))
    for k in range(-1, 8):
        x = k * 400 - off
        d.rectangle([x, 855, x + 200, 868], fill=(240, 220, 120))
    d.rectangle([0, 960, SW, SH], fill=(120, 115, 80))
    for k in range(-1, 12):
        x = k * 200 - (t * speed * 1.3) % 200
        d.rectangle([x, 900, x + 14, 1040], fill=(140, 110, 80), outline=OUT, width=3)
    d.line([(0, 940), (SW, 940)], fill=(120, 95, 70), width=6)
    c = Cv()
    cx = 960 + math.sin(t * 1.3) * 8
    cy = 900 + abs(math.sin(t * 9)) * 3
    people = None
    if spec.get("car") == "int_lily":
        people = [(-40, (60, 45, 35)), (60, (150, 70, 40)), (-110, (25, 25, 30))]
    elif spec.get("car") == "drive":
        people = [(-40, (60, 45, 35)), (60, (150, 70, 40))]
    bgs.draw_car(c, cx, cy, 1.4, people=people)
    bgs.wheel(c, cx - 230, cy - 20, 1.4, t * 12)
    bgs.wheel(c, cx + 200, cy - 20, 1.4, t * 12)
    car = c.done()
    scene.alpha_composite(car)

def paint_car_arrive(scene, spec, t, dur):
    k = ease(t / max(1, dur * 0.8))
    c = Cv()
    x = -300 + k * 1100
    y = 980
    bgs.draw_car(c, x, y, 0.9, people=[(-40, (60, 45, 35)), (60, (150, 70, 40))])
    bgs.wheel(c, x - 150, y - 12, 0.9, k * 40)
    bgs.wheel(c, x + 130, y - 12, 0.9, k * 40)
    scene.alpha_composite(c.done())

def paint_car_int_bg(scene, spec, t):
    d = ImageDraw.Draw(scene)
    # moving corn through rear window
    d.polygon([(300, 120), (1620, 120), (1700, 420), (220, 420)], fill=(180, 182, 184))
    for k in range(-1, 60):
        x = 220 + ((k * 28 + t * 380) % 1500)
        d.line([(x, 420), (x + 4, 300 + (k * 13 % 50))], fill=(150, 140, 80), width=6)
    d.polygon([(300, 120), (1620, 120), (1700, 420), (220, 420)], outline=OUT, width=6)
    c = Cv()
    bgs.car_seats(c, spec.get("empty_seat"))
    scene.alpha_composite(c.done())

@functools.lru_cache(maxsize=2)
def seats_img(empty):
    c = Cv()
    bgs.car_seats(c, empty)
    return c.done()

def paint_mirror(scene, spec, t, dur, actors, gt):
    d = ImageDraw.Draw(scene)
    # windshield view ahead
    d.rectangle([0, 0, SW, 520], fill=(175, 178, 182))
    d.rectangle([0, 520, SW, SH], fill=(140, 130, 85))
    d.polygon([(900, 520), (1020, 520), (1700, SH), (220, SH)], fill=(70, 70, 75))
    for k in range(6):
        ph = ((k / 6) + t * 0.9) % 1.0
        y0 = 520 + (ph ** 2) * 560
        y1 = 520 + (min(1, ph + 0.05) ** 2) * 560
        w0 = 2 + ph * 14
        d.polygon([(960 - w0, y0), (960 + w0, y0), (960 + w0 * 1.2, y1), (960 - w0 * 1.2, y1)], fill=(240, 220, 120))
    d.rectangle([0, 0, SW, 90], fill=(40, 40, 44))
    d.rectangle([930, 0, 990, 250], fill=(30, 30, 32))
    # mirror
    mx0, my0, mx1, my1 = 360, 230, 1560, 760
    inner = Image.new("RGBA", (mx1 - mx0, my1 - my0), (95, 92, 90, 255))
    idr = ImageDraw.Draw(inner)
    idr.rectangle([0, 0, inner.width, 120], fill=(170, 175, 180))
    for k in range(-1, 40):
        x = ((k * 40 - t * 300) % (inner.width + 80)) - 40
        idr.line([(x, 120), (x + 3, 40 + k * 7 % 40)], fill=(150, 140, 80), width=6)
    idr.rectangle([0, 120, inner.width, inner.height], fill=(85, 80, 75))
    idr.rectangle([60, 300, inner.width - 60, inner.height], fill=(95, 90, 84), outline=OUT, width=5)
    for a in actors:
        if spec.get("show_lily"):
            aa = dict(a)
            pose_box = (mx0, my0)
            sub = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
            place_actor(sub, (0, 0), aa, t, dur, gt, 7)
            inner.alpha_composite(sub.crop((mx0, my0, mx1, my1)))
    inner = inner.transpose(Image.FLIP_LEFT_RIGHT)
    mask = Image.new("L", inner.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, inner.width - 1, inner.height - 1], 120, fill=255)
    d.rounded_rectangle([mx0 - 26, my0 - 26, mx1 + 26, my1 + 26], 140, fill=(25, 25, 28), outline=OUT, width=6)
    scene.paste(inner, (mx0, my0), mask)
    # glass sheen
    sheen = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    ImageDraw.Draw(sheen).polygon([(mx0 + 80, my0), (mx0 + 260, my0), (mx0 + 60, my1), (mx0 - 20, my1)], fill=(255, 255, 255, 28))
    scene.alpha_composite(sheen)

def paint_hospital(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    flat_at = dur * 0.55
    pts = []
    for i in range(0, 1120, 4):
        x = 400 + i
        tt = t - (1120 - i) / 500.0
        y = 500
        if tt < flat_at:
            ph = (tt * 1.4) % 1.0
            if 0.1 < ph < 0.14:
                y = 500 - (ph - 0.1) / 0.04 * 220
            elif 0.14 <= ph < 0.18:
                y = 280 + (ph - 0.14) / 0.04 * 300
            elif 0.18 <= ph < 0.2:
                y = 580 - (ph - 0.18) / 0.02 * 80
        pts.append((x, y))
    d.line(pts, fill=(80, 255, 120), width=6)
    bpm = "72" if t < flat_at else "0"
    d.text((1460, 230), bpm, font=ImageFont.truetype(FONT_SUB, 60), fill=(80, 255, 120), anchor="rm")

def paint_fire(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    # yellow dress hanging out of barrel
    d.polygon([(900, 560), (1000, 560), (1040, 470), (870, 470)], fill=(245, 205, 60), outline=OUT)
    rnd = random.Random(int(t * 12))
    for k in range(18):
        x = 790 + k * 20 + rnd.uniform(-10, 10)
        h = 120 + rnd.uniform(0, 260) * (0.6 + 0.4 * math.sin(t * 6 + k))
        w = 40 + rnd.uniform(0, 30)
        col = rnd.choice([(255, 120, 30), (255, 180, 50), (255, 80, 20), (255, 220, 120)])
        d.polygon([(x - w / 2, 580), (x + w / 2, 580), (x + rnd.uniform(-15, 15), 580 - h)], fill=col)
    for k in range(8):
        y = 520 - ((t * 120 + k * 80) % 520)
        x = 960 + math.sin(t * 2 + k) * 60
        r = 30 + (520 - y) / 6
        d.ellipse([x - r, y - r, x + r, y + r], fill=(90, 90, 95, 90))

def paint_lake2009(scene, spec, t, dur, actors, gt):
    d = ImageDraw.Draw(scene)
    for i, (px, ph) in enumerate(((560 + 120, 0.0), (1100 - 120, 1.5))):
        th = math.radians(20 * math.sin(t * 2.2 + ph)) if not spec.get("swing_empty") else math.radians(8 * math.sin(t * 1.2 + ph))
        L = 430
        sx, sy = px + L * math.sin(th), 425 + L * math.cos(th)
        d.line([(px - 45, 425), (sx - 45, sy)], fill=(90, 80, 70), width=5)
        d.line([(px + 45, 425), (sx + 45, sy)], fill=(90, 80, 70), width=5)
        d.rectangle([sx - 65, sy - 4, sx + 65, sy + 14], fill=(120, 80, 50), outline=OUT, width=4)
        for a in actors:
            if a.get("anim") == "swing" and ((i == 0 and a["c"] == "kemma") or (i == 1 and a["c"] == "klily")):
                p = make_pose(dict(c=a["c"], anim="idle", expr="happy", sit=True), t, dur, 0, i + 2)
                p["aL"] = (165, -5); p["aR"] = (165, -5)
                ki, ox, oy = draw_character(a["c"], p, 3.5)
                ki = ki.rotate(-math.degrees(th), resample=Image.BICUBIC, center=(ox, oy - 30 * 3.5))
                scene.alpha_composite(ki, (int(sx - ox), int(sy + 4 - oy + 28 * 3.5 - 30 * 3.5 + 30 * 3.5 - 28 * 3.5 + 0)))
    if spec.get("ripples"):
        for k in range(4):
            r = ((t * 120 + k * 70) % 280)
            d.ellipse([500 - r * 1.8, 610 - r * .3, 500 + r * 1.8, 610 + r * .3], outline=(200, 220, 235, int(255 * (1 - r / 280))), width=4)
        if t < 1.2:
            d.ellipse([470, 590, 530, 630], fill=(245, 205, 60))
    if any(a.get("anim") == "cpr" for a in actors):
        # little girl lying on the shore
        p = make_pose(dict(c="kemma", anim="idle", expr="sleep"), 0, 5, 0, 1)
        ki, ox, oy = draw_character("klily", p, 2.8)
        ki = ki.rotate(90, expand=True, resample=Image.BICUBIC)
        scene.alpha_composite(ki, (300, 880))
        # ambulance lights
        on = (t * 3) % 1 < 0.5
        d.ellipse([1500, 700, 1560, 760], fill=(255, 40, 40) if on else (60, 60, 200))
        d.rectangle([1380, 740, 1820, 960], fill=(240, 240, 240), outline=OUT, width=5)
        d.rectangle([1560, 790, 1640, 830], fill=(220, 40, 40))
        d.rectangle([1590, 770, 1610, 850], fill=(220, 40, 40))

def paint_hands(scene, spec, t, dur):
    d = ImageDraw.Draw(scene)
    def hand(x, y, col, a=255, ang=0):
        im = Image.new("RGBA", (700, 420), (0, 0, 0, 0))
        hd = ImageDraw.Draw(im)
        hd.rounded_rectangle([150, 120, 520, 330], 90, fill=col + (a,), outline=(38, 28, 30, a), width=6)
        for k in range(4):
            hd.rounded_rectangle([480, 120 + k * 52, 660, 168 + k * 52], 24, fill=col + (a,), outline=(38, 28, 30, a), width=6)
        hd.rounded_rectangle([0, 150, 200, 300], 30, fill=(52, 68, 108, a) if col[0] > 236 else (214, 160, 58, a), outline=(38, 28, 30, a), width=6)
        im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
        scene.alpha_composite(im, (int(x), int(y)))
    hand(520, 520, (238, 196, 160), 255, 10)
    k = min(1, t / 1.5)
    a = int(255 * spec.get("hand_alpha", .3) * (0.6 + 0.4 * math.sin(t * 3)))
    hand(100 + 420 * ease(k), 440, (244, 205, 175), a, -6)

def paint_title(scene, t, dur):
    scene.paste((10, 8, 10, 255), [0, 0, SW, SH])
    pim = polaroid_img("front", "right", "")
    r = pim.rotate(-6, expand=True, resample=Image.BICUBIC).resize((520, 600))
    r.putalpha(r.getchannel("A").point(lambda v: int(v * 0.55)))
    scene.alpha_composite(r, (1260, 300))
    d = ImageDraw.Draw(scene)
    f = ImageFont.truetype(FONT_TITLE, 104)
    f2 = ImageFont.truetype(FONT_TITLE, 70)
    jit = (random.Random(int(t * 24)).uniform(-6, 6) if t < 0.8 or (t % 2.3) < 0.1 else 0)
    for dx, col in ((-6 + jit, (255, 0, 40, 160)), (6 - jit, (0, 220, 255, 120)), (0, (240, 235, 225, 255))):
        d.text((720 + dx, 380), "MY GIRLFRIEND", font=f, fill=col, anchor="mm")
        d.text((720 + dx, 510), "HAS NEVER HAD", font=f, fill=col, anchor="mm")
    d.text((720, 650), "A SISTER", font=ImageFont.truetype(FONT_TITLE, 140), fill=(200, 20, 30), anchor="mm")
    d.line([(300, 740), (1140, 740)], fill=(200, 20, 30), width=6)
    d.text((720, 800), "A HORROR STORY", font=ImageFont.truetype(FONT_SUB, 40), fill=(200, 195, 190), anchor="mm")

def draw_like_sub(d, scene, cx, cy, t, scale=1.0):
    """Animated LIKE + SUBSCRIBE + bell (on a scene-sized canvas)."""
    s = scale
    clicked_like = t > 1.1
    clicked_sub = t > 2.0
    bell = t > 2.7
    # like button
    lw = 300 * s
    d.rounded_rectangle([cx - 700 * s, cy - 60 * s, cx - 700 * s + lw, cy + 60 * s], 60 * s, fill=(240, 240, 240) if not clicked_like else (50, 120, 230), outline=OUT, width=int(5 * s))
    tc = (30, 30, 30) if not clicked_like else (255, 255, 255)
    # thumb
    tx, ty = cx - 640 * s, cy
    d.rounded_rectangle([tx - 25 * s, ty - 10 * s, tx + 30 * s, ty + 38 * s], 10 * s, fill=tc)
    d.polygon([(tx - 10 * s, ty - 10 * s), (tx + 5 * s, ty - 45 * s), (tx + 20 * s, ty - 40 * s), (tx + 15 * s, ty - 10 * s)], fill=tc)
    d.rectangle([tx - 45 * s, ty - 8 * s, tx - 30 * s, ty + 38 * s], fill=tc)
    d.text((cx - 520 * s, cy), "LIKE", font=ImageFont.truetype(FONT_SUB, int(52 * s)), fill=tc, anchor="mm")
    # subscribe
    sw_ = 460 * s
    sx0 = cx - 330 * s
    d.rounded_rectangle([sx0, cy - 60 * s, sx0 + sw_, cy + 60 * s], 60 * s if clicked_sub else 14 * s, fill=(204, 0, 0) if not clicked_sub else (90, 90, 90), outline=OUT, width=int(5 * s))
    d.text((sx0 + sw_ / 2, cy), "SUBSCRIBED" if clicked_sub else "SUBSCRIBE", font=ImageFont.truetype(FONT_SUB, int(50 * s)), fill=(255, 255, 255), anchor="mm")
    # bell
    bx, by = cx + 230 * s, cy
    ang = math.sin(t * 25) * 18 if bell and t < 3.6 else 0
    bel = Image.new("RGBA", (int(160 * s), int(160 * s)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bel)
    c0 = 80 * s
    bd.pieslice([c0 - 45 * s, c0 - 55 * s, c0 + 45 * s, c0 + 35 * s], 180, 360, fill=(255, 255, 255) if bell else (230, 230, 230), outline=OUT, width=int(4 * s))
    bd.rectangle([c0 - 45 * s, c0 - 12 * s, c0 + 45 * s, c0 + 25 * s], fill=(255, 255, 255) if bell else (230, 230, 230))
    bd.polygon([(c0 - 58 * s, c0 + 35 * s), (c0 + 58 * s, c0 + 35 * s), (c0 + 45 * s, c0 + 15 * s), (c0 - 45 * s, c0 + 15 * s)], fill=(255, 255, 255) if bell else (230, 230, 230), outline=OUT)
    bd.ellipse([c0 - 12 * s, c0 + 35 * s, c0 + 12 * s, c0 + 55 * s], fill=(255, 255, 255), outline=OUT, width=int(3 * s))
    bel = bel.rotate(ang, resample=Image.BICUBIC)
    scene.alpha_composite(bel, (int(bx - 80 * s), int(by - 80 * s)))
    # cursor
    if t < 3.2:
        if t < 1.1:
            k = ease(t / 1.1)
            px, py = cx + 200 * s + (-640 * s - 200 * s) * k, cy + 260 * s - 240 * s * k
        elif t < 2.0:
            k = ease((t - 1.1) / 0.9)
            px, py = cx - 640 * s + (-100 * s + 640 * s) * k, cy + 20 * s
        else:
            k = ease((t - 2.0) / 0.7)
            px, py = cx - 100 * s + (330 * s) * k, cy + 20 * s - 10 * s * k
        press = (abs(t - 1.1) < 0.1) or (abs(t - 2.0) < 0.1) or (abs(t - 2.7) < 0.1)
        sc = 0.85 if press else 1.0
        pts = [(0, 0), (0, 70), (18, 54), (32, 84), (44, 78), (30, 50), (52, 50)]
        d.polygon([(px + x * s * sc, py + y * s * sc) for x, y in pts], fill=(255, 255, 255), outline=(0, 0, 0))

def paint_endcard(scene, t, dur):
    scene.paste((8, 6, 8, 255), [0, 0, SW, SH])
    d = ImageDraw.Draw(scene)
    paint2.paint_endcard_text(d, t)
    draw_like_sub(d, scene, 960 + 100, 760, max(0, t - 0.5), 1.15)

@functools.lru_cache(maxsize=1)
def photowall_img():
    bg, _, _ = get_bg(("photowall", "{}"))
    bg = bg.copy()
    rnd = random.Random(12)
    for i in range(16):
        x = 80 + (i % 8) * 290 + rnd.uniform(-20, 20)
        y = 120 + (i // 8) * 420 + rnd.uniform(-30, 30)
        for j, nm in enumerate(("you", "emma")):
            p = make_pose(dict(c=nm, anim="idle", expr="happy", look=((1 if j == 0 else -1) * .5, 0)), 0.5 + i, 5, 0, i + j)
            im, ox, oy = draw_character(nm, p, 3.0, bust=True)
            bg.alpha_composite(im, (int(x + 115 + (j * 2 - 1) * 48 - im.width / 2), int(y + 290 - im.height)))
    return bg

# ------------------------------------------------------------------ scene composition
def render_scene(shot, t, gt, box):
    """Return scene crop for box (x0,y0,x1,y1) in scene coords."""
    spec = shot["spec"]
    dur = shot["t1"] - shot["t0"]
    name = spec["bg"]
    ib = (int(math.floor(box[0])), int(math.floor(box[1])), int(math.ceil(box[2])), int(math.ceil(box[3])))
    full_special = name in ("album", "polaroid", "clock", "title", "endcard", "mirror", "hospital", "road", "hands", "notebook", "floor_drip", "tv", "fire", "car_int")
    if name in ("title", "endcard", "album", "polaroid", "clock", "mirror", "note", "phone", "monitor"):
        scene = Image.new("RGBA", (SW, SH), (0, 0, 0, 255))
        if name == "note":
            paint2.paint_note(scene, spec, t, dur)
        elif name == "phone":
            paint2.paint_phone(scene, spec, t, dur)
        elif name == "monitor":
            paint2.paint_monitor(scene, spec, t, dur)
        elif name == "title":
            paint2.paint_title(scene, t, dur)
        elif name == "endcard":
            paint_endcard(scene, t, dur)
        elif name == "album":
            paint_album(scene, spec, t, dur)
        elif name == "polaroid":
            paint_polaroid(scene, spec, t, dur)
        elif name == "clock":
            paint2.paint_clock(scene, spec, t, dur)
        elif name == "mirror":
            paint_mirror(scene, spec, t, dur, spec["actors"], gt)
        return scene.crop(ib), ib
    bg, fg, fgbb = get_bg(bg_key(spec))
    if name == "photowall":
        bg = photowall_img()
    if name == "face" and spec.get("corn_wall"):
        off = int(t * 260) % SW
        b2 = Image.new("RGBA", (SW, SH))
        b2.paste(bg.crop((off, 0, SW, SH)), (0, 0))
        b2.paste(bg.crop((0, 0, off, SH)), (SW - off, 0))
        scene = b2.crop(ib)
    else:
        scene = bg.crop(ib)
    # dynamic background layers (drawn in full-scene coords on a temp, then cropped)
    DYN2 = {"floor_steps": paint2.paint_floor_steps, "house_windows": paint2.paint_house_windows, "mansion": paint2.paint_mansion_car,
            "living2": paint2.paint_living_lights, "frontdoor_in": paint2.paint_frontdoor_silh, "stairs": paint2.paint_stairs_shape,
            "crib_top": paint2.paint_crib_top, "monitor_table": paint2.paint_monitor_table}
    if name in DYN2 and not (name == "living2" and not spec.get("headlights")) and not (name == "frontdoor_in" and not spec.get("silh")) and not (name == "stairs" and not spec.get("shape")) and not (name == "mansion" and not spec.get("car")):
        tmp = bg.copy()
        DYN2[name](tmp, spec, t, dur)
        scene = tmp.crop(ib)
    if name in ("road", "tv", "notebook", "floor_drip", "hospital", "fire", "hands", "lake2009", "car_int") or (name in ("farm_ext", "farm_xmas") and spec.get("car") == "arrive"):
        tmp = bg.copy()
        if name == "road":
            paint_road(tmp, spec, t, dur)
        elif name == "tv":
            paint_tv(tmp, spec, t, dur)
        elif name == "notebook":
            paint_notebook(tmp, spec, t, dur)
        elif name == "floor_drip":
            paint_floor(tmp, spec, t, dur)
        elif name == "hospital":
            paint_hospital(tmp, spec, t, dur)
        elif name == "fire":
            paint_fire(tmp, spec, t, dur)
        elif name == "hands":
            paint_hands(tmp, spec, t, dur)
        elif name == "lake2009":
            paint_lake2009(tmp, spec, t, dur, spec["actors"], gt)
        elif name == "car_int":
            paint_car_int_bg(tmp, spec, t)
        elif name in ("farm_ext", "farm_xmas"):
            paint_car_arrive(tmp, spec, t, dur)
        scene = tmp.crop(ib)
    for i, a in enumerate(spec["actors"]):
        if name == "lake2009" and a.get("anim") == "swing":
            continue
        aa = dict(a)
        if spec.get("emma_fade") and a["c"] == "emma":
            f0, f1 = spec["emma_fade"]
            aa["alpha"] = f0 + (f1 - f0) * min(1, t / max(1, dur))
        place_actor(scene, ib, aa, t, dur, gt, i * 3 + shot["idx"])
        if a.get("morph"):
            bb = dict(aa); bb["c"] = "fakenoah"; bb["alpha"] = min(1.0, t / max(1.0, dur * 0.8))
            place_actor(scene, ib, bb, t, dur, gt, i * 3 + shot["idx"])
    if fg is not None and fgbb is not None:
        x0, y0 = max(ib[0], fgbb[0]), max(ib[1], fgbb[1])
        x1, y1 = min(ib[2], fgbb[2]), min(ib[3], fgbb[3])
        if x1 > x0 and y1 > y0:
            scene.alpha_composite(fg.crop((x0, y0, x1, y1)), (x0 - ib[0], y0 - ib[1]))
    ov = None
    if name == "closet":
        ov = paint2.paint_closet_over(spec, t, dur)
    elif name == "bouncer_close":
        ov = paint2.paint_bouncer_hand(spec, t, dur)
    if ov is not None:
        scene.alpha_composite(ov.crop(ib))
    return scene, ib

# ------------------------------------------------------------------ camera
def camera_box(shot, t, dur):
    spec = shot["spec"]
    cam = spec.get("cam", "static")
    sw = SW
    if spec["bg"] in ("photowall", "dogwall", "house_windows"):
        sw = get_bg(bg_key(spec))[0].width
    k = ease(t / max(0.001, dur))
    if cam == "static" or cam is None:
        z, cx, cy = 1.0, .5, .5
    elif cam[0] == "z":
        _, z0, z1, cx, cy = cam
        z = z0 + (z1 - z0) * k
    elif cam[0] == "pan":
        _, z, x0, y0, x1, y1 = cam
        cx, cy = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    else:
        z, cx, cy = 1.0, .5, .5
    if cam == "static" and spec["bg"] in ("photowall",):
        z = 1.0
    w, h = SW / z, SH / z
    X = cx * sw + math.sin(t * 0.6 + shot["idx"]) * 6 / z
    Y = cy * SH + math.cos(t * 0.5 + shot["idx"]) * 4 / z
    shake = spec.get("shake", 0)
    if shake:
        X += math.sin(t * 53) * 14 * shake
        Y += math.cos(t * 47) * 10 * shake
    x0 = min(max(X - w / 2, 0), sw - w)
    y0 = min(max(Y - h / 2, 0), SH - h)
    return (x0, y0, x0 + w, y0 + h)

# ------------------------------------------------------------------ post effects
YY, XX = np.mgrid[0:OH, 0:OW].astype(np.float32)
_r = np.sqrt(((XX - OW / 2) / (OW / 2)) ** 2 + ((YY - OH / 2) / (OH / 2)) ** 2)
VIGNETTE = np.clip(1.0 - 0.42 * np.clip(_r - 0.45, 0, None) ** 1.6 * 1.6, 0.25, 1.0)[..., None].astype(np.float32)
rs = np.random.RandomState(7)
GRAIN = [(rs.randn(OH // 2, OW // 2) * 7).astype(np.float32) for _ in range(6)]
GRAIN = [np.kron(g, np.ones((2, 2), np.float32))[..., None] for g in GRAIN]
# paper texture
_pt = np.random.RandomState(3).rand(OH // 8, OW // 8).astype(np.float32)
PAPER = np.array(Image.fromarray((_pt * 255).astype(np.uint8)).resize((OW, OH), Image.BICUBIC)).astype(np.float32)[..., None] / 255.0
PAPER = 0.965 + 0.05 * PAPER

GRADES = {
    "night": ((0.62, 0.68, 0.88), (0, 2, 10)),
    "warm": ((1.06, 0.99, 0.86), (4, 0, 0)),
    "dim": ((0.8, 0.77, 0.78), (0, 0, 0)),
    "overcast": ((0.93, 0.96, 1.0), (0, 0, 0)),
    "cold": ((0.86, 0.94, 1.1), (0, 0, 4)),
    "garage": ((0.98, 0.9, 0.76), (0, 0, 0)),
    "day": ((1.03, 1.02, 0.99), (0, 0, 0)),
    "dawn": ((1.08, 0.95, 0.9), (6, 0, 0)),
    "moon": ((0.85, 0.93, 1.12), (0, 0, 6)),
    "lamp": ((1.12, 0.96, 0.74), (6, 0, 0)),
    "tv_glow": ((0.75, 0.82, 1.02), (0, 0, 8)),
    "dusk": ((1.0, 0.86, 0.92), (6, 0, 6)),
}

def subtitle_img(text):
    return _subtitle_img(text)

@functools.lru_cache(maxsize=64)
def _subtitle_img(text):
    f = ImageFont.truetype(FONT_SUB, 30)
    # wrap
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 46 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    W, H = OW, 46 * len(lines) + 20
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((W / 2, 28 + i * 44), ln, font=f, fill=(255, 255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0, 255))
    return im

def post(img, shot, t, dur, gt, fi):
    spec = shot["spec"]
    fx = spec.get("fx", [])
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    mul = np.array([1.0, 1.0, 1.0], np.float32)
    add = np.array([0.0, 0.0, 0.0], np.float32)
    for f in fx:
        if f in GRADES:
            m, a = GRADES[f]
            mul *= np.array(m, np.float32)
            add += np.array(a, np.float32)
    arr = arr * mul + add
    if "sepia" in fx:
        l = arr @ np.array([0.3, 0.59, 0.11], np.float32)
        arr = np.stack([l * 1.08 + 18, l * 0.95 + 8, l * 0.75], -1) * 0.95
    if "desat" in fx or "overcast" in fx or "memory" in fx:
        amt = 0.55 if "desat" in fx else 0.25
        l = (arr @ np.array([0.3, 0.59, 0.11], np.float32))[..., None]
        arr = arr * (1 - amt) + l * amt
    if "memory" in fx:
        arr = arr * 0.85 + 40
    if "red" in fx:
        p = 0.5 + 0.5 * math.sin(gt * 3.0)
        arr *= np.array([1.0 + 0.18 * p, 1.0 - 0.18 * p, 1.0 - 0.2 * p], np.float32)
    if "siren" in fx:
        on = (gt * 3) % 1 < 0.5
        arr *= np.array([1.18, 0.88, 0.88] if on else [0.88, 0.92, 1.2], np.float32)
    bright = 1.0
    if "flicker" in fx or "tv_glow" in fx:
        r = random.Random(fi)
        bright *= 0.88 + 0.12 * r.random()
    if "old_film" in fx:
        r = random.Random(fi * 3)
        bright *= 0.9 + 0.1 * r.random()
    arr *= bright
    # base mood: slightly crushed contrast for horror
    arr = (arr - 128) * 1.04 + 126
    arr = arr * VIGNETTE * PAPER + GRAIN[fi % 6]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out, "RGBA")
    if "old_film" in fx:
        r = random.Random(fi)
        for k in range(r.randint(0, 3)):
            x = r.uniform(0, OW)
            d.line([(x, 0), (x + r.uniform(-4, 4), OH)], fill=(240, 230, 210, 70), width=1)
        for k in range(r.randint(2, 9)):
            x, y = r.uniform(0, OW), r.uniform(0, OH)
            s = r.uniform(1, 3.5)
            d.ellipse([x - s, y - s, x + s, y + s], fill=(20, 15, 10, 150))
    if "fog" in fx:
        fogim = Image.new("RGB", (OW, OH), (150, 155, 170))
        out = Image.blend(out, fogim, 0.18 + 0.05 * math.sin(gt * 0.5))
        d = ImageDraw.Draw(out, "RGBA")
    if "snow" in fx:
        for k in range(120):
            x = (k * 97.3 + math.sin(gt * 0.7 + k) * 30) % OW
            y = (k * 53.1 + gt * (40 + k % 5 * 12)) % OH
            s = 1.5 + (k % 3)
            d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, 200))
    if spec.get("rain"):
        for k in range(140):
            x = (k * 71.3 + gt * 120) % OW
            y = (k * 37.7 + gt * 900) % OH
            d.line([(x, y), (x - 4, y + 18)], fill=(210, 220, 235, 110), width=1)
    if "drip" in fx:
        for k in range(4):
            x = 200 + k * 290
            y = ((gt * 260 + k * 170) % (OH + 60)) - 30
            d.ellipse([x - 3, y - 7, x + 3, y + 7], fill=(160, 190, 220, 120))
    if "tv_static" in fx:
        nz = (np.random.RandomState(fi).rand(OH // 4, OW // 4) * 255).astype(np.uint8)
        nzi = Image.fromarray(nz).resize((OW, OH), Image.NEAREST).convert("RGB")
        out = Image.blend(out, nzi, 0.12)
        d = ImageDraw.Draw(out, "RGBA")
    if "glitch_in" in fx and t < 0.9:
        a = np.asarray(out).copy()
        r = random.Random(fi)
        sh_ = r.randint(6, 22)
        a[..., 0] = np.roll(a[..., 0], sh_, axis=1)
        a[..., 2] = np.roll(a[..., 2], -sh_, axis=1)
        for k in range(5):
            y0 = r.randint(0, OH - 40)
            hh = r.randint(5, 40)
            a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], r.randint(-60, 60), axis=1)
        out = Image.fromarray(a)
        d = ImageDraw.Draw(out, "RGBA")
    # transitions
    tr = spec.get("trans", "cut")
    if tr == "black" and t < 0.6:
        out = Image.blend(Image.new("RGB", (OW, OH)), out, ease(t / 0.6))
    elif tr == "fade" and t < 0.5:
        out = Image.blend(Image.new("RGB", (OW, OH)), out, 0.3 + 0.7 * ease(t / 0.5))
    elif tr == "flash" and t < 0.35:
        out = Image.blend(Image.new("RGB", (OW, OH), (255, 255, 255)), out, ease(t / 0.35))
    # fade out before a black transition
    nxt = shot["idx"] + 1
    if nxt < len(shots) and shots[nxt]["spec"].get("trans") == "black" and dur - t < 0.45:
        out = Image.blend(Image.new("RGB", (OW, OH)), out, max(0, (dur - t) / 0.45))
    if shot["idx"] == len(shots) - 1 and dur - t < 1.5:
        out = Image.blend(Image.new("RGB", (OW, OH)), out, max(0, (dur - t) / 1.5))
    # subscribe reminder
    if spec.get("subscribe") and 0.8 < t < 7.5:
        tt = t - 0.8
        ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        slide = ease(min(1, tt / 0.4)) if tt < 6 else 1 - ease((tt - 6) / 0.5)
        draw_like_sub(od, ov, 960 + 200, 200 - (1 - slide) * 300, tt, 0.85)
        ov = ov.resize((OW, OH), Image.BILINEAR)
        o2 = out.convert("RGBA")
        o2.alpha_composite(ov)
        out = o2.convert("RGB")
    # subtitles
    for (a, b, txt) in CUES:
        if a <= gt < b:
            si = subtitle_img(txt)
            o2 = out.convert("RGBA")
            o2.alpha_composite(si, (0, OH - si.height - 26))
            out = o2.convert("RGB")
            break
    return out

def shot_at(gt):
    for s in shots:
        if s["t0"] <= gt < s["t1"]:
            return s
    return shots[-1]

def render_frame(fi):
    gt = fi / FPS
    shot = shot_at(gt)
    t = gt - shot["t0"]
    dur = shot["t1"] - shot["t0"]
    box = camera_box(shot, t, dur)
    scene, ib = render_scene(shot, t, gt, box)
    rel = (box[0] - ib[0], box[1] - ib[1], box[2] - ib[0], box[3] - ib[1])
    img = scene.resize((OW, OH), Image.BILINEAR, box=rel)
    return post(img, shot, t, dur, gt, fi)

if __name__ == "__main__":
    if sys.argv[1] == "--still":
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[2].split(","):
            fi = int(float(ts) * FPS)
            render_frame(fi).save(f"stills/s_{float(ts):07.2f}.jpg", quality=88)
        sys.exit()
    if sys.argv[1] == "--info":
        print("frames", NFRAMES, "total", TOTAL)
        for s in shots:
            print(s["idx"], round(s["t0"], 2), round(s["t1"], 2), s["spec"]["bg"])
        sys.exit()
    a, b, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    b = min(b, NFRAMES)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    import time
    t0 = time.time()
    for fi in range(a, b):
        p.stdin.write(render_frame(fi).tobytes())
        if (fi - a) % 240 == 0:
            print(f"[{a}-{b}] frame {fi} {(fi - a + 1) / (time.time() - t0 + 1e-6):.1f} fps", flush=True)
    p.stdin.close()
    p.wait()
