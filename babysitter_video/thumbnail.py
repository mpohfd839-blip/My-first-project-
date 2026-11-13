import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from chars import draw_character, make_pose
import paint2
W, H = 1280, 720
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
img = Image.new("RGBA", (W, H), (10, 6, 8, 255))
g = Image.new("L", (W, H), 0)
ImageDraw.Draw(g).ellipse([660, 60, 1360, 780], fill=210)
img.paste((150, 10, 20, 255), (0, 0), g.filter(ImageFilter.GaussianBlur(120)))
p = make_pose(dict(c="fakenoah", anim="still", expr="creepy_smile", look=(-0.2, 0)), 0.2, 5, 0, 1)
p["head_tilt"] = -8
bi, ox, oy = draw_character("fakenoah", p, 16.0, bust=True)
img.alpha_composite(bi, (int(990 - bi.width / 2), int(40 - 30 * 16)))
# fridge note
note = Image.new("RGBA", (1920, 1080))
paint2.paint_note(note, {"hl": 5}, 2.0, 3.0)
note = note.crop((300, 120, 1640, 1080)).resize((470, 336), Image.LANCZOS).rotate(6, expand=True, resample=Image.BICUBIC)
img.alpha_composite(note, (40, 300))
a = np.asarray(img.convert("RGB")).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
a *= np.clip(1.15 - 0.45 * r ** 2, 0.35, 1.1)[..., None]
a += np.random.RandomState(1).randn(H, W, 1) * 5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img)
d.text((40, 30), "RULE #5:", font=ImageFont.truetype(B, 70), fill=(255, 225, 40), stroke_width=6, stroke_fill=(0, 0, 0))
d.text((40, 115), "DON'T OPEN", font=ImageFont.truetype(B, 92), fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
d.text((40, 215), "THE DOOR", font=ImageFont.truetype(B, 92), fill=(255, 40, 40), stroke_width=7, stroke_fill=(0, 0, 0))
d.ellipse([88, 545, 500, 625], outline=(255, 30, 30), width=8)
img.convert("RGB").save("thumbnail.png")
print("ok")
