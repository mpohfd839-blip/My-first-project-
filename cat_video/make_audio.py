"""Background soundtrack for the cat behaviour video.

No voice / narration: only a soft ambient bed (pad chords + gentle kalimba
plucks + room tone) with a few diegetic background sounds (birds outside the
window, purring). Pure numpy, writes a 16-bit stereo WAV.

Usage: python3 make_audio.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 300.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(sig, start, gain=1.0, pan=0.0):
    i0 = int(start * SR)
    if i0 >= N:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[: N - i0]
    lg = gain * np.sqrt(0.5 * (1 - pan))
    rg = gain * np.sqrt(0.5 * (1 + pan))
    L[i0:i0 + len(sig)] += sig * lg
    R[i0:i0 + len(sig)] += sig * rg


def lowpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


# ---- 1. Pad chords -------------------------------------------------------
chords = [
    [48, 52, 55, 59],  # Cmaj7
    [45, 48, 52, 55],  # Am7
    [41, 45, 48, 52],  # Fmaj7
    [43, 47, 50, 52],  # G6
]
SEG = 10.0
seg_len = int((SEG + 2.5) * SR)
tt = np.arange(seg_len) / SR
fade = 2.5
env = np.ones(seg_len)
env[tt < fade] = np.sin(0.5 * np.pi * tt[tt < fade] / fade) ** 2
tail = tt > (SEG + 2.5 - fade)
env[tail] = np.sin(0.5 * np.pi * (SEG + 2.5 - tt[tail]) / fade) ** 2
for k in range(int(DUR / SEG) + 1):
    ch = chords[k % 4]
    for m in ch:
        f = note_hz(m)
        for det, pan in ((-0.6, -0.5), (0.6, 0.5)):
            ph = rng.uniform(0, 2 * np.pi)
            wob = 1 + 0.002 * np.sin(2 * np.pi * 0.2 * tt + ph)
            s = np.sin(2 * np.pi * (f + det) * tt * wob + ph)
            s += 0.18 * np.sin(2 * np.pi * 2 * (f + det) * tt + ph)
            add(s * env, k * SEG - 1.25, gain=0.035, pan=pan)

# ---- 2. Kalimba-like plucks ---------------------------------------------
penta = [60, 62, 64, 67, 69, 72, 74, 76, 79]


def pluck(midi, length=2.2):
    t = np.arange(int(length * SR)) / SR
    f = note_hz(midi)
    e = np.exp(-t * 3.2) * np.minimum(1, t / 0.006)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    s += 0.08 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 10)
    return s * e


def pluck_rate(t):
    if 240 <= t < 270:      # zoomies: busier
        return 0.35, 0.7
    if 90 <= t < 150:       # play / hunting: lively
        return 0.8, 1.6
    if t >= 270 or t < 20:  # waking / sleeping: sparse
        return 2.2, 4.0
    return 1.3, 2.6


t = 2.0
while t < DUR - 4:
    m = int(rng.choice(penta))
    add(pluck(m), t, gain=0.07, pan=float(rng.uniform(-0.6, 0.6)))
    if rng.random() < 0.25:  # occasional soft octave echo
        add(pluck(m + 12, 1.2), t + 0.18, gain=0.025, pan=float(rng.uniform(-0.6, 0.6)))
    lo, hi = pluck_rate(t)
    t += rng.uniform(lo, hi)

# ---- 3. Room tone --------------------------------------------------------
room = lowpass(rng.standard_normal(N), 350)
room /= np.abs(room).max()
L += room * 0.02
R += np.roll(room, 997) * 0.02


# ---- 4. Birds outside ----------------------------------------------------
def chirp():
    d = rng.uniform(0.05, 0.12)
    t = np.arange(int(d * SR)) / SR
    f0 = rng.uniform(2800, 4200)
    sweep = rng.uniform(-1500, 1500)
    f = f0 + sweep * t / d + 300 * np.sin(2 * np.pi * rng.uniform(20, 45) * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.sin(np.pi * t / d) ** 2
    return np.sin(ph) * e


def birds(t0, t1, density, gain):
    t = t0
    while t < t1:
        pan = float(rng.uniform(-0.9, -0.2))  # window is on the left
        for _ in range(int(rng.integers(2, 6))):
            add(chirp(), t, gain=gain, pan=pan)
            t += rng.uniform(0.08, 0.2)
        t += rng.exponential(density)


birds(1, 30, 3.0, 0.035)
birds(210, 240, 1.2, 0.06)
birds(60, 90, 6.0, 0.02)


# ---- 5. Purring ----------------------------------------------------------
def purr(t0, t1, gain):
    n = int((t1 - t0) * SR)
    t = np.arange(n) / SR
    base = lowpass(rng.standard_normal(n), 180)
    base /= np.abs(base).max()
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 26 * t)  # 26 Hz flutter
    breath = 0.6 + 0.4 * np.sin(2 * np.pi * t / 2.4) ** 2
    e = np.minimum(1, np.minimum(t / 2, (t1 - t0 - t) / 2))
    add(base * am * breath * e, t0, gain=gain)


purr(151, 179.5, 0.22)
purr(180.5, 209.5, 0.28)
purr(284, 299, 0.14)

# ---- master --------------------------------------------------------------
mix = np.stack([L, R], axis=1)
tm = np.arange(N) / SR
master = np.minimum(1, np.minimum(tm / 3, (DUR - tm) / 5))
mix *= master[:, None]
mix *= 0.8 / np.abs(mix).max()

out = sys.argv[1] if len(sys.argv) > 1 else "background.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out)
