import sys,glob
from PIL import Image
fs=sorted(glob.glob('stills/*.jpg'))
cols=2; w,h=640,360
rows=(len(fs)+1)//2
S=Image.new('RGB',(w*cols,h*rows))
for i,f in enumerate(fs):
    S.paste(Image.open(f).resize((w,h)),((i%cols)*w,(i//cols)*h))
S.save(sys.argv[1] if len(sys.argv)>1 else 'sheet.jpg',quality=85)
