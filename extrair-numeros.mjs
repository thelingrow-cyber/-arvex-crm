import AdmZip from 'adm-zip';
import path from 'path';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';
import { fileURLToPath } from 'url';

const ZIP_PATH = process.argv[2];

async function extrairNumerosDePDF(buffer, nomeArquivo) {
  try {
    const uint8 = new Uint8Array(buffer);
    const loadingTask = getDocument({ data: uint8, useWorkerFetch: false, isEvalSupported: false });
    const pdf = await loadingTask.promise;

    let textoTotal = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const textoPage = content.items.map(item => item.str).join(' ');
      textoTotal += textoPage + '\n';
    }

    const numeros = textoTotal.match(/\d+([.,]\d+)*/g) || [];

    console.log(`\n📄 Arquivo: ${nomeArquivo}`);
    console.log('─'.repeat(50));
    console.log('📝 Texto extraído:');
    console.log(textoTotal.trim());
    console.log('─'.repeat(50));
    console.log(`🔢 Números encontrados (${numeros.length}):`);
    console.log(numeros.join(', '));
  } catch (err) {
    console.error(`❌ Erro ao processar ${nomeArquivo}: ${err.message}`);
  }
}

async function main() {
  console.log(`\n🗜️  Abrindo ZIP: ${ZIP_PATH}\n`);

  let zip;
  try {
    zip = new AdmZip(ZIP_PATH);
  } catch (err) {
    console.error(`❌ Não foi possível abrir o ZIP: ${err.message}`);
    process.exit(1);
  }

  const entradas = zip.getEntries();
  const pdfs = entradas.filter(e => e.entryName.toLowerCase().endsWith('.pdf'));

  if (pdfs.length === 0) {
    console.log('⚠️  Nenhum PDF encontrado no ZIP.');
    console.log('Arquivos encontrados:');
    entradas.forEach(e => console.log(' -', e.entryName));
    return;
  }

  console.log(`✅ ${pdfs.length} PDF(s) encontrado(s)\n`);

  for (const entrada of pdfs) {
    const buffer = entrada.getData();
    await extrairNumerosDePDF(buffer, path.basename(entrada.entryName));
  }

  console.log('\n✅ Extração concluída.');
}

main();
