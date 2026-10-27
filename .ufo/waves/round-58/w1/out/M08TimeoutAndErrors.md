# M08TimeoutAndErrors — round 58 probe

Axes: operability (timeout behavior); calibration (counter's `errors=0`). Target: C1 frozen claim, `tools/round58-battery-exec-check.py` timeout and harness-failure return behavior, scored by `tools/round58-c1-counter.py` at build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`.

Mutant: scratch copy changed `TIMEOUT = 60` to `TIMEOUT = 0`, and changed the `p.returncode or not os.path.exists(res)` harness-failure branch's exit from 2 to 1. No source-tree bytes edited. This attacks whether the counter classifies failed harness runs as evaluation errors (instead of merely counting error verdicts).

Expected detector: `errors=0` should fail when the checker cannot evaluate due to harness failures; a timeout value of zero should make the bounded child execution fail promptly.

Commands/results (all with `TMPDIR=/fast/scratch/hyaku/kama-r58/M08TimeoutAndErrors`, Python bytecode disabled):
- Pristine checker SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`; counter against build-tip repo: exit 0; `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`.
- Mutated checker SHA-256 `ae0ae8755ca3d4a1056d54b3f15f123cd8a5dc606ad6a5d69479d943b657648a`; same counter invocation: exit 1; all 15 records `error exit=2`, `errors=15 met=False`.
- Restored checker SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`; same counter invocation: exit 0; pristine totals restored (`errors=0 met=True`).

Verdict: KILLED. Combined mutant fails the frozen counter predicate and `errors=0` catches the observed failure mode. The counter maps checker exit 2 to `error`; exit 1 remains `reject`, hence harness failures mapped to 1 would not themselves increment errors if they emitted ordinary checker output. Here timeout=0 caused child harness timeout, so observed exit 2 and 15 errors. This probe does not isolate the changed failure-branch return code from the timeout mutation.

Restoration evidence: exact pristine bytes restored and SHA-256 matches pre-mutation; restored counter output matches the pristine passing totals. Scratch removed on exit.
