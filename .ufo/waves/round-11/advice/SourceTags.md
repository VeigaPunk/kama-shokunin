# Source Reconnaissance: Ollama `/api/tags` (C2 Served Identity)

- **Source URL**: `https://docs.ollama.com/api/tags` (alternate markdown: `https://docs.ollama.com/api/tags.md`)
- **Verified-at**: `2026-10-20` (actual UTC review timestamp from `date -u`; steered round label is `2026-10-19`)
- **Document Identity**: Ollama HTTP API OpenAPI Specification 3.1.0 (`info.version`: 0.1.0, default server: `http://localhost:11434`)
- **Assigned Seat**: `SourceTags` (scout)
- **Report Path**: `.ufo/waves/round-11/advice/SourceTags.md`

---

## 1. Grounded Citations & Verbatim Quotes (<= 25 words)

### Citation 1: Endpoint Purpose
- **Section**: `# List models` (header blockquote) / `paths./api/tags.get.description`
- **Quote**:
  > "Fetch a list of models and their details"
- **Word count**: 7 words.

### Citation 2: Response 200 Semantic Meaning
- **Section**: `## OpenAPI` -> `paths./api/tags.get.responses['200'].description`
- **Quote**:
  > "List available models"
- **Word count**: 3 words.

### Citation 3: Model Object Semantic Scope
- **Section**: `## OpenAPI` -> `components.schemas.ModelSummary.description`
- **Quote**:
  > "Summary information for a locally available model"
- **Word count**: 6 words.

---

## 2. Served Identity & Inventory Semantics (C2 Verification)

### A. Availability vs. Running (Loaded) State
- `GET /api/tags` enumerates models that exist in local disk storage (or configured remote mirrors).
- The `size` field is explicitly documented as `Total size of the model on disk in bytes`.
- It does **not** indicate that a model is currently loaded into RAM/VRAM or running. Running/loaded models are governed by a separate endpoint (`GET /api/ps`), which reports active VRAM footprint and context.

### B. Availability vs. Health & Readiness
- A `200 OK` response from `/api/tags` indicates that the Ollama HTTP daemon is reachable and can read its model inventory catalog.
- It does **not** represent a readiness probe or execution health check. The presence of a model in the `/api/tags` array gives no assurance that the model will successfully allocate GPU/CPU resources, load weights without error, or answer an inference call.
- The documentation on this page defines no health, liveness, or readiness endpoint.

### C. Alias Identity vs. Cryptographic Content Identity
- `name`: string representing the model tag/alias (e.g. `gemma4`, `llama3.2:latest`).
- `model`: string matching the model name.
- `digest`: SHA256 digest string (`SHA256 digest identifier of the model contents`).
- `remote_model` / `remote_host`: identifies upstream model coordinates when proxied/remote.
- Tags are mutable references; only `digest` guarantees content-addressed immutable identity.

---

## 3. Schema Fields Breakdown

The endpoint returns a `ListResponse` object containing `models: ModelSummary[]`:

| Field | Type | Description / Constraints |
|---|---|---|
| `models` | `array` | List of `ModelSummary` items for available models |
| `models[].name` | `string` | Model name / tag label |
| `models[].model` | `string` | Model name |
| `models[].remote_model` | `string` | Name of upstream model, if model is remote |
| `models[].remote_host` | `string` | URL of upstream Ollama host, if model is remote |
| `models[].modified_at` | `string` | Last modified timestamp in ISO 8601 format |
| `models[].size` | `integer` | Total size of the model on disk in bytes |
| `models[].digest` | `string` | SHA256 digest identifier of the model contents |
| `models[].details` | `object` | Format, architecture family, and quantization details |
| `models[].details.format` | `string` | Model file format (e.g., `gguf`) |
| `models[].details.family` | `string` | Primary model family (e.g., `llama`, `gemma4`) |
| `models[].details.families` | `string[]` | All families the model belongs to, when applicable |
| `models[].details.parameter_size` | `string` | Approximate parameter count label (e.g., `7B`, `8.0B`, `13B`) |
| `models[].details.quantization_level` | `string` | Quantization level label (e.g., `Q4_0`, `Q4_K_M`) |

---

## 4. Limits & Boundary Constraints

1. **No Inference Readiness Guarantee**: Documented as inventory metadata only. Model corruption, incompatible GGUF architectures, or insufficient host VRAM will not be reflected in `/api/tags`.
2. **No Memory Residency Representation**: Memory/VRAM residency is omitted; `/api/tags` strictly reflects disk-backed inventory.
3. **No Filtering / Query Parameters**: The OpenAPI definition declares no query parameters (e.g. pagination or family filtering). The full local inventory is returned.
4. **Mutable Tag Ambiguity**: The `name` field may drift across upstream pulls; canonical identity requires pairing `name` with `digest`.
5. **No Health Route Surface**: Neither liveness nor readiness is exposed by this endpoint.

---

## 5. Comparison with Existing S-Row (S011) and Drift Analysis

### Existing S-Row Entry (`corpus/SOURCES.md:23`)
```markdown
| S011 | Ollama List models — https://docs.ollama.com/api/tags | docs | A | Ollama locally available model inventory, not proof of a loaded model | OpenAPI 3.1.0, info.version 0.1.0; List models; GET /api/tags | Lists locally available models with names, digests, and format or quantization metadata; availability is distinct from running state. | queued | 2026-10-19 | 90d | — |
```

### Evaluation & Drift Assessment
1. **Contract Stability**:
   - **No Semantic Drift**: The live documentation at `https://docs.ollama.com/api/tags` matches the specification in S011 (`OpenAPI 3.1.0, info.version 0.1.0; List models; GET /api/tags`).
   - The distinction stated in S011 ("availability is distinct from running state") is fully affirmed by `ModelSummary.description` ("Summary information for a locally available model") and `size` ("Total size of the model on disk in bytes").
2. **Uncaptured Attributes in S011 Summary**:
   - S011 notes "names, digests, and format or quantization metadata".
   - The live schema also specifies remote lineage fields (`remote_model`, `remote_host`), multiple family tags (`details.families`), and timestamping (`modified_at`).
3. **Status Flag**:
   - S011 is currently marked `queued` in `corpus/SOURCES.md`. When C2 crosswalk work incorporates this entry, S011 is qualified for elevation to `mined` targeting the C2 crosswalk artifact (e.g., `corpus/knowledge/served-model-identity.md` or successor crosswalk).

---

## 6. Tooling Directive Record

- No packages, tools, or dependencies were installed or upgraded during this reconnaissance slice.
- Read operations used native session tools (`read`, `bash date -u`).
