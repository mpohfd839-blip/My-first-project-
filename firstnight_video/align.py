"""Align story sentences to narration audio using silence detection + DP.
Writes timeline.json: list of {shot, sentences:[{text,start,end}]}"""
import json, re, subprocess, sys
from story import SHOTS

AUDIO = sys.argv[1]
out = subprocess.run(["ffmpeg", "-i", AUDIO, "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                           capture_output=True, text=True).stdout)
sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
# speech segments
segs = []
t = 0.0
for s, e in sil:
    if s - t > 0.05:
        segs.append((t, s))
    t = e
if dur - t > 0.05:
    segs.append((t, dur))
print("speech segments:", len(segs))

sents = []
for si, (spec, lines) in enumerate(SHOTS):
    for ln in lines:
        sents.append((si, ln))
n = len(sents)
def weight(txt):
    w = re.sub(r"[^A-Za-z0-9 ]", "", txt)
    return len(w) + 6  # base cost per sentence
W = [weight(t) for _, t in sents]
total_speech = sum(e - s for s, e in segs)
rate = total_speech / sum(W)
m = len(segs)
INF = 1e18
# dp[i][k]: sentences[:i] consumed, segments[:k] consumed
dp = [[INF] * (m + 1) for _ in range(n + 1)]
bk = [[None] * (m + 1) for _ in range(n + 1)]
dp[0][0] = 0
for i in range(n):
    for k in range(m):
        if dp[i][k] >= INF:
            continue
        for gi in range(1, 4):           # sentences in group
            j = i + gi
            if j > n:
                break
            wsum = sum(W[i:j])
            exp = wsum * rate
            for gk in range(1, 6):       # segments in group
                kk = k + gk
                if kk > m:
                    break
                act = sum(e - s for s, e in segs[k:kk])
                c = (act - exp) ** 2 / (exp + 0.5)
                c += 0.6 * (gi - 1) + 0.25 * (gk - 1)
                # mismatch between sentence count and segment count is plausible either way
                v = dp[i][k] + c
                if v < dp[j][kk]:
                    dp[j][kk] = v
                    bk[j][kk] = (i, k)
print("cost", dp[n][m])
# backtrack
groups = []
j, kk = n, m
while j > 0:
    i, k = bk[j][kk]
    groups.append((i, j, k, kk))
    j, kk = i, k
groups.reverse()
times = [None] * n
for i, j, k, kk in groups:
    gsegs = segs[k:kk]
    t0, t1 = gsegs[0][0], gsegs[-1][1]
    if j - i == 1:
        times[i] = (t0, t1)
        continue
    # distribute sentence boundaries: prefer segment boundaries close to proportional split
    wsum = sum(W[i:j])
    acc = 0
    cur = t0
    bounds = [s for s, e in gsegs[1:]]
    ends_ = [e for s, e in gsegs[:-1]]
    for q in range(i, j):
        acc += W[q]
        if q == j - 1:
            times[q] = (cur, t1)
            break
        target = t0 + (t1 - t0) * acc / wsum
        # snap to a gap if one is within 0.6s
        best = None
        for e, s in zip(ends_, bounds):
            if abs(e - target) < 0.6 and (best is None or abs(e - target) < abs(best[0] - target)):
                best = (e, s)
        if best:
            times[q] = (cur, best[0]); cur = best[1]
        else:
            times[q] = (cur, target); cur = target
timeline = []
for si, (spec, lines) in enumerate(SHOTS):
    timeline.append({"shot": si, "sentences": []})
for (si, txt), tt in zip(sents, times):
    timeline[si]["sentences"].append({"text": txt, "start": round(tt[0], 3), "end": round(tt[1], 3)})
json.dump({"duration": dur, "timeline": timeline}, open("timeline.json", "w"), indent=1)
for (si, txt), tt in list(zip(sents, times))[:25]:
    print(f"{tt[0]:7.2f} {tt[1]:7.2f}  {txt}")
print("...")
for (si, txt), tt in list(zip(sents, times))[-12:]:
    print(f"{tt[0]:7.2f} {tt[1]:7.2f}  {txt}")
