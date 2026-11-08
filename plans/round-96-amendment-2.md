# Round 96 — amendment 2 (wave-1 RV01 findings; claim wording and instrument repairs)

Date: 2026-11-08. Author: L1 `KamaR96`. Freeze `58001b71`; amendment 1 `e2fed9f5`; this amendment plus
the repaired instruments land in the commit that measures M1/M2/M3. Wave-1 seat `RV01StepBudget`
(`.ufo/waves/round-96/w1/out/RV01StepBudget.md`) raised one BLOCKER and four narrower falsifications
against the frozen wording; each is answered below, and the frozen predicates are unchanged in their
property — only the fixtures and figures the code actually produces are corrected.

## F1 (BLOCKER) — W12-strings could not grade `MODEL_OK`

The fixture wrote one 6 MB string with a declared array length of 6 000 000; the probe's
`base + 8 * n > size` guard fired before the step loop, so the state was `invalid` and the cell could
never reach the `MODEL_OK` expectation. **Repair:** the fixture now writes 9 bytes per element (a u64
length prefix plus a one-byte string) — `54 MB + 49` — so the per-element loop charges a step and trips
`MAX_STEPS` at element 5 000 001, grading `-` (undecidable → loadable). RV01's own counter-proof used
exactly this shape and got `MODEL_OK` in 0.9 s.

## F2 — `5 + nd` steps per tensor header, not 6

The parser charges `5 + nd`: name length `u64` + `skip` = 2, `nd` = 1, `nd` dims = `nd`, type + offset = 2.
Six is the `nd = 1` case. **Repair:** the SKILL table now prices `5 + nd` and states the per-rank
ceiling; the C2 predicate's table row carries the same arithmetic. C1's claim is unaffected in kind —
W11's fixture is nd = 1 by construction and the 700 000-tensor file is graded on that rank — but the
claim now says `nd = 1` instead of asserting an unqualified 833 333.

## F3 — four preamble steps; the nd = 1 boundary is 833,332, not 833,333

`(5 000 000 - 4) / 6 = 833 332` decidable headers, measured (833 332 → `invalid` at 4 999 996 steps;
833 333 → `-` at 5 000 002). **Repair:** the SKILL figure is 833,332 and the depth counter's
`CEILING` derives `(max_steps - PREAMBLE) // STEPS_PER_HEADER`, so the counter and the prose share one
arithmetic; the probe's own comment keeps `~833 333` and is now the only rounded figure.

## F4 — C2's "before" was misdescribed

The base `SKILL.md` carried **no** tensor-ceiling sentence at all, so the claim's before-state is
"the step cost is undocumented outside the parser" — not "a false 1 000 000 sentence". **Repair:** the
plan's C2 before-state is restated in this amendment; the depth counter DROPS the vacuous
`"ceiling 1,000,000"` check (true of neither revision) and instead grades the five arithmetic cells the
table must satisfy. Base control re-committed: `DEPTH_AUDIT checks=9 mismatches=9 met=False`.

## F5 — C3 green while the new counter's docstring repeated `MAX_STEPS (4 000 000)`

**Repair:** the counter's docstring states 5 000 000, and the disclosure counter gained a fourth check
that reads the counter's own module docstring against the probe's `MAX_STEPS`. Base control re-committed:
`DISCLOSURE_AUDIT checks=6 mismatches=3 met=False`.

## F6 — the C1 base control used `--skip-load`

The plan named `--burners 0` (two natural passes); the committed control used `--skip-load`, whose
summary is structurally red and cannot express "W11 red, everything else green". **Repair:** the base
control is re-run as `--allow-clock --burners 0` (the flag only disables the W03 margin guard, which the
red control is expected to fail at this host's load) and the per-cell lines carry the discriminator.
`--skip-load` remains a self-test of the honesty rule, not a control.

## F7 — W03's truncation belongs to round 94, not round 95

The plan's parenthetical is corrected in this amendment: round 95's probe decides W03's 600 000-tensor
files (3 600 004 steps ≤ 4 000 000); the constant 60 s wrapper whose truncation W03 discriminates is
round 94's.

## Consequence

C1, C2 and C3 keep their axes and their properties; every figure now comes from the measured arithmetic.
Kill rule K3 ("the counter changes after this commit") binds the amended commit as the new reference:
`tools/round96-router-budget.py`, `tools/round96-depth-audit.py` and `tools/round96-disclosure-audit.py`
are byte-identical at the amendment commit and at the M commits measured below.
