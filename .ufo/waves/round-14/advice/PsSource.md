# PsSource — Round 14 Ollama ps Documentation & Replay Evidence Findings

Seat: `KamaR14.PsSource` (role: scout, leaf member).
Absolute Lane Root: `/home/vgpnk/Projects/shokunin/kama-shokunin`
Report Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/advice/PsSource.md`
Tooling Record: No tools installed or upgraded (none required; official docs opened via standard web fetch).
Verification: None executed (leaf scout contract forbids test/build/smoke runs; verification reserved for L1).

---

## 1. Official Documentation Access & Provenance

- **Source Row**: S012 (Ollama List running models, OpenAPI 3.1.0, info.version 0.1.0; GET `/api/ps`).
- **URL Opened**: `https://docs.ollama.com/api/ps`
- **Access Timestamp**: 2026-10-20 (reopened live).
- **Target Specification**: OpenAPI 3.1.0 specification published by Ollama for endpoint `GET /api/ps`.
- **Operation Summary**: `List running models`
- **Operation Description**: `Retrieve a list of models that are currently running`

---

## 2. Located Quotes (≤ 25 Words)

- **200 Response Description (Loaded-memory wording)**:
  > “Models currently loaded into memory”
  *(5 words)*

- **Field Description: `expires_at`**:
  > “Time when the model will be unloaded”
  *(7 words)*

- **Field Description: `digest`**:
  > “SHA256 digest of the model”
  *(5 words)*

- **Schema Item Description: `PsResponse.models`**:
  > “Currently running models”
  *(3 words)*

---

## 3. Detailed Field & Semantic Analysis

### A. Loaded-Memory Wording
- `GET /api/ps` documents that successful HTTP 200 responses return `PsResponse` where `models` represents "Currently running models", described at the response level as "Models currently loaded into memory".
- The schema defines items in `models` with fields: `name`, `model`, `size`, `digest`, `details`, `expires_at`, `size_vram`, `context_length`.
- Both `name` and `model` carry the identical description: "Name of the running model".

### B. `digest` Semantics & Join Policy
- In `Ps`, `digest` is documented as "SHA256 digest of the model".
- In `/api/tags` (`ModelSummary`), `digest` is documented as "SHA256 digest identifier of the model contents".
- **Join Rule Status `[INFERENCE]`**: The documentation does not specify a join algorithm between `/api/tags` and `/api/ps`. Reconciling availability and loaded state by joining on identical `digest` strings is an analytical inference (`[INFERENCE]`) adopted by the lane's replay classifier contract, not a first-party documented join behavior.
- **Comparison Boundary**: Digest matching must be an exact string equality check on non-empty strings. Basename normalization, hashing, or truncation must not be performed.

### C. `expires_at` Semantics
- `expires_at` is documented as "Time when the model will be unloaded", presented as an ISO 8601 formatted timestamp string with timezone offset (e.g., `'2025-10-17T16:47:07.93355-07:00'`).
- It represents the point-in-time schedule at which Ollama's memory manager plans to evict the model from memory if inactive.

---

## 4. Strict Readiness Non-Inference Boundary

1. **Loaded State is NOT Execution Readiness**:
   - Being "loaded into memory" at the moment an offline snapshot was captured does not establish that the model is ready to process inference requests, that the engine is healthy, or that forward passes will succeed.
   - The contract explicitly fixes: `readiness="unknown"` and `scope="offline-captures-not-runtime"`.
   - Exit 0 signifies `loaded_same_digest` (metadata correspondence between tags and ps captures), **NOT** runtime readiness.

2. **No Timestamps or Expiry Inferences**:
   - The classifier contract explicitly states: *"No timestamps/expiry/current-liveness inferences. Inputs explicitly caller-authorized exported metadata, no acquisition feature."*
   - Neither past nor future `expires_at` timestamps may be evaluated against the host clock.
   - An expired timestamp in an offline capture does not invalidate a `loaded_same_digest` finding; the classifier must ignore expiration calculations completely.

3. **Schema Fail-Closed Invariants**:
   - A valid empty ps models array (`{"models": []}`) combined with a matching local tags entry yields `available_not_loaded` (exit 1).
   - Missing `--ps` input, malformed JSON, missing `models` key, non-array `models`, or a selected entry with missing/empty `digest` must fail closed to `invalid_input` (exit 2).
   - A ps-only match with no corresponding tags match must yield `unknown` (exit 2), never `loaded_same_digest`.

---

## 5. Bounded Peer Recommendations Sent

Prior to file finalization, bounded recommendations were messaged to owning peers via `agent://`:

- **To `KamaR14.Classifier` (`agent://KamaR14.Classifier`)**:
  - Advised that `GET /api/ps` 200 description is "Models currently loaded into memory" with `expires_at` ("Time when the model will be unloaded") and `digest` ("SHA256 digest of the model").
  - Confirmed contract boundary: do not evaluate clock or timestamps; past `expires_at` must still classify as `loaded_same_digest` (exit 0) when digests match.
  - Required output keys: `readiness="unknown"`, `scope="offline-captures-not-runtime"`.
  - Required schema handling: valid empty `models: []` with tags match -> `available_not_loaded` (exit 1); malformed/non-array -> `invalid_input` (exit 2); exact string digest comparison.

- **To `KamaR14.Fixtures` (`agent://KamaR14.Fixtures`)**:
  - Recommended fixture controls:
    1. Past `expires_at` timestamp with identical digest -> exit 0 `loaded_same_digest` (proves absence of clock/staleness creep).
    2. Matching tags with `{"models": []}` in ps -> exit 1 `available_not_loaded`.
    3. Missing or non-array `models` in ps -> exit 2 `invalid_input`.
    4. Missing or empty `digest` on selected ps entry -> exit 2 `invalid_input`.
    5. Matching model name in ps with conflicting digest -> exit 1 `identity_conflict`.
    6. Matching model in ps but absent from tags -> exit 2 `unknown`.

- **To `KamaR14.ReplayKnowledge` (`agent://KamaR14.ReplayKnowledge`)**:
  - Emphasized citing S012 with literal 200 quote "Models currently loaded into memory" and field descriptions.
  - Advised explicitly recording that joining `/api/tags` and `/api/ps` via `digest` is an `[INFERENCE]`, and that metadata correspondence does not guarantee runtime readiness.

---

## 6. Limits & Grounding

- **Observed Static Facts**: Live documentation at `https://docs.ollama.com/api/ps` (OpenAPI 3.1.0, info.version 0.1.0), and committed corpus files (`SOURCES.md`, `served-identity-crosswalk.md`).
- **Inference vs Source**: The term "Models currently loaded into memory" is first-party documentation. The joining of tags and ps on `digest` to classify loaded status is a lane-adopted `[INFERENCE]`.
- **No Verification Executed**: As a leaf scout, no tests, builds, or scripts were run.
