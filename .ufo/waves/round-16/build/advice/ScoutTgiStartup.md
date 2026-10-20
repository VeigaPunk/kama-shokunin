# ScoutTgiStartup — TGI `/health` and `/info` during warmup/loading

Seat: leaf scout, read-only. No server launched, no lane gate/harness run, no endpoint
probed; findings are the pinned source and pinned docs. No installs.

## Pin

- **Hugging Face text-generation-inference v3.3.7**, tag commit
  `dfb3fbe78e0d1d69251bd33065591c61bafdfaa8` (tag date 2025-12-18). Checked
  2026-10-20: `releases/latest` redirects to `releases/tag/v3.3.7`, and `git ls-remote`
  shows no newer tag (`v3.3.0` … `v3.3.7` are the tail).
  <https://github.com/huggingface/text-generation-inference/releases/latest>
- The lane registry has **no TGI row**: `corpus/SOURCES.md` ends at S034
  (`corpus/SOURCES.md:6-7`, registry rows S001–S034). This pin is therefore
  upstream-only, not corpus-backed, and cannot be cited as a lane source until a row is
  admitted.
- All file:line citations below are at that commit; the durable permalink base is
  `https://github.com/huggingface/text-generation-inference/blob/dfb3fbe78e0d1d69251bd33065591c61bafdfaa8/`.
  Line numbers were read from a sparse checkout of the tag, not from `master`.

## Bottom line

1. **During both weight loading and router warmup, a launcher-managed TGI v3.3.7 binds
   no HTTP port at all.** A client gets TCP connection refused — there is no status code
   to observe. A probe that treats "loading" as a 503 window is describing llama.cpp,
   not TGI.
2. **`/health` is the only dynamic surface.** Once the port is up: `200` with an empty
   body when healthy; `503` `{"error":"unhealthy","error_type":"healthcheck"}` when the
   backend health call fails. That 503 is a **post-start backend-unhealthy** signal,
   never a loading signal.
3. **`/info` is static metadata and 200-only.** It has no readiness gate and no error
   path; it answers from an `Extension<Info>` built before the listener binds.
4. **`/v1/models` is likewise static 200**, so an identity-matched TGI endpoint reads as
   `MODEL_OK`/`MODEL_MISMATCH` even while `/health` is 503.
5. **With `--features kserve`, `/v2/health/ready` always returns 200 `{"live":true}`**
   regardless of backend health — a readiness endpoint that does not check readiness.

## Findings

### F1 — `/health`: exact statuses and body

`router/src/server.rs:230-241`:

> `async fn health(infer: Extension<Infer>) -> Result<(), (StatusCode, Json<ErrorResponse>)>`
> `true => Ok(())`
> `false => Err((`
> `StatusCode::SERVICE_UNAVAILABLE,`
> `error: "unhealthy".to_string(),`
> `error_type: "healthcheck".to_string(),`

- Healthy: **HTTP 200, empty body** (handler returns `()`; the utoipa entry documents
  `(status = 200, description = "Everything is working fine")`, `server.rs:221-226`).
- Unhealthy: **HTTP 503**, JSON object with exactly the two string fields `error` and
  `error_type` (`ErrorResponse`, `router/src/lib.rs:1516-1519`), i.e.
  `{"error":"unhealthy","error_type":"healthcheck"}`. No `code` field, no nested
  `error` object.
- No third status: `Infer::health()` collapses backend errors into `false`
  (`router/src/infer/mod.rs:357-364`), so a gRPC failure yields 503, not 500.

Confidence: high (source).

### F2 — `/health` is dynamic, per request, and probes the shard

Route registration is in the same table as `/info`: `router/src/server.rs:2237-2244`

> `.route("/health", get(health))` `.route("/ping", get(health))` `.route("/", get(health))`

`Infer::health` calls the backend on every request and caches only a boolean
(`router/src/infer/mod.rs:357-364`):

> `.health(self.backend_health.load(Ordering::SeqCst))`

For the v3 backend (`backends/v3/src/backend.rs:105-113`) the branch is meaningful:

> `// Generation is healthy, we only check that the shards can allocate on device`
> `self.client.device_health().await` … `self.client.model_health().await`

`model_health` is explicitly the expensive recovery probe
(`backends/v3/src/client/mod.rs:25-29`):

> `/// Check if a generate server is healthy by doing a forward pass.`
> `/// EXPENSIVE`

and the shard-side Health RPC is not free either
(`server/text_generation_server/server.py:76-79`):

> `if self.model.device.type == "cuda":` `torch.zeros((2, 2)).cuda()`

So `/health` is a real backend check, and a single 503 flips the instance to the
forward-pass recovery path on the next call. Confidence: high for code paths; the
latency/blocking behavior of a hung shard was not measured.

### F3 — `/info`: static metadata, 200 only, no readiness gate

`router/src/server.rs:153-163`:

> `path = "/info"` … `responses((status = 200, description = "Served model info", body = Info))`
> `async fn get_model_info(info: Extension<Info>) -> Json<Info> {`
> `Json(info.0)`

The handler cannot return an error and does not consult `Infer`. Body fields are
`model_id`, `model_sha`, `model_pipeline_tag`, the router limits, `router`, `version`,
`sha`, `docker_label` (`router/src/lib.rs:261-301`). It is constructed from Hub/tokenizer
metadata, not from loaded weights (`router/src/server.rs:2122-2143`).

Consequence: `/info` is **not a readiness surface**. At runtime, after a shard failure,
`/info` stays 200 while `/health` is 503. Confidence: high.

### F4 — Auth boundary: `/health`, `/info`, `/v1/models` bypass `--api-key`

`router/src/server.rs:2213-2235` applies the bearer check only to `base_routes`:

> `base_routes = base_routes.layer(axum::middleware::from_fn(auth))`

Then `info_routes` is created **after** that (`server.rs:2237-2244`) and merged without
the auth layer (`server.rs:2250-2253`). So with `--api-key`, `/health` remains probeable
(required), but `/info` and `/v1/models` are unauthenticated metadata surfaces.
Confidence: high (source structure).

### F5 — Loading and warmup happen before the HTTP listener exists

The chain is ordered, not concurrent:

1. Shard loads weights, then binds its gRPC UDS —
   `server/text_generation_server/server.py:266,305`:
   `model = get_model_with_lora_adapters(` … `server.add_insecure_port(local_url)`.
2. Launcher marks a shard ready only when that UDS exists —
   `launcher/src/main.rs:1239-1242`:
   `if uds.exists() && !ready {` … `status_sender.send(ShardStatus::Ready)`.
3. `spawn_shards` blocks until every shard reports Ready
   (`launcher/src/main.rs:1664-1690`), and only then the launcher starts the router:
   `launcher/src/main.rs:2294,2317` — `spawn_shards(` … `let mut webserver = spawn_webserver(`.
4. The router connects, fetches shard info, and runs the max-size warmup before it ever
   calls the HTTP server — `backends/v3/src/lib.rs:125-133`:
   `tracing::info!("Warming up model");` `.warmup(`;
   `backends/v3/src/main.rs:151,199` — `connect_backend(` … `// Run server` `server::run(`.
5. `server::run` binds the listener only at the end —
   `router/src/server.rs:2322`:
   `let listener = match tokio::net::TcpListener::bind(&addr).await {`.

Therefore, in the launcher-managed deployment, for the whole of "model loading + warmup",
the router port is unbound. A client sees `ECONNREFUSED`, not 503/500/200. If warmup
fails, the router exits with
`V3Error::Warmup` (`backends/v3/src/lib.rs:134` `.map_err(V3Error::Warmup)?;`;
message at `backends/v3/src/lib.rs:179` “Unable to warmup the Python model shards”)
and the port never opens. Default router port is 3000
(`launcher/src/main.rs:773-774`: `default_value = "3000"`), not 8080.

Confidence: high for v3.3.7 and v2.4.1 ordering (v2.4.1 checkout: same launcher wait at
`launcher/src/main.rs:1409-1430` and same connect-then-run order at
`backends/v2/src/main.rs:164,177`). No live container was run.

### F6 — The pinned docs say the same thing

`docs/source/architecture.md:156,175,179`:

> `Router->>Model Server: warmup(max_input_tokens, max_batch_prefill_tokens, max_total_tokens, max_batch_size)`
> `After these are done, the router is ready to receive generate calls from multiple clients.`

The document frames “ready to receive generate calls” as *after* warmup; it never
documents an HTTP 503 loading state. The API reference itself defers endpoint detail to
the generated OpenAPI (`docs/source/reference/api_reference.md:21`), whose source is the
utoipa annotations quoted in F1/F3.

Confidence: high (pinned docs), with the caveat that this is a prose diagram, not a
normative status table.

### F7 — Observable matrix (v3.3.7)

| State | TCP connect | `GET /health` | `GET /info` | `GET /v1/models` |
|---|---|---|---|---|
| Launcher downloading/converting weights | refused (no listener) | — | — | — |
| Shard loading weights, before UDS | refused | — | — | — |
| Router warmup (after UDS, before bind) | refused | — | — | — |
| Running, backend healthy | accepted | `200`, empty body | `200` static Info | `200` static list |
| Running, backend health call fails | accepted | `503` `{"error":"unhealthy","error_type":"healthcheck"}` | `200` static Info | `200` static list |
| `--features kserve` ready/live routes | accepted | n/a | n/a | `/v2/health/ready` `200` `{"live":true}` |

The “—” cells are no HTTP response by the ordering above (not a live observation):
`kama-probe.sh` maps the connect failure to `DEAD` `connection-refused`
(`tools/kama-probe.sh:452-470`), which is the truthful observation for every load phase.
`/v1/models` is the constant handler at `router/src/server.rs:176-183`
(`async fn openai_get_model_info(info: Extension<Info>) -> Json<ModelsInfo>`).

### F8 — KServe ready/live are unconditional 200s

`router/src/kserve.rs:92-95`:

> `pub async fn kserve_health_ready() -> Json<ReadyResponse> {`
> `let data = ReadyResponse { live: true };`

`kserve_health_live` is identical (`kserve.rs:77-80`), and the per-model ready route is
also a constant (`kserve.rs:151-156`). None of them take `Infer` or call `health()`.
So under the `kserve` feature a Kubernetes-style readiness probe reports ready even when
`/health` would return 503. Confidence: high (source).

### F9 — `/info.version` does not identify the release

At tag v3.3.7 the workspace package version is still the development string —
`Cargo.toml:24`: `version = "3.3.6-dev0"` — and `/info` copies it verbatim:
`router/src/server.rs:2140`: `version: env!("CARGO_PKG_VERSION")`.

The image build instead stamps `GIT_SHA` and `DOCKER_LABEL` as build args
(`.github/workflows/build.yaml:222-224`):

> `GIT_SHA=${{ env.GITHUB_SHA }}`
> `DOCKER_LABEL=sha-${{ env.GITHUB_SHA_SHORT }}${{ env.LABEL_EXTENSION }}`

`/info.sha` and `/info.docker_label` carry those values (`server.rs:2141-2142`), so those,
not `version`, identify the binary. [INFERENCE] for the official image: a build from this
tag with the repo’s Dockerfile reports `version: "3.3.6-dev0"` plus a `sha-<short>`
docker label; the published image was not pulled to confirm.

### F10 — Cross-version check of the handler (not of startup order)

- v2.4.1 `router/src/server.rs:225-237`: same `health` handler, same
  `StatusCode::SERVICE_UNAVAILABLE`, same `{"error":"unhealthy","error_type":"healthcheck"}`.
- v1.4.5 `router/src/server.rs:115-127`: same status and body, but health is read from a
  shared `Extension<Health>` checker rather than a per-request `Infer` call.

Confidence: high for the handler shape; v1.4.5 startup ordering was not checked.

## Calibration relevance (advice for L1, not a verdict)

- **C1’s exact-envelope guard is what keeps TGI out.** TGI’s 503 has a *string* `error`
  plus `error_type`; the repaired probe requires `doc["error"]` to be an object with
  exact `message`/`type`/integer `code` (`tools/kama-probe.sh:426-447`). Structurally,
  TGI cannot match `body_is_llamacpp_loading`, so it falls through to
  `FOREIGN_SERVICE / non-2xx-non-model-http` — the same as before the repair.
- **Do not generalize `MODEL_LOADING` to “any 503”.** TGI has no HTTP loading status at
  all; its only 503 is post-start backend unhealth. If the lane later wants cross-engine
  loading detection, TGI would be evidence *against* a generic 503 rule, not for it.
- **A TGI-shaped 503 is a ready-made negative control** for C1’s stub matrix if L1 wants
  one: `GET /v1/models -> 503` with
  `{"error":"unhealthy","error_type":"healthcheck"}` must stay `FOREIGN_SERVICE`
  `non-2xx-non-model-http` (exit 2) under both the frozen baseline and the repaired
  probe, by code reading (not executed here). I did not edit any matrix file.
- **`/v1/models` is not a health surface in TGI.** It is a constant 200 handler
  (`server.rs:176-183`). The current probe appends `/health` only as evidence and does
  not gate `MODEL_OK` on it (`tools/kama-probe.sh:525-542`), so a running-but-unhealthy
  TGI would grade `MODEL_OK`/`MODEL_MISMATCH` on identity alone. That is a known,
  source-backed gap in the probe’s health semantics — relevant to the operability axis,
  not to C1’s loading claim.
- Frozen baseline reference for that control: `.ufo/waves/round-16/frozen/kama-probe-before.sh`,
  sha256 `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`
  (computed here; it contains no `MODEL_LOADING` token).

## Limitations and remaining unknowns

- No TGI process was started and no capture was taken; every status/body statement is
  read from source at the pinned tag, cross-checked against the pinned docs. Measurements
  belong to L1.
- Behaviour behind a proxy/ingress is out of scope: a fronting proxy can synthesize 503s
  that TGI itself never emits.
- The official container’s `/info.version`, `sha`, and `docker_label` values were not
  observed; F9’s image-level statement is [INFERENCE].
- Only v3.3.7 startup ordering was traced end to end. v2.4.1/v1.4.5 were checked for the
  handler; their launcher/runtime ordering is cited only where read.
- The utoipa annotations were treated as the API contract source; the rendered docs site
  (`huggingface.github.io/text-generation-inference/`) was not fetched.

## Installs

None. No package manager, `uv`, `npx`, or binary install was performed.
