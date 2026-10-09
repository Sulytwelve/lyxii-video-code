from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Make a character reference contact sheet.')
parser.add_argument('directory',nargs='?',type=Path,default=root/'assets')
p=parser.parse_args().directory
(root/'qa').mkdir(exist_ok=True)
out=Image.new('RGB',(1200,380),'#171723');d=ImageDraw.Draw(out)
for i,f in enumerate(p.glob('*.png')):
    im=Image.open(f).convert('RGB');print(f.name,im.size)
    out.paste(ImageOps.fit(im,(290,320)),(i*300,0));d.text((i*300+8,330),f.name[:16],fill='white')
out.save(root/'qa'/'characters.jpg')
