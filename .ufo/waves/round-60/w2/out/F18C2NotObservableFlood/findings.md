# F18C2NotObservableFlood — C2 not-observable saturation

Axes: calibration (primary), operability (secondary; predicate controls still pass despite empty observable coverage).

Counterexample: W1 K03MetaLoopCritic's `score()` fixture used 14 valid rows: 6 live-predicate rows on 6 population lines plus 8 `not-observable` rows on the remaining 8. It returned `covered=14/14 evaluated=6 eval_lines=6 sensitive=6 bound=6 contradicted=0 amended=0 receipt_ok=True errors=0 met=True`; all five controls rejected. Thus 8/14 may be marked not-observable while meeting the frozen minimums. The frozen predicate has no cap; mathematically, with 14 fixed lines and minimum 5 live evaluations over ≥4 lines, up to 9/14 rows may be not-observable, with 5 live rows distributed across 4+ lines.

Evidence: `w1/out/K03MetaLoopCritic.md` lines 40–43 records exact construction/results; frozen predicate `controls/freeze.txt` lines 28–43 fixes population 14, coverage and minima, but imposes no not-observable ceiling. Counter `tools/round60-c2-counter.py` lines 200–207 credits such a row toward coverage/good_rows solely for empty predicate and reason length ≥20; `score()` lines 230–231 checks minimum live counts, not maximum unobservable count. Frozen limit only says not-observable rows do not count as evaluated.

Smallest safe correction: freeze a per-line observable/unobservable rationale criterion and cap unobservable rows (or require each to match a bounded frozen list of unobservable causes); retain minimum evaluated rows/lines. This is a finding only; no lane files or predicates changed.