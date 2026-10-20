# ScoutKoboldCppServer — KoboldCpp `/v1/models` and pre-load behaviour

Axis: operability + calibration (cross-vendor witness for the `MODEL_LOADING` verdict).
Read-only scout: no edits outside this file, no installs, no lane gate or harness run.

## Version pin

- Release `v1.123.1`, tag commit `9be8c136ae7e17eb50d9b7a6f3dff5038fcc3186`, published 2026-10-13 —
  `https://api.github.com/repos/LostRuins/koboldcpp/releases/latest` → `"tag_name": "v1.123.1"`.
- In-source version: `koboldcpp.py:93` — `KcppVersion = "1.123.1"`.
- Sources read at that commit (raw.githubusercontent.com with the full SHA): `README.md`,
  `koboldcpp.py` (13,964 lines), `kcpp_src/expose.cpp` (482 lines; no HTTP server in the ctypes
  exposure), `Makefile`. A separate `llamaserver` build target compiles llama.cpp `tools/server/*`
  (`Makefile:746,818`), but `koboldcpp.py` never spawns it (`grep llamaserver` empty); `/lcpp` is
  served as embedded static UI (`7300-7306`), so the routes below are the Python server's.
  Working copies in `/tmp/kobold-re/`, not in the lane.

## Findings

### 1. Endpoint exists, OpenAI-shaped, and is a constant
- Route: `koboldcpp.py:7098` — `elif clean_path.endswith('/v1/models') or clean_path=='/models':`.
  Both `/v1/models` and bare `/models`; trailing slash is stripped first (6961).
- Body: `koboldcpp.py:7103` —
  `{"id":modelNameToReturn,"object":"model","created":int(time.time()),"owned_by":"koboldcpp","status":{"value":"loaded"},"permission":[],"root":"koboldcpp"}`,
  wrapped at `7108` — `response_body = (json.dumps({"object":"list","data":mlist}).encode())`.
- Content-Type: `koboldcpp.py:6970` — `content_type = 'application/json'` (never overridden in this branch).
- README: `README.md:139` — `` | OpenAI-compatible API | `http://localhost:5001/v1` | ``;
  no per-endpoint documentation of `/v1/models` beyond that base URL.

### 2. Model id is `koboldcpp/<file stem>`
- `koboldcpp.py:12943-12946` — basename, `os.path.splitext`, then
  `friendlymodelname = "koboldcpp/" + sanitize_string(newmdldisplayname)`.
- `koboldcpp.py:11759-11761` — `sanitize_string` keeps only `[\w\d\.\-_]`;
  `koboldcpp.py:12955` forces the same `koboldcpp/` prefix on `--hordemodelname`.
- Example: `stories260K.gguf` → `koboldcpp/stories260K`.
- Probe side: `tools/kama-probe.sh:376` — `normalize_id() { local s=${1-}; s=${s##*/}; s=${s%.gguf}; … }`
  strips the `koboldcpp/` prefix, so `--expect stories260K` matches. [INFERENCE] for the literal
  runtime id; the derivation is source-observed.

### 3. `status` is hardcoded, never load state
- `koboldcpp.py:7103` and `7107` both emit `"status":{"value":"loaded"}` unconditionally; the handler
  has no reference to load state.
- Router mode (`--routermode`, `7104-7107`) appends every `get_current_admindir_list()` entry —
  admin-dir `.kcpps/.kcppt/.gguf` scan plus `initial_model`/`unload_model` (`1592-1600`) — each
  labelled `loaded`. The response is a catalog, never readiness.

### 4. No auth on GET /v1/models
- Block `7098-7108` calls no `check_header_password` (`def` at `6756`; call sites `6773`, `6999`,
  `7029`, and POST paths `7681+`). With `--password`, `/v1/models` still answers 200; only
  `/api/v1/model` substitutes `koboldcpp/protected-model` (`6999-7001`). [INFERENCE from code path]
- Consequence: this vendor can never produce `UNAUTHORIZED_SERVICE` from `/v1/models`.

### 5. Before load, default single-process mode: port is not listening (DEAD)
- Load: `koboldcpp.py:13165` — `print(f"Loading Text Model: {modelname}", flush=True)`;
  `13168` — `loadok = load_model(modelname)` (blocking, inside `kcpp_main_process`).
- Listener only after load, at `13729` —
  `asyncio.run(RunServerMultiThreaded(args.host, args.port, KcppServerRequestHandler, on_server_ready))`;
  the socket bind is `8625` — `ipv4_sock.bind((addr, port))`.
- Load failure: `13169-13172` — `exit_with_error(3,"Could not load text model: " + modelname)`;
  the process exits and never binds.
- Documentation: `README.md:128` — "The browser cannot connect: Wait for model loading to finish and
  check the address printed in the terminal."
- So `GET /v1/models` during load is a TCP connect refusal, i.e. probe `DEAD` / `connection-refused`
  (`tools/kama-probe.sh:449,462`), never HTTP 503.

### 6. Before load, router mode (forces admin): 502 + HTML
- Router mode is the only mode with a listening socket before load. `--admin` alone still binds the
  real port only after load, i.e. behaves as §5. `main()` forces admin for router (`12354-12357`),
  reserves an internal port from 15001-15010 (`12359-12365`), then `12377` —
  `run_router_proxy(args.proxy_port,newport)`. The user-facing port is bound before any model exists.
- The model process starts only afterwards: `12407` —
  `kcpp_instance = multiprocessing.Process(target=kcpp_main_process,…)`; it loads at `13168`.
- Proxy covers every method: `5623-5629` — `do_GET = _handle`, `do_POST = _handle`, …; upstream
  connect failure hits `5555` — `except OSError as e:` → `5593` — `self.send_response(502)` with
  `Content-Type: text/html; charset=utf-8` (`5594`).
- Page body: `5571` — `<h2>KoboldCpp is not available.</h2>`; `5573` — "It may take some time
  during a model (re)load before it is ready to use."
- The proxy also sends `Server: KoboldCppServer/1` (`5396-5397`), i.e. the header is present on the
  502 as well.
- Probe classification of this shape: 502 + HTML → `FOREIGN_SERVICE` / `html-non-model`
  (`tools/kama-probe.sh:549`). That is accurate for the bytes served, but it is also the vendor's
  documented "still loading" page.

### 7. Autoswap mode: 200 that claims loaded while nothing is loaded
- Startup sets `nomodel` and disables model fields: `12745-12746`; the configured text model is only
  recorded as `textName` (`12717` — `textName = "koboldcpp/" + sanitize_string(tempName)`).
- `/v1/models` returns `textName` whenever `autoswapmode and textName is not None` (`7100-7101`),
  still with `status=loaded`.
- `/v1/models` is not a wake trigger: it is absent from `wake_requests` (`koboldcpp.py:5452` —
  `wake_requests = ["/api/extra/generate/stream","/api/extra/tokencount","/api/v1/generate",…]`), so a
  sleeping autoswap instance answers 200 "loaded" (child up) or 502 (child unloaded) until a
  generation request wakes it.

### 8. Adjacent surfaces the probe may touch
- No `/health`: absent from `koboldcpp.py` (whole-file grep). Unmatched GET → `7343-7346`: 404,
  `content_type='text/html'`, "Error: KoboldCpp HTTP Server is running, but this endpoint does not exist."
- `/slots` → `7285` `self.send_response(501)` + `7287`
  `{"error":{"code":501,"message":"This server does not support slots endpoint.","type":"not_supported_error"}}`
  (hardcoded, no auth). `/props` exists (`7258-7282`). `/v1` itself is 200 HTML (`7328-7330`).
- All `send_response(503)` occurrences (`7812`, `7830`, `7934`) are inside `do_POST` (`7357+`).
  GET `/v1/models` can only be 200 (post-load) or 502 (router, upstream down); never 401/403/503.

### 9. No-model launch
- `--nomodel` (`13823`) permits a listener with no text model. `friendlymodelname` stays `"inactive"`
  (`101`), so `data[0].id == "inactive"` with `status=loaded`.
- Probe outcome: `--expect <stem>` → `MODEL_MISMATCH`/`served-id-mismatch`; `--expect '*'` →
  `MODEL_OK`. [INFERENCE: runtime path not executed]

## Calibration advice (advice only; L1 measures)

1. Do not extend C1's `MODEL_LOADING` predicate to any non-llama.cpp shape. KoboldCpp has no
   503-on-GET surface at all; its genuine loading states are connection-refused (default) and
   502+HTML (router). The latter is byte-identical to a sleeping autoswap instance, so reclassifying
   it as loading would recreate the overreach C1 removes, one vendor over. The existing
   `tests/probe-verdicts/NonLoadingStatuses.json` `err502-envelope` control (502 + the exact llama.cpp
   loading JSON → `FOREIGN_SERVICE`/`non-2xx-non-model-http`) already separates status from body;
   KoboldCpp's 502 is `text/html`, so it lands in the distinct `html-non-model` branch. No matrix
   change is required for this vendor.
2. If a KoboldCpp family is ever added under `tests/probe-verdicts/`, the stub shapes that match this
   source are:
   (a) `port_mode: closed` → `{"verdict":"DEAD","reason":"connection-refused","exit":2}` for
       single-process pre-load;
   (b) `routes {"/v1/models": {"status":502,"headers":{"content-type":"text/html; charset=utf-8"},
       "body_text":"<h2>KoboldCpp is not available.</h2>"}}` → `FOREIGN_SERVICE`/`html-non-model`;
   (c) 200 `{"object":"list","data":[{"id":"koboldcpp/stories260K","object":"model",
       "status":{"value":"loaded"}}]}` → `MODEL_OK` with `--expect stories260K`.
3. Post-load `--expect` needs no special casing: `normalize_id` already hides the `koboldcpp/` prefix.
4. `Server: KoboldCppServer/1` is emitted by both the real server and the loading router's 502 page;
   the probe's v3 rule (status/Server never sufficient) already handles this. Keep it that way.

## Limitations / not done

- Static source + README only. No KoboldCpp binary is installed or was launched; no runtime capture.
  Every statement about the load window is a code-path reading; runtime-specific claims are marked
  [INFERENCE].
- Upstream `tests/` was not enumerated (one GitHub tree query returned a null tree; not retried).
- No tool installs, no lane gate, no harness run. Writes limited to this file; temp read-only copies
  in `/tmp/kobold-re/`.

## Remaining unknowns

- Whether the shipped 1.123.1 Linux binary (PyInstaller-packed from this same `koboldcpp.py`) diverges
  in any header or ordering from the source read — not verified.
- Exact duration of the router-mode 502 window on slow storage (proxy up → child load → bind); order is
  proven by `12377` vs `12407`/`13168`/`13729`, timing is not.
