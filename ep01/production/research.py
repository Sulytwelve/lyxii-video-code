import urllib.request, json, pathlib, re
root=pathlib.Path(__file__).resolve().parents[1]
urls={"site":"https://www.sulyhub.cn/", "apps":"https://www.sulyhub.cn/apps", "bili_info":"https://api.bilibili.com/x/space/acc/info?mid=78712560", "bili_videos":"https://api.bilibili.com/x/space/arc/search?mid=78712560&ps=10&pn=1", "afdian":"https://ifdian.net/a/Lyxii", "repos":"https://api.github.com/users/Sulytwelve/repos?per_page=30"}
for key,url in urls.items():
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://space.bilibili.com/78712560'})
        raw=urllib.request.urlopen(req,timeout=20).read().decode('utf-8')
        (root/'production'/f'{key}.public.txt').write_text(raw,encoding='utf-8')
        if key=='repos':
            print(key, [(x['name'],x.get('description')) for x in json.loads(raw)])
        elif key.startswith('bili'):print(key,raw[:6000])
        else:print(key, re.sub('<[^>]+>',' ',raw)[:4500])
    except Exception as e:print(key,type(e).__name__,str(e)[:180])
