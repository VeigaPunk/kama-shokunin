source: upstream llama.cpp commit 704366d76 (release b11755) — tools/server/server-http.cpp (sha256 24ede172e5267635…, 940 lines), tools/server/server.cpp (sha256 21439622…, 591 lines), tools/server/server-http.h (sha256 fafbdb8d…), tools/server/server-context.cpp (sha256 dd1de0f2…, 6320 lines), tools/server/server-common.cpp (sha256 b4f4aae7…, 2147 lines), tools/server/README.md (sha256 714c067b…, 2402 lines), each fetched read-only from https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/<file>; lane artifacts (not upstream): `tools/kama-probe.sh` classify() lines 415-525, `tools/kama-llamacpp-live.py` (C2, not yet present in the lane tree when this draft was written), `tests/probe-verdicts/*.json` (C1 stub matrix, not yet present)
verified-at: 2026-10-20 — all upstream files opened read-only at the commit above; the installed binary at ~/.local/opt/llama-b11755 was inspected only with `strings` (it contains the build string 704366d76 seven times); no server was started, no probe was run and no lane gate was executed by this draft's author
recheck: 90d — README.md §"GET /health" (lines 479-490) and §"Sleeping on Idle" (lines 2333-2345); on-change — server-http.cpp middleware_server_state (lines 307-328), server.cpp is_ready.store sites (lines 460, 515), server-context.cpp get_health (5288-5299) and fail_on_no_slot (5394-5397), and the probe's classify() branch that emits `non-2xx-non-model-http`

# llama.cpp loading-to-ready lifecycle and the MODEL_LOADING verdict scope

## Claim

A llama.cpp server that is still loading its model answers almost every request with
HTTP 503 and a fixed JSON envelope whose message is `Loading model`. That body is
documented (README) and produced by one middleware that runs before routing. A probe
that reads this body as a generic non-model HTTP response (today's `FOREIGN_SERVICE /
non-2xx-non-model-http`) is over-reaching. The narrow, evidence-backed reading is a
distinct `MODEL_LOADING / llamacpp-loading` verdict, chosen only for the exact envelope
on `GET /v1/models`. Everything else about the verdict is scope-limited below.

Nothing in this entry is a live measurement. The live section at the end is a field list
for L1 to fill from the C2 receipt.

## Documented lifecycle at b11755

1. **Listener up, model not loaded.** `is_ready` is declared as
   `std::atomic<bool> is_ready = false;` (server-http.h:71). It is the single gate read
   by the state middleware.
2. **Single-model mode (a model path, hf repo or docker repo was given).** The listener
   starts, then `ctx_server.load_model(params)` runs, and only after it returns true does
   `ctx_http.is_ready.store(true);` execute (server.cpp:507-515, inside the `else` of
   `if (is_router_server)` opened at server.cpp:440 and closed at 481).
3. **Router mode (no model given).** The router logs "starting server in router mode.
   models will be automatically loaded on-demand" (server.cpp:441). `ctx_http.is_ready.store(true);`
   runs at server.cpp:460, inside the `if (is_router_server)` branch, right after
   `ctx_http.start()` succeeds and before any model is loaded. The router process therefore
   never reaches the loading gate at all; child-instance readiness is a separate question
   (see scope limits).
4. **Middleware (every request, before routing).** `middleware_server_state` is installed
   as a pre-routing handler (server-http.cpp:331-361). When `!is_ready.load()`:
   - frontend paths (`/` and embedded UI asset names) are allowed through
     (server-http.cpp:309-311: "frontend asset, allow it to load and show 'loading'");
   - every other path gets `res.status = 503;` and the body
     `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
     (server-http.cpp:314-325; the message and type strings are at lines 318-319).
   The handler returns `false` and the request is handled. Ordering inside the
   pre-routing handler is: OPTIONS short-circuit (lines 347-353), then
   `middleware_server_state` (354-356), then `middleware_validate_api_key` (357-359). So
   a loading server answers 503 to an unauthenticated request even when `--api-key` is set.
5. **Ready.** Once `is_ready` is true, the middleware no longer intervenes. In the five
   fetched `tools/server` sources `is_ready` is written only with `store(true)`
   (server.cpp:460 and 515; no `store(false)` appears in those files), so a loaded
   single-model server does not drop back into the loading state. `GET /health` then
   returns `{"status":"ok"}` (server-context.cpp:5288-5299; comment at 5289: "error and
   loading states are handled by middleware").
6. **Documented body.** README.md:485-490 documents the same 503 body for `GET /health`
   ("HTTP status code 503 ... Body: {"error": {"code": 503, "message": "Loading model",
   "type": "unavailable_error"}} ... Explanation: the model is still being loaded.") and the
   200 body `{"status": "ok" }` once "the server is ready". The README body key order
   differs from the source; JSON object equality is what matters.
7. **Sleep is not loading.** README.md:2337 says a sleeping model is unloaded and "Any
   new incoming task will automatically trigger the model to reload." README.md:2341
   lists `GET /health`, `GET /props`, `GET /models` and `GET /metrics` as exempt from
   waking the model. In code, `get_models` returns `cached_models` while
   `queue_tasks.is_sleeping()` (server-context.cpp:5725-5730, comment at 5727: "this
   endpoint must be accessible during sleep"). Nothing in the five fetched sources sets
   `is_ready` back to false on sleep, so sleep does not reproduce the `Loading model` body
   by this path. [INFERENCE from code paths; not observed live.]

## Probe verdict mapping (current probe vs. C1 target)

Lines are from `tools/kama-probe.sh` classify() unless noted. The probe fetches with a
plain `curl` GET (fetch(), line 290-293). Only `GET /v1/models` decides the verdict.

| Observed on GET /v1/models | Current verdict / reason (kama-probe.sh) | Target after C1 |
|---|---|---|
| connect refused / timeout (rc 7; rc 28) | DEAD connection-refused / timeout (425-435) | unchanged |
| empty reply, reset, no HTTP (rc 52, 56, 1/2/92, other) | NOT_HTTP empty-reply / connection-reset / no-http-response (436-455) | unchanged |
| 401 / 403 | UNAUTHORIZED_SERVICE http-401 / http-403 (459-460) | unchanged; a loading server returns 503 before the key check, so this only appears once ready |
| 503, JSON `error` object with exact message "Loading model", type "unavailable_error", integer code 503 | FOREIGN_SERVICE non-2xx-non-model-http (513-522) — the overreach | **MODEL_LOADING llamacpp-loading, drift true, exit 2** |
| 2xx with model array, id matches or no expected id | MODEL_OK matched / expected-wildcard (479-498) | unchanged |
| 2xx with model array, id mismatch | MODEL_MISMATCH served-id-mismatch / unresolvable-id (495-496) | unchanged |
| 2xx HTML or other 2xx without model array | FOREIGN_SERVICE html-non-model / non-model-2xx / schema-unrecognized (506-519) | unchanged |
| other non-2xx, any other body | FOREIGN_SERVICE non-2xx-non-model-http (521-522) | unchanged |

The trigger for MODEL_LOADING is the response to `/v1/models` alone. `/health` returns the
same 503 body during loading (README.md:485-486), but the probe's `/health` call is
evidence-only (it is run only after a 2xx model array has been seen, lines 500-501).

## Exact-envelope scope limits (what MODEL_LOADING must not claim)

- **"no slot available" is not "Loading model".** The only other 503 `unavailable_error`
  in the fetched tree is the `/slots?fail_on_no_slot=1` path:
  `res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));`
  (server-context.cpp:5394-5397), which maps to code 503 and type `unavailable_error`
  (server-common.cpp:119-121). Its message differs, so the exact-envelope rule keeps it
  FOREIGN_SERVICE, as the contract states. This path is `/slots`, not `/v1/models`, so
  it cannot reach the MODEL_LOADING branch at all.
- **Sleeping** is not a 503 path (see lifecycle point 7). A sleeping server is expected to
  answer `/v1/models` from cache. What the probe then reports is MODEL_OK if the cached
  body carries a model array. [INFERENCE; not run.]
- **Router mode.** The router's own `/v1/models` is not gated by the loading middleware
  after its listener starts (server.cpp:460). Whether a child instance's loading 503 is
  relayed unchanged through the router's proxy handlers was **not verified** here
  (server-models.cpp was not opened). Treat router-mode behaviour as unknown until read.
- **Other engines and proxies.** This body is llama.cpp-specific as far as the fetched
  sources show. The Ollama entry (`ollama-evidence-replay.md`) documents only the
  `/api/tags` and `/api/ps` bodies; Ollama error envelopes were **not checked** here, and
  whether Ollama or any gateway emits a 503 with this exact message is unknown. A reverse
  proxy that copies the message string would also match the exact-envelope test; the rule
  cannot tell an upstream llama.cpp from a copy. That is a known limit, not something the
  verdict proves.
- **Frontend paths.** `/` and embedded UI assets are exempt during loading
  (server-http.cpp:309-311). The probe does not classify on `/`; its body sniff of `/`
  appears only in evidence text. Do not infer MODEL_LOADING from `/`.
- **OPTIONS** requests are answered before the state gate (server-http.cpp:347-353). The
  probe sends GET only, so this does not change the verdict; it is noted so no one
  "fixes" the probe to use OPTIONS.
- **Body exactness.** The match must be on decoded JSON fields (message, type, integer
  code), not on a substring. A 503 body that is not JSON, has extra top-level keys, or has
  `code` as a string stays FOREIGN_SERVICE under the contract. [INFERENCE: the contract's
  wording; the C1 matrix is what enforces it.]

## Unknown (not verified in this draft)

- Declared default and every `is_ready` write were checked only in the five fetched
  files (server-http.cpp, server.cpp, server-http.h, server-context.cpp, server-common.cpp)
  at 704366d76; no other translation unit was searched.
- Whether the shipped binary's bytes contain the same `Loading model` string: only the
  commit string `704366d76` was checked with `strings`. This is build provenance, not a
  byte-level match of the middleware.
- Router proxy relay of child 503 bodies (server-models.cpp not read).
- Ollama and third-party gateway error envelopes (not read).
- Exact timing of the 503 → 200 transition on the lane's tiny model (stories260K): that
  is a live fact for the receipt, not for this entry.

## Live observation (L1 fills from the C2 receipt; no values in this draft)

Titled section for L1. Fill each row from the receipt verbatim; do not infer any value
from this draft. Record `unrecorded` when the receipt lacks a field.

- Binary: resolved path, `llama-server --version` output (build string and commit), and
  sha256 of the binary at `~/.local/opt/llama-b11755/llama-server`.
- Model: path, sha256 of `~/.cache/kama-shokunin/models/stories260K.gguf`, and the alias
  passed with `--alias`.
- Port: the loopback port chosen, the selection method, and the attestation that it is not
  a registered consumer port.
- Load window: each `GET /v1/models` status line and body captured during load, with
  timestamps; the same for `GET /health`, and for `GET /` (frontend).
- Ready window: `GET /health` status and body; `GET /v1/models` status, `owned_by`,
  presence of `data[0].id` and its value, presence of the Ollama-shaped `models[]` array;
  `GET /slots` status; `GET /metrics` status and whether `--metrics` was passed.
- Probe run: the frozen probe result (verdict, reason, exit code) during load, and the
  repaired probe result (verdict, reason, exit code) during load and after ready. Record
  both; do not merge them.
- Teardown: process exit status, the post-teardown port check, and the statement that no
  `~/.config`, `~/.omp` or systemd path was written (from the receipt's own write log).
- Any fields the receipt does not carry are written as `unrecorded`, never estimated.
