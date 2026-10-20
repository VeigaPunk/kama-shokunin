## Coverage map — round 16 additions (2026-10-20)

Appended rather than inserted, so no existing line moves (`QUALITY.md` KQ7). Each row is admitted only when its file exists at the exact path below; if a file is absent at integration, its row is omitted and the omission is recorded in the round lesson.

| Entry | Covers | Round |
|---|---|---|
| `knowledge/llamacpp-loading-lifecycle.md` | llama.cpp loading-state lifecycle at pinned revisions b11755 (`704366d76`) and c0fd7862: the pre-ready 503 `Loading model` envelope, the `/health` documentation, the single-model `update_meta`-before-ready ordering, and the sleep and router-mode scope limits; documentation at a revision pin, not a live responder | 16 |
| `lessons/round-16.md` | round-16 gate decisions on the exact loading-envelope rule and rejected widenings, mined mistakes, and the measured results as recorded there; calibration claim only | 16 |

## Frontier disposition — round 16 (2026-10-20)

**C1 (calibration).** `tools/kama-probe.sh` grades a pre-ready llama.cpp server as `MODEL_LOADING` (reason `llamacpp-loading`, drift true) only when `GET /v1/models` returns HTTP 503 and the body is a JSON object whose `error` object has `message` "Loading model", `type` "unavailable_error", and integer `code` 503 (`tools/kama-probe.sh:426-445`, branch at `:501-506`; sha256 `d0d48d8d…`). Other top-level keys are ignored. Every other 503 body and every non-503 status keeps its prior verdict, including `no slot available` (`/slots` with `fail_on_no_slot`, `tools/server/server-context.cpp:5395-5396` at b11755). The predicate fails closed to the prior verdict when `python3` is unavailable. Admission of this change rests on the L1 red/green stub matrix against the frozen probe, with positive controls, not on this README.

The source basis is the pre-routing middleware, which answers every non-frontend path with the envelope while `is_ready` is false (`tools/server/server-http.cpp:307-328` at b11755; `:308-320` at c0fd7862; `:312` "no endpoints are allowed to be accessed when the server is not ready"). In single-model mode `routes.update_meta(ctx_server)` runs before `is_ready.store(true)` at both pins (`server.cpp:514-515` at b11755; `:495-496` at c0fd7862). Consequently the sentence "The `meta` field can be `null` (for example, while the model is still loading)" (`tools/server/README.md:1258` at b11755) is not observable through single-model `/v1/models` at either pin; the revisions do not skew on it. Router mode is not covered by this statement and is not measured.

Correction owed to `knowledge/served-identity-crosswalk.md`: its statements that a server "can answer while that model is still loading", the nullable-`meta` premise, and "can even be observed mid-load" are overreach for single-model mode. The historical bytes stay unchanged; an appended note carries the correction and both pins.

**C2 (operability).** A lane-owned ephemeral llama.cpp b11755 fixture on an unregistered loopback port exercises the documented lifecycle surfaces against a real runtime, then tears down and proves the port closed. Admission of this claim rests on a validated receipt and an independent process and port check, not on this README. The fixture supports the mechanism only. It cannot evidence registered-consumer health or served-model identity: its served id is the caller's own `--alias`, and llama.cpp reports no model digest. It retires the "parser evidence, not runtime integration" qualifier for llama.cpp only.

**Frontier items.**

- Stale anchors (`corpus/README.md:68-70`): advanced for llama.cpp by the correction above, once appended.
- Declared-vs-served context size (`:71-72`; gap `:63`): open. The fixture passes `--ctx 256` as launch argument only; no `n_ctx` reconciliation or declared consumer is involved, and the snapshot schema is unchanged.
- Non-author admit/reject sample (`:73-74`): open. `QUALITY.md` criteria headers still read "author-appended; no outside review yet".
- Operator and integrator prerequisites (`:75-78`): open. The fixture proves a lane-owned runtime can be acquired, launched, probed and torn down without a unit, timer, config write or registered port. It does not dispose of any operator serving runtime.
- Registered consumers: not re-measured in this round. Their last admitted state is the 2026-10-14 census: three `DEAD` rows (`corpus/knowledge/consumer-registry.md:70-75`, "Neither port answers."). The fixture is not evidence of any consumer's health.
- Sleeping (`--sleep-idle-seconds`) and router mode: `[INFERENCE]` only. Source shows that `/health` and `/v1/models` do not return the loading envelope during sleep and that router `is_ready` is set before any model loads (`server-context.cpp:5288-5298`, `:5725-5730`; `server.cpp:440-441`, `:460`). A probe `data[]` check could then pass on cached or catalog entries, which is a residency-blind identity pass. The C2 probe runs only after `/health` returns 200, so the round cannot measure either verdict.
- Other engines (vLLM, SGLang, Ollama): open. Not installed or measured. The round-10 matrix records vLLM `/health` as 503 only on engine death and Ollama as having no documented health route (`corpus/knowledge/runtime-health-surface-matrix.md:8`, `:15`; documentation only).
- Verdict vocabulary parity: open. `registry/endpoint-consumers.tsv:32` lists the six pre-round verdicts and omits `MODEL_LOADING`; `SKILL.md:11-13` does the same. Until those surfaces are updated or the deferral is recorded in the round lesson, this section does not assert a shared vocabulary.

### Admission gate for this section

This section is appended only when all of the following hold. Otherwise the round is recorded as not admitted, and this section is replaced by a single not-admitted statement naming the blocking gate.

1. `tools/kama-probe.sh` differs from the frozen `93ee4302…` and L1's stub matrix is green on the repaired probe and red on the frozen one, including positive controls.
2. The C2 receipt validates and an independent process and port check shows no survivor.
3. The crosswalk correction above is appended with both pins and the `update_meta` ordering.
4. The b11755 pin is recorded in `corpus/SOURCES.md` as a new row or appended supplement, with `S001` unchanged.
5. Verdict vocabulary is updated on every live surface listed above.
6. The coverage-map files exist at the exact paths named.

### Sources opened this session (access date 2026-10-20)

| Source | URL or path | Location | Located quote (≤25 words; verbatim except markdown) |
|---|---|---|---|
| server-http.cpp, c0fd7862 | https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/server-http.cpp | `:308-320` | `if (!is_ready.load()) {`; `{"message", "Loading model"},` |
| server.cpp, c0fd7862 | https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/server.cpp | `:495-496` | `routes.update_meta(ctx_server);` then `ctx_http.is_ready.store(true);` |
| server-http.cpp, b11755 | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp | `:307-328` | `// no endpoints are allowed to be accessed when the server is not ready` (`:312`) |
| server.cpp, b11755 | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | `:440-441`, `:460`, `:514-515` | `starting server in router mode. models will be automatically loaded on-demand`; `routes.update_meta(ctx_server);` then `ctx_http.is_ready.store(true);` |
| server-context.cpp, b11755 | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | `:5288-5298`, `:5395-5396`, `:5725-5730` | `// error and loading states are handled by middleware` (`:5289`); `format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE)` (`:5396`); `if (queue_tasks.is_sleeping()) {` (`:5728`) |
| README.md, b11755 | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md | `:479-490`, `:987`, `:1993`, `:2026-2028`, `:2337-2345` | `Explanation: the model is still being loaded.` (`:487`); `If query param ?fail_on_no_slot=1 is set, this endpoint will respond with status code 503 if there is no available slots.` (`:987`); `Any new incoming task will automatically trigger the model to reload.` (`:2337`) |
| GitHub API tag | https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755 | JSON `object.sha` | `"sha": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"` |
| probe predicate and branch | /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh | `:426-445`, `:501-506` | `if err.get("message") == "Loading model" and err.get("type") == "unavailable_error"` (`:440`); `if [ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then` (`:501`) |
| vocabulary, registry | /home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv | `:32` | `MODEL_OK \| MODEL_MISMATCH \| FOREIGN_SERVICE \| UNAUTHORIZED_SERVICE \| DEAD \| NOT_HTTP` (six verdicts, no `MODEL_LOADING`) |
| vocabulary, SKILL | /home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md | `:11-13` | `MODEL_OK` `MODEL_MISMATCH` `FOREIGN_SERVICE` (six verdicts listed, no `MODEL_LOADING`) |
| consumer census | /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/consumer-registry.md | `:70-75` | `Neither port answers.`; `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2` |
| engine matrix, round 10 | /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/runtime-health-surface-matrix.md | `:8`, `:15` | `503 only on EngineDeadError; no model-loaded flag in the contract` (vLLM); `Ollama's opened pages document no dedicated health route at all.` |
