"""Quiet, dark orchestral-style pad bed to sit under the narration.

Usage: python3 music.py SECONDS out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = float(sys.argv[1])
N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, g, pan=0.0):
    i = int(t0 * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * g * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * g * np.sqrt(0.5 * (1 + pan))


# D minor progression: Dm - Bb - F - C (strings-like pads)
chords = [[38, 50, 53, 57], [34, 46, 50, 53], [41, 48, 53, 57], [36, 48, 52, 55]]
SEG = 8.0
ln = int((SEG + 3) * SR)
t = np.arange(ln) / SR
env = np.minimum(1, np.minimum(t / 2.5, (SEG + 3 - t) / 2.5)) ** 2
for k in range(int(DUR / SEG) + 1):
    for m in chords[k % 4]:
        for det, pan in ((-0.8, -0.6), (0.8, 0.6)):
            f = hz(m) + det
            ph = rng.uniform(0, 6.28)
            vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * t + ph)
            s = sum(np.sin(2 * np.pi * f * h * t * vib + ph) / h ** 1.3 for h in (1, 2, 3, 4))
            add(s * env, k * SEG - 1.5, 0.03, pan)

# soft timpani-like pulse on each chord change
for k in range(int(DUR / SEG) + 1):
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    f = 55 * (1 + 0.2 * np.exp(-tt * 30))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.5)
    add(s, k * SEG, 0.12)

mix = np.stack([L, R], 1)
tm = np.arange(N) / SR
mix *= np.minimum(1, np.minimum(tm / 4, (DUR - tm) / 6))[:, None]
mix *= 0.7 / np.abs(mix).max()
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[2])
