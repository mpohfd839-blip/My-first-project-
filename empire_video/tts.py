import wave, json, os, sys, re
import numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig
from script import BEATS
v = PiperVoice.load("joe.onnx")
cfg = SynthesisConfig(length_scale=1.17, noise_scale=0.6, noise_w_scale=0.75)
os.makedirs("vo", exist_ok=True)
info = []
for i, b in enumerate(BEATS):
    txt = b["text"].replace("—", ",")
    p = f"vo/b{i:03d}.wav"
    with wave.open(p, "wb") as w:
        v.synthesize_wav(txt, w, syn_config=cfg)
    with wave.open(p) as w:
        d = w.getnframes() / w.getframerate()
    info.append(d)
    print(i, round(d, 2), txt[:50], flush=True)
json.dump(info, open("vo/durs.json", "w"))
print("total speech", sum(info))
