import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import render as r
from PIL import Image,ImageDraw
im=r.BASE.copy();d=ImageDraw.Draw(im)
# Clean the episodic chrome for a compact title treatment.
d.rectangle((0,0,1920,140),fill=r.BG)
r.text(im,'梨希 Lyxii / AI 自给自足实验 01',(106,63),32,r.PINK,True)
r.char(im,1200,147,0,1.08)
r.robot(im,1510,722,1,.57,'shock')
r.text(im,'让 AI',(105,226),152,r.WHITE,True)
r.text(im,'自己赚月费？',(105,419),134,r.PINK,True)
r.pill(im,'月目标 ¥150',110,649,r.LILAC,47)
r.rr(im,(108,799,941,940),22,fill='#392939',outline=r.PINK,width=3)
r.text(im,'第一天：收入 ¥0',(147,835),69,r.MINT,True)
r.text(im,'交出一个能用的小工具',(116,988),36,r.DIM)
r.rr(im,(1100,886,1779,975),15,fill='#231c2c',outline=r.LINE)
r.text(im,'形象由 ChatGPT 临时生成',(1131,911),34,r.WHITE)
im.save(r.ROOT/'deliverables'/'Lyxii_EP01_cover.png')
im.resize((1280,720),Image.Resampling.LANCZOS).save(r.ROOT/'deliverables'/'Lyxii_EP01_cover_1280.jpg',quality=95)
