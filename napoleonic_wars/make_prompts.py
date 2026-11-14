"""Build the image-prompt list for the Napoleonic Wars video.

Each scene is tied to the narration line where it should appear; the
timestamp is estimated from that line's word position, scaled to the
recorded audio length (17:50).
Usage: python3 make_prompts.py  -> writes image_prompts.txt
"""
import re

AUDIO_SECONDS = 17 * 60 + 50

STYLE = ("3D cartoon illustration, stylized toy-like characters with big heads and small bodies, "
         "smooth clay-like rendering, bright saturated colors, soft cinematic lighting, simple clean "
         "background, low-poly trees and terrain, historically accurate early-1800s uniforms, "
         "no text, no letters, 16:9")

NAP = ("Napoleon (short man, black bicorne hat worn sideways, dark blue coat with gold epaulettes, "
       "white waistcoat and breeches, black boots, short dark hair)")
YNAP = ("young Napoleon (thin, long straight dark hair to the shoulders, simple dark blue officer coat, "
        "no epaulettes)")
OLDNAP = "older, heavier Napoleon (receding hair, plain green coat)"
WELL = ("the Duke of Wellington (tall thin man, large hooked nose, plain dark blue coat, "
        "dark cloak, bicorne hat worn front-to-back)")
NEL = ("Admiral Nelson (slim man, empty right sleeve pinned to his chest, dark navy admiral coat "
       "with gold stars and medals)")
TSAR = "Tsar Alexander I (tall, balding with blond side-whiskers, dark green Russian uniform with gold epaulettes)"

S = [
    # ---------------------------------------------------------- cold open
    ("Belgium. The eighteenth of June, 1815.", "Wide shot of rainy dawn over muddy green Belgian fields, small farmhouses, dark grey storm clouds, puddles reflecting the sky"),
    ("It rained all night.", "Soaked, tired soldiers in red and blue coats huddled around a smoky campfire in the rain, mud on their boots"),
    ("On one side of the valley", f"British redcoat army lined up on a green ridge with Union flags, {WELL} on a chestnut horse in front"),
    ("On the other side stands the man", "French army across the valley in blue coats with tricolour flags and golden eagle standards, cannons in front"),
    ("Napoleon Bonaparte.\nHe has", f"Dramatic low-angle close-up of {NAP} on a white horse, stern face, rain falling, dark sky behind"),
    ("He has crowned himself Emperor.", f"{NAP} raising a golden laurel crown above his head, glowing light"),
    ("He has redrawn the map", f"{NAP} leaning over a giant map of Europe on a table, moving toy soldiers across it"),
    ("And today, near a small village called Waterloo", "Small Belgian village with a church spire and a windmill, two armies tiny in the distance, misty morning"),
    ("But to understand how Europe", "Old calendar pages and paper maps swirling backwards through the air like a time tunnel, warm sepia light"),
    ("This is the story of the Napoleonic Wars.", "Epic title shot: silhouette of Napoleon in a bicorne hat against a fiery orange sunset, marching armies and cannons below"),
    # ---------------------------------------------------------- revolution
    ("In 1789, France explodes.", "Parisian crowd storming the Bastille fortress, tricolour flags waving, smoke rising, energetic"),
    ("The king loses his power", "King Louis XVI looking worried as his crown slips off his head, crowd shadows behind him, not gory"),
    ("The monarchies of Europe watch in horror.", "Four cartoon kings in crowns (Austria, Prussia, Britain, Spain) peeking over a stone wall in shock"),
    ("So Austria, Prussia, Britain, Spain and others go to war", "Map of Europe with coloured army arrows converging on France from every side"),
    ("France is surrounded.", "Disorganised French army camp, soldiers in patched mismatched uniforms looking confused"),
    ("Napoleon Bonaparte was born in 1769 on Corsica", "Sunny Mediterranean island town on Corsica, stone houses, green mountains, turquoise sea"),
    ("He spoke French with an accent.", f"{YNAP} as a lonely military-school cadet reading books, other cadets laughing in the background"),
    ("In 1793, at the port of Toulon", "Harbour of Toulon with British warships at anchor and stone forts on the hills"),
    ("A twenty-four-year-old artillery captain", f"{YNAP} on a hilltop pointing at a map beside a row of cannons, harbour below"),
    ("The British fleet was forced out.", "Cannons firing from the hill, British ships sailing away from a burning harbour at night"),
    ("Two years later, in 1795", "Angry royalist mob with white flags marching down a Paris street toward a palace"),
    ("Napoleon met them with cannon fire", f"{YNAP} beside cannons in a Paris street, smoke clouds, the mob running away (no gore)"),
    ("In 1796, they gave him command", "Ragged French soldiers in torn uniforms, some barefoot, camped in rocky mountains"),
    ("He told them:", f"{YNAP} standing on a rock addressing his ragged troops, pointing toward sunny green plains of Italy"),
    ("In one campaign, he beat the Austrians", f"{YNAP} carrying a tricolour flag across a narrow bridge, leading a charge through smoke"),
    ("He moved faster than his enemies", "Map of northern Italy with fast blue arrows splitting apart slow white arrows"),
    ("By 1797, Austria asked for peace.", f"Paris crowds cheering {YNAP} in a victory parade, flowers in the air"),
    # ---------------------------------------------------------- egypt
    ("Britain remained at war with France.", "Mighty Royal Navy ships of the line on a blue sea, white cliffs of Dover behind"),
    ("So Napoleon proposed something bold.", "Map with a bold arrow from France across the Mediterranean to Egypt, continuing toward India"),
    ("In 1798, he sailed for Egypt", "French fleet sailing in sunshine, scientists on deck with telescopes, books and globes"),
    ("On land, he won.", "Battle of the Pyramids: French infantry squares facing charging Mamluk cavalry in colourful robes, pyramids behind"),
    ("At Aboukir Bay", "Night naval battle, British ships attacking anchored French fleet, a huge French flagship exploding in orange light"),
    ("His scholars, though", "French scholars uncovering a black carved stone (the Rosetta Stone) in the desert sand, amazed faces"),
    ("In 1799, Napoleon heard that France was in trouble.", f"{NAP} reading a letter by lamplight in a desert tent, worried expression"),
    ("So he slipped away from Egypt", "Small sailing ship leaving the Egyptian coast secretly at night under the moon"),
    ("Within weeks, in November 1799", "Soldiers with bayonets entering a grand hall, politicians in red robes running away in panic"),
    ("Napoleon was First Consul.", f"{NAP} in a red-and-gold consul coat sitting in the middle of three chairs, two smaller men beside him"),
    # ---------------------------------------------------------- consul
    ("So Napoleon did something Hannibal had done", f"{NAP} riding a mule across the snowy Alps, soldiers dragging cannons up a mountain pass"),
    ("In June 1800, at Marengo", "French troops retreating on a sunny battlefield, Austrian soldiers in white coats advancing"),
    ("Then fresh troops arrived", "Fresh French reinforcements and cavalry charging over a hill, Austrians surprised"),
    ("Peace followed with Austria in 1801.", "Diplomats in wigs signing a treaty with quill pens at a grand table"),
    ("For a brief moment, Europe was quiet.", "Peaceful French countryside at sunset, farmers in fields, a calm village"),
    ("He reformed taxes.", f"{NAP} at a desk piled high with papers, a new bank building and school visible through the window"),
    ("And in 1804 came the work he was proudest of", f"A large leather-bound law book glowing on a table, {NAP} standing proudly beside it"),
    ("Parts of it still shape legal systems", "Globe with glowing points on many countries, stacks of law books around it"),
    ("By 1803, Britain and France were at war again.", "British and French warships exchanging cannon fire, smoke over the sea"),
    ("And on the second of December, 1804, in the cathedral", "Grand Gothic interior of Notre-Dame cathedral filled with nobles in rich clothes, candles"),
    ("Instead, Napoleon took the crown", f"{NAP} in a red velvet coronation robe placing a crown on his own head, the Pope seated behind looking surprised"),
    ("The Revolution had executed a king.", f"{NAP} as Emperor on a golden throne, red robe with golden bees, eagle symbols"),
    # ---------------------------------------------------------- trafalgar / austerlitz
    ("Napoleon gathered a huge army on the Channel coast", "Huge army camp on the French coast at Boulogne, soldiers looking across the sea at English white cliffs"),
    ("He never got it.", "Empty English Channel with rough grey waves and stormy sky"),
    ("On the twenty-first of October, 1805", "Two great fleets lining up on a calm blue sea off a Spanish cape, sails full"),
    ("Nelson sent a signal to his ships", f"Colourful signal flags hoisted on HMS Victory, {NEL} standing on deck"),
    ("The British broke the enemy line.", "British warships cutting through a line of French and Spanish ships, cannon smoke everywhere"),
    ("Nelson himself was shot", f"{NEL} lying on the deck, sailors kneeling around him, solemn mood, no blood"),
    ("So he turned east.", f"{NAP} turning away from the sea and pointing east on a map"),
    ("Austria and Russia had joined Britain", "Grande Armée marching in long blue columns along German country roads, autumn trees"),
    ("At Ulm, in October 1805", f"Austrian soldiers in white coats laying down flags and muskets in front of {NAP}"),
    ("On the second of December, 1805, exactly one year", f"Winter battlefield at Austerlitz, the Austrian Emperor and {TSAR} watching from a hill"),
    ("He deliberately made his right flank look weak.", "Battle map: a thin French line on the right, big allied arrows attacking it"),
    ("Out of the morning fog", "Bright sun breaking through thick morning fog, French columns storming up a hill"),
    ("It became known as the Battle of the Three Emperors.", f"{NAP} victorious on a hill, surrounded by captured enemy flags, golden light"),
    ("Austria made peace.", "An old imperial crown crumbling into dust on a velvet cushion"),
    # ---------------------------------------------------------- prussia / russia
    ("In 1806, Prussia, proud of the army", "Proud Prussian army in dark blue coats with old-fashioned pigtails, marching in perfect lines"),
    ("On a single day, the fourteenth of October", "French cavalry charging, Prussian lines breaking and fleeing across a field"),
    ("Napoleon rode into Berlin.", f"{NAP} riding a white horse through the Brandenburg Gate in Berlin"),
    ("If he could not beat Britain at sea", "European harbour closed with a chain, British cargo ships blocked, crates piling up on the dock"),
    ("Then Russia. In the frozen snow of Eylau", "Cavalry charging through a blizzard on a snowy battlefield, dark sky"),
    ("But in June, at Friedland", "Sunny summer battlefield, Russian army retreating across a river, French cannons firing"),
    ("At Tilsit, in July 1807", f"{NAP} and {TSAR} shaking hands on a decorated raft in the middle of a river, crowds on both banks"),
    ("Prussia lost huge territories.", "Three young men being crowned kings at once, each holding a sceptre"),
    ("From Spain to Poland", "Map of Europe almost completely coloured French blue"),
    ("It seemed nothing could stop him.", f"{NAP} on a throne before a giant map, a thin crack spreading across the marble floor"),
    # ---------------------------------------------------------- spain
    ("Portugal refused to obey the Continental System.", "French troops marching through dry dusty Spanish hills under a hot sun"),
    ("Then Napoleon went further.", "Joseph Bonaparte being crowned King of Spain while Spanish nobles frown"),
    ("On the second of May, 1808", "Madrid street, crowds fighting French soldiers, chaos, dust"),
    ("The French answered with mass executions.", "Night scene lit by a lantern, line of soldiers seen from behind, dramatic Goya-inspired mood, non-graphic"),
    ("The revolt spread across the country.", "Spanish guerrilla fighters ambushing a French supply wagon in rocky hills"),
    ("Britain sent an army to Portugal", f"{WELL} landing on a Portuguese beach with redcoat soldiers"),
    ("For six years, Spain became a trap", "Exhausted French soldiers in Spanish heat, a map where Spain glows red like a wound"),
    ("Meanwhile, in 1809, Austria tried again.", "Austrian army in white coats marching again with drums and flags"),
    ("At Aspern-Essling", "French troops pushed back across broken bridges on the Danube river"),
    ("But six weeks later, at Wagram", "Huge line of French cannons firing on a wide plain, smoke clouds"),
    ("To secure his dynasty", f"Joséphine (elegant woman, dark curls, white empire-waist dress) crying while {NAP} looks away"),
    ("In 1810 he married Marie-Louise", f"Wedding of {NAP} and Marie-Louise (young blonde woman, white dress) in a grand palace chapel"),
    ("In 1811, she gave birth to a son.", f"{NAP} proudly holding a baby above a golden cradle"),
    ("It wasn't.", "Dark storm clouds gathering over a grand imperial palace"),
    # ---------------------------------------------------------- russia 1812
    ("Tsar Alexander was tired of the Continental System.", f"{TSAR} frowning, British trade ships unloading in a Russian port behind him"),
    ("In June 1812, he gathered the largest army", "Enormous army crossing a river on pontoon bridges, columns stretching to the horizon"),
    ("The Russians refused to give him one.", "Russian army retreating, villages and wheat fields burning behind them"),
    ("Men died of exhaustion", "French soldiers marching through summer heat and dust, some collapsing beside the road"),
    ("Finally, on the seventh of September, at Borodino", "Massive battle with earthwork forts, cannon smoke covering the field"),
    ("A week later, he entered Moscow.", f"{NAP} on a hill looking at Moscow's colourful onion domes"),
    ("Then Moscow began to burn.", f"Moscow in flames at night, {NAP} watching from a Kremlin window"),
    ("The message never came.", f"{NAP} waiting alone at a table with one candle and an empty chair"),
    ("What followed is one of the great disasters", "Long line of soldiers retreating through a blizzard, grey sky"),
    ("Snow. Freezing cold.", "Soldiers huddled in snow, abandoned cannons, Cossack horsemen on a distant ridge"),
    ("At the Berezina River in November", "Engineers standing waist-deep in an icy river building a wooden bridge, soldiers crossing"),
    ("Napoleon rushed back to Paris", f"{NAP} in a fur coat in a sleigh racing through snow at night"),
    ("The myth of the unbeatable Emperor was broken.", "A broken bronze statue of Napoleon half-buried in snow"),
    # ---------------------------------------------------------- 1813-1814
    ("Now everyone turned against him.", "Allied monarchs shaking hands under the flags of Prussia, Russia, Austria, Sweden and Britain"),
    ("Napoleon raised a new army", "Very young nervous soldiers in oversized uniforms and shakos"),
    ("But in October 1813, near Leipzig", "Huge battlefield around a German city, armies closing in from all sides"),
    ("Napoleon lost.\nIn 1814", "French troops retreating across a river as a stone bridge explodes behind them"),
    ("In 1814, the allies invaded France itself.", f"{NAP} leading a small army through a snowy French countryside"),
    ("On the thirty-first of March, 1814", "Allied soldiers parading through Paris streets, crowds watching"),
    ("On the sixth of April, Napoleon abdicated.", f"{NAP} signing a paper at a desk in a palace, sad marshals standing around him"),
    ("He was sent into exile on Elba", f"{NAP} standing alone on a tiny rocky island, staring at the sea"),
    ("The old French royal family returned.", "Louis XVIII (elderly, very heavy king in a blue sash) on a throne"),
    ("The great powers gathered at the Congress of Vienna", "Diplomats around a giant map in a chandelier-lit ballroom, couples dancing behind"),
    # ---------------------------------------------------------- hundred days
    ("Less than a year later, in February 1815", "Small boat escaping an island at night under the moon"),
    ("He landed in the south of France", f"{NAP} landing on a beach with a small band of guards in tall bearskin hats"),
    ("Near Grenoble", f"{NAP} standing alone opening his coat in front of a line of soldiers aiming muskets on a mountain road"),
    ("The soldiers did not fire.", "Soldiers cheering and throwing their hats in the air"),
    ("On the twentieth of March, he entered Paris.", f"Cheering crowd carrying {NAP} up the stairs of a palace"),
    ("Europe declared him an outlaw.", "Allied armies gathering and marching from every direction across a map"),
    ("On the sixteenth of June", "Battle of Ligny: an old Prussian general with a white moustache fallen under his horse, battle around"),
    ("Because of the rain", f"{NAP} at a breakfast table looking out at a muddy field, waiting"),
    ("Every hour mattered", "Prussian columns marching through mud on a forest road, pulling cannons"),
    ("The French attacked the farm of Hougoumont.", "Walled farmhouse burning, defenders at the gate, smoke"),
    ("Marshal Ney led wave after wave", "French armoured cavalry in shining breastplates charging around British infantry squares"),
    ("In the late afternoon", "Prussian soldiers emerging from the woods on the side of the battlefield"),
    ("In the evening, Napoleon sent in his last reserve", "Imperial Guard in tall bearskin hats advancing up a slope in the evening light"),
    ("A cry went through the French ranks", "French soldiers running away across a field at dusk, abandoned flags"),
    ("Napoleon abdicated for the second time.", f"{NAP} on the deck of a British warship looking back at the coast"),
    ("to Saint Helena", "Remote rocky island in a vast empty ocean, cloudy sky"),
    ("He spent his last years there", f"{OLDNAP} dictating to a secretary at a desk in a small room"),
    ("He died on the fifth of May, 1821.", "Empty armchair with a black bicorne hat resting on it, a candle just blown out"),
    # ---------------------------------------------------------- legacy
    ("The Napoleonic Wars cost millions of lives.", "Quiet memorial field with rows of small crosses at sunset, solemn mood"),
    ("The old Holy Roman Empire was gone.", "Map of Europe with borders shifting and new nations appearing"),
    ("And after Waterloo, Britain stood", "British fleet sailing past London with the Thames and old buildings"),
    ("The Congress of Vienna built a new balance of power.", "Large balance scale holding small flags of European countries, perfectly level"),
    ("Napoleon remains one of the most debated", f"Split portrait of {NAP}: one half heroic and golden, the other half in dark shadow"),
    ("He once said:", f"Close-up of {NAP} with a confident smirk"),
    ("And then, on a muddy field in Belgium", "Lonely black bicorne hat lying in the mud of an empty battlefield at sunset"),
]


def main():
    lines = [l for l in open("narration.txt", encoding="utf-8").read().splitlines()
             if not l.startswith("[") and not l.startswith("THE ")]
    text = "\n".join(lines).strip()
    total = len(text.split())
    out = ["NAPOLEONIC WARS - IMAGE PROMPTS",
           f"{len(S)} images for a {AUDIO_SECONDS // 60}:{AUDIO_SECONDS % 60:02d} voiceover "
           "(about one image every 8 seconds).",
           "Times are estimates from the script: check the cue line against your audio.",
           "",
           "STYLE (already added at the end of every prompt below):",
           STYLE, ""]
    for i, (cue, scene) in enumerate(S, 1):
        pos = text.find(cue)
        if pos < 0:
            raise SystemExit(f"cue not found: {cue!r}")
        sec = round(len(text[:pos].split()) / total * AUDIO_SECONDS)
        out.append(f"{i:03d} | {sec // 60:02d}:{sec % 60:02d} | Cue: \"{cue.splitlines()[0]}\"")
        out.append(f"{scene}. {STYLE}")
        out.append("")
    open("image_prompts.txt", "w", encoding="utf-8").write("\n".join(out))
    print(len(S), "prompts")


if __name__ == "__main__":
    main()
