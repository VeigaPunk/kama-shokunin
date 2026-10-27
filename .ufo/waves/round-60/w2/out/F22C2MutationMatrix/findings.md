# F22C2MutationMatrix — C2 score gate-drop review

Axes: calibration (primary), operability (counter reliability). Frozen claim remains unchanged.

## Counterexample / evidence

W1 assigned evidence is the C2 calibration claim at the frozen base tip; it fixes population=14. The corresponding W1 control-clause mutation report is `MT01CounterClauseDrops.md`, but that report explicitly mutates **C1**, not C2, so it is not evidence that C2 gates are protected.

Inspected `round60-c2-counter.py::score` lines 180–234 and `controls` lines 243–282. Individual `met` gates are: coverage all population lines; >=5 evaluated rows; >=4 evaluated distinct lines; amended==contradicted; receipt hash/schema integrity; all syntactically good rows accepted; zero parse/evaluation errors. Evaluated rows also require predicate evaluation to agree with recorded verdict, and must be falsifiable.

The five in-counter families mutate all predicates to tautology, flip each non-not-observable verdict, corrupt each quote, drop each population line, and alter a capture body without updating its hash. Strongest counterexample: eliminate the minimum evaluation volume gates (`ev_rows >= 5` and/or `len(ev_lines) >= 4`). The existing controls do not directly mutate a valid registry into one with only four evaluated rows or three evaluated lines while retaining valid coverage through `not-observable` rows; those rows count toward covered/good, but not evaluated/evaluated-lines. Thus a registry can retain coverage=14/14 and valid receipt while satisfying fewer evaluated claims than the frozen threshold, yet clause-drop mutation is not detected by the listed controls.

A further exposed gate is `amended == contra`: controls do not independently remove an amendment entry for an otherwise valid contradicted row. The captured receipt tamper protects receipt hashes, not amendment linkage. This is a detection-gap hypothesis derived directly from the control transformations; no execution of an independently mutated scratch counter/registry was performed, so no acceptance result is claimed.

## Smallest safe correction

Add independent synthetic-registry controls that preserve quote coverage with not-observable rows while reducing evaluated rows below 5 and evaluated lines below 4 (one mutation per threshold), and remove the id/observed text for a contradicted row from amendment text; require each to make `met` false. Keep frozen thresholds, claim, and verdicts unchanged.
