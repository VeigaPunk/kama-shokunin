# Source Reconnaissance Report: Ollama OpenAI Compatibility (S010)

source: https://docs.ollama.com/api/openai-compatibility
source-repo: https://github.com/ollama/ollama/blob/c1737589973d5cefd676ef16eb43835663540035/docs/api/openai-compatibility.mdx
verified-at: 2026-10-20 — read-only web/API check; historical S010 observation dated 2026-10-19
recheck: on-release
relevant-s-row: S010 (`corpus/SOURCES.md:22`)

## 1. Scope & Objective

Leaf-scout reconnaissance for Round 11 C2 coverage (served-identity crosswalk). Evaluates `https://docs.ollama.com/api/openai-compatibility` strictly for:
1. Served model identity and inventory semantics.
2. Clear separation of availability, running/loaded state, and health/readiness.
3. Verification of existing S-row S010 and drift detection.

## 2. Document Identity & Upstream Anchor

- Document URL: `https://docs.ollama.com/api/openai-compatibility`
- Upstream Source File: `docs/api/openai-compatibility.mdx` in repository `ollama/ollama`
- Upstream Commit SHA: `c1737589973d5cefd676ef16eb43835663540035`
- Upstream Commit Date: `2026-09-23T01:28:11Z` (`docs: document thinking control discovery (#18501)`)
- Verification Date: `2026-10-20` (UTC review date); historic observation in S010 recorded `2026-10-19`.

## 3. Exact Sections and Grounded Quotes (<= 25 words each)

### A. General Compatibility & Surface Boundary
- **Section**: Opening introductory paragraph (`# OpenAI compatibility`)
- **Quote**: "Ollama supports a subset of the OpenAI API." (8 words)
- **Significance**: Explicitly bounds the `/v1` surface; Ollama does not implement the full OpenAI specification.

### B. Served Model Inventory & Identity Fields
- **Section**: `## Endpoints` -> `### /v1/models` -> `#### Notes`
- **Quote 1**: "`created` corresponds to when the model was last modified" (8 words)
- **Quote 2**: "`owned_by` corresponds to the ollama username, defaulting to `\"library\"`" (8 words)
- **Significance**: Identifies the exact model metadata returned by `GET /v1/models` and `GET /v1/models/{model}`. Returned fields do not include memory residency or operational status.

### C. Model Availability (Offline / Stored Tags)
- **Section**: `## Models`
- **Quote**: "For local inference, download a model before using it:" (8 words)
- **Significance**: Models exposed under `/v1/models` are local downloaded artifacts (`ollama pull`), reflecting available inventory rather than active execution state.

### D. Model Aliasing Semantics
- **Section**: `## Models` -> `### Default model names on a local server`
- **Quote**: "For tooling that relies on default OpenAI model names such as `gpt-3.5-turbo`, use `ollama cp` to copy an existing model name" (21 words)
- **Significance**: Demonstrates that model names on Ollama can be aliased using `ollama cp <source> <alias>`, and clients request the aliased name in the `model` request field.

### E. Context Size Limitations
- **Section**: `## Models` -> `### Setting the local context size`
- **Quote**: "The OpenAI API does not have a way of setting the context size for a model." (15 words)
- **Significance**: Highlights that context window configuration cannot be queried or updated via the OpenAI-compatible `/v1` endpoints; it requires creating a custom `Modelfile` via `ollama create`.

### F. Stateless Responses Boundary
- **Section**: `### Responses API` -> `POST /v1/responses`
- **Quote**: "Only the non-stateful flavor is supported (i.e., there is no `previous_response_id` or `conversation` support)." (13 words)
- **Significance**: Added in Ollama v0.13.3; restricts `/v1/responses` to stateless invocations.

## 4. C2 Served Identity Crosswalk Analysis

### Availability vs. Running (Loaded) vs. Health
1. **Available Model Inventory**:
   - `GET /v1/models` returns the inventory of locally downloaded/created models available for invocation on the instance.
   - Documented response fields: `created` (modification timestamp), `owned_by` (Ollama username or `"library"`), alongside standard OpenAI `id` fields.
   - An entry in `/v1/models` confirms local availability; it does **not** prove that weights are loaded into VRAM/RAM.

2. **Running (Loaded) Models**:
   - The OpenAI compatibility surface has **no** concept or indicator for running models.
   - There are no fields in `/v1/models` representing memory residency, VRAM allocation, active slot status, or expiration.
   - Distinguishing loaded/running models requires Ollama's native endpoint `GET /api/ps` (S012), which returns active VRAM footprint and context expiration.

3. **Health and Readiness**:
   - There is **no health or readiness route** anywhere on this page.
   - Documented endpoints on the OpenAI compatibility surface are strictly:
     - `/v1/chat/completions`
     - `/v1/completions`
     - `/v1/models`
     - `/v1/models/{model}`
     - `/v1/embeddings`
     - `POST /v1/responses`
   - A `200 OK` on `/v1/models` only establishes that the HTTP daemon is serving the catalog; it does not constitute a readiness probe for model execution.

### Documented Limits & Exclusions
- **Unsupported Endpoints**: No `/v1/audio/*`, `/v1/files`, `/v1/fine_tuning`, `/v1/batches`, `/v1/moderations`, `/v1/assistants`, `/v1/threads`.
- **Unsupported Fields in `/v1/chat/completions`**: `logprobs`, `tool_choice`, `logit_bias`, `user`, `n`, and URL-based `image_url` (only Base64 image content is supported).
- **Unsupported Fields in `/v1/completions`**: `best_of`, `echo`, `logit_bias`, `user`, `n`, `logprobs`. `prompt` accepts string only.
- **Unsupported Fields in `/v1/embeddings`**: `array of tokens`, `array of token arrays`, `user`.
- **Unsupported Fields in `/v1/responses`**: `previous_response_id`, `conversation`, `truncation`.

## 5. Existing S-Row Comparison & Drift Assessment

### Current S-Row in `corpus/SOURCES.md`:
```markdown
| S010 | Ollama OpenAI compatibility — https://docs.ollama.com/api/openai-compatibility | docs | A | Ollama OpenAI-compatible surface | §Endpoints `/v1/models`; source docs/api/openai-compatibility.mdx @ ollama/ollama c1737589973d5cefd676ef16eb43835663540035 (2026-09-23) | Ollama supports a subset of the OpenAI API; `/v1/models` notes `created` and `owned_by` semantics; no health route appears on this page. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md |
```

### Verification & Drift Findings:
1. **Upstream Commit Drift**: **None**.
   - Remote HEAD for `docs/api/openai-compatibility.mdx` on `github.com/ollama/ollama` was re-verified against GitHub API on 2026-10-20. The latest commit remains `c1737589973d5cefd676ef16eb43835663540035` from 2026-09-23.
2. **Anchor Drift**: **None**.
   - Anchors `§Endpoints `/v1/models`` and `### /v1/models` exist verbatim.
3. **Semantic Drift**: **None**.
   - Abstract in S010 accurately summarizes the page: subset support, `/v1/models` metadata (`created`, `owned_by`), and total absence of health routes.
4. **C2 Coverage Crosswalk Role**:
   - S010 is currently `used-by: corpus/knowledge/runtime-health-surface-matrix.md`.
   - In Round 11, S010 is required as foundational input for `corpus/knowledge/served-identity-crosswalk.md` to establish how Ollama surfaces available model inventory and local model alias identity (`ollama cp`), contrasting with native `/api/tags` (available) and `/api/ps` (loaded/running).
   - SourceCurator should append `corpus/knowledge/served-identity-crosswalk.md` to S010's `used-by` field.

## 6. Tooling Directive Record

- No packages or tools were installed or updated during this reconnaissance.
- Existing tools (`curl`, `jq`, `date`) were used read-only.
