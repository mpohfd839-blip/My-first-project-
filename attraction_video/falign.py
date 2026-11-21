"""Forced alignment of the script to the narration with PocketSphinx (word-level).
Aligns each chapter-sized chunk separately (windows taken from the coarse silence alignment),
then rewrites timeline.json with exact sentence start/end times."""
import json, re, subprocess
import numpy as np
from pocketsphinx import Decoder
from story import SHOTS

SR = 16000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "narration.mp3", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
pcm = np.frombuffer(raw, np.int16)
TL = json.load(open("timeline.json"))
_o = subprocess.run(["ffmpeg", "-i", "narration.mp3", "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"], capture_output=True, text=True).stderr
ONSETS = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", _o)]
sents = []
for si, (sp, ss) in enumerate(SHOTS):
    for k, s in enumerate(ss):
        c = TL["timeline"][si]["sentences"][k]
        sents.append(dict(shot=si, k=k, text=s, c0=c["start"], c1=c["end"]))


def words_of(s):
    return re.sub(r"[^a-z' ]", " ", s.lower().replace("-", " ")).split()


# chunks of ~12 sentences, cut where there is a pause between sentences
chunks, cur = [], []
for j, s in enumerate(sents):
    cur.append(j)
    if len(cur) >= 10 and (j + 1 == len(sents) or sents[j + 1]["c0"] - s["c1"] > 0.35):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)

dec = Decoder(samprate=SR, bestpath=False)
dec.add_word("reshapes", "R IY SH EY P S", False)
dec.add_word("vasopressin", "V EY Z OW P R EH S IH N", True)
out = {}
for ch in chunks:
    a = max(0, sents[ch[0]]["c0"] - 0.6); b = sents[ch[-1]]["c1"] + 0.6
    seg = pcm[int(a * SR): int(b * SR)].tobytes()
    text = " ".join(" ".join(words_of(sents[j]["text"])) for j in ch)
    dec.set_align_text(text)
    dec.start_utt(); dec.process_raw(seg, full_utt=True); dec.end_utt()
    ws = [(w.word, a + w.start_frame / 100, a + (w.end_frame + 1) / 100) for w in dec.seg() if w.word not in ("<sil>", "<s>", "</s>", "[NOISE]")]
    ws = [(re.sub(r"\(\d+\)$", "", w), s0, s1) for w, s0, s1 in ws]
    p = 0
    ok = True
    for j in ch:
        n = len(words_of(sents[j]["text"]))
        piece = ws[p:p + n]
        if len(piece) < n:
            ok = False; break
        out[j] = (piece[0][1], piece[-1][2], [(w, round(a0, 3)) for w, a0, a1 in piece]); p += n
    print(f"chunk {a:7.1f}-{b:7.1f}  words {len(ws)} expected {len(text.split())} {'OK' if ok and len(ws)==len(text.split()) else 'MISMATCH'}")
# write back; keep coarse times where alignment failed
dev = []
for j, s in enumerate(sents):
    if j in out:
        st, en, wl = out[j]
        near = min(ONSETS, key=lambda e: abs(e - st))
        if abs(near - st) < 0.4:
            st = near                     # snap to the real speech onset
        dev.append(st - s["c0"])
        TL["timeline"][s["shot"]]["sentences"][s["k"]].update(start=round(st, 3), end=round(en, 3), words=wl)
dev = np.array(dev)
print("aligned", len(out), "of", len(sents), " mean|dev| %.2fs  max %.2fs" % (np.abs(dev).mean(), np.abs(dev).max()))
json.dump(TL, open("timeline.json", "w"), indent=1)
