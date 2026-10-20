# Probe health body — byte-exact `/health` observation of llama-server b11755 (draft)

Owner: KamaR17.ProbeHealthBody-2 (round 17, build wave). Status: draft for L1 to integrate. Feeds the C2 `health_ready` predicate in receipt `kama-llamacpp-live/v2` (exact-body grading) and the fake-server controls in `tests/llamacpp-live/controls.py`.

## Method

One server, one capture, GET/HEAD only (no POST, no generation). Scratch script under `/tmp/KamaR17.ProbeHealthBody-2/` (removed after capture). Launch argv mirrors `tools/kama-llamacpp-live.py:860-869`:

```
/home/vgpnk/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf \
  --alias kama-health-body-probe --host 127.0.0.1 --port 38739 -c 256 -t 4 --no-webui --offline
```

Model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches context pin). Port 38739 chosen by `bind(127.0.0.1, 0)`; not in `registry/endpoint-consumers.tsv`. Poll: `http.client` keep-alive GET `/health`, no sleep, from before first accept until 200; then 10 fresh-connection samples; then variants. Teardown: SIGTERM, `term_wait_ms 113.4`, `returncode 0`, no SIGKILL; post-teardown GET → `ConnectionRefusedError`; `ss -ltn` clean (no listener on 38739, no `llama` listener).

## Findings — byte-exact

### (a) Loading window (from first accept)

First accept at t=6.765 ms after `Popen`; the listener is bound before the model is ready. Every `/health` answer during loading was the generic 503 envelope — **the same body the loading middleware returns for every non-frontend path** (matches pinned source: `middleware_server_state` 503s all non-frontend, non-OPTIONS paths while `!is_ready`, `.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp:307-328`):

- status: `503`; observed 46 consecutive identical responses, t=6.765→11.644 ms; first `200` at t=11.732 ms (loading-answer window ≈5.0 ms).
- body hex (75 bytes): `7b226572726f72223a7b226d657373616765223a224c6f6164696e67206d6f64656c222c2274797065223a22756e617661696c61626c655f6572726f72222c22636f6465223a3530337d7d`
- body decoded: `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` — no trailing newline; sha256 `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c`.
- headers: `Server: llama.cpp`, `Content-Type: application/json; charset=utf-8`, `Content-Length: 75`.

### (b) Ready state (10 samples)

All 10 samples byte-identical:

- status: `200`.
- body hex (15 bytes): `7b22737461747573223a226f6b227d` = `{"status":"ok"}` — **exactly**, no whitespace, no trailing newline; sha256 `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288`.
- headers: `Server: llama.cpp`, `Content-Type: application/json; charset=utf-8`, `Content-Length: 15`.

`{"status":"ok"}` is exactly the ready body on b11755 with this fixture. An exact-byte check is implementable; no drift observed across samples.

### (c) Variants

- `GET /health?include_slots` → `200`, body `{"status":"ok"}` (15 bytes) — query parameter **ignored**; identical to bare `/health`. Same for `include_slots=true`. A fake server that expands the body when `include_slots` is present would diverge from the real subject.
- `HEAD /health` → `200`, same headers (`Content-Length: 15`) with an empty body — supported. A `health_ready` check that needs the body must use GET.
- `GET /slots` → `200`, 253 bytes: `[{"id":0,"n_ctx":256,"speculative":false,"is_processing":false},{...id 1..3 same}]` — 4 slots (default `-np 4`), all `is_processing:false`, `n_ctx` echoes `-c 256`.
- `GET /v1/models` → `200`, 706 bytes; `data[0].id == "kama-health-body-probe"` (the `--alias`), `data[0].meta.n_ctx == 256`, `object == "list"`. (Full body retained in scratch `result.json` during capture; digest of observation only.)

### (d) Busy state

Not induced (GET-only constraint honoured). `/slots` before and after the variant probes showed `is_processing:false` on all 4 slots. Whether `/health` stays `200 {"status":"ok"}` while slots are busy is unverified this round — flag for controls design: a fake server that flips `/health` to non-200 under load has no observed real-subject analogue.

## Design implications for `kama-llamacpp-live/v2` `health_ready`

1. Grade `status == 200` **and** `body == b'{"status":"ok"}'` exactly (byte-compare or sha256 `a29ee2b1…`). A `200 {"status":"degraded"}` fails under v2; it passes under v1 (`tools/kama-llamacpp-live.py:78-82` documents status-only intent).
2. The loading body is the shared 503 envelope, not a `/health`-specific body — a `loading_envelope_exact` check must expect `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` on `/health`, `/v1/models`, and every other non-frontend path alike.
3. `Content-Length` is fixed (15 ready / 75 loading) — a body-exact check makes the length header redundant but keeping it costs nothing.
4. `include_slots` is a no-op: do not let controls assert slot expansion from `/health`; use `/slots` if slot state is wanted.
5. `HEAD /health` works and returns 200 with no body — v2 predicates must remain GET-based to grade the body.

## Limitations

- Single run, single model (stories260K, ~1.1 MB). The ≈5 ms loading-answer window is this fixture's; larger models widen it, none of the bytes change [INFERENCE].
- Busy-slot `/health` unobserved (no generation allowed).
- `Server: llama.cpp` and `Content-Type: application/json; charset=utf-8` observed but not proposed as graded fields — upstream could legitimately vary them; the body is the stable contract.
