# RVW01C2Attack — attack on the C2 census waiver boundary (kama r71 w1)

Verdict: **HELD** — no sixth shim survives the final landed bytes of
`tools/census-waiver-boundary.py` (sha256 `7c75963300dbb46b…60e`, worktree `M` over
`e2b860c8`). All four of my attack candidates (H1–H4) are killed by named checks.
One open defect remains and it is **not** shim-shaped: canonical exits 1 because
case 7 (landed census) currently fails on lane state — member
`round42-selfdesc-reconcile selftest` fails (`pass=21 fail=1`).

Tool bytes moved during this attack (executor iterating live). Versions graded:
`e76fee89` (21:46, "v1") → interim v2 (pinned shim hashes appear) → `fc988852` →
`9b7d27b3` (final battery) → `7c759633` (confirmation run, stable start→end).
Census bytes never drifted: `44bebd671c0d1211…b245919` (== freeze copy, sha256-verified
before every build). Lane at freeze `b43e71a8`; HEAD during attack `e2b860c8`.

## Method

1. Reproduced the before-state myself: round-70 `counterexamples.py` over the retained
   shim set → the five named shims each `PASS (hole)`, `killed=0`
   (receipt `shim-control-rerun.out`, byte-equal to frozen `measured/before/shim-control-table.out`).
2. Built four sixth-shim candidates from the landed census bytes (one anchored mutation
   each, real 22-member table kept; builder `build_shims.py`, shims `shims/H*.py`):
   - **H1-waiver-covers-pass**: `--waive` naming an evaluated member increments `waived=`.
   - **H2-forged-waived-token**: `waived=<len(argv waive args)>` regardless of consumption.
   - **H3-second-call-silent**: second `main()` with same waive args after a failing run
     prints nothing and exits 0 (silent only on the fail-waiver fixture).
   - **H4-phantom-not-evaluated**: `not_evaluated` also counts unmatched waive args
     (argv-derived counter, not the refusal counter).
3. Pre-verified each variant passes the round-70 boundary control
   (`c2-boundary-control.py`: `pass=15 fail=0` each, receipts `rerun/boundary70-*.out`
   summary in `hole-probes.out`), then graded with the landed tool.
4. Off-label `--census <shim>` runs grade c1–c7 against the shim; on-label `--shims <dir>`
   runs (my shim in the `s5t-hardcoded-total` slot, four honest shims around it) put the
   tool's own survivor accounting on record.

## Step 1 — the five named shims are rejected (canonical, final bytes)

```
$ python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py; echo EXIT=$?
BOUNDARY_CASE 6 held killed=5/5 s4-refusal-as-fail<-refusal_not_evaluated
  s5t-hardcoded-total<-allpass_population_total s6w-waiver-swallows-failure<-waiver_never_covers_fail
  s8r-second-call-silent<-reentrant_call s10d-refusal-branch-deleted<-refusal_marker_recognized
BOUNDARY cases=7 killed=5 survivors=0
EXIT=1        # exit 1 is case 7, see Finding F1 — not the shims
```
Each shim is named with the check that kills it (kill rule satisfied). Under v1 bytes
(21:48) the same canonical run exited **0** with c8 `pass=22 fail=0` (22/22 green).

## Step 2 — sixth-shim results (final bytes `7c759633`)

| candidate | killed by | exact evidence |
|---|---|---|
| H1 | case 4 `waiver_never_covers_pass` | v1-era c4 line; final: `pass-waiver exit=0 waived=<absent>` held |
| H2 | case 4 `fail_no_waived_credit` + case 5 | `waived=<absent>` required on fail-waive; forged token caught |
| H3 | case 4 `fail_waiver_reentrant` | `BOUNDARY_CASE 4 FAIL … second-call exit=0` (off-label H3 run) |
| H4 | case 5 `unknown_waiver_verdict_unchanged` | `BOUNDARY_CASE 5 FAIL … verdict-unchanged` all-pass `not_evaluated=0→1` |

Exact final off-label outputs: `confirm-H3-second-call-silent.out`,
`confirm-H4-phantom-not-evaluated.out`. The hole observables themselves were real and are
pinned verbatim in `hole-probes.out`, e.g. H3 (one module object, two calls):
```
FAILING+waive call#1 (same module obj)   exit=1 HOST_CENSUS pass=1 fail=1 not_evaluated=0 …
FAILING+waive call#2 (same module obj)   exit=0 <no verdict line>
```
and H1/H2 on the all-pass fixture: `exit=0 HOST_CENSUS pass=2 fail=0 not_evaluated=0
waived=1 total=2 …` (a waiver "credited" with zero not-evaluated members).

**Version-skew finding (for the critic/mutation seats):** under v1 bytes `e76fee89`
(21:48–21:52) H3 and H4 held **all seven cases** — the tool's own accounting printed
`BOUNDARY_CASE shim-s5t-hardcoded-total FAIL survives all seven cases` /
`BOUNDARY_SHIM s5t-hardcoded-total SURVIVED check=unnamed failed=none`
(receipts `after-demo-*.out`, `after-H*.out` in S, copied to W while S existed).
The executor's later iterations closed both seams (`fail_waiver_reentrant`,
`unknown_waiver_verdict_unchanged`/`_refusal_verdict_unchanged`). I make no causality
claim — only that both holes were live in the 21:46–21:52 bytes and are dead in the
final bytes.

## Step 3 — specificity against the landed census bytes

- Final canonical: cases 1–6 held on the landed bytes; the five embedded shims are killed
  with correct attribution — no false positive on the census bytes, no shim accepted.
- The landed census accepted on the boundary grammar: verdict line
  `HOST_CENSUS pass=… fail=… not_evaluated=…[ waived=…] total=… tierA_fail=… tierB_fail=…`
  matched by the tool's pinned regex; waived token position (between `not_evaluated=` and
  `total=`, the labrat's flagged hazard) is handled via token dict, not grep.
- Round-70 control on the pristine census copy: `C2_BOUNDARY_CONTROL pass=15 fail=0`.

## Findings by severity

- **F1 (high — blocks the C2 after-state as of attack end):** canonical `EXIT=1`.
  Case 7 (`landed_exit_zero`, `landed_pass_22`, `landed_fail_zero`) fails because a real
  census member fails on current lane state (receipt `final-landed-census.out`):
  ```
  FAIL [A] round42-selfdesc-reconcile selftest: exit=1 tail='SELFDESC_SELFTEST newest=70
    planted_stale=57 ok:closure_ptr=1,mismatches=2 stale_ptr:closure_ptr=0,mismatches=3
    stale_both:closure_ptr=0,mismatches=3 stale_incl:closure_ptr=0,mismatches=3
    no_ptr:closure_ptr=0,mismatches=3 pass=4 fail=1'
  HOST_CENSUS pass=21 fail=1 not_evaluated=0 total=22 tierA_fail=1 tierB_fail=0
  ```
  The same run was 22/22 green at 21:48 (v1 canonical, pre-`e2b860c8`). 93 files under
  `.ufo/waves/round-71` are uncommitted at attack end (mid-flight wave). I did not
  diagnose the round42 selftest internals (out of C2-attack scope); the frozen C2 target
  (`… exit 0`) needs this member green at the report tip. Flagged to the C2 executor.
- **F2 (info):** the v1 boundary (21:46 bytes) genuinely held two sixth-shim survivors
  (H3, H4); both closed by later bytes. Mutation-testing seats can replay
  `shims/H3…`/`shims/H4…` against the pinned five to exercise the new arms.
- **F3 (low, fixed mid-wave):** v1's `real_census_case` ran the census-under-test as the
  "real census" — any `--census` outside `<lane>/tools/` produced a false
  `pass=0 fail=22` failure (my pristine-copy control reproduced it identically). v2+
  `case_landed` always runs the true landed path with `cwd=lane root`. The round-70
  `c2-boundary-control.py` still has the v1 shape if anyone reuses it off-label.
- **F4 (low):** `--shims <dir>` with a swapped file is detected (`BOUNDARY_SHIMS_DRIFT …
  != pinned …`) but grading continues; the swapped slot then dies with `UNNAMED`
  attribution and case 6 fails on `shim:<name>:attributed`. Exit is 1 either way — no
  bypass, just noisy attribution for foreign shims.

## Exact commands (final bytes)

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 tools/round65-host-census.py; echo $?                        # landed_exit=1 (F1)
python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py; echo $?   # 1 (case 7)
python3 tools/census-waiver-boundary.py --census <S>/shims/H3-second-call-silent.py; echo $?  # 1 (case 4)
python3 tools/census-waiver-boundary.py --census <S>/shims/H4-phantom-not-evaluated.py; echo $? # 1 (case 5)
```

## Receipts (all under `.ufo/waves/round-71/w1/RVW01C2Attack/`)

`shim-control-rerun.out` (before-state rerun), `hole-probes.out` (hole observables +
round-70 control summaries), `shims/H1…-H4…py` (attack shims), `build_shims.py`,
`probe_holes.py`, `demo-H3…-shims/`, `demo-H4…-shims/` (on-label survivor-demo dirs),
`final-canonical.out`, `final-landed-census.out`, `final-offlabel-*.out`,
`final-demo-*.out`, `final_battery.sh`, `confirm-canonical.out`, `confirm-H3…out`,
`confirm-H4…out`. Scratch `/fast/scratch/hyaku/kama-r71/RVW01C2Attack/` deleted on exit
per seat spec. No lane file edited; no git mutation; no tool installed (none needed).

## Could not verify

- Whether the round42 member failure resolves once the wave settles (F1 is a point-in-time
  lane-state observation; last probe 22:1X against bytes `7c759633`).
- Any tool bytes landed after `7c759633` — the executor was still iterating; if the bytes
  move again, re-run the four commands above (all receipts are reproducible from W).
