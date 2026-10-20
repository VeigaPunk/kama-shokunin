# SourceRunning — Source Reconnaissance for Ollama `/api/ps` (List Running Models)

**Seat:** `SourceRunning` (scout)  
**Lane:** `kama-shokunin`  
**Round:** Round 11 (steered round label/date: 2026-10-19; actual UTC access and verification date: 2026-10-20, `date -u` recorded 2026-10-20T02:14:20Z)  
**Target:** Read-only source reconnaissance of `https://docs.ollama.com/api/ps` for C2 (served-identity crosswalk).  
**Contract adherence:** Leaf seat only; no subagent dispatch; no edits to corpus, registry, `LOG.md`, `SCORECARD.md`, or lessons; no endpoint scans or network requests to local runtime. Read-only inspection of public vendor documentation.

---

## 1. Tooling Directive

- **Installs or updates:** None. Existing tools (`curl`, `read`, `grep`, `glob`) were sufficient.
- **Safety gate:** No system package modifications attempted.

---

## 2. Source Provenance & Document Identity

- **Source URL:** `https://docs.ollama.com/api/ps`
- **Alternate Markdown URL:** `https://docs.ollama.com/api/ps.md` (via Mintlify documentation platform on Vercel)
- **HTTP Header Verification:** `date: Tue, 20 Oct 2026 02:15:11 GMT`, `server: Vercel`, `etag: W/"qllptr0tw668m4"`, `x-matched-path: /_sites/[subdomain]/[[...slug]]`
- **Document Title:** "List running models"
- **OpenAPI Specification Version:** `openapi: 3.1.0`
- **API Info:** `title: "Ollama API"`, `version: 0.1.0`, `description: "OpenAPI specification for the Ollama HTTP API"`
- **Server Base URL:** `http://localhost:11434`
- **Path & Method:** `GET /api/ps`
- **Operation ID:** `ps`

---

## 3. Grounded Citations (Exact Quotes $\le$ 25 Words)

1. **Section: OpenAPI `GET /api/ps` 200 Response Description**  
   *Location:* OpenAPI specification `/openapi.yaml` under `paths./api/ps.get.responses.200.description`  
   *Quote:*  
   > "Models currently loaded into memory" (5 words)

2. **Section: Page Subtitle & Operation Summary**  
   *Location:* OpenAPI specification `/openapi.yaml` under `paths./api/ps.get.description` and header blockquote  
   *Quote:*  
   > "Retrieve a list of models that are currently running" (8 words)

3. **Section: Schema `PsResponse` Property Description**  
   *Location:* OpenAPI specification `/openapi.yaml` under `components.schemas.PsResponse.properties.models.description`  
   *Quote:*  
   > "Currently running models" (3 words)

---

## 4. Returned Fields & Schema Definitions

The endpoint returns HTTP 200 with schema `PsResponse`:

- `models` (array of `Ps` objects): "Currently running models".

Each model item in `models` implements schema `Ps`:
- `name` (`string`): "Name of the running model" (e.g., `"gemma4"`, `"llama3.2:latest"`).
- `model` (`string`): "Name of the running model" (duplicate field matching `name`).
- `size` (`integer`): "Size of the model in bytes" (e.g., `6591830464`).
- `digest` (`string`): "SHA256 digest of the model" (e.g., `"c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"`).
- `details` (`object`): "Model details such as format and family".
  - `parent_model` (`string`): Parent model name or empty string.
  - `format` (`string`): Model format (e.g., `"gguf"`).
  - `family` (`string`): Primary model family (e.g., `"gemma4"`).
  - `families` (`array` of `string`): All families (e.g., `["gemma4"]`).
  - `parameter_size` (`string`): Approximate parameter count (e.g., `"8.0B"`).
  - `quantization_level` (`string`): Quantization identifier (e.g., `"Q4_K_M"`).
- `expires_at` (`string`): "Time when the model will be unloaded" (ISO 8601 timestamp, e.g., `'2025-10-17T16:47:07.93355-07:00'`).
- `size_vram` (`integer`): "VRAM usage in bytes" (e.g., `5333539264`).
- `context_length` (`integer`): "Context length for the running model" (e.g., `4096`).

---

## 5. Served Identity & Inventory Semantics for C2

The C2 crosswalk requires separating four distinct operational concepts: **availability**, **loaded models**, **alias identity**, and **readiness**.

### A. Running (`/api/ps`) vs. Available (`/api/tags`)
- **Available Inventory (`GET /api/tags`):** Returns models stored on local disk under `ModelSummary` (`modified_at`, `size` as total disk bytes, `remote_model`, `remote_host`). It answers: *"What models can this daemon run if requested?"*
- **Running / Resident Inventory (`GET /api/ps`):** Returns only models currently resident in RAM/VRAM (`size_vram`, `context_length`, `expires_at`). It answers: *"What models are currently resident in memory right now?"*
- **Key semantic separation:** Presence in `/api/tags` does NOT prove a model is loaded into memory. Conversely, an empty array `models: []` from `/api/ps` is a valid response indicating the daemon is running but has no model currently in memory.

### B. Running (`/api/ps`) vs. Readiness & Health
- **No Native Health Route:** As documented in `corpus/knowledge/runtime-health-surface-matrix.md` (citing S009/S010), Ollama documents no dedicated `/health`, `/healthz`, `/live`, or `/ready` endpoints.
- **Process Liveness vs. Model Readiness:**
  - A successful 200 response from `/api/ps` proves HTTP process liveness of the Ollama daemon.
  - An entry in `/api/ps` proves memory residency (`size_vram > 0`), but does **not** prove readiness to complete an inference generation.
  - **No concurrency or queue state:** Unlike `llama-server` (`/slots` exposing `is_processing`, `/props`), Ollama's `/api/ps` does not expose slot occupancy, active prompt processing state, or queue backlog.
  - **On-demand loading behavior:** Ollama automatically loads models on receiving generation requests (`/api/generate`, `/api/chat`, or `/v1/chat/completions`). Therefore, a model absent from `/api/ps` may still be successfully served (incurring a cold-start load latency), provided it exists in `/api/tags`. Absence from `/api/ps` does not mean traffic admission failure.

### C. Running (`/api/ps`) vs. Alias & OpenAI-Compatible Identity (`/v1/models`)
- `/api/ps` reports Ollama-native names and model tags (`name: "gemma4"` or `"gemma4:latest"`), format, family, VRAM, and expiry.
- OpenAI-compatible `/v1/models` (S010) returns `{ "id": "gemma4", "object": "model", "created": ..., "owned_by": "library" }`. It strips runtime memory metrics (`size_vram`, `context_length`, `expires_at`) and provides no indicator of whether the model is in VRAM or on disk.
- Consumers using OpenAI base URLs (`/v1`) cannot distinguish loaded models from available models without hitting native `/api/ps`.

---

## 6. Limits & What Cannot Be Concluded from `/api/ps`

1. **Cannot infer execution readiness or non-blocking generation:** Loaded models in memory can still fail on inference due to GPU driver faults, illegal memory access, or context overflow (see S029).
2. **Cannot infer capacity or queue depth:** `/api/ps` lacks slot-level or request-level saturation counters.
3. **Cannot infer static residency:** Every model entry has an `expires_at` lease. Unless configured with `keep_alive: -1`, Ollama will unload the model once the timer expires. A probe observing a model at $t_0$ cannot assume the model is resident at $t_0 + \Delta$.
4. **Cannot assume exclusivity:** Multiple models may appear in `models` if VRAM/RAM permits multi-model concurrency, or an empty list if idle.
5. **Cold-start ambiguity:** A health check that fails because `/api/ps` is empty would falsely reject a healthy Ollama server capable of serving on-demand models from `/api/tags`.

---

## 7. Comparison with Existing S-Row (S012) & Drift Analysis

### Existing Row in `corpus/SOURCES.md`:
```markdown
| S012 | Ollama List running models — https://docs.ollama.com/api/ps | docs | A | Ollama model inventory currently loaded into memory | OpenAPI 3.1.0, info.version 0.1.0; List running models; GET /api/ps | Separates running models from the available-model list and exposes digest, context length, VRAM use, and expiry. | queued | 2026-10-19 | 90d | — |
```

### Comparative Analysis:
- **URL & Title:** Matches exactly (`https://docs.ollama.com/api/ps`, "List running models").
- **OpenAPI Version & Info:** Matches exactly (`openapi: 3.1.0`, `info.version: 0.1.0`).
- **Claimed Summary:** "Separates running models from the available-model list and exposes digest, context length, VRAM use, and expiry." Matches observed fields `digest`, `context_length`, `size_vram`, and `expires_at`.
- **Drift Verdict:** **NO DRIFT.** The upstream documentation and OpenAPI specification have experienced zero syntactic or semantic drift since round 10.
- **Status & Handoff Recommendation for Parent/Integration:**
  - S012 is currently `queued` with consumer `—`.
  - When C2 integrates the served-identity crosswalk entry into `corpus/knowledge/served-model-identity.md` (or sibling knowledge entry), S012 should be updated from `queued` to `mined` with consumer pointing to `corpus/knowledge/served-model-identity.md`.
  - Original accessed date on S012 is `2026-10-19`. The verification date performed in this round is `2026-10-20` UTC.

---

## 8. Defects & Limits of Documentation Source

- **Lack of explicit date/version tag in prose:** The Mintlify documentation page does not display a visible release tag or last-updated timestamp in human-readable text; versioning is anchored solely to `info.version: 0.1.0` in the embedded OpenAPI 3.1.0 specification and HTTP headers (`etag`, `date`).
- **No documented HTTP error responses:** The OpenAPI snippet documents only HTTP 200 (`PsResponse`); failure states (e.g., internal engine error or daemon initialization) are not enumerated in the schema.
