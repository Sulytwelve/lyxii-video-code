"""A cozy, reproducible cut-paper animation. Python/Pillow/NumPy + FFmpeg.

Character artwork is an explicitly credited CC BY-NC-SA 4.0 adaptation.
The atlas is a visual input, not pre-generated video. Every frame is made here.
"""
from pathlib import Path
from functools import lru_cache
import argparse, json, math, subprocess, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS, SR = 1920, 1080, 24, 48000
TOTAL = 64
STORY = json.loads((ROOT / 'production/timeline.json').read_text('utf-8'))
CREAM, INK, BLUE, MUTED = '#f5eddf', '#494a59', '#637fa8', '#8d867d'
ROSE, GOLD, GREEN = '#d69b88', '#e7bf7c', '#96ac92'
TEXT_BOUNDS = []

@lru_cache(80)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)

@lru_cache(1000)
def glyph(s, size=45, color=INK, bold=False):
    f = font(size, bold)
    b = f.getbbox(s)
    p = Image.new('RGBA', (max(1, b[2]-b[0]+8), b[3]-b[1]+8))
    ImageDraw.Draw(p).text((4-b[0], 4-b[1]), s, font=f, fill=color)
    return p

def text(im, s, x, y, size=45, color=INK, bold=False, anchor='left'):
    p = glyph(str(s), size, color, bold)
    if anchor == 'center': x -= p.width / 2
    if anchor == 'right': x -= p.width
    im.paste(p, (round(x), round(y)), p)
    TEXT_BOUNDS.append((str(s), round(x), round(y), p.width, p.height))

def rr(im, box, r=24, fill=CREAM, outline=None, width=3):
    ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in box), r, fill, outline, width)

def ease(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

def bezier(points, n=32):
    p0, p1, p2, p3 = np.asarray(points, float)
    return [tuple((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3) for t in np.linspace(0, 1, n)]

def curve(im, points, color=INK, width=4):
    ImageDraw.Draw(im).line(bezier(points), fill=color, width=width, joint='curve')

def shadow(im, box, opacity=30, blur=16):
    p = Image.new('RGBA', (W, H))
    ImageDraw.Draw(p).ellipse(box, fill=(100, 74, 55, opacity))
    p = p.filter(ImageFilter.GaussianBlur(blur))
    im.paste(p, (0, 0), p)

def plant(im, x, y, scale=1, t=0):
    d = ImageDraw.Draw(im)
    s = scale
    rr(im, (x-48*s, y-82*s, x+48*s, y), 15, '#c99574')
    d.ellipse((x-49*s, y-95*s, x+49*s, y-64*s), fill='#d8ad8b')
    d.line((x, y-79*s, x, y-230*s), fill='#899477', width=round(7*s))
    for i in range(6):
        xx = x + (1 if i%2 else -1) * (35+2*math.sin(t+i))*s
        yy = y-(110+i*23)*s
        d.line((x, yy+15*s, xx, yy), fill='#8a967b', width=round(4*s))
        d.ellipse((xx-29*s, yy-20*s, xx+29*s, yy+15*s), fill=['#a3b49a','#8da28a'][i%2])

def whale_mark(im, x, y, scale=1, color=BLUE):
    d = ImageDraw.Draw(im); s=scale
    d.ellipse((x, y, x+90*s, y+52*s), fill=color)
    d.polygon([(x+60*s,y+32*s),(x+103*s,y+8*s),(x+109*s,y+25*s),(x+122*s,y+5*s),(x+120*s,y+38*s),(x+86*s,y+46*s)], fill=color)
    d.ellipse((x+17*s,y+15*s,x+22*s,y+20*s), fill=CREAM)

@lru_cache(3)
def room(night=False):
    rng = np.random.default_rng(42)
    col = np.array([245,237,224] if not night else [237,229,220])
    noise = rng.normal(0, 0.8, (H,W,1))
    im = Image.fromarray(np.uint8(np.clip(col+noise,0,255)))
    d = ImageDraw.Draw(im)
    d.rectangle((0,810,W,H), fill='#eadac2')
    d.rectangle((0,801,W,816), fill='#d5c3a9')
    for y in [880,964,1050]: d.line((0,y,W,y), fill='#e0cfb4', width=2)
    for x,y in [(340,880),(1400,880),(840,964),(1710,964),(260,1050)]:d.line((x,y-65,x,y),fill='#dfceb5',width=2)
    # Deep window with a warm dusk landscape.
    rr(im,(108,192,482,538),32,'#d6c3aa')
    rr(im,(128,210,462,517),22,'#bccfd8' if not night else '#869baa')
    d.ellipse((351,249,406,304),fill='#f6d29a')
    d.polygon([(129,445),(217,369),(319,450),(399,396),(462,429),(462,514),(129,514)],fill='#a6b6ab')
    d.polygon([(128,479),(269,422),(414,465),(462,450),(462,515),(128,515)],fill='#91a59b')
    d.line((295,211,295,516),fill='#f2e5ce',width=13)
    d.line((129,367,461,367),fill='#f2e5ce',width=13)
    rr(im,(90,521,500,553),10,'#c7b096')
    for x in [77,476]:
        rr(im,(x,169,x+38,537),13,'#efe0cc')
        for xx in [x+12,x+25]:d.line((xx,182,xx,518),fill='#deceb9',width=2)
    # Sofa, cushion seams, oval rug and tea table.
    shadow(im,(315,850,1305,987),28)
    d.ellipse((249,814,1552,1023),fill='#ddd0ba',outline='#cec3ad',width=3)
    d.ellipse((280,832,1518,1000),outline='#e7ddca',width=4)
    rr(im,(355,539,1251,859),73,'#baaaa0',outline='#ab9b91')
    rr(im,(363,554,1241,827),60,'#cbbcb0')
    d.line((790,575,790,793),fill='#b4a599',width=3)
    rr(im,(322,675,435,875),36,'#b8a59b')
    rr(im,(1175,675,1290,875),36,'#b8a59b')
    rr(im,(425,761,1172,868),31,'#d1c2b4',outline='#bca99a')
    rr(im,(458,588,658,775),37,'#f0d1b7')
    rr(im,(921,593,1128,776),37,'#bdd0ca')
    whale_mark(im,969,658,.85,'#91aaa3')
    for x in [387,1200]:rr(im,(x,868,x+38,902),8,'#9f8068')
    # Framed whale drawing and warm little bookshelf.
    rr(im,(640,211,944,430),14,'#b89a79')
    rr(im,(654,225,930,416),5,'#f9f2e5')
    whale_mark(im,728,286,1.05)
    for yy in [365,379]:curve(im,[(693,yy),(728,yy-8),(813,yy+8),(886,yy)],'#c6d3d3',3)
    rr(im,(1377,302,1803,327),7,'#ba9672')
    for i,(h,c) in enumerate([(118,'#c69d83'),(94,'#95aaa3'),(128,'#97acc5'),(108,'#e0ba86'),(92,'#b8a9b8')]):
        x=1407+i*47;rr(im,(x,299-h,x+37,300),5,c);d.line((x+9,311-h,x+9,282),fill='#ece4d8',width=2)
    plant(im,1745,300,.6)
    plant(im,1630,891,1.4)
    # Lamp casts a low-opacity glow, baked once.
    glow=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(glow)
    gd.ellipse((1330,312,1690,882),fill=(255,207,123,27))
    glow=glow.filter(ImageFilter.GaussianBlur(65));im.paste(glow,(0,0),glow)
    d=ImageDraw.Draw(im);d.line((1510,551,1510,874),fill='#aa8e70',width=9)
    d.ellipse((1465,862,1555,882),fill='#ab9076')
    d.polygon([(1460,399),(1560,399),(1610,550),(1409,550)],fill='#edc79b',outline='#c5a57e',width=3)
    d.ellipse((1410,533,1609,561),fill='#f4d8b1',outline='#d0b18c',width=3)
    return im

ATLAS = Image.open(ROOT/'assets/whale_sprite_atlas.png').convert('RGBA')
# Technical atlas regions include complete silhouettes; no image retouching.
REGIONS = [(22,0,517,519),(536,0,1026,521),(1050,0,1536,517),
           (25,519,521,1024),(535,571,1025,1024),(1045,518,1536,1024)]
POSES=[]
for box in REGIONS:
    a=ATLAS.crop(box)
    bbox=a.getchannel('A').point(lambda v:255 if v>12 else 0).getbbox()
    POSES.append(a.crop(bbox) if bbox else a)

@lru_cache(500)
def scaled_pose(pose,height):
    a=POSES[pose]
    return a.resize((round(a.width*height/a.height),height),Image.Resampling.LANCZOS)

def fish(im,pose,x,bottom,t,height=660,action='breathe'):
    dh=round(3*math.sin(t*2.1)) if action=='breathe' else 0
    a=scaled_pose(pose,height+dh)
    angle = math.sin(t*1.4)*1.05
    if action=='walk':angle=math.sin(t*8)*3
    if action=='caught':angle=math.sin(t*15)*1.2*max(0,1-t/1.1)
    if action=='sleep':angle=math.sin(t*1.1)*.55
    a=a.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    bob=math.sin(t*8)*8 if action=='walk' else math.sin(t*1.6)*4
    im.paste(a,(round(x-a.width/2),round(bottom-a.height+bob)),a)
    return (x-a.width/2,bottom-a.height,a.width,a.height)

def person(im,x,bottom,t,scale=1,mood='tired',cup=False):
    p=Image.new('RGBA',(440,510));d=ImageDraw.Draw(p)
    # Original bean-shaped human stand-in, with procedural eyelids and arms.
    rr(p,(103,258,334,435),76,'#ce9d88',outline='#a37f70',width=4)
    d.ellipse((72,37,351,313),fill='#fae6ca',outline='#a58e7e',width=4)
    d.polygon([(157,79),(137,26),(185,42),(196,8),(220,50),(269,39),(258,96)],fill='#b28b73')
    for xx in [133,261]:
        if mood=='happy':curve(p,[(xx,175),(xx+11,160),(xx+30,160),(xx+39,176)],INK,5)
        elif mood=='sleep':curve(p,[(xx,175),(xx+11,184),(xx+27,184),(xx+37,175)],INK,4)
        else:d.line((xx,182,xx+39,187),fill=INK,width=5)
    d.ellipse((107,209,155,228),fill='#ebbc9e');d.ellipse((269,209,316,228),fill='#ebbc9e')
    if mood=='happy':curve(p,[(199,220),(207,237),(225,237),(235,220)],INK,4)
    else:d.line((203,234,230,234),fill=INK,width=4)
    d.line((139,337,81,404),fill='#a78272',width=37)
    if cup:
        d.line((301,341,324,296),fill='#a78272',width=37)
        rr(p,(296,254,362,312),12,'#e8eee0',outline='#82948c',width=3)
        d.arc((344,262,377,300),-90,90,fill='#82948c',width=6)
    else:d.line((301,337,357,404),fill='#a78272',width=37)
    d.ellipse((120,408,207,466),fill='#92776c');d.ellipse((245,408,330,466),fill='#92776c')
    bob=math.sin(t*1.4)*2
    p=p.resize((round(p.width*scale),round(p.height*scale)),Image.Resampling.LANCZOS)
    im.paste(p,(round(x-p.width/2),round(bottom-p.height+bob)),p)

def calendar(im,day,x=140,y=610,tilt=0):
    p=Image.new('RGBA',(214,218))
    rr(p,(6,8,208,213),17,'#fff8e9',outline='#c6b399',width=3)
    rr(p,(6,8,208,57),15,'#ce9f89')
    text(p,'十月',107,20,25,'#fff9ef',True,'center')
    text(p,str(day),107,78,89,INK,True,'center')
    text(p,'假期后的一天' if day==8 else '快乐假期',107,184,19,MUTED,False,'center')
    if tilt:p=p.rotate(tilt,resample=Image.Resampling.BICUBIC,expand=True)
    im.paste(p,(x,y),p)

def bowl(im,x,y,t,empty=False,s=1):
    d=ImageDraw.Draw(im)
    d.ellipse((x-91*s,y-19*s,x+91*s,y+20*s),fill='#e8e9df',outline='#9aacae',width=3)
    d.pieslice((x-90*s,y-57*s,x+90*s,y+86*s),0,180,fill='#d5e1df',outline='#80999d',width=4)
    d.ellipse((x-83*s,y-17*s,x+83*s,y+15*s),fill='#ecece4' if empty else '#fff3d8',outline='#9aacae',width=3)
    if not empty:
        for k in range(31):
            rx=x+(k*29%146-73)*s;ry=y-(k*13%26)*s
            d.ellipse((rx-6*s,ry-3*s,rx+6*s,ry+3*s),fill='#fff8e9',outline='#e9ddc5')
        steam(im,x,y-55*s,t,s)
    whale_mark(im,x-29*s,y+24*s,.4*s)

def steam(im,x,y,t,s=1):
    for i in range(3):
        phase=(t*.45+i/3)%1;xx=x+(i-1)*26*s;yy=y-phase*85*s
        col=tuple([255,248,233,round(110*(1-phase))])
        p=Image.new('RGBA',(W,H))
        curve(p,[(xx,yy),(xx-13*s,yy-18*s),(xx+14*s,yy-31*s),(xx,yy-47*s)],col,round(5*s))
        im.paste(p,(0,0),p)

def bubble(im,lines,x,y,w,who='鱼',size=43,tail=True):
    if isinstance(lines,str):lines=[lines]
    h=76+len(lines)*(size+16)
    fill='#fffaf0' if who=='鱼' else '#e7eddf'
    rr(im,(x+4,y+7,x+w+4,y+h+7),32,'#dfd3c3')
    rr(im,(x,y,x+w,y+h),32,fill,outline='#cdbda8',width=3)
    if tail:
        tx=x+w-110 if who=='鱼' else x+110
        ImageDraw.Draw(im).polygon([(tx-25,y+h-3),(tx+29,y+h-3),(tx+(22 if who=='鱼' else -20),y+h+31)],fill=fill)
    text(im,'大肥鱼' if who=='鱼' else '我',x+30,y+19,23,BLUE if who=='鱼' else '#799177',True)
    for i,ln in enumerate(lines):text(im,ln,x+30,y+60+i*(size+16),size,INK,True)

def header(im):
    text(im,'一条鱼，和你的一点日常',90,59,25,MUTED)
    text(im,'梨希 Lyxii',1827,59,25,BLUE,False,'right')

def footer(im,caption):
    p=glyph(caption,34,INK)
    x=(W-p.width)//2
    rr(im,(x-27,985,x+p.width+27,1047),21,'#f7f0e3')
    im.paste(p,(x,999),p)

def mood_note(im,level,x=673,y=315):
    rr(im,(x,y,x+435,y+112),15,'#faf2d8',outline='#dfcfac',width=2)
    text(im,'今日精神状态',x+25,y+17,24,MUTED)
    rr(im,(x+27,y+64,x+276,y+84),7,'#e4d7bf')
    if level>0:rr(im,(x+27,y+64,x+27+249*level,y+84),7,GREEN if level>.4 else ROSE)
    text(im,f'{round(level*100)}%',x+395,y+58,28,INK,True,'right')

def sparkles(im,x,y,t,color=GOLD):
    d=ImageDraw.Draw(im)
    for i in range(5):
        a=t*.6+i*1.257;r=80+12*math.sin(t+i)
        xx=x+math.cos(a)*r;yy=y+math.sin(a)*r*.6
        d.line((xx-6,yy,xx+6,yy),fill=color,width=3);d.line((xx,yy-6,xx,yy+6),fill=color,width=3)

def scene_at(now):
    return next(s for s in STORY if s['start']<=now<s['start']+s['duration']) if now<TOTAL else STORY[-1]

def frame_at(now,clean=False):
    TEXT_BOUNDS.clear()
    s=scene_at(now);t=now-s['start'];k=s['id']
    im=room(k in ['sleep','together']).copy()
    if k=='holiday':
        person(im,899,902,t,1.16,'tired')
        day=1 if t<.65 else 7 if t<1.25 else 8
        calendar(im,day,153,602,math.sin(t*12)*7*max(0,1-t/1.8))
        mood_note(im,.08,1340,128)
        if not clean:
            rr(im,(514,124,1278,306),27,'#fff7e8')
            text(im,'假期结束后的我',896,148,76,INK,True,'center')
            text(im,'身体已到岗  /  灵魂还在床上',896,250,32,MUTED,False,'center')
    elif k=='enter':
        calendar(im,8);person(im,715,894,t,1,'tired')
        x=2100-770*ease(t/2.0)
        fish(im,0,x,953,t,650,'walk' if t<2 else 'breathe')
        if not clean and t>.8:bubble(im,['人，你怎么比我','还像在摸鱼？'],919,150,695)
    elif k=='rice':
        calendar(im,8);person(im,653,895,t,1,'tired')
        fish(im,1,1261-67*ease(t/1.8),951,t,677)
        steam(im,1058,548,t,.8)
        if not clean:bubble(im,['别急。','先吃一碗热乎的。'],617,135,690)
    elif k=='caught':
        person(im,514,944,t,.78,'tired')
        z=1+.09*ease(t/.4)
        fish(im,2,1292,969,t,round(705*z),'caught')
        if not clean:
            bubble(im,['等一下……','这碗不是给我的吗？'],108,184,834,'人',47)
            if t>2.5:text(im,'（嚼嚼）',1066,873,28,BLUE)
    elif k=='full':
        person(im,573,919,t,.89,'tired')
        fish(im,3,1275,952,t,654)
        if not clean:
            if t<2.8:bubble(im,['我帮你试过了。','很好吃。'],918,146,746)
            else:bubble(im,['你这吃白饭的','蓝色大肥鱼！'],97,188,865,'人',54)
        sparkles(im,1490,482,t,ROSE)
    elif k=='sleep':
        person(im,644,899,t,.95,'tired')
        # Lowering onto the cushion is animated; the pose is not a video clip.
        bottom=922-57*ease(t/1.5)
        fish(im,4,1090,bottom,t,520,'sleep')
        if not clean:
            bubble(im,['吃饱了，才有力气……'],682,141,881)
            if t>2.2:
                text(im,'休息。',1065,777,53,BLUE,True,'center')
                text(im,'z',1365,467-math.sin(t)*9,37,BLUE)
                text(im,'Z',1407,406-math.sin(t+.5)*10,47,BLUE)
    elif k=='together':
        person(im,640,896,t,.94,'sleep')
        fish(im,4,1091,865,t,518,'sleep')
        # A shared knitted blanket is procedurally drawn over both laps.
        rr(im,(434,765,1225,874),30,'#b8c8bd',outline='#9daf9f',width=3)
        d=ImageDraw.Draw(im)
        for x in range(458,1200,32):d.line((x,776,x-5,862),fill='#d0ddd0',width=3)
        if not clean:
            rr(im,(630,127,1291,316),27,'#fff7e8')
            text(im,'原来，今天没电的',960,145,56,INK,True,'center')
            text(im,'不止我一个。',960,232,56,BLUE,True,'center')
    elif k=='tea':
        person(im,628,897,t,.97,'happy',cup=t>3.3)
        fish(im,5,1275-65*ease(t/2),954,t,667)
        steam(im,1078,561,t,.6)
        if not clean:
            bubble(im,['这杯，真的给你。'],864,148,786)
            if t>3.3:text(im,'（这次没有偷偷喝掉）',969,876,30,MUTED)
    elif k=='end':
        person(im,663,894,t,.98,'happy',True)
        fish(im,5,1226,952,t,620)
        # A second bowl physically slides into the foreground.
        rr(im,(571,896,1092,922),13,'#bd9876');rr(im,(618,919,642,973),6,'#a4876b');rr(im,(1035,919,1059,973),6,'#a4876b')
        bowl(im,819+120*(1-ease(t/2)),887,t,False,.7)
        if not clean:
            rr(im,(547,124,1377,323),27,'#fff7e8')
            text(im,'假期结束了。',960,145,66,INK,True,'center')
            text(im,'你可以慢慢回来。',960,242,67,BLUE,True,'center')
    else:
        # End credits are also a gentle provenance explainer, not a tech pitch.
        im=Image.new('RGB',(W,H),CREAM)
        fish(im,1,1460,947,t,631)
        rr(im,(88,174,1187,865),36,'#fff8eb',outline='#dfccb4',width=3)
        if not clean:
            text(im,'这条鱼，是大家接力画出来的。',132,214,48,INK,True)
            text(im,'角色原型「溟月」  上善无形',132,334,35,BLUE,True)
            text(im,'女仆版设计与三视图  ZipZipPipe',132,419,35,BLUE,True)
            text(im,'本片绘本衍生美术与动画  梨希 Lyxii / AI 辅助',132,514,29,INK)
            text(im,'CC BY-NC-SA 4.0',132,633,41,INK,True)
            text(im,'署名 · 非商业使用 · 相同方式共享',132,708,31,MUTED)
            text(im,'原帖链接和改编说明见视频简介',132,786,27,MUTED)
    if not clean:
        header(im)
        caption=s['caption']
        if k=='full' and t>=2.8:caption='你这吃白饭的蓝色大肥鱼！'
        if k=='sleep':caption='吃饱了，才有力气……' if t<2.2 else '休息。'
        if k=='together' and t>=3.5:caption='那就一起歇五分钟吧。'
        if k=='end' and t>=3.5:caption='先吃饭。再去做一件小小的事。'
        footer(im,caption)
    # Slow floating dust motes in the window light, no random frame flicker.
    d=ImageDraw.Draw(im)
    if k!='credits':
        for i in range(9):
            px=147+i*31+math.sin(now*.21+i)*15;py=590-(now*9+i*57)%400
            d.ellipse((px,py,px+3,py+3),fill='#faf3df')
    fade=1
    if now<.22:fade=ease(now/.22)
    if now>TOTAL-.8:fade=ease((TOTAL-now)/.8)
    if fade<1:im=Image.blend(Image.new('RGB',(W,H),CREAM),im,fade)
    return im

def ts(s):
    ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{sec:02},{ms:03}'

def subtitles():
    cues=[(0,5,'人回来了，电量没回来。'),(5,10,'人，你怎么比我还像在摸鱼？'),
          (10,16,'别急。先吃一碗热乎的。'),(16,21,'等一下……这碗不是给我的吗？'),
          (21,23.8,'我帮你试过了。很好吃。'),(23.8,27,'你这吃白饭的蓝色大肥鱼！'),
          (27,29.2,'吃饱了，才有力气……'),(29.2,33,'休息。'),
          (33,36.5,'原来，今天没电的不止我一个。'),(36.5,40,'那就一起歇五分钟吧。'),
          (40,47,'这杯，真的给你。'),(47,50.5,'假期结束了。你可以慢慢回来。'),
          (50.5,56,'先吃饭。再去做一件小小的事。'),
          (56,64,'非官方同人小剧场。原型：上善无形；女仆版：ZipZipPipe。CC BY-NC-SA 4.0。')]
    s='\n\n'.join(f'{i+1}\n{ts(a)} --> {ts(b)}\n{c}' for i,(a,b,c) in enumerate(cues))+'\n'
    (ROOT/'deliverables/Lyxii_EP02.srt').write_text(s,'utf-8')
    (ROOT/'qa/subtitle_cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),'utf-8')

def note_freq(n):return 440*2**((n-69)/12)

def make_audio():
    # A newly composed score, no sampled song or copied melody.
    n=TOTAL*SR;mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(71)
    def add(at,midi,dur,amp=.09,pan=0,kind='bell'):
        start=round(at*SR);length=min(round(dur*SR),n-start)
        if length<=0:return
        tt=np.arange(length)/SR;f=note_freq(midi)
        if kind=='bell':
            v=(np.sin(2*np.pi*f*tt)+.24*np.sin(2*np.pi*f*2.01*tt)+.10*np.sin(2*np.pi*f*3.99*tt))*np.exp(-tt*3.1)
        elif kind=='pluck':
            v=(np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*f*2*tt)+.12*np.sin(2*np.pi*f*3*tt))*np.exp(-tt*4.5)
        else:
            v=(np.sin(2*np.pi*f*tt)+.08*np.sin(2*np.pi*f*2*tt))*np.minimum(tt/.08,1)*np.minimum((dur-tt)/.22,1)*np.exp(-tt*.9)
        v*=np.minimum(tt/.008,1)*amp
        for channel,gain in enumerate([(1-pan)*.7,(1+pan)*.7]):mix[start:start+length,channel]+=v*gain
    # 80 BPM, C major / A minor / F major / G suspended.
    beat=.75;chords=[[48,55,60,64],[45,52,57,60],[41,48,53,57],[43,50,55,60]]
    melody=[72,76,79,76,74,72,None,71,69,72,76,72,71,69,None,67,
            69,72,77,76,74,72,None,69,71,74,79,77,76,74,72,None]
    for bar in range(21):
        at=bar*3;ch=chords[bar%4]
        if at>=63:break
        amp=.055 if 27<=at<40 else .078
        for j,nn in enumerate(ch):add(at+j*.015,nn,2.9,.038,(-1 if j%2 else 1)*.22,'pad')
        for j in range(8):add(at+j*beat/2,ch[(j*3)%4]+12,1.4,amp*.50,math.sin(j)*.32,'pluck')
        for j in range(2):
            mm=melody[(bar*2+j)%len(melody)]
            if mm is not None:add(at+j*1.5+.06,mm,2.4,amp,.23 if j else -.18)
    # Gentle scene accents and a brief music dip around the comic cut.
    for at in [5.75,10,16,23.8,29.2,40,47]:
        if at==16:add(at,84,.6,.13,0,'pluck');add(at+.12,79,.8,.09,0,'pluck')
        elif at==23.8:add(at,72,.8,.1);add(at+.13,76,.8,.07)
        elif at==40:
            for j,nn in enumerate([72,76,79]):add(at+j*.16,nn,1.5,.08)
        else:add(at,76,1.2,.055)
    # Very quiet soft shaker pulse, synthesized locally rather than a sample.
    for at in np.arange(0,63,beat):
        start=round(at*SR);ln=2400;tt=np.arange(ln)/SR
        noise=rng.normal(0,1,ln);v=np.diff(noise,prepend=0)*np.exp(-tt*75)*.0022
        mix[start:start+ln,0]+=v;mix[start:start+ln,1]+=v
    # Small stereo delay provides room tone with controlled level.
    delay=round(.13*SR);dry=mix.copy();mix[delay:,0]+=dry[:-delay,1]*.11;mix[delay:,1]+=dry[:-delay,0]*.11
    ramp=np.minimum(np.arange(n)/(SR*.5),1)*np.minimum((n-np.arange(n))/(SR*1.25),1)
    mix*=ramp[:,None]
    peak=float(np.max(np.abs(mix)))
    if peak>.85:mix*=.85/peak
    path=ROOT/'production/mix.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(np.int16(np.clip(mix,-1,1)*32767).tobytes())
    (ROOT/'qa/audio_source.json').write_text(json.dumps({'source':'new original procedural composition','title':'慢慢回来','composer':'Lyxii / AI-assisted code','sample_rate':SR,'duration':TOTAL,'pre_normalization_peak':peak,'copied_song':False},ensure_ascii=False,indent=2),'utf-8')

def previews():
    sheets=[];allbounds=[]
    for s in STORY:
        now=s['start']+s['duration']*.55
        im=frame_at(now);im.save(ROOT/f'qa/frame_{s["id"]}.jpg',quality=94)
        allbounds.extend([(s['id'],)+b for b in TEXT_BOUNDS if b[1]>250 or b[2]<550])
        cell=Image.new('RGB',(640,395),CREAM);cell.paste(im.resize((640,360)),(0,0))
        text(cell,f'{now:.1f}s  /  {s["id"]}',18,371,18,MUTED);sheets.append(cell)
    sheet=Image.new('RGB',(1920,395*math.ceil(len(sheets)/3)),CREAM)
    for i,p in enumerate(sheets):sheet.paste(p,(i%3*640,i//3*395))
    sheet.save(ROOT/'qa/storyboard.jpg',quality=94)
    # Cover tells the actual story, not an AI capability pitch.
    im=room().copy();person(im,554,963,0,.83,'tired');fish(im,3,1296,1012,0,787)
    # All important cover content stays inside the central 4:3 crop as well.
    rr(im,(246,115,1015,454),36,'#fff8e9',outline='#d8c4ac')
    text(im,'假期结束了',280,150,103,INK,True)
    text(im,'大肥鱼也没电了',280,304,77,BLUE,True)
    text(im,'一碗白饭引发的休息',280,479,35,MUTED)
    text(im,'梨希 Lyxii · 同人小剧场',280,987,29,BLUE)
    im.save(ROOT/'deliverables/Lyxii_EP02_cover.jpg',quality=97)
    # Clean image for optional image-to-video experiments; not used in this cut.
    frame_at(12,True).save(ROOT/'qa/clean_rice_scene.png')
    (ROOT/'qa/text_bounds.json').write_text(json.dumps(allbounds,ensure_ascii=False,indent=2),'utf-8')

def mux():
    wav=ROOT/'production/mix.wav';picture=ROOT/'production/picture.mp4'
    measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(wav),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    raw=measure.stderr;stats=json.JSONDecoder().raw_decode(raw[raw.rfind('{'):])[0]
    (ROOT/'qa/audio_loudness.json').write_text(json.dumps(stats,indent=2),'utf-8')
    filt=f"loudnorm=I=-18:TP=-2:LRA=7:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
    subprocess.run(['ffmpeg','-y','-v','warning','-i',str(picture),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(SR),'-af',filt,'-t',str(TOTAL),'-movflags','+faststart',str(ROOT/'deliverables/Lyxii_EP02.mp4')],check=True)

def film():
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'production/picture.mp4')]
    start=time.time()
    with (ROOT/'production/encode.log').open('w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(TOTAL*FPS):
                p.stdin.write(frame_at(n/FPS).tobytes())
                if n%(FPS*5)==0:print(f'{n/FPS:.0f}/{TOTAL}s | elapsed {time.time()-start:.1f}s',flush=True)
            p.stdin.close()
            if p.wait()!=0:raise RuntimeError('FFmpeg failed; see encode.log')
        except Exception:
            p.kill();raise
    mux();print('FINISHED',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--previews',action='store_true');parser.add_argument('--frame',type=float);parser.add_argument('--mux',action='store_true');args=parser.parse_args()
    for folder in ['qa','deliverables','production']:(ROOT/folder).mkdir(exist_ok=True)
    if args.previews:subtitles();previews();make_audio()
    elif args.frame is not None:frame_at(args.frame).save(ROOT/'qa/sample.png')
    elif args.mux:mux()
    else:subtitles();previews();make_audio();film()
