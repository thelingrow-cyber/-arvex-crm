"""Two user-supplied film stills and the exact quoted headline."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

root=Path(__file__).resolve().parent
assets=root/'assets'
assets.mkdir(exist_ok=True)
overlay=Image.new('RGBA',(1080,900),(0,0,0,0))
for name,x,center in [('imagem-1.jpg',140,(.6,.35)),('imagem-2.webp',540,(.88,.35))]:
    im=Image.open(assets/name).convert('RGB')
    im=ImageOps.fit(im,(400,540),Image.Resampling.LANCZOS,centering=center)
    overlay.paste(im,(x,130))
fontpath=root.parents[1]/'tools/video-recut/assets/fontes/Inter-800.ttf'
font=ImageFont.truetype(str(fontpath),60)
lines=['“quanto mais você finge,','menos você finge.”']
shadow=Image.new('RGBA',overlay.size,(0,0,0,0))
sd=ImageDraw.Draw(shadow)
for i,line in enumerate(lines):
    sd.text((540,690+i*74),line,font=font,anchor='mt',fill=(0,0,0,245),stroke_width=7,stroke_fill=(0,0,0,245))
overlay=Image.alpha_composite(overlay,shadow.filter(ImageFilter.GaussianBlur(2)))
draw=ImageDraw.Draw(overlay)
for i,line in enumerate(lines):
    assert draw.textbbox((540,690+i*74),line,font=font,anchor='mt',stroke_width=3)[0]>=60
    draw.text((540,690+i*74),line,font=font,anchor='mt',fill='white',stroke_width=3,stroke_fill=(0,0,0,255))
overlay.save(assets/'topo-headline.png')
print('Prepared two stills and quoted headline at 1080x900')
