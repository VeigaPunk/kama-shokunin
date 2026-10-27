# X08ExitReceipts — do round-56 battery receipts record an exit code and the exact outcome field?

Seat: `X08ExitReceipts` (round 56, kama, wave 1). Axes: operability, calibration.
Verdict: **five of six receipts carry both the exit code and their exact outcome field; the
C2 freeze receipt `measured/build-c2.out` carries the outcome field but no exit code.** The
defect is a receipt-completeness defect against the C2 target text ("exit 0"), not a
falsification of C2: the roster predicate is fully determined by the bytes present, and
`exit=0` follows from `met=True` plus the producer's `return 0 if met else 1`. One minimal
producer patch closes it; validated on a scratch fixture at three tips, including the
matching red control shape.

## 1. Receipt census (frozen bytes, hashed)

| # | receipt | class | exit field | outcome field | status |
|---|---------|-------|-----------|---------------|--------|
| 1 | `controls/base-c1.out` | C1 red control | `exit=0` | `ld_audit=missed` | PASS |
| 2 | `controls/base-c2.out` | C2 red control | `exit=1` | `met=False` (+`present=0 roster_match=0 kills=0 controls=0`) | PASS |
| 3 | `measured/base-c1.out` | C1 control | `exit=0` | `ld_audit=missed` | PASS |
| 4 | `measured/build-c1.out` | C1 positive control | `exit=0` | `ld_audit=detected`, `problems=['env: server environment carries LD_AUDIT']` | PASS |
| 5 | **`measured/build-c2.out`** | C2 freeze measurement | **ABSENT** | `met=True` (+`present=1 roster_match=1 kills=1 controls=2`) | **FAIL** |
| 6 | `measured/m-drop-ldaudit.out` | C1 kill mutant | `exit=0` | `ld_audit=missed` | PASS |

Receipt sha256 (measured from the lane, 2026-10-27):

```
48a6f7457a8d015ed52c0a1f9877fa8548d393b8f87f442f7d4c08687eabacec  controls/base-c1.out
13d5516a3b391ef1175b975c0ffa5fa3adc235c1ddc8565252f62bb0ecb9d9fc  controls/base-c2.out
ece98c2fd69fdd7dab5cc0f05025cf69fc487d589db7120e2c1b6615816a00e8  measured/base-c1.out
1aea0d276711e33190962338192054db3f221a8ae8f42a53217dec578c124991  measured/build-c1.out
01d95f526ed731b1fe0c4fd3aa72457d27662d261736d31d8e3eb88f1dd9ae1c  measured/build-c2.out
93813bd7b61d95c3ff631fb5da073f3f25ce9980678ef1c3cadc6b146e9241c7  measured/m-drop-ldaudit.out
```

Every C1 receipt's recorded exit also agrees with its outcome under the test driver's own
rule (`tools/round56-env-leg-test.py`: `return 0 if result == a.expect else 1`) and with the
roster expectation for its label, so no exit/outcome contradiction exists anywhere.

## 2. R1 (defect) — the C2 freeze receipt has no exit code

Evidence:

- `od -c measured/build-c2.out` ends `... m e t = T r u e \n` at offset `0000142` (98 bytes,
  two lines). No `exit=` token anywhere in the file.
- `od -c controls/base-c2.out` ends `... m e t = F a l s e \n e x i t = 1 \n` (106 bytes).
  The same round therefore records the red C2 leg's exit but not the green one's.
- Producer root cause, `tools/round56-prereg-check.py` (sha256
  `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`): both write sites emit
  the verdict text only — line 44-45 `if a.out: open(a.out, "w").write(text)` on the
  absent-files path, line 69-71 on the scored path followed by `return 0 if met else 1`. The
  return code is never written into the receipt, so a receipt-only reader cannot recover it.
  `controls/base-c2.out` shows the 7-byte `exit=1\n` was appended out of band, not produced.
- Reproduced on the live surface (not only on the copies): the checker run with
  `--receipts .ufo/waves/round-56` returns red on exactly this file, and the same run over
  byte-identical copies returns the identical verdict (`receipts-check.json` and
  `receipts-check.live.json` are byte-identical).

Impact on the claim: C2's target sentence says "Freeze-tip check: present=1 roster_match=1
kills=1 controls=2 met=True, exit 0". The four roster fields are receipted; `exit 0` is
not. The claim is still decidable — `met=True` plus the producer's return expression pins
the code — but the receipt does not *record* what the claim *cites*, which is precisely the
exit-receipt property this seat audits. It also breaks intra-round symmetry: two receipts
from the same producer class differ in schema.

### Fix (one file, two lines; patch retained)

`producer-exit-field.patch` (in this seat's output directory):

```diff
--- a/tools/round56-prereg-check.py
+++ b/tools/round56-prereg-check.py
@@ -39,7 +39,7 @@
     if preg.returncode or bat.returncode:
-        text = f"tip={tip}\npresent=0 roster_match=0 kills=0 controls=0 met=False\n"
+        text = f"tip={tip}\npresent=0 roster_match=0 kills=0 controls=0 met=False\nexit=1\n"
@@ -63,12 +63,13 @@
     met = match and kills == 1 and controls == 2
+    rc = 0 if met else 1
     text = (f"tip={tip}\npresent=1 roster_match={int(match)} kills={kills} controls={controls} "
-            f"met={met}\n")
+            f"met={met}\nexit={rc}\n")
     print(text, end="")
     if a.out:
         open(a.out, "w").write(text)
-    return 0 if met else 1
+    return rc
```

Validation (scratch git fixture `/fast/scratch/hyaku/kama-r56/X08ExitReceipts/work/fixture`,
`git rev-parse --show-toplevel` asserted on the fixture dir before every commit; patch applied
to a copy, never to the lane):

| tip | content | receipt produced | rc | evidence file |
|-----|---------|------------------|----|----------------|
| `ab8809c0` base | round-56 files absent | `present=0 … met=False` + `exit=1` (106 B) | 1 | `fix-demo/base-c2.exit1.out` |
| `f9c43303` freeze | files present, roster matches | `present=1 … met=True` + `exit=0` (105 B) | 0 | `fix-demo/build-c2.exit0.out` |
| `ba5163e3` roster-flip | files present, `kill`→`control` | `roster_match=0 kills=0 controls=3 met=False` + `exit=1` (106 B) | 1 | `fix-demo/build-c2-mismatch.exit1.out` |

The patched base receipt is tail-identical to the frozen `controls/base-c2.out`
(`diff <(tail -n +2 controls/base-c2.out) <(tail -n +2 fix-demo/base-c2.exit1.out)` →
identical), so the patch reproduces the existing red-receipt discipline exactly. The
roster-flip tip proves `exit` is not hardcoded: a `met=False` outcome with files present
still records `exit=1`. Re-running this seat's checker over a receipt set built with the
patched outputs is green with `exit=0` (`receipts-check.patched.out`).

## 3. R2 (advisory) — outcome-only receipts are not self-identifying

`measured/base-c1.out` (C1 plain control) and `measured/m-drop-ldaudit.out` (C1 kill
mutant) are identical after normalising the pid: `diff <(sed -E 's/pid=[0-9]+/pid=N/' …)`
prints nothing. Neither file contains any counter identity, sha256, label or argv
(`grep -c 'counter\|sha\|label'` → 0 in both). The only attribution is the file name.

Consequence: the kill leg of C1 is receipt-indistinguishable from the plain control leg, so
a swapped pair of receipt files would leave the battery green and be undetectable from
receipt bytes alone. The round's claims are unaffected — the driver (`run()`) labels its own
runs and the preregistration freezes the file names — but the receipts cannot carry their
own provenance. Proposed one-line addition in `tools/round56-env-leg-battery.py`'s `run()`:

```python
body = (f"label={label} counter={pathlib.Path(counter).name} "
        f"sha256={hashlib.sha256(pathlib.Path(counter).read_bytes()).hexdigest()}\n"
        + p.stdout + p.stderr + f"exit={p.returncode}\n")
```

This would also bind each receipt to the frozen counter digest
(`fc3d4b63…444ff6f`), making the C1 kill rule ("measured counter sha256 differs") checkable
from receipts rather than by re-hashing `tools/`.

## 4. R3 (minor) — dead code in both producers

- `tools/round56-prereg-check.py:12` declares `BASE = "e10b6d39…"` and never reads it (the
  base tip arrives via `--tip`). Verified by `grep -n BASE` → declaration only.
- `tools/round56-env-leg-battery.py:27` computes `expected_result = f"ld_audit={expected}"`
  and never uses it (`grep -n expected_result` → single hit).

Neither affects a receipt; both are dead weight in files whose bytes are frozen and hashed,
so removal is a post-round move, not a round-56 edit.

## 5. What this does not establish

- The receipts were not regenerated: no battery or C1 child process was run by this seat, and
  the lane's `measured/` and `controls/` directories were not written. Whether each recorded
  exit code equals the historic child's actual return code can only be asserted from the
  driver source (`subprocess.run(...).returncode` is the only writer of the field), not from
  a re-execution. That is the bound of a receipt-parsing audit.
- Receipts are hashed as found; if a receipt were hand-edited before hashing, this seat would
  see a consistent file. Binding receipts to producer output (R2) is the structural answer.
- C2's predicate is graded here only as "the cited outcome fields exist and are internally
  consistent". Whether the roster match is *correct* is the C2 counter's and the other C2
  seats' work (`R09C2Roster`, `R10C2Counter`, `X02ReplayC2`).

## 6. Reproduction

```
# this seat's checker over the live lane surfaces (read-only)
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 .ufo/waves/round-56/w1/out/X08ExitReceipts/receipts-check.py \
  --receipts .ufo/waves/round-56 --prereg .ufo/waves/round-56/preregistration.json \
  --json <out>/receipts-check.live.json --tsv <out>/receipts.live.tsv --scratch "$TMPDIR"
# → 5 PASS, 1 FAIL (measured/build-c2.out, missing-field:exit), 4/4 selftests PASS, exit 1

# same checker over the frozen byte copies retained by this seat
python3 .../receipts-check.py --receipts .../X08ExitReceipts/receipts \
  --prereg .../X08ExitReceipts/receipts/preregistration.json ...   # → identical verdict, exit 1

# same checker over the patched-producer receipt set
python3 .../receipts-check.py --receipts <patched-set> --prereg <patched-set>/preregistration.json ...
# → 6 PASS, 4/4 selftests PASS, exit 0
```

Recorded exits: live run `exit=1`, copies run `exit=1`, patched run `exit=0`. The checker
carries four synthetic self-tests that run on the same invocation, so a green run cannot be
vacuous: no-exit → red, contradiction (`met=True` with `exit=1`) → red, matching
(`met=True` with `exit=0`) → green, wrong outcome (`ld_audit=missed` for the
`expected=detected` label) → red.

## 7. Seat artifacts

All under `.ufo/waves/round-56/w1/out/X08ExitReceipts/` (checksums in `SHA256SUMS.txt`):

`receipts-check.py` (parser + field/consistency rules + self-tests), `receipts-check.out`,
`receipts-check.live.out`, `receipts-check.patched.out`, `receipts-check{,.live,.patched}.json`,
`receipts{,.live,.patched}.tsv`, `producer-exit-field.patch`,
`fix-demo/{base-c2.exit1.out, build-c2.exit0.out, build-c2-mismatch.exit1.out,
unpatched-freeze-no-exit.out}`, `receipts/{controls,measured}/*.out` and
`receipts/preregistration.json` (frozen byte copies, so this audit survives the integration
deletion that already cost round 55 two named receipts).

No lane file, jj state, PATH entry or fleet-root tracked file was written. No tool was
installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r56/X08ExitReceipts/` was removed
before yielding; `TMPDIR` was set to it for every run that wrote temporary files.
