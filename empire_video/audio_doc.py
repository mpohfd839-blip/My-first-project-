"""Orchestral-style score + SFX for the empire documentary, mixed with narration."""
import json, math, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt, oaconvolve
from script import BEATS

SR = 44100
TL = json.load(open("timeline.json"))
TOTAL = TL["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(3)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)


def noise(d):
    return rng.standard_normal(int(d * SR))


def norm(x, p=1.0):
    return x / (np.max(np.abs(x)) + 1e-9) * p


def env(n, a, r, sustain=True):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-3))
    if r:
        tail = np.minimum(1, (n / SR - t) / r)
        e = e * np.clip(tail, 0, 1)
    return e


def saw(f, d, det=0.0):
    t = tt(d)
    ph = (f * (1 + det)) * t
    return 2 * (ph - np.floor(ph + 0.5))


NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name, octv):
    return NOTE[name] * 2 ** (octv - 4)


CH_MINOR = [("D", "F", "A"), ("A#", "D", "F"), ("F", "A", "C"), ("C", "E", "G")]
CH_MAJOR = [("D", "F#", "A"), ("G", "B", "D"), ("A", "C#", "E"), ("D", "F#", "A")]
CH_SOMBER = [("D", "F", "A"), ("G", "A#", "D"), ("A", "C#", "E"), ("D", "F", "A")]


def strings(chord, d, bright=900, oct_=3, amp=1.0):
    out = np.zeros(int(d * SR))
    for i, n in enumerate(chord):
        f = hz(n, oct_ + (1 if i > 0 else 0))
        for det in (-0.004, 0.0, 0.005):
            out += saw(f, d, det) * (0.5 if i == 0 else 0.35)
        out += saw(hz(chord[0], oct_ - 1), d) * 0.25
    out = lp(out, bright, 2)
    t = tt(d)
    out *= (1 + 0.08 * np.sin(2 * np.pi * 5.2 * t))
    return out * env(len(out), 0.8, 0.8) * amp


def brass(chord, d, amp=1.0):
    out = np.zeros(int(d * SR))
    t = tt(d)
    for i, n in enumerate(chord):
        f = hz(n, 3 if i == 0 else 4)
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
        ph = np.cumsum(f * vib) / SR
        out += (2 * (ph - np.floor(ph + .5))) * 0.4
    e = env(len(out), 0.15, 0.6)
    out = lp(out, 600, 2) * (1 - e) + lp(out, 2200, 2) * e
    return out * e * amp


def timp(f=55, d=2.0, amp=1.0):
    t = tt(d)
    fr = f * (1 + 0.15 * np.exp(-t * 8))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 2.5)
    x += lp(noise(d), 400) * np.exp(-t * 18) * 0.5
    return x * amp


def taiko(d=1.5, amp=1.0):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(70 * (1 + .6 * np.exp(-t * 20))) / SR) * np.exp(-t * 5)
    x += lp(noise(d), 900) * np.exp(-t * 25) * .6
    return x * amp


def pluck(f, d=1.2, amp=1.0):
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) + .2 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 3.5)
    return x * amp


def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n] * g


# ------------------------------------------------------------------ score
music = np.zeros(N)
segs = TL["beats"]
moods = []
cur = 0
for s in segs:
    m = BEATS[s["i"]].get("mood")
    if m is not None:
        cur = m
    moods.append((s["start"], s["end"], cur))
moods.append((TL["endcard"][0], TL["endcard"][1], 5))
BAR = 4.0
tpos = 0.0
bi = 0
while tpos < TOTAL - 1:
    m = next((mm for a, b, mm in moods if a <= tpos + 0.01 < b), 0)
    prog = {0: CH_MINOR, 1: CH_SOMBER, 2: CH_MINOR, 3: CH_MINOR, 4: CH_MAJOR, 5: CH_MAJOR}[m]
    ch = prog[bi % 4]
    d = BAR + 0.8
    if m == 0:
        add(music, strings(ch, d, 700, 3, .5), tpos)
        for k in range(8):
            n = ch[k % 3]
            add(music, pluck(hz(n, 5 if k % 4 else 4), 1.4, .25), tpos + k * BAR / 8)
    elif m == 1:
        add(music, strings(ch, d, 450, 2, .6), tpos)
        add(music, pluck(hz(ch[0], 4), 3.0, .3), tpos)
        add(music, pluck(hz(ch[2], 4), 3.0, .2), tpos + 2)
    elif m == 2:
        add(music, strings(ch, d, 900, 3, .5), tpos)
        for k in range(16):
            x = saw(hz(ch[0], 2), 0.2) * env(int(0.2 * SR), .01, .1)
            add(music, lp(x, 600) * .5, tpos + k * BAR / 16)
        add(music, timp(hz(ch[0], 2), 2, .8), tpos)
        add(music, timp(hz(ch[0], 2), 2, .6), tpos + 2.5)
    elif m == 3:
        add(music, strings(ch, d, 1500, 3, .7), tpos)
        add(music, brass(ch, d, .6), tpos)
        add(music, taiko(1.5, 1.0), tpos)
        add(music, taiko(1.5, .7), tpos + 1.5)
        add(music, taiko(1.5, .9), tpos + 3)
    elif m == 4:
        add(music, strings(ch, d, 1200, 3, .6), tpos)
        add(music, brass(ch, d, .5), tpos + 0.05)
        add(music, timp(hz(ch[0], 2), 2, .5), tpos)
    else:
        add(music, strings(ch, d, 1600, 3, .8), tpos)
        add(music, brass(ch, d, .7), tpos)
        add(music, timp(hz(ch[0], 2), 2.5, .8), tpos)
        for k in range(8):
            add(music, pluck(hz(ch[k % 3], 5), 1.2, .2), tpos + k * .5)
    tpos += BAR
    bi += 1
music = norm(music, 0.8)

# ------------------------------------------------------------------ sfx
def whoosh(d=1.0, rev=False):
    x = noise(d); t = tt(d)
    out = np.zeros(len(x))
    seg = 1024
    for i in range(0, len(x), seg):
        f = 300 + 3000 * (i / len(x))
        out[i:i + seg] = bp(x[i:i + seg], f, min(f * 1.8, 18000), 1)
    out = lp(out * np.sin(np.pi * t / d) ** 2, 6000)
    out = norm(out, .5)
    return out[::-1].copy() if rev else out


def boom(d=3.0, f=40):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + .7 * np.exp(-t * 5))) / SR) * np.exp(-t * 1.3)
    x += lp(noise(d), 250) * np.exp(-t * 4) * .5
    return norm(x)


def riser(d=2.5):
    t = tt(d)
    f = 200 + 1800 * (t / d) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + bp(noise(d), 1000, 8000) * .4
    return norm(x * (t / d) ** 2, .6)


def ping(f, d=.5):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 9)


def click(g=1.0):
    return hp(noise(.02), 2500) * np.exp(-tt(.02) * 300) * g


def SFX(name, d):
    if name == "wind":
        x = bp(noise(d), 200, 900) * (0.6 + .4 * np.sin(2 * np.pi * .15 * tt(d))); return norm(x, .25)
    if name == "drone":
        t = tt(d); return (np.sin(2 * np.pi * 55 * t) + .5 * np.sin(2 * np.pi * 82.5 * t)) * env(len(t), 1, 1) * .25
    if name == "boom":
        return boom() * .8
    if name == "riser":
        return riser() * .7
    if name == "hit4":
        out = np.zeros(int(4 * SR))
        for k in range(4):
            add(out, taiko(1, .8), .6 + k * .9)
        return out
    if name == "brass":
        return brass(("D", "F#", "A"), 3.0, .8)
    if name == "page":
        x = bp(noise(.5), 1500, 8000) * np.sin(np.pi * tt(.5) / .5) ** 2; return norm(x, .35)
    if name == "chapter":
        out = np.zeros(int(3 * SR)); add(out, boom(2.5, 50) * .6, 0); add(out, whoosh(1.0, True) * .6, 0); return out
    if name == "quill":
        n = int(min(d, 4) * SR); x = bp(noise(n / SR), 2500, 9000) * (0.5 + .5 * (np.sin(2 * np.pi * 4 * tt(n / SR)) > 0)); return norm(x, .12)
    if name == "seal":
        return norm(lp(noise(.3), 600) * np.exp(-tt(.3) * 15), .6)
    if name == "coins":
        out = np.zeros(int(2.5 * SR))
        for k in range(12):
            add(out, ping(rng.uniform(2500, 5000), .4) * .25, rng.uniform(0, 2))
        return out
    if name in ("march", "footsteps"):
        out = np.zeros(int(min(d, 6) * SR) + SR)
        for k in range(int(min(d, 6) / .5)):
            add(out, lp(noise(.12), 1200) * np.exp(-tt(.12) * 40) * .5, k * .5)
            if name == "march" and k % 2 == 0:
                add(out, hp(noise(.08), 3000) * np.exp(-tt(.08) * 60) * .3, k * .5 + .25)
        return out
    if name == "waves":
        t = tt(d); x = lp(noise(d), 700) * (0.4 + .6 * np.sin(2 * np.pi * .18 * t) ** 2); return norm(x, .3)
    if name == "creak":
        t = tt(1.5); f = 120 + 50 * np.sin(2 * np.pi * .8 * t)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + .5 * (np.sin(2 * np.pi * 9 * t) > .3))
        return bp(x, 300, 2500) * np.sin(np.pi * t / 1.5) * .15
    if name == "tick":
        out = np.zeros(int(min(d, 6) * SR) + SR)
        for k in range(int(min(d, 6))):
            add(out, click(.6), k)
        return out
    if name in ("cannon", "cannon2", "gunfire"):
        out = np.zeros(int(5 * SR))
        n = 3 if name != "gunfire" else 8
        for k in range(n):
            g = boom(1.5, 60) if name != "gunfire" else hp(noise(.3), 800) * np.exp(-tt(.3) * 25)
            add(out, g * (.8 if name != "gunfire" else .5), .2 + k * (1.1 if name != "gunfire" else .25) + rng.uniform(0, .2))
        return out
    if name == "sitar":
        out = np.zeros(int(4 * SR))
        for k, n in enumerate(["D", "E", "F", "A", "G", "F", "E", "D"]):
            x = pluck(hz(n, 4), 1.0, .3); x = x + .3 * np.sin(2 * np.pi * hz(n, 5) * 1.003 * tt(1.0)) * np.exp(-tt(1.0) * 3)
            add(out, x, k * .4)
        return out
    if name == "crack":
        return norm(hp(noise(.6), 1500) * np.exp(-tt(.6) * 8), .5)
    if name == "thud_seq":
        out = np.zeros(int(5 * SR))
        for k in range(6):
            add(out, timp(70, 1, .6), .3 + k * .7)
        return out
    if name == "fire":
        n = int(d * SR); x = lp(noise(d), 900) * .5
        pops = np.zeros(n)
        for k in range(int(d * 10)):
            i = rng.integers(0, max(1, n - 500)); pops[i:i + 500] += hp(noise(500 / SR), 1500) * np.exp(-tt(500 / SR) * 200) * rng.uniform(.3, 1)
        return norm(x + pops, .3)
    if name == "factory":
        out = np.zeros(int(min(d, 8) * SR) + SR)
        for k in range(int(min(d, 8) / .6)):
            add(out, ping(180, .4) * .3, k * .6); add(out, lp(noise(.1), 2000) * .2, k * .6 + .3)
        return out
    if name == "whoosh":
        return whoosh(1.2) * .7
    if name == "train":
        t = tt(min(d, 8)); x = lp(noise(len(t) / SR), 1500) * (0.4 + .6 * (np.sin(2 * np.pi * 3.2 * t) > .5)); x = norm(x, .3)
        add(x, (np.sin(2 * np.pi * 700 * tt(1)) + np.sin(2 * np.pi * 880 * tt(1))) * env(SR, .1, .3) * .12, 0.3)
        return x
    if name == "morse":
        out = np.zeros(int(min(d, 6) * SR) + SR)
        pat = ".-.. --- -. -.. --- -.   -... --- -- -... .- -.--"
        tp = .2
        for c in pat:
            if c == ".":
                add(out, np.sin(2 * np.pi * 800 * tt(.08)) * .12, tp); tp += .16
            elif c == "-":
                add(out, np.sin(2 * np.pi * 800 * tt(.24)) * .12, tp); tp += .32
            else:
                tp += .2
        return out
    if name == "stamp":
        out = np.zeros(int(4 * SR))
        for k in range(6):
            add(out, norm(lp(noise(.2), 900) * np.exp(-tt(.2) * 30), .5), .4 + k * .35)
        return out
    if name == "tear":
        return norm(bp(noise(1.0), 1500, 7000) * (np.abs(np.sin(2 * np.pi * 30 * tt(1.0))) > .3), .3)
    if name == "pen_lines":
        out = np.zeros(int(5 * SR))
        for k in range(6):
            add(out, norm(bp(noise(.4), 2500, 9000), .12), .3 + k * .6)
        return out
    if name == "chains":
        out = np.zeros(int(3 * SR))
        for k in range(10):
            add(out, ping(rng.uniform(1500, 3000), .3) * .2, rng.uniform(0, 2.5))
        return out
    if name == "flags":
        return norm(bp(noise(min(d, 4)), 300, 2000) * (0.5 + .5 * np.sin(2 * np.pi * 6 * tt(min(d, 4)))), .2)
    if name == "rain":
        return norm(hp(noise(d), 1500), .12)
    if name == "anthem":
        out = np.zeros(int(6 * SR))
        for k, (ch, dd) in enumerate([(("G", "B", "D"), 1.5), (("C", "E", "G"), 1.5), (("D", "F#", "A"), 3)]):
            add(out, brass(ch, dd + .3, .35), [0, 1.5, 3][k])
        return out
    return np.zeros(10)


SUST = {"wind", "drone", "waves", "fire", "rain", "train", "factory", "quill", "flags"}
sfx = np.zeros(N)
for s in segs:
    b = BEATS[s["i"]]
    d = s["end"] - s["start"]
    for nm in b.get("sfx", []):
        x = SFX(nm, d)
        if nm in SUST:
            x = x[: int(d * SR)].copy()
            fo = min(len(x), int(.5 * SR)); x[-fo:] *= np.linspace(1, 0, fo)
        add(sfx, x, s["start"] - (0.1 if nm != "riser" else 0))
    # soft transition swoosh + paper rustle on palette change
    if s["i"] > 0 and BEATS[s["i"] - 1]["pal"] != b["pal"]:
        add(sfx, whoosh(1.0, True) * .5, s["start"] - .8)
    else:
        add(sfx, whoosh(.6) * .15, s["start"] - .1)
add(sfx, boom(3, 45) * .6, TL["endcard"][0])

# reverb
irt = tt(2.5)
ir = rng.standard_normal(len(irt)) * np.exp(-irt * 2.6)
ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
bed = music * .9 + sfx
wet = oaconvolve(bed, ir)[:N]
bed = bed * .75 + wet * .45

# music + sfx only (no narration)
bed = bed / (np.sqrt(np.mean(bed ** 2)) + 1e-9) * 0.16
mix = bed
fo = int(3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
# light stereo widening of the bed
L_ = mix + 0.0
st = np.stack([mix + wet[:N] * .03, mix - wet[:N] * .03], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("final_audio_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio", TOTAL)
