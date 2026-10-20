# ScoutLocalAiStartup — LocalAI /readyz, /healthz, /v1/models during model load (round 16, build wave)

Seat: read-only scout. Advice only; L1 owns judgment and every measurement. Nothing was run against the lane: no gate, harness, matrix, or test. No installs. The only write is this file.

Axes: **calibration** (primary — does LocalAI force the C1 `MODEL_LOADING` predicate to widen?), **operability** (secondary — would a LocalAI endpoint be probeable/registerable as-is?).

## Pin

- **LocalAI v4.11.0**, release published `2026-10-02T21:56:09Z` (GitHub releases API, `mudler/LocalAI`); tag `v4.11.0` -> commit `58830f7ac508845a6f4efa32cfca06af422d4d82` (`git ls-remote --tags`).
- Source and docs read from the tag tarball (`codeload.github.com/mudler/LocalAI/tar.gz/refs/tags/v4.11.0`, 27 MB, extracted under `/tmp`, outside the lane). Docs are in-repo at the same tag under `docs/content/**` and `website/static/**`, so one commit pins both. Echo v4.15.1 (`go.mod:33`).
- Citations below are `repo-relative:line` at that pin.

## Findings (observed at the pin)

### F1. `/healthz` is unconditional liveness, independent of load state

- `core/http/routes/health.go:23-25`: `app.GET("/healthz", func(c echo.Context) error { return c.NoContent(http.StatusOK) })`.
- Comment, `health.go:19-22`: `// Liveness: "is this process alive?". Deliberately independent of` (line 19), continuing "a long startup preload must not read as a hung process".
- Test, `core/http/routes/health_test.go:40-48`: "keeps /healthz green during startup" — asserts 200 with `ready` false and true.
- Consequence: `/healthz` can never distinguish loading from ready. It is a liveness-only signal by design.

### F2. `/readyz` is 200 when startup finished, 503 + JSON while it has not

- `core/http/routes/health.go:31-39`:
  `if ready != nil && !ready() { return c.JSON(http.StatusServiceUnavailable, map[string]string{"status": "starting", "reason": "startup preload in progress"}) }`, else `c.NoContent(http.StatusOK)`.
- Backing state: `core/application/application.go:120-121` — "startupComplete flips to true once New() has finished its whole startup sequence. It backs the /readyz probe."; `application.go:137` — `func (a *Application) Ready() bool { return a.startupComplete.Load() }`.
- Flip site: `core/application/startup.go:579-583` — "Everything that must happen before this process can serve a request has happened. Flip readiness last", then `application.markStartupComplete()`.
- What "model load" means for readiness: the startup preloads run **inside** `New()` — config preload `startup.go:508`, gallery/JSON/YAML preload `startup.go:512-519`, `LoadToMemory` loop `startup.go:558-567` — all before the flip. So a startup preload is readiness-blocking.
- `nil` readiness fails open (`health.go:14-17`, `health_test.go:50-60`).

### F3. In the shipped CLI path the listener starts *after* readiness flips — so `/readyz`=503 is not observable over the network

- `core/cli/run.go:782` `app, err := application.New(opts...)`; `run.go:803` `appHTTP, err := http.API(app)`; `run.go:836` `return appHTTP.Start(listenAddress)`.
- `http.API(...)` is built **after** `New()` returns, and `New()` flips readiness at its very end (`startup.go:583`). `http.API` has exactly one production caller (`run.go:803`; `grep 'http\.API('` over non-test Go). By construction, the frontend's `/readyz` answers 200 to every network client that can reach it; the 503 branch is reachable for library embedders and unit tests, not for a curl during startup.
- Docs corroborate the pre-bind window: `docs/content/getting-started/containers.md:127-129` — "startup preload can download tens of GB before the API binds".
- Socket activation does not change ordering: the inherited listener is acquired before `New` (`core/cli/run.go:259-275`; `core/cli/run_socket_activation_linux.go:50-66` -> `net.FileListener`), but accept still begins only at `appHTTP.Start` (`run.go:836`). [INFERENCE] During preload the systemd socket is kernel-listening, so a TCP connect succeeds and then gets **no HTTP answer** until start — a 2 s probe would grade `DEAD timeout` (curl rc 28), never "loading". Not measured here.

### F4. The `/readyz` 503 body is not a model envelope

- Body is `{"status":"starting","reason":"startup preload in progress"}` (`health.go:33-36`): no `error` object, no `data`/`models` array.
- Under `tools/kama-probe.sh` `classify()` that shape would land in `FOREIGN_SERVICE non-2xx-non-model-http` — but only if `/readyz` were the fetched path. It is not: `classify()` fetches `/v1/models` only (`tools/kama-probe.sh:452` `fetch "$port" "/v1/models" "m$port"`). No probe-visible effect today.

### F5. `GET /v1/models` is a configuration listing — it does not consult load state and does not return 503 while loading

- Route: `core/http/routes/openai.go:276` — `app.GET("/v1/models", openai.ListModelsEndpoint(application.ModelConfigLoader(), application.ModelLoader(), application.ApplicationConfig(), application.AuthDB()))`.
- Handler: `core/http/endpoints/openai/list.go:24` calls `listVisibleModelNames`, then `list.go:35-38` returns `c.JSON(200, schema.ModelsDataResponse{Object: "list", Data: dataModels})`.
- Name source: `core/services/galleryop/list_models.go:33` — `for _, c := range bcl.GetModelConfigsByFilter(filter)` (configured models), plus loose files `list_models.go:46-55` via `ml.ListFilesInModelPath()`.
- No readiness or backend-loaded check exists anywhere in that path. [INFERENCE] A ready frontend therefore answers 200 + `data[]` whether the named backends are loaded, loading, failed, or never started; it is a "what is configured/available" answer, not a serving-readiness answer.
- Doc/behaviour drift worth recording: `docs/content/getting-started/troubleshooting.md:19` labels the same call "# List loaded models" (command at `:20`) — the source lists configured/available models, not loaded ones. This matches the lane's C1 framing that `/v1/models` 200 is not, by itself, proof of serviceability.

### F6. LocalAI's actual "model loading" signal is a POST inference 503 with a `model_loading` envelope (distributed mode), unreachable from a GET `/v1/models` probe

- `core/http/app.go:112-128` `respondModelLoading` writes 503 with `schema.ModelLoadingResponse{Error: {Message, Code: "model_loading", Type: "model_loading"}, Loading: ...}` plus `Retry-After` (`app.go:143-150`).
- Producer: `core/services/nodes/load_job_runner.go:123` `return newModelLoadingError(job, budget)`; budget default `config.DefaultModelLoadWait = 60 * time.Second` (`core/config/distributed_config.go:458`), override `LOCALAI_MODEL_LOAD_WAIT` (`docs/content/features/distributed-mode.md:78`).
- Wired only under distributed mode: `core/application/startup.go:302-303` — "Wire ModelRouter so grpcModel() delegates to SmartRouter in distributed mode".
- Docs: `docs/content/features/distributed-mode.md:128` — answered with "`503`, a `Retry-After` header, and a body that says exactly where the load is"; `distributed-mode.md:350-351` documents the probe split; `distributed-mode.md:357` — "Neither a cold start nor an ordinary shutdown makes a worker report 503".
- `docs/content/reference/api-errors.md:93` — 503 is "Also used during model-load cooldown and while a model is still cold-loading."
- Consequence: the LocalAI loading signal exists only on inference routes (POST), only after the model is already listed, and carries `type`/`code` = `model_loading`. It does not appear on `GET /v1/models`.

### F7. Probe-visible surface, by phase

| Phase | `/healthz` | `/readyz` | `GET /v1/models` |
|---|---|---|---|
| Startup preload, default CLI | no listener | no listener | connect refused -> `DEAD connection-refused` |
| Startup preload, systemd socket activation | no listener | no listener | connect queues, no answer -> `DEAD timeout` [INFERENCE] |
| Ready, model cold-staging (distributed) | 200 | 200 (readiness is startup-only) | 200 + `data[]` (config listing) |
| Worker backend cold start | 200 | 200 — `distributed-mode.md:357` | worker transfer server has no `/v1/models` |
| Worker NATS down | 200 | 503 `text/plain`, `not ready: <err>` | n/a |

Worker probe shapes differ from the frontend: `core/services/nodes/file_transfer_server.go:172-183` writes `text/plain`, 200 `ok`, 503 `not ready: <err>`; registration at `file_transfer_server.go:193-195`; a nil readiness fails open (`core/services/nodes/worker_readiness.go:28-31`).

### F8. Auth and route boundaries

- `/healthz` and `/readyz` are anonymous public routes: `core/http/auth/public_routes.go:24-26`; documented at `docs/content/features/authentication.md:52` — "Health checks: `GET /healthz` and `GET /readyz`."
- `/v1/models` is **not** public (`grep -n 'v1/models' core/http/auth/public_routes.go` -> no match) and is registered after `e.Use(authMiddleware)` (`core/http/app.go:426` vs `app.go:584`). With auth enabled a keyless call returns 401 JSON (`core/http/auth/middleware.go:116-121`), which `classify()` maps to `UNAUTHORIZED_SERVICE http-401` (`tools/kama-probe.sh:493`) — correct behaviour, not a defect.
- Pinned k8s manifest uses the split: `website/static/install/kubernetes.yaml:115-133` — `startupProbe` and `readinessProbe` on `/readyz`, `livenessProbe` on `/healthz`.

## Advice

### For C1 (calibration) — keep the verdict llama.cpp-scoped; do not add LocalAI

1. **Do not widen `MODEL_LOADING` / `llamacpp-loading`.** At v4.11.0 LocalAI has no `GET /v1/models` 503-with-model-body response. The two loading states it does have are (a) pre-listener startup, which a probe sees as `DEAD`, and (b) a POST inference 503 with `type`/`code` `model_loading` plus a `loading` object, which a GET-only probe cannot reach. A LocalAI branch would match nothing reachable and would attach a second body schema to one verdict with no measured positive control — exactly the overfit the matrix controls are meant to catch.
2. **State the C1 boundary in one sentence.** "`MODEL_LOADING` recognises the single-model llama.cpp b11755 `Loading model` 503 on `GET /v1/models` only; LocalAI, vLLM, TGI, and Ollama are separate families with their own not-ready surfaces." This keeps a future reader from inferring coverage that was never measured.
3. **No LocalAI rows are needed in the C1 matrix.** If L1 wants an over-broad-match negative control, the useful one is structural, not LocalAI-specific: the stated predicate inspects only `error.message`, `error.type`, `error.code` and (as written) tolerates sibling top-level keys. A stub serving `{"error":{"message":"Loading model","type":"unavailable_error","code":503},"loading":{...}}` would still match. [INFERENCE from C1's stated predicate] That case is unreachable through today's GET-only probe, so it is a spec-precision question, not a calibration defect.
4. If a future probe ever issues a POST to classify loading, LocalAI's inference 503 is a clean discriminator (`code == "model_loading"` and a `loading` object) and should then get its own verdict and its own matrix, not be folded into `llamacpp-loading`.

### For operability

5. **LocalAI is not a consumer in this lane, so nothing is due.** `registry/endpoint-consumers.tsv` has three rows (omp llama.cpp default `8080`; two ufo-fsd rows on `34113`), and a case-insensitive `LocalAI` grep over the lane matches only wave dispatch/spec files. There is no LocalAI listener to reconcile and no C2 launch work to extend. Do not add a registry row speculatively.
6. **If LocalAI is ever registered, record two facts in the row's notes.** (a) Its default bind is `:8080` (`core/cli/run.go:71` `default:":8080"`), which collides with the declared `http://127.0.0.1:8080` of `omp-llama-cpp-default`; starting LocalAI on defaults would squat the port that row already claims. (b) A `GET /v1/models` 200 from LocalAI proves the config loader answers, not that a model can serve; during distributed staging that 200 coexists with 503 inference.
7. **If readiness-aware probing of LocalAI is ever wanted, it is a separate mode, not a verdict edit.** It would need its own stub matrix at minimum: `/readyz` 200 with empty body, `/readyz` 503 with `{"status":"starting","reason":"startup preload in progress"}`, and a dead port. Note the default launch makes the 503 case unreachable over the network (F3), so such a mode would be mostly theoretical for the shipped CLI.

## Limitations

- No LocalAI binary was launched and no endpoint was probed. Every claim is source/doc at the tag; verdict mappings are static readings of `classify()`, not measurements.
- The socket-activation timeout behaviour (F3) is [INFERENCE] from code (kernel-listening inherited socket, accept only at `Start`), not exercised.
- `localai.io` pages are unversioned, so no site page is cited as authority; all doc quotes come from `docs/content/**` and `website/static/**` at v4.11.0.
- Only v4.11.0 was surveyed. `/readyz` and the startup-preload readiness semantics reference issue #10949 and may differ in earlier tags; none were checked.
- Echo v4.15.1's `NoContent(200)` body behaviour is taken as its documented API (status with no body written), not re-read from vendored source.

## Remaining unknowns

- Whether the intended `MODEL_LOADING` implementation tolerates extra top-level keys; this decides whether a LocalAI-inference-shaped 503 would match if a POST probe is ever added.
- Whether any shipped deployment path other than library embedding can serve `/readyz` before `markStartupComplete`; I found no second production `http.API` caller.
- Whether LocalAI versions before v4.11.0 exposed a different readiness contract (e.g. an always-200 `/readyz` or a `/health` alias); `core/http` at this tag registers no `/health` route.

## Installs

None. No tool was installed or upgraded; the only external artifact was the 27 MB tag tarball downloaded to `/tmp` for off-lane reading.
