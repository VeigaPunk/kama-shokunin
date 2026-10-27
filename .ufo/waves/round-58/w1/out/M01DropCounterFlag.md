# M01DropCounterFlag — round-58 C1 mutation probe: delete the `--counter in argv` requirement

Seat M01DropCounterFlag (leaf, advisory), 2026-10-27.
Attacked: C1 frozen predicate (accept genuine+3/3 benign, reject 11/11 no-op, errors=0) and
specifically whether the frozen counter `tools/round58-c1-counter.py` guards the checker clause
that requires every expected roster label's `run` frame to issue at least one subprocess
invocation carrying `--counter`.

## Mutant
Target: committed build-tip bytes of `tools/round58-battery-exec-check.py` at e4891d8a4c9c70e97124980c2ec9aee5762a7f0a
(blob sha256 89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5; lane working tree identical).
Smallest behavior-bearing point, one line in `main()` (full diff: receipts/mutant.diff):

```diff
-    ran = {f["label"] for f in frames if f["fn"] == "run" and f["counter"] >= 1}
+    ran = {f["label"] for f in frames if f["fn"] == "run"}
```

Worked on scratch copies only under /fast/scratch/hyaku/kama-r58/M01DropCounterFlag; the lane
tree was never modified.

## Detector
Frozen counter bytes at dcd69473dd7e33b316e2ba238a48e5119a6cd809, extracted with
`git show dcd69473…:tools/round58-c1-counter.py` (sha256 32f615d8805747dfd615f852f9c65bc557861d1faae648e2c4c7b9749cb411b9):
```
python3 counter-frozen.py --repo <lane> --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a \
  --checker <copy> --work <scratch-under-TMPDIR>
```
Expected: if the clause is load-bearing, an N variant flips reject→accept and the counter exits 1
(met=False); if the counter still passes, the clause is unguarded (survivor = coverage LIMIT).

## Outputs (verbatim counter text in receipts/)
1. Baseline (pristine copy): `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0.
2. Mutant: `genuine=1/1 benign=3/3 noop_rejected=10/11 errors=0 met=False`, exit 1.
   Sole flip: `detail: N06-run-body-noop accept exit=0` (every other row unchanged).
3. Restored pristine bytes, rerun: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0.
Baseline passed, so the mutant verdict is conclusive (not inconclusive).

## Verdict
KILLED. The frozen C1 counter does guard the `--counter in argv` clause: deleting it lets
N06-run-body-noop pass — its `run` frames still carry the roster labels but their bodies no
longer issue a `--counter` subprocess, so the label set is satisfied by empty frames —
flipping noop_rejected 11/11 → 10/11, met True → False, counter exit 0 → 1. The mutation lands
inside enumerated variant N06's behaviour, so it opens no new survivor class; no LIMIT finding
from this probe.

## Restoration evidence
- checker-pristine.py  89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5
- checker-restored.py  89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5 (identical)
- lane tools/round58-battery-exec-check.py 89ad4e5d… (unchanged; lane read-only throughout)
- mutant f0eb54273ba3c6b983105c96a970518489a1f848c6ee2f92eb1bce3fc99d3a4d existed only in scratch
Receipts: .ufo/waves/round-58/w1/out/M01DropCounterFlag/receipts/
  {mutant.diff, out-baseline-pristine.txt, out-mutant.txt, out-restored.txt, sha256.txt}
