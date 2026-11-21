"""36-second cold-open hook. Each shot is one narration fragment, so the cuts land on the words."""
from story import S, Y, C, M, O, R

RAW = [
    (S("H01_time_freeze", (1.0, 1.45, .5, .5, .3, .55), dof=(.3, .62, .15), pulse=(.3, .6, .08, 1.2), sfx=["heartbeat", "swell"], mood=3,
       head=("A FRACTION OF A [SECOND]", 0)), ["In a fraction of a second,"]),
    (S("H02_brain_stopwatch", (1.25, 1.6, .5, .5, .5, .5), pulse=(.5, .5, .16, 2.0), shake=.15, sfx=["tick", "zap"],
       big=("< 1 SECOND", "", 0)), ["your brain makes a decision about her."]),
    (S("S02_eye_closeup", (1.4, 2.2, .5, .5, .5, .5), pulse=(.5, .5, .2, 1.5), sfx=["shimmer"], head=("PUPILS [WIDEN]", 0)), ["Your pupils widen."]),
    (S("S33_heart_race", (1.2, 1.5, .5, .42, .5, .4), pulse=(.5, .38, .16, 2.6), ekg=True, shake=.1, sfx=["heartbeat_fast"],
       head=("HEART RATE [JUMPS]", 0)), ["Your heart rate jumps."]),
    (S("N13_photo_brain", (1.1, 1.5, .5, .4, .42, .25), pulse=(.42, .22, .16, 1.6), sfx=["power_on"],
       head=("SAME CIRCUITS AS [ADDICTION]", 0)), ["And the same reward circuits that light up for addictive drugs…"]),
    (S("S34_dopamine_rain", (1.3, 1.0, .5, .5, .5, .5), rain=True, shake=.3, sfx=["dopamine", "boom"],
       big=("FIRING.", "", 0)), ["start firing."]),
    (S("H03_invisible_strings", (1.0, 1.3, .5, .6, .5, .45), sfx=["villain"], head=("YOU DIDN'T [CHOOSE] THIS", 0)), ["You didn't choose any of this."]),
    (S("H03_invisible_strings", (1.5, 1.9, .5, .55, .5, .45), tint=(150, 60, 255), sfx=["whisper"],
       head=("SOMETHING ELSE [CHOSE]", 0)), ["Something else chose for you."]),
    (S("S52_billion_years", (1.5, 1.0, .5, .5, .5, .5), spin=True, sfx=["rewind"], big=("1,000,000,000", "YEARS OF EVOLUTION", 0), count=1e9),
     ["A billion years of evolution."]),
    (S("S27_tshirt_lab", (1.0, 1.35, .45, .5, .5, .4), smoke=True, sfx=["sniff", "mystery"], head=("[INVISIBLE] CLUES", 0)),
     ["Invisible clues your nose picks up without telling you."]),
    (S("S38_rose_glasses", (1.5, 2.0, .82, .78, .85, .8), zzz=(.85, .74), sfx=["snore"], head=("THE CRITIC: [OFF]", 0)),
     ["And a brain that quietly switches off its own critic."]),
    (S("S51_street_return", (1.0, 1.35, .5, .5, .5, .5), sparks=(.5, .45), sfx=["swell", "heartbeat"], mood=4,
       head=("BY THE END OF THIS VIDEO...", 0)), ["By the end of this video, you'll know exactly why her…"]),
    (S("H01_time_freeze", (1.6, 2.3, .3, .55, .3, .55), pulse=(.3, .6, .1, 1.2), sfx=["boom"], big=("WHY HER?", "", 0)), ["and not someone else."]),
    (S("N21_podium", (1.0, 1.1, .5, .5, .5, .5), hide=True, qmarks=True, sfx=["riser"], head=("THE [LAST] REASON?", 0)), ["And the last reason?"]),
    (S("N21_podium", (1.1, 1.3, .5, .5, .5, .5), hide=True, qmarks=True, sfx=["riser"], head=("ALMOST NOBODY TALKS ABOUT [THIS]", 0)),
     ["It's the one almost nobody talks about."]),
    (S("S54_endcard_bg", (1.0, 1.1, .5, .55, .5, .55), title=True, tail=5.0, sfx=["title"], mood=5,
       chars=[("MASCOT_lumi", .5, .78, 300, 0, 1.0, "pop")]), []),
]
SHOTS = RAW
