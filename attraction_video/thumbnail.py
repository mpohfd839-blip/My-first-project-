from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1280, 720
FRED = "fonts/fredoka-latin-700-normal.woff"
NUN9 = "fonts/nunito-latin-900-normal.woff"
im = Image.open("assets/S02_eye_closeup.jpg").convert("RGB")
# heart-eye on the right half
sc = 900 / im.height
eye = im.resize((int(im.width * sc), 900), Image.LANCZOS)
im = Image.new("RGB", (W, H), (20, 8, 45))
im.paste(eye, (int(880 - eye.width / 2), -90))
import numpy as np
x = np.linspace(0, 1, W)[None, :].repeat(H, 0)
m = np.clip((0.62 - x) / 0.35, 0, 1) * 0.85
dark = Image.new("RGB", (W, H), (20, 8, 45))
im = Image.composite(dark, im, Image.fromarray((m * 255).astype(np.uint8)))
im = im.convert("RGBA")
L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(L)


def glow_text(xy, txt, f, fill, glow, r=14, stroke=6):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).text(xy, txt, font=f, fill=glow + (255,), stroke_width=stroke + 6, stroke_fill=glow + (255,))
    g = g.filter(ImageFilter.GaussianBlur(r))
    L.alpha_composite(g); L.alpha_composite(g)
    ImageDraw.Draw(L).text(xy, txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(25, 10, 50))


glow_text((48, 60), "WHY", ImageFont.truetype(FRED, 170), (255, 255, 255), (255, 60, 170))
glow_text((48, 230), "HER?", ImageFont.truetype(FRED, 210), (255, 214, 80), (255, 120, 60))
d = ImageDraw.Draw(L)
d.rounded_rectangle([52, 500, 640, 590], 45, fill=(70, 230, 240, 255))
d.text((346, 545), "YOUR BRAIN DECIDES", font=ImageFont.truetype(NUN9, 46), fill=(25, 10, 50), anchor="mm")
glow_text((60, 605), "IN UNDER 1 SECOND", ImageFont.truetype(NUN9, 52), (255, 255, 255), (70, 230, 240), 8, 4)
lumi = Image.open("cut/MASCOT_lumi.png"); lumi = lumi.resize((int(lumi.width * 190 / lumi.height), 190), Image.LANCZOS)
L.alpha_composite(lumi.rotate(-10, expand=True), (1080, 505))
im.alpha_composite(L)
im.convert("RGB").save("thumbnail.png")
