# C02ClaimSeparability — round 58 cross-claim scan (C1 vs C2)

Question: could C1's landing change C2's counter output, or the reverse, through shared files (SCORECARD.md, tools/)?

Method: scratch commits built with `git read-tree` / `update-index` / `commit-tree` on a `git clone --shared` (toplevel asserted). Parents: base 2f53614e. Each variant = base + listed files from the frozen/tip blobs:
- base: 2f53614e
- c1only: + tools/round58-battery-exec-check.py, tools/round58-c1-counter.py, tests/round58-battery-variants/
- c2only: + SCORECARD.md (tip version)
- both: c1only + c2only (= 1be0db77)
- bv / c2v: base or c2only + tests/round58-battery-variants/ only (so the r57 checker can read its fixtures)

Counters: frozen `tools/round58-c1-counter.py` and `tools/round58-c2-counter.py` at dcd69473, run from outside the tip with `--repo` (receipts in receipts/).

| commit | C1 counter (exec checker) | C1 counter (r57 checker) | C2 counter (--manifest-rev 941acf70) |
|---|---|---|---|
| base 87f25b54 | not run as-is (no variants) | — | exit 1: r42=1 stale=1 verdict=1 including=1 mismatches=4 met=False |
| c1only c9ef0ded | exit 0: genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True | — | exit 1: r42=1 stale=1 verdict=1 including=1 mismatches=4 met=False |
| c2only 8d101b67 | — | exit 1 genuine=1/1 benign=1/3 noop_rejected=1/11 errors=0 met=False (bv+c2v) | exit 0: r42=0 mismatches=0 met=True |
| both 1be0db77 | exit 0: 1/1, 3/3, 11/11, errors=0 met=True | — | exit 0: r42=0 mismatches=0 met=True |
| bv ff8a49a8 (base+variants) | exit 0 met=True (exec checker from 1be0db77) | exit 1 benign=1/3 noop_rejected=1/11 met=False | — |
| c2v 3e51a57d (c2only+variants) | exit 0 met=True | exit 1 benign=1/3 noop_rejected=1/11 met=False | — |
| build tip e4891d8a | exit 0: 1/1, 3/3, 11/11, errors=0 met=True | exit 1: 1/1, 1/3, 1/11 met=False | exit 0: r42=0 mismatches=0 met=True |

Commands (exact, from the run): `python3 tools/round58-c1-counter.py --repo <clone> --tip <rev> --checker-blob <rev>:tools/round58-battery-exec-check.py --work <S>` (exit 0 each); `python3 tools/round58-c2-counter.py --repo <clone> --tip <rev> --manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e` (exit 1 at base/c1only, exit 0 at c2only/both/tip); r57 checker run with `--checker-blob`/`--checker` from base blob `tools/round56-prereg-check.py`.

## Findings

1. **No cross-claim interference found on the tested surfaces.** C1 files (exec checker, counter, variants) do not touch SCORECARD.md; the C2 counter reads only SCORECARD + `tools/round42-selfdesc-reconcile.py` + `round41`, and the C1 counter reads only `tests/round58-battery-variants/`, `tools/round56-env-leg-battery.py`, `tools/round56-env-leg-test.py`, `tools/round54/56-replay-code-audit.py`, `.ufo/waves/round-56/preregistration.json`. The C1 exec checker reads `tools/round56-env-leg-battery.py` and `.ufo/waves/round-56/preregistration.json` from the tip. Neither claim's counter output depends on the other claim's files. C2's r42 row ran identically at base, c1only, and both.
2. Counter outputs are independent: C2 `mismatches` is unchanged by C1 (c1only = base = 4; both = c2only = 0). C1 `met` is unchanged by SCORECARD (c2v = bv, c1 exec met=True at both c2only and base+variants).
3. **Freeze text inconsistency (LIMIT, not a claim failure).** The freeze states r42 "stays 1 until the L1 lands the round-58 SCORECARD section (banner and Planned heading)". At the scratch c2only commit the frozen counter reports r42=0 with no round-58 section beyond the existing `### Planned (round 58)` at line 3160 of the base SCORECARD. The base r42=1 is entirely the `r41` calibration item (`corpus/lessons` glob count `43` in SCORECARD, tree has 44). After the closure row fix, `r41` = 0. The `planned` check passes at base because the heading already exists. The freeze note's expectation is therefore not what the frozen counter produces; the counter's own predicate (r42=0 and pointer mismatches=0) is the one that holds, and it is met at the build tip (r42=0 mismatches=0 met=True, verified at e4891d8a).
4. **Observed, not a C2 defect:** the tip C2 row names round 57 (`rejected-honest-stop`), and MANIFEST rounds 56 and 57 both read `rejected-honest-stop`, so the pointer is consistent with the ledger. The `corpus/lessons/round-58-verifier-spotcheck.md` is absent at tip (0 matches), as the measured-tip rule requires.
5. **Base C1 counter cannot run on base alone.** The fixture variants are not in the base tree, so `round58-c1-counter.py --tip 2f53614e` is not evaluable; this is a harness precondition, not a result. The r57-checker-under-test numbers (1/3, 1/11) are reproduced exactly at bv and c2v, so they are a property of the checker and not of SCORECARD.

## Verification
- Ancestry: base 2f53614e <- freeze dcd69473 <- tip e4891d8a (git merge-base --is-ancestor, exit 0 both).
- Tip diff vs scratch `both` restricted to tools/tests/SCORECARD.md: only `tools/round58-c2-counter.py` (the counter itself, not a tip file) — exit 0.
- Receipts: 26 files under `.ufo/waves/round-58/w1/out/C02ClaimSeparability/receipts/`.
- Scratch clone and commits removed; scratch dir empty.

## Limits
- Only the surfaces listed were checked; I did not audit other SCORECARD rows or tools/ beyond these counters' read sets.
- The 11 no-op variants are the enumerated set; no survivors outside them were searched for (out of scope for this item).
- Did not touch the lane tree, fleet root, or MANIFEST; the lane working tree is dirty with other waves' files (not mine).
- Tool installs: none.
