# MatrixOverbroad503 — C1 negative controls for the MODEL_LOADING envelope

## Deliverable
- `tests/probe-verdicts/Overbroad503.json` — 8 stub-matrix tests, all `port_mode: "stub"`, `expect: "*"`.

## Coverage
Each test serves a 503 on `/v1/models` that fails **exactly one** condition of the C1 envelope rule (503 AND JSON object whose `error` object has `message == "Loading model"`, `type == "unavailable_error"`, integer `code == 503`), so a passing matrix proves the fix is not overbroad:

| Test | Violated condition | Expected |
|---|---|---|
| `nginx-html-503` | not JSON at all (text/html) | FOREIGN_SERVICE / html-non-model / 2 |
| `error-string` | `error` is a string, not an object | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| `no-slot-available` | `message` ("no slot available" — real llama.cpp busy error, per C1 scope limit) | same |
| `lowercase-loading` | `message` case ("loading model") | same |
| `server-error-type` | `type` (server_error) | same |
| `code-string` | `code` is `"503"` string, not integer | same |
| `no-error-wrapper` | fields at top level, no `error` member | same |
| `plaintext-loading` | text/plain "Loading model", not the JSON envelope | same |

## Oracle derivation (not executed)
From `tools/kama-probe.sh:415-525` (frozen probe): `F_RC=0`, `F_CODE=503` → not DEAD/NOT_HTTP/UNAUTHORIZED; not 2xx-with-model-array → falls to the bottom branch. `ishtml=1` (Content-Type `*html*` or `<html`/`<!doctype` body sniff at `:470-475`) → `html-non-model`; all other rows → `non-2xx-non-model-http` (`:521`). `body_json` never parses to a dict with `data`/`models` list keys, so `has_models=0` holds everywhere. Exit 2 for all non-MODEL_OK verdicts.

## Design choices
- Only `/v1/models` is routed; `default_route: null` makes the probe's auxiliary `/` and `/health` pokes return 404, which cannot alter these verdicts.
- `expect: "*"` — model matching is never reached on a 503, so the wildcard cannot mask a mis-verdict.
- 8 tests (within the 4–10 band), one per distinct failure axis; `default_route` 404s are implicit and uncounted.

## Known limitations
- Oracles are literal values derived from classify() source + C1 rule text, per assignment; nothing was executed against a stub.
- No positive (exact-envelope → MODEL_LOADING) test here — that is presumed owned by `ProbeLoadingVerdict`'s matrix; this file is purely negative control.
- No `closed`-mode or raw-close rows; the family is defined as 503-body overreach only.
- Assumes the runner invokes `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1` exactly as specified in the shared schema.

## Installs
None.
