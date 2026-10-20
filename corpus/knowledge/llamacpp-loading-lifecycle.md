source: S036 (llama.cpp `tools/server/server-http.cpp` @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad = release b11755, `middleware_server_state` lines 307-328, pre-routing order 347-359); S037 (`tools/server/server.cpp` @ same commit, lines 440-515); S035 (README @ same commit, §GET `/health` lines 479-490, §GET `/v1/models` line 1258); S038 (release b11755 asset identity); S039 (pinned GGUF identity); S040 (llm-d v0.10 readiness-probe page, liveness versus model-aware readiness); S017 (Kubernetes probe lifecycle vocabulary); S041 (own-work live receipt `.ufo/waves/round-16/live/receipt.json`)
verified-at: 2026-10-20 — upstream files fetched at the pinned commit and saved with digests under `.ufo/waves/round-16/sources/llama.cpp-704366d/`; final live run 2026-10-20T14:06:27.859Z–14:06:27.974Z by L1 through `tools/kama-llamacpp-live.py` (sha256 b8c5e8d4…); stub matrix run by L1 through `tests/probe-verdicts/check.py`
recheck: on-release — re-open the pinned middleware and re-run the live harness when the installed llama.cpp build changes; the receipt is a dated sample, never present service state

# llama.cpp loading-to-ready lifecycle and the MODEL_LOADING verdict

## Claim

A single-model llama-server answers almost every request with HTTP 503 and one
fixed JSON body while its model loads. Before round 16, `tools/kama-probe.sh`
graded that body `FOREIGN_SERVICE` / `non-2xx-non-model-http`, an evidence
string that calls the endpoint a "non-model service". The probe now grades the
exact body `MODEL_LOADING` / `llamacpp-loading` (drift, exit 2). The match is on
body shape only: it does not prove the runtime is llama.cpp, which model is
loading, or that the server will become ready.

Earlier corpus ground: `runtime-health-surface-matrix.md:14` already recorded
the README's `/health` 503 body (round 10). That fact is not new. This entry
adds the code-level path that puts the same body on `/v1/models`, the probe's
mapping, the scope limits, and one live lane-owned run.

## Lifecycle at b11755 (S036, S037)

1. **Listener before model.** Single-model mode starts the HTTP listener, then
   calls `load_model`, and stores `is_ready = true` only after it returns
   (server.cpp:493-515). No `store(false)` appears in the server sources read.
2. **Loading gate.** `middleware_server_state` runs in the pre-routing handler.
   While `is_ready` is false it lets frontend assets through (`/` and embedded UI
   files, server-http.cpp:309-311) and answers every other path, `/health` and
   `/v1/models` included, with status 503 and
   `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
   (server-http.cpp:314-325).
3. **Before the API key.** The pre-routing handler short-circuits `OPTIONS`,
   then runs the state gate, then the API-key check (server-http.cpp:347-359).
   A loading server with `--api-key` therefore answers 503, not 401.
4. **Ready.** `/health` returns `{"status":"ok"}`; `/v1/models` returns 200 with
   one `data[]` entry (id = the first `--alias` in sorted order, else the `-m`
   path; `owned_by` `llamacpp`, server-context.cpp:5168-5225) and an
   Ollama-shaped `models[]` array.
5. **Router mode is different.** The router stores `is_ready = true` right after
   its listener starts, before any model loads (server.cpp:455-460), so the
   router's own `/health` and `/v1/models` never answer with this body; its
   `/v1/models` is a catalog with per-model `status`. Routes the router proxies
   to a per-model child (`/metrics`, `/slots`, inference) can relay a loading
   child's 503 [INFERENCE from server-models.cpp; not run]. The probe only asks
   `/v1/models`, so its verdicts are unaffected.
6. **Sleep is different.** A sleeping server answers `/v1/models` and `/health`
   200 from cache (server-context.cpp:5725-5733); sleeping does not reset
   `is_ready` [INFERENCE from code paths; not run].
7. **Documentation lags code.** The README documents the 503 body only under
   `/health` (README:485-487, key order `code, message, type`) and says `/v1/models`
   `meta` "can be `null` (for example, while the model is still loading)"
   (README:1258). In direct mode the code answers that window with the 503, not
   a 200; the same code order holds at the round-10 pin c0fd7862, so the README
   reading was never observable there either. The server emits keys in
   insertion order `message, type, code` (server-http.cpp:318-320), so matching
   must parse JSON, never compare bytes.

## Probe mapping (repaired `tools/kama-probe.sh`)

| `GET /v1/models` answer | Verdict / reason |
|---|---|
| refused / timeout | `DEAD` connection-refused / timeout |
| 401 / 403 (any body, even the loading body) | `UNAUTHORIZED_SERVICE` http-401 / http-403 |
| 503 + JSON `error` with `message` exactly `Loading model`, `type` exactly `unavailable_error`, integer `code` 503 (extra top-level keys allowed; any `Content-Type`) | **`MODEL_LOADING` llamacpp-loading**, drift, exit 2 |
| 503 with any other body (`no slot available`, `Stream owner model is loading, retry later`, `loading model`, `code` `"503"`/`503.0`/`true`, empty, HTML, text) | `FOREIGN_SERVICE` non-2xx-non-model-http (or html-non-model) — unchanged |
| exact loading body at 200/500/502/504 | unchanged generic verdicts |
| 2xx with model array | `MODEL_OK` / `MODEL_MISMATCH` — unchanged |

The verdict needs python3. Without it the probe keeps the old `FOREIGN_SERVICE`
reading (fail closed: still drift, never a false `MODEL_OK`).

## Scope limits

- **Engine-specific; other engines are leads, not admitted facts.** Build-wave
  source and doc reads (advice under `.ufo/waves/round-16/build/advice/`, no
  SOURCES row, no runtime run; KQ6 does not admit them) suggest: vLLM v0.32.0,
  TGI v3.3.7 and KoboldCpp 1.123.1 (default mode) do not listen until ready, so a
  probe would see `DEAD`; SGLang v0.5.22 answers `/v1/models` 200 while
  `/health` is 503; Ollama v0.40.6 lists available models with 200 whatever the
  load state; LocalAI v4.11.0 binds only after startup preload; LM Studio's docs
  mention no 503 (docs only). `MODEL_LOADING` claims none of these engines.
- **Not-ready is not dead and not foreign.** Kubernetes separates readiness
  (withhold traffic, keep running) from liveness (restart) (S017); llm-d's v0.10
  guide separates process liveness on `/health` from model-aware readiness on
  `/v1/models` for vLLM (S040). `MODEL_LOADING` is the readiness class. S040 is
  vLLM-scoped and does not support the llama.cpp body.
- **Older builds can be false-ready.** Sampled tags (not bisected) suggest that
  between roughly b6000 and b7502 llama.cpp let `/v1/models` through during
  load. A probe there sees a model list and can grade a loading server
  `MODEL_OK` [lead: `RevengerEnvelopeHistory.md`, `ReviewMatcherExactness.md`].
  The verdict is tied to the pinned build; re-open S036 when the build changes.
- **A copied body matches.** Any server or proxy sending the exact body is
  graded `MODEL_LOADING`. That is still drift (exit 2 from `check`/`snapshot`).
- **Overlap with earlier entries.** The router catalog and sleep cache were
  already held in `served-identity-crosswalk.md` (round 11); they are repeated
  here only as limits, not as new ground.

## Live observation — round 16 (lane-owned fixture, not service restoration)

Final receipt `.ufo/waves/round-16/live/receipt.json` (`kama-llamacpp-live/v1`,
tool sha256 `b8c5e8d402595f3b…`, probe sha256 `36b64978ee3a3aa2…`),
2026-10-20T14:06:27.859Z–14:06:27.974Z:

- Binary: `~/.local/opt/llama-b11755/llama-server`, launcher sha256
  `b6a31a8e97615a2a…`, `libllama-server-impl.so` `e404b91a81c9ab65…`, install
  tree of 51 files hashed (`install_tree_sha256` `6c216313a88d71b1…`);
  `/props` `build_info` `b11755-704366d76`.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` before and
  after the run; alias `kama-stories260k`.
- Port 37527 on 127.0.0.1, listener proven owned by the child at the first HTTP
  answer, before captures and before each probe; refusal set {8080, 34113} plus
  every registry port, and a port already listening is refused. Child
  environment: `HOME`, `LANG`, `PATH` only; `--offline`.
- Load window (polling `/v1/models` alone on one keep-alive connection):
  connection refused for the first 6 ms (210 attempts), then 38 answers of HTTP
  503 with `Server: llama.cpp`, `Content-Type: application/json; charset=utf-8`
  and body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
  (sha256 `baa09177…957c`, keys in `message, type, code` order;
  `loading_envelope_exact` true), then `/v1/models` 200 and `/health` 200 at
  11 ms. Server log: model loaded at about 8.4 ms after start.
- The captured body, replayed on a stub with its status and headers
  (`live/replay-captured-503.py`, output `replay-captured-503.txt`), grades
  `MODEL_LOADING` / `llamacpp-loading` exit 2 with the current probe and
  `FOREIGN_SERVICE` / `non-2xx-non-model-http` exit 2 with the frozen one.
- Ready: `/health` 200; `/v1/models` 200 with `data[].id` `kama-stories260k` and
  `owned_by` `llamacpp`; `/metrics` 501 (no `--metrics`); `/slots` 200.
- Probe: `MODEL_OK` matched exit 0 with the alias; `MODEL_MISMATCH`
  served-id-mismatch exit 2 with `kama-not-this-model`.
- Teardown: SIGTERM, return code 0, port refuses afterwards; no `llama-server`
  process and nothing on 8080/34113 afterwards (`live/controls.txt`).

Control: a separate run with the frozen pre-round probe
(`receipt-frozen-probe.json`, port 43229) also passes all 10 checks, so this
capability does not depend on the `MODEL_LOADING` change.

What the receipt does not show: which weights a production deployment serves
(the id is the caller's alias), health of the registered consumers (8080 and
34113 were refused, never touched, and stay `DEAD` in `registry/history/latest.tsv`),
generation, quality, performance, GPU paths, router mode or sleep, and a live
probe verdict during load (the harness records the raw 503 but runs the probe
only after `/health` is 200; the probe verdict on that body comes from the
replay). Known harness limits from the falsify wave: `health_ready` checks the
status only, not the `{"status":"ok"}` body; `teardown_exited` and
`teardown_port_closed` prove reaping and a refused port, not that SIGTERM caused
the exit; `loading_envelope_exact` is recorded, not graded
(`.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md`).
