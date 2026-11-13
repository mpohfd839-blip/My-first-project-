"""Orchestral-style score + SFX for the empire documentary, mixed with narration."""
import json, math, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt, oaconvolve
from story import SHOTS
BEATS = [sp for sp, _ in SHOTS]

SR = 44100
TL = json.load(open("timeline.json"))
AUD = TL["duration"]
TOTAL = AUD + 8.0
_SEG = []
for i, (sp, lines) in enumerate(SHOTS):
    ss = TL["timeline"][i]["sentences"]
    t0 = (0.0 if i == 0 else max(0.0, ss[0]["start"] - 0.3)) if ss else _SEG[-1]["sents"][-1]["end"] + 1.0
    _SEG.append(dict(i=i, start=t0, sents=ss))
for i, s_ in enumerate(_SEG):
    s_["end"] = _SEG[i + 1]["start"] if i + 1 < len(_SEG) else TOTAL
TL["beats"] = _SEG
TL["endcard"] = [_SEG[-1]["start"], TOTAL]
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
    if i < 0:
        x = x[-i:]; i = 0
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


def zap(d=0.6, big=False):
    n = int(d * SR)
    x = hp(noise(d), 1500 if not big else 600) * (rng.random(n) > (0.6 if not big else 0.4))
    x *= np.exp(-tt(d) * (3 if big else 6))
    buzz = np.sign(np.sin(2 * np.pi * 120 * tt(d))) * 0.3 * np.exp(-tt(d) * 4)
    return norm(lp(x + buzz, 9000), .8)


def thunder(d=4.0, far=False):
    t = tt(d)
    x = lp(noise(d), 160 if far else 400) * (np.exp(-t * 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * t) ** 2))
    if not far:
        x[: int(.3 * SR)] += hp(noise(.3), 1000) * np.exp(-tt(.3) * 10) * 1.5
    return norm(x, .9 if not far else .45)


def SFX(name, d):
    if name == "thunder":
        return thunder()
    if name == "thunder_far":
        return thunder(5, True)
    if name == "zap":
        return zap(.7) * .6
    if name == "zap_big":
        out = np.zeros(int(3 * SR)); add(out, zap(1.4, True), 0); add(out, thunder(3)[: int(2.5 * SR)] * .5, .1); return out
    if name == "switch":
        out = np.zeros(int(2 * SR)); add(out, click(1.0), .8); add(out, boom(1, 80) * .4, .8); return out
    if name == "hum":
        t = tt(d); x = (np.sin(2 * np.pi * 60 * t) + .5 * np.sin(2 * np.pi * 120 * t) + .3 * np.sign(np.sin(2 * np.pi * 180 * t))) * env(len(t), .5, .5)
        return lp(x, 900) * .18
    if name == "spark_loop":
        n = int(min(d, 8) * SR); out = np.zeros(n + SR)
        for k in range(int(min(d, 8) * 8)):
            add(out, zap(.08) * .35, rng.uniform(0, min(d, 8)))
        return out
    if name == "clock":
        out = np.zeros(int(3 * SR))
        for k in range(12):
            add(out, ping(1200, .4) * .2, k * .22)
        return out
    if name == "rain":
        return norm(hp(noise(d), 1200), .15)
    if name == "chime":
        out = np.zeros(int(4 * SR))
        for k, f in enumerate((1318, 1568, 1976, 2637)):
            add(out, ping(f, 2.0) * .25, k * .15)
        return out
    if name == "laugh":
        out = np.zeros(int(2.5 * SR))
        for k in range(6):
            tt_ = tt(.18); x = (np.sin(2 * np.pi * 180 * tt_) + .5 * np.sin(2 * np.pi * 540 * tt_) + .3 * noise(.18)) * np.sin(np.pi * tt_ / .18)
            add(out, lp(x, 1200) * .3, .1 + k * .25)
        return out
    if name == "scratch":
        n = min(d, 4); x = bp(noise(n), 1500, 6000) * (0.5 + .5 * (np.sin(2 * np.pi * 2.5 * tt(n)) > 0)); return norm(x, .18)
    if name == "birds":
        out = np.zeros(int(4 * SR))
        for k in range(6):
            tt_ = tt(.25); f = 3000 + 1500 * np.sin(2 * np.pi * 14 * tt_)
            add(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt_ / .25) * .06, rng.uniform(0, 3.5))
        return out
    if name == "harbor":
        out = SFX("waves", d) * .8
        add(out, (np.sin(2 * np.pi * 110 * tt(2.5)) + .5 * np.sin(2 * np.pi * 165 * tt(2.5))) * env(int(2.5 * SR), .2, .6) * .25, .5)
        return out
    if name == "door_slam":
        out = np.zeros(int(1.5 * SR)); add(out, boom(1, 90) * .7, .1); add(out, click(1.0), .1); return out
    if name == "dig":
        out = np.zeros(int(min(d, 8) * SR) + SR)
        for k in range(int(min(d, 8) / .84)):
            add(out, norm(lp(noise(.25), 2500) * np.exp(-tt(.25) * 12), .4), .42 + k * .84)
        return out
    if name in ("motor", "turbine"):
        t = tt(d); f = 140 if name == "motor" else 220
        x = (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 1.5) + lp(noise(d), 400) * .3
        return norm(x, .2)
    if name == "crowd":
        x = bp(noise(min(d, 6)), 300, 2500) * (0.6 + .4 * np.sin(2 * np.pi * .7 * tt(min(d, 6))) ** 2); return norm(x, .15)
    if name == "crowd_gasp":
        t = tt(1.2); x = bp(noise(1.2), 400, 3000) * np.minimum(1, t / .15) * np.exp(-t * 2.5); out = np.zeros(int(3 * SR)); add(out, norm(x, .35), 1.0); return out
    if name == "waterfall":
        return norm(lp(noise(d), 3000), .3)
    if name == "click":
        out = np.zeros(int(2 * SR))
        for k in range(4):
            add(out, click(.8), .3 + k * .4)
        return out
    if name == "water":
        return norm(lp(noise(d), 600) * (0.5 + .5 * np.sin(2 * np.pi * .4 * tt(d)) ** 2), .15)
    if name == "beep":
        out = np.zeros(int(min(d, 8) * SR) + SR)
        for k in range(int(min(d, 8) / 1.2)):
            add(out, np.sin(2 * np.pi * 1500 * tt(.1)) * .1, .3 + k * 1.2)
        return out
    if name == "radio":
        t = tt(min(d, 6)); x = np.sin(2 * np.pi * (600 + 400 * np.sin(2 * np.pi * .5 * t)) * t) * .1 + hp(noise(len(t) / SR), 2000) * .05; return x
    if name == "rumble":
        return norm(lp(noise(min(d, 6)), 120) * np.minimum(1, tt(min(d, 6)) / .5), .6)
    if name == "glass":
        out = np.zeros(int(3 * SR))
        for k in range(14):
            add(out, ping(rng.uniform(3000, 6000), .3) * .15, rng.uniform(.5, 2.5))
        return out
    if name == "hit":
        return boom(1.2, 70) * .7
    if name == "powerdown":
        t = tt(3); f = 400 * np.exp(-t * 1.2) + 30
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * .8); out = np.zeros(int(4 * SR)); add(out, lp(x, 1200) * .3, .8); return out
    if name == "beeps3":
        out = np.zeros(int(4 * SR))
        for k in range(3):
            add(out, np.sin(2 * np.pi * 900 * tt(.25)) * .15, 1.2 + k * .6)
        return out
    if name == "gavel":
        out = np.zeros(int(2 * SR)); add(out, boom(.6, 140) * .6, .9); add(out, click(1.0), .9); return out
    if name == "pigeons":
        out = np.zeros(int(min(d, 6) * SR) + SR)
        for k in range(8):
            tt_ = tt(.5); x = np.sin(2 * np.pi * (300 + 40 * np.sin(2 * np.pi * 8 * tt_)) * tt_) * np.sin(np.pi * tt_ / .5)
            add(out, lp(x, 800) * .06, rng.uniform(0, min(d, 6)))
        add(out, norm(bp(noise(.6), 500, 3000), .1), 1.0)
        return out
    if name == "bell":
        t = tt(6); x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dc) for f, a, dc in ((196, 1, .5), (392, .5, .8), (470, .3, 1.0)))
        return norm(x, .3)
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


SUST = {"wind", "drone", "waves", "fire", "rain", "train", "factory", "quill", "flags", "hum", "motor", "turbine", "crowd", "waterfall", "water", "radio", "rumble", "spark_loop"}
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

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "narration.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
nar = np.frombuffer(raw, np.float32).astype(np.float64)
narr = np.zeros(N); narr[:min(N, len(nar))] = nar[:N]
narr = narr / (np.max(np.abs(narr)) + 1e-9) * 0.9
envn = np.abs(narr)
k = int(.3 * SR)
envs = np.convolve((envn > .03).astype(float)[::32], np.ones(k // 32) / (k // 32), mode="same")
envs = np.interp(np.arange(N), np.arange(len(envs)) * 32, envs)
bed *= (1 - .4 * np.clip(envs, 0, 1))
rn = np.sqrt(np.mean(narr[np.abs(narr) > .01] ** 2)); rb = np.sqrt(np.mean(bed ** 2))
bed *= rn * .28 / rb
mix = narr + bed
fo = int(3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
# light stereo widening of the bed
L_ = mix + 0.0
st = np.stack([mix + wet[:N] * .03, mix - wet[:N] * .03], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("final_audio_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio", TOTAL)
