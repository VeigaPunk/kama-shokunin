# ScoutSglangStartup — SGLang `/health`, `/health_generate`, `/v1/models` during load/warmup

Read-only seat. Question: what do those three routes answer while SGLang is loading or warming up?

## Pin

- Tag `v0.5.22` (release 2026-10-19T02:55Z) → annotated tag `35ce313293052f8362e0829e7512bc9bc3d336c9`, commit `baa9befa381511cd4d56f83980951e5a45fffc6d` (verified `git ls-remote --tags https://github.com/sgl-project/sglang.git 'refs/tags/v0.5.22*'`). Matches corpus S020's `baa9bef`.
- Files opened at that tag (raw.githubusercontent.com, `v0.5.22`):
  - `python/sglang/srt/entrypoints/http_server.py` (2961 lines)
  - `python/sglang/srt/entrypoints/engine.py` (2066 lines)
  - `python/sglang/srt/managers/tokenizer_manager.py` (4102 lines)
  - `python/sglang/srt/environ.py`, `python/sglang/srt/entrypoints/openai/protocol.py`
  - `docs/docs/basic_usage/native_api.mdx` (docs page: https://docs.sglang.io/docs/basic_usage/native_api)
- Local copies under `/tmp/sgl/` (scratch, not lane artifacts). No SGLang runtime was started; every runtime statement below is read from the lifecycle code and marked when inferred.

## Answer in one table

| Phase | `GET /health` | `GET /health_generate` | `GET /v1/models` |
|---|---|---|---|
| Weight load / graph capture (HTTP not yet bound) | connect refused — DEAD [INFERENCE from ordering] | same | same |
| HTTP up, `server_status == Starting` (warmup in flight) | **503, empty body** | **503, empty body** | **200** with `data[0].id = served_model_name` |
| Warmup returned 200 (`Up`) | 200; **runs one-token generation** by default (up to 20 s) | 200; runs one-token generation | 200, unchanged |
| Warmup failed | process killed → DEAD | same | same |

The surprising cell is the third column: `/v1/models` is not readiness-gated, so a warming SGLang looks `MODEL_OK` to kama while `/health` and `/ready` are still 503.

## Observed facts (source)

F1. `/health` and `/health_generate` are one handler with two decorators.
`http_server.py:705-707` — `@app.get("/health")` / `@app.get("/health_generate")` / `async def health_generate(request: Request) -> Response:`
Quote: "`@app.get("/health")` / `@app.get("/health_generate")`" (two decorators, one function).

F2. While `Starting`, both routes short-circuit to 503 — before any generation and before the diag bypass.
`http_server.py:719-720` — `if _global_state.tokenizer_manager.server_status == ServerStatus.Starting:` / `return Response(status_code=503)`
Quote: "server_status == ServerStatus.Starting" → "Response(status_code=503)".
This check sits *above* `SGLANG_DIAG_BYPASS_HEALTH_GENERATE` (`:723-727`) and the fast-200 branch (`:729-733`), so no env var overrides the 503 during startup.

F3. `server_status` begins as `Starting` at manager init and is a three-value enum.
`tokenizer_manager.py:703` — `self.server_status = ServerStatus.Starting`
`tokenizer_manager.py:4023-4026` — `class ServerStatus(Enum): Up = "Up"; Starting = "Starting"; UnHealthy = "UnHealthy"`

F4. v0.5.22 also ships a dedicated readiness route, `/ready`, not used by `/v1/models`.
`http_server.py:698-702` — `@app.get("/ready")` / `"""Report whether the server is ready to receive new requests."""` / `status_code = 200 if _global_state.tokenizer_manager.is_ready() else 503`
`tokenizer_manager.py:713-718` — `return (not self.is_pause and not self.gracefully_exit and self.server_status == ServerStatus.Up)`
Quote: "not self.gracefully_exit and self.server_status == ServerStatus.Up".

F5. `/v1/models` consults no status or readiness field at all.
`http_server.py:1926-1955` — `@app.get("/v1/models", response_class=ORJSONResponse)` / `served_model_names = [_global_state.tokenizer_manager.served_model_name]` / `id=served_model_name` / `return ModelList(data=model_cards)`
Quote: "served_model_names = [_global_state.tokenizer_manager.served_model_name]".
No `server_status`, `is_ready`, or `gracefully_exit` appears in the handler body, so it answers 200 whenever the app is serving, including the whole `Starting` window and during graceful shutdown.

F6. Response shape: `data[].object` is `"model"`, `data[].owned_by` defaults to `"sglang"`, list-level `object` is `"list"`.
`protocol.py:81-97` — `class ModelCard(BaseModel):` / `object: str = "model"` / `owned_by: str = "sglang"` / `class ModelList(BaseModel):` / `object: str = "list"`
Quote: "owned_by: str = \"sglang\"".

F7. The HTTP port is not bound until weights are loaded.
`http_server.py:2924-2937` — `# Launch subprocesses` … `Engine._launch_subprocesses(`
`engine.py:1337-1338` — `# Wait for the model to finish loading` / `scheduler_init_result.wait_for_ready()`
`http_server.py:2952` — `_setup_and_run_http_server(` (uvicorn/Granian bind happens here, after the wait above)
`engine.py:1986` — `"""Wait for the model to finish loading and return scheduler infos.`
Quote: "Wait for the model to finish loading".
So the model-load phase is a closed port, not an HTTP 503. [INFERENCE: on the wire that is `connection-refused`, i.e. kama `DEAD`/`connection-refused`.]

F8. Warmup runs in a background thread started before the ASGI app yields, so the server serves while warmup is in flight.
`http_server.py:436-444` — `# Execute the general warmup` / `warmup_thread = threading.Thread(` / `warmup_thread.start()` / `# Start the HTTP server` / `yield`
Quote: "warmup_thread.start()" then "# Start the HTTP server" then "yield".
Until the warmup request returns 200, `server_status` stays `Starting`, so F2 applies for the whole warmup.

F9. `Up` is set only after the warmup generation succeeds; failure kills the process.
`http_server.py:2423-2424` — `assert res.status_code == 200, f"{res.text}"` / `_global_state.tokenizer_manager.server_status = ServerStatus.Up`
`http_server.py:2453-2457` — `except Exception:` … `kill_process_tree(os.getpid())`
`http_server.py:2497-2501` — `if not get_serving().skip_server_warmup and not skip_elastic_joiner_warmup:` … else `server_status = ServerStatus.Up`
Quote: "server_status = ServerStatus.Up" (post-200), "kill_process_tree(os.getpid())" (failure).

F10. After `Up`, `/health` is a generation check by default, not a cheap liveness read.
`environ.py:341` — `SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION = EnvBool(True)`
`http_server.py:729-733` — `not envs.SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION.get()` / `and request.url.path == "/health"` → bare 200 only when that env is disabled.
`http_server.py:207` — `HEALTH_CHECK_TIMEOUT = int(os.getenv("SGLANG_HEALTH_CHECK_TIMEOUT", 20))`
`http_server.py:763-769` — `while time.time() < tic + HEALTH_CHECK_TIMEOUT:` / `if _global_state.tokenizer_manager.last_receive_tstamp > tic:` → 200; timeout sets `UnHealthy` and 503 at `:782-783`.
Quote: "HEALTH_CHECK_TIMEOUT = int(os.getenv(\"SGLANG_HEALTH_CHECK_TIMEOUT\", 20))".
Consequence: a ready, idle model normally answers `/health` in ~1 s (the loop sleeps one second before its first check, `:764`), but a busy model can hold the request up to 20 s.

F11. Docs document only the two routes, and state nothing about 503-during-startup or `/ready`.
`docs/docs/basic_usage/native_api.mdx:108-110` — `## Health Check` / `- \`/health\`: Check the health of the server.` / `- \`/health_generate\`: Check the health of the server by generating one token.`
Quote: "Check the health of the server by generating one token."
Grep of that page for `503`, `ready`, `loading` returns nothing.

F12. Upstream corroborates the 503-until-warmup intent in the Rust-server comment.
`http_server.py:2943-2947` — `# Each Rust listener runs its own startup warmup and keeps /health at` / `# 503 until it succeeds, so the main process does not warm up here.`
Quote: "keeps /health at 503 until it succeeds" (7 words).
This is a second entrypoint with the same contract, not evidence about the Python path.

## Consequences for kama (advice, not a verdict)

A1. **SGLang never reaches the probe's 503 branch by default.** `GET /v1/models` returns 200 + a model array from the moment the port binds, so kama grades `MODEL_OK` (identity matched) while `server_status == Starting`. Under kama's identity-only contract that is not an identity defect, but it must not be read as readiness: `/health` and `/ready` are 503 at the same instant (F2, F4, F5). [INFERENCE: not measured against a live SGLang in this seat.]

A2. **The loading phase is `DEAD`, not `FOREIGN_SERVICE`.** Because binding follows `wait_for_ready` (F7), a model that is still loading its weights shows a closed port. A probe started too early will therefore report `DEAD connection-refused`, then flip to `MODEL_OK` at bind time — with no intermediate "loading" verdict for SGLang.

A3. **C1's exact-body `MODEL_LOADING` rule cannot and should not generalize to SGLang.** The 503s at `:717`/`:720`/`:783` are `Response(status_code=503)` with no content (F2), so there is no JSON `error.message` to match. If `/v1/models` ever 503'd, SGLang would land on the existing `non-2xx-non-model-http` FOREIGN_SERVICE at frozen `kama-probe-before.sh:521`; in v0.5.22's default path that branch is unreachable for SGLang. [INFERENCE: body emptiness at the wire level; FastAPI sends no body for a content-less `Response`.]

A4. **The probe currently discards the one signal that would explain SGLang's state.** Frozen probe `:500-501` appends `/health` to `MODEL_OK` evidence only for `200|*json*`, so a concurrent `503` is dropped from evidence. For an SGLang target the evidence line cannot distinguish "ready" from "warmup in flight" even though the server itself says which.

A5. **Do not use SGLang `/health` as a cheap liveness probe.** With the default `EnvBool(True)` (F10), a ready server's `/health` is a generation request with a 20 s ceiling; kama's `--timeout 2` will usually surface `err-28` and, per A4, silently omit it. `/ready` (`:698-702`) is the only cheap 200/503 readiness route SGLang v0.5.22 ships — and it is undocumented on the native API page (F11), so it must never be relied on cross-engine.

A6. **Scope limit to record with C1.** "Non-model service" remains the wording for SGLang's empty 503 only in a hypothetical path; on the documented/observed lifecycle, the overreach for SGLang is the opposite one: `MODEL_OK` before readiness. If the lane wants one sentence for the calibration entry, it is: *llama.cpp says "loading" in a JSON 503; SGLang answers 200 on `/v1/models` and 503 on `/health`/`/ready`; llama.cpp's 503 body rule is engine-specific.*

## Limitations / unresolved

- No SGLang process was launched (read-only seat; no GPU/weights here), so the table's wire-level cells are source-derived. Body emptiness, absent `Content-Type`, and the exact status line are [INFERENCE] from `Response(status_code=...)` without content.
- Default single-tokenizer path only. `--tokenizer-worker-num > 1` (uvicorn supervisor re-import, `:2811-2826`) and DP/disaggregation warmup (`:2426-2451`) were read but not traced.
- `--skip-server-warmup` skips the 503 window entirely (`:2497-2501`): the server goes straight to `Up` after bind.
- Graph-capture timing (whether CUDA graph capture happens before the scheduler's `ready` message) was not investigated; it affects only the length of the `DEAD` phase, not the verdict.
- Version drift after v0.5.22 unverified; the pin is `baa9bef`.

## Installs

None — no package, binary, or tool was installed or upgraded in this seat.
