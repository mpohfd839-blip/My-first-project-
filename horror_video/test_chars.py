from PIL import Image
from chars import *
bg=Image.new("RGBA",(1920,1080),(200,190,175,255))
x=120
for n,ex in [("you","smile"),("emma","happy"),("lily","blank"),("diane","smile"),("frank","neutral"),("kemma","smile"),("klily","blank")]:
    a=dict(c=n,anim="talk" if n=="emma" else "idle",expr=ex,look=(0.3,0))
    p=make_pose(a,1.0,5,0.5,3)
    u=4.5 if n[0]!='k' else 2.6
    im,ox,oy=draw_character(n,p,u,opts={"wet":n=="lily"})
    bg.alpha_composite(im,(int(x-ox),int(1000-oy)))
    x+=260
for i,(n,ex) in enumerate([("lily","creepy_smile"),("emma","cry"),("you","terrified"),("frank","angry")]):
    a=dict(c=n,anim="idle",expr=ex,look=(0,0))
    p=make_pose(a,1.0,5,0.0,3)
    im,ox,oy=draw_character(n,p,4.0,bust=True,opts={"wet":n=="lily"})
    bg.alpha_composite(im,(i*460, 0))
bg.convert("RGB").save("test_chars.png")
