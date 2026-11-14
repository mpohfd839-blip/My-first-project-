"""Image prompts for the Russian Revolution video, in the flat stick-figure history-cartoon style.

Each entry is tied to a cue line in narration_part1/2.txt so the images can be synced later.
Usage: python3 make_image_prompts.py -> image_prompts_part1.txt, image_prompts_part2.txt, image_prompts_detailed.txt
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = ("flat 2D cartoon illustration in the style of a simple educational history animation, characters with "
         "thin stick-like arms and legs, small round heads with dot eyes and simple expressions, clean vector "
         "shapes, soft flat colours, minimal uncluttered background, soft shadows, lots of empty space, 16:9, "
         "no text, no letters, no words, no captions")

# fixed character looks, reused in every prompt so they stay consistent
C = {
    "NICHOLAS": "Tsar Nicholas II (thin cartoon man with a neat short brown beard and moustache, dark green military "
                "tunic with gold epaulettes and a light blue sash)",
    "ALEXANDRA": "Tsarina Alexandra (tall thin cartoon woman, auburn hair in a bun, long pale lilac dress, pearl "
                 "necklace, serious face)",
    "ALEXEI": "little Tsarevich Alexei (small cartoon boy in a white sailor suit)",
    "DAUGHTERS": "the four grand duchesses (four cartoon girls in matching long white dresses with big white bows)",
    "RASPUTIN": "Rasputin (tall cartoon monk with long greasy black hair parted in the middle, long black beard, wild "
                "staring eyes, black robe, big cross on a chain)",
    "LENIN": "Lenin (short cartoon man with a bald head, red-brown goatee beard and moustache, dark three-piece suit)",
    "TROTSKY": "Trotsky (thin cartoon man with wild black curly hair, round glasses, small goatee, black leather "
               "jacket)",
    "KERENSKY": "Kerensky (cartoon man with short crew-cut hair and a plain khaki military-style jacket, dramatic pose)",
    "STALIN": "Stalin (cartoon man with a thick black moustache, swept-back black hair and a plain grey military "
              "tunic)",
    "GAPON": "Father Gapon (cartoon priest with a black beard, black robe and a cross)",
    "STOLYPIN": "Stolypin (cartoon man with a bald head, big dark beard and a black frock coat)",
    "YUSUPOV": "Prince Yusupov (slim elegant cartoon young man with slicked-back hair and a fine suit)",
    "PEASANTS": "Russian peasants (cartoon people in rough linen shirts with rope belts and bast shoes, women in "
                "headscarves)",
    "WORKERS": "factory workers (cartoon men in dark flat caps and grimy shirts)",
    "SOLDIERS": "Russian soldiers (cartoon men in khaki tunics and peaked caps with rifles)",
    "REDGUARDS": "Red Guards (cartoon workers with red armbands and rifles)",
    "REDARMY": "Red Army soldiers (cartoon men in long grey coats and pointed cloth helmets with a red star)",
    "WHITES": "White Army officers (cartoon officers in neat dark-green uniforms with gold shoulder boards)",
    "SAILORS": "revolutionary sailors (cartoon sailors in striped shirts, round black caps and ammunition belts)",
    "CHEKA": "Cheka agents (cartoon men in long black leather coats and caps)",
    "GERMANS": "German officers (cartoon officers in grey uniforms and spiked helmets)",
}


def P(text):
    for k, v in C.items():
        text = text.replace(k, v)
    return text


PART1 = [
    # ---------------------------------------------------------------- cold open
    ("Yekaterinburg, Russia. The night of the sixteenth of July, 1918.",
     "exterior of a large two-storey merchant house at night with whitewashed windows, a tall wooden fence, one "
     "guard silhouette at the gate, dark blue sky with stars"),
    ("It is past midnight.", "a dim bedroom at night, a guard with a lantern in the doorway waking a sleepy family"),
    ("There is fighting nearby", "a guard pointing down a staircase while NICHOLAS and ALEXANDRA get dressed nervously"),
    ("A father carries his sick thirteen-year-old son", "NICHOLAS carrying ALEXEI down a narrow wooden staircase by "
                                                        "lantern light"),
    ("His wife follows.", "ALEXANDRA, DAUGHTERS, a doctor with round glasses and a maid walking down the stairs in a "
                          "line"),
    ("They are told to wait.", "a bare basement room with faded striped wallpaper, two wooden chairs, the royal family "
                               "standing and waiting under a single dim light bulb"),
    ("The father is a quiet, polite man", "close-up of NICHOLAS looking calm and tired"),
    ("Just eighteen months earlier, he ruled one-sixth", "simple world map with the huge Russian Empire glowing gold"),
    ("He commanded the largest army in the world.", "NICHOLAS on a white horse reviewing endless rows of saluting "
                                                    "SOLDIERS"),
    ("More than a hundred and seventy million people", "a huge crowd of PEASANTS bowing to a giant golden portrait "
                                                        "of the Tsar"),
    ("Tsar Nicholas the Second, the last Emperor of Russia.", "NICHOLAS on a golden throne wearing a jewelled crown, "
                                                              "red double-headed eagle banners behind"),
    ("And the men who are about to walk into that basement", "long dark shadows of several men falling across a "
                                                              "basement door, ominous mood"),
    ("How did the most powerful monarch", "split image: NICHOLAS on a golden throne on the left, NICHOLAS sitting in "
                                           "a bare basement on the right"),
    ("How did a country of peasants and priests", "a village with an onion-domed church and PEASANTS, slowly turning "
                                                  "into a crowd waving red flags"),
    ("This is the story of the Russian Revolution.", "a big red flag waving over the Winter Palace in St Petersburg "
                                                      "at sunset, empty sky for a title"),
    # ---------------------------------------------------------------- empire
    ("To understand how it happened", "an old clock with its hands spinning backwards, sepia tones"),
    ("The Romanov family had ruled Russia since 1613.", "a palace wall covered with oval portraits of crowned "
                                                        "cartoon tsars, gold frames"),
    ("He was believed to be chosen by God.", "NICHOLAS standing in a beam of golden light from the sky, priests "
                                             "bowing around him"),
    ("There was no parliament", "an empty dusty parliament hall with a big padlock and chain on the door"),
    ("Russia was enormous.", "a tiny steam train crossing an endless snowy Siberian plain, little clocks floating in "
                             "the sky showing different times"),
    ("Around eighty percent of the people were peasants.", "a village of wooden huts, PEASANTS ploughing a muddy field "
                                                            "with a thin horse"),
    ("Until 1861, many of them had been serfs", "a fat landlord in a top hat selling a peasant family together with "
                                                "a cow at a market"),
    ("Even after they were freed", "a peasant family inside a tiny wooden hut with a big stove, a candle and an icon "
                                   "in the corner"),
    ("At the very top sat a tiny aristocracy", "a grand ballroom with crystal chandeliers, cartoon aristocrats "
                                               "waltzing in gowns and uniforms"),
    ("speaking French at dinner", "aristocrats at a long banquet table with champagne, roast swan and candelabras"),
    ("In the cities, a new class was growing.", "a red-brick factory with smoking chimneys, a stream of WORKERS "
                                                "walking in through the gates"),
    ("working twelve or fourteen hours a day", "tired WORKERS at big noisy machines, a wall clock showing late night"),
    ("sleeping in crowded barracks", "a cramped dormitory with rows of bunk beds packed with WORKERS"),
    ("They were angry.", "WORKERS secretly reading leaflets by candlelight in a cellar"),
    # ---------------------------------------------------------------- Nicholas
    ("In 1894, a twenty-six-year-old man became Tsar.", "a young NICHOLAS being crowned in a golden cathedral"),
    ("He was gentle, devoted to his family", "NICHOLAS smiling, playing with a small dog in a palace garden"),
    ("He once admitted", "NICHOLAS sitting at a huge desk piled with papers, holding his head in his hands"),
    ("In May 1896, to celebrate his coronation", "a festival field with colourful tents and stalls full of bread "
                                                  "rolls and enamel souvenir cups, flags"),
    ("Hundreds of thousands gathered", "a massive crowd of PEASANTS filling an open field at dawn"),
    ("The crowd surged forward.", "the crowd pushing forward in a cloud of dust toward the stalls, people stumbling "
                                  "into a ditch, panic, non-graphic"),
    ("More than a thousand people died.", "an empty field with scattered caps and enamel cups under a grey sky, sad "
                                          "and quiet"),
    ("That same evening, Nicholas attended a grand ball", "NICHOLAS and ALEXANDRA dancing at an elegant ball with "
                                                          "French flags"),
    # ---------------------------------------------------------------- family
    ("Nicholas married a German princess, Alexandra.", "the wedding of NICHOLAS and ALEXANDRA in a palace chapel, "
                                                       "ALEXANDRA in a white gown"),
    ("Together they had four daughters", "family portrait pose: NICHOLAS, ALEXANDRA and DAUGHTERS"),
    ("But Russia's law said that only a son could inherit", "NICHOLAS staring at a small empty crown on a red "
                                                            "velvet cushion"),
    ("Finally, in 1904, a boy was born.", "palace celebration with cannons firing a salute, NICHOLAS proudly holding "
                                          "a baby"),
    ("Within weeks, the doctors discovered", "worried doctors with stethoscopes around a royal crib"),
    ("A simple fall or bruise", "ALEXEI fallen on the floor holding his bruised knee, ALEXANDRA running to him in "
                                "panic"),
    ("The illness was kept a state secret.", "ALEXANDRA closing heavy palace doors with a finger on her lips"),
    # ---------------------------------------------------------------- Japan
    ("In 1904, Russia went to war with Japan", "simple map of Manchuria and Korea with a Russian flag and a Japanese "
                                               "flag facing each other"),
    ("The Russian court laughed", "NICHOLAS and his generals laughing around a table with cigars"),
    ("The Japanese besieged and captured", "a fortress on a hill above a harbour, Japanese soldiers advancing up the "
                                           "slope"),
    ("Russia then sent its Baltic Fleet", "a line of old grey Russian battleships steaming across the ocean, a dotted "
                                          "route curving around a globe"),
    ("When the fleet finally arrived", "naval battle: Russian battleships sinking in smoke while Japanese ships fire"),
    ("For the first time in modern history", "a Japanese admiral standing proudly on his ship's bridge, rising sun "
                                             "flag"),
    # ---------------------------------------------------------------- Bloody Sunday
    ("On a freezing Sunday in January 1905", "GAPON leading a huge peaceful crowd through a snowy street"),
    ("They carried religious icons", "marchers in the snow holding religious icons and portraits of the Tsar, "
                                     "singing"),
    ("They wanted to hand him a petition", "close-up of a worker's hands holding a rolled-up petition"),
    ("Nicholas was not even in the city.", "NICHOLAS calmly having tea in a quiet country palace"),
    ("As the crowds approached, soldiers opened fire.", "a line of SOLDIERS in front of the Winter Palace with rifle "
                                                        "smoke, the crowd fleeing, non-graphic"),
    ("It became known as Bloody Sunday.", "a fallen icon and a red banner lying in the trampled snow, crows on a "
                                          "lamppost"),
    ("That day, something broke.", "a cracked portrait of NICHOLAS hanging on a peasant hut wall"),
    # ---------------------------------------------------------------- 1905
    ("The year 1905 turned into a revolution.", "WORKERS on strike in front of locked factory gates, red flags"),
    ("Peasants burned their landlords' manor houses.", "a manor house burning at night, PEASANTS with torches"),
    ("the battleship Potemkin", "a battleship at sea with SAILORS raising a red flag on the mast, an officer falling "
                                "into the water with a splash"),
    ("They called it a \"soviet.\"", "WORKERS in a hall raising their hands to vote at a council meeting"),
    ("a brilliant young revolutionary named Leon Trotsky", "a young TROTSKY giving a fiery speech on a small stage"),
    ("Terrified, Nicholas gave in.", "NICHOLAS reluctantly signing a document with a quill"),
    ("called the Duma", "a parliament hall with white columns full of deputies in suits"),
    ("But Nicholas never truly accepted it.", "NICHOLAS locking the parliament doors with a huge key"),
    ("It had only gone underground.", "revolutionaries printing leaflets on a secret printing press in a cellar"),
    # ---------------------------------------------------------------- Rasputin
    ("Meanwhile, inside the palace, the Tsarina was desperate.", "ALEXANDRA crying beside ALEXEI lying in bed"),
    ("Then, around 1907, a strange visitor arrived at court.", "RASPUTIN arriving at the palace gates, the guards "
                                                               "staring at him"),
    ("He was a wandering holy man from Siberia", "full-length RASPUTIN in a palace hall, wild staring eyes"),
    ("He drank heavily.", "RASPUTIN in a tavern laughing and dancing with bottles all around"),
    ("And somehow, when Rasputin prayed beside the boy's bed", "RASPUTIN praying with his hand on ALEXEI's head, a "
                                                               "soft golden glow"),
    ("Perhaps he told the doctors to stop giving aspirin", "RASPUTIN tossing away a medicine bottle while doctors "
                                                           "gasp"),
    ("But to Alexandra, Rasputin was a miracle", "ALEXANDRA kneeling and kissing RASPUTIN's hand"),
    ("To the rest of Russia", "RASPUTIN as a giant puppeteer above the palace, controlling NICHOLAS and ALEXANDRA "
                              "like puppets on strings"),
    # ---------------------------------------------------------------- Stolypin
    ("The Prime Minister, Pyotr Stolypin.", "STOLYPIN sitting at a big desk, stern"),
    ("So many were hanged", "an empty wooden gallows with a row of nooses at a grey dawn, no people"),
    ("But he also tried to give peasants their own land", "STOLYPIN handing a land deed to a happy peasant in a "
                                                          "field"),
    ("In 1911, Stolypin was shot dead at the opera", "an opera house with red balconies, STOLYPIN clutching his chest, "
                                                     "NICHOLAS shocked in the royal box, non-graphic"),
    # ---------------------------------------------------------------- WWI
    ("In August 1914, the First World War broke out.", "simple map of Europe with flags and small explosions"),
    ("Huge crowds knelt in front of the Winter Palace", "a huge crowd kneeling in the palace square, NICHOLAS on the "
                                                        "balcony"),
    ("St. Petersburg was even renamed Petrograd", "a worker on a ladder painting over a big blank city sign"),
    ("at the Battle of Tannenberg", "Russian SOLDIERS surrounded in a forest by GERMANS"),
    ("Soldiers were sent to the front without boots.", "barefoot SOLDIERS in the snow, three of them sharing one "
                                                       "rifle"),
    ("By 1915, millions of Russians had been killed", "an endless field of small wooden crosses in the snow"),
    ("He travelled to the front and took personal command", "NICHOLAS at army headquarters studying a big map with "
                                                             "generals"),
    ("Now, every defeat was his defeat.", "NICHOLAS standing alone in the rain holding a telegram"),
    ("he left the government in the hands of his German-born wife", "ALEXANDRA and RASPUTIN sitting behind a "
                                                                     "government desk handing out papers"),
    ("Ministers were hired and fired", "ministers rushing in and out of a revolving door while RASPUTIN points"),
    ("Rumours spread that the Tsarina was a German spy.", "people whispering in a street, a thought bubble showing "
                                                          "ALEXANDRA wearing a German spiked helmet"),
    # ---------------------------------------------------------------- Rasputin's murder
    ("On a December night, a group of nobles", "YUSUPOV welcoming RASPUTIN into a cosy cellar dining room with "
                                               "candles"),
    ("According to the legend, they fed him cakes", "RASPUTIN happily eating pink cakes and drinking wine, nobles "
                                                    "peeking from behind a curtain"),
    ("Rasputin seemed to die, then suddenly leapt up", "RASPUTIN springing up and grabbing a terrified YUSUPOV, "
                                                       "comedic horror"),
    ("thrown through a hole in the ice", "a frozen river at night with a dark hole in the ice, nobles running away"),
    ("The nobles thought they had saved the monarchy.", "nobles raising champagne glasses in a toast"),
    # ---------------------------------------------------------------- February 1917
    ("The winter of 1917 was brutally cold.", "a snowy Petrograd street, a big thermometer showing freezing cold, "
                                              "people shivering"),
    ("women stood in bread queues for hours", "a long queue of women in headscarves outside a bakery with empty "
                                              "shelves, snow falling"),
    ("it was International Women's Day.", "women textile workers walking out of a factory gate"),
    ("shouting one word: \"Bread!\"", "women marching through the snow raising loaves of bread and blank banners"),
    ("Within three days, two hundred thousand workers", "a huge crowd filling a wide avenue with red flags"),
    ("The government ordered the army to restore order.", "a line of SOLDIERS facing the crowd, an officer shouting "
                                                          "orders"),
    ("The soldiers refused.", "SOLDIERS lowering their rifles, one of them hugging a worker"),
    ("One regiment after another mutinied.", "SOLDIERS handing rifles to WORKERS in front of an open arsenal"),
    ("Prisons were thrown open. Police stations burned.", "a police station on fire, prisoners walking out of an open "
                                                          "prison gate"),
    ("In a few days, the Tsar's government in Petrograd simply ceased to exist.", "an empty government office, papers "
                                                                                 "flying, a torn portrait of the "
                                                                                 "Tsar on the floor"),
    ("His train was stopped near the city of Pskov.", "the imperial train stopped on a snowy track at night"),
    ("There, his own generals told him the truth.", "generals inside a train carriage, NICHOLAS listening grimly"),
    ("Nicholas the Second signed his abdication.", "close-up of NICHOLAS signing a document at a small table in a "
                                                   "train carriage"),
    ("The next day, Michael refused the crown.", "Grand Duke Michael (tall cartoon man with a moustache) pushing "
                                                 "away a crown on a cushion"),
    ("the Romanov dynasty was over.", "a golden double-headed eagle emblem falling and cracking on the floor"),
    ("That night, Nicholas wrote in his diary", "NICHOLAS alone writing in a diary by candlelight"),
    ("Russia was free.", "cheering crowds pulling down imperial eagles from buildings"),
    ("Two new powers rose to fill the empty throne", "split image: politicians in suits at a table on the left, "
                                                     "WORKERS and SOLDIERS at a council on the right"),
    ("They decided to keep fighting the war.", "politicians pointing towards the front line while tired SOLDIERS "
                                               "groan"),
    ("in a small apartment in Zurich, Switzerland", "LENIN reading a newspaper with excitement in a cosy Swiss "
                                                    "apartment, snowy mountains through the window"),
    ("Russia's greatest enemy, Germany, was about to give him a ride.", "GERMANS holding a train door open for LENIN, "
                                                                        "dramatic cliffhanger"),
]

PART2 = [
    ("His name was Vladimir Ilyich Ulyanov.", "close-up of LENIN looking confident and determined"),
    ("He was the son of a school inspector.", "young Lenin as a schoolboy at a wooden desk with books"),
    ("his older brother Alexander was hanged", "young Lenin reading a letter in shock, a portrait of his older "
                                               "brother with a black ribbon"),
    ("He became a follower of Karl Marx", "LENIN reading a thick book under a portrait of Karl Marx with a big white "
                                          "beard"),
    ("overthrow the rich", "WORKERS pushing a fat capitalist in a top hat off a big pile of gold coins"),
    ("They needed to be led by a small, disciplined party", "LENIN leading a small secret meeting of serious "
                                                            "revolutionaries"),
    ("His party was called the Bolsheviks", "a small group with a red banner standing next to a much larger crowd"),
    ("In April 1917, the German government made a cold calculation.", "GERMANS around a map table pointing at Russia"),
    ("So they put Lenin and about thirty other revolutionaries on a train", "a train carriage with sealed doors, "
                                                                            "revolutionaries waving from the "
                                                                            "windows"),
    ("like a plague bacillus", "a train crossing Germany trailing a funny green germ-like cloud"),
    ("Lenin arrived at the Finland Station", "a railway station at night packed with people, red flags and a "
                                             "brass band"),
    ("Lenin climbed onto an armoured car", "LENIN giving a speech from the top of an armoured car under searchlights"),
    ("No cooperation with the Provisional Government.", "LENIN shouting with a raised fist, his own followers shocked"),
    ("\"Peace. Land. Bread.\"", "three big symbols side by side: a white dove, a golden wheat field and a loaf of "
                                "bread, on a red background"),
    ("Over the summer, the Provisional Government lost control.", "a chaotic government office with ministers "
                                                                   "arguing"),
    ("A young, dramatic lawyer named Alexander Kerensky", "KERENSKY giving a dramatic speech to SOLDIERS"),
    ("In June 1917, he launched a new offensive", "SOLDIERS charging forward, then turning and running back"),
    ("Soldiers deserted by the hundreds of thousands.", "SOLDIERS walking home along a country road with their "
                                                        "rifles"),
    ("Many walked home with their rifles to seize land", "PEASANTS dividing up a landlord's field, the landlord "
                                                         "fleeing"),
    ("In July, armed crowds of workers and sailors", "armed SAILORS and WORKERS filling a city street"),
    ("The government accused Lenin of being a German agent", "a wanted poster with LENIN's face on a wall"),
    ("Lenin shaved off his beard, put on a wig", "LENIN looking in a mirror with no beard and a funny wig, comedic"),
    ("escaped to Finland, disguised as a railway worker", "LENIN disguised as a railway stoker shovelling coal in a "
                                                          "locomotive cab"),
    ("General Lavr Kornilov", "General Kornilov (cartoon general with a dark goatee) leading troops on horseback"),
    ("In panic, Kerensky turned to the only people", "KERENSKY handing out rifles to REDGUARDS"),
    ("Kornilov's coup collapsed without a fight.", "Kornilov's soldiers sitting down and chatting with WORKERS"),
    ("Lenin, still in hiding, sent letter after letter", "LENIN writing letters by candlelight in a small wooden hut"),
    ("The October Revolution actually happened in November.", "two big wall calendars side by side, one red and one "
                                                              "blue, pages flying, no writing"),
    ("Russia still used the old Julian calendar", "a globe where Russia's clock is far behind all the other clocks, "
                                                  "funny"),
    ("organised by Leon Trotsky", "TROTSKY directing REDGUARDS at a map in a busy headquarters at night"),
    ("Bridges. Railway stations.", "REDGUARDS quietly taking over a bridge over a river at night"),
    ("The telephone exchange.", "REDGUARDS entering a telephone exchange, operators raising their hands"),
    ("the cruiser Aurora", "the cruiser Aurora on a river at night firing a single bright flash"),
    ("Bolshevik forces moved into the Winter Palace", "REDGUARDS entering the Winter Palace gates at night"),
    ("In later Soviet films", "a heroic movie-style scene of a huge crowd charging over the palace gates"),
    ("In reality, the palace was defended by a few hundred cadets", "a few bored young cadets and women soldiers "
                                                                    "standing around in a palace courtyard"),
    ("The attackers wandered through the endless corridors", "REDGUARDS lost in a very long golden palace corridor, "
                                                             "scratching their heads"),
    ("broke into the Tsar's wine cellars", "REDGUARDS in a wine cellar surrounded by bottles, looking tipsy, comedic"),
    ("Kerensky had already escaped in a car", "KERENSKY speeding away in an old car with a small American flag"),
    ("In just one night, with almost no bloodshed", "a red flag rising over the Winter Palace at dawn"),
    ("He announced that Russia would leave the war.", "LENIN at a podium in a packed hall, delegates cheering"),
    ("Land was taken from the nobles", "PEASANTS measuring out plots on a noble estate"),
    ("Factories were placed under workers' control.", "WORKERS cheerfully showing a factory owner the door"),
    ("for a Constituent Assembly", "a long queue of voters at a ballot box in a snowy village"),
    ("The Bolsheviks lost.", "a big pie chart with only a small red slice"),
    ("Lenin's guards closed it down after just one day.", "a yawning sailor guard in a striped shirt and round black cap telling deputies in suits to go home"),
    ("the deputies found the doors locked.", "deputies standing in front of doors locked with heavy chains"),
    ("the Cheka", "CHEKA standing in a dark office, cold expressions"),
    ("In March 1918, at the town of Brest-Litovsk", "Russian and GERMANS signing a treaty at a long table"),
    ("Russia gave up Poland, the Baltic lands, Finland and Ukraine.", "a map of Russia with giant scissors cutting off "
                                                                     "the western lands"),
    ("Lenin moved the capital from Petrograd to Moscow", "a train carrying government desks and filing cabinets "
                                                         "toward the red walls of the Kremlin"),
    ("And then Russia exploded into civil war.", "a map of Russia with red and white arrows clashing and small fires"),
    ("On one side were the Bolsheviks, now called the Reds.", "REDARMY marching with a red banner"),
    ("On the other side were the Whites", "WHITES standing together with Cossacks in tall fur hats and a priest"),
    ("Foreign powers joined in too.", "British, French, American and Japanese soldiers landing at a snowy port"),
    ("At one point, the Reds controlled only a small heartland", "a map with a small red area surrounded by white "
                                                                 "arrows"),
    ("The man who saved them was Leon Trotsky.", "TROTSKY in a leather coat saluting in front of REDARMY"),
    ("He built the Red Army from almost nothing", "recruits being drilled in a muddy yard"),
    ("He travelled from front to front in an armoured train", "an armoured train with cannons, TROTSKY standing on "
                                                              "its platform"),
    ("including a legion of Czech soldiers", "Czech legion soldiers riding a train with machine guns on the roof"),
    ("in a house now called the \"House of Special Purpose,\"", "the merchant house with a tall wooden fence and "
                                                                "guards in daylight"),
    ("Which brings us back to where our story began.", "NICHOLAS, ALEXANDRA, ALEXEI and DAUGHTERS waiting in "
                                                       "a dim basement room with faded striped wallpaper"),
    ("A guard read out a short statement.", "a guard reading a piece of paper, the family looking shocked, no "
                                            "weapons shown"),
    ("their doctor and three servants were all killed.", "an empty basement with one chair knocked over under a "
                                                         "single bulb, quiet and sombre, no people"),
    ("The daughters had sewn diamonds and jewels", "close-up of a white dress with hidden diamonds sparkling inside "
                                                   "the seams"),
    ("The bodies were taken to a forest and hidden.", "a dark birch forest at night with the headlights of an old "
                                                      "truck"),
    ("For decades, the Soviet Union kept the details secret.", "a file folder with a red seal being locked in a safe"),
    ("rumours spread that one of the daughters, Anastasia, had survived", "the silhouette of a young woman walking "
                                                                          "away into fog"),
    ("The most famous, Anna Anderson", "Anna Anderson (cartoon woman in a 1920s cloche hat) surrounded by reporters "
                                       "with cameras"),
    ("the remains were dug up from the forest", "scientists carefully digging in a forest clearing"),
    ("DNA tests proved", "a scientist in a lab looking at a DNA helix on a screen"),
    ("declared Nicholas and his family saints.", "a golden church icon of NICHOLAS, ALEXANDRA, ALEXEI and DAUGHTERS "
                                                 "with halos"),
    ("Fanny Kaplan shot Lenin twice", "a factory yard, LENIN stumbling, a woman with a pistol, people turning, "
                                      "non-graphic"),
    ("He survived, but one bullet stayed lodged", "LENIN in bed with a bandage around his neck, doctors around him"),
    ("The Bolsheviks answered with the Red Terror.", "CHEKA knocking on a door at night, a frightened family inside"),
    ("Nobles, priests, officers, merchants", "a line of arrested people being led away through the snow"),
    ("The Whites carried out their own massacres", "a burning village and White cavalry riding away, non-graphic"),
    ("To feed the army and the cities", "SOLDIERS taking sacks of grain from crying PEASANTS"),
    ("Money almost disappeared.", "a man using worthless banknotes to light his stove, comedic"),
    ("The Reds won the civil war, slowly, battle by battle.", "Red cavalry charging with sabres across the steppe"),
    ("fled across the Black Sea", "overcrowded ships leaving a Crimean port full of White refugees"),
    ("But the country they had won was in ruins.", "a ruined town with a broken factory and rubble"),
    ("somewhere between seven and twelve million people died", "an endless cemetery of small crosses under a grey sky"),
    ("a terrible famine struck the Volga region", "cracked dry fields and a starving village with empty bowls"),
    ("Russia had to accept food aid from the United States.", "American relief workers handing out soup to children"),
    ("the sailors of the naval fortress of Kronstadt", "SAILORS holding a meeting on a fortress island in a frozen sea"),
    ("Trotsky's Red Army crossed the frozen sea", "REDARMY in white camouflage crossing the ice toward a fortress"),
    ("He introduced a New Economic Policy", "a busy reopened market with stalls, PEASANTS happily selling vegetables"),
    ("the Union of Soviet Socialist Republics. The USSR.", "a big red map of the USSR with a hammer and sickle flag"),
    ("In 1922, he suffered the first of several strokes.", "LENIN in a wheelchair under a blanket in a country garden"),
    ("he watched from his bed as his comrades began to fight", "STALIN, TROTSKY and other leaders arguing around a "
                                                               "table, LENIN watching from his bed"),
    ("he dictated a secret letter", "LENIN dictating to a secretary at a typewriter"),
    ("\"Stalin is too rude,\" Lenin wrote.", "STALIN reading a letter over someone's shoulder, frowning, comedic"),
    ("Lenin died on the twenty-first of January, 1924.", "a funeral procession across a snowy Red Square, huge crowd"),
    ("his body was embalmed and put on display", "Lenin's red granite mausoleum on Red Square with guards"),
    ("His warning about Stalin was quietly hidden away.", "STALIN locking a letter in a drawer with a sly smile"),
    ("Most people expected Trotsky", "TROTSKY being applauded by REDARMY"),
    ("But Joseph Stalin was a master of patience", "STALIN at a desk full of files, moving chess pieces"),
    ("He played his rivals against each other, one by one.", "STALIN as a puppet master above his rivals"),
    ("Trotsky was pushed out of the government", "TROTSKY with a suitcase being shown the door"),
    ("In 1940, in exile in Mexico", "TROTSKY writing in a study in a Mexican villa with cacti in the garden, a "
                                    "shadowy figure in the doorway, no violence"),
    ("By then, Stalin ruled the Soviet Union with absolute power", "a giant portrait of STALIN above a parade with "
                                                                   "red flags"),
    ("the labour camps of the Gulag", "a prison camp in the snow with barbed wire and a watchtower"),
    ("would defeat Hitler in the Second World War", "a Soviet soldier raising a red flag on top of a ruined building"),
    ("put the first human in space", "a smiling cosmonaut in an orange spacesuit in front of a rocket"),
    ("a Cold War that brought the world to the edge of nuclear destruction", "American and Soviet missiles facing "
                                                                             "each other over a globe"),
    ("Communist revolutions would follow in China, Vietnam, Cuba", "a world map with red spreading across countries"),
    ("the red flag was lowered over the Kremlin for the last time", "the Kremlin at night in the snow with the red "
                                                                    "flag coming down"),
    ("The empire of the Tsars had lasted three hundred years.", "a golden double-headed eagle and a red star side by "
                                                                "side"),
    ("It all began with women in a bread queue", "women in a bread queue in the snow, one of them raising a loaf "
                                                 "high"),
    ("This was the Russian Revolution.", "a red flag over Petrograd at sunrise in the snow, calm ending"),
]


def main():
    out_detail = ["RUSSIAN REVOLUTION - IMAGE PROMPTS (flat history-cartoon style)",
                  f"Part 1: {len(PART1)} images · Part 2: {len(PART2)} images · total {len(PART1) + len(PART2)}",
                  "", "STYLE (added to the end of every prompt):", STYLE, "", "CHARACTERS (used inside prompts):"]
    out_detail += [f"  {k}: {v}" for k, v in C.items()]
    out_detail.append("")
    for part, items, fname in ((1, PART1, "narration_part1.txt"), (2, PART2, "narration_part2.txt")):
        text = open(os.path.join(HERE, fname), encoding="utf-8").read()
        last = 0
        lines = []
        out_detail.append(f"===================== PART {part} =====================")
        for n, (cue, scene) in enumerate(items, 1):
            pos = text.find(cue, last)
            if pos < 0:
                raise SystemExit(f"part {part}: cue not found in order: {cue!r}")
            last = pos + 1
            prompt = f"{P(scene)}. {STYLE}"
            lines.append(prompt)
            out_detail.append(f"P{part}-{n:03d} | Cue: \"{cue}\"")
            out_detail.append(prompt)
            out_detail.append("")
        with open(os.path.join(HERE, f"image_prompts_part{part}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    open(os.path.join(HERE, "image_prompts_detailed.txt"), "w", encoding="utf-8").write("\n".join(out_detail))
    print(len(PART1), len(PART2))


if __name__ == "__main__":
    main()
