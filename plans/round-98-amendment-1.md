# Round 98 — amendment 1 (wave-1 findings: the unreachable C1 term, the invisible overcharge, the window edges)

Recorded `2026-11-08` after wave 1 landed its first reports and **before any measurement**
(`.ufo/waves/round-98/measured/` was empty; no cell had scored). Trigger artifacts, this round's
own wave:

- **`SN01StepFlips` (BLOCKING, sent by IRC and in `.ufo/waves/round-98/w1/SN01StepFlips.md`) —
  C1's predicate was unreachable with the frozen bytes.** `tools/round98-self-assessment-audit.py`
  check 16 parsed `adds (\w+) cells` from the budget counter's docstring, whose true sentence is
  "Round 98 adds two cells past that (new set = six cells, mutants = five)": `WORDS["two"] = 2`
  against `len(NEW_CELLS) = 6`, a term no edit to SKILL.md or SCORECARD.md can satisfy. Measured:
  a scratch tree with every surface at the plan's target values still prints `mismatches=1`, the
  sole failure being that term.
- **`SN01StepFlips` — check 18's docstring claim was false.** It said a `+1/header` parser "fails
  the set equality"; `charge_line`'s token filter does not see a bare `steps[0] += 1`, so an
  overcharging probe passes check 18, and (measured) a perfect-surface tree with an overcharging
  probe scored C1 `mismatches=0` and C3 `rows=8 mismatches=0` — RV03 F5's class still open.
- **`CR02Wording` + `SN01StepFlips` — the plan's overcharge window is off by one at the lower
  edge** (`714,286 < T` / `500,000 < T` should be `≤`), and disclosed limit (f) wrongly credits
  W11 with pinning the budget's lower bound (W11 sits outside the window; W14 pins it).
- **`CR02Wording` — M2's captured-by was false** (the control run exited 0; the L1's read of the
  `cells=` line caught it) and it cited a 16-cell receipt that was never committed.

## Corrections (the frozen sentence is narrowed to what the instrument enforces, never widened)

**A. C1 check 16 (the unreachable term).** The doc_cells term now parses the counter docstring's
own true sentence: `new set = (\w+) cells` → `six` → `len(NEW_CELLS)`. The base control receipt is
byte-identical after the change (SN01 measured this before proposing it).

**B. C1 check 18 / C3 (the invisible overcharge).** Both counters add one term: the tensor loop
must contain no `steps[0] +=`. Shown able to fail before it is trusted: on the real probe the term
is false (`overcharge detected: False`); on a one-line-patched probe it is true
(`overcharge detected: True`), and the patched probe's `steps[0] += 1` is exactly the frozen
`overcharge` mutant's injection site.

**C. C1 check 19 (duplicate headings).** RV01 measured that a duplicated live heading, or a
numeral count, passed or false-redded. Check 19 now also requires exactly one live
`### Round 97 correction` heading, so a second contradicting heading cannot hide behind `next()`.

**D. Plan text corrections (no predicate change).** The window is `714,286 ≤ T ≤ 833,332` at nd=1
and `500,000 ≤ T ≤ 555,555` at nd=4; disclosed limit (f) credits **W14** (not W11) with pinning
the lower bound from the `-` side; the C1 headline is narrowed to "the lane's **20 named**
self-assessment surfaces match the repo, heading included"; C2's graded class is stated as
**uniform** ≥+1/header (a conditional or compensating overcharge is outside it).

**E. Lesson M2** re-attributes capture to the L1's read of the `cells=` summary line (the control
run exits 0 on a short set) and drops the never-committed "16-cell receipt stands in the wave dir"
claim. A counter-level fix (fail `--control` when `n != len(selected)`) is routed to round 99.

The counters are re-frozen by this amendment's commit; K1 in the plan binds the post-amendment
bytes. No cell had scored when this landed.
