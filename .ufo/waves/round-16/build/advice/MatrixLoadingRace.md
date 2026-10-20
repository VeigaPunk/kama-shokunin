# MatrixLoadingRace — LoadingRace.json advice

## Deliverable
- `tests/probe-verdicts/LoadingRace.json` — 9 tests, `family: "LoadingRace"`, names `LoadingRace.*`, all `port_mode: "stub"`. Parses as JSON (`json.load`, verified).

## Design (oracle values read from classify(), not computed)
Source basis, `tools/kama-probe.sh`:
- `classify()` fetches `/v1/models` first and lets the C1 rule key on it (kama-probe.sh:418, 458-524).
- `/health` is fetched only inside the `MODEL_OK` evidence branch (`h=$(probe_short "$port" "/health")`, kama-probe.sh:500-501); it is never consulted for non-OK paths.
- Therefore any `/health` state (200 ok / explicit 404 / unlisted->stub 404 / loading envelope / raw-close) combined with an exact loading envelope on `/v1/models` must still yield `MODEL_LOADING`/`llamacpp-loading`/exit 2 — the frozen probe reports `FOREIGN_SERVICE`/`non-2xx-non-model-http`/exit 2 here (red side).
- Inverse race: `/health` = loading envelope while `/v1/models` is 200 with a model array. The `is2 && has_models` branch (kama-probe.sh:479-498) decides before any envelope check can fire:
  - id match on `--expect stories260K` -> `MODEL_OK`/`matched`/exit 0.
  - `--expect *` -> `MODEL_OK`/`expected-wildcard`/exit 0.
  - id mismatch (`--expect qwen3-8b`) -> `MODEL_MISMATCH`/`served-id-mismatch`/exit 2 — included so the inverse direction cannot be satisfied by an always-OK implementation.
- Race boundary: `/health` 200 ok + `/v1/models` 503 with a *non-exact* `unavailable_error` ("no slot available") -> stays `FOREIGN_SERVICE`/`non-2xx-non-model-http`/exit 2 per the C1 scope limit; defeats a loading-all blanket.
- Envelope kept byte-exact to the observed b11755 body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`; `Server: llama.cpp` and `Content-Type: application/json` mirror the real server. `served_ids` reads `data[].id` (kama-probe.sh:325).

## Coverage / limitations
- Does not cover near-miss envelope field variants (wrong code/type/message) — owned by MatrixEnvelopeShapes / MatrixOverbroad503 siblings.
- Reachability caveat (peer E11, ConnectKengaku): on b11755 one atomic `is_ready` gates both `/v1/models` and `/health`, so health-green/models-loading and the inverse health-loading/models-ready pairs are unreachable on the real server. Those cases are synthetic probe-robustness controls only; `why` lines were reworded to say so. `HealthAlsoLoading` remains the b11755-faithful fixture.
- `default_route: null` means unlisted `/` and `/metrics` probes (used only for FOREIGN evidence strings) get stub 404; verdicts never depend on them.
- Expected exit codes follow the contract rule: 0 iff `MODEL_OK` else 2; `MODEL_LOADING` exits 2.
- Oracles are literal derivations from the C1 rule text + classify() source; never executed against the probe. All measurements belong to L1.

## Installs
None.
