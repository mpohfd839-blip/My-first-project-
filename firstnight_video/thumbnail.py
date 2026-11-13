import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scenes import font, FXB, creature
from picto import draw_person, draw_dog, make_pose
W, H = 1280, 720
YEL, BLK, RED, WH = (255, 204, 0), (10, 9, 9), (230, 25, 30), (240, 238, 232)
FY = 640
# spotlight background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - 900) / 520) ** 2 + ((yy - 300) / 460) ** 2)
k = np.clip(1 - r, 0, 1) ** 1.5
bg = np.array([8, 7, 7], np.float32) + (np.array([215, 196, 155], np.float32) - 8) * k[..., None]
img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
# giant shadow on the wall rising from behind the door
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
creature(ImageDraw.Draw(sh), 900, FY + 40, 1.25, 1.3, black=True, alpha=235)
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
d = ImageDraw.Draw(img)
# door
d.rectangle([760, 300, 1060, FY], fill=WH)
d.rectangle([780, 320, 1040, FY], fill=(226, 224, 218))
d.rectangle([805, 345, 1015, 470], fill=(40, 38, 36))
# golden dog shape in the frosted window (blurred)
dg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(dg)
gd.ellipse([840, 410, 960, 480], fill=(215, 165, 70, 255))
gd.ellipse([930, 370, 990, 425], fill=(215, 165, 70, 255))
gd.line([(850, 430), (815, 395)], fill=(215, 165, 70, 255), width=14)
dg = dg.filter(ImageFilter.GaussianBlur(7))
m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([805, 345, 1015, 470], fill=255)
from PIL import ImageChops
img.paste(dg, (0, 0), ImageChops.multiply(dg.getchannel("A"), m))
fr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fr)
rs = np.random.RandomState(2)
for _ in range(90):
    x, y, rr = rs.uniform(805, 1015), rs.uniform(345, 470), rs.uniform(3, 9)
    fd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 30))
img.alpha_composite(fr)
d = ImageDraw.Draw(img)
d.ellipse([1000, 540, 1024, 564], fill=(150, 148, 144))
d.rectangle([0, FY, W, FY + 4], fill=WH)
# kid stepping back
p = make_pose(dict(anim="back_off", face=1), 2, 5, 1)
p["aL"] = (35, -120); p["aR"] = (35, -120)
kid, ox, oy = draw_person("kid", p, 2.6)
kshadow = kid.getchannel("A").resize((int(kid.width * 1.6), int(kid.height * 1.6)))
shl = Image.new("L", (W, H), 0); shl.paste(kshadow, (int(640 - ox * 1.6), int(FY - oy * 1.6)))
shl = shl.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .6))
img.paste((14, 12, 11, 255), (0, 0), shl)
img.alpha_composite(kid, (int(690 - ox), int(FY - oy)))
# grade + grain + vignette
a = np.asarray(img.convert("RGB")).astype(np.float32)
rv = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
a *= np.clip(1.1 - 0.3 * rv ** 2, 0.35, 1.1)[..., None]
a += np.random.RandomState(1).randn(H, W, 1) * 5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
# text panel gradient
pan = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pan)
for x in range(0, 620):
    pd.line([(x, 0), (x, H)], fill=(0, 0, 0, int(200 * max(0, 1 - x / 620) ** 0.8)))
img.alpha_composite(pan)
d = ImageDraw.Draw(img)
def hazard(y0, y1):
    d.rectangle([0, y0, W, y1], fill=YEL)
    for x in range(-200, W + 200, 70):
        d.polygon([(x, y1), (x + 35, y1), (x + 35 + (y1 - y0), y0), (x + (y1 - y0), y0)], fill=BLK)
hazard(0, 28); hazard(H - 28, H)
tx, ty, ts = 92, 130, 66
tri = [(tx, ty - ts * .88), (tx + ts, ty + ts * .85), (tx - ts, ty + ts * .85)]
d.polygon(tri, fill=YEL); d.line(tri + [tri[0]], fill=BLK, width=7, joint="curve")
d.rounded_rectangle([tx - 7, ty - 30, tx + 7, ty + 28], 6, fill=BLK); d.ellipse([tx - 9, ty + 36, tx + 9, ty + 53], fill=BLK)
def txt(xy, s, size, fill, sw=7):
    d.text(xy, s, font=font(FXB, size), fill=fill, stroke_width=sw, stroke_fill=BLK)
txt((180, 62), "WARNING", 92, YEL, 8)
txt((36, 240), "DON'T LET", 88, WH, 8)
txt((36, 338), "THE DOG IN", 88, WH, 8)
txt((36, 452), "IT'S NOT BUSTER", 60, RED, 7)
# arrow to the shadow
d.line([(640, 200), (760, 160)], fill=RED, width=12)
d.polygon([(770, 150), (742, 145), (752, 180)], fill=RED)
img.convert("RGB").save("thumbnail.png")
print("ok")
