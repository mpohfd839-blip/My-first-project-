"""Synthesize horror music bed + SFX, mix with narration -> final_audio.wav"""
import json, math, subprocess
import numpy as np
from scipy.signal import oaconvolve, butter, sosfilt
from story import SHOTS

SR = 32000
TL = json.load(open("timeline.json"))
DUR = TL["duration"]
END_EXTRA = 9.0
TOTAL = DUR + END_EXTRA
N = int(TOTAL * SR)
rng = np.random.default_rng(1)

# shot times (same logic as render.py)
shots = []
for i, (spec, lines) in enumerate(SHOTS):
    shots.append(dict(spec=spec, sents=TL["timeline"][i]["sentences"]))
for i, s in enumerate(shots):
    s["t0"] = max(0.0, s["sents"][0]["start"] - 0.25) if s["sents"] else shots[i - 1]["sents"][-1]["end"] + 0.6
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
    "tv": sfx_tv,
}
SUSTAINED = {"car", "car_in", "wind", "water", "fridge", "tv_low", "tv_loud", "drip_loop", "static", "radio_static",
             "radio_music", "siren", "flatline", "mower", "fire", "sizzle", "pencil", "whisper"}

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
