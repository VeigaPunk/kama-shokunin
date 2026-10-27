Survived: C2’s eight fixture scenarios kill only the two ledger-cutoff mutants; six applicable behavioral regressions survive, and the attempted in-tree-ledger override mutant survives too.

## Evidence

Detector contract: `tools/round52-append-restore-check.py` lines 41–53 and 331–432; invoked by importing that exact frozen counter and calling `fixtures(tool, S, detail)`. Pristine tool SHA-256: `343e8c18cab102fceb0c8735b60916015f2bfc6dbe4423e45471c7558c97d459`. Pristine baseline: `8/8`; each case reported `ok`.

| Mutant | Result |
|---|---:|
| Remove ledger-introduction cutoff | killed, 7/8 |
| Restrict cutoff to equality (miss descendant commits) | killed, 7/8 |
| Read in-tree ledger despite explicit contract | survived, 8/8 |
| `only=` prefix comparison changed to exact equality | survived, 8/8 |
| Exempt eligibility always true (`>= pcount` to `>= 0`) | survived, 8/8 |
| Fence opener accepts backticks in backtick-fence info | survived, 8/8 |
| Fence closer requires a longer-than-open fence | survived, 8/8 |
| Held formula drops `min(n, ...)` cap | survived, 8/8 |
| A-row permitted cell set also exempts immutable cell 9 | survived, 8/8 |
| A-row immutable-cell comparison always equal | survived, 8/8 |
| Fence closer requires exact rather than minimum length | survived, 8/8 |

Interpretation: fixture result `N/8` counts scenarios with expected CLI exit and independent-counter result, so a result below 8 kills the mutant. The cutoff regressions fail the after-introduction scenario. For the other surviving region/fence/held/A-row variants, none of these eight constructions exposes the altered behavior. No mutant was applied to the lane source; only scratch copies were mutated. Each run had a separate scratch fixture directory to avoid collisions. Restoring/byte-integrity evidence: source file remained untouched; pristine scratch copy hash before/after detector remains `343e8c18cab102fceb0c8735b60916015f2bfc6dbe4423e45471c7558c97d459`. Full per-case outputs and mutant inventory are in `.../w1/out/M5Fixtures/pristine-fixtures.json`.

Commands exercised (paths expanded): `python3` imported `tools/round52-append-restore-check.py`; called `fixtures(<mutant>, <unique scratch run dir>, detail)` for each listed mutant and pristine baseline. Fixture return values: pristine `8`; cutoff-removed `7`; cutoff-equality-only `7`; remaining mutants `8`.
