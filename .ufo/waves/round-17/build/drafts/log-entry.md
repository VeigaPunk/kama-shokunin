## round 17 — calibration gate and live-harness fail-capability (2026-10-20)

- Start `[L1 fills]`. Observed read-only at drafting: `master` =
  `cff9e62f05aa7cfb9059444f62eb787100719713`; tree not clean, with
  ` M .gitignore`, ` M AGENTS.md` and `?? .ufo/waves/round-17/` present
  before this seat wrote anything. Assignment operability + calibration;
  calibration 7 is lowest (operability `[L1 fills]`). Declared claims C1 and
  C2 are causally separable; the SOURCES, routed-defect and jj items are
  process, not claims.
- Motivating evidence, C1 calibration. `tests/probe-verdicts/check.py` is
  documented as grading verdict, reason, exit and drift; the pass expression
  is at lines 340-347. Round-16 mutation
  (`.ufo/waves/round-16/falsify/advice/MutateHarness.md`): 5 of 5
  grading-weakening mutants survived the pair detector (frozen 55/17 versus
  current 72/0) — ignore-reason, ignore-exit, ignore-drift, casefold-verdict,
  timeout-pass. The timeout path was not exercised. `served_model` is never
  graded and no route-match assertion exists. Malformed output: `row.get` at
  lines 337-338 sits outside the `try` at 329-336, so a non-object `rows[0]`
  is [INFERENCE] an uncaught exception, not a recorded row failure; not run.
- Motivating evidence, C2 operability. `tools/kama-llamacpp-live.py` (1078
  lines) grades `health_ready` on status only (lines 938-939): a 200
  `{"status":"degraded"}` body passed 10/10, gate VALID. `teardown_exited`
  (1024-1028) passes on any returncode: a self-exit rc 0 with
  `sigterm_sent false` passed. `teardown_port_closed` (1029-1032) is vacuous
  on failed runs. `loading_envelope_exact` is computed at line 922 and no
  check reads it: a 503 body with message "Busy" and string code "503" gave
  exit 0, 10/10, gate VALID. A teardown exception (1020-1021 stores an error,
  then 1026 indexes `returncode`) escaped with `receipt_written False`.
  Source: `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md`,
  reviewed at harness sha `b8c5e8d4…`; line numbers re-checked this session.
- Mined mistake, SOURCES S041: the own-work row (`corpus/SOURCES.md:53`)
  had its anchor and teaches cells amended after first commit `b8e485c`
  (`corpus/lessons/round-16-verifier-spotcheck.md:184`, routed defect 3).
  Contract rule 2 allows only `status`, `recheck` and `used-by` to change in
  place. Unknown: the contract text itself is not in the lane
  (`corpus/SOURCES.md:3` names `SOURCES-CONTRACT-v1` only). Fix path is a
  fail-capable `tools/sources-append-only.py`; `[L1 fills]` once landed.
  `corpus/lessons/round-16.md:147` words the same amendment as "before
  closure"; both accounts agree the first commit was `b8e485c`.
- Round-16 routed defects carried (`corpus/lessons/round-16-verifier-spotcheck.md`
  §Routed defects 1-6, lines 182-187): wave provenance, falsify summary
  accuracy, append-only SOURCES, wording precision, install disclosure, and
  carried harness debt (defect 6, lines 187). Status per defect: `[L1 fills]`.
- jj-migration risks (`.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md`):
  R1 round-13 live gate exits 1 `documentation_mismatch` when the worktree
  QUALITY.md differs from HEAD (line 154). R2 unborn HEAD gives exit 128 at
  the round-12 selftest and round-13 live (line 156). R3 `jj commit` on
  untracked paths with `snapshot.auto-track="none()"` exits 0 with an empty
  commit (lines 66-78). Ignore rules, checked against committed bytes:
  `master:.gitignore` contains only `.ufo/interactive-sessions/`, so
  `.ufo/state/` is not ignored in committed history; the ignore line exists
  only as an uncommitted worktree edit (` M .gitignore`). `registry/history/.lock`
  is ignored by committed `registry/history/.gitignore` line 3 (`.lock`); that
  risk is not present.
- Measured numbers, all `[L1 fills]`: C1 surviving mutants before (frozen
  check.py plus round-16 pair) and after (current check.py, pair, fault
  controls); fault-control results; matrix set digest `bf9068d8…` and the
  72/17 breadth unchanged; C2 accepted-bad controls before and after; live
  receipt `kama-llamacpp-live/v2` result and exit; gate result. Installs
  this round: `[L1 fills]` (this entry's author installed nothing).
