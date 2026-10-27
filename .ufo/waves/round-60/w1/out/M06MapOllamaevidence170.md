# M06 — round 60 w1 (line 170, C2 calibration, advisory leaf)

Mapped frozen population line `corpus/knowledge/ollama-evidence-replay.md:170` ("markers is a
conservative lane inference, not a ps OpenAPI field", rule 7 of the replay contract) to the committed
live Ollama receipt. Files: `.ufo/waves/round-60/w1/out/M06MapOllamaevidence170/{rows.tsv,notes.md,fresh-receipt.json,check.txt}`.
Lane source untouched; no commit/push/jj; no pacman (nothing installed this wave).

Rows (id prefix OL06, 2 rows, one population line):
- OL06a quote "not a ps OpenAPI field" — **confirmed**. Predicate over `c['ps-after']['models']` and
  `c['ps-before']['models']`: ≥1 loaded model and no `remote_model`/`remote_host` key on any ps object.
  Observed: ps-after 1 model, keys name,model,size,digest,details,expires_at,size_vram,context_length,runner;
  ps-before `{"models": []}`; neither marker key anywhere.
- OL06b quote "markers is a conservative lane inference" — **not-observable** (empty predicate, 220-char
  reason): whether the recognition rule is conservative is a judgment about the lane's classifier; no
  capture body or receipt field records the lane's rationale.

Evidence (exact): python3 importlib of `tools/round60-c2-counter.py` on
`.ufo/waves/round-60/live/receipt.json` → `receipt_ok=True`, 2 rows ×8 cols, quotes exact substrings
(5/6 words), OL06a `evaluate=True falsifiable=True`, OL06b empty predicate; `score()` on these rows only →
`covered=1 population=14 evaluated=1 eval_lines=1 sensitive=1/1 bound=1 contradicted=0 amended=0/0
receipt_ok=True good_rows=2 errors=0 met=False` (met false only because the other 13 lines are other seats').
Second look: own lane-owned child, `tools/kama-ollama-live.py --work /fast/scratch/hyaku/kama-r60/M06MapOllamaevidence170/run
--out .../r.json` → exit 0, verdict MODEL_OK, nonce c72aafd1c719, port 55195; same ps key set, same
predicate eval/falsifiable True; receipt copied as `fresh-receipt.json`.

No contradicted row → no amendment paragraph proposed. Risk: one capture of v0.40.11 cannot settle a schema
question, so the clause is confirmed only as "no such key emitted on the captured ps entries"; a reviewer may
prefer that wording in a later wave. Not-observable row is not credited as evaluated (counter rule).
