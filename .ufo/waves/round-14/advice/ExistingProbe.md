# ExistingProbe — Mapping kama-probe Normalization vs Ollama Exact-Name Capture Classifier

**Seat:** `KamaR14.ExistingProbe` (UFO-FSD scout, leaf member)  
**verified-at:** actual review 2026-10-20 (UTC)  
**Scope:** Map existing `tools/kama-probe.sh` extraction and normalization mechanics and identify why the new C1 offline Ollama evidence capture classifier (`tools/kama-ollama-evidence.py`) must NOT reuse GGUF normalization.  
**Execution:** Read-only inspection of repository contracts, code, and knowledge corpus. No checks, tests, builds, smoke runs, or runtime commands executed. No network or endpoint access. Leaf bounds preserved: no subagent dispatch.  
**Tooling:** None installed or upgraded (RULES.md reviewed; no external tools required).

---

## 1. Executive Summary

In `tools/kama-probe.sh`, served-model identity comparison and persistence use a heuristic normalization routine (`normalize_id`: basename extraction via `s##*/` followed by stripping one trailing `.gguf`). This heuristic was engineered specifically for single-model `llama.cpp` serving over HTTP, where the runtime returns full local filesystem paths in `/v1/models` (e.g. `/scratch/models/.../model.gguf`) while consumer configurations pin clean model names.

In contrast, the new round-14 capability (`tools/kama-ollama-evidence.py`) performs offline reconciliation of Ollama exported metadata (`/api/tags` and `/api/ps`). Reusing GGUF normalization for Ollama evidence capture is architecturally unsound, semantically invalid, and a direct contract violation:
1. **Namespace Collapse:** Ollama identifiers follow structured repository/namespace paths (`[host/][namespace/]model[:tag]`). Basename stripping collapses distinct namespaces and remote hosts into bare names, creating cross-namespace collisions and model spoofing.
2. **Blob Architecture vs Bare Files:** Ollama manages models as content-addressed multi-layer blobs referenced by logical tags, not bare filesystem `.gguf` files. Stripping `.gguf` mutates explicit user tags and custom Modelfile names.
3. **Cryptographic Digests Replace Filename Heuristics:** Ollama provides SHA-256 content digests (`digest`) on both `/api/tags` and `/api/ps`. Exact metadata correspondence is established via cryptographic digest equality, rendering filename-stripping heuristics obsolete and dangerous.
4. **Remote Inventory Integrity:** Ollama tags distinguish remote/cloud models via `remote_model` and `remote_host` (S031). Stripping host/namespace paths risks conflating remote inventory with local models.
5. **Fail-Closed Calibration (KQ17):** Strict calibration demands that any discrepancy in name, tag, namespace, or case fail closed as `unknown` (exit 2) or `identity_conflict` (exit 1), rather than silently succeeding via heuristic normalization.

---

## 2. Grounded Mapping of Existing `kama-probe.sh` Extraction & Normalization

### 2.1 Extraction Precedence (`served_ids`)
In `tools/kama-probe.sh:324-369`, extraction from `/v1/models` JSON responses follows a strict priority cascade where the first non-empty group wins:
```text
data[].id -> models[].id -> models[].name -> models[].model -> top-level id
```
- In Python mode (`tools/kama-probe.sh:349-358`), each group is extracted as non-empty strings, deduplicated via `dict.fromkeys(g)`, and printed.
- In grep fallback mode (`tools/kama-probe.sh:363-368`), `"id"` takes precedence over `"model"`/`"name"`.
- As recorded in `SKILL.md:152-157`, `llama.cpp` historical runtime responses lacked `models[].id`, requiring fallback to `models[].name` or `data[].id`.

### 2.2 Normalization Implementation (`normalize_id`)
In `tools/kama-probe.sh:371`:
```bash
# drop directory, strip ONE trailing .gguf
normalize_id() { local s=${1-}; s=${s##*/}; s=${s%.gguf}; printf '%s' "$s"; }
```
- **Basename extraction (`s=${s##*/}`):** Strips everything up to and including the final slash `/`.
- **Extension stripping (`s=${s%.gguf}`):** Strips exactly one trailing literal `.gguf` (lowercase).
- **Case preservation:** Does **not** fold case.

### 2.3 Comparison Semantics (`model_matches`)
In `tools/kama-probe.sh:374-388`:
- Both the configured `expected` ID and each extracted `served` ID are passed through `normalize_id`.
- If normalization produces an empty string (`[ -n "$exp_n" ] || return 2`), the check aborts with status 2, mapping to `MODEL_MISMATCH` with reason `unresolvable-id`.
- Matching is evaluated via exact case-sensitive string equality: `[ "$sn" = "$exp_n" ]`.
- A single matching served ID yields success (exit 0); failure to match any served ID yields exit 1 (`MODEL_MISMATCH`).

### 2.4 Persistence Hygiene (`served_persist`)
In `tools/kama-probe.sh:925-926, 959-971`:
- Persisted entries in `latest.tsv` and `DELTA.md` store normalized basenames (`normalize_id "$(persist_clean "$p")"`).
- The explicit design rationale (`tools/kama-probe.sh:925-926`) was:
  > `served_model compares PERSISTED form (normalised basename) on both sides — a raw GGUF-path change that keeps the basename is not an identity change.`
- This ensured that moving model weights between host directories (e.g. `/scratch/models/...` to `/mnt/models/...`) did not register as a model identity transition.

---

## 3. Why Ollama Exact-Name Capture Classifier MUST NOT Reuse GGUF Normalization

The round-14 offline classifier (`tools/kama-ollama-evidence.py`) operates under a fundamentally different data model and contract. The table below contrasts the two environments:

| Dimension | `kama-probe.sh` (llama.cpp) | `kama-ollama-evidence.py` (Ollama offline) |
|---|---|---|
| **Domain** | Live HTTP probe against `llama-server` | Offline reconciliation of exported metadata JSON |
| **Identity Source** | File path in `/v1/models` (`models[].name`) | Manifest entries in `/api/tags` and `/api/ps` |
| **Identifier Format** | Absolute filesystem path (`/path/to/model.gguf`) | OCI-style model tag (`[host/][namespace/]name:tag`) |
| **Artifact Structure** | Single `.gguf` binary on host disk | Content-addressed multi-layer blobs (`blobs/sha256:...`) |
| **Verification Token** | None (no digest field in `/v1/models`) | Cryptographic `digest` (`sha256:...`) on both captures |
| **Namespace Meaning** | Filesystem directory structure (irrelevant to model) | Publisher/registry authority (vital to identity) |
| **Normalization Rule** | Basename + strip `.gguf` (`normalize_id`) | **Strict exact case-sensitive string match** |

### 3.1 Namespace and Registry Hierarchy Invalidation
Ollama identifiers mirror OCI/Docker container image references:
- Full syntax: `[registry_host[:port]/][namespace/]model[:tag]`
- Examples: `registry.internal.corp/team-nlp/qwen2.5:32b`, `library/llama3:8b`, `myorg/llama3:8b`.
If `s##*/` (basename) is applied:
- `registry.internal.corp/team-nlp/qwen2.5:32b` becomes `qwen2.5:32b`.
- `myorg/llama3:8b` becomes `llama3:8b`.
- `library/llama3:8b` becomes `llama3:8b`.
**Failure:** Basename normalization strips the namespace and host qualifiers. This conflates private, internal, or untrusted models with official library models, enabling namespace collision, model impersonation, and false-positive reconciliation.

### 3.2 Semantic Invalidation of `.gguf` Extension Stripping
In `llama.cpp`, `.gguf` is an operating-system file extension indicating the binary container format of the weights file.  
In Ollama:
- Models are cataloged by logical names and tags. The physical weights are stored as SHA-256 content-addressed blobs inside `~/.ollama/models/blobs/`.
- If an Ollama model is imported from a GGUF file via a Modelfile (e.g. `ollama create my-model.gguf -f Modelfile`), the string `.gguf` may be part of the literal model name or tag.
- Stripping `.gguf` alters the intended model identifier. For instance, `--expect my-model.gguf` would normalize to `my-model`, failing to match the user's explicit tag or falsely matching an unrelated model named `my-model`.

### 3.3 Cryptographic Digest Replaces Filename Heuristics
`kama-probe.sh` used heuristic normalization because `llama.cpp`'s `/v1/models` provided no cryptographic signature or content hash; filename matching was the only available signal.  
In contrast, Ollama `/api/tags` and `/api/ps` provide a cryptographic SHA-256 digest (`digest: "sha256:..."`):
- Selection is performed by exact name or alias match.
- Metadata correspondence is established by cryptographic equality: `tags_entry["digest"] == ps_entry["digest"]`.
Introducing loose string heuristics (dropping paths, trimming extensions) dilutes cryptographic precision and re-introduces the very ambiguity that content-addressed digests eliminate.

### 3.4 Protection of Remote Inventory Precedence (S031)
Under `corpus/SOURCES.md:43` (S031) and `corpus/knowledge/served-identity-crosswalk.md:29,38`, `/api/tags` entries can represent remote or cloud models indicated by `remote_model` and `remote_host`.  
The round-14 contract dictates:
> `remote tags or selected ps markers -> remote_inventory regardless digest`
Remote entries often carry full upstream URLs or namespaced identifiers. Stripping paths risks creating false collisions between remote entries and local expectations, corrupting the precedence hierarchy.

### 3.5 Contractual and Calibration Boundary (KQ17)
The round-14 specification explicitly commands:
> `Exact name or model alias match, case-sensitive; no GGUF basename normalization.`
Reusing `normalize_id` would directly violate the contract. Calibration C1 requires proving that the replay classifier correctly categorizes fixed adversarial cases without loose heuristic crutches.

---

## 4. Specific Failure Modes & Adversarial Counterexamples

The table below catalogs six adversarial cases where GGUF normalization would fail or produce hazardous false positives, contrasting it with the required exact-match behavior:

| # | Scenario | Caller `--expect` | Captured Metadata Entry (`name` / `model`) | Result under GGUF Normalization | Required Exact-Match Result | Failure Impact if Normalized |
|---|---|---|---|---|---|---|
| **C1** | Namespace Collision | `llama3:8b` | `name: "untrusted_user/llama3:8b"` | `llama3:8b` == `llama3:8b` (**False Match**) | `unknown` (exit 2) | **HIGH:** Untrusted user model masquerades as base model. |
| **C2** | Remote Upstream Collision | `qwen2.5:7b` | `name: "ollama.com/library/qwen2.5:7b"`, `remote_host: "https://ollama.com"` | `qwen2.5:7b` == `qwen2.5:7b` (**Collides**) | `unknown` (exit 2) or `remote_inventory` (exit 1) | **HIGH:** Remote host stripped; risks local classification of remote model. |
| **C3** | Explicit `.gguf` Tag | `qwen-custom.gguf` | `name: "qwen-custom.gguf"` (tags), `name: "qwen-custom"` (ps) | Both normalize to `qwen-custom` (**False Match**) | Tags matches; ps does not -> `available_not_loaded` (exit 1) | **MEDIUM:** Falsely reconciles two distinct tags as identical. |
| **C4** | Path Traversal / Hierarchy | `models/deepseek-r1` | `name: "backup/models/deepseek-r1"` | Both normalize to `deepseek-r1` (**False Match**) | `unknown` (exit 2) | **MEDIUM:** Directory hierarchy erased; ambiguous match. |
| **C5** | Case Variation | `Qwen2.5:7b` | `name: "qwen2.5:7b"` | Case-sensitive equality fails unless normalizer folds case | `unknown` (exit 2) | **LOW:** Confirms case must remain strictly exact. |
| **C6** | Tag/Basename Disambiguation | `mistral:latest` | `name: "archive/mistral:latest"` | Normalizes to `mistral:latest` (**False Match**) | `unknown` (exit 2) | **HIGH:** Archive snapshot accepted as production pin. |

---

## 5. Concrete Recommendations for Implementation Owners

### 5.1 To `KamaR14.Classifier` (`tools/kama-ollama-evidence.py`)
1. **Strict Selection Predicate:**
   Match an entry if and only if `expected == entry.get("name")` or `expected == entry.get("model")` via exact string equality.
   ```python
   # REQUIRED: Exact, case-sensitive matching only
   def select_entries(models: list, expected: str) -> list:
       return [
           e for e in models
           if isinstance(e, dict) and (e.get("name") == expected or e.get("model") == expected)
       ]
   ```
2. **Strictly Avoid Normalization Helpers:**
   Do **not** import or re-implement `normalize_id`, `os.path.basename`, `os.path.split`, `str.rstrip(".gguf")`, or `str.lower()`.
3. **Fail-Closed Cardinality:**
   Require `len(selected_tags) == 1` and `len(selected_ps) <= 1`. Multiple selected entries on either side must fail closed as `unknown` or `invalid_input` (exit 2).
4. **Internal Name/Model Conflict:**
   If a selected entry defines both `name` and `model` as non-empty strings and `entry["name"] != entry["model"]`, return `identity_conflict` (exit 1), unless one strictly matches `--expect` and the other is a documented valid alias.

### 5.2 To `KamaR14.Fixtures` (`tests/ollama-evidence/cases.json`)
Include literal, independent fixture entries explicitly validating the prohibition of GGUF normalization:
- **Case `no_basename_normalization_tags`:**
  `expect: "qwen:7b"`, tags entry `name: "library/qwen:7b"`. Must yield `unknown` (exit 2), proving path prefixes are not stripped.
- **Case `no_gguf_strip_tags`:**
  `expect: "custom-model"`, tags entry `name: "custom-model.gguf"`. Must yield `unknown` (exit 2), proving `.gguf` is not stripped.
- **Case `no_gguf_strip_ps`:**
  `expect: "model.gguf"`, tags `name: "model.gguf"`, ps `name: "model"`. Must yield `available_not_loaded` (exit 1), proving ps does not loosely match stripped tags.
- **Case `case_sensitive_exact`:**
  `expect: "Llama3:8b"`, tags entry `name: "llama3:8b"`. Must yield `unknown` (exit 2).

### 5.3 To `KamaR14.ReviewDigest` & `KamaR14.ReviewSchema`
- Enforce that digest comparison occurs **only** after exact identifier selection. A matching digest under a non-exact name must never be upgraded to `loaded_same_digest`.
- Ensure schema validation verifies that `name`, `model`, and `digest` are strictly `str` types before any selection or comparison logic executes.

---

## 6. Limits & Evidence Grounding

- **Cited Code & Documents:**
  - `tools/kama-probe.sh:324-388` (`served_ids`, `normalize_id`, `model_matches`).
  - `tools/kama-probe.sh:925-926, 959-971` (`served_persist`).
  - `SKILL.md:142-159` (§Served-id normalization).
  - `corpus/knowledge/endpoint-identity.md:20-22` (§ID normalization).
  - `corpus/knowledge/served-identity-crosswalk.md:23-45` (Crosswalk & Grounded failure cases).
  - `corpus/knowledge/gguf-runtime-compatibility-boundary.md:8-14` (GGUF naming convention limits).
  - `corpus/SOURCES.md:23,24,43` (S011, S012, S031).
  - `.ufo/waves/round-14/spec.json` (Classifier shared interface contract).
- **Verification Limits:** No code or tests executed. All findings are derived through static architectural analysis of repository source and authoritative contract specifications.
