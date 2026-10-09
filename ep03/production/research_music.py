from pathlib import Path
from urllib.request import Request,urlopen
import json,re,gzip
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/music'
OUT.mkdir(parents=True,exist_ok=True)
def fetch(u):
    b=urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/'}),timeout=30).read()
    return gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b
def save_json(n,j):
    (OUT/n).write_text(json.dumps(j,ensure_ascii=False,indent=2),'utf-8')
for bv in ['BV1XbY66nEWr','BV1R5YL69EC5','BV13SYr6dEiQ']:
    try:
        b=fetch('https://www.bilibili.com/video/'+bv+'/')
        (OUT/(bv+'.html')).write_bytes(b)
        s=b.decode('utf-8');m=re.search(r'window\.__INITIAL_STATE__\s*=\s*',s)
        if not m:
            print(bv,'no state');continue
        j=json.JSONDecoder().raw_decode(s[m.end():])[0];v=j.get('videoData',{})
        q={k:v.get(k) for k in ['bvid','aid','cid','title','pubdate','desc','owner','copyright','duration','pages']}
        save_json(bv+'_summary.json',q)
        print(json.dumps(q,ensure_ascii=False))
        m=re.search(r'window\.__playinfo__\s*=\s*',s)
        if m:
            p=json.JSONDecoder().raw_decode(s[m.end():])[0];save_json(bv+'_playinfo.json',p)
            print('embedded playinfo', list(p))
        for label,u in [('replies',f'https://api.bilibili.com/x/v2/reply?type=1&oid={v.get("aid")}&sort=2&pn=1'),('playurl',f'https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={v.get("cid")}&qn=16&fnval=16&fnver=0&fourk=0')]:
            try:
                q=json.loads(fetch(u));save_json(bv+'_'+label+'.json',q)
                print(label,'code',q.get('code'))
            except Exception as e:print(label,type(e).__name__,str(e))
    except Exception as e:print(bv,type(e).__name__,str(e))
