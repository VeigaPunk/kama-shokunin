# SourceLlama — llama.cpp server identity, inventory, and health reconnaissance

Advisory, read-only scout report.
Seat: `SourceLlama` (scout).
Lane: `kama-shokunin`.
Round label: steered 2026-10-19; actual UTC review date: 2026-10-20 (`date -u`, `2026-10-20T02:14:36Z`).
Target: `https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md`.
Scope: Served identity, inventory, running vs. available, and health semantics for C2 crosswalk.
Boundaries: Leaf scout; no edits to corpus, registry, or code; no subagent dispatch; no tool installs performed.

---

## 1. Upstream Source Provenance

- **URL**: `https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md`
- **Upstream HEAD Commit**: `7adf160c411e7a55d9ee75b5d41deb497969dac4`
- **Commit Date**: `2026-10-19T22:23:14Z` (Author: Xuan-Son Nguyen, PR #28277: `server: add --connect, allow p2p access to server outside LAN`)
- **Review Date**: `2026-10-20` UTC (verified via GitHub API commits and raw source fetch)
- **Historical Baseline Commit (S001)**: `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (`2026-10-17T15:20:51Z`)

---

## 2. Served Identity & Inventory Semantics (C2 Grounded Findings)

llama.cpp server exhibits two distinct operational modes that govern served identity and inventory: **Single-Model Mode** (started with `-m / --model`) and **Router Mode** (started without specifying a model).

### 2.1 Health Semantics (`/health` and `/v1/health`)

- **Exact Section**: `## API Endpoints` → `### GET /health: Returns health check result` (lines 477–488)
- **Exact Quote (<=25 words)**:
  > *"This endpoint is public (no API key check). `/v1/health` also works."* (11 words)
- **Second Exact Quote (<=25 words)**:
  > *"Explanation: the model is successfully loaded and the server is ready."* (11 words)
- **Observed Response Codes and Payloads**:
  - `HTTP 503 Service Unavailable`:
    ```json
    {"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}
    ```
    *Meaning*: The model is still being loaded into memory.
  - `HTTP 200 OK`:
    ```json
    {"status": "ok"}
    ```
    *Meaning*: The model is successfully loaded and the server is ready to accept requests.
- **Fields**: `error.code` (int), `error.message` (string), `error.type` (string), `status` (string).
- **Limits & Distinctions**:
  - `/health` is purely a *load-state surface* (503 while loading, 200 when ready).
  - It carries **zero model identity information**: it does not return model name, file path, alias, context window, or hash.
  - Passing `/health` confirms process readiness to accept inference, but cannot verify whether the served model matches consumer expectations.

---

### 2.2 Served Identity in Single-Model Mode (`GET /v1/models`)

- **Exact Section**: `## OpenAI-compatible API Endpoints` → `### GET /v1/models: OpenAI-compatible Model Info API` (lines 1250–1309)
- **Exact Quote (<=25 words)**:
  > *"Returns information about the loaded model. See OpenAI Models API documentation. The returned list always has one single element."* (19 words)
- **Exact Quote on Model ID / Alias (<=25 words)**:
  > *"By default, model `id` field is the path to model file, specified via `-m`. You can set a custom value for model `id` field via `--alias` argument."* (25 words)
- **Observed Response Schema**:
  ```json
  {
    "object": "list",
    "data": [
      {
        "id": "../models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "object": "model",
        "architecture": {
          "input_modalities": ["text"],
          "output_modalities": ["text"]
        },
        "created": 1735142223,
        "owned_by": "llamacpp",
        "meta": {
          "vocab_type": 2,
          "n_vocab": 128256,
          "n_ctx_train": 131072,
          "n_embd": 4096,
          "n_params": 8030261312,
          "size": 4912898304
        }
      }
    ]
  }
  ```
- **Fields**:
  - `object`: string (always `"list"`).
  - `data`: array of objects, containing:
    - `id`: string. Defaults to the literal filepath passed to `-m`; overridden by `--alias <alias>`.
    - `object`: string (always `"model"`).
    - `created`: unix epoch timestamp (integer).
    - `owned_by`: string (always `"llamacpp"`).
    - `architecture.input_modalities`: string array (e.g. `["text"]`, `["text", "image"]`).
    - `architecture.output_modalities`: string array (`["text"]` or `["decisions"]`).
    - `meta`: object of GGUF architecture metadata, or `null` while model is still loading.
- **Limits & Distinctions**:
  - **Single Element Guarantee**: In single-model mode, `data[]` *always* contains exactly one element.
  - **No Availability Concept**: Single-model mode has no notion of "available on disk but not running"; `GET /v1/models` only reports what is loaded.
  - **Alias vs. Tags**:
    - `-a, --alias STRING`: sets model name aliases (used by API and routing).
    - `--tags STRING`: sets model tags ("informational, not used for routing").

---

### 2.3 Available vs. Running Inventory in Router Mode (`GET /models`)

- **Exact Section**: `## Using multiple models` → `### GET /models: List available models` (lines 1990–2131)
- **Exact Quote (<=25 words)**:
  > *"Listing all models in cache. The model metadata will also include a field to indicate the status of the model:"* (19 words)
- **Observed Response Schema**:
  ```json
  {
    "data": [
      {
        "id": "ggml-org/gemma-3-4b-it-GGUF:Q4_K_M",
        "path": "/Users/REDACTED/Library/Caches/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf",
        "status": {
          "value": "loaded",
          "args": ["llama-server", "-ctx", "4096"]
        },
        "architecture": {
          "input_modalities": ["text", "image"],
          "output_modalities": ["text"]
        }
      }
    ]
  }
  ```
- **Model Status Lifecycle (`status.value`)**:
  | `status.value` | Meaning | Running/In-Memory? | Available? | Additional Fields |
  |---|---|---|---|---|
  | `"unloaded"` | Model present in cache/dir/preset, not in RAM | **No** | **Yes** | Optional: `failed: true`, `exit_code: 1` |
  | `"loading"` | Model load is currently in flight | **Transitioning** | **Yes** | `args`: string array |
  | `"loaded"` | Model loaded and actively running | **Yes** | **Yes** | `args`: string array |
  | `"sleeping"` | Model memory paged/sleeping after `--sleep-idle-seconds` | **Dormant** | **Yes** | `args`: string array |
  | `"downloading"`| Background download active | **No** | In-flight | `progress`: object with per-file byte counts |
  | `"incomplete"` | Download paused/interrupted; partial files on disk | **No** | Incomplete | `args: []`, `incomplete_sidecars: [...]` |
- **Router Autoload & Control Routes**:
  - `POST /models/load` (`{"model": "<name>"}`): explicitly triggers model loading.
  - `POST /models/unload` (`{"model": "<name>"}`): unloads model instance from memory.
  - `POST /models`: non-blocking trigger for new Hugging Face model download.
  - `DELETE /models`: removes model and sidecars from cache.
  - `GET /models/sse`: Server-Sent Events stream for real-time load and download progress.
  - Autoload flag: `--models-autoload` (default enabled; disabled with `--no-models-autoload`) loads an available model automatically upon request.
  - Router `/v1/models` forwarding: *"When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`. This includes metadata about the model and the runtime instance."*
- **Limits & Distinctions**:
  - `GET /models` is only available in router mode (not exposed in standard single-model `llama-server -m`).
  - `GET /models` cleanly separates **available** inventory (all cached/configured models) from **running** inventory (`status.value == "loaded"`).

---

### 2.4 Capacity vs. Identity (`GET /slots` and `GET /props`)

- **GET `/slots`**:
  - Exact Section: `### GET /slots: Returns the current slots processing state` (lines 979–982)
  - Exact Quote: *"This endpoint is enabled by default and can be disabled with `--no-slots`. It can be used to query various per-slot metrics"* (21 words)
  - Reports slot-level processing state (`id`, `is_processing`, context token usage).
  - Distinguishes capacity/saturation from health or identity.
- **GET `/props`**:
  - Exact Section: `### GET /props: Get server global properties.` (lines 835–838)
  - Exact Quote: *"By default, it is read-only. To make POST request to change global properties, you need to start server with `--props`"* (20 words)
  - Reports server-wide settings and properties, not model inventory.

---

## 3. Comparison with Existing S-Row (S001) and Drift Analysis

### 3.1 Existing Baseline S-Row

From `corpus/SOURCES.md`:
```markdown
| S001 | llama.cpp server README — https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | docs | A | llama.cpp server HTTP routes: health, model list and metrics exporter | §GET `/health`, §GET `/v1/models`, §GET `/metrics` @ file commit c0fd78626405c6d9b934efef0ec7291fcc20e3d6 (2026-10-17); repo master 4c3c5810 when the metrics section was read | `/health` is a load-state surface (503 loading, 200 loaded); model `id` defaults to the `-m` path unless `--alias`; `/metrics` exists only with `--metrics`. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/serving-metrics-crosswalk.md |
```

### 3.2 Observed Drift & Gaps

1. **Commit / Hash Anchor Drift**:
   - S001 cites file commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (dated `2026-10-17T15:20:51Z`).
   - Current master HEAD commit for `tools/server/README.md` is `7adf160c411e7a55d9ee75b5d41deb497969dac4` (dated `2026-10-19T22:23:14Z`, PR #28277, adding `--connect` / `--connect-code`).
   - *Verdict*: Minor upstream content drift (tunneling flags added); core endpoint documentation remains stable.

2. **Inventory Surface Omission (Single-Model vs Router Mode)**:
   - S001 anchors only `GET /health`, `GET /v1/models`, and `GET /metrics`.
   - S001 completely omits the router / multi-model mode routes:
     - `GET /models` (listing available models across cache, `--models-dir`, and `--models-preset`).
     - `POST /models/load`, `POST /models/unload`, `GET /models/sse`, `POST /models`, `DELETE /models`.
   - *Consequence for C2*: A crosswalk relying solely on S001 would claim llama.cpp cannot report "available" models separately from "running" models. In reality, router mode exposes `GET /models` with `status.value: "unloaded" | "loading" | "loaded" | "sleeping" | "downloading" | "incomplete"`, precisely separating availability from execution state.

3. **Model ID Resolution & Normalization**:
   - S001 states: *"model `id` defaults to the `-m` path unless `--alias`"*.
   - Upstream README confirms this rule, and further details:
     - `--alias STRING`: sets model aliases (used by API).
     - `--tags STRING`: sets model tags (informational, not used for routing).
     - Single-model `GET /v1/models` returns `id` as the exact `-m` path (unless `--alias` is set).
     - Router `GET /models` returns `id` as the repo/quant tag or preset name, plus a separate `path` field pointing to the physical GGUF file.

4. **Schema Evolution (`architecture` & `meta`)**:
   - Upstream `GET /v1/models` and `GET /models` include `architecture.input_modalities` and `architecture.output_modalities` (`"text"` vs `"decisions"` for native decision models).
   - In `GET /v1/models`, `meta` is explicitly documented as nullable (*"The `meta` field can be `null` (for example, while the model is still loading)"*).
   - S001 does not mention `architecture` modalities or nullable `meta`.

---

## 4. Synthesis for C2 Crosswalk Entry

| Category | llama.cpp Single-Model Mode (`llama-server -m ...`) | llama.cpp Router Mode (`llama-server [--models-dir/preset]`) |
|---|---|---|
| **Health Route** | `GET /health` (or `/v1/health`) → 503 loading, 200 ready (`{"status":"ok"}`). No identity fields. | `GET /health` → identical loading/ready status semantics. |
| **Available Models Route** | *None* (only the single loaded model exists). | `GET /models` → returns all available cached/preset models, reporting `status.value: "unloaded"` when not in RAM. |
| **Running Models Route** | `GET /v1/models` → returns single-element list of the currently loaded model. | `GET /models` filtered to `status.value == "loaded"`, or `GET /v1/models` (forwarded from loaded model). |
| **Alias / ID Semantics** | `id` defaults to `-m` path; overridden by `--alias`. Informational tags via `--tags`. | Preset section key or Hugging Face repo tag; `path` field retains physical filesystem location. |
| **Readiness Distinction** | `/health` is binary ready/loading; does not prove model match. Identity must be verified against `/v1/models` `data[0].id`. | `/health` confirms router readiness; model availability is queried via `GET /models`; load state is tracked via `status.value`. |

---

## 5. Tooling & Execution Audit

- **Tools installed/updated**: None.
- **Commands executed**:
  - `date -u`: verified actual review timestamp `2026-10-20T02:14:36Z`.
  - HTTP `read` on GitHub raw content and GitHub commit API.
  - Read-only file inspection of `spec.json`, `dispatch.json`, `ReportScribe.md`, and `corpus/SOURCES.md`.
- **Modifications**: Wrote only `.ufo/waves/round-11/advice/SourceLlama.md`. No changes made to registry, corpus, or code.
