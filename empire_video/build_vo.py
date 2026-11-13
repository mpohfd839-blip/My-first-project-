import json, wave, numpy as np, subprocess
from script import BEATS
durs = json.load(open("vo/durs.json"))
SR = 22050
LEAD = 0.8
segs, t = [], LEAD
timeline = []
audio = [np.zeros(int(LEAD * SR), np.int16)]
for i, b in enumerate(BEATS):
    with wave.open(f"vo/b{i:03d}.wav") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
    pause = 1.0
    if b["art"] in ("chapter", "title"):
        pause = 1.6
    if i + 1 < len(BEATS) and BEATS[i + 1]["art"] == "chapter":
        pause = 1.5
    start = t
    audio.append(x)
    audio.append(np.zeros(int(pause * SR), np.int16))
    t += len(x) / SR + pause
    timeline.append(dict(i=i, start=round(start, 3), speech_end=round(start + len(x) / SR, 3), end=round(t, 3)))
END = 8.0
audio.append(np.zeros(int(END * SR), np.int16))
a = np.concatenate(audio)
with wave.open("vo/narration_raw.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(a.tobytes())
json.dump(dict(beats=timeline, total=len(a) / SR, endcard=[t, t + END]), open("timeline.json", "w"), indent=1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vo/narration_raw.wav", "-af",
                "highpass=f=70,equalizer=f=140:t=q:w=1.2:g=3,equalizer=f=3200:t=q:w=1.5:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=180,aecho=0.85:0.5:35|70:0.10|0.06,loudnorm=I=-17:TP=-2",
                "-ar", "44100", "narration.wav"], check=True)
print("total", len(a) / SR)
