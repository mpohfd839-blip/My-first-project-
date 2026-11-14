"""Word-level timing of the narration against the voiceover.

Runs offline speech recognition (pocketsphinx) over the audio in chunks cut
at quiet points, then aligns the recognised words to the known script with
difflib; matched words become time anchors and the rest are interpolated.

Usage: python3 align.py audio16k.raw ../narration.txt words.json
"""
import difflib
import json
import re
import sys
from multiprocessing import Pool

import numpy as np

SR = 16000


def load(path):
    return np.frombuffer(open(path, "rb").read(), dtype="<i2")


def cut_points(x, every=25.0):
    win = int(0.05 * SR)
    n = len(x) // win
    rms = np.sqrt((x[: n * win].astype(np.float64).reshape(n, win) ** 2).mean(1))
    cuts, t = [0], every
    while t < len(x) / SR - 5:
        a, b = int((t - 4) / 0.05), int((t + 4) / 0.05)
        i = a + int(np.argmin(rms[a:b]))
        cuts.append(int((i + 0.5) * win))
        t = cuts[-1] / SR + every
    cuts.append(len(x))
    return cuts


def recog(args):
    path, s, e = args
    from pocketsphinx import Decoder
    x = load(path)[s:e]
    d = Decoder(samprate=SR, loglevel="FATAL")
    d.start_utt()
    d.process_raw(x.tobytes(), full_utt=True)
    d.end_utt()
    fr = d.config["frate"]
    out = []
    for sg in d.seg():
        w = re.sub(r"\(\d+\)$", "", sg.word)
        if w.startswith("<") or w.startswith("[") or w == "<sil>":
            continue
        out.append((w.lower(), s / SR + sg.start_frame / fr, s / SR + (sg.end_frame + 1) / fr))
    return out


NUM = {"1769": "seventeen sixty nine", "1789": "seventeen eighty nine", "1793": "seventeen ninety three",
       "1795": "seventeen ninety five", "1796": "seventeen ninety six", "1797": "seventeen ninety seven",
       "1798": "seventeen ninety eight", "1799": "seventeen ninety nine", "1800": "eighteen hundred",
       "1801": "eighteen oh one", "1802": "eighteen oh two", "1803": "eighteen oh three",
       "1804": "eighteen oh four", "1805": "eighteen oh five", "1806": "eighteen oh six",
       "1807": "eighteen oh seven", "1808": "eighteen oh eight", "1809": "eighteen oh nine",
       "1810": "eighteen ten", "1811": "eighteen eleven", "1812": "eighteen twelve",
       "1813": "eighteen thirteen", "1814": "eighteen fourteen", "1815": "eighteen fifteen",
       "1821": "eighteen twenty one"}


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def two(n):
    if n < 20:
        return ONES[n]
    return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])


def year_words(t):
    if t in NUM:
        return NUM[t]
    if re.fullmatch(r"1[0-9]{3}", t):
        a, b = int(t[:2]), int(t[2:])
        tail = "hundred" if b == 0 else ("oh " + ONES[b] if b < 10 else two(b))
        return two(a) + " " + tail
    if re.fullmatch(r"[0-9]{1,2}", t):
        return two(int(t))
    return t


def norm(tok):
    t = tok.lower().strip(".,:;!?\"'()").replace("’", "'")
    t = re.sub(r"[^a-z0-9'éèüö-]", "", t)
    return year_words(t).split() if t else []


def main():
    raw, script, out = sys.argv[1:4]
    x = load(raw)
    cuts = cut_points(x)
    jobs = [(raw, a, b) for a, b in zip(cuts, cuts[1:])]
    with Pool(4) as p:
        rec = [w for part in p.map(recog, jobs) for w in part]
    print("recognised", len(rec), "words")

    lines = [l for l in open(script, encoding="utf-8").read().splitlines()
             if l.strip() and not l.startswith("[") and not l.startswith("THE END")
             and not l.startswith("THE NAPOLEONIC")]
    text = "\n".join(lines)
    words = []  # display tokens
    keys = []   # (normalised piece, display index)
    for li, line in enumerate(lines):
        for tok in line.split():
            words.append({"w": tok, "line": li})
            for k in norm(tok):
                keys.append((k, len(words) - 1))
    sm = difflib.SequenceMatcher(None, [k for k, _ in keys], [w for w, _, _ in rec], autojunk=False)
    anchors = {}
    for a, b, n in sm.get_matching_blocks():
        for j in range(n):
            wi = keys[a + j][1]
            _, s, e = rec[b + j]
            anchors.setdefault(wi, [s, e])
            anchors[wi][1] = e
    print("anchored", len(anchors), "of", len(words))
    dur = len(x) / SR
    idx = sorted(anchors)
    # interpolate unanchored words by character length between anchors
    pts = [(-1, 0.0)] + [(i, anchors[i][0]) for i in idx] + [(len(words), dur)]
    for (i0, t0), (i1, t1) in zip(pts, pts[1:]):
        gap = list(range(i0 + 1, i1))
        if not gap:
            continue
        start = anchors[i0][1] if i0 >= 0 else t0
        span = max(0.0, t1 - start)
        L = [len(words[g]["w"]) + 2 for g in gap]
        tot = sum(L)
        acc = start
        for g, l in zip(gap, L):
            words[g]["s"] = acc
            acc += span * l / tot
            words[g]["e"] = acc
    for i in idx:
        words[i]["s"], words[i]["e"] = anchors[i]
    json.dump({"duration": dur, "lines": lines, "words": words}, open(out, "w"), indent=0)
    print("wrote", out)


if __name__ == "__main__":
    main()
