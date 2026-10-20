# Ollama loading-state surface — scout findings

Question: do Ollama's `/v1/models` or `/api/tags` ever answer a loading-state status, and what does
`/api/ps` show while a model is loading?

Direct answers:

1. **No.** `/v1/models` and `/api/tags` have no loading-state response. Both always describe
   installed on-disk models (200) or fail with 500; there is no 503/loading branch.
2. **`/api/ps` never reports a loading model.** While the first load runs it returns 200 with the
   previously loaded set (often `{"models":[]}`) and no entry for the loading model; the wire schema
   has no status/progress field. In a narrow insert-before-ready window the request can instead
   block on the runner lock until readiness [INFERENCE].

Scope read: `docs.ollama.com` (tags, ps, openai-compatibility, errors, faq pages) and tagged source
`github.com/ollama/ollama` at **v0.40.6** (latest stable; `releases/latest` redirects to
`releases/tag/v0.40.6`). No local Ollama install and nothing listening on 127.0.0.1:11434
(`command -v ollama` empty; connection refused), so wire-timing statements below are marked
[INFERENCE] where they depend on runtime scheduling.

## F1 — `/api/tags` and `/v1/models` have no loading-state response at all

- Both routes are bound to the same list handler: `server/routes.go:2370-2371`
  (`r.HEAD("/api/tags"…)`, `r.GET("/api/tags", s.ListHandler)`) and `server/routes.go:2406`
  (`r.GET("/v1/models", middleware.ListMiddleware(), s.ListHandler)`).
- `ListHandler` can emit only 200 or 500: `server/routes.go:2120-2128`, quote
  `c.JSON(http.StatusOK, api.ListResponse{Models: models})`; a `listModels` error becomes
  `http.StatusInternalServerError`. No 503 branch, no state branch.
- The list is built from on-disk manifests, not scheduler state: `server/model_list.go:19-23`,
  quote: "listModels builds /api/tags from the manifests and the per-blob metadata files".
  A loaded-or-loading model is indistinguishable from an idle, installed one here.
- OpenAI projection preserves that: `middleware/openai.go:254-268` decodes `api.ListResponse` and
  encodes `openai.ToListCompletion`; the OpenAI model object is only `id`, `object`, `created`,
  `owned_by` (`openai/openai.go:219-224`, `509-522`). Docs `/api/openai-compatibility` confirm:
  "`created` corresponds to when the model was last modified"; "`owned_by` corresponds to the
  ollama username, defaulting to `"library"`".
- Docs `/api/tags`: only a `200` response is specified ("Fetch a list of models and their
  details"); the fields are name/model/remote_*/modified_at/size/digest/details — no status.

Consequence: a probe pointed at `/v1/models` gets 200 whether the model is cold, loading, or ready.
These endpoints cannot answer a loading question.

## F2 — `/api/ps` has no loading state, and the loading model is not listed while it loads

Docs (`/api/ps`): "Retrieve a list of models that are currently running"; response 200 is
"Models currently loaded into memory"; schema fields are name, model, size, digest, details,
expires_at, size_vram, context_length — no `status`/`loading`/`progress`.

Source confirms and explains the timing:

- `PsHandler` iterates only the scheduler's loaded-runner snapshot and always answers 200:
  `server/routes.go:2778-2828`, ending `c.JSON(http.StatusOK, api.ProcessResponse{Models: models})`
  (`:2828`).
- The wire struct has no state field: `api/types.go:943-953` (`ProcessModelResponse`) declares
  `ExpiresAt time.Time` (`json:"expires_at"`) and `SizeVRAM int64` (`json:"size_vram"`) but no
  `status`, `loading`, or `progress` member.
- A model is inserted into the loaded map only after `llama.Load` returns:
  `server/sched.go:678` (`llama.Load(...)`), `:787` (`s.loaded[runner.modelKey] = runner`).
- `Load` blocks until the backend is ready: `llm/llama_server.go:1078-1085`, "Load waits for
  llama-server to finish loading the model"; `WaitUntilRunning` is at `:1322`.
- Therefore, during the ordinary first-load window (before readiness), `/api/ps` returns 200 with
  the previously loaded models — commonly `{"models":[]}` — and no entry for the loading model.
  Observed from source ordering; live timing not exercised [INFERENCE].
- Narrow transition window: after insertion the runner's `refMu` is held until the readiness
  goroutine finishes (`server/sched.go:776`, `:1390` "True only during initial load"; the lock is
  released after `WaitUntilRunning`). `loadedModels()` takes a blocking `refMu.Lock()`
  (`server/sched.go:1810-1847`), so a `/api/ps` request that lands in that window waits rather than
  emitting a loading row [INFERENCE]. If `expires_at` is still zero it is synthesized as
  `time.Now()+sessionDuration` (`server/sched.go:1841-1846`: "a model that is still loading may have
  the zero value") — still with no obvious state marker.
- Ollama does know the state internally: it polls llama-server's `/health` and maps
  `{"status":"loading model"}` (also the error-message variant) to `ServerStatusLoadingModel`
  (`llm/llama_server.go:1232`, `1264-1288`). That enum is consumed by `WaitUntilRunning`
  (`:1393`) and is never serialized by `/api/ps` or the list endpoints; the `ServerStatusResponse`
  struct with `status`/`progress` (`llm/server.go:150-153`) is the internal health shape, not an
  exported API. (`ProgressResponse.status` belongs to pull/create progress streams, not ps/list.)
  `/api/status` is unrelated: it reports cloud sign-in status only (`server/routes.go:2362`,
  `:2639-2643`).

Practical summary: during load, `/api/ps` shows either the previous model set (200) or, briefly,
stalls; it never says "loading". Empty `models` is ambiguous between "nothing loaded" and
"first model still loading".

## F3 — 503 does exist, but only for queue pressure or cloud state, not model loading

- The scheduler rejects excess pending requests with `ErrMaxQueue`:
  `server/sched.go:129` — "server busy, please try again.  maximum pending requests exceeded".
  `handleScheduleError` maps that to 503 (`server/routes.go:3589-3590`); cloud auth also uses 503
  with `"account unavailable"` (`server/routes.go:2722`).
- Docs `/faq` corroborate: "it will respond with a 503 error indicating the server is overloaded"
  (OLLAMA_MAX_QUEUE), and "all new requests will be queued until the new model can be loaded" —
  loading is handled by blocking/queuing client requests, not by a loading HTTP status.
- Docs `/api/errors` lists 200/400/404/429/500/502 only; 503 is not in the documented status set
  (it is an overload behavior described in the FAQ).

## Implications for the probe (advice only)

- Do not generalize llama.cpp's `503 {"error":{"message":"Loading model",…
  "unavailable_error",… "code":503}}` to Ollama. Ollama's list endpoints never return 503, and an
  Ollama 503 during a load window can only be the queue-full body above (different shape/text) or
  cloud unavailability.
- `/v1/models` on Ollama is a disk inventory, not readiness: an installed model is listed (200)
  whether it is cold, loading, or ready. Treating list presence as a loading signal is a false
  negative; treating its mere 200 as ready is also wrong.
- `/api/ps` carries no status, progress, or `loading` field. A specific model's absence from
  `models` (or an empty `models` array on a single-model host) is the only loading-adjacent signal,
  and it is ambiguous with "not loaded at all"; the endpoint can also block briefly on `refMu`
  during the load-to-loaded transition [INFERENCE].

## Confidence

- High (docs + tagged source, v0.40.6) for: route bindings, handler status codes, response schemas,
  manifest-only list construction, internal `ServerStatusLoadingModel` mapping, and 503 causes.
- [INFERENCE] for exact `/api/ps` timing/blocking during load; no live server was run (read-only
  seat, no port opened, no lane measurement).
- No tools installed or upgraded; nothing written outside this report.
