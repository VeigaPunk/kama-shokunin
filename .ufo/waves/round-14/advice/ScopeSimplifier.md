# ScopeSimplifier — round-14 C1 offline Ollama evidence classifier (advice only)

Lane: ScopeSimplifier (leaf). Read-only except this report. No tests, builds, formatters, smoke runs, network, or live runtime contact. No tools installed or upgraded.

## State observed
- `tools/kama-ollama-evidence.py` does not exist yet. `tests/ollama-evidence/cases.json` does not exist yet. `tests/` does not exist. Both are pending; the findings below come from the contract text in the Classifier shared interface and the round-11 source/crosswalk evidence, not from the planned code.
- Field names used in the advice (`name`, `model`, `digest`, `remote_model`, `remote_host`, `expires_at`) come from the round-11 crosswalk and SOURCES rows already in the tree (`corpus/knowledge/served-identity-crosswalk.md`, S011/S012/S031). I did not re-open the vendor pages.

## Axes
1. Acquisition / network surface (cut to zero).
2. Time semantics (cut to zero).
3. Output schema surface (keep exactly the six keys).
4. CLI surface (keep the four inputs and flags, nothing else).
5. Matching rules (exact only, no normalization).
6. Testability and fixture count (one case per rule, no matrix).
7. Second-convention risk against `tools/kama-probe.sh`.

## Keep (required, cheap, do not trim)
- Python stdlib only; offline file inputs only; no writes beyond stdout.
- Exact, case-sensitive name/model match; no `.gguf` or basename stripping.
- Fail-closed: missing, malformed, duplicate-selected, or unreadable input → `unknown` / `invalid_input`, exit 2. Never `loaded_same_digest` or `available_not_loaded`.
- `readiness` is the constant `"unknown"` in every output. Do not compute it.
- `--selftest` spawns the real CLI as a child process and checks committed fixtures. The round-13 `measure.py` pattern (`[sys.executable, "-I", "-B", script, ...]`, `shell=False`, `stdin=DEVNULL`, timeout) is an existing convention; reuse it rather than inventing another.

## Cut or refuse (scope creep)
1. **Acquisition/network.** No URL, socket, `urllib`, `http`, or `requests` imports. No invoking the `ollama` binary. No reading `~/.ollama`, `OLLAMA_*` env, or the `/api/*` routes. No retries, polling, watch loops, or backoff. The contract's "no acquisition feature" already forbids these; keep it that way.
2. **Time.** Do not parse `expires_at`, do not compare against "now", and do not add staleness windows or "as of" fields. `expires_at` is not an input. Add one adversarial fixture (`expires_at` in the past) that still yields `loaded_same_digest`, so the absence of time logic is tested.
3. **Output keys.** Emit exactly `finding_id`, `verdict_exit`, `expected_model`, `readiness`, `scope`, `reasons`. No echoed digests, paths, input hashes, tool version, counts, or timings.
4. **CLI flags.** Only `--tags`, `--ps`, `--expect`, `--selftest`, plus argparse's default `--help`. Reject `--out`, `--format`, `--json-indent`, `--verbose`, `--host`, `--port`, `--strict`, and any alias file option.
5. **Name normalization.** No `.gguf` stripping, basename handling, case folding, `sha256:` prefix stripping, prefix/fuzzy matching, or quantization-suffix parsing. `tools/kama-probe.sh` `normalize_id` does basename + `.gguf` stripping; do not copy or import it. That would create a second identity convention and violate the contract's no-normalization rule.
6. **Alias graph.** No alias table, no `ollama cp` lineage. The only alias handling is the within-entry `name`/`model` check. Anything wider is a new feature.
7. **Best-match selection.** No ranking or choosing among multiple candidates. Two selected entries → `unknown`.
8. **Free-form reasons.** `reasons` should be a closed set of short codes, each used by at least one fixture. Prose reasons make the selftest brittle and invite scope growth.
9. **Writes/caches.** No temp directory (committed fixtures need none; `measure.py` needs one only because it generates trees). No ledger, history, or baseline file. Do not touch `registry/` beyond the one-line documents-map entry the contract requires.
10. **Integration.** Do not wire the classifier into `kama-probe.sh check`, `snapshot`, or the consumer registry. The verdict vocabulary differs (`loaded_same_digest` vs `MODEL_OK`). Document the difference rather than mapping one to the other.
11. **Schema validation.** Use plain `isinstance` checks on the fields the rules read. No JSON Schema, no dataclasses-with-validators, no generic walker.

## Spec ambiguities to pin before coding (each one removes a possible branch)
a. **`finding_id` values.** No separate verdict key exists, so `finding_id` must carry the verdict name. Pin the six values: `loaded_same_digest`, `available_not_loaded`, `remote_inventory`, `identity_conflict`, `unknown`, `invalid_input`. Exit mapping: 0 / 1 / 1 / 1 / 2 / 2. Also state which of `unknown` and `invalid_input` applies to a missing file versus a malformed model entry.
b. **`--ps` required or optional.** The contract says a missing ps input must not permit `available_not_loaded`. Make both flags required and let argparse handle absence (usage error to stderr, exit 2, no JSON). Document that exception. Do not add an optional-ps code path.
c. **Argparse errors vs JSON.** Pick one: argparse's default usage error (stderr, exit 2) for CLI misuse; JSON `invalid_input` only for unreadable or malformed input files. Write this in the module docstring.
d. **Entry selection.** Define one rule: an entry is selected when `expected` equals its `name` or its `model`. Then: two selected entries → `unknown`; `name` and `model` both present and unequal within the selected entry → `identity_conflict`; a missing identity or digest → `invalid_input`.
e. **Digest comparison.** Exact string equality between selected tags and ps digests. Empty or non-string digest → `invalid_input`. Differing digests across the two selected entries → `identity_conflict`.
f. **Remote markers.** Define "marker" as a present, nonempty `remote_model` or `remote_host` on either selected entry. Any marker → `remote_inventory`, regardless of digest.
g. **ps-only hit.** A selected ps entry with no selected tags entry → `unknown`, not `loaded_same_digest` and not `available_not_loaded`. State this explicitly; it is the most likely place for an implementer to take a shortcut.
h. **Valid empty ps array.** `{"models": []}` with a matching tags entry → `available_not_loaded`. A ps file lacking a `models` array → `invalid_input`.

## Minimal adversarial fixture set (one per rule)
Target about 16 cases in `tests/ollama-evidence/cases.json`. Each case names the rule it exercises. Do not build a cross-product.
1. Same name and digest in tags and ps, no remote markers → exit 0 `loaded_same_digest`.
2. Same digest, ps entry carries `remote_host` → `remote_inventory`.
3. Tags entry carries `remote_model`, ps loaded with same digest → `remote_inventory`.
4. Tags match, ps empty array → exit 1 `available_not_loaded`.
5. Tags match, ps entry for a different model → `available_not_loaded`.
6. ps-only match, no tags match → exit 2 `unknown`.
7. Case variant (`Llama3.2` vs `llama3.2`) → `unknown`.
8. `.gguf` suffix or directory-prefixed expected name → `unknown` (no normalization).
9. Tags and ps digests differ → exit 1 `identity_conflict`.
10. Selected entry with `name` ≠ `model` → `identity_conflict`.
11. Two selected tags entries → exit 2 `unknown`.
12. Selected ps entry missing `digest` → exit 2 `invalid_input`.
13. Empty-string digest → `invalid_input`.
14. `models` key absent or not an array → `invalid_input`.
15. Unreadable `--ps` path → `invalid_input`.
16. Same as case 1 but `expires_at` in the past → still exit 0 (no time logic).

## Tradeoff
Case 8 and case 16 are the two least obvious to a reviewer. Keep them: they are the only fixtures that prove the classifier refuses normalization and time logic, which are the two most likely scope-creep paths.

## Limits
- Static review of the contract and existing evidence. Nothing was executed.
- The classifier and fixtures are absent in the tree at the time of review; re-check the file against items a–h and cases 1–16 once it lands.
- Vendor field names were taken from existing round-11 rows, not re-fetched.
- Installs or upgrades: none.
