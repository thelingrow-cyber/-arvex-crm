"""Cards do vídeo da água do mar — no padrão da referência do Jett (card pequeno no terço superior).

Card 1 é FOTO REAL: Wikimedia Commons, "Richly colored sky over calm sea water (Unsplash)",
licença **CC0** — uso livre, sem exigência de atribuição. Arquivo local: `opt-a.jpg`.
Cards 2 a 5 são ilustração própria em PIL. Nenhuma arte de terceiro é copiada.

Saída: 5 PNGs 1120x630 (entram no camadas com largura 660).
"""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1120, 630

# Paleta puxada da foto de abertura: céu quente do pôr do sol + água azul-ardósia.
FUNDO = (236, 231, 222)
GRAFITE = (62, 66, 72)
OURO = (214, 158, 66)
AZUL = (94, 128, 150)
CLARO = (186, 182, 174)
SOMBRA = (202, 196, 186)


def base(cor=FUNDO):
    """Fundo com leve vinheta, pra não ficar com cara de slide chapado."""
    im = Image.new("RGB", (W, H), cor)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.30, -H * 0.42, W * 1.30, H * 1.42], fill=60)
    v = v.filter(ImageFilter.GaussianBlur(120))
    escuro = Image.new("RGB", (W, H), (int(cor[0] * 0.90), int(cor[1] * 0.90), int(cor[2] * 0.89)))
    return Image.composite(im, escuro, v)


def figura(d, x, y, alt, cor, bracos=False, sombra=True):
    """Bonequinho chapado com sombra de contato. alt = altura total."""
    rc = alt * 0.22
    topo = y + 2 * rc + alt * 0.06
    larg = alt * 0.30
    if sombra:                                   # elipse de apoio: dá peso à figura
        d.ellipse([x - larg * 1.3, y + alt - alt * 0.05, x + larg * 1.3, y + alt + alt * 0.08],
                  fill=SOMBRA)
    if bracos:                                   # braços atrás do tronco
        lw = int(alt * 0.115)
        for lado in (-1, 1):
            px, py = x + lado * (larg + alt * 0.36), topo - alt * 0.20
            d.line([(x + lado * larg * 0.6, topo + alt * 0.14), (px, py)], fill=cor, width=lw)
            d.ellipse([px - lw / 2, py - lw / 2, px + lw / 2, py + lw / 2], fill=cor)
    d.rounded_rectangle([x - larg, topo, x + larg, y + alt], radius=larg * 0.55, fill=cor)
    d.ellipse([x - rc, y, x + rc, y + 2 * rc], fill=cor)


def seta(d, x0, y, comp, lado, cor=GRAFITE, w=11):
    """Seta com haste e ponta proporcionais."""
    pt = x0 + lado * comp
    d.line([(x0, y), (pt - lado * w, y)], fill=cor, width=w)
    p = w * 2.4
    d.polygon([(pt + lado * p * 0.6, y), (pt - lado * p * 0.5, y - p * 0.70),
               (pt - lado * p * 0.5, y + p * 0.70)], fill=cor)


def perfil(d, x, cy, s, cor, estranho=False):
    """Cabeça de perfil virada pra direita. `estranho` = contorno fora do padrão."""
    p = [(x - 52 * s, cy - 78 * s), (x + 26 * s, cy - 92 * s), (x + 62 * s, cy - 40 * s),
         (x + 74 * s, cy + 4 * s), (x + 52 * s, cy + 14 * s), (x + 56 * s, cy + 48 * s),
         (x + 18 * s, cy + 62 * s), (x + 22 * s, cy + 96 * s), (x - 52 * s, cy + 96 * s)]
    if estranho:
        p = [(x - 52 * s, cy - 78 * s), (x + 14 * s, cy - 110 * s), (x + 72 * s, cy - 50 * s),
             (x + 106 * s, cy + 12 * s), (x + 54 * s, cy + 20 * s), (x + 64 * s, cy + 56 * s),
             (x + 16 * s, cy + 64 * s), (x + 24 * s, cy + 96 * s), (x - 52 * s, cy + 96 * s)]
    d.ellipse([x - 54 * s, cy + 88 * s, x + 46 * s, cy + 108 * s], fill=SOMBRA)   # apoio
    d.polygon(p, fill=cor)
    d.ellipse([x + 14 * s, cy - 36 * s, x + 33 * s, cy - 17 * s], fill=FUNDO)     # olho


# ---------------------------------------------------------------- os cinco cards

def c_mar():
    """Abertura em FOTO REAL (CC0). Recorte 16:9 na linha do horizonte + leve grade."""
    src = Image.open(os.path.join(AQUI, "opt-a.jpg")).convert("RGB")
    lw, lh = src.size
    nh = int(lw / (W / H))
    topo = max(0, int((lh - nh) * 0.55))
    im = src.crop((0, topo, lw, min(lh, topo + nh))).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.08)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Brightness(im).enhance(0.98)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    im.save(os.path.join(AQUI, "c-mar.png"))


def c_tracos():
    """Perfis: dois iguais, um fora do padrão. O traço que não combina."""
    im = base()
    d = ImageDraw.Draw(im)
    cy = int(H * 0.50)
    perfil(d, int(W * 0.17), cy, 1.45, CLARO)
    perfil(d, int(W * 0.45), cy, 1.45, CLARO)
    perfil(d, int(W * 0.74), cy, 1.66, OURO, estranho=True)
    im.save(os.path.join(AQUI, "c-tracos.png"))


def c_repele():
    """Repulsão: os incompatíveis SAINDO do quadro — metade deles já fora da borda."""
    im = base()
    d = ImageDraw.Draw(im)
    for lado in (-1, 1):
        figura(d, int(W * (0.50 + lado * 0.50)), int(H * 0.32), 226, CLARO)   # cortados na borda
        figura(d, int(W * (0.50 + lado * 0.335)), int(H * 0.40), 178, CLARO)
        seta(d, W * (0.50 + lado * 0.155), H * 0.44, 120, lado)
    figura(d, int(W * 0.50), int(H * 0.19), 330, OURO)
    im.save(os.path.join(AQUI, "c-repele.png"))


def c_atrai():
    """Atração: só compatíveis, em arco fechado em volta. Os azuis são os que compram."""
    im = base()
    d = ImageDraw.Draw(im)
    for r, a in [(330, 14), (240, 24)]:                        # o arco de aproximação
        d.ellipse([W / 2 - r * 1.35, H * 0.62 - r, W / 2 + r * 1.35, H * 0.62 + r],
                  fill=(int(FUNDO[0] - a * 0.5), int(FUNDO[1] - a * 0.6), int(FUNDO[2] - a * 0.8)))
    for dx, alt in [(-0.30, 182), (-0.165, 156), (0.165, 156), (0.30, 182)]:
        figura(d, int(W * (0.50 + dx)), int(H * 0.44), alt, AZUL)
        lado = 1 if dx < 0 else -1
        seta(d, W * (0.50 + dx) + lado * 76, H * 0.34, 58, lado, w=9)
    figura(d, int(W * 0.50), int(H * 0.17), 340, OURO)
    im.save(os.path.join(AQUI, "c-atrai.png"))


def c_liberdade():
    """A liberdade: um só, grande, de braços abertos. Sem multidão — ela virou card próprio."""
    im = base()
    d = ImageDraw.Draw(im)
    for r, a in [(360, 16), (270, 26), (190, 40)]:            # halo concêntrico discreto
        d.ellipse([W / 2 - r, H * 0.60 - r, W / 2 + r, H * 0.60 + r],
                  fill=(int(FUNDO[0] - a * 0.5), int(FUNDO[1] - a * 0.6), int(FUNDO[2] - a * 0.8)))
    figura(d, int(W * 0.50), int(H * 0.16), 400, OURO, bracos=True)
    im.save(os.path.join(AQUI, "c-liberdade.png"))


def c_multidao():
    """FOTO REAL de multidão: Wikimedia Commons, 'Front row audience (Unsplash)', CC0.
    Recorte na faixa de baixo (só a massa anônima, de costas) + dessaturação."""
    src = Image.open(os.path.join(AQUI, "mult-b.jpg")).convert("RGB")
    lw, lh = src.size
    nh = int(lw / (W / H))
    topo = max(0, lh - nh - int(lh * 0.02))
    im = src.crop((0, topo, lw, min(lh, topo + nh))).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.5)
    im = ImageEnhance.Brightness(im).enhance(1.08)
    im = ImageEnhance.Contrast(im).enhance(1.14)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
    im.save(os.path.join(AQUI, "c-multidao.png"))


if __name__ == "__main__":
    c_mar(); c_tracos(); c_repele(); c_atrai(); c_liberdade(); c_multidao()
    print("6 cards gerados (2 foto real + 4 ilustração)")
