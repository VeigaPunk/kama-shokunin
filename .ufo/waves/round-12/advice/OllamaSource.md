# OllamaSource — Advisory Scout Report: Ollama `/api/tags` Schema & S031 Boundary

**Seat:** `KamaR12.OllamaSource` (scout)  
**Assigned Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC (actual documentation access date)  
**Assigned Target:** Open `https://docs.ollama.com/api/tags` for S031 `remote_model` and `remote_host` actual schema; report located quote $\le 25$ words, source-vs-inference boundary, and actual access date. No runtime behavior claim.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/advice/OllamaSource.md`  
**Execution Constraints:** Leaf scout seat; no subagent dispatch; static documentation review only; no verification runs, test executions, or runtime mutations.

---

## 1. Named Axes (Godspeed Posture)

1. **Calibration ($7 \to 7$, $\Delta 0$):** Lowest non-retired assigned axis ($7 < 8$). Rigorously anchors historical provenance and schema evidence to upstream documentation; explicitly demarcates verbatim source facts from learner inferences (addressing verifier defect D4 and `QUALITY.md` criteria KQ11–KQ14); prohibits ungrounded claims or scalar inflation.
2. **Operability ($8 \to 8$, $\Delta 0$):** Preserved without harm. No daemon process, local socket (`http://localhost:11434`), or live runtime service was probed; no probe implementation changed.

---

## 2. Upstream Document & OpenAPI Schema Verification

- **Document URL:** `https://docs.ollama.com/api/tags`
- **Actual Access Date:** `2026-10-20` (UTC)
- **Document Title:** `List models` ("Fetch a list of models and their details")
- **Specification Identity:** OpenAPI 3.1.0 (`info.title`: "Ollama API", `info.version`: "0.1.0", `servers[0].url`: "http://localhost:11434")
- **Operation:** `GET /api/tags` (`operationId`: `list`, summary: "List models")
- **Schema Hierarchy:**
  - `paths./api/tags.get.responses['200'].content['application/json'].schema`: `$ref: '#/components/schemas/ListResponse'`
  - `components.schemas.ListResponse.properties.models`: array of `$ref: '#/components/schemas/ModelSummary'`
  - `components.schemas.ModelSummary`: object describing model entries returned by the tag list.

### Extracted `ModelSummary` Schema Properties
```yaml
ModelSummary:
  type: object
  description: Summary information for a locally available model
  properties:
    name:
      type: string
      description: Model name
    model:
      type: string
      description: Model name
    remote_model:
      type: string
      description: Name of the upstream model, if the model is remote
    remote_host:
      type: string
      description: URL of the upstream Ollama host, if the model is remote
    modified_at:
      type: string
      description: Last modified timestamp in ISO 8601 format
    size:
      type: integer
      description: Total size of the model on disk in bytes
    digest:
      type: string
      description: SHA256 digest identifier of the model contents
    details:
      type: object
      description: Additional information about the model's format and family
```

---

## 3. Located Verbatim Quotes ($\le 25$ Words Each)

All quotes below are verbatim from `https://docs.ollama.com/api/tags` (OpenAPI specification), cited with exact JSON/YAML schema paths and word counts:

1. **`remote_model` Property Description:**
   - **Schema Path:** `components.schemas.ModelSummary.properties.remote_model.description`
   - **Verbatim Quote:**
     > "Name of the upstream model, if the model is remote"
   - **Word Count:** 10 words.

2. **`remote_host` Property Description:**
   - **Schema Path:** `components.schemas.ModelSummary.properties.remote_host.description`
   - **Verbatim Quote:**
     > "URL of the upstream Ollama host, if the model is remote"
   - **Word Count:** 11 words.

3. **`ModelSummary` Top-Level Description:**
   - **Schema Path:** `components.schemas.ModelSummary.description`
   - **Verbatim Quote:**
     > "Summary information for a locally available model"
   - **Word Count:** 7 words.

4. **Response Status 200 Description:**
   - **Schema Path:** `paths./api/tags.get.responses['200'].description`
   - **Verbatim Quote:**
     > "List available models"
   - **Word Count:** 3 words.

---

## 4. Source-vs-Inference Boundary Analysis (Grounding D4 & KQ11–KQ14)

Per verifier spotcheck defect D4 (`corpus/lessons/round-11-verifier-spotcheck.md:221-225`) and `SOURCES-CONTRACT-v1`, clear demarcation between directly observed source text and analytical inference is contractually required.

### 4.1 Direct Source Observations (Observed Ground Truth)
1. **Field Definitions Exist Upstream:** The published OpenAPI 3.1.0 schema for `GET /api/tags` explicitly defines both `remote_model` and `remote_host` under `ModelSummary`.
2. **Conditional Descriptions:** Upstream defines each field as conditional: `"if the model is remote"`.
3. **Upstream Summary Text Retained:** Upstream explicitly retains the top-level description `"Summary information for a locally available model"` on `ModelSummary` and `"List available models"` on the 200 response.
4. **Behavioral Silence on `size`:** The schema specifies `size` as `"Total size of the model on disk in bytes"` (integer) but provides no schema constraint or prose specifying whether `size` is `0`, `null`, or represents cached metadata when `remote_model` is populated.

### 4.2 Inferences Drawn by the Lane (`[INFERENCE]`)
1. **Available Inventory $\ne$ Proof of Local Disk Residency:**  
   Because `ModelSummary` contains fields identifying an upstream model (`remote_model`) and upstream host (`remote_host`) when a model is remote, `/api/tags` returns available inventory that can include non-local upstreams. Therefore, an entry in `/api/tags` does not constitute proof that model weights reside on local disk.  
   *(Boundary note: Upstream does not state "membership is not proof of local residency" verbatim; this is an analytical inference drawn from the presence of `remote_model`/`remote_host`).*
2. **Registry Supersession vs. Upstream Documentation Change:**  
   In `corpus/SOURCES.md:43`, the statement `supersedes S011` denotes **lane-registry supersession** under `SOURCES-CONTRACT-v1`. It establishes that within `kama-shokunin`'s knowledge corpus, S031 supersedes the naive "local residency" implication previously drawn from S011. It does **not** assert that Ollama upstream altered its documentation, deprecated S011, or withdrew the text `"locally available"`.

---

## 5. Explicit Disclaimer: No Runtime Behavior Claim

- **Zero Runtime Probes Executed:** No requests were dispatched to `http://localhost:11434/api/tags` or any live Ollama daemon.
- **Documentation Contract Only:** These findings characterize the public OpenAPI documentation published at `https://docs.ollama.com/api/tags` as accessed on 2026-10-20 UTC.
- **No Claims on Deployed Binary Behavior:** This report does not assert how an installed Ollama binary on this host or any other host actually populates `remote_model` or `remote_host`, handles offline remote models, or behaves during network partitions.

---

## 6. Verification Checks for L1 (Main Integrator)

As a leaf scout, no verification, test runner, or linter was executed. Main L1 should verify:

1. **Quote Fidelity Check:**
   Verify that quotes cited in this report match `https://docs.ollama.com/api/tags` OpenAPI block verbatim:
   - `remote_model`: "Name of the upstream model, if the model is remote" (10 words $\le 25$).
   - `remote_host`: "URL of the upstream Ollama host, if the model is remote" (11 words $\le 25$).
2. **Corpus S031 Alignment:**
   Verify that `corpus/SOURCES.md` S031 row (line 43) and `corpus/knowledge/served-identity-crosswalk.md` citations match the extracted schema paths and access date `2026-10-20`.
3. **D4 Conformance:**
   Verify that `corpus/knowledge/served-identity-crosswalk.md` explicit `[INFERENCE]` label and S031 registry supersession distinction (worked by `InferenceClarify`) align with Section 4 of this report.

---

## 7. Tooling Record

- **Tools Installed / Updated:** None.
- **Channel / Gate:** N/A.
