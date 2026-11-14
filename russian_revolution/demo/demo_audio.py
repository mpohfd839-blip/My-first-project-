"""Sound for the style demo: placeholder music bed + scene sound effects (no voice yet).

Usage: python3 demo_audio.py music.mp3 out.wav
"""
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "napoleonic_wars", "video"))
import soundtrack as st  # noqa: E402
import rr_demo as D  # noqa: E402

SR = st.SR


def main():
    music_path, out = sys.argv[1:3]
    N = int(D.DUR * SR)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", music_path, "-t", str(D.DUR + 1), "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2)[:N].astype(np.float64)
    mix = np.zeros((N, 2))
    mix[:len(m)] += m / (np.abs(m).max() + 1e-9) * 0.45

    def place(x, t0, g, pan=0.0):
        i = int(t0 * SR)
        x = x[: max(0, N - i)]
        mix[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
        mix[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))

    def amb(name, a, b, g):
        x = st.AMB[name](b - a + 0.5)
        x = st.fades(x / (np.abs(x).max() + 1e-9), 0.3, 0.5)
        place(x, a, g)

    sc = [s for s, _ in D.SCENES] + [D.DUR]
    seg = {fn.__name__: (sc[i], sc[i + 1]) for i, (_, fn) in enumerate(D.SCENES)}
    place(st.whoosh(1.2), 0.2, 0.25)
    amb("wind", *seg["s_house"], 0.25)
    amb("clock", *seg["s_bedroom"], 0.25)
    amb("march", *seg["s_stairs"], 0.18)
    amb("march", *seg["s_procession"], 0.18)
    amb("heart", *seg["s_wait"], 0.35)
    place(st.whoosh(1.0), seg["s_empire"][0] - 0.3, 0.25)
    amb("marchH", *seg["s_army"], 0.22)
    amb("murmur", *seg["s_people"], 0.3)
    place(st.bell(262), seg["s_throne"][0] + 0.2, 0.2)
    amb("heart", *seg["s_door"], 0.45)
    place(st.impact(), seg["s_title"][0], 0.45)
    # soft pop on every cut, like the reference
    for s in sc[1:-1]:
        n = int(0.06 * SR)
        tt = np.arange(n) / SR
        place(np.sin(2 * np.pi * 900 * tt) * np.exp(-tt * 70), s, 0.08)
    tm = np.arange(N) / SR
    mix *= np.clip(np.minimum(tm / 0.8, (D.DUR - tm) / 1.5), 0, 1)[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix /= np.abs(mix).max() / 0.9
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
