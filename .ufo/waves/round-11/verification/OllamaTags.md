# OllamaTags — Advisory Verification Report: Ollama `/api/tags` & S031 Crosswalk

**Author / Seat:** `KamaR11.OllamaTags` (scout)  
**Assigned Target:** Open `https://docs.ollama.com/api/tags`; compare S031 `remote_model`/`remote_host` and crosswalk available inventory/local residency claims; quote/date.  
**Report Path:** `kama-shokunin/.ufo/waves/round-11/verification/OllamaTags.md`  
**Execution Scope:** Static documentation and corpus review; leaf member; no checks, builds, tests, linters, formatters, or runtime probes executed; no implementation, corpus, or fleet files modified.

---

## 1. Public Documentation Opening & Located Citations

- **Assigned URL:** `https://docs.ollama.com/api/tags` (markdown source: `https://docs.ollama.com/api/tags.md`)
- **Verified Date:** `2026-10-20` (actual UTC review date; steered round baseline label `2026-10-19`)
- **Specification Version:** OpenAPI 3.1.0 (`info.title`: "Ollama API", `info.version`: "0.1.0", server: `http://localhost:11434`)
- **Operation:** `GET /api/tags` (`operationId`: `list`)

### Located Verbatim Quotes (≤ 25 words each)

1. **`remote_model` property description**
   - **Location:** `## OpenAPI` → `components.schemas.ModelSummary.properties.remote_model.description`
   - **Verbatim Quote:**
     > "Name of the upstream model, if the model is remote"
   - **Word count:** 10 words.

2. **`remote_host` property description**
   - **Location:** `## OpenAPI` → `components.schemas.ModelSummary.properties.remote_host.description`
   - **Verbatim Quote:**
     > "URL of the upstream Ollama host, if the model is remote"
   - **Word count:** 11 words.

3. **`ModelSummary` schema description**
   - **Location:** `## OpenAPI` → `components.schemas.ModelSummary.description`
   - **Verbatim Quote:**
     > "Summary information for a locally available model"
   - **Word count:** 7 words.

4. **`200 OK` response description**
   - **Location:** `## OpenAPI` → `paths./api/tags.get.responses['200'].description`
   - **Verbatim Quote:**
     > "List available models"
   - **Word count:** 3 words.

5. **`size` property description**
   - **Location:** `## OpenAPI` → `components.schemas.ModelSummary.properties.size.description`
   - **Verbatim Quote:**
     > "Total size of the model on disk in bytes"
   - **Word count:** 9 words.

---

## 2. Evidence Comparison: S031 vs. Documentation vs. Crosswalk

### A. S031 Registry Row Verification (`kama-shokunin/corpus/SOURCES.md:43`)

The registry row for S031 is recorded as:
```markdown
| S031 | Ollama List models (remote entries) — https://docs.ollama.com/api/tags | docs | A | Ollama `/api/tags` remote inventory caveat: available-model membership is not proof of local residency | OpenAPI 3.1.0, info.version 0.1.0; GET /api/tags; ModelSummary `remote_model` and `remote_host` descriptions | supersedes S011 — available inventory may include `remote_model`/`remote_host`; list membership does not prove local residency; `remote_model` names the upstream model and `remote_host` the upstream Ollama URL. | mined | 2026-10-20 | 90d | corpus/knowledge/served-identity-crosswalk.md |
```

- **URL & Anchor Match:** Exactly matches the opened page `https://docs.ollama.com/api/tags` and section `ModelSummary remote_model and remote_host descriptions`.
- **Field Representation:** Accurately states that `remote_model` names the upstream model and `remote_host` names the upstream Ollama URL.
- **Supersession Relationship:** Appropriately targets the limitation of S011 (`corpus/SOURCES.md:23`), which originally defined the scope as "Ollama locally available model inventory". S031 establishes that `/api/tags` membership does not guarantee local residency.

### B. Served-Identity Crosswalk Analysis (`kama-shokunin/corpus/knowledge/served-identity-crosswalk.md`)

The crosswalk incorporates S031 across multiple sections:

1. **Header & Provenance (`:1-3`):**
   - Cites S031 (`https://docs.ollama.com/api/tags §OpenAPI ModelSummary (remote-entry caveat; supersedes S011's local-residency implication)`).
   - Recheck cadence set to `90d`.
2. **Core Claim (`:9`):**
   - States: `"/api/tags reports available inventory that may include remote entries. A MODEL_OK id match therefore proves only that the expected id was listed at sample time — not that weights are loaded, local, or ready to execute."`
   - This directly reflects the documentation: `/api/tags` returns available models, some of which may be remote upstreams.
3. **Prior Coverage Boundary (`:13`):**
   - Explicitly acknowledges that the bare `/api/tags` (available) vs `/api/ps` (running) split is pre-existing in `corpus/knowledge/runtime-health-surface-matrix.md:17` and credits that row.
   - Accurately claims only the addition of remote entries (`remote_model`/`remote_host`, S031), expiry bounds (`expires_at`, S012), alias limits, and router states as new coverage.
4. **Crosswalk Table (`:22`):**
   - Quotes `remote_model`/`remote_host` ("if the model is remote"), `size` ("Total size of the model on disk in bytes"), and `digest` ("SHA256 digest identifier of the model contents").
   - Captures the upstream tension: `tags = "Summary information for a locally available model" (200 description: "List available models"), membership may be remote`.
5. **Grounded Failure Case 6 (`:31`):**
   - Identifies: `"Ollama remote entry — a tag may carry remote_model/remote_host. S010's cloud-model selection example requires a signed-in local server; do not drop that precondition. Available inventory is not proof of local weights (S031/S010)."`
   - Soundly grounds the distinction that catalog availability is decoupled from local weight storage.
6. **Kama Probe Application (`:56`):**
   - Advises keeping `check` metadata-only: `"On Ollama that is availability, not loaded residency (S031/S010)"`.

---

## 3. Grounded Defects & Discrepancies

### Defect 1 — S011 Row In Isolation Still Carries Overstated Scope (Severity: Medium)
- **Path & Line:** `kama-shokunin/corpus/SOURCES.md:23`
- **Observed Text:**
  - `scope`: `"Ollama locally available model inventory, not proof of a loaded model"`
  - `teaches`: `"Lists locally available models with names, digests, and format or quantization metadata; availability is distinct from running state."`
- **Defect:** While `SOURCES.md:7`, `SOURCES.md:57`, `SOURCES.md:67-68`, and `served-identity-crosswalk.md:52` state that S031 supersedes S011's local-residency implication, row S011 itself carries no pointer to S031 and retains the phrase "locally available". A reader or automated parser reading only S011 receives an unamended, potentially misleading claim.
- **Smallest Safe Repair:** In `kama-shokunin/corpus/SOURCES.md:23`, amend `teaches` to append: `(local-residency implication superseded by S031 for remote models)`.

### Defect 2 — Runtime Matrix Mentions Remote Tags Without Citing S031 (Severity: Low)
- **Path & Line:** `kama-shokunin/corpus/knowledge/runtime-health-surface-matrix.md:49-50`
- **Observed Text:**
  - Lines 49–50 state: `"The tags schema also contains remote_model and remote_host: available inventory is not proof of local weights."`
  - However, in line 2 (`source:`) and line 40 (`Cited sources`), only `S011` and `S012` are listed; `S031` is omitted from the citation list.
- **Defect:** The matrix's round-11 correction incorporates the exact fact discovered in S031 (`remote_model`/`remote_host`), but fails to include S031 in its formal citation header/footer, violating strict 1:1 provenance traceability.
- **Smallest Safe Repair:** Add `S031` to `runtime-health-surface-matrix.md:2` and `:40` alongside `S011` and `S012`.

### Defect 3 — Upstream Schema Ambiguity in `size` for Remote Models (Severity: Low / Informational)
- **Path & Line:** `https://docs.ollama.com/api/tags` (`ModelSummary.properties.size`) vs `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md:22, 31`
- **Observed State:** Upstream OpenAPI defines `size` as integer ("Total size of the model on disk in bytes") but does not define its value or behavior when `remote_model` and `remote_host` are populated (e.g. whether it is 0, null, or represents an on-disk sparse/cached manifest).
- **Crosswalk Posture:** The crosswalk correctly infers that an entry in `/api/tags` does not prove local weights (`served-identity-crosswalk.md:31`), but does not explicitly document that the upstream schema leaves the disk size behavior of remote entries unspecified.
- **Smallest Safe Repair:** Under `served-identity-crosswalk.md:22` or `:31`, add a concise note: `"[INFERENCE] Upstream schema does not specify whether size is 0 or cached bytes when remote_model is set."`

---

## 4. What Is Already Correct

1. **Substantiated Remote Lineage Fields:** Live documentation at `https://docs.ollama.com/api/tags` unequivocally confirms the existence and exact descriptions of `remote_model` and `remote_host` in `ModelSummary`.
2. **Honest Boundary Between Availability and Residency:** S031 and `served-identity-crosswalk.md` correctly decouple available model inventory (`/api/tags`) from active loaded residency (`/api/ps`).
3. **No False Novelty Claim on Tags/Ps Split:** The crosswalk rigorously attributes the initial tags/ps distinction to `runtime-health-surface-matrix.md:17` and limits C2 novelty claims to the remote model caveat (S031), expiry bounds (S012), alias ambiguities, and router states.
4. **Registry Conformance:** S031 in `SOURCES.md:43` adheres to all schema rules: valid tier `A`, type `docs`, recheck cadence `90d`, status `mined`, explicit anchor, and grounded `teaches`.
5. **No Runtime Probes or Invasive Calls:** Review was conducted purely via static documentation fetch and corpus analysis, honoring the documentation-only contract.

---

## 5. Tooling Directive Record

- No packages, utilities, or dependencies were installed or upgraded during this review.
- All operations used built-in session tools (`read`, `grep`, `glob`).
- **Actual install record:** `none`.
