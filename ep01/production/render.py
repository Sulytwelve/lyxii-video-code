"""Original layered motion graphics, 1920x1080 / 30fps. No third-party footage."""
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from pathlib import Path
from functools import lru_cache
import json,math,subprocess,sys,time,random,re
import numpy as np
ROOT=Path(__file__).resolve().parents[1];W,H=1920,1080;FPS=30
PINK='#f4b4cf';LILAC='#c6b3f3';MINT='#a6e5cf';WHITE='#fff1f7';DIM='#b7a5be';BG='#17141f';PANEL='#27212f';LINE='#49394f';ORANGE='#f3bc91'
STORY=json.loads((ROOT/'production'/'timeline.json').read_text('utf-8'))
@lru_cache(64)
def font(size,bold=False,mono=False):
    return ImageFont.truetype('C:/Windows/Fonts/consola.ttf' if mono else ('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc'),size)
@lru_cache(700)
def tx(text,size=38,color=WHITE,bold=False,mono=False):
    if any(ord(c)>127 for c in text):mono=False
    f=font(size,bold,mono);b=f.getbbox(text);im=Image.new('RGBA',(max(1,b[2]+8),size*2),(0,0,0,0));ImageDraw.Draw(im).text((2,-b[1]+3),text,font=f,fill=color);return im.crop((0,0,im.width,b[3]-b[1]+9))
def text(im,s,xy,size=38,color=WHITE,bold=False,mono=False,anchor='left'):
    p=tx(str(s),size,color,bold,mono);x,y=xy
    if anchor=='center':x-=p.width/2
    elif anchor=='right':x-=p.width
    im.paste(p,(int(x),int(y)),p)
def rr(im,box,r=22,fill=PANEL,outline=None,width=2):ImageDraw.Draw(im).rounded_rectangle(tuple(int(a) for a in box),radius=r,fill=fill,outline=outline,width=width)
def line(im,points,fill=LINE,width=2):ImageDraw.Draw(im).line(points,fill=fill,width=width)
def ease(v):v=max(0,min(1,v));return 1-(1-v)**3
def alpha_paste(im,layer,x,y):im.paste(layer,(int(x),int(y)),layer if layer.mode=='RGBA' else None)
@lru_cache(40)
def asset(name,w,h,mode='fit'):
    a=Image.open(ROOT/'assets'/name).convert('RGBA')
    if mode=='fit':return ImageOps.fit(a,(w,h),method=Image.Resampling.LANCZOS)
    return ImageOps.contain(a,(w,h),method=Image.Resampling.LANCZOS)
front=Image.open(ROOT/'assets'/'lyxii_turnaround.png').convert('RGBA').crop((0,0,530,1086))
front=ImageOps.contain(front,(475,770),method=Image.Resampling.LANCZOS)
def char(im,x,y,t,scale=1):
    a=front if scale==1 else front.resize((int(front.width*scale),int(front.height*scale)),Image.Resampling.LANCZOS)
    alpha_paste(im,a,x,y+math.sin(t*1.7)*5)
def avatar(im,x,y,size=180):
    p=asset('lyxii_portrait.png',size,size);m=Image.new('L',(size,size));ImageDraw.Draw(m).ellipse((0,0,size-1,size-1),fill=255);im.paste(p,(int(x),int(y)),m)
def robot(im,x,y,t,scale=1,mood='normal'):
    # A little original code terminal mascot, with a moving face and hinged arms.
    s=scale;bob=math.sin(t*3)*7*s;y+=bob
    def B(a,b,c,d):return (x+a*s,y+b*s,x+c*s,y+d*s)
    d=ImageDraw.Draw(im);d.ellipse(B(2,290,272,320),fill='#110e18')
    d.line([(x+137*s,y+16*s),(x+137*s,y-35*s)],fill=LILAC,width=max(2,int(6*s)))
    d.ellipse(B(124,-55,150,-29),fill=PINK)
    rr(im,B(0,0,275,210),int(34*s),fill='#cbb3ec',outline='#efd2e5',width=max(2,int(3*s)))
    rr(im,B(23,26,252,180),int(20*s),fill='#292036')
    eye_y=86 if mood!='tired' else 102
    blink=(t%4.7)>4.54
    if mood=='shock':
        d.ellipse(B(58,65,91,110),outline=MINT,width=max(2,int(5*s)));d.ellipse(B(180,65,213,110),outline=MINT,width=max(2,int(5*s)))
        d.ellipse(B(122,127,150,156),outline=PINK,width=max(2,int(4*s)))
    else:
        eh=4 if blink else (13 if mood=='tired' else 27)
        rr(im,B(61,eye_y,87,eye_y+eh),int(5*s),fill=MINT);rr(im,B(183,eye_y,209,eye_y+eh),int(5*s),fill=MINT)
        d.line([(x+119*s,y+144*s),(x+154*s,y+144*s)],fill=PINK,width=max(2,int(5*s)))
    rr(im,B(44,211,231,284),int(17*s),fill='#776187',outline=LINE)
    text(im,'{ }',(x+110*s,y+222*s),int(34*s),MINT,mono=True)
    d.line([(x+44*s,y+236*s),(x-31*s,y+(240+math.sin(t*2)*24)*s)],fill=LILAC,width=max(2,int(17*s)))
    d.line([(x+231*s,y+236*s),(x+303*s,y+(210+math.cos(t*2)*23)*s)],fill=LILAC,width=max(2,int(17*s)))
    rr(im,B(60,279,100,308),int(8*s),fill=LILAC);rr(im,B(178,279,218,308),int(8*s),fill=LILAC)
def pill(im,s,x,y,color=MINT,size=25):
    a=tx(s,size,color);rr(im,(x,y,x+a.width+32,y+a.height+22),20,fill='#25212e',outline=LINE);text(im,s,(x+16,y+10),size,color)
def arrow(im,a,b,color=DIM,width=4):
    line(im,[a,b],color,width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);p=[b,(b[0]-18*math.cos(ang-.5),b[1]-18*math.sin(ang-.5)),(b[0]-18*math.cos(ang+.5),b[1]-18*math.sin(ang+.5))];ImageDraw.Draw(im).polygon(p,fill=color)
def title(im,s,kicker=None):
    if kicker:text(im,kicker,(110,148),25,PINK,mono=True)
    text(im,s,(110,206),64,WHITE,True)
def window(im,box,label='LYXII LAB',color=PANEL):
    rr(im,box,24,fill=color,outline=LINE);x,y,_,_=box
    for i,c in enumerate([PINK,ORANGE,MINT]):ImageDraw.Draw(im).ellipse((x+25+i*27,y+22,x+38+i*27,y+35),fill=c)
    text(im,label,(x+125,y+16),24,DIM,mono=True)
    line(im,[(box[0]+1,y+55),(box[2]-1,y+55)],LINE,2)
def monitor(im,t,x=680,y=285,w=920,h=480,label='LOCAL WORKSPACE'):
    window(im,(x,y,x+w,y+h),label);rr(im,(x+w//2-45,y+h,x+w//2+45,y+h+60),10,fill=LINE);rr(im,(x+w//2-190,y+h+60,x+w//2+190,y+h+82),12,fill='#62516b')
def document(im,x,y,w,h,label,amount=None):
    rr(im,(x,y,x+w,y+h),12,fill='#fbecf2');text(im,label,(x+30,y+35),30,'#65415f',True)
    line(im,[(x+30,y+100),(x+w-30,y+100)],'#d8bdcc',2)
    if amount:text(im,amount,(x+30,y+140),74,'#403046',True)
    for yy in range(y+250,y+h-35,35):line(im,[(x+32,yy),(x+w-32,yy)],'#decbd6',2)
    ImageDraw.Draw(im).polygon([(x+w-50,y),(x+w,y+50),(x+w-50,y+50)],fill='#dfc2d4')
def receipt(im,x,y,t):
    document(im,int(x),int(y),400,500,'本月订阅预算','¥150')
    text(im,'约 28.98 SGD',(x+32,y+228),26,'#70596e')
    pill(im,'谁来付？',x+225,y+370,ORANGE,30)
# Cached background with warm radial pools, subtle grid, and fixed branded chrome.
xx,yy=np.meshgrid(np.arange(W),np.arange(H));a=np.zeros((H,W,3),np.float32)+np.array([23,20,31])
for cx,cy,r,col in [(250,800,650,[24,8,17]),(1720,240,700,[8,5,23])]:
    g=np.exp(-((xx-cx)**2+(yy-cy)**2)/(r*r))[:,:,None];a+=g*np.array(col)
BASE=Image.fromarray(np.uint8(np.clip(a,0,255)));del a,xx,yy
d=ImageDraw.Draw(BASE)
for x in range(0,W,80):d.line((x,100,x,920),fill='#282030',width=1)
for y in range(120,920,80):d.line((0,y,W,y),fill='#282030',width=1)
text(BASE,'梨希 Lyxii',(110,45),29,PINK,True);text(BASE,'AI 自给自足实验 / EP.01',(355,49),24,DIM)
rr(BASE,(1560,33,1812,94),20,fill='#28212c',outline=LINE);text(BASE,'实际收入  ¥0',(1582,47),28,MINT,True)
line(BASE,[(110,113),(1810,113)],LINE)
def background(s,t):
    im=BASE.copy();text(im,s['chapter'],(110,120),22,DIM)
    # Persistent drifting pixels, not random frame noise.
    d=ImageDraw.Draw(im)
    for j in range(14):
        px=(j*137+42+math.sin(t*.2+j)*15)%W;py=170+(j*109+t*8)%720
        d.ellipse((px,py,px+3,py+3),fill='#6d4b6a')
    return im
def photo_card(im,name,box,label,t):
    x,y,w,h=box;rr(im,(x-3,y-3,x+w+3,y+h+3),16,fill=LINE)
    a=asset(name,w,h);alpha_paste(im,a,x,y)
    rr(im,(x,y+h-55,x+w,y+h),0,fill='#221c2a');text(im,label,(x+20,y+h-42),23,WHITE)
def screen_asset(im,name,x,y,w,h,offset=0):
    a=screen_crop(name,w,h,int(offset))
    im.paste(a,(int(x),int(y)))
@lru_cache(128)
def screen_crop(name,w,h,offset=0):
    a=Image.open(ROOT/'assets'/name).convert('RGB')
    # Crop inside the app/document only, then enlarge for legibility.
    a=a.crop((0,int(offset),a.width,min(a.height,int(offset)+round(a.width*h/w))))
    a=ImageOps.fit(a,(w,h),method=Image.Resampling.LANCZOS)
    return a
def progress(im,t,total):
    rr(im,(110,1046,1810,1052),3,fill='#3b2d43');rr(im,(110,1046,110+1700*min(t/total,1),1052),3,fill=PINK)
def render(s,local,absolute):
    k=s['kind'];t=local;dur=s['duration'];v=t/dur;im=background(s,absolute);dr=ImageDraw.Draw(im)
    if k=='invoice':
        text(im,'每个月，我在养 AI。',(110,235),70,WHITE,True)
        text(im,'这次能不能反过来？',(110,334),61,PINK,True)
        pill(im,'月目标 ¥150 / 半程目标 ¥75',110,448,LILAC,27)
        robot(im,1370,540,t,1.18,mood='shock')
        receipt(im,890+240*(1-ease(t/1.1)),265-30*ease(t/1.1),t)
        arrow(im,(1340,470),(1500,495),PINK)
        text(im,'AI 合成旁白 · 情景化表达',(110,828),23,DIM)
        # Empty wallet: expressive motion, while the actual-revenue counter stays zero.
        if t>3:
            wx=1390+math.sin(t*12)*5
            rr(im,(wx,800,wx+210,874),15,fill='#493546',outline=PINK)
            text(im,'¥0',(wx+105,811),43,ORANGE,True,anchor='center')
    elif k=='dialog':
        avatar(im,170,255,300);robot(im,1270,400,t,1.4,mood='tired')
        text(im,'梨希',(260,598),31,PINK);text(im,'Codex · 角色演绎',(1240,855),24,LILAC)
        window(im,(590,245,1660,440),'MESSAGE / 001')
        if s['speaker']=='ai':
            text(im,'目标已记录。',(640,330),43,LILAC,True);text(im,'收入：',(650,530),39,DIM)
            text(im,'0',(650,610),180,MINT,True);text(im,'元',(795,744),45,DIM)
        else:
            text(im,'报表技能 +1',(640,330),48,PINK,True)
            text(im,'收款技能',(660,564),43,DIM);pill(im,'尚未解锁',660,652,ORANGE,37)
            for i in range(5):rr(im,(670+i*70,735,725+i*70,753),5,fill=LINE)
    elif k in ['identity','character']:
        # A large portrait moving slowly behind a dedicated typographic foreground.
        a=asset('lyxii_daily.png',800,850);alpha_paste(im,a,1050,145-int(10*math.sin(t*.15)))
        char(im,805,210,t,.87)
        text(im,'梨希',(110,263),120,PINK,True);text(im,'Lyxii',(113,424),94,WHITE,True)
        text(im,'会写代码，也想把故事讲好。',(110,589),38,LILAC)
        if k=='character':
            rr(im,(104,705,1040,874),22,fill='#3b293c',outline=PINK)
            text(im,'当前形象：ChatGPT 临时生成',(135,737),38,WHITE,True)
            text(im,'后续会找画师另外设计',(135,804),31,PINK)
        else:
            pill(im,'独立软件开发',112,707,MINT);pill(im,'AI 创作内容',350,707,LILAC)
            text(im,'这不是第一段折腾，是一个新系列的开始。',(110,821),26,DIM)
    elif k in ['budget','target','zero']:
        title(im,'先把账算清楚。','SUBSCRIPTION / BUDGET')
        if k=='budget':
            receipt(im,130,330,t);arrow(im,(600,575),(780,575),LILAC,7)
            text(im,'¥150',(840,388),180,PINK,True);text(im,'每月预算目标',(852,628),43,WHITE)
            pill(im,'28.98 SGD / 用户提供的费用估算',810,738,DIM,25);robot(im,1500,560,t,.8)
        elif k=='target':
            for i,(n,l,c)in enumerate([('75','半程也有意义',LILAC),('150','理想月目标',PINK)]):
                x=130+i*880;window(im,(x,352,x+740,812),'MONTHLY TARGET')
                text(im,'¥'+n,(x+50,466),140,c,True);text(im,l,(x+56,668),39,WHITE)
                rr(im,(x+50,747,x+685,765),8,fill=LINE);rr(im,(x+50,747,x+50+635*(.5 if i==0 else 1)*ease(t/3),765),8,fill=c)
            text(im,'进度条表示目标关系，不是已赚金额。',(110,861),25,DIM)
        else:
            text(im,'0',(660,304),370,MINT,True);text(im,'元',(944,624),68,DIM)
            robot(im,1250,534,t,1.1,'tired');char(im,145,280,t,.75)
            pill(im,'没有收入 / 没有客户 / 从零开始',617,800,PINK,28)
    elif k in ['portfolio','apps']:
        title(im,'不是从空文件夹开始。','EXISTING WORK / 公开作品')
        char(im,70,323,t,.76)
        if k=='portfolio':
            window(im,(505,315,1190,897),'sulyhub.cn / apps')
            screen_asset(im,'lily_apps.png',525,380,645,487,offset=int(t*14))
            window(im,(1230,360,1810,827),'lily-nest / Rust')
            for i,st in enumerate(['梨窝','纯 Rust 个人网站','门户 / 笔记 / 应用','继续做轻量作品']):text(im,st,(1260,440+i*83),44 if i==0 else 29,PINK if i==0 else WHITE,i==0)
            text(im,'已存在的项目，不计为本实验收入。',(1250,856),25,DIM)
        else:
            window(im,(465,312,1070,890),'cURL → Code')
            screen_asset(im,'curl_code.png',485,374,565,485,offset=int(t*8))
            window(im,(1110,315,1810,890),'Formula Atelier / 概念示意')
            text(im,'F = ma',(1150,410),90,LILAC,True,mono=True)
            for i in range(9):
                x=1180+i*65;y=684-80*math.sin(t+i*.6);dr.ellipse((x,y,x+20,y+20),fill=PINK)
            line(im,[(1160,770),(1760,770)],DIM);text(im,'把公式变成可玩的东西',(1150,813),32,WHITE)
    elif k=='machine':
        title(im,'先用手边的能力。','NO EXTRA BILL')
        monitor(im,t,610,329,1120,430);char(im,100,277,t,.8)
        text(im,'LOCAL / Windows 11',(660,425),36,LILAC,mono=True)
        for i,st in enumerate(['Ryzen 7 7840HS / Radeon 780M','32 GB RAM','Rust  ·  Python  ·  嵌入式  ·  AI']):text(im,st,(660,509+i*78),34,WHITE,mono=i<2)
        pill(im,'先做不依赖额外付费 API 的工具',634,835,MINT,29)
    elif k=='candidates':
        title(im,'AI 打工面试。','SCOPE / 一次只验证一件事')
        items=[('大软件','维护压力大',LILAC),('批量内容','容易流水线化',ORANGE),('小工具','问题明确，先试它',MINT)]
        for i,(a,b,c)in enumerate(items):
            x=110+i*577;y=360+int((1-ease((t-i*.35)/.7))*120)
            window(im,(x,y,x+535,y+400),f'CANDIDATE / 0{i+1}')
            text(im,a,(x+36,y+100),57,c,True);text(im,b,(x+36,y+221),31,WHITE)
            if i==2:pill(im,'本期选择',x+35,y+300,MINT,30)
            else:line(im,[(x+35,y+336),(x+490,y+336)],LINE,5)
        robot(im,1590,808,t,.34)
    elif k=='pain':
        title(im,'字幕：我先下班了。','CREATOR PROBLEM / 测试场景')
        window(im,(290,323,1510,792),'VIDEO PREVIEW / 模拟画面')
        robot(im,760,419,t,.8,'shock')
        for i in range(50):
            x=335+i*23;y=724;h=10+abs(math.sin(i*.8+t*4))*48
            line(im,[(x,y-h),(x,y+h)],LILAC,5)
        blink=int(t*3.333)%4==0
        if blink:rr(im,(402,597,1374,650),12,fill='#53344c');text(im,'这一长串字幕只给零点三秒……',(450,608),35,WHITE)
        pill(im,'重叠',1550,415,ORANGE,32);pill(im,'倒置',1550,507,PINK,32);pill(im,'太快',1550,599,LILAC,32)
        text(im,'你看完了吗？',(480,838),60,PINK,True)
    elif k=='brief':
        title(im,'第一份任务：梨字幕。','BRIEF / 小而具体')
        document(im,140,330,630,530,'交付清单')
        for i,st in enumerate(['离线打开','检查 SRT','保留原文','导出报告']):text(im,f'{i+1:02}  '+st,(185,465+i*85),45,'#493649',True)
        arrow(im,(840,587),(1080,587),PINK,7);robot(im,1320,481,t,1.1)
        pill(im,'需求假设 · 尚未验证付费意愿',990,794,ORANGE,29)
    elif k=='build':
        title(im,'从任务，到能运行的代码。','ACTUAL IMPLEMENTATION / 实际代码')
        window(im,(110,320,1370,885),'checker.js / 编排展示')
        code=['if (end <= start) {',"  add(n, 'error', '结束时间早于或等于开始时间');",'  return;','}',"if (end - start < 0.7)","  add(n, 'warning', '显示不足 0.7 秒');",'// 只检查，保留输入原文']
        # Excerpt of implemented logic; whitespace changed for readability.
        for i,st in enumerate(code):
            if t>.4*i:
                # Typewriter build, rather than revealing a complete static slide.
                shown=st[:min(len(st),int(max(0,t-.4*i)*38))]
                text(im,shown,(145,410+i*52),29,MINT if i in [0,6] else WHITE,mono=True)
        text(im,'实际逻辑节选，排版调整 · 完整源码随视频交付',(140,825),24,DIM)
        robot(im,1490,458,t,.86);pill(im,'无需 API',1435,795,MINT,29)
    elif k in ['demo_bad','demo_good']:
        title(im,'实测：'+('4 条字幕 / 6 个问题' if k=='demo_bad' else '修订后，重新检查'),'ACTUAL UI / 真实原型界面')
        rr(im,(106,319,984,913),17,fill=LINE)
        a=asset('demo_bad.png' if k=='demo_bad' else 'demo_good.png',864,584,'contain');alpha_paste(im,a,113,325)
        c=Image.open(ROOT/'assets'/('demo_bad.png' if k=='demo_bad' else 'demo_good.png')).convert('RGB')
        c=c.crop((645,244,1216,774));c=ImageOps.contain(c,(710,575),method=Image.Resampling.LANCZOS)
        rr(im,(1080,319,1802,913),18,fill=LINE);im.paste(c,(1087,329))
        text(im,'结果放大',(1100,840),27,PINK)
        if k=='demo_good':pill(im,'预先人工修订的另一份样例',111,889,MINT,22)
        else:pill(im,'故意带错的演示数据',111,889,ORANGE,22)
    elif k in ['overlap','reverse','fast','limit']:
        title(im,{'overlap':'两条字幕，挤在同一秒。','reverse':'字幕试图穿越时间。','fast':'观众还没读完，它已经走了。','limit':'自动改时间，不一定是修好。'}[k],'TIMELINE / 演示数据可视化')
        window(im,(110,330,1810,880),'SRT / 时间线')
        x0=225;y0=695;width=1460
        for i in range(10):
            x=x0+i*width/9;line(im,[(x,440),(x,760)],'#46344c',2);text(im,str(i)+'s',(x,795),25,DIM,mono=True,anchor='center')
        if k=='overlap':
            rr(im,(x0,472,x0+2*width/9,536),10,fill='#765777');text(im,'#1 / 0.0 → 2.0',(x0+15,485),28,WHITE,mono=True)
            rr(im,(x0+1.8*width/9,579,x0+3.6*width/9,643),10,fill='#7c4c59');text(im,'#2 / 1.8 → 3.6',(x0+1.8*width/9+10,592),27,WHITE,mono=True)
            overlap_x=x0+1.8*width/9
            dr.rectangle((overlap_x,455,x0+2*width/9,664),outline=PINK,width=4)
            pill(im,'重叠 0.2 秒',1005,509,PINK,42);pill(im,'另有：编号不连续 / 重复编号',920,667,ORANGE,27)
        elif k=='reverse':
            a=x0+4*width/9;b=x0+3.5*width/9
            arrow(im,(a,550),(b,550),ORANGE,10);text(im,'4.0s',(a+25,463),55,PINK,True);text(im,'3.5s',(b-200,586),55,LILAC,True)
            text(im,'开始',(a+35,533),29,DIM);text(im,'结束',(b-130,656),29,DIM)
            robot(im,1300,437,t,.7,'shock');pill(im,'结束 ≤ 开始 → 错误',1080,733,ORANGE,31)
        elif k=='fast':
            rr(im,(x0+4.2*width/9,500,x0+4.5*width/9,612),6,fill=PINK)
            text(im,'0.3 秒',(1010,421),94,ORANGE,True)
            blink=(t%3)<.3
            if blink:text(im,'这一大长串字幕只给零点三秒真的来得及看完吗？',(200,677),44,WHITE)
            else:text(im,'（字幕已经消失了）',(570,677),44,DIM)
            pill(im,'过短提示 + 阅读速度提示',980,790,LILAC,27)
        else:
            for j,st in enumerate(['声音','原字幕','自动后移']):text(im,st,(140,435+j*125),31,DIM)
            for j in range(3):
                offset=0 if j<2 else 120
                rr(im,(490+offset,442+j*125,805+offset,488+j*125),8,fill=MINT if j==0 else PINK)
                rr(im,(800+offset,442+j*125,1150+offset,488+j*125),8,fill=LILAC)
            arrow(im,(1360,490),(1360,700),ORANGE,6);text(im,'画面修好了？',(1410,510),31,WHITE);text(im,'声音可能错位。',(1410,616),31,ORANGE)
            pill(im,'只报问题 · 不擅自改写',1270,787,MINT,27)
        play=x0+(t%7)/7*width;line(im,[(play,416),(play,770)],'#f5d8e4',3)
        dr.polygon([(play-9,416),(play+9,416),(play,430)],fill=WHITE)
    elif k=='tests':
        title(im,'不能只在“正常样例”里正常。','VALIDATION / 实际测试结果')
        window(im,(110,319,1360,888),'node tool/test.cjs / 真实结果编排')
        names=['正常字幕','边界相接不重叠','嵌套字幕也能发现重叠','倒置时间','非法分钟','空正文','重复编号','BOM 与 Windows 换行','不修改输入','高速阅读提示','空文件','没有时间码']
        n=min(12,int(t*2)+1)
        for i,st in enumerate(names[:n]):
            col=i//6;row=i%6;text(im,'PASS',(145+col*580,414+row*61),30,MINT,True,True);text(im,st,(252+col*580,414+row*61),28,WHITE)
        text(im,f'{n:02} / 12',(1440,434),78,MINT,True,True);robot(im,1480,641,t,.64)
    elif k in ['product','market']:
        title(im,'有代码 ≠ 有人买。','REALITY CHECK / 需求尚未验证')
        window(im,(140,361,790,852),'DELIVERED / 本期原型')
        text(im,'梨字幕',(195,472),75,PINK,True);pill(im,'能运行',197,601,MINT,38)
        arrow(im,(875,588),(1100,588),DIM,6)
        window(im,(1180,361,1790,852),'MARKET / 待验证')
        text(im,'?',(1400,430),170,LILAC,True);text(im,'省事吗？值得支持吗？',(1228,689),33,WHITE)
        if k=='market':
            rr(im,(695,678,1183,806),19,fill='#523445',outline=PINK)
            text(im,'畅销标签：未解锁',(726,723),36,PINK,True)
        else:text(im,'这段路，不能用一句“已完成”跳过。',(835,842),29,DIM)
    elif k=='loop':
        title(im,'先验证，再继续开发。','FEEDBACK / 下一步计划')
        nodes=[(270,485,'试用',PINK),(740,485,'反馈',LILAC),(1210,485,'取舍',MINT)]
        for x,y,label,c in nodes:
            rr(im,(x,y,x+360,y+210),25,fill=PANEL,outline=c,width=3);text(im,label,(x+180,y+73),62,c,True,anchor='center')
        arrow(im,(630,590),(735,590),PINK,5);arrow(im,(1100,590),(1205,590),LILAC,5)
        line(im,[(1390,720),(1390,805),(450,805),(450,715)],LINE,4);arrow(im,(450,745),(450,715),MINT,5)
        p=(t%6)/6;dr.ellipse((320+1280*p,782,344+1280*p,806),fill=MINT)
        text(im,'先问：哪里真的省事？哪里根本多余？',(270,852),32,WHITE)
        pill(im,'未进行用户采访 / 尚未收集反馈',115,340,ORANGE,25)
    elif k=='channels':
        title(im,'作品与内容，互相推动。','INDEPENDENT DEV + AI CONTENT')
        labels=[('软件','解决具体问题',PINK),('视频','记录过程',LILAC),('网站','展示作品',MINT),('爱发电','自愿支持',ORANGE)]
        for i,(a,b,c)in enumerate(labels):
            x=110+i*433;window(im,(x,423,x+392,761),'EXISTING CHANNEL')
            text(im,a,(x+36,510),56,c,True);text(im,b,(x+36,618),29,WHITE)
            if i<3:arrow(im,(x+394,588),(x+428,588),DIM,3)
            q=((t+i*.7)%3)/3
            rr(im,(x+40+280*q,713,x+75+280*q,736),7,fill=c)
        text(im,'有渠道 ≠ 已有收入',(650,811),54,PINK,True)
        text(im,'sulyhub.cn   /   ifdian.net/a/Lyxii',(480,343),31,DIM,mono=True)
    elif k=='ledger':
        title(im,'收入，和成本分开记。','LEDGER / 后续记录规则')
        rows=[('销售收入','¥0',MINT),('自愿赞助','¥0',MINT),('退款 / 手续费','单列',ORANGE),('额外工具开销','单列',ORANGE),('人工时间','另记，不算免费',LILAC)]
        window(im,(120,335,1170,888),'本期收入为零 / 后续逐项记账')
        for i,(a,b,c)in enumerate(rows):
            y=428+i*81;text(im,a,(166,y),36,WHITE);text(im,b,(1100,y),36,c,True,anchor='right');line(im,[(165,y+61),(1110,y+61)],LINE)
        robot(im,1440,530,t,.95,'tired');pill(im,'先看净贡献，再谈养活订阅',1240,796,PINK,25)
    elif k=='math':
        title(im,'这个目标，到底有多小？','HYPOTHESIS / 仅作算术演示')
        pill(im,'假设每份净贡献 ¥15',110,331,ORANGE,35)
        for i in range(10):
            if t<.5+i*.28:continue
            x=130+(i%5)*225;y=446+(i//5)*180
            rr(im,(x,y,x+185,y+133),18,fill='#433047' if i<5 else '#49304a',outline=LILAC if i<5 else PINK)
            text(im,'¥15',(x+92,y+41),52,LILAC if i<5 else PINK,True,anchor='center')
        if t>1.6:text(im,'5 份 → ¥75',(1338,478),48,LILAC,True)
        if t>3.0:text(im,'10 份 → ¥150',(1278,674),48,PINK,True)
        text(im,'不是定价 / 不是销量预测',(110,859),31,DIM)
    elif k=='boundary':
        title(im,'AI 去工作，我来负责。','RESPONSIBILITY / 合作实验')
        robot(im,305,420,t,1.1);char(im,1310,270,t,.82)
        text(im,'Codex',(276,847),37,LILAC,True);text(im,'梨希',(1400,847),37,PINK,True)
        rr(im,(720,350,1150,833),26,fill=PANEL,outline=LINE)
        for i,(a,c)in enumerate([('构思 / 开发 / 制作',LILAC),('审核 / 发布 / 收款',PINK)]):text(im,a,(935,463+i*187),31,c,True,anchor='center')
        arrow(im,(612,620),(714,620),LILAC,6);arrow(im,(1158,620),(1280,620),PINK,6)
    elif k=='schedule':
        title(im,'现在先做视频。','RECORD / 以后条件合适再直播')
        photo_card(im,'lyxii_daily.png',(1180,283,550,605),'梨希 Lyxii',t)
        window(im,(110,352,1050,819),'CREATOR WORKSPACE')
        text(im,'视频记录',(180,458),80,PINK,True)
        for i in range(36):
            x=190+i*21;y=633;h=15+math.sin(t*2+i*.7)**2*62;line(im,[(x,y-h),(x,y+h)],LILAC,7)
        pill(im,'未来：开发直播 + 互动',172,750,MINT,27)
    elif k=='score':
        title(im,'第一期结算。','EXPERIMENT / DAY ZERO')
        document(im,160,327,735,565,'实际交付')
        text(im,'01  可运行的原型',(200,460),43,'#493649',True);text(im,'02  原创视频',(200,560),43,'#493649',True)
        text(im,'收入：¥0',(200,690),66,'#80556f',True)
        robot(im,1290,473,t,1.05,'tired');pill(im,'开工了，尚未回本。',1140,825,PINK,34)
    elif k=='end':
        char(im,1190,210,t,.9);robot(im,1580,656,t,.51)
        text(im,'你最想省掉',(110,256),82,WHITE,True);text(im,'创作中的哪一步？',(110,376),82,PINK,True)
        text(im,'下一步：先验证有没有人需要它。',(115,558),41,LILAC)
        pill(im,'梨希 Lyxii / AI 自给自足实验',110,690,MINT,31)
        text(im,'B 站：梨希Lyxii',(115,789),31,WHITE);text(im,'sulyhub.cn  ·  ifdian.net/a/Lyxii',(115,845),28,DIM,mono=True)
    return im
def sub_parse():
    raw=(ROOT/'deliverables'/'Lyxii_EP01.srt').read_text('utf-8');out=[]
    def sec(s):h,m,r=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(r)
    for b in raw.strip().split('\n\n'):
        ls=b.splitlines();a,z=ls[1].split(' --> ');out.append((sec(a),sec(z),' '.join(ls[2:])))
    return out
SUBS=sub_parse();TOTAL=sum(s['duration'] for s in STORY)+2
def caption(im,now):
    for a,b,st in SUBS:
        if a<=now<b:
            p=tx(st,40,WHITE);w=p.width+50;x=(W-w)//2
            # Dedicated safe area; no scene information below y=910.
            rr(im,(x,963,x+w,1030),12,fill='#120f1d');alpha_paste(im,p,x+25,975);break
def frame_at(now):
    s=next((s for s in STORY if s['start']<=now<s['start']+s['duration']),STORY[-1]);local=now-s['start']
    im=render(s,local,now);caption(im,now);progress(im,now,TOTAL)
    # Short fade-throughs on chapter changes, gentle beginning and end fades.
    f=1
    if now<.3:f=ease(now/.3)
    if now>TOTAL-1:f=max(0,(TOTAL-now))
    if f<1:im=Image.blend(Image.new('RGB',(W,H),BG),im,f)
    return im.convert('RGB')
def previews():
    pics=[]
    for s in STORY:
        im=frame_at(s['start']+min(4,s['duration']*.5));im.save(ROOT/'qa'/('frame_'+s['id']+'.jpg'),quality=92)
        a=im.resize((480,270));pad=Image.new('RGB',(480,306),BG);pad.paste(a,(0,0));text(pad,s['id']+' / '+str(round(s['start']))+'s',(8,278),18,WHITE);pics.append(pad)
    sheet=Image.new('RGB',(1920,306*math.ceil(len(pics)/4)),BG)
    for i,a in enumerate(pics):sheet.paste(a,((i%4)*480,(i//4)*306))
    sheet.save(ROOT/'qa'/'storyboard.jpg',quality=91)
def film():
    target=ROOT/'production'/'picture.mp4';log=open(ROOT/'production'/'encode-picture.log','w')
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);start=time.time()
    for n in range(round(TOTAL*FPS)):
        p.stdin.write(frame_at(n/FPS).tobytes())
        if n%(FPS*10)==0:print(f'{n/FPS:.0f}/{TOTAL:.1f}s | render {time.time()-start:.0f}s',flush=True)
    p.stdin.close();rc=p.wait();log.close()
    if rc:raise RuntimeError('picture encode failed')
    mux()
def mux():
    target=ROOT/'production'/'picture.mp4'
    # First pass obtains measured loudness. Second pass produces a controlled AAC mix.
    cmd=['ffmpeg','-hide_banner','-i',str(ROOT/'production'/'mix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');raw=r.stderr
    if r.returncode:raise RuntimeError(raw[-3000:])
    loud=json.JSONDecoder().raw_decode(raw[raw.rfind('{'):])[0];(ROOT/'qa'/'audio_loudness.json').write_text(json.dumps(loud,indent=2))
    filt=f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={loud['input_i']}:measured_TP={loud['input_tp']}:measured_LRA={loud['input_lra']}:measured_thresh={loud['input_thresh']}:offset={loud['target_offset']}:linear=true"
    subprocess.run(['ffmpeg','-y','-v','warning','-i',str(target),'-i',str(ROOT/'production'/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-af',filt,'-movflags','+faststart','-shortest',str(ROOT/'deliverables'/'Lyxii_EP01.mp4')],check=True)
    print('FINISHED',flush=True)
if __name__=='__main__':
    if '--previews' in sys.argv:previews()
    elif '--mux' in sys.argv:mux()
    elif '--frame' in sys.argv:frame_at(float(sys.argv[-1])).save(ROOT/'qa'/'sample.png')
    else:film()
