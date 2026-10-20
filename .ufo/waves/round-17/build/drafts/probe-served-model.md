# probe-served-model — independent evidence for the C1 served_model + route-match invariants

Seat: KamaR17.ProbeServedModel-2. Scratch experiment only; the nine matrix
`*.json` and `check.py` in `tests/probe-verdicts/` are untouched (byte-identical
copies were exercised under `/tmp`).

## Method

1. Copied `tests/probe-verdicts/` (`check.py` + the nine `*.json`) to
   `/tmp/ProbeServedModel-a/`.
2. Ran the scratch copy against the real probe:
   `python3 /tmp/ProbeServedModel-a/check.py --probe tools/kama-probe.sh --json`
   — exit 0, 72/72 rows pass (wall 37.6s). Redirected output lives outside the
   matrix dir: `load_matrix()` globs `CHECK_DIR/*.json`, so a `results.json`
   written into that directory would be parsed as a tenth matrix file and fail
   schema validation (observed: `invalid JSON: Expecting value`).
3. Re-derived the expected `served_model` for every row **from that row's own
   stub routes alone**, mirroring `classify()`'s branch structure
   (`tools/kama-probe.sh:453-570`) and the `served_ids()` precedence
   (`tools/kama-probe.sh:357-367`), then diffed prediction vs. observed.

## Verdict counts observed

| verdict | rows |
|---|---|
| FOREIGN_SERVICE | 37 |
| MODEL_LOADING | 17 |
| MODEL_OK | 8 |
| UNAUTHORIZED_SERVICE | 5 |
| MODEL_MISMATCH | 3 |
| DEAD | 1 |
| NOT_HTTP | 1 |

## Derived rule: (stub /v1/models route) -> served_model

`classify()` sets `C_SERVED` only inside the `2xx && body_has_model_array`
branch (kama-probe.sh:524-529); every other verdict path leaves the default `-`
(kama-probe.sh:455). The exact rule the repair should grade:

- Let `R` be the stub route bound to `/v1/models` (falling back to
  `default_route` when the route key is absent — this is the stub's own
  lookup rule, check.py:215-221).
- If `port_mode == "closed"`, or `R` is `raw: "close"`, or `R` is absent, or
  `R.status` is not 2xx, or `R`'s body has no `data`/`models` array →
  `served_model` MUST be `"-"`.
- Otherwise `served_model` MUST equal the comma-joined **raw** ids extracted by
  `served_ids()` precedence — `data[].id` → `models[].id` → `models[].name` →
  `models[].model` → top-level `id` — first non-empty group wins, order
  preserved, duplicates removed (kama-probe.sh:335-377). Empty id list → `"-"`.

Corollaries, all confirmed against the run:

- `served_model != "-"` occurs only for `MODEL_OK` and
  `MODEL_MISMATCH`/`served-id-mismatch`. All 11 non-dash rows are MODEL_OK (8)
  or MODEL_MISMATCH (3).
- `MODEL_MISMATCH`/`unresolvable-id` yields `-`, **not** the expected id —
  `model_matches` returns 2 when no id is extractable (kama-probe.sh:386-395).
  No current matrix row exercises this (a `data:[]` + non-wildcard `expect`
  case); a derived-invariant checker gets it for free, a
  "MODEL_MISMATCH ⇒ non-dash" checker would be wrong.
- `served_model` reports **raw** ids, never normalised:
  `ReadyControls.served-id-carries-gguf-suffix` records `kama-ready.gguf`
  (full suffix kept) while `expect: kama-ready` still yields MODEL_OK —
  normalisation lives only in `normalize_id`/`model_matches`
  (kama-probe.sh:380-397) and `served_persist` (kama-probe.sh:1007-1017).
  An invariant check must compare against raw stub ids, not basenames.
- Multi-id bodies join comma-separated with no spaces:
  `ReadyControls.second-data-id-match` → `kama-ready,tiny-vocab`.
- `MODEL_LOADING` always reports `-` even when the stub body is JSON —
  the loading check returns before `served_ids` runs (kama-probe.sh:505-510).
- `UNAUTHORIZED_SERVICE` (401/403) returns before any body extraction
  (kama-probe.sh:496-503): `-` even when the stub body carries a model array.
- Extraction-precedence confirmed live:
  `ReadyControls.ollama-name-not-served-id` serves a body whose `data` entries
  carry `id: kama-ready` while `models[].name` carries `stories260K` →
  `served_model` is `kama-ready` (data wins) → MODEL_MISMATCH.

Prediction-vs-observed diff over all 72 rows: **0 mismatches** — no row where
the probe's `served_model` looks wrong.

## Route-match: every stub row requested GET /v1/models

`requests` is recorded per row by the stub handler (check.py:214) before any
response is sent, so even `raw:"close"` and `send_error` paths record the hit.
All 71 stub-mode rows record `GET /v1/models` **as the first request**
(the single closed-port row, `AuthAndDead.closed-port-connection-refused`,
records none — that is expected, nothing listened). Follow-on requests match
`classify()` exactly: `GET /` + `GET /metrics` for FOREIGN_SERVICE evidence,
`GET /health` for MODEL_LOADING/2xx-model-array evidence, `GET /` for
UNAUTHORIZED evidence. Recorded `path` includes the query string verbatim;
the stub strips it only for route lookup (check.py:216-217).

## Gradeable-invariant formulation (for check.py repair)

1. **served_model invariant** — per row, compute the predicted value by the
   rule above from the row's own `routes`/`default_route`/`port_mode`, and
   require `record["served_model"] == predicted`. Pure function of the matrix
   row + observed field; needs no verdict coupling. (Optionally also assert
   consistency with `verdict`: non-dash `served_model` implies the verdict
   came through the 2xx+model-array branch, i.e. `MODEL_OK` or
   `MODEL_MISMATCH/served-id-mismatch`.)
2. **route-match invariant** — for `port_mode == "stub"` rows that reach
   verdict grading, require `GET /v1/models` among `record["requests"]`.
   Membership is the safe predicate (the probe's future evidence fetches could
   reorder); in today's probe it is also always first.

## Two live gaps in current check.py (both demonstrated on the scratch copy)

- **Malformed-output traceback.** `doc["rows"][0]` is guarded (check.py:330-332
  catches JSONDecodeError/KeyError/IndexError/TypeError) but `row.get(...)` at
  check.py:337-338 is *outside* that guard, and nothing catches
  `AttributeError` anywhere (outer `except` is OSError-only, check.py:349;
  `main` catches only HarnessError, check.py:479). A fake probe that hits the
  stub and prints `{"rows":[5]}` produces:
  `AttributeError: 'int' object has no attribute 'get'` at check.py:338 —
  full traceback, all remaining tests lost, exit 1 via propagating exception.
- **served_model + route-match ungraded.** A fake probe that fetches only
  `/health` (never `/v1/models`) and emits
  `verdict:MODEL_OK, reason:expected-wildcard, served_model:"FABRICATED-NOT-SERVED"`
  passes the row: `passed: true`, `requests: [GET /health]`. Confirms the
  round-16 mutation result — `served_model` is recorded but never graded, and
  requests are only checked for non-emptiness (check.py:323-328).

## Known limitations

- Prediction mirrors the python3-present probe path (`HAVE_PY=1`); the grep
  fallback (kama-probe.sh:371-376) can emit different ids for exotic bodies —
  irrelevant here (python3 present) but an invariant keyed to stub routes is
  probe-version independent anyway.
- `served_model` equality is a string compare; a probe emitting ids in a
  different order or with different dedup semantics would fail it. That is the
  desired strictness — the precedence/dedup is contract v2 documented
  behaviour (kama-probe.sh:43-48).
- Evidence was produced on the scratch copy; the lane files and probe were
  not modified. No ports other than the scratch stub's ephemeral loopback
  ports were bound; nothing on 8080/34113/registry ports.
