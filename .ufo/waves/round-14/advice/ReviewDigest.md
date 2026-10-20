# ReviewDigest — round 14 static review (Ollama tags/ps digest and name matching)

Scope: static review of the digest-match and name-match rules in the round-14 classifier contract only. Target: exact digest match, missing/malformed identity, tag/ps name mismatch, no basename identity shortcuts.

## Status of inputs

- `tools/kama-ollama-evidence.py` is **pending** (absent at review time). Classifier findings below are contract-level, not code-level.
- `tests/ollama-evidence/cases.json` is **pending** (absent). Fixture findings are candidate inputs only.
- Reviewed: `.ufo/waves/round-14/spec.json` (context, "Classifier shared interface"), `.ufo/waves/round-14/dispatch.json` (Classifier, Fixtures, ReviewDigest task text, lines 232-234 and 312-314), `.ufo/waves/round-14/advice/swarm-registry.json`, `.ufo/waves/round-13/advice/ReviewIdentity.md` (F2, F4 on tags/ps semantics), `corpus` SKILL.md served-id normalization (`SKILL.md:142-150`), `tools/kama-probe.sh:925-926` (persisted basename comparison).
- No code, tests, builds, or verification were run. No network. Nothing installed or updated (RULES.md read; no tool needed).

## Findings (severity order)

### F1 — HIGH — No explicit verdict precedence; the contract has overlapping rules that collide

The contract has several rules that can all match one input, with no ordering:

- "remote tags or selected ps markers -> remote_inventory regardless digest"
- "missing identity/digest ... fail closed unknown/invalid_input"
- "unavailable inputs fail closed unknown/invalid_input"
- "absent ps match and local tags digest -> available_not_loaded"

Unresolved candidates:

- C-F1a: remote tags entry, no `digest` key. "Regardless digest" says `remote_inventory`; "missing digest" says `unknown`.
- C-F1b: selected remote ps entry, plus a malformed unselected tags entry. Is the result `remote_inventory` or `invalid_input`?
- C-F1c: remote ps marker plus two identical selected tags entries (duplicate). `remote_inventory` or `unknown`?

Recommendation to Classifier (owner decision, reviewer's proposed ladder): evaluate in this order and stop at first match:
1. `invalid_input`: unreadable/non-JSON file, top-level not an object, `models` missing or not an array, any entry not an object, any present field of wrong type (name, model, digest, remote_model, remote_host), argparse errors.
2. `unknown`: no selected tags entry; more than one selected tags entry; more than one selected ps entry; selected entry missing name/model/digest.
3. `remote_inventory`: selected tags entry or selected ps entry carries a nonempty remote marker (digest ignored).
4. `identity_conflict`: name/model disagree within one selected entry; or selected tags digest != selected ps digest (both nonempty).
5. `loaded_same_digest` / `available_not_loaded` per the match rules below.

This ladder puts `remote_inventory` before digest checks (as the contract says) but after structural validation and uniqueness, so C-F1a resolves to `unknown` only if the ladder is read as "missing digest is checked before remote". Owners must pick and document one; fixtures must lock it.

### F2 — HIGH — `invalid_input` vs `unknown` is not mapped to any input class

Both are exit 2, and the contract writes "unknown/invalid_input" as one slash-pair for several different cases (missing models array, malformed entry, duplicate selected entries, unavailable input). The fixture schema needs one literal `expected_finding` per case, so the mapping must be fixed before Fixtures writes literals.

Recommended table for owners:
- `invalid_input`: unreadable or missing file (both `--tags` and `--ps`), malformed JSON, missing/non-array `models`, non-object entry, wrong-type fields.
- `unknown`: well-formed inputs where selection is empty (no tags match) or ambiguous (duplicate selected entries), or a selected entry lacks name/model/digest.

Open decision for owners: a missing `--ps` file. The contract says it "does not" permit `available_not_loaded`; it does not say whether that is `invalid_input` (unavailable input) or `unknown`. Reviewer recommends `invalid_input` (unavailable input), consistent with "unavailable inputs fail closed".

### F3 — HIGH — Tag/ps name mismatch with equal digest is classified as a negative claim

Candidate input (static, not run):
- `--expect m:latest`
- tags: `[{"name":"m:latest","model":"m:latest","digest":"D"}]`
- ps: `[{"name":"m","model":"m","digest":"D"}]`

Under the literal rules: no ps entry equals `m:latest`, so "absent ps match and local tags digest" yields `available_not_loaded` (exit 1). But ps reports a loaded entry with the same digest D under a different name. Reporting "not loaded" is an absence claim the contract does not license. Exact-name rules forbid joining it, so the honest result is not "not loaded".

Recommendation: when any ps entry (not only the selected one) has a digest equal to the selected tags digest and does not match the expected name/model exactly, return `unknown` with reason naming the digest correspondence under a non-exact name. Do not return `available_not_loaded`. Do not return `loaded_same_digest` (no exact name). Note: ReviewIdentity F4 (`.ufo/waves/round-13/advice/ReviewIdentity.md:37-40`) already records that digest join is [INFERENCE], not a documented Ollama mapping, so it must not become an identity match either.

### F4 — HIGH — Validation scope is unstated; a malformed entry can be skipped and hide a duplicate selection

"Malformed entries fail closed" does not say whether all entries are validated or only the selected ones. If only well-formed entries are considered for selection, this input yields a false `loaded_same_digest`:

- `--expect m`
- tags: `[{"name":"m","model":"m","digest":"D"}]`
- ps: `[{"name":5,"model":"m","digest":"D"},{"name":"m","model":"m","digest":"D"}]`

The first ps entry has a non-string `name` and is malformed; the second is a valid exact match. Skipping the malformed entry leaves exactly one selected ps entry and returns `loaded_same_digest` (exit 0), so the contract's duplicate-selection fail-closed rule is never applied. Validating every entry first returns `invalid_input`.

Recommendation: validate every entry of both arrays and every top-level field type before any selection. Any structural defect → `invalid_input`. This is the fail-closed direction and removes the hidden-entry case entirely.

### F5 — MEDIUM — "Exact name or model alias" is undefined; selection predicate must be written out

"Alias" is not defined. Recommended predicate (owners to confirm): an entry is selected iff `expected == entry.name` or `expected == entry.model`, both exact, case-sensitive string equality. The contract's "no GGUF basename normalization" forbids the kama-probe shortcut at `tools/kama-probe.sh:925-926` (persisted basename on both sides) and `SKILL.md:147-150` (take basename, strip `.gguf`, compare case-sensitively). Reviewer concludes:

- Candidates that must NOT match (fixtures should lock each as `unknown`, exit 2):
  - `--expect qwen.gguf` vs entry `model: "/store/qwen.gguf"` (basename equality)
  - `--expect qwen` vs entry `name: "qwen.gguf"` (strip-extension equality)
  - `--expect Qwen:7b` vs entry `name: "qwen:7b"` (case)
  - `--expect m` vs entry `name: "m:latest"` (implicit `:latest` default)

Recommendation: an entry with a non-exact name match must not be selected even if its digest equals the selected digest (see F3).

### F6 — MEDIUM — Digest equality rule is implicit

"Nonempty string equal digest" does not say whether comparison is exact. Owners should state: exact string equality; no case folding; no `sha256:` prefix stripping; no truncation; whitespace-only counts as present (no trimming). Candidate: tags `"sha256:ab…"` vs ps `"ab…"`. Under exact equality this is "differing matching digests" → `identity_conflict` (spec-literal). Owners should confirm that outcome and lock it in fixtures, because a reader could reasonably expect `unknown`.

### F7 — MEDIUM — "differing matching digests" does not say which two sides are compared

Recommendation: compare only the selected tags digest against the selected ps digest. Non-selected entries never participate (consistent with F3 handling, which is a separate rule).

### F8 — MEDIUM — Remote-marker typing is unspecified and drives the precedence

"neither remote_model nor remote_host nonempty" does not define types. Recommended (fail closed toward not-loaded):
- absent or JSON `null` → not remote;
- exact empty string `""` → not remote;
- any non-string → `invalid_input`;
- any other string, including whitespace-only, → remote (no trimming).

Without this, `"remote_host": " "` could pass as local and yield `loaded_same_digest`, which is the exit-0 claim the contract forbids without a local-match proof.

### F9 — LOW — Timing fields must be ignored and proven ignored

`expires_at` is present in ps (S012, `.ufo/waves/round-13/advice/ReviewIdentity.md:37-40`). The contract forbids timing inference. Recommendation: fixture pair with identical identity and different or past `expires_at` must yield the same verdict.

## Candidate inputs summary (static, not executed)

| Candidate | Expected under the recommended ladder | Contract gap closed |
|---|---|---|
| Remote tags entry, no digest | remote check then `unknown` per ladder — owners choose and lock | F1 |
| ps name `m` digest equal to tags `m:latest` digest | `unknown` | F3 |
| malformed ps entry (`name: 5`) that matches by `model`, plus a valid duplicate selected ps entry | `invalid_input` (not `loaded_same_digest`) | F4 |
| `--expect qwen.gguf` vs model `/store/qwen.gguf` | `unknown` (no basename shortcut) | F5 |
| `--expect m` vs name `m:latest` | `unknown` (no implicit tag) | F5 |
| `"sha256:X"` vs `"X"` on selected pair | `identity_conflict` (exact equality) | F6 |
| `"remote_host": " "` on selected ps | `remote_inventory` (no trim) | F8 |
| `--ps` file absent | `invalid_input` (reviewer recommendation) | F2 |

## Owner recommendations (bounded)

- Classifier (executor, `tools/kama-ollama-evidence.py`): implement the F1 ladder; validate whole arrays (F4) before selection; define the selection predicate (F5); exact digest comparison (F6); remote typing (F8); no timestamp handling (F9); map each path to exactly one finding ID (F2).
- Fixtures (executor, `tests/ollama-evidence/cases.json`): add literal cases for the candidate table above, including the F3 non-exact-name equal-digest case and the F4 malformed-plus-duplicate case, which are the two most likely to be missed. One literal `expected_finding` per case; do not derive expectations from the classifier.
- ReviewSchema / ReviewSelftest (reviewers): confirm the F1 ladder and F2 mapping are reflected in the selftest literals before accepting.

## Residual risk and verification gaps

- Classifier and fixtures are pending; every point above is contract-level. The F1 ladder and the F3 `unknown` choice are reviewer recommendations and need owner or planner decision, not silent adoption.
- Digest-to-model correspondence is an [INFERENCE] (`ReviewIdentity.md` F4). Nothing here proves a digest identifies weights; the classifier reports metadata correspondence only, as the contract says.
- No runtime or live Ollama behavior was observed. No readiness claim is made or implied.
- No checks, tests, or smoke runs were executed, as instructed.

Tooling: none installed or updated.
