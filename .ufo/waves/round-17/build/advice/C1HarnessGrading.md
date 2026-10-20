VERDICT: confirm — check.py now grades served_model + GET /v1/models route-match per row, malformed probe output is a recorded failure not a traceback, and all 72 matrix rows still pass (advice run, 37.7s).

# Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py`
  sha256 `b460b7867b4970a33f5202faec9b32d28f6e58f2b87c794b5446628ac65f3c58`

No `*.json` in the matrix dir was touched (set digest preserved); `__pycache__` side-effects removed; no other files written.

# What changed

## 1. `served_model` grading (`served_model_ok`, `served_model_expected` per row)

`expected_served_model(test, verdict)` (check.py:339) re-derives the contract
value from the row's own literal stub routes, keyed on the **observed**
verdict:

- `MODEL_OK` / `MODEL_MISMATCH` → comma-joined ids extracted from the
  effective `/v1/models` route body (`routes["/v1/models"]` →
  `default_route` → implicit 404/`raw:close` ⇒ `"-"`) via the probe's
  `served_ids()` precedence — docstring cites kama-probe.sh:335-368 and the
  `is2 && has_models` arm at 524-529 where `C_SERVED` is the only place it
  is ever set.
- Every other verdict (`DEAD`, `NOT_HTTP`, `FOREIGN_SERVICE`,
  `UNAUTHORIZED_SERVICE`, `MODEL_LOADING`, any unknown) → `"-"`, because
  `classify()` (kama-probe.sh:455) returns with `C_SERVED` still `'-'` on
  every other arm. This direction also fails a mutant that reports a served
  id for a dead endpoint, or `-` for a served model.

Extraction mirrors the probe's python3 path exactly (dict required,
first-non-empty group wins `data[].id → models[].id → models[].name →
models[].model → top-level id`, `dict.fromkeys` dedup). Both
`served_model_ok` and `served_model_expected` are recorded per row;
`served_model_ok` is a conjunct of `passed`.

## 2. Route-match (`route_ok` per row)

`fetched_models_route(test, requests)` returns `None` for `port_mode
"closed"` (exempt) else whether the stub recorded `GET` on
`/v1/models` (query stripped, matching the handler's own `?`-split fallback).
Folded into `passed` as `record["route_ok"] is not False`, so `None`
(closed rows, pre-parse early exits) never blocks and only a proven miss
fails. Computed in the timeout branch too.

## 3. Malformed probe output → per-row failure

`probe_output_row(stdout)` enforces: stdout parses to one JSON object;
`rows` is a non-empty list; `rows[0]` is an object with `verdict`/`reason`
strings and `drift` bool. Any deviation sets `record["error"] =
"malformed probe output: <why>; stdout=… stderr=…"` and the row continues
— the old `doc["rows"][0]` path could traceback on `TypeError`/`KeyError`
outside its narrow except tuple, and silently `None`-graded missing keys.
Verified: `''`, `'not json'`, `'[1,2]'`, `'{"rows":[]}'`, `'{"rows":[42]}'`,
non-string `verdict` all → recorded error, no traceback.

## 4. `--selftest` reaches the duplicate-name guard

`load_matrix()` now takes `directory=CHECK_DIR`; selftest writes two files
with the same test name into a `tempfile.TemporaryDirectory` (never the
matrix dir) and asserts `HarnessError`. Result is appended to the existing
`results` list — `malformed_tests` now counts 5. 5/5 rejected in the run.

## 5. Preserved contract

CLI flags unchanged (help text widened for `--selftest`); exits 0/1/2
unchanged; schema `kama-probe-verdicts/v1` and all existing per-row keys
unchanged — only `route_ok`, `served_model_expected`, `served_model_ok`
added. `human_summary` appends `served_model=… (expected …)` and
`route=missing-GET-/v1/models` only on failures. Timeouts untouched.

# Verification (advice only; L1 re-measures)

- `python3 check.py --json` → `tests=72 passes=72 failures=0`, exit 0.
  `served_model_expected`/`served_model_ok`/`route_ok` populated correctly
  on all row kinds incl. closed-port (`route_ok: null`) and raw-close.
- `check.py --selftest --only ReadyControls.expect-exact-id` →
  `selftest: 5/5 malformed tests rejected (ok)`.
- `python3 -B` helper probe: malformed outputs all rejected; no `__pycache__`
  left behind (dir listing re-verified clean after sentinel report).

# Known limitations

- [INFERENCE] served-model derivation mirrors the probe's *python3* path;
  the no-python3 grep fallback could legitimately differ on exotic
  `body_text` — not reachable in this lane (python3 is a harness dep).
- `served_model_ok` on an observed wrong verdict is graded against the
  *observed* verdict's contract arm, so a mutant that both misclassifies
  and mis-reports is still failed (verdict mismatch does that anyway).
- No installs; no tools installed or upgraded this session.
