"""Renderer for the pictogram/spotlight style. Usage: render.py a b out.mp4 | --still t1,t2 | --info"""
import json, math, random, sys, os, subprocess, functools, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from story import SHOTS
import scenes as SC
from scenes import CW, CH, FY, font, FB, FXB, W3, RED
from picto import draw_person, draw_dog, make_pose

FPS = 24
OW, OH = 1280, 720
CONT_H = int(OW * CH / CW)        # 573
CONT_Y = 30
END_EXTRA = 7.0

TL = json.load(open("timeline.json"))
AUDIO_DUR = TL["duration"]
shots = []
for i, (spec, lines) in enumerate(SHOTS):
    shots.append(dict(spec=spec, sents=TL["timeline"][i]["sentences"], idx=i))
for i, s in enumerate(shots):
    if s["sents"]:
        s["t0"] = max(0.0, s["sents"][0]["start"] - 0.25)
    else:
        s["t0"] = (shots[i - 1]["sents"][-1]["end"] + 0.6) if shots[i - 1]["sents"] else shots[i - 1]["t0"] + 3.0
shots[0]["t0"] = 0.0
TOTAL = AUDIO_DUR + END_EXTRA
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL
NFRAMES = int(TOTAL * FPS)

# carry HUD state (time + rule) forward
cur_tm, cur_rule = "06:30 PM", 0
for s in shots:
    cur_tm = s["spec"].get("tm", cur_tm)
    if "rule" in s["spec"]:
        cur_rule = s["spec"]["rule"]
    s["tm"], s["rule"] = cur_tm, cur_rule

CUES = []
for s in shots:
    for se in s["sents"]:
        txt = se["text"].upper()
        a, b = se["start"], se["end"]
        parts = [txt]
        if len(txt) > 64:
            words, parts, cur = txt.split(" "), [], ""
            for w in words:
                if len(cur) + len(w) > 48 and cur:
                    parts.append(cur.strip()); cur = ""
                cur += w + " "
                if cur.rstrip().endswith((",", ";", ":")) and len(cur) > 26:
                    parts.append(cur.strip()); cur = ""
            if cur.strip():
                parts.append(cur.strip())
        L = sum(len(p) for p in parts)
        t = a
        for p in parts:
            d = (b - a) * len(p) / L
            CUES.append((t, t + d + (0.3 if p is parts[-1] else 0), p))
            t += d


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


SCENE_KEYS = ("dusk", "night", "morning", "lights_off", "car", "grandma", "wallphone", "wide", "extra", "door_open")


def scene_key(spec):
    a = {k: spec.get(k) for k in SCENE_KEYS if spec.get(k) is not None}
    if a.get("car") not in ("parked",):
        a.pop("car", None)
    return json.dumps(a, sort_keys=True)


def shadow_quick(img, layer, px, py, lx, fy, scale=1.55, alpha=0.75):
    """Project actor layer (placed at px,py) as an enlarged soft shadow from (lx,fy) onto img (RGBA)."""
    q = 4
    a = layer.getchannel("A")
    nw, nh = max(1, int(a.width * scale / q)), max(1, int(a.height * scale / q))
    a2 = a.resize((nw, nh), Image.BILINEAR)
    m = Image.new("L", (CW // q, CH // q), 0)
    sx = (lx + (px - lx) * scale) / q
    sy = (fy + (py - fy) * scale) / q
    m.paste(a2, (int(sx), int(sy)))
    m = m.filter(ImageFilter.GaussianBlur(2.5))
    ImageDraw.Draw(m).rectangle([0, fy // q, CW // q, CH // q], fill=0)
    m = m.resize((CW, CH), Image.BILINEAR).point(lambda v: int(v * alpha))
    dark = Image.new("RGBA", (CW, CH), (14, 12, 11, 255))
    img.paste(dark, (0, 0), m)


def render_actor(a, t, dur, seed, b, spec):
    c = a["c"]
    floor = b.get("floor", FY)
    amul = b.get("amul", 1.0)
    x = a["x"] * CW
    if "x1" in a:
        x = x + (a["x1"] * CW - x) * min(1.0, t / max(1.0, dur * 0.9))
    y = floor
    if spec["sc"] == "stairs":
        anim = a.get("anim")
        if anim == "climb":
            c0, c1 = spec.get("count", (a.get("step", 0), a.get("step", 0)))
            st = c0 + (c1 - c0) * min(1, t / max(1, dur * 0.95))
        elif anim == "descend":
            st = a["step"] + (a.get("step1", 0) - a["step"]) * min(1, t / max(1, dur * 0.9))
        else:
            st = a.get("step", 0)
        x, y = SC.stair_pos(max(0, st - 1) if st > 0 else 0)
        x += 40
        if st == 0:
            x, y = 200, FY
    u = a["s"] * CH / 105.0 * amul * 1.2
    if c == "dog":
        im, ox, oy = draw_dog(dict(anim=a.get("anim"), face=a.get("face", 1)), u * 1.3, t)
    else:
        p = make_pose(a, t, dur, seed)
        nm = "kidmom" if a.get("kidmom") else c
        im, ox, oy = draw_person(nm, p, u)
        if a.get("anim") == "lie_couch":
            im = im.rotate(-82, expand=True, resample=Image.BICUBIC)
            ox, oy = im.width / 2, im.height * 0.85
            y = floor - 120 * a["s"] / .3
    if a.get("anim") == "jump" and c == "dog":
        y -= 40 * abs(math.sin(t * 3))
    return im, x - ox, y - oy


def render_content(shot, t, gt):
    spec = shot["spec"]
    dur = shot["t1"] - shot["t0"]
    name = spec["sc"]
    if name in SC.TEXT_SCENES:
        img = Image.new("RGBA", (CW, CH), (8, 7, 7, 255))
        SC.paint_text_scene(name, img, spec, t, dur)
        b = {}
    else:
        base, b = SC.base_scene(name, scene_key(spec))
        img = base.copy()
        SC.paint_dynamic(name, img, spec, t, dur, b)
        for i, a in enumerate(spec["actors"]):
            im, px, py = render_actor(a, t, dur, i * 7 + shot["idx"], b, spec)
            if not b.get("noshadow"):
                shadow_quick(img, im, px, py, b["lx"], b.get("floor", FY))
            img.alpha_composite(im, (int(px), int(py)))
    return img


def camera(shot, t, dur):
    cam = shot["spec"].get("cam") or ("z", 1, 1, .5, .5)
    k = ease(t / max(0.001, dur))
    if cam[0] == "z":
        _, z0, z1, cx, cy = cam
        z = z0 + (z1 - z0) * k
    else:
        _, z, x0, y0, x1, y1 = cam
        cx, cy = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    w, h = CW / z, CH / z
    X = cx * CW + math.sin(t * .5 + shot["idx"]) * 5 / z
    Y = cy * CH + math.cos(t * .4 + shot["idx"]) * 3 / z
    sh = shot["spec"].get("shake", 0)
    if sh:
        X += math.sin(t * 53) * 18 * sh
        Y += math.cos(t * 47) * 12 * sh
    x0 = min(max(X - w / 2, 0), CW - w)
    y0 = min(max(Y - h / 2, 0), CH - h)
    return (x0, y0, x0 + w, y0 + h)


# ------------------------------------------------------------------ overlays
rs = np.random.RandomState(5)
GRAIN = [np.kron((rs.randn(OH // 2, OW // 2) * 6).astype(np.float32), np.ones((2, 2), np.float32))[..., None] for _ in range(6)]
YY, XX = np.mgrid[0:OH, 0:OW].astype(np.float32)
_r = np.sqrt(((XX - OW / 2) / (OW / 2)) ** 2 + ((YY - OH / 2) / (OH / 2)) ** 2)
VIG = np.clip(1.0 - 0.35 * np.clip(_r - 0.5, 0, None) ** 1.5 * 1.8, 0.3, 1)[..., None].astype(np.float32)
FADE = np.ones((OH, OW, 1), np.float32)
for y in range(CONT_Y + CONT_H - 70, OH):
    FADE[y] = max(0.0, 1 - (y - (CONT_Y + CONT_H - 70)) / 70)
FADE[: CONT_Y + CONT_H - 70] = 1


@functools.lru_cache(maxsize=64)
def sub_img(text):
    f = font(FB, 27)
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 50 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    im = Image.new("RGBA", (OW, 40 * len(lines) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((OW / 2, 20 + i * 38), ln, font=f, fill=(240, 238, 232, 255), anchor="mm")
    return im


def hud(d, shot, gt):
    d.text((40, 16), "FILE 112  //  FIRST NIGHT ALONE", font=font(FB, 14), fill=(120, 118, 114), anchor="lm")
    SC.hud_boxes(d, OW / 2, 16, shot["rule"], size=16, gap=5, done_upto=shot["rule"])
    d.text((OW - 40, 16), shot["tm"], font=font(FB, 14), fill=(120, 118, 114), anchor="rm")


def draw_like_sub(d, scene, cx, cy, t, s=1.0):
    clicked_like = t > 1.1
    clicked_sub = t > 2.0
    bell = t > 2.7
    d.rounded_rectangle([cx - 700 * s, cy - 60 * s, cx - 400 * s, cy + 60 * s], 60 * s, fill=(240, 240, 240) if not clicked_like else (50, 120, 230))
    tc = (30, 30, 30) if not clicked_like else (255, 255, 255)
    tx, ty = cx - 640 * s, cy
    d.rounded_rectangle([tx - 25 * s, ty - 10 * s, tx + 30 * s, ty + 38 * s], 10 * s, fill=tc)
    d.polygon([(tx - 10 * s, ty - 10 * s), (tx + 5 * s, ty - 45 * s), (tx + 20 * s, ty - 40 * s), (tx + 15 * s, ty - 10 * s)], fill=tc)
    d.rectangle([tx - 45 * s, ty - 8 * s, tx - 30 * s, ty + 38 * s], fill=tc)
    d.text((cx - 520 * s, cy), "LIKE", font=font(FXB, 50 * s), fill=tc, anchor="mm")
    sx0 = cx - 330 * s
    d.rounded_rectangle([sx0, cy - 60 * s, sx0 + 460 * s, cy + 60 * s], 60 * s if clicked_sub else 14 * s, fill=(204, 0, 0) if not clicked_sub else (90, 90, 90))
    d.text((sx0 + 230 * s, cy), "SUBSCRIBED" if clicked_sub else "SUBSCRIBE", font=font(FXB, 46 * s), fill=(255, 255, 255), anchor="mm")
    bx, by = cx + 230 * s, cy
    bel = Image.new("RGBA", (int(160 * s), int(160 * s)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bel)
    c0 = 80 * s
    col = (255, 255, 255) if bell else (200, 200, 200)
    bd.pieslice([c0 - 45 * s, c0 - 55 * s, c0 + 45 * s, c0 + 35 * s], 180, 360, fill=col)
    bd.rectangle([c0 - 45 * s, c0 - 12 * s, c0 + 45 * s, c0 + 25 * s], fill=col)
    bd.polygon([(c0 - 58 * s, c0 + 35 * s), (c0 + 58 * s, c0 + 35 * s), (c0 + 45 * s, c0 + 15 * s), (c0 - 45 * s, c0 + 15 * s)], fill=col)
    bd.ellipse([c0 - 12 * s, c0 + 35 * s, c0 + 12 * s, c0 + 55 * s], fill=col)
    bel = bel.rotate(math.sin(t * 25) * 18 if bell and t < 3.6 else 0, resample=Image.BICUBIC)
    scene.alpha_composite(bel, (int(bx - 80 * s), int(by - 80 * s)))
    if t < 3.2:
        if t < 1.1:
            k = ease(t / 1.1); px, py = cx + 200 * s + (-840 * s) * k, cy + 260 * s - 240 * s * k
        elif t < 2.0:
            k = ease((t - 1.1) / 0.9); px, py = cx - 640 * s + 540 * s * k, cy + 20 * s
        else:
            k = ease((t - 2.0) / 0.7); px, py = cx - 100 * s + 330 * s * k, cy + 20 * s
        pts = [(0, 0), (0, 70), (18, 54), (32, 84), (44, 78), (30, 50), (52, 50)]
        d.polygon([(px + x * s, py + y * s) for x, y in pts], fill=(255, 255, 255), outline=(0, 0, 0))


def endcard(frame, t):
    d = ImageDraw.Draw(frame)
    k = min(1, t / 0.8)
    d.text((OW / 2, 200), "GOODNIGHT, HOUSE.", font=font(FXB, 64), fill=(240, 238, 232, int(255 * k)), anchor="mm")
    d.rectangle([OW / 2 - 260 * k, 250, OW / 2 + 260 * k, 254], fill=RED)
    d.text((OW / 2, 300), "THANKS FOR WATCHING", font=font(FB, 26), fill=(150, 148, 144), anchor="mm")
    ov = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw_like_sub(ImageDraw.Draw(ov), ov, 1060, 700, max(0, t - 0.6), 1.0)
    ov = ov.resize((OW, OH), Image.BILINEAR)
    frame.alpha_composite(ov)
    d = ImageDraw.Draw(frame)
    d.text((OW / 2, 610), "Would you follow the rules? Tell us in the comments.", font=font(FB, 22), fill=(130, 128, 124), anchor="mm")


def post(frame, shot, t, dur, gt, fi):
    fx = shot["spec"].get("fx", [])
    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
    if "sepia" in fx:
        l = arr @ np.array([.3, .59, .11], np.float32)
        arr = np.stack([l * 1.08 + 10, l * .95 + 4, l * .72], -1)
    if "desat" in fx:
        l = (arr @ np.array([.3, .59, .11], np.float32))[..., None]
        arr = arr * .4 + l * .6
    if "warm" in fx:
        arr *= np.array([1.06, 1.0, .88], np.float32)
    if "dawn" in fx:
        arr = arr * np.array([1.08, .98, .95], np.float32) + np.array([10, 2, 4], np.float32)
    if "night_blue" in fx:
        arr *= np.array([.8, .88, 1.05], np.float32)
    if "memory" in fx:
        arr = arr * .85 + 25
    if "flicker" in fx:
        arr *= 0.85 + 0.15 * random.Random(fi).random()
    if "red" in fx:
        p = 0.5 + 0.5 * math.sin(gt * 3)
        arr *= np.array([1 + .12 * p, 1 - .1 * p, 1 - .1 * p], np.float32)
    arr = arr * VIG + GRAIN[fi % 6]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    # glitch on scary/intro shots
    glitch = ("glitch_in" in fx and t < 0.8) or ("red" in fx and t < 0.35) or (shot["spec"]["sc"] == "rulecard" and t < 0.25)
    if glitch:
        a = np.asarray(out).copy()
        r = random.Random(fi)
        s = r.randint(5, 18)
        a[..., 0] = np.roll(a[..., 0], s, 1)
        a[..., 2] = np.roll(a[..., 2], -s, 1)
        for k in range(4):
            y0 = r.randint(0, OH - 30); h = r.randint(4, 30)
            a[y0:y0 + h] = np.roll(a[y0:y0 + h], r.randint(-50, 50), 1)
        out = Image.fromarray(a)
    # occasional VHS line
    if random.Random(fi // 3).random() < 0.04:
        a = np.asarray(out).copy()
        y0 = random.Random(fi).randint(0, OH - 6)
        a[y0:y0 + 3] = np.clip(a[y0:y0 + 3].astype(int) + 40, 0, 255)
        out = Image.fromarray(a)
    return out


def render_frame(fi):
    gt = fi / FPS
    shot = next((s for s in shots if s["t0"] <= gt < s["t1"]), shots[-1])
    t = gt - shot["t0"]
    dur = shot["t1"] - shot["t0"]
    frame = Image.new("RGBA", (OW, OH), (6, 5, 5, 255))
    name = shot["spec"]["sc"]
    if name == "endcard":
        endcard(frame, t)
    else:
        content = render_content(shot, t, gt)
        box = camera(shot, t, dur)
        cimg = content.convert("RGB").resize((OW, CONT_H), Image.BILINEAR, box=box)
        frame.paste(cimg, (0, CONT_Y))
        arr = np.asarray(frame.convert("RGB")).astype(np.float32) * FADE
        frame = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(frame)
    if name not in ("title", "endcard"):
        hud(d, shot, gt)
    if shot["spec"].get("subscribe") and 0.8 < t < 7.5:
        tt = t - 0.8
        ov = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        slide = ease(min(1, tt / 0.4)) if tt < 6 else 1 - ease((tt - 6) / 0.5)
        draw_like_sub(ImageDraw.Draw(ov), ov, 1160, 230 - (1 - slide) * 300, tt, 0.8)
        frame.alpha_composite(ov.resize((OW, OH), Image.BILINEAR))
    out = post(frame, shot, t, dur, gt, fi).convert("RGBA")
    for (a, b, txt) in CUES:
        if a <= gt < b:
            si = sub_img(txt)
            out.alpha_composite(si, (0, OH - 70 - si.height // 2 - 20))
            break
    # fades
    o = out.convert("RGB")
    if gt < 0.8:
        o = Image.blend(Image.new("RGB", (OW, OH)), o, ease(gt / 0.8))
    if TOTAL - gt < 1.5:
        o = Image.blend(Image.new("RGB", (OW, OH)), o, max(0, (TOTAL - gt) / 1.5))
    if shot["spec"]["sc"] in ("rulecard", "title") and t < 0.12:
        o = Image.blend(Image.new("RGB", (OW, OH), (255, 255, 255)), o, 0.6 + t / 0.3)
    return o


if __name__ == "__main__":
    if sys.argv[1] == "--still":
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[2].split(","):
            render_frame(int(float(ts) * FPS)).save(f"stills/s_{float(ts):07.2f}.jpg", quality=88)
        sys.exit()
    if sys.argv[1] == "--info":
        print("frames", NFRAMES, "total", TOTAL)
        for s in shots:
            print(s["idx"], round(s["t0"], 2), round(s["t1"], 2), s["spec"]["sc"])
        sys.exit()
    a, b, outp = int(sys.argv[1]), min(int(sys.argv[2]), NFRAMES), sys.argv[3]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(a, b):
        p.stdin.write(render_frame(fi).tobytes())
        if (fi - a) % 240 == 0:
            print(f"[{a}-{b}] frame {fi} {(fi - a + 1) / (time.time() - t0 + 1e-6):.1f} fps", flush=True)
    p.stdin.close(); p.wait()
