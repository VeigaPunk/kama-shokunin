# X03ReplayC2 — Round 58 C2 (calibration) replay at base / freeze / build

Seat: leaf replay. Lane tree read-only; nothing in production edited. Scratch `S=/fast/scratch/hyaku/kama-r58/X03ReplayC2`, TMPDIR forced to `$S`, one shared clone `$S/lane` (`git rev-parse --show-toplevel` = `$S/lane`), all runs against committed bytes via `git show`.

Counter under test: `tools/round58-c2-counter.py` blob `99798397bd7de0477b07a89ec675ee97994a8814` at both freeze `dcd6947` and build `e4891d8` (byte-identical, sha256 `61ef1f565706db459b55e3224a0fbedcacf944a080b0a2c31c22ce3b3fcaaeee`); extracted from the freeze commit, never the working tree. Fleet MANIFEST pinned at `941acf70583a2b3a1d33460b31967e0efd291f3e`.

Command form (identical for each rev):
`python3 c2-counter-frozen.py --repo $S/lane --tip <rev> --manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e`

## 1. Base 2f53614e6f5895560edb775cc3e74841aa0dd44c — exit 1
```
tip=2f53614e6f5895560edb775cc3e74841aa0dd44c
predicate=C2-r58 r42 mismatches=0 and closure pointer mismatches=0
claim=N=56 token=admitted maxN=57 manifest=rejected-honest-stop
r42=1 missing=0 stale=1 verdict=1 including=1 mismatches=4 met=False
```
**Base mismatches=4 CONFIRMED**, with exactly the frozen decomposition r42=1 stale=1 verdict=1 including=1 and met=False. Independent detail from `tools/round42-selfdesc-reconcile.py` at base: `r41=1 ... mismatches=1 maxN=57 met=False`, `detail: r41 calibration run ... no stdout line == '43' (exit 0)` — the base row's blob-count literal `43` while the base tree already holds **44** `corpus/lessons/round-{N}-verifier-spotcheck.md` blobs (`git ls-tree ... | grep -c` = 44 at base). So at base the pointer was stale by one round (row says round 56/`admitted`, tree max N=57, MANIFEST 56=`rejected-honest-stop`) *and* the count literal was stale. Determinism: base rerun byte-identical. Attacks: SCORECARD calibration row + r42 counter at base.

## 2. Freeze dcd69473dd7e33b316e2ba238a48e5119a6cd809 — exit 1
```
tip=dcd69473dd7e33b316e2ba238a48e5119a6cd809
predicate=C2-r58 r42 mismatches=0 and closure pointer mismatches=0
claim=N=56 token=admitted maxN=57 manifest=rejected-honest-stop
r42=1 missing=0 stale=1 verdict=1 including=1 mismatches=4 met=False
```
Byte-identical to the committed receipt `.ufo/waves/round-58/controls/c2-base.out` (same tip, same 4 counters), so my replay reproduces the frozen "before" state and the control receipt. Base and freeze agree because `git diff --stat 2f53614 dcd6947 -- SCORECARD.md corpus/lessons/` is empty (freeze only adds round-58 tools/variants/controls; no M on SCORECARD).

## 3. Build e4891d8a4c9c70e97124980c2ec9aee5762a7f0a — exit 0
```
tip=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a
predicate=C2-r58 r42 mismatches=0 and closure pointer mismatches=0
claim=N=57 token=rejected-honest-stop maxN=57 manifest=rejected-honest-stop
r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True
```
Row at build: ``latest outside closure `corpus/lessons/round-57-verifier-spotcheck.md` (rejected-honest-stop)``, `including round 57`, count literal `44` (= actual 44), pin text `--manifest-rev 941acf70...` matches the frozen pin. `tools/round42-selfdesc-reconcile.py` at build: `r41=0 ... mismatches=0 maxN=57 met=True`. Rerun and `--no-r42` run both give mismatches=0 / met=True / exit 0, so the r42 arm and the four pointer arms are independently zero, not one arm masking another.

## Probes (fail-closed / operability)
- invalid tip `deadbeef` → `could-not-evaluate: invalid tip`, exit 2 (not a pass).
- nonexistent manifest rev → `could-not-evaluate: missing SCORECARD, lessons tree or MANIFEST blob`, exit 2.
- current lane HEAD `e4f207f544315612a6ea55b5b7a1cc2d2d4b4a79` → mismatches=0 met=True exit 0 (deliberately not a scored tip; shows integration so far added no round-58 spotcheck, so maxN is still 57).

## Limits (reported, not scored)
- C2 does not check the row's numeric blob-count literal (`44`) or the `outside closures on record` figure; only maxN, `including round N` and the token. At base the literal was wrong-by-one and only r42's r41 arm caught it — C2 alone would have been blind to a right-N/right-token row with a wrong count.
- The verdict token is validated only against fleet `MANIFEST.json` at the pinned rev (outside this tree); if that ledger row is edited without a pin bump, C2 silently follows it.
- The moment a round-58 spotcheck blob lands, maxN→58 and C2 flips stale until the L1's planned row/section edit; that is expected sequencing, not a defect.

Receipts: `X03ReplayC2/c2-base.out`, `X03ReplayC2/c2-freeze.out`, `X03ReplayC2/c2-build.out` beside this file. No tools installed; no repo mutations.
