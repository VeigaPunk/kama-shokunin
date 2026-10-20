# Round 14 — ReviewSchema (static review of classifier schema, fail-closed behavior)

Lane: kama-shokunin · Seat: ReviewSchema (reviewer, leaf) · Mode: read-only, no tests/builds/smoke runs.

## Evidence scope

- Contract: `.ufo/waves/round-14/spec.json` line 2 ("Classifier shared interface"), items Classifier (line 9), Fixtures (line 14), Harness (line 19), ReviewSchema (line 84).
- Pending files, not present at review time: `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`, `.ufo/waves/round-14/measure.py`. Per contract, these are pending, not defects. Findings below are contract-level and must be re-checked against the file once it lands.
- Source fields, fetched read-only 2026-10-20 (UTC) from `https://docs.ollama.com/api/tags.md` and `https://docs.ollama.com/api/ps.md` (OpenAPI 3.1.0, info.version 0.1.0):
  - `/api/tags` `ModelSummary`: `name`, `model`, `remote_model` ("Name of the upstream model, if the model is remote"), `remote_host` ("URL of the upstream Ollama host, if the model is remote"), `digest` ("SHA256 digest identifier of the model contents"). Example: `name: gemma4`, `model: gemma4`, `digest` 64-hex with no `sha256:` prefix.
  - `/api/ps` `Ps`: `name`, `model`, `digest` ("SHA256 digest of the model"), `expires_at`, `size_vram`, `context_length`, `details`. No `remote_model` or `remote_host` property is documented for `Ps`.
  - Consequence: exact string digest comparison without prefix normalization matches both documented examples. The `remote_*` checks on ps entries are defensive only; they are not a documented field.

## Findings by severity

### HIGH

**H1. Uncaught Python exception exits 1, which is a verdict code.** Exit 1 means `available_not_loaded`, `remote_inventory` or `identity_conflict`. An unhandled traceback (default CPython status 1) would be read as a real verdict by any exit-code-only consumer. Owner: Classifier. Recommendation: wrap `main` in a catch-all that maps every failure path (I/O, decode, type, argparse-adjacent, internal) to exit 2 with a `kama-ollama-evidence/v1` JSON object on stdout (`finding_id` = `invalid_input`, `verdict_exit` = 2, `readiness` = `unknown`). No traceback on stdout or stderr. Owner: Harness. Recommendation: a case passes only when both exit code AND `finding_id` equal the literal fixture values; exit code alone must never pass a case.

**H2. `--help` / `-h` exits 0 by argparse default.** Exit 0 is contractually reserved for `loaded_same_digest`. A script that checks only exit status would treat help output as a loaded verdict. Usage errors (argparse default exit 2) print to stderr and emit no JSON, which also breaks the "JSON stdout" schema for those paths. Owner: Classifier. Recommendation: override the help action so `--help` exits with a non-zero, non-verdict-compatible status documented as "no verdict" (2 is the only code the contract defines for non-verdicts), and state in the module docstring that exit 2 without JSON means CLI usage error. Alternative, if the owner keeps exit 0 for help: document it explicitly as "exit 0 without JSON is not a verdict" and add a fixture asserting that consumers must parse JSON before trusting exit 0. Choose one; the current silent default is a fail-open path.

**H3. Duplicate JSON object keys are silently collapsed.** `json.loads` keeps the last of duplicate keys. Two `name` keys in one entry (or two `models` keys at top level) can hide an identity conflict or change which entry is selected. Owner: Classifier. Recommendation: `object_pairs_hook` that raises a typed error mapped to `invalid_input` on any duplicate key within an object.

**H4. The contract has no total precedence order; the same input can produce different exits.** Owner: Classifier and Fixtures must pin one order before implementation. Unresolved collisions found:

| # | Input shape | Reading A | Reading B | Exit difference |
|---|---|---|---|---|
| a | Two selected tags entries, same digest | `duplicate selected` → unknown | — | none |
| b | Two selected tags entries, differing digests | `differing matching digests` → identity_conflict | `duplicate selected` → unknown | 1 vs 2 |
| c | Selected tags remote entry whose digest differs from selected ps digest | remote_inventory ("regardless digest") | identity_conflict ("differing digests") | 1 vs 1 (finding differs) |
| d | Selected ps has remote marker; no tags entry matches expect | remote_inventory ("selected ps markers") | unknown ("no tags match") | 1 vs 2 |
| e | Remote entry in tags, unrelated to expect; selected local entry + matching ps | remote_inventory if "remote tags" means any entry | loaded_same_digest if only selected entries count | 1 vs 0 |
| f | Schema-invalid file that also contains a remote marker | remote_inventory ("regardless digest") | invalid_input ("remote takes precedence only after schema valid", Fixtures prompt) | 1 vs 2 |
| g | expect equals `name` of entry A and `model` of entry B (A≠B) | duplicate selected → unknown | — | none (define "selected" explicitly) |

Recommended order (fail-closed, total):
1. Input layer: file readable, UTF-8 JSON, no duplicate keys, top-level object with `models` array, every entry object with string `name` and `model`, `digest` present as a string where required. Any failure → invalid_input (2).
2. Selection: entry selected iff `expect` equals its `name` OR its `model` (case-sensitive). Selected count ≠ 1 in either file → unknown (2). Count is taken before any digest comparison.
3. Within-entry identity: selected entry with `name` ≠ `model` → identity_conflict (1).
4. Remote markers on the selected tags entry or the selected ps entry → remote_inventory (1), regardless of digest, once steps 1–3 pass. Unselected entries never change the verdict.
5. Tags selected absent → unknown (2). This also covers case (d): a ps remote marker with no tags match is unknown, not remote_inventory. Owner chooses; recommended because the contract lists "no tags match → unknown" as the explicit rule.
6. Selected ps present: digest differs from selected tags digest → identity_conflict (1); digest equal → loaded_same_digest (0), only when no remote markers.
7. Selected ps absent (ps list valid, possibly empty) → available_not_loaded (1). A ps entry matching only by digest under a different name is ignored, and the verdict is still available_not_loaded.

Case (b) and (c) need an explicit owner decision; the table above shows the choice I recommend (duplicate → unknown first, identity_conflict only on a single selected pair). State the choice in the module docstring and in cases.json.

**H5 (naming collision, MEDIUM-HIGH).** `--selftest` emits a JSON object with `verdict_exit` 0 for `clean`. That key name matches the classifier's exit-0 meaning (`loaded_same_digest`). A reader of the JSON could take the selftest's `verdict_exit: 0` as a loaded verdict. Owner: Classifier. Recommendation: rename the selftest exit field (for example `selftest_exit`), or keep `verdict_exit` only for classifier output and make selftest output use `finding_id: clean|selftest_failed` plus `selftest_exit`.

### MEDIUM

**M1. `remote_*` value typing.** The contract says "nonempty". Read literally, `"remote_host": ""` is not a remote marker and a digest match would reach `loaded_same_digest`. The same applies to `null`. Owner: Classifier. Recommendation (fail-closed): a `remote_model` or `remote_host` key present with a value that is not a nonempty string (including empty string, null, number, bool, object, list) → invalid_input (2). Absent key → no marker. Fixtures must encode this explicitly; the contract is silent.

**M2. Identity type checks.** `name`, `model`, `digest` must be `type(x) is str`, not `isinstance`, so booleans are not coerced. Empty string `name`/`model`/`digest` → invalid_input (contract: "missing identity/digest" fails closed; empty is missing). Owner: Classifier.

**M3. `--expect` validation.** Empty or whitespace-only `expect` → invalid_input (2). Matching is exact and case-sensitive; no GGUF basename, no lowercasing, no `:latest` default insertion. A fixture should show `expect=llama3.2` does not match `llama3.2:latest` (unknown). Owner: Classifier and Fixtures.

**M4. Digest comparison.** Documented digests are bare 64-hex (both schemas). Exact string equality with no prefix stripping matches the docs and the contract. Do not add `sha256:` normalization. Owner: Classifier (informational).

**M5. I/O edge cases.** Missing file, directory path, permission error, invalid UTF-8, UTF-8 BOM, empty file, top-level JSON array, and `models: null` must each map to invalid_input (2) with JSON on stdout and no traceback. Owner: Classifier. The contract does not set an input size bound; I do not recommend adding one unless the owner already plans it (scope).

**M6. `finding_id` value is unspecified.** The contract lists `finding_id` as a key but not its value set. Fixtures refer to `expected_finding` and Harness compares IDs. Recommendation: `finding_id` equals the verdict string exactly (`loaded_same_digest`, `available_not_loaded`, `remote_inventory`, `identity_conflict`, `unknown`, `invalid_input`). Owner: Classifier and Fixtures must agree before cases.json is written.

**M7. Required flags.** `--tags`, `--ps`, `--expect` should be `required=True` in argparse. A missing `--ps` must not be treated as "empty ps" (contract: "missing ps input does not" permit available_not_loaded). Owner: Classifier.

### LOW / notes

- `json.loads` accepts `NaN`/`Infinity` by default. These cannot affect identity fields, but `parse_constant` rejection is a cheap way to keep the input strict. Optional.
- Stdout must be exactly one JSON object per run. Owner: Classifier.
- The `ps` schema has no documented `remote_*` fields; the defensive check is contract-driven, not source-driven. Document it that way.

## Owner recommendations (no tests; no edits by this seat)

### Classifier (`tools/kama-ollama-evidence.py`)
1. Catch-all → exit 2 + JSON `invalid_input`; no traceback (H1).
2. Decide `--help` exit behavior and document it (H2).
3. Duplicate-key rejection (H3).
4. Implement the seven-step total order above; document it in the module docstring (H4).
5. Rename selftest exit field (H5).
6. Strict `remote_*` typing (M1), `type(x) is str` checks (M2), `expect` validation (M3), required flags (M7).

### Fixtures (`tests/ollama-evidence/cases.json`)
Add literal cases (independent expected values, not computed):
- name matches entry A, model matches entry B → unknown (alias ambiguity, g)
- two selected tags entries, same digest → unknown; differing digests → per decided order (b)
- selected entry with `name` ≠ `model` → identity_conflict
- `ollama cp`-style alias: different name in ps, same digest as selected tags entry → available_not_loaded (adversarial: digest alone must not load)
- remote tags entry selected → remote_inventory even with matching ps digest
- selected ps remote marker, tags local → remote_inventory
- selected ps remote marker with no tags match → per decided order (d)
- unselected remote tags entry plus selected local matching ps → per decided order (e)
- `remote_host: ""`, `remote_model: null`, `remote_host: 42` → invalid_input (M1)
- duplicate key in tags entry → invalid_input (H3)
- schema-invalid file plus remote marker → invalid_input (f)
- ps `{"models": []}` with tags match → available_not_loaded; ps `{}` → invalid_input
- tags `models: null`, top-level array, missing `models` → invalid_input
- missing file, directory path, invalid UTF-8 → invalid_input
- `expect` empty string → invalid_input; `expect` case mismatch → unknown; `expect=llama3.2` vs `llama3.2:latest` → unknown; GGUF-style `model.Q4_K_M.gguf` vs `model:Q4_K_M` → unknown
- digest empty string on selected entry → invalid_input

### Harness (`.ufo/waves/round-14/measure.py`)
- A case passes only when exit code AND `finding_id` both equal the literal fixture values (H1). A traceback exit 1 must fail every case expecting a non-1 verdict and every case expecting exit 1 whose ID differs.

### Owners of other files
- None touched by this seat.

## Verification gaps / limits

- Static review only. No tests, builds, smoke runs, or classifier execution (per contract and assignment).
- Pending files (`tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`, `measure.py`) were not present. Findings are contract-level; re-check each finding against the landed file.
- Docs were read once each from docs.ollama.com `.md` alternates on 2026-10-20 UTC. Field semantics are from the OpenAPI schema text, not from Ollama source; no Ollama server behavior was observed or assumed.
- No network acquisition, no local runtime or endpoint contact, no secret or environment reads.
- The contract is silent on several points listed in H4 and M1; those are decisions for owners, not verified defects.

## Tooling record

- No tools installed or upgraded by this seat.

## Final static read — landed `tools/kama-ollama-evidence.py` (snapshot tag 1E5E)

Re-read at three snapshots (58A5 → BA73 → 1E5E); the report reflects the latest, 1E5E, 531 lines. Static only; no execution, no tests.

### Ladder conformance (code vs rulings.json and L1 ladder)

Checked in `classify()` (lines ~215-262) in order:

1. Structure: `validate_capture` rejects non-object envelope, missing or non-array `models`, non-object entries, and any present non-`str` name/model/digest/remote_model/remote_host (null included). Applied to all entries, selected or not. Pass.
2. Duplicate selection: >1 match in tags or ps → invalid_input (2), before any conflict check. Pass.
3. Name/model conflict on selected tags or ps entry (both nonempty, unequal) → identity_conflict (1). Pass. Name-only and model-only identity accepted.
4. No tags match → unknown (2), even when ps matches. Pass.
5. Selected tags digest missing/empty → unknown (2); selected ps digest missing/empty → unknown (2), checked only when a ps match exists. Pass.
6. Remote marker (nonempty string) on selected tags, then selected ps → remote_inventory (1), before digest comparison. Pass.
7. No selected ps → available_not_loaded (1). Empty ps array passes; missing ps file fails closed upstream in `read_json_file`. Pass.
8. Unequal exact digests → identity_conflict (1); equal → loaded_same_digest (0). Exact string compare, no normalization. Pass.

Unselected entries affect nothing except global type validity (step 1). Pass.

### Prior owner-directed items, confirmed closed in code

- H1 uncaught traceback → exit 2: `main()` catch-all emits invalid_input JSON; selftest child crash yields `stdout_not_single_json_object` and fails the case. Closed.
- H2 help exit 0: documented in the epilog as non-classification; `SystemExit` re-raised. Closed by documentation, per ruling.
- H3 duplicate keys: `_pairs` object_pairs_hook on every object, including nested ones and cases.json. Closed.
- H5 selftest key collision: selftest emits `kama-ollama-evidence-selftest/v1` with `finding_id` clean|selftest_failed and `verdict_exit` 0|1; the classifier schema is distinct. Closed.
- M1 remote typing: null, number, bool, and list values rejected; empty string is not a marker. Closed.
- M3 expect: empty string (and absent) → missing_required_argument (2). Whitespace is accepted and matched exactly, per "no trimming". Closed.
- M5 I/O: non-regular (directory, FIFO via O_NONBLOCK plus S_ISREG), oversize (4 MiB bound, read loop capped), invalid UTF-8, and BOM (json.loads rejects) all map to invalid_input. Closed.
- M7 required flags: `not args.tags or not args.ps or not args.expect`. Closed.
- Child invocation for selftest: `-I -B`, isolated cwd, 30 s timeout, TemporaryDirectory only. Closed.

### Residual code findings

- LOW-1 (robustness, `main()` lines ~520-527): the catch-all calls `emit()` and, if stdout is closed or a broken pipe (`OSError`), that second write raises out of `main` and produces a traceback with exit 1, a verdict code. Recommended fix: wrap the emit in the except branch with `except OSError: pass` before returning 2. Not reachable by the fixtures; reachable by `| head` style pipelines.
- LOW-2 (docs nit, module docstring line 38): one line exceeds the rest of the docstring width and joins two sentences. Cosmetic; no contract effect.
- INFO: `--expect` whitespace-only strings are valid and exact-match only. Consistent with the ruling; noted so the Fixtures owner does not expect trimming.

### Fixture expectations (names and literal expectations only)

I listed the committed cases (about 56 unique names, well above the 16 minimum) and scanned each expected finding against the ladder. The adversarial rows (ps-only alias with no tags match → identity_conflict; ps digest mismatch → identity_conflict; remote on unselected entries ignored; empty-string markers absent; invalid types → invalid_input; missing digest → unknown; duplicate selected → invalid_input) match the ladder. I did not re-derive each row's input bytes.

### Verification gaps

- Static only; no selftest, classifier, or harness run, per assignment.
- Ladder conformance is from reading code and the fixture names/expectations, not from executing the 56 cases.
- Ollama field semantics (digest join, ps remote marker) remain INFERENCE per the rulings; not re-verified here.

### Conclusion

No blocking defects against the rulings ladder. One LOW robustness item (LOW-1) and one cosmetic item. Ready for L1 final gate.

