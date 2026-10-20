# Source Reconnaissance: OpenAI `GET /models` / `GET /v1/models` (C2 Served Identity)

- **Source URL**: `https://developers.openai.com/api/reference/resources/models/methods/list` (alternate markdown: `https://developers.openai.com/api/reference/resources/models/methods/list/index.md`)
- **Verified-at**: `2026-10-20` (actual UTC review timestamp from `date -u`; steered round label is `2026-10-19`)
- **Document Identity**: OpenAI API Reference — `List models` (`GET /models`, base path `/v1/models`, OpenAPI commit `c396f25f2f8112d7761097b7b0217808dc65ddd4`, metadata version 2.3.0, generated with Astro v7.3.1)
- **Assigned Seat**: `SourceOpenAI` (scout)
- **Report Path**: `.ufo/waves/round-11/advice/SourceOpenAI.md`

---

## 1. Grounded Citations & Verbatim Quotes (<= 25 words)

### Citation 1: Endpoint Purpose
- **Section**: `## List models` / Description
- **Quote**:
  > "Lists the currently available models, and provides basic information about each one such as the owner and availability."
- **Word count**: 18 words.
- **Location**: Paragraph immediately below `**get** \`/models\``.

### Citation 2: Model Identifier Semantic Role
- **Section**: `### Returns` -> `data: array of Model` -> `id: string`
- **Quote**:
  > "The model identifier, which can be referenced in the API endpoints."
- **Word count**: 11 words.
- **Location**: Property description under `id: string`.

### Citation 3: Object Type Guarantee
- **Section**: `### Returns` -> `data: array of Model` -> `object: "model"`
- **Quote**:
  > "The object type, which is always \"model\"."
- **Word count**: 7 words.
- **Location**: Property description under `object: "model"`.

### Citation 4: Shutdown Date Specification
- **Section**: `### Returns` -> `data: array of Model` -> `shutdown_date: optional string or null`
- **Quote**:
  > "The date when the model will shut down, or null if not announced."
- **Word count**: 13 words.
- **Location**: Property description under `shutdown_date`.

---

## 2. Served Identity & Inventory Semantics (C2 Verification)

### A. Availability vs. Running (Loaded) State
- `GET /models` (and the standard base path `GET /v1/models`) enumerates **available** models configured or exposed by the service.
- The description explicitly specifies that it "Lists the currently available models".
- It does **not** indicate whether a model is currently executing, active in memory, or resident in GPU/VRAM.
- In cloud multi-tenant systems, availability represents account entitlement and catalog routing, not pre-allocated hardware state.
- In local runtime engines that emulate this route (e.g. `llama-server`, `vLLM`, `Ollama`):
  - An entry appearing in `data[].id` signifies that the endpoint can receive requests for that identifier.
  - It does **not** prove that model weights are currently resident in VRAM or that execution will avoid cold-start delays or capacity exhaustion.
  - Local engines like Ollama distinguish available inventory (`/api/tags` or `/v1/models`) from loaded/running inventory (`/api/ps`). An OpenAI-shaped `/v1/models` list answers solely for availability.

### B. Availability vs. Health & Readiness
- A successful `200 OK` response with an `{"object":"list","data":[...]}` payload proves that the HTTP listener is operational and can query its model catalog.
- It provides **zero** readiness or health semantics:
  - There is no field indicating engine health, worker process status, slot saturation, or inference error states.
  - Fleet records (e.g. `LOG.md:195–200`) show that an endpoint can present valid model IDs while failing completions with `resource_exhausted` or HTTP 503 errors.
  - The endpoint cannot serve as a Kubernetes-style liveness or readiness probe; separate health routes (e.g. `/health`, `/slots`, `/props` in local engines) govern process life and load state.

### C. Alias Identity vs. Served Model Identity
- Upstream OpenAI model IDs are opaque strings (e.g. `gpt-4o`, `text-embedding-3-small`, or example values `model-id-0`).
- They contain no file paths, GGUF metadata, or content-addressed digests.
- Local runtimes implementing the OpenAI schema frequently map local filesystem paths (e.g. `/scratch/models/.../Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf`) into `data[].id`.
- When local engines support `--alias`, the alias replaces or supplements the path. However, the OpenAI specification itself defines no alias resolution layer, path stripping convention, or digest mapping.

---

## 3. Schema Fields Breakdown

The endpoint returns an object with `object: "list"` and `data: array of Model`:

| Field | Type | Description / Constraints |
|---|---|---|
| `object` | `string` | The object type, always `"list"` |
| `data` | `array` | Array of `Model` objects |
| `data[].id` | `string` | The model identifier, which can be referenced in the API endpoints |
| `data[].created` | `number` | Unix timestamp (in seconds) when the model was created |
| `data[].object` | `string` | The object type, always `"model"` |
| `data[].owned_by` | `string` | The organization that owns the model (e.g. `"openai"`, `"system"`, organization slug) |
| `data[].shutdown_date` | `string \| null` | Optional. The date when the model will shut down, or null if not announced |

---

## 4. Limits & Boundary Constraints

1. **Catalog Inventory Only**: The route defines catalog metadata only. It does not measure or return execution concurrency, context length limits, remaining token quotas, or compute load.
2. **No Health / Readiness Probing**: Does not expose daemon health, queue length, or slot availability.
3. **No Execution Guarantee**: Inclusion in `data` guarantees only that the ID is valid for submission, not that the request will succeed or that capacity is available.
4. **Authentication Boundary**: Upstream OpenAI requires `Authorization: Bearer $OPENAI_API_KEY`. While local loopback emulators often allow unauthenticated requests, upstream endpoints return `401 Unauthorized` (`UNAUTHORIZED_SERVICE`).
5. **Local Compatibility Divergence**:
   - Local emulators (such as `llama-server`) add non-standard fields (e.g. top-level `models: [...]` array) and output file paths as `id`.
   - Local emulators rarely implement `shutdown_date` or cloud ownership structures.
   - Probing `/v1/models` without validating server identity (e.g. `Server: llama.cpp` header) risks misclassifying proxies, web servers, or foreign servlets as OpenAI model engines.

---

## 5. Comparison with Existing S-Row (S016) and Drift Analysis

### Existing S-Row Entry (`corpus/SOURCES.md:28`)
```markdown
| S016 | OpenAI List models — https://developers.openai.com/api/reference/resources/models/methods/list | docs | A | OpenAI API model-list reference for served-identity crosswalks, not local readiness | List models; GET /models; OpenAI OpenAPI commit c396f25f2f8112d7761097b7b0217808dc65ddd4, metadata version 2.3.0 | Provides the reference list shape and basic model metadata; it does not establish local-server health or loaded weights. | queued | 2026-10-19 | 90d | — |
```

### Reference in Lessons (`corpus/lessons/round-10.md:76, 101`)
```markdown
| S016 | https://developers.openai.com/api/reference/resources/models/methods/list | 2026-10-19 | "Lists the currently available models, and provides basic information about each one such as the owner and availability." | `List models`; description |
```
```markdown
| K02 served-identity crosswalk, K05 context capacity | deferred (not rejected) | rows S011 S012 S016 are opened and queued; K05 needs an authorized runtime for the declared-vs-served comparison (README §Frontier) |
```

### Evaluation & Drift Assessment
1. **Contract Stability & No Semantic Drift**:
   - The live documentation at `https://developers.openai.com/api/reference/resources/models/methods/list` confirms the exact quote recorded in `corpus/lessons/round-10.md:76`:
     > "Lists the currently available models, and provides basic information about each one such as the owner and availability."
   - The scope and teaches assertions in S016 ("reference list shape and basic model metadata; it does not establish local-server health or loaded weights") are completely verified by the live documentation.
2. **Schema Attributes & Clarifications**:
   - S016 notes "basic model metadata".
   - The live schema specifies `id`, `created`, `object: "model"`, `owned_by`, and `shutdown_date: optional string or null`.
   - The OpenAPI commit reference (`c396f25f2f8112d7761097b7b0217808dc65ddd4`, metadata version `2.3.0`) remains a sound anchor for the spec snapshot.
3. **Status Transition for C2**:
   - In `corpus/SOURCES.md`, S016 is currently marked `status: queued` and `used-by: —`.
   - For C2 served-identity crosswalk work (`corpus/knowledge/served-identity-crosswalk.md`), S016 is now grounded by this scout slice and ready for transition to `status: mined` and `used-by: corpus/knowledge/served-identity-crosswalk.md` (to be performed by the designated owner seat, `SourceCurator`).

---

## 6. Tooling Directive Record

- No packages, tools, or dependencies were installed or upgraded during this reconnaissance slice.
- Read operations used native tools (`read`, `bash date -u`).
