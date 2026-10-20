# LlamaModel Verification Report — llama.cpp Single-Model `GET /v1/models` & Nullable Loading

**Seat**: `LlamaModel` (scout)  
**Lane**: `kama-shokunin`  
**Wave**: `kama-round-11-verification`  
**Review Date**: 2026-10-20 UTC  
**Target URL**: `https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md`  
**Target Document**: `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md`  

---

## 1. Godspeed Posture & Axes

1. **Name the axes**: `calibration` (current score 7, round-11 lowest non-retired focus C1) and `operability` (current score 8, C2 coverage focus).
2. **Iterate cheap, in parallel**: Verification inspection of upstream source against crosswalk documentation claims conducted via direct read-only artifact tools without spinning heavy runtime infrastructure or blocking peers.
3. **Keep moves that improve any axis and harm none**: Verify fidelity of factual claims in `served-identity-crosswalk.md` to prevent calibration drift or over-claiming; ensure no implementation/corpus/fleet repo files are mutated.
4. **Don't aim — let the frontier walk itself**: Provide grounded observations, literal quotes, and precise line references so the parent integrator can land exact, defect-free updates.

---

## 2. Upstream Source Evidence & Located Quotes

- **Upstream URL**: `https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md`
- **Pinned File Commit**: `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (dated 2026-10-17T15:20:51Z)
- **Access Date**: 2026-10-20 UTC
- **LSP Availability**: N/A (Markdown documentation and remote GitHub raw text; no language server available for Markdown HTTP resources; literal read/grep tools used as grounded evidence).

### Located Quote 1 (Nullable `meta` during model load)
- **Section**: `## OpenAI-compatible API Endpoints` → `### GET /v1/models: OpenAI-compatible Model Info API` (lines 1252–1254)
- **Verbatim Quote (20 words)**:
  > *"The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)."*

### Located Quote 2 (Model `id` and `--alias` override)
- **Section**: `## OpenAI-compatible API Endpoints` → `### GET /v1/models: OpenAI-compatible Model Info API` (lines 1279–1280)
- **Verbatim Quote (25 words)**:
  > *"By default, model `id` field is the path to model file, specified via `-m`. You can set a custom value for model `id` field via `--alias` argument."*

### Located Quote 3 (`--alias` parameter description)
- **Section**: `### Server-specific params` / Options Table (line 198)
- **Verbatim Quote (11 words)**:
  > *"`-a, --alias STRING` \| set model name aliases, comma-separated (to be used by API)"*

### Located Quote 4 (`--tags` parameter description)
- **Section**: `### Server-specific params` / Options Table (line 199)
- **Verbatim Quote (9 words)**:
  > *"`--tags STRING` \| set model tags, comma-separated (informational, not used for routing)"*

---

## 3. Grounded Verification of Crosswalk Claims

Verification of `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md` across lines 1, 9, 13, 20, 26, 36, 43, 56, and 73:

### 3.1 Observed Facts vs. Upstream Documentation
1. **Single-Element List Guarantee**:
   - `crosswalk.md:20`: *"The documented list always has one element"*
   - `upstream:1252`: *"The returned list always has one single element."*
   - **Verdict**: Fully grounded.

2. **Nullable `meta` Field During Load**:
   - `crosswalk.md:9, 13, 20, 26`: Reports that `meta` can be `null` while the model is still loading (`"for example, while the model is still loading"`).
   - `upstream:1254`: *"The `meta` field can be `null` (for example, while the model is still loading)."*
   - **Verdict**: Verbatim match, fully grounded.

3. **`GET /v1/models` Answers Mid-Load**:
   - `crosswalk.md:9`: *"llama.cpp's `/v1/models` reports 'information about the loaded model' but can answer while that model is still loading"*
   - `crosswalk.md:26`: *"the documented list always has one element and `meta` can be `null` 'for example, while the model is still loading'. [INFERENCE] Therefore identifier listing alone cannot be used as a load-completion guarantee (S001); this is not a runtime observation."*
   - **Verdict**: Fully grounded. The documentation explicitly accounts for `meta` being `null` during load in the response schema of `GET /v1/models`.

4. **Model `id` Derivation & `--alias`**:
   - `crosswalk.md:20`: *"data[].id defaults to the -m path, overridable via --alias"*
   - `crosswalk.md:36`: *"llama.cpp: id defaults to the -m path; --alias overrides it, and -a, --alias STRING is 'set model name aliases, comma-separated (to be used by API)' — the docs do not state which alias lands in id when several are given."*
   - `upstream:1279`: *"By default, model `id` field is the path to model file, specified via `-m`. You can set a custom value for model `id` field via `--alias` argument. For example, `--alias gpt-4o-mini`."*
   - `upstream:198`: `"-a, --alias STRING | set model name aliases, comma-separated (to be used by API)"`
   - **Verdict**: Fully grounded. The upstream documentation indeed documents comma-separated aliases for `--alias`, but defines `data[0].id` as a single string and gives no rule for which element is selected if multiple aliases are passed.

5. **`--tags` vs `--alias` Boundary**:
   - `crosswalk.md:36`: *"`--tags` is 'set model tags, comma-separated (informational, not used for routing)'"*
   - `upstream:199`: `"--tags STRING | set model tags, comma-separated (informational, not used for routing)"`
   - **Verdict**: Verbatim match, fully grounded.

6. **Absence of Content Digest**:
   - `crosswalk.md:20`: *"The documented response has no digest field; the choice among comma-separated aliases is undocumented; alias-to-path mapping is not a documented identity proof"*
   - `upstream:1284-1308`: Response payload contains only `id`, `object`, `architecture` (`input_modalities`, `output_modalities`), `created`, `owned_by`, and `meta` (`vocab_type`, `n_vocab`, `n_ctx_train`, `n_embd`, `n_params`, `size`). No SHA-256 or digest field exists.
   - **Verdict**: Fully grounded.

7. **`GET /props` Model Path Cross-Reference**:
   - `crosswalk.md:20`: Cites `GET /props (model_path)`.
   - `upstream:833, 909, 915`: `GET /props` response includes `"model_path": "../models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"` and documentation notes: `"- model_path - the path to model file (same with -m argument)"`.
   - **Verdict**: Fully grounded.

---

## 4. Separation of Facts, Inference, and Gaps

- **Observed Facts (Documentation Grounding)**:
  - `GET /v1/models` in single-model mode always returns a single-item array in `data`.
  - `meta` is `null` when the model is still loading.
  - `data[0].id` is the literal `-m` path unless `--alias` is supplied.
  - `--alias` is documented in options as comma-separated, but `id` schema is a single string.
  - `--tags` is explicitly informational and not used for routing.
  - `GET /v1/models` contains no cryptographic or content hash/digest.

- **Inference (Properly Marked in Crosswalk)**:
  - In `crosswalk.md:20` and `crosswalk.md:26`, the assertion *"Identifier listing alone is not a load-completion guarantee"* is explicitly tagged with `[INFERENCE]`. This inference is deductively sound from the observed fact that `meta` can be `null` while loading is in progress.
  - In `crosswalk.md:26`, crosswalk states: *"this is not a runtime observation."*

- **Unresolved Gaps**:
  - The upstream documentation does not explain how comma-separated values in `--alias` are mapped to `data[0].id` (e.g., whether the first alias is chosen or comma-joined).
  - The exact conditions under which `GET /v1/models` answers 200 during model loading versus whether `/health` returns 503 are not cross-referenced in upstream documentation.

---

## 5. Grounded Defects, Severity, and Smallest Repair

### Defect 1: S001 Anchor Omission in `corpus/SOURCES.md`
- **Location**: `kama-shokunin/corpus/SOURCES.md:13`
- **Observed Text**:
  `anchor` column lists: `§GET /health, §GET /v1/models, §GET /metrics @ file commit c0fd78626405c6d9b934efef0ec7291fcc20e3d6 (2026-10-17); repo master 4c3c5810 when the metrics section was read`
- **Discrepancy**:
  `served-identity-crosswalk.md:1` and `served-identity-crosswalk.md:73` cite S001 anchors:
  `§GET /v1/models, §GET /models, §Sleeping on idle @ c0fd78626405c6d9b934efef0ec7291fcc20e3d6`
  Additionally, the crosswalk relies on command-line parameter definitions (`-a, --alias` and `--tags`) located under `### Server-specific params` / Options table. `corpus/SOURCES.md:13` does not mention `§GET /models`, `§Sleeping on idle`, or `§Server-specific params`.
- **Severity**: Minor / Registry Conformance Defect.
- **Smallest Repair**:
  Parent integrator should update `corpus/SOURCES.md:13` `anchor` column to:
  `§GET /health, §GET /v1/models, §GET /models, §Sleeping on idle, §Server-specific params @ file commit c0fd78626405c6d9b934efef0ec7291fcc20e3d6 (2026-10-17); repo master 4c3c5810 when the metrics section was read`

### Defect 2: Missing Section Title Anchors for Parameter Flags in Cited Sources
- **Location**: `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md:1, 73`
- **Observed Text**:
  Cites `§GET /v1/models, §GET /models, §Sleeping on idle`.
- **Discrepancy**:
  The flags `-a, --alias` and `--tags` cited in `served-identity-crosswalk.md:36` are located in `### Server-specific params` (lines 198–199), not within `### GET /v1/models`. While `### GET /v1/models` discusses `--alias` in prose (line 1279), the comma-separated specification and `--tags` are documented exclusively in `### Server-specific params`.
- **Severity**: Trivial / Precision improvement.
- **Smallest Repair**:
  In `served-identity-crosswalk.md:1, 73`, expand the section anchor to:
  `§GET /v1/models, §Server-specific params (--alias, --tags), §GET /models, §Sleeping on idle`

---

## 6. What Is Already Correct

1. **Single-model endpoint semantics**: Correctly identified as returning a single model object in `data[]`.
2. **Nullable `meta` field during load**: Accurately captured with exact quotation from line 1254 of the pinned revision.
3. **Readiness vs. Inventory distinction**: Correctly derives that a matching `id` in `GET /v1/models` does not prove loaded readiness since it may return mid-load with `meta: null`.
4. **Parameter behaviors**: Accurately differentiates `-a, --alias` (routing/API identifier) and `--tags` (informational, not used for routing).
5. **No runtime claims made**: Adheres strictly to KQ4/KQ6 by treating all findings as documentation-level analysis without claiming live integration or active endpoint state.

---

## 7. Tooling & Environment Audit

- **Tools installed/updated**: None (0 installs, 0 updates).
- **Environment**: Linux 7.2.3-arch1-3 x86_64; working directory maintained per protocol without mutating implementation, corpus, or fleet files.
- **Write scope**: Strictly restricted to `.ufo/waves/round-11/verification/LlamaModel.md`.
