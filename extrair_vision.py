import sys
import zipfile
import os
import io
import re

# Força UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from google.cloud import vision
import fitz  # PyMuPDF

CHAVE_JSON = r'C:\Users\Vitor Simões\Downloads\vocal-camera-493421-g7-38938351a250.json'
ZIP_PATH = None  # recebe via argumento

def pdf_para_imagens(pdf_bytes):
    from PIL import Image
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    imagens = []
    for page in doc:
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        # Comprime para JPEG se passar de 10MB
        if len(img_bytes) > 10 * 1024 * 1024:
            img = Image.open(io.BytesIO(img_bytes))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            img_bytes = buf.getvalue()
        imagens.append(img_bytes)
    doc.close()
    return imagens

def extrair_numeros_vision(imagem_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=imagem_bytes)
    response = client.text_detection(image=image)
    textos = response.text_annotations
    if not textos:
        return "", []
    texto_completo = textos[0].description
    numeros = re.findall(r'\d+(?:[.,]\d+)*', texto_completo)
    numeros = [n for n in numeros if len(re.sub(r'[.,]', '', n)) >= 10]
    return texto_completo, numeros

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CHAVE_JSON

    zip_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not zip_path:
        print("Uso: python extrair_vision.py <caminho_do_zip>")
        sys.exit(1)

    print(f"\n🗜️  Abrindo ZIP: {zip_path}\n")

    with zipfile.ZipFile(zip_path, 'r') as z:
        pdfs = [f for f in z.namelist() if f.lower().endswith('.pdf')]

        if not pdfs:
            print("⚠️  Nenhum PDF encontrado.")
            return

        print(f"✅ {len(pdfs)} PDF(s) encontrado(s)\n")

        todos_numeros = []

        for nome in pdfs:
            print(f"📄 Processando: {nome}")
            pdf_bytes = z.read(nome)
            imagens = pdf_para_imagens(pdf_bytes)
            print(f"   {len(imagens)} página(s) — enviando para Google Vision...")

            for i, img in enumerate(imagens):
                print(f"   Página {i+1}/{len(imagens)}...", end=" ")
                texto, numeros = extrair_numeros_vision(img)
                print(f"{len(numeros)} números encontrados")
                todos_numeros.extend(numeros)

        # Remove duplicatas mantendo ordem
        vistos = set()
        unicos = []
        for n in todos_numeros:
            if n not in vistos:
                vistos.add(n)
                unicos.append(n)

        print(f"\n🔢 Total de números únicos: {len(unicos)}")

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        txt_path = os.path.join(desktop, "numeros_otica.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Números extraídos via Google Vision\n")
            f.write(f"Total: {len(unicos)}\n")
            f.write("─" * 40 + "\n")
            for n in unicos:
                f.write(n + "\n")

        print(f"✅ Arquivo salvo em: {txt_path}")

if __name__ == "__main__":
    main()
