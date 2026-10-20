VERDICT: confirm — b11755 `/health` ready body is byte-exact `{"status":"ok"}` (15 bytes, sha256 a29ee2b1…); loading answers are the shared 503 envelope; `include_slots` is ignored; HEAD works.

## What was run

- One `llama-server` b11755 (`~/.local/opt/llama-b11755/llama-server`, resolved from `~/.local/bin/llama-server`), model `~/.cache/kama-shokunin/models/stories260K.gguf` sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, argv matching `tools/kama-llamacpp-live.py:860-869` (`--alias kama-health-body-probe --host 127.0.0.1 --port 38739 -c 256 -t 4 --no-webui --offline`). Ephemeral port 38739 via `bind(:0)`; not in `registry/endpoint-consumers.tsv`.
- GET/HEAD only; no POST, no generation. Poll from before first accept on a keep-alive `http.client` connection, then 10 fresh-connection ready samples, then variants. SIGTERM teardown: `term_wait_ms 113.4`, `returncode 0`, no SIGKILL; post-teardown GET refused; `ss -ltn` shows no listener on 38739.

## Byte-exact results

- Loading `GET /health` (46 identical responses, t=6.765–11.644 ms after spawn; first 200 at t=11.732): status `503`, `Content-Type: application/json; charset=utf-8`, `Content-Length: 75`, body hex `7b226572726f72223a7b226d657373616765223a224c6f6164696e67206d6f64656c222c2274797065223a22756e617661696c61626c655f6572726f72222c22636f6465223a3530337d7d` = `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (sha256 `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c`). No trailing newline. Same envelope the loading middleware gives every non-frontend path (pinned source `.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp:307-328`).
- Ready `GET /health` (10/10 identical): status `200`, `Content-Type: application/json; charset=utf-8`, `Content-Length: 15`, body hex `7b22737461747573223a226f6b227d` = `{"status":"ok"}` exactly (sha256 `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288`), `Server: llama.cpp`.
- `GET /health?include_slots` and `?include_slots=true` → `200 {"status":"ok"}` — parameter ignored, no slot expansion.
- `HEAD /health` → `200`, same headers (`Content-Length: 15`), empty body.
- `GET /slots` → `200`, 253 bytes, 4 slots all `"is_processing":false`, `"n_ctx":256`.
- `GET /v1/models` → `200`, 706 bytes, `data[0].id` == `--alias`, `meta.n_ctx` == 256.
- Busy `/health` unobserved (GET-only honoured).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ProbeHealthBody.md` — this report.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/drafts/probe-health-body.md` — sha256 `c991877d3e399ba406a1472d9e095fa1e16e138bdd33cae1784ccf9b4e7754a2`.
Design implication for C2 `health_ready` v2: grade `status==200 AND body==b'{"status":"ok"}'` exactly; a `200 {"status":"degraded"}` fails v2 while passing v1's status-only check (`tools/kama-llamacpp-live.py:78-82`). `loading_envelope_exact` must expect the shared envelope on `/health` too — `/health` is not exempt from the loading gate.

## Limitations / inferences

- Single run, ~1.1 MB fixture model; the ≈5 ms loading window is fixture-specific — bytes are the contract, not the timing. [INFERENCE for larger models]
- Busy-slot `/health` behaviour unverified; controls should not assert a busy-state body.
- `Server`/`Content-Type` headers observed but not recommended as graded fields.

## Installs

None. Tools used: `python3 3.14.8` (stdlib `http.client`/`socket`/`subprocess`), `ss`, `sha256sum` — all pre-existing.
