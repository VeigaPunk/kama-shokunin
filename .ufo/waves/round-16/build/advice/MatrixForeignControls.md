# KamaR16.MatrixForeignControls — advice

## File written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ForeignControls.json` — new stub-matrix file, 8 tests, `Family` = `ForeignControls`. Validated as JSON only (`python3 json.load` + schema-shape assertions; OK, 8 tests, unique `ForeignControls.*` names). Probe was never run — expected values are literal oracles from the C1 rule text and `classify()` source.

## Oracle derivation (evidence, tools/kama-probe.sh @ 746C)
- `html-non-model`: `classify()` lines 506-511 — HTML via Content-Type or body sniff at ANY status → `FOREIGN_SERVICE`.
- `schema-unrecognized` / `non-model-2xx`: lines 514-519 — 2xx, no model array; json CT → `schema-unrecognized`, else `non-model-2xx`.
- `non-2xx-non-model-http`: lines 520-522 — any non-2xx from a non-model service.
- `body_has_model_array` (392-411): requires `data` or `models` as a JSON **list**; object-valued `data` fails.
- Exit code: 0 iff `MODEL_OK`, else 2 → all 8 tests expect `exit: 2`.

## Design choices
- All tests `port_mode: "stub"`, `default_route: null` — evidence-only fetches (`/`, `/health`, `/metrics` via `probe_short`/`metrics_trap`, lines 306-324, 463, 500-501, 509-522) get the schema 404/empty-body and never change a `FOREIGN_SERVICE` verdict.
- `expect: "*"` — verdict is determined before `--expect` matching (matching only runs inside the `MODEL_OK` branch, 487-498), so wildcard keeps the matrix declarative.
- Tests cover every required row plus three guards:
  - `json-data-object-not-array` — defeats a naive `"data" key present` model check.
  - `busy-unavailable-error` — 503 `"no slot available"` `unavailable_error` (C1-named scope limit): matches llama.cpp type+code, not the exact `"Loading model"` message.
  - `loading-message-wrong-type` — 503 `"Loading model"` with `server_error`: defeats a message-only `MODEL_LOADING` implementation.
- Together they bound the C1 rule on both sides: same-message-wrong-type and same-type-wrong-message both stay `FOREIGN_SERVICE`.

## Known limitations
- No negative control for a JSON 200 that *does* contain a model array (that is the `MODEL_OK` family's job, not this file's).
- Oracles assume python3 present (`HAVE_PY=1`); the grep fallback at line 410 would behave identically for these bodies.
- No installs made; no pacman transaction attempted (pause respected).
