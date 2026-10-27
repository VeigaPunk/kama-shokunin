# M02DropAssertClause — round-58 mutation probe: `assert_ok` forced true

Attacks: C1 frozen kill rule via variant `N07-mutant-assert-noop` and checker gate
`tools/round58-battery-exec-check.py` line 206
(`assert_ok = (not defines_assert) or (bool(asserts) and all(f["sub"] >= 1 for f in asserts))`).
Plausible defect: checker stops binding `assert_mutant_breaks_detection` to executed work;
a battery whose mutant-assert is a stub (`return True` before any subprocess, exactly N07)
would then pass. Question: does the frozen counter kill it?

## Setup
- Frozen bytes: counter + variants at dcd69473dd7e33b316e2ba238a48e5119a6cd809
  (`sha256(frozen-c1-counter.py)=32f615d8805747dfd615f852f9c65bc557861d1faae648e2c4c7b9749cb411b9`);
  checker under test from build tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a
  (`sha256(pristine)=89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`).
- Mutation (scratch only): line 206 replaced by
  `assert_ok = True  # MUTANT M02DropAssertClause: ignore assert_mutant_breaks_detection execution`
  (`sha256(mutant)=533a8c172d8073f648161d37eb66fdbbe45e5e24026c2b9b07a5eb1f9a537dad`).
- Detector (same command all three legs, exit code recorded):
  `python3 frozen-c1-counter.py --repo <lane> --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker <file> --work $S/tmp`

## Runs (full outputs in receipts)
1. Pristine: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0. Baseline passes.
2. Mutant: `N07-mutant-assert-noop accept exit=0` (was `reject exit=1`);
   `genuine=1/1 benign=3/3 noop_rejected=10/11 errors=0 met=False`, exit 1.
3. Restored (pristine bytes recopied over the scratch mutant path):
   `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0.

## Verdict: KILLED
The frozen counter detects the defect exactly through the enumerated variant the ticket
named: N07 flips to accepted, the noop tally drops to 10/11, kill rule fires (exit 1).
No survivor, no LIMIT. The genuine battery and the 3 benign rewrites stayed accepted and
the other 10 no-ops stayed rejected — the assert-execution gate is the sole detector for
this defect class, and it is load-bearing.

## Restoration evidence
- `sha256` after restore = `89ad4e5d…83eec5` = pristine hash (both scratch copies).
- Mutant bytes preserved pre-restore as `mutant-checker.py.asm-receipt`, rebuilt and
  hash-verified `533a8c17…37dad` (identical to the scored mutant).
- Lane tree untouched: `git status --porcelain` on checker, counter, variants and controls
  dirs is empty; mutation never left my scratch
  `/fast/scratch/hyaku/kama-r58/M02DropAssertClause` (removed at cleanup).

## Receipts (relative to kama-shokunin)
- .ufo/waves/round-58/w1/out/M02DropAssertClause/c1-pristine.out
- .ufo/waves/round-58/w1/out/M02DropAssertClause/c1-mutant.out
- .ufo/waves/round-58/w1/out/M02DropAssertClause/c1-restored.out
- .ufo/waves/round-58/w1/out/M02DropAssertClause/mutant-checker.py.asm-receipt
