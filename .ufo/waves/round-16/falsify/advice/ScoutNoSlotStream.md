VERDICT: confirm — the two cited `unavailable_error` producers in llama.cpp b11755 (`server-context.cpp:5396` "no slot available"; `server-models.cpp:2585` "Stream owner model is loading, retry later") exist verbatim at the cited lines and both map to `unavailable_error` / HTTP 503.

# Attack

Re-open llama.cpp @ `704366d76` `tools/server/server-context.cpp` (no slot available) and
`tools/server/server-models.cpp` (Stream owner model is loading); confirm the quoted messages,
the line numbers, and that both map to `unavailable_error`/503.

# What ran, with exit codes

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `git ls-remote --tags https://github.com/ggml-org/llama.cpp \| grep b11755` | 0 | `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad  refs/tags/b11755` |
| 2 | `curl -fsSL .../704366d76.../tools/server/server-context.cpp -o ...` | 0 | 264205 bytes, sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` |
| 3 | `curl -fsSL .../704366d76.../tools/server/server-models.cpp -o ...` | 0 | 117111 bytes, sha256 `9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a` |
| 4 | same two files via `cdn.jsdelivr.net/gh/ggml-org/llama.cpp@704366d76...` | 0 | byte-identical sha256 to #2/#3 (independent mirror) |
| 5 | `grep -n "no slot available" server-context.cpp` | 0 | `5396` |
| 6 | `grep -n -E "Loading model" server-context.cpp server-models.cpp` | **1** | **absent from both files** |
| 7 | `grep -n "Stream owner" server-models.cpp` | 0 | `2585` |
| 8 | `grep -n "ERROR_TYPE_UNAVAILABLE"` across both files + pinned tree | 0 | exactly the two call sites below + the enum/switch |
| 9 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/.../current.json` | 0 | `tests=72 passes=72 failures=0` |
| 10 | `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json > /tmp/.../frozen.json` | 1 | `tests=72 passes=55 failures=17` |

# Observed facts

**Producer 1 — `tools/server/server-context.cpp:5396`** (1-based; read via `splitlines()[5395]`):

```cpp
res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));
```

- Contained in the lambda assigned at `server-context.cpp:5363` (`this->get_slots`), inside
  `server_routes::init_routes()` (`server-context.cpp:5284`); the next route starts at 5405.
- Guarded by `if (!req.get_param("fail_on_no_slot").empty())` and `if (res_task->n_idle_slots == 0)`
  (5393-5395) — i.e. only `GET /slots?fail_on_no_slot=…` with zero idle slots.
- Route binding: `server.cpp:318` `ctx_http.get("/slots", ex_wrapper(routes.get_slots))`.
  In router mode `server.cpp:264` overrides `routes.get_slots = models_routes->proxy_get`, so this
  producer is single-model only.

**Producer 2 — `tools/server/server-models.cpp:2585`**:

```cpp
res_err(res, format_error_response("Stream owner model is loading, retry later", ERROR_TYPE_UNAVAILABLE));
```

- Inside `router_stream_get` (starting 2565): after `resolve_child_for_conv` returns no owner
  (2573) and the tracked meta status is `LOADING`/`DOWNLOADING`/`DOWNLOADED` (2575-2584).
- Route binding: `server.cpp:326-335` — `GET /v1/stream` binds `models_routes->router_stream_get`
  only under `is_router_server`; the else branch binds `server_stream_make_get_handler()`. So this
  producer is router mode only.

**Mapping to `unavailable_error` / 503** (shared, not per-site):

- `server-common.cpp:119-121`: `case ERROR_TYPE_UNAVAILABLE: type_str = "unavailable_error"; code = 503;`
  and the returned object is `{"code": code, "message": message, "type": type_str}` (128-132).
- `server-context.cpp:4872-4875`: `void error(const json & error_data) { status = json_value(error_data, "code", 500); data = safe_json_to_str({{"error", error_data}}); }`
- `server-models.cpp:2158-2161`: `res_err` does the same — `res->status = json_value(error_data, "code", 500);`
  then `{{"error", error_data}}`.
- Result for both sites: HTTP 503, body
  `{"error":{"code":503,"message":<quoted>,"type":"unavailable_error"}}`.

**The separating nuance (the actual falsifiable edge):** `"Loading model"` does not occur in either
attacked file (command 6, exit 1). The MODEL_LOADING envelope is a hardcoded literal in
`server-http.cpp:314-325` — `{"message","Loading model"}` at 318, `{"type","unavailable_error"}` at
319, `{"code",503}` at 320 — inside `middleware_server_state` (307), gated on `!is_ready.load()` (308),
with the frontend exemption at 309-311 and the state gate (354) running before the API-key check
(357). So the two attacked messages share only type+code with the loading body; they are not it.
This is exactly the distinction the landed corpus states
(`corpus/knowledge/llamacpp-loading-lifecycle.md:59`, `corpus/knowledge/endpoint-identity.md:205-206`,
`corpus/lessons/round-16.md:44`), and it is correct.

**Probe behaviour on the real strings** (both matrices): four stub rows carry these exact source
literals at status 503 with `type` `unavailable_error` and integer `code` 503 —
`ForeignControls.busy-unavailable-error`, `LoadingRace.HealthOkNonLoading503`,
`Overbroad503.no-slot-available` (message `no slot available`) and
`NearMissTriple.router-stream-owner-loading` (message `Stream owner model is loading, retry later`).
All four grade `FOREIGN_SERVICE` / `non-2xx-non-model-http` with `probe_exit 2` under **both** the
current and the frozen pre-round probe. Current matrix reproduced 72/72, 9 families, 17
`MODEL_LOADING`; frozen reproduced 55 pass / 17 fail — matching the L1 headline numbers.

# Limitations / residual gaps

- **Neither attacked file is pinned by the lane.** `.ufo/waves/round-16/sources/llama.cpp-704366d/`
  contains `README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`, `server.cpp`;
  `pins.json` records only the first four. The `5396` / `2585` citations therefore rest on my fresh
  content-addressed fetches (full 40-char commit in the raw URL, cross-checked against an independent
  jsDelivr mirror), not on a lane receipt. Recommendation (no edit made): pin both files with
  digests, and add `server.cpp` to `pins.json` — its pinned bytes match the S037 digest
  `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` exactly, but it is absent
  from the manifest while `pins.json`'s four entries all match their files. Bookkeeping drift only;
  no factual correction to the corpus is warranted.
- GitHub Contents API returned HTTP 403 (unauthenticated rate limit), so I could not cross-check
  blob SHA-1s via the tree API; commit identity rests on the full-sha URL + mirror + the matching
  `server.cpp`/S036 digests.
- I did not run `llama-server` (this item does not call for it) and did not run `measure.py`.
- No lane, fleet, manifest, `.ufo/state`, or sibling repo file was modified; only this Report and
  `/tmp/kama-r16-ScoutNoSlotStream/` were written, and the scratch was removed.

# Installs

None.
