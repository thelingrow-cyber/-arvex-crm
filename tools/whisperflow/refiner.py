"""refiner.py — ADR-14: serial background worker for two-stage async refine.

While the synchronous flow (main.py, `base` model) stays exactly as it
was, this worker independently reprocesses the SAME audio buffer with the
`small` model and writes the result into history.db as `refined_text`.
Never recols, never notifies (decision closed in ADR-14/ADR-15 — the
Vitor's product call, not up for re-litigation here).

Queue design (ADR-14 bugfix over the v1 plan): a plain "depth-1, drop the
previous" queue is WRONG here, because each job belongs to a DIFFERENT
dictation — dropping job N to make room for N+1 would leave dictation N
without a refined version forever, for zero benefit. So this is a real
`queue.Queue(maxsize=5)`; when full, the OLDEST pending job is dropped
(not the newest), and a job already being processed is never cancelled
(faster-whisper doesn't support that) — it's left to finish and write.

The `small` model is lazy-loaded on the FIRST refine job, not at daemon
boot (AD-1's 2-6s boot time stays unchanged), and is created with
`cpu_threads = max(2, os.cpu_count() // 2)` so the synchronous `base`
transcription of the NEXT dictation always has CPU headroom while a
refine is running (ADR-14 "contenção de CPU").
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from typing import Optional

import numpy as np

import history as history_mod
import polish as polish_mod
from transcriber import Transcriber

QUEUE_MAXSIZE = 5
REFINE_MODEL_SIZE = "small"


class RefineWorker:
    """One instance per daemon. `start()` launches the single serial
    worker thread; `submit()` is the non-blocking entry point called from
    the hotkey loop right after a normal (synchronous) paste."""

    def __init__(
        self,
        language: str = "pt",
        custom_vocabulary: Optional[list] = None,
        polish_enabled: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._queue: "queue.Queue[tuple[int, np.ndarray]]" = queue.Queue(maxsize=QUEUE_MAXSIZE)
        self._language = language
        self._custom_vocabulary = custom_vocabulary
        self._polish_enabled = polish_enabled
        self._logger = logger or logging.getLogger("whisperflow")
        self._model: Optional[Transcriber] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True, name="whisperflow-refiner")
        self._thread.start()

    def submit(self, entry_id: Optional[int], audio: np.ndarray) -> None:
        """Enqueue a refine job. Never blocks the hotkey loop.

        entry_id is None when history.add_entry() itself failed (disk
        error) — nothing to refine into, skip silently (AD-10 spirit: a
        history failure must not cascade into more work).
        """
        if entry_id is None or audio is None or len(audio) == 0:
            return
        try:
            self._queue.put_nowait((entry_id, audio))
        except queue.Full:
            # ADR-14: drop the OLDEST pending job, never the incoming one —
            # each job is a different dictation, so dropping the newest
            # would just silently strand IT instead, with no upside.
            try:
                dropped_id, _ = self._queue.get_nowait()
                self._logger.warning(
                    "fila de refino cheia (%d) -- descartado job MAIS ANTIGO (entry_id=%s)",
                    QUEUE_MAXSIZE, dropped_id,
                )
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait((entry_id, audio))
            except queue.Full:
                self._logger.warning(
                    "fila de refino ainda cheia -- job entry_id=%s descartado", entry_id
                )

    def _ensure_model(self) -> Transcriber:
        if self._model is None:
            cpu_threads = max(2, (os.cpu_count() or 4) // 2)
            self._logger.info(
                "carregando modelo de refino (%s, cpu_threads=%d, lazy no 1o job)...",
                REFINE_MODEL_SIZE, cpu_threads,
            )
            t0 = time.time()
            self._model = Transcriber(
                model_size=REFINE_MODEL_SIZE,
                language=self._language,
                cpu_threads=cpu_threads,
                custom_vocabulary=self._custom_vocabulary,
            )
            self._logger.info("modelo de refino carregado em %.2fs", time.time() - t0)
        return self._model

    def _run(self) -> None:
        while True:
            entry_id, audio = self._queue.get()
            try:
                self._process(entry_id, audio)
            except Exception:
                # AD-10 spirit: one bad job must not kill the worker thread
                # for every job after it.
                self._logger.exception("erro no worker de refino (entry_id=%s)", entry_id)

    def _process(self, entry_id: int, audio: np.ndarray) -> None:
        t0 = time.time()
        model = self._ensure_model()
        text = model.transcribe(audio)
        elapsed = time.time() - t0

        if not text:
            self._logger.info("refino (%.2fs, entry_id=%s): <vazio/silencio>", elapsed, entry_id)
            return

        final_text = text
        if self._polish_enabled:
            try:
                t1 = time.time()
                final_text = polish_mod.polish(text)
                self._logger.info(
                    "refino+polish (entry_id=%s, whisper %.2fs, polish %.2fs): %s",
                    entry_id, elapsed, time.time() - t1, final_text,
                )
            except polish_mod.PolishUnavailable as exc:
                # ADR-14: polish failure on the refine path falls back to
                # the raw refine (same AD-10 spirit — never lose data over
                # an optional step).
                self._logger.warning(
                    "polish do refino indisponivel (entry_id=%s): %s -- gravando refino cru",
                    entry_id, exc,
                )
        else:
            self._logger.info("refino (%.2fs, entry_id=%s): %s", elapsed, entry_id, final_text)

        history_mod.update_refined_text(entry_id, final_text, logger=self._logger)


if __name__ == "__main__":
    # Manual test: python refiner.py [wav_path]
    # Loads history.db under whatever LOCALAPPDATA points at (set it to a
    # scratch dir before running this if you don't want to touch the real
    # production history), submits 3 jobs back-to-back from the same real
    # WAV to exercise the queue, waits for the worker to drain, prints the
    # 3 rows with their refined_text filled in.
    import sys
    from pathlib import Path

    import recorder as recorder_mod

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    test_logger = logging.getLogger("whisperflow")

    history_mod.init_db()

    wav_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bench/frase-padrao.wav")
    audio = recorder_mod.load_wav_as_float32(wav_path)
    print(f"audio: {wav_path} ({len(audio) / recorder_mod.SAMPLE_RATE:.2f}s)")

    worker = RefineWorker(language="pt", polish_enabled=False, logger=test_logger)
    worker.start()

    ids = []
    for i in range(3):
        eid = history_mod.add_entry(f"job de teste #{i+1}", was_polished=False, raw_text=f"job de teste #{i+1}")
        ids.append(eid)
        worker.submit(eid, audio)
        print(f"job {i+1} enfileirado (entry_id={eid})")

    # Wait for ALL 3 rows to actually have refined_text filled in -- NOT
    # just "queue reports empty", which is also true while the last job is
    # still mid-_process() (get() already dequeued it). Polling the DB
    # itself is the only correct completion signal here.
    deadline = time.time() + 180
    while time.time() < deadline:
        rows = [history_mod.get_entry(eid) for eid in ids]
        if all(r is not None and r["refined_text"] is not None for r in rows):
            break
        time.sleep(1.0)

    for eid in ids:
        print(history_mod.get_entry(eid))
