# M03 — mapped `ollama-evidence-replay.md:46` (base ec3b0d5) to the live receipt

Line statement: the *conclusion* "a remote `/api/tags` entry cannot be counted as locally loaded" is kama
lane policy `[INFERENCE]`, already labelled in `served-identity-crosswalk.md` (base lines 43-47).
Rows (`.ufo/waves/round-60/w1/out/M03MapOllamaevidence46/rows.tsv`, prefix OL03, path/line = base coordinate):
- `OL03A` confirmed — `counted as locally loaded`: predicate binds tags=1, `ps-before.models=[]`, `ps-after`
  digest = tags digest; receipt evaluates True, `falsifiable=True` (forcing ps-before non-empty flips it False).
  Exercises the local branch only.
- `OL03B` not-observable — `is also **[INFERENCE]**`: no captured entry carries `remote_model`/`remote_host`
  (tags keys are name/model/modified_at/size/digest/details/capabilities), so the remote exclusion is never
  exercised; the rule lives only in `tools/kama-ollama-evidence.py:244-246` (`remote_inventory`).
- `OL03C` not-observable — `and is already labeled that`: captures are 11 HTTP responses with no document
  text; the pointer is textually correct at tip (`served-identity-crosswalk.md:96,132`) but that is a repo
  read, not a live observation, so the row keeps an empty predicate.
Validation (importlib on `tools/round60-c2-counter.py`): `receipt_ok=True`, `good_rows=3`, `errors=0`,
`bound=1`, `sensitive=1`, `contradicted=0`; `met=False` is expected — these three rows cover 1 of the 14
frozen lines and 1 evaluated row, the registry-wide floor is other seats' rows.
Evidence: committed `.ufo/waves/round-60/live/receipt.json` checks `evidence-before-load`
(`available_not_loaded exit 1`), `evidence-after-load` (`loaded_same_digest exit 0`), `ps-lists-loaded`,
`tags-lists-model` — all `passed: true`; no fresh server run and no lane edit; no amendment text contributed.
Files: `rows.tsv`, `notes.md` (both in the out dir above) and this report. Risk: OL03A is the only live row
from this line and is a ps-gating test, not a test of the remote clause; a seat that wants the clause tested
needs a capture with a remote tags entry, which the frozen receipt does not contain.
