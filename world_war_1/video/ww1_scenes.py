"""WWI timeline: cartoon scenes + the 79 real images, each tied to a narration cue.

Every beat: cue (text in narration.txt where it starts), what to draw, headline label,
sound effects (see soundtrack tokens) and music mood.
"""
import math
import random

from ww1gfx import *  # noqa: F401,F403
import ww1gfx as G

BEATS = []
_mood = ["tense"]


def _add(d):
    if "mood" in d and d["mood"]:
        _mood[0] = d["mood"]
    d["mood"] = _mood[0]
    BEATS.append(d)


def img(n, cue, mode="full", ov=None, label=None, sfx="", mood=None, legend=None, bg="hall", who=None, name=None,
        kb=None):
    _add(dict(kind="img", n=n, cue=cue, mode=mode, ov=ov, label=label, sfx=sfx, mood=mood, legend=legend, bg=bg,
              who=who, name=name, kb=kb))


def cart(cue, label=None, sfx="", mood=None, focus=(640, 360), zoom=0.07):
    def deco(f):
        _add(dict(kind="cart", fn=f, cue=cue, label=label, sfx=sfx, mood=mood, focus=focus, zoom=zoom))
        return f
    return deco


C = G.wcentroid
PARIS = (452, 345)


def mapscene(c, t, u, colors=None, arrows=(), pulses=(), base=None, glow=None, labels=True):
    ww1map(c, t, colors=colors, base=base, glow=glow, labels=labels)
    for pts, col in arrows:
        arrow(c, pts, smooth(u * 1.6), col)
    for (x, y), col in pulses:
        pulse_dot(c, x, y, t, col)


def street_bg(c, t, night=False, skyk="day"):
    sky(c, "night" if night else skyk, 520)
    if not night:
        clouds(c, t, n=3)
    building_row(c, 470, t, seed=21, cols=("#E9DCC4", "#E3CFA8", "#F2E6D2", "#D9C3A0"), night=night)
    c.set_source(vgrad(c, 470, H, hexc("#B9A98C"), hexc("#9A8A6E")))
    c.rectangle(0, 470, W, H)
    c.fill()
    for k in range(0, W, 120):
        seg(c, (k, 560), (k + 60, 560), 4, (1, 1, 1, 0.4))


def ff_riders(c):
    char(c, "ff", 70, -60, 0.62, seated=True, t=0, arms="up")
    char(c, "sophie", 10, -60, 0.6, t=0, face=1)


# ======================================================================== SARAJEVO
img(1, "Sarajevo. The twenty-eighth of June, 1914.", ov="light", label="SARAJEVO · 28 JUNE 1914",
    sfx="murmur birds bell@1 impact@0", mood="tense")


@cart("An open-topped car rolls slowly", "ARCHDUKE FRANZ FERDINAND", sfx="murmur car")
def s_car(c, u, t):
    street_bg(c, t)
    crowd(c, 0, 1280, 520, rows=2, s=0.55, t=t, flags=["ah", "ah"], cheer=True)
    old_car(c, 200 + 700 * u, 660, 1.2, 1, t, col="#2A2A2E", riders=lambda cc: (
        char(cc, "sophie", -30, -60, 0.75, t=t), char(cc, "ff", 60, -60, 0.8, t=t, arms="up")))


img(2, "Inside sits Archduke Franz Ferdinand", label="FRANZ FERDINAND & SOPHIE", sfx="murmur")


@cart("Hidden in the crowd", "THE ASSASSINS", sfx="heart murmur", mood="dark", zoom=0.12, focus=(640, 520))
def s_assassins(c, u, t):
    street_bg(c, t)
    crowd(c, 0, 1280, 640, rows=3, s=0.75, t=t, cheer=False, expr="neutral")
    for i, x in enumerate((240, 640, 1000)):
        char(c, "gentleman", x, 700, 0.95, t=t, expr="stern", coat="#1E1E22", trou="#1E1E22", hat="bowler",
             look=1 if i % 2 else -1)
    tint(c, (0.1, 0.05, 0.1), 0.25)
    vignette(c, 0.6)


@cart("One of them throws a bomb.", "A BOMB!", sfx="explosion@1.2 panic", mood="tense")
def s_bomb(c, u, t):
    street_bg(c, t)
    crowd(c, 0, 1280, 520, rows=2, s=0.55, t=t, cheer=False, expr="shock", arms="up")
    old_car(c, 820 + 300 * u, 660, 1.0, 1, t, riders=lambda cc: char(cc, "ff", 40, -60, 0.8, t=t, expr="shock"))
    old_car(c, 300 + 100 * u, 670, 1.0, 1, t, col="#3A3A42")
    explosion(c, 330, 600, (t - 1.2) / 1.6, 1.4)
    if t > 1.2:
        smoke(c, 330, 560, t, n=7, s=1.6, col=(0.3, 0.3, 0.3), rise=140)


@cart("The Archduke survives.", "THE PLAN FAILS", sfx="murmur")
def s_survive(c, u, t):
    street_bg(c, t)
    old_car(c, 640, 660, 1.4, 1, t, riders=lambda cc: (char(cc, "sophie", -30, -60, 0.75, t=t, expr="worried"),
                                                       char(cc, "ff", 60, -60, 0.8, t=t, expr="angry")),
            moving=False)


img(3, "One of the assassins", mode="split", who="princip", name="GAVRILO PRINCIP · 19", bg="street",
    label="GAVRILO PRINCIP", sfx="heart")


@cart("And then, by pure chance", "A WRONG TURN", sfx="car whoosh@0.5", mood="tense")
def s_turn(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#E9DCC4"), hexc("#D9C3A0")))
    c.paint()
    for x in range(0, W, 210):
        for y in range(0, H, 190):
            rrect(c, x + 20, y + 20, 170, 150, 8)
            fill(c, hexc("#C9B48E"))
    seg(c, (0, 380), (W, 380), 50, hexc("#9A8A6E"))
    seg(c, (640, 380), (640, 720), 50, hexc("#9A8A6E"))
    arrow(c, [(80, 380), (600, 380), (640, 420), (640, 640)], smooth(u * 1.4), "#C8322F", 14, 30)
    old_car(c, lerp(100, 600, smooth(u * 1.3)), 400, 0.35, 1, t)
    pulse_dot(c, 700, 440, t)


@cart("The driver stops.", "THE ENGINE STALLS", sfx="heart", mood="dark", zoom=0.14, focus=(500, 520))
def s_stall(c, u, t):
    street_bg(c, t)
    old_car(c, 760, 660, 1.3, -1, t, riders=lambda cc: (char(cc, "sophie", -30, -60, 0.75, t=t),
                                                        char(cc, "ff", 60, -60, 0.8, t=t)), moving=False)
    if (t % 1.2) < 0.6:
        smoke(c, 940, 640, t, n=4, s=0.6, col=(0.4, 0.4, 0.4), rise=60)
    char(c, "princip", 260, 700, 1.5, t=t, expr="shock", look=1)


@cart("Princip steps forward", "TWO SHOTS", sfx="shot@1.0 shot@1.5 heart", zoom=0.1, focus=(400, 450))
def s_shots(c, u, t):
    street_bg(c, t)
    old_car(c, 820, 660, 1.3, -1, t, moving=False, riders=lambda cc: (char(cc, "sophie", -30, -60, 0.75, t=t),
                                                                       char(cc, "ff", 60, -60, 0.8, t=t,
                                                                            expr="shock")))
    char(c, "princip", 330, 700, 1.6, t=t, expr="angry", arms="aim")
    for tt in (1.0, 1.5):
        if 0 < t - tt < 0.12:
            ellipse(c, 330 + 150, 700 - 160 * 1.6 * 0.62, 30, 20)
            fill(c, (1, 0.9, 0.4, 0.95))
            tint(c, (1, 1, 1), 0.3)


img(4, "Within minutes, the Archduke and his wife are dead.", label="28 JUNE 1914", sfx="panic")
img(5, "Two bullets. Fired by a teenager.", ov="light", label="TWO BULLETS", sfx="heart")


@cart("Those two bullets would start a war", "15 MILLION DEAD · 4 EMPIRES FALL", sfx="rwhoosh@0 impact@1.5",
      mood="epic")
def s_toll(c, u, t):
    mapscene(c, t, u, base="blocs")
    for i, (x, y) in enumerate(((460, 400), (600, 330), (720, 290), (1000, 320), (712, 400), (1000, 525))):
        if u > i * 0.12:
            flames(c, x, y + 20, 90, 90, t, seed=i)
    tint(c, (0.2, 0.05, 0), 0.25)


@cart("This is the story of the First World War.", "THE FIRST WORLD WAR · 1914–1918", sfx="impact@0 wind",
      zoom=0.04)
def s_title(c, u, t):
    sky(c, "sunset")
    sun(c, 640, 430, 90, "#FFD27A", t, rays=True)
    c.set_source_rgba(*hexc("#2A1C1C"))
    c.rectangle(0, 560, W, H)
    c.fill()
    barbed_wire(c, -20, W + 20, 600, 1.4, (0.1, 0.07, 0.06, 1))
    for i, x in enumerate((360, 520, 760, 920)):
        soldier(c, x, 600, 1.1, "tommy", t, walk=t * 3 + i, coat="#1A1212", trou="#1A1212", skin=hexc("#1A1212"),
                blink=False, hat="brodie")
    poppies(c, 640, 720, t, n=60)


# ======================================================================== EUROPE 1914
img(6, "To understand how two bullets could set the world on fire", mode="map", label="EUROPE · 1914",
    sfx="whoosh@0 clock", mood="calm")


@cart("On the surface, it was a golden age.", "A GOLDEN AGE", sfx="birds")
def s_golden(c, u, t):
    landscape(c, t, "day", "grass", 430, seed=31, sunpos=(1050, 140))
    seg(c, (0, 560), (W, 540), 6, hexc("#5A4A3A"))
    train(c, -300 + 1500 * u, 560, 0.7, 1, t, cars=3, col="#7A2E2E")
    building_row(c, 470, t, seed=3, h0=60, h1=120)


img(7, "Cities glowed with electric light.", ov="light", sfx="murmur")


@cart("But underneath, Europe was a powder keg.", "A POWDER KEG", sfx="heart", mood="dark", zoom=0.12,
      focus=(640, 420))
def s_keg(c, u, t):
    mapscene(c, t, u, base="blocs", labels=False)
    tint(c, (0, 0, 0), 0.35)
    c.save()
    c.translate(640, 520)
    rrect(c, -120, -200, 240, 260, 50)
    fill_ol(c, hexc("#8A5A32"), INK, 4)
    for y in (-160, -70, 20):
        seg(c, (-118, y), (118, y), 12, hexc("#4A4A4A"))
    c.select_font_face("DejaVu Sans", 0, 1)
    c.set_font_size(34)
    c.move_to(-80, -90)
    c.set_source_rgba(0.95, 0.9, 0.8, 1)
    c.show_text("EUROPE")
    c.move_to(0, -200)
    c.curve_to(30, -260, 90, -260, 110 - 60 * u, -300 + 40 * u)
    c.set_line_width(5)
    c.set_source_rgba(0.2, 0.15, 0.1, 1)
    c.stroke()
    for k in range(6):
        a = t * 9 + k
        ellipse(c, 110 - 60 * u + math.cos(a) * 10, -300 + 40 * u + math.sin(a) * 10, 4, 4)
        fill(c, hexc("#FFD43B"))
    c.restore()


img(8, "Britain had the largest navy", ov="sea+smoke", label="THE ROYAL NAVY", sfx="sea")
img(9, "Germany, a young and ambitious nation", mode="split", who="kaiser", name="KAISER WILHELM II",
    label="GERMANY", sfx="march")


@cart("France had never forgotten", "ALSACE-LORRAINE · LOST 1871", sfx="whoosh@0.3")
def s_alsace(c, u, t):
    mapscene(c, t, u, colors={"france": "#8FA8E0", "germany": "#C9A06A"}, pulses=[((528, 352), "#C8322F")])
    poly(c, [(522, 320), (548, 320), (552, 380), (526, 384)])
    c.set_source_rgba(0.8, 0.2, 0.2, 0.5 + 0.2 * math.sin(t * 3))
    c.fill()


@cart("Russia saw itself as the protector", "RUSSIA · PROTECTOR OF THE SLAVS")
def s_russia(c, u, t):
    mapscene(c, t, u, colors={"russia": "#B8D6A8", "serbia": "#E79A94", "balkans": "#F2D9A0"},
             arrows=[([(980, 330), (880, 400), (790, 460)], "#3E7A3E")])
    char(c, "tsar", 1120, 720, 1.5, face=-1, arms="point", t=t)


@cart("And Austria-Hungary, an old and fragile empire", "AUSTRIA-HUNGARY", sfx="crack@1")
def s_austria(c, u, t):
    mapscene(c, t, u, colors={"austria": "#F2F2F2"})
    c.set_line_width(4)
    c.set_source_rgba(0.2, 0.1, 0.05, 0.9)
    pts = [(640, 380), (680, 400), (700, 390), (730, 420), (760, 410), (790, 430)]
    c.move_to(*pts[0])
    for p in pts[1:max(2, int(len(pts) * u * 1.5))]:
        c.line_to(*p)
    c.stroke()
    char(c, "franzj", 170, 720, 1.5, t=t, expr="worried")


@cart("For years, they had been building armies", "THE ARMS RACE", sfx="march sea")
def s_arms(c, u, t):
    sky(c, "grey", 420)
    sea(c, t, 380)
    for i, x in enumerate((-200 + 300 * u, 500 + 200 * u)):
        dreadnought(c, x, 520, 0.6, 1, t)
    c.set_source(vgrad(c, 560, H, hexc("#8A9A6A"), hexc("#6A7A4A")))
    c.rectangle(0, 560, W, H)
    c.fill()
    army(c, -100, 600, 700, rows=2, s=0.55, uni="hun14", t=t, march=True, flags="de")
    army(c, 700, 1400, 700, rows=2, s=0.55, uni="poilu14", t=t, march=True, face=-1, flags="fr")


img(10, "On one side stood the Triple Entente", mode="map", label="TWO ALLIANCES",
    legend=[("TRIPLE ENTENTE", ENTENTE), ("CENTRAL POWERS", CENTRAL)], sfx="whoosh@0")


@cart("These alliances were meant to keep the peace.", "ALLIANCES", sfx="crack@1.5")
def s_chains(c, u, t):
    mapscene(c, t, u, base="blocs")
    links = [((385, 230), (460, 400)), ((460, 400), (1000, 320)), ((580, 330), (712, 400))]
    for (a, b) in links:
        n = 14
        for k in range(n):
            x, y = lerp(a[0], b[0], k / n), lerp(a[1], b[1], k / n)
            ellipse(c, x, y, 12, 7, rot=math.atan2(b[1] - a[1], b[0] - a[0]) + (k % 2) * 1.5)
            c.set_line_width(4)
            c.set_source_rgba(0.3, 0.3, 0.32, 1)
            c.stroke()


DOMS = ["rs", "ah", "ru", "de", "fr", "be", "uk"]


def dominos(c, t, k0, k1, u):
    sky(c, "dusk", H)
    c.set_source(vgrad(c, 560, H, hexc("#5A4030"), hexc("#3A2A1E")))
    c.rectangle(0, 600, W, H)
    c.fill()
    p = lerp(k0, k1, smooth(u * 1.4))
    for i, kind in enumerate(DOMS):
        a = clamp(p - i) * 1.18
        domino(c, 160 + i * 150, 620, a, kind, 1.25)


@cart("Instead, they turned a local quarrel into a chain reaction.", "A CHAIN REACTION", sfx="whoosh@0.5")
def s_dom0(c, u, t):
    dominos(c, t, 0, 0.15 * math.sin(t * 3) ** 2, u)


# ======================================================================== JULY CRISIS
@cart("Austria-Hungary blamed Serbia for the assassination.", "AUSTRIA BLAMES SERBIA", mood="tense")
def s_blame(c, u, t):
    mapscene(c, t, u, colors={"austria": "#F2F2F2", "serbia": "#E79A94"},
             arrows=[([(700, 400), (740, 430), (765, 455)], "#C8322F")], pulses=[((770, 465), "#C8322F")])
    char(c, "franzj", 1100, 720, 1.5, face=-1, arms="point", expr="angry", t=t)


@cart("Germany promised Austria its full support.", "THE BLANK CHEQUE", sfx="quill")
def s_cheque(c, u, t):
    hall(c, t)
    char(c, "kaiser", 400, 690, 1.7, arms="hold", item="paper", expr="smirk", t=t)
    char(c, "franzj", 880, 690, 1.7, face=-1, arms="hold", expr="happy", t=t)
    poly(c, [(520, 520), (720, 500), (730, 580), (530, 600)])
    fill_ol(c, hexc("#F4EAD0"), hexc("#8A7A5A"), 2)
    c.select_font_face("DejaVu Serif", 0, 1)
    c.set_font_size(22)
    c.move_to(560, 556)
    c.set_source_rgba(0.3, 0.2, 0.1, 1)
    c.show_text("PAY: ∞")


img(11, "On the twenty-third of July, Austria sent Serbia an ultimatum", ov="light",
    label="THE ULTIMATUM · 23 JULY 1914", sfx="clock")


@cart("Serbia accepted almost everything.", "ALMOST EVERYTHING...", sfx="quill")
def s_accept(c, u, t):
    desk_bg(c, t)
    rrect(c, 380, 80, 520, 600, 6)
    fill_ol(c, hexc("#F4EAD0"), hexc("#8A7A5A"), 2)
    for k in range(10):
        y = 140 + k * 52
        seg(c, (470, y), (840, y), 4, (0.4, 0.3, 0.2, 0.5))
        if u * 11 > k:
            if k == 9:
                seg(c, (410, y - 14), (440, y + 14), 6, RED)
                seg(c, (440, y - 14), (410, y + 14), 6, RED)
            else:
                c.move_to(410, y)
                c.line_to(422, y + 12)
                c.line_to(446, y - 16)
                c.set_line_width(6)
                c.set_source_rgba(0.2, 0.6, 0.3, 1)
                c.stroke()


@cart("On the twenty-eighth of July, 1914", "28 JULY 1914 · WAR ON SERBIA", sfx="impact@0 cannonD*2", mood="epic")
def s_war(c, u, t):
    mapscene(c, t, u, colors={"austria": "#F2F2F2", "serbia": "#E79A94"},
             arrows=[([(690, 410), (730, 440), (768, 462)], "#C8322F")])
    shell_burst(c, 775, 470, t, 2.2, 0, 0.4)


@cart("Then the dominoes began to fall.", "THE DOMINOES FALL", sfx="crack@0.8")
def s_dom1(c, u, t):
    dominos(c, t, 0, 2, u)


img(12, "Russia began to mobilise its huge army", label="RUSSIA MOBILISES", sfx="train march")


@cart("Germany saw Russia's mobilisation as a threat", "GERMANY DECLARES WAR ON RUSSIA", sfx="crack@0.5")
def s_dom2(c, u, t):
    dominos(c, t, 2, 4, u)


@cart("Two days later, Germany declared war on France", "...AND ON FRANCE", sfx="crack@0.4")
def s_dom3(c, u, t):
    dominos(c, t, 4, 5, u)


@cart("But Germany had a problem.", "A WAR ON TWO FRONTS")
def s_twofront(c, u, t):
    mapscene(c, t, u, colors={"germany": "#C9A06A", "france": ENTENTE, "russia": ENTENTE},
             arrows=[([(450, 420), (520, 360), (570, 340)], "#2B4C9B"), ([(1000, 320), (820, 300), (700, 300)],
                                                                         "#3E7A3E")])
    char(c, "kaiser", 640, 760, 1.6, expr="worried", t=t)


img(13, "Years earlier, its generals had prepared a solution", mode="map", label="THE SCHLIEFFEN PLAN",
    sfx="whoosh@0")


@cart("The idea was simple and ruthless.", "6 WEEKS TO DEFEAT FRANCE", sfx="clock")
def s_plan(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "lowlands": "#F2D27A"},
             arrows=[([(580, 300), (510, 290), (470, 330), (455, 345)], "#5A5A4A"),
                     ([(600, 340), (800, 320), (980, 320)], "#5A5A4A")])
    clock_face(c, 1150, 600, 70, 0, (u * 6) % 1 * 60)


img(14, "On the fourth of August, German troops crossed into Belgium.", label="4 AUGUST 1914 · BELGIUM",
    sfx="march")
img(15, "Britain had promised to protect Belgian neutrality", mode="frame:desk", label="“A SCRAP OF PAPER”",
    sfx="quill")


@cart("But that same day, Britain declared war on Germany.", "BRITAIN DECLARES WAR", sfx="impact@0 bell@0.5")
def s_britain(c, u, t):
    sky(c, "grey")
    clouds(c, t)
    palace(c, 640, 520, 1.1, col="#D9CFB8")
    c.set_source(vgrad(c, 520, H, hexc("#B9AE98"), hexc("#9A8E78")))
    c.rectangle(0, 520, W, H)
    c.fill()
    crowd(c, 0, 1280, 720, rows=3, s=0.7, t=t, flags=["uk", "uk", "uk"])


@cart("In just one week", "ONE WEEK · ALL OF EUROPE AT WAR", sfx="whoosh@0")
def s_week(c, u, t):
    dominos(c, t, 5, 7, u)


# ======================================================================== ENTHUSIASM
img(16, "Across Europe, crowds cheered.", label="AUGUST 1914", sfx="cheer", mood="triumph")
img(17, "In Berlin, in Paris, in London, young men rushed to sign up.", mode="frame:board",
    label="VOLUNTEERS", sfx="cheer")


@cart("Most people believed the war would be short.", "A SHORT WAR?", sfx="train cheer")
def s_trainoff(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.set_source(vgrad(c, 470, H, hexc("#B9AE98"), hexc("#9A8E78")))
    c.rectangle(0, 470, W, H)
    c.fill()
    train(c, 900 + 200 * u, 560, 0.85, 1, t, cars=4)
    crowd(c, 0, 1280, 720, rows=2, s=0.75, t=t, flags=["uk", "fr", "de"])


@cart("\"Home before the leaves fall,\" the Kaiser told his troops.", "“HOME BEFORE THE LEAVES FALL”")
def s_leaves(c, u, t):
    landscape(c, t, "day", "autumn", 420, seed=8, tree_col="#D98A3A")
    army(c, 380, 1280, 690, rows=3, s=0.6, uni="hun14", t=t, face=-1, arms="cheer", expr="happy")
    char(c, "kaiser", 200, 690, 1.6, arms="point", expr="proud", t=t)
    r = random.Random(3)
    for i in range(30):
        ph = (t * 0.2 + r.random()) % 1
        ellipse(c, (r.uniform(0, W) + t * 30) % W, ph * H, 8, 4, rot=t * 3 + i)
        fill(c, hexc(r.choice(["#D98A3A", "#C8642A", "#E9B04A"])))


@cart("\"Over by Christmas,\" people said in Britain.", "“OVER BY CHRISTMAS”", sfx="cheer")
def s_xmas_hope(c, u, t):
    street_bg(c, t, skyk="winter")
    snowfall(c, t, n=80)
    c.save()
    c.translate(1080, 640)
    for k in range(4):
        poly(c, [(-90 + k * 18, -k * 70), (90 - k * 18, -k * 70), (0, -k * 70 - 110)])
        fill(c, hexc("#2E7D4A"))
    c.restore()
    crowd(c, 0, 900, 720, rows=2, s=0.75, t=t, flags=["uk"])


@cart("They could not have been more wrong.", None, sfx="thunder@0.3 wind", mood="dark", zoom=0.04)
def s_wrong(c, u, t):
    sky(c, "storm")
    clouds(c, t, n=8, col=(0.3, 0.3, 0.35, 0.95), speed=30)
    c.set_source_rgba(*hexc("#2A2A26"))
    c.rectangle(0, 560, W, H)
    c.fill()
    army(c, 200 - 300 * u, 1400, 640, rows=2, s=0.55, uni="tommy", t=t, march=True, coat="#222", trou="#222",
         skin=hexc("#222"), blink=False)
    smoke_bank(c, 560, t, a=0.6, col=(0.3, 0.3, 0.3))
    if (t % 3) < 0.1:
        tint(c, (1, 1, 1), 0.5)


# ======================================================================== 1914 CAMPAIGN
@cart("At first, the Schlieffen Plan seemed to work.", "THE GERMAN ADVANCE", mood="epic")
def s_adv(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "lowlands": "#F2D27A", "france": ENTENTE},
             arrows=[([(585, 300), (520, 285), (480, 320), (462, 345)], "#5A5A4A"),
                     ([(590, 330), (530, 330), (480, 355)], "#5A5A4A")])


img(18, "German armies smashed through Belgium.", ov="smoke+flash", label="SIEGE GUNS", sfx="cannon*3")
img(19, "Refugees fled down every road.", label="REFUGEES", sfx="wind murmur", mood="sad")


@cart("The small British army fought bravely at Mons", "MONS · AUGUST 1914", sfx="volley*3", mood="epic")
def s_mons(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=12)
    for i in range(12):
        tree(c, i * 110, 560, 1.1, kind="round", col="#4E8A3E")
    army(c, 60, 600, 690, rows=2, s=0.7, uni="tommy", t=t, arms="aim")
    for i in range(5):
        muzzle(c, 130 + i * 100, 620, t, phase=i * 0.3, s=0.8)
    army(c, 800, 1300, 560, rows=2, s=0.5, uni="hun14", t=t, face=-1, march=True)


img(20, "The French threw themselves at the Germans", mode="split", who="poilu14", name="FRENCH INFANTRY · 1914",
    bg="field", label="BLUE COATS, RED TROUSERS", sfx="volley*2")


@cart("By early September", "50 KM FROM PARIS", sfx="heart")
def s_paris(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE},
             arrows=[([(560, 290), (500, 300), (468, 330)], "#5A5A4A")], pulses=[(PARIS, "#C8322F")])


@cart("Then, at the River Marne", "THE MARNE · SEPTEMBER 1914", sfx="cannon*3 volley*2", mood="epic")
def s_marne(c, u, t):
    landscape(c, t, "day", "grass", 380, seed=14)
    river(c, 470, 560, t)
    army(c, 700, 1280, 470, rows=2, s=0.4, uni="hun14", t=t, face=-1)
    army(c, 0, 640, 700, rows=3, s=0.65, uni="poilu14", t=t, march=True, run=True, flags="fr")
    for x in (150, 380):
        cannon(c, x, 610, 0.9, 1, t)


img(21, "The French were so desperate for men", ov="", label="THE TAXIS OF THE MARNE", sfx="car")


@cart("The Germans were exhausted", "A GAP IN THE LINE")
def s_gap(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE},
             arrows=[([(400, 380), (440, 360), (480, 330)], "#2B4C9B")])
    for (x, y) in ((440, 315), (515, 345)):
        rrect(c, x - 20, y - 10, 40, 20, 4)
        fill(c, hexc("#5A5A4A"))


@cart("The Battle of the Marne stopped the German advance", "PARIS IS SAVED", sfx="cheer volley*2",
      mood="triumph")
def s_saved(c, u, t):
    landscape(c, t, "gold", "grass", 420, seed=15, sunpos=(1000, 200))
    army(c, 700 + 300 * u, 1400, 560, rows=2, s=0.5, uni="hun14", t=t, march=True, run=True, expr="worried")
    army(c, 0, 640, 700, rows=2, s=0.7, uni="poilu14", t=t, arms="cheer", expr="happy", flags="fr")


# ======================================================================== TRENCHES
@cart("What happened next would define the entire war.", "THE RACE TO THE SEA", mood="tense")
def s_race(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE},
             arrows=[([(470, 360), (470, 320), (460, 280)], "#2B4C9B"), ([(520, 350), (510, 310), (500, 280)],
                                                                          "#5A5A4A")])


@cart("So they did the only thing they could. They dug.", "THEY DUG", sfx="march")
def s_dig(c, u, t):
    nomansland(c, t, "grey", 380, wire=False)
    rrect(c, 0, 560, W, 160, 0)
    fill(c, hexc("#5A4630"))
    for i in range(6):
        x = 120 + i * 200
        soldier(c, x, 660, 1.0, "tommy" if i < 3 else "hun14", t + i, arms="up" if (t * 2 + i) % 2 < 1 else "down",
                face=1 if i < 3 else -1)
        ph = ((t * 2 + i) % 1)
        ellipse(c, x + 40, 560 - 80 * math.sin(math.pi * ph), 10, 8)
        fill(c, hexc("#6A5236"))


img(22, "By the end of 1914, a continuous line of trenches", mode="map", label="700 KM OF TRENCHES",
    legend=[("THE WESTERN FRONT", "#8A1A1A")], sfx="whoosh@0")


@cart("The Western Front was born.", "THE WESTERN FRONT", sfx="wind cannonD*2")
def s_front(c, u, t):
    trench(c, t, wet=True)
    for i, x in enumerate((240, 520, 820, 1080)):
        soldier(c, x, 690, 1.2, "tommy", t + i, arms="musket", expr="sad", look=-1 if i % 2 else 1)


img(23, "Life in the trenches was a nightmare.", ov="rain", label="LIFE IN THE TRENCHES", sfx="rain", mood="dark")


def rat(c, x, y, s, t, face=1):
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    ellipse(c, 0, 0, 30, 14)
    fill(c, hexc("#5A524A"))
    ellipse(c, 26, -4, 12, 9)
    fill(c, hexc("#5A524A"))
    ellipse(c, 30, -12, 5, 5)
    fill(c, hexc("#C99A8A"))
    c.move_to(-30, 0)
    c.curve_to(-50, -10, -60, 10, -76, 0)
    c.set_line_width(3)
    c.set_source_rgba(0.6, 0.5, 0.45, 1)
    c.stroke()
    c.restore()


@cart("Soldiers lived in narrow ditches", "RATS · LICE · MUD", sfx="rain")
def s_rats(c, u, t):
    trench(c, t, wet=True)
    rain(c, t, n=120)
    for i, x in enumerate((300, 700, 1000)):
        soldier(c, x, 690, 1.25, "tommy", t + i, arms="hug", expr="sad")
    for i in range(3):
        rat(c, (-100 + (t * 160 + i * 500)) % 1500 - 100, 690, 0.8, t)


@cart("Many men developed \"trench foot,\"", "TRENCH FOOT", sfx="rain")
def s_foot(c, u, t):
    trench(c, t, wet=True)
    rain(c, t, n=100)
    soldier(c, 640, 690, 1.6, "tommy", t, arms="down", expr="sad", barefoot=True, seated=True)
    rrect(c, 760, 650, 40, 40, 6)
    fill(c, BLACK)


img(24, "Between the two lines of trenches lay a strip of ground", ov="fog", label="NO MAN'S LAND", sfx="wind")
img(25, "To cross it meant facing machine guns", mode="frame:board", label="MACHINE GUNS", sfx="mg")


@cart("The generals had been trained for a war of cavalry charges", "A WAR OF MACHINES", sfx="gallop mg@2",
      mood="epic")
def s_machines(c, u, t):
    nomansland(c, t, "grey", 400)
    cavalry(c, -300, 600, 700, t, uni="poilu14", s=0.55, speed=100)
    machine_gun(c, 1100, 640, 1.3, -1, t, fire=t > 2)
    soldier(c, 1180, 650, 1.0, "hun", t, face=-1, arms="aim")
    if t > 2:
        smoke_bank(c, 560, t, a=0.3)


# ======================================================================== CHRISTMAS TRUCE
@cart("Yet even in this hell, there were moments of humanity.", "MOMENTS OF HUMANITY", sfx="wind", mood="calm")
def s_quiet(c, u, t):
    trench(c, t, night=True, snow=True)
    snowfall(c, t, n=90)
    for i, x in enumerate((400, 860)):
        soldier(c, x, 690, 1.3, "tommy", t + i, arms="hug", expr="neutral")


def xmas_tree(c, x, y, s, t):
    for k in range(4):
        poly(c, [(x - (60 - k * 12) * s, y - k * 40 * s), (x + (60 - k * 12) * s, y - k * 40 * s),
                 (x, y - (k * 40 + 70) * s)])
        fill(c, hexc("#2E6A3E"))
    for k in range(7):
        cx = x + math.sin(k * 2.3) * 35 * s
        cy = y - (20 + k * 18) * s
        g = 0.7 + 0.3 * math.sin(t * 6 + k)
        ellipse(c, cx, cy, 4 * s, 6 * s)
        fill(c, (1, 0.85 * g, 0.4, 1))


@cart("Singing. \"Stille Nacht.\"", "CHRISTMAS EVE · 1914", sfx="silentnight@0", zoom=0.1, focus=(640, 300))
def s_stille(c, u, t):
    nomansland(c, t, "night", 420, wet=False)
    c.set_source_rgba(1, 1, 1, 0.7)
    c.rectangle(0, 420, W, 300)
    c.fill()
    for k in range(-1, 18):
        rrect(c, k * 76, 400, 74, 26, 11)
        fill_ol(c, hexc("#E8EAEC"), hexc("#7A7A7A"), 1.5)
    for x in (200, 520, 840, 1160):
        xmas_tree(c, x, 410, 0.9, t)
    snowfall(c, t, n=100)
    moon(c, 1100, 110, 34)


img(26, "Slowly, carefully, men climbed out of their trenches.", ov="snow", label="THE CHRISTMAS TRUCE",
    sfx="murmur")


@cart("In some places, they even played football.", "FOOTBALL IN NO MAN'S LAND", sfx="cheer")
def s_football(c, u, t):
    landscape(c, t, "winter", "snow", 380, trees=False, seed=4)
    barbed_wire(c, -20, W + 20, 470, 0.7)
    ph = (t * 0.8) % 2
    bx = 300 + 600 * (ph if ph < 1 else 2 - ph)
    by = 640 - 120 * math.sin(math.pi * (ph % 1))
    for i in range(3):
        soldier(c, 220 + i * 140, 690, 1.0, "tommy", t + i, walk=t * 6 + i, arms="cheer" if i == 1 else "down",
                expr="happy")
        soldier(c, 760 + i * 140, 690, 1.0, "hun14", t + i, walk=t * 6 + i, face=-1, expr="happy")
    ellipse(c, bx, by, 16, 16)
    fill_ol(c, WHITE, INK, 2)
    snowfall(c, t, n=60)


@cart("The generals were furious.", "THE GENERALS ARE FURIOUS", sfx="room")
def s_furious(c, u, t):
    interior(c, t, wall="#C9B48E")
    table(c, 640, 690, 520, 130, cloth="#3A6A4A")
    char(c, "officer", 640, 640, 1.7, arms="fist", expr="angry", t=t)


@cart("And the next day, the killing resumed.", None, sfx="cannon*3 volley*1", mood="dark")
def s_resume(c, u, t):
    nomansland(c, t, "grey", 400)
    for i in range(4):
        shell_burst(c, 200 + i * 300, 600 - (i % 2) * 60, t, 2.4, i * 0.6, 1.0)


# ======================================================================== EASTERN FRONT
@cart("Meanwhile, in the east, the war looked very different.", "THE EASTERN FRONT", mood="tense")
def s_east(c, u, t):
    mapscene(c, t, u, colors={"russia": ENTENTE, "prussia": CENTRAL, "germany": CENTRAL},
             arrows=[([(900, 270), (820, 270), (770, 265)], "#3E7A3E")])


img(27, "But at the Battle of Tannenberg", label="TANNENBERG · HINDENBURG & LUDENDORFF", sfx="cannonD*2")
img(28, "Around ninety thousand Russians were taken prisoner.", label="90,000 PRISONERS", sfx="wind march")


@cart("The Eastern Front was vast and open.", "VAST & OPEN", sfx="wind gallop")
def s_vast(c, u, t):
    landscape(c, t, "grey", "dry", 460, seed=22, trees=False)
    cavalry(c, -200, 900, 640, t, uni="cossack", s=0.45, speed=150)
    army(c, 900, 1300, 520, rows=2, s=0.35, uni="hun14", t=t, face=-1)


img(29, "And the war kept spreading.", mode="map", label="THE WAR SPREADS", sfx="whoosh@0")


@cart("This was no longer a European war.", "A WORLD WAR", sfx="impact@0.5", mood="epic")
def s_world(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#1E2A4A"), hexc("#3A4A7A")))
    c.paint()
    stars(c, t, ymax=720)
    globe(c, 640, 330, 220, t)
    for k in range(10):
        a = t * 0.6 + k * 0.63
        flames(c, 640 + 170 * math.cos(a), 330 + 120 * math.sin(a * 1.3), 26, 34, t, seed=k)


# ======================================================================== INDIA
@cart("And soldiers came from every corner of the globe.", "FROM EVERY CORNER OF THE GLOBE", sfx="sea march",
      mood="triumph")
def s_empire(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 520)
    rrect(c, -40, 560, 1360, 200, 10)
    fill(c, hexc("#8A6A48"))
    for i, (uni, f) in enumerate((("sepoy", "uk"), ("anzac", "uk"), ("tommy", "uk"), ("sepoy", None),
                                   ("anzac", None))):
        soldier(c, 160 + i * 240, 690, 1.25, uni, t + i, walk=t * 5 + i, arms="musket")


img(30, "But the largest volunteer army of all came from India.", label="1,000,000+ INDIAN SOLDIERS",
    sfx="march")


@cart("In the autumn of 1914, Indian troops arrived in France", "YPRES · AUTUMN 1914", sfx="wind rain")
def s_sepoy_trench(c, u, t):
    trench(c, t, wet=True, skyk="grey")
    rain(c, t, n=100)
    for i, x in enumerate((260, 560, 860, 1120)):
        soldier(c, x, 690, 1.25, "sepoy", t + i, arms="hug" if i % 2 else "musket", expr="sad")


@cart("They fought in France and Belgium", "INDIAN SOLDIERS ON EVERY FRONT", sfx="whoosh@0")
def s_fronts(c, u, t):
    mapscene(c, t, u, base="blocs", pulses=[((470, 300), "#E2B53B"), ((1000, 690), "#E2B53B"),
                                            ((880, 505), "#E2B53B"), ((1200, 600), "#E2B53B")])


img(31, "Indian soldiers won the Victoria Cross", mode="split", who="khudadad", name="KHUDADAD KHAN · VC",
    bg="trench", label="THE FIRST INDIAN VICTORIA CROSS", sfx="impact@0")


@cart("More than seventy thousand Indian soldiers never came home.", "70,000+ NEVER CAME HOME", sfx="wind",
      mood="sad")
def s_indian_dead(c, u, t):
    landscape(c, t, "dusk", "grass", 420, seed=20, trees=False)
    crosses(c, 700, t, n=8)
    for i in range(10):
        candle(c, 100 + i * 120, 710, t + i, 0.7)


img(32, "Today many of their names are carved on the India Gate", ov="light", label="INDIA GATE · NEW DELHI",
    sfx="bellL@0.3")


# ======================================================================== 1915 GAS
@cart("By 1915, both sides were desperate to break the deadlock.", "1915 · DEADLOCK", sfx="wind cannonD*2",
      mood="tense")
def s_deadlock(c, u, t):
    trench(c, t, skyk="grey")
    for i, x in enumerate((300, 640, 980)):
        soldier(c, x, 690, 1.25, "tommy", t + i, arms="musket", expr="worried", look=1)


img(33, "On the twenty-second of April, near the Belgian town of Ypres", ov="gas", label="YPRES · 22 APRIL 1915",
    sfx="wind", mood="dark")


@cart("It was chlorine gas.", "CHLORINE GAS", sfx="panic gas")
def s_gas(c, u, t):
    trench(c, t, skyk="grey")
    for i, x in enumerate((240, 520, 820, 1080)):
        soldier(c, x + (20 * u if i % 2 else -20 * u), 690, 1.2, "poilu14", t + i, arms="up", expr="shock",
                walk=t * 7 + i)
    gas_cloud(c, t, 300 + 1200 * u, 520, a=0.75)


img(34, "Soon both sides were using it", mode="frame:desk", label="MUSTARD GAS · PHOSGENE", sfx="gas")


@cart("Gas masks became part of every soldier's equipment.", "GAS MASKS", sfx="gas")
def s_masks(c, u, t):
    trench(c, t, skyk="grey")
    gas_cloud(c, t, 1400, 300, a=0.4)
    for i, x in enumerate((260, 560, 860, 1120)):
        soldier(c, x, 690, 1.25, "gasman", t + i, arms="musket")


# ======================================================================== GALLIPOLI
img(35, "A young politician named Winston Churchill", mode="split", who="churchill", name="WINSTON CHURCHILL",
    bg="hall", label="FIRST LORD OF THE ADMIRALTY", sfx="room", mood="tense")


@cart("Instead of attacking Germany head-on", "THE DARDANELLES", sfx="sea whoosh@0.3")
def s_dard(c, u, t):
    mapscene(c, t, u, base="blocs", colors={"ottoman": CENTRAL},
             arrows=[([(600, 600), (760, 580), (870, 510)], "#C8322F")], pulses=[((880, 505), "#C8322F")])


img(36, "On the twenty-fifth of April, 1915, British, French, Australian and New Zealand troops landed",
    ov="sea+smoke", label="GALLIPOLI · 25 APRIL 1915", sfx="sea volley*3", mood="epic")


@cart("It was a disaster.", "A DISASTER", sfx="volley*3 cannon*2")
def s_gall(c, u, t):
    sky(c, "dawn")
    sea(c, t, 560)
    poly(c, [(500, 720), (620, 300), (800, 220), (1280, 200), (1280, 720)])
    fill(c, hexc("#A88A5A"))
    poly(c, [(0, 600), (700, 580), (720, 720), (0, 720)])
    fill(c, hexc("#E6C890"))
    for i in range(5):
        soldier(c, 840 + i * 90, 260 - i * 4, 0.6, "ott", t + i, face=-1, arms="aim")
        muzzle(c, 790 + i * 90, 230, t, phase=i * 0.4, s=0.6, face=-1)
    for i in range(6):
        soldier(c, 80 + i * 90, 690, 0.95, "anzac", t + i, arms="musket", expr="worried")
    boat(c, 300, 600, 0.7, t)


img(37, "The Ottoman defenders, led by a determined officer named Mustafa Kemal", mode="split", who="kemal",
    name="MUSTAFA KEMAL", bg="desert", label="MUSTAFA KEMAL", sfx="wind")


@cart("For eight months they clung on", "8 MONTHS", sfx="wind")
def s_clung(c, u, t):
    skyk = "gold" if u < 0.5 else "winter"
    sky(c, skyk)
    if u < 0.5:
        sun(c, 1050, 140, 60, t=t, rays=True)
    sea(c, t, 520)
    c.set_source(vgrad(c, 560, H, hexc("#D9B87A"), hexc("#A88A5A")))
    c.rectangle(0, 560, W, H)
    c.fill()
    for i in range(5):
        tent(c, 120 + i * 230, 620, 0.9)
    for i in range(4):
        soldier(c, 220 + i * 280, 700, 1.0, "anzac", t + i, arms="hug" if u > 0.5 else "down", expr="sad")
    if u > 0.5:
        snowfall(c, t, n=80)


@cart("For Australia and New Zealand, Gallipoli became a defining moment", "ANZAC DAY · 25 APRIL",
      sfx="bellL@0.5", mood="sad")
def s_anzac(c, u, t):
    sky(c, "dawn")
    sun(c, 640, 440, 70, "#FFD27A", t, rays=True)
    c.set_source_rgba(*hexc("#2A1C1C"))
    c.rectangle(0, 520, W, H)
    c.fill()
    soldier(c, 640, 600, 1.6, "anzac", t, arms="musket", coat="#1A1212", trou="#1A1212", skin=hexc("#1A1212"),
            blink=False)
    poppies(c, 600, 720, t, n=50)


@cart("And Mustafa Kemal would later become Atatürk", "ATATÜRK · FOUNDER OF MODERN TURKEY", sfx="cheer")
def s_ataturk(c, u, t):
    hall(c, t)
    for x in (240, 1040):
        flag(c, x, 650, t, "tr", pole=380, w=140, h=90)
    char(c, "kemal", 640, 690, 2.0, arms="hand_in", expr="proud", t=t)


# ======================================================================== SEA
@cart("At sea, Britain's navy blockaded Germany", "THE BLOCKADE", sfx="sea", mood="tense")
def s_blockade(c, u, t):
    sky(c, "grey")
    clouds(c, t, col=(0.75, 0.75, 0.8, 0.8))
    sea(c, t, 400)
    for i in range(3):
        dreadnought(c, 200 + i * 440, 560 + (i % 2) * 40, 0.5, 1, t)


img(74, "Germany struck back with a new weapon", ov="sea", label="THE U-BOAT", sfx="sea sonar@0.5")
img(38, "On the seventh of May, 1915", ov="sea", label="LUSITANIA · 7 MAY 1915", sfx="sea")


@cart("She sank in just eighteen minutes.", "18 MINUTES", sfx="explosion@0.3 sea", mood="dark")
def s_sink(c, u, t):
    sky(c, "grey")
    sea(c, t, 440)
    liner(c, 640, 560, 0.8, t, sink=smooth(u))
    explosion(c, 700, 560, t / 1.5, 1.3)


@cart("The United States was outraged.", "1,198 DEAD · 128 AMERICANS", sfx="angry")
def s_outrage(c, u, t):
    street_bg(c, t)
    for x in (300, 980):
        flag(c, x, 520, t, "usa", pole=200, w=110, h=70)
    crowd(c, 0, 1280, 720, rows=3, s=0.75, t=t, expr="angry", arms="fist")


# ======================================================================== 1916
@cart("Then came 1916.", "1916 · THE YEAR OF THE GREAT SLAUGHTERS", sfx="impact@0 cannonD*3", mood="dark",
      zoom=0.05)
def s_1916(c, u, t):
    nomansland(c, t, "night", 420)
    for i in range(5):
        shell_burst(c, 120 + i * 260, 560 + (i % 2) * 60, t, 2.0, i * 0.4, 0.9)


img(39, "In February, Germany attacked the French fortress city of Verdun.", ov="smoke+flash",
    label="VERDUN · FEBRUARY 1916", sfx="cannon*4", mood="epic")


@cart("The German commander, Erich von Falkenhayn", "“BLEED FRANCE WHITE”", sfx="heart")
def s_falk(c, u, t):
    interior(c, t, wall="#B8A888", night=True)
    table(c, 640, 690, 600, 130, cloth="#3A4A3A")
    c.save()
    c.translate(400, 545)
    c.scale(0.37, 0.07)
    c.rectangle(0, 0, W, H)
    c.clip()
    ww1map(c, t, labels=False)
    c.restore()
    char(c, "falkenhayn", 640, 640, 1.7, arms="point", expr="smirk", t=t)
    candle(c, 300, 560, t, 1.0)


@cart("Millions of shells turned forests and villages into a lunar landscape.", "A LUNAR LANDSCAPE",
      sfx="cannon*5")
def s_lunar(c, u, t):
    nomansland(c, t, "grey", 380, wire=False)
    for i in range(6):
        shell_burst(c, 100 + i * 220, 520 + (i % 3) * 60, t, 1.8, i * 0.35, 0.8)
    smoke_bank(c, 450, t, a=0.4)


img(40, "The French vowed: \"They shall not pass.\"", mode="split", who="poilu", name="“ILS NE PASSERONT PAS”",
    bg="trench", label="“THEY SHALL NOT PASS”", sfx="volley*2")
img(71, "But the cost was staggering.", mode="frame:board", label="~700,000 CASUALTIES", sfx="heart", mood="sad")


@cart("To take pressure off Verdun, the British launched their own great offensive", "THE SOMME · 1916",
      mood="tense")
def s_somme_map(c, u, t):
    mapscene(c, t, u, colors={"france": ENTENTE, "germany": CENTRAL},
             pulses=[((466, 322), "#C8322F"), ((505, 345), "#8A1A1A")])


img(41, "For a week, British guns fired", ov="flash+smoke", label="1,500,000 SHELLS", sfx="cannon*6", mood="epic")
img(42, "On the morning of the first of July, 1916", ov="smoke", label="1 JULY 1916 · 7:30 AM",
    sfx="whistle@0.5 volley*2")


@cart("But the Germans had survived", "DEEP UNDERGROUND", sfx="cannonD*2")
def s_bunker(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#5A4630"), hexc("#3A2A1E")))
    c.paint()
    sky(c, "grey", 200)
    rrect(c, 120, 420, 700, 220, 10)
    fill(c, hexc("#2A2018"))
    for x in range(140, 820, 70):
        seg(c, (x, 420), (x, 640), 6, hexc("#5A4028"))
    candle(c, 400, 640, t, 0.8)
    for i in range(3):
        k = (u * 1.6 - i * 0.2)
        x = lerp(300 + i * 120, 980, clamp(k))
        y = lerp(640, 200, clamp(k))
        soldier(c, x, y, 0.9, "hun", t + i, walk=t * 7 + i, arms="musket")
    for k in range(8):
        seg(c, (840 + k * 20, 640 - k * 55), (900 + k * 20, 640 - k * 55), 6, hexc("#7A5A3A"))
    machine_gun(c, 1060, 200, 1.0, -1, t, fire=u > 0.6)


@cart("On that single day, the British Army suffered", "57,000 CASUALTIES IN ONE DAY", sfx="mg volley*3",
      mood="dark")
def s_july1(c, u, t):
    nomansland(c, t, "grey", 400)
    for i in range(7):
        soldier(c, 100 + i * 150 + 40 * u, 660 - (i % 2) * 40, 0.9, "tommy", t + i, walk=t * 3 + i, arms="musket")
    smoke_bank(c, 520, t, a=0.35)
    for i in range(6):
        if (t * 9 + i) % 1 < 0.25:
            ellipse(c, 1200, 460 + i * 6, 12, 8)
            fill(c, (1, 0.85, 0.3, 0.9))


img(72, "It remains the bloodiest day in British military history.", label="THE BLOODIEST DAY", sfx="wind heart",
    mood="sad")


@cart("The Battle of the Somme dragged on until November.", "15 SEPT 1916 · A NEW MACHINE", sfx="tank",
      mood="epic")
def s_tank(c, u, t):
    nomansland(c, t, "grey", 400)
    tank(c, -200 + 1100 * u, 660, 1.0, 1, t)
    for i in range(3):
        soldier(c, 1050 + i * 70, 560, 0.7, "hun", t + i, face=-1, arms="up", expr="shock")


img(43, "To keep it secret, the British had called it a \"water tank.\"", label="THE MARK I TANK", sfx="tank")


@cart("By the end of the Somme", "1,000,000+ CASUALTIES · 10 KM", sfx="wind", mood="sad")
def s_somme_end(c, u, t):
    mapscene(c, t, u, colors={"france": ENTENTE, "germany": CENTRAL})
    arrow(c, [(455, 330), (472, 326)], smooth(u * 1.4), "#C8322F", 10, 22)
    c.select_font_face("DejaVu Sans", 0, 1)
    c.set_font_size(30)
    c.move_to(500, 300)
    c.set_source_rgba(0.6, 0.1, 0.1, 1)
    c.show_text("10 km")


# ======================================================================== BRUSILOV / AIR / JUTLAND
img(44, "In the east, that same summer, Russia struck one more great blow.", mode="split", who="brusilov",
    name="GENERAL BRUSILOV", bg="field", label="THE BRUSILOV OFFENSIVE", sfx="march", mood="epic")


@cart("The Austro-Hungarian army was caught by surprise and crumbled.", "AUSTRIA-HUNGARY CRUMBLES",
      sfx="cheer volley*2")
def s_brus(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=24)
    army(c, -200 + 300 * u, 600, 690, rows=3, s=0.6, uni="ivan", t=t, march=True, run=True, flags="ru")
    army(c, 760, 1280, 600, rows=2, s=0.55, uni="au", t=t, face=-1, arms="up", expr="shock")
    for k in range(3):
        flag(c, 800 + k * 160, 640, t, "white", pole=110, w=50, h=34)


@cart("But Russia's own losses were enormous.", "RUSSIA LOSES FAITH", sfx="angry", mood="dark")
def s_rus_loss(c, u, t):
    street_bg(c, t, skyk="winter")
    snowfall(c, t, n=80)
    crowd(c, 0, 1280, 720, rows=3, s=0.75, t=t, expr="angry", arms="fist")


@cart("The war was also fought in the skies.", "WAR IN THE AIR", sfx="plane", mood="epic")
def s_sky(c, u, t):
    sky(c, "day")
    clouds(c, t, n=7, speed=40)
    biplane(c, -200 + 1500 * u, 280, 0.9, 1, t, col="#7A8A5A", mark="roundel")
    biplane(c, 1400 - 1300 * u, 460, 0.8, -1, t, col="#9A8A6A", mark="cross")


@cart("Then they started throwing bricks.", "BRICKS... THEN PISTOLS... THEN MACHINE GUNS", sfx="plane mg@2.5")
def s_bricks(c, u, t):
    sky(c, "day")
    clouds(c, t, n=6, speed=60)
    biplane(c, 420, 280, 1.1, 1, t, col="#7A8A5A", mark="roundel")
    biplane(c, 860, 460, 1.1, -1, t, col="#9A8A6A")
    ph = (t % 2) / 2
    rrect(c, lerp(470, 820, ph), 300 + 180 * ph * ph, 30, 18, 2)
    fill(c, hexc("#B5523A"))


img(45, "Aces became celebrities.", mode="split", who="redbaron", name="MANFRED VON RICHTHOFEN", bg="sky",
    label="THE ACES", sfx="plane")
img(46, "They called him the Red Baron.", label="THE RED BARON", sfx="plane mg@1")


@cart("He shot down eighty enemy aircraft", "80 VICTORIES", sfx="plane mg*3")
def s_redbaron(c, u, t):
    sky(c, "gold")
    clouds(c, t, n=6, speed=50)
    biplane(c, 300 + 300 * u, 340, 1.0, 1, t, col="#C8322F", tri=True)
    biplane(c, 900 + 300 * u, 300 + 40 * math.sin(t), 0.8, 1, t, col="#7A8A5A", mark="roundel")
    if (t * 10) % 1 < 0.5:
        seg(c, (420 + 300 * u, 340), (800 + 300 * u, 310), 2, (1, 0.9, 0.4, 0.8))


img(47, "And at sea, in May 1916, the two great battle fleets finally met", ov="sea+smoke+flash",
    label="JUTLAND · MAY 1916", sfx="sea cannon*5")


@cart("It was the largest naval battle of the war.", "THE LARGEST NAVAL BATTLE", sfx="sea cannon*4")
def s_jutland(c, u, t):
    sky(c, "grey")
    sea(c, t, 400)
    dreadnought(c, 300, 560, 0.55, 1, t, fire=True)
    dreadnought(c, 1000, 520, 0.45, -1, t, fire=True, phase=0.7)
    smoke_bank(c, 430, t, a=0.4)


@cart("The blockade continued. And in Germany, people began to go hungry.", "HUNGER", sfx="wind", mood="sad")
def s_hunger(c, u, t):
    interior(c, t, wall="#B8A888", night=True)
    table(c, 640, 690, 520, 130)
    ellipse(c, 640, 560, 50, 12)
    fill(c, WHITE)
    lady(c, 420, 690, 1.5, dress="#5A4A4A", expr="sad", t=t)
    person(c, 860, 690, 1.0, coat="#6A5A4A", hair="short", expr="sad", t=t, face=-1, young=True)


# ======================================================================== HOME FRONT
img(73, "Because this was a total war", ov="search", label="ZEPPELINS OVER LONDON", sfx="zeppelin",
    mood="tense")


@cart("Factories that once made cars, toys and sewing machines", "TOTAL WAR", sfx="factory")
def s_factory(c, u, t):
    interior(c, t, wall="#8A8070", window=False)
    for k in range(8):
        x = (k * 170 + t * 80) % 1500 - 120
        rrect(c, x, 520, 40, 90, 18)
        fill_ol(c, hexc("#B8902E"), hexc("#7A5A1A"), 2)
    seg(c, (0, 612), (W, 612), 14, hexc("#3A3A3A"))
    for i in range(4):
        char(c, "worker", 160 + i * 320, 690, 1.3, arms="hold", t=t + i)


img(48, "With millions of men at the front, women took their places.", label="THE MUNITIONETTES", sfx="factory")


@cart("In Britain, women filling shells with explosives", "“CANARIES”", sfx="factory")
def s_canaries(c, u, t):
    interior(c, t, wall="#8A8070", window=False)
    for k in range(5):
        rrect(c, 120 + k * 230, 540, 46, 100, 20)
        fill_ol(c, hexc("#B8902E"), hexc("#7A5A1A"), 2)
    for i in range(3):
        char(c, "worker", 260 + i * 360, 700, 1.5, arms="hold", t=t + i, skin=hexc("#E8CF5A"), expr="happy")
img(49, "Governments used propaganda", mode="split", who="kitchener", name="“YOUR COUNTRY NEEDS YOU”", bg="street",
    label="PROPAGANDA", sfx="march")
img(75, "Food was rationed.", mode="frame:board", label="RATIONS & CENSORED LETTERS", sfx="quill")
img(50, "In Germany, the British blockade was so effective", mode="frame:desk", label="THE TURNIP WINTER",
    sfx="wind", mood="sad")


@cart("At home and at the front, the whole of society was now at war.", "A WHOLE SOCIETY AT WAR",
      sfx="factory cannonD*2")
def s_society(c, u, t):
    c.save()
    c.rectangle(0, 0, 640, H)
    c.clip()
    interior(c, t, wall="#8A8070", window=False)
    for i in range(2):
        char(c, "worker", 160 + i * 300, 690, 1.3, arms="hold", t=t + i)
    c.restore()
    c.save()
    c.rectangle(640, 0, 640, H)
    c.clip()
    trench(c, t)
    for i in range(2):
        soldier(c, 800 + i * 300, 690, 1.2, "tommy", t + i, arms="musket")
    c.restore()
    seg(c, (640, 0), (640, H), 8, BLACK)


# ======================================================================== 1917
@cart("By 1917, Europe was exhausted.", "1917 · EXHAUSTED", sfx="rain", mood="dark")
def s_exhaust(c, u, t):
    trench(c, t, wet=True)
    rain(c, t, n=140)
    for i, x in enumerate((260, 560, 860, 1120)):
        soldier(c, x, 690, 1.25, ["tommy", "poilu", "hun", "tommy"][i], t + i, arms="hug", expr="sad")


@cart("In the French army, after yet another failed offensive", "MUTINY", sfx="angry")
def s_mutiny(c, u, t):
    landscape(c, t, "grey", "mud", 420, seed=26)
    for i in range(6):
        soldier(c, 160 + i * 190, 690, 1.1, "poilu", t + i, arms="shrug" if i % 2 else "fist", expr="angry")
    char(c, "officer", 640, 600, 1.0, coat="#5A6A8A", trou="#5A6A8A", hat="kepi", arms="point", expr="shout",
         t=t, face=-1)


@cart("But in Russia, the exhaustion turned into revolution.", "REVOLUTION IN RUSSIA", sfx="angry", mood="tense")
def s_revo(c, u, t):
    street_bg(c, t, skyk="winter")
    snowfall(c, t, n=80)
    crowd(c, 0, 1280, 720, rows=4, s=0.75, t=t, expr="angry", arms="fist", flags=["red", "red", "red"])


img(51, "In March 1917, protests in Petrograd turned into a revolution.", mode="split", who="tsar",
    name="TSAR NICHOLAS II", bg="hall", label="THE TSAR ABDICATES", sfx="bellL@0.5")


@cart("Germany saw an opportunity.", "THE SEALED TRAIN", sfx="train")
def s_sealed(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "russia": "#E79A94"})
    pts = [(560, 420), (600, 330), (720, 260), (900, 200), (1000, 160)]
    k = smooth(u * 1.2)
    i = min(len(pts) - 2, int(k * (len(pts) - 1)))
    f = k * (len(pts) - 1) - i
    x = lerp(pts[i][0], pts[i + 1][0], f)
    y = lerp(pts[i][1], pts[i + 1][1], f)
    c.set_line_width(4)
    c.set_dash([10, 8])
    c.set_source_rgba(0.3, 0.2, 0.1, 0.8)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    c.set_dash([])
    train(c, x, y + 20, 0.25, 1, t, cars=1, heads=False)


img(52, "His name was Vladimir Lenin.", label="VLADIMIR LENIN", sfx="cheer")


@cart("In November 1917, Lenin and his Bolsheviks seized power.", "“PEACE, LAND AND BREAD”", sfx="cheer")
def s_lenin(c, u, t):
    street_bg(c, t, skyk="grey")
    crowd(c, 0, 1280, 720, rows=3, s=0.7, t=t, flags=["red", "red"])
    rrect(c, 520, 470, 240, 90, 6)
    fill(c, hexc("#8A2A2A"))
    char(c, "lenin", 640, 480, 1.4, arms="point", t=t)


img(53, "Soon after, Russia made peace with Germany", mode="frame:desk", label="BREST-LITOVSK · MARCH 1918",
    sfx="quill")


@cart("The Eastern Front was closed.", "TROOPS RUSH WEST", sfx="train")
def s_west(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "russia": "#D9C9C9"},
             arrows=[([(820, 300), (700, 310), (560, 330)], "#5A5A4A"), ([(840, 360), (720, 360), (580, 360)],
                                                                         "#5A5A4A")])


# ======================================================================== OTHER FRONTS
img(54, "Italy had joined the Allies in 1915", ov="snow", label="THE ALPINE FRONT", sfx="blizzard", mood="tense")


@cart("In October 1917, at a place called Caporetto", "CAPORETTO · OCTOBER 1917", sfx="cannon*3 panic")
def s_caporetto(c, u, t):
    landscape(c, t, "grey", "stone", 440, mountains=True, trees=False, seed=6)
    army(c, 300 + 300 * u, 1400, 690, rows=2, s=0.6, uni="alpini", t=t, march=True, run=True, expr="shock")
    army(c, -200, 300 + 200 * u, 690, rows=2, s=0.6, uni="hun", t=t, march=True)


@cart("But Italy did not surrender.", "THE PIAVE LINE HOLDS", sfx="volley*2", mood="triumph")
def s_piave(c, u, t):
    landscape(c, t, "day", "grass", 380, seed=7, mountains=True)
    river(c, 470, 560, t)
    army(c, 0, 1280, 700, rows=2, s=0.7, uni="alpini", t=t, arms="aim", flags="it")


@cart("In the deserts of the Middle East", "THE ARAB REVOLT", sfx="wind gallop", mood="mystic")
def s_desert(c, u, t):
    landscape(c, t, "desert", "sand", 420, trees=False, seed=3, sunpos=(1100, 140))
    for i in range(5):
        camel(c, -200 + i * 220 + 500 * u, 680 - (i % 2) * 40, 0.85, 1, t + i)


img(56, "Fighting alongside them was a young British officer", mode="split", who="lawrence", name="T. E. LAWRENCE",
    bg="desert", label="T. E. LAWRENCE", sfx="wind")
img(55, "Wearing Arab robes and riding camels", label="AQABA · 1917", sfx="gallopH wind", mood="epic")


@cart("He became a legend: Lawrence of Arabia.", "LAWRENCE OF ARABIA", sfx="wind", mood="mystic", zoom=0.05)
def s_lawrence(c, u, t):
    sky(c, "sunset")
    sun(c, 900, 420, 100, "#FFD27A", t, rays=True)
    c.move_to(0, 560)
    for x in range(0, W + 40, 40):
        c.line_to(x, 560 + 30 * math.sin(x / 200))
    c.line_to(W, H)
    c.line_to(0, H)
    fill(c, hexc("#C99A5E"))
    camel(c, 500, 640, 1.4, 1, t * 0.4, rider=False)
    char(c, "lawrence", 494, 430, 1.1, seated=True, t=t)


img(57, "Meanwhile, British and Indian troops pushed north from Egypt", label="JERUSALEM · DECEMBER 1917",
    sfx="march bell@1")


# ======================================================================== USA
@cart("But in 1917, Germany also made a fatal mistake.", "UNRESTRICTED SUBMARINE WARFARE", sfx="sea sonar@0 explosion@2",
      mood="tense")
def s_unres(c, u, t):
    sky(c, "grey")
    sea(c, t, 400)
    ship(c, 900, 560, 0.6, -1, t, "usa", sink=clamp((t - 2) / 4))
    uboat(c, 300, 600, 0.8, 1, t)
    if t > 1:
        x = lerp(500, 880, clamp((t - 1) / 1))
        seg(c, (x - 40, 610), (x, 610), 6, hexc("#3A3E44"))
    explosion(c, 900, 560, (t - 2) / 1.5, 1.0)


img(58, "Then the British intercepted and decoded a secret German message", mode="frame:desk",
    label="THE ZIMMERMANN TELEGRAM", sfx="morse")

US_POLY = [(120, 160), (980, 140), (1100, 240), (1050, 400), (820, 420), (700, 480), (560, 440), (380, 430),
           (200, 380)]
MX_POLY = [(380, 430), (560, 440), (700, 480), (760, 600), (700, 700), (560, 640), (420, 540)]
TX_POLY = [(560, 440), (700, 480), (690, 400), (580, 390)]


@cart("In it, Germany offered Mexico an alliance.", "TEXAS · NEW MEXICO · ARIZONA", sfx="whoosh@0.4")
def s_mexico(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#A9CFD8"), hexc("#8DBAC6")))
    c.paint()
    poly(c, US_POLY)
    fill_ol(c, hexc("#EAD9B0"), hexc("#7A6A4A"), 2.5)
    poly(c, MX_POLY)
    fill_ol(c, hexc("#C9E0A8"), hexc("#7A6A4A"), 2.5)
    poly(c, [(380, 430), (560, 440), (580, 390), (400, 380)])
    c.set_source_rgba(0.8, 0.2, 0.2, 0.3 + 0.2 * math.sin(t * 3))
    c.fill()
    poly(c, TX_POLY)
    c.set_source_rgba(0.8, 0.2, 0.2, 0.3 + 0.2 * math.sin(t * 3))
    c.fill()
    c.select_font_face("DejaVu Sans", 0, 1)
    c.set_font_size(30)
    for txt, (x, y) in (("USA", (560, 280)), ("MEXICO", (520, 580))):
        c.move_to(x, y)
        c.set_source_rgba(0.25, 0.2, 0.15, 0.8)
        c.show_text(txt)
    arrow(c, [(1270, 300), (1100, 500), (700, 580)], smooth(u * 1.4), "#5A5A4A")
    flag(c, 1180, 260, t, "de", pole=120, w=70, h=46)


@cart("When the telegram was published, Americans were furious.", "AMERICA IS FURIOUS", sfx="angry")
def s_furious_us(c, u, t):
    street_bg(c, t)
    for x in (260, 1020):
        flag(c, x, 520, t, "usa", pole=200, w=110, h=70)
    crowd(c, 0, 1280, 720, rows=3, s=0.75, t=t, expr="angry", arms="fist")


img(59, "On the sixth of April, 1917, the United States declared war on Germany.", mode="split", who="wilson",
    name="PRESIDENT WOODROW WILSON", bg="hall", label="6 APRIL 1917 · AMERICA ENTERS THE WAR", sfx="impact@0 cheer",
    mood="triumph")
img(60, "America's army was still small.", ov="sea", label="ACROSS THE ATLANTIC", sfx="sea cheer")


@cart("But America had something no other country had left", "MEN · MONEY · FACTORIES", sfx="march factory")
def s_america(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=28)
    building_row(c, 470, t, seed=4, h0=80, h1=160, cols=("#B85A3A", "#A84A2A", "#C86A4A"))
    for i in range(4):
        smoke(c, 160 + i * 300, 260, t + i, n=4, s=1.0, col=(0.4, 0.4, 0.42), rise=120)
    army(c, -200 + 300 * u, 1400, 700, rows=3, s=0.6, uni="doughboy", t=t, march=True, flags="usa")


@cart("The clock was now ticking for Germany.", "THE CLOCK IS TICKING", sfx="clock heart", mood="tense")
def s_tick(c, u, t):
    interior(c, t, wall="#8A8070", night=True)
    clock_face(c, 880, 330, 170, 11, 40 + 15 * u + (t % 1) * 0.3)
    char(c, "kaiser", 330, 690, 1.7, expr="worried", t=t, look=1)


# ======================================================================== PASSCHENDAELE
@cart("Meanwhile, on the Western Front, the slaughter went on.", "THE SLAUGHTER GOES ON", sfx="cannon*3",
      mood="dark")
def s_slaughter(c, u, t):
    nomansland(c, t, "storm", 400)
    for i in range(4):
        shell_burst(c, 200 + i * 280, 600, t, 2.2, i * 0.5, 1.0)
    rain(c, t, n=100)


img(61, "In the second half of 1917, the British attacked near Ypres", ov="rain", label="PASSCHENDAELE · 1917",
    sfx="rainH")


@cart("It rained and rained.", "RAIN · RAIN · RAIN", sfx="rainH thunder@1")
def s_rained(c, u, t):
    nomansland(c, t, "storm", 380)
    rain(c, t, heavy=True)
    for i in range(3):
        soldier(c, 300 + i * 340, 680, 1.1, "tommy", t + i, arms="hug", expr="sad")


@cart("Men and horses slipped off wooden duckboards", "AN OCEAN OF MUD", sfx="rainH heart")
def s_mud(c, u, t):
    sky(c, "storm", 400)
    c.set_source(vgrad(c, 360, H, hexc("#6A5A42"), hexc("#3E3226")))
    c.rectangle(0, 360, W, H)
    c.fill()
    for i in range(8):
        crater(c, 80 + i * 170, 520 + (i % 3) * 60, 90)
    for k in range(-1, 20):
        rrect(c, k * 70 + (t * 10) % 70, 620, 60, 14, 2)
        fill(c, hexc("#8A6A48"))
    for i in range(5):
        soldier(c, 100 + i * 230 + 40 * u, 625, 1.0, "tommy", t + i, walk=t * 2.5 + i, arms="musket", expr="sad")
    rain(c, t, heavy=True)


@cart("After more than three months, the village of Passchendaele was finally captured.",
      "HUNDREDS OF THOUSANDS FALLEN", sfx="wind", mood="sad")
def s_ruins(c, u, t):
    nomansland(c, t, "grey", 420, wire=False)
    for i, x in enumerate((240, 420, 700, 980)):
        poly(c, [(x - 60, 520), (x - 50, 440 - i * 10), (x - 10, 460), (x + 10, 420), (x + 50, 470), (x + 60, 520)])
        fill(c, hexc("#8A847A"))
    smoke_bank(c, 480, t, a=0.3)


# ======================================================================== 1918
@cart("By the spring of 1918, Germany knew it had one last chance.", "1918 · ONE LAST CHANCE", sfx="clock",
      mood="tense")
def s_lastchance(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE, "russia": "#D9C9C9"})
    clock_face(c, 1130, 580, 80, 11, 45 + 10 * u)


@cart("Ludendorff decided to gamble everything on one massive attack.", "LUDENDORFF'S GAMBLE", sfx="heart")
def s_gamble(c, u, t):
    interior(c, t, wall="#B8A888", night=True)
    table(c, 640, 690, 600, 130, cloth="#3A4A3A")
    char(c, "ludendorff", 640, 640, 1.8, arms="fist", expr="angry", t=t)
    candle(c, 330, 560, t, 1.0)


img(62, "On the twenty-first of March, 1918, the German Spring Offensive began.", ov="smoke",
    label="THE SPRING OFFENSIVE · 21 MARCH 1918", sfx="cannon*4 volley*2", mood="epic")


@cart("After a short but devastating bombardment", "STORMTROOPERS", sfx="volley*3 explosion@1")
def s_storm(c, u, t):
    nomansland(c, t, "grey", 400)
    smoke_bank(c, 520, t, a=0.4)
    for i in range(5):
        soldier(c, -100 + i * 160 + 600 * u, 680 - (i % 2) * 40, 1.0, "hun", t + i, walk=t * 7 + i,
                arms="musket")
    shell_burst(c, 1000, 640, t, 1.8, 0, 1.1)


@cart("For the first time in years, the front moved.", "THE FRONT MOVES", sfx="march")
def s_moves(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE},
             arrows=[([(540, 300), (500, 320), (470, 340)], "#5A5A4A"), ([(560, 340), (520, 350), (480, 360)],
                                                                         "#5A5A4A")], pulses=[(PARIS, "#C8322F")])


img(63, "They shelled Paris with a giant long-range gun", ov="flash+smoke", label="THE PARIS GUN · 120 KM",
    sfx="cannon*2")


@cart("The Allies were close to breaking.", "ON THE BRINK", sfx="heart volley*2", mood="dark")
def s_brink(c, u, t):
    trench(c, t, skyk="storm")
    for i in range(4):
        shell_burst(c, 200 + i * 300, 260, t, 1.6, i * 0.4, 0.7)
    for i, x in enumerate((300, 640, 980)):
        soldier(c, x, 690, 1.25, "tommy", t + i, arms="musket", expr="worried")


@cart("But the German army had lost its best soldiers in the attacks.", "EXHAUSTED & HUNGRY", sfx="room")
def s_depot(c, u, t):
    interior(c, t, wall="#9A8A6A", window=False)
    for k in range(6):
        rrect(c, 80 + k * 200, 470, 160, 110, 4)
        fill_ol(c, hexc("#B88A52"), w=2)
    for i in range(4):
        soldier(c, 220 + i * 280, 690, 1.25, "hun", t + i, arms="hold", item="paper", expr="happy" if i % 2 else "shock")
        ellipse(c, 260 + i * 280, 590, 18, 10)
        fill(c, hexc("#D9A85A"))


img(64, "And the Americans were now arriving.", label="10,000 AMERICANS A DAY", sfx="march cheer", mood="triumph")


@cart("In July, at the Second Battle of the Marne", "SECOND MARNE · JULY 1918", sfx="cannon*3")
def s_marne2(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE})
    arrow(c, [(500, 300), (470, 330), (462, 340)], 1.0, "#5A5A4A")
    for k in range(6):
        seg(c, (430 + k * 12, 360 - k * 4), (442 + k * 12, 350 - k * 4), 7, hexc("#2B4C9B"))
    pulse_dot(c, 462, 345, t, "#2B4C9B")


@cart("The gamble had failed.", "THE GAMBLE HAS FAILED", sfx="impact@0", mood="triumph")
def s_failed(c, u, t):
    interior(c, t, wall="#B8A888", night=True)
    table(c, 640, 690, 600, 130, cloth="#3A4A3A")
    char(c, "ludendorff", 640, 690, 1.8, expr="sad", t=t, seated=False)


# ======================================================================== HUNDRED DAYS
img(65, "On the eighth of August, 1918, the Allies struck back near Amiens", ov="smoke",
    label="AMIENS · 8 AUGUST 1918", sfx="tank cannon*3 plane", mood="epic")


@cart("The German lines collapsed.", "THE GERMAN LINES COLLAPSE", sfx="cheer volley*2")
def s_collapse(c, u, t):
    nomansland(c, t, "day", 400)
    tank(c, 200 + 300 * u, 640, 0.8, 1, t)
    army(c, 700, 1280, 600, rows=2, s=0.55, uni="hun", t=t, face=-1, arms="up", expr="worried")


@cart("Ludendorff called it", "“THE BLACK DAY OF THE GERMAN ARMY”", sfx="heart", mood="dark")
def s_blackday(c, u, t):
    interior(c, t, wall="#8A8070", night=True)
    char(c, "ludendorff", 640, 690, 1.9, expr="sad", t=t, arms="hand_in")
    tint(c, (0, 0, 0), 0.25)


@cart("It was the beginning of the Hundred Days Offensive.", "THE HUNDRED DAYS OFFENSIVE", sfx="march cannonD*2",
      mood="triumph")
def s_hundred(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "france": ENTENTE},
             arrows=[([(450, 360), (500, 330), (540, 300)], "#2B4C9B"), ([(470, 380), (520, 360), (560, 330)],
                                                                         "#2B4C9B")])


@cart("Animals, too, played their part in this war.", "ANIMALS AT WAR", sfx="gallop", mood="calm")
def s_animals(c, u, t):
    landscape(c, t, "grey", "mud", 420, seed=30, trees=False)
    for i in range(3):
        horse(c, 200 + i * 300 + 60 * u, 650, 0.8, 1, ["#7A5232", "#3A2A22", "#A87A4A"][i], t + i, gallop=False)
    cannon(c, 1050, 660, 1.0, 1, t, fire=False)


@cart("And pigeons carried messages when telephone lines were cut.", "MESSENGER PIGEONS", sfx="wind")
def s_pigeons(c, u, t):
    sky(c, "day")
    clouds(c, t, n=6, speed=30)
    for i in range(4):
        pigeon(c, -100 + 1500 * ((u + i * 0.22) % 1), 200 + i * 90, 0.9, 1, t + i)


img(66, "In October 1918, an American battalion was trapped", mode="split", who="gunther", name="CHER AMI",
    bg="trench", label="THE LOST BATTALION", sfx="cannon*2", mood="tense")


@cart("She was shot through the chest", "CHER AMI", sfx="volley*2 wind", mood="triumph")
def s_cherami(c, u, t):
    sky(c, "grey")
    smoke_bank(c, 500, t, a=0.5)
    pigeon(c, -100 + 1500 * u, 300 + 40 * math.sin(t * 2), 1.4, 1, t)
    for i in range(3):
        shell_burst(c, 300 + i * 350, 700, t, 2.0, i * 0.5, 0.8)


@cart("The shelling stopped. Almost two hundred men were saved.", "~200 MEN SAVED", sfx="cheer")
def s_saved2(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=31)
    army(c, 100, 1180, 700, rows=2, s=0.7, uni="doughboy", t=t, arms="cheer", expr="happy", flags="usa")


@cart("Germany's allies began to fall.", "THE CENTRAL POWERS COLLAPSE", sfx="crack@0.5 crack@1.5", mood="tense")
def s_allies_fall(c, u, t):
    p = smooth(u * 1.3)
    cols = {"germany": CENTRAL, "austria": CENTRAL, "ottoman": CENTRAL, "balkans": CENTRAL}
    for i, n in enumerate(("balkans", "ottoman", "austria")):
        if p > (i + 1) * 0.25:
            cols[n] = "#BBBBBB"
    mapscene(c, t, u, colors=cols)


@cart("In Germany itself, sailors mutinied.", "REVOLUTION IN GERMANY", sfx="angry")
def s_kiel(c, u, t):
    street_bg(c, t, skyk="grey")
    crowd(c, 0, 1280, 720, rows=3, s=0.75, t=t, expr="angry", arms="fist", flags=["red", "red"])
    army(c, 300, 980, 560, rows=1, s=0.5, uni="sailor", t=t, arms="fist", expr="angry")


@cart("On the ninth of November, Kaiser Wilhelm the Second abdicated", "THE KAISER ABDICATES", sfx="train")
def s_kaiser_leaves(c, u, t):
    landscape(c, t, "grey", "grass", 430, seed=33)
    seg(c, (0, 600), (W, 600), 6, hexc("#5A4A3A"))
    train(c, 200 + 1000 * u, 600, 0.8, 1, t, cars=2)
    char(c, "kaiser", 300, 700, 1.4, expr="sad", t=t, face=1)


@cart("Germany was now a republic. And it asked for peace.", "GERMANY ASKS FOR PEACE", sfx="room")
def s_peace(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=34)
    flag(c, 640, 700, t, "white", pole=400, w=200, h=130)


img(67, "In the early hours of the eleventh of November, 1918", label="COMPIÈGNE · 11 NOVEMBER 1918",
    sfx="quill clock", mood="calm")


@cart("The fighting would stop at eleven o'clock that morning.", "11 O'CLOCK", sfx="clock")
def s_clock11(c, u, t):
    interior(c, t, wall="#C9B48E")
    clock_face(c, 640, 330, 200, 10, 50 + 9 * u)


@cart("The eleventh hour of the eleventh day of the eleventh month.", "11 · 11 · 11", sfx="clock", zoom=0.1)
def s_111111(c, u, t):
    c.set_source_rgba(*hexc("#1E1A16"))
    c.paint()
    clock_face(c, 640, 360, 240, 10, 55 + 4 * u)


@cart("But even on that last morning, men kept fighting and dying.", "THE LAST MORNING", sfx="cannon*3 volley*1",
      mood="dark")
def s_lastmorning(c, u, t):
    nomansland(c, t, "dawn", 400)
    for i in range(3):
        shell_burst(c, 250 + i * 360, 620, t, 2.0, i * 0.6, 1.0)


@cart("At one minute before eleven, an American soldier named Henry Gunther", "10:59 · HENRY GUNTHER",
      sfx="heart mg@3", zoom=0.1)
def s_gunther(c, u, t):
    nomansland(c, t, "grey", 400)
    soldier(c, 200 + 500 * u, 680, 1.4, "doughboy", t, walk=t * 6, arms="musket", expr="stern")
    machine_gun(c, 1100, 620, 1.2, -1, t, fire=False)
    for i in range(2):
        soldier(c, 1150 + i * 80, 620, 0.9, "hun", t + i, face=-1, arms="up" if (t * 2) % 2 < 1 else "down",
                expr="worried")


@cart("Henry Gunther is believed to be the last soldier killed", "THE LAST SOLDIER KILLED", sfx="wind", mood="sad")
def s_lastkilled(c, u, t):
    landscape(c, t, "grey", "grass", 420, trees=False, seed=36)
    seg(c, (640, 700), (640, 520), 12, hexc("#EDE6D6"))
    seg(c, (590, 570), (690, 570), 12, hexc("#EDE6D6"))
    c.save()
    c.translate(640, 520)
    draw_hat(c, "brodie", 26, None, t)
    c.restore()


@cart("One minute later, the guns fell silent.", "11:00 · SILENCE", sfx="birds bellL@0.5", mood="calm", zoom=0.05)
def s_silence(c, u, t):
    nomansland(c, t, "dawn", 420, wet=False)
    sun(c, 640, 320, 70, "#FFE9A8", t, rays=True)


@cart("Along the front, soldiers on both sides climbed out of their trenches.", "IT'S OVER", sfx="cheer",
      mood="triumph")
def s_climbout(c, u, t):
    landscape(c, t, "gold", "mud", 420, trees=False, seed=37, sunpos=(640, 300))
    barbed_wire(c, -20, W + 20, 560, 0.8)
    for i in range(4):
        soldier(c, 160 + i * 140, 690, 1.0, "tommy", t + i, arms="cheer" if i % 2 else "down",
                expr="happy" if i % 2 else "sad")
        soldier(c, 760 + i * 140, 690, 1.0, "hun", t + i, face=-1, arms="cheer" if i % 2 == 0 else "down",
                expr="happy" if i % 2 == 0 else "sad")


img(68, "In London, Paris and New York, huge crowds celebrated in the streets.", label="ARMISTICE DAY · 11 NOV 1918",
    sfx="cheer bell@0.5 bell@1.5")


@cart("After four years, three months and two weeks, the Great War was over.", "THE GREAT WAR IS OVER",
      sfx="bellL@0 cheer", zoom=0.05)
def s_over(c, u, t):
    sky(c, "gold")
    sun(c, 640, 380, 90, "#FFE9A8", t, rays=True)
    c.set_source_rgba(*hexc("#3A2A1E"))
    c.rectangle(0, 560, W, H)
    c.fill()
    poppies(c, 560, 720, t, n=100)


# ======================================================================== AFTERMATH
@cart("But the world that emerged was not the world that had gone to war.", "~10 MILLION SOLDIERS DEAD",
      sfx="wind", mood="sad")
def s_aftermath(c, u, t):
    landscape(c, t, "dusk", "grass", 400, trees=False, seed=38)
    crosses(c, 700, t, n=9, rows=5)


@cart("An entire generation of young men had been scarred", "A LOST GENERATION", sfx="wind heart")
def s_lostgen(c, u, t):
    street_bg(c, t, skyk="grey")
    for i in range(5):
        soldier(c, 160 + i * 240, 700, 1.2, "tommy", t + i, arms="down", expr="sad", walk=t * 2 + i, hat="peaked",
                plume="#8A7D52")
    tint(c, (0.2, 0.15, 0.1), 0.25)


img(76, "Soldiers came home with missing limbs", label="COMING HOME", sfx="train murmur")


@cart("And as the war ended, another killer swept across the world.", "THE SPANISH FLU · 1918", sfx="heart",
      mood="dark")
def s_flu(c, u, t):
    hospital(c, t, n=6)
    for i in range(3):
        char(c, "nurse", 220 + i * 400, 700, 1.1, t=t + i, arms="hold")


@cart("Four great empires had collapsed.", "FOUR EMPIRES FALL", sfx="crack@0.3 crack@1 crack@1.7 crack@2.4",
      mood="tense")
def s_empires(c, u, t):
    hall(c, t, night=True)
    for i, (x, kind) in enumerate(((220, "de"), (500, "ah"), (780, "ru"), (1060, "ot"))):
        fall = clamp((u * 4 - i))
        flag(c, x, 640, t, kind, pole=260, w=110, h=70)
        draw_crown(c, x + 50, 300 + 380 * fall * fall, 2.0)


img(77, "From their ruins, new countries appeared on the map.", mode="map", label="EUROPE · 1919",
    sfx="whoosh@0")
img(69, "In 1919, the victorious Allies met at the Palace of Versailles", ov="light",
    label="VERSAILLES · 28 JUNE 1919", sfx="murmur quill")


@cart("Germany lost territory, its colonies, most of its army and navy.", "THE TREATY OF VERSAILLES",
      sfx="crack@0.5")
def s_versailles(c, u, t):
    mapscene(c, t, u, colors={"germany": CENTRAL, "poland": "#E8B8C8", "france": ENTENTE},
             glow=("germany", "#C8322F", 0.25 + 0.2 * math.sin(t * 3)))


@cart("Many Germans felt humiliated and betrayed.", "HUMILIATION", sfx="angry", mood="dark")
def s_humil(c, u, t):
    street_bg(c, t, skyk="grey")
    crowd(c, 0, 1280, 720, rows=3, s=0.75, t=t, expr="angry", arms="fist")
    tint(c, (0, 0, 0), 0.25)


@cart("Among the bitter veterans was a former corporal", None, sfx="heart wind", zoom=0.04)
def s_corporal(c, u, t):
    sky(c, "dusk")
    c.set_source_rgba(*hexc("#1A1414"))
    c.rectangle(0, 540, W, H)
    c.fill()
    soldier(c, 300 + 300 * u, 620, 1.5, "hun", t, walk=t * 3, coat="#141010", trou="#141010", skin=hexc("#141010"),
            blink=False, arms="down")
    vignette(c, 0.6)


@cart("Barely twenty years later, the world would be at war again.", "1939", sfx="thunder@0.5", zoom=0.05)
def s_1939(c, u, t):
    mapscene(c, t, u, labels=False)
    clouds(c, t, n=10, col=(0.15, 0.15, 0.18, 0.85), speed=40, y0=0, y1=700, scale=2.0)
    if (t % 3) < 0.1:
        tint(c, (1, 1, 1), 0.4)


@cart("People at the time called it", "“THE WAR TO END ALL WARS”", sfx="wind", mood="sad")
def s_endall(c, u, t):
    landscape(c, t, "dusk", "grass", 420, trees=False, seed=40)
    crosses(c, 700, t, n=8)


@cart("But the First World War changed almost everything.", "IT CHANGED EVERYTHING", sfx="plane tank",
      mood="epic_soft")
def s_changed(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.set_source(vgrad(c, 470, H, hexc("#8A9A6A"), hexc("#6A7A4A")))
    c.rectangle(0, 470, W, H)
    c.fill()
    biplane(c, 300 + 400 * u, 200, 0.8, 1, t, col="#7A8A5A", mark="roundel")
    tank(c, 900, 640, 0.8, -1, t)
    char(c, "worker", 300, 700, 1.3, t=t, arms="cheer", expr="happy")


@cart("It pulled women into factories and offices", "VOTES FOR WOMEN", sfx="cheer")
def s_votes(c, u, t):
    street_bg(c, t)
    rrect(c, 560, 520, 160, 140, 8)
    fill_ol(c, hexc("#7A5232"), w=3)
    for i in range(4):
        char(c, "worker", 180 + i * 300 + (0 if i < 2 else 120), 700, 1.3, arms="cheer", expr="happy", t=t + i,
             dress=["#6A4A7A", "#3E6A4A", "#7A3A3A", "#4A5A7A"][i])


img(79, "Today, on the eleventh of November", ov="fog", label="REMEMBRANCE · 11 NOVEMBER", sfx="bellL@0.3 wind",
    mood="sad")
img(70, "In Britain and the Commonwealth, they wear red poppies", label="THE POPPY", sfx="wind birds")


@cart("A Canadian doctor, John McCrae", "JOHN McCRAE · 1915", sfx="quill wind")
def s_mccrae(c, u, t):
    landscape(c, t, "dusk", "grass", 420, trees=False, seed=41)
    poppies(c, 520, 720, t, n=90)
    char(c, "mccrae", 640, 690, 1.8, arms="write", item="paper", expr="sad", t=t)


img(78, "\"In Flanders fields the poppies blow", label="“IN FLANDERS FIELDS”", sfx="wind")


@cart("It all began with two bullets", "SARAJEVO · 1914", sfx="shot@0.8 heart", mood="sad")
def s_began(c, u, t):
    street_bg(c, t, skyk="dawn")
    tint(c, (0.4, 0.3, 0.2), 0.35)


@cart("And it ended with millions of crosses", "ROW ON ROW", sfx="wind")
def s_crosses(c, u, t):
    landscape(c, t, "sunset", "grass", 380, trees=False, seed=42, sunpos=(640, 330))
    crosses(c, 720, t, n=9, rows=6)
    poppies(c, 640, 720, t, n=60)


@cart("This was the First World War.", "THE FIRST WORLD WAR · 1914–1918", sfx="impact@0 bellL@1", zoom=0.04)
def s_end(c, u, t):
    sky(c, "sunset")
    sun(c, 640, 430, 90, "#FFD27A", t, rays=True)
    c.set_source_rgba(*hexc("#2A1C1C"))
    c.rectangle(0, 560, W, H)
    c.fill()
    poppies(c, 560, 720, t, n=120)
    vignette(c, 0.5)
