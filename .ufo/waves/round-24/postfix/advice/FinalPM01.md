# FinalPM01 — PM01-blanket-metadata-refusal (bounded falsification, fresh pin)

**VERDICT: KILLED.** The exact registered PM01 operator, applied to the pinned
auditor, is detected by the current-arm graded row PG02-complete-fleet-promisor-config.

## Mutant and identity
- Operator: `PM01-blanket-metadata-refusal` from `tests/report-audit/promisor-mutants.py`
  sha256 `971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200`
  (pin `92063cfc60e217fa7e2098c568578119b16a1b95`); applied via the pinned
  `apply_mutation()`/`compiles()` API imported from that file — no re-anchoring.
- Alternative census: regex `state = promisor_state(repo)` x0 (not applicable),
  insert anchor `if __name__ == "__main__":` x1 → exactly one applicable
  alternative (index 1, the spelling-independent PM01_INSERT form); mutant compiles.
- Auditor pristine sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`
  (byte-identical to the pinned file); mutant sha256 `1aab8149bb1c3ab165b15b8330101367856534d2501306a3643aa887a703becc`.
- Clone: `/fast/scratch/hyaku/kama-r24/postfix/FinalPM01/clone` (--no-hardlinks,
  detached at the pin, worktree clean). Grid sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`;
  manifest sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (47 cells, bytes untouched).

## Detector actually run (bounded, 2 cells per tool, current arm only)
`python3 tests/report-audit/promisor-grid.py --arm current --current <auditor>
--case PG02-complete-fleet-promisor-config --case PG08-complete-fleet-plain --json --out <dir>`,
TMPDIR = own scratch (`tmp-pristine` / `tmp-mutant`). The mutator's default
sensitivity path (47 pristine cells) was NOT invoked.

## Decisive observations (actual outputs)
- Pristine tool: grid exit 0; violations 0; PG02 exit 0 (expected 0) met/met_amended/met_original
  all true, twin_equal true; PG08 exit 0 met true. No timeouts, tracebacks, harness_leaks 0,
  `objects_acquired` empty.
- Mutant tool: grid exit 1; violating_cases `[PG02-complete-fleet-promisor-config]`;
  PG02 exit **2** vs expected 0 → problems `exit 2 != 0`, `reason is the r23 metadata refusal`,
  `reason does not name the unavailable object`; met=false, met_amended=false,
  met_original=false; stderr `could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)`.
  No internal_error, traceback, timeout or leak; `objects_acquired` empty.
- PG08 (plain twin) exit 0, met true under both tools — the mutant refuses only the
  promisor-marked fleet, i.e. it is a metadata over-refusal, not a general breakage.
- Exit taxonomy: PG02 pristine 0 → mutant 2 = **normal→2 refusal-2** (a changed substantive
  verdict, not a names/reason-only or same-exit diagnostic failure).

## Residual / limits
- The kill rests on the graded row PG02 itself (exit 2 != 0). The PG02↔PG08 twin comparison
  is **not** established in the mutant run (twin_equal None: PG02 produced no verdict document
  under the refusal), so no twin-mismatch credit is claimed.
- Bounded sample: 1 discriminating graded cell (+1 plain-twin control) per tool. This is
  survival/kill evidence for that cell only, not a global-equivalence claim about PM01.
- Restored: the pinned auditor was copied, never edited in place; the pristine copy and the
  clone file are byte-identical to `b9be4f42…`, clone `git status` clean, production tree
  untouched. The 47-cell manifest bytes were read only.
- PM08 remains manual review-only; no executable/static-wiring assertion was made for it.

Raw evidence: `.ufo/waves/round-24/postfix/out/FinalPM01/pm01-evidence.json`,
`pm01-application.json`, `pristine-grid.json`, `mutant-grid.json`, `pm01-mutant.diff`.
No tool installs were needed (git 2.56.0, Python 3.14.8, pre-existing).
