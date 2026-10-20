# MatrixNonLoadingStatuses — advice (C1, calibration)

## Files changed
- `tests/probe-verdicts/NonLoadingStatuses.json` — new; 7 tests, all `NonLoadingStatuses.` prefixed, `port_mode: stub`, literal stub-matrix schema. Parses as JSON (verified via `python3 json.load`; 7 unique names).

## Design
- Family: the exact llama.cpp b11755 loading envelope `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` served on `GET /v1/models` at statuses **other than 503**. Purpose: prove the C1 `MODEL_LOADING`/`llamacpp-loading` matcher requires status 503, not just the body.
- Oracle values derived statically from `tools/kama-probe.sh` `classify()` (lines 415-525), never by running the probe:
  - Body has no `data`/`models` array → `has_models=0` → MODEL_OK unreachable (line 477-479).
  - Non-503 statuses bypass the new 503-gated loading branch → terminal FOREIGN_SERVICE block (lines 513-523).
  - 2xx + `*json*` CT → `schema-unrecognized`; 2xx non-JSON CT → `non-model-2xx`; all non-2xx (non-401/403) → `non-2xx-non-model-http` (lines 458-461, 514-521). All exit 2.
- Test rows:
  - `ok200-json-envelope` — 200 + JSON CT → FOREIGN_SERVICE / schema-unrecognized.
  - `ok200-plain-envelope` — 200 + text/plain → FOREIGN_SERVICE / non-model-2xx (CT selects the reason).
  - `err500-envelope`, `err502-envelope`, `err504-envelope` — the assigned 5xx statuses → non-2xx-non-model-http.
  - `err404-envelope`, `err429-envelope` — added coverage: non-5xx non-2xx statuses also hold FOREIGN_SERVICE; 404 is the schema's default_route shape, 429 a realistic throttle. Both within the 4-10 budget.
- `default_route: null` on all rows → `/`, `/health`, `/metrics` probes return 404/empty and cannot perturb classification.
- `expect: "stories260K"` uniform: verdict is expectation-independent here; the field only matters on the MODEL_OK path.
- 503 deliberately absent (sibling `MatrixOverbroad503` owns the 503 gate/body-variation axis; `MatrixEnvelopeShapes` owns body-shape variation). No overlap by design.

## Known limitations
- Statuses 401/403 excluded: they hit UNAUTHORIZED_SERVICE before the loading check, not FOREIGN_SERVICE — out of this family's claim.
- Assumes the stub harness honors `body_json` verbatim and that `curl` reports `F_CODE` equal to the stub status; both per the shared schema.
- A boundary status like 503-with-wrong-body is intentionally left to siblings to keep family claims disjoint.

## Installs
- None.
