# ScoutVllmStartup — vLLM pre-ready surface (`/v1/models`, `/health`)

Read-only scout, 2026-10-20. Axes: operability + calibration. Question: what does a vLLM
OpenAI server answer on `/v1/models` and `/health` before the engine is ready, and does C1's
llama.cpp-only scope leave a vLLM gap?

## Answer (v0.32.0, the current stable release)

**Neither endpoint answers: the TCP connection is refused.** The API server `bind()`s the port
*before* the engine is built and never calls `listen()` there; `serve_http` is not invoked until
the engine core has reported READY (weights loaded). [INFERENCE: uvicorn performs the actual
`listen()` in `Server.serve`; the socket code here only binds — the Rust frontend's comment at
`listener.rs:84-87` confirms Python leaves the inherited socket unlistened.] A client sees
`curl` rc 7 / `ECONNREFUSED` on both routes — **not 503, and no HTTP response at all**. Same
ordering in v0.10.2 and v0.6.4. Once listening: `/health` is 200 (503 only on
`EngineDeadError`), `/v1/models` is 200 with `data[]`.

Version pin: v0.32.0, `published_at 2026-10-18T06:50:48Z`, `tag_name v0.32.0`
(`https://api.github.com/repos/vllm-project/vllm/releases/latest`, 2026-10-20). Sources read
as raw files at that tag; cross-checks at `v0.10.2` and `v0.6.4`. All citations below are
reproducible as `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/<path>` (substitute
the tag for the cross-checks).

## 1. Startup ordering (v0.32.0)

| Step | Cite (path:line) | Evidence |
|---|---|---|
| Bind before engine | `vllm/entrypoints/launchers/launcher.py:391-393` | "workaround to make sure that we bind the port before the engine is set up." |
| Bind only, no listen | `vllm/entrypoints/launchers/launcher.py:344-350` | `sock.setsockopt(...); sock.bind(addr)` then `return sock` — no `listen()` |
| `run_server` order | `vllm/entrypoints/launchers/api_server/entry.py:176,195` | `sock = setup_server(...)` precedes `async with build_async_engine_client(` |
| Engine blocks until READY | `vllm/v1/engine/core_client.py:735-753` | "Wait for ready messages from each engine on the input socket."; timeout text: "often caused by slow weight loading for large models" |
| READY sent after core init | `vllm/v1/engine/core.py:1217-1228,1871-1877` | input thread starts after `EngineCore` construction; `input_socket.send(ready_payload)` |
| App built after engine | `entry.py:133,140,142` | `supported_tasks = await engine_client.get_supported_tasks()`; only then `serve_http` |
| Load window default | `vllm/envs.py:809-813` | "Default is 600 seconds (10 minutes)." (`VLLM_ENGINE_READY_TIMEOUT_S`) |

Kernel control (run locally 2026-10-20, loopback ephemeral port, no vLLM): a socket that is
`bind()`-ed but not listening returns `ConnectionRefusedError` errno 111 to `connect()`.
`kama-probe.sh` maps curl rc 7 to `DEAD` / `connection-refused` (`tools/kama-probe.sh:460-463`).

## 2. Cross-tag check (same invariant)

| Tag | Bind | Engine | Serve |
|---|---|---|---|
| v0.6.4 | `vllm/entrypoints/openai/api_server.py:597-601` ("workaround to make sure that we bind the port before the engine is set up.") | `:609` | `:615` `serve_http` |
| v0.10.2 | `vllm/entrypoints/openai/api_server.py:1904-1911` (same comment) | `:1961` | `:1973` `serve_http` |
| v0.32.0 | `launchers/api_server/entry.py:176` | `:195` | `:199-200` |

No tag in this span serves HTTP before the engine is ready. The bind-early workaround (issue
8204, cited in the comment) is what makes "connection refused" the pre-ready observation.

## 3. Endpoint semantics once listening

- `/health` — `vllm/entrypoints/serve/instrumentator/health.py:23-33`: `check_health()` then
  "return Response(status_code=200)", with `except EngineDeadError: return Response(status_code=503)`.
  No readiness gate; 503 means **engine dead**, never "loading". Render-only servers return 200
  unconditionally (`:26-28`).
- `/v1/models` — `vllm/entrypoints/openai/models/api_router.py:24-29` returns the serving
  handler; `vllm/entrypoints/openai/models/serving.py:149-165` builds cards from static
  `base_model_paths`/`lora_requests`. It never consults engine health.

## 4. Other launch topologies (v0.32.0)

| Topology | What happens pre-ready | Cite |
|---|---|---|
| `--api-server-count > 1` | Parent binds (`setup_server(args, reuse_port=num_api_servers > 1)`), launches engines, then spawns workers with the inherited `sock`; each worker serves only after its engine client is ready | `vllm/entrypoints/cli/serve.py:298`; `vllm/v1/utils.py:248-257,509-520` |
| DP supervisor | `/health` would be 503 while `is_ready` is false, but its uvicorn starts **only after** children are ready; app has `/health`, `/ready`, `/readyz` and no `/v1` route | `launchers/dp_supervisor.py:228-230,303-307,324-326` ("This avoids the supervisor /health endpoint returning 503") |
| Rust frontend (opt-in; `VLLM_USE_RUST_FRONTEND` default 0, `envs.py:1475-1477`) | `/health` returns 503 when not healthy (`rust/src/server/src/routes/health.rs:11-17`), but `EngineCoreClient::connect` completes before `Listener::bind`; Python only pre-binds, Rust calls `socket.listen` on the inherited fd | `rust/src/server/src/lib.rs:116-124,214`; `rust/src/server/src/listener.rs:84-87` |

Direct code statement that the Python pre-bound socket is **not** listening: "The Python
supervisor pre-binds the socket to reserve the endpoint early, but Rust is responsible for
transitioning inherited stream sockets into the listening state" (`listener.rs:84-87`).

## 5. Documentation statements

- `docs/deployment/k8s.md:244-255`: both `livenessProbe` and `readinessProbe` use
  `path: /health` with `initialDelaySeconds: 60` — consistent with no early HTTP.
- `docs/serving/online_serving/openai_compatible_server.md` at v0.32.0: **zero `health` matches**
  (observed absence; 9,650-byte file). `docs/deployment/k8s.md` is the docs file I opened that
  configures `/health` probes; no repo-wide docs sweep was done, so this is not an absence proof
  for every docs page.
- Lane source S021 (llm-d v0.10, `docs/operations/readiness-probes.md`): §`/health` says
  "Returns `200 OK` immediately when vLLM server starts / Does **not** wait for model loading";
  §`/v1/models` says "Returns `503` or connection refused during model loading".
  Reconciliation: the first sentence is **handler-level** (the handler has no readiness gate),
  not listener-level. The listener is not up before load, so "200 immediately" cannot be
  observed on a real vLLM during load; the page's own `/v1/models` line already admits
  "connection refused". Any lane entry repeating the `/health` sentence must add "once the HTTP
  server is up (after load)" or it overstates vLLM availability. [INFERENCE on intent: the doc
  does not state which vLLM version it measured.]

## 6. Does C1's llama.cpp-only scope leave a vLLM gap?

- **Misclassification: no.** Pre-ready vLLM yields rc 7 -> `DEAD`/`connection-refused`
  (`kama-probe.sh:460-463`); the C1 branch cannot fire because there is no HTTP response to
  parse. Frozen and repaired probes agree for vLLM, so there is no red/green mutation here:
  vLLM cannot be a C1 positive control, and a vLLM "loading 503" fixture would encode a surface
  that does not exist.
- **Semantic/operability gap: yes, small and already bounded.** `DEAD` now covers two
  operator situations: never-was (crash, wrong port) and not-yet (weights loading, up to 600 s
  by default). C1's vocabulary cannot reach the second because the evidence is a refused
  connection, not an HTTP body. Covering it would need process/socket evidence outside the
  probe's HTTP contract, or a status-only rule — which the code forbids: vLLM's 503 is
  `EngineDeadError` **after** readiness, and the other 503s are `/health`-only (DP supervisor:
  unreachable pre-ready; Rust: reachable only post-ready).
- **Adjacent post-ready limit [INFERENCE, from code + probe logic].** With a dead engine,
  `/v1/models` still answers 200 from cached config while `/health` answers 503
  (`health.py:30-33`; `models/serving.py:149-165`). `classify()` decides on `/v1/models` first
  and keeps `MODEL_OK` (`kama-probe.sh:506-536`); `/health` is evidence only, so the probe
  reports `MODEL_OK` for a dead-engine vLLM. Not a C1 defect, but the same surface-mismatch
  class the lane is calibrating.

## 7. Advice for L1

1. **Keep C1 llama.cpp-only.** Add one scope sentence to the MODEL_LOADING text/knowledge:
   "vLLM is not covered: before the engine is ready it accepts no TCP connection (bind-only
   socket), so clients see connection refused, not a 503; `DEAD` is the honest verdict."
2. **Do not add a vLLM 503 loading fixture** to the stub matrix. There is no such surface on
   `/v1/models`; a fixture would assert behaviour the server never exhibits. If a vLLM row is
   wanted, it belongs in a closed/refused family, which already exists.
3. **If S021 is mined, qualify its `/health` sentence** per §5; cite the `/v1/models` line
   ("503 or connection refused during model loading") as the accurate one.
4. **If a source row is added,** pin v0.32.0 and anchor to
   `launchers/api_server/entry.py:176,195` + `launchers/launcher.py:391-393` for bind-before-engine.
5. **No new verdict.** A `LOADING_UNREACHABLE` state would need non-HTTP evidence and would
   widen the probe's contract; the existing `DEAD` reason is factually correct at the socket.

## 8. Limitations / tooling

- No local vLLM install; no live vLLM was started. Findings are static (raw GitHub at tag)
  plus a kernel-level socket control on this host (127.0.0.1 ephemeral port); not a lane
  measurement.
- `api_server.py` was refactored into `vllm/entrypoints/launchers/` in v0.32.0; line numbers
  differ per tag (given above). Rust-frontend and DP-supervisor statements are source-level,
  not executed.
- No LSP applies to upstream files not checked out locally; retrieval is literal raw-file
  reading and `grep`, not semantic navigation.
- Installs or updates: none. No lane gate, harness, probe, or test was run. Only this Report
  was written.
