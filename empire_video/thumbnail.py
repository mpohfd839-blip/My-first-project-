from PIL import Image, ImageDraw
from core import W, H, background, font, CINZEL9, CINZEL7, PAL, glow_layer
from arts import art_globe, union_jack, crown
img = background("ink").convert("RGBA")
b = dict(pal="ink", stage="S1920")
art_globe(img, b, 8.0, 10, cx=1380, cy=560, R=470)
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
crown(d, 1380, 110, 0.55, PAL["ink"]["acc"] + (255,), 1.0)
glow_layer(img, L, 16, 1.2)
d = ImageDraw.Draw(img)
def t(xy, s, size, fill, f=CINZEL9):
    d.text(xy, s, font=font(f, size), fill=fill, stroke_width=8, stroke_fill=(10, 8, 6))
t((70, 120), "HOW ONE", 120, (240, 225, 190))
t((70, 260), "ISLAND", 160, (240, 225, 190))
t((70, 440), "RULED", 120, (240, 225, 190))
t((70, 580), "1/4 OF THE", 120, (255, 170, 60))
t((70, 720), "WORLD", 160, (255, 170, 60))
union_jack(d, 80, 930, 170, 100)
d.text((280, 980), "THE BRITISH EMPIRE · 1600 – 1997", font=font(CINZEL7, 40), fill=(200, 180, 140), anchor="lm")
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save("thumbnail.png")
print("ok")
