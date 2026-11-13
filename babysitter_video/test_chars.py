from PIL import Image
from chars import *
bg=Image.new("RGBA",(1920,1080),(200,190,175,255))
x=150
for n,ex,an in [("you","smile","idle"),("claire","smile_wide","talk"),("david","neutral","tie"),("noah","happy","baby"),("fakenoah","creepy_smile","baby"),("claire","smile","idle")]:
    a=dict(c=n,anim=an,expr=ex,look=(0.3,0),back=(n=="claire" and ex=="smile"))
    p=make_pose(a,1.0,5,0.5,3)
    u=4.5
    im,ox,oy=draw_character(n,p,u)
    bg.alpha_composite(im,(int(x-ox),int(1050-oy)))
    x+=300
for i,(n,ex) in enumerate([("claire","smile_huge"),("fakenoah","blank"),("noah","happy"),("david","smile_huge")]):
    a=dict(c=n,anim="idle",expr=ex,look=(0,0),phone=(i==0),birthmark=(i==2))
    p=make_pose(a,1.0,5,0.0,3)
    im,ox,oy=draw_character(n,p,4.0,bust=True)
    bg.alpha_composite(im,(i*460, 0))
bg.convert("RGB").save("test_chars.png")
