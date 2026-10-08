"""Cards do "freio da IA" — arte própria no estilo página de relatório (molde: 2026-09-mckinsey).
Fontes conferidas em docs/conteudo/pautas/2026-09-24.md (pautas 5 e 6)."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1520, 860
PAPEL, TINTA, CINZA, AZUL = (244, 245, 247), (15, 26, 43), (120, 128, 140), (43, 108, 232)
F = r"C:\Windows\Fonts\seguisb.ttf"
FL = r"C:\Windows\Fonts\segoeui.ttf"


def frase(nome, linhas, rotulo, rodape_txt):
    """Linha marcada com * sai em azul."""
    im = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.055)], fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.012)), rotulo, font=ImageFont.truetype(F, int(H * 0.032)), fill=(235, 238, 245))
    tam = int(H * 0.155) if len(linhas) <= 2 else int(H * 0.115)
    y = int(H * 0.22) if len(linhas) <= 2 else int(H * 0.16)
    for l in linhas:
        texto = l.lstrip("*")
        t2 = tam
        f2 = ImageFont.truetype(F, t2)
        while d.textlength(texto, font=f2) > W * 0.93 and t2 > 40:
            t2 -= 6
            f2 = ImageFont.truetype(F, t2)
        d.text((int(W * 0.035), y), texto, font=f2, fill=AZUL if l.startswith("*") else TINTA)
        y += int(t2 * 1.22)
    d.line([(int(W * 0.035), int(H * 0.86)), (W - int(W * 0.035), int(H * 0.86))], fill=(210, 214, 222), width=3)
    d.text((int(W * 0.035), int(H * 0.885)), rodape_txt, font=ImageFont.truetype(FL, int(H * 0.042)), fill=CINZA)
    im.save(os.path.join(AQUI, nome))


if __name__ == "__main__":
    frase("c-manchete.png", ["AS GIGANTES DA IA", "*DEFENDEM IR", "*MAIS DEVAGAR"], "NOTÍCIA", "Axios · 12/09/2026")
    frase("c-ensaio.png", ["WE MUST PACE", "*THE FRONTIER"], "ENSAIO",
          "Dario Amodei, CEO da Anthropic · OpenAI concordou · 12/09/2026")
    frase("c-motivo.png", ["A IA ANDA MAIS RÁPIDO", "*DO QUE ELES", "*CONSEGUEM CONFERIR"], "O MOTIVO",
          "argumento central do ensaio · Axios, 12/09/2026")
    frase("c-perplexity.png", ["QUEM ESTÁ NA FRENTE", "*FICA NA FRENTE"], "A CRÍTICA",
          "Perplexity e Cohere · NPR, 23/09/2026")
    frase("c-preco.png", ["GPT-6", "*−50% NO PREÇO"], "ESSA SEMANA", "OpenAI · API · 22/09/2026")
    print("artes geradas")
