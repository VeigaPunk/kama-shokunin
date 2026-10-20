# C1 scope: `ERROR_TYPE_UNAVAILABLE` and literal `503` in llama.cpp `tools/server` @ `704366d76` (b11755)

Read-only scout. Source pinned to commit `704366d76`: all 29 `*.cpp`/`*.h` files under
`tools/server` were fetched from `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/<name>`
(plus `tools/server/README.md` for doc corroboration). Fetched content digests include
`server-http.cpp` sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`,
`server-common.cpp` `b4f4aae7…d442`, `server-models.cpp` `9c5a6f2c…8b4a`.

Method: exhaustive literal search (`ERROR_TYPE_UNAVAILABLE`, `unavailable`, `503`, `Loading model`)
over the fetched tree; no LSP server exists for this remote snapshot (no checkout / compile DB), so
grep is the literal fallback, not semantic proof. Line numbers are at this commit.

## Totals

- `ERROR_TYPE_UNAVAILABLE`: **4 textual occurrences in 4 files** — 1 enum declaration, 1 central
  type→code mapping, **2 response producers**.
- Literal `503`: **3 tokens in 2 files** — `server-common.cpp:121`, `server-http.cpp:314`,
  `server-http.cpp:320`. Only **one logical response** builds a 503 from a literal: the
  not-ready middleware; the other literal is the shared `ERROR_TYPE_UNAVAILABLE` mapping.
- The exact body value `"Loading model"` (capital L) appears **exactly once** in the whole server
  tree: `server-http.cpp:318`. (Lowercase `"loading model …"` strings exist only in log lines,
  e.g. `server-context.cpp:1152`, `server-models.cpp:1228`; they are never response bodies.)

## Every `ERROR_TYPE_UNAVAILABLE` occurrence

| Site | Role | Endpoint / condition | Message | HTTP status |
|---|---|---|---|---|
| `tools/server/server-common.h:65` | enum member | `ERROR_TYPE_UNAVAILABLE, // custom error` | — | — |
| `tools/server/server-common.cpp:119-121` | type→code mapping in `format_error_response` | any caller of the enum | caller-supplied | `type_str = "unavailable_error"`, `code = 503` |
| `tools/server/server-context.cpp:5396` | producer | `GET /slots` with `?fail_on_no_slot=` non-empty and `n_idle_slots == 0` | `"no slot available"` | 503 via `res->error` |
| `tools/server/server-models.cpp:2585` | producer (router mode only) | `GET /v1/stream?conv_id=` whose owning model is `LOADING`/`DOWNLOADING`/`DOWNLOADED` | `"Stream owner model is loading, retry later"` | 503 via `res_err` |

Mapping quote (`server-common.cpp:119-121`):

```cpp
case ERROR_TYPE_UNAVAILABLE:
    type_str = "unavailable_error";
    code = 503;
```

Contexts:

- `/slots` — `server-context.cpp:5394` `if (!req.get_param("fail_on_no_slot").empty()) {` then
  `:5395` `if (res_task->n_idle_slots == 0) {`. The handler is gated by
  `:5365` `if (!params.endpoint_slots) {` (default `true`: `common/common.h:686`
  `bool endpoint_slots   = true;`). Router mode rebinds `get_slots` to the proxy:
  `server.cpp:264` `routes.get_slots = models_routes->proxy_get;` — so in router mode this body
  comes from the child, surfaced verbatim (see proxy note below).
- `/v1/stream` — `server-models.cpp:2581-2583`:
  `meta->status == SERVER_MODEL_STATUS_LOADING || … DOWNLOADING || … DOWNLOADED`.
  This handler is bound only in router mode (`server.cpp:326-327`
  `stream_get_h = models_routes->router_stream_get;`).

Status derivation: both producers put the status inside the JSON, and the helpers take the HTTP
status from it — `server-context.cpp:4873` `status = json_value(error_data, "code", 500);`,
`server-models.cpp:2159` identical. Consequently **any future `ERROR_TYPE_UNAVAILABLE` use
automatically becomes 503 with its own message**; the message is the only discriminator between
them.

## Every literal `503`

| Site | Expression | Condition |
|---|---|---|
| `tools/server/server-common.cpp:121` | `code = 503;` | `ERROR_TYPE_UNAVAILABLE` case of `format_error_response` |
| `tools/server/server-http.cpp:314` | `res.status = 503;` | `middleware_server_state`, `if (!is_ready.load()) {` (`:308`) |
| `tools/server/server-http.cpp:320` | `{"code", 503}` | same middleware, body field |

The middleware body (`server-http.cpp:314-324`) is:

```cpp
res.status = 503;
res.set_content(
    safe_json_to_str(json {
        {"error", {
            {"message", "Loading model"},
            {"type", "unavailable_error"},
            {"code", 503}
        }}
    }),
    "application/json; charset=utf-8"
);
```

Serialization is `data.dump_safe()` (`server-common.cpp:1695-1696`), i.e. nlohmann's key-ordered
dump; the documented bytes in README line 486 are
`{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`.

## Conditions on the loading 503 (the C1 positive)

- Gate: `server-http.h:71` `std::atomic<bool> is_ready = false;`; checked per request at
  `server-http.cpp:308` `if (!is_ready.load()) {`.
- Scope: **every path except `"/"` and embedded UI assets** —
  `server-http.cpp:242-248`: `std::unordered_set<std::string> paths { "/" };` plus
  `llama_ui_get_assets()` names; `:309` `if (frontend_paths.count(req.path)) {` returns early
  (`// frontend asset, allow it to load and show "loading"`). `/health`, `/v1/health`,
  `/v1/models`, `/props`, `/metrics`, `/slots`, all completions paths, and unknown paths are
  **not** in `frontend_paths`, so all receive the same 503 body.
- `/health` is explicitly delegated to this middleware: `server-context.cpp:5289`
  `// error and loading states are handled by middleware`, and it returns
  `:5297` `res->ok({{"status", "ok"}});` only after readiness. README confirms the wire body:
  `README.md:485-487` "HTTP status code 503 / Body: … "Loading model" … / the model is still being loaded."
- Ordering: state is checked **before** API-key validation —
  `server-http.cpp:354` `if (!middleware_server_state(req, res)) {` precedes `:357`
  `if (!middleware_validate_api_key(req, res)) {` — so a loading server answers 503 even when
  `--api-key` is configured (not 401). `OPTIONS` is short-circuited earlier (`:347-352`) with a
  blank 200.
- Window (single-model mode): HTTP listener starts before the model
  (`server.cpp:493` "start the HTTP server before loading the model…"), `load_model` at `:507`,
  then `:515` `ctx_http.is_ready.store(true);`. If loading fails the process exits (`:507-511`).
  So the 503 window is "listening but model not yet loaded".
- Router mode sets `is_ready` immediately after `start()`: `server.cpp:460`
  `ctx_http.is_ready.store(true);`, before `load_startup_models()` at `:472`; the router therefore
  does **not** emit this body itself. Child instances are spawned as full servers with their own
  port — `server-models.cpp:480` `preset.set_option(ctx_preset, "LLAMA_ARG_PORT", …)`, `:1414`
  "spawning server instance … on port %d" — so [INFERENCE] each child has the same middleware
  and emits this body on its own port while loading.
- The body is emitted for every method and path before routing, so it also replaces what would
  otherwise be 404/401 during the load window; it is not `/v1/models`-specific.

## Consequences for the C1 exact-message matcher

1. **Positive signature (all exact):** HTTP **503**, JSON object with a single top-level key
   `error` whose value is an object with `message == "Loading model"`,
   `type == "unavailable_error"`, `code` integer **503**. No other 503 in `tools/server` reuses
   this message, so this triple is sufficient and (per source) unambiguous.
2. **503 `unavailable_error` bodies that must keep their current verdict:**
   - `"no slot available"` (`server-context.cpp:5396`) — same status and type, different message.
     Reachable while fully ready, so a message-only status/type matcher would misfire.
   - `"Stream owner model is loading, retry later"` (`server-models.cpp:2585`) — same status and
     type, *contains the word “loading”*, router-only `/v1/stream`. This is the strongest
     near-miss control for a substring/regex matcher; it requires phrase equality, not contains.
3. **Non-503 near-misses already in the existing taxonomy:** `/metrics` without `--metrics`
   returns `ERROR_TYPE_NOT_SUPPORTED` → 501 `not_supported_error`
   (`server-context.cpp:5304`; `common/common.h:688` `endpoint_metrics = false`); the generic
   exception handler returns **500 text/plain** (`server-http.cpp:194`), and the error handler
   rewrites only 404 (`:199-210`). Neither is 503 and neither should change verdict.
4. **Router `/v1/models` never proxies:** `server.cpp:269`
   `routes.get_models = models_routes->get_router_models;` and that handler is a local 200 list
   (`server-models.cpp:2448-2451` `res_ok(res, {{"data", models_json}, {"object", "list"}});`).
   So on a router, `GET /v1/models` returning 200 does not prove a child is ready; conversely the
   loading 503 on `/v1/models` can only come from a single-model/child listener's middleware.
5. **Proxy pass-through caveat (not `/v1/models`):** router binds `/metrics`, `/slots` and the
   POST generation routes to the proxy (`server.cpp:242`, `:262-265`). The proxy copies upstream
   status and body verbatim — `server-models.cpp:2857` `msg.status = response.status;`,
   `:2884` forwards raw body chunks, `:2974` `this->status = header.status;`. Therefore a router
   endpoint that proxies to a still-loading child *can* surface the exact loading body; a matcher
   keyed only on the body cannot tell router-passthrough from child middleware. This does not
   affect the assigned `GET /v1/models` probe.
6. **No other producer:** there is no other literal 503, no other `"Loading model"`, and no other
   `ERROR_TYPE_UNAVAILABLE` call site in `tools/server/*.cpp|*.h`. Anything returning 503 with a
   different body is either one of the two messages above, an upstream service proxied through,
   or a non-llama.cpp service.

## Explicit non-uses (do not classify)

- `server-mcp.cpp:741` `return {{"error", "MCP server unavailable: " + server_name}};` — a field
  inside an MCP tool result, no HTTP status, no 503.
- `server-connect.cpp:167` `std::string server_connect::unavailable_reason(const common_params & params) {`
  — startup CLI validation for `--connect`, returns a string printed before exit, never an HTTP body.
- Log/comments containing "unavailable": `server-context.cpp:2859-2860`, `:3001-3002`,
  `:3063-3064`, `:3132-3133` (deferred-task debug lines) and `server-models.cpp:2577-2578`
  ("model is still loading") — internal logging/comments, not responses.

## Facts vs inference

- Observed: all sites, line numbers, quotes, counts, conditions, ordering, status derivation and
  proxy verbatim forwarding above, from fetched source at `704366d76`.
- [INFERENCE] Child instances (spawned with `LLAMA_ARG_PORT`) reuse the same middleware and hence
  emit the identical body on their own ports while loading — inferred from the spawn argument and
  the shared `llama_server` entry path; not measured at runtime.
- [INFERENCE] nlohmann key ordering makes the middleware body byte-identical to README line 486;
  a field-level JSON match is the robust choice regardless.

## Limitations

- Read-only seat: no server was launched, no probe run, no stub matrix executed; all claims are
  static source analysis.
- Scope is exactly `tools/server/*.cpp` and `*.h` at one commit; `tools/server/tests/*.py`,
  `common/`, `src/`, vendored `httplib`, and the embedded UI assets were not exhaustively scanned.
- 503s injected by an intermediate proxy or by httplib itself are outside this scan.
