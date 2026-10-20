# Verification Report: OpenAI Reference Row & Claims (`OpenAI.md`)

- **Seat**: `OpenAI` (Role: `scout`, Leaf member)
- **Target URL**: `https://developers.openai.com/api/reference/resources/models/methods/list`
  - Alternate markdown: `https://developers.openai.com/api/reference/resources/models/methods/list/index.md`
- **Access Date**: `2026-10-20` (Actual UTC review timestamp; steered round-10 label is `2026-10-19`)
- **Evaluation Subject**: `corpus/knowledge/served-identity-crosswalk.md` (lines 1, 9, 19, 32, 39, 43, 72) and `corpus/SOURCES.md:28` (S016)
- **Scope**: Advisory verification report only; leaf member with no subagent delegation, no execution of test/check commands, and zero modifications to implementation, corpus, or fleet repositories.

---

## 1. Captured Verbatim Quotes (<= 25 words)

### Quote 1: Model Listing Purpose & Availability Boundary
- **Location**: `https://developers.openai.com/api/reference/resources/models/methods/list` § `## List models` (Description paragraph directly under `**get** /models`)
- **Verbatim Quote**:
  > "Lists the currently available models, and provides basic information about each one such as the owner and availability."
- **Word Count**: 18 words
- **Access Date**: 2026-10-20

### Quote 2: Model Identifier Semantics
- **Location**: `https://developers.openai.com/api/reference/resources/models/methods/list` § `### Returns` -> `data: array of Model` -> `id: string`
- **Verbatim Quote**:
  > "The model identifier, which can be referenced in the API endpoints."
- **Word Count**: 11 words
- **Access Date**: 2026-10-20

### Quote 3: Object Type Specification
- **Location**: `https://developers.openai.com/api/reference/resources/models/methods/list` § `### Returns` -> `data: array of Model` -> `object: "model"`
- **Verbatim Quote**:
  > "The object type, which is always \"model\"."
- **Word Count**: 7 words
- **Access Date**: 2026-10-20

### Quote 4: Shutdown Date Specification
- **Location**: `https://developers.openai.com/api/reference/resources/models/methods/list` § `### Returns` -> `data: array of Model` -> `shutdown_date: optional string or null`
- **Verbatim Quote**:
  > "The date when the model will shut down, or null if not announced."
- **Word Count**: 13 words
- **Access Date**: 2026-10-20

---

## 2. Comparison: Crosswalk OpenAI Row & Claims

### A. Comparison Against `corpus/knowledge/served-identity-crosswalk.md`

| Item in Crosswalk | Line | Crosswalk Claim / Statement | Live Spec Finding | Verification Verdict |
|---|---|---|---|---|
| **Source Citation** | `line 1` | `source: S016 https://developers.openai.com/api/reference/resources/models/methods/list §List models; ...` | Valid URL, anchor §`List models` directly corresponds to `## List models`. | **MATCH** |
| **Recheck Cadence** | `line 3` | `recheck: ... 90d — S011, S012, S016, S031 list pages` | Matches standard API reference cadence. | **MATCH** |
| **Claim Summary** | `line 9` | `The OpenAI-shaped model-list routes here do not guarantee residency or readiness: OpenAI's reference lists catalog availability...` | Confirmed: spec states "Lists the currently available models", lacking any residency or execution state. | **MATCH** |
| **Table: Engine / Revision** | `line 19` | `OpenAI reference (S016, OpenAPI commit c396f25f, metadata 2.3.0)` | Pinned against OpenAPI metadata 2.3.0 (`c396f25f2f8112d7761097b7b0217808dc65ddd4`). | **MATCH** |
| **Table: Actual Route** | `line 19` | `GET /models (base /v1/models)` | Endpoint path is `GET /models`; curl example explicitly targets `https://api.openai.com/v1/models`. | **MATCH** |
| **Table: Documented Fields** | `line 19` | `data[].id ("The model identifier, which can be referenced in the API endpoints"); object, created, owned_by, optional shutdown_date; no digest field` | Returns `data: array of Model` containing `id`, `created`, `object`, `owned_by`, `shutdown_date` (optional string or null), and container `object: "list"`. No digest field exists. | **MATCH** |
| **Table: Semantics** | `line 19` | `"Lists the currently available models, and provides basic information about each one such as the owner and availability." — catalog/account availability only; no loaded/running field` | Verbatim quote (18 words); correctly bounds semantics to catalog availability. | **MATCH** |
| **Table: What cannot be concluded** | `line 19` | `Nothing about a local server: not its health, not loaded weights, not that a listed id will execute. The reference shape is not local runtime proof` | Grounded: Upstream reference defines cloud catalog query; provides zero local process/weight/readiness guarantees. | **MATCH** |
| **Failure Case 7** | `line 32` | `7. **OpenAI reference misuse** — shutdown_date and owned_by are catalog lifecycle/ownership fields; reading them as local readiness or loaded weights is unfounded (S016).` | `shutdown_date` is model sunset date ("The date when the model will shut down, or null if not announced"); `owned_by` is owning org. Neither indicates local memory or runtime readiness. | **MATCH** |
| **Alias / Normalization** | `line 39` | `Cross-engine: OpenAI ids are opaque references; id string equality across engines is not content identity. S016's reference schema has no digest field...` | Upstream IDs are strings without content digests or hashing schemes. | **MATCH** |
| **Universal Readiness Limit** | `line 43` | `No universal readiness predicate... the OpenAI reference has no residency field...` | Confirmed: no residency, memory, slot, or worker field exists. | **MATCH** |
| **Cited Sources** | `line 72` | `S016 — OpenAI List models, §List models + §Returns, OpenAPI commit c396f25f2f8112d7761097b7b0217808dc65ddd4, metadata version 2.3.0 (round-10 open 2026-10-19; re-opened 2026-10-20)` | Accurately distinguishes historical round-10 open date (2026-10-19) from round-11 review date (2026-10-20). | **MATCH** |

---

## 3. Analysis: Inventory is Not Local Readiness

1. **Catalog Availability vs. Execution Readiness**:
   - The live specification explicitly states the purpose of `GET /models`: `"Lists the currently available models, and provides basic information about each one such as the owner and availability."`
   - In upstream OpenAI multi-tenant architecture, "availability" denotes account permission and routing capability to accept requests for that identifier.
   - It conveys **zero information** about whether backend compute is warm, whether capacity is currently available, or whether an inference request will succeed without throttling or errors.

2. **Absence of Memory / Hardware Residency Semantics**:
   - The response schema defines only:
     - `id`: string identifier for reference in endpoints
     - `created`: Unix timestamp of model creation
     - `object`: string literal `"model"`
     - `owned_by`: string organization identifier
     - `shutdown_date`: optional string or null (sunset date)
     - `object`: string literal `"list"`
   - There are **no fields** representing VRAM footprint, memory residency, execution state, loaded status, worker readiness, queue saturation, or hardware binding.
   - Unlike Ollama's native `/api/ps` (which exposes `size_vram` and `expires_at`), an OpenAI `/v1/models` endpoint cannot distinguish between an unloaded model registered in catalog metadata and a model actively held in GPU memory.

3. **Implications for Local Runtimes & Probes**:
   - When local engines (e.g., `llama-server`, `vLLM`, `Ollama`) emulate `GET /v1/models`:
     - Presence of an entry in `data[].id` signifies only that the server's router/catalog recognizes the name.
     - In `llama-server` single-model mode, `/v1/models` can return `data[].id` while the model is still loading (`meta` is `null`).
     - In `llama-server` router mode, `/models` returns cached models regardless of whether their status is `unloaded`, `sleeping`, or `loading`.
     - In `Ollama`, `/v1/models` is a compatibility wrapper reflecting available metadata, not the active residency reported by `/api/ps`.
   - Therefore, a `200 OK` from `GET /v1/models` with a matching `id` proves only **inventory presence at sample time**; it does **not** prove local readiness, weight residency, or capacity to execute inference.

---

## 4. Grounded Defects & Observations

### Defect Assessment: None (Zero Grounded Defects Found)
A line-by-line comparison of `corpus/knowledge/served-identity-crosswalk.md` (lines 1, 9, 19, 32, 39, 43, 72) and `corpus/SOURCES.md:28` against `https://developers.openai.com/api/reference/resources/models/methods/list` confirms:
- All quoted strings are verbatim matches against the opened documentation.
- All quotes are strictly $\le 25$ words.
- All locations (§`List models`, §`Returns`, `data: array of Model -> id: string`) exist on the page.
- All schema field names and types (`id`, `created`, `object`, `owned_by`, `shutdown_date`) strictly match.
- Semantic boundaries ("catalog availability only; no loaded/running field", "not its health, not loaded weights, not that a listed id will execute") accurately reflect the specification.
- No repairs or modifications to `corpus/knowledge/served-identity-crosswalk.md` are required.

### What is Already Correct:
1. **Verbatim Fidelity**: The primary quote in line 19 (`"Lists the currently available models, and provides basic information about each one such as the owner and availability."`) exactly replicates the documentation lead sentence.
2. **Schema Completeness**: All returned fields are accounted for; the absence of content digests, execution metrics, and health/readiness indicators is rigorously identified.
3. **Boundary Clarity**: The crosswalk correctly keeps S016 framed as a reference schema shape rather than evidence of local runtime integration (adhering to KQ4 and KQ6).
4. **Historical vs. Live Access Attribution**: The crosswalk explicitly notes both the historical round-10 access (2026-10-19) and the round-11 verification re-open (2026-10-20 UTC).

---

## 5. Tooling Directive Record

- In accordance with the operator tooling directive of 2026-10-19, no packages or tools were installed or upgraded during this reconnaissance slice.
- Tools used: native session tools (`read`, `grep`, `write`).
- Actual install record: **none**.
