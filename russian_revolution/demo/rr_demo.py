"""Russian Revolution style demo (~65 s): the cold open in the stick-figure history-cartoon style.

Usage: python3 rr_demo.py out_dir [--preview]
"""
import math
import os
import subprocess
import sys

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stickgfx import (EMPIRE, H, HAND, PLACES, W, clamp, ellipse, fill_ol, grey_bg, hand_arrow, hand_text,  # noqa
                      hexc, lantern, lerp, line, map_bg, pin, poly, room_bg, rrect, sky_bg, smooth, stick,
                      year_tag, ensure_fonts)

FPS = 24
WPS = 140 / 60  # narration pace (words per second) of the earlier voiceovers

LINES = [
    "Yekaterinburg, Russia. The night of the sixteenth of July, 1918.",
    "It is past midnight. In a large house with whitewashed windows, a family is woken up and told to get dressed.",
    "There is fighting nearby, the guards tell them. For their own safety, they must move to the basement.",
    "A father carries his sick thirteen-year-old son down the stairs.",
    "His wife follows. Then four young daughters, their family doctor, and three loyal servants.",
    "They are told to wait. Chairs are brought for the mother and the boy.",
    "The father is a quiet, polite man with a neat beard.",
    "Just eighteen months earlier, he ruled one-sixth of the Earth's land surface.",
    "He commanded the largest army in the world. More than a hundred and seventy million people called him "
    "\"Little Father.\"",
    "His name is Nicholas Romanov. Tsar Nicholas the Second, the last Emperor of Russia.",
    "And the men who are about to walk into that basement are not there to protect him.",
    "How did the most powerful monarch in the world end up in a cellar in the Ural Mountains, with no throne, "
    "no army, and no friends?",
    "How did a country of peasants and priests become the first communist state in history?",
    "This is the story of the Russian Revolution.",
]
# timing per line (seconds): words / pace + a short breath
T = []
_t = 0.6
for ln in LINES:
    d = len(ln.split()) / WPS + 0.5
    T.append((_t, _t + d))
    _t += d
DUR = _t + 2.0


def L(i, frac=0.0):
    a, b = T[i]
    return a + (b - a) * frac


# ======================================================================== scenes
def s_map(c, t, lt):
    k = lerp(1.0, 1.9, smooth(lt / 5.0))
    x, y = PLACES["yekaterinburg"]
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(k, k)
    c.translate(-lerp(W / 2, x, smooth(lt / 5)), -lerp(H / 2, y, smooth(lt / 5)))
    map_bg(c)
    c.set_source_rgba(0, 0, 0.1, 0.25)
    c.paint()
    pin(c, x, y, t, appear=clamp((lt - 0.6) / 0.4))
    c.restore()
    hand_text(c, "Yekaterinburg", W / 2, H / 2 - 80, 56, lt - 1.4, outline=True)
    hand_text(c, "the Ural Mountains", W / 2, H / 2 + 110, 34, lt - 2.8, col=(1, 1, 1, 0.95), outline=True)
    year_tag(c, "1918")


def house(c, x, y, night=True):
    wall = hexc("#E8E2D6") if not night else hexc("#8E8A84")
    rrect(c, x - 260, y - 300, 520, 300, 4)
    fill_ol(c, wall, 3)
    poly(c, [(x - 280, y - 300), (x + 280, y - 300), (x + 230, y - 350), (x - 230, y - 350)])
    fill_ol(c, hexc("#5A6A7E") if not night else hexc("#2E3446"), 3)
    for row in range(2):
        for col in range(5):
            wx, wy = x - 220 + col * 92, y - 270 + row * 135
            rrect(c, wx, wy, 52, 80, 4)
            fill_ol(c, hexc("#F2EFE6") if row == 0 else hexc("#FFD98A"), 2.4)


def s_house(c, t, lt):
    sky_bg(c, t, night=True, horizon=520)
    house(c, 640, 560)
    for x in range(0, W, 26):  # tall fence
        rrect(c, x, 470, 22, 120, 3)
        fill_ol(c, hexc("#5A4030"), 1.6)
    stick(c, lerp(200, 1080, (lt / 6) % 1), 640, 1.1, "guard", t, walk=t * 6, arm_f=10)
    hand_text(c, "past midnight", W / 2, 130, 40, lt - 0.8)
    year_tag(c, "1918")


def s_bedroom(c, t, lt):
    room_bg(c, t, night=True)
    for i, x in enumerate((240, 470, 700)):
        rrect(c, x - 90, 470, 180, 60, 6)
        fill_ol(c, hexc("#E8E4DA"), 2)
        rrect(c, x - 90, 450, 30, 80, 4)
        fill_ol(c, hexc("#8A5A3A"), 2)
    up = smooth((lt - 1.5) / 0.8)
    for i, (x, who) in enumerate(((250, "nicholas"), (480, "alexandra"), (710, "daughter"))):
        if up < 0.5:
            ellipse(c, x - 40, 462, 22, 18)
            fill_ol(c, hexc("#F5D3B3"), 2)
        else:
            stick(c, x, 520, 1.2, who, t, arm_f=-20, mood="worried", look=1, extra=dict(hat=None))
    gx = lerp(1350, 1000, smooth(lt / 1.4))
    hx, hy = stick(c, gx, 680, 1.5, "guard", t, face=-1, walk=t * 6 if lt < 1.4 else None, arm_f=80,
                   talk=1.4 < lt < 3.5)
    lantern(c, hx, hy + 8, t)
    if lt > L(2) - L(1, 0.5):
        hand_arrow(c, 980, 300, 1150, 420, (lt - (L(2) - L(1, 0.5))) / 0.6)
        hand_text(c, "to the basement", 930, 270, 34, lt - (L(2) - L(1, 0.5)))
    year_tag(c, "1918")


def stairs_bg(c):
    room_bg(c, 0, night=False, dim=0.5)
    for i in range(10):
        x0 = 260 + i * 80
        y0 = 260 + i * 34
        rrect(c, x0, y0, 80, 34, 2)
        fill_ol(c, hexc("#8A6A48"), 2)
    line(c, (250, 220), (1070, 560), 6, hexc("#5A3A22"))


def s_stairs(c, t, lt):
    stairs_bg(c)
    u = clamp(lt / 4.5)
    x = lerp(300, 900, u)
    y = lerp(262, 540, u)
    hx, hy = stick(c, x, y, 1.3, "nicholas", t, walk=t * 5, arm_f=70, arm_b=60, extra=dict(hat=None), mood="worried")
    # Alexei carried in his arms
    c.save()
    c.translate(hx + 10, hy + 10)
    c.rotate(-1.2)
    stick(c, 0, 0, 0.9, "alexei", t, arm_f=20, eyes_closed=True)
    c.restore()
    hand_text(c, "13 years old", x + 170, y - 230, 30, lt - 1.2)
    hand_arrow(c, x + 120, y - 220, x + 40, y - 150, (lt - 1.6) / 0.5)
    hand_text(c, "haemophilia", x + 170, y - 190, 24, lt - 2.2, col=(1, 0.85, 0.75, 1))


def s_procession(c, t, lt):
    room_bg(c, t, wall="#BFB6A4", stripe="#B3A994", dim=0.25)
    who = ["alexandra", "daughter", "daughter", "daughter", "daughter", "doctor", "maid", "maid", "maid"]
    for i, w in enumerate(who):
        x = lerp(-150, 1700, lt / 9.0) - i * 150
        stick(c, x, 680, 1.4, w, t, walk=t * 5 + i, arm_f=10, mood="worried")
    labels = [("his wife", 0.3), ("4 daughters", 1.6), ("the doctor", 3.0), ("3 servants", 4.4)]
    for i, (txt, at) in enumerate(labels):
        end = labels[i + 1][1] if i + 1 < len(labels) else 99
        if at < lt < end:
            hand_text(c, txt, 640, 160, 44, lt - at)


def basement_bg(c, t):
    room_bg(c, t, wall="#A9A396", stripe="#9E988A", floor="#6E6254", dim=0.2)
    line(c, (640, 0), (640, 70), 3, hexc("#2A2A2A"))
    ellipse(c, 640, 82, 12, 14)
    c.set_source_rgba(1, 0.9, 0.6, 1)
    c.fill()
    g = cairo.RadialGradient(640, 82, 10, 640, 82, 650)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.25)
    c.set_source(g)
    c.paint()


def chair(c, x, y):
    rrect(c, x - 30, y - 120, 60, 70, 6)
    fill_ol(c, hexc("#8A5A3A"), 2)
    rrect(c, x - 34, y - 56, 68, 14, 3)
    fill_ol(c, hexc("#7A4A2A"), 2)
    for dx in (-28, 22):
        line(c, (x + dx + 3, y - 42), (x + dx + 3, y), 5, hexc("#5A3A22"))


def s_wait(c, t, lt):
    basement_bg(c, t)
    chair(c, 470, 680)
    chair(c, 600, 680)
    stick(c, 470, 680, 1.3, "alexandra", t, arm_f=30, mood="worried")
    stick(c, 600, 680, 1.3, "alexei", t, arm_f=30, mood="worried")
    for i, (x, w) in enumerate(((340, "nicholas"), (730, "daughter"), (820, "daughter"), (910, "daughter"),
                                (1000, "daughter"), (220, "doctor"), (1110, "maid"))):
        stick(c, x, 690, 1.3, w, t, arm_f=8, mood="worried", look=0.3, extra=dict(hat=None) if w == "nicholas"
              else None)
    hand_text(c, "\"wait here\"", 640, 170, 40, lt - 0.5)


def s_closeup(c, t, lt):
    basement_bg(c, t)
    k = 2.6
    stick(c, 640, 830, k, "nicholas", t, arm_f=10, mood="neutral", extra=dict(hat=None))
    hand_text(c, "quiet · polite · a neat beard", 640, 120, 36, lt - 0.6)


def s_empire(c, t, lt):
    map_bg(c)
    c.save()
    poly(c, EMPIRE)
    c.clip()
    c.set_source_rgba(1, 0.78, 0.2, 0.45 * smooth(lt / 1.2))
    c.paint()
    c.restore()
    poly(c, EMPIRE)
    c.set_line_width(4)
    c.set_source_rgba(1, 0.85, 0.3, smooth(lt / 1.2))
    c.stroke()
    hand_text(c, "the Russian Empire", 820, 300, 50, lt - 0.8)
    hand_text(c, "1/6 of the Earth's land", 820, 360, 34, lt - 2.0, col=(1, 0.95, 0.75, 1))
    year_tag(c, "1916")


def s_army(c, t, lt):
    sky_bg(c, t)
    for row in range(4):
        for i in range(16):
            x = 420 + i * 55 + row * 18
            stick(c, x, 520 + row * 40, 0.55 + row * 0.06, "guard", t, arm_f=150 if (lt > 1 + i * 0.05) else 10,
                  extra=dict(col="#6E6A4E", legs="#4E4A38", hatcol="#6E6A4E", moustache=None))
    stick(c, 210, 680, 1.35, "nicholas", t, arm_f=120, mood="happy")
    hand_text(c, "the largest army in the world", 700, 120, 42, lt - 0.6)


def s_people(c, t, lt):
    sky_bg(c, t)
    rrect(c, 520, 120, 240, 300, 10)
    fill_ol(c, hexc("#E9B93A"), 4)
    stick(c, 640, 400, 1.2, "nicholas", t, arm_f=10, mood="happy")
    for row in range(3):
        for i in range(14):
            x = 60 + i * 90 + (row % 2) * 40
            bow = 40 if (lt * 2 + i * 0.3) % 2 < 1 else 0
            c.save()
            c.translate(x, 560 + row * 55)
            c.rotate(math.radians(bow * 0.4))
            stick(c, 0, 0, 0.55, "peasant", t + i, arm_f=60, look=1, extra=None if i % 2 else
                  dict(col="#C9705A", beard=None, hair="#5A3A2A"))
            c.restore()
    hand_text(c, "170,000,000 people", 640, 90, 46, lt - 0.5)
    hand_text(c, "\"Little Father\"", 1040, 260, 34, lt - 2.5, col=(1, 0.9, 0.6, 1))


def throne_room(c, t):
    c.set_source_rgba(*hexc("#7A1F2E"))
    c.paint()
    for x in range(80, W, 220):
        rrect(c, x, 60, 40, 520, 6)
        fill_ol(c, hexc("#E9B93A"), 2)
    c.rectangle(0, 580, W, H)
    c.set_source_rgba(*hexc("#5A2A1E"))
    c.fill()
    rrect(c, 480, 590, 320, 130, 4)
    c.set_source_rgba(*hexc("#B5293A"))
    c.fill()


def s_throne(c, t, lt):
    throne_room(c, t)
    rrect(c, 560, 260, 160, 330, 30)
    fill_ol(c, hexc("#E9B93A"), 3)
    rrect(c, 580, 290, 120, 220, 20)
    fill_ol(c, hexc("#9C2A3A"), 2)
    stick(c, 640, 640, 1.45, "nicholas", t, arm_f=40, mood="neutral", extra=dict(hat="crown"), talk=False)
    hand_text(c, "Nicholas Romanov", 330, 230, 40, lt - 0.4)
    hand_arrow(c, 380, 250, 560, 330, (lt - 1.0) / 0.5)
    hand_text(c, "Tsar Nicholas II", 330, 290, 30, lt - 2.0, col=(1, 0.9, 0.6, 1))
    hand_text(c, "the last Emperor of Russia", 940, 640, 30, lt - 3.4)
    year_tag(c, "1894 – 1917")


def s_door(c, t, lt):
    c.set_source_rgba(*hexc("#2A2622"))
    c.paint()
    rrect(c, 520, 160, 240, 420, 8)
    fill_ol(c, hexc("#5A4030"), 4)
    ellipse(c, 730, 380, 9, 9)
    c.set_source_rgba(*hexc("#C9A23A"))
    c.fill()
    for i in range(4):
        x = lerp(1400, 820, smooth(lt / 3.0)) + i * 90
        c.save()
        c.translate(x, 620)
        c.scale(1.6, 1.6)
        stick(c, 0, 0, 1.0, "guard", t, face=-1, walk=t * 4 + i,
              extra=dict(col="#000000", legs="#000000", hatcol="#000000", skin="#000000", hair="#000000",
                                                     moustache="#000000"))
        c.restore()
    c.set_source_rgba(0, 0, 0, 0.35)
    c.paint()
    hand_text(c, "not there to protect him", 640, 110, 40, lt - 1.0, col=(1, 0.85, 0.8, 1))


def s_host_q(c, t, lt):
    grey_bg(c)
    stick(c, 300, 640, 1.45, "host", t, arm_f=120 if lt > 1 else 20, talk=True, mood="neutral", look=1)
    c.select_font_face(HAND, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    k = smooth((lt - 0.6) / 0.4)
    if k > 0:
        c.save()
        c.translate(820, 360)
        c.scale(k, k)
        c.set_font_size(260)
        c.move_to(-60, 90)
        c.set_source_rgba(*hexc("#C8322F"))
        c.show_text("?")
        c.restore()
    items = [("no throne", 1.6), ("no army", 2.6), ("no friends", 3.6)]
    for i, (txt, at) in enumerate(items):
        hand_text(c, txt, 1060, 260 + i * 70, 40, lt - at, col=hexc("#2B2420"), shadow=False)


def s_host_flag(c, t, lt):
    grey_bg(c)
    stick(c, 260, 640, 1.45, "host", t, arm_f=110, talk=True, look=1)
    stick(c, 640, 620, 1.1, "peasant", t)
    stick(c, 760, 620, 1.1, "peasant", t, extra=dict(col="#1E1E22", legs="#1E1E22", beard="#3A2A1E",
                                                         hat="crown", belt=None))
    k = smooth((lt - 2.0) / 0.5)
    if k > 0:
        x = 1020
        line(c, (x, 640), (x, 640 - 380 * k), 6, hexc("#5A3A22"))
        poly(c, [(x, 640 - 380 * k), (x + 180, 640 - 380 * k + 10 + 8 * math.sin(t * 5)),
                 (x + 180, 640 - 380 * k + 110), (x, 640 - 380 * k + 100)])
        fill_ol(c, hexc("#D2222A"), 2)
    hand_text(c, "peasants & priests", 700, 260, 38, lt - 0.4, col=hexc("#2B2420"), shadow=False)
    hand_text(c, "the first communist state", 1010, 160, 36, lt - 2.6, col=hexc("#C8322F"), shadow=False)


def palace(c, x, y):
    rrect(c, x - 520, y - 220, 1040, 220, 2)
    fill_ol(c, hexc("#7FB59A"), 3)
    for k in range(-12, 13):
        line(c, (x + k * 42, y - 210), (x + k * 42, y - 10), 7, hexc("#F4F1EA"))
    for k in range(-11, 12):
        rrect(c, x + k * 42 - 10, y - 160, 20, 40, 8)
        c.set_source_rgba(*hexc("#4A5A6A"))
        c.fill()
    for k in range(-12, 13, 2):
        ellipse(c, x + k * 42, y - 232, 7, 12)
        c.set_source_rgba(*hexc("#C9A23A"))
        c.fill()


def s_title(c, t, lt):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexc("#F2A65A"))
    g.add_color_stop_rgba(1, *hexc("#FBD9A0"))
    c.set_source(g)
    c.paint()
    c.rectangle(0, 600, W, H)
    c.set_source_rgba(*hexc("#6A7A8A"))
    c.fill()
    palace(c, 640, 600)
    x = 640
    line(c, (x, 380), (x, 160), 6, hexc("#3A2A1E"))
    wave = math.sin(t * 4)
    poly(c, [(x, 160), (x + 200, 170 + 8 * wave), (x + 200, 280 + 8 * wave), (x, 270)])
    fill_ol(c, hexc("#D2222A"), 2)
    hand_text(c, "The Russian Revolution", 640, 470, 86, lt - 0.3, col=(1, 1, 1, 1), outline=True)
    year_tag(c, "1917")


SCENES = [
    (L(0), s_map), (L(1), s_house), (L(1, 0.5), s_bedroom), (L(3), s_stairs), (L(4), s_procession),
    (L(5), s_wait), (L(6), s_closeup), (L(7), s_empire), (L(8), s_army), (L(8, 0.45), s_people), (L(9), s_throne),
    (L(10), s_door), (L(11), s_host_q), (L(12), s_host_flag), (L(13), s_title),
]
SCENES[0] = (0.0, s_map)


def subtitle(c, t):
    for i, (a, b) in enumerate(T):
        if a <= t < b:
            txt = LINES[i]
            c.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            size = 26
            c.set_font_size(size)
            words = txt.split()
            lines, cur = [], ""
            for w in words:
                trial = (cur + " " + w).strip()
                if c.text_extents(trial).x_advance > 1050:
                    lines.append(cur)
                    cur = w
                else:
                    cur = trial
            lines.append(cur)
            y0 = H - 40 - 34 * (len(lines) - 1)
            for k, ln in enumerate(lines):
                e = c.text_extents(ln)
                c.move_to(W / 2 - e.x_advance / 2, y0 + k * 34)
                c.text_path(ln)
                c.set_line_width(5)
                c.set_source_rgba(0, 0, 0, 0.75)
                c.stroke_preserve()
                c.set_source_rgba(1, 1, 1, 1)
                c.fill()


def frame(c, t):
    idx = 0
    for i, (s, _) in enumerate(SCENES):
        if s <= t:
            idx = i
    s, fn = SCENES[idx]
    c.save()
    c.set_source_rgb(0, 0, 0)
    c.paint()
    fn(c, t, t - s)
    c.restore()
    lt = t - s
    if idx > 0 and lt < 0.12:  # quick soft cut
        c.set_source_rgba(1, 1, 1, 0.25 * (1 - lt / 0.12))
        c.paint()
    subtitle(c, t)
    a = max(clamp(1 - t / 0.6), clamp((t - (DUR - 1.2)) / 1.2))
    if a > 0:
        c.set_source_rgba(0, 0, 0, a)
        c.paint()


def main():
    ensure_fonts()
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    if "--preview" in sys.argv:
        for i, (s, fn) in enumerate(SCENES):
            e = SCENES[i + 1][0] if i + 1 < len(SCENES) else DUR
            frame(c, s + (e - s) * 0.7)
            surf.write_to_png(os.path.join(out, f"d{i + 1:02d}.png"))
        return
    path = os.path.join(out, "video_only.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s",
                          f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        frame(c, f / FPS)
        surf.flush()
        p.stdin.write(surf.get_data())
    p.stdin.close()
    p.wait()
    print("wrote", path, round(DUR, 1), "s")


if __name__ == "__main__":
    main()
