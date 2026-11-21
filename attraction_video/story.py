"""Why Are Men Attracted to Women? - shot list.
Each shot: (spec, narration text).  Text is split into sentences for alignment.
Coordinates (x, y) are normalised to the source image (0..1).
cam = (zoom_start, zoom_end, cx0, cy0, cx1, cy1); zoom 1 = full 16:9 width of the image.
labels: (text, x, y, sentence_index, delay, colour)
"""
import re

Y, C, M, O, G, R = (255, 214, 80), (70, 230, 240), (255, 90, 190), (255, 140, 90), (140, 255, 160), (255, 80, 90)


def S(img, cam=(1.0, 1.12, .5, .5, .5, .5), **kw):
    d = dict(img=img, cam=cam)
    d.update(kw)
    return d


def CH(num, title, img, mood):
    return S(img, (1.15, 1.3, .5, .5, .5, .5), chapter=(num, title), mood=mood, sfx=["chapter"])


def split(text):
    text = " ".join(text.split())
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z\"])", text)
    return [p for p in parts if p]


RAW = [
    # ------------------------------------------------------------ COLD OPEN
    (S("S01_street", (1.0, 1.35, .5, .5, .47, .62), sfx=["city"], mood=0, kw=["busy street", "Hundreds of faces"]),
     "You are walking down a busy street. Hundreds of faces pass you by."),
    (S("S01_street", (1.6, 2.6, .47, .62, .475, .6), dof=(.475, .6, .16), sfx=["heartbeat", "swell"], pulse=(.475, .6, .07, 1.2), kw=["stops you"]),
     "And then, for no reason you can explain, one of them stops you."),
    (S("S33_heart_race", (1.15, 1.45, .5, .45, .5, .4), pulse=(.5, .38, .16, 2.0), sfx=["heartbeat"], kw=["heart"]),
     "Your heart speeds up."),
    (S("S02_eye_closeup", (1.0, 1.6, .5, .5, .5, .5), pulse=(.5, .5, .2, 0.9), sfx=["shimmer"], kw=["pupils widen", "warm"]),
     "Your pupils widen. Your palms get a little warm."),
    (S("S03_brain_flash", (1.05, 1.3, .5, .5, .58, .45), pulse=(.66, .32, .14, .8), sfx=["whisper"], kw=["look again"]),
     "Something inside you whispers: look again."),
    (S("S03_brain_flash", (1.35, 1.0, .62, .42, .5, .5), big=("< 1 SECOND", "", 1), sfx=["zap"], kw=["Your brain decided", "less than a second"]),
     "You did not decide this. Your brain decided it for you, in less than a second, long before you had a single conscious thought."),
    (S("S54_endcard_bg", (1.0, 1.08, .5, .5, .5, .55),
       chars=[("CHAR_man", .3, .62, 640, 0, 0.0, "left"), ("CHAR_woman", .7, .62, 620, 1, 0.2, "right")],
       qmarks=True, big=("WHY HER?", "", 2), sfx=["pop"], kw=["Why her"]),
     "So what just happened? Why is a man drawn to a woman at all? Why her, and not someone else?"),
    (S("S54_endcard_bg", (1.0, 1.05, .5, .5, .5, .5),
       quad=[("S05_ancient_ocean", "EVOLUTION", C), ("S34_dopamine_rain", "CHEMISTRY", Y), ("S31_brain_city", "BRAIN ON FIRE", M), ("S22_culture_shapes", "CULTURE", O)],
       sfx=["pop4"], kw=["ancient evolution", "invisible chemistry", "brain on fire", "culture"]),
     "The answer is a strange mix of ancient evolution, invisible chemistry, a brain on fire, and the culture you grew up in."),
    (S("S54_endcard_bg", (1.0, 1.1, .5, .55, .5, .55), title=True, sfx=["title"], mood=1,
       chars=[("MASCOT_lumi", .5, .78, 300, 0, 1.0, "pop")]),
     "Let us take attraction apart, piece by piece, and see what is really going on inside you."),

    # ------------------------------------------------------------ PART 1
    (CH(1, "The Oldest Story on Earth", "S52_billion_years", 1), "Part One. The Oldest Story on Earth."),
    (S("S52_billion_years", (1.0, 1.5, .5, .5, .48, .5), spin=True, sfx=["rewind"], kw=["go back"]),
     "To understand attraction, we have to go back. Way back."),
    (S("S05_ancient_ocean", (1.25, 1.0, .5, .3, .5, .5), big=("1,000,000,000", "YEARS AGO", 0), count=1e9, sfx=["ocean", "bubbles"], kw=["one billion years", "copied themselves"]),
     "About one billion years. For most of the history of life, living things simply copied themselves."),
    (S("S06_cell_split", (1.0, 1.25, .5, .5, .5, .5), pulse=(.5, .5, .3, .6), sfx=["blob", "blob2"], kw=["split in two", "Simple", "Efficient"]),
     "A cell split in two. Then those two split again. Simple. Efficient. But there was a problem."),
    (S("S07_identical_cells", (1.5, 1.0, .5, .5, .5, .5), sfx=["swell"], kw=["copy", "enemies"]),
     "A copy is only ever as good as the original. And the world is full of enemies."),
    (S("S08_virus_attack", (1.1, 1.3, .5, .5, .5, .55), shake=.25, sfx=["villain", "pop3"],
       labels=[("VIRUSES", .2, .2, 0, 0, R), ("PARASITES", .83, .22, 1, 0, M), ("BACTERIA", .78, .8, 2, 0, O)],
       kw=["Viruses", "Parasites", "Bacteria", "weaknesses"]),
     "Viruses. Parasites. Bacteria. They evolve fast, and they are constantly searching for weaknesses."),
    (S("S07_identical_cells", (1.0, 1.15, .5, .5, .5, .5), tint=(255, 60, 80),
       chars=[("CHAR_virus", .5, .52, 560, 0, 0.0, "sweep")], big=("ALL OF THEM", "", 1), sfx=["villain", "crunch"], kw=["buffet", "crack all of them"]),
     "A population of identical copies is a buffet. Once a parasite cracks the code of one, it can crack all of them."),
    (S("S09_dna_mixing", (1.3, 1.0, .5, .45, .5, .5), sfx=["magic"], big=("MIXING", "", 1), mood=2, kw=["Mixing", "combine its genes"]),
     "So life invented something radical. Mixing. Instead of copying itself, an organism could combine its genes with someone else's genes."),
    (S("S10_new_lock", (1.0, 1.4, .5, .45, .52, .42), pulse=(.52, .42, .14, .7), sfx=["lock"], kw=["brand new combination", "new lock"]),
     "Every child would be a brand new combination. A new lock that the parasites had never seen before."),
    (S("S11_sperm_egg_meet", (1.0, 1.25, .4, .5, .62, .5), sfx=["swish"], kw=["birth of sex", "two different strategies"]),
     "This was the birth of sex. And with it came two different strategies."),
    (S("S54_endcard_bg", (1.0, 1.06, .5, .5, .5, .5), dim=.25,
       chars=[("CHAR_sperm", .28, .42, 340, 0, 0.0, "left"), ("CHAR_egg", .72, .4, 560, 2, 0.0, "right")],
       labels=[("SPERM", .28, .66, 1, 0, C), ("TINY  ·  CHEAP  ·  PLENTIFUL", .28, .74, 1, .5, C),
               ("EGG", .72, .66, 3, 0, O), ("LARGE  ·  RARE  ·  RICH", .72, .74, 3, .5, O)],
       nopoint=True, sfx=["swish", "pop"], kw=["sperm", "eggs", "tiny", "large"]),
     "One partner made tiny cells that were cheap and plentiful. We call them sperm. The other made large cells that were rare and full of resources. We call them eggs."),
    (S("S12_millions_vs_400", (1.0, 1.08, .5, .5, .5, .5),
       labels=[("MILLIONS  /  DAY", .27, .14, 1, 0, C), ("~400  /  LIFETIME", .78, .14, 2, 0, O)], nopoint=True,
       sfx=["tick"], kw=["millions of sperm", "four hundred"]),
     "In humans, the difference is enormous. A man produces millions of sperm every single day. A woman is born with all the eggs she will ever have, and only around four hundred of them will mature in her lifetime."),
    (S("S13_pregnancy_time", (1.0, 1.3, .5, .5, .45, .6), pulse=(.45, .66, .08, 1.0), big=("9 MONTHS", "+ YEARS OF CARE", 1), sfx=["chime"], kw=["Nine months", "energy, time, and risk"]),
     "And then comes pregnancy. Nine months of carrying a child, followed by years of feeding and care. For most of human history, that was a huge investment of energy, time, and risk."),
    (S("S16_ancestors", (1.3, 1.0, .5, .6, .5, .5), fire=(.5, .75), sfx=["fire"], kw=["shaped everything", "different instincts"]),
     "This imbalance shaped everything. Evolution built men and women with slightly different instincts, because their bodies faced different challenges."),
    (S("S14_genes_puppet", (1.0, 1.2, .5, .5, .5, .45), sfx=["swell"], kw=["oldest story on Earth", "genes"]),
     "Attraction is the engine that drives the oldest story on Earth: the story of genes trying to survive into the future."),
    (S("S14_genes_puppet", (1.5, 2.1, .48, .55, .47, .62), pulse=(.47, .6, .1, 1.0), sparks=(.47, .6), big=("A PULL. A SPARK.", "", 4), sfx=["spark"], kw=["do not care", "A feeling", "A pull", "A spark", "attraction"]),
     "But here is the important part. Your genes do not care about your feelings. They do not give you a plan. They give you a feeling. A pull. A spark. And you experience that spark as attraction."),

    # ------------------------------------------------------------ PART 2
    (CH(2, "What the Eyes Are Looking For", "S15_scanning_vision", 2), "Part Two. What the Eyes Are Looking For."),
    (S("S15_scanning_vision", (1.0, 1.3, .5, .5, .5, .45), scan=True, sfx=["scan"], kw=["scanning"]),
     "So what exactly is a man's brain scanning for when he looks at a woman?"),
    (S("S46_world_survey", (1.0, 1.25, .5, .5, .45, .5), sfx=["ping3"], kw=["dozens of cultures", "again and again"], subscribe=True),
     "Scientists have studied this across dozens of cultures, and some patterns appear again and again."),
    (S("S17_health_signals", (1.2, 1.05, .5, .5, .5, .5), num=("1", "HEALTH"), sfx=["badge"], kw=["health"]),
     "The first is health."),
    (S("S16_ancestors", (1.0, 1.25, .5, .5, .5, .6), fire=(.5, .75), sfx=["fire"], kw=["healthy children", "blood test", "signals of health"]),
     "For our ancestors, a healthy partner meant healthy children. But nobody could run a blood test. So the brain learned to read signals of health directly from the body."),
    (S("S17_health_signals", (1.05, 1.3, .5, .5, .52, .5),
       labels=[("CLEAR SKIN", .43, .55, 0, 0, Y), ("BRIGHT EYES", .79, .2, 1, 0, C), ("SHINY HAIR", .5, .14, 2, 0, M), ("FULL LIPS", .53, .66, 3, 0, O)],
       sfx=["pop4"], kw=["Clear skin", "Bright eyes", "Shiny hair", "Full lips", "youth", "nutrition", "immune system"]),
     "Clear skin. Bright eyes. Shiny hair. Full lips. These are not random preferences. Many of them are signs of youth, good nutrition, and a strong immune system."),
    (S("S19_symmetry", (1.2, 1.05, .5, .5, .5, .5), num=("2", "SYMMETRY"), sfx=["badge"], kw=["symmetry"]),
     "Then there is symmetry."),
    (S("S18_womb_blueprint", (1.0, 1.45, .55, .5, .55, .48), pulse=(.55, .48, .2, .5), grid=True, sfx=["heartbeat_soft", "hum"], kw=["genetic blueprint", "perfectly balanced"]),
     "As you grew in your mother's womb, your body was built from a genetic blueprint. But stress, illness, and parasites can push that building process slightly off course. A face that grew up perfectly balanced can be a sign that the body handled those challenges well."),
    (S("S19_symmetry", (1.0, 1.35, .5, .5, .5, .5), mirror=.5, sfx=["scan"], kw=["more symmetrical", "more attractive", "no idea why"]),
     "In experiments, when people are shown faces that have been made more symmetrical by a computer, they usually rate them as more attractive. Most of the time, people have no idea why."),
    (S("S20_average_face", (1.25, 1.05, .5, .5, .5, .5), num=("3", "AVERAGE"), sfx=["badge"], kw=["Average", "surprising"]),
     "Next comes something surprising. Average."),
    (S("S20_average_face", (1.0, 1.5, .5, .5, .5, .5), pulse=(.5, .5, .2, .4), swirl=True, sfx=["magic"], kw=["blend dozens of faces", "more attractive", "Not boring", "mix of many genes"]),
     "When researchers blend dozens of faces together into one composite face, the result is almost always rated as more attractive than the individual faces. Not boring. Attractive. An average face may signal a mix of many genes, and a smaller chance of rare genetic problems."),
    (S("S21_estrogen", (1.2, 1.05, .5, .5, .5, .5), num=("4", "HORMONES"), sfx=["badge"], kw=["hormones"]),
     "And then there are hormones written on the body."),
    (S("S21_estrogen", (1.05, 1.4, .4, .5, .55, .5), labels=[("ESTROGEN", .3, .35, 0, .3, M)], sfx=["shimmer"], kw=["estrogen", "narrower than their hips"]),
     "As a girl becomes a woman, the hormone estrogen reshapes her body. It softens the face, makes the lips fuller, and changes how fat is stored, giving many women a waist that is narrower than their hips."),
    (S("S22_culture_shapes", (1.0, 1.2, .5, .5, .5, .45), sfx=["world"], kw=["Across many cultures", "Not one exact body type", "hormones of adulthood"]),
     "Across many cultures, men are drawn to this waist to hip ratio. Not one exact body type, but a shape that signals that the hormones of adulthood are working."),
    (S("S03_brain_flash", (1.0, 1.4, .5, .5, .6, .45), pulse=(.62, .4, .16, 2.4), sfx=["zap"], kw=["fraction of a second", "without permission"]),
     "All of these signals are processed in a fraction of a second, deep in the brain, without permission. You do not think: this face is symmetrical."),
    (S("S23_wow", (1.25, 1.0, .5, .4, .5, .5), big=("WOW.", "", 0), confetti=True, sfx=["wow"], kw=["wow"]),
     "You just think: wow."),

    # ------------------------------------------------------------ PART 3
    (CH(3, "The Invisible Signals", "S30_senses_to_brain", 3), "Part Three. The Invisible Signals."),
    (S("S30_senses_to_brain", (1.3, 1.6, .25, .55, .22, .6), sfx=["mystery"], kw=["cannot see at all"]),
     "But attraction is not only about what you see. Some of the most powerful signals are things you cannot see at all."),
    (S("S24_voice_waves", (1.0, 1.25, .5, .5, .58, .5), waves=(.5, .48), sfx=["voice"], kw=["voice", "higher, softer voices", "estrogen"]),
     "Let us start with the voice. When men listen to recordings of women's voices, they often rate higher, softer voices as more attractive. A higher voice can be linked to higher levels of estrogen."),
    (S("S25_cycle_calendar", (1.0, 1.3, .55, .5, .6, .45), spinring=(.6, .45), badge=("STILL DEBATED", 1, Y), sfx=["tick"], kw=["fertile days", "debate", "the ear"]),
     "Some studies even suggest that a woman's voice can become slightly higher and more attractive around the most fertile days of her cycle. The effect is small, and scientists still debate it. But the ear may be quietly listening for information the eyes cannot see."),
    (S("S26_dog_vs_nose", (1.1, 1.3, .3, .5, .55, .5), sfx=["sniff"], kw=["smell", "dogs", "collecting information"]),
     "Then there is smell. You might think humans have a weak sense of smell compared to dogs. And you would be right. But our noses are still collecting information all the time."),
    (S("S27_tshirt_lab", (1.0, 1.3, .45, .5, .5, .45), labels=[("THE SWEATY T-SHIRT STUDY", .5, .1, 0, .5, Y)], nopoint=True, smoke=True, sfx=["sniff", "lab"], kw=["T-shirts", "two nights", "immune system genes were different"]),
     "In a famous experiment, women were asked to smell T-shirts that men had worn for two nights. On average, they preferred the smell of men whose immune system genes were different from their own."),
    (S("S28_immune_puzzle", (1.0, 1.25, .5, .5, .55, .5), snap=True, sfx=["click", "shield"], kw=["two different sets of immune genes", "completes your defenses"]),
     "Why would that matter? Because a child who inherits two different sets of immune genes may be able to recognize a wider range of diseases. Your nose might be helping you choose a partner who completes your defenses."),
    (S("S29_perfume_myth", (1.0, 1.3, .55, .5, .5, .5), badge=("NOT PROVEN", 2, R), sfx=["stamp", "magic"], kw=["pheromones", "not found", "Magic perfumes, probably not"]),
     "There are also claims about human pheromones, invisible chemical messages that make people instantly attracted. Many perfume companies love this idea. But the truth is that scientists have not found a clear, proven human sex pheromone yet. Smell matters. Magic perfumes, probably not."),
    (S("S30_senses_to_brain", (1.0, 1.15, .45, .5, .55, .5), flow=True,
       labels=[("EYES", .1, .12, 1, 0, C), ("EARS", .1, .48, 1, .4, M), ("NOSE", .1, .9, 1, .8, Y)], sfx=["stream"], kw=["whole body experience", "one place"]),
     "So attraction is a whole body experience. Your eyes, your ears, and your nose are all sending reports to one place."),
    (S("S30_senses_to_brain", (1.4, 2.2, .7, .45, .73, .45), pulse=(.73, .45, .2, 1.0), sfx=["boom"], kw=["Your brain"]),
     "Your brain."),

    # ------------------------------------------------------------ PART 4
    (CH(4, "Your Brain on Fire", "S31_brain_city", 4), "Part Four. Your Brain on Fire."),
    (S("S31_brain_city", (1.0, 1.35, .5, .5, .5, .45), citylights=True, sfx=["power_on"], kw=["lights up", "city at night"]),
     "The moment you see someone attractive, your brain lights up like a city at night."),
    (S("S32_hypothalamus", (1.0, 1.45, .5, .5, .5, .55), labels=[("HYPOTHALAMUS", .5, .4, 0, .6, Y)], blink=True, sfx=["buttons"], kw=["hypothalamus", "signal"]),
     "Deep inside, a small region called the hypothalamus sends a signal to your body."),
    (S("S33_heart_race", (1.0, 1.25, .5, .5, .5, .42), pulse=(.5, .38, .16, 2.6), ekg=True, sfx=["heartbeat_fast"], kw=["heart beats faster", "blood pressure"]),
     "Your heart beats faster. Your blood pressure rises."),
    (S("S02_eye_closeup", (1.3, 2.0, .5, .5, .5, .5), pulse=(.5, .5, .2, 0.5), sfx=["shimmer"], kw=["pupils widen"]),
     "Your pupils widen to let in more light, so you can see the person better."),
    (S("S34_dopamine_rain", (1.0, 1.3, .5, .3, .5, .5), rain=True, labels=[("DOPAMINE", .5, .55, 0, .8, Y)], sfx=["dopamine"], mood=5, kw=["dopamine"]),
     "At the same time, your brain releases a chemical called dopamine."),
    (S("S35_reward_icons", (1.0, 1.15, .5, .5, .5, .5),
       hilite=[(.2, .36, 1), (.5, .36, 1), (.78, .36, 1)],
       labels=[("THE MOLECULE OF WANTING", .5, .06, 0, .3, Y)], nopoint=True, sfx=["reward3"], kw=["wanting", "delicious", "win a game", "notification", "want more"]),
     "Dopamine is the molecule of wanting. It is the same chemical that is released when you eat something delicious, win a game, or get a notification on your phone. It does not make you happy, exactly. It makes you want more."),
    (S("S34_dopamine_rain", (1.5, 1.2, .5, .55, .5, .5), rain=True, labels=[("REWARD!", .5, .5, 1, .3, M)], sfx=["dopamine"], kw=["pull", "reward"]),
     "This is why attraction feels like a pull. Your brain has flagged this person as a reward, and it wants you to go after that reward."),
    (S("S36_brain_scan", (1.0, 1.35, .6, .5, .62, .55), scanpulse=(.61, .6), sfx=["scan", "riser"], kw=["even more intense", "addictive drugs", "photo of their partner"]),
     "If the attraction grows into something stronger, the brain chemistry becomes even more intense. Brain scans of people who are newly in love show something remarkable. The same reward circuits that are activated by addictive drugs light up when they look at a photo of their partner."),
    (S("S37_overthinking", (1.0, 1.3, .4, .45, .35, .4), labels=[("SEROTONIN  ↓", .7, .2, 0, .5, C)], nopoint=True, bubbles=(.33, .25), phone=(.46, .64), sfx=["notify"], kw=["serotonin", "obsessive thinking", "cannot stop thinking", "again and again"]),
     "Meanwhile, levels of a chemical called serotonin can drop. Low serotonin is linked to obsessive thinking. That is why, when you fall for someone, you cannot stop thinking about them. You replay every conversation. You check your phone again and again."),
    (S("S38_rose_glasses", (1.6, 1.9, .82, .78, .85, .8), zzz=(.85, .74), labels=[("THE CRITIC", .85, .9, 0, .8, C)], sfx=["snore"], kw=["careful judgment", "switches off the critic"]),
     "And the part of the brain responsible for careful judgment and criticism becomes quieter. In other words, your brain partly switches off the critic."),
    (S("S38_rose_glasses", (1.2, 1.55, .4, .5, .37, .45), pulse=(.36, .45, .15, .8), sparks=(.36, .45), labels=[("VERY STRONG GLASSES", .36, .45, 1, .3, M)], sfx=["sparkle"], kw=["not blind", "very strong glasses"]),
     "Love is not blind. But in the beginning, it does wear very strong glasses."),

    # ------------------------------------------------------------ PART 5
    (CH(5, "From Spark to Bond", "S39_fire_to_campfire", 5), "Part Five. From Spark to Bond."),
    (S("S39_fire_to_campfire", (1.5, 1.7, .25, .5, .22, .45), fire=(.2, .5), embers=(.2, .5), shake=.08, sfx=["fire_big"], kw=["cannot burn forever", "exhausted", "eat, sleep, and work"]),
     "Here is a problem. That fire cannot burn forever. A brain flooded with dopamine and obsession would be exhausted. You still need to eat, sleep, and work."),
    (S("S39_fire_to_campfire", (1.5, 1.5, .25, .5, .72, .55), fire=(.72, .55), sfx=["fire"], kw=["chemistry changes", "calms down", "two new chemicals"]),
     "So over months, the chemistry changes. The wild excitement slowly calms down. And if the relationship continues, two new chemicals take center stage."),
    (S("S40_oxytocin_hug", (1.0, 1.35, .5, .5, .5, .45), hearts=True, labels=[("OXYTOCIN", .5, .1, 0, .6, M)], nopoint=True, sfx=["warm"], mood=6, kw=["oxytocin", "cuddle hormone", "trust", "safety"]),
     "The first is oxytocin, sometimes called the cuddle hormone. It is released when people hug, hold hands, or spend close time together. It builds trust and a feeling of safety."),
    (S("S41_prairie_voles", (1.0, 1.35, .5, .55, .5, .5), labels=[("VASOPRESSIN", .5, .1, 0, .6, C), ("PRAIRIE VOLES", .5, .64, 1, 0, Y)], nopoint=True, pulse=(.47, .28, .1, 1.0), sfx=["nature"], kw=["vasopressin", "prairie voles", "long lasting bonds", "did not form"]),
     "The second is vasopressin, which is especially important in males. In studies with small rodents called prairie voles, vasopressin helps males form long lasting bonds with a single partner. When scientists blocked it, the bond did not form."),
    (S("S39_fire_to_campfire", (1.0, 1.08, .5, .5, .5, .5), fire=(.72, .55),
       labels=[("THE SPARK", .25, .74, 2, 0, M), ("THE BOND", .72, .76, 3, 0, Y)], nopoint=True, sfx=["fire"], kw=["spark", "fire that keeps you warm"]),
     "In humans, the picture is more complicated. But the idea is similar. Attraction is the spark. Bonding is the fire that keeps you warm for years."),
    (S("S42_family", (1.0, 1.3, .5, .5, .5, .55), shield=True, pulse=(.5, .75, .08, .8), sfx=["warm", "chime"], kw=["helpless", "two caring parents", "built them to stay"]),
     "And there is a good evolutionary reason for this. Human babies are incredibly helpless. They need years of care. For our ancestors, children with two caring parents had a better chance of survival. So evolution did not just build men to be attracted to women. It also built them to stay."),

    # ------------------------------------------------------------ PART 6
    (CH(6, "It Is Not Only Biology", "S43_history_beauty", 6), "Part Six. It Is Not Only Biology."),
    (S("S14_genes_puppet", (1.0, 1.3, .5, .5, .5, .3), sfx=["robot"], kw=["just a program", "executed by chemicals"]),
     "At this point, you might think attraction is just a program. A set of instructions written in your genes and executed by chemicals."),
    (S("S49_diversity", (1.3, 1.0, .5, .5, .5, .5), sfx=["swell"], kw=["only half the story", "exactly the same people", "clearly not true"]),
     "But that is only half the story. Because if attraction were purely biological, everyone would be attracted to exactly the same people. And that is clearly not true."),
    (S("S43_history_beauty", (1.0, 1.15, .5, .5, .5, .5),
       labels=[("ANCIENT EGYPT", .14, .72, 0, 0, Y), ("RENAISSANCE", .38, .72, 0, .5, M), ("1920s", .62, .72, 0, 1.0, C), ("TODAY", .87, .72, 0, 1.5, O)], nopoint=True,
       sfx=["pop4"], kw=["Beauty standards", "fuller body", "thinness"]),
     "Beauty standards change dramatically across cultures and across history. In some times and places, a fuller body was a sign of wealth and good food. In others, thinness became the ideal."),
    (S("S44_media", (1.0, 1.25, .5, .5, .5, .55), screens=True, sfx=["notify"], kw=["Fashion, media"]),
     "Fashion, media, and the people around you constantly shape what you find attractive."),
    (S("S45_classmates", (1.0, 1.25, .5, .55, .5, .55), labels=[("MERE EXPOSURE EFFECT", .5, .1, 1, .3, Y)], nopoint=True, sunrays=True, sfx=["school"], kw=["familiarity", "mere exposure effect", "classmate", "Being close matters"]),
     "Then there is familiarity. Psychologists call it the mere exposure effect. The more often you see someone, the more you tend to like them. This is why so many people fall for a classmate, a neighbor, or a coworker. Being close matters."),
    (S("S46_world_survey", (1.0, 1.25, .5, .5, .5, .5), spinglobe=True,
       labels=[("#1  KINDNESS", .18, .55, 3, 0, M), ("#2  INTELLIGENCE", .82, .55, 3, .6, Y)], nopoint=True, sfx=["ping3"], kw=["personality", "not looks or money", "kindness and intelligence"]),
     "And then there is personality. In large studies across dozens of countries, when people were asked what they want most in a long term partner, the top answers were not looks or money. They were kindness and intelligence."),
    (S("S47_kindness", (1.0, 1.3, .45, .5, .4, .5), sparks=(.35, .55), sfx=["sparkle"], kw=["smile", "sense of humor", "treats a stranger", "more attractive over time"]),
     "A smile, a sense of humor, a warm voice, the way someone treats a stranger. These things can make a person more attractive over time, even if they did not stand out at first glance."),
    (S("S48_two_forces", (1.0, 1.15, .5, .5, .5, .5), pulse=(.52, .45, .14, 1.0),
       labels=[("BIOLOGY", .17, .76, 1, 0, C), ("CULTURE", .83, .76, 2, 0, O)], nopoint=True, sfx=["swell"], kw=["two forces", "Ancient biology", "culture"]),
     "So attraction is a conversation between two forces. Ancient biology on one side. Your personal life and culture on the other."),

    # ------------------------------------------------------------ PART 7
    (CH(7, "You Are Not a Robot", "S50_choice_brain", 7), "Part Seven. You Are Not a Robot."),
    (S("S20_average_face", (1.6, 1.0, .5, .5, .5, .5), labels=[("AVERAGES, NOT RULES", .5, .1, 2, 0, Y)], nopoint=True, sfx=["swell"], kw=["averages", "not rules"]),
     "It is also important to remember that these are averages. Patterns across thousands of people. They are not rules for any single person."),
    (S("S49_diversity", (1.0, 1.25, .5, .5, .5, .5), hearts=True, sfx=["warm"], kw=["wonderfully diverse", "checklist"]),
     "Humans are wonderfully diverse. Some men are attracted to men. Some people feel little attraction at all. Many people find themselves drawn to someone who does not match any checklist."),
    (S("S50_choice_brain", (1.0, 1.35, .5, .5, .5, .6), pathglow=True, sfx=["magic"], kw=["tendencies, not orders", "choose", "reflect", "love"]),
     "Evolution gave us tendencies, not orders. And our big, complex brains allow us to choose, to reflect, and to love in ways that go far beyond our genes."),
    (S("S52_billion_years", (1.4, 1.0, .5, .5, .5, .5), spin=True, sfx=["swell"], mood=7, kw=["fascinating", "billion years", "single moment"]),
     "That is what makes human attraction so fascinating. It is the meeting point of a billion years of evolution and a single moment in your own life."),

    # ------------------------------------------------------------ EPILOGUE
    (CH(8, "Epilogue", "S51_street_return", 7), "Epilogue."),
    (S("S01_street", (1.0, 1.3, .5, .5, .47, .6), sfx=["city"], kw=["that street", "Hundreds of faces"]),
     "So let us go back to that street. Hundreds of faces pass you by."),
    (S("S51_street_return", (1.2, 1.45, .5, .5, .5, .5), sparks=(.5, .45), sfx=["heartbeat", "swell"], kw=["stops you"]),
     "And then one of them stops you."),
    (S("S02_eye_closeup", (1.0, 1.4, .5, .5, .5, .5), pulse=(.5, .5, .2, .9), sfx=["shimmer"], kw=["hormones and genes"]),
     "In that one second, your eyes read a face built by hormones and genes."),
    (S("S20_average_face", (1.0, 1.3, .5, .5, .5, .5), swirl=True, sfx=["magic"], kw=["millions of faces"]),
     "Your brain compares it to millions of faces you have seen before."),
    (S("S30_senses_to_brain", (1.2, 1.05, .35, .55, .5, .5), flow=True, sfx=["stream"], kw=["ears", "nose"]),
     "Your ears and your nose collect clues you will never notice."),
    (S("S34_dopamine_rain", (1.0, 1.3, .5, .5, .5, .45), rain=True, pulse=(.5, .5, .2, 2.4), sfx=["dopamine", "heartbeat"], kw=["Dopamine", "heart"]),
     "Dopamine floods your reward system. Your heart beats a little faster."),
    (S("S52_billion_years", (1.0, 1.6, .5, .5, .5, .5), spin=True, sfx=["swell"], kw=["ancient story", "in an instant"]),
     "An ancient story, written over a billion years, plays out inside you in an instant."),
    (S("S51_street_return", (1.5, 1.2, .5, .5, .5, .5), sfx=["pad"], kw=["not written in your genes"]),
     "But what happens next is not written in your genes."),
    (S("S53_hello", (1.0, 1.2, .62, .5, .62, .45), wave=(.48, .45), sfx=["pop3"], kw=["smile", "say hello", "walk away"]),
     "Do you smile? Do you say hello? Do you walk away?"),
    (S("S51_street_return", (1.0, 1.4, .5, .5, .5, .5), sparks=(.5, .45), big=("THAT PART IS UP TO YOU.", "", 0), sfx=["final"], kw=["up to you"]),
     "That part is up to you."),
    (S("S54_endcard_bg", (1.0, 1.05, .5, .5, .5, .5), endcard=True, sfx=["boom"]), ""),
]

SHOTS = [(spec, split(text)) for spec, text in RAW]

if __name__ == "__main__":
    n = sum(len(s) for _, s in SHOTS)
    print(len(SHOTS), "shots,", n, "sentences")
