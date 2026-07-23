"""migrate_history.py — ADR-16 one-shot migration: history.jsonl -> history.db.

Run once (`python migrate_history.py`). Avulso, não vive no daemon (S7
plan). Safe to re-run:

- Every .jsonl line becomes one `entries` row: pasted_text=text,
  was_polished=polished, created_at=timestamp. raw_text/refined_text stay
  NULL — they never existed in the old format (ADR-16).
- Idempotent via upsert-by-(timestamp, text): the OLD daemon keeps
  appending to the .jsonl in parallel with this script's run (and again
  after every reboot until the S7 code is what's actually running), so a
  second run must not duplicate rows already migrated. Timestamp alone
  isn't a safe uniqueness key (two dictations in the same second are
  possible); the (created_at, pasted_text) pair is what's checked before
  each insert.
- The .jsonl is renamed to .jsonl.bak only once every line in THIS run
  parsed cleanly — a run that hit malformed lines leaves the original
  file in place untouched so it can be re-attempted after investigating.
"""

from __future__ import annotations

import json
import sys

import history as history_mod


def _already_migrated(conn, created_at: str, pasted_text: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM entries WHERE created_at = ? AND pasted_text = ? LIMIT 1",
        (created_at, pasted_text),
    ).fetchone()
    return row is not None


def migrate() -> int:
    history_mod.init_db()
    jsonl_path = history_mod.get_history_path()

    if not jsonl_path.exists():
        print(f"nada para migrar -- {jsonl_path} não existe (já migrado ou instalação nova).")
        return 0

    with jsonl_path.open("r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    migrated = 0
    skipped_dupe = 0
    skipped_bad = 0

    with history_mod.connect() as conn:
        for line in lines:
            try:
                entry = json.loads(line)
                text = entry["text"]
                polished = bool(entry.get("polished", False))
                created_at = entry["timestamp"]
            except (json.JSONDecodeError, KeyError) as exc:
                print(f"AVISO: linha ignorada (formato inesperado): {exc}")
                skipped_bad += 1
                continue

            if not text:
                skipped_bad += 1
                continue

            if _already_migrated(conn, created_at, text):
                skipped_dupe += 1
                continue

            conn.execute(
                "INSERT INTO entries "
                "(created_at, raw_text, pasted_text, was_polished, refined_text, duration_ms, tags) "
                "VALUES (?, NULL, ?, ?, NULL, NULL, NULL)",
                (created_at, text, int(polished)),
            )
            migrated += 1

    print(
        f"migração concluída: {migrated} nova(s), {skipped_dupe} já existente(s) (skip), "
        f"{skipped_bad} inválida(s) de {len(lines)} linha(s) no .jsonl."
    )

    if skipped_bad == 0:
        bak_path = jsonl_path.parent / (jsonl_path.name + ".bak")
        if bak_path.exists():
            print(f"AVISO: {bak_path} já existe -- não sobrescrevendo, .jsonl original mantido no lugar.")
        else:
            jsonl_path.rename(bak_path)
            print(f"{jsonl_path.name} renomeado para {bak_path.name}.")
    else:
        print("linha(s) inválida(s) encontrada(s) -- .jsonl NÃO renomeado (rode de novo após investigar).")

    return 0


if __name__ == "__main__":
    sys.exit(migrate())
