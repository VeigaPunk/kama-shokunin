# OllamaPs — Advisory Verification Report for Ollama `/api/ps`

**Seat:** `OllamaPs` (scout)  
**Role:** Scout / Source Verifier  
**Lane:** `kama-shokunin`  
**Round:** 11  
**Axes:** `operability + calibration` (local model serving and endpoint health)  
**Target URL:** `https://docs.ollama.com/api/ps`  
**Verification Date:** 2026-10-20 UTC  
**Scope & Lane Bounds:** Leaf member verification report only; no subagent dispatch; no checks, test suites, linters, or builders executed; no modifications to implementation, corpus, or fleet repo.

---

## 1. Tooling Record

- **Installs or upgrades:** None.
- **Actual install record:** `none`. All inspection conducted using existing read tools without external downloads or package installations.

---

## 2. Source Provenance & Document Identity

- **Source URL:** `https://docs.ollama.com/api/ps`
- **Alternate Markdown URL:** `https://docs.ollama.com/api/ps.md`
- **Document Title:** "List running models"
- **OpenAPI Specification Version:** `openapi: 3.1.0`
- **Info Object:** `title: "Ollama API"`, `version: 0.1.0`
- **Route & Operation:** `GET /api/ps` (`operationId: ps`)
- **Server URL:** `http://localhost:11434`
- **Access Date:** 2026-10-20

---

## 3. Located Verbatim Quotes ($\le$ 25 Words)

1. **HTTP 200 Response Description**  
   *Location:* OpenAPI spec under `paths./api/ps.get.responses.200.description`  
   *Quote:*  
   > "Models currently loaded into memory" (5 words)

2. **`expires_at` Schema Property**  
   *Location:* OpenAPI spec under `components.schemas.Ps.properties.expires_at.description`  
   *Quote:*  
   > "Time when the model will be unloaded" (7 words)

3. **`digest` Schema Property**  
   *Location:* OpenAPI spec under `components.schemas.Ps.properties.digest.description`  
   *Quote:*  
   > "SHA256 digest of the model" (5 words)

4. **`context_length` Schema Property**  
   *Location:* OpenAPI spec under `components.schemas.Ps.properties.context_length.description`  
   *Quote:*  
   > "Context length for the running model" (6 words)

5. **`size_vram` Schema Property**  
   *Location:* OpenAPI spec under `components.schemas.Ps.properties.size_vram.description`  
   *Quote:*  
   > "VRAM usage in bytes" (4 words)

6. **Operation Description**  
   *Location:* OpenAPI spec under `paths./api/ps.get.description`  
   *Quote:*  
   > "Retrieve a list of models that are currently running" (8 words)

---

## 4. Verification of Crosswalk Fields (`served-identity-crosswalk.md`)

The newly drafted knowledge entry `corpus/knowledge/served-identity-crosswalk.md` was verified against the upstream documentation at `https://docs.ollama.com/api/ps`:

### A. Field `expires_at`
- **Upstream OpenAPI definition:** Type `string`, description `"Time when the model will be unloaded"`; example ISO-8601 timestamp `'2025-10-17T16:47:07.93355-07:00'`.
- **Crosswalk claims:**
  - `served-identity-crosswalk.md:9`: "Ollama's separate native `/api/ps` does report loaded models, bounded by an unload time"
  - `served-identity-crosswalk.md:13`: "What is new here: ... `/api/ps` loaded state is time-bounded (`expires_at`, S012)"
  - `served-identity-crosswalk.md:22`: lists `expires_at` in ps properties and quotes `expires_at = "Time when the model will be unloaded"`
  - `served-identity-crosswalk.md:29` (Failure Case 4): "**Ollama expiry** — `expires_at` is 'Time when the model will be unloaded': a `/api/ps` hit is a time-bounded observation, not durable readiness (S012)."
  - `served-identity-crosswalk.md:44`: "Ollama `/api/ps` entries bounded by `expires_at`. Neither is a durable readiness guarantee."
  - `served-identity-crosswalk.md:57`: "or Ollama `/api/ps` with its `expires_at` bound — and treat each as a dated observation, never as readiness."
- **Verification verdict:** **CORRECT & FULLY GROUNDED.** The quote is verbatim, and the semantic claim that `/api/ps` yields a time-bounded lease observation rather than permanent inference readiness is strictly grounded.

### B. Loaded Memory (`size`, `size_vram`, "Models currently loaded into memory")
- **Upstream OpenAPI definition:**
  - 200 response description: `"Models currently loaded into memory"`
  - `size`: Type `integer`, description `"Size of the model in bytes"` (example `6591830464`)
  - `size_vram`: Type `integer`, description `"VRAM usage in bytes"` (example `5333539264`)
- **Crosswalk claims:**
  - `served-identity-crosswalk.md:9`: "Ollama's separate native `/api/ps` does report loaded models"
  - `served-identity-crosswalk.md:22`: enumerates `size` and `size_vram` under `ps: name, model, size, digest, details, expires_at, size_vram, context_length`
  - `served-identity-crosswalk.md:22`: quotes `ps = "Models currently loaded into memory"`
  - `served-identity-crosswalk.md:22`: explicitly contrasts with `/api/tags` `size ("Total size of the model on disk in bytes")`
  - `served-identity-crosswalk.md:44`: "Loaded-residency statements exist where documented: ... Ollama `/api/ps` entries bounded by `expires_at`."
- **Verification verdict:** **CORRECT & GROUNDED.** The 200 response description is quoted verbatim. Memory residency fields are accurately enumerated and contrasted with disk size.

### C. Field `digest`
- **Upstream OpenAPI definition:** Type `string`, description `"SHA256 digest of the model"` (example `"c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"`).
- **Crosswalk claims:**
  - `served-identity-crosswalk.md:22`: lists `digest` in `ps` schema.
  - `served-identity-crosswalk.md:22`: notes "joining tags/ps by digest is [INFERENCE] — the pages do not describe the join and prove no on-disk artifact identity".
  - `served-identity-crosswalk.md:38`: quotes `"SHA256 digest of the model"` verbatim and contrasts with `/api/tags` `"SHA256 digest identifier of the model contents"`, identifying the join as `[INFERENCE]`.
  - `served-identity-crosswalk.md:58`: "Never compare names across engines as identity; digests exist only on Ollama's native routes, and their join is a candidate, not a documented mapping."
- **Verification verdict:** **CORRECT & FULLY GROUNDED.** Verbatim quote matches upstream. Marking the tags-to-ps digest join as `[INFERENCE]` adheres strictly to KQ9 and KQ6.

### D. Field `context_length`
- **Upstream OpenAPI definition:** Type `integer`, description `"Context length for the running model"` (example `4096`).
- **Crosswalk claims:**
  - `served-identity-crosswalk.md:22`: enumerates `context_length` among `ps` fields.
  - `served-identity-crosswalk.md:30` (Failure Case 5): references context-size variants created via `ollama create`.
- **Verification verdict:** **CORRECT & GROUNDED.** Field name and type match the OpenAPI specification.

---

## 5. Grounded Defects & Recommendations

### Defect 1: Minor Omission of `size_vram` Schema Description Quote in Crosswalk Table
- **Location:** `corpus/knowledge/served-identity-crosswalk.md:22`
- **Severity:** Low (Informational / Precision defect)
- **Description:** In the table row for Ollama (`:22`), the entry quotes the `/api/tags` description for `size` (`"Total size of the model on disk in bytes"`), but lists `size` and `size_vram` for `/api/ps` without citing their schema property descriptions (`"Size of the model in bytes"` and `"VRAM usage in bytes"`).
- **Smallest repair:** In `corpus/knowledge/served-identity-crosswalk.md:22`, expand the `ps:` field list to include the exact descriptions:
  `size ("Size of the model in bytes"), size_vram ("VRAM usage in bytes")`
  This makes the contrast between disk footprint and active VRAM allocation immediately evident from the quoted schema text.

---

## 6. What Is Already Correct

1. **Exact S012 Citation & Scope:** `corpus/knowledge/served-identity-crosswalk.md:1,76` accurately anchors S012 to `https://docs.ollama.com/api/ps §OpenAPI /api/ps`, with info.version `0.1.0` and OpenAPI `3.1.0`.
2. **Prior Coverage Attribution:** Section `## Prior coverage` (`:11-14`) properly credits `runtime-health-surface-matrix.md:17` for the basic `tags` (available) vs `ps` (running) split, claiming only the new distinctions (`expires_at`, digest join limits, remote tags, and failure modes).
3. **Discipline on Negative Assertions:** The crosswalk strictly distinguishes between what the vendor documentation states (running models, memory, expiry) and what it does **not** state (no readiness guarantee, no documented relational foreign key join on `digest`, no health check).
4. **Honest `[INFERENCE]` Tagging:** Where logical extensions are made (such as attempting to join available tags and running ps records via SHA256 digest), the crosswalk labels them as `[INFERENCE]`.
5. **No Runtime Freshness Overclaim:** The crosswalk explicitly notes in `verified-at:` (`:2`) and section `## What cannot be concluded` (`:46`) that no local Ollama runtime was contacted, preserving calibration integrity.
