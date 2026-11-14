"""WWI soundtrack: narration + mood score + per-beat sound effects (all synthesised).

Usage: python3 ww1_soundtrack.py words.json narration.wav out.wav
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
from st_ww1_timing import beats_and_times  # noqa: E402

SR = st.SR
rng = np.random.default_rng(21)
filt, noise, env_exp, norm, reverb = st.filt, st.noise, st.env_exp, st.norm, st.reverb


# ------------------------------------------------------------------ new effects
def amb_car(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    put = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11 * t))) * filt(noise(sec), hi=400)
    return put * 0.8 + filt(noise(sec), hi=120) * 0.4


def amb_train(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    k = 0
    while k * 0.28 < sec:
        i = int(k * 0.28 * SR)
        m = int(0.22 * SR)
        s = filt(noise(0.22), lo=200, hi=3000) * env_exp(m, 14, 0.01) * (1 if k % 2 else 0.6)
        out[i:i + m] += s[: n - i]
        k += 1
    w = int(min(1.4, sec) * SR)
    tt = np.arange(w) / SR
    whistle = sum(np.sin(2 * np.pi * f * tt) for f in (620, 780, 930)) * np.clip(np.sin(np.pi * tt / tt[-1]), 0, 1) ** 0.5
    out[:w] += whistle * 0.25
    return out + filt(noise(sec), hi=150) * 0.4


def amb_mg(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.2
    while t < sec - 0.3:
        burst = rng.uniform(0.8, 1.8)
        k = 0
        while k * 0.09 < burst and t + k * 0.09 < sec:
            i = int((t + k * 0.09) * SR)
            m = int(0.07 * SR)
            s = filt(noise(0.07), lo=500, hi=5000) * env_exp(m, 60, 0.0005) + filt(noise(0.07), hi=200) * env_exp(
                m, 30) * 0.8
            out[i:i + m] += s[: n - i]
            k += 1
        t += burst + rng.uniform(0.6, 1.5)
    return reverb(out, 0.8, 0.25)[:n]


def amb_plane(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = 78 + 4 * np.sin(2 * np.pi * 0.2 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    eng = sum(np.sin(h * ph) / h for h in range(1, 9))
    eng *= 0.7 + 0.3 * np.sin(2 * np.pi * 26 * t)
    sw = np.minimum(1, np.minimum(t / 2, (sec - t) / 2)).clip(0.2, 1)
    return filt(eng, hi=1500) * sw


def amb_tank(sec):
    n = int(sec * SR)
    out = filt(noise(sec), hi=120) * 1.2
    for k in range(int(sec * 6)):
        i = int(k / 6 * SR)
        m = int(0.05 * SR)
        out[i:i + m] += (filt(noise(0.05), lo=800, hi=4000) * env_exp(m, 80))[: n - i] * 0.6
    t = np.arange(n) / SR
    out += np.sin(2 * np.pi * 42 * t) * 0.3
    return out


def amb_zeppelin(sec):
    t = np.arange(int(sec * SR)) / SR
    drone = sum(np.sin(2 * np.pi * f * t) for f in (55, 82.5, 110)) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t))
    return drone * 0.5 + filt(noise(sec), hi=200) * 0.4


def amb_factory(sec):
    n = int(sec * SR)
    out = filt(noise(sec), hi=300) * 0.2
    k = 0
    while k * 0.6 < sec:
        i = int(k * 0.6 * SR)
        m = int(0.3 * SR)
        tt = np.arange(m) / SR
        clank = sum(np.sin(2 * np.pi * f * tt) for f in (420, 1130, 2210)) * np.exp(-tt * 18)
        out[i:i + m] += clank[: n - i] * (0.6 if k % 2 else 0.35)
        if k % 4 == 2:
            hs = filt(noise(0.4), lo=3000, hi=8000) * np.sin(np.pi * np.arange(int(0.4 * SR)) / (0.4 * SR)) * 0.3
            out[i:i + len(hs)] += hs[: n - i]
        k += 1
    return out


def amb_gas(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    return filt(noise(sec), lo=2000, hi=9000) * (0.5 + 0.3 * np.sin(2 * np.pi * 0.5 * t)) * 0.6


def amb_morse(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    t = 0.3
    while t < sec - 0.3:
        d = rng.choice([0.07, 0.07, 0.21])
        m = int(d * SR)
        tt = np.arange(m) / SR
        out[int(t * SR):int(t * SR) + m] += (np.sin(2 * np.pi * 750 * tt) * np.minimum(1, np.minimum(tt, d - tt) / 0.005))[
            : n - int(t * SR)]
        t += d + rng.choice([0.07, 0.07, 0.21, 0.5])
    return out * 0.5


def whistle():
    d = 1.4
    t = np.arange(int(d * SR)) / SR
    f = 2900 + 160 * np.sign(np.sin(2 * np.pi * 28 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + filt(noise(d), lo=2500, hi=4000) * 0.3
    return norm(x * np.minimum(1, np.minimum(t / 0.02, (d - t) / 0.2)))


def sonar():
    t = np.arange(int(2.5 * SR)) / SR
    x = np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 3)
    return reverb(norm(x), 2.0, 0.5, 1.5)


def silent_night():
    notes = [(67, 1.5), (69, .5), (67, 1), (64, 3), (67, 1.5), (69, .5), (67, 1), (64, 3), (74, 2), (74, 1),
             (71, 3), (72, 2), (72, 1), (67, 3)]
    beat = 0.42
    total = sum(d for _, d in notes) * beat + 3
    out = np.zeros(int(total * SR))
    t0 = 0.0
    for m, d in notes:
        f = 440 * 2 ** ((m + 12 - 69) / 12)
        ln = int(2.5 * SR)
        tt = np.arange(ln) / SR
        s = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 4)
             + 0.15 * np.sin(2 * np.pi * 4.2 * f * tt) * np.exp(-tt * 8)) * np.exp(-tt * 2.2) * np.minimum(1, tt / .003)
        i = int(t0 * SR)
        out[i:i + ln] += s[: len(out) - i]
        t0 += d * beat
    return reverb(norm(out), 2.2, 0.4, 1.6)


st.AMB.update({"car": amb_car, "train": amb_train, "mg": amb_mg, "plane": amb_plane, "tank": amb_tank,
               "zeppelin": amb_zeppelin, "factory": amb_factory, "gas": amb_gas, "morse": amb_morse})
st.AMB_GAIN.update({"car": 0.3, "train": 0.35, "mg": 0.4, "plane": 0.3, "tank": 0.4, "zeppelin": 0.35,
                    "factory": 0.3, "gas": 0.25, "morse": 0.2})
st.ONE.update({"whistle": whistle, "sonar": sonar, "silentnight": silent_night,
               "mg": lambda: amb_mg(2.0)})
st.ONE_GAIN.update({"whistle": 0.4, "sonar": 0.3, "silentnight": 0.45, "mg": 0.45})


# ------------------------------------------------------------------ score in blocks (memory friendly)
def score(N, starts, moods, talk_s):
    music = np.zeros((N, 2), dtype=np.float32)
    BLOCK = int(480 * SR)
    OV = int(3 * SR)
    weights = [0.22, 0.2, 0.32, 0.16, 0.16, 0.22, 0.14]
    a0 = 0
    while a0 < N:
        a1 = min(N, a0 + BLOCK + OV)
        L = a1 - a0
        block = np.zeros((L, 2))
        stems = [lambda: st.pad_stem(L, st.MINOR), lambda: st.pad_stem(L, st.MAJOR, True),
                 lambda: st.drum_stem(L), lambda: st.brass_stem(L, st.MINOR),
                 lambda: st.brass_stem(L, st.MAJOR), lambda: st.melody_stem(L), lambda: st.drone_stem(L)]
        for si, fn in enumerate(stems):
            pts = [(max(0.0, s - a0 / SR), st.MIXES[m][si]) for s, m in zip(starts, moods) if s < a1 / SR]
            # keep only the latest point before block start + points inside
            first = [p for p in pts if p[0] == 0.0]
            pts = ([first[-1]] if first else [(0.0, 0.0)]) + [p for p in pts if p[0] > 0]
            g = st.smooth_env(pts, L, 2.0)
            if g.max() <= 0:
                continue
            block += fn()[:L] * g[:, None] * weights[si]
        fade = np.ones(L)
        if a0 > 0:
            fade[:OV] = np.linspace(0, 1, OV)
        if a1 < N:
            fade[-OV:] = np.linspace(1, 0, OV)
        music[a0:a1] += (block * fade[:, None]).astype(np.float32)
        print("score block", a0 / SR, flush=True)
        a0 += BLOCK
    music /= np.abs(music).max()
    music *= 0.6
    music *= (1 - 0.5 * talk_s)[:, None]
    return music


def main():
    words_path, narr_path, out = sys.argv[1:4]
    beats, starts, dur, words = beats_and_times(words_path)
    ends = starts[1:] + [dur]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", narr_path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    narr = np.frombuffer(raw, dtype=np.float32).astype(np.float32)
    N = len(narr)
    talk = np.zeros(N, dtype=np.float32)
    for w in words:
        talk[int(w["s"] * SR):int(w["e"] * SR)] = 1
    k = int(0.4 * SR)
    cs = np.cumsum(np.concatenate([np.zeros(k), talk, np.zeros(k)]))
    talk_s = np.clip((cs[2 * k:] - cs[:-2 * k])[:N] / (k * 0.6), 0, 1).astype(np.float32)
    del cs

    music = score(N, starts, [b["mood"] for b in beats], talk_s)

    fx = np.zeros((N, 2), dtype=np.float32)

    def place(x, t0, gain, pan=0.0):
        i = int(t0 * SR)
        if i < 0:
            x, i = x[-i:], 0
        if i >= N:
            return
        x = x[: N - i]
        fx[i:i + len(x), 0] += (x * gain * np.sqrt(0.5 * (1 - pan))).astype(np.float32)
        fx[i:i + len(x), 1] += (x * gain * np.sqrt(0.5 * (1 + pan))).astype(np.float32)

    for i, (b, s, e) in enumerate(zip(beats, starts, ends)):
        d = e - s + 0.4
        for tok in b["sfx"].split():
            if "@" in tok:
                name, at = tok.split("@")
                place(st.ONE[name](), s + float(at), st.ONE_GAIN[name], float(rng.uniform(-0.3, 0.3)))
            elif "*" in tok:
                name, n = tok.split("*")
                for j in range(int(n)):
                    at = s + (j + rng.uniform(0.1, 0.9)) * max(0.3, d - 1) / int(n)
                    place(st.ONE[name](), at, st.ONE_GAIN[name] * rng.uniform(0.6, 1), float(rng.uniform(-0.7, 0.7)))
            else:
                x = st.AMB[tok](d + 0.6)
                x = st.fades(x / (np.abs(x).max() + 1e-9), 0.35, 0.6)
                place(x, s - 0.2, st.AMB_GAIN[tok] * 0.6, float(rng.uniform(-0.2, 0.2)))
        # soft whoosh on every cut between photo and animation
        if i > 0 and b["kind"] != beats[i - 1]["kind"]:
            place(st.whoosh(0.7), s - 0.35, 0.12)
        if i % 25 == 0:
            print("sfx beat", i + 1, flush=True)
    fx *= (1 - 0.35 * talk_s)[:, None]

    narr = narr / np.abs(narr).max() * 0.9
    mix = np.empty((N, 2), dtype=np.float32)
    mix[:, 0] = narr
    mix[:, 1] = narr
    mix += music * 0.55 + fx * 0.5
    tm = np.arange(N, dtype=np.float32) / SR
    mix *= np.clip((dur - tm) / 3, 0, 1)[:, None]
    mix = np.nan_to_num(mix)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix /= np.abs(mix).max() / 0.95
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
