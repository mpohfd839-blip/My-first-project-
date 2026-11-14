"""Beat timing shared by the soundtrack (same rule as ww1_render.load_timing, without cairo setup)."""
import json

import importlib
import os

BEATS = importlib.import_module(os.environ.get("BEATS_MODULE", "ww1_scenes")).BEATS


def beats_and_times(words_path):
    d = json.load(open(words_path))
    words = d["words"]
    text = "\n".join(d["lines"])
    starts, last = [], 0
    for b in BEATS:
        if b.get("follow"):
            starts.append(None)
            continue
        pos = text.find(b["cue"], last)
        if pos < 0:
            raise SystemExit(f"cue not found in order: {b['cue']!r}")
        last = pos + 1
        wi = len(text[:pos].split())
        starts.append(max(0.0, words[wi]["s"] - 0.12))
    for i, st0 in enumerate(starts):
        if st0 is None:  # beat that takes over part-way through the previous one
            nxt = next((x for x in starts[i + 1:] if x is not None), d["duration"])
            starts[i] = starts[i - 1] + max(4.5, (nxt - starts[i - 1]) * BEATS[i]["follow"])
    starts[0] = 0.0
    for i in range(1, len(starts)):
        starts[i] = max(starts[i], starts[i - 1] + 1.0)
    return BEATS, starts, d["duration"], words
