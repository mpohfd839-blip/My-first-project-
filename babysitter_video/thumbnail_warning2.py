import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from chars import draw_character, make_pose
W, H = 1280, 720
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def F(s): return ImageFont.truetype(B, s)
YEL, BLK, RED = (255, 204, 0), (12, 10, 10), (230, 25, 30)

img = Image.new("RGBA", (W, H), (14, 6, 8, 255))
# red alarm glow behind the face
g = Image.new("L", (W, H), 0)
ImageDraw.Draw(g).ellipse([640, 40, 1380, 800], fill=230)
img.paste((170, 10, 18, 255), (0, 0), g.filter(ImageFilter.GaussianBlur(110)))
# light rays (siren)
rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for k in range(12):
    a = k * math.pi / 6
    rd.polygon([(980, 330), (980 + 1400 * math.cos(a - .06), 330 + 1400 * math.sin(a - .06)), (980 + 1400 * math.cos(a + .06), 330 + 1400 * math.sin(a + .06))], fill=(255, 40, 40, 28))
img.alpha_composite(rays)
# creepy baby
p = make_pose(dict(c="fakenoah", anim="still", expr="creepy_smile", look=(-0.25, 0)), 0.2, 5, 0, 1)
p["head_tilt"] = -9
bi, ox, oy = draw_character("fakenoah", p, 15.0, bust=True)
img.alpha_composite(bi, (int(985 - bi.width / 2), int(70 - 30 * 15)))
# vignette + grain on picture layer
a = np.asarray(img.convert("RGB")).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
a *= np.clip(1.15 - 0.4 * r ** 2, 0.4, 1.1)[..., None]
a += np.random.RandomState(2).randn(H, W, 1) * 5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img)

def hazard(y0, y1):
    d.rectangle([0, y0, W, y1], fill=YEL)
    for x in range(-200, W + 200, 70):
        d.polygon([(x, y1), (x + 35, y1), (x + 35 + (y1 - y0), y0), (x + (y1 - y0), y0)], fill=BLK)
    d.line([(0, y0), (W, y0)], fill=BLK, width=4); d.line([(0, y1), (W, y1)], fill=BLK, width=4)
hazard(0, 34)
hazard(H - 34, H)

# warning triangle
tx, ty, ts = 128, 168, 102
tri = [(tx, ty - ts * .88), (tx + ts, ty + ts * .85), (tx - ts, ty + ts * .85)]
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).polygon(tri, fill=(255, 200, 0, 170))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
d = ImageDraw.Draw(img)
d.polygon(tri, fill=YEL, outline=BLK)
d.line(tri + [tri[0]], fill=BLK, width=9, joint="curve")
d.rounded_rectangle([tx - 10, ty - 45, tx + 10, ty + 42], 8, fill=BLK)
d.ellipse([tx - 12, ty + 52, tx + 12, ty + 76], fill=BLK)

def txt(xy, s, size, fill, sw=8):
    d.text(xy, s, font=F(size), fill=fill, stroke_width=sw, stroke_fill=BLK)
txt((250, 62), "WARNING", 104, YEL, 9)
txt((262, 196), "5 BABYSITTING RULES", 44, (255, 255, 255), 6)
txt((40, 300), "ONE BABY", 112, (255, 255, 255), 9)
txt((40, 422), "ISN'T HUMAN", 96, RED, 9)

# caution tape across bottom-left
tape = Image.new("RGBA", (1500, 82), (0, 0, 0, 0))
td = ImageDraw.Draw(tape)
td.rectangle([0, 0, 1500, 82], fill=YEL)
td.line([(0, 3), (1500, 3)], fill=BLK, width=6); td.line([(0, 78), (1500, 78)], fill=BLK, width=6)
td.text((750, 41), "\u26A0 NEVER GO UPSTAIRS  \u26A0  DON'T LOOK AT THE MONITOR  \u26A0  NEVER GO", font=F(40), fill=BLK, anchor="mm")
tape = tape.rotate(7, expand=True, resample=Image.BICUBIC)
img.alpha_composite(tape, (-160, 520))
img.convert("RGB").save("thumbnail_warning2.png")
print("ok")
