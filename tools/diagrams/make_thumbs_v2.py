# 썸네일 v2: 홈 카드에서 좌우가 잘려도 글자가 보이도록 텍스트를 가운데 70% 안전 영역(x 180~1020)에 둔다.
import re, glob, os
from PIL import Image, ImageDraw, ImageFont
TTC='/System/Library/Fonts/AppleSDGothicNeo.ttc'
def face(weight,size):
    for idx in range(20):
        try: f=ImageFont.truetype(TTC,size,index=idx)
        except Exception: break
        if f.getname()[1].lower()==weight.lower(): return f
    return ImageFont.truetype(TTC,size,index=0)
PAL={'backend':((30,41,99),(59,91,219),(255,214,102)),'devops':((13,71,71),(20,140,130),(255,214,102)),
     'data':((120,53,15),(217,119,6),(255,241,200)),'sql':((20,83,45),(34,150,94),(255,241,200)),
     'etc':((55,48,89),(109,94,173),(255,214,102)),'frontend':((15,60,90),(14,116,144),(255,214,102)),'ai':((70,30,20),(217,119,87),(255,241,200))}
W,H=1200,630; L,R=180,1020   # safe zone
def wrap(d,text,font,maxw):
    words=text.split(' '); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines
for f in sorted(glob.glob('_posts/*/*.md')):
    fm=re.match(r'---\n(.*?)\n---\n',open(f,encoding='utf-8').read(),re.S).group(1)
    title=re.search(r'^title:\s*(.+)$',fm,re.M).group(1).strip().strip('"')
    slug=re.search(r'^slug:\s*(\S+)',fm,re.M).group(1)
    top,sub=re.search(r'^categories:\s*\[(\w+),\s*([\w-]+)\]',fm,re.M).groups()
    c1,c2,acc=PAL[top]
    img=Image.new('RGB',(W,H)); px=img.load()
    for y in range(H):
        for x in range(W):
            u=(x/W)*0.35+(y/H)*0.65
            px[x,y]=tuple(int(c1[i]+(c2[i]-c1[i])*u) for i in range(3))
    img=img.convert('RGBA'); ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for gx in range(60,W,60):
        for gy in range(60,H,60):
            if gx<L-40 or gx>R+40: od.ellipse((gx,gy,gx+3,gy+3),fill=(255,255,255,60))
    img=Image.alpha_composite(img,ov).convert('RGB'); d=ImageDraw.Draw(img)
    d.text((L,84),f"{top.upper()}  ·  {sub.upper()}",font=face('Bold',28),fill=acc)
    d.rounded_rectangle((L,126,L+70,132),radius=3,fill=acc)
    size=68
    while True:
        ft=face('Heavy',size); lines=wrap(d,title,ft,R-L)
        if len(lines)<=3 or size<=44: break
        size-=4
    y=172
    for ln in lines:
        d.text((L,y),ln,font=ft,fill=(255,255,255)); y+=int(size*1.3)
    d.text((L,H-100),'nogamsung.github.io',font=face('Medium',28),fill=(255,255,255))
    d.text((L,H-64),'nogamsung 개발 블로그  ·  프로덕트 엔지니어 안검성',font=face('Regular',24),fill=(230,230,240))
    out=f'assets/img/thumbnail/{slug}.jpg'
    img.save(out,'JPEG',quality=88,optimize=True,progressive=True)
    print('thumb',slug,size,len(lines),os.path.getsize(out)//1024,'KB')
