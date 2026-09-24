"""Cards originais do CAFEIA McKinsey — estilo página de relatório, arte própria (nada de terceiro).

capa.png    -> cartão de abertura com o nome do relatório e a fonte
n80.png     -> 80% relatam ganho de produtividade individual (com barras desenhadas aqui)
software.png-> quase 1/3 deixou de comprar software e construiu por dentro
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1520, 860                      # 2x do tamanho na tela
PAPEL = (244, 245, 247)
TINTA = (15, 26, 43)
CINZA = (120, 128, 140)
AZUL = (43, 108, 232)
F = r"C:\Windows\Fonts\seguisb.ttf"
FL = r"C:\Windows\Fonts\segoeui.ttf"


def base():
    im = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.055)], fill=TINTA)          # faixa superior
    d.text((int(W * 0.035), int(H * 0.012)), "RELATÓRIO", font=ImageFont.truetype(F, int(H * 0.032)),
           fill=(235, 238, 245))
    return im, d


def rodape(d, texto):
    d.line([(int(W * 0.035), int(H * 0.86)), (W - int(W * 0.035), int(H * 0.86))], fill=(210, 214, 222), width=3)
    d.text((int(W * 0.035), int(H * 0.885)), texto, font=ImageFont.truetype(FL, int(H * 0.042)), fill=CINZA)


def capa():
    im, d = base()
    d.text((int(W * 0.035), int(H * 0.22)), "THE STATE OF AI", font=ImageFont.truetype(F, int(H * 0.15)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.44)), "2026", font=ImageFont.truetype(F, int(H * 0.15)), fill=AZUL)
    d.rectangle([int(W * 0.035), int(H * 0.66), int(W * 0.30), int(H * 0.685)], fill=AZUL)
    rodape(d, "McKinsey & Company · pesquisa global anual")
    im.save(os.path.join(AQUI, "capa.png"))


def n80():
    im, d = base()
    d.text((int(W * 0.035), int(H * 0.16)), "80%", font=ImageFont.truetype(F, int(H * 0.30)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.56)), "dizem que a IA aumentou", font=ImageFont.truetype(FL, int(H * 0.075)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.66)), "a produtividade individual", font=ImageFont.truetype(FL, int(H * 0.075)), fill=TINTA)
    x0 = int(W * 0.62)                                        # barras desenhadas aqui
    for i, alt in enumerate((0.20, 0.30, 0.42, 0.55, 0.62)):
        x = x0 + i * int(W * 0.065)
        d.rectangle([x, int(H * 0.72) - int(H * alt), x + int(W * 0.045), int(H * 0.72)],
                    fill=AZUL if i == 4 else (178, 200, 244))
    rodape(d, "McKinsey · State of AI 2026")
    im.save(os.path.join(AQUI, "n80.png"))


def software():
    im, d = base()
    d.text((int(W * 0.035), int(H * 0.16)), "≈ 1/3", font=ImageFont.truetype(F, int(H * 0.28)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.54)), "das empresas deixou de comprar", font=ImageFont.truetype(FL, int(H * 0.072)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.635)), "software e construiu por dentro,", font=ImageFont.truetype(FL, int(H * 0.072)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.73)), "com agentes de IA", font=ImageFont.truetype(FL, int(H * 0.072)), fill=AZUL)
    for i in range(9):                                        # grade de quadradinhos: 3 de 9 destacados
        cx = int(W * 0.70) + (i % 3) * int(W * 0.075)
        cy = int(H * 0.22) + (i // 3) * int(H * 0.17)
        cor = AZUL if i < 3 else (205, 212, 224)
        d.rounded_rectangle([cx, cy, cx + int(W * 0.055), cy + int(H * 0.12)], 12, fill=cor)
    rodape(d, "McKinsey · State of AI 2026")
    im.save(os.path.join(AQUI, "software.png"))


def frase(nome, linhas, rotulo="LEITURA PRÓPRIA", rodape_txt="leitura própria · não está no relatório"):
    """Card tipográfico com a frase do próprio Vitor. Linha marcada com * sai em azul."""
    im = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.055)], fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.012)), rotulo, font=ImageFont.truetype(F, int(H * 0.032)), fill=(235, 238, 245))
    tam = int(H * 0.155) if len(linhas) <= 2 else int(H * 0.115)
    fonte = ImageFont.truetype(F, tam)
    y = int(H * 0.22) if len(linhas) <= 2 else int(H * 0.16)
    for l in linhas:
        azul = l.startswith("*")
        texto = l.lstrip("*")
        # encolhe a fonte se a linha não couber na largura útil
        f2, t2 = fonte, tam
        while d.textlength(texto, font=f2) > W * 0.93 and t2 > 40:
            t2 -= 6
            f2 = ImageFont.truetype(F, t2)
        d.text((int(W * 0.035), y), texto, font=f2, fill=AZUL if azul else TINTA)
        y += int(t2 * 1.22)
    rodape(d, rodape_txt)
    im.save(os.path.join(AQUI, nome))




def cards_opus():
    """Cards do vídeo do Opus 5.5 (22/09/2026)."""
    im, d = base()
    d.text((int(W * 0.035), int(H * 0.20)), "CLAUDE OPUS 5.5", font=ImageFont.truetype(F, int(H * 0.13)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.40)), "22 · SET · 2026", font=ImageFont.truetype(F, int(H * 0.13)), fill=AZUL)
    d.rectangle([int(W * 0.035), int(H * 0.60), int(W * 0.26), int(H * 0.625)], fill=AZUL)
    rodape(d, "anúncio oficial · Anthropic")
    im.save(os.path.join(AQUI, "o-capa.png"))

    im, d = base()
    d.text((int(W * 0.035), int(H * 0.16)), "-40%", font=ImageFont.truetype(F, int(H * 0.30)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.58)), "de custo para rodar", font=ImageFont.truetype(FL, int(H * 0.075)), fill=TINTA)
    d.text((int(W * 0.035), int(H * 0.68)), "o mesmo trabalho", font=ImageFont.truetype(FL, int(H * 0.075)), fill=TINTA)
    d.text((int(W * 0.60), int(H * 0.22)), "+30%", font=ImageFont.truetype(F, int(H * 0.16)), fill=AZUL)
    d.text((int(W * 0.60), int(H * 0.42)), "de velocidade", font=ImageFont.truetype(FL, int(H * 0.06)), fill=CINZA)
    rodape(d, "Anthropic · Claude Opus 5.5")
    im.save(os.path.join(AQUI, "o-40.png"))

    im, d = base()
    d.text((int(W * 0.035), int(H * 0.15)), "PREÇO POR MILHÃO DE TOKENS", font=ImageFont.truetype(F, int(H * 0.05)), fill=CINZA)
    linhas = [("entrada", "US$ 5", "US$ 4"), ("saída", "US$ 25", "US$ 20"), ("memória (cache)", "US$ 0,50", "US$ 0,20")]
    y = int(H * 0.28)
    for rotulo, antes, agora in linhas:
        d.text((int(W * 0.035), y), rotulo, font=ImageFont.truetype(FL, int(H * 0.062)), fill=TINTA)
        d.text((int(W * 0.46), y), antes, font=ImageFont.truetype(FL, int(H * 0.062)), fill=(170, 176, 188))
        d.line([(int(W * 0.455), y + int(H * 0.035)), (int(W * 0.60), y + int(H * 0.035))], fill=(200, 80, 70), width=5)
        d.text((int(W * 0.66), y), agora, font=ImageFont.truetype(F, int(H * 0.068)), fill=AZUL)
        y += int(H * 0.16)
    rodape(d, "Anthropic · Claude Opus 5.5")
    im.save(os.path.join(AQUI, "o-precos.png"))

    frase("o-piso.png", ["ISSO NÃO É VANTAGEM.", "*É PISO NOVO."])
    frase("o-tarde.png", ["O QUE PRECISAVA DE TIME", "*AGORA PRECISA DE UMA TARDE."])
    frase("o-abaixo.png", ["QUEM NÃO SUBIR JUNTO", "NÃO TÁ IGUAL.", "*TÁ ABAIXO."])

if __name__ == "__main__":
    cards_opus()
    frase("f-achados.png", ["3 ACHADOS", "*QUE PASSAM BATIDO"], rotulo="RELATÓRIO", rodape_txt="McKinsey · State of AI 2026")
    frase("f-produtividade.png", ["PRODUTIVIDADE", "*NÃO É RESULTADO"])
    frase("f-achado1.png", ["ACHADO 1"], rotulo="RELATÓRIO", rodape_txt="McKinsey · State of AI 2026")
    frase("f-integrar.png", ["INTEGRAR", "*NÃO É RECONSTRUIR"])
    frase("f-achado3.png", ["ACHADO 3"], rotulo="RELATÓRIO", rodape_txt="McKinsey · State of AI 2026")
    frase("f-corte.png", ["O CORTE NÃO VEIO", "NA VELOCIDADE PREVISTA.", "*MAS ESTÁ ACONTECENDO."])
    frase("f-hype.png", ["O MUNDO DISCUTE", "*SE É EXAGERO"])
    frase("f-mesa.png", ["VENCE NA MESA.", "*PERDE NO RESULTADO."])
    frase("f-reconstruir.png", ["NÃO É TECNOLOGIA.", "*É RECONSTRUÇÃO."])
    print("artes geradas")
