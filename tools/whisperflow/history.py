"""history.py — SQLite-backed transcription history (ADR-16, S7).

Replaces the old .jsonl-with-a-50-entry-cap (V1.1/AD-8) with an uncapped
SQLite database. Two reasons forced this in the S7 refactor: (1) ADR-14's
async refine worker needs a stable row it can UPDATE once the `small`
model's result is ready, seconds after the original paste already
happened — a flat-file rewrite-the-whole-thing-every-append scheme (the
old append_entry) can't do that; (2) the S8 web UI needs to search/tag/
delete by id.

Access discipline (ADR-16, mandatory — the daemon's hotkey loop, the
refine worker thread, and the S8 web UI's request threads all touch this
same file): WAL journal mode + every function opens its OWN short-lived
connection (open -> execute -> close), never a connection shared across
threads. That combination is what makes concurrent access safe without
hitting sqlite3's default same-thread restriction — see REFACTOR-PLAN.md
ADR-16.

Schema (3 text versions max — "refined" already embeds polish when it
ran, see ADR-14; there's no 4th column):
    id, created_at (ISO8601 UTC), raw_text (NULL on migrated rows),
    pasted_text (NOT NULL — what actually got pasted), was_polished (0/1),
    refined_text (NULL until the async worker fills it in), duration_ms,
    tags (simple CSV — one person's volume doesn't justify a join table).
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

import config as cfg

DB_FILENAME = "history.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY,
  created_at TEXT NOT NULL,
  raw_text TEXT,
  pasted_text TEXT NOT NULL,
  was_polished INTEGER NOT NULL,
  refined_text TEXT,
  duration_ms INTEGER,
  tags TEXT
);
"""


def get_history_db_path() -> Path:
    return cfg.get_data_dir() / DB_FILENAME


def get_history_path() -> Path:
    """Old .jsonl location — kept only so migrate_history.py knows where to
    read from (and main.py's old callers, if any, keep resolving a path)."""
    return cfg.get_data_dir() / "history.jsonl"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Open -> yield -> commit -> close, every call (ADR-16 access
    discipline). Public (not `_connect`) because migrate_history.py and
    the S8 routes both need it for anything not covered by the helpers
    below."""
    conn = sqlite3.connect(str(get_history_db_path()), timeout=10.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Idempotent: create the table (and switch the file to WAL) if not
    already done. Safe to call on every daemon boot."""
    with connect() as conn:
        conn.execute(_SCHEMA)


def add_entry(
    pasted_text: str,
    was_polished: bool,
    raw_text: Optional[str] = None,
    duration_ms: Optional[int] = None,
    logger=None,
) -> Optional[int]:
    """Insert one entry, return its id (the refine worker needs it to
    UPDATE this exact row later) — or None on failure. Never raises:
    history is a convenience feature (AD-10 spirit), a disk/permission
    error here must not block dictation."""
    if not pasted_text:
        return None
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO entries "
                "(created_at, raw_text, pasted_text, was_polished, refined_text, duration_ms, tags) "
                "VALUES (?, ?, ?, ?, NULL, ?, NULL)",
                (created_at, raw_text, pasted_text, int(was_polished), duration_ms),
            )
            return cur.lastrowid
    except sqlite3.Error:
        if logger is not None:
            logger.exception("erro ao gravar entrada em history.db")
        return None


def update_refined_text(entry_id: int, refined_text: str, logger=None) -> None:
    """ADR-14: the refine worker calls this seconds after add_entry, once
    the `small` (+ optional polish) pass finishes. Never raises."""
    try:
        with connect() as conn:
            conn.execute(
                "UPDATE entries SET refined_text = ? WHERE id = ?",
                (refined_text, entry_id),
            )
    except sqlite3.Error:
        if logger is not None:
            logger.exception("erro ao gravar refined_text (entry_id=%s)", entry_id)


def get_entry(entry_id: int) -> Optional[dict]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None


def list_entries(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    """Recent-first. `search` is a LIKE across pasted/refined/raw text
    (ADR-17 — no FTS, volume doesn't justify it). `tag` filters entries
    whose CSV tags field contains that exact tag."""
    query = "SELECT * FROM entries"
    clauses = []
    params: list = []
    if search:
        like = f"%{search}%"
        clauses.append("(pasted_text LIKE ? OR refined_text LIKE ? OR raw_text LIKE ?)")
        params.extend([like, like, like])
    if tag:
        clauses.append("(',' || COALESCE(tags, '') || ',') LIKE ?")
        params.append(f"%,{tag},%")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def set_tags(entry_id: int, tags: list[str]) -> None:
    """Overwrites the CSV tags field (no join table — ADR-16)."""
    csv_tags = ",".join(t.strip() for t in tags if t.strip())
    with connect() as conn:
        conn.execute(
            "UPDATE entries SET tags = ? WHERE id = ?",
            (csv_tags or None, entry_id),
        )


def delete_entry(entry_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))


if __name__ == "__main__":
    # Manual test: python history.py -- inserts a test entry, reads it
    # back, prints the WAL check.
    init_db()
    new_id = add_entry(
        "teste de history sqlite",
        was_polished=False,
        raw_text="teste de history sqlite",
        duration_ms=1234,
    )
    print("gravado id=", new_id, "em", get_history_db_path())
    print(get_entry(new_id))
    with connect() as conn:
        print("journal_mode:", conn.execute("PRAGMA journal_mode").fetchone()[0])
    print("list_entries(limit=3):", list_entries(limit=3))
