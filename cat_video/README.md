# Cat Behaviour – 5-minute animated video

`cat_behaviour_5min.mp4` — 1280x720, 24 fps, exactly 5:00. No voice or narration, only background sound
(soft ambient music, room tone, birds outside the window, purring).

Scenes (30 s each): waking & stretching · grooming · tail language · playing with yarn ·
stalking & pouncing · kneading · slow blink & purring · bird watching & chattering · zoomies · curling up to sleep.

Regenerate (needs `ffmpeg`, `numpy`, `pycairo`):

```
python3 make_audio.py background.wav
python3 make_video.py background.wav cat_behaviour_5min.mp4
```
