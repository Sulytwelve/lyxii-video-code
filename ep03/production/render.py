"""EP03: character sprite choreography, props and compositing made in Python.

No web-generated video is used. EP02 room/whale art remains unmodified.
Usage: --previews; --picture; --mux [--music FILE] [--music-start SECONDS].
"""
from pathlib import Path
from functools import lru_cache
import argparse, importlib.util, json, math, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS,SR,TOTAL=1920,1080,24,48000,54
CREAM,INK,BLUE,MUTED='#f5eddf','#494a59','#637fa8','#8d867d'
PURPLE,GREEN,GOLD='#9482aa','#96ac92','#e7bf7c'
STORY=json.loads((ROOT/'production/timeline.json').read_text('utf-8'))
TEXT_BOUNDS=[]
# Import reads the existing atlas and definitions; EP02 files are never written.
spec=importlib.util.spec_from_file_location('ep02_art',ROOT.parent/'ep02/production/render.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
font,glyph,rr,ease=old.font,old.glyph,old.rr,old.ease

def text(im,s,x,y,size=43,color=INK,bold=False,anchor='left'):
    p=glyph(str(s),size,color,bold)
    if anchor=='center':x-=p.width/2
    elif anchor=='right':x-=p.width
    x,y=round(x),round(y);im.paste(p,(x,y),p)
    TEXT_BOUNDS.append((str(s),x,y,p.width,p.height))

@lru_cache(1)
def dragon_poses():
    atlas=Image.open(ROOT/'assets/dragon_sprite_atlas.png').convert('RGBA')
    # Atlas cells are technical cuts, not bitmap editing. Exact regions optional.
    cfg=ROOT/'assets/dragon_regions.json'
    regions=json.loads(cfg.read_text('utf-8')) if cfg.exists() else [(c*atlas.width//3,r*atlas.height//2,(c+1)*atlas.width//3,(r+1)*atlas.height//2) for r in range(2) for c in range(3)]
    result=[]
    for region in regions:
        p=atlas.crop(region);box=p.getchannel('A').point(lambda v:255 if v>12 else 0).getbbox()
        if not box:raise ValueError('Dragon atlas has an empty pose')
        result.append(p.crop(box))
    return result

@lru_cache(200)
def sprite(who,pose,height,flip):
    a=(dragon_poses() if who=='dragon' else old.POSES)[pose]
    a=a.resize((round(a.width*height/a.height),height),Image.Resampling.LANCZOS)
    if flip:a=a.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return a

def actor(im,who,pose,x,bottom,t,height=635,mode='breathe',flip=False):
    a=sprite(who,pose,height,flip)
    if mode=='dance':angle=math.sin(t*8)*5;bob=abs(math.sin(t*8))*-22
    elif mode=='walk':angle=math.sin(t*9)*2.8;bob=math.sin(t*9)*7
    elif mode=='shock':angle=math.sin(t*22)*2.4*math.exp(-t*2);bob=-13*math.exp(-t*2)
    else:angle=math.sin(t*1.7)*.9;bob=math.sin(t*2.2)*3
    a=a.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    im.paste(a,(round(x-a.width/2),round(bottom-a.height+bob)),a)

def speech(im,who,line,x,y=147,width=680,size=49):
    label='龙娘' if who=='dragon' else '大肥鱼'
    color=PURPLE if who=='dragon' else BLUE
    rr(im,(x+4,y+7,x+width+4,y+142),26,'#dfd3c3')
    rr(im,(x,y,x+width,y+135),26,'#f7eff9' if who=='dragon' else '#edf3f6',outline='#cfbeb0')
    text(im,label,x+25,y+14,23,color,True)
    text(im,line,x+25,y+54,size,INK,True)
    # Small triangular pointer identifies the speaking side without covering faces.
    xx=x+(width*.3 if who=='dragon' else width*.72)
    ImageDraw.Draw(im).polygon([(xx-14,y+132),(xx+14,y+132),(xx,y+157)],fill='#f7eff9' if who=='dragon' else '#edf3f6')

def banner(im,line,sub=None):
    text(im,line,W/2,77,54,INK,True,'center')
    if sub:text(im,sub,W/2,140,27,MUTED,False,'center')

def footer(im,line):
    p=glyph(line,31,INK);x=(W-p.width)//2
    rr(im,(x-23,1000,x+p.width+23,1059),17,'#fbf4e9')
    text(im,line,W/2,1012,31,INK,False,'center')

def rules_card(im,x,y,t,rows=3,width=500,large=False):
    height=205+rows*75
    p=Image.new('RGBA',(width+20,height+20))
    rr(p,(11,13,width+9,height+12),20,'#d9c7b2')
    rr(p,(0,0,width,height),20,'#fff8e9',outline='#c5ad91',width=4)
    # Local text bounds must be translated into frame coordinates.
    before=len(TEXT_BOUNDS)
    text(p,'龙娘的家规',width/2,35,49 if large else 41,PURPLE,True,'center')
    lines=['① 不准只吃白饭','② 不准摸鱼','③ 不准偷懒','④ 饭要一起吃']
    for i,line in enumerate(lines[:rows]):
        text(p,line,33,119+i*75,37 if large else 34,GREEN if i==3 else INK,i==3)
    text(p,'先说好，谁都不许钻空子！' if rows==3 else '这条，不许钻空子。',width/2,height-55,25,MUTED,False,'center')
    # Card drops into place; local glyph bounds are translated exactly.
    shift=round((1-ease(t/.8))*-440)
    im.paste(p,(round(x),round(y)+shift),p)
    for i in range(before,len(TEXT_BOUNDS)):
        s,xx,yy,ww,hh=TEXT_BOUNDS[i];TEXT_BOUNDS[i]=(s,xx+round(x),yy+round(y)+shift,ww,hh)

def scallions(im,x,y,t):
    d=ImageDraw.Draw(im)
    count=min(26,max(0,int((t-2.0)*15)))
    for i in range(count):
        f=min(1,max(0,(t-2-i*.035)/.58))
        xx=x+(i*37%110-55);yy=y-135*(1-f)+(i*13%29-14)
        d.rounded_rectangle((xx-7,yy-4,xx+7,yy+4),2,fill='#699965',outline='#547b50',width=1)
    if 2<t<3.5:
        text(im,'撒一撮葱',x-230,y-200,30,GREEN,True)

def rice_bowl(im,x,y,t,green=False,scale=1.25):
    old.bowl(im,x,y,t,s=scale)
    if green:scallions(im,x,y,t)

def table(im,t,two=False):
    d=ImageDraw.Draw(im)
    d.line((615,864,598,978),fill='#b18c6b',width=25)
    d.line((1300,864,1326,978),fill='#b18c6b',width=25)
    rr(im,(468,804,1452,884),36,'#c5a280',outline='#a88462',width=4)
    rr(im,(468,804,1452,848),27,'#dfc5a1')
    if two:
        rice_bowl(im,720,810,t,scale=.9);rice_bowl(im,1203,810,t,scale=.9)
        d.ellipse((908,805,1026,846),fill='#d3e1d1',outline='#819780',width=3)
        for i in range(7):d.ellipse((932+i*8,808,944+i*8,825),fill='#95b783')

def touch_arm(im,t):
    # A clearly visible procedural chibi sleeve/hand reaches from fish to wing.
    approach=ease((t-2)/.7)*(1-ease((t-5.4)/.6))
    start=np.array([1218.-320*approach,672.]);end=np.array([798.,632.])
    travel=ease((t-2.7)/.7);back=1-ease((t-5.4)/.6)
    hand=start+(end-start)*travel*back
    d=ImageDraw.Draw(im)
    elbow=start+np.array([-35.,10.])*travel*back
    wrist=hand+np.array([22.,2.])
    old.curve(im,[tuple(start),tuple(elbow),tuple(wrist+np.array([66.,12.])),tuple(wrist)],'#31446e',35)
    old.curve(im,[tuple(start),tuple(elbow),tuple(wrist+np.array([66.,12.])),tuple(wrist)],'#455a84',27)
    d.ellipse((wrist[0]-17,wrist[1]-17,wrist[0]+17,wrist[1]+17),fill='#e6e5ed',outline='#536284',width=2)
    d.ellipse((hand[0]-20,hand[1]-14,hand[0]+20,hand[1]+16),fill='#fae3d4',outline='#b89b90',width=3)
    for i in range(3):d.line((hand[0]-8+i*7,hand[1]-9,hand[0]-8+i*7,hand[1]+2),fill='#d8b7a7',width=2)
    if 3.4<t<5.4:
        for i in range(3):
            xx=end[0]-19-i*17;yy=end[1]-39-i*11
            d.line((xx,yy,xx-10,yy-16),fill=GOLD,width=5)
        text(im,'戳',882,524,38,GOLD,True)

def confetti(im,t):
    d=ImageDraw.Draw(im)
    for i in range(36):
        x=(i*227+90)%W;y=((t*100+i*119)%850)+150
        c=[BLUE,PURPLE,GOLD,GREEN,'#dca996'][i%5]
        a=math.sin(t*2+i)*7
        d.line((x-a,y-8,x+a,y+8),fill=c,width=6)

def frame_at(now):
    TEXT_BOUNDS.clear();old.TEXT_BOUNDS.clear()
    now=min(max(0,now),TOTAL-.001)
    scene=next(s for s in STORY if s['start']<=now<s['start']+s['duration'])
    k=scene['id'];t=now-scene['start'];im=old.room().copy()
    if k=='rules':
        # Large distinct characters flank a physical falling rules card.
        actor(im,'dragon',0,392,960,t,640)
        actor(im,'fish',1,1540,960,t,640)
        banner(im,'龙娘立了三条家规');rules_card(im,710,260,t,3,500,True)
        footer(im,'大肥鱼：好哦。')
    elif k=='rice':
        actor(im,'dragon',0 if t<5 else 1,570,960,t,650)
        actor(im,'fish',1 if t<4 else 2,1350,960,t,650)
        banner(im,'第一条 · 不准只吃白饭')
        table(im,t)
        # Bowl approaches from the side and scallions visibly fall onto it.
        bx=1035+310*(1-ease(t/1.4));rice_bowl(im,bx,791,t,green=True,scale=1.18)
        if t<2:speech(im,'dragon','不准只吃白饭。',235,width=640)
        elif t<5.5:speech(im,'fish','那就……加一撮葱！',1070,width=685,size=46)
        else:speech(im,'fish','现在是葱花拌饭。',1070,width=685,size=46)
        if t>5.5:footer(im,'龙娘：你还挺严谨。')
    elif k=='touch':
        xx=1370-320*ease((t-2)/.7)*(1-ease((t-5.4)/.6))
        dp=0 if t<3.4 else 2 if t<6.0 else 1
        actor(im,'dragon',dp,570,960,max(0,t-3.4) if dp==2 else t,660,'shock' if dp==2 else 'breathe')
        actor(im,'fish',5,xx,960,t,660,'walk' if 2<t<3 else 'breathe',True)
        banner(im,'第二条 · 不准摸鱼')
        if t<2.7:speech(im,'dragon','还有，不准摸鱼。',235,width=640)
        elif t<5.8:speech(im,'fish','那我摸龙。',1090,width=605)
        else:speech(im,'dragon','……龙也不准摸！',235,width=680)
        if 2.7<t<6.3:touch_arm(im,t)
        if t>6.3:footer(im,'大肥鱼：好严格的家规。')
    elif k=='sleep':
        actor(im,'dragon',0 if t<3 else 1,590,960,t,665)
        # Fish sinks from standing into a seated nap with a small squash cut.
        pose=3 if t<2.8 else 4
        actor(im,'fish',pose,1350,963,t,650 if pose==3 else 550)
        banner(im,'第三条 · 不准偷懒')
        if t<3:speech(im,'dragon','吃完饭，不准偷懒。',235,width=700,size=46)
        elif t<7:speech(im,'fish','我在工作。',1090,width=610)
        else:speech(im,'fish','消化，也是工作。',1040,width=720,size=47)
        if t>3:
            for i in range(3):
                phase=(t*.34+i*.33)%1
                text(im,'z' if i<2 else 'Z',1540+phase*70,470-phase*90,25+i*7,BLUE,True)
            # Stomach status card progresses while the character naps.
            rr(im,(983,879,1666,976),21,'#fff6e6',outline='#d9c4a4')
            text(im,'消化中',1013,899,29,MUTED)
            rr(im,(1173,918,1613,940),8,'#e5d8c0')
            rr(im,(1173,918,1174+439*min(.99,(t-3)/8+.10),940),8,GREEN)
        if t>7:footer(im,'龙娘：这条鱼，没一条守的。')
    elif k=='together':
        actor(im,'dragon',3 if t<3 else 5,610,950,t,630)
        actor(im,'fish',1 if t<3 else 2,1300,950,t,630)
        banner(im,'于是，龙娘加了第四条')
        table(im,t,True)
        if t<3:speech(im,'dragon','第四条，饭要一起吃。',220,width=755,size=46)
        elif t<5.4:speech(im,'fish','这条，我超会遵守！',1030,width=755,size=46)
        else:speech(im,'dragon','慢慢吃。还有呢。',220,width=710,size=46)
        # A physical little rule placard appears on the shared dining table.
        if t>2:
            rr(im,(805,891,1110,968),13,'#f9f4e6',outline=GREEN,width=3)
            text(im,'④ 饭要一起吃',957,909,33,GREEN,True,'center')
    elif k=='dance':
        actor(im,'dragon',4,585+math.sin(t*4)*15,960,t,650,'dance')
        actor(im,'fish',3 if int(t*2)%2==0 else 5,1340-math.sin(t*4)*15,960,t,650,'dance')
        banner(im,'家规最终解释权：一起开心！')
        confetti(im,t);speech(im,'fish','干饭要紧，快乐也要紧。',745,181,1000,47)
        footer(im,'这次，一起守规矩。')
    else:
        # Credits have their own 6-second still-readable layout, small characters.
        rr(im,(260,143,1660,825),40,'#fff8ed',outline='#d4bfaa',width=3)
        text(im,'三条家规，都不如一起吃饭。',960,190,60,INK,True,'center')
        text(im,'社区同人小剧场 · 原创情景演绎',960,294,32,MUTED,False,'center')
        lines=[('鲸鱼原型','上善无形'),('女仆鲸鱼 / GPT 龙娘','ZipZipPipe 社区版本'),('音乐','Let Me Go · 罐装毕加索'),('歌曲原作','星落落_oi'),('创作','梨希 Lyxii'),('AI 协作','Codex · 基于 GPT-6')]
        for i,(label,value) in enumerate(lines):
            text(im,label,425,367+i*61,29,MUTED)
            text(im,value,848,362+i*61,35,BLUE if i==5 else INK,i==5)
        text(im,'绘本衍生美术 · 代码动画',960,759,25,MUTED,False,'center')
        actor(im,'dragon',5,477,1058,t,231)
        actor(im,'fish',5,1425,1058,t,231)
        footer(im,'素材出处与许可、歌曲原作链接见简介。')
    # Stable branding outside plot/dialogue areas.
    if k!='credits':text(im,'梨希 Lyxii · 同人小剧场',1865,1039,22,BLUE,False,'right')
    return im.convert('RGB')

CUES=[(0,4,'龙娘立了三条家规。大肥鱼：好哦。'),(4,6,'龙娘：不准只吃白饭。'),(6,9.5,'大肥鱼：那就……加一撮葱！'),(9.5,13,'大肥鱼：现在是葱花拌饭。'),(13,15.7,'龙娘：还有，不准摸鱼。'),(15.7,18.8,'大肥鱼：那我摸龙。'),(18.8,23,'龙娘：……龙也不准摸！'),(23,26,'龙娘：吃完饭，不准偷懒。'),(26,30,'大肥鱼：我在工作。'),(30,34,'大肥鱼：消化，也是工作。'),(34,37,'龙娘：第四条，饭要一起吃。'),(37,39.4,'大肥鱼：这条，我超会遵守！'),(39.4,42,'龙娘：慢慢吃。还有呢。'),(42,48,'大肥鱼：干饭要紧，快乐也要紧。'),(48,54,'三条家规，都不如一起吃饭。创作：梨希 Lyxii；AI 协作：Codex，基于 GPT-6。')]

def subtitles():
    def stamp(v):
        ms=round(v*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (ROOT/'deliverables/Lyxii_EP03.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(CUES))+'\n','utf-8-sig')
    (ROOT/'qa/subtitle_cues.json').write_text(json.dumps(CUES,ensure_ascii=False,indent=2),'utf-8')

SAMPLES=[1.4,4.8,6.8,10.8,14.2,16.9,19.8,24.2,27.4,31.7,35.4,38.7,40.5,43.7,49.7]
def previews():
    sheet=Image.new('RGB',(1920,390*5),CREAM);allbounds=[]
    for i,now in enumerate(SAMPLES):
        im=frame_at(now);im.save(ROOT/f'qa/frame_{now:04.1f}.jpg',quality=94)
        allbounds.extend([{'time':now,'text':b[0],'box':b[1:]} for b in TEXT_BOUNDS])
        cell=Image.new('RGB',(640,390),CREAM);cell.paste(im.resize((640,360)),(0,0))
        ImageDraw.Draw(cell).text((17,363),f'{now:.1f}s',font=font(18),fill=MUTED)
        sheet.paste(cell,(i%3*640,i//3*390))
    sheet.save(ROOT/'qa/storyboard.jpg',quality=95)
    (ROOT/'qa/text_bounds.json').write_text(json.dumps(allbounds,ensure_ascii=False,indent=2),'utf-8')
    im=old.room().copy();actor(im,'dragon',0,545,974,0,690);actor(im,'fish',2,1390,974,0,690)
    rr(im,(340,68,1580,272),30,'#fff8ea',outline='#cbb79e',width=3)
    text(im,'龙娘的三条家规',960,94,96,INK,True,'center')
    text(im,'大肥鱼全钻了空子',960,218,43,BLUE,True,'center')
    rr(im,(800,410,1096,800),19,'#fff8e9',outline='#c5ad91',width=3)
    for i,s in enumerate(['不准只吃白饭','不准摸鱼','不准偷懒']):text(im,s,948,455+i*107,36,INK,True,'center')
    text(im,'梨希 Lyxii · 欢乐同人小剧场',960,1009,29,BLUE,False,'center')
    im.save(ROOT/'deliverables/Lyxii_EP03_cover.jpg',quality=97)

def picture():
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'production/picture.mp4')]
    start=time.time()
    with (ROOT/'production/encode.log').open('w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(TOTAL*FPS):
                p.stdin.write(frame_at(n/FPS).tobytes())
                if n%(FPS*5)==0:print(f'{n/FPS:.0f}/{TOTAL}s | elapsed {time.time()-start:.1f}s',flush=True)
            p.stdin.close()
            if p.wait()!=0:raise RuntimeError('FFmpeg encode failed')
        except BaseException:p.kill();raise

def mux(music,start):
    if not music.is_file():raise FileNotFoundError(music)
    mix=ROOT/'production/music_excerpt.wav'
    # The requested song is extracted unchanged in tempo/pitch, no substitute tune.
    subprocess.run(['ffmpeg','-y','-v','warning','-ss',str(start),'-i',str(music),'-t',str(TOTAL),'-vn','-af','afade=t=in:st=0:d=0.35,afade=t=out:st=49:d=5','-ar',str(SR),'-ac','2',str(mix)],check=True)
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(mix),'-af','loudnorm=I=-18:TP=-2:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    stats=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
    (ROOT/'qa/audio_loudness.json').write_text(json.dumps(stats,indent=2),'utf-8')
    filt=f"loudnorm=I=-18:TP=-2:LRA=8:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
    subprocess.run(['ffmpeg','-y','-v','warning','-i',str(ROOT/'production/picture.mp4'),'-i',str(mix),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(SR),'-ac','2','-af',filt,'-t',str(TOTAL),'-movflags','+faststart',str(ROOT/'deliverables/Lyxii_EP03.mp4')],check=True)
    (ROOT/'qa/audio_source.json').write_text(json.dumps({'music_file':str(music),'source_title':'Let Me Go · 罐装毕加索 BV1XbY66nEWr','excerpt_start_seconds':start,'excerpt_duration_seconds':TOTAL,'fade_in_seconds':.35,'fade_out_seconds':5,'tempo_pitch_changed':False},ensure_ascii=False,indent=2),'utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--previews',action='store_true');p.add_argument('--picture',action='store_true');p.add_argument('--mux',action='store_true');p.add_argument('--frame',type=float);p.add_argument('--music',type=Path,default=ROOT/'assets/music/Let_Me_Go_Guanzhuang_Bijiasuo_BV1XbY66nEWr.m4a');p.add_argument('--music-start',type=float,default=15.0);args=p.parse_args()
    for folder in ['qa','deliverables','production']:(ROOT/folder).mkdir(exist_ok=True)
    if args.frame is not None:frame_at(args.frame).save(ROOT/'qa/sample.png')
    elif args.previews:subtitles();previews()
    elif args.picture:subtitles();picture()
    elif args.mux:mux(args.music,args.music_start)
    else:subtitles();previews();picture();mux(args.music,args.music_start)
