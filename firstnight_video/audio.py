"""Synthesize horror music bed + SFX, mix with narration -> final_audio.wav"""
import json, math, subprocess
import numpy as np
from scipy.signal import oaconvolve, butter, sosfilt
from story import SHOTS

SR = 32000
TL = json.load(open("timeline.json"))
DUR = TL["duration"]
END_EXTRA = 7.0
TOTAL = DUR + END_EXTRA
N = int(TOTAL * SR)
rng = np.random.default_rng(1)

# shot times (same logic as render.py)
shots = []
for i, (spec, lines) in enumerate(SHOTS):
    shots.append(dict(spec=spec, sents=TL["timeline"][i]["sentences"]))
for i, s in enumerate(shots):
    s["t0"] = max(0.0, s["sents"][0]["start"] - 0.25) if s["sents"] else (shots[i - 1]["sents"][-1]["end"] + 0.6 if shots[i - 1]["sents"] else shots[i - 1]["t0"] + 3.0)
shots[0]["t0"] = 0.0
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL

def tt(d):
    return np.arange(int(d * SR)) / SR

def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)

def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)

def bp(x, f0, f1, order=2):
    return sosfilt(butter(order, [f0, f1], "band", fs=SR, output="sos"), x)

def noise(d):
    return rng.standard_normal(int(d * SR))

def env_ad(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e

def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak

# ------------------------------------------------------------ SFX
def boom(d=3.0, f=42):
    t = tt(d)
    fr = f * (1 + 0.6 * np.exp(-t * 6))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) * np.exp(-t * 1.4)
    x += lp(noise(d), 300) * np.exp(-t * 4) * 0.6
    return norm(x)

def cluster(d=2.5, fs=(466, 494, 523, 740, 784), swell=True):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * (5 + i) * t) * 0.02 * f / 50) for i, f in enumerate(fs))
    e = np.sin(np.pi * np.minimum(1, t / d)) if swell else np.exp(-t * 1.5)
    return norm(x * e)

def sfx_drone_hit(d):
    return boom(4.0, 38) * 1.0

def sfx_sting_big(d):
    b = boom(4.0, 36)
    c = cluster(3.0, (311, 330, 349, 622, 659, 1245), swell=False)
    scr = bp(noise(1.2), 1500, 5000) * env_ad(int(1.2 * SR), 0.01, 0.3)
    out = np.zeros(int(4.0 * SR))
    out[:len(b)] += b
    out[:len(c)] += c * 0.45
    out[:len(scr)] += norm(scr) * 0.35
    return norm(out)

def sfx_sting_soft(d):
    return cluster(3.0, (880, 932, 1245, 1319)) * 0.5

def sfx_whoosh(d, rev=False):
    n = int(1.0 * SR)
    x = noise(1.0)
    t = tt(1.0)
    out = np.zeros(n)
    seg = 800
    for i in range(0, n, seg):
        f = 300 + 2500 * (i / n)
        out[i:i + seg] = bp(x[i:i + seg + 0], f, f * 1.8, 1)[:len(out[i:i + seg])]
    e = np.sin(np.pi * t) ** 2
    out = norm(lp(out * e, 4000)) * 0.6
    return out[::-1].copy() if rev else out

def sfx_heartbeat(d):
    n = int(5.0 * SR)
    out = np.zeros(n)
    beat = np.sin(2 * np.pi * 55 * tt(0.18)) * env_ad(int(0.18 * SR), 0.005, 0.05)
    for k in range(4):
        for off, g in ((0, 1.0), (0.28, 0.7)):
            i = int((k * 1.0 + off) * SR)
            out[i:i + len(beat)] += beat * g * (0.6 + 0.1 * k)
    return norm(lp(out, 200)) * 0.9

def sfx_engine(d, interior=False):
    t = tt(d)
    f = 48 + 3 * np.sin(2 * np.pi * 0.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.3 + np.sin(ph * 2) * 0.4
    x += lp(noise(d), 500) * 0.5
    x = lp(x, 260 if interior else 600)
    return norm(x) * (0.45 if interior else 0.6)

def sfx_wind(d):
    x = lp(noise(d), 700)
    t = tt(d)
    m = 0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
    x = bp(noise(d), 200, 900) * m
    return norm(x) * 0.35

def sfx_crows(d):
    out = np.zeros(int(3.5 * SR))
    for k, st in enumerate((0.2, 0.7, 2.0)):
        t = tt(0.35)
        f = 700 + 150 * np.sin(2 * np.pi * 30 * t)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * env_ad(len(t), 0.02, 0.12)
        x = bp(x, 600, 2500)
        i = int(st * SR)
        out[i:i + len(x)] += x
    return norm(out) * 0.3

def sfx_water(d):
    t = tt(d)
    x = lp(noise(d), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t) ** 2)
    return norm(x) * 0.3

def sfx_gravel(d):
    n = int(min(d, 5) * SR)
    out = np.zeros(n)
    for k in range(int(n / SR * 60)):
        i = rng.integers(0, n - 800)
        out[i:i + 800] += hp(noise(800 / SR), 1500) * env_ad(800, 0.001, 0.006) * rng.uniform(.3, 1)
    return norm(lp(out, 6000)) * 0.45

def sfx_creak(d):
    t = tt(1.6)
    f = 140 + 60 * np.sin(2 * np.pi * 0.7 * t) + 20 * rng.standard_normal(len(t)).cumsum() / 3000
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(ph)) * 0.5 + np.sin(ph * 3) * 0.5) * (0.5 + 0.5 * (np.sin(2 * np.pi * 9 * t) > 0.3))
    x = bp(x, 300, 2500) * np.sin(np.pi * t / 1.6)
    return norm(x) * 0.35

def sfx_door_open(d):
    return sfx_creak(d)

def sfx_door_slam(d):
    x = boom(0.8, 80) + hp(noise(0.8), 2000) * env_ad(int(0.8 * SR), 0.001, 0.02)
    return norm(x) * 0.6

def click(g=0.5):
    return hp(noise(0.03), 2000) * env_ad(int(0.03 * SR), 0.0005, 0.005) * g

def sfx_clock(d):
    n = int(min(d, 6) * SR)
    out = np.zeros(n)
    for k in range(int(n / SR)):
        c = click(0.5)
        i = int(k * SR)
        out[i:i + len(c)] += c
    return norm(out) * 0.4

def sfx_clock_beep(d):
    out = np.zeros(int(2.5 * SR))
    b = np.sin(2 * np.pi * 2000 * tt(0.09)) * 0.5
    for k in range(4):
        for j in range(2):
            i = int((k * 0.6 + j * 0.15) * SR)
            out[i:i + len(b)] += b
    return out * 0.5

def ping(f, d=0.6):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 9)

def sfx_cutlery(d):
    out = np.zeros(int(min(d, 6) * SR) + SR)
    for k in range(10):
        p = ping(rng.uniform(2500, 4500), 0.4) * rng.uniform(.2, .5)
        i = rng.integers(0, len(out) - len(p))
        out[i:i + len(p)] += p
    return out * 0.25

def sfx_plates(d):
    out = np.zeros(int(4 * SR))
    for k in range(4):
        p = ping(1800 + k * 120, 0.5) * 0.4
        i = int(k * 0.7 * SR)
        out[i:i + len(p)] += p
    return out * 0.4

def sfx_page(d, fast=False):
    n = int((2.5 if fast else 0.6) * SR)
    out = np.zeros(n)
    count = 6 if fast else 1
    for k in range(count):
        x = bp(noise(0.35), 1500, 7000) * np.sin(np.pi * tt(0.35) / 0.35) ** 2
        i = int(k * 0.4 * SR)
        out[i:i + len(x)] += x
    return norm(out) * 0.35

def sfx_shutter(d):
    out = np.zeros(int(0.5 * SR))
    for st in (0, 0.08):
        c = click(1.0)
        i = int(st * SR)
        out[i:i + len(c)] += c
    return norm(out) * 0.5

def sfx_pencil(d):
    n = int(min(d, 4) * SR)
    x = bp(noise(n / SR), 2000, 8000) * (0.4 + 0.6 * (np.sin(2 * np.pi * 3 * tt(n / SR)) > 0))
    return norm(x) * 0.12

def sfx_fridge(d):
    t = tt(d)
    x = np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t) + 0.2 * np.sin(2 * np.pi * 180 * t)
    return x / 1.7 * 0.35 * np.minimum(1, t / 0.5)

def sfx_tv(d, loud=False):
    t = tt(d)
    x = bp(noise(d), 300, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t) ** 2)
    x = norm(x)
    if loud:
        x *= 0.15 + 0.85 * np.minimum(1, t / max(1, d * 0.85))
        return x * 0.6
    return x * 0.12

def sfx_footsteps(d):
    out = np.zeros(int(min(d, 3) * SR) + SR)
    st = boom(0.25, 90) * 0.5
    for k in range(int(min(d, 3) / 0.4)):
        i = int(k * 0.4 * SR)
        out[i:i + len(st)] += st
    return out * 0.6

def drip_one():
    t = tt(0.08)
    f = 1400 * np.exp(-t * 18) + 500
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)

def sfx_drip(d):
    return drip_one() * 0.5

def sfx_drip_loop(d):
    n = int(d * SR)
    out = np.zeros(n + SR)
    k = 0.0
    while k < d:
        dd = drip_one()
        i = int(k * SR)
        out[i:i + len(dd)] += dd * 0.45
        k += 0.95
    return out

def sfx_laugh(d):
    out = np.zeros(int(2.5 * SR))
    for k in range(5):
        t = tt(0.16)
        x = (np.sin(2 * np.pi * 260 * t) + 0.5 * np.sin(2 * np.pi * 780 * t) + 0.3 * noise(0.16)) * np.sin(np.pi * t / 0.16)
        i = int((0.3 + k * 0.22) * SR)
        out[i:i + len(x)] += x
    return norm(lp(out, 900)) * 0.25

def sfx_whisper(d):
    n = int(min(d, 4) * SR)
    t = tt(n / SR)
    x = bp(noise(n / SR), 1500, 6000) * (np.sin(2 * np.pi * 2.3 * t) > 0) * 0.5
    return norm(x) * 0.12

def sfx_lamp_click(d):
    return click(1.0) * 0.6

def sfx_scratch(d):
    n = int(1.5 * SR)
    out = np.zeros(n)
    for k in range(5):
        x = bp(noise(0.2), 1800, 6000) * np.sin(np.pi * tt(0.2) / 0.2)
        i = int(k * 0.25 * SR)
        out[i:i + len(x)] += x
    return norm(out) * 0.4

def sfx_birds(d):
    out = np.zeros(int(4 * SR))
    for k in range(6):
        t = tt(0.25)
        f = 3000 + 1500 * np.sin(2 * np.pi * 14 * t)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.25)
        i = int(rng.uniform(0, 3.5) * SR)
        out[i:i + len(x)] += x
    return out * 0.08

def sfx_sizzle(d):
    n = int(min(d, 8) * SR)
    x = hp(noise(n / SR), 3000) * (rng.random(n) > 0.7)
    return norm(x) * 0.08

def sfx_hum(d):
    notes = [392, 440, 392, 349, 330, 349, 392, 0, 330, 349, 392, 440, 392]
    out = np.zeros(int(len(notes) * 0.45 * SR) + SR)
    for k, f in enumerate(notes):
        if not f:
            continue
        t = tt(0.45)
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.sin(np.pi * t / 0.45)
        i = int(k * 0.45 * SR)
        out[i:i + len(x)] += x
    return lp(out, 1500) * 0.08

def sfx_wrench(d):
    out = np.zeros(int(3 * SR))
    for k in range(4):
        p = ping(rng.uniform(1200, 2200), 0.3) * 0.4
        i = int((0.2 + k * 0.6) * SR)
        out[i:i + len(p)] += p
    return out * 0.4

def sfx_thud(d):
    return boom(0.6, 70) * 0.5

def sfx_hit(d):
    return norm(boom(0.8, 60) + lp(noise(0.8), 1500) * env_ad(int(0.8 * SR), 0.001, 0.05)) * 0.6

def sfx_mower(d):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(95 + 5 * np.sin(2 * np.pi * 3 * t)) / SR
    x = np.sign(np.sin(ph)) * 0.6 + np.sin(2 * ph) * 0.3
    return norm(lp(x, 1200)) * 0.3

def sfx_splash(d, small=False):
    n = int(2.0 * SR)
    x = lp(noise(2.0), 2500) * env_ad(n, 0.005, 0.25)
    for k in range(10):
        b = np.sin(2 * np.pi * np.cumsum(rng.uniform(400, 900) * (1 + tt(0.06) * 8)) / SR) * env_ad(int(0.06 * SR), 0.002, 0.02)
        i = rng.integers(int(0.1 * SR), int(1.4 * SR))
        x[i:i + len(b)] += b * 0.5
    return norm(x) * (0.35 if small else 0.7)

def sfx_siren(d):
    t = tt(d)
    f = 850 + 250 * np.sin(2 * np.pi * 0.5 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return lp(x, 2000) * 0.15

def sfx_flatline(d):
    t = tt(d)
    flat = d * 0.55
    beep = ((t % (1 / 1.4)) < 0.1) & (t < flat)
    x = np.sin(2 * np.pi * 1000 * t) * (beep | (t >= flat + 0.3))
    return x * 0.18

def sfx_bell(d):
    t = tt(6)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, a, dcy in ((220, 1, .5), (440, .6, .8), (528, .4, 1.0), (660, .3, 1.3), (880, .2, 1.6)))
    out = np.zeros(int(8 * SR))
    out[:len(x)] += x
    out[int(3 * SR):int(3 * SR) + len(x) - int(1 * SR)] += x[:len(x) - int(1 * SR)] * 0.8
    return norm(out) * 0.35

def sfx_scissors(d):
    out = np.zeros(int(2 * SR))
    for k in range(3):
        c = np.concatenate([click(0.8), np.zeros(int(0.05 * SR)), click(0.6)])
        i = int(k * 0.45 * SR)
        out[i:i + len(c)] += c
    return out * 0.6

def sfx_fire(d):
    n = int(d * SR)
    x = lp(noise(d), 800) * 0.5
    pops = np.zeros(n)
    for k in range(int(d * 12)):
        i = rng.integers(0, n - 400)
        pops[i:i + 400] += hp(noise(400 / SR), 1500) * env_ad(400, 0.0005, 0.004) * rng.uniform(.3, 1)
    return norm(x + pops) * 0.35

def sfx_static(d):
    return hp(noise(d), 500) * 0.06

def sfx_radio_music(d):
    t = tt(d)
    chords = [(261, 329, 392), (220, 261, 329), (174, 220, 261), (196, 246, 293)]
    x = np.zeros(len(t))
    for k, ch in enumerate(chords * 4):
        i0 = int(k * 1.6 * SR)
        if i0 >= len(t):
            break
        seg = tt(1.6)[: len(t) - i0]
        x[i0:i0 + len(seg)] += sum(np.sin(2 * np.pi * f * seg) for f in ch) * np.exp(-seg * 1.2)
    return norm(bp(x, 300, 2500)) * 0.12

def sfx_turn_signal(d):
    out = np.zeros(int(min(d, 5) * SR) + SR)
    for k in range(int(min(d, 5) / 0.5)):
        c = click(0.7)
        i = int(k * 0.5 * SR)
        out[i:i + len(c)] += c
    return out * 0.5

def sfx_seat(d):
    x = bp(noise(1.2), 300, 2000) * np.sin(np.pi * tt(1.2) / 1.2)
    return norm(x) * 0.2

def sfx_buckle(d):
    return np.concatenate([click(1.0), np.zeros(int(0.1 * SR)), click(0.8)]) * 0.6

def sfx_notify(d):
    out = np.zeros(int(0.8 * SR))
    for k, f in enumerate((1320, 1760)):
        p = ping(f, 0.4) * 0.5
        i = int(k * 0.12 * SR)
        out[i:i + len(p)] += p
    return out * 0.5

def babble(d, f0=380, cry=False, n=6):
    out = np.zeros(int(d * SR) + SR)
    tpos = 0.1
    for k in range(n):
        L = rng.uniform(0.25, 0.6) if cry else rng.uniform(0.12, 0.25)
        t = tt(L)
        f = f0 * (1 + (0.25 if cry else 0.15) * np.sin(np.pi * t / L)) * (1 + 0.02 * np.sin(2 * np.pi * 7 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph) + 0.25 * np.sin(4 * ph)
        x = bp(x, 500, 3500) * np.sin(np.pi * t / L) ** 0.7
        i = int(tpos * SR)
        if i + len(x) > len(out):
            break
        out[i:i + len(x)] += x
        tpos += L + rng.uniform(0.08, 0.3)
    return norm(out)

def sfx_giggle(d):
    return babble(2.0, 520, False, 6) * 0.25

def sfx_giggle_evil(d):
    x = babble(2.5, 300, False, 7)
    x2 = babble(2.5, 150, False, 7)
    n = min(len(x), len(x2))
    return norm(x[:n] + x2[:n] * 0.7) * 0.35

def sfx_baby_cry(d):
    return babble(min(d, 6), 450, True, 8) * 0.3

def sfx_mama(d):
    t = tt(0.9)
    out = np.zeros(int(1.2 * SR))
    for k in range(2):
        tt_ = tt(0.3)
        f = 330 * (1 - 0.15 * tt_ / 0.3)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * np.sin(np.pi * tt_ / 0.3)
        x *= (tt_ > 0.05)
        i = int((0.1 + k * 0.35) * SR)
        out[i:i + len(x)] += x
    return norm(bp(out, 250, 2500)) * 0.35

def sfx_ringtone(d):
    out = np.zeros(int(min(d, 5) * SR) + SR)
    mel = [1318, 1046, 1174, 784]
    tpos = 0
    while tpos < min(d, 5) - 0.5:
        for k, f in enumerate(mel):
            p = ping(f, 0.3) * 0.4
            i = int((tpos + k * 0.15) * SR)
            out[i:i + len(p)] += p
        tpos += 1.4
    return out * 0.6

def sfx_breath(d):
    n = int(min(d, 6) * SR)
    t = tt(n / SR)
    x = lp(noise(n / SR), 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t)) ** 2
    return norm(x) * 0.25

def sfx_hangup(d):
    return np.concatenate([click(1.0), np.zeros(int(0.1 * SR)), ping(600, 0.2) * 0.2])

def sfx_wet_steps(d):
    out = np.zeros(int(min(d, 4) * SR) + SR)
    for k in range(int(min(d, 4) / 0.35)):
        x = lp(noise(0.08), 1500) * env_ad(int(0.08 * SR), 0.002, 0.02)
        i = int(k * 0.35 * SR)
        out[i:i + len(x)] += norm(x) * 0.5
    return out * 0.7

def sfx_lullaby(d):
    notes = [659, 587, 523, 587, 659, 659, 659, 0, 587, 587, 587, 0, 659, 784, 784, 0]
    out = np.zeros(int(min(d, 10) * SR) + SR)
    tpos = 0
    k = 0
    while tpos < min(d, 10) - 0.5:
        f = notes[k % len(notes)]
        if f:
            t = tt(0.5)
            x = (np.sin(2 * np.pi * f * 0.5 * t) + 0.3 * np.sin(2 * np.pi * f * t)) * np.sin(np.pi * t / 0.5)
            i = int(tpos * SR)
            out[i:i + len(x)] += x
        tpos += 0.5
        k += 1
    return lp(out, 1200) * 0.12

def knock_one():
    return norm(boom(0.25, 110) * 0.7 + lp(noise(0.25), 1200) * env_ad(int(0.25 * SR), 0.001, 0.02)) * 0.7

def sfx_knock3(d):
    out = np.zeros(int(2 * SR))
    for k, tpos in enumerate((0.25, 0.85, 1.45)):
        x = knock_one()
        i = int(tpos * SR)
        out[i:i + len(x)] += x
    return out

def sfx_knock_around(d):
    out = np.zeros(int(d * SR) + SR)
    tpos = 0.3
    g = 1.0
    while tpos < d - 0.5:
        for j in range(3):
            x = knock_one() * g
            i = int((tpos + j * 0.3) * SR)
            out[i:i + len(x)] += lp(x, 600 + 1500 * g)
        tpos += 1.8
        g = 0.4 + 0.6 * abs(math.sin(tpos))
    return out

def sfx_cash(d):
    out = np.zeros(int(3 * SR))
    for k in range(10):
        x = bp(noise(0.08), 2000, 7000) * env_ad(int(0.08 * SR), 0.003, 0.03)
        i = int(k * 0.22 * SR)
        out[i:i + len(x)] += x
    return norm(out) * 0.25

def sfx_keys(d):
    out = np.zeros(int(2 * SR))
    for k in range(8):
        p = ping(rng.uniform(3000, 5000), 0.2) * 0.3
        i = int(rng.uniform(0, 0.8) * SR)
        out[i:i + len(p)] += p
    c_ = click(1.0)
    out[int(1.0 * SR):int(1.0 * SR) + len(c_)] += c_
    return out * 0.5

def sfx_scratch_door(d):
    n = int(min(d, 5) * SR)
    out = np.zeros(n + SR)
    k = 0.1
    while k < min(d, 5) - 0.3:
        x = bp(noise(0.18), 1200, 6000) * np.sin(np.pi * tt(0.18) / 0.18)
        i = int(k * SR)
        out[i:i + len(x)] += x
        k += 0.28
    return norm(out) * 0.35

def sfx_whine(d):
    t = tt(1.6)
    f = 900 + 250 * np.sin(np.pi * t / 1.6) - 200 * t
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 1.6) ** 0.5
    return lp(x, 2500) * 0.18

def sfx_bark(d):
    out = np.zeros(int(1.5 * SR))
    for st in (0.05, 0.45):
        t = tt(0.16)
        f = 420 * (1 - 0.4 * t / 0.16)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + 0.5 * noise(0.16)
        x = bp(x, 300, 2500) * env_ad(len(t), 0.005, 0.05)
        i = int(st * SR)
        out[i:i + len(x)] += x
    return norm(out) * 0.45

def sfx_card(d):
    n = int(1.2 * SR)
    x = boom(1.2, 55)[:n] * 0.8
    h = bp(noise(0.25), 1000, 6000) * env_ad(int(0.25 * SR), 0.002, 0.06)
    x[:len(h)] += h
    return norm(x) * 0.55

def sfx_crickets(d):
    n = int(d * SR)
    t = tt(d)
    x = np.sin(2 * np.pi * 4400 * t) * (np.sin(2 * np.pi * 30 * t) > 0.6) * (np.sin(2 * np.pi * 0.9 * t) > 0)
    return x * 0.025

def sfx_curtain(d, fast=False):
    L = 0.4 if fast else 1.0
    x = bp(noise(L), 800, 5000) * np.sin(np.pi * tt(L) / L)
    out = norm(x) * 0.25
    ring = ping(2500, 0.3) * 0.15
    out[:len(ring)] += ring
    return out

def sfx_tap1(d):
    x = knock_one() * 0.6
    return lp(x, 3000)

def sfx_tap_round(d):
    out = np.zeros(int(min(d, 8) * SR) + SR)
    k = 0.3
    while k < min(d, 8) - 0.2:
        x = lp(knock_one(), 2500) * 0.4
        i = int(k * SR)
        out[i:i + len(x)] += x
        k += 1.3
    return out

def sfx_tap_rain(d):
    n = int(d * SR)
    out = np.zeros(n + SR)
    for k in range(int(d * 14)):
        x = lp(knock_one(), rng.uniform(1500, 4000)) * rng.uniform(.05, .2)
        i = rng.integers(0, n)
        out[i:i + len(x)] += x[: len(out) - i]
    return out[:n]

def sfx_typing(d):
    out = np.zeros(int(1.5 * SR))
    for k in range(10):
        c = click(0.4)
        i = int(k * 0.12 * SR)
        out[i:i + len(c)] += c
    return out * 0.6

def sfx_heavy_steps(d):
    out = np.zeros(int(min(d, 6) * SR) + SR)
    for k in range(int(min(d, 6) / 0.9)):
        x = boom(0.5, 45) * 0.7 + lp(noise(0.5), 300) * env_ad(int(0.5 * SR), 0.002, 0.05) * 0.4
        i = int(k * 0.9 * SR)
        out[i:i + len(x)] += x
    return out * 0.7

def sfx_scrape(d):
    n = int(d * SR)
    t = tt(d)
    x = bp(noise(d), 800, 4000) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    x += np.sin(2 * np.pi * (300 + 40 * np.sin(2 * np.pi * 0.3 * t)) * t) * 0.15
    return norm(x) * 0.22

def sfx_step(d):
    out = np.zeros(int(min(d, 8) * SR) + SR)
    k = 0.2
    while k < min(d, 8) - 0.3:
        x = boom(0.3, 80) * 0.4
        cr = sfx_creak(1)[: int(0.4 * SR)] * 0.25 if rng.random() < 0.25 else np.zeros(1)
        i = int(k * SR)
        out[i:i + len(x)] += x
        out[i:i + len(cr)] += cr
        k += 0.75
    return out

def ring_burst():
    t = tt(1.0)
    x = (np.sin(2 * np.pi * 1300 * t) + np.sin(2 * np.pi * 1700 * t)) * (np.sin(2 * np.pi * 20 * t) > 0)
    return x * np.minimum(1, (1 - t) * 8) * 0.12

def sfx_ring_old(d):
    return ring_burst()

def sfx_ring_seq(d):
    out = np.zeros(int(min(d, 10) * SR) + 2 * SR)
    n = 4
    step = max(1.0, min(d, 10) / 5)
    for k in range(n):
        x = ring_burst()
        i = int((0.6 + k * step) * SR)
        out[i:i + len(x)] += x
    return out

def sfx_pickup(d):
    return np.concatenate([click(1.0), np.zeros(int(0.05 * SR)), click(0.6)]) * 0.6

def sfx_furnace(d):
    t = tt(d)
    x = lp(noise(d), 200) * 0.8 + np.sin(2 * np.pi * 50 * t) * 0.3
    return norm(x) * 0.45 * np.minimum(1, t / 0.5)

def sfx_groan(d):
    t = tt(4)
    f = 70 + 15 * np.sin(2 * np.pi * 0.3 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / 4)
    return lp(x, 400) * 0.25

def sfx_cuckoo(d, loop=False):
    out = np.zeros(int((min(d, 8) if loop else 1.5) * SR) + SR)
    k = 0.1
    while True:
        for f, st in ((740, 0), (587, 0.28)):
            t = tt(0.25)
            x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.sin(np.pi * t / 0.25)
            i = int((k + st) * SR)
            if i + len(x) < len(out):
                out[i:i + len(x)] += x
        k += 0.9
        if not loop or k > min(d, 8) - 0.6:
            break
    return out * 0.18

def sfx_alarm(d):
    out = np.zeros(int(2.5 * SR))
    b = np.sin(2 * np.pi * 1800 * tt(0.1)) * 0.4
    for k in range(8):
        i = int(k * 0.25 * SR)
        out[i:i + len(b)] += b
    return out * 0.5

def sfx_pipe_knock(d):
    out = np.zeros(int(2 * SR))
    for st in (0.3, 0.9):
        x = ping(160, 0.6) * 0.5
        bb = boom(0.4, 90) * 0.3
        x[:len(bb)] += bb[:len(x)]
        i = int(st * SR)
        out[i:i + len(x)] += x[: len(out) - i]
    return out * 0.6

def sfx_paper(d):
    x = bp(noise(0.7), 1000, 7000) * np.sin(np.pi * tt(0.7) / 0.7) ** 2
    return norm(x) * 0.2

def sfx_flicker2(d):
    out = np.zeros(int(2 * SR))
    for st in (0.6, 1.1):
        x = np.sin(2 * np.pi * 120 * tt(0.15)) * 0.2 + click(0.6)[:1].sum() * 0
        i = int(st * SR)
        out[i:i + len(x)] += x
    return out

SFX = {
    "drone_hit": sfx_drone_hit, "sting_big": sfx_sting_big, "sting_soft": sfx_sting_soft,
    "whoosh": sfx_whoosh, "whoosh_rev": lambda d: sfx_whoosh(d, True), "heartbeat": sfx_heartbeat,
    "car": sfx_engine, "car_in": lambda d: sfx_engine(d, True), "wind": sfx_wind, "crows": sfx_crows,
    "water": sfx_water, "gravel": sfx_gravel, "creak": sfx_creak, "door_open": sfx_door_open,
    "door_slam": sfx_door_slam, "clock": sfx_clock, "clock_beep": sfx_clock_beep, "cutlery": sfx_cutlery,
    "plates": sfx_plates, "page": sfx_page, "page_fast": lambda d: sfx_page(d, True), "shutter": sfx_shutter,
    "pencil": sfx_pencil, "fridge": sfx_fridge, "tv_low": sfx_tv, "tv_loud": lambda d: sfx_tv(d, True),
    "footsteps": sfx_footsteps, "drip": sfx_drip, "drip_loop": sfx_drip_loop, "laugh_muffled": sfx_laugh,
    "whisper": sfx_whisper, "lamp_click": sfx_lamp_click, "scratch": sfx_scratch, "birds": sfx_birds,
    "sizzle": sfx_sizzle, "hum": sfx_hum, "wrench": sfx_wrench, "thud": sfx_thud, "hit": sfx_hit,
    "mower": sfx_mower, "splash": sfx_splash, "splash_small": lambda d: sfx_splash(d, True), "siren": sfx_siren,
    "flatline": sfx_flatline, "bell": sfx_bell, "scissors": sfx_scissors, "fire": sfx_fire,
    "static": sfx_static, "radio_static": sfx_static, "radio_music": sfx_radio_music,
    "turn_signal": sfx_turn_signal, "seat": sfx_seat, "buckle": sfx_buckle,
    "kids": lambda d: np.zeros(10), "musicbox": lambda d: np.zeros(10), "silence": lambda d: np.zeros(10),
    "tv": sfx_tv, "notify": sfx_notify, "giggle": sfx_giggle, "giggle_evil": sfx_giggle_evil, "baby_cry": sfx_baby_cry,
    "mama": sfx_mama, "ringtone": sfx_ringtone, "breath": sfx_breath, "hangup": sfx_hangup, "wet_steps": sfx_wet_steps,
    "lullaby": sfx_lullaby, "scratch_door": sfx_scratch_door, "whine": sfx_whine, "bark": sfx_bark, "card": sfx_card,
    "crickets": sfx_crickets, "curtain": sfx_curtain, "curtain_fast": lambda d: sfx_curtain(d, True), "tap1": sfx_tap1,
    "tap_round": sfx_tap_round, "tap_rain": sfx_tap_rain, "typing": sfx_typing, "heavy_steps": sfx_heavy_steps,
    "scrape": sfx_scrape, "step": sfx_step, "ring_old": sfx_ring_old, "ring_seq": sfx_ring_seq, "pickup": sfx_pickup,
    "furnace": sfx_furnace, "groan": sfx_groan, "cuckoo": sfx_cuckoo, "cuckoo_loop": lambda d: sfx_cuckoo(d, True),
    "furnace_off": lambda d: sfx_furnace(1.5)[::-1].copy(), "alarm": sfx_alarm, "pipe_knock": sfx_pipe_knock,
    "paper": sfx_paper, "flicker2": sfx_flicker2, "knock3": sfx_knock3, "knock_around": sfx_knock_around, "cash": sfx_cash, "keys": sfx_keys,
}
SUSTAINED = {"car", "car_in", "wind", "water", "fridge", "tv_low", "tv_loud", "drip_loop", "static", "radio_static",
             "radio_music", "siren", "flatline", "mower", "fire", "sizzle", "pencil", "whisper", "knock_around", "breath", "lullaby", "crickets", "scrape", "tap_rain", "furnace"}

sfx_bus = np.zeros(N + 10 * SR)
for s in shots:
    d = s["t1"] - s["t0"]
    for name in s["spec"].get("sfx", []):
        x = SFX[name](d)
        if name in SUSTAINED:
            x = x[: int(d * SR)].copy()
            fo = min(len(x), int(0.4 * SR))
            x[-fo:] *= np.linspace(1, 0, fo)
            fi = min(len(x), int(0.15 * SR))
            x[:fi] *= np.linspace(0, 1, fi)
        i = int(s["t0"] * SR)
        sfx_bus[i:i + len(x)] += x
    # subtle transition whoosh on hard flashes
    if s["spec"].get("trans") == "flash":
        x = sfx_whoosh(1, True)
        i = max(0, int((s["t0"] - 0.9) * SR))
        sfx_bus[i:i + len(x)] += x * 0.6
sfx_bus = sfx_bus[:N]

# ------------------------------------------------------------ music
mood = np.zeros(N, np.float32)
cur = 0
for s in shots:
    if s["spec"].get("mood") is not None:
        cur = s["spec"]["mood"]
    mood[int(s["t0"] * SR):int(s["t1"] * SR)] = cur
t = np.arange(N, dtype=np.float32) / SR

def smooth_mask(cond, secs=2.5):
    m = cond.astype(np.float32)
    k = int(secs * SR / 64)
    ds = m[::64]
    ker = np.ones(k) / k
    ds = np.convolve(ds, ker, mode="same")
    return np.interp(np.arange(N), np.arange(len(ds)) * 64, ds).astype(np.float32)

music = np.zeros(N, np.float32)
# 1. base drone (always), louder when tense
tense = smooth_mask(mood >= 2, 3)
calm = smooth_mask(mood == 0, 3)
sad = smooth_mask(mood == 4, 3)
scare = smooth_mask(mood == 3, 1.5)
endm = smooth_mask(mood == 5, 2)
lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
drone = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 55.4 * t) * 0.4 + np.sin(2 * np.pi * 82.4 * t) * 0.25
         + np.sin(2 * np.pi * 110.3 * t) * 0.15 + np.sin(2 * np.pi * 130.8 * t) * 0.12 * (1 - calm))
music += drone * lfo * (0.10 + 0.08 * tense + 0.06 * scare)
# airy pad for calm
pad = (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 261.6 * t) * .8 + np.sin(2 * np.pi * 329.6 * t) * .6) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t))
music += pad * 0.025 * calm
# dissonant high strings with tremolo (tense)
trem = 0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)
hi = (np.sin(2 * np.pi * 880 * t + 0.3 * np.sin(2 * np.pi * 5 * t)) + np.sin(2 * np.pi * 932.3 * t) * .8 + np.sin(2 * np.pi * 1318.5 * t) * .4)
music += hi * trem * 0.018 * (tense + scare)
# low pulsing for scare
pulse = np.sin(2 * np.pi * 41 * t) * (np.sin(2 * np.pi * 1.4 * t) > 0.6)
music += lp(pulse, 120).astype(np.float32) * 0.12 * scare
# music box melody (sad / flashback / end) + soft piano notes in other moods
def bell_note(f, d=1.6):
    tn = np.arange(int(d * SR)) / SR
    return ((np.sin(2 * np.pi * f * tn) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tn) + 0.15 * np.sin(2 * np.pi * f * 3.01 * tn)) * np.exp(-tn * 3.0)).astype(np.float32)
melody = [880, 1046.5, 987.8, 880, 659.3, 698.5, 659.3, 587.3, 523.3, 587.3, 659.3, 0, 880, 1046.5, 1174.7, 1046.5, 987.8, 880, 830.6, 880, 0, 0]
mb = np.zeros(N, np.float32)
step = 0.42
k = 0
tpos = 0.0
while tpos < TOTAL - 2:
    f = melody[k % len(melody)]
    if f:
        x = bell_note(f)
        i = int(tpos * SR)
        mb[i:i + len(x)] += x[: len(mb[i:i + len(x)])]
    k += 1
    tpos += step
music += mb * 0.05 * np.clip(sad + endm, 0, 1)
pn = np.zeros(N, np.float32)
notes = [220, 261.6, 329.6, 246.9, 196, 174.6, 164.8]
tpos = 1.0
k = 0
while tpos < TOTAL - 2:
    x = bell_note(notes[(k * 3) % len(notes)] / 2, 3.0)
    i = int(tpos * SR)
    pn[i:i + len(x)] += x[: len(pn[i:i + len(x)])]
    k += 1
    tpos += 2.9
music += pn * 0.07 * (1 - np.clip(sad + endm, 0, 1))
# room tone / air
music += lp(rng.standard_normal(N), 400).astype(np.float32) * 0.015

# ------------------------------------------------------------ reverb on bed
ir_t = np.arange(int(2.2 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.0)
ir = lp(ir, 3500)
ir /= np.sqrt(np.sum(ir ** 2))
bed = music + sfx_bus.astype(np.float32)
wet = oaconvolve(bed, ir)[:N]
bed = bed * 0.8 + wet * 0.35

# ------------------------------------------------------------ narration + ducking
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "narration.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
nar = np.frombuffer(raw, np.float32)
narr = np.zeros(N, np.float32)
narr[: min(N, len(nar))] = nar[:N]
narr = narr / (np.max(np.abs(narr)) + 1e-9) * 0.9
envn = np.abs(narr)
envn = smooth_mask(envn > 0.03, 0.6)
music_duck = 1 - 0.3 * envn
bed = bed * music_duck
# level bed relative to narration
rms_n = np.sqrt(np.mean(narr[narr != 0] ** 2))
rms_b = np.sqrt(np.mean(bed ** 2))
bed = bed * (rms_n * 0.26 / rms_b)
mix = narr + bed
# fade end
fo = int(3 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
st = np.stack([mix, mix], 1)
# slight stereo width for the bed
st[:, 0] += 0.0
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
import wave
with wave.open("final_audio_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("audio done", TOTAL)
