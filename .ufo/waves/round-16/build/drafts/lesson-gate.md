## Gate

Draft by ScribeLessonGate, 2026-10-20, for integration into `corpus/lessons/round-16.md`. Every source below was opened this session; access date 2026-10-20 for all. Nothing here runs the lane probe, a lane gate, or any serving process; the live smoke observation is L1's and is cited only as L1's observation.

| Candidate | Decision | Grounding / limitation |
|---|---|---|
| Admit the exact `MODEL_LOADING` / `llamacpp-loading` rule: `GET /v1/models` returns 503 AND the body is a JSON object whose `error` has `message` == "Loading model", `type` == "unavailable_error", and integer `code` == 503; drift true | admit, scoped to llama.cpp b11755 | The literal 503 body is produced at one site in the b11755 source (S-LC1 lines 307-325). README (S-LC2 lines 479-490) documents the same body for `/health`. Limitation: pinned to b11755; no statement here about other llama.cpp builds. The rule checks body shape, not provenance, so any server emitting this exact body matches. |
| Reject widening to any 503 or any `unavailable_error` | reject | Same `unavailable_error`/503 pair is produced for a different state: `?fail_on_no_slot=1` with no idle slot emits message "no slot available" (S-LC3, S-LC4 lines 5394-5396; README line 987). Keeping the message check exact is what leaves that body `FOREIGN_SERVICE` (scope limit as stated in the contract). |
| Reject "a live toy run proves registered consumers are healthy" | reject | The toy run exercises one ephemeral instance (stories260K, lane-owned port). S-LC2 line 489-490 ties `/health` 200 to "the model is successfully loaded and the server is ready" for that server only. Registered consumer ports were not served or measured; that claim is outside the evidence. |
| Admit the live capability, scoped to the lane-owned ephemeral server | admit, scoped | README supports the surfaces the harness will capture: `/health` (S-LC2 479-490), `--host` default 127.0.0.1 (line 193), `--port` default 9931 (line 194), `--metrics` default disabled (line 225), `--slots` default enabled (line 227). Unknown from my sources: the `/metrics` 501 response body, the `owned_by "llamacpp"` field, and the Ollama-shaped `models[]` array; these are L1 observations, not sourced here. |
| S021 flip if supported | partial: flip queued -> mined, vLLM-scoped; repair URL; no llama.cpp claim | S021's registry URL `https://llm-d.ai/docs/operations/readiness-probes` returned HTTP 404 on fetch today (S-LLMD0). Current pages carry the same vLLM statements (S-LLMD2, S-LLMD1). Those statements describe vLLM's `/health` (liveness only) and `/v1/models` (readiness). They do not describe llama.cpp, so they do not support the `MODEL_LOADING` rule. The round-10 lesson still cites the 404 URL; L1 decides whether to repair that link. |

### Opened sources

**S-LC1 llama.cpp b11755 server middleware** — `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/server-http.cpp`, fetched 2026-10-20, SHA-256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`.
- Lines 307-308: `auto middleware_server_state = [this](const httplib::Request & req, httplib::Response & res) { if (!is_ready.load()) {`
- Line 312 located quote (13 words): "no endpoints are allowed to be accessed when the server is not ready"
- Lines 314 and 318-320: `res.status = 503;`, `{"message", "Loading model"},`, `{"type", "unavailable_error"},`, `{"code", 503}`.
- Lines 354-355 (pre-routing handler calls the middleware for every request, returning Handled on false): `if (!middleware_server_state(req, res)) { return httplib::Server::HandlerResponse::Handled;`
- Within the b11755 file, the literal "Loading model" and "unavailable_error" appear only at lines 318-319 (grep-verified).
- Readiness flag set at `tools/server/server.cpp:460`: `ctx_http.is_ready.store(true);` (fetched at the same commit; SHA-256 prefix `dd1de0f26536ce3e`).

**S-LC2 llama.cpp b11755 server README** — `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/README.md`, fetched 2026-10-20, SHA-256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`.
- Lines 479-490, section `### GET /health`: status 503 with body `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, and located quote (line 487, 8 words): "the model is still being loaded."
- Line 490 located quote (12 words): "the model is successfully loaded and the server is ready."
- Line 193: `--host HOST` ... `(default: 127.0.0.1)`; line 194: `--port PORT` `(default: 9931)`; line 225: "enable prometheus compatible metrics endpoint (default: disabled)"; line 227: "expose slots monitoring endpoint (default: enabled)".

**S-LC3 llama.cpp error-type mapping** — `tools/server/server-common.cpp` at 704366d76 (fetched 2026-10-20, SHA-256 prefix `b4f4aae7eed919f9`), lines 119-121: `case ERROR_TYPE_UNAVAILABLE: type_str = "unavailable_error"; code = 503;`. Shows that every `ERROR_TYPE_UNAVAILABLE` error shares the type and code, so a rule on type and code alone would over-match.

**S-LC4 llama.cpp no-slot 503** — `tools/server/server-context.cpp` at 704366d76 (fetched 2026-10-20, SHA-256 prefix `dd1de0f26536ce3e`), lines 5394-5396: `if (!req.get_param("fail_on_no_slot").empty()) { if (res_task->n_idle_slots == 0) { res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));`. README line 987 (S-LC2): located quote (20 words): "If query param `?fail_on_no_slot=1` is set, this endpoint will respond with status code 503 if there is no available slots."

**S-LLMD2 llm-d current readiness page (v1.0, latest)** — `https://llm-d.ai/docs/operations/lifecycle/readiness-probes`, opened 2026-10-20, page titled "vLLM Model-Aware Readiness Probes". Section "/health Endpoint": located quote (21 words): "The vLLM `/health` endpoint only indicates that the server process is running, **not** that models are loaded and ready to serve." Section "/v1/models Endpoint (OpenAI-Compatible)": located quote (10 words): "The `/v1/models` endpoint is model-aware and indicates true readiness". Page has no line numbers; locators are section headings.

**S-LLMD1 llm-d v0.10 readiness page** — `https://llm-d.ai/docs/0.10/operations/readiness-probes`, opened 2026-10-20. Same two sections and the same located quotes as S-LLMD2; the page states it is v0.10 and "no longer actively maintained".

**S-LLMD0 registry URL (S021)** — `https://llm-d.ai/docs/operations/readiness-probes`, fetched 2026-10-20: `HTTP 404`. A web search the same day returns the moved pages above (S-LLMD1, S-LLMD2) and a GitHub copy at `https://github.com/llm-d/llm-d/blob/main/docs/operations/readiness-probes.md`, which I did not open. Unknown: whether the old URL is a permanent removal or a transient fault; one fetch only.

**S-REG S021 registry row** — `corpus/SOURCES.md:33`, status `queued`, used-by "—". Located quote (from the row, 10 words): "Distinguishes process liveness on `/health` from the guide's model-aware `/v1/models`".

### Unknowns L1 must carry

- Whether `~/.local/opt/llama-b11755` and its linked `llama-server` binary are built from commit 704366d76 and match the asset SHA-256 in the brief. Not checked by this scribe.
- Whether any other llama.cpp build uses the same `Loading model` body. Not checked; the rule is pinned to b11755.
- The `/metrics` 501 response, the `owned_by` value and the Ollama-shaped `models[]` array in the L1 smoke run. Not sourced here.
- Whether the `MODEL_LOADING` rule's ordering (checked only when `/v1/models` returns 503) matches the frozen probe's current `classify()` flow. Not checked; the classifier is L1's and the other critics' scope.
