# KamaExecHealth source fragment — round 10 (2026-10-19)

Rows opened by KamaExecHealth for `corpus/knowledge/runtime-health-surface-matrix.md`. All opened this session on 2026-10-19; web docs only, no endpoint contacted.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | llama.cpp server README — https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | docs | A | llama.cpp HTTP API semantics | §GET `/health` and §GET `/v1/models` @ commit c0fd78626405c6d9b934efef0ec7291fcc20e3d6 (2026-10-17) | `/health` is a load-state surface (503 loading, 200 loaded) and model `id` defaults to the `-m` path unless `--alias` is set. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S002 | vLLM Online Serving — https://docs.vllm.ai/en/stable/serving/online_serving/ | docs | A | vLLM server route inventory | §Instrumentator APIs, stable docs page footer 2026-10-08 | `/health`, `/v1/models`, `/load`, `/version`, `/metrics` are distinct instrumentator surfaces. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S004 | vLLM health API — https://docs.vllm.ai/en/stable/api/vllm/entrypoints/serve/instrumentator/health/ | docs | A | vLLM `/health` handler semantics | `health(raw_request)` source block, stable docs page footer 2026-10-17 | `/health` calls engine `check_health()` and render-only servers always return 200. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S006 | SGLang Native APIs — https://docs.sglang.io/docs/basic_usage/native_api | docs | A | SGLang native server routes | §Health Check, §Get Model Info, §Get Server Info (page opened 2026-10-19, unversioned docs) | `/health` and one-token `/health_generate` are separate checks; model metadata lives on `/get_model_info`. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S009 | Ollama API Introduction — https://docs.ollama.com/api/introduction | docs | A | Ollama API base URLs | §Base URLs (page opened 2026-10-19, unversioned docs) | Local native `/api` and OpenAI-compatible `/v1` roots at `localhost:11434` are distinct surfaces; no health route appears on this page. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S010 | Ollama OpenAI compatibility — https://docs.ollama.com/api/openai-compatibility | docs | A | Ollama OpenAI-compatible surface | §Endpoints `/v1/models` (page opened 2026-10-19, unversioned docs) | Ollama supports a subset of the OpenAI API; `/v1/models` notes `created` and `owned_by` semantics; no health route appears on this page. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
| S017 | Kubernetes Liveness, Readiness, and Startup Probes — https://kubernetes.io/docs/concepts/workloads/pods/probes/ | docs | A | Probe lifecycle vocabulary | §Types of probe, §Caution under Liveness probe; page modified 2026-06-30 | Startup, liveness and readiness probes answer initialization, restart and traffic-admission questions; bad liveness checks cause cascading restarts. | mined | 2026-10-19 | 90d | corpus/knowledge/runtime-health-surface-matrix.md |
| S020 | SGLang v0.5.22 release — https://github.com/sgl-project/sglang/releases/tag/v0.5.22 | docs | A | SGLang current release facts | §Parallelism & Disaggregation, release tag v0.5.22 @ commit baa9bef released 2026-10-19 (latest release, verified via releases/latest redirect) | Versioned release notes carry a health-check routing fix; a release note is not a local defect observation. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |

## Gate blocks

### S001
- URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md (rendered path https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
- accessed: 2026-10-19
- quote: "Explanation: the model is successfully loaded and the server is ready."
- location: §GET `/health` response format, 200 branch
- revision: latest commit touching the file per the GitHub commits page is c0fd78626405c6d9b934efef0ec7291fcc20e3d6 dated 2026-10-17 (Commits API returned 403, so the commits HTML page was used)

### S002
- URL: https://docs.vllm.ai/en/stable/serving/online_serving/
- accessed: 2026-10-19
- quote: "`/health` - Health check"
- location: §Instrumentator APIs → Basic APIs list
- revision: `en/stable` docs build; page footer date 2026-10-08

### S004
- URL: https://docs.vllm.ai/en/stable/api/vllm/entrypoints/serve/instrumentator/health/
- accessed: 2026-10-19
- quote: "Render-only servers have no engine; they are always healthy."
- location: `health(raw_request)` source block comment
- revision: `en/stable` API reference; page footer date 2026-10-17

### S006
- URL: https://docs.sglang.io/docs/basic_usage/native_api
- accessed: 2026-10-19
- quote: "`/health_generate`: Check the health of the server by generating one token."
- location: §Health Check bullet list
- revision: live docs site, unversioned page; opened on date

### S009
- URL: https://docs.ollama.com/api/introduction
- accessed: 2026-10-19
- quote: "Ollama's API isn't strictly versioned, but the API is expected to be stable and backwards compatible."
- location: §Versioning paragraph (Base URLs table at §Base URLs)
- revision: live docs site, unversioned page; opened on date

### S010
- URL: https://docs.ollama.com/api/openai-compatibility
- accessed: 2026-10-19
- quote: "Ollama supports a subset of the OpenAI API"
- location: opening paragraph; endpoint details under §Endpoints `/v1/models`
- revision: live docs site, unversioned page; opened on date

### S017
- URL: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ (301s to canonical https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- accessed: 2026-10-19
- quote: "Liveness probes determine when to restart a container."
- location: §Liveness probe under §Types of probe
- revision: page `meta-article:modified_time` 2026-06-30; canonical URL recorded

### S020
- URL: https://github.com/sgl-project/sglang/releases/tag/v0.5.22
- accessed: 2026-10-19
- quote: "[Fix][DP] Prevent health checks from perturbing user request routing"
- location: §Parallelism & Disaggregation first bullet (PR #35721)
- revision: tag v0.5.22 @ commit baa9bef, released 2026-10-19; confirmed as current latest release via https://github.com/sgl-project/sglang/releases/latest redirect to this tag

## Leads (unopened)

- Ollama metrics/health surface — a health or Prometheus endpoint was not found in the two opened Ollama pages (S009, S010); absence here is a sweep result, not a claim of non-existence. Unopened: https://docs.ollama.com/api/usage
- GitHub REST API for llama.cpp file history — `api.github.com/repos/ggml-org/llama.cpp/commits?path=tools/server/README.md` returned HTTP 403 this session; the HTML commits page supplied the pin instead.
