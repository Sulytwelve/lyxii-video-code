from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib
p=Path(__file__).resolve().parents[1]/'assets/music'
j=json.loads((p/'BV1XbY66nEWr_playurl.json').read_text('utf-8'))
audio=max(j['data']['dash']['audio'],key=lambda q:q.get('bandwidth',0))
url=audio.get('baseUrl') or audio['base_url']
out=p/'Let_Me_Go_Guanzhuang_Bijiasuo_BV1XbY66nEWr.m4a'
req=Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/video/BV1XbY66nEWr/'})
with urlopen(req,timeout=60) as r: out.write_bytes(r.read())
record={'source_video':'https://www.bilibili.com/video/BV1XbY66nEWr/','method':'Anonymous public Bilibili DASH playurl; highest advertised audio bandwidth; no account/cookie/paywall used','audio_id':audio['id'],'bandwidth':audio['bandwidth'],'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'authorization_source':'https://www.bilibili.com/video/BV1XbY66nEWr/#reply314678966401','authorization_author_uid':290500073,'authorization_reply_id':314678966401}
(p/'download_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(record,ensure_ascii=False))
