import sys
import zipfile
import fitz  # PyMuPDF
import re
import os
import io

# Força UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def extrair_texto_pdf(pdf_bytes, nome):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    texto_total = ""
    for page in doc:
        texto_total += page.get_text()
    doc.close()
    return texto_total

def extrair_com_ocr(pdf_bytes, nome):
    try:
        import pytesseract
        from PIL import Image
        import io

        # Tenta localizar o Tesseract
        possiveis = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for p in possiveis:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                break
        else:
            return None, "Tesseract não encontrado. Instale manualmente."

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto_total = ""
        for i, page in enumerate(doc):
            mat = fitz.Matrix(3, 3)  # zoom 3x para melhor qualidade
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
            texto = pytesseract.image_to_string(img, lang="eng", config=config)
            texto_total += texto + "\n"
        doc.close()
        return texto_total, None
    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 2:
        print("Uso: python extrair_ocr.py <caminho_do_zip>")
        sys.exit(1)

    zip_path = sys.argv[1]
    print(f"\n🗜️  Abrindo ZIP: {zip_path}\n")

    with zipfile.ZipFile(zip_path, 'r') as z:
        pdfs = [f for f in z.namelist() if f.lower().endswith('.pdf')]

        if not pdfs:
            print("⚠️  Nenhum PDF encontrado.")
            print("Arquivos:", z.namelist())
            return

        print(f"✅ {len(pdfs)} PDF(s) encontrado(s)\n")

        for nome in pdfs:
            print(f"\n📄 Arquivo: {nome}")
            print("─" * 50)
            pdf_bytes = z.read(nome)

            # Tenta extração direta de texto
            texto = extrair_texto_pdf(pdf_bytes, nome)

            if not texto.strip():
                print("⚠️  PDF baseado em imagem — tentando OCR...")
                texto, erro = extrair_com_ocr(pdf_bytes, nome)
                if erro:
                    print(f"❌ OCR falhou: {erro}")
                    continue
            print("─" * 50)
            numeros = re.findall(r'\d+(?:[.,]\d+)*', texto or "")
            # Filtra só números com 3+ dígitos (elimina lixo de 1-2 dígitos)
            numeros = [n for n in numeros if len(re.sub(r'[.,]', '', n)) >= 10]
            print(f"🔢 Números encontrados ({len(numeros)})")

            # Salva em TXT na área de trabalho
            import os
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            txt_path = os.path.join(desktop, "numeros_otica.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Números extraídos do PDF: {nome}\n")
                f.write(f"Total: {len(numeros)}\n")
                f.write("─" * 40 + "\n")
                for n in numeros:
                    f.write(n + "\n")
            print(f"✅ Arquivo salvo em: {txt_path}")

    print("\n✅ Extração concluída.")

if __name__ == "__main__":
    main()
