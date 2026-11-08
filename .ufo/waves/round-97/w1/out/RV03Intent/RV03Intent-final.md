# RV03Intent — final output (verbatim from w1-results.json by the L1)

Seat `RV03Intent`, agent `revenger`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "report": "kama-shokunin/.ufo/waves/round-97/w1/RV03Intent.md",
  "receipts": [
    "kama-shokunin/.ufo/waves/round-97/w1/out/RV03Intent/rv03-zerorun17.out",
    "kama-shokunin/.ufo/waves/round-97/w1/out/RV03Intent/rv03-newcells.out",
    "kama-shokunin/.ufo/waves/round-97/w1/out/RV03Intent/rv03-legacy-plus1.out",
    "kama-shokunin/.ufo/waves/round-97/w1/out/RV03Intent/rv03-legacy-plus2.out"
  ],
  "what_round96_enforced": "One sentence: a candidate's verdict is a pure function of its bytes, not of the host clock and not of a constant pass wrapper. 13 cells, each graded at two host loads; W03 = the round-94 timeout-60 wrapper discriminator guarded by w03 >= 1.25x60s (exit 2 rather than claim a nonexistent discriminator); W11 = the MAX_STEPS-vs-constant-6 cell; W12/W13 = disclosed undecidable cells; W10 = file identity (ctime); positive_mismatches separates disclosed cells from hard ones. Its own oracle still carried the false constant (round96:222 `n_tensors > 833_333 -> '-'`), which round-97's rank-aware oracle fixes.",
  "gaming_attempts": [
    "R2 PASSED: `--runs 0 --allow-clock --burners 0` prints the exact frozen string `ROUTER_BUDGET97 cells=17 mismatches=0 positive_mismatches=0 load_cells=17 load_stable=1 ... w03_seconds=0.0 burners=0` and exits 0 with the probe invoked for 1 of 17 cells (W10 only). `all([])` is True and --allow-clock (a documented flag for the round-94 red control) disables the only guard (MARGIN at :633). Inherited: round96:431 `runs = a.runs`, no --runs validation.",
    "R3/R4 PASSED: a probe overcharging +1 step per tensor header passes all 17 cells (4 new, then 13 legacy incl. W11) with `survived=1 ... ok=1` exit 0. Its true nd=1 ceiling is 714,285, not the 833,332 SKILL.md:2453 states. R8 shows +2 flips W11 (`cells_ok=12 survived=0 caught=1`, exit 1) - so the window is exactly +1 step/header and W11 is the overcharge sentinel.",
    "R5 PASSED: `--probe-file` (:607-608, mode=override) lets a 40-line probe with no GGUF parse and no step budget survive the four new cells: `survived=1 ... probe=override ok=1` exit 0. The receipt is bound to the probe only by probe_sha256=, which a reader must recompute.",
    "C1+C3 GREEN ON THAT PROBE (scratch clone commit ef60fd43): `SELF_ASSESS97 checks=14 mismatches=0 met=True` and `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True`, both exit 0. So a false self-assessment still passes: C1's arithmetic checks are substring tests on the probe text (:143,:151) and C3 recomputes from a formula literal (depth:103) against MAX_STEPS only, never against the parser's charges.",
    "R6 honest control: `--cells new --control --expect survived --mutant flat6` -> survived=0 caught=1 exit 1, so control mode does discriminate when the expectation is right.",
    "Refused (fail-safe): skipped cell (unreachable, and the count is printed); oracle mislabel (fixture_class is only consulted by build_fixtures, never for a cell verdict, so it can only cause exit 2); non-applying mutant patch (`mutant flat6: anchor appears 0 times, not exactly once`, exit 2)."
  ],
  "exit_codes": {
    "predicate_met": "0",
    "cell_red_or_mutant_survives": "1",
    "CannotEvaluate (unresolvable rev, W03 margin guard, anchor mismatch, missing probe)": "2",
    "other exception (e.g. PermissionError on --work)": "1 traceback",
    "bad control flags": "64",
    "empty_selected_cell_set": "0 via `survived = int(n_ok == n)` with n=0 - LATENT only: the selection can never be empty (new cells unconditional at :480; legacy forces n_slow=max(8,..) at :467). --control therefore never returns 0 on an empty set or on a fixture build failure.",
    "--runs 0": "0 with no probe graded (R2)"
  },
  "receipts_verdict": "All five probe_sha256 values in the two committed control files recompute exactly from `git show 40763bd2:tools/kama-probe.sh` + the counter's own MUTANTS table (11e5b01b/14efbe6f/2e31ff3b/6b5f6db4/9035b55e), so the 4 legacy survived=1 and 4 mutant caught=1 receipts are authentic byte-for-byte. They do NOT prove: (a) behaviour at M2 - they ran at base 40763bd2, and the base->freeze probe diff is comment-only (my computed diff, not their evidence); (b) cell-specificity - caught=1 means `any cell red`, and undercharge/nopreamble take collateral reds; (c) the predicate itself - at e057166e `.ufo/waves/round-97/measured/c2.out` is byte-identical to `controls/c2-could-not-evaluate.out` (diff: identical) and ends `c2_exit=2`, with no rev=/probe_sha256= field. C2 is unmeasured as committed; amendment 1 (e057166e) records this honestly and touches no tools/ byte, so K1 holds.",
  "count_defect": "The C2 predicate's own sentence carries a false count: 'the three control receipts ... the three new cells' (plans/round-97-claims.md:76-77) vs CELLS=17 (counter:142), four NEW_CELLS (:147) and two control files with 4 and 5 CONTROL blocks. Same 'three' at tools/round97-router-budget.py:13 and SKILL.md:2443; the wave dispatch says a third tally ('16 cells; W14/W15/W16', w1-spec.json/w1-dispatch.json). No counter reads the plan, the counter docstring, the SKILL heading or the dispatch, so all survive a green C1 - round-96's failure class with the grader removed rather than inverted. (Corroborated independently by CR02Wording.md and RV01SelfAssess.md; dedupe at integration.)",
  "findings": [
    "F1 block, calibration: false 'three' in the frozen predicate + counter docstring + SKILL heading + wave dispatch, ungraded",
    "F2 high, operability: --runs 0 + --allow-clock yields the frozen summary and exit 0 with no probe graded",
    "F3 high, operability: --control --expect survived --mutant none accepted; survived=1 needs no forgery",
    "F4 high, operability: --probe-file grades arbitrary bytes; a budget-free probe survives the new cells",
    "F5 high, calibration+depth: +1 step/header overcharge passes all 17 cells and keeps C1 (14/0) and C3 (rows=6, 8/0) green while the 833,332 ceiling is false of it (disclosed as C2 limit (a), but C1/C3 do not inherit the disclosure)",
    "F6 medium, operability: load_cells/cells = len(union), so load_cells=17 prints even when the load pass graded nothing (R2)",
    "F7 medium, calibration: C1 checks 13-14 are substring co-presence against lane-owned, un-pinned round-96 receipts (one commit f6122036 - not exploited)",
    "F8 high, process: measured/c2.out is a copy of the refusal, c2_exit=2, no rev= field; C2 unmeasured",
    "F9 low: no n==0 guard on the control summary (vacuous survived=1, unreachable via CLI)",
    "F10 low: counter docstring states the W03 guard as 1.5x where MARGIN=1.25 (:93 vs :157), copied from round96:58"
  ],
  "tools_installed": "none",
  "scratch": "/fast/scratch/hyaku/kama-r97/RV03Intent removed (clone, probe patches, work dirs); nothing over 50 MB left under /tmp; no pacman, no host service, no process-kill, no tracked-file edit, no mutating git in the lane.",
  "checks_for_main": [
    "python3 tools/round97-self-assessment-audit.py --repo . --rev <M1>",
    "python3 tools/round97-depth-boundary-audit.py --repo . --rev <M3>",
    "python3 tools/round97-router-budget.py --repo . --rev <M2> --work <scratch> --slow-files 72  (amendment 1; expect exit 0, cells=17)"
  ],
  "confidence": {
    "high": "F1..F4, F6, F8, F10; F5's 17-cell survival and +1/+2 window (R3, R4, R8 executed)",
    "medium": "base->M2 transfer of control receipts (comment-only probe diff, computed not receipted); C1/C3 behaviour under forgery classes other than the +1 overcharge",
    "not_claimed": "ctime memo shape, slow /props verdict, pass-level wrapper (disclosed, out of seat scope); no live llama.cpp probe run"
  }
}
```
