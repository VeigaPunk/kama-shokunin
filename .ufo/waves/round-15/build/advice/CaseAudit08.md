# CaseAudit08 — cases 16/17 literals vs the new corpus duplicate guard

Read-only audit; no code executed, no tests run. Confidence labels: **[observed]** =
direct file read; **[inference]** = static code-path reading.

## Scope and files

- Fixtures: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json`
  (51 objects, indexes 0–50).
- Classifier: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py`
  (the file `measure.py` defaults to via `LANE = WAVE.parents[2]`, lines 55–58).
- Runner under repair: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py`
  (`corpus_problems`, lines 350–362; call site line 372; branch line 375).
- New guard fixtures: `tests/ollama-corpus-guard/*.json` — **absent at read time**
  (`glob` returned path-not-found).

## Assigned fixtures (exact literals) **[observed]**

### index 16 — `unknown_case_sensitive_name`

```
tags: {"models":[{"name":"llama3:8b","model":"llama3:8b",
       "digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111"}]}
ps:   {"models":[{"name":"llama3:8b","model":"llama3:8b",
       "digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111"}]}
expect: "Llama3:8B"
expected_exit: 2
expected_finding: "unknown"
```

### index 17 — `unknown_gguf_suffix_not_stripped`

```
tags: {"models":[{"name":"llama3:8b.gguf","model":"llama3:8b.gguf",
       "digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111"}]}
ps:   {"models":[{"name":"llama3:8b.gguf","model":"llama3:8b.gguf",
       "digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111"}]}
expect: "llama3:8b"
expected_exit: 2
expected_finding: "unknown"
```

Both names are non-blank, whitespace-free lowercase-ASCII strings; `strip()` is the
identity on them. They are distinct from each other and from the other 49 names
(round-14 `acceptance.json` records `unique_case_names: 51`, `total: 51`).

## Classifier branch trace (identical for both) **[observed code]**

1. `read_json_file` (`:137`) — both captures are regular UTF-8 JSON, no duplicate
   keys, no NaN/Infinity → no `InputError`.
2. `validate_capture` (`:172–187`) — both documents are objects with a `models`
   list of objects; `name`/`model`/`digest` are strings → validation passes.
3. `_matching` (`:190–192`) — selection is exact `entry.get('name') == expected or
   entry.get('model') == expected`, no `strip`, no casefold, no `.gguf` basename, no
   `:latest` or digest-prefix normalization (module docstring `:12–14`).
   - Case 16: `"llama3:8b" != "Llama3:8B"` → `tags_matches == []`.
   - Case 17: `"llama3:8b.gguf" != "llama3:8b"` → `tags_matches == []`.
4. `classify` (`:218`) — duplicate-selection checks (`:226–229`) see 0 matches and
   are not taken; `if not tags_matches: return 'unknown',
   ['no_tags_entry_matches_expected_name']` (`:231–232`) fires **first**. Everything
   after it (name/model conflict, digest presence, remote markers, ps match,
   digest equality) is unreachable for these two cases.
5. `classify_payload` (`:267–276`) sets `finding_id: "unknown"`,
   `verdict_exit: FINDING_EXIT['unknown'] == 2`; `_run` (`:510–514`) returns
   `FINDING_EXIT[finding] == 2`. `FINDING_EXIT` is `:91–98`.

So literal exit 2 / ID `unknown` is the only self-consistent pair: `_valid_case`
(`:334–343`) rejects any case whose `expected_exit` differs from
`FINDING_EXIT[expected_finding]`. `measure.py` independently compares the observed
process exit to 2, the observed `finding_id` to `unknown`, `verdict_exit` to the
process exit, plus constant `schema`/`readiness`/`scope` (`measure.py` `:290–323`).

Contrast that pins "no normalization" as deliberate: index 3
`loaded_exact_gguf_name_no_stripping` uses `expect: "model.gguf"` against
`name/model: "model.gguf"` and expects `loaded_same_digest`/0. The suffix is matched
only when the caller passes it exactly; case 17 is the negative twin.

## Why the new duplicate guard cannot alter these two results

The specified repair is name-keyed: `corpus_problems` already builds
`declared = [case["name"].strip() for dict cases with a non-blank str name]` and
`unique = len(set(declared))` (`measure.py:350–362`); the repair adds a rejection
when `len(declared) != unique` (stable reason "duplicate case names") alongside the
existing `unique < 16` check. Consequences:

1. **Placement is pre-child and corpus-wide.** `corpus_problems` is called at
   `measure.py:372`, before the `if corpus:` / `elif tool_present:` fork (`:375–383`).
   A non-empty `corpus` records every case via `unmeasured_record` (`observed_exit:
   None`, `observed_finding: None`) and forces `EXIT_FAIL`; the per-case
   `measure_case` path is never entered. On the committed corpus the guard must
   therefore yield `corpus == []`.
2. **The committed corpus passes the guard.** 51 declared names, 51 distinct,
   `51 >= 16`; cases 16/17 contribute one distinct name each and no duplicate.
   `strip()` changes nothing. So the run takes the unchanged
   `elif tool_present` branch and per-case behavior is byte-identical to pre-repair.
3. **The guard never reads classification fields.** It touches only `case["name"]`.
   It does not inspect `expect`, `tags`, `ps`, `expected_exit`, or
   `expected_finding`. Cases 16/17 sharing `expected_finding: "unknown"` (as do
   indexes 13/14/15/18/38/39/40/47) does not enter `declared`, so a shared finding
   class cannot reduce the unique count or trigger rejection.
4. **Case names are not inputs to the classifier.** `measure_case` builds argv with
   `--tags/--ps/--expect` only (`measure.py:230–235`); the name is a record label
   (`case_name`, `:131–137`) and the temp dir is `f"{index:02d}"` (`:220`), so
   neither renaming nor dedupe logic can reach the classification of `Llama3:8B` or
   `llama3:8b.gguf`. The classifier also never opens `cases.json` except under
   `--selftest`.
5. **No path drift in the record.** Because the guard passes, records for indexes
   16/17 keep `expected_exit: 2`, `expected_finding: "unknown"`, `readiness:
   "unknown"`, and reasons derived from the child, not from the corpus gate.

## Contrary evidence / risks (must hold for the claim to hold)

- **Guard key must be names, not content.** 46 of 51 fixtures share
  `expect: "llama3:8b"` (only indexes 3, 5, 12, 16, 18 differ). A guard that
  deduped on `expect`, on `(tags, ps)`, or on `expected_finding` would collapse the
  real corpus to 6 unique values `< 16` and reject it, converting every record to
  `unmeasured`/exit 1 — a guard bug that looks like the original one. The spec's
  "existing stripped declared names" wording is load-bearing; do not widen it.
- **Two canonicalizations coexist.** The classifier's own `--selftest` checks
  `len(names) != len(set(names))` on **raw** names (`:359–365`), while the runner
  guard uses `strip()`. Committed names contain no whitespace, so both agree today;
  a future whitespace-collision fixture (`tests/ollama-corpus-guard/WhitespaceCollision.json`)
  exercises the stricter runner rule and would not be caught by the classifier selftest.
- **Prior artifact does not show these literals observed.** Round-14
  `acceptance.json` records all 51 cases with `observed_finding: "unsupported"`,
  `observed_exit: null`, `passed: 0` — the measured run had the tool absent. The
  exit-2/`unknown` expectations above are contract-and-code derived; a round-15
  tool-present replay is still required to call them observed.
- **Guard failure mode is total, by design.** If a duplicate is injected into the
  real corpus, cases 16/17 are not measured at all (unmeasured records, exit 1).
  That is the intended fail-closed behavior and is not a classification change.
- **Current file state.** At read time `measure.py:350–362` still contained only
  the `unique < MINIMUM_UNIQUE_CASES` check; the duplicate rejection was not yet
  present in the file, so the exact reason token/format is unverified here
  (GuardRepair owns it).

## Limitations

- No execution of `measure.py`, the classifier, `--selftest`, or any guard harness;
  findings are static traces of the cited lines.
- Only cases 16/17 payloads, the corpus name list (for uniqueness), and the
  classifier/runner code paths were read; the remaining fixture bodies were not
  re-audited.
- No tool installs or upgrades were performed; nothing was written outside this
  report.
