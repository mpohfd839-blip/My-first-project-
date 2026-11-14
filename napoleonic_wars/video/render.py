"""Render the Napoleonic Wars cartoon documentary.

Scene timing comes from the word alignment (words.json) and the cue lines in
../make_prompts.py; frames are drawn with pycairo and encoded with ffmpeg in
parallel chunks.

Usage:
  python3 render.py words.json out_dir --preview          # one frame per scene
  python3 render.py words.json out_dir --chunk i n        # render chunk i of n
"""
import json
import math
import os
import subprocess
import sys

import cairo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from make_prompts import S as CUES  # noqa: E402

from gfx import H, W, clamp, hexc, rrect, smooth  # noqa: E402
from scenes import SCENES  # noqa: E402

FPS = 24
XFADE = 0.3


def load_timing(path):
    d = json.load(open(path))
    words = d["words"]
    text = "\n".join(d["lines"])
    starts = []
    for cue, _ in CUES:
        pos = text.find(cue)
        assert pos >= 0, cue
        wi = len(text[:pos].split())
        starts.append(max(0.0, words[wi]["s"] - 0.15))
    starts[0] = 0.0
    for i in range(1, len(starts)):  # keep monotonic
        starts[i] = max(starts[i], starts[i - 1] + 0.8)
    return d["duration"], starts, words


def phrases(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        end = w["w"][-1] in ".,!?:;”\"" or len(cur) == 3
        nxt = words[i + 1] if i + 1 < len(words) else None
        if end or nxt is None or nxt["line"] != w["line"]:
            out.append(cur)
            cur = []
    res = []
    for i, ph in enumerate(out):
        s = ph[0]["s"]
        e = out[i + 1][0]["s"] if i + 1 < len(out) else ph[-1]["e"] + 1
        e = min(e, ph[-1]["e"] + 0.7)
        res.append((s, e, ph))
    return res


def text_outline(c, txt, x, y, size, fill_col, stroke=8):
    c.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    c.move_to(x, y)
    c.text_path(txt)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_width(stroke)
    c.set_source_rgba(0.08, 0.06, 0.05, 1)
    c.stroke_preserve()
    c.set_source_rgba(*fill_col)
    c.fill()


def draw_caption(c, ph, t):
    s, e, ws = ph
    a = clamp((t - s) / 0.08) * clamp((e - t) / 0.12)
    if a <= 0:
        return
    size = 54
    c.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    toks = [w["w"] for w in ws]
    widths = [c.text_extents(tk).x_advance for tk in toks]
    space = c.text_extents(" ").x_advance + 4
    total = sum(widths) + space * (len(toks) - 1)
    scale = min(1.0, (W - 120) / total)
    pop = 1 + 0.12 * (1 - smooth((t - s) / 0.15))
    c.save()
    c.translate(W / 2, 640)
    c.scale(scale * pop, scale * pop)
    x = -total / 2
    for w, tk, wd in zip(ws, toks, widths):
        active = w["s"] - 0.05 <= t < w["e"] + 0.05
        col = hexc("#FFD43B") if active else (1, 1, 1, 1)
        c.push_group()
        text_outline(c, tk, x, 18, size, col, 10)
        c.pop_group_to_source()
        c.paint_with_alpha(a)
        x += wd + space
    c.restore()


def draw_label(c, label, lt):
    if not label:
        return
    k = smooth(lt / 0.25)
    if k < 0.02:
        return
    pop = 1 + 0.25 * math.sin(math.pi * clamp(lt / 0.35)) if lt < 0.35 else 1
    c.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(30)
    e = c.text_extents(label)
    w, h = e.x_advance + 44, 56
    c.save()
    c.translate(W / 2, 62)
    c.scale(k * pop, k * pop)
    c.rotate(-0.015)
    rrect(c, -w / 2 + 5, -h / 2 + 6, w, h, 10)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.fill()
    rrect(c, -w / 2, -h / 2, w, h, 10)
    c.set_source_rgba(*hexc("#FFD43B"))
    c.fill_preserve()
    c.set_line_width(4)
    c.set_source_rgba(0.1, 0.08, 0.06, 1)
    c.stroke()
    c.move_to(-e.x_advance / 2, 11)
    c.set_source_rgba(0.1, 0.08, 0.06, 1)
    c.show_text(label)
    c.restore()


class Renderer:
    def __init__(self, words_path):
        self.dur, self.starts, words = load_timing(words_path)
        self.ends = self.starts[1:] + [self.dur + 0.5]
        self.phr = phrases(words)
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.surf)

    def scene_index(self, t):
        lo, hi = 0, len(self.starts) - 1
        while lo < hi:
            m = (lo + hi + 1) // 2
            if self.starts[m] <= t:
                lo = m
            else:
                hi = m - 1
        return lo

    def draw_scene(self, i, t):
        c = self.c
        sc = SCENES[i]
        s, e = self.starts[i], self.ends[i]
        lt = t - s
        u = clamp(lt / max(0.1, e - s))
        z = sc["zoom"]
        k = 1 + z * (u if i % 2 == 0 else 1 - u)
        fx, fy = sc["focus"]
        pan = (8 * math.sin(i * 1.7)) * u
        c.save()
        c.translate(fx + pan, fy)
        c.scale(k, k)
        c.translate(-fx, -fy)
        c.set_source_rgb(0, 0, 0)
        c.paint()
        sc["fn"](c, u, lt)
        c.restore()

    def frame(self, t):
        c = self.c
        i = self.scene_index(t)
        lt = t - self.starts[i]
        if i > 0 and lt < XFADE:
            self.draw_scene(i - 1, t)
            c.push_group()
            self.draw_scene(i, t)
            c.pop_group_to_source()
            c.paint_with_alpha(smooth(lt / XFADE))
        else:
            self.draw_scene(i, t)
        draw_label(c, SCENES[i]["label"], lt)
        # captions: binary search phrase
        for ph in self._phr_near(t):
            draw_caption(c, ph, t)
        # global fade in / out
        a = max(clamp(1 - t / 0.8), clamp((t - (self.dur - 1.5)) / 1.5))
        if a > 0:
            c.set_source_rgba(0, 0, 0, a)
            c.paint()
        self.surf.flush()

    def _phr_near(self, t):
        lo, hi = 0, len(self.phr) - 1
        while lo < hi:
            m = (lo + hi + 1) // 2
            if self.phr[m][0] <= t:
                lo = m
            else:
                hi = m - 1
        return [self.phr[lo]] if self.phr[lo][0] <= t < self.phr[lo][1] else []


def main():
    words, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    r = Renderer(words)
    if "--preview" in sys.argv:
        only = None
        if "--only" in sys.argv:
            only = [int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")]
        for i in range(len(SCENES)):
            if only and i + 1 not in only:
                continue
            t = (r.starts[i] + r.ends[i]) / 2
            r.frame(t)
            r.surf.write_to_png(os.path.join(out, f"s{i + 1:03d}.png"))
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
