# B3 — prompts das cenas (Kie.ai, não gerados: saldo zerado em 20/10)

Rodar da raiz do repo, depois de recarregar créditos:

```bash
python .claude/skills/kieai/scripts/gerar.py --modelo imagem --params '{"aspect_ratio":"9:16"}' --nome b3-vitrine --prompt "Realistic smartphone-style photograph, vertical 9:16. Exterior of a small neighborhood optical store (eyewear shop) in an ordinary Brazilian commercial street, evening. The shop window displays eyeglass frames and is covered with generic yellow and black Black Friday discount posters, identical to the posters on the neighboring shops visible beside it. Plain shapes only, no readable text, no letters, no numbers, no logos anywhere in the image. Natural light, slightly gritty, documentary realism, Brazil, no people in focus."
python .claude/skills/kieai/scripts/gerar.py --modelo imagem --params '{"aspect_ratio":"9:16"}' --nome b3-balcao --prompt "Realistic documentary photograph, vertical 9:16. Inside a small, crowded Brazilian neighborhood optical store on Black Friday: many customers of different ages pressed against the glass counter with eyeglass frames, some holding phones showing prices, gesturing and asking the saleswoman for prices. Busy, slightly chaotic, fluorescent store lighting, shelves of eyeglass frames on the wall. Ordinary everyday people, Brazil. Absolutely no readable text, no letters, no numbers, no logos."
python .claude/skills/kieai/scripts/gerar.py --modelo imagem --params '{"aspect_ratio":"9:16"}' --nome b3-caixa --prompt "Realistic cinematic documentary photograph, vertical 9:16. Night, a small Brazilian neighborhood optical store after closing time, empty, half the lights off. A tired Brazilian woman in her 40s, owner of the store, sits alone behind the counter closing the cash register, a receipt roll and calculator in front of her, hand on her forehead, exhausted. Eyeglass frames on wall shelves in the background, dark street visible through the glass door. Warm dim light, quiet, sober mood. Absolutely no readable text, no letters, no numbers, no logos."
```

Copiar as saídas de `output/midia/` para esta pasta. Máximo 6 imagens no total (3 + 3 refações).
