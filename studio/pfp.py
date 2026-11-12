from PIL import Image, ImageDraw
L = 60; S = 18
INK=(24,18,34); GOLD=(255,200,40); GOLD_D=(214,128,20); GOLD_L=(255,245,170); RED=(255,80,100)
SHIRT=(60,200,190); SHIRT_D=(30,130,130)
im = Image.new("RGB",(L,L)); d = ImageDraw.Draw(im)
top, bot = (40,30,90), (110,60,150)
for y in range(L):
    p=y/L; d.line([0,y,L,y], fill=tuple(int(a+(b-a)*p) for a,b in zip(top,bot)))
for (x,y) in [(8,10),(50,8),(12,40),(52,36),(46,18),(6,26),(30,4)]:
    d.point((x,y), fill=(255,255,220))
for (x,y) in [(9,10),(51,8)]:
    d.point((x+1,y),fill=(200,200,255)); d.point((x-1,y),fill=(200,200,255))
# shoulders / shirt
d.rectangle([14,48,46,60], fill=INK); d.rectangle([15,49,45,60], fill=SHIRT); d.rectangle([38,49,45,60], fill=SHIRT_D)
d.rectangle([27,52,32,57], fill=GOLD); d.point((29,53),fill=GOLD_L)
# head
cx, cy, R = 30, 29, 18
d.ellipse([cx-R-1,cy-R-1,cx+R+1,cy+R+1], fill=INK)
d.ellipse([cx-R,cy-R,cx+R,cy+R], fill=GOLD)
d.ellipse([cx-R+3,cy-R+3,cx+R-3,cy+R-3], outline=GOLD_D)
d.rectangle([cx+R-2,cy-6,cx+R-1,cy+R-7], fill=GOLD_D)
d.rectangle([cx-R+5,cy-R+4,cx-R+7,cy-R+5], fill=GOLD_L); d.point((cx-R+4,cy-R+6),fill=GOLD_L)
# happy eyes ^ ^
for s in (-1,1):
    ex=cx+s*7; ey=cy-3
    d.line([ex-3,ey+1,ex-1,ey-1],fill=INK,width=1); d.line([ex-1,ey-1,ex+1,ey-1],fill=INK); d.line([ex+1,ey-1,ex+3,ey+1],fill=INK)
    d.line([ex-3,ey+2,ex-1,ey],fill=INK); d.line([ex+1,ey,ex+3,ey+2],fill=INK)
# smile
d.rectangle([cx-5,cy+5,cx+5,cy+6],fill=INK); d.point((cx-6,cy+4),fill=INK); d.point((cx+6,cy+4),fill=INK)
d.rectangle([cx-4,cy+7,cx+4,cy+8],fill=INK); d.rectangle([cx-3,cy+7,cx+3,cy+8],fill=RED)
# cheeks
for s in (-1,1): d.rectangle([cx+s*12-1,cy+2,cx+s*12+1,cy+3],fill=(255,140,120))
im = im.resize((L*S,L*S), Image.NEAREST)
im.save("/home/claude/dime-money-quest/studio/dime_profile.png")
