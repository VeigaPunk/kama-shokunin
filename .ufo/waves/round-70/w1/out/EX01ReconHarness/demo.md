# demo.md — EX01ReconHarness, round 70 w1, lane kama (calibration C1 harness repair)

Environment: host per freeze.txt (python3 3.14.8, git 2.56.0). `LANE=/home/vgpnk/Projects/shokunin/kama-shokunin`,
base `B=6035e952c2521999e192d6f236331f265ac98392`, scratch `S=/fast/scratch/hyaku/kama-r70/EX01ReconHarness`
(deleted before yield; every run below used `TMPDIR=$S/tmp` so the throwaway checkout never touched /tmp).
Candidate: `.ufo/waves/round-70/w1/out/EX01ReconHarness/round41-scorecard-reconcile.py` (compiled clean:
`PYTHONPYCACHEPREFIX=$S/pycache python3 -m py_compile <candidate>` → `COMPILE_OK`, exit 0).
No tools were installed or upgraded.

## (a) Old bytes reproduce r41=2 at base — and match the committed BEFORE receipt

```
cd $LANE
TMPDIR=$S/tmp python3 tools/round42-selfdesc-reconcile.py --repo $LANE --tip $B \
  --out $S/before/round42-at-base-old.out ; echo "OLD-EXIT=$?"
```
Output (exit 1):
```
tip=6035e952c2521999e192d6f236331f265ac98392
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False
detail: r41 operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)
detail: banner: head lacks 'Latest measured round: 69'
detail: planned: section does not name '### Planned (round 70)'
detail: retired: does not state '15 capabilities'
detail: province: PROVINCE.md lacks tools/round67-worktree-landing-check.py (capability worktree-landing-check)
detail: province: PROVINCE.md lacks tools/round68-receipt-pointer-audit.py (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks registry/receipt-pointer-resolutions.tsv (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks tools/round69-newest-closure-counter.py (capability newest-closure-counter)
detail: closure_ptr: calibration row latest outside closure is round-68; newest at tip is round-69
OLD-EXIT=1
```
Receipt equality: `diff $LANE/.ufo/waves/round-70/measured/before/reconciler-at-base.out $S/before/round42-at-base-old.out`
→ only difference is the receipt's own trailing `EXIT=1` bookkeeping line (`13d12 < EXIT=1`); the 12 measured lines are byte-identical.

## (b) New bytes at base: r41 drops 2→1; every other counter unchanged

```
mkdir -p $S/tools-new && cp $LANE/tools/round42-selfdesc-reconcile.py $S/tools-new/ \
  && cp <OUT>/round41-scorecard-reconcile.py $S/tools-new/
cd $S/tools-new
TMPDIR=$S/tmp python3 round42-selfdesc-reconcile.py --repo $LANE --tip $B \
  --out $S/after/round42-at-base-final.out ; echo "FINAL-EXIT=$?"
diff $S/before/round42-at-base-old.out $S/after/round42-at-base-final.out ; echo "diff-exit=$?"
```
Output (exit 1):
```
tip=6035e952c2521999e192d6f236331f265ac98392
r41=1 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=9 maxN=69 met=False
detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 1)
detail: banner: head lacks 'Latest measured round: 69'
detail: planned: section does not name '### Planned (round 70)'
detail: retired: does not state '15 capabilities'
detail: province: PROVINCE.md lacks tools/round67-worktree-landing-check.py (capability worktree-landing-check)
detail: province: PROVINCE.md lacks tools/round68-receipt-pointer-audit.py (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks registry/receipt-pointer-resolutions.tsv (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks tools/round69-newest-closure-counter.py (capability newest-closure-counter)
detail: closure_ptr: calibration row latest outside closure is round-68; newest at tip is round-69
FINAL-EXIT=1
```
The old-vs-new diff is exactly 3 lines: the verdict line (`r41=2 … mismatches=10` → `r41=1 … mismatches=9`),
removal of the operability gate detail (fact now passes), and the round69 detail changing `(exit 2)` → `(exit 1)`.
banner/planned/retired/saturation/caps/receipts/readme/province/rel/closure_ptr/maxN are byte-identical.

### Why r41=1 at base, not the seat's expected r41=0 — with the 2→0 isolation proof

The remaining mismatch is NOT harness git-dependence. Two measured facts:

1. At base the calibration row is genuinely stale (names round-68; newest is round-69) — the same truth the
   independent `closure_ptr=0` verdict records. Run in a real checkout (see (d)) the command now executes and
   honestly exits 1 with `row_current=false` + `STALE_CALIBRATION`; its stdout can never contain the cited line.
2. Even with a current row, the cited output `NEWEST_CLOSURE … row_current=true` (U+2026 ellipsis, exact bytes in
   the `## Axes` calibration cell at base and HEAD) can never equal the counter's full line
   `NEWEST_CLOSURE newest=corpus/lessons/round-N-verifier-spotcheck.md date=YYYY-MM-DD round=N row_names=… row_current=true`
   (`run_fact` requires a stripped stdout line == citation). This citation defect is invisible in the old
   harness only because the git-less export made the command die at exit 2 first.

Isolation fixture (tree = base + pointer/incl planted to round-69 + citation re-anchored to the exact counter
line; built in my own scratch fixture `fx.r41`, commits with throwaway identity inside the fixture only,
toplevel asserted; fixture tip `1c6ab96f7571cd14b57faac36b30d247a377d128`):
counter at that tip: exit 0, prints
`NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69 row_names=corpus/lessons/round-69-verifier-spotcheck.md row_current=true`.
Then, `python3 <round41> --repo $S/fx.r41 --tip 1c6ab96f…`:

Old bytes (exit 1):
```
tip=1c6ab96f7571cd14b57faac36b30d247a377d128
axes=6 facts=44 hash_bad=0 lines_bad=0 run_bad=2 dead=0 score_bad=0 hollow=0 mismatches=2 met=False
detail: operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
detail: calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69 row_names=corpus/lessons/round-69-verifier-spotcheck.md row_current=true' (exit 2)
```
New bytes (exit 0):
```
tip=1c6ab96f7571cd14b57faac36b30d247a377d128
axes=6 facts=44 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True
```
Identical content, only the execution environment changed: run_bad 2→0, met False→True. The harness repair is
complete; reaching r41=0 at base additionally needs the L1's content re-anchoring (see report.md §L1 actions).

## (c) round42 selftest arms (imported counter)

Old bytes: `TMPDIR=$S/tmp python3 $LANE/tools/round42-selfdesc-reconcile.py --selftest --repo $LANE --tip $B --work $S/work-old`
```
SELFDESC_SELFTEST newest=69 planted_stale=57 ok:closure_ptr=1,mismatches=9 stale_ptr:closure_ptr=0,mismatches=10 stale_both:closure_ptr=0,mismatches=10 stale_incl:closure_ptr=0,mismatches=10 no_ptr:closure_ptr=0,mismatches=10 pass=4 fail=1
```
New bytes: same command via `$S/tools-new`, `--work $S/work-new3`
```
SELFDESC_SELFTEST newest=69 planted_stale=57 ok:closure_ptr=1,mismatches=8 stale_ptr:closure_ptr=0,mismatches=9 stale_both:closure_ptr=0,mismatches=9 stale_incl:closure_ptr=0,mismatches=9 no_ptr:closure_ptr=0,mismatches=9 pass=4 fail=1
```
Reading: at the base/HEAD tip both are red exactly because the `ok` arm requires r41 contribution 0 and the ok
arm still carries the loose `NEWEST_CLOSURE …` citation mismatch (old bytes carried that PLUS the two
git-less failures: ok 9 = 7 content + 2 run; new bytes: ok 8 = 7 content + 1 citation). The freeze's
`pass=5 fail=0` target is defined at the round-70 landing tip; it becomes reachable only after the L1
re-anchors the citation (then ok arm = 0, planted arms = 1 each). The planted-variant invariant
("each planted variant exactly one mismatch above ok") holds in every measured run: old ok=9 with planted
10/10/10/10; new ok=8 with planted 9/9/9/9. The gate's own fixture arms (hermetic 1–5, stale-index 7) pass inside the
checkout: see `GATE_SELFTEST pass=7 fail=0` in (d).

## (d) Git-dependent and git-independent facts reproduce

Probe checkout built with the same primitive the new harness uses, plus a reference archive export:
```
git clone --shared --no-checkout --quiet $LANE $S/probe && git -C $S/probe checkout --detach --quiet $B
mkdir -p $S/archive-export && git -C $LANE archive --format=tar $B | tar -x -C $S/archive-export
diff -r --exclude=.git $S/archive-export $S/probe && echo TREES-IDENTICAL   # → TREES-IDENTICAL
git -C $S/probe rev-parse HEAD          # → 6035e952c2521999e192d6f236331f265ac98392 (== tip)
git -C $S/probe status --porcelain      # → empty
```
Git-dependent fact 1 (operability `python3 tools/gate-registry-check.py --selftest`):
```
cd $S/probe           && python3 tools/gate-registry-check.py --selftest   # … PASS lane-tip 0e14facd0c61: exit=0 line='registered 79 unregistered 0 defective 0' … GATE_SELFTEST pass=7 fail=0   → exit 0
cd $S/archive-export  && python3 tools/gate-registry-check.py --selftest   # … FAIL lane-tip: cannot resolve master: fatal: not a git repository … GATE_SELFTEST pass=6 fail=1                 → exit 1
```
Cited truth `GATE_SELFTEST pass=7 fail=0` reproduces in the checkout; fails only in the git-less export.

Git-dependent fact 2 (calibration `python3 tools/round69-newest-closure-counter.py --since-round 63`):
```
cd $S/probe          ; python3 tools/round69-newest-closure-counter.py --since-round 63   # SCOPE population=rounds>=63 members=7 / NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69 row_names=corpus/lessons/round-68-verifier-spotcheck.md row_current=false / STALE_CALIBRATION row_names=… newest=… newest_date=2026-11-01 → exit 1
cd $S/archive-export ; python3 tools/round69-newest-closure-counter.py --since-round 63   # COULD_NOT_EVALUATE git ls-tree --name-only failed (rc=128): fatal: not a git repository … → exit 2
```
The command now executes against the tip and its honest verdict (stale row) agrees with the independent
`closure_ptr=0` detail; in the export it could not evaluate at all.

Git-independent fact (`grep -c '^## ' SKILL.md`, depth row): `48` in the checkout and `48` in the export —
identical. All other RUN facts are covered by (b): every counter other than r41 byte-identical.

## (e) diff.patch verification

```
git -C $S/fx.verify apply --check <OUT>/diff.patch   # exit 0
git -C $S/fx.verify apply <OUT>/diff.patch           # exit 0
cmp $S/fx.verify/tools/round41-scorecard-reconcile.py <OUT>/round41-scorecard-reconcile.py   # identical
```
Patch is a plain unified diff of base-bytes vs candidate with `a/tools/… b/tools/…` paths (55 lines), applies
with `git apply -p1` at a repo root, result byte-identical to the candidate.

## (f) Cleanup proof

After all runs: `ls -A $S/tmp | grep -c r41c1` → `0`; `ls -A /tmp | grep -c r41c1` → `0`. The atexit hook
removed every throwaway checkout; TMPDIR was honored everywhere.

## (g) Observation: lane working tree already carries candidate + one addendum hunk

During measurement, `$LANE/tools/round41-scorecard-reconcile.py` was modified in the working tree = my exact
candidate bytes plus one appended line after the mirror loop:
`git(export, "update-ref", "refs/heads/master", tip)` (pins the checkout's master at the measured tip).
Measured (read-only, from a copy): base run output byte-identical to (b) (`diff` clean → BASE-OUTPUT-IDENTICAL-TO-CANDIDATE)
and selftest identical (`ok:…mismatches=8 … pass=4 fail=1`). Behavior-neutral on every measured path.
