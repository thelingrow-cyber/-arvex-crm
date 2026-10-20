import os, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\Vitor Simões\Desktop\ARVEX\docs\lancamento-black-recorde\criativos"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&display=block');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{background:#14172E;color:#fff;font-family:'Inter',sans-serif;position:relative;
 background:radial-gradient(120%% 80%% at 15%% 0%%,#1F2D52 0%%,#14172E 60%%,#0D0F20 100%%)}
.pad{position:absolute;inset:0;padding:%(p)dpx;display:flex;flex-direction:column}
.eyebrow{font-weight:800;letter-spacing:6px;text-transform:uppercase;color:#C9A24A;font-size:30px}
.big{font-weight:900;letter-spacing:-3px;line-height:1.02}
.gold{color:#D4AF5A}
.muted{color:#A9ADC4}
.rule{width:120px;height:8px;background:#C9A24A;margin:44px 0}
.corner{position:absolute;font-weight:900;color:#C9A24A}
.brand{position:absolute;font-weight:800;letter-spacing:4px;font-size:24px;color:#8E93AE;text-transform:uppercase}
.cta{display:inline-block;background:#25D366;color:#0D0F20;font-weight:900;font-size:44px;padding:30px 48px;border-radius:14px;letter-spacing:-.5px}
.num{position:absolute;font-weight:800;font-size:26px;color:#8E93AE;letter-spacing:3px}
"""
def page(w,h,p,body):
    return "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>"+(CSS%dict(w=w,h=h,p=p))+"</style></head><body>"+body+"</body></html>"
def render(name,w,h,html):
    f=os.path.join(S,name+".html"); open(f,"w",encoding="utf-8").write(html)
    out=os.path.join(OUT,name+".png")
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=1",
      "--virtual-time-budget=6000",f"--window-size={w},{h}",f"--screenshot={out}","file:///"+f.replace("\\","/")],check=True,capture_output=True)
    print(out)

# B2
b2 = lambda fs,p,cx,cy: f"""<div class='pad' style='justify-content:center'>
<div class='big' style='font-size:{fs}px'>A Black Friday<br>não começa<br>em <span class='gold'>novembro.</span></div></div>
<div class='corner' style='right:{cx}px;bottom:{cy}px;font-size:46px;letter-spacing:2px'>27/11</div>"""
render("b2-feed-1080x1350",1080,1350,page(1080,1350,96,b2(150,96,96,90)))
render("b2-stories-1080x1920",1080,1920,page(1080,1920,96,b2(150,96,96,300)))

# B6
cards = [
 """<div class='eyebrow'>Florianópolis · 7º andar · sem vitrine</div>
 <div style='flex:1;display:flex;flex-direction:column;justify-content:center'>
 <div class='muted' style='font-weight:700;font-size:44px;margin-bottom:18px'>Faturava entre</div>
 <div class='big muted' style='font-size:150px'>10–12 mil</div>
 <div style='font-weight:700;font-size:44px;margin:44px 0 18px'>Foi para</div>
 <div class='big gold' style='font-size:250px'>22 mil</div>
 <div style='font-weight:700;font-size:40px;margin-top:20px' class='muted'>por mês.</div></div>""",
 """<div class='eyebrow'>O que ela fez</div>
 <div style='flex:1;display:flex;flex-direction:column;justify-content:center'>
 <div class='big' style='font-size:124px'>Parou de<br>anunciar<br><span class='gold'>promoção.</span></div></div>""",
 """<div class='eyebrow'>O que ela fez</div>
 <div style='flex:1;display:flex;flex-direction:column;justify-content:center'>
 <div class='big' style='font-size:106px'>Passou a<br>anunciar com<br><span class='gold'>direcionamento.</span></div></div>""",
 """<div class='eyebrow'>Nas palavras dela</div>
 <div style='flex:1;display:flex;flex-direction:column;justify-content:center'>
 <div class='big' style='font-size:92px'>“Promoção,<br>promoção,<br>promoção. <span class='gold'>E não<br>é isso.</span>”</div>
 <div class='rule'></div>
 <div style='font-weight:700;font-size:40px' class='muted'>Rafaela, dona de ótica em Florianópolis</div></div>""",
 """<div class='eyebrow'>Workshop ao vivo</div>
 <div style='flex:1;display:flex;flex-direction:column;justify-content:center'>
 <div class='big' style='font-size:96px'>Como essa campanha é montada para a <span class='gold'>Black Friday.</span></div>
 <div class='rule'></div>
 <div class='big' style='font-size:120px'>27 de outubro</div>
 <div style='font-weight:700;font-size:44px;margin-top:16px' class='muted'>Ao vivo · gratuito</div>
 <div style='margin-top:64px'><span class='cta'>Entre no grupo VIP</span></div></div>""",
]
for i,c in enumerate(cards,1):
    body=f"<div class='pad'>{c}</div><div class='num' style='right:96px;bottom:84px'>{i}/{len(cards)}</div><div class='brand' style='left:96px;bottom:84px'>Cindy Batista</div>"
    render(f"b6-card{i}-1080x1350",1080,1350,page(1080,1350,96,body))
