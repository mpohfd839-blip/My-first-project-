"""Napoleonic Wars timeline for the shared WWI renderer: the 135 cartoon scenes merged with the
58 period images, each tied to its narration cue.

Used via BEATS_MODULE=nap_beats with world_war_1/video/ww1_render.py and ww1_soundtrack.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

import gfx  # noqa: E402
from make_prompts import S as CART_CUES  # noqa: E402
from make_real_image_prompts import I as IMG_CUES  # noqa: E402
from scenes import SCENES  # noqa: E402
from soundtrack import SFX  # noqa: E402

WORDS = os.environ.get("WORDS", os.path.join(HERE, "words.json"))


def _w(fn, **kw):
    return lambda c, x, y, s, t: fn(c, x, y, s, t=t, **kw)


# image number -> (label, overlay, sfx, extra)
IMG = {
    1: ("WATERLOO · 18 JUNE 1815", "fog+rain", "rainH wind", {}),
    2: ("WELLINGTON'S ARMY", "rain", "rain march", {}),
    3: ("NAPOLEON BONAPARTE", None, "impact@0", dict(who=_w(gfx.napoleon, arms="point"), name="NAPOLEON BONAPARTE")),
    4: ("1789 · THE BASTILLE FALLS", "smoke+embers", "angry cannonD@1", {}),
    5: ("KING LOUIS XVI", None, "murmur", dict(who=_w(gfx.king, arms="shrug", expr="worried"), name="KING LOUIS XVI")),
    6: ("AJACCIO · CORSICA", "light", "sea gulls", {}),
    7: ("TOULON · 1793", "embers+flash", "cannon*3 sea", {}),
    8: ("THE ARMY OF ITALY · 1796", None, "wind march", {}),
    9: ("THE BRIDGE AT ARCOLE", "smoke", "marchH volley*2", {}),
    10: ("1798 · TO EGYPT", "sea", "sea gulls", {}),
    11: ("THE BATTLE OF THE PYRAMIDS", "smoke", "volley*3 gallopH", {}),
    12: ("THE NILE · 1798", "embers", "explosion@0.5 sea", {}),
    13: ("THE ROSETTA STONE", None, "room", dict(mode="frame:desk")),
    14: ("THE COUP · NOVEMBER 1799", None, "panic", {}),
    15: ("FIRST CONSUL", None, "room", dict(who=_w(gfx.young_nap, arms="point"), name="FIRST CONSUL BONAPARTE")),
    16: ("ACROSS THE ALPS", "snow", "blizzard", {}),
    17: ("MARENGO · 1800", "smoke", "volley*2 cannon*2", {}),
    18: ("THE NAPOLEONIC CODE · 1804", None, "quill", dict(mode="frame:desk")),
    19: ("CORONATION · 2 DECEMBER 1804", "light", "bellL@0.3 murmur", {}),
    20: ("BOULOGNE · INVASION ARMY", None, "sea march", {}),
    21: ("TRAFALGAR · 21 OCTOBER 1805", "smoke+sea", "sea cannon*4", {}),
    22: ("ADMIRAL NELSON", None, "sea", dict(who=_w(gfx.nelson, arms="point"), name="ADMIRAL HORATIO NELSON")),
    23: ("THE DEATH OF NELSON", "smoke", "sea heart", {}),
    24: ("ULM · OCTOBER 1805", None, "march", {}),
    25: ("AUSTERLITZ · 2 DECEMBER 1805", "fog", "marchH cannonD*2", {}),
    26: ("THE SUN OF AUSTERLITZ", "light", "cheer", {}),
    27: ("BERLIN · 1806", None, "march gallop", {}),
    28: ("EYLAU · 1807", "snow", "blizzard gallopH", {}),
    29: ("TILSIT · JULY 1807", None, "river cheer", {}),
    30: ("EUROPE · 1810", None, "whoosh@0", dict(legend=[("FRENCH EMPIRE & ALLIES", "#7FA6D8"),
                                                       ("BRITAIN", "#D86A6A"), ("RUSSIA", "#9CC48A")])),
    31: ("MADRID · 2 MAY 1808", "smoke", "angry volley*2", {}),
    32: ("3 MAY 1808", None, "heart volley@1.5", {}),
    33: ("ARTHUR WELLESLEY", None, "sea march",
         dict(who=_w(gfx.wellington, arms="point"), name="ARTHUR WELLESLEY", bg="field")),
    34: ("WAGRAM · 1809", "smoke+flash", "cannon*5", {}),
    35: ("EMPRESS JOSÉPHINE", None, "heart",
         dict(who=_w(gfx.lady, expr="sad", arms="hand_in"), name="EMPRESS JOSÉPHINE")),
    36: ("EMPRESS MARIE-LOUISE", None, "bell@0.3",
         dict(who=_w(gfx.lady, hair_col="#D8B66A", expr="happy"), name="EMPRESS MARIE-LOUISE")),
    37: ("TSAR ALEXANDER I", None, "room", dict(who=_w(gfx.tsar, arms="point"), name="TSAR ALEXANDER I")),
    38: ("THE NIEMEN · JUNE 1812", None, "marchH river", {}),
    39: ("BORODINO · 7 SEPTEMBER 1812", "smoke+flash", "cannon*6 volley*2", {}),
    40: ("MOSCOW BURNS", "embers", "fireH", {}),
    41: ("THE RETREAT FROM MOSCOW", "snow", "blizzard", {}),
    42: ("THE BEREZINA", "snow", "river blizzard", {}),
    43: ("LEIPZIG · OCTOBER 1813", "smoke", "cannon*5 volley*2", {}),
    44: ("FAREWELL AT FONTAINEBLEAU", None, "heart", {}),
    45: ("EXILE ON ELBA", "light", "sea gulls", {}),
    46: ("THE CONGRESS OF VIENNA", None, "murmur", dict(mode="frame:board")),
    47: ("GRENOBLE · MARCH 1815", None, "heart wind", {}),
    48: ("PARIS · 20 MARCH 1815", "light", "cheer bell@0.5", {}),
    49: ("WATERLOO", "smoke", "cannon*3 marchH", {}),
    50: ("HOUGOUMONT", "embers+smoke", "fire volley*3", {}),
    51: ("NEY'S CAVALRY CHARGES", "smoke", "gallopH volley*3", {}),
    52: ("THE IMPERIAL GUARD", "smoke", "marchH volley*2", {}),
    53: ("SAINT HELENA", "fog", "sea wind", {}),
    54: ("5 MAY 1821", None, "clock heart", dict(mode="frame:desk", zoom=1.25)),
    55: ("THE COST", "embers", "wind", {}),
    56: ("EUROPE · 1815", None, "whoosh@0", dict(legend=[("THE CONGRESS OF VIENNA", "#C9A06A")])),
    57: ("LES INVALIDES · PARIS", "light", "bellL@0.5", {}),
    58: ("WATERLOO TODAY", "light", "wind birds", {}),
}
MODE = {"FULL": "full", "OUTRO": "full", "MAP": "map", "SPLIT": "split", "FRAME": "frame:board"}


def _build():
    d = json.load(open(WORDS))
    text = "\n".join(d["lines"])
    words = d["words"]

    def t_of(pos):
        return words[len(text[:pos].split())]["s"]

    items = []
    last = 0
    for i, ((cue, _), sc) in enumerate(zip(CART_CUES, SCENES)):
        pos = text.find(cue, last)
        last = pos + 1
        items.append((pos, 1, dict(kind="cart", fn=sc["fn"], cue=cue, label=sc["label"], sfx=SFX.get(i + 1, ""),
                                   mood="tense", focus=sc["focus"], zoom=sc["zoom"])))
    last = 0
    for n, (cue, typ, use, _) in enumerate(IMG_CUES, 1):
        pos = text.find(cue, last)
        last = pos + 1
        label, ov, sfx, extra = IMG[n]
        b = dict(kind="img", n=n, cue=cue, mode=MODE[use], ov=ov, label=label, sfx=sfx, mood="tense",
                 legend=None, bg="hall", who=None, name=None, kb=None, zoom=None)
        b.update(extra)
        items.append((pos, 0, b))
    items.sort(key=lambda x: (x[0], x[1]))
    # same position: keep the image; remember the cartoon so it can follow a long image
    merged = []
    shadow = {}
    for pos, pri, b in items:
        if merged and merged[-1][0] == pos:
            shadow[id(merged[-1][2])] = b
            continue
        merged.append((pos, pri, b))
    # drop cartoon beats that would flash by too quickly, and give images at least 3.5 s
    changed = True
    while changed:
        changed = False
        times = [t_of(p) for p, _, _ in merged]
        for i in range(len(merged) - 1):
            dur = times[i + 1] - times[i]
            b, nxt = merged[i][2], merged[i + 1][2]
            if b["kind"] == "cart" and dur < 2.5 and i > 0:
                merged.pop(i)
                changed = True
                break
            if b["kind"] == "img" and nxt["kind"] == "cart" and dur < 3.5:
                merged.pop(i + 1)
                changed = True
                break
    # long images (> 9 s): let the matching cartoon take over halfway through
    times = [t_of(p) for p, _, _ in merged] + [d["duration"]]
    out = []
    for i, (_, _, b) in enumerate(merged):
        out.append(b)
        dur = times[i + 1] - times[i]
        if b["kind"] == "img" and dur > 9 and id(b) in shadow:
            f = dict(shadow[id(b)])
            f["follow"] = 0.5
            out.append(f)
    return out


BEATS = _build()
