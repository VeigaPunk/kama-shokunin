# M13MapServedidentity103 — report (round 60 w1, C2 row mapping)

Line mapped: `corpus/knowledge/served-identity-crosswalk.md:103` (base `ec3b0d58`), text
`  row's claim cell as the upstream Ollama URL). [INFERENCE] Because the page` — the S031 parenthetical plus the
start of the locality inference in lines 96-108. Evidence: committed receipt `.ufo/waves/round-60/live/receipt.json`
(`receipt_caps` ok=True, 10 bodies); no fresh run needed, no lane source touched.

Rows (`.ufo/waves/round-60/w1/out/M13MapServedidentity103/rows.tsv`, no header, 3 rows):
- `OL13A` not-observable — the statement attributes `remote_host`'s "upstream Ollama URL" description to kama's own
  S031 cell (`corpus/SOURCES.md:43` confirms the wording); the receipt holds HTTP bodies only, no registry text.
- `OL13B` not-observable — the premise ("the page documents remote membership") is a documentation fact; the run is
  `OLLAMA_NO_CLOUD=1` with one local import (tags = 1 entry, keys without `remote_model`/`remote_host`), so no
  captured surface can exhibit or refute remote membership.
- `OL13C` confirmed — predicate (abridged) `len(c['tags']['models'])==1 and 'remote_model' not in ... and 'remote_host' not in ...
  and c['ps-before']['models']==[]`, verbatim in rows.tsv, where the ellipses are `c['tags']['models'][0]`; eval True, falsifiable True (adding `remote_host` or a loaded entry flips it to
  False). Confirms only that tags membership reports no loaded state; ps-after digest `8cf91c71…` equals the tags digest.
`m.score(pop, my_rows, receipt, "")` → rows=3 covered=1/14 evaluated=1 sensitive=1 bound=1 contradicted=0 errors=0
receipt_ok=True good_rows=3 (met=False only because coverage is global, not seat-local).

Calibration note: lines 103 carries no Ollama-behaviour clause that this capture can decide beyond the tags/ps surface
separation; claiming the remote-membership premise as confirmed would be laundry. No contradicted row, so no amendment
paragraph. Chart and per-row reasoning: `.ufo/waves/round-60/w1/out/M13MapServedidentity103/notes.md`.
