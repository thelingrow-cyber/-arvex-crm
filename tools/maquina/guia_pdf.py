"""Máquina de conteúdo, etapa 10b: transforma o guia.md do vídeo no PDF que vai no direct.

Molde: o PDF que o Fabiano entrega (A4, fundo branco, títulos em laranja, passos numerados, rodapé com o site).
Conversor próprio de markdown (só o que o guia usa: títulos, negrito, itálico, listas, caixas de marcar,
tabelas, citação, linha) → HTML → PDF pelo Edge headless. Sem dependência nova.

uso:  python tools/maquina/guia_pdf.py <pasta-do-rascunho>     # grava guia.html + guia.pdf na pasta
"""
import html, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
RASC = os.path.join(RAIZ, "docs", "conteudo", "maquina", "02-Rascunhos")
EDGE = os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe")
RODAPE = "@vitorsimoesb"

CSS = """
@page{size:A4;margin:18mm 20mm}
body{font:10.5pt/1.5 Helvetica,Arial,sans-serif;color:#1d1d1b}
.selo{font-size:8pt;letter-spacing:.12em;color:#e8640c;font-weight:700;text-transform:uppercase}
h1{font-size:20pt;line-height:1.2;margin:6px 0 14px;padding-bottom:12px;border-bottom:1px solid #f0a46c}
h2{font-size:14pt;margin:22px 0 6px}
h3,p.passo{color:#e8640c;font-weight:700;font-size:11pt;margin:14px 0 2px}
table{border-collapse:collapse;width:100%;margin:10px 0}td,th{border:1px solid #eee;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#fdf1e8}blockquote{margin:10px 0;padding:8px 12px;border-left:3px solid #e8640c;background:#fdf6f1}
ul{padding-left:18px}li.box{list-style:none;margin-left:-18px}li.box:before{content:"\\2610  ";color:#e8640c}
hr{border:0;border-top:1px solid #f0a46c;margin:18px 0}.rodape{margin-top:28px;color:#888;font-size:8.5pt}
"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", t)
    return re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', t)


def md_html(md):
    out, lista, tabela = [], None, []

    def fecha():
        nonlocal lista, tabela
        if lista:
            out.append(f"</{lista}>")
            lista = None
        if tabela:
            linhas = [l for l in tabela if not re.fullmatch(r"\|[\s:|-]+\|", l)]
            cel = lambda l: [c.strip() for c in l.strip("|").split("|")]
            out.append("<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cel(linhas[0])) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cel(l)) + "</tr>" for l in linhas[1:]) + "</table>")
            tabela = []

    for raw in md.splitlines():
        l = raw.rstrip()
        if l.startswith("|"):
            if lista:
                out.append(f"</{lista}>"); lista = None
            tabela.append(l); continue
        if tabela:
            fecha()
        m_ul = re.match(r"^\s*[-*] (\[[ x]\] )?(.*)", l)
        m_ol = re.match(r"^\s*\d+[.)] (.*)", l)
        if m_ul or m_ol:
            tipo = "ul" if m_ul else "ol"
            if lista != tipo:
                fecha(); out.append(f"<{tipo}>"); lista = tipo
            if m_ul:
                out.append(f'<li class="box">{inline(m_ul.group(2))}</li>' if m_ul.group(1) else f"<li>{inline(m_ul.group(2))}</li>")
            else:
                out.append(f"<li>{inline(m_ol.group(1))}</li>")
            continue
        fecha()
        if not l.strip():
            continue
        if re.fullmatch(r"\*\*GUIA EXCLUSIVO\*\*", l.strip(), re.I):
            out.append('<div class="selo">Guia exclusivo</div>')
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("# "):
            out.append(f"<h1>{inline(l[2:])}</h1>")
        elif l.strip() == "---":
            out.append("<hr>")
        elif l.startswith(">"):
            out.append(f"<blockquote>{inline(l.lstrip('> '))}</blockquote>")
        elif re.fullmatch(r"\*\*\d+\.[^*]+\*\*", l.strip()):  # "**1. Separe o silêncio…**" vira o título laranja do passo
            out.append(f'<p class="passo">{inline(l.strip("*"))}</p>')
        else:
            out.append(f"<p>{inline(l)}</p>")
    fecha()
    return "\n".join(out)


def gerar(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    md = open(os.path.join(pasta, "guia.md"), encoding="utf-8").read()
    titulo = (re.search(r"^# (.+)$", md, re.M) or [None, "Guia"])[1]
    doc = (f'<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
           f"<style>{CSS}</style></head><body>{md_html(md)}<div class='rodape'>{RODAPE}</div></body></html>")
    h = os.path.join(pasta, "guia.html")
    open(h, "w", encoding="utf-8").write(doc)
    pdf = os.path.join(pasta, "guia.pdf")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file:///" + h.replace("\\", "/")], check=True,
                   capture_output=True, timeout=120)
    return pdf


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    p = gerar(sys.argv[1])
    print(f"guia.pdf: {os.path.relpath(p, RAIZ)} ({os.path.getsize(p) // 1024} KB)")
