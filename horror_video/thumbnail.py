import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from chars import draw_character, make_pose
import render
W, H = 1280, 720
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
img = Image.new("RGBA", (W, H), (10, 6, 8, 255))
# red radial glow behind Lily
g = Image.new("L", (W, H), 0)
ImageDraw.Draw(g).ellipse([640, 40, 1340, 760], fill=200)
g = g.filter(ImageFilter.GaussianBlur(120))
img.paste((150, 10, 20, 255), (0, 0), g)
# Lily creepy bust
p = make_pose(dict(c="lily", anim="still", expr="creepy_smile", look=(-0.25, 0)), 0.2, 5, 0, 1)
p["head_tilt"] = -6
li, ox, oy = draw_character("lily", p, 14.0, bust=True, opts={"wet": True})
img.alpha_composite(li, (int(960 - li.width / 2), H - li.height + 10))
# polaroid with scratched face
pol = render.polaroid_img("front", "right", "").resize((380, 440), Image.LANCZOS)
pol = pol.rotate(8, expand=True, resample=Image.BICUBIC)
sh = Image.new("RGBA", pol.size, (0, 0, 0, 0)); sh.putalpha(pol.getchannel("A").point(lambda v: v * .7))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (60, 250))
img.alpha_composite(pol, (40, 230))
# vignette + grain
a = np.asarray(img.convert("RGB")).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W/2) / (W/2))**2 + ((yy - H/2) / (H/2))**2)
a *= np.clip(1.15 - 0.45 * r**2, 0.35, 1.1)[..., None]
a += np.random.RandomState(1).randn(H, W, 1) * 5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img)
# red circle around scratched face + arrow
d.ellipse([235, 300, 375, 440], outline=(255, 30, 30), width=9)
d.line([(420, 330), (380, 360)], fill=(255, 30, 30), width=12)
d.polygon([(372, 352), (400, 378), (365, 385)], fill=(255, 30, 30))
# headline
f1 = ImageFont.truetype(B, 92)
f2 = ImageFont.truetype(B, 50)
d.text((40, 30), "SHE NEVER", font=f1, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
d.text((40, 128), "EXISTED", font=f1, fill=(255, 225, 40), stroke_width=7, stroke_fill=(0, 0, 0))
d.text((470, 640), "\"WE ONLY HAVE ONE DAUGHTER\"", font=ImageFont.truetype(B, 34), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
img.convert("RGB").save("thumbnail.png")
print("ok")
