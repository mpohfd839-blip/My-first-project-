"""Period-style image prompts (paintings, engravings, portraits, maps, places today) for the
Napoleonic Wars video, timed from the aligned voiceover (video/words.json).

Usage: python3 make_real_image_prompts.py -> real_image_prompts.txt, prompts_one_per_line.txt
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

STYLES = {
    "PAINTING": "early 19th-century romantic oil painting of a historical scene, dramatic lighting, rich deep colours, "
                "visible brushstrokes, canvas texture, slightly aged varnish, museum quality, cinematic composition, "
                "16:9, no text, no signature, no frame",
    "PORTRAIT": "formal early 19th-century oil portrait, plain dark background, chiaroscuro lighting, fine brushwork, "
                "aged varnish, chest-up, subject centred with empty space on both sides, 16:9, no text, no signature, "
                "no frame",
    "ENGRAVING": "early 19th-century hand-coloured copper engraving, fine hatching lines, muted watercolour tints, "
                 "aged cream paper, 16:9, no text, no caption",
    "MAP": "antique hand-painted map of Europe from around 1810 on aged parchment, muted watercolour colours, ink "
           "coastlines, decorative compass rose, top-down flat view, no text, no labels, no letters, 16:9",
    "STILL": "photorealistic still life, dramatic low-key candle lighting, shallow depth of field, cinematic, 16:9, "
             "no readable text, no watermark",
    "TODAY": "modern photorealistic colour photograph, cinematic golden-hour light, high detail, 16:9, no text, "
             "no watermark",
}

USE = {
    "FULL": "Full screen, slow Ken Burns zoom 5-7 s, crossfade in/out",
    "FRAME": "Inside the cartoon scene as a framed painting or print on a wall/desk, 4-5 s",
    "SPLIT": "Gold-framed portrait on one half, cartoon character on the other, 4-6 s",
    "MAP": "Full screen base map; animate labels and arrows on top in the edit, 6-10 s",
    "OUTRO": "Full screen, very slow zoom out, long crossfade",
}

NAP = ("Napoleon Bonaparte (short, pale, dark hair, black bicorne hat worn sideways, dark blue coat with gold "
       "epaulettes, white waistcoat)")

I = [
    # ------------------------------------------------------------- cold open
    ("Belgium. The eighteenth of June, 1815.", "PAINTING", "FULL",
     "Misty dawn over muddy rain-soaked fields near Waterloo in 1815, scattered farmhouses, distant armies camped "
     "on two ridges, campfire smoke rising, grey clouds breaking"),
    ("On one side of the valley stands an army", "PAINTING", "FULL",
     "Long lines of British redcoat infantry standing on a green ridge in light rain, Union flags, officers on "
     "horseback, muddy field in front"),
    ("Napoleon Bonaparte.", "PORTRAIT", "SPLIT",
     f"{NAP}, stern piercing gaze, hand tucked inside his waistcoat, grey greatcoat over his shoulders"),
    # ------------------------------------------------------------- revolution
    ("In 1789, France explodes.", "PAINTING", "FULL",
     "The storming of the Bastille in Paris in 1789, a huge crowd with muskets, pikes and tricolour cockades "
     "attacking a grim stone fortress with round towers, smoke and fire"),
    ("The king loses his power", "PORTRAIT", "SPLIT",
     "King Louis XVI of France, plump face, powdered white wig, blue sash and royal robes, worried expression"),
    ("Napoleon Bonaparte was born in 1769 on Corsica", "TODAY", "FULL",
     "The old harbour town of Ajaccio on Corsica, pastel stone houses, fishing boats, green mountains behind, "
     "turquoise Mediterranean sea"),
    ("In 1793, at the port of Toulon", "PAINTING", "FULL",
     "Siege of Toulon at night in 1793, a young thin French artillery officer with long hair directing cannons on "
     "a hill, British warships burning in the harbour below"),
    ("In 1796, they gave him command", "PAINTING", "FULL",
     "A ragged French army of 1796 in torn blue uniforms, some barefoot, marching through rocky Alpine passes "
     "towards the sunny plains of Italy"),
    ("In one campaign, he beat the Austrians", "PAINTING", "FULL",
     "Young general Napoleon with long hair, holding a tricolour flag high and charging across a narrow bridge "
     "through gunsmoke, soldiers following him"),
    # ------------------------------------------------------------- Egypt
    ("In 1798, he sailed for Egypt", "PAINTING", "FULL",
     "A great French fleet of sailing warships crossing the Mediterranean in 1798 under a bright sky, white sails, "
     "tricolour flags"),
    ("On land, he won.", "PAINTING", "FULL",
     "Battle of the Pyramids 1798, French infantry squares firing at charging Mamluk cavalry in colourful robes and "
     "turbans, the pyramids of Giza on the horizon, dust and smoke"),
    ("At Aboukir Bay", "PAINTING", "FULL",
     "Night naval battle at Aboukir Bay 1798, a huge French flagship exploding in a fireball, burning sailing ships, "
     "red reflections on dark water"),
    ("One of their finds was a black stone", "TODAY", "FRAME",
     "The Rosetta Stone, a dark granite slab carved with three scripts, displayed in a glass case in a dim museum "
     "gallery, soft spotlight"),
    ("Within weeks, in November 1799, he took part in a coup.", "PAINTING", "FULL",
     "The coup of 1799, General Napoleon in uniform confronting angry politicians in red robes inside a grand "
     "assembly hall, soldiers with bayonets at the doors"),
    ("Napoleon was First Consul.", "PORTRAIT", "SPLIT",
     "Napoleon as First Consul in 1800, young lean face, short dark hair, red velvet coat embroidered with gold, "
     "confident expression"),
    # ------------------------------------------------------------- consul / emperor
    ("So Napoleon did something Hannibal had done", "PAINTING", "FULL",
     "Napoleon crossing the Alps on a rearing white horse, flowing orange cloak, pointing upward, snowy mountain "
     "pass, soldiers dragging cannons behind"),
    ("In June 1800, at Marengo", "PAINTING", "FULL",
     "Battle of Marengo 1800 on the plains of northern Italy, French cavalry charging Austrian infantry in white "
     "coats, cannon smoke, afternoon light"),
    ("And in 1804 came the work he was proudest of", "STILL", "FRAME",
     "A thick leather-bound law book with gold-embossed eagle on the cover lying open on a desk beside a quill, "
     "inkwell and candle, early 1800s"),
    ("And on the second of December, 1804, in the cathedral of Notre-Dame", "PAINTING", "FULL",
     "The coronation of Napoleon in Notre-Dame cathedral 1804, Napoleon in red velvet and ermine robes raising a "
     "golden laurel crown, the Pope seated behind, nobles in rich clothes"),
    # ------------------------------------------------------------- 1805
    ("Napoleon gathered a huge army on the Channel coast", "PAINTING", "FULL",
     "A vast French army camp at Boulogne in 1804, rows of tents and soldiers on the cliffs, flat-bottomed boats "
     "on the beach, the white cliffs of England faint across the Channel"),
    ("On the twenty-first of October, 1805", "PAINTING", "FULL",
     "Battle of Trafalgar 1805, huge British and French sailing warships firing broadsides at close range, thick "
     "white smoke, shattered masts, rough sea"),
    ("Nelson sent a signal to his ships", "PORTRAIT", "SPLIT",
     "Admiral Horatio Nelson, slim, grey hair, empty right sleeve pinned to his chest, dark naval coat covered in "
     "gold braid and star medals"),
    ("Nelson himself was shot", "PAINTING", "FULL",
     "The death of Nelson on the deck of HMS Victory 1805, the wounded admiral supported by sailors and officers, "
     "smoke, ropes and rigging, solemn mood, no blood"),
    ("At Ulm, in October 1805", "PAINTING", "FULL",
     "Surrender at Ulm 1805, Austrian officers in white coats handing over their swords and flags to Napoleon on "
     "horseback, a walled town in the background"),
    ("near the village of Austerlitz", "PAINTING", "FULL",
     "Battle of Austerlitz 1805 at sunrise, a bright sun breaking through fog over snowy hills, French columns "
     "storming up the slope, Russian and Austrian troops below"),
    ("It became known as the Battle of the Three Emperors.", "PAINTING", "FULL",
     "Napoleon on a white horse surrounded by his staff on a hill after victory at Austerlitz, captured enemy flags "
     "at his feet, golden winter light"),
    # ------------------------------------------------------------- 1806-1807
    ("Napoleon rode into Berlin.", "PAINTING", "FULL",
     "Napoleon riding at the head of his Imperial Guard through the Brandenburg Gate into Berlin in 1806, crowds "
     "watching silently"),
    ("Then Russia. In the frozen snow of Eylau", "PAINTING", "FULL",
     "Battle of Eylau 1807 in a blizzard, cavalry charging through deep snow, dark sky, burning village"),
    ("At Tilsit, in July 1807", "PAINTING", "FULL",
     "Napoleon and Tsar Alexander I meeting on a decorated raft with a white pavilion in the middle of the Niemen "
     "river in 1807, crowds and soldiers on both banks"),
    ("From Spain to Poland", "MAP", "MAP",
     "Map of Europe in 1810 with the French Empire and its allies tinted soft blue covering most of the continent, "
     "Britain in red, Russia in green"),
    # ------------------------------------------------------------- Spain
    ("On the second of May, 1808", "PAINTING", "FULL",
     "The uprising in Madrid on 2 May 1808, Spanish townspeople with knives and sticks fighting French cavalry in a "
     "sunny street, chaos and dust, in the style of Goya"),
    ("The French answered with mass executions.", "PAINTING", "FULL",
     "Night scene in Madrid 1808 in the style of Goya, a line of French soldiers seen from behind, lit by a single "
     "lantern on the ground, dark hill and city behind, dramatic, non-graphic"),
    ("Britain sent an army to Portugal", "PORTRAIT", "SPLIT",
     "Arthur Wellesley, Duke of Wellington, tall and lean, large hooked nose, short brown hair, dark blue coat and "
     "white cravat, calm stern gaze"),
    ("But six weeks later, at Wagram", "PAINTING", "FULL",
     "Battle of Wagram 1809 on a wide plain near Vienna, a huge line of French cannons firing, columns of infantry "
     "advancing, smoke covering the horizon"),
    ("To secure his dynasty, Napoleon divorced his beloved Joséphine", "PORTRAIT", "SPLIT",
     "Empress Joséphine, elegant woman with dark curls, white empire-waist silk gown, pearl necklace and small "
     "tiara, gentle sad smile"),
    ("In 1810 he married Marie-Louise", "PORTRAIT", "SPLIT",
     "Empress Marie-Louise of Austria, young woman with light blonde hair, pale skin, white silk court gown with "
     "gold embroidery, diamond tiara"),
    # ------------------------------------------------------------- Russia 1812
    ("Tsar Alexander was tired of the Continental System.", "PORTRAIT", "SPLIT",
     "Tsar Alexander I of Russia, tall, balding with blond side-whiskers, dark green Russian uniform with gold "
     "epaulettes and a blue sash"),
    ("In June 1812, he gathered the largest army Europe had ever seen.", "PAINTING", "FULL",
     "The Grande Armée crossing the Niemen river on pontoon bridges in June 1812, endless columns of infantry, "
     "cavalry and wagons stretching to the horizon"),
    ("Finally, on the seventh of September, at Borodino", "PAINTING", "FULL",
     "Battle of Borodino 1812, massive armies clashing around earthwork fortifications, cannon smoke covering the "
     "field, Russian church domes in the distance"),
    ("Then Moscow began to burn.", "PAINTING", "FULL",
     "Napoleon watching Moscow burn from a window of the Kremlin at night in 1812, flames and smoke over colourful "
     "onion domes, red glow"),
    ("What followed is one of the great disasters of military history.", "PAINTING", "FULL",
     "Retreat from Moscow 1812, exhausted French soldiers wrapped in blankets trudging through a blizzard, "
     "abandoned cannons and wagons in the snow, grey sky"),
    ("At the Berezina River in November", "PAINTING", "FULL",
     "French engineers standing chest-deep in an icy river building wooden bridges in 1812, soldiers crossing "
     "above them, snow and floating ice"),
    # ------------------------------------------------------------- 1813-1814
    ("But in October 1813, near Leipzig, he was surrounded.", "PAINTING", "FULL",
     "Battle of Leipzig 1813, the Battle of Nations, huge armies of many nations attacking around a German city, "
     "church spires, smoke and cavalry charges"),
    ("On the sixth of April, Napoleon abdicated.", "PAINTING", "FULL",
     "Napoleon saying farewell to his Old Guard in the courtyard of the palace of Fontainebleau in 1814, emotional "
     "veterans with bearskin hats, a flag lowered"),
    ("He was sent into exile on Elba", "TODAY", "FULL",
     "The island of Elba seen from the sea, the small harbour of Portoferraio with old fortress walls, green hills, "
     "calm blue water"),
    ("The great powers gathered at the Congress of Vienna", "PAINTING", "FRAME",
     "The Congress of Vienna 1815, diplomats in elegant coats and powdered hair gathered around a table with maps "
     "in a grand palace room with chandeliers"),
    # ------------------------------------------------------------- Hundred Days / Waterloo
    ("Near Grenoble, a regiment of royal soldiers blocked the road.", "PAINTING", "FULL",
     f"{NAP} walking alone towards a line of soldiers aiming muskets at him on a mountain road near Grenoble in "
     "1815, opening his grey coat, tense dramatic moment"),
    ("On the twentieth of March, he entered Paris.", "PAINTING", "FULL",
     "Napoleon carried up the stairs of the Tuileries palace by a cheering crowd of officers and soldiers in March "
     "1815, candlelight, flags waving"),
    ("Two days later came Waterloo.", "PAINTING", "FULL",
     "Panoramic view of the battlefield of Waterloo on 18 June 1815, two great armies facing each other across a "
     "muddy valley, smoke rising, dramatic clouds"),
    ("The French attacked the farm of Hougoumont.", "PAINTING", "FULL",
     "The fortified farm of Hougoumont burning at Waterloo, British guardsmen defending the gate against French "
     "infantry, thick smoke"),
    ("Marshal Ney led wave after wave of cavalry", "PAINTING", "FULL",
     "French cuirassiers in shining steel breastplates and helmets charging around British infantry squares at "
     "Waterloo, bayonets bristling, smoke"),
    ("In the evening, Napoleon sent in his last reserve", "PAINTING", "FULL",
     "The French Imperial Guard in tall bearskin hats advancing up a slope at Waterloo in the evening light, "
     "drums, eagles, British lines waiting at the top"),
    ("to Saint Helena, a lonely island in the South Atlantic.", "TODAY", "FULL",
     "The remote island of Saint Helena in the South Atlantic, steep dark volcanic cliffs rising from a vast "
     "empty ocean, clouds over the peaks"),
    ("He died on the fifth of May, 1821.", "ENGRAVING", "FRAME",
     "Napoleon on his deathbed in a small simple room on Saint Helena in 1821, a few loyal companions standing in "
     "silence, candles, quiet and solemn"),
    # ------------------------------------------------------------- legacy
    ("The Napoleonic Wars cost millions of lives.", "PAINTING", "FULL",
     "The empty battlefield of Waterloo at dusk after the battle, abandoned cannons, broken wagons and fallen "
     "flags in the mud, a red sunset, sombre mood, non-graphic"),
    ("The Congress of Vienna built a new balance of power.", "MAP", "MAP",
     "Map of Europe in 1815 after the Congress of Vienna with redrawn borders, each country a different soft colour"),
    ("Napoleon remains one of the most debated figures in history.", "TODAY", "FULL",
     "Napoleon's red stone tomb under the golden dome of Les Invalides in Paris, seen from the balcony above, soft "
     "light, marble floor"),
    ("And then, on a muddy field in Belgium", "TODAY", "OUTRO",
     "The Lion's Mound monument at Waterloo at sunset, a tall grassy hill topped by a bronze lion, wide fields "
     "around, golden sky"),
]


def main():
    d = json.load(open(os.path.join(HERE, "video", "words.json")))
    text = "\n".join(d["lines"])
    words = d["words"]
    dur = d["duration"]
    out = ["NAPOLEONIC WARS - PERIOD IMAGE PROMPTS (to mix with the animation)",
           f"{len(I)} images for the {int(dur) // 60}:{int(dur) % 60:02d} voiceover. Times come from the aligned "
           "audio.", "", "STYLE BLOCKS (already added to the end of each prompt below):"]
    for k, v in STYLES.items():
        out.append(f"  [{k}] {v}")
    out += ["", "HOW TO USE IN THE EDIT:"] + [f"  {k}: {v}" for k, v in USE.items()] + [""]
    last = 0
    times = []
    for n, (cue, typ, use, scene) in enumerate(I, 1):
        pos = text.find(cue, last)
        if pos < 0:
            raise SystemExit(f"cue not found in order: {cue!r}")
        last = pos + 1
        sec = int(round(words[len(text[:pos].split())]["s"]))
        times.append(sec)
        out.append(f"{n:02d} | {sec // 60:02d}:{sec % 60:02d} | {typ} | USE: {use} | Cue: \"{cue}\"")
        out.append(f"{scene}. {STYLES[typ]}")
        out.append("")
    open(os.path.join(HERE, "real_image_prompts.txt"), "w", encoding="utf-8").write("\n".join(out))
    with open(os.path.join(HERE, "prompts_one_per_line.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(f"{scene}. {STYLES[typ]}" for _, typ, _, scene in I) + "\n")
    print(" · ".join(f"{n:02d}→{s // 60:02d}:{s % 60:02d}" for n, s in enumerate(times, 1)))


if __name__ == "__main__":
    main()
