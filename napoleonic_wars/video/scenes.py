"""The 135 scenes of the video, in narration order (same order as make_prompts.S).

Each scene is f(c, u, t): u = progress 0..1 through the scene, t = seconds
since the scene started. A scene may carry a yellow headline label.
"""
import math

from gfx import *  # noqa: F401,F403

SCENES = []


def sc(label=None, focus=(640, 360), zoom=0.07):
    def deco(f):
        SCENES.append(dict(fn=f, label=label, focus=focus, zoom=zoom))
        return f
    return deco


def battle_bg(c, t, skyk="day", ground="grass", horizon=420, seed=5, smokey=True):
    landscape(c, t, skyk, ground, horizon, seed=seed)
    if smokey:
        smoke_bank(c, horizon + 10, t, a=0.35, seed=seed)


# =============================================================== COLD OPEN
@sc("WATERLOO · 18 JUNE 1815")
def s001(c, u, t):
    landscape(c, t, "storm", "mud", 400, seed=3)
    village(c, 440, t, x0=760, n=3, windmill=False)
    rain(c, t, heavy=True)
    fog(c, 0.4, 380, 560, t)


@sc("IT RAINED ALL NIGHT")
def s002(c, u, t):
    landscape(c, t, "storm", "mud", 380, trees=False, seed=8)
    tent(c, 200, 470, 1.4, "#D9CBB0")
    tent(c, 1080, 460, 1.2, "#D9CBB0")
    campfire(c, 640, 600, t, 1.3)
    for i, (x, uni, f) in enumerate(((470, "br", 1), (540, "fr", 1), (760, "br", -1), (830, "fr", -1))):
        soldier(c, x, 640 - (i % 2) * 20, 0.95, uni, t + i, face=f, arms="down", expr="sad")
    rain(c, t, heavy=True)


@sc("THE DUKE OF WELLINGTON", focus=(640, 400))
def s003(c, u, t):
    landscape(c, t, "grey", "grass", 400, seed=4)
    army(c, 80, 1200, 470, rows=4, s=0.5, uni="br", t=t, flags="uk")
    mounted(c, 640, 690, 1.2, 1, t, who="wellington", col="#7A5232")
    rain(c, t, n=80)


@sc("THE FRENCH ARMY")
def s004(c, u, t):
    landscape(c, t, "grey", "grass", 400, seed=6)
    army(c, 60, 1220, 500, rows=4, s=0.5, uni="fr", t=t, face=-1, flags="fr")
    for x in (200, 520, 840, 1120):
        cannon(c, x, 650, 1.1, -1, t, fire=False)
    rain(c, t, n=80)


@sc("NAPOLEON BONAPARTE", focus=(640, 300), zoom=0.12)
def s005(c, u, t):
    landscape(c, t, "storm", "mud", 470, trees=False, seed=2)
    mounted(c, 640, 760, 1.9, 1, t, who="napoleon", col="#F2EEE6", expr="stern")
    rain(c, t, heavy=True)
    vignette(c, 0.55)


@sc("EMPEROR")
def s006(c, u, t):
    hall(c, t, red=True)
    throne(c, 640, 640, 1.5)
    napoleon(c, 640, 690, 2.0, arms="crown", item="laurel", robe="#9C2A3A", expr="proud", t=t)
    sun(c, 640, 120, 1, t=t, rays=True)


@sc("A NEW MAP OF EUROPE")
def s007(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0"})
    for i, (x, y) in enumerate(((470, 400), (580, 330), (700, 300), (760, 400), (980, 330))):
        if u > i * 0.15:
            soldier(c, x, y, 0.45, "fr", t)
    napoleon(c, 210, 760, 2.2, arms="point", expr="smirk", t=t)


@sc("WATERLOO")
def s008(c, u, t):
    landscape(c, t, "dawn", "grass", 430, seed=9)
    village(c, 470, t, x0=330, n=5, seed=4)
    army(c, 40, 260, 440, rows=2, s=0.28, uni="br", t=t)
    army(c, 1040, 1250, 440, rows=2, s=0.28, uni="fr", t=t, face=-1)
    fog(c, 0.5, 380, 600, t)


@sc("BUT FIRST... GO BACK")
def s009(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#3A2A1A"), hexc("#B8915A")))
    c.paint()
    for i in range(18):
        a = t * (0.8 + i * 0.05) + i
        r = 60 + (i * 37 + t * 120) % 520
        x, y = 640 + math.cos(a) * r, 360 + math.sin(a) * r * 0.6
        c.save()
        c.translate(x, y)
        c.rotate(a)
        rrect(c, -40, -28, 80, 56, 4)
        fill_ol(c, hexc("#F1E3C2"), w=2)
        c.select_font_face("DejaVu Sans", 0, 1)
        c.set_font_size(18)
        c.move_to(-26, 8)
        c.set_source_rgba(0.3, 0.2, 0.1, 1)
        c.show_text(str(1815 - (i * 2) % 27))
        c.restore()
    vignette(c, 0.6)


@sc("THE NAPOLEONIC WARS", zoom=0.05)
def s010(c, u, t):
    sky(c, "sunset")
    sun(c, 640, 430, 90, "#FFD27A", t, rays=True)
    hills(c, 520, cols=("#5A3A3A", "#3A2626"), amp=20)
    c.set_source_rgba(*hexc("#2A1C1C"))
    c.rectangle(0, 560, W, H)
    c.fill()
    army(c, 0, 1280, 640, rows=3, s=0.42, uni="fr", t=t, march=True, coat="#2A1C1C", trou="#2A1C1C",
         plume="#2A1C1C", belts=False, skin=hexc("#2A1C1C"))
    napoleon(c, 640, 560, 1.7, coat="#1A1212", trou="#1A1212", waist="#1A1212", skin=hexc("#1A1212"),
             epaulettes=False, hair_col="#1A1212", arms="hand_in", t=t, blink=False)


# =============================================================== REVOLUTION
@sc("1789 · THE FRENCH REVOLUTION")
def s011(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.set_source(vgrad(c, 470, H, hexc("#C9B79A"), hexc("#A8967A")))
    c.rectangle(0, 470, W, H)
    c.fill()
    bastille(c, 640, 520, 1.0)
    smoke(c, 420, 220, t, n=8, s=1.5, col=(0.4, 0.38, 0.36), rise=140)
    crowd(c, 0, 1280, 720, rows=4, s=0.75, t=t, flags=["fr", "red", "fr"])


@sc("KING LOUIS XVI")
def s012(c, u, t):
    hall(c, t, night=True)
    king(c, 640, 690, 2.3, expr="worried", t=t, hat="none", arms="shrug")
    draw_crown(c, 700 + 60 * smooth(u), 300 + 80 * smooth(u), 1.8 + 0 * u)
    crowd(c, 0, 1280, 470, rows=1, s=0.6, t=t, expr="angry", arms="fist")
    tint(c, (0.1, 0.05, 0.1), 0.25)


@sc("THE KINGS OF EUROPE")
def s013(c, u, t):
    hall(c, t)
    rrect(c, 0, 470, W, 250, 0)
    fill(c, hexc("#9C958A"))
    for k in range(0, W, 80):
        rrect(c, k, 470, 78, 40, 2)
        fill_ol(c, hexc("#A9A296"), w=2)
    for i, (x, rob) in enumerate(((240, "#EEEDE6"), (500, "#1F2A44"), (780, "#C8322F"), (1040, "#E2B53B"))):
        hop = 10 * abs(math.sin(t * 2 + i))
        king(c, x, 640 - hop, 1.7, robe=rob, expr="shock", t=t)
        rrect(c, x - 140, 520, 280, 200, 4)
        fill_ol(c, hexc("#9C958A"), w=2)


@sc("WAR ON FRANCE")
def s014(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0", "britain": "#E79A94", "austria": "#F2F2F2", "prussia": "#B9B9C6",
                         "iberia": "#F2D27A"})
    p = smooth(u * 1.3)
    arrow(c, [(380, 230), (430, 290), (450, 340)], p, "#C8322F")
    arrow(c, [(760, 400), (650, 400), (545, 410)], p, "#EEEDE6")
    arrow(c, [(720, 290), (620, 320), (540, 350)], p, "#555566")
    arrow(c, [(330, 540), (380, 500), (430, 470)], p, "#E2B53B")


@sc("CHAOS")
def s015(c, u, t):
    landscape(c, t, "grey", "dry", 420, seed=7)
    tent(c, 220, 520, 1.2, "#CFC2A5")
    tent(c, 1010, 500, 1.0, "#CFC2A5")
    for i in range(7):
        x = 150 + i * 160
        soldier(c, x, 660 - (i % 2) * 40, 0.9, "fr_rag", t + i, face=1 if i % 2 else -1,
                arms=["shrug", "down", "musket", "shrug"][i % 4], expr=["worried", "shock", "neutral"][i % 3],
                look=math.sin(t + i))


@sc("CORSICA · 1769")
def s016(c, u, t):
    sky(c, "day")
    sun(c, 1050, 120, 50, t=t)
    clouds(c, t, n=3)
    mount(c, 380, snow=False, col="#6FA25A")
    sea(c, t, 520)
    for i in range(7):
        x = 160 + i * 120
        rrect(c, x, 400 - (i % 3) * 25, 100, 120 + (i % 3) * 25, 3)
        fill_ol(c, hexc(["#F0E2C8", "#E9C9A0", "#F2D6C6"][i % 3]), w=2)
        poly(c, [(x - 6, 400 - (i % 3) * 25), (x + 106, 400 - (i % 3) * 25), (x + 50, 370 - (i % 3) * 25)])
        fill(c, hexc("#C0603A"))
    boat(c, 980, 600, 0.9, t)


@sc("AN OUTSIDER")
def s017(c, u, t):
    interior(c, t, wall="#C9B48E")
    table(c, 380, 640, 300, 100)
    book(c, 380, 540, 0.7)
    young_nap(c, 300, 690, 1.5, arms="hold", item="paper", expr="stern", t=t, look=1)
    for i, x in enumerate((840, 960, 1080)):
        soldier(c, x, 650, 1.15, "conscript", t + i, face=-1, arms="shrug" if i != 1 else "point",
                expr="happy", walk=None)


@sc("TOULON · 1793")
def s018(c, u, t):
    sky(c, "day")
    clouds(c, t)
    mount(c, 420, snow=False, col="#8EA06A", seed=5)
    sea(c, t, 440)
    for i, x in enumerate((360, 700, 1020)):
        ship(c, x, 580 + i * 10, 0.6, 1 if i % 2 else -1, t, "uk")
    for x in (120, 1180):
        rrect(c, x - 70, 360, 140, 90, 4)
        fill_ol(c, hexc("#B5AFA2"), w=2)


@sc("THE YOUNG ARTILLERY CAPTAIN")
def s019(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 470)
    for x in (900, 1150):
        ship(c, x, 600, 0.45, -1, t, "uk")
    c.move_to(0, 470)
    c.curve_to(300, 380, 600, 420, 760, 720)
    c.line_to(0, 720)
    fill(c, hexc("#8EAA5A"))
    for i, x in enumerate((420, 560)):
        cannon(c, x, 540 + i * 40, 1.1, 1, t, fire=False)
    young_nap(c, 200, 640, 1.6, arms="point", expr="stern", t=t)


@sc("THE BRITISH RETREAT")
def s020(c, u, t):
    sky(c, "night")
    stars(c, t)
    sea(c, t, 470, night=True)
    for i, x in enumerate((700, 980)):
        ship(c, x + 60 * u, 600, 0.5, 1, t, "uk", burning=(i == 0))
    flames(c, 1180, 470, 200, 120, t)
    c.move_to(0, 470)
    c.curve_to(200, 400, 350, 430, 500, 720)
    c.line_to(0, 720)
    fill(c, hexc("#2E3A2A"))
    for i, x in enumerate((180, 300)):
        cannon(c, x, 520 + i * 50, 1.0, 1, t, phase=i * 0.8)


@sc("PARIS · 1795")
def s021(c, u, t):
    sky(c, "grey")
    building_row(c, 470, t, seed=3)
    c.set_source(vgrad(c, 470, H, hexc("#B9AE98"), hexc("#9A8E78")))
    c.rectangle(0, 470, W, H)
    c.fill()
    crowd(c, 0, 1280, 700, rows=4, s=0.75, t=t, flags=["white", "white"], expr="angry", arms="fist", walk=True)


@sc("A WHIFF OF GRAPESHOT")
def s022(c, u, t):
    sky(c, "grey")
    building_row(c, 470, t, seed=3)
    c.set_source(vgrad(c, 470, H, hexc("#B9AE98"), hexc("#9A8E78")))
    c.rectangle(0, 470, W, H)
    c.fill()
    crowd(c, 820, 1280, 560, rows=3, s=0.55, t=t, face=1, expr="shock", arms="up", cheer=True)
    for i, x in enumerate((360, 500)):
        cannon(c, x, 640 - i * 30, 1.2, 1, t, phase=i * 1.1)
    young_nap(c, 170, 690, 1.5, arms="point", expr="stern", t=t)
    smoke_bank(c, 560, t, a=0.3)


@sc("THE ARMY OF ITALY · 1796")
def s023(c, u, t):
    landscape(c, t, "grey", "stone", 430, mountains=True, trees=False, seed=2)
    campfire(c, 640, 620, t)
    for i in range(6):
        x = 220 + i * 170
        if 560 < x < 720:
            continue
        soldier(c, x, 660 - (i % 2) * 30, 1.0, "fr_rag", t + i, face=1 if x < 640 else -1, arms="down",
                expr="sad", barefoot=(i % 2 == 0))


@sc("“THE MOST FERTILE PLAINS IN THE WORLD”")
def s024(c, u, t):
    sky(c, "day")
    sun(c, 1100, 160, 60, t=t, rays=True)
    hills(c, 470, cols=("#9ED36E", "#7FBF5A"), seed=8)
    c.move_to(0, 720)
    c.line_to(0, 380)
    c.curve_to(200, 360, 360, 420, 460, 720)
    fill(c, hexc("#9A948A"))
    young_nap(c, 230, 420, 1.3, arms="point", expr="happy", t=t)
    army(c, 380, 1280, 720, rows=2, s=0.7, uni="fr_rag", t=t, face=-1, arms="cheer", expr="happy")


@sc("ARCOLE · RIVOLI · LODI")
def s025(c, u, t):
    landscape(c, t, "day", "grass", 400, trees=False, seed=3)
    river(c, 520, 720, t)
    bridge(c, 0, 1280, 560)
    young_nap(c, 640, 560, 1.6, arms="flag", item="fr", expr="shout", t=t, walk=t * 6)
    army(c, 60, 520, 560, rows=1, s=0.9, uni="fr", t=t, march=True, run=True)
    smoke_bank(c, 380, t, a=0.5)


@sc("FASTER THAN HIS ENEMIES")
def s026(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0", "austria": "#F2F2F2", "italy": "#CDE6B0"})
    c.save()
    c.translate(-700, -400)
    c.scale(2.0, 2.0)
    europe(c, t, colors={"france": "#8FA8E0", "austria": "#F2F2F2", "italy": "#CDE6B0"}, labels=False)
    p = smooth(u * 1.4)
    arrow(c, [(700, 395), (650, 430), (610, 450)], p * 0.6, "#EEEDE6", 7, 16)
    arrow(c, [(760, 420), (690, 450), (640, 470)], p * 0.5, "#EEEDE6", 7, 16)
    arrow(c, [(530, 420), (580, 440), (620, 455)], p, "#2B4C9B", 9, 20)
    arrow(c, [(540, 440), (600, 470), (650, 480)], clamp(p * 1.2 - 0.2), "#2B4C9B", 9, 20)
    c.restore()


@sc("A NATIONAL HERO")
def s027(c, u, t):
    sky(c, "day")
    building_row(c, 470, t, seed=6)
    c.set_source(vgrad(c, 470, H, hexc("#C9BBA0"), hexc("#A89A80")))
    c.rectangle(0, 470, W, H)
    c.fill()
    crowd(c, 0, 400, 600, rows=3, s=0.65, t=t, flags=["fr"])
    crowd(c, 880, 1280, 600, rows=3, s=0.65, t=t, face=-1, flags=["fr"])
    mounted(c, 640, 690, 1.25, 1, t, who="ynap", col="#F2EEE6", expr="happy")
    for i in range(30):
        ph = (t * 0.6 + i * 0.137) % 1
        x = (i * 97) % W + math.sin(t * 2 + i) * 20
        ellipse(c, x, ph * 720, 6, 4, rot=t + i)
        fill(c, hexc(["#E84A5F", "#FFD166", "#F7F4EC", "#2B4C9B"][i % 4]))


# =============================================================== EGYPT
@sc("THE ROYAL NAVY")
def s028(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.move_to(800, 380)
    c.line_to(860, 300)
    c.line_to(1280, 290)
    c.line_to(1280, 380)
    fill(c, hexc("#F2F2EC"))
    sea(c, t, 380)
    for i, x in enumerate((180, 520, 860)):
        ship(c, x, 560 + (i % 2) * 40, 0.7, 1, t, "uk")


@sc("TARGET: EGYPT")
def s029(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0", "britain": "#E79A94"})
    p = smooth(u * 1.2)
    arrow(c, [(480, 470), (600, 600), (900, 640), (1100, 690)], p, "#2B4C9B")
    arrow(c, [(1100, 690), (1200, 640), (1270, 600)], clamp(p * 1.6 - 0.8), "#E2B53B", 10, 24)


@sc("1798 · TO EGYPT")
def s030(c, u, t):
    sky(c, "day")
    sun(c, 1100, 120, 50, t=t)
    clouds(c, t)
    sea(c, t, 420)
    ship(c, 840, 600, 0.9, 1, t, "fr", hull="#4A3A2E", stripe="#2B4C9B")
    for i, x in enumerate((780, 860, 940)):
        person(c, x, 548, 0.55, coat=CIV_COATS[i], hat="tricorne", hair="wig", t=t, arms="hold", item="paper")
    ship(c, 300, 520, 0.5, 1, t, "fr", hull="#4A3A2E", stripe="#2B4C9B")


@sc("THE BATTLE OF THE PYRAMIDS")
def s031(c, u, t):
    landscape(c, t, "desert", "sand", 420, trees=False, cloud=False, seed=1)
    pyramids(c, 450, t)
    army(c, 60, 420, 640, rows=4, s=0.55, uni="fr", t=t, arms="aim")
    for i in range(4):
        muzzle(c, 160 + i * 80, 590, t, phase=i * 0.4, s=0.8)
    cavalry(c, 700, 1300, 680, t, uni="mam", face=-1, s=0.62, cols=("#F2EEE6", "#3A2A22", "#A87A4A"))
    smoke_bank(c, 560, t, a=0.25, col=(0.95, 0.9, 0.8))


@sc("THE BATTLE OF THE NILE")
def s032(c, u, t):
    sky(c, "night")
    stars(c, t)
    sea(c, t, 400, night=True)
    for i, x in enumerate((180, 460, 1060)):
        ship(c, x, 580, 0.55, 1, t, "fr", hull="#3A2E26")
    ship(c, 760, 600, 0.75, -1, t, "fr", hull="#3A2E26", burning=True)
    explosion(c, 760, 450, (t % 4) / 4, 1.2)
    for x in (300, 900):
        ship(c, x, 680, 0.6, 1 if x < 640 else -1, t, "uk", fire_side=True)


@sc("THE ROSETTA STONE")
def s033(c, u, t):
    landscape(c, t, "desert", "sand", 420, trees=False, seed=2)
    pyramids(c, 440, t)
    rosetta(c, 640, 640, 1.5)
    for i, (x, f) in enumerate(((380, 1), (900, -1), (1050, -1))):
        person(c, x, 690, 1.25, face=f, coat=CIV_COATS[i + 2], hat="tricorne", hair="wig", expr="shock", t=t,
               arms="up" if i == 0 else "point")


@sc("TROUBLE IN FRANCE")
def s034(c, u, t):
    tent_in(c, t)
    table(c, 640, 660, 380, 120)
    candle(c, 520, 540, t, 1.2)
    napoleon(c, 720, 690, 1.9, hat="none", arms="hold", item="paper", expr="worried", t=t)
    tint(c, (0.1, 0.05, 0), 0.25)


@sc("HE SLIPS AWAY")
def s035(c, u, t):
    sky(c, "night")
    stars(c, t)
    moon(c, 1040, 130, 40)
    sea(c, t, 440, night=True)
    landscape_strip = [(0, 440), (360, 430), (420, 470), (0, 480)]
    poly(c, landscape_strip)
    fill(c, hexc("#4A4030"))
    boat(c, 380 + 500 * u, 580, 1.1, t)


@sc("THE COUP · NOVEMBER 1799")
def s036(c, u, t):
    hall(c, t)
    for i, x in enumerate((640, 820, 1000, 1160)):
        person(c, x + 60 * u, 680 - (i % 2) * 30, 1.2, face=1, coat="#A8323A", robe="#A8323A", hair="wig",
               expr="shock", arms="up", t=t, walk=t * 8)
    army(c, 40, 460, 690, rows=2, s=0.95, uni="fr", t=t, march=True)


@sc("FIRST CONSUL")
def s037(c, u, t):
    hall(c, t)
    for x in (380, 640, 900):
        chair(c, x, 640, 1.3)
    person(c, 380, 640, 1.2, coat="#A8323A", hair="short", t=t, expr="neutral", seated=True)
    person(c, 900, 640, 1.2, coat="#A8323A", hair="bald", hair_col="#888", t=t, expr="neutral", seated=True)
    napoleon(c, 640, 640, 1.55, coat="#B02A30", hat="none", t=t, seated=True, expr="smirk")


# =============================================================== CONSUL
@sc("ACROSS THE ALPS")
def s038(c, u, t):
    landscape(c, t, "winter", "snow", 460, trees=False, mountains=True, seed=3)
    snowfall(c, t)
    army(c, 500, 1280, 560, rows=2, s=0.5, uni="fr", t=t, march=True, arms="down")
    cannon(c, 860, 640, 0.9, -1, t, fire=False)
    mounted(c, 330, 700, 1.15, 1, t, who="napoleon", col="#8A6A4E", expr="stern")


@sc("MARENGO · 1800")
def s039(c, u, t):
    battle_bg(c, t, "day", "grass", 400, seed=4)
    army(c, 80 - 80 * u, 600, 640, rows=3, s=0.6, uni="fr", t=t, face=-1, march=True, expr="worried")
    army(c, 760, 1280, 600, rows=3, s=0.55, uni="au", t=t, face=-1, march=True, flags="au")


@sc("COUNTERATTACK!")
def s040(c, u, t):
    battle_bg(c, t, "day", "grass", 400, seed=4)
    cavalry(c, -200, 700, 700, t, uni="cuir", s=0.62, speed=120)
    army(c, 900, 1280, 560, rows=3, s=0.5, uni="au", t=t, face=-1, expr="shock", arms="up")


@sc("PEACE")
def s041(c, u, t):
    hall(c, t)
    table(c, 640, 690, 640, 140, cloth="#3A6A4A")
    for i, x in enumerate((420, 860)):
        person(c, x, 600, 1.2, face=1 if i == 0 else -1, coat=["#2B4C9B", "#EEEDE6"][i], hair="wig", t=t,
               arms="write", item="paper", expr="neutral")
    poly(c, [(560, 560), (720, 560), (730, 590), (550, 590)])
    fill_ol(c, hexc("#F3EAD3"))


@sc("A BRIEF PEACE")
def s042(c, u, t):
    landscape(c, t, "sunset", "grass", 430, seed=12, sunpos=(1000, 300))
    village(c, 470, t, x0=150, n=4, seed=7)
    for i, x in enumerate((700, 800, 1100)):
        civilian(c, x, 640 + (i % 2) * 30, 0.9, i + 40, t, arms="down", expr="happy")


@sc("REBUILDING FRANCE")
def s043(c, u, t):
    interior(c, t)
    palace(c, 970, 330, 0.36)
    table(c, 520, 690, 520, 130)
    for k in range(6):
        rrect(c, 320 + k * 14, 520 - k * 22, 120, 22, 3)
        fill_ol(c, hexc("#F3EAD3"))
    napoleon(c, 640, 690, 1.6, hat="none", arms="write", item="paper", expr="stern", t=t, seated=False)


@sc("THE NAPOLEONIC CODE · 1804")
def s044(c, u, t):
    hall(c, t)
    table(c, 520, 690, 460, 140)
    book(c, 520, 550, 1.6, glow=0.8 + 0.2 * math.sin(t * 2), t=t)
    napoleon(c, 900, 690, 1.8, arms="hand_in", expr="proud", t=t)


@sc("STILL USED TODAY")
def s045(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#1E2A4A"), hexc("#3A4A7A")))
    c.paint()
    stars(c, t, ymax=720)
    globe(c, 640, 330, 200, t)
    for k in range(9):
        a = t * 0.8 + k * 0.7
        x, y = 640 + 150 * math.cos(a), 330 + 120 * math.sin(a * 1.3)
        ellipse(c, x, y, 7, 7)
        fill(c, hexc("#FFE08A"))
    for k in range(4):
        book(c, 220, 700 - k * 46, 0.9)
        book(c, 1060, 700 - k * 46, 0.9)


@sc("WAR AGAIN · 1803")
def s046(c, u, t):
    sky(c, "grey")
    clouds(c, t, col=(0.8, 0.8, 0.85, 0.8))
    sea(c, t, 400)
    ship(c, 330, 590, 0.75, 1, t, "uk", fire_side=True)
    ship(c, 950, 600, 0.75, -1, t, "fr", hull="#3A2E26", fire_side=True, phase=0.6)
    smoke_bank(c, 470, t, a=0.4)


@sc("NOTRE-DAME · 2 DEC 1804")
def s047(c, u, t):
    cathedral_in(c, t)
    crowd(c, 0, 1280, 720, rows=4, s=0.65, t=t, cheer=False, expr="neutral")


@sc("HE CROWNS HIMSELF", focus=(640, 280), zoom=0.12)
def s048(c, u, t):
    cathedral_in(c, t)
    person(c, 1000, 640, 1.5, face=-1, coat="#F4F1EA", robe="#F4F1EA", hat="mitre", hair="bald", hair_col="#BBB",
           expr="shock", t=t, seated=False)
    napoleon(c, 600, 690, 2.0, arms="crown", item="crown", robe="#9C2A3A", coat="#9C2A3A", expr="proud", t=t)


@sc("EMPEROR NAPOLEON I")
def s049(c, u, t):
    hall(c, t, red=True)
    throne(c, 640, 650, 1.6)
    napoleon(c, 640, 640, 1.9, hat="crown", robe="#9C2A3A", coat="#9C2A3A", seated=True, expr="proud", t=t)
    for x in (260, 1020):
        flag(c, x, 650, t, "fr", pole=380, w=120, h=80, eagle=True)


# =============================================================== TRAFALGAR / AUSTERLITZ
@sc("BOULOGNE · INVASION ARMY")
def s050(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.move_to(860, 330)
    c.line_to(900, 290)
    c.line_to(1280, 280)
    c.line_to(1280, 330)
    fill(c, hexc("#F2F2EC"))
    sea(c, t, 330)
    c.move_to(0, 470)
    c.curve_to(400, 430, 700, 460, 900, 720)
    c.line_to(0, 720)
    fill(c, hexc("#A8B86A"))
    for i in range(5):
        tent(c, 80 + i * 130, 500 + i * 6, 0.8)
    army(c, 60, 640, 700, rows=3, s=0.7, uni="fr", t=t, face=1)


@sc("NO CONTROL OF THE SEA")
def s051(c, u, t):
    sky(c, "storm")
    clouds(c, t, n=6, col=(0.4, 0.42, 0.48, 0.9))
    sea(c, t * 2.5, 300, "#4A6A86", "#2A3E54")
    rain(c, t, n=120)


@sc("TRAFALGAR · 21 OCT 1805")
def s052(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 380)
    for i in range(5):
        ship(c, 120 + i * 250, 500, 0.38, -1, t, "fr" if i % 2 else "es", hull="#3A2E26")
    for i in range(4):
        ship(c, 240 + i * 270, 650, 0.48, 1, t, "uk")


@sc("“ENGLAND EXPECTS...”", focus=(500, 320))
def s053(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 520)
    rrect(c, -40, 560, 1360, 200, 10)
    fill(c, hexc("#8A6A48"))
    seg(c, (900, 560), (900, -10), 18, hexc("#5A3A22"))
    for k in range(7):
        seg(c, (900, 40 + k * 70), (1180, 80 + k * 60), 2, INK)
        flag(c, 900 + 34 * k + 40, 90 + k * 64, t + k, ["uk", "fr", "es", "red", "sw", "ru", "pr"][k],
             pole=1, w=44, h=30)
    nelson(c, 460, 640, 2.0, arms="point", expr="proud", t=t)


@sc("BREAKING THE LINE")
def s054(c, u, t):
    sky(c, "grey")
    sea(c, t, 380)
    for i in range(4):
        ship(c, 100 + i * 360, 500, 0.42, -1, t, "fr", hull="#3A2E26", fire_side=True)
    ship(c, 200 + 700 * u, 640, 0.6, 1, t, "uk", fire_side=True)
    smoke_bank(c, 460, t, a=0.5)


@sc("NELSON FALLS")
def s055(c, u, t):
    sky(c, "grey")
    smoke_bank(c, 300, t, a=0.5)
    rrect(c, -40, 480, 1360, 260, 10)
    fill(c, hexc("#8A6A48"))
    for k in range(0, W, 70):
        seg(c, (k, 480), (k, 720), 2, (0, 0, 0, 0.12))
    c.save()
    c.translate(640, 620)
    c.rotate(-math.pi / 2)
    nelson(c, 0, 0, 1.4, expr="sleep", t=t, blink=False)
    c.restore()
    for i, (x, f) in enumerate(((420, 1), (860, -1), (960, -1))):
        soldier(c, x, 650 + (i % 2) * 20, 1.2, "sailor", t + i, face=f, arms="down", expr="sad")
    tint(c, (0.1, 0.1, 0.2), 0.2)


@sc("HE TURNS EAST")
def s056(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0"})
    arrow(c, [(470, 380), (560, 360), (660, 380)], smooth(u * 1.5), "#2B4C9B")
    napoleon(c, 200, 760, 2.0, arms="point", expr="stern", t=t)


@sc("THE GRANDE ARMÉE")
def s057(c, u, t):
    landscape(c, t, "day", "autumn", 400, seed=21, tree_col="#D98A3A")
    c.move_to(0, 640)
    c.curve_to(400, 560, 800, 520, 1280, 470)
    c.line_to(1280, 560)
    c.curve_to(800, 610, 400, 650, 0, 720)
    fill(c, hexc("#C9B48A"))
    for k in range(4):
        x0 = -300 + k * 380 + (t * 40) % 380
        army(c, x0, x0 + 300, 680 - k * 52, rows=2, s=0.55 - k * 0.06, uni="fr", t=t, march=True,
             flags="fr" if k % 2 else None)


@sc("ULM · AN ARMY SURRENDERS")
def s058(c, u, t):
    battle_bg(c, t, "grey", "grass", 400, smokey=False, seed=9)
    army(c, 520, 1280, 600, rows=3, s=0.6, uni="au", t=t, face=-1, arms="down", expr="sad")
    for k in range(4):
        flag(c, 600 + k * 50, 690, t, "au", pole=40, w=60, h=30)
    mounted(c, 260, 700, 1.15, 1, t, who="napoleon", expr="smirk")


@sc("AUSTERLITZ · 2 DEC 1805")
def s059(c, u, t):
    landscape(c, t, "winter", "snow", 420, seed=6, snow=True)
    c.move_to(700, 720)
    c.curve_to(800, 460, 1000, 420, 1280, 440)
    c.line_to(1280, 720)
    fill(c, hexc("#E6ECF2"))
    person(c, 960, 520, 1.15, coat="#EEEDE6", trou="#C8322F", hair="short", hat="bicorne_front", epaulettes=True,
           expr="smirk", t=t, face=-1)
    tsar(c, 1120, 530, 1.15, face=-1, expr="proud", t=t)
    army(c, 60, 640, 680, rows=3, s=0.5, uni="ru", t=t, march=True)


@sc("THE TRAP")
def s060(c, u, t):
    c.set_source(vgrad(c, 0, H, hexc("#EFE3C6"), hexc("#D9C69E")))
    c.paint()
    for k in range(5):
        ellipse(c, 640, 360, 420 - k * 70, 220 - k * 38)
        c.set_line_width(2)
        c.set_source_rgba(0.5, 0.4, 0.25, 0.4)
        c.stroke()
    for k in range(7):
        rrect(c, 380 + k * 70, 300, 36, 22, 4)
        fill(c, BLUE)
    for k in range(2):
        rrect(c, 900, 360 + k * 60, 36, 22, 4)
        fill(c, BLUE)
    p = smooth(u * 1.3)
    for k in range(3):
        arrow(c, [(560 + k * 60, 110), (700 + k * 40, 250), (880, 360 + k * 40)], p, "#EEEDE6", 14, 30)
    c.select_font_face("DejaVu Sans", 0, 1)
    c.set_font_size(26)
    c.move_to(860, 520)
    c.set_source_rgba(0.6, 0.15, 0.15, 0.9)
    c.show_text("WEAK?")


@sc("THE SUN OF AUSTERLITZ", focus=(640, 300))
def s061(c, u, t):
    sky(c, "dawn")
    sun(c, 640, 160, 70, "#FFE08A", t, rays=True)
    c.move_to(0, 720)
    c.curve_to(300, 360, 900, 300, 1280, 520)
    c.line_to(1280, 720)
    fill(c, hexc("#E9EEF2"))
    army(c, 200, 1100, 600 - 120 * smooth(u), rows=4, s=0.6, uni="fr", t=t, march=True, flags="fr")
    fog(c, 0.8 * (1 - u) + 0.2, 300, 720, t)


@sc("BATTLE OF THE THREE EMPERORS")
def s062(c, u, t):
    landscape(c, t, "gold", "snow", 460, seed=6, snow=True, sunpos=(1050, 200))
    for k, fk in enumerate(("au", "ru", "au", "ru")):
        flag(c, 360 + k * 70, 640, t + k, fk, pole=170, w=60, h=40)
        flag(c, 760 + k * 70, 640, t + k, ["ru", "au"][k % 2], pole=170, w=60, h=40, face=-1)
    napoleon(c, 640, 690, 2.0, arms="hand_in", expr="proud", t=t)


@sc("END OF THE HOLY ROMAN EMPIRE")
def s063(c, u, t):
    hall(c, t, night=True)
    rrect(c, 520, 520, 240, 60, 20)
    fill(c, hexc("#7A1F2E"))
    p = smooth(u)
    c.save()
    c.translate(640, 470)
    c.scale(3, 3)
    poly(c, [(-22, 10), (-24, -14), (-12, -2), (0, -20), (12, -2), (24, -14), (22, 10)])
    fill(c, (*GOLD[:3], 1 - p))
    c.restore()
    for k in range(40):
        a = k * 2.39
        r = p * (60 + (k * 13) % 200)
        ellipse(c, 640 + math.cos(a) * r, 470 + math.sin(a) * r * 0.5 + p * 100, 5, 5)
        fill(c, (*GOLD[:3], 1 - p * 0.7))


# =============================================================== PRUSSIA / RUSSIA
@sc("PRUSSIA · 1806")
def s064(c, u, t):
    landscape(c, t, "day", "grass", 400, seed=31)
    army(c, -100 + 60 * u, 1380, 660, rows=4, s=0.6, uni="pr", t=t, march=True, flags="pr")


@sc("JENA & AUERSTEDT")
def s065(c, u, t):
    battle_bg(c, t, "grey", "grass", 400, seed=31)
    army(c, 700 + 300 * u, 1400, 580, rows=3, s=0.5, uni="pr", t=t, march=True, run=True, expr="shock")
    cavalry(c, -300, 600, 690, t, uni="cuir", s=0.62, speed=160)


@sc("BERLIN")
def s066(c, u, t):
    sky(c, "day")
    clouds(c, t)
    c.set_source(vgrad(c, 470, H, hexc("#C9BBA0"), hexc("#A89A80")))
    c.rectangle(0, 470, W, H)
    c.fill()
    brandenburg(c, 640, 560, 1.15)
    mounted(c, 420 + 260 * u, 700, 1.1, 1, t, who="napoleon", gallop=False)
    army(c, -60, 260 + 260 * u, 700, rows=2, s=0.7, uni="guard", t=t, march=True)


@sc("THE CONTINENTAL SYSTEM")
def s067(c, u, t):
    sky(c, "grey")
    sea(c, t, 420)
    rrect(c, 0, 560, 560, 160, 0)
    fill(c, hexc("#A8967A"))
    for i in range(8):
        rrect(c, 60 + (i % 4) * 100, 470 - (i // 4) * 70 + 90, 90, 64, 4)
        fill_ol(c, hexc("#B88A52"), w=2)
        seg(c, (60 + (i % 4) * 100, 470 - (i // 4) * 70 + 120), (150 + (i % 4) * 100, 470 - (i // 4) * 70 + 120), 3,
            hexc("#8A6232"))
    for k in range(9):
        ellipse(c, 560 + k * 26, 520 + math.sin(k * 0.8) * 10, 13, 8)
        c.set_line_width(5)
        c.set_source_rgba(0.3, 0.3, 0.32, 1)
        c.stroke()
    ship(c, 960, 600, 0.6, -1, t, "uk")
    soldier(c, 480, 690, 1.1, "fr", t, face=1, arms="musket")


@sc("EYLAU · 1807")
def s068(c, u, t):
    landscape(c, t, "grey", "snow", 400, seed=8, snow=True, trees=False)
    cavalry(c, -200, 800, 700, t, uni="cuir", s=0.6, speed=100)
    army(c, 900, 1280, 600, rows=3, s=0.5, uni="ru", t=t, face=-1, arms="aim")
    snowfall(c, t, heavy=True)


@sc("FRIEDLAND")
def s069(c, u, t):
    landscape(c, t, "day", "grass", 380, seed=13)
    river(c, 470, 560, t)
    army(c, 620, 1280, 460, rows=2, s=0.4, uni="ru", t=t, face=1, march=True, run=True, expr="shock")
    for i, x in enumerate((160, 360, 560)):
        cannon(c, x, 680, 1.0, 1, t, phase=i * 0.7)


@sc("TILSIT · JULY 1807")
def s070(c, u, t):
    sky(c, "day")
    clouds(c, t)
    hills(c, 420, cols=("#8FCB68", "#74B356"))
    river(c, 440, 720, t)
    crowd(c, 0, 260, 470, rows=1, s=0.4, t=t, flags=["fr"])
    crowd(c, 1020, 1280, 470, rows=1, s=0.4, t=t, flags=["ru"])
    raft(c, 640, 650, t, 1.0)
    napoleon(c, 590, 640, 1.2, arms="hug", expr="happy", t=t)
    tsar(c, 700, 640, 1.2, face=-1, arms="hug", expr="happy", t=t)


@sc("THE BONAPARTE KINGS")
def s071(c, u, t):
    hall(c, t, red=True)
    for i, (x, rob) in enumerate(((360, "#2B4C9B"), (640, "#9C2A3A"), (920, "#3A6A4A"))):
        person(c, x, 680, 1.55, coat=rob, robe=rob, hat="crown", hair="short", expr="proud", t=t + i,
               arms="hold")
        seg(c, (x + 52, 600), (x + 70, 520), 6, GOLD)
        ellipse(c, x + 70, 516, 10, 10)
        fill(c, GOLD)


@sc("MASTER OF EUROPE")
def s072(c, u, t):
    blue = "#8FA8E0"
    p = u * 1.4
    cols = {"france": blue}
    for i, n in enumerate(("lowlands", "germany", "italy", "iberia", "poland", "prussia", "austria")):
        if p > i * 0.15:
            cols[n] = blue if n not in ("prussia", "austria") else "#B6C4E6"
    europe(c, t, colors=cols)


@sc("NOTHING COULD STOP HIM...")
def s073(c, u, t):
    hall(c, t)
    throne(c, 640, 600, 1.4)
    napoleon(c, 640, 590, 1.6, seated=True, expr="smirk", t=t, robe="#9C2A3A")
    p = smooth(u)
    c.set_line_width(4)
    c.set_source_rgba(0.15, 0.1, 0.08, 0.9)
    c.move_to(120, 720)
    pts = [(120, 720), (200, 680), (260, 700), (330, 640), (420, 660), (520, 610), (600, 640), (720, 600),
           (820, 630), (950, 590), (1080, 620), (1200, 580)]
    for q in pts[1:max(2, int(len(pts) * p))]:
        c.line_to(*q)
    c.stroke()


# =============================================================== SPAIN
@sc("INTO SPAIN · 1807")
def s074(c, u, t):
    landscape(c, t, "desert", "dry", 420, seed=14, tree_col="#7A8A3A")
    sun(c, 1100, 120, 50, t=t)
    army(c, -200 + 120 * u, 1300, 680, rows=3, s=0.55, uni="fr", t=t, march=True, expr="worried")


@sc("JOSEPH, KING OF SPAIN")
def s075(c, u, t):
    hall(c, t)
    person(c, 640, 690, 1.8, coat="#2B4C9B", robe="#9C2A3A", hat="crown", hair="short", expr="happy", t=t)
    for i, x in enumerate((240, 380, 900, 1040)):
        person(c, x, 690, 1.25, face=1 if x < 640 else -1, coat=["#2A2A2A", "#7A1F2E"][i % 2],
               hat="none", hair="wig", expr="angry", t=t, arms="down")


@sc("MADRID · 2 MAY 1808")
def s076(c, u, t):
    sky(c, "day")
    building_row(c, 470, t, seed=9, cols=("#E9C9A0", "#F0D8B0", "#E6B88A"))
    c.set_source(vgrad(c, 470, H, hexc("#C9A878"), hexc("#A88A5A")))
    c.rectangle(0, 470, W, H)
    c.fill()
    army(c, 820, 1280, 640, rows=2, s=0.65, uni="fr", t=t, face=-1, arms="aim")
    crowd(c, 0, 660, 700, rows=3, s=0.7, t=t, expr="angry", arms="fist", flags=["es"])
    smoke_bank(c, 540, t, a=0.35, col=(0.85, 0.75, 0.6))


@sc("REPRISALS", focus=(640, 400))
def s077(c, u, t):
    sky(c, "night")
    c.set_source_rgba(*hexc("#1E1A22"))
    c.rectangle(0, 400, W, H)
    c.fill()
    g = cairo.RadialGradient(700, 520, 20, 700, 520, 520)
    g.add_color_stop_rgba(0, 1, 0.85, 0.4, 0.55)
    g.add_color_stop_rgba(1, 1, 0.85, 0.4, 0)
    c.set_source(g)
    c.paint()
    rrect(c, 690, 600, 60, 60, 6)
    fill(c, hexc("#E9C46A"))
    for i in range(6):
        soldier(c, 120 + i * 80, 700, 1.15, "fr", t, face=1, arms="aim", coat="#1E2238", trou="#2A2A3A",
                skin=hexc("#2A2A2A"), belts=False, blink=False)


@sc("GUERRILLA · “THE LITTLE WAR”")
def s078(c, u, t):
    landscape(c, t, "desert", "dry", 400, trees=False, seed=5, mountains=True)
    c.move_to(0, 520)
    c.line_to(260, 430)
    c.line_to(420, 720)
    c.line_to(0, 720)
    fill(c, hexc("#A88A5A"))
    c.move_to(1280, 500)
    c.line_to(1000, 430)
    c.line_to(880, 720)
    c.line_to(1280, 720)
    fill(c, hexc("#A88A5A"))
    rrect(c, 520, 560, 200, 90, 8)
    fill_ol(c, hexc("#8A6A48"), w=2)
    for x in (550, 690):
        ellipse(c, x, 660, 26, 26)
        fill_ol(c, hexc("#5A3A22"), w=3)
    soldier(c, 760, 690, 0.95, "fr", t, face=-1, arms="up", expr="shock")
    for i, (x, y, f) in enumerate(((140, 520, 1), (240, 470, 1), (1060, 500, -1), (1160, 470, -1))):
        soldier(c, x, y, 0.85, "sp", t + i, face=f, arms="aim", expr="angry")


@sc("ARTHUR WELLESLEY")
def s079(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 420)
    c.set_source(vgrad(c, 560, H, hexc("#EBCB8B"), hexc("#D8AE68")))
    c.rectangle(0, 560, W, H)
    c.fill()
    for i in range(3):
        boat(c, 900 + i * 120, 560, 0.6, t + i)
    army(c, 380, 900, 680, rows=2, s=0.65, uni="br", t=t, march=True, flags="uk")
    wellington(c, 220, 700, 1.6, arms="point", expr="stern", t=t)


@sc("THE SPANISH ULCER")
def s080(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0"},
           glow=("iberia", "#D2333A", 0.35 + 0.3 * math.sin(t * 3)))
    for i in range(6):
        soldier(c, 290 + i * 26, 560 - (i % 2) * 30, 0.4, "fr_rag", t + i, expr="sad", arms="down")


@sc("AUSTRIA AGAIN · 1809")
def s081(c, u, t):
    landscape(c, t, "day", "grass", 400, seed=41)
    army(c, -100 + 80 * u, 1380, 660, rows=4, s=0.6, uni="au", t=t, march=True, flags="au")


@sc("ASPERN-ESSLING · DEFEAT")
def s082(c, u, t):
    landscape(c, t, "grey", "grass", 380, seed=12)
    river(c, 460, 600, t)
    bridge(c, 0, 1280, 500, broken=(520, 760))
    army(c, 0, 480, 500, rows=1, s=0.6, uni="fr", t=t, face=-1, march=True, run=True, expr="shock")
    army(c, 820, 1280, 500, rows=1, s=0.6, uni="fr", t=t, face=-1, march=True, run=True, expr="worried")
    army(c, 200, 1180, 720, rows=1, s=0.8, uni="au", t=t, face=-1, arms="aim")


@sc("WAGRAM")
def s083(c, u, t):
    battle_bg(c, t, "day", "dry", 400, seed=9)
    for i in range(8):
        cannon(c, 80 + i * 150, 560 + (i % 2) * 90, 0.9, 1, t, phase=i * 0.3)
    smoke_bank(c, 460, t, a=0.55, seed=6)


@sc("FAREWELL, JOSÉPHINE")
def s084(c, u, t):
    hall(c, t)
    lady(c, 480, 690, 1.8, expr="sad", t=t, look=1)
    for k in range(2):
        ph = (t * 0.8 + k * 0.5) % 1
        ellipse(c, 500 + k * 16, 440 + ph * 30, 3, 5)
        fill(c, hexc("#7AC0F0", 1 - ph))
    napoleon(c, 820, 690, 1.8, face=1, expr="sad", t=t, arms="hand_in")


@sc("MARIE-LOUISE · 1810")
def s085(c, u, t):
    cathedral_in(c, t)
    napoleon(c, 560, 690, 1.8, expr="proud", t=t, arms="hug")
    lady(c, 720, 690, 1.75, face=-1, hair_col="#D8B66A", expr="happy", t=t, arms="hug")
    for k in range(12):
        ph = (t * 0.4 + k / 12) % 1
        ellipse(c, 300 + k * 60 + math.sin(t + k) * 20, ph * 720, 5, 3)
        fill(c, hexc("#F7C6D0"))


@sc("AN HEIR · 1811")
def s086(c, u, t):
    hall(c, t, red=True)
    rrect(c, 420, 560, 260, 110, 50)
    fill_ol(c, GOLD, hexc("#9A7414"), 3)
    napoleon(c, 760, 690, 1.9, arms="cradle", expr="happy", t=t)


@sc("BUT...")
def s087(c, u, t):
    sky(c, "storm")
    clouds(c, t, n=8, col=(0.25, 0.27, 0.32, 0.95), speed=30)
    c.set_source(vgrad(c, 470, H, hexc("#3A4A3A"), hexc("#2A3528")))
    c.rectangle(0, 470, W, H)
    c.fill()
    palace(c, 640, 600, 0.9, night=True)
    if (t % 2.5) < 0.12:
        tint(c, (1, 1, 1), 0.6)


# =============================================================== RUSSIA 1812
@sc("TSAR ALEXANDER I")
def s088(c, u, t):
    sky(c, "grey")
    sea(c, t, 440)
    ship(c, 1000, 600, 0.6, -1, t, "uk")
    rrect(c, 0, 560, 760, 160, 0)
    fill(c, hexc("#A8967A"))
    tsar(c, 420, 690, 2.0, expr="angry", t=t, arms="fist")


@sc("JUNE 1812 · ~500,000 MEN")
def s089(c, u, t):
    landscape(c, t, "day", "grass", 330, seed=17)
    river(c, 470, 600, t)
    for k in range(2):
        bridge(c, 0, 1280, 520 + k * 60)
    for k in range(5):
        y = 360 + k * 70
        if 450 < y < 610:
            y = 510 + (k % 2) * 60
        army(c, -200 + (t * 30) % 100, 1400, y, rows=1, s=0.25 + k * 0.08, uni="fr", t=t, march=True,
             spacing=26, flags="fr" if k == 4 else None)


@sc("SCORCHED EARTH")
def s090(c, u, t):
    landscape(c, t, "fire", "dry", 420, seed=18, trees=False)
    village(c, 470, t, x0=120, n=6, church=True, windmill=False, night=True)
    flames(c, 400, 470, 600, 160, t)
    smoke_bank(c, 250, t, a=0.5, col=(0.2, 0.18, 0.18))
    army(c, 600, 1280, 680, rows=2, s=0.6, uni="ru", t=t, face=1, march=True)


@sc("HEAT · HUNGER · DISEASE")
def s091(c, u, t):
    landscape(c, t, "gold", "dry", 430, seed=19, sunpos=(1050, 140), sunrays=True)
    army(c, 100, 1200, 640, rows=2, s=0.6, uni="fr", t=t, march=True, expr="sad", speed=2)
    c.save()
    c.translate(520, 690)
    c.rotate(-math.pi / 2)
    soldier(c, 0, 0, 0.75, "fr", t, expr="sleep", arms="down", blink=False)
    c.restore()


@sc("BORODINO · 7 SEPT 1812")
def s092(c, u, t):
    battle_bg(c, t, "grey", "grass", 400, seed=22)
    for x in (300, 900):
        poly(c, [(x - 160, 520), (x - 110, 470), (x + 110, 470), (x + 160, 520)])
        fill(c, hexc("#8A7A58"))
    army(c, 40, 600, 690, rows=3, s=0.55, uni="fr", t=t, march=True, run=True)
    army(c, 760, 1260, 560, rows=2, s=0.45, uni="ru", t=t, face=-1, arms="aim")
    for i in range(3):
        cannon(c, 820 + i * 140, 470, 0.7, -1, t, phase=i * 0.5)
    smoke_bank(c, 450, t, a=0.6)


@sc("MOSCOW")
def s093(c, u, t):
    sky(c, "day")
    clouds(c, t)
    onion_city(c, 520, t)
    hills(c, 600, cols=("#8FCB68", "#74B356"), layers=1)
    mounted(c, 260, 720, 1.1, 1, t, who="napoleon", expr="smirk")


@sc("MOSCOW BURNS")
def s094(c, u, t):
    sky(c, "fire")
    onion_city(c, 600, t, night=True, burning=True)
    smoke_bank(c, 200, t, a=0.5, col=(0.2, 0.15, 0.15))
    c.set_source_rgba(*hexc("#2A1E1A"))
    c.rectangle(0, 0, 230, H)
    c.rectangle(0, 0, W, 60)
    c.rectangle(1050, 0, 230, H)
    c.rectangle(0, 620, W, 100)
    c.fill()
    napoleon(c, 230, 720, 1.7, expr="shock", t=t, look=1)


@sc("WAITING FOR THE TSAR...")
def s095(c, u, t):
    interior(c, t, night=True)
    table(c, 640, 690, 520, 130)
    candle(c, 640, 560, t, 1.4)
    chair(c, 860, 690, 1.0)
    napoleon(c, 420, 690, 1.7, seated=True, expr="worried", t=t, look=1)
    tint(c, (0.05, 0.05, 0.15), 0.2)


@sc("THE RETREAT")
def s096(c, u, t):
    landscape(c, t, "winter", "snow", 380, seed=23, snow=True)
    c.move_to(0, 520)
    c.curve_to(400, 470, 800, 450, 1280, 430)
    c.line_to(1280, 470)
    c.curve_to(800, 500, 400, 540, 0, 600)
    fill(c, hexc("#D3DDE6"))
    for k in range(3):
        army(c, -200 + k * 500, 200 + k * 500, 560 - k * 40, rows=1, s=0.5 - k * 0.08, uni="fr", t=t, march=True,
             expr="sad", face=-1, speed=1.5)
    snowfall(c, t, heavy=True)


@sc("WINTER")
def s097(c, u, t):
    landscape(c, t, "grey", "snow", 420, seed=24, snow=True, trees=False)
    for i in range(3):
        c.save()
        c.translate(300 + i * 60, 640)
        c.rotate(0.3 * (i - 1))
        cannon(c, 0, 0, 0.9, 1, t, fire=False)
        c.restore()
    for i in range(4):
        soldier(c, 560 + i * 70, 680, 0.9, "fr", t + i, arms="hug", expr="sad", face=1 if i % 2 else -1)
    for i in range(4):
        mounted(c, 900 + i * 90, 440, 0.45, -1, t, who="cossack", col="#3A2A22")
    snowfall(c, t, heavy=True)


@sc("THE BEREZINA")
def s098(c, u, t):
    landscape(c, t, "winter", "snow", 360, seed=25, snow=True)
    river(c, 440, 720, t, icy=True)
    bridge(c, 0, 1280, 480)
    army(c, -100, 1300, 480, rows=1, s=0.45, uni="fr", t=t, march=True, face=1, speed=2)
    for i in range(6):
        soldier(c, 160 + i * 190, 720, 0.9, "fr", t + i, arms="up", expr="worried", trou="#5A7A9A")
    snowfall(c, t)


@sc("HE RUSHES BACK TO PARIS")
def s099(c, u, t):
    sky(c, "night")
    stars(c, t)
    moon(c, 1100, 120, 36)
    c.set_source(vgrad(c, 450, H, hexc("#C9D6E2"), hexc("#9AAABA")))
    c.rectangle(0, 450, W, H)
    c.fill()
    for i in range(6):
        tree(c, (i * 260 - t * 300) % 1600 - 160, 470, 0.9, snow=True)
    sleigh(c, 420, 660, 1.0, t)
    snowfall(c, t, heavy=True)


@sc("THE MYTH IS BROKEN")
def s100(c, u, t):
    landscape(c, t, "grey", "snow", 440, seed=26, snow=True, trees=False)
    statue_broken(c, 640, 640, t)
    snowfall(c, t)


# =============================================================== 1813-1814
@sc("THE SIXTH COALITION")
def s101(c, u, t):
    hall(c, t)
    for i, (x, fk) in enumerate(((220, "pr"), (430, "ru"), (640, "au"), (850, "sw"), (1060, "uk"))):
        flag(c, x, 470, t + i, fk, pole=300, w=110, h=70)
    tsar(c, 420, 690, 1.4, arms="hug", expr="happy", t=t)
    king(c, 640, 690, 1.4, robe="#EEEDE6", expr="happy", t=t, arms="hug")
    king(c, 860, 690, 1.4, robe="#1F2A44", expr="happy", t=t, arms="hug", face=-1)


@sc("A NEW, YOUNG ARMY")
def s102(c, u, t):
    landscape(c, t, "day", "grass", 420, seed=27)
    for i in range(5):
        soldier(c, 220 + i * 210, 690, 1.25, "conscript", t + i, arms="musket", expr="worried", face=1,
                look=math.sin(t * 2 + i))


@sc("LEIPZIG · BATTLE OF NATIONS")
def s103(c, u, t):
    battle_bg(c, t, "grey", "grass", 420, seed=28)
    building_row(c, 470, t, seed=12, h0=60, h1=120)
    army(c, 380, 900, 570, rows=2, s=0.4, uni="fr", t=t, flags="fr")
    army(c, 0, 300, 680, rows=2, s=0.6, uni="pr", t=t, march=True)
    army(c, 980, 1280, 680, rows=2, s=0.6, uni="ru", t=t, face=-1, march=True)
    army(c, 300, 980, 720, rows=1, s=0.7, uni="au", t=t, march=True)


@sc("DEFEAT")
def s104(c, u, t):
    landscape(c, t, "grey", "grass", 380, seed=29)
    river(c, 470, 620, t)
    bridge(c, 300, 980, 500, stone=True, broken=(560, 760) if u > 0.4 else None)
    explosion(c, 660, 470, (u - 0.4) * 2.5, 1.2)
    army(c, 0, 280, 500, rows=1, s=0.55, uni="fr", t=t, face=1, march=True, run=True, expr="shock")


@sc("FRANCE INVADED · 1814")
def s105(c, u, t):
    landscape(c, t, "winter", "snow", 420, seed=30, snow=True)
    village(c, 460, t, x0=820, n=3, windmill=False)
    army(c, 40, 520, 680, rows=2, s=0.55, uni="fr", t=t, march=True)
    mounted(c, 620, 690, 1.0, 1, t, who="napoleon")
    snowfall(c, t)


@sc("PARIS FALLS · 31 MARCH 1814")
def s106(c, u, t):
    sky(c, "grey")
    building_row(c, 470, t, seed=3)
    c.set_source(vgrad(c, 470, H, hexc("#B9AE98"), hexc("#9A8E78")))
    c.rectangle(0, 470, W, H)
    c.fill()
    army(c, -200 + 200 * u, 1400, 690, rows=3, s=0.6, uni="ru", t=t, march=True, flags="ru")


@sc("ABDICATION · 6 APRIL 1814")
def s107(c, u, t):
    hall(c, t)
    table(c, 640, 690, 420, 130)
    poly(c, [(580, 560), (700, 560), (710, 580), (570, 580)])
    fill_ol(c, hexc("#F3EAD3"))
    napoleon(c, 640, 640, 1.5, seated=True, arms="write", expr="sad", t=t)
    for i, x in enumerate((260, 380, 900, 1020)):
        person(c, x, 690, 1.35, face=1 if x < 640 else -1, coat="#22408A", trou="#F1EEE6", hat="bicorne_front",
               plume="#F1EEE6", epaulettes=True, hair="short", expr="sad", t=t + i)


@sc("EXILE ON ELBA")
def s108(c, u, t):
    sky(c, "day")
    clouds(c, t)
    sea(c, t, 420)
    c.move_to(300, 720)
    c.curve_to(380, 520, 900, 500, 1000, 720)
    fill(c, hexc("#9A8E6A"))
    napoleon(c, 640, 560, 1.4, arms="hand_in", expr="sad", t=t, face=1)


@sc("KING LOUIS XVIII")
def s109(c, u, t):
    hall(c, t)
    throne(c, 640, 660, 1.5)
    king(c, 640, 650, 1.9, robe="#2B4C9B", coat="#2B4C9B", seated=True, expr="happy", t=t, sash="#4A7AC8")
    c.save()
    c.translate(640, 560)
    ellipse(c, 0, 0, 70, 50)
    fill(c, hexc("#2B4C9B"))
    c.restore()


@sc("THE CONGRESS OF VIENNA")
def s110(c, u, t):
    hall(c, t)
    for i in range(4):
        x = 160 + i * 300 + 40 * math.sin(t * 0.8 + i)
        lady(c, x, 520, 0.9, dress=["#F4C6D0", "#C6DCF4", "#F4E6C6", "#D6F4C6"][i], t=t)
        person(c, x + 50, 520, 0.9, face=-1, coat="#2A2A3A", hair="wig", t=t, expr="happy")
    table(c, 640, 700, 760, 130, cloth="#3A6A4A")
    c.save()
    c.translate(400, 565)
    c.scale(0.37, 0.07)
    c.rectangle(0, 0, W, H)
    c.clip()
    europe(c, t, labels=False)
    c.restore()
    for i, x in enumerate((300, 500, 800, 1000)):
        person(c, x, 720, 1.15, face=1 if i < 2 else -1, coat=["#C8322F", "#EEEDE6", "#1F2A44", "#2F5A35"][i],
               hair="wig", t=t, arms="point" if i == 1 else "down", expr="neutral")


# =============================================================== HUNDRED DAYS
@sc("ESCAPE · FEBRUARY 1815")
def s111(c, u, t):
    sky(c, "night")
    stars(c, t)
    moon(c, 260, 120, 34)
    sea(c, t, 430, night=True)
    c.move_to(0, 430)
    c.curve_to(120, 380, 260, 380, 360, 440)
    fill(c, hexc("#2A2A30"))
    boat(c, 420 + 600 * u, 600, 1.1, t)


@sc("BACK IN FRANCE")
def s112(c, u, t):
    sky(c, "day")
    sea(c, t, 380)
    c.set_source(vgrad(c, 520, H, hexc("#EBCB8B"), hexc("#D8AE68")))
    c.rectangle(0, 520, W, H)
    c.fill()
    boat(c, 1060, 500, 0.8, t)
    army(c, 520, 980, 680, rows=2, s=0.6, uni="guard", t=t, march=True, face=-1, flags="fr")
    napoleon(c, 380, 690, 1.6, face=-1, arms="point", expr="proud", t=t)


@sc("“HERE I AM”", focus=(420, 380), zoom=0.1)
def s113(c, u, t):
    landscape(c, t, "day", "road", 430, mountains=True, seed=8)
    army(c, 720, 1280, 690, rows=2, s=0.75, uni="fr", t=t, face=-1, arms="aim", coat="#F1EEE6",
         trou="#F1EEE6", expr="worried")
    napoleon(c, 380, 690, 1.7, arms="shrug", expr="stern", t=t)


@sc("THEY JOIN HIM!")
def s114(c, u, t):
    landscape(c, t, "day", "road", 430, mountains=True, seed=8)
    for i in range(7):
        hop = abs(math.sin(t * 6 + i)) * 24
        soldier(c, 160 + i * 160, 690 - hop, 1.05, "fr", t + i, face=1 if i % 2 else -1, arms="cheer",
                expr="happy", coat="#F1EEE6")
    for i in range(6):
        ph = (t * 0.9 + i / 6) % 1
        c.save()
        c.translate(200 + i * 180, 360 - 300 * math.sin(math.pi * ph))
        c.rotate(t * 4 + i)
        rrect(c, -16, -20, 32, 30, 4)
        fill(c, BLACK)
        c.restore()


@sc("PARIS · 20 MARCH 1815")
def s115(c, u, t):
    sky(c, "day")
    clouds(c, t)
    palace(c, 640, 520, 1.1)
    c.set_source(vgrad(c, 520, H, hexc("#C9BBA0"), hexc("#A89A80")))
    c.rectangle(0, 520, W, H)
    c.fill()
    crowd(c, 0, 1280, 720, rows=3, s=0.7, t=t, flags=["fr", "fr", "fr"])
    napoleon(c, 640, 600 + 10 * math.sin(t * 6), 1.3, arms="up", expr="happy", t=t)


@sc("ALL OF EUROPE AGAINST HIM")
def s116(c, u, t):
    europe(c, t, colors={"france": "#8FA8E0", "britain": "#E79A94", "prussia": "#B9B9C6", "austria": "#F2F2F2",
                         "russia": "#B8D6A8"})
    p = smooth(u * 1.3)
    arrow(c, [(390, 250), (440, 290), (470, 320)], p, "#C8322F")
    arrow(c, [(700, 290), (600, 300), (520, 320)], p, "#555566")
    arrow(c, [(1000, 300), (800, 330), (560, 380)], p, "#3E7A3E")
    arrow(c, [(720, 400), (620, 410), (540, 420)], p, "#EEEDE6")


@sc("LIGNY · 16 JUNE 1815")
def s117(c, u, t):
    battle_bg(c, t, "grey", "grass", 400, seed=33)
    army(c, 700, 1280, 560, rows=2, s=0.5, uni="fr", t=t, face=-1, march=True, run=True)
    horse(c, 420, 640, 1.0, 1, "#3A2A22", t, rear=0.0)
    c.save()
    c.translate(330, 680)
    c.rotate(-0.4)
    person(c, 0, 0, 1.0, coat="#1F2A44", trou="#8A8E98", hat="none", hair="bald", hair_col="#EEE",
           moust=True, expr="shock", t=t, epaulettes=True)
    c.restore()


@sc("WAITING FOR THE GROUND TO DRY")
def s118(c, u, t):
    tent_in(c, t)
    rrect(c, 760, 120, 400, 260, 10)
    c.set_source(vgrad(c, 120, 380, hexc("#8A96A0"), hexc("#7A6A48")))
    c.fill()
    rain(c, t, n=40)
    table(c, 460, 690, 420, 130, cloth="#F3EDE0")
    ellipse(c, 400, 560, 40, 10)
    fill(c, WHITE)
    napoleon(c, 300, 690, 1.6, seated=True, expr="stern", t=t, look=1)


@sc("THE PRUSSIANS ARE COMING")
def s119(c, u, t):
    landscape(c, t, "grey", "mud", 400, seed=34)
    for i in range(10):
        tree(c, i * 140 + 30, 470, 1.2, col="#3E7A3E", kind="round")
    army(c, -100 + 100 * u, 1300, 660, rows=2, s=0.55, uni="pr", t=t, march=True, flags="pr", speed=3)
    cannon(c, 640 + 100 * u, 720, 0.9, 1, t, fire=False)


@sc("HOUGOUMONT")
def s120(c, u, t):
    battle_bg(c, t, "grey", "grass", 380, seed=35)
    farmhouse(c, 640, 600, 1.0, burning=True, t=t)
    for i, x in enumerate((540, 600, 680, 740)):
        soldier(c, x, 700, 0.75, "br", t + i, arms="aim")


@sc("NEY'S CAVALRY CHARGES")
def s121(c, u, t):
    battle_bg(c, t, "grey", "grass", 400, seed=36)
    army(c, 820, 1100, 600, rows=4, s=0.5, uni="br", t=t, face=-1, arms="aim", spacing=30, depth=20)
    cavalry(c, -400, 700, 700, t, uni="cuir", s=0.66, speed=140)
    cavalry(c, -300, 600, 560, t, uni="cuir", s=0.5, speed=120, seed=4, rows=1)


@sc("BLÜCHER ARRIVES")
def s122(c, u, t):
    landscape(c, t, "dusk", "grass", 400, seed=37)
    for i in range(8):
        tree(c, 800 + i * 70, 480 + (i % 3) * 20, 1.3, col="#3E6A3E", kind="round")
    army(c, 820 - 300 * u, 1280, 680, rows=3, s=0.6, uni="pr", t=t, face=-1, march=True, flags="pr")


@sc("THE IMPERIAL GUARD")
def s123(c, u, t):
    landscape(c, t, "sunset", "grass", 300, seed=38, sunpos=(1100, 260))
    c.move_to(0, 720)
    c.line_to(0, 560)
    c.curve_to(400, 480, 900, 380, 1280, 360)
    c.line_to(1280, 720)
    fill(c, hexc("#6E9A4E"))
    army(c, 200 + 120 * u, 900 + 120 * u, 720 - 80 * u, rows=4, s=0.75, uni="guard", t=t, march=True,
         flags="fr", speed=2.5)


@sc("“THE GUARD RETREATS!”")
def s124(c, u, t):
    landscape(c, t, "dusk", "grass", 400, seed=39)
    army(c, 1400 - 900 * u - 300, 1500 - 900 * u, 660, rows=2, s=0.6, uni="fr", t=t, face=-1, march=True,
         run=True, expr="shock", arms="up")
    for x in (300, 520):
        c.save()
        c.translate(x, 700)
        c.rotate(1.2)
        flag(c, 0, 0, 0, "fr", pole=160, w=60, h=40, wave=0)
        c.restore()
    smoke_bank(c, 440, t, a=0.4)


@sc("SAINT HELENA")
def s125(c, u, t):
    sky(c, "grey")
    sea(c, t, 380)
    rrect(c, -40, 520, 1360, 240, 10)
    fill(c, hexc("#8A6A48"))
    seg(c, (100, 520), (100, 0), 16, hexc("#5A3A22"))
    flag(c, 160, 500, t, "uk", pole=140, w=90, h=60)
    napoleon(c, 820, 650, 1.7, face=-1, arms="hand_in", expr="sad", t=t)


@sc("A LONELY ISLAND")
def s126(c, u, t):
    sky(c, "grey")
    clouds(c, t, col=(0.85, 0.87, 0.9, 0.8))
    sea(c, t, 440)
    poly(c, [(420, 500), (520, 330), (640, 300), (780, 350), (880, 500)])
    fill(c, hexc("#6A5E4A"))
    poly(c, [(520, 330), (640, 300), (700, 330), (580, 360)])
    fill(c, hexc("#6E8A4E"))


@sc("WRITING HIS LEGEND")
def s127(c, u, t):
    interior(c, t, wall="#C9B48E", sky_k="grey")
    table(c, 760, 690, 360, 120)
    for k in range(4):
        rrect(c, 680 + k * 6, 556 - k * 4, 110, 20, 2)
        fill_ol(c, hexc("#F3EAD3"))
    old_nap(c, 360, 690, 1.65, arms="point", expr="neutral", t=t)
    person(c, 860, 640, 1.4, face=-1, coat="#3A3A44", hair="short", seated=True, arms="write", t=t)


@sc("5 MAY 1821")
def s128(c, u, t):
    interior(c, t, night=True)
    chair(c, 640, 690, 1.6)
    c.save()
    c.translate(640, 560)
    c.scale(2.2, 2.2)
    draw_hat(c, "bicorne_side", 26, None, t)
    c.restore()
    rrect(c, 900, 600, 14, 60, 3)
    fill(c, hexc("#F3EBD9"))
    smoke(c, 907, 580, t, n=3, s=0.25, col=(0.8, 0.8, 0.8), rise=120)
    tint(c, (0.02, 0.02, 0.08), 0.35)


# =============================================================== LEGACY
@sc("MILLIONS DEAD")
def s129(c, u, t):
    landscape(c, t, "sunset", "grass", 400, seed=40, sunpos=(640, 380), trees=False)
    crosses(c, 700, t)
    tint(c, (0.2, 0.1, 0.05), 0.15)


@sc("A NEW EUROPE")
def s130(c, u, t):
    cols = {}
    p = u * 1.5
    pal = ["#E79A94", "#8FA8E0", "#F2D27A", "#B8D6A8", "#C9B6E4", "#F2B98A", "#9AD0D0", "#EEC0D4"]
    for i, n in enumerate(("britain", "france", "iberia", "italy", "germany", "prussia", "austria", "russia",
                           "poland", "scandinavia")):
        if p > i * 0.1:
            cols[n] = pal[i % len(pal)]
    europe(c, t, colors=cols)


@sc("BRITAIN RULES THE WAVES")
def s131(c, u, t):
    sky(c, "day")
    clouds(c, t)
    building_row(c, 420, t, seed=15, h0=80, h1=160, cols=("#CFC6B6", "#B9AE98", "#D9D0C0"))
    c.save()
    c.translate(640, 250)
    rrect(c, -40, -40, 80, 220, 4)
    fill_ol(c, hexc("#CFC6B6"), w=2)
    ellipse(c, 0, -40, 60, 50)
    fill_ol(c, hexc("#B9AE98"), w=2)
    c.restore()
    river(c, 420, 720, t, "#5F8EA6", "#3E6E86")
    for i, x in enumerate((300, 900)):
        ship(c, x, 640, 0.6, 1, t, "uk")


@sc("BALANCE OF POWER")
def s132(c, u, t):
    hall(c, t)
    scale_balance(c, 640, 690, t, flags_l=("uk", "au"), flags_r=("pr", "ru"))


@sc("HERO OR TYRANT?")
def s133(c, u, t):
    c.set_source_rgba(*hexc("#F2C46A"))
    c.rectangle(0, 0, 640, H)
    c.fill()
    c.set_source_rgba(*hexc("#2A2236"))
    c.rectangle(640, 0, 640, H)
    c.fill()
    sun(c, 320, 200, 40, t=t, rays=True)
    napoleon(c, 640, 760, 2.6, arms="hand_in", expr="stern", t=t)
    c.save()
    c.rectangle(640, 0, 640, H)
    c.clip()
    tint(c, (0.1, 0.05, 0.2), 0.55)
    c.restore()


@sc("“IMPOSSIBLE”", focus=(640, 300), zoom=0.12)
def s134(c, u, t):
    hall(c, t, red=True)
    napoleon(c, 640, 820, 3.2, expr="smirk", t=t, arms="hand_in")
    vignette(c, 0.5)


@sc("THE END", zoom=0.05)
def s135(c, u, t):
    landscape(c, t, "sunset", "dry", 420, seed=42, sunpos=(1000, 360), trees=False)
    ellipse(c, 640, 640, 230, 40)
    fill(c, (0.25, 0.18, 0.1, 0.35))
    c.save()
    c.translate(640, 630)
    c.rotate(-0.15)
    c.scale(3.4, 3.4)
    draw_hat(c, "bicorne_side", 26, None, t)
    c.restore()
    smoke_bank(c, 430, t, a=0.25)
    vignette(c, 0.35)
