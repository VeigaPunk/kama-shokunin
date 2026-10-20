# ScoutMiddlewareOrder — b11755 pre-routing order, exemptions, loading-time responses

Read-only seat. No installs; no server started; nothing written outside this file.

## Provenance (all verified this run)

- Primary source: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/server-http.cpp`
  (940 lines), sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`.
- Same file fetched at tag `b11755`: identical sha256 (`diff -q` clean). The tag and the
  commit are the same source.
- Installed binary confirms the pin: `llama-server --version` →
  `version: 0.7.0-dev (build 11755, commit 704366d76)` (`~/.local/bin/llama-server`).
- Supporting files read at the same commit: `tools/server/server.cpp`,
  `tools/server/server-context.cpp`, `tools/server/server-http.h`,
  `tools/server/server-common.h`, `tools/server/README.md`, `common/arg.cpp`,
  `common/common.h`, `common/json.h`, `common/json.cpp`,
  `vendor/cpp-httplib/httplib.h` + `httplib.cpp` (CPPHTTPLIB_VERSION "0.62.0",
  `httplib.h:11`).

## Findings

**F1 — There is one pre-routing handler, and the readiness gate runs before the API-key
check.** Both lambdas are created as locals — key validator at `server-http.cpp:260`,
state gate at `:307` — but they are not registered separately. A single handler is
installed at `:331`:

> `srv->set_pre_routing_handler([&params, middleware_validate_api_key, middleware_server_state](`

and its body dispatches state first, key second (`:354-358`):

> `if (!middleware_server_state(req, res)) {`
> `return httplib::Server::HandlerResponse::Handled;`
> `if (!middleware_validate_api_key(req, res)) {`

So *creation/capture* order is key → state; *execution* order is **state → key**. While
`!is_ready`, the key middleware is never reached.

**F2 — The gate is pre-routing, i.e. it precedes route lookup and mount-point file
serving.** `vendor/cpp-httplib/httplib.cpp:9799-9806`:

> `if (!skip_pre_routing && pre_routing_handler_ && pre_routing_handler_(req, res) == HandlerResponse::Handled) {`
> `...` `if ((req.method == "GET" || req.method == "HEAD") && handle_file_request(req, res)) {`

`routing()` runs the handler before `handle_file_request()` and before any registered
route, so every method/path — including `--path` static files — is gated.

**F3 — `frontend_paths` and `get_public_endpoints` are two different sets.**

`server-http.cpp:242-248`:

> `std::unordered_set<std::string> paths { "/" };`
> `for (const llama_ui_asset & a : llama_ui_get_assets()) { paths.insert("/" + a.name); }`

`server-http.cpp:251-256`:

> `std::unordered_set<std::string> endpoints { "/health", "/v1/health", };`
> `endpoints.insert(frontend_paths.begin(), frontend_paths.end());`

- `frontend_paths` = `{"/"}` ∪ `{"/"+asset}` for every embedded UI asset. The official
  b11755 build embeds **70** assets — symbol
  `_ZNSt5arrayI14llama_ui_assetLm70EED2Ev` in `libllama-server-impl.so`; `strings` shows
  `index.html` (string-pooled into `/index.html`), `favicon.ico`, `manifest.webmanifest`,
  `_app/immutable/bundle.ChI885x-.js`, `_app/immutable/assets/bundle.D9-6832b.css`,
  48 `apple-splash-*` and PWA icons. The set is build-dependent, not a protocol constant.
- `get_public_endpoints` = `frontend_paths` ∪ `{"/health","/v1/health"}` — and nothing
  else. The comment at `:250` ("API routes plus all embedded UI assets") is misleading:
  `/v1/models`, `/models`, `/props`, `/slots`, `/metrics` are **not** public.
- The key validator returns early when no keys are configured (`:262-264`) and on a
  public/UI path (`:267-269`); otherwise it accepts `Authorization` or `X-Api-Key`,
  strips `"Bearer "`, and on failure sets `res.status = 401` with
  `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`
  (`:272-304`). `--api-key` is CSV, empty entries dropped (`common/arg.cpp:3533-3542`),
  so `--api-key ""` leaves auth off.

**F4 — Exemptions do not compose.** The readiness gate's only exemption is
`frontend_paths` (`:309-311`), *not* `get_public_endpoints`:

> `if (frontend_paths.count(req.path)) { return true; // frontend asset, allow it to load`

`/health` is exempt from the key check but **not** from the readiness gate. The gate then
answers every other path, including `/health`, `/v1/health` and `/v1/models` (`:308-325`):

> `if (!is_ready.load()) {` … `res.status = 503;` …
> `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`

**F5 — OPTIONS bypasses both middlewares, on any path, in any state**, at `:347-352`:

> `if (req.method == "OPTIONS") {` … `return httplib::Server::HandlerResponse::Handled;`

**F6 — The loading window is real and is the only one.** `is_ready` starts false
(`server-http.h:71`, `std::atomic<bool> is_ready = false;`). In single-model mode the
listener is started *before* the model is loaded (`server.cpp:493`):

> `// start the HTTP server before loading the model to be able to serve /health requests`

then `ctx_server.load_model(params)` (`:507`), and only afterwards
`ctx_http.is_ready.store(true);` (`:515`). Note the comment means *answerable*, not
*200*: during that window `/health` is answered with 503. There are exactly two stores of
`is_ready` in the whole server tree (`server.cpp:460`, `:515`), both `true` — the latch is
one-way for the life of the process, so sleep/unload never re-enters the loading state.

**F7 — `/health`'s 200 is unconditional; the 503 is purely middleware.**
`server-context.cpp:5288-5298`:

> `// error and loading states are handled by middleware`
> `res->ok({{"status", "ok"}});`

**F8 — The docs state the same contract.** `README.md:479-487`:

> `This endpoint is public (no API key check).` `/v1/health` also works.
> Body: `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`
> `Explanation: the model is still being loaded.`

## Direct answer: GET /v1/models and GET /health while loading, `--api-key` set

Routes are registered once and shared by both modes: `/health` and `/v1/health` →
`routes.get_health` (“public endpoint (no API key check)”), `/v1/models` → `routes.get_models`
(`server.cpp:278-284`). Because F1/F4 run first:

| State | `GET /v1/models` | `GET /health` |
|---|---|---|
| loading, `--api-key` set, no/wrong/correct key | **503** `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` | **503**, same body |
| ready, `--api-key` set, no/wrong key | 401 `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}` | 200 `{"status":"ok"}` |
| ready, `--api-key` set, valid key | 200 model list | 200 `{"status":"ok"}` |
| ready, no `--api-key` | 200 model list | 200 `{"status":"ok"}` |

A 401 is **impossible** while loading, and a 503 is not evidence of missing credentials.
The 503 also covers arbitrary unknown paths (`/v1/nope`, `/slots`, `/metrics`), since the
gate runs before routing.

Body bytes: `common_json` is `nlohmann::ordered_json` (`common/json.cpp:14`) and
“object keys keep the order in which they are added” (`common/json.h:24`), so the wire
body is exactly
`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` — no
trailing newline, `Content-Type: application/json; charset=utf-8`, `res.status = 503`.
`code` is the integer 503. (README prints the same fields in a different order; JSON
order is not semantic — the server emits message, type, code.)

## Bearing on C1 (calibration) and the stub matrix

- **C1 is confirmed at source level.** A loading b11755 direct server answers
  `GET /v1/models` with the exact documented loading envelope, not merely “some non-2xx”.
  `FOREIGN_SERVICE` / `non-2xx-non-model-http` for that shape is an overreach; the new
  `MODEL_LOADING` / `llamacpp-loading` verdict is correct.
- **The envelope is a runtime fingerprint, not a route check.** It is emitted for every
  non-frontend path pre-routing, so it proves “a llama.cpp-family process in loading state
  answered”, not “this path exists”. Exact three-field matching is therefore the right
  gate; `Overbroad503.*` controls (no-slot, lowercase, code-as-string, no `error` wrapper,
  plaintext) all still fall to `FOREIGN_SERVICE`.
- **Realistic pairing:** on b11755 the loading envelope on `/v1/models` implies `/health`
  is 503 at the same instant. `LoadingRace.HealthAlreadyOk` (models 503 + health 200) is
  reachable only as a race — `is_ready` may flip between the probe's two fetches, and the
  flip is one-way false→true. `LoadingRace.InverseHealthLoadingModelsOk` (models 200 +
  health 503) is **unreachable** on b11755 given the one-way latch; keep it if you want a
  “health is not in the decision” control, but it must not be cited as observed llama.cpp
  behavior.
- **Auth interplay:** with `--api-key`, auth failures are always 401 and the gate wins
  first while loading, so a probe can never mistake a key problem for loading, nor vice
  versa. `AuthAndDead.401-carrying-loading-envelope` matches this precedence. (The stub
  body says “Invalid API key”; the server emits “Invalid API Key” — cosmetic only, the
  verdict keys on status.)
- **Scope: single-model mode only.** Router mode (no `-m`/HF/docker model,
  `server.cpp:152-154`) sets `is_ready` true immediately after `start()` (`:460`), before
  any startup model load, and swaps in `models_routes->get_router_models` (`:269`).
  `server-models.cpp` contains no `"Loading model"` / 503 emission, and README `:1258`
  says `meta` “can be `null` (for example, while the model is still loading)” for
  `/v1/models`. So a router-mode server answers 200-with-null-meta, never the loading
  envelope. [INFERENCE for the exact router payload; grounded in README:1258 + absent
  envelope producer.]
- **`--api-prefix` caveat (not exercised in the matrix):** `get_public_endpoints` is
  compared against the raw `req.path` (`:267`) while routes are registered at
  `path_prefix + path` (`:690`). With a non-empty `--api-prefix`, `/x/health` is not in
  the public set, so `/health` would require the key. Default is empty
  (`common/common.h:650`, `api_prefix = ""`), so this does not affect the lane today.
  [INFERENCE for the prefixed behavior; the comparison is literal.]

## Limitations

- Source + binary-symbol evidence only; no live server was started (measurements are L1's).
  The one-way latch and byte ordering are read from code, not observed on the wire.
- The 70-asset count comes from the mangled `std::array<…,70>` symbol; the exact 70 names
  were not enumerated (asset names are build-dependent and partially string-pooled).
- Router-mode `/v1/models` payload shape is inferred from README + code structure, not
  measured; `server-models.cpp` was checked for the loading envelope only.

Report: `.ufo/waves/round-16/build/advice/ScoutMiddlewareOrder.md`
