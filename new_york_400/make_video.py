"""Render the 'What New York Looked Like 400 Years Ago' video.

Usage (needs a virtual X display for OpenGL):
  xvfb-run -a -s "-screen 0 1280x720x24" python3 make_video.py out_dir --preview 10,60,200
  xvfb-run -a -s "-screen 0 1280x720x24" python3 make_video.py out_dir --range 0 720
"""
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import timeline as TL
from render3d import H, W, Renderer
from world import World

FPS = 24


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    world = World()
    R = Renderer(world)
    print("setup", round(time.time() - t0, 1), "s", flush=True)

    def frame(t):
        S = TL.state_at(t)
        # first pass for VP (used for anchored labels): cheap to compute separately
        from render3d import look_at, perspective
        V = look_at(np.array(S["cam"], np.float32), np.array(S["target"], np.float32))
        dist = float(np.linalg.norm(np.array(S["cam"]) - np.array(S["target"])))
        VP = perspective(S["fov"], W / H, max(2.0, dist * 0.004), 60000) @ V
        ov = TL.overlay(t, S, VP)
        parts = TL.particles(world, t, S["year"], S)
        img, _ = R.render(S, ov, parts)
        return img

    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for t in ts:
            a = time.time()
            img = frame(t)
            im = Image.frombytes("RGB", (W, H), img).transpose(Image.FLIP_TOP_BOTTOM)
            im.save(os.path.join(out, f"p{t:06.1f}.png"))
            print(f"t={t} {time.time() - a:.2f}s", flush=True)
        return
    a, b = (float(x) for x in sys.argv[sys.argv.index("--range") + 1:sys.argv.index("--range") + 3])
    path = os.path.join(out, f"seg_{int(a):04d}_{int(b):04d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                          f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", "vflip", "-c:v", "libx264", "-preset",
                          "medium", "-crf", "19", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n0, n1 = int(round(a * FPS)), int(round(b * FPS))
    st = time.time()
    for f in range(n0, n1):
        p.stdin.write(frame(f / FPS))
        if (f - n0) % (FPS * 10) == 0:
            el = time.time() - st
            print(f"{f / FPS:6.1f}s  {(f - n0 + 1) / max(el, 1e-6):.2f} fps", flush=True)
    p.stdin.close()
    p.wait()
    print("done", path, flush=True)


if __name__ == "__main__":
    main()
