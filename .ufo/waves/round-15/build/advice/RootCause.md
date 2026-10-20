# RootCause — duplicate-corpus guard (read-only)

## Axes
- **Contract correspondence:** whether the runner does what its author documentation promises.
- **Pre-child rejection:** whether a duplicate corpus that meets the 16-distinct-name floor is stopped before any classifier child launches.
- **Valid-corpus preservation:** whether the existing unique-corpus measurement path remains admitted.

## Reconstructed contract and defect

`.ufo/waves/round-14/measure.py:13-14` promises that a narrower **or duplicated** corpus fails the whole measurement before any child is spawned; `LIMITS` repeats that claim at line 77. The round-start snapshot, `.ufo/waves/round-15/frozen/measure-before.py:350-362`, instead canonicalizes each nonblank string name with `strip()`, computes `unique = len(set(declared))`, and adds a corpus problem only for `unique < MINIMUM_UNIQUE_CASES` (16). It never compares the number of declared names with the unique count.

Consequently, a corpus with at least 16 distinct stripped names and any repeated stripped name leaves `problems` empty. In the baseline `run()` (`measure-before.py:372-383`), that skips the corpus-rejection branch and, when the tool is present, calls `measure_case` once per entry; `measure_case` invokes `subprocess.run` (`measure.py:211-240`). Thus the minimum-only test does not implement the documented duplicate rejection. This is a static control-flow reconstruction, not a run.

The latest relevant historical verifier is `corpus/lessons/round-14-verifier-spotcheck.md:142`. It independently names this R1 defect, describes the ≥16-distinct duplicate evasion, and explicitly limits its finding to static inference. It also preserves the distinction that the fixed round-14 repertoire was independently counted 51/51 unique; that count cannot establish rejection of arbitrary duplicate corpora. The inherited `acceptance.json` `final_corpus` receipt (`.ufo/waves/round-14/acceptance.json:1831-1857`) records the normal corpus at 51 unique / 16 minimum, 51 passed, 0 failed. It is positive evidence for that historical unique-corpus measurement, not a duplicate-guard test.

The classifier fixtures named `invalid_duplicate_selected_tags` / `invalid_duplicate_selected_ps` concern duplicate selected records in tags/ps inputs, not duplicate fixture `name` values in the measurement corpus. Their presence in the ordinary corpus does not cover the R1 runner defect.

## Current source state

The historical pre-edit source is pinned by `.ufo/waves/round-15/frozen/manifest.json` (source path `.ufo/waves/round-14/measure.py`, source commit `6e348e28943849aceb08d6954dee92be48ce9ba8`). The current `.ufo/waves/round-14/measure.py:350-364` now includes `if len(declared) != unique: problems.append("duplicate case names")` before the unchanged minimum check. Its `run()` keeps the pre-child `if corpus` branch (`:374-385`), so read-only source inspection shows the missing duplicate predicate has been added while the 16-name floor remains. This current-source observation is not behavioral verification.

`.ufo/waves/round-15/build/advice/GuardRepair.md:48-55` likewise records source read-back only and says no tests or runner executions were performed. `.ufo/waves/round-15/build/validation.json` is the wave-spec runner's exit-0 validation record, not evidence that duplicate inputs were rejected by the measurement CLI. I found no round-15 behavioral red/green receipt in the inspected artifacts; the fixture JSON files alone are expected cases, not observations.

## Limits

Read-only inspection only; no runner, harness, tests, build, or verifier was executed. No behavior is claimed as experimentally proven. The `lsp` device was unavailable in the mounted tool inventory (`xd://lsp` returned “No such tool”), so these findings rely on direct source and committed-artifact reads rather than semantic LSP references. No other callsite audit is claimed. No tools were installed or updated.

Report: .ufo/waves/round-15/build/advice/RootCause.md
