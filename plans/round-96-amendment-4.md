# Round 96 — amendment 4 (the nd=3 ceiling is 624,999; the counter derives every rank)

Date: 2026-11-08. Author: L1 `KamaR96`. Amendment 3 `b3289c18`; this amendment lands the arithmetic
correction wave-1 `SC02BaseDiscriminator` found by binary-searching every row of the new table at the
tip's own parser.

## The defect

SKILL.md's table stated `625,000` decidable headers at `nd = 3`. The naive quotient `5 000 000 / 8` is
625,000; the preamble's four steps were subtracted from ranks 0, 1, 2 and 4 but not from rank 3. Measured
at `nd = 3` (8 steps/header + 4 preamble):

```
n = 624,999  ->  invalid   (4 + 8 x 624 999 = 4 999 996 steps; decided)
n = 625,000  ->  "-"       (4 + 8 x 625 000 = 5 000 004 steps; undecidable)
```

Worse, `tools/round96-depth-audit.py` carried `("625,000", "nd3-ceiling")` as a required needle, so the
instrument printed `mismatches=0 met=True` at the tip while blessing the figure the code does not enforce
— the exact class C3 exists to catch, found by a seat rather than by the L1.

## The repair

- `SKILL.md` row `| 3 | 8 | 624,999 |`.
- The depth audit derives `(MAX_STEPS - 4) // (5 + nd)` for every rank 0–4 and requires **both** that the
  derived count equals its stated expectation **and** that `"{:,}".format(derived)` appears in SKILL.md —
  so no rank can drift from the code without reddening the counter. `checks` goes 9 → 14.

## Measured

```
python3 tools/round96-depth-audit.py --repo . --rev 20317286   -> checks=14 mismatches=0 met=True  exit 0
python3 tools/round96-depth-audit.py --repo . --rev 5d43528b   -> checks=14 mismatches=14 met=False exit 1
```
