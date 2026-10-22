# FinalPM05 — PM05-ignore-second-repo (canonical operator, fresh pin 92063cfc60e217fa7e2098c568578119b16a1b95)

**VERDICT: KILLED.** The exact registered PM05 operator, applied to the pinned auditor at that pin, is detected by the two current-arm graded rows it declares: `PG26-cross-repo-found-promisor` and `PG27-cross-repo-found-plain`.

## Mutant
- Operator `PM05-ignore-second-repo` from `tests/report-audit/promisor-mutants.py` sha256 `971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200`, applied through the pinned `apply_mutation()` / `compiles()` / `run_grid()` APIs imported from that file — no re-anchoring, no retargeting, no hand-written variant.
- Census: both registered alternatives match exactly once (regex x1, regex x1); the pinned `apply_mutation` canonically returns the first applicable one (index 0, the `--anchors` rule). Applied delta, one line, verbatim: `for store in stores:` → `for store in stores[:1]:` inside `lookup()` (auditor line 241). Mutant compiles (`compiles()` true).
- Auditor pristine sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f` (byte-identical to the pinned file); mutant sha256 `83a650f7b7123950d928db2b994eddd838db826c6fccb4d6951eb0c11a40bca1`; the grid reported the auditor digests it measured (`b9be4f42…` pristine, `83a650f7…` mutant).
- Clone `/fast/scratch/hyaku/kama-r24/postfix/FinalPM05/clone` (`--no-hardlinks`, detached at the pin, worktree clean); grid sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`; expectations manifest sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (47 cells, read-only); TMPDIR = own existing scratch `…/FinalPM05/tmp`.

## Detector actually run (bounded, 2 cells per tool, current arm)
Pinned `run_grid(grid, auditor, "current", ["PG26-cross-repo-found-promisor", "PG27-cross-repo-found-plain"], 600)`: one invocation for the pristine tool, one for the mutant, one for the restored bytes. The mutator's default/main sensitivity path (47 pristine cells) was NOT invoked; no full grid, no selftest, no historical suite.

## Decisive observations (actual outputs)
- Pristine: grid exit **0**, violations 0; PG26 and PG27 each exit 0 (expected 0), met, `twin_equal` true, `problems`/`amended_problems`/`original_problems` empty, `stderr_tail` empty, `objects_acquired {"lane": [], "fleet": []}`.
- Mutant: grid exit **1**, violations 2 — both declared rows unmet (PG26 policy, PG27 control): each exit **1** vs expected **0**; `kinds ["landed-unresolved","unresolved-full-hash"]` vs expected `[]`; defects `('landed-unresolved', 'f723c76c41609df00704d93c29bd44408dcbdd2e')` and `('unresolved-full-hash', 'f723c76c41609df00704d93c29bd44408dcbdd2e')` — the fleet-only commit the lane lacks; `met=false`; `objects_acquired {"lane": [], "fleet": []}` (no lazy fetch, no transport); no `internal_error`, traceback, timeout or leak (`harness_leaks` 0, `harness_fault` None).
- Restored bytes: the same detector on the restored pristine auditor returns grid exit **0**, violations 0, both rows met — the failure is attributable to the mutant, not to the fixture.
- Taxonomy (pinned `classify_row`): pristine 0 → mutant 1 = **verdict-change** (0↔1): a changed substantive verdict, not a names/reason-only failure and not a same-exit diagnostic difference.

## Residual / limits
- Bounded sample, 2 cells per tool, exactly the operator's declared `expect_rows`; no unexpected rows. `expect_rows` was used as an attribution envelope, not a promise; both rows happened to kill. This is kill evidence for those two cells at this pin only — no global-equivalence claim about PM05, and no claim about the other 45 cells (not run).
- In the mutant run `twin_equal` is **true** on both rows (both cells fail identically): the kill rests on the per-row graded miss, not on a twin mismatch, so no twin-mismatch credit is claimed.
- Manifest bytes read-only and unchanged (`d86b7bea…`); `population_sha256` `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (size 47) identical in all three runs; production auditor/grid/mutator/manifest hashes unchanged; the mutant lives only in my scratch and out dir. No tool installs were needed (git 2.56.0, Python 3.14.8, pre-existing). PM08 untouched.
- Raw evidence (all under `.ufo/waves/round-24/postfix/out/FinalPM05/`): `probe-record.json`, `restore-record.json`, `grid-pristine.json`, `grid-mutated.json`, `grid-restored.json`, `pm05-mutant.diff`, `mutant-report-landing-audit.py`, `probe.py`, `restore.py`.
