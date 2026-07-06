#!/usr/bin/env node
/* Regressão do parser/core — roda cada fixture em Chrome headless real (--dump-dom),
 * lê o <pre id="result"> que a fixture escreve (JSON com name/pass/expected/actual)
 * e agrega um relatório. Sem dependências novas (usa o Chrome já instalado).
 * Uso: node tests/run.js  (exit 0 = tudo verde, exit 1 = alguma fixture falhou) */
"use strict";
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const CHROME_CANDIDATES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, "Google/Chrome/Application/chrome.exe") : null,
].filter(Boolean);

function findChrome() {
  for (const p of CHROME_CANDIDATES) if (fs.existsSync(p)) return p;
  throw new Error("Chrome não encontrado em nenhum caminho conhecido — ajuste CHROME_CANDIDATES em tests/run.js");
}

function decodeEntities(s) {
  return s
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function runFixture(chrome, fixturePath) {
  const url = "file:///" + fixturePath.replace(/\\/g, "/");
  let dom;
  try {
    dom = execFileSync(chrome, [
      "--headless=new",
      "--disable-gpu",
      "--no-sandbox",
      "--virtual-time-budget=11000",
      "--dump-dom",
      url,
    ], { encoding: "utf8", timeout: 15000 });
  } catch (e) {
    return { name: path.basename(fixturePath), pass: false, error: "chrome falhou: " + e.message };
  }
  const m = dom.match(/<pre id="result">([\s\S]*?)<\/pre>/);
  if (!m) return { name: path.basename(fixturePath), pass: false, error: "sem <pre id=result> no dump (fixture não rodou?)" };
  try {
    return JSON.parse(decodeEntities(m[1]));
  } catch (e) {
    return { name: path.basename(fixturePath), pass: false, error: "JSON inválido: " + m[1].slice(0, 200) };
  }
}

function main() {
  const chrome = findChrome();
  const fixturesDir = path.join(__dirname, "fixtures");
  const files = fs.readdirSync(fixturesDir).filter((f) => f.endsWith(".html")).sort();
  if (!files.length) {
    console.error("Nenhuma fixture em tests/fixtures/");
    process.exit(1);
  }
  let allPass = true;
  for (const f of files) {
    const result = runFixture(chrome, path.join(fixturesDir, f));
    const status = result.pass ? "PASS" : "FAIL";
    console.log(`[${status}] ${result.name || f}`);
    if (!result.pass) {
      allPass = false;
      console.log("  expected:", JSON.stringify(result.expected));
      console.log("  actual:  ", JSON.stringify(result.actual));
      if (result.error) console.log("  error:   ", result.error);
    }
  }
  console.log(allPass ? "\n✅ tudo verde" : "\n❌ há fixture(s) falhando");
  process.exit(allPass ? 0 : 1);
}

main();
