# Verification Report: llama.cpp Router Mode, `GET /models`, and Sleeping on Idle (`LlamaRouter.md`)

- **Seat**: `LlamaRouter` (Role: `scout`, Leaf member)
- **Lane**: `kama-shokunin`
- **Round**: 11
- **Axes**: `calibration + operability` (local model serving and endpoint health)
- **Target URL**: `https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md`
  - Upstream file commit: `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (2026-10-17T15:20:51Z)
  - GitHub blob view: `https://github.com/ggml-org/llama.cpp/blob/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md`
- **Access Date**: `2026-10-20` (Actual UTC review timestamp; steered round-10 label is `2026-10-19`)
- **Evaluation Subject**: `corpus/knowledge/served-identity-crosswalk.md` (lines 1, 9, 13, 21, 27, 36, 43, 44, 56–57, 73) and `corpus/SOURCES.md:13` (S001)
- **Scope & Lane Bounds**: Advisory verification report only; leaf member with no subagent delegation, no execution of check/build/test commands, and zero modifications to implementation, corpus, or fleet repositories.

---

## 1. Tooling Record

- In accordance with the operator tooling directive of 2026-10-19, no packages or tools were installed or upgraded during this verification slice.
- Tools used: native session inspection tools (`read`, `grep`, `write`).
- Actual install record: **none**.

---

## 2. Located Verbatim Quotes ($\le 25$ Words)

### Quote 1: Purpose & Description of `GET /models`
- **Location**: `tools/server/README.md` line 1992 (§ `### GET /models: List available models`)
- **Verbatim Quote**:
  > "Listing all models in cache. The model metadata will also include a field to indicate the status of the model:"
- **Word Count**: 19 words
- **Access Date**: 2026-10-20

### Quote 2: Forwarding to Router `/v1/models` Upon Load
- **Location**: `tools/server/README.md` line 2026 (§ `### GET /models: List available models` -> Note 2)
- **Verbatim Quote**:
  > "When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`. This includes metadata about the model and the runtime instance."
- **Word Count**: 24 words
- **Access Date**: 2026-10-20

### Quote 3: Starting Server in Router Mode
- **Location**: `tools/server/README.md` lines 1858–1859 (§ `## Using multiple models`)
- **Verbatim Quote**:
  > "To start in router mode, launch `llama-server` without specifying any model: `llama-server`"
- **Word Count**: 12 words
- **Access Date**: 2026-10-20

### Quote 4: Memory Unloading in Sleep Mode
- **Location**: `tools/server/README.md` line 2335 (§ `## Sleeping on Idle`)
- **Verbatim Quote**:
  > "When the server enters sleep mode, the model and its associated memory (including the KV cache) are unloaded from RAM to conserve resources."
- **Word Count**: 23 words
- **Access Date**: 2026-10-20

### Quote 5: Exempt Monitoring Endpoints During Sleep
- **Location**: `tools/server/README.md` lines 2339–2340 (§ `## Sleeping on Idle`)
- **Verbatim Quote**:
  > "Note that the following endpoints are exempt from being considered as incoming tasks. They do not trigger model reloading and do not reset the idle timer:"
- **Word Count**: 24 words
- **Access Date**: 2026-10-20

### Quote 6: Retrieving Sleep Status via `/props`
- **Location**: `tools/server/README.md` line 2337 (§ `## Sleeping on Idle`)
- **Verbatim Quote**:
  > "The sleeping status can be retrieved from the `GET /props` endpoint (or `/props?model=(model_name)` in router mode)."
- **Word Count**: 16 words
- **Access Date**: 2026-10-20

---

## 3. Grounded Verification of Crosswalk Router & Readiness Assertions

The newly drafted knowledge entry `corpus/knowledge/served-identity-crosswalk.md` was evaluated against the pinned upstream documentation (`tools/server/README.md` @ commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`):

### A. Operational Modes and Launch Trigger
- **Upstream specification**: `llama-server` operates in single-model mode when passed `-m, --model <path>`, and in router mode when launched without specifying any model (`llama-server`, lines 1858–1860).
- **Crosswalk assertion** (`served-identity-crosswalk.md:21`): Cites `llama.cpp router mode (S001; launch without '-m')`.
- **Verdict**: **MATCH & VERIFIED.** The launch condition is accurately captured.

### B. Route Inventory in Router Mode
- **Upstream specification**: Router mode exposes `GET /models` to list all available cached and configured models. Only when a model instance is actively loaded is its info forwarded to `GET /v1/models` (lines 2026–2027). Sleeping status is retrieved via `GET /props?model=(model_name)` (line 2337).
- **Crosswalk assertion** (`served-identity-crosswalk.md:21`): Documents routes as `GET /models (cache listing); /v1/models (forwarded per loaded model); GET /props?model= for sleeping status`.
- **Verdict**: **MATCH & VERIFIED.** The distinct roles of native router catalog (`GET /models`), forwarded loaded instance info (`GET /v1/models`), and model-specific properties (`GET /props?model=`) match upstream.

### C. Router Model Identifier and Physical Path
- **Upstream specification**: In `GET /models`, each element of `data[]` provides `id` (e.g. `"ggml-org/gemma-3-4b-it-GGUF:Q4_K_M"` or preset identifier) and a separate `path` field pointing to the physical GGUF file on disk (`path: "/Users/.../..."`, lines 1997–1998).
- **Crosswalk assertion** (`served-identity-crosswalk.md:21, 36`): States `id is the preset/repo tag with a separate path field` and `Router ids are preset/repo tags plus a separate path; the -m-path rule does not transfer (S001)`.
- **Verdict**: **MATCH & VERIFIED.** Contrasts router `id` cleanly against the single-model convention where `id` defaults to the literal `-m` file path.

### D. Router Status Lifecycle (`status.value`)
- **Upstream specification**: Upstream lines 2070–2120 document the exact variants of `status.value`:
  1. `"unloaded"` (present in cache/preset/dir, not resident in RAM; optional `failed: true` and `exit_code: 1` upon execution failure)
  2. `"loading"` (model process launch/load in-flight, carries `args`)
  3. `"loaded"` (model active and resident in memory, carries `args`)
  4. `"sleeping"` (idle timeout reached; model memory and KV cache unloaded from RAM, carries `args`)
  5. `"downloading"` (background file retrieval active, carries `progress` byte map)
  6. `"incomplete"` (interrupted/partial download on disk, `args: []`)
- **Crosswalk assertion** (`served-identity-crosswalk.md:21`): Enumerates `status.value is loaded / unloaded / loading / sleeping / downloading / incomplete`.
- **Verdict**: **MATCH & VERIFIED.** All six documented status strings are accurately and exhaustively transcribed.

### E. Sleeping on Idle Semantics & Readiness Decoupling
- **Upstream specification**:
  - Activated via `--sleep-idle-seconds SECONDS` (line 249, 2333).
  - Unloads model weights and KV cache from RAM to conserve host resources (line 2335).
  - Incoming tasks automatically trigger reloading (line 2335).
  - Monitoring endpoints (`GET /health`, `GET /props`, `GET /models`, `GET /metrics`) are explicitly exempt: *"They do not trigger model reloading and do not reset the idle timer"* (lines 2339–2343).
- **Crosswalk assertions**:
  - `line 21`: Quotes `"They do not trigger model reloading and do not reset the idle timer", so a 200 does not wake a sleeping model; the single-model -m-path id rule must not be applied to router ids`.
  - `line 27` (Failure Case 2): `llama.cpp router sleep/unload — /models lists a model with status.value: "unloaded" or "sleeping" while /health still answers, because the exempt routes "do not trigger model reloading and do not reset the idle timer"; a health 200 names no model (S001)`.
  - `lines 43–44`: Asserts no universal readiness predicate exists: router lists include unloaded/sleeping models; `status.value == "loaded"` and `/props` sleeping state are dated observations, not permanent readiness.
  - `line 57`: Directs kama to treat `status.value == "loaded"` or `/props` sleeping state as dated observations, never as universal readiness.
- **Verdict**: **MATCH & FULLY GROUNDED.** Upstream proves that `GET /health` returning `200 OK` on a router instance does **not** indicate that any given model is resident in memory or ready for execution. A sleeping or unloaded model remains dormant across health probes.

---

## 4. Grounded Defects & Precision Recommendations

### Defect 1: Omission of Router Sections in `corpus/SOURCES.md:13` Anchor Field
- **Location**: `kama-shokunin/corpus/SOURCES.md:13` (S001 row)
- **Severity**: Low (Anchor precision defect)
- **Description**: The S001 row in `corpus/SOURCES.md:13` lists its section anchors as:
  `§GET '/health', §GET '/v1/models', §GET '/metrics' @ file commit c0fd78626405c6d9b934efef0ec7291fcc20e3d6`
  However, `corpus/knowledge/served-identity-crosswalk.md:1, 73` explicitly anchors S001 to:
  `§GET '/v1/models', §GET '/models', §Sleeping on idle @ c0fd78626405c6d9b934efef0ec7291fcc20e3d6`
  While `SOURCES.md:13` added `corpus/knowledge/served-identity-crosswalk.md` to its `used-by` column, the anchor cell was not updated to reflect the newly mined sections (`§GET '/models'` and `§Sleeping on idle`).
- **Smallest repair**: In `corpus/SOURCES.md:13`, update the anchor cell from:
  `§GET '/health', §GET '/v1/models', §GET '/metrics'`
  to:
  `§GET '/health', §GET '/v1/models', §GET '/models', §Sleeping on idle, §GET '/metrics'`

### Defect 2: Minor Scope Narrowing in Crosswalk Table Column 2 (`cache listing`)
- **Location**: `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md:21`
- **Severity**: Low (Informational / Scope wording precision)
- **Description**: In the table row for router mode (`:21`), column 2 describes `GET /models` as `GET /models (cache listing)`. While line 1992 of the upstream README says *"Listing all models in cache"*, lines 1864–1870 define three distinct sources for router models:
  1. Cached models (`LLAMA_CACHE`)
  2. Custom model directories (`--models-dir`)
  3. Custom presets (`--models-preset`)
  Calling it strictly a "cache listing" might lead an analyst to infer that models loaded from local directories or preset files are omitted from `GET /models`, which is not the case (they appear with their preset or local path identity).
- **Smallest repair**: In `corpus/knowledge/served-identity-crosswalk.md:21`, expand the parenthetical descriptor from `GET /models (cache listing)` to `GET /models (cache/preset/dir inventory)`.

---

## 5. What Is Already Correct

1. **Pinned Upstream Commit Fidelity**: All inspections match the pinned commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (2026-10-17).
2. **Verbatim Quote Accuracy**: All cited quotes (Quotes 1 through 6) are strictly $\le 25$ words, verified verbatim against the pinned source text, and dated.
3. **Six-State Status Accuracy**: The lifecycle enumeration (`loaded`, `unloaded`, `loading`, `sleeping`, `downloading`, `incomplete`) accurately matches the upstream specification without hallucinated states.
4. **Readiness Decoupling**: The crosswalk correctly captures that router `/health` answers at the process supervisor level and does not represent model weight residency or execution readiness.
5. **Exempt Route Rigor**: The crosswalk grounds its failure analysis on the fact that `/health`, `/props`, `/models`, and `/metrics` do not trigger model reloading or reset idle timers, precluding false claims that a health probe proves inference readiness.
6. **Calibration & KQ Compliance**: Strictly adheres to KQ1 (no live claims), KQ4 (docs are not integration), and KQ6 (revision-pinned documentation statements). No local runtime was contacted.
