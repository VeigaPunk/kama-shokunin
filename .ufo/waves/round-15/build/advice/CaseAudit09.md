# CaseAudit09 — original cases 18 and 19 vs. the duplicate-corpus guard

Scope: read-only audit. No code executed (no classifier child, no measure run, no
selftest); all conclusions below are static traces. No installs or upgrades.

## Artifacts read

- `tests/ollama-evidence/cases.json` — indexes 18 and 19 only (lines 293-306 and
  309-322 respectively).
- `tools/kama-ollama-evidence.py` — classifier actually invoked by the runner
  (`DEFAULT_TOOL` at `.ufo/waves/round-14/measure.py:57`).
- `.ufo/waves/round-14/measure.py` — `corpus_problems` (lines 350-363), `run`
  (365-424), `measure_case` (211-343), `case_name` (131-137),
  `case_problems` (139-149).
- `.ufo/waves/round-15/frozen/measure-before.py` — byte-identical to the current
  `.ufo/waves/round-14/measure.py` (`cmp -s` reported IDENTICAL), so the before
  snapshot preserves the pre-repair guard.

## Literal case data (observed)

### Index 18 — `unknown_tag_qualifier_not_normalized`

```json
{"name": "unknown_tag_qualifier_not_normalized",
 "tags": {"models": [{"name": "llama3:8b", "model": "llama3:8b",
                      "digest": "sha256:1111...1111"}]},
 "ps":   {"models": [{"name": "llama3:8b", "model": "llama3:8b",
                      "digest": "sha256:1111...1111"}]},
 "expect": "llama3", "expected_exit": 2, "expected_finding": "unknown"}
```

Expected pair: **exit 2 / `unknown`**.

### Index 19 — `identity_conflict_ps_digest_mismatch`

```json
{"name": "identity_conflict_ps_digest_mismatch",
 "tags": {"models": [{"name": "llama3:8b", "model": "llama3:8b",
                      "digest": "sha256:1111...1111"}]},
 "ps":   {"models": [{"name": "llama3:8b", "model": "llama3:8b",
                      "digest": "sha256:2222...2222"}]},
 "expect": "llama3:8b", "expected_exit": 1, "expected_finding": "identity_conflict"}
```

Expected pair: **exit 1 / `identity_conflict`**.

Both fixtures are well-formed for `case_problems`: `expect` is a string,
`expected_exit` is a non-bool int, `expected_finding` is a string. Each pair
`(expected_finding, expected_exit)` is consistent with the classifier's
`FINDING_EXIT` map (`tools/kama-ollama-evidence.py:91-97`: `unknown: 2`,
`identity_conflict: 1`).

## Exact classifier branches

Classifier precedence is fixed in the module docstring (lines 30-36) and in
`classify` (218-263).

### Case 18 → `unknown` 2

- `_matching` (190-192) is exact, case-sensitive equality against
  `entry.get('name')` **or** `entry.get('model')`; there is no `:tag`
  normalization, no `:latest` inference, no basename/case/digest-prefix
  normalization (docstring lines 10-14).
- `expect="llama3"`; both tags and ps entries carry `"llama3:8b"`, so
  `tags_matches == []` and `ps_matches == []`.
- Line 231-232: `if not tags_matches: return 'unknown',
  ['no_tags_entry_matches_expected_name']` — exit 2 via `FINDING_EXIT`.
- Precedence note: the no-tags-match branch fires even when a ps entry matches
  or conflicts; here ps does not match either, so the result is
  unambiguously `unknown`, not `identity_conflict` or `available_not_loaded`.
- `available_not_loaded` requires a selected tags entry (line 254), which does
  not exist here, so the same-name/digest data cannot produce exit 1.

### Case 19 → `identity_conflict` 1

Static walk through `classify`, first match wins:

1. `validate_capture` for tags and ps (172-187): both are objects with
   `models` arrays of objects and string `name`/`model`/`digest`; no
   `remote_*` fields; passes.
2. Duplicate selection (227-230): exactly one tags match and one ps match for
   `"llama3:8b"`; passes.
3. Tags match exists (231 skipped).
4. `_identity_conflict(tag)` (195-202, 234-235): `name == model ==
   "llama3:8b"`, both nonempty and equal → false. Same for the ps entry
   (236-237) → false.
5. `_digest_present` (213-215, 238-241): both digests are nonempty strings →
   false.
6. Remote markers (205-210, 243-252): no `remote_model`/`remote_host` →
   no match.
7. `ps_matches` is nonempty, so `available_not_loaded` (254-256) is skipped.
8. Line 259-260: `tag['digest'] != ps_entry['digest']` (`…1111` vs `…2222`)
   → `return 'identity_conflict', ['tags_ps_digest_mismatch']` — exit 1.

The name/model equality means the earlier identity-conflict branches cannot
fire; the only conflict evidence is the unequal digest strings. The classifier
does not validate hex form, prefix case, or digest length, so the literal
strings are compared as-is.

## Runner behavior for these two cases (unchanged by the guard)

`measure_case` (211-343) takes `expect`, `expected_exit`, `expected_finding`
verbatim from the fixture, stages `tags.json`/`ps.json` with
`json.dumps(...)+"\n"`, and spawns `python -I -B <tool> --tags … --ps …
--expect …`. It then compares child exit, `finding_id`, schema
`kama-ollama-evidence/v1`, `verdict_exit == observed exit`, readiness
`unknown`, and scope `offline-captures-not-runtime`. Nothing in this path
normalizes `expect` or the expected literals, so the two expected pairs above
are the literal fixtures and the classifier branches traced in the previous
section produce them.

## Why the new duplicate-corpus guard cannot alter these results

Guard semantics under repair (`.ufo/waves/round-15/build/spec.json`,
`GuardRepair`): inside `corpus_problems`, using the already-collected stripped
`declared` names, reject `len(declared) != unique` with the stable reason
`"duplicate case names"`, preserving the existing `unique < 16` minimum check.
Current `.ufo/waves/round-14/measure.py:350-363` implements only the minimum
check; the module `LIMITS` string at line 77 already claims narrower **or
duplicated** corpora fail, which is the documented-but-unimplemented behavior
being repaired.

Observed facts about the committed corpus relevant to that guard:

- 51 cases; `unique_raw == unique_stripped == 51`; no duplicate stripped names,
  no blank names, no non-string names.
- `"unknown_tag_qualifier_not_normalized"` and
  `"identity_conflict_ps_digest_mismatch"` each occur exactly once; `strip()`
  is the identity for both (no leading/trailing whitespace), so the guard's
  canonical form equals the recorded `case_name`.

Therefore:

1. **Guard scope is corpus-level only.** `corpus_problems` reads only
   `case["name"]` (350-355) and never touches `expect`, `expected_exit`,
   `expected_finding`, `tags`, or `ps`. It cannot rewrite any case's expected
   or observed pair.
2. **The committed corpus passes the repaired guard.** With 51 declared names
   and 51 unique stripped names, `len(declared) == unique`, so the new
   duplicate reason is not appended; the minimum check is also satisfied
   (51 ≥ 16). `run()` takes the `elif tool_present:` branch (375 onward) and
   measures cases 18/19 exactly as before.
3. **A rejected corpus never reaches the classifier.** If the guard did fire,
   `run()` (375-378) emits `unmeasured_record` for every case with detail
   `"corpus: …"`, `observed_exit=None`, `passed=False`, and exit 1, before the
   `tempfile`/`subprocess` block is entered. That is fail-closed wholesale
   rejection, not a per-case change: cases 18/19 would become unmeasured, never
   silently re-graded to a different finding/exit.
4. **These names are not duplicate-collision candidates.** A duplicate guard
   keyed on `strip()` can only flag a name that appears at least twice after
   stripping. Neither assigned name does, and neither collides with another
   case name; adding the guard cannot single them out.

## Contrary evidence / limits

- I did not execute the runner or classifier (per assignment), so the branch
  traces are static, not observed process exits. Confidence: high for the
  classifier branch mapping and for the corpus name census (both read
  directly); high for the guard interaction given the GuardRepair spec.
- The duplicate-rejection branch was **not yet present** in
  `.ufo/waves/round-14/measure.py` at read time (only the minimum check at
  358-363). The "cannot alter" argument therefore assumes the landed edit
  matches the spec: append a problem when `len(declared) != unique`, without
  changing `measure_case`, CLI schema, or classification. If the final edit
  changes name canonicalization (e.g., compares raw vs. stripped) or rejects
  per-case, re-check.
- Minor, non-affecting divergence: `case_name` (131-137) returns the
  **unstripped** name for records while the guard canonicalizes with
  `strip()`. For cases 18/19 raw == stripped, so record names and guard names
  agree; a future whitespace-bearing name could differ in reporting only, not
  in these results.
- The classifier's own `--selftest` (`run_selftest`, 347+) reads the same
  `cases.json` and is untouched by the runner guard; not audited beyond that
  observation. No other classifier path exists: the runner's `DEFAULT_TOOL`
  points at `tools/kama-ollama-evidence.py`.
- No other case in indexes 18/19-adjacent range was audited (remaining tail
  assigned elsewhere).

Remaining unknowns: exact final bytes of the repaired `corpus_problems` (edit
not landed at read time); whether any sibling lane modifies the classifier
(no evidence in the read files).

Report: .ufo/waves/round-15/build/advice/CaseAudit09.md
