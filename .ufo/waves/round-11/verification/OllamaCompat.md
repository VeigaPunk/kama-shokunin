# OllamaCompat — Verification of Ollama OpenAI Compatibility Crosswalk Assertions (S010)

**Scope:** Static source verification of `https://docs.ollama.com/api/openai-compatibility` against assertions in `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md` and registry entries in `kama-shokunin/corpus/SOURCES.md`. No test runs, execution checks, or implementation edits were performed.

---

## 1. Source Identification & Located Quotes (<= 25 words)

- **Assigned URL**: `https://docs.ollama.com/api/openai-compatibility` (alternate markdown: `https://docs.ollama.com/api/openai-compatibility.md`)
- **Upstream Source**: `docs/api/openai-compatibility.mdx` in repository `ollama/ollama`
- **Upstream Commit**: `c1737589973d5cefd676ef16eb43835663540035` (`2026-09-23`)
- **Access Timestamp**: `2026-10-20` (UTC review date)
- **Relevant S-Row**: S010 (`corpus/SOURCES.md:22`)

### Located Quotes

1. **Alias `cp` mechanism**:
   - *Location*: Section `## Models` -> `### Default model names on a local server`
   - *Quote*: "For tooling that relies on default OpenAI model names such as `gpt-3.5-turbo`, use `ollama cp` to copy an existing model name to a temporary name:" (24 words)
2. **`/v1/models` metadata (`created`)**:
   - *Location*: Section `## Endpoints` -> `### /v1/models` -> `#### Notes`
   - *Quote*: "`created` corresponds to when the model was last modified" (8 words)
3. **`/v1/models` metadata (`owned_by`)**:
   - *Location*: Section `## Endpoints` -> `### /v1/models` -> `#### Notes`
   - *Quote*: "`owned_by` corresponds to the ollama username, defaulting to `\"library\"`" (8 words)
4. **Cloud signed-in precondition (Local server)**:
   - *Location*: Section `## Local server usage`
   - *Quote*: "To use cloud models through this server, [sign in to Ollama](/api/authentication#signing-in)." (11 words)
5. **Cloud model selection precondition**:
   - *Location*: Section `## Models`
   - *Quote*: "Through a signed-in local server, select a cloud model such as `gemma4:cloud`." (12 words)
6. **OpenAI compatibility surface boundary**:
   - *Location*: Section `# OpenAI compatibility`
   - *Quote*: "Ollama supports a subset of the OpenAI API." (8 words)

---

## 2. Verification of Crosswalk Assertions

### A. Alias `cp` Semantics
- **Crosswalk assertion (`served-identity-crosswalk.md:22,30`)**:
  `ollama cp` copies "an existing model name to a temporary name" to satisfy tooling expecting default OpenAI model names. Whether the copy keeps the original digest is not documented; therefore, a name match can match a name that maps to a different or duplicated artifact, and digest joins remain an inference candidate.
- **Source verification**:
  `https://docs.ollama.com/api/openai-compatibility` §Models explains that `ollama cp llama3.2 gpt-3.5-turbo` creates a temporary name for tooling expecting standard OpenAI identifiers, and that this new name is passed to the `model` parameter of `/v1/chat/completions`. The page provides zero documentation on whether `ollama cp` shares the original blob/manifest SHA-256 digest, creates a symlink/alias pointer, or duplicates model data on disk.
- **Finding**: **Verified**. The assertion in `served-identity-crosswalk.md:30` is grounded in source omission.

### B. `/v1/models` and `/v1/models/{model}` Metadata
- **Crosswalk assertion (`served-identity-crosswalk.md:9,22,43-44`)**:
  `/v1/models` documents metadata only (`created`, `owned_by`) without loaded-state or memory residency guarantees. A listed model proves only that the identifier was cataloged at sample time, not that weights are loaded, local, or ready to execute.
- **Source verification**:
  Under `## Endpoints` -> `### /v1/models` and `### /v1/models/{model}`, the documentation provides only two bulleted notes: `created` (modification timestamp) and `owned_by` (Ollama username, default `"library"`). There are no response fields indicating memory footprint, VRAM allocation, residency status, context length, or operational readiness.
- **Finding**: **Verified**. The crosswalk's assertion that `/v1/models` documents only basic catalog metadata and does not guarantee residency is accurate and grounded.

### C. Cloud Model Signed-in Precondition
- **Crosswalk assertion (`served-identity-crosswalk.md:31,56`)**:
  Selecting cloud models via a local server requires a **signed-in local server** precondition (`S010`). Available inventory is not proof of local weights.
- **Source verification**:
  `https://docs.ollama.com/api/openai-compatibility` explicitly states in `## Local server usage`: "To use cloud models through this server, [sign in to Ollama](/api/authentication#signing-in)" and in `## Models`: "Through a signed-in local server, select a cloud model such as `gemma4:cloud`". Direct cloud requests bypass the local server using `api_key=os.environ["OLLAMA_API_KEY"]` at `https://ollama.com/v1`.
- **Finding**: **Verified**. The crosswalk's requirement to preserve the signed-in precondition for local-server cloud model routing is grounded verbatim.

---

## 3. Grounded Defects & Smallest Repairs

### Low — Anchor Path Precision in Crosswalk Header and Citations
- **Exact Path & Lines**: `corpus/knowledge/served-identity-crosswalk.md:1,74`
- **Defect**: Line 1 cites `§Endpoints `/v1/models` + §Models`, and line 74 cites `§Endpoints `/v1/models` Notes + §Models + §Default model names`. On the actual documentation page, `Default model names on a local server` is an H3 subsection (`### Default model names on a local server`) nested within H2 `## Models`.
- **Severity**: Low (cosmetic anchor naming precision).
- **Smallest Repair**: Update citation at line 74 to read: `§Endpoints ### /v1/models Notes + §Models ### Default model names on a local server`.

### Low — Omission of `/v1/models/{model}` in Metadata Description Column
- **Exact Path & Lines**: `corpus/knowledge/served-identity-crosswalk.md:22` (table column 3)
- **Defect**: The "Actual model routes" column lists both `/v1/models` and `/v1/models/{model}`, but column 3 only mentions `/v1/models` when explaining that "`created` corresponds to when the model was last modified". In S010, the exact same notes apply to `### /v1/models/{model}`.
- **Severity**: Low (clarity).
- **Smallest Repair**: Change text in column 3 to read: "`/v1/models` and `/v1/models/{model}` document only that `created` corresponds to when the model was last modified and `owned_by` corresponds to the ollama username, defaulting to `\"library\"`".

---

## 4. What Is Already Correct

1. **Separation of Availability vs. Residency**:
   `served-identity-crosswalk.md:22` correctly contrasts Ollama's available model inventory (`/api/tags`, `/v1/models`) with its loaded model state (`/api/ps`).
2. **Aliasing Boundary**:
   The crosswalk accurately documents that `ollama cp` creates temporary alias names for OpenAI client tooling compatibility, and cautions that matching a name does not prove artifact identity.
3. **No Phantom Health Surface**:
   The crosswalk and `corpus/SOURCES.md:22` correctly refrain from attributing any health, liveness, or readiness semantics to `GET /v1/models` or the Ollama OpenAI compatibility surface.
4. **Precondition Integrity**:
   The crosswalk preserves the signed-in requirement for cloud models on a local server, preventing false assumptions of local model weight presence.
5. **Quality Rule Adherence (KQ1–KQ10)**:
   The crosswalk presents S010 as a documented API surface specification without claiming that Ollama is currently running locally or that documentation equates to runtime integration.

---

## 5. Tooling Directive Record

- **Installed or Upgraded Tools**: None.
- All inspections were performed using read-only environment tools (`read`, `glob`, `grep`).
- **Actual install record**: `none`.
