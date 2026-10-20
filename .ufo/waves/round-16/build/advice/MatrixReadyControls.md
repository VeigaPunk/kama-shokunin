# MatrixReadyControls — ReadyControls.json

## Files written
- `tests/probe-verdicts/ReadyControls.json` — 8 tests, all `port_mode: "stub"`, `default_route: null`; parses as a JSON array (validated with `python3 -c json.load`). Unique `ReadyControls.*` names.

## Oracle derivation (never executed the probe)
Verdicts/reasons/exits derived from `tools/kama-probe.sh` as written:
- `body_has_model_array` (tools/kama-probe.sh:392-411): object JSON with `data` or `models` as a list → eligible for the MODEL_OK/MODEL_MISMATCH branch; every test body carries both arrays.
- `served_ids` precedence (tools/kama-probe.sh:348-358): `data[].id` → `models[].id` → `models[].name` → `models[].model` → top-level `id`, first non-empty group wins. `aliases[]` and `owned_by` are never consulted.
- `normalize_id` (tools/kama-probe.sh:371): basename + strip ONE trailing `.gguf`, applied to both `--expect` and each served id.
- classify() arms (tools/kama-probe.sh:479-498): `''|'*'|'-'` → `expected-wildcard`; normalized match → `matched`; no match → `served-id-mismatch` (2); empty normalized expected → `unresolvable-id` (2). Exit 0 iff MODEL_OK.

## Test matrix
| name | --expect | oracle |
|---|---|---|
| expect-exact-id | `kama-ready` (== data[0].id) | MODEL_OK / matched / 0 |
| expect-wildcard-star | `*` | MODEL_OK / expected-wildcard / 0 |
| expect-wildcard-dash | `-` | MODEL_OK / expected-wildcard / 0 |
| expect-different-id | `qwen2.5-7b-instruct` | MODEL_MISMATCH / served-id-mismatch / 2 |
| expect-gguf-path-basename | `…/models/stories260K.gguf` vs served `stories260K` | MODEL_OK / matched / 0 |
| served-id-carries-gguf-suffix | `kama-ready` vs served `kama-ready.gguf` | MODEL_OK / matched / 0 |
| ollama-name-not-served-id | `stories260K` (== models[].name and data[].aliases, ≠ data[].id) | MODEL_MISMATCH / served-id-mismatch / 2 |
| second-data-id-match | `tiny-vocab` (== data[1].id) | MODEL_OK / matched / 0 |

Bodies mirror the L1 smoke observation of ready b11755: `data[]` with `id`, `object`, `created`, `owned_by: "llamacpp"`, `aliases`, plus an Ollama-shaped `models[]` (`name`, `model`, `size`, `digest`, `details`). `Server: llama.cpp` and `Content-Type: application/json` headers are set for realism (evidence text only — neither affects the verdict). Some rows include `/health` → 200 `{"status":"ok"}` for realism; `/health` feeds only the evidence string (probe.sh:500-501), not the verdict.

## Design choices
- All-ready 2xx bodies → nothing can satisfy a `MODEL_LOADING` oracle, so the file is a pure positive-control set: any "everything is MODEL_LOADING" or "any 200 is MODEL_OK" implementation fails (the three MODEL_MISMATCH rows), and a "matching id → MODEL_LOADING" implementation fails the five MODEL_OK rows.
- `ollama-name-not-served-id` pins the `data[].id`-precedence rule: an implementation that accepted `models[].name`/`model` or `aliases` as served ids would wrongly pass this row.
- `second-data-id-match` guards against first-entry-only id extraction (llama.cpp router mode serves multiple `data[]` entries).
- `served-id-carries-gguf-suffix` pins symmetric `normalize_id` on the served side.

## Known limitations
- No `unresolvable-id` row: reaching it on a 2xx-with-model-array body requires `--expect` to normalize to empty (e.g. `.gguf` alone), which is a degenerate CLI input better owned by another family; adding it here would blur this file's "ready controls" scope.
- `expected-wildcard` empty-string expect (`--expect ""`) omitted for the same reason; `*` and `-` cover the wildcard arm.
- Evidence strings are not asserted by the schema, so the `/health` routes are decorative; if the harness ever asserts evidence text, `GET /health -> 200|application/json` would appear only on rows that define the route.
- Nothing in this file exercises the loading 503 path — by design (positive controls only, per assignment).

## Installs
None.
