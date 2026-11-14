"""Pick the 100 strongest scenes (50 per part) from make_image_prompts for a 100-image version."""
import os
import make_image_prompts as M

K1 = [1, 4, 6, 9, 11, 13, 15, 20, 22, 24, 26, 28, 30, 32, 33, 35, 37, 39, 43, 45, 48, 49, 51, 52, 55, 56,
      59, 60, 62, 68, 70, 71, 74, 78, 80, 83, 85, 88, 91, 92, 93, 96, 98, 101, 103, 105, 107, 109, 114, 115]
K2 = [1, 9, 11, 14, 18, 22, 23, 25, 28, 30, 33, 37, 38, 39, 40, 41, 44, 46, 48, 49, 50, 53, 54, 55, 59,
      61, 62, 64, 68, 71, 72, 73, 75, 79, 80, 84, 87, 89, 90, 93, 94, 98, 101, 102, 104, 105, 106, 108, 110, 111]
assert len(K1) == 50 and len(K2) == 50 and len(set(K1)) == 50 and len(set(K2)) == 50

out, detail = [], ["RUSSIAN REVOLUTION - 100 IMAGE VERSION (01-50 = Part 1, 51-100 = Part 2)", ""]
n = 0
for part, items, keep in ((1, M.PART1, K1), (2, M.PART2, K2)):
    for k in keep:
        cue, scene = items[k - 1]
        n += 1
        p = f"{M.P(scene)}. {M.STYLE}"
        out.append(p)
        detail += [f"{n:03d} | Part {part} | Cue: \"{cue}\"", p, ""]
open("image_prompts_100.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
open("image_prompts_100_detailed.txt", "w", encoding="utf-8").write("\n".join(detail))
print(n)
