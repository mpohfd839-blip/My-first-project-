"""Empire video renderer. render.py a b out.mp4 | --still t1,t2 | --info"""
import json, math, random, sys, os, subprocess, time, functools
import numpy as np
from PIL import Image, ImageDraw
from core import W, H, PAL, background, draw_headline, hud, ease, ease_out, font, CINZEL9, CINZEL7, MONO
from arts import ARTS, LAYOUT, crown
from script import BEATS

FPS = 24
OW, OH = 1280, 720
TL = json.load(open("timeline.json"))
TOTAL = TL["total"]
NF = int(TOTAL * FPS)
SEG = TL["beats"]
END0, END1 = TL["endcard"]


def beat_at(gt):
    for s in SEG:
        if gt < s["end"]:
            return s
    return None


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
    img = background("gold").convert("RGBA")
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    crown(d, W / 2, 250, 0.8, PAL["gold"]["acc"] + (255,), ease(t / 1.2))
    d.text((W / 2, 470), "THANKS FOR WATCHING", font=font(CINZEL9, 84), fill=PAL["gold"]["ink"] + (int(255 * ease((t - .3) / .6)),), anchor="mm")
    d.text((W / 2, 560), "WHICH EMPIRE SHOULD WE COVER NEXT?", font=font(CINZEL7, 32), fill=PAL["gold"]["faint"] + (255,), anchor="mm")
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


rs = np.random.RandomState(9)
GRAIN = [np.kron((rs.randn(OH // 2, OW // 2) * 5).astype(np.float32), np.ones((2, 2), np.float32))[..., None] for _ in range(6)]


def render_frame(fi):
    gt = fi / FPS
    s = beat_at(gt)
    if s is None:
        img = endcard(gt - END0)
        pal = "gold"
        b = None
    else:
        b = BEATS[s["i"]]
        t = gt - s["start"]
        dur = s["end"] - s["start"]
        pal = b["pal"]
        img = background(pal).convert("RGBA")
        ARTS[b["art"]](img, b, t, dur)
        mode, hx, hy, hs = LAYOUT.get(b["art"], ("left", 110, 360, 92))
        if mode != "none":
            maxw = 820 if mode == "left" else (1500 if mode == "center" else 1100)
            size = head_size(b["head"], hs, maxw)
            if mode == "top":
                # dark plate for legibility
                pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(pl).rectangle([0, 0, W, 330], fill=PAL[pal]["bg"] + (150,))
                img.alpha_composite(pl)
            draw_headline(img, b["head"], pal, t, hx, hy, size, "center" if mode == "center" else "left", b.get("cap", ""))
        elif b.get("cap"):
            pass
        hud(img, pal, b.get("chap", ""), b["year"], b.get("metric"), t, gt / TOTAL)
        if s["i"] == 8 and 0.8 < t < 7:
            subscribe_overlay(img, t - 0.8)
    # camera push
    z = 1.0 + 0.03 * min(1, max(0, (gt - (s["start"] if s else END0)) / max(1, (s["end"] - s["start"]) if s else 8)))
    cw, ch = W / z, H / z
    box = ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)
    out = img.convert("RGB").resize((OW, OH), Image.BILINEAR, box=box)
    arr = np.asarray(out).astype(np.float32) + GRAIN[fi % 6]
    # transition: fade through bg colour at beat start
    if s:
        t = gt - s["start"]
        prev_pal = BEATS[s["i"] - 1]["pal"] if s["i"] > 0 else pal
        tl = 0.45 if prev_pal != pal else 0.25
        if t < tl:
            k = 1 - ease(t / tl)
            arr = arr * (1 - k * (0.85 if prev_pal != pal else 0.5)) + np.array(PAL[pal]["edge"], np.float32) * k * (0.85 if prev_pal != pal else 0.5)
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
