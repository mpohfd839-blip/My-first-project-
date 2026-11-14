"""Render the WWI documentary: cartoon beats + real photos, captions, labels, film look.

Usage:
  python3 ww1_render.py words.json img_dir out_dir --preview [--only 1,2,3]
  python3 ww1_render.py words.json img_dir out_dir --chunk i n
"""
import json
import math
import os
import subprocess
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "napoleonic_wars", "video"))

import ww1gfx as G  # noqa: E402
from ww1gfx import *  # noqa: E402,F401,F403
from ww1_scenes import BEATS, street_bg  # noqa: E402
import render as R  # noqa: E402  (captions + labels from the Napoleon renderer)

FPS = 24
NARR = os.path.join(HERE, "..", "narration.txt")


def load_timing(words_path):
    d = json.load(open(words_path))
    words = d["words"]
    text = "\n".join(d["lines"])
    starts, last = [], 0
    for b in BEATS:
        pos = text.find(b["cue"], last)
        if pos < 0:
            raise SystemExit(f"cue not found in order: {b['cue']!r}")
        last = pos + 1
        wi = len(text[:pos].split())
        starts.append(max(0.0, words[wi]["s"] - 0.12))
    starts[0] = 0.0
    for i in range(1, len(starts)):
        starts[i] = max(starts[i], starts[i - 1] + 1.0)
    return d["duration"], starts, words


# ------------------------------------------------------------------ film look
def make_grain(n=6):
    out = []
    rng = np.random.default_rng(5)
    for _ in range(n):
        g = rng.normal(128, 38, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)
        buf = np.zeros((H // 2, W // 2, 4), dtype=np.uint8)
        buf[..., 0] = buf[..., 1] = buf[..., 2] = g
        buf[..., 3] = 255
        s = cairo.ImageSurface.create_for_data(memoryview(buf).cast("B"), cairo.FORMAT_ARGB32, W // 2, H // 2,
                                               W // 2 * 4)
        out.append((s, buf))
    return out


GRAIN = None


def film_look(c, t, photo):
    global GRAIN
    if GRAIN is None:
        GRAIN = make_grain()
    s, _ = GRAIN[int(t * FPS) % len(GRAIN)]
    if not photo:
        c.save()
        c.set_operator(cairo.OPERATOR_SOFT_LIGHT)
        c.set_source_rgba(0.78, 0.62, 0.42, 0.35)
        c.paint()
        c.restore()
    c.save()
    c.scale(2, 2)
    c.set_operator(cairo.OPERATOR_OVERLAY)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_FAST)
    c.paint_with_alpha(0.22 if photo else 0.12)
    c.restore()
    # gentle exposure flicker
    f = 0.03 * math.sin(t * 23) * math.sin(t * 7.3)
    if f > 0:
        c.set_source_rgba(1, 0.95, 0.85, f)
        c.paint()
    if photo:
        G.specks(c, t, 1.0)
    vignette(c, 0.42 if photo else 0.32)


# ------------------------------------------------------------------ photo beats
def split_bg(c, kind, t):
    if kind == "hall":
        hall(c, t)
    elif kind == "street":
        street_bg(c, t)
    elif kind == "trench":
        G.trench(c, t)
    elif kind == "field":
        landscape(c, t, "day", "grass", 430, seed=11)
    elif kind == "desert":
        landscape(c, t, "desert", "sand", 430, trees=False, seed=3, sunpos=(1100, 120))
    elif kind == "sky":
        sky(c, "day")
        clouds(c, t, n=6, speed=40)
    else:
        hall(c, t)


def draw_img(c, b, u, lt, idx):
    n = b["n"]
    mode = b["mode"]
    if mode in ("full", "map"):
        zin = (idx % 2 == 0)
        z0, z1 = (1.03, 1.16) if mode == "full" else (1.0, 1.07)
        z = lerp(z0, z1, u) if zin else lerp(z1, z0, u)
        dx = 0.5 + (0.14 if n % 3 == 0 else -0.14 if n % 3 == 1 else 0) * (u - 0.5)
        dy = 0.5 + (0.08 if n % 2 else -0.08) * (u - 0.5)
        paint_img(c, n, 0, 0, W, H, zoom=z, fx=dx, fy=dy)
        G.photo_overlay(c, b["ov"], lt, u)
        if mode == "map" and b["legend"]:
            G.map_legend(c, b["legend"], u)
        return True
    if mode.startswith("frame"):
        bg = mode.split(":")[1]
        k = 1 + 0.08 * u
        c.save()
        c.translate(640, 360)
        c.scale(k, k)
        c.translate(-640, -360)
        (G.desk_bg if bg == "desk" else G.board_bg)(c, lt)
        G.photo_print(c, n, 640, 330, 780, 480, 0.035 if n % 2 else -0.035, u, lt)
        c.restore()
        return False
    if mode == "split":
        k = 1 + 0.05 * u
        c.save()
        c.translate(640, 360)
        c.scale(k, k)
        c.translate(-640, -360)
        split_bg(c, b["bg"], lt)
        tint(c, (0, 0, 0), 0.15)
        who = b["who"]
        if who in G.UNIFORMS:
            soldier(c, 290, 700, 1.9, who, lt, arms="point", expr="proud")
        else:
            G.char(c, who, 290, 700, 1.9, arms="point", t=lt)
        G.gold_frame(c, n, 600, 110, 560, 370, u, b["name"])
        c.restore()
        return False
    raise ValueError(mode)


# ------------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, words_path, img_dir):
        G.IMG_DIR = img_dir
        self.dur, self.starts, words = load_timing(words_path)
        self.ends = self.starts[1:] + [self.dur + 0.5]
        self.phr = R.phrases(words)
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.surf)

    def idx(self, t):
        lo, hi = 0, len(self.starts) - 1
        while lo < hi:
            m = (lo + hi + 1) // 2
            if self.starts[m] <= t:
                lo = m
            else:
                hi = m - 1
        return lo

    def draw_beat(self, i, t):
        c = self.c
        b = BEATS[i]
        s, e = self.starts[i], self.ends[i]
        lt = t - s
        u = clamp(lt / max(0.1, e - s))
        c.save()
        c.set_source_rgb(0, 0, 0)
        c.paint()
        if b["kind"] == "img":
            photo = draw_img(c, b, u, lt, i)
        else:
            z = b["zoom"]
            k = 1 + z * (u if i % 2 == 0 else 1 - u)
            fx, fy = b["focus"]
            c.translate(fx, fy)
            c.scale(k, k)
            c.translate(-fx, -fy)
            b["fn"](c, u, lt)
            photo = False
        c.restore()
        film_look(c, t, photo)

    def frame(self, t):
        c = self.c
        i = self.idx(t)
        lt = t - self.starts[i]
        kinds_differ = i > 0 and BEATS[i]["kind"] != BEATS[i - 1]["kind"]
        xf = 0.5 if kinds_differ else 0.35
        if i > 0 and lt < xf:
            self.draw_beat(i - 1, t)
            c.push_group()
            self.draw_beat(i, t)
            c.pop_group_to_source()
            c.paint_with_alpha(smooth(lt / xf))
            if kinds_differ:
                c.set_source_rgba(1, 0.93, 0.8, 0.45 * math.sin(math.pi * lt / xf))
                c.paint()
        else:
            self.draw_beat(i, t)
        R.draw_label(c, BEATS[i]["label"], lt)
        for ph in self._phr(t):
            R.draw_caption(c, ph, t)
        a = max(clamp(1 - t / 0.8), clamp((t - (self.dur - 2.0)) / 2.0))
        if a > 0:
            c.set_source_rgba(0, 0, 0, a)
            c.paint()
        self.surf.flush()

    def _phr(self, t):
        P = self.phr
        lo, hi = 0, len(P) - 1
        while lo < hi:
            m = (lo + hi + 1) // 2
            if P[m][0] <= t:
                lo = m
            else:
                hi = m - 1
        return [P[lo]] if P[lo][0] <= t < P[lo][1] else []


def main():
    words, img_dir, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    r = Renderer(words, img_dir)
    if "--timeline" in sys.argv:
        for i, b in enumerate(BEATS):
            print(f"{i + 1:3d} {r.starts[i]:7.1f} {r.ends[i] - r.starts[i]:5.1f} {b['kind']:4s} "
                  f"{b.get('n', '')!s:3s} {b['mood']:9s} {b['cue'][:50]}")
        return
    if "--preview" in sys.argv:
        only = None
        if "--only" in sys.argv:
            only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
        for i in range(len(BEATS)):
            if only and i + 1 not in only:
                continue
            r.frame((r.starts[i] + r.ends[i]) / 2)
            r.surf.write_to_png(os.path.join(out, f"b{i + 1:03d}.png"))
        return
    ci, cn = int(sys.argv[sys.argv.index("--chunk") + 1]), int(sys.argv[sys.argv.index("--chunk") + 2])
    n = int(math.ceil(r.dur * FPS))
    f0, f1 = n * ci // cn, n * (ci + 1) // cn
    path = os.path.join(out, f"chunk{ci:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        r.frame(f / FPS)
        p.stdin.write(r.surf.get_data())
        if (f - f0) % (FPS * 30) == 0:
            print(f"chunk {ci}: {(f - f0) / (f1 - f0) * 100:5.1f}%", flush=True)
    p.stdin.close()
    p.wait()
    print(f"chunk {ci} done", flush=True)


if __name__ == "__main__":
    main()
