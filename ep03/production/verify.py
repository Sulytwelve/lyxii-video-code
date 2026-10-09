"""Verify the actual encoded EP03 file, subtitle boundaries and sampled text boxes."""
from pathlib import Path
import hashlib, json, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
film=ROOT/'deliverables/Lyxii_EP03.mp4';qa=ROOT/'qa'

def run(args):
    r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stderr[-4000:])
    return r

def main():
    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(film)]).stdout)
    (qa/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2),'utf-8')
    v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'])==(1920,1080,'24/1','h264')
    assert int(v['nb_read_frames'])==1296
    assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and a['channels']==2
    assert abs(float(probe['format']['duration'])-54)<.05
    dec=run(['ffmpeg','-v','error','-i',str(film),'-f','null','-']);(qa/'decode.log').write_text(dec.stderr,'utf-8')
    volume=run(['ffmpeg','-hide_banner','-i',str(film),'-af','volumedetect','-vn','-f','null','-'])
    (qa/'final_volume.log').write_text(volume.stderr,'utf-8')
    peak=float(re.search(r'max_volume: ([\-\d.]+) dB',volume.stderr).group(1));assert peak<=-1.0,peak
    run(['ffmpeg','-y','-v','error','-i',str(film),'-vf','fps=1/3,scale=480:270','-q:v','2',str(qa/'encoded_%02d.jpg')])
    pics=sorted(qa.glob('encoded_[0-9][0-9].jpg'));sheet=Image.new('RGB',(1920,310*((len(pics)+3)//4)),'#f5eddf')
    d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
    for i,p in enumerate(pics):
        x=i%4*480;y=i//4*310;sheet.paste(Image.open(p),(x,y));d.text((x+12,y+279),f'encoded / ~{i*3+1.5:.1f}s',font=font,fill='#494a59')
    sheet.save(qa/'encoded_contact.jpg',quality=95)
    sys.path.insert(0,str(ROOT/'production'));import render
    cues=json.loads((qa/'subtitle_cues.json').read_text('utf-8'))
    assert all(0<=c[0]<c[1]<=54 for c in cues)
    assert all(cues[i][1]<=cues[i+1][0] for i in range(len(cues)-1))
    # Include every scene, dialogue cut boundary and prop transition. First .8s
    # intentionally has the rules card enter from outside frame; sample afterwards.
    samples=sorted(set(render.SAMPLES+[.9,3.9,4.1,5.9,6.1,9.4,9.6,12.9,13.1,15.6,15.8,18.7,18.9,22.9,23.1,25.9,26.1,29.9,30.1,33.9,34.1,36.9,37.1,39.3,39.5,41.9,42.1,47.9,48.1,53.8]))
    bad=[]
    for t in samples:
        render.frame_at(t)
        for s,x,y,w,h in render.TEXT_BOUNDS:
            if x<0 or y<0 or x+w>1920 or y+h>1080:bad.append({'time':t,'text':s,'box':[x,y,w,h]})
    assert not bad,bad
    report={'duration_seconds':54,'video':'H.264 1920x1080 24fps / yuv420p','decoded_frames':1296,'audio':'AAC 48kHz stereo','full_decode':'passed','peak_dbfs':peak,'text_bounds_sampled_frames':len(samples),'text_bounds':'passed','subtitle_cues':len(cues),'sha256':hashlib.sha256(film.read_bytes()).hexdigest(),'bytes':film.stat().st_size,'visual_review':'manual review recorded separately after encoded contact/full-frame inspection','audio_review':'technical decode, loudness and peak checked; not a claim of subjective listening'}
    (qa/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
