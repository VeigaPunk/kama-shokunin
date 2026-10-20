# TagsSource — Kama Round 14 Scoped Source Findings (Official Ollama Tags)

**Seat:** `KamaR14.TagsSource` (scout, leaf)  
**Assigned Scope:** Open official `/api/tags` documentation; exact model/name/digest and remote fields; <=25-word located quotes and ambiguities; advise Classifier and Fixtures owners.  
**Execution Mode:** Read-only inspection; no tests, builds, formatters, smoke runs, or runtime execution. No git commits or delegation.  
**Tooling:** None installed or modified.

---

## 1. Documentation Source Evidence

- **Document Opened:** `https://docs.ollama.com/api/tags` (raw OpenAPI representation verified at `https://docs.ollama.com/api/tags.md`).
- **Specification Metadata:** OpenAPI 3.1.0, `info.title`: "Ollama API", `info.version`: "0.1.0", path: `GET /api/tags`.
- **Response Schema:** 200 OK returns `ListResponse` containing `models: array` of `$ref: '#/components/schemas/ModelSummary'`.

---

## 2. Exact Fields in `ModelSummary`

| Field | Type | Description in Official Schema | Role in Replay Classifier |
|---|---|---|---|
| `name` | `string` | "Model name" | Primary candidate for exact matching against `--expect` |
| `model` | `string` | "Model name" | Secondary candidate / alias; must equal `name` |
| `remote_model` | `string` | "Name of the upstream model, if the model is remote" | Presence of non-empty string signals remote inventory |
| `remote_host` | `string` | "URL of the upstream Ollama host, if the model is remote" | Presence of non-empty string signals remote inventory |
| `digest` | `string` | "SHA256 digest identifier of the model contents" | Content-addressed artifact hash joined against `/api/ps` |
| `modified_at` | `string` | "Last modified timestamp in ISO 8601 format" | Informational metadata; classifier must not infer freshness |
| `size` | `integer` | "Total size of the model on disk in bytes" | Informational disk footprint |
| `details` | `object` | "Additional information about the model's format and family" | Container for `format`, `family`, `families`, `parameter_size`, `quantization_level` |

---

## 3. Located Quotes (<= 25 Words Each)

1. **ModelSummary Description:**
   > "Summary information for a locally available model"
   - *Location:* `https://docs.ollama.com/api/tags.md` OpenAPI `#/components/schemas/ModelSummary/description` (7 words).

2. **Remote Model Property:**
   > "Name of the upstream model, if the model is remote"
   - *Location:* `https://docs.ollama.com/api/tags.md` OpenAPI `#/components/schemas/ModelSummary/properties/remote_model/description` (9 words).

3. **Remote Host Property:**
   > "URL of the upstream Ollama host, if the model is remote"
   - *Location:* `https://docs.ollama.com/api/tags.md` OpenAPI `#/components/schemas/ModelSummary/properties/remote_host/description` (10 words).

4. **Digest Property:**
   > "SHA256 digest identifier of the model contents"
   - *Location:* `https://docs.ollama.com/api/tags.md` OpenAPI `#/components/schemas/ModelSummary/properties/digest/description` (7 words).

5. **200 Response Summary:**
   > "List available models"
   - *Location:* `https://docs.ollama.com/api/tags.md` OpenAPI `paths./api/tags.get.responses.200.description` (3 words).

---

## 4. Grounded Ambiguities & Semantic Contradictions

1. **"Locally Available" vs. Remote Inventory Contradiction:**  
   The schema description headers state "List available models" and "Summary information for a locally available model", yet `ModelSummary` explicitly documents `remote_model` and `remote_host`. Membership in `/api/tags` alone does **not** prove local residency or locally resident model weights.

2. **Dual Identity Fields (`name` vs. `model`):**  
   Both `name` and `model` share the exact description `"Model name"`. The documentation does not explain when or why they differ (e.g. tag aliases, `ollama cp`, registry namespace prefixes). When `name != model` within an entry, internal identity ambiguity exists and must be classified as `identity_conflict` (exit 1).

3. **Undefined Local Representation for Remote Keys:**  
   The OpenAPI schema defines `remote_model` and `remote_host` as `type: string`. It does not specify whether local models omit the keys entirely, set them to `null`, or set them to empty string `""`. Naive truthiness checks (`if entry.get("remote_host"):`) treat `0`, `false`, `null`, `[]`, `{}` as false/absent, allowing remote models to falsely qualify as `loaded_same_digest`. A non-string or malformed value must fail closed as `invalid_input` (exit 2).

4. **Undocumented Tags-to-Ps Digest Join:**  
   The schema defines `digest` as "SHA256 digest identifier of the model contents" (OpenAPI example: 64-character lowercase hex string without `sha256:` prefix). The upstream documentation nowhere defines or documents joining `/api/tags` and `/api/ps` by digest. The join is an operational inference (`[INFERENCE]`). Strict character-exact string comparison without prefix/case normalization is required.

5. **Absence of Canonicalization / Case Folding Rules:**  
   OpenAPI documentation uses literal examples (`"name": "gemma4"`). No case-insensitivity or default `:latest` tag truncation is specified in the schema. The offline replay classifier must strictly enforce exact, case-sensitive matching against `--expect` and refuse GGUF basename stripping.

6. **Multiple Matching Entries:**  
   The schema permits arbitrary lists in `models: array`. It does not guarantee uniqueness of `name` or `model`. Multiple selected entries matching `--expect` constitute an ambiguous selection and must fail closed (`unknown`, exit 2).

---

## 5. Bounded Owner Recommendations

### Advice to `KamaR14.Classifier` (`tools/kama-ollama-evidence.py`)
1. **Entry Selection:** An entry in `tags["models"]` is selected if `entry["name"] == expect` or `entry["model"] == expect` (exact string equality). If matching count == 0: return `unknown` (exit 2). If matching count > 1: return `unknown` (exit 2).
2. **Structural Validation:** Validate all entries upfront: `tags` must be an object with a `models` list; every entry must be an object with non-empty string `name`, `model`, and `digest`. Any malformed entry or unreadable file -> `invalid_input` (exit 2).
3. **Identity Coherence:** If both `name` and `model` are present on the selected entry, verify `entry["name"] == entry["model"]`. If they differ -> `identity_conflict` (exit 1).
4. **Remote Precedence:** On the selected entry, inspect `remote_model` and `remote_host`:
   - If present and not `type(val) is str`: return `invalid_input` (exit 2).
   - If present and non-empty string: return `remote_inventory` (exit 1), regardless of digest value.
   - Do **not** allow an unselected remote entry to taint a clean selected local entry.
5. **Digest Matching:** Check `tags_entry["digest"] == ps_entry["digest"]`. Exact string equality; no `sha256:` prefix stripping. If digests differ -> `identity_conflict` (exit 1).

### Advice to `KamaR14.Fixtures` (`tests/ollama-evidence/cases.json`)
Include literal, distinct test fixtures covering official schema facets:
1. `tags_local_clean`: `{"name": "m:tag", "model": "m:tag", "digest": "d123", "size": 1000}` matching ps -> `loaded_same_digest` (exit 0).
2. `tags_remote_model`: `{"name": "m:tag", "model": "m:tag", "digest": "d123", "remote_model": "upstream-m"}` -> `remote_inventory` (exit 1).
3. `tags_remote_host`: `{"name": "m:tag", "model": "m:tag", "digest": "d123", "remote_host": "http://ollama.upstream:11434"}` -> `remote_inventory` (exit 1).
4. `tags_remote_both`: both `remote_model` and `remote_host` populated -> `remote_inventory` (exit 1).
5. `tags_remote_wrong_type`: `remote_host: null` or `remote_host: 0` or `remote_host: false` -> `invalid_input` (exit 2).
6. `tags_remote_empty_string`: `remote_host: ""` -> `invalid_input` (exit 2) (fail closed).
7. `tags_name_model_conflict`: `{"name": "m:tag1", "model": "m:tag2", "digest": "d123"}` -> `identity_conflict` (exit 1).
8. `tags_missing_digest`: `digest` key missing or empty string -> `invalid_input` (exit 2).
9. `tags_duplicate_selected`: two entries matching `--expect` -> `unknown` (exit 2).
10. `tags_unselected_remote`: another entry has `remote_host`, but selected entry is local and matches ps -> `loaded_same_digest` (exit 0).
11. `tags_case_mismatch`: `--expect Llama3` with entry `llama3` -> `unknown` (exit 2).

---

## 6. Peer Coordination

- Bounded advice dispatched to `KamaR14.Classifier` regarding `ModelSummary` field definitions, internal name/model identity conflict, and strict remote typing.
- Bounded advice dispatched to `KamaR14.Fixtures` proposing specific schema-accurate fixture objects and edge cases.

---

## 7. Residual Limits & Gaps

- **Static Analysis Only:** No live Ollama server or network endpoints were contacted.
- **In-flight Artifacts:** `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json` were pending at report time; findings are grounded in official documentation and the contract specification in `.ufo/waves/round-14/spec.json`.
- **Join Semantics:** The tags-to-ps digest join is an operational inference (`[INFERENCE]`) not specified in vendor documentation.
