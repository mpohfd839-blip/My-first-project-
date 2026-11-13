"""Empire video renderer. render.py a b out.mp4 | --still t1,t2 | --info"""
import json, math, random, sys, os, subprocess, time, functools
import numpy as np
from PIL import Image, ImageDraw
from core import W, H, PAL, background, draw_headline, hud, ease, ease_out, font, CINZEL9, CINZEL7, MONO
import arts as A
from arts import crown
from tesla_arts import TESLA_ARTS as ARTS, LAYOUT, bolt_burst
from story import SHOTS

FPS = 24
OW, OH = 1280, 720
TL = json.load(open("timeline.json"))
AUD = TL["duration"]
BEATS = [sp for sp, _ in SHOTS]
SEG = []
for i, (sp, lines) in enumerate(SHOTS):
    ss = TL["timeline"][i]["sentences"]
    if ss:
        t0 = 0.0 if i == 0 else max(0.0, ss[0]["start"] - 0.3)
    else:
        t0 = SEG[-1]["sents"][-1]["end"] + 1.0
    SEG.append(dict(i=i, start=t0, sents=ss))
TOTAL = AUD + 8.0
for i, s_ in enumerate(SEG):
    s_["end"] = SEG[i + 1]["start"] if i + 1 < len(SEG) else TOTAL
NF = int(TOTAL * FPS)
END0 = SEG[-1]["start"]


def beat_at(gt):
    for s in SEG:
        if gt < s["end"]:
            return s
    return SEG[-1]


@functools.lru_cache(maxsize=256)
def head_size(head, base, maxw):
    from core import parse_head
    from PIL import ImageDraw as _D
    lines = parse_head(head)
    size = base
    while size > 40:
        f = font(CINZEL9, size)
        img = Image.new("RGB", (10, 10)); d = _D.Draw(img)
        wmax = max(sum(d.textlength(w + " ", font=f) for w, _ in ln) for ln in lines)
        if wmax <= maxw:
            break
        size -= 4
    return size


def subscribe_overlay(img, tt):
    d = ImageDraw.Draw(img)
    k = ease(tt / 0.4) if tt < 5.5 else 1 - ease((tt - 5.5) / 0.5)
    y = 960 + (1 - k) * 200
    x = W - 640
    liked = tt > 1.2
    subd = tt > 2.2
    d.rounded_rectangle([x, y - 50, x + 220, y + 50], 50, fill=(50, 110, 220, 255) if liked else (235, 235, 235, 255))
    d.text((x + 110, y), "LIKE", font=font(CINZEL9, 38), fill=(255, 255, 255) if liked else (30, 30, 30), anchor="mm")
    d.rounded_rectangle([x + 240, y - 50, x + 580, y + 50], 50 if subd else 12, fill=(90, 90, 90, 255) if subd else (204, 0, 0, 255))
    d.text((x + 410, y), "SUBSCRIBED" if subd else "SUBSCRIBE", font=font(CINZEL9, 34), fill=(255, 255, 255), anchor="mm")
    if tt < 3:
        if tt < 1.2:
            kk = ease(tt / 1.2); px, py = x + 600 - 490 * kk, y + 120 - 110 * kk
        else:
            kk = ease((tt - 1.2) / 1.0); px, py = x + 110 + 300 * kk, y + 10
        d.polygon([(px, py), (px, py + 46), (px + 12, py + 36), (px + 22, py + 56), (px + 30, py + 52), (px + 20, py + 32), (px + 36, py + 32)], fill=(255, 255, 255), outline=(0, 0, 0))


def endcard(t):
    img = background("volt").convert("RGBA")
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    bolt_burst(d, W / 2, 260, t, 4, 220, outer=PAL["volt"]["acc"] + (200,))
    d.text((W / 2, 470), "THANKS FOR WATCHING", font=font(CINZEL9, 84), fill=PAL["volt"]["ink"] + (int(255 * ease((t - .3) / .6)),), anchor="mm")
    d.text((W / 2, 560), "WHICH GENIUS SHOULD WE COVER NEXT?", font=font(CINZEL7, 32), fill=PAL["volt"]["faint"] + (255,), anchor="mm")
    from core import glow_layer
    glow_layer(img, L, 18, 1.2)
    subscribe_overlay_center(img, max(0, t - 0.8))
    return img


def subscribe_overlay_center(img, tt):
    d = ImageDraw.Draw(img)
    x, y = W / 2 - 290, 760
    liked = tt > 1.2; subd = tt > 2.2
    d.rounded_rectangle([x, y - 55, x + 220, y + 55], 55, fill=(50, 110, 220, 255) if liked else (235, 235, 235, 255))
    d.text((x + 110, y), "LIKE", font=font(CINZEL9, 40), fill=(255, 255, 255) if liked else (30, 30, 30), anchor="mm")
    d.rounded_rectangle([x + 240, y - 55, x + 580, y + 55], 55 if subd else 12, fill=(90, 90, 90, 255) if subd else (204, 0, 0, 255))
    d.text((x + 410, y), "SUBSCRIBED" if subd else "SUBSCRIBE", font=font(CINZEL9, 36), fill=(255, 255, 255), anchor="mm")


@functools.lru_cache(maxsize=128)
def wrap_text(text, maxw, size):
    from core import GARAI
    f = font(GARAI, size)
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, cur = [], ""
    for w in text.split():
        tryl = (cur + " " + w).strip()
        if d.textlength(tryl, font=f) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = tryl
    lines.append(cur)
    return tuple(lines)


def story_line(img, b, gt, sents):
    from core import GARAI
    cur = None
    for se in sents:
        if se["start"] - 0.1 <= gt < se["end"] + 0.35:
            cur = se
    if not cur:
        return
    size = 40
    lines = wrap_text(cur["text"], 1500, size)
    k = ease((gt - cur["start"] + 0.1) / 0.25)
    p = PAL[b["pal"]]
    y0 = H - 150 - (len(lines) - 1) * 48
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pl).rectangle([0, y0 - 30, W, H - 92], fill=p["edge"] + (int(120 * k),))
    img.alpha_composite(pl)
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        d.text((W / 2, y0 + i * 48), ln, font=font(GARAI, size), fill=p["ink"] + (int(245 * k),), anchor="mm")


rs = np.random.RandomState(9)
GRAIN = [np.kron((rs.randn(OH // 2, OW // 2) * 5).astype(np.float32), np.ones((2, 2), np.float32))[..., None] for _ in range(6)]


def render_frame(fi):
    gt = fi / FPS
    s = beat_at(gt)
    b = BEATS[s["i"]]
    t = gt - s["start"]
    dur = s["end"] - s["start"]
    if b["art"] == "endcard":
        img = endcard(t)
        pal = "volt"
    else:
        pal = b["pal"]
        img = background(pal).convert("RGBA")
        ARTS[b["art"]](img, b, t, dur)
        mode, hx, hy, hs = LAYOUT.get(b["art"], ("left", 110, 340, 96))
        if mode != "none" and b["head"]:
            maxw = 820 if mode == "left" else 1500
            size = head_size(b["head"], hs, maxw)
            draw_headline(img, b["head"], pal, t, hx, hy, size, "center" if mode == "center" else "left", b.get("cap", ""))
        story_line(img, b, gt, s["sents"])
        hud(img, pal, b.get("chap", ""), b["year"], b.get("metric"), t, gt / TOTAL)
        if s["i"] == 9 and 0.8 < t < 7:
            subscribe_overlay(img, t - 0.8)
    z = 1.0 + 0.035 * min(1, max(0, t / max(1.0, dur)))
    sh = b.get("shake", 0)
    ox = math.sin(gt * 53) * 14 * sh if sh else 0
    oy = math.cos(gt * 47) * 10 * sh if sh else 0
    cw, ch = W / z, H / z
    x0 = min(max((W - cw) / 2 + ox, 0), W - cw); y0 = min(max((H - ch) / 2 + oy, 0), H - ch)
    out = img.convert("RGB").resize((OW, OH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    arr = np.asarray(out).astype(np.float32) + GRAIN[fi % 6]
    prev_pal = BEATS[s["i"] - 1]["pal"] if s["i"] > 0 else pal
    tl = 0.45 if prev_pal != pal else 0.22
    if t < tl and s["i"] > 0:
        k = 1 - ease(t / tl)
        m = 0.85 if prev_pal != pal else 0.45
        arr = arr * (1 - k * m) + np.array(PAL[pal]["edge"], np.float32) * k * m
    if gt < 1.0:
        arr *= ease(gt / 1.0)
    if TOTAL - gt < 2.0:
        arr *= max(0, (TOTAL - gt) / 2.0)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    if sys.argv[1] == "--still":
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[2].split(","):
            render_frame(int(float(ts) * FPS)).save(f"stills/s_{float(ts):07.2f}.jpg", quality=88)
        sys.exit()
    if sys.argv[1] == "--info":
        print("frames", NF, "total", TOTAL)
        sys.exit()
    a, b_, outp = int(sys.argv[1]), min(int(sys.argv[2]), NF), sys.argv[3]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(a, b_):
        p.stdin.write(render_frame(fi).tobytes())
        if (fi - a) % 240 == 0:
            print(f"[{a}-{b_}] frame {fi} {(fi - a + 1) / (time.time() - t0 + 1e-6):.1f} fps", flush=True)
    p.stdin.close(); p.wait()
