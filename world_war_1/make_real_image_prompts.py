"""Prompts for realistic / archival-style images to mix into the WWI animation.

Each entry: (cue line in narration.txt, type, how to use it in the edit, scene).
Timestamps are estimated at 141 words per minute (the pace of the previous
voiceover); check the cue against the real audio.
Usage: python3 make_real_image_prompts.py -> real_image_prompts.txt
"""
WPM = 141

STYLES = {
    "PHOTO": "authentic 1914-1918 black and white archival war photograph, warm sepia tone, heavy film grain, "
             "slight blur, dust and scratches, realistic, documentary, 16:9, no text, no watermark",
    "COLOUR": "early colour autochrome photograph from 1914-1918, soft muted pastel colours, grainy, slightly "
              "faded, realistic, documentary, 16:9, no text, no watermark",
    "PORTRAIT": "formal studio portrait photograph from the 1910s, black and white with sepia tone, film grain, "
                "chest-up, subject centred with plain dark background and empty space on both sides, realistic, "
                "16:9, no text, no watermark",
    "MAP": "vintage 1914 hand-painted map on aged parchment, muted watercolour colours, ink coastlines, "
           "decorative compass rose, top-down flat view, no text, no labels, no letters, 16:9",
    "STILL": "photorealistic still life, dramatic low-key lighting, shallow depth of field, cinematic, "
             "16:9, no readable text, no watermark",
    "TODAY": "modern photorealistic colour photograph, cinematic golden-hour light, high detail, 16:9, "
             "no text, no watermark",
}

USE = {
    "FULL": "Full screen, slow Ken Burns zoom 5-7 s, crossfade in/out",
    "FRAME": "Inside the cartoon scene as an old photo print (white border, slight tilt, tape), 4-5 s",
    "MAP": "Full screen base map; animate labels, arrows and colours on top in the edit, 6-10 s",
    "SPLIT": "Left/right half of screen next to the cartoon character, 4-6 s",
    "OUTRO": "Full screen, very slow zoom out, long crossfade",
}

I = [
    # ------------------------------------------------------------- Sarajevo
    ("Sarajevo. The twenty-eighth of June, 1914.", "PHOTO", "FULL",
     "Sarajevo street along a narrow river in 1914, Austro-Hungarian era stone buildings, an old stone bridge, "
     "crowds lining the pavement, flags hanging from windows, sunny summer morning"),
    ("Inside sits Archduke Franz Ferdinand", "PHOTO", "FRAME",
     "A heavyset Austrian archduke with an upturned waxed moustache, wearing a light blue general's tunic and a "
     "plumed helmet, sitting with his wife in a white dress and wide hat in the back of an open-top 1910 touring "
     "car, crowd behind"),
    ("a nineteen-year-old student named Gavrilo Princip", "PORTRAIT", "SPLIT",
     "Thin, gaunt nineteen-year-old Bosnian Serb student with dark wavy hair and intense dark eyes, wearing a "
     "dark suit and white collar"),
    ("Within minutes, the Archduke and his wife are dead.", "PHOTO", "FULL",
     "Chaotic street scene in 1914, policemen and men in bowler hats seizing a young man in a dark suit, crowd "
     "pushing, motion blur"),
    ("Those two bullets would start a war", "STILL", "FULL",
     "An early 1900s semi-automatic pocket pistol and two brass bullet cartridges lying on an old wooden table, "
     "single beam of light, dust in the air"),
    # ------------------------------------------------------------- Europe 1914
    ("To understand how two bullets could set the world on fire", "MAP", "MAP",
     "Map of Europe in 1914 showing all countries, Britain, France and Russia tinted soft green, Germany and "
     "Austria-Hungary tinted soft brown, other countries pale grey"),
    ("Cities glowed with electric light.", "COLOUR", "FULL",
     "A grand Paris boulevard around 1913 at dusk, glowing electric street lamps, horse carriages and early "
     "motor cars, people in long coats and hats"),
    ("Britain had the largest navy", "PHOTO", "FULL",
     "A huge grey British dreadnought battleship steaming at sea in 1914, big gun turrets, smoke from two "
     "funnels, waves at the bow"),
    ("Germany, a young and ambitious nation", "PORTRAIT", "SPLIT",
     "German Kaiser Wilhelm II, upturned pointed moustache, wearing a spiked Pickelhaube helmet and a military "
     "uniform covered in medals, proud stern expression"),
    ("On one side stood the Triple Entente", "MAP", "MAP",
     "Map of Europe 1914 with two clearly separated alliance blocs, France, Britain and Russia in green on the "
     "west and east, Germany and Austria-Hungary in brown in the centre, surrounded"),
    ("On the twenty-third of July, Austria sent Serbia an ultimatum", "STILL", "FULL",
     "An official 1914 diplomatic document with a red wax seal, a fountain pen and an inkwell on a dark "
     "wooden desk, the writing blurred and unreadable"),
    ("Russia began to mobilise its huge army", "PHOTO", "FULL",
     "Russian soldiers in long greatcoats and peaked caps crowding onto a steam train at a city station in "
     "1914, families waving goodbye"),
    ("Years earlier, its generals had prepared a solution: the Schlieffen Plan.", "MAP", "MAP",
     "Map of Belgium, northern France and western Germany in 1914, a huge sweeping arc of thick red arrows "
     "curving from Germany through Belgium down towards Paris"),
    ("On the fourth of August, German troops crossed into Belgium.", "PHOTO", "FULL",
     "Long column of German infantry in grey uniforms and spiked Pickelhaube helmets marching through a "
     "cobbled Belgian town square, onlookers in doorways"),
    ("a scrap of paper", "STILL", "FRAME",
     "An old yellowed nineteenth-century treaty page with signatures and a cracked wax seal, edges torn"),
    # ------------------------------------------------------------- enthusiasm
    ("Across Europe, crowds cheered.", "PHOTO", "FULL",
     "Huge cheering crowd of men in straw boater hats and caps waving hats in a city square in August 1914, "
     "national flags"),
    ("young men rushed to sign up", "PHOTO", "FRAME",
     "Long queue of eager young men in caps and suits outside a London army recruiting office in 1914, "
     "smiling, a policeman nearby"),
    # ------------------------------------------------------------- 1914 battles
    ("The Belgian fortresses were pounded by enormous siege guns.", "PHOTO", "FULL",
     "An enormous German siege howitzer firing, giant barrel tilted up, gun crew covering their ears, huge "
     "cloud of smoke"),
    ("Refugees fled down every road.", "PHOTO", "FULL",
     "Belgian refugee families in 1914 walking along a country road with handcarts piled with belongings, "
     "children and old people"),
    ("in bright blue coats and red trousers", "COLOUR", "SPLIT",
     "French infantry soldiers of 1914 in dark blue greatcoats, bright red trousers and red kepis, holding "
     "long rifles with bayonets, standing in a field"),
    ("commandeered Paris taxis", "PHOTO", "FULL",
     "A long line of 1910s Renault taxicabs parked along a road outside Paris at night, French soldiers "
     "climbing in"),
    ("By the end of 1914, a continuous line of trenches", "MAP", "MAP",
     "Map of western Europe with a single thick jagged dark red line running from the Belgian coast through "
     "northern France to the Swiss border"),
    # ------------------------------------------------------------- trenches
    ("Life in the trenches was a nightmare.", "PHOTO", "FULL",
     "British soldiers in a deep muddy trench, sandbag walls, wooden duckboards in water, tired faces, "
     "rifles leaning on the parapet"),
    ("Between the two lines of trenches lay a strip of ground called No Man's Land.", "PHOTO", "FULL",
     "Desolate No Man's Land, tangled barbed wire, water-filled shell craters, shattered tree stumps, grey "
     "sky"),
    ("To cross it meant facing machine guns", "PHOTO", "FRAME",
     "Two soldiers operating a water-cooled heavy machine gun on a tripod behind sandbags in a trench"),
    ("It became known as the Christmas Truce.", "PHOTO", "FULL",
     "British and German soldiers standing together in a frosty field in winter 1914, smiling, shaking "
     "hands and swapping cigarettes, trenches in the background"),
    # ------------------------------------------------------------- eastern front / world
    ("But at the Battle of Tannenberg", "PHOTO", "SPLIT",
     "Two German generals studying a map on a table: an older broad-shouldered general with a square head "
     "and a white brushed moustache, and a younger stern general with a small moustache"),
    ("Around ninety thousand Russians were taken prisoner.", "PHOTO", "FULL",
     "Endless column of Russian prisoners of war in long greatcoats marching along a dirt road through "
     "flat countryside"),
    ("The Ottoman Empire joined the Central Powers.", "MAP", "MAP",
     "Vintage world map, Europe, the Middle East and Africa with war zones shaded in soft red, ocean in pale "
     "blue-green"),
    # ------------------------------------------------------------- India
    ("But the largest volunteer army of all came from India.", "PHOTO", "FULL",
     "Indian infantry of 1914 marching through a French village street, Sikh and Punjabi soldiers in khaki "
     "uniforms and turbans with rifles, French villagers watching"),
    ("The first went to Khudadad Khan", "PORTRAIT", "SPLIT",
     "Proud Indian Muslim soldier of 1914 in a khaki uniform and khaki turban, neat moustache, a bronze "
     "cross medal on his chest"),
    ("Today many of their names are carved on the India Gate", "TODAY", "FULL",
     "India Gate war memorial arch in New Delhi at dusk, warm lights, an eternal flame, people walking on the "
     "lawns"),
    # ------------------------------------------------------------- 1915
    ("a strange greenish-yellow cloud", "COLOUR", "FULL",
     "A low greenish-yellow poison gas cloud rolling across a battlefield towards trenches, eerie light"),
    ("Gas masks became part of every soldier's equipment.", "PHOTO", "FRAME",
     "Soldiers in a trench wearing early First World War gas hoods with round glass eyepieces, holding rifles"),
    ("A young politician named Winston Churchill", "PORTRAIT", "SPLIT",
     "Winston Churchill aged forty in 1915, round face, receding hair, dark three-piece suit with a bow "
     "tie, confident determined look"),
    ("landed on the Gallipoli peninsula", "PHOTO", "FULL",
     "Australian and New Zealand soldiers jumping from rowing boats onto a narrow beach under steep scrubby "
     "cliffs, dawn, warships offshore"),
    ("led by a determined officer named Mustafa Kemal", "PORTRAIT", "SPLIT",
     "Ottoman officer Mustafa Kemal in 1915, slim face, sharp light eyes, neat moustache, wearing a fur "
     "kalpak hat and military uniform"),
    ("torpedoed the British ocean liner Lusitania", "PHOTO", "FULL",
     "The four-funnelled ocean liner Lusitania at sea in 1915, dark hull, smoke trailing, calm grey sea"),
    # ------------------------------------------------------------- 1916
    ("In February, Germany attacked the French fortress city of Verdun.", "PHOTO", "FULL",
     "Aerial view of the Verdun battlefield in 1916, a moonscape of overlapping shell craters, no trees "
     "left, ruined fort outline"),
    ("The French vowed: \"They shall not pass.\"", "COLOUR", "SPLIT",
     "French soldiers of 1916 in horizon-blue uniforms and steel Adrian helmets holding a trench line, "
     "determined faces"),
    ("For a week, British guns fired", "PHOTO", "FULL",
     "A row of British artillery guns firing at night, bright muzzle flashes lighting up the gun crews"),
    ("whistles blew along the British trenches", "PHOTO", "FULL",
     "British soldiers climbing wooden ladders out of a trench and going over the top into smoke, officer "
     "with a whistle"),
    ("The name stuck. The tank had been born.", "PHOTO", "FULL",
     "A British Mark I rhomboid tank with caterpillar tracks crossing a muddy trench in 1916, soldiers "
     "watching"),
    ("General Aleksei Brusilov", "PORTRAIT", "SPLIT",
     "Russian general Aleksei Brusilov, slim face, neat grey moustache, Russian general's uniform with "
     "epaulettes and medals"),
    ("They called him the Red Baron.", "PORTRAIT", "SPLIT",
     "Young German fighter pilot Manfred von Richthofen, clean-shaven, leather flying coat, a blue cross "
     "medal at the collar"),
    ("He shot down eighty enemy aircraft", "COLOUR", "FULL",
     "A bright red Fokker triplane fighter plane flying through clouds in 1918, another biplane in the "
     "distance"),
    ("at the Battle of Jutland in the North Sea.", "PHOTO", "FULL",
     "Line of grey battleships firing broadsides at sea, huge smoke clouds, splashes of shells in the water"),
    # ------------------------------------------------------------- home front
    ("With millions of men at the front, women took their places.", "PHOTO", "FULL",
     "Women munitions workers in long dresses, caps and aprons working among rows of artillery shells in a "
     "large factory"),
    ("\"Your country needs you.\"", "STILL", "SPLIT",
     "A First World War British recruitment poster: a stern officer with a large moustache and peaked cap "
     "pointing his finger straight at the viewer, cream background, leave empty space for text"),
    ("\"turnip winter.\"", "PHOTO", "FRAME",
     "Hungry German women and children queuing with baskets outside a food shop in winter 1916"),
    # ------------------------------------------------------------- 1917
    ("Tsar Nicholas the Second was forced to abdicate.", "PORTRAIT", "SPLIT",
     "Tsar Nicholas II of Russia, short neat brown beard and moustache, Russian army tunic, calm sad eyes"),
    ("His name was Vladimir Lenin.", "PHOTO", "FULL",
     "Vladimir Lenin in 1917, bald with a goatee beard, coat and cap in hand, passionately addressing a "
     "crowd of workers and soldiers from a platform"),
    ("in the Treaty of Brest-Litovsk.", "PHOTO", "FRAME",
     "German and Russian delegates in uniforms and suits seated around a long table signing a treaty in 1918"),
    ("Its soldiers fought in the high mountains of the Alps", "PHOTO", "FULL",
     "Italian Alpine soldiers with feathered hats and rifles climbing a snowy mountain ridge on ropes, "
     "dramatic peaks"),
    ("He became a legend: Lawrence of Arabia.", "PORTRAIT", "SPLIT",
     "T. E. Lawrence, slim clean-shaven young British officer wearing flowing white Arab robes and a white "
     "headdress with a gold agal, desert light"),
    ("they captured the port of Aqaba", "COLOUR", "FULL",
     "Arab fighters on camels charging across a desert towards a small coastal town by a blue sea, dust "
     "clouds"),
    ("captured Jerusalem in December 1917", "PHOTO", "FULL",
     "British and Indian soldiers marching through the old stone Jaffa Gate of Jerusalem in 1917, crowds "
     "watching"),
    ("the Zimmermann Telegram.", "STILL", "FRAME",
     "An old 1917 telegram covered in rows of coded numbers, a magnifying glass and a pencil lying on it"),
    ("the United States declared war on Germany.", "PORTRAIT", "SPLIT",
     "US President Woodrow Wilson in 1917, thin face, rimless glasses, dark suit, serious expression"),
    ("ship its soldiers across the Atlantic.", "PHOTO", "FULL",
     "Crowded deck of a troopship packed with young American soldiers in campaign hats waving, 1917"),
    ("Passchendaele.", "PHOTO", "FULL",
     "Soldiers walking in single file along wooden duckboards across a flooded sea of mud and craters, "
     "broken tree stumps, grey sky"),
    # ------------------------------------------------------------- 1918
    ("specially trained \"stormtroopers\"", "PHOTO", "FULL",
     "German stormtroopers in coal-scuttle steel helmets carrying stick grenades running through smoke and "
     "barbed wire"),
    ("They shelled Paris with a giant long-range gun", "PHOTO", "FULL",
     "An enormously long railway gun barrel pointing at the sky in a forest, tiny soldiers beside it"),
    ("And the Americans were now arriving.", "PHOTO", "FULL",
     "American soldiers marching through a French town with the US flag, cheering French civilians in 1918"),
    ("the Allies struck back near Amiens", "PHOTO", "FULL",
     "Allied Mark V tanks and infantry advancing together across an open field in 1918, biplanes overhead"),
    ("Their last hope was a pigeon named Cher Ami.", "STILL", "SPLIT",
     "A brave grey homing pigeon with one injured leg and a small metal message capsule, perched on a "
     "wooden crate, soft light"),
    ("in a railway carriage parked in a forest near Compi", "PHOTO", "FULL",
     "An old wooden railway dining carriage standing on tracks in a quiet autumn forest clearing in 1918, "
     "officers standing outside"),
    ("an American soldier named Henry Gunther", "PORTRAIT", "SPLIT",
     "Young American soldier of 1918, round face, wearing a flat steel helmet and olive drab uniform"),
    ("One minute later, the guns fell silent.", "PHOTO", "FULL",
     "Exhausted soldiers in a trench cheering and raising their helmets in the air on 11 November 1918"),
    ("In London, Paris and New York, huge crowds celebrated", "PHOTO", "FULL",
     "Huge joyful crowd filling a London square on Armistice Day 1918, people on top of buses, waving flags "
     "and hats"),
    # ------------------------------------------------------------- aftermath
    ("\"shell shock,\"", "PHOTO", "FRAME",
     "Wounded soldiers in a long hospital ward with iron beds, nurses in white uniforms and caps caring for "
     "them"),
    ("The Spanish flu pandemic of 1918", "PHOTO", "FULL",
     "An emergency hospital hall in 1918 filled with rows of cots, nurses wearing white gauze masks"),
    ("Four great empires had collapsed.", "MAP", "MAP",
     "Map of Europe and the Middle East in 1919 with many newly drawn borders, each new country a different "
     "soft colour"),
    ("The Treaty of Versailles was signed", "PHOTO", "FULL",
     "The Hall of Mirrors at the Palace of Versailles in 1919, packed with statesmen in suits around a "
     "signing table, chandeliers and mirrors"),
    ("Among the bitter veterans was a former corporal", "PHOTO", "FRAME",
     "Small group of German First World War soldiers posing in field uniforms, one corporal with a large "
     "bushy moustache sitting at the side"),
    ("they wear red poppies", "TODAY", "FULL",
     "A field of bright red poppies in Flanders swaying in the wind, white war grave crosses in the "
     "background"),
    ("A Canadian doctor, John McCrae", "PORTRAIT", "SPLIT",
     "Canadian army doctor John McCrae in 1915, moustache, military officer's uniform with peaked cap"),
    ("millions of crosses, row on row", "TODAY", "FULL",
     "Huge First World War cemetery with endless rows of white headstones on green grass, sunset, aerial "
     "view"),
    ("This was the First World War.", "TODAY", "OUTRO",
     "The Menin Gate memorial in Ypres at night, warm light on the stone arch, names carved on the walls, "
     "a few poppy wreaths"),
]


def main():
    text = open("narration.txt", encoding="utf-8").read()
    out = ["WORLD WAR I - REAL / ARCHIVAL IMAGE PROMPTS (to mix with the animation)",
           f"{len(I)} images. Times estimated at {WPM} words/min - match the cue line to your audio.", ""]
    out.append("STYLE BLOCKS (already added to the end of each prompt below):")
    for k, v in STYLES.items():
        out.append(f"  [{k}] {v}")
    out.append("")
    out.append("HOW TO USE IN THE EDIT:")
    for k, v in USE.items():
        out.append(f"  {k}: {v}")
    out.append("")
    for n, (cue, typ, use, scene) in enumerate(I, 1):
        pos = text.find(cue)
        if pos < 0:
            raise SystemExit(f"cue not found: {cue!r}")
        sec = round(len(text[:pos].split()) / WPM * 60)
        out.append(f"{n:02d} | {sec // 60:02d}:{sec % 60:02d} | {typ} | USE: {use} | Cue: \"{cue}\"")
        out.append(f"{scene}. {STYLES[typ]}")
        out.append("")
    open("real_image_prompts.txt", "w", encoding="utf-8").write("\n".join(out))
    print(len(I), "prompts")


if __name__ == "__main__":
    main()
