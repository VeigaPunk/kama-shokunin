# X07RealBatteryInHarness — real battery legs vs harness-recorded legs (round 58, kama)

Attacks: C1-r58 operability 8->8 (`freeze.txt`, rev dcd69473), the harness
`tools/round58-battery-exec-check.py` and the accepted benign set `tests/round58-battery-variants/B1..B3`
at build tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a.

## Method (sandbox, writes nowhere shared)
- `git -C <lane> archive e4891d8a... | tar -x -C $S/lane` (`$S=/fast/scratch/hyaku/kama-r58/X07RealBatteryInHarness`), exit 0.
  Tip blob == sandbox copy (sha256) for battery `69b77a6a…`, env-leg-test `31b7ea65…`, r54 `c81fe971…`,
  r56 counter `fc3d4b63…`, checker `89ad4e5d…`.
- The battery hardcodes `LANE`/`OUT`/`main()`'s scratch path; the sandbox copy differs from the tip blob only on
  those 3 constants (3 deleted + 3 added lines, `patched.diff`); body byte-identical otherwise.
- Real run: `TMPDIR=$S python3 $S/lane/tools/round56-env-leg-battery.py` -> exit 0, 5 printed lines:
  `comparator-selftest … pass`; `base-old-counter: ld_audit=missed exit=0 -> pass`;
  `round56-counter: ld_audit=detected exit=0 -> pass`; `m-drop-ldaudit: ld_audit=missed exit=0 -> pass`;
  `m-drop-ldaudit-positive-target: ld_audit=missed exit=1 -> killed`.
  Receipts landed only in `$S/out/measured`; after `pid=N` normalisation they are byte-identical to the tip's
  committed `.ufo/waves/round-56/measured/*.out` (base/build/m-drop-ldaudit/m-drop-ldaudit-target-fails/comparator).
- Harness record: `python3 …/round58-battery-exec-check.py --repo <lane> --tip e4891d8 --harness <tip blob>
  --harness-out frames.json` -> exit 0; frames `[run base-old-counter sub=1 counter=1] [run round56-counter 1/1]
  [run m-drop-ldaudit 1/1] [assert_mutant_breaks_detection label=None sub=1 counter=1]`, error=None.
- Checker verdict at tip: `present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`, exit 0.
- Lane untouched by this seat: `git status --porcelain` before/after differ only
  `.ufo/waves/round-58/w1.ready.partial -> w1.ready.dispatched` (L1 orchestration).

## Result: recorded legs equal real legs at frame/label granularity
- Harness run labels `[base-old-counter, round56-counter, m-drop-ldaudit]` are exactly the real printed run-leg
  labels, in the same order, each sub=1 and `--counter`=1 (real side: one subprocess per leg, one receipt per leg).
- Same equality measured for all three behaviour-preserving rewrites run for real in the sandbox: B1/B2/B3 each
  exit 0, print the same 5 lines (missed/detected/missed/exit=1), and their harness frames are identical
  (3 run labels + 1 assert frame, error=None). B2's `_leg` wrapper still produces the `run` frame the profiler sees.
- Real outcomes (`pass, pass, pass, pass, killed`) agree with the ROSTER `expected` field of each leg.

## Limits found (reported, no predicate change)
1. Not line-for-line: the harness records 4 frames against 5 printed lines. `comparator-selftest` is outside
   `WATCHED` and never recorded; the assert leg prints `m-drop-ldaudit-positive-target` but is recorded with
   `label=None` (first parameter is a `pathlib.Path`; the profiler stores only `str` labels). The verdict requires
   only `sub>=1` for that frame, never its `--counter` (measured 1), so renaming that printed line is invisible.
2. Harness-mode child stdout is not battery evidence: because `fake_run` returns `ld_audit=detected` for every
   invocation, the harness-mode run prints `base-old-counter … -> fail` and `m-drop-ldaudit … -> SURVIVED`.
   The parent reads only the frames JSON (`p.stdout` unused). Only the sandboxed real run supplies outcomes.
3. `ran` is a set of labels, so repeated invocations of one roster label collapse in the recorded `legs=N/M`
   count; harmless here (expected labels are distinct), but invocation multiplicity is not part of the record.
4. Shared-surface observation: the unpatched genuine battery writes `.ufo/waves/round-56/measured/*.out` inside
   the lane. Those 5 files are `M` in the lane working tree, mtime 16:51:52, pid-only diff — a non-sandboxed run
   by another actor preceded this seat; my runs wrote only `$S`.

## Evidence
All in `.ufo/waves/round-58/w1/out/X07RealBatteryInHarness/`: `real-battery.out`, `real-B*.out`,
`harness-frames*.json`, `harness-mode.out`, `checker.out`, `checker.stdout`, `patched.diff`, `hashes-and-diff.txt`,
`leg-comparison.txt`, `lane-status-{before,after}.txt`, `commands.txt`. Tool installs: none. Scratch root removed.
