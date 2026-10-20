# Scout — llama.cpp router mode vs `kama-probe`'s `/v1/models` identity check

**Roots.** `LANE=/home/vgpnk/Projects/shokunin/kama-shokunin`. `UP=ggml-org/llama.cpp@704366d76`
(<https://github.com/ggml-org/llama.cpp/blob/704366d76/…>). Citations of `tools/server/…`,
`common/…`, and `tools/server/README.md:<n>` are `UP`; `tools/kama-probe.sh`,
`registry/…`, `tests/…` are `LANE`.

**Probe revision read.** Working tree sha256 `d0d48d8d…db8fe` (already carries C1's
`MODEL_LOADING` patch). Frozen baseline `93ee4302…2cd64` is line-shifted but logically
identical on the identity path (frozen `normalize_id` :371, `fetch /v1/models` :418,
`case "$expected"` :487).

**Answer in one line.** A router answers `GET /v1/models` with a **200 catalog of every
model it knows** (`id` + `status.value`), so the probe reads catalog membership as
"served"; every non-`loaded` state — loading, unloaded, sleeping, downloading, incomplete,
failed — grades `MODEL_OK`.

## 1. Observed — what a router puts on `/v1/models`

- **F1. Same handler as `/models`, not a proxy.** `UP tools/server/server.cpp:269`
  `routes.get_models = models_routes->get_router_models;` and `:284`
  `ctx_http.get ("/v1/models", … routes.get_models));`.
- **F2. The handler always answers 200 over the whole catalog.** `UP
  tools/server/server-models.cpp:2448-2455` `res_ok(res, { {"data", models_json},
  {"object", "list"},` and `res_ok` is `res->status = 200;` (:2153-2155). There is no
  error/503 branch. The `/models` docs describe the same catalog: `UP
  tools/server/README.md:1995`
  "Listing all models in cache. The model metadata will also include a field to indicate
  the status of the model".
- **F3. Router-only fields per entry: id, aliases, status.** `UP
  tools/server/server-models.cpp:2364-2370` `{"id", meta.name},` `{"aliases",
  meta.aliases},` … `{"status", status},`.
- **F4. Seven status values.** `UP tools/server/server-models.h:56-62`: `"downloading"`,
  `"incomplete"`, `"downloaded"`, `"unloaded"`, `"loading"`, `"loaded"`, `"sleeping"`.
- **F5. IDs are router names, not child aliases.** Cache: `UP common/preset.cpp:356`
  `preset.name = model.to_string();` (repo tag, e.g. `ggml-org/gemma-3-4b-it-GGUF:Q4_K_M`).
  `--models-dir` subdirectory: `UP common/preset.cpp:435` the name is the **directory**
  (`scan_subdir(entry.path(), …filename())`). Top-level file: `UP common/preset.cpp:450`
  `string_replace_all(name, ".gguf", "");`.
- **F6. Router is "ready" at listen time, so the loading envelope is unreachable.** `UP
  tools/server/server.cpp:460` `ctx_http.is_ready.store(true);` (single-model sets it only
  after load, :515; no reset exists). The 503 middleware `UP tools/server/server-http.cpp:307-325`
  (`{"message", "Loading model"}`) therefore never fires on a router — including with zero
  models and while children load.
- **F7. Empty catalog is real and is 200 + `data: []`.** `UP tools/server/server-models.cpp:990`
  `"  no models found on the system (visit https://llama.app/models for suggestions)"`;
  the response builder adds nothing when `mapping` is empty.
- **F8. Docs are ambiguous in a way a probe author can over-read.** `UP
  tools/server/README.md:1258` (single-model API section) "The returned list always has one
  single element."; `:2026` "the info from `/v1/models` is forwarded to router's
  `/v1/models`". In code that "forwarding" is a metadata merge into the catalog entry
  (`UP tools/server/server-models.cpp:2411` `// merge with loaded_info from the child process
  if available`), while the endpoint itself returns the whole catalog (F1). Read as a proxy
  shape, 2026 predicts a single-model list that does not exist.

## 2. Observed — how the probe consumes that body

- **P1.** One unparameterised, unauthenticated GET: `LANE tools/kama-probe.sh:452`
  `fetch "$port" "/v1/models" "m$port"`.
- **P2.** Gate = 2xx AND a `data`/`models` array: `:518` `body_has_model_array`,
  `:520` `if [ "$is2" -eq 1 ] && [ "$has_models" -eq 1 ]`. `data: []` passes.
- **P3.** IDs come from `:522` `ids=$(served_ids "$FBODY")` with precedence `:36-42`
  `data[].id -> models[].id -> …`; the router body has only `data[]`, so only router
  names are compared.
- **P4.** Wildcard short-circuits before any id: `:528-530` `''|'*'|'-')` →
  `C_VERDICT=MODEL_OK; C_REASON='expected-wildcard'`.
- **P5.** Match: `:533` `model_matches "$ids" "$expected"`; `:376`
  `s=${s##*/}; s=${s%.gguf}` drops the directory and one trailing `.gguf`; exact,
  case-sensitive; **any** id may match.
- **P6.** The classifier block (`:449-565`) never reads `status`, `aliases`,
  `architecture`, or merged `loaded_info`.
- **P7.** The only corroboration appended to MODEL_OK is `/health` (`:546-548`), and on a
  router that is unconditional: `UP tools/server/server-context.cpp:5297`
  `res->ok({{"status", "ok"}});`.

## 3. Derived verdict table

[INFERENCE: derived statically from §1–§2; not measured — measurements belong to L1.]

| Router state (`/v1/models` = 200 + `data[]`) | `--expect <model>` | `--expect -` |
|---|---|---|
| `loaded` | MODEL_OK `matched` | MODEL_OK `expected-wildcard` |
| `loading` | MODEL_OK `matched` | MODEL_OK |
| `unloaded` (autoload on) | MODEL_OK | MODEL_OK |
| `unloaded` + `--no-models-autoload` | MODEL_OK | MODEL_OK |
| `sleeping` | MODEL_OK | MODEL_OK |
| `downloading` (no file on disk) | MODEL_OK | MODEL_OK |
| `incomplete` (partial download, no instance) | MODEL_OK | MODEL_OK |
| `unloaded` + `failed:true` (child crashed) | MODEL_OK | MODEL_OK |
| empty catalog (`data: []`) | MODEL_MISMATCH `unresolvable-id` | MODEL_OK `expected-wildcard` |
| `--api-key` set (probe sends none) | UNAUTHORIZED_SERVICE `http-401` | same |
| router not listening | DEAD `connection-refused` | same |

## 4. Misgrade risks, ranked

- **R1. Catalog read as residency — false green, high.** `id` is present whether or not an
  instance exists (F2–F4); the probe still labels the result `matched` / `served_model`
  (`:522-525`, `:534-535`). A consumer pointed at a router therefore reconciles against a
  name list, not a live model.
- **R2. Loading split-brain vs C1 — false green, high.** A loading child behind a router
  yields 200 + `status.value:"loading"` → MODEL_OK; a direct child yields the 503 envelope
  → MODEL_LOADING (`LANE tools/kama-probe.sh:501-507`). Same physical state, opposite
  verdicts.
- **R3. Downloading/incomplete pass with zero model bytes — false green, high in ops.**
  `UP tools/server/README.md:2097` "for \"downloading\" state, there can be multiple files
  be downloading in parallel" and `:2112` "\"incomplete\" status, without an instance";
  entries are emitted at `UP tools/server/server-models.cpp:2427-2444`.
- **R4. Crashed-at-load model passes — false green, high.** `UP tools/server/server-models.cpp:2358-2361`
  `if (meta.is_failed()) { status["exit_code"] = …; status["failed"] = true; }`; the entry
  keeps its `id`, so `is_failed` (`server-models.h:107`) is invisible to the probe.
- **R5. `--no-models-autoload` false green — medium.** A request for an unloaded model then
  fails: `UP tools/server/server-models.cpp:2175-2178` `if (!models_autoload && !meta->is_running())`
  → `"model is not loaded"`. Probe still says MODEL_OK. (Autoload is on by default:
  `README.md:1993`.)
- **R6. Empty catalog + wildcard = MODEL_OK — high on this lane.** The lane's only llama
  row expects `-`: `LANE registry/endpoint-consumers.tsv:35`; `:528-530` then short-circuits,
  so a router with zero models passes the gate.
- **R7. Empty catalog + concrete expect = `unresolvable-id` — labelling, medium.** Nothing
  is "unresolvable"; the list is empty (`:522-525`, `:535`). The reason reads as a bad id.
- **R8. Aliases structurally invisible — false red, medium.** Routing resolves aliases
  (`UP tools/server/server-models.cpp:2174` `// resolve alias to canonical model name`) and
  exposes them at `:2365`, but the probe reads only `data[].id`. A consumer addressing an
  alias is graded `served-id-mismatch`. The matrix pins this as intended behaviour:
  `LANE tests/probe-verdicts/ReadyControls.json:178` ("never falls through to
  models[].name/.model or aliases[]") with the expected mismatch at `:196-197`.
- **R9. ID-form mismatch — false red, medium.** Worked example [INFERENCE from `:376`]:
  router cache id `…/gemma-3-4b-it-GGUF:Q4_K_M` normalises to `gemma-3-4b-it-GGUF:Q4_K_M`,
  while an expected written as `gemma-3-4b-it-Q4_K_M.gguf` normalises to
  `gemma-3-4b-it-Q4_K_M` → mismatch for one and the same model.
- **R10. Owner collapse — false green, low.** `s=${s##*/}` (`:376`) maps `a/foo:Q4` and
  `b/foo:Q4` to one key; with any-of matching (`:533-534`) a multi-model catalog can satisfy
  the expected id from a different repo. [INFERENCE]
- **R11. Catalog churn pollutes DELTA — noise, low.** `C_SERVED` is the whole catalog joined
  by commas (`:522-525`); snapshots compare `served_model` (`:966-975`, `:1003-1011`), so an
  unrelated model appearing mints a transition. It does not gate (`drift` comes only from
  verdict/file_match, `:861-862`) but it degrades the bounded drift window.
- **R12. `/health` corroboration is unfalsifiable on a router — low.** `UP
  tools/server/server-context.cpp:5297` is unconditional, so evidence reads "healthy" with
  zero models loaded.
- **R13. Matrix has no router-realistic shape — coverage, medium.** The two multi-entry
  controls (`LANE tests/probe-verdicts/ReadyControls.json:176-198`, `:199-229`) add an
  Ollama-style `models[]` array that this router never emits, and neither entry carries a
  `status` object; no test uses `data: []`, and none uses `--expect -`. Today's green matrix
  cannot distinguish a loaded catalog from a download-in-progress catalog.

## 5. Frontier advice (cheap, axis-monotone)

- **A1. Scope C1, do not stretch it.** C1's 503 envelope is a child-process artifact
  (`UP tools/server/server-http.cpp:307-325`) that router mode cannot emit
  (`server.cpp:460`). Record that limit in the C1 artifact so "loading llama.cpp is drift"
  is not read as router coverage. Harm: none.
- **A2. Cheapest calibration win: surface the status already fetched.** When
  `data[].status.value` exists, append it to evidence (e.g. `router-status=unloaded`).
  No verdict, vocabulary, or stub-schema change (`body_json` already expresses it); it makes
  R1/R3/R4 visible per row. This is the highest calibration gain per line.
- **A3. If a router verdict is ever added, name it for catalog semantics**
  (`MODEL_CATALOG_ONLY` / `catalog-unloaded`) and keep `MODEL_LOADING` exclusively for the
  exact 503 envelope. Overloading either would make direct and router rows indistinguishable.
- **A4. Do not claim identity coverage while the row expects `-`.** `registry/endpoint-consumers.tsv:35`
  passes `--expect -`, which short-circuits at `:528-530`; a router that "passes the probe"
  proves liveness only. A concrete expected is a prerequisite — an L1/registry decision, not
  this seat's.
- **A5. Router readiness has exactly one GET surface.** There is no `GET /models/{id}`
  (only `/models`, `/models/sse`, POST load/unload, DELETE), so `status.value` in the body
  already fetched is authoritative. `/metrics` and `/props` require `?model=`
  (`UP README.md:1135`, `:1988`) and are not router-wide liveness probes.
- **A6. If a router family is ever added, four stubs suffice — no schema change:** loaded,
  loading (id present + `status.value:"loading"`), empty (`data: []`, tested with both a
  concrete expect and `-`), and incomplete (partial download). All are expressible as
  `body_json`. A stub cannot prove autoload behaviour (R5); that needs a real router, which
  no lane tool launches at read time — `tools/kama-llamacpp-live.py` is absent and C2's
  pinned-GGUF launcher is single-model.
- **A7. Keep the any-of match.** `:533`'s iterate-all is the right router primitive and the
  matrix already pins it (`ReadyControls.json:202`); do not narrow to `data[0]`.

## 6. Limitations

- Read-only static analysis: no router launched, no probe invocation, no lane gate run
  (measurement belongs to L1).
- Line numbers are the working probe `d0d48d8d…`; the frozen `93ee4302…` baseline carries
  the same identity logic at frozen `:371` / `:418` / `:487`.
- Upstream quotes are from the same commit's `tools/server/README.md` (119,661 bytes,
  HTTP 200) and source files fetched at `704366d76`.
- The `--api-key` row in §3 is statically verified, not measured: `UP
  tools/server/server-http.cpp:251-258` makes only `/health`, `/v1/health` and frontend
  paths public, and the rejected path sets `res.status = 401` (`:290`).
- No installs or upgrades were made; the only file written is this report.
