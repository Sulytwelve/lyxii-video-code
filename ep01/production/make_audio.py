import asyncio,json,pathlib,subprocess,math,wave,re,hashlib
import edge_tts
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'production'/'audio';OUT.mkdir(exist_ok=True)
story=json.loads((ROOT/'production'/'story.json').read_text('utf-8'))
sem=asyncio.Semaphore(3)
async def make(s):
    async with sem:
        f=OUT/(s['id']+'.mp3')
        md=OUT/(s['id']+'.words.jsonl');hp=OUT/(s['id']+'.sha256');hashval=hashlib.sha256(s['text'].encode()).hexdigest()
        if not f.exists() or not md.exists() or not hp.exists() or hp.read_text()!=hashval:
            voice='zh-CN-YunxiNeural' if s['speaker']=='ai' else 'zh-CN-XiaoxiaoNeural'
            for retry in range(3):
                try:
                    await edge_tts.Communicate(s['text'],voice,rate='+6%' if s['speaker']=='host' else '+0%',pitch='+0Hz',boundary='WordBoundary').save(str(f),str(md));hp.write_text(hashval);break
                except Exception:
                    if retry==2:raise
                    await asyncio.sleep(1)
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)],text=True).strip())
        s['voice_duration']=dur;s['duration']=math.ceil((dur+0.8)*30)/30
        print(s['id'],round(dur,2),flush=True)
async def main():await asyncio.gather(*(make(s) for s in story))
asyncio.run(main())
start=0;sr=48000
total=sum(s['duration'] for s in story)+2
audio=np.zeros((int(total*sr),2),np.float32)
for s in story:
    s['start']=start
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(OUT/(s['id']+'.mp3')),'-f','f32le','-ac','1','-ar',str(sr),'pipe:1'])
    a=np.frombuffer(raw,dtype=np.float32);s['audio_start']=start+0.2
    idx=int(s['audio_start']*sr);audio[idx:idx+len(a),0]+=a;audio[idx:idx+len(a),1]+=a
    start+=s['duration']
(ROOT/'production'/'timeline.json').write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding='utf-8')
# Original procedural music: gentle 88 BPM electric-piano / pluck pattern, no samples.
music=np.zeros(len(audio),np.float32);beat=60/88
chords=[[57,60,64,67],[53,57,60,64],[48,52,55,59],[55,59,62,65]]
def tone(at,note,duration,level,kind='pluck'):
    a=int(at*sr);n=min(int(duration*sr),len(music)-a)
    if n<=0:return
    t=np.arange(n,dtype=np.float32)/sr;freq=440*2**((note-69)/12)
    if kind=='bass':sig=np.sin(2*np.pi*freq*t)*np.exp(-t*3)
    else:sig=(np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*2*freq*t)+.07*np.sin(2*np.pi*3*freq*t))*np.exp(-t*4.5)
    env=np.minimum(t/.009,1)*np.minimum((duration-t)/.035,1)
    music[a:a+n]+=sig*env*level
for k in range(math.ceil(total/beat)):
    ch=chords[(k//8)%4]
    tone(k*beat,ch[(k%8)//2%4]+12,1.1,.017)
    if k%4==0:tone(k*beat,ch[0]-12,1.6,.026,'bass')
    if k%8==6:tone((k+.5)*beat,ch[2]+24,.6,.009)
# Subtle designed UI sound cues and transitions.
for s in story:
    tone(s['start']+.05,84,.12,.027)
    if s['kind'] in ['reply','zero','score']:tone(s['start']+.25,57,.2,.024,'bass')
fade=np.minimum(np.arange(len(music))/sr/2,1)*np.minimum((len(music)-np.arange(len(music)))/sr/3,1)
audio[:,0]+=music*fade;audio[:,1]+=music*fade
audio=np.clip(audio,-.95,.95)
with wave.open(str(ROOT/'production'/'mix.wav'),'wb')as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((audio*32767).astype('<i2').tobytes())
def st(t):
    m=int(round(t*1000));return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
subs=[];num=0
for s in story:
    pieces=[p for p in re.split(r'(?<=[。！？])',s['text']) if p]
    # Split long sentences at phrase boundaries for comfortable burned-in captions.
    parts=[]
    for p in pieces:
        while len(p)>36:
            breaks=[i+1 for i,c in enumerate(p[:32]) if c in '，。！？：']
            cut=breaks[-1] if breaks else 30
            # Never split an English identifier such as Windows between letters.
            while cut>0 and cut<len(p) and p[cut-1].isascii() and p[cut-1].isalnum() and p[cut].isascii() and p[cut].isalnum():cut-=1
            if cut<8:cut=30
            parts.append(p[:cut]);p=p[cut:]
        if p:parts.append(p)
    lengths=[len(x) for x in parts];acc=0
    words=[json.loads(x) for x in (OUT/(s['id']+'.words.jsonl')).read_text('utf-8').splitlines()]
    pos=0
    for w in words:
        idx=s['text'].find(w['text'],pos)
        if idx<0:idx=pos
        w['char_start']=idx;w['char_end']=idx+len(w['text']);pos=w['char_end']
    for p,l in zip(parts,lengths):
        startchar=acc;acc+=l
        hit=[w for w in words if w['char_end']>startchar and w['char_start']<acc]
        if hit:
            a=s['audio_start']+hit[0]['offset']/1e7
            b=s['audio_start']+(hit[-1]['offset']+hit[-1]['duration'])/1e7+.12
        else:
            a=s['audio_start']+s['voice_duration']*startchar/sum(lengths)
            b=s['audio_start']+s['voice_duration']*acc/sum(lengths)
        if len(subs) and a<last_b:a=last_b
        b=max(a+.72,b);last_b=b
        num+=1;subs.append(f'{num}\n{st(a)} --> {st(b)}\n{p}\n')
(ROOT/'deliverables'/'Lyxii_EP01.srt').write_text('\n'.join(subs),encoding='utf-8')
print('TOTAL',total,'seconds',flush=True)
