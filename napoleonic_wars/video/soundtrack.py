"""Cinematic soundtrack: narration + mood-driven score + scene sound effects.

Everything is synthesised with numpy (no samples). Scene timing comes from
render.load_timing so effects land on the same cuts as the pictures.

Usage: python3 soundtrack.py words.json narration.mp3 out.wav
"""
import json
import subprocess
import sys
import wave

import numpy as np

from render import load_timing

SR = 44100
rng = np.random.default_rng(11)


# ====================================================================== dsp
def filt(x, lo=None, hi=None, order=2):
    """Zero-phase band filter via FFT (Butterworth-like magnitude)."""
    n = len(x)
    if n < 8:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, n)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def env_exp(n, decay, attack=0.002):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * decay)


def norm(x, peak=1.0):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def reverb(x, length=1.4, mix=0.35, damp=3.0):
    n = int(length * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * damp)
    ir = filt(ir, hi=4000)
    ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)
    out = np.zeros(m)
    out[:len(x)] += x * (1 - mix)
    return out + y * mix * 3


def fades(x, fin=0.3, fout=0.4):
    n = len(x)
    t = np.arange(n) / SR
    return x * np.minimum(1, np.minimum(t / fin, (n / SR - t) / fout)).clip(0, 1)


# ====================================================================== sfx: one-shots
def cannon(dist=0.0):
    n = int(2.6 * SR)
    t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = filt(noise(2.6), hi=2500) * env_exp(n, 7, 0.001)
    tail = filt(noise(2.6), hi=300) * env_exp(n, 1.6, 0.02)
    x = body * 1.0 + crack * 0.6 + tail * 0.9
    if dist:
        x = filt(x, hi=900 - 600 * dist)
    return reverb(norm(x), 2.0, 0.4)


def explosion():
    x = cannon() * 1.0
    deb = filt(noise(3.5), lo=800, hi=6000) * env_exp(int(3.5 * SR), 1.5, 0.05) * 0.25
    deb = np.pad(deb, (int(0.15 * SR), 0))
    m = max(len(x), len(deb))
    return norm(np.pad(x, (0, m - len(x))) + np.pad(deb, (0, m - len(deb))))


def musket_volley(n_shots=18, spread=0.7):
    out = np.zeros(int((spread + 1.2) * SR))
    for _ in range(n_shots):
        i = int(rng.uniform(0, spread) * SR)
        m = int(0.18 * SR)
        s = filt(noise(0.18), lo=600, hi=5000) * env_exp(m, 40, 0.0005)
        s += filt(noise(0.18), hi=250) * env_exp(m, 18) * 0.8
        out[i:i + m] += s * rng.uniform(0.5, 1)
    return reverb(norm(out), 1.2, 0.3)


def thunder():
    n = int(5 * SR)
    t = np.arange(n) / SR
    x = filt(noise(5), hi=180) * (np.exp(-t * 0.9) * (0.6 + 0.4 * np.sin(t * 7 + 1) ** 2))
    x += filt(noise(5), lo=500, hi=3000) * env_exp(n, 9, 0.003) * 0.4
    return norm(x)


def impact():
    n = int(3.5 * SR)
    t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    x += filt(noise(3.5), hi=400) * env_exp(n, 4, 0.002) * 0.7
    x += filt(noise(3.5), lo=2000, hi=8000) * env_exp(n, 14, 0.001) * 0.25
    return reverb(norm(x), 2.5, 0.45, 2)


def whoosh(sec=1.1, rev=False):
    n = int(sec * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / sec) ** 3
    lo_part = filt(noise(sec), lo=300, hi=1500)
    hi_part = filt(noise(sec), lo=1500, hi=6000)
    mixw = t / sec
    x = (lo_part * (1 - mixw) + hi_part * mixw) * e
    if rev:
        x = x[::-1]
    return norm(x)


def bell(f0=330, sec=6.0):
    n = int(sec * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for ratio, amp, dec in ((0.5, 0.6, 0.6), (1, 1, 1.0), (1.19, 0.5, 1.4), (1.5, 0.45, 1.6), (2, 0.4, 2),
                            (2.52, 0.25, 2.6), (3, 0.2, 3.2)):
        x += amp * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t * dec)
    x *= np.minimum(1, t / 0.003)
    return reverb(norm(x), 2.5, 0.35, 1.5)


def heartbeat():
    out = np.zeros(int(0.9 * SR))
    for off, g in ((0, 1), (0.22, 0.7)):
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * (45 + 25 * np.exp(-t * 30)) * t) * np.exp(-t * 18)
        i = int(off * SR)
        out[i:i + n] += s * g
    return norm(out)


def tick(high=True):
    n = int(0.05 * SR)
    return filt(noise(0.05), lo=2500 if high else 1800, hi=7000) * env_exp(n, 120, 0.0003)


def neigh():
    n = int(1.3 * SR)
    t = np.arange(n) / SR
    f = 600 + 300 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 1.2) - 250 * t
    x = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in (1, 2, 3, 4))
    x *= np.sin(np.pi * t / 1.3) ** 0.6 * (0.7 + 0.3 * np.sin(2 * np.pi * 22 * t))
    return reverb(norm(filt(x, lo=300, hi=3500)), 1.0, 0.25)


def gull():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = 1500 - 700 * t / 0.55
    x = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h ** 1.5 for h in (1, 2, 3))
    return norm(x * np.sin(np.pi * t / 0.55) ** 2)


def chirp():
    d = rng.uniform(0.05, 0.12)
    t = np.arange(int(d * SR)) / SR
    f = rng.uniform(2800, 4200) + rng.uniform(-1500, 1500) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2


def crack():
    out = np.zeros(int(1.5 * SR))
    for _ in range(9):
        i = int(rng.uniform(0, 0.9) * SR)
        n = int(0.08 * SR)
        out[i:i + n] += filt(noise(0.08), lo=200, hi=3000) * env_exp(n, 50) * rng.uniform(0.4, 1)
    return reverb(norm(out), 1.0, 0.3)


# ====================================================================== sfx: ambiences (length = sec)
def amb_rain(sec, heavy=False):
    x = filt(noise(sec), lo=1200, hi=9000) * (0.5 if heavy else 0.32)
    n = len(x)
    for _ in range(int(sec * (60 if heavy else 30))):
        i = rng.integers(0, max(1, n - 800))
        x[i:i + 800] += filt(noise(800 / SR), lo=2000) * env_exp(800, 200) * rng.uniform(0.2, 0.6)
    x += filt(noise(sec), hi=400) * 0.15
    return x


def amb_wind(sec, strong=False):
    n = int(sec * SR)
    t = np.arange(n) / SR
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * t / rng.uniform(3, 6) + rng.uniform(0, 6)) ** 2
    x = filt(noise(sec), lo=80, hi=700 if not strong else 1600) * lfo
    if strong:
        x += filt(noise(sec), lo=1500, hi=4000) * lfo ** 3 * 0.35
    return x * (1.3 if strong else 0.9)


def amb_sea(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    sw = 0.25 + 0.75 * np.sin(np.pi * t / 5.5 + rng.uniform(0, 3)) ** 4
    return filt(noise(sec), lo=60, hi=900) * sw * 1.1 + filt(noise(sec), lo=2000, hi=6000) * sw ** 3 * 0.25


def amb_river(sec):
    return filt(noise(sec), lo=300, hi=2500) * 0.45 * (1 + 0.2 * np.sin(np.arange(int(sec * SR)) / SR * 13))


def amb_fire(sec, big=False):
    x = filt(noise(sec), hi=500) * (0.6 if big else 0.25)
    n = len(x)
    for _ in range(int(sec * (40 if big else 14))):
        i = rng.integers(0, max(1, n - 600))
        x[i:i + 600] += filt(noise(600 / SR), lo=1500, hi=8000) * env_exp(600, 250) * rng.uniform(0.3, 1)
    if big:
        x += filt(noise(sec), lo=60, hi=200) * 0.6
    return x


def amb_crowd(sec, mood="cheer"):
    n = int(sec * SR)
    t = np.arange(n) / SR
    lo, hi = {"cheer": (400, 3000), "angry": (200, 1500), "murmur": (250, 1800), "panic": (600, 3500)}[mood]
    x = np.zeros(n)
    for _ in range(6):
        rate = rng.uniform(2, 7)
        am = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6)) ** 2
        x += filt(noise(sec), lo=lo, hi=hi) * am
    swell = {"cheer": 0.7 + 0.3 * np.sin(np.pi * np.minimum(1, t / max(sec, 1))) , "angry": 1.0,
             "murmur": 0.35, "panic": 0.9}[mood]
    return x * swell * 0.35


def amb_march(sec, heavy=False):
    n = int(sec * SR)
    out = np.zeros(n)
    beat = 0.5
    k = 0
    while k * beat < sec:
        i = int(k * beat * SR)
        m = int(0.12 * SR)
        step = filt(noise(0.12), hi=260) * env_exp(m, 25)
        out[i:i + m] += step[: n - i] * (1.0 if heavy else 0.7)
        # snare rudiment: roll on beat 4 of each bar, taps otherwise
        if k % 4 in (1, 3) or (heavy and k % 2 == 0):
            s = filt(noise(0.09), lo=900, hi=6000) * env_exp(int(0.09 * SR), 35)
            out[i:i + len(s)] += s[: n - i] * 0.5
        if k % 8 == 7:
            for r in range(8):
                j = i + int(r * 0.0625 * SR)
                s = filt(noise(0.05), lo=900, hi=6000) * env_exp(int(0.05 * SR), 60)
                if j < n:
                    out[j:j + len(s)] += s[: n - j] * 0.35
        k += 1
    return out


def amb_gallop(sec, heavy=False):
    n = int(sec * SR)
    out = np.zeros(n)
    t0 = 0.0
    while t0 < sec:
        for off in (0, 0.09, 0.18):
            i = int((t0 + off) * SR)
            m = int(0.08 * SR)
            s = filt(noise(0.08), lo=60, hi=900) * env_exp(m, 40)
            if i < n:
                out[i:i + m] += s[: n - i] * rng.uniform(0.6, 1)
        t0 += 0.42 if heavy else 0.5
    if heavy:
        out += filt(noise(sec), hi=150) * 0.3
    return out


def amb_clock(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    for k in range(int(sec)):
        s = tick(k % 2 == 0)
        i = int(k * SR)
        out[i:i + len(s)] += s[: n - i]
    return out * 1.4


def amb_quill(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.2
    while t < sec - 0.5:
        d = rng.uniform(0.15, 0.5)
        m = int(d * SR)
        tt = np.arange(m) / SR
        s = filt(noise(d), lo=3000, hi=9000) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(8, 15) * tt) ** 2)
        s *= np.sin(np.pi * tt / d)
        i = int(t * SR)
        out[i:i + m] += s[: n - i] * 0.5
        t += d + rng.uniform(0.05, 0.4)
    return out


def amb_birds(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.3
    while t < sec - 0.5:
        for _ in range(int(rng.integers(2, 5))):
            c = chirp()
            i = int(t * SR)
            out[i:i + len(c)] += c[: n - i] * 0.3
            t += rng.uniform(0.08, 0.2)
        t += rng.exponential(1.6)
    return out


def amb_gulls(sec):
    n = int(sec * SR)
    out = amb_sea(sec) * 0.0
    t = rng.uniform(0.3, 1.5)
    while t < sec - 0.6:
        g = gull()
        i = int(t * SR)
        out[i:i + len(g)] += g[: n - i] * 0.18
        t += rng.uniform(1.5, 4)
    return out


def amb_sleigh(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.0
    while t < sec - 0.2:
        for f in rng.uniform(2500, 4500, 3):
            m = int(0.25 * SR)
            tt = np.arange(m) / SR
            s = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 25)
            i = int((t + rng.uniform(0, 0.05)) * SR)
            out[i:i + m] += s[: n - i] * 0.25
        t += 0.25
    return out + amb_gallop(sec) * 0.6


def amb_heart(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.0
    while t < sec - 0.5:
        h = heartbeat()
        i = int(t * SR)
        out[i:i + len(h)] += h[: n - i]
        t += 0.95
    return out * 0.9


def amb_room(sec):
    return filt(noise(sec), hi=300) * 0.08


AMB = {
    "rain": lambda s: amb_rain(s), "rainH": lambda s: amb_rain(s, True), "wind": lambda s: amb_wind(s),
    "blizzard": lambda s: amb_wind(s, True), "sea": amb_sea, "river": amb_river, "fire": lambda s: amb_fire(s),
    "fireH": lambda s: amb_fire(s, True), "cheer": lambda s: amb_crowd(s, "cheer"),
    "angry": lambda s: amb_crowd(s, "angry"), "murmur": lambda s: amb_crowd(s, "murmur"),
    "panic": lambda s: amb_crowd(s, "panic"), "march": lambda s: amb_march(s),
    "marchH": lambda s: amb_march(s, True), "gallop": lambda s: amb_gallop(s),
    "gallopH": lambda s: amb_gallop(s, True), "clock": amb_clock, "quill": amb_quill, "birds": amb_birds,
    "gulls": amb_gulls, "sleigh": amb_sleigh, "heart": amb_heart, "room": amb_room,
}
AMB_GAIN = {"rain": 0.35, "rainH": 0.45, "wind": 0.35, "blizzard": 0.45, "sea": 0.35, "river": 0.3,
            "fire": 0.35, "fireH": 0.45, "cheer": 0.32, "angry": 0.32, "murmur": 0.22, "panic": 0.3,
            "march": 0.35, "marchH": 0.45, "gallop": 0.4, "gallopH": 0.5, "clock": 0.35, "quill": 0.3,
            "birds": 0.3, "gulls": 0.5, "sleigh": 0.35, "heart": 0.5, "room": 0.3}
ONE = {"cannon": lambda: cannon(), "cannonD": lambda: cannon(0.7), "volley": lambda: musket_volley(),
       "shot": lambda: musket_volley(1, 0.01), "thunder": thunder, "impact": impact, "whoosh": lambda: whoosh(),
       "rwhoosh": lambda: whoosh(1.6, True), "bell": lambda: bell(rng.choice([262, 330, 392])),
       "bellL": lambda: bell(131, 8), "explosion": explosion, "neigh": neigh, "crack": crack}
ONE_GAIN = {"cannon": 0.75, "cannonD": 0.45, "volley": 0.5, "shot": 0.5, "thunder": 0.7, "impact": 0.7,
            "whoosh": 0.3, "rwhoosh": 0.35, "bell": 0.35, "bellL": 0.4, "explosion": 0.85, "neigh": 0.25,
            "crack": 0.5}

# scene number -> effects. "x" = ambience for whole scene, "x@t" one-shot at t s, "x*n" n spread one-shots
SFX = {
    1: "rainH wind thunder@1.5 impact@0", 2: "rainH fire", 3: "rain march neigh@2", 4: "rain march",
    5: "rainH thunder@0.3 impact@0", 6: "bell@0.2 cheer impact@0", 7: "whoosh@0.2 room", 8: "wind birds",
    9: "clock rwhoosh@0.5", 10: "impact@0 marchH wind", 11: "angry cannonD@1 fire", 12: "angry",
    13: "murmur whoosh@0", 14: "whoosh@0.3 march", 15: "wind murmur", 16: "sea gulls birds", 17: "room",
    18: "sea gulls", 19: "wind sea", 20: "sea fire cannon*4", 21: "angry march", 22: "panic cannon*3",
    23: "wind fire", 24: "cheer", 25: "marchH volley*3 cannonD*2", 26: "whoosh@0.2 whoosh@1.4",
    27: "cheer bell@0.5", 28: "sea gulls", 29: "whoosh@0.3", 30: "sea gulls", 31: "wind volley*4 gallopH",
    32: "sea cannon*4 explosion@1.5", 33: "wind", 34: "fire room", 35: "sea", 36: "panic march",
    37: "room", 38: "blizzard march", 39: "volley*3 cannonD*2", 40: "gallopH cannon*2", 41: "quill room",
    42: "birds", 43: "quill room", 44: "impact@0 room", 45: "whoosh@0.2", 46: "sea cannon*4",
    47: "murmur bellL@0.2", 48: "bell@0.1 impact@0 murmur", 49: "cheer bell@0.3", 50: "sea march",
    51: "blizzard rainH sea thunder@1", 52: "sea march", 53: "sea gulls", 54: "sea cannon*6 volley*2",
    55: "sea heart", 56: "whoosh@0.3", 57: "march", 58: "march wind", 59: "wind march",
    60: "whoosh@0.3 whoosh@1.2", 61: "impact@0 marchH", 62: "cheer cannonD*2", 63: "crack@0.4 room",
    64: "marchH", 65: "gallopH volley*2 cannon*2", 66: "march cheer gallop", 67: "sea gulls",
    68: "blizzard gallopH volley*2", 69: "river cannon*4", 70: "river cheer", 71: "bell@0.2 cheer",
    72: "whoosh@0.2", 73: "crack@0.3 heart", 74: "wind march", 75: "murmur", 76: "angry volley*2",
    77: "volley@1.5 heart", 78: "wind shot*3", 79: "sea march", 80: "heart", 81: "marchH",
    82: "river volley*2 cannonD*2", 83: "cannon*6", 84: "room heart", 85: "bell@0.2 bell@1.2 murmur",
    86: "bell@0.2", 87: "thunder@0.2 wind", 88: "sea gulls", 89: "marchH river", 90: "fireH",
    91: "wind march", 92: "cannon*6 volley*3 explosion@2", 93: "wind bellL@0.5", 94: "fireH",
    95: "clock fire", 96: "blizzard", 97: "blizzard gallop", 98: "river blizzard", 99: "sleigh wind",
    100: "wind crack@0.5", 101: "cheer", 102: "wind march", 103: "cannon*5 volley*3 marchH",
    104: "river explosion@0.4", 105: "blizzard march", 106: "marchH", 107: "quill clock", 108: "sea gulls",
    109: "murmur", 110: "murmur", 111: "sea", 112: "sea march", 113: "heart wind", 114: "cheer",
    115: "cheer bell@0.4", 116: "whoosh@0.3 march", 117: "cannon*3 volley*2 gallop", 118: "rain clock",
    119: "rain march", 120: "fire volley*3", 121: "gallopH volley*3", 122: "marchH", 123: "marchH impact@0",
    124: "panic volley*2", 125: "sea", 126: "sea wind", 127: "clock quill", 128: "clock heart",
    129: "wind", 130: "whoosh@0.2", 131: "sea bell@0.5", 132: "whoosh@0.2", 133: "impact@0",
    134: "impact@0", 135: "wind impact@0",
}

# ====================================================================== score
MOODS = {}
for a, b, m in ((1, 4, "tense"), (5, 6, "epic"), (7, 9, "tense"), (10, 10, "epic"), (11, 15, "tense"),
                (16, 17, "calm"), (18, 22, "tense"), (23, 23, "sad"), (24, 27, "triumph"), (28, 30, "mystic"),
                (31, 32, "epic"), (33, 35, "mystic"), (36, 37, "tense"), (38, 40, "epic"), (41, 45, "calm"),
                (46, 46, "tense"), (47, 49, "triumph"), (50, 52, "tense"), (53, 54, "epic"), (55, 55, "sad"),
                (56, 61, "epic"), (62, 63, "triumph"), (64, 69, "epic"), (70, 72, "triumph"), (73, 73, "dark"),
                (74, 80, "dark"), (81, 83, "epic"), (84, 84, "sad"), (85, 86, "calm"), (87, 88, "dark"),
                (89, 92, "epic"), (93, 95, "dark"), (96, 100, "sad"), (101, 103, "epic"), (104, 108, "sad"),
                (109, 110, "calm"), (111, 116, "triumph"), (117, 123, "epic"), (124, 124, "dark"),
                (125, 129, "sad"), (130, 132, "calm"), (133, 135, "epic_soft")):
    for k in range(a, b + 1):
        MOODS[k] = m

# stem gains per mood: dark pad, bright pad, drums, brass(minor), brass(major), melody, drone
MIXES = {
    "tense": (0.9, 0, 0.35, 0, 0, 0, 0.6), "epic": (1.0, 0, 1.0, 0.8, 0, 0, 0.3),
    "triumph": (0, 1.0, 0.6, 0, 0.8, 0, 0), "calm": (0, 0.8, 0, 0, 0, 0.4, 0),
    "sad": (0.7, 0, 0, 0, 0, 1.0, 0.3), "mystic": (0.6, 0, 0.25, 0, 0, 0.6, 0.8),
    "dark": (1.0, 0, 0.45, 0.4, 0, 0, 1.0), "epic_soft": (0.8, 0.5, 0.4, 0.3, 0.3, 0.6, 0.2),
}

MINOR = [[38, 50, 53, 57], [34, 46, 50, 53], [41, 48, 53, 57], [36, 48, 52, 55]]  # Dm Bb F C
MAJOR = [[38, 50, 54, 57], [43, 50, 55, 59], [35, 50, 54, 59], [33, 49, 52, 57]]  # D G Bm A
BAR = 2.5  # seconds per bar (96 bpm, 4/4)
CHORD = BAR * 2


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def pad_stem(N, chords, bright=False):
    out = np.zeros((N, 2))
    ln = int((CHORD + 2.5) * SR)
    t = np.arange(ln) / SR
    e = np.minimum(1, np.minimum(t / 1.5, (CHORD + 2.5 - t) / 2.0)).clip(0, 1) ** 2
    for k in range(int(N / SR / CHORD) + 1):
        for m in chords[k % 4]:
            for det, ch in ((-0.9, 0), (0.9, 1)):
                f = hz(m + (12 if bright else 0) * (m > 45)) + det
                ph = rng.uniform(0, 6.28)
                vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t + ph)
                s = sum(np.sin(2 * np.pi * f * h * t * vib + ph * h) / h ** (1.2 if bright else 1.5)
                        for h in (1, 2, 3, 4, 5))
                i = int((k * CHORD - 1.0) * SR)
                a, b = max(0, i), min(N, i + ln)
                if b > a:
                    out[a:b, ch] += (s * e)[a - i:b - i]
    return out / np.abs(out).max()


def drum_stem(N):
    out = np.zeros(N)
    beat = BAR / 4
    pattern = [1, 0, 0.5, 0, 0.8, 0.4, 0.6, 0]  # eighth notes
    k = 0
    while k * beat / 2 < N / SR:
        g = pattern[k % 8]
        bar = k // 8
        if bar % 4 == 3 and k % 8 >= 4:
            g = max(g, 0.7)
        if g:
            n = int(1.2 * SR)
            t = np.arange(n) / SR
            f = 48 + 40 * np.exp(-t * 25)
            s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
            s += filt(noise(1.2), hi=500) * env_exp(n, 12) * 0.4
            i = int(k * beat / 2 * SR)
            out[i:i + n] += s[: N - i] * g
        if k % 8 in (2, 6):
            n = int(0.25 * SR)
            s = filt(noise(0.25), lo=1500, hi=7000) * env_exp(n, 20) * 0.25
            i = int(k * beat / 2 * SR)
            out[i:i + n] += s[: N - i]
        k += 1
    out = reverb(out, 1.5, 0.35)[:N]
    return np.stack([out, out], 1) / np.abs(out).max()


def brass_stem(N, chords):
    out = np.zeros(N)
    ln = int(CHORD * SR)
    t = np.arange(ln) / SR
    e = (np.minimum(1, t / 0.35) * np.exp(-t * 0.5)) * (t < CHORD - 0.3)
    for k in range(int(N / SR / CHORD) + 1):
        root = chords[k % 4][0]
        for m in (root + 12, root + 19, root + 24):
            f = hz(m)
            s = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 9))
            i = int(k * CHORD * SR)
            b = min(N, i + ln)
            if b > i:
                out[i:b] += (s * e)[: b - i]
    out = filt(out, hi=1800)
    out = reverb(out, 1.8, 0.35)[:N]
    return np.stack([out * 0.9, out], 1) / np.abs(out).max()


def melody_stem(N):
    scale = [62, 64, 65, 67, 69, 70, 72, 74]
    out = np.zeros(N)
    t0, idx = 0.5, 3
    while t0 < N / SR - 3:
        idx = int(np.clip(idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, len(scale) - 1))
        d = rng.choice([BAR / 2, BAR, BAR, BAR * 1.5])
        n = int((d + 2.5) * SR)
        t = np.arange(n) / SR
        f = hz(scale[idx])
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 2)
             + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 4))
        s *= np.minimum(1, t / 0.01) * np.exp(-t * 0.9)
        i = int(t0 * SR)
        out[i:i + n] += s[: N - i]
        t0 += d
    out = reverb(out, 2.5, 0.45, 1.6)[:N]
    return np.stack([out, out * 0.9], 1) / np.abs(out).max()


def drone_stem(N):
    t = np.arange(N) / SR
    s = np.zeros(N)
    for f, a in ((36.7, 1), (73.4, 0.5), (55.0, 0.3)):
        s += a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    s += filt(rng.standard_normal(N), lo=60, hi=240) * 0.6
    s *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 11)
    return np.stack([s, s], 1) / np.abs(s).max()


def smooth_env(points, N, ramp=1.5):
    """points: list of (t_start, value) step function -> smoothed per-sample gain."""
    g = np.zeros(N, dtype=np.float32)
    for i, (t, v) in enumerate(points):
        a = int(t * SR)
        b = int(points[i + 1][0] * SR) if i + 1 < len(points) else N
        g[a:b] = v
    k = int(ramp * SR)
    ker = np.ones(k, dtype=np.float32) / k
    cs = np.cumsum(np.concatenate([np.full(k, g[0]), g, np.full(k, g[-1])]))
    sm = (cs[k:] - cs[:-k])[k // 2: k // 2 + N]
    return sm.astype(np.float32)


# ====================================================================== main
def place(buf, x, t0, gain, pan=0.0):
    i = int(t0 * SR)
    if i < 0:
        x, i = x[-i:], 0
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x), 0] += x * gain * np.sqrt(0.5 * (1 - pan))
    buf[i:i + len(x), 1] += x * gain * np.sqrt(0.5 * (1 + pan))


def main():
    words_path, narr_path, out = sys.argv[1:4]
    dur, starts, words = load_timing(words_path)
    ends = starts[1:] + [dur]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", narr_path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    narr = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    N = len(narr)
    print("narration", N / SR, "s")

    # ---- score
    moods = [MOODS[i + 1] for i in range(len(starts))]
    stems = [("dark", lambda: pad_stem(N, MINOR)), ("bright", lambda: pad_stem(N, MAJOR, True)),
             ("drums", lambda: drum_stem(N)), ("brassm", lambda: brass_stem(N, MINOR)),
             ("brassM", lambda: brass_stem(N, MAJOR)), ("melody", lambda: melody_stem(N)),
             ("drone", lambda: drone_stem(N))]
    music = np.zeros((N, 2))
    for si, (name, fn) in enumerate(stems):
        pts = [(s, MIXES[m][si]) for s, m in zip(starts, moods)]
        g = smooth_env(pts, N, 2.0)
        if g.max() <= 0:
            continue
        music += fn() * g[:, None] * [0.22, 0.2, 0.32, 0.16, 0.16, 0.22, 0.14][si]
        print("stem", name)
    music = music / np.abs(music).max() * 0.6

    # ---- duck music under speech
    talk = np.zeros(N, dtype=np.float32)
    for w in words:
        talk[int(w["s"] * SR):int(w["e"] * SR)] = 1
    k = int(0.4 * SR)
    cs = np.cumsum(np.concatenate([np.zeros(k), talk, np.zeros(k)]))
    talk_s = np.clip((cs[2 * k:] - cs[:-2 * k])[:N] / (k * 0.6), 0, 1)
    music *= (1 - 0.5 * talk_s)[:, None]

    # ---- effects
    fx = np.zeros((N, 2))
    for i, (s, e) in enumerate(zip(starts, ends)):
        spec = SFX.get(i + 1, "")
        d = e - s + 0.4
        for tok in spec.split():
            if "@" in tok:
                name, at = tok.split("@")
                place(fx, ONE[name](), s + float(at), ONE_GAIN[name], float(rng.uniform(-0.3, 0.3)))
            elif "*" in tok:
                name, n = tok.split("*")
                for j in range(int(n)):
                    at = s + (j + rng.uniform(0.1, 0.9)) * max(0.3, d - 1) / int(n)
                    place(fx, ONE[name](), at, ONE_GAIN[name] * rng.uniform(0.6, 1), float(rng.uniform(-0.7, 0.7)))
            else:
                x = AMB[tok](d + 0.6)
                x = fades(x / (np.abs(x).max() + 1e-9), 0.35, 0.6)
                place(fx, x, s - 0.2, AMB_GAIN[tok] * 0.6, float(rng.uniform(-0.2, 0.2)))
        if i % 15 == 0:
            print("sfx scene", i + 1)
    fx *= (1 - 0.35 * talk_s)[:, None]

    # ---- final mix
    narr = narr / np.abs(narr).max() * 0.9
    mixd = np.stack([narr, narr], 1) * 1.0 + music * 0.55 + fx * 0.5
    tm = np.arange(N) / SR
    mixd *= np.minimum(1, (dur - tm) / 3).clip(0, 1)[:, None]
    mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
    mixd = mixd / np.abs(mixd).max() * 0.95
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mixd * 32767).astype("<i2").tobytes())
    # also save stems for inspection/remix
    print("wrote", out)


if __name__ == "__main__":
    main()
