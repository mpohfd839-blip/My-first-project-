"""Soundtrack for 'What New York Looked Like 400 Years Ago': an era-changing score
(wilderness flute -> colonial harpsichord -> 19th-century piano -> modern pulse) and timed
sound effects. Everything synthesised with numpy.

Usage: python3 audio.py out.wav
"""
import math
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "napoleonic_wars", "video"))
sys.path.insert(0, os.path.join(HERE, "..", "world_war_1", "video"))
import soundtrack as st  # noqa: E402
import ww1_soundtrack  # noqa: E402,F401  (registers extra sounds: factory, train, ...)
import timeline as TL  # noqa: E402

SR = st.SR
DUR = TL.DUR
N = int(DUR * SR)
rng = np.random.default_rng(400)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * d)


def place(buf, x, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i < 0:
        x, i = x[-i:], 0
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x), 0] += x * g * math.sqrt(0.5 * (1 - pan))
    buf[i:i + len(x), 1] += x * g * math.sqrt(0.5 * (1 + pan))


def era_gain(t, a, b, fade=6.0):
    return np.clip(np.minimum((t - a) / fade + 1, (b - t) / fade + 1), 0, 1)


# ------------------------------------------------------------------ instruments
def strings(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for det in (-0.25, 0.0, 0.3):
        f = freq * 2 ** (det / 12 / 4)
        ph = rng.uniform(0, 6.28)
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + ph)
        # band-limited saw (8 partials)
        x += sum(np.sin(2 * np.pi * f * k * t * vib + ph * k) / k for k in range(1, 9))
    x = st.filt(x, hi=freq * 4)
    e = np.minimum(1, np.minimum(t / 1.6, (dur - t) / 1.8)).clip(0, 1) ** 1.5
    return x * e / 3


def piano(freq, dur=3.5, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)):
        fk = freq * k * (1 + 0.0004 * k * k)
        x += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.9 + 0.7 * k))
    hammer = st.filt(rng.standard_normal(n), lo=1500, hi=6000) * np.exp(-t * 80) * 0.05
    return (x + hammer) * np.minimum(1, t / 0.003) * vel


def harpsichord(freq, dur=1.6):
    """Karplus-Strong pluck, block-vectorised."""
    n = int(dur * SR)
    L = max(2, int(SR / freq))
    y = np.zeros(n + L + 1)
    y[:L] = rng.uniform(-1, 1, L)
    i = L
    while i < n + L:
        j = min(i + L, n + L)
        prev = y[i - L:j - L]
        prev2 = y[i - L - 1:j - L - 1] if i - L - 1 >= 0 else np.concatenate([[0], y[i - L:j - L - 1]])
        y[i:j] = 0.996 * 0.5 * (prev + prev2[:len(prev)])
        i = j
    x = y[L:L + n]
    x = st.filt(x, lo=180)
    return x * np.minimum(1, np.arange(n) / SR / 0.002)


def flute(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t) * np.clip(t / 0.6, 0, 1)
    x = np.sin(2 * np.pi * freq * t * vib) + 0.18 * np.sin(4 * np.pi * freq * t * vib)
    breath = st.filt(rng.standard_normal(n), lo=1200, hi=5000) * 0.08
    e = np.minimum(1, np.minimum(t / 0.25, (dur - t) / 0.4)).clip(0, 1)
    return (x + breath) * e


def synth_pluck(freq, dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 6))
    return st.filt(x, hi=2500) * np.exp(-t * 7) * np.minimum(1, t / 0.004)


def drum(dur=2.5, pitch=55):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = pitch * (1 + 0.6 * np.exp(-t * 18))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    x += st.filt(rng.standard_normal(n), hi=600) * np.exp(-t * 14) * 0.5
    return st.norm(x)


# ------------------------------------------------------------------ score
# D major / B minor: D - A - Bm - G, then Bm - G - D - A for variety
PROG = [[50, 57, 62, 66], [45, 57, 61, 64], [47, 54, 59, 62], [43, 55, 59, 62],
        [47, 54, 59, 62], [43, 55, 59, 62], [50, 57, 62, 66], [45, 57, 61, 64]]
CH = 6.0  # seconds per chord


def score():
    mus = np.zeros((N, 2))
    t_axis = np.arange(N) / SR
    n_ch = int(DUR / CH) + 1
    for k in range(n_ch):
        t0 = k * CH
        ch = PROG[k % len(PROG)]
        tension = 440 <= t0 < 465
        # strings bed throughout (darker during the fire)
        for m in ch:
            f = hz(m - (12 if m > 60 else 0))
            if tension:
                f *= 2 ** (-1 / 12) if m == ch[2] else 1
            place(mus, strings(f, CH + 2.0), t0 - 1.0, 0.055, rng.uniform(-0.5, 0.5))
        place(mus, strings(hz(ch[0] - 12), CH + 2.0), t0 - 1.0, 0.07)
        # wilderness: flute phrases over the strings (0-112 s)
        if t0 < 112:
            penta = [62, 64, 66, 69, 71, 74, 76]
            tt = t0 + 0.4
            while tt < t0 + CH - 0.6:
                d = rng.choice([0.6, 0.9, 1.2, 1.8])
                place(mus, flute(hz(rng.choice(penta)), d + 0.3), tt, 0.06 * era_gain(tt, 0, 112), 0.15)
                tt += d + rng.choice([0.0, 0.3, 0.6])
        # colonial: harpsichord arpeggios (112-430 s)
        if 100 <= t0 < 440:
            step = 0.25
            pat = [0, 1, 2, 3, 2, 1, 2, 3]
            for i in range(int(CH / step)):
                m = ch[pat[i % 8]] + (12 if i % 8 in (3, 4) else 0)
                g = 0.07 * era_gain(t0 + i * step, 112, 430)
                place(mus, harpsichord(hz(m)), t0 + i * step, g, 0.25 if i % 2 else -0.25)
        # 19th century: piano (465-600 s)
        if 460 <= t0 < 610:
            for i, m in enumerate([ch[0], ch[1], ch[2], ch[3], ch[2], ch[1]]):
                place(mus, piano(hz(m + 12), 3.0, 0.8), t0 + i * CH / 6, 0.08 * era_gain(t0, 465, 600))
        # modern: pulsing synth + low drum (600-720 s)
        if t0 >= 596:
            for i in range(int(CH / 0.25)):
                m = ch[(i // 2) % 4] + 12
                place(mus, synth_pluck(hz(m)), t0 + i * 0.25, 0.05 * era_gain(t0, 602, 760), 0.3 * (-1) ** i)
            for b in range(int(CH / 1.5)):
                place(mus, drum(1.5, 50), t0 + b * 1.5, 0.12 * era_gain(t0, 620, 760))
        # gentle piano motif in the quieter colonial middle
        if 340 <= t0 < 430 and k % 2 == 0:
            for i, m in enumerate((ch[3] + 12, ch[2] + 12, ch[1] + 12)):
                place(mus, piano(hz(m), 3.0, 0.6), t0 + 1 + i * 1.2, 0.05)
    # big moments: drums
    for tt, n in ((258, 4), (419, 6), (444, 8), (602, 3), (704, 4)):
        for i in range(n):
            place(mus, drum(2.5, 45 + 5 * (i % 2)), tt + i * 0.75, 0.22)
    mus = st.reverb(mus[:, 0], 2.4, 0.3)[:N, None] * np.array([1, 0]) + \
        st.reverb(mus[:, 1], 2.4, 0.3)[:N, None] * np.array([0, 1])
    mus /= np.abs(mus).max()
    fade = np.clip(np.minimum(t_axis / 3.0, (DUR - t_axis) / 4.0), 0, 1)
    return mus * fade[:, None]


# ------------------------------------------------------------------ sound effects
def sfx():
    fx = np.zeros((N, 2))

    def amb(name, a, b, g, pan=0.0):
        x = st.AMB[name](b - a + 1.0)
        x = st.fades(x / (np.abs(x).max() + 1e-9), 1.5, 2.0)
        place(fx, x, a - 0.5, g, pan)

    def one(name, at, g, pan=0.0):
        place(fx, st.ONE[name](), at, g, pan)

    # nature
    amb("sea", 0, DUR, 0.18)
    amb("wind", 0, 115, 0.22)
    amb("birds", 0, 115, 0.40)
    amb("birds", 115, 300, 0.22)
    amb("gulls", 50, 112, 0.35)
    amb("gulls", 255, 300, 0.30)
    amb("gulls", 340, 420, 0.30)
    # Halve Maen: creaking and splashing
    for tt in np.arange(52, 72, 2.7):
        n = int(0.6 * SR)
        tt_ = np.arange(n) / SR
        creak = st.filt(rng.standard_normal(n), lo=300, hi=900) * np.sin(np.pi * tt_ / 0.6) ** 2 * \
            (0.5 + 0.5 * np.sin(2 * np.pi * 35 * tt_))
        place(fx, creak, tt, 0.15, -0.3)
    amb("sea", 52, 72, 0.25)
    # construction (hammering) while the town grows
    for tt in np.arange(115, 600, 0.37):
        if rng.random() < 0.35:
            n = int(0.09 * SR)
            ttt = np.arange(n) / SR
            s = (np.sin(2 * np.pi * 900 * ttt) * 0.4 + st.filt(rng.standard_normal(n), lo=1500, hi=6000)) * \
                np.exp(-ttt * 60)
            place(fx, s, tt + rng.uniform(0, 0.2), 0.05, rng.uniform(-0.6, 0.6))
    # town life grows
    amb("murmur", 170, 440, 0.18)
    amb("murmur", 470, 600, 0.28)
    amb("gallop", 520, 600, 0.12)
    amb("march", 120, 150, 0.08)
    # 1664 English fleet
    for i in range(5):
        one("cannonD", 262 + i * 2.2, 0.35, rng.uniform(-0.5, 0.5))
    one("bell", 282, 0.25)
    # 1673 Dutch return
    for i in range(3):
        one("cannonD", 295 + i * 2.5, 0.3, rng.uniform(-0.5, 0.5))
    # Trinity church bells
    for i in range(5):
        one("bellL", 320 + i * 2.2, 0.22)
    # 1776 fleet + fire
    for i in range(8):
        one("cannon", 425 + i * 1.6, 0.30, rng.uniform(-0.7, 0.7))
    amb("fireH", 444, 466, 0.55)
    amb("panic", 446, 462, 0.25)
    for i in range(6):
        one("bell", 446 + i * 1.3, 0.18, 0.4)
    one("explosion", 452, 0.25)
    # Evacuation + inauguration
    amb("cheer", 466, 478, 0.30)
    for i in range(4):
        one("bellL", 486 + i * 2.0, 0.22)
    amb("cheer", 494, 506, 0.45)
    for i in range(13):
        one("cannonD", 495 + i * 0.8, 0.12, rng.uniform(-0.6, 0.6))
    # steam era
    for tt in (604, 612, 626):
        n = int(1.8 * SR)
        ttt = np.arange(n) / SR
        whistle = sum(np.sin(2 * np.pi * f * ttt) for f in (380, 470, 560)) * np.clip(
            np.minimum(ttt / 0.1, (1.8 - ttt) / 0.4), 0, 1)
        place(fx, st.filt(whistle, hi=2500), tt, 0.10, 0.5)
    amb("factory", 600, 640, 0.10)
    # modern city
    n = int((720 - 640) * SR)
    ttt = np.arange(n) / SR
    traffic = st.filt(rng.standard_normal(n), lo=60, hi=900) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * ttt))
    place(fx, st.fades(traffic / np.abs(traffic).max(), 4, 4), 640, 0.18)
    for tt in rng.uniform(645, 700, 10):
        m = int(0.35 * SR)
        tm = np.arange(m) / SR
        horn = (np.sign(np.sin(2 * np.pi * 420 * tm)) * 0.3 + np.sign(np.sin(2 * np.pi * 530 * tm)) * 0.3)
        place(fx, st.filt(horn, hi=1800) * np.clip(np.minimum(tm / 0.02, (0.35 - tm) / 0.05), 0, 1), tt, 0.03,
              rng.uniform(-0.8, 0.8))
    # fireworks synced with the finale bursts
    for k in range(10):
        for b in range(6):
            tb = 704 + 1.6 * (k - b / 6)
            if 704 <= tb < 719:
                one("shot", tb, 0.25, rng.uniform(-0.7, 0.7))
                n = int(1.4 * SR)
                ttt = np.arange(n) / SR
                crackle = st.filt(rng.standard_normal(n), lo=2000, hi=9000) * (rng.random(n) < 0.02) * \
                    np.exp(-ttt * 2.5)
                place(fx, crackle, tb + 0.2, 0.5, rng.uniform(-0.7, 0.7))
    # whooshes on every titled moment
    for t0, _, _, _, _ in TL.CAPTIONS:
        place(fx, st.whoosh(1.1), t0 - 0.6, 0.06)
    return fx


def main():
    out = sys.argv[1]
    m = score()
    f = sfx()
    mix = m * 0.55 + f * 0.6
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix /= np.abs(mix).max() / 0.95
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
