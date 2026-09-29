# Binding-contract mutation matrix

Axis: operability (fresh live re-verification). The repository currently has no `tools/kama-probe.sh` or `registry/endpoint-consumers.tsv`, so this lesson records executable fixtures and the contract-level observations that the L1 implementation must satisfy. Live claims below were re-verified on 2026-09-28.
The stale-port census also includes `/home/vgpnk/.local/bin/the-janitor:16-19`: `MODEL_PROVIDER="qwen-local"`, `MODEL_ID="Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS"`, and `MODEL_ENDPOINT="http://127.0.0.1:8080/v1"` (verified directly). This shell consumer is outside the opencode tree and MUST be represented in the registry or `check` can report a false-clean fleet. The distiller consumer has an explicit cloud cascade and should be marked cascade-protected, but remains declared.

## Matrix

| Mutation | Fixture command | Expected verdict | Observed | Gap |
|---|---|---|---|---|
| M1 stale port serving a foreign HTTP service | `curl -sS --max-time 2 -D - http://127.0.0.1:8080/v1/models` | `FOREIGN_SERVICE` | **RIGHT**: `HTTP/1.1 404 Not Found`; `Content-Type: text/html;charset=iso-8859-1` (the body is Jetty HTML) | None for this classification. This is the real stale pin: L1-F3, while the model is live on 34113 (L1-F4/L1-F5). |
| M2 stale port with nothing listening | `python3 -c 'import socket,time; s=socket.socket(); s.bind(("127.0.0.1",18766)); s.listen(); time.sleep(0.2)'`; after it exits: `curl -sS --max-time 2 http://127.0.0.1:18766/v1/models` | `DEAD` | **RIGHT by rule**: connection-refused is explicitly `DEAD`; no listener remained after the bind-and-kill fixture. | No target script exists yet to execute the classification. |
| M3 port moved, consumers updated, served id unchanged | Start the declared server on 18767, register `http://127.0.0.1:18767/v1`, and serve the same expected id; then run `check --json` | `MODEL_OK` | **RIGHT by rule**: 2xx JSON `models[]`, served id equal to expected id | No target script/registry exists, so end-to-end execution is unavailable. |
| M4 right port, wrong model from look-alike JSON server | Fixture: `python3 /tmp/kama-mutation/m4_stub.py` (HTTP server on 127.0.0.1:18764; returns `{"models":[{"id":"other"}]}`); observed command: `curl -sS --max-time 2 -D /tmp/kama-mutation/m4.headers http://127.0.0.1:18764/v1/models` | `MODEL_MISMATCH` | **EXECUTED**: `HTTP/1.0 200 OK`, `Content-Type: application/json`, body `{"models":[{"id":"other"}]}`. Contract comparison yields `MODEL_MISMATCH`. | Probe must inspect both `models[].id` and the llama.cpp `name`/`model` shape, or document the accepted field. The fixture proves a non-llama look-alike is still classifiable by the generic rule. |
| M5 auth-protected model port | `curl -sS --max-time 2 -D - http://127.0.0.1:8790/v1/models` | `UNAUTHORIZED_SERVICE` | **EXECUTED**: `HTTP/1.1 401 Unauthorized`, `Content-Type: application/json`; contract yields `UNAUTHORIZED_SERVICE`. | None for 401/403 precedence. |
| M6 non-HTTP bytes | `python3 /tmp/kama-mutation/m6_stub.py` accepts one connection and sends `garbage\\n`; then `curl -sS --max-time 2 http://127.0.0.1:18765/v1/models` | `NOT_HTTP` | **EXECUTED**: curl returned rc=1 in 17 ms: `curl: (1) Received HTTP/0.9 when not allowed`. It did not hang with the explicit 2-second timeout. | **MISS/undefined**: the contract names `NOT_HTTP` but does not define how to detect malformed bytes or whether the probe has a mandatory connect/read timeout. Without a timeout, a silent listener can hang indefinitely. `nc` was unavailable, so the equivalent real TCP fixture used Python (the artifact's declared optional Python dependency is sufficient for this fixture). |
| M7 real llama.cpp id is an absolute path | `curl http://127.0.0.1:34113/v1/models` | `MODEL_OK` if expected id is the served id; otherwise `MODEL_MISMATCH` | **SPEC HOLE / highest risk**: live response is 200 JSON, `Server: llama.cpp`, and `models[0].name`/`model` is `/scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`; the service's alias is the same absolute path (L1-F4, command output). The contract does not define whether comparison uses `models[].id`, `name`, `model`, `data[].id`, or basename normalization. A basename expected id therefore cannot be proven equal by the current string rule. |

## Reproduction fixtures

Created under `/tmp/kama-mutation/`:

- `m4_stub.py`: deterministic 200 JSON look-alike returning model id `other` on port 18764. Observed output: `HTTP/1.0 200 OK`, `Content-Type: application/json`, `{"models":[{"id":"other"}]}`.
- `m6_stub.py`: deterministic TCP listener on port 18765 sending non-HTTP bytes and closing. Observed curl rc=1, elapsed 17 ms, `Received HTTP/0.9 when not allowed`.

These are scratch fixtures, not repository dependencies. The live M1/M5/M7 probes were metadata-only and sent no credentials.

## Contract holes to patch, ordered by risk

1. **M7 identity semantics (highest risk):** define one canonical served-id extraction order (`models[].id`, then `models[].name`/`model`, or an explicit llama.cpp mapping) and exact-vs-basename/path normalization. The real 34113 response is path-shaped, so current vocabulary alone cannot establish `MODEL_OK`.
2. **M6 timeout and malformed-response behavior:** require bounded connect and read/header/body timeouts; classify malformed/non-HTTP bytes as `NOT_HTTP` rather than surfacing a curl-specific error or hanging.
3. **M4 schema boundary:** define whether a generic JSON `models[]` response is trusted, and which field(s) constitute its served id. Rejecting an unrecognized schema should have a specified verdict (currently unspecified).
4. **M2 transport detail:** specify whether DNS errors, connection reset, and timeout all map to `DEAD`, and preserve exit code 1 for probe/tool errors only.
5. **M3 registry execution:** ship the probe and registry artifacts so consumer reconciliation can be run rather than inferred from the contract.

## Evidence anchors

- L1-F3: real 8080 is Jetty HTML 404, not the model API.
- L1-F4/L1-F5: real llama.cpp is on 34113; `/v1/models` is JSON and `/health` is `{"status":"ok"}`.
- L1-F6/L1-F7: consumers still pin `http://localhost:8080/v1` / `127.0.0.1:8080/v1`.
- L1-F8/L1-F9: active service uses 34113; the stale 8080 pin originated in the old unit.
- Live census: `/home/vgpnk/.local/bin/the-janitor:16-19` is a fourth stale-port pin, in addition to the opencode provider and agent pins.
- Live commands and outputs are recorded in the matrix and fixture files above.
