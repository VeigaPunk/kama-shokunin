# MatrixLoadingEnvelope — round 16 build advice (C1)

## Deliverable

- `tests/probe-verdicts/LoadingEnvelope.json` — 8 literal stub-matrix tests, all positive
  oracle cases for the C1 loading-envelope rule. Every test expects
  `MODEL_LOADING` / `llamacpp-loading` / exit 2. No probe execution was performed
  (L1 owns all measurement); oracles were derived from the C1 rule text and
  `tools/kama-probe.sh:415-525` (classify) read directly.

## Design choices

- **Canonical wire body** (`canonical-alias`): byte-exact
  `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
  served on `/v1/models` and `/health` via `body_text`, matching the pinned
  llama.cpp b11755 source
  (`.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp:307-325`:
  `res.status = 503` + that JSON on every non-frontend path while `!is_ready`)
  and the L1 smoke observation.
- **`--expect` triplet covered**: `stories260K` (alias, the pinned GGUF basename),
  `*`, and `-` — all three hit classify()'s wildcard/id branches identically
  (`kama-probe.sh:487-498`) and none may promote to `expected-wildcard` or
  `matched` because no model array exists.
- **Header independence**: `no-server-header` drops `Server: llama.cpp`
  (classify documents a Server header is never proof on its own,
  `kama-probe.sh:390-391`); `plain-json-content-type` uses bare
  `application/json` without `; charset=utf-8`. Both must still fire — the rule
  is status-503 + body-envelope only.
- **Structural, not literal, body match**: `key-order-permuted`
  (`type,code,message` serialization order) and `pretty-printed-body` prove a
  JSON-object implementation is required; a byte compare or regex on key order
  would fail these.
- **`every-non-frontend-path`**: `routes: {}` with `default_route` returning the
  envelope — mirrors middleware semantics where `/v1/models` and `/health`
  resolve through the catch-all. Other tests set `default_route` to the
  envelope or `null` (both faithful; the verdict only consumes `/v1/models`,
  and the envelope route is always correct for `/health`/`/`/`/metrics` under
  `!is_ready` for non-frontend paths).
- Family/name conventions and `expected`/`expect` key names copied verbatim
  from sibling `tests/probe-verdicts/Overbroad503.json`.

## Positive-control coverage note

Sibling `Overbroad503.json` already covers the negative envelope-space
(lowercase message, `no slot available`, string code `503`, server_error type,
missing `error` wrapper, plaintext, HTML-503), so this file stays purely
positive per the assignment. Together the two files should defeat both a
reject-all and a loading-all implementation.

## Verification performed

- `python3 -c "json.load(...)"` parse check: **ok, 8 tests**; asserted
  name prefix, family string, and uniform oracle `{MODEL_LOADING,
  llamacpp-loading, exit 2}`. This is the only check my brief permits; L1 runs
  the stub harness against frozen + repaired probes.

## Known limitations

- The stub cannot reproduce frontend-path behavior (llama.cpp lets `/`,
  `/index.html` etc. serve the loading SPA under `!is_ready`,
  `server-http.cpp:309-311`). `default_route: envelope` treats `/` as
  non-frontend — harmless to the verdict, noted for fidelity.
- Tests assume the C1 rule triggers on `/v1/models`'s 503 response alone, which
  is the only body classify() inspects before verdict; `/health` bodies are
  realism, not oracle input.
- No installs, no edits outside the owned file. Advice only; no verdicts.
