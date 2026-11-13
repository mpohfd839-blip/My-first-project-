from PIL import Image, ImageDraw
from core import W, H, background, font, CINZEL9, CINZEL7, PAL, glow_layer
import tesla_arts as T
img = background("volt").convert("RGBA")
b = dict(pal="volt", big=True)
T.art_coil_big(img, b, 3.33, 10)
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
T.bolt_burst(d, 1380, 300, 7.7, 7, 650, outer=(150, 220, 255, 220))
glow_layer(img, L, 26, 1.8)
d = ImageDraw.Draw(img)
def t(xy, s, size, fill):
    d.text(xy, s, font=font(CINZEL9, size), fill=fill, stroke_width=9, stroke_fill=(8, 8, 20))
t((60, 140), "TESLA'S", 130, (235, 240, 255))
t((60, 300), "CRAZIEST", 150, (235, 240, 255))
t((60, 480), "EXPERIMENTS", 120, (110, 220, 255))
t((60, 660), "HE MADE LIGHTNING", 72, (255, 210, 90))
d.text((64, 820), "1856 – 1943 · THE MAN WHO LIT THE WORLD", font=font(CINZEL7, 40), fill=(170, 180, 220))
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save("thumbnail.png")
print("ok")
