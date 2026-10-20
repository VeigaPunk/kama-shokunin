# Runtime health surfaces are not portable across engines
source: S001 https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md §GET `/health` @c0fd7862; S002 https://docs.vllm.ai/en/stable/serving/online_serving/ §Instrumentator APIs; S004 https://docs.vllm.ai/en/stable/api/vllm/entrypoints/serve/instrumentator/health/ §health(raw_request); S006 https://docs.sglang.io/docs/basic_usage/native_api §Health Check; S009 https://docs.ollama.com/api/introduction §Base URLs; S010 https://docs.ollama.com/api/openai-compatibility §Endpoints; S017 https://kubernetes.io/docs/concepts/workloads/pods/probes/ §Types of probe; S020 https://github.com/sgl-project/sglang/releases/tag/v0.5.22 §Parallelism & Disaggregation
verified-at: 2026-10-19 — vendor/spec docs opened; no local runtime contacted
recheck: on-release — S001 §GET `/health`; S004 `health(raw_request)` source; S006 §Health Check; S009/S010 for a documented Ollama health route; S020 current SGLang release notes

## Claim

One `/health` URL shape does not carry one portable readiness meaning across llama.cpp, vLLM and SGLang — each engine's documented route semantics differ, and Ollama's opened pages document no dedicated health route at all.

## Crosswalk

| Engine | Documented revision | Liveness route | Readiness / loaded meaning | Identity route (separate) | Caveat | S-id |
|---|---|---|---|---|---|---|
| llama.cpp server | tools/server/README.md @ c0fd7862 | `GET /health` (public, `/v1/health` alias) | 503 `unavailable_error` "Loading model" while loading; 200 `{"status": "ok"}` when loaded — the closest to readiness of the set | `GET /v1/models` (`data[].id` = `-m` path, or `--alias`) | 200 proves a model finished loading, not which model; identity still needs the normalized-id check | S001 |
| vLLM | stable online-serving + instrumentator API pages | `GET /health` listed under Instrumentator APIs | Handler calls engine `check_health()`, 503 only on `EngineDeadError`; no model-loaded flag in the contract | `GET /v1/models`; `/load` and `/version` are separate surfaces | Render-only servers have no engine and return 200 unconditionally — a passing `/health` may not even reach an engine | S002, S004 |
| SGLang | native_api docs page; v0.5.22 release | `GET /health` | `/health_generate` "Check the health of the server by generating one token" — deeper check, but it is a generation request | `GET /get_model_info` (`model_path`, `weight_version`, `model_type`, `architectures`); `/server_info` for limits | `/health_generate` issues real generation; kama's SKILL forbids generation requests as identity tests, so it is documented but out of scope for kama probes. v0.5.22 §Parallelism & Disaggregation: "Prevent health checks from perturbing user request routing" | S006, S020 |
| Ollama | docs.ollama.com (API stated stable, unversioned) | No dedicated health route in the two opened pages | N/A documented — absence in opened pages is not a claim of non-existence | `/api/tags` (available models), `/api/ps` (running models); OpenAI-compat `/v1/models` | Distinct `/api` and `/v1` roots; the OpenAI-compatible surface is an explicit subset | S009, S010 |
| Kubernetes (vocabulary) | probes doc, modified 2026-06-30 | liveness probe → restart decision | readiness probe → traffic admission; startup probe gates both during initialization | n/a — not a model server | Lifecycle vocabulary only; a non-Kubernetes local server inherits none of these semantics | S017 |

## What this does not establish

No local runtime was contacted: nothing here says any engine is installed, running, or conforms to its docs today (KQ4). Ollama's missing health row means "not found in the two opened pages", not "no such route exists". Kubernetes probe categories are borrowed vocabulary for slow model loads, not a policy this lane applies. Routing/gateway health dispatch is kumitate's surface; model quality is kengaku's.

## kama use

`kama-probe.sh check` stays metadata-only: the identity decision uses `GET /v1/models` plus normalized id comparison (per `endpoint-identity.md`); `/health` remains a lightweight liveness signal whose body must not be read as identity. This matrix records, per engine and documented revision, why an engine other than llama.cpp could answer `2xx` on a health path and still never satisfy `MODEL_OK` — and why SGLang's deeper `/health_generate` is documented here but excluded from kama probes by the no-generation-request rule.

## QUALITY clearance

- KQ1: no current endpoint claim; every row is a documentation statement pinned to revision and section.
- KQ2: pin provenance untouched; no endpoint verdict or effective-URL claim is made.
- KQ3: each anchor names section plus commit SHA, release tag, or page-modified date; recheck cadence declared.
- KQ4: docs are not integration; fixtures/runtime claims explicitly out of scope above.
- KQ5: no service started, no request sent, no credentials read; external remediation stays operator-owned.
- KQ6: every engine statement names engine + documented revision (commit, release or dated page) + section and cites an opened `SOURCES.md` row (tier A for its scope; no C-tier row supports this entry); never asserted as local runtime fact.
- KQ7–KQ10: not a correction entry (KQ7); no privilege-bounded verdict (KQ8); no negative claim — absences are stated as 'not documented in the opened page', not as non-existence (KQ9); no census or probe run by the entry's author (KQ10).

## Cited sources

S001 llama.cpp server README §GET `/health`, §GET `/v1/models` (commit c0fd7862, opened 2026-10-19); S002 vLLM Online Serving §Instrumentator APIs; S004 vLLM `health(raw_request)` source block; S006 SGLang Native APIs §Health Check, §Get Model Info, §Get Server Info; S009 Ollama API introduction §Base URLs; S010 Ollama OpenAI compatibility §Endpoints; S017 Kubernetes Liveness, Readiness, and Startup Probes §Types of probe (canonical path `/docs/concepts/workloads/pods/probes/`); S020 SGLang v0.5.22 release notes §Parallelism & Disaggregation.

## Correction — round 11 (reviewed 2026-10-20 UTC)

The Ollama row at line 17 already named `/api/tags` versus `/api/ps`; round 11
does not claim that distinction as new coverage. Its S009/S010 citations support
the base roots and compatibility subset, not the native inventory semantics.
The native routes are grounded in reopened S011 (`GET /api/tags`, 200 description
“List available models”) and S012 (`GET /api/ps`, 200 description “Models currently
loaded into memory”). S031's same-page remote-entry correction grounds
`remote_model` and `remote_host`: [INFERENCE] available inventory is not proof
of local weights.

The llama.cpp row at line 14 must not be generalized to router or sleeping-model
state. S001's pinned README at `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`
documents nullable `/v1/models` `meta` while loading, a separate router
`GET /models` status field, and `/health` as exempt from waking sleeping models.
A successful model-list identity match is not an inference-readiness guarantee.
These are documentation corrections, not observations of a local runtime.

## Correction — round 16 (2026-10-20)

Line 55's "nullable `/v1/models` `meta` while loading" is README text (S001,
re-read at 704366d76 as `S035`, README:1258). In direct single-model mode at
that build the loading window is served by the 503 middleware on every
non-frontend path, `/v1/models` included (`S036`, `S037`). The llama.cpp row at
line 14 is consistent with that code. Engine contrasts gathered this round are
leads, not admitted rows: they cite build-wave advice, not SOURCES rows, so they
do not meet this file's KQ6 bar (line 35) and are not knowledge. vLLM v0.32.0
and TGI v3.3.7 (launcher-managed) do not listen until ready; SGLang v0.5.22
(default warmup) answers `/v1/models` 200 while `/health` is 503, and its ready
`/health` runs a one-token generation, so it is not a cheap liveness probe;
Ollama v0.40.6 `/v1/models` lists available models whatever the load state.
Lead files: `.ufo/waves/round-16/build/advice/` `ScoutVllmStartup.md`,
`ScoutTgiStartup.md`, `ScoutSglangStartup.md`, `ScoutOllamaLoading.md`. None of
these is a runtime observation of the engine.
