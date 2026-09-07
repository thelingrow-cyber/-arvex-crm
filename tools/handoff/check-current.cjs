#!/usr/bin/env node

'use strict';

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const currentPath = path.join(root, 'docs', 'sessions', 'CURRENT.md');
const contractPath = path.join(root, 'docs', 'sessions', 'README.md');
const instructionPaths = [
  path.join(root, 'AGENTS.md'),
  path.join(root, '.claude', 'CLAUDE.md'),
];

const requiredSections = [
  '## Objetivo ativo',
  '## Estado atual',
  '## Decisões',
  '## Commits relevantes',
  '## Validação',
  '## Bloqueios e riscos',
  '## Próximo passo recomendado',
  '## Como retomar',
];

const secretPatterns = [
  /sk-ant-[A-Za-z0-9_-]+/i,
  /sk-proj-[A-Za-z0-9_-]+/i,
  /sbp_[A-Za-z0-9]+/i,
  /(?:api[_-]?key|token|secret)\s*[:=]\s*["'][^"']{12,}["']/i,
];

function fail(message) {
  console.error(`ERRO: ${message}`);
  process.exitCode = 1;
}

for (const file of [currentPath, contractPath, ...instructionPaths]) {
  if (!fs.existsSync(file)) fail(`arquivo ausente: ${path.relative(root, file)}`);
}

if (process.exitCode) process.exit();

const current = fs.readFileSync(currentPath, 'utf8');
for (const section of requiredSections) {
  if (!current.includes(section)) fail(`CURRENT.md sem a seção: ${section}`);
}

for (const pattern of secretPatterns) {
  if (pattern.test(current)) fail(`CURRENT.md contém possível segredo (${pattern})`);
}

for (const instructionPath of instructionPaths) {
  const body = fs.readFileSync(instructionPath, 'utf8');
  if (!body.includes('docs/sessions/CURRENT.md')) {
    fail(`${path.relative(root, instructionPath)} não aponta para CURRENT.md`);
  }
}

if (!process.exitCode) {
  console.log('OK: handoff Codex ↔ Claude íntegro, referenciado e sem padrões de segredo.');
}
