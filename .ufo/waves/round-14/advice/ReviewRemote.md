# ReviewRemote — Kama round 14 (C1 offline Ollama tags/ps classifier)

**Seat:** `KamaR14.ReviewRemote` (reviewer, leaf, read-only except this report)
**Scope:** static review of remote_model/remote_host precedence, wrong-type handling, and whether mixed loaded/remote input can reach `loaded_same_digest`.
**Execution:** no checks, builds, tests, or runtime probes run. No network. No edits to shared files.
**Tooling:** none installed or updated.

## Inputs and limits

- `tools/kama-ollama-evidence.py` is **pending** (absent on disk at review time). `tests/ollama-evidence/cases.json` is **pending** (absent). This review therefore rests on the contract text in `.ufo/waves/round-14/spec.json` (`context`, "Classifier shared interface"), the `Classifier` and `Fixtures` prompts in the same file, and the corpus grounding below. It is not a code review. Re-check every finding once the file lands.
- Grounding (corpus, not re-opened this seat):
  - `corpus/SOURCES.md:23` S011 — "Lists locally available models with names, digests, and format or quantization metadata".
  - `corpus/SOURCES.md:24` S012 — `/api/ps` "Models currently loaded into memory"; the row lists digest, context length, VRAM, expiry. It lists **no** remote fields.
  - `corpus/SOURCES.md:43` S031 — `ModelSummary.remote_model` "Name of the upstream model, if the model is remote"; `remote_host` "URL of the upstream Ollama host, if the model is remote".
  - `corpus/knowledge/served-identity-crosswalk.md:29` — tags fields are `name`, `model`, `remote_model`/`remote_host`.
  - `corpus/knowledge/served-identity-crosswalk.md:38` — "Available inventory is not proof of local weights (S031/S010)."

## Findings (by severity)

### F1 — HIGH — Truthiness or type-less checks let a wrong-typed remote marker reach `loaded_same_digest`
- The contract requires loaded only when "neither remote_model nor remote_host nonempty", and says "invalid types … fail closed unknown/invalid_input".
- An implementation that writes `if entry.get("remote_model"):` treats `0`, `false`, `[]`, `{}`, and `""` as absent. Each would reach `loaded_same_digest` with a remote marker present. JSON `null` has the same problem if it is read as absent.
- Python `isinstance(True, int)` is also true. Type checks must use explicit `type(x) is str` or equivalent, not isinstance on int-like values.
- **Recommendation to Classifier:** presence is tested with `key in entry`. A present remote key must be a string that is nonempty after type check; any other present value is `invalid_input` (exit 2). Never use truthiness.
- **Fixture coverage needed (Fixtures):** remote_model/remote_host set to `0`, `false`, `[]`, `{}`, `null`, `""`, and a number. Each must not be `loaded_same_digest`. The literal expected result is exit 2 `invalid_input`.

### F2 — HIGH — Duplicate JSON object keys silently override remote markers
- Stdlib `json.load` keeps the last value for a repeated key. `{"model":"m","digest":"d","remote_host":"http://x","remote_host":null}` parses as local, which hides the remote declaration.
- **Recommendation to Classifier:** parse with `object_pairs_hook` and reject any duplicate key as `invalid_input` (exit 2), for the tags and ps envelopes and for every entry.
- **Fixture (Fixtures):** a duplicate-key case with a remote key whose last value is local. Expected exit 2 `invalid_input`.

### F3 — HIGH — The contract has no single total order; three statements conflict
The spec gives three precedence statements that do not agree:
1. "remote tags or selected ps markers → `remote_inventory` regardless digest";
2. "missing identity/digest … fail closed unknown/invalid_input";
3. Fixtures prompt: "remote takes precedence only after schema valid".

Conflicts that change the exit code or the finding ID:
- (a) remote entry with **missing or empty digest**: `remote_inventory` (exit 1) vs `invalid_input` (exit 2).
- (b) remote entry with a digest that **differs** from the other side: `remote_inventory` (exit 1) vs `identity_conflict` (exit 1). Same exit, different finding; a literal selftest ID pins one arbitrarily.

**Recommended total order** (planner ruling required on (a) and (b); the order below resolves both):
1. Envelope, entry-type, duplicate-key, and identity-field-type validation, for every entry. Failure → `invalid_input` (2).
2. Exact selection by `name` or `model`. More than one selected entry on either side → `invalid_input` (2). Zero tags matches → `unknown` (2).
3. Present remote key on a selected entry: must be nonempty string (F1), else `invalid_input` (2).
4. Missing or empty digest on a selected entry → `invalid_input` (2). This is schema validity, and it runs before remote, which satisfies "remote only after schema valid". It does **not** make the digest value matter for remote.
5. Name/model conflict within the selected entry → `identity_conflict` (1).
6. Any remote marker on a selected tags or ps entry → `remote_inventory` (1), regardless of digest value. This runs before any digest comparison, so mixed loaded/remote cannot reach loaded.
7. Differing digests across the selected tags and ps entries → `identity_conflict` (1).
8. ps has no selected entry, or an empty ps array → `available_not_loaded` (1). A missing ps input is `invalid_input` (2), not available.
9. Otherwise → `loaded_same_digest` (0).

Under this order, (a) is exit 2 and (b) is `remote_inventory`. If the planner reads "regardless digest" as also overriding missing digest, the owner must say so and Fixtures must pin that outcome. Until then the order above is the recommendation.

### F4 — MEDIUM — Scope of "selected" versus malformed unselected entries is unspecified
- "Selected ps markers" presumably means only entries that match `--expect`. A remote marker on a non-selected ps entry must not flip the result.
- The contract also says "malformed … entries fail closed". It does not say whether that covers unselected entries.
- **Recommendation:** validate types for **all** entries (fail closed), and interpret remote, digest, and identity only for selected entries. Owner must record this choice; Fixtures need one case for each reading.

### F5 — MEDIUM — Present-but-empty remote strings and null are undefined
- The contract's "nonempty" gate, read literally, lets `remote_host: ""` pass as local.
- **Recommendation:** present `""` or `null` is malformed → `invalid_input` (2), not local. This matches fail-closed and S031's "if the model is remote" wording, which implies presence signals remoteness. The owner must state the choice in `reasons`.

### F6 — LOW — ps-side remote markers are undocumented
- S012 (`corpus/SOURCES.md:24`) lists digest, context, VRAM, and expiry for `/api/ps`. It documents no `remote_model`/`remote_host` on ps entries.
- Treating a ps remote marker as `remote_inventory` (exit 1) is the conservative direction and cannot produce a false loaded. The Classifier should mark that rule as `[INFERENCE]` in `reasons`. No docs claim should be added.

### F7 — LOW — Digest comparison rule is not stated
- "nonempty string equal digest" implies exact string equality. It does not say whether `sha256:` prefix or hex case is normalized.
- **Recommendation:** exact equality, no normalization (matching the name rule). A prefixed-vs-bare pair is then `identity_conflict` (1). Owner should state this in the module docstring and add one fixture.

## Adversarial mixed-input matrix (recommended literal expectations for Fixtures)

Expected results follow the total order above. Fixtures must write each as a literal, not computed.

| # | Case | Tags (selected) | ps (selected) | Expected exit | Expected finding |
|---|---|---|---|---|---|
| 1 | Local tags + local ps, same digest | local, digest D | local, digest D | 0 | loaded_same_digest |
| 2 | Local tags + ps remote, same digest D | local, D | remote_host set, digest D | 1 | remote_inventory |
| 3 | Remote tags + local ps, same digest D | remote_model set, D | local, D | 1 | remote_inventory |
| 4 | Remote tags + ps remote, digests differ | remote, D1 | remote, D2 | 1 | remote_inventory |
| 5 | Remote tags digest differs from local ps | remote, D1 | local, D2 | 1 | remote_inventory |
| 6 | Remote tags, empty ps array | remote, D | `[]` | 1 | remote_inventory |
| 7 | Remote tags, ps absent (input missing) | remote, D | input missing | 2 | invalid_input |
| 8 | Remote tags, missing digest | remote, no digest | local, D | 2 | invalid_input |
| 9 | `remote_model: 0` on tags, otherwise loaded | `0`, D | local, D | 2 | invalid_input |
| 10 | `remote_host: null` on ps, otherwise loaded | local, D | `null`, D | 2 | invalid_input |
| 11 | Duplicate `remote_host` key, last value local | duplicate keys, D | local, D | 2 | invalid_input |
| 12 | Remote on non-selected ps entry only | local, D | other name remote; selected local D | 0 | loaded_same_digest |
| 13 | Two selected ps entries, one remote | local, D | two selected, one remote | 2 | invalid_input |
| 14 | Name/model conflict within selected tags entry | name≠model | local, D | 1 | identity_conflict |
| 15 | Prefixed vs bare digest, both local | `sha256:D` | `D` | 1 | identity_conflict |

Row 12 depends on the F4 ruling. If the owner chooses "malformed unselected entries fail closed", row 12 must still be `loaded_same_digest` only if the unselected entry is well-typed.

## Messages sent

- To `KamaR14.Classifier`: F1, F2, F3 total order, F4, F5 (summary, pointing here).
- To `KamaR14.Fixtures`: matrix rows 1–15 as literal fixture candidates, plus the F3/F4 rulings pending.

## Residual risk and verification gaps

- Nothing was executed. Every finding depends on the classifier and cases files as written later; re-review both when they land.
- F3 and F4 require a planner ruling. Until it is recorded, the classifier and fixtures can disagree silently.
- Ollama's real behaviour for wrong-typed or duplicate-key JSON was not observed. The findings are fail-closed design controls, not claims about upstream output.
