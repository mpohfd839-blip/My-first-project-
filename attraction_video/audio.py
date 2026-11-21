"""Self-made ambient synth score + SFX, mixed under the narration -> final_audio.m4a"""
import math, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt, oaconvolve
import render as R

SR = 44100
TOTAL = R.TOTAL
N = int(TOTAL * SR)
rng = np.random.default_rng(7)


def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def noise(d): return rng.standard_normal(int(d * SR))
def norm(x, p=1.0): return x / (np.max(np.abs(x)) + 1e-9) * p


def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i < 0:
        x = x[-i:]; i = 0
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n] * g


def adsr(n, a, r):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-3))
    return e * np.clip((n / SR - t) / max(r, 1e-3), 0, 1)


def mx(*xs):
    n = max(len(x) for x in xs); out = np.zeros(n)
    for x in xs: out[:len(x)] += x
    return out


def midi(m): return 440 * 2 ** ((m - 69) / 12)


def pad(notes, d, bright=1400, amp=1.0):
    t = tt(d); out = np.zeros(len(t))
    for m in notes:
        f = midi(m)
        for det in (-0.006, 0.0, 0.007):
            ph = f * (1 + det) * t + rng.random()
            out += 2 * (ph - np.floor(ph + .5)) * 0.18
    out = lp(out, bright, 2)
    out *= 1 + 0.12 * np.sin(2 * np.pi * 0.25 * t)
    return out * adsr(len(t), 1.2, 1.4) * amp


def bell(m, d=2.5, amp=1.0):
    t = tt(d); f = midi(m)
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 1.6 * np.exp(-t * 3)
    x = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 2.2) + 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
    return x * adsr(len(t), 0.004, 0.2) * amp


def pluck(m, d=0.6, amp=1.0):
    t = tt(d); f = midi(m)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) + .25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 7)
    return x * adsr(len(t), .003, .05) * amp


def sub(m, d, amp=1.0):
    t = tt(d)
    return np.sin(2 * np.pi * midi(m) * t) * adsr(len(t), 0.05, 0.3) * amp


def kick(amp=1.0):
    t = tt(.45)
    return np.sin(2 * np.pi * np.cumsum(50 * (1 + 2.5 * np.exp(-t * 30))) / SR) * np.exp(-t * 8) * amp


def hat(amp=1.0):
    return hp(noise(.06), 7000) * np.exp(-tt(.06) * 70) * amp


# chord progressions (root-position voicings as midi notes) per mood
P = {
    0: [[57, 64, 67, 71], [53, 60, 64, 67], [55, 62, 67, 71], [52, 59, 64, 67]],        # Am9 F G Em  (mysterious)
    1: [[53, 60, 64, 69], [55, 62, 67, 71], [57, 64, 69, 72], [48, 55, 64, 67]],        # F(lyd) G Am C (wonder)
    2: [[48, 55, 64, 67], [57, 64, 69, 72], [53, 60, 65, 69], [55, 62, 67, 71]],        # C Am F G (playful)
    3: [[50, 57, 65, 69], [46, 53, 62, 69], [55, 62, 67, 70], [57, 64, 69, 73]],        # Dm9 Bbmaj7 Gm A (mystery)
    4: [[52, 59, 64, 67], [48, 55, 64, 67], [55, 62, 67, 71], [50, 57, 62, 66]],        # Em C G D (energy)
    5: [[52, 59, 64, 71], [48, 55, 64, 71], [55, 62, 67, 74], [50, 57, 66, 69]],        # brighter
    6: [[50, 57, 62, 66], [47, 54, 62, 66], [55, 62, 67, 71], [57, 64, 69, 73]],        # D Bm G A (warm)
    7: [[53, 60, 65, 69], [52, 60, 64, 67], [50, 57, 65, 69], [46, 53, 62, 65]],        # F C/E Dm Bb (hopeful)
}
moods = []
cur = 0
for s in R.SEG:
    m = R.SPECS[s["i"]].get("mood")
    if m is not None:
        cur = m
    moods.append((s["start"], s["end"], cur))

music = np.zeros(N)
BEAT = 60 / 92
BAR = BEAT * 4
tpos, bi = 0.0, 0
while tpos < TOTAL - 2:
    m = next((mm for a, b, mm in moods if a <= tpos + 0.01 < b), 7)
    ch = P[m][(bi // 2) % 4]
    first = bi % 2 == 0
    if first:
        add(music, pad(ch, BAR * 2 + 1.4, 900 if m in (0, 3) else 1500, .5), tpos)
        add(music, sub(ch[0] - 12, BAR * 2, .55), tpos)
    if m in (0, 3):
        for k in (0, 3, 6):
            add(music, bell(ch[(k + bi) % 4] + 12, 3, .16), tpos + k * BEAT / 2)
    elif m in (1, 7):
        for k in range(8):
            add(music, bell(ch[k % 4] + 12 + (12 if k == 7 else 0), 2.5, .12), tpos + k * BEAT / 2)
    elif m in (2, 6):
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(8):
            add(music, pluck(ch[pat[k]] + 12, .7, .22), tpos + k * BEAT / 2)
        if m == 6:
            add(music, bell(ch[3] + 24, 3, .08), tpos)
    else:  # 4, 5 energy
        for k in range(16):
            add(music, pluck(ch[[0, 1, 2, 3, 2, 1][k % 6]] + 12, .4, .2), tpos + k * BEAT / 4)
        for k in range(4):
            add(music, kick(.55), tpos + k * BEAT)
            add(music, hat(.15), tpos + k * BEAT + BEAT / 2)
        if m == 5:
            add(music, bell(ch[2] + 24, 2, .08), tpos)
    tpos += BAR
    bi += 1
music = norm(music, .8)

# ------------------------------------------------------------------ SFX
def whoosh(d=.8, rev=False, lo=300, hi=4000):
    x = noise(d); t = tt(d); out = np.zeros(len(x))
    for i in range(0, len(x), 1024):
        f = lo + (hi - lo) * (i / len(x))
        out[i:i + 1024] = bp(x[i:i + 1024], f, min(f * 1.8, 18000), 1)
    out = norm(out * np.sin(np.pi * t / d) ** 2, .5)
    return out[::-1].copy() if rev else out


def popsfx(f=600, amp=.6):
    t = tt(.15)
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-t * 40))) / SR) * np.exp(-t * 30) * amp


def chime(m=84, amp=.4):
    return bell(m, 2, amp) + bell(m + 7, 2, amp * .6)


def sparkle(d=1.5):
    out = np.zeros(int(d * SR))
    for k in range(10):
        add(out, bell(rng.integers(84, 100), .6, .12), rng.uniform(0, d - .6))
    return out


def heartbeat(d, bpm=72, amp=.9):
    out = np.zeros(int(d * SR)); p = 60 / bpm
    t = tt(.25)
    thump = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 18)
    k = 0.2
    while k < d - .3:
        add(out, thump, k, amp); add(out, thump, k + .28, amp * .65); k += p
    return lp(out, 200)


def boom(d=2.5, f=42):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + .8 * np.exp(-t * 6))) / SR) * np.exp(-t * 1.6)
    return norm(x + lp(noise(d), 200) * np.exp(-t * 5) * .4)


def riser(d=2.0):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(300 + 1500 * (t / d) ** 2) / SR) * .2 + bp(noise(d), 1500, 9000) * .3
    return norm(x * (t / d) ** 2, .5)


def zap(d=.5):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(2000 * np.exp(-t * 6) + 200) / SR) * np.exp(-t * 5)
    return norm(x + hp(noise(d), 4000) * np.exp(-t * 12) * .3, .5)


def blob():
    t = tt(.35)
    return np.sin(2 * np.pi * np.cumsum(220 + 500 * t / .35) / SR) * np.sin(np.pi * t / .35) * .5


def amb(d, lo, hi, g, mod=0.3):
    x = bp(noise(d), lo, hi) * (1 - mod + mod * np.sin(2 * np.pi * .3 * tt(d)))
    return norm(x, g)


def SFX(name, d):
    D = min(d, 14)
    if name == "city":
        x = amb(D, 200, 2500, .18)
        for k in range(int(D)):
            add(x, bp(noise(.4), 400, 1500) * np.exp(-tt(.4) * 6) * .08, k + rng.random())
        return x
    if name in ("heartbeat", "heartbeat_soft"): return heartbeat(D, 70, .9 if name == "heartbeat" else .5)
    if name == "heartbeat_fast": return heartbeat(D, 120, 1.0)
    if name in ("swell", "pad"): return mx(norm(lp(noise(3), 600) * np.sin(np.pi * tt(3) / 3) ** 2, .25), riser(3) * .4)
    if name in ("shimmer", "sparkle", "magic"): return sparkle(2.0)
    if name == "whisper": return norm(bp(noise(1.5), 2500, 7000) * np.sin(np.pi * tt(1.5) / 1.5) ** 2, .15)
    if name == "zap": return zap()
    if name == "pop": return popsfx(500)
    if name in ("pop3", "pop4"):
        out = np.zeros(int(3 * SR))
        for k in range(3 if name == "pop3" else 4):
            add(out, popsfx(500 + 120 * k), .2 + k * .55)
        return out
    if name == "title": return mx(boom(3) * .7, chime(76, .5))
    if name == "chapter": return mx(whoosh(1.0), chime(81, .35))
    if name == "rewind": return whoosh(1.6, True, 200, 6000)
    if name == "ocean": return amb(D, 150, 900, .25, .5)
    if name == "bubbles":
        out = np.zeros(int(D * SR))
        for k in range(int(D * 3)):
            add(out, popsfx(rng.uniform(700, 1500), .15), rng.uniform(0, D - .2))
        return out
    if name in ("blob", "blob2"): return blob()
    if name == "villain":
        t = tt(2.0)
        return norm(lp(np.sign(np.sin(2 * np.pi * 55 * t)) + np.sign(np.sin(2 * np.pi * 58 * t)), 400) * np.exp(-t * 1.2), .35)
    if name == "crunch": return norm(lp(noise(.4), 2500) * (rng.random(int(.4 * SR)) > .6) * np.exp(-tt(.4) * 8), .4)
    if name == "lock":
        out = np.zeros(int(1.5 * SR)); add(out, hp(noise(.03), 2000) * .6, .3); add(out, hp(noise(.04), 1500) * .7, .45); add(out, chime(88, .25), .55)
        return out
    if name in ("swish",): return whoosh(.6)
    if name == "tick":
        out = np.zeros(int(D * SR))
        for k in np.arange(0, D, .5):
            add(out, hp(noise(.02), 3000) * np.exp(-tt(.02) * 200) * .25, k)
        return out
    if name == "chime": return chime(79)
    if name in ("fire", "fire_big"):
        x = amb(D, 300, 3000, .12 if name == "fire" else .25, .2)
        for k in range(int(D * 6)):
            add(x, hp(noise(.01), 2000) * .3, rng.uniform(0, D))
        return x
    if name == "spark": return mx(sparkle(1.0), zap(.3) * .3)
    if name == "scan":
        t = tt(2.0)
        return norm(np.sin(2 * np.pi * (800 + 400 * np.sin(2 * np.pi * 1.5 * t)) * t) * .2 * np.sin(np.pi * t / 2), .12)
    if name == "ping3":
        out = np.zeros(int(3 * SR))
        for k in range(3): add(out, bell(84 + k * 4, 1, .2), .3 + k * .5)
        return out
    if name == "badge": return mx(whoosh(.4) * .5, np.concatenate([np.zeros(int(.25 * SR)), popsfx(400, .8), chime(88, .25)]))
    if name == "hum": return amb(D, 80, 300, .12, .4)
    if name == "world": return sparkle(1.5) * .7
    if name == "wow":
        out = chime(84, .5); add(out, sparkle(1.5), .1); return out
    if name == "mystery": return pad([62, 65, 69, 72], 4, 800, .3)
    if name == "voice":
        t = tt(3); return norm(np.sin(2 * np.pi * (600 + 80 * np.sin(2 * np.pi * 3 * t)) * t) * np.sin(np.pi * t / 3) ** 2, .07)
    if name == "sniff":
        out = np.zeros(int(1.5 * SR))
        for k in range(2): add(out, bp(noise(.25), 1500, 5000) * np.sin(np.pi * tt(.25) / .25) * .25, .2 + k * .35)
        return out
    if name == "lab": return amb(D, 600, 2000, .05)
    if name == "click": return hp(noise(.02), 2000) * np.exp(-tt(.02) * 200) * .6
    if name == "shield": return mx(chime(72, .3), whoosh(.8) * .3)
    if name == "stamp":
        out = np.zeros(int(4 * SR)); add(out, boom(1.0, 70) * .6, 0); return out
    if name == "stream": return mx(amb(D, 500, 3000, .1, .5), sparkle(1.5) * .5)
    if name == "boom": return boom(3)
    if name == "power_on": return norm(np.sin(2 * np.pi * np.cumsum(60 + 400 * tt(1.5) / 1.5) / SR) * adsr(int(1.5 * SR), .05, .4), .3) * 1 + sparkle(1.5)
    if name == "buttons":
        out = np.zeros(int(3 * SR))
        for k in range(6): add(out, popsfx(rng.uniform(900, 1600), .2), .3 + k * .3)
        return out
    if name == "dopamine":
        out = np.zeros(int(4 * SR))
        for k in range(12): add(out, bell(rng.choice([76, 79, 83, 86, 88, 91]), 1.2, .12), rng.uniform(0, 3))
        return out
    if name == "reward3":
        out = np.zeros(int(9 * SR))
        for k, tm in enumerate((2.5, 4.0, 5.6)): add(out, chime(84 + k * 3, .3), tm)
        return out
    if name == "riser": return riser(2.5)
    if name == "notify":
        out = np.zeros(int(3 * SR))
        for k in range(3): add(out, mx(bell(88, .4, .2), np.concatenate([np.zeros(int(.1 * SR)), bell(93, .3, .2)])), .5 + k * .9)
        return out
    if name == "snore":
        t = tt(3); return norm(lp(noise(3), 300) * (np.sin(2 * np.pi * .5 * t) > 0) * np.sin(2 * np.pi * .5 * t), .15)
    if name == "warm": return pad([62, 66, 69, 74], 4, 1200, .35)
    if name == "nature":
        out = amb(D, 1500, 6000, .03)
        for k in range(int(D / 2)):
            f = rng.uniform(2500, 4000); t = tt(.15)
            add(out, np.sin(2 * np.pi * (f + 800 * np.sin(2 * np.pi * 20 * t)) * t) * np.exp(-t * 15) * .06, rng.uniform(0, D))
        return out
    if name == "robot":
        out = np.zeros(int(3 * SR))
        for k in range(5): add(out, np.sign(np.sin(2 * np.pi * rng.choice([440, 660, 880]) * tt(.08))) * .06, .3 + k * .15)
        return out
    if name == "school": return amb(D, 300, 2000, .05)
    if name == "final": return mx(chime(77, .5), pad([65, 69, 72, 76], 6, 1500, .4))
    return chime(84, .2)


SUST = {"city", "heartbeat", "heartbeat_soft", "heartbeat_fast", "ocean", "bubbles", "tick", "fire", "fire_big", "hum", "lab", "stream", "nature", "school"}
sfx = np.zeros(N)
for s in R.SEG:
    spec = R.SPECS[s["i"]]
    d = s["end"] - s["start"]
    for nm in spec.get("sfx", []):
        x = SFX(nm, d)
        if nm in SUST:
            x = x[: int(d * SR)].copy(); fo = min(len(x), int(.6 * SR)); x[-fo:] *= np.linspace(1, 0, fo)
        add(sfx, x, s["start"], 0.9)
    if s["i"] > 0:
        add(sfx, whoosh(.7, False, 400, 5000) * .18, s["start"] - .35)
    # auto sounds for animated elements
    for lab in spec.get("labels", []):
        add(sfx, popsfx(700, .35), R.sent_t(s, lab[3]) + lab[4])
    for ch in spec.get("chars", []):
        ta = (R.sent_t(s, ch[4]) if ch[4] else s["start"]) + ch[5]
        add(sfx, whoosh(.5) * .4, ta - .1); add(sfx, popsfx(450, .4), ta + .3)
    if "big" in spec:
        ta = R.sent_t(s, spec["big"][2])
        add(sfx, boom(1.5, 55) * .35, ta); add(sfx, chime(81, .2), ta)
    if "badge" in spec:
        add(sfx, boom(1.0, 70) * .5, R.sent_t(s, spec["badge"][1]))
    if "num" in spec:
        add(sfx, popsfx(500, .5), s["start"] + .2)
    if spec.get("subscribe"):
        for tm in (2.3, 3.4, 4.3):
            add(sfx, hp(noise(.02), 2500) * np.exp(-tt(.02) * 200) * .5, s["start"] + tm)
        add(sfx, chime(91, .2), s["start"] + 4.3)
    if spec.get("endcard"):
        for tm in (2.8, 3.9, 4.8):
            add(sfx, hp(noise(.02), 2500) * np.exp(-tt(.02) * 200) * .5, s["start"] + tm)
        add(sfx, chime(91, .25), s["start"] + 4.8)

# reverb
irt = tt(2.2)
ir = rng.standard_normal(len(irt)) * np.exp(-irt * 2.8)
ir = lp(ir, 6000); ir /= np.sqrt(np.sum(ir ** 2))
bed = music * .8 + sfx * .9
wet = oaconvolve(bed, ir)[:N]
bed = bed * .8 + wet * .4

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "narration.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
nar = np.frombuffer(raw, np.float32).astype(np.float64)
narr = np.zeros(N); narr[:min(N, len(nar))] = nar[:N]
narr = narr / (np.max(np.abs(narr)) + 1e-9) * 0.9
envn = (np.abs(narr) > .03).astype(float)[::32]
k = int(.35 * SR) // 32
envs = np.convolve(envn, np.ones(k) / k, mode="same")
envs = np.interp(np.arange(N), np.arange(len(envs)) * 32, envs)
bed *= (1 - .45 * np.clip(envs * 1.5, 0, 1))
rn = np.sqrt(np.mean(narr[np.abs(narr) > .01] ** 2)); rb = np.sqrt(np.mean(bed ** 2))
bed *= rn * .32 / rb
mix = narr + bed
fo = int(2 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
side = wet * .04 * (np.max(np.abs(mix)) / (np.max(np.abs(wet)) + 1e-9))
st = np.stack([mix + side, mix - side], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("final_audio_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "final_audio_raw.wav", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "final_audio.m4a"], check=True)
print("audio", TOTAL)
