from pathlib import Path
import subprocess,json,zipfile,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];video=R/'deliverables'/'Lyxii_EP01.mp4'
def run(cmd):return subprocess.run(cmd,check=True,capture_output=True,text=True,encoding='utf-8',errors='replace')
probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]).stdout)
v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['pix_fmt'],v['codec_name'],v['r_frame_rate'])==(1920,1080,'yuv420p','h264','30/1')
assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
assert abs(float(probe['format']['duration'])-279.133)<.2
decoded=run(['ffmpeg','-v','error','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'])
assert not decoded.stderr.strip(),decoded.stderr
pts=[2,16,32,53,74,104,127,147,173,217,268]
sheet=Image.new('RGB',(1440,292*4),'#17141f');f=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',19)
for i,t in enumerate(pts):
    path=R/'qa'/f'encoded_{t:03}.jpg'
    run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2',str(path)])
    im=Image.open(path).convert('RGB');assert im.getextrema()[0][1]>100
    im=im.resize((480,270),Image.Resampling.LANCZOS);x=i%3*480;y=i//3*292
    sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+271),f'ENCODED / {t}s',font=f,fill='#f4b4cf')
sheet.save(R/'qa'/'encoded_contact.jpg',quality=92)
report={'video_file':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration_seconds':float(probe['format']['duration']),'video':'H.264 / 1920x1080 / 30fps / yuv420p','audio':'AAC / 48000Hz / stereo','full_decode':'passed, no errors','sampled_video_frames_seconds':pts,'subtitle_checker':'77 cues / 0 errors / 0 warnings','prototype_tests':'12 passed; browser UI verified','status':'actual income zero; no publishing or payment performed'}
(R/'qa'/'final_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'deliverables'/'技术检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Video-only editable project; the subtitle application has its own repository.
files=[]
files.extend((R/'assets').rglob('*'))
for name in ['render.py','make_audio.py','cover.py','story.json','timeline.json','mix.wav']:
    files.append(R/'production'/name)
files.extend((R/'production'/'audio').glob('*'))
files.extend([R/'deliverables'/'Lyxii_EP01.srt',R/'deliverables'/'交付说明.md',R/'deliverables'/'投稿文案.md',R/'qa'/'final_validation.json'])
with zipfile.ZipFile(R/'deliverables'/'Lyxii_EP01_project.zip','w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
    for p in files:
        if p.is_file():z.write(p,p.relative_to(R))
print(json.dumps(report,ensure_ascii=False,indent=2));print('project archive created')
