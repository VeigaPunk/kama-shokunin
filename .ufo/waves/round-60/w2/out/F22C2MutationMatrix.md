F22C2MutationMatrix — C2 score gate attack. Axes: calibration (primary), operability.
Inspected frozen C2 claim and score()/controls() in round60-c2-counter.py; W1 mutation report is C1-specific, not C2 evidence.
The five controls cover tautologies, verdict flips, quote corruption, dropped population lines, and capture hash tamper.
Unprotected gates: evaluated-row minimum (5), distinct evaluated-line minimum (4), and amendment linkage (`amended == contra`).
Counterexample construction: use not-observable rows to preserve full coverage while lowering evaluated counts; omit a contradicted row's amendment linkage.
These are source-derived control gaps; I did not execute scratch mutations, so do not treat as observed `met=True` counterexamples.
Smallest correction: add independent synthetic controls for each threshold and amendment linkage; leave frozen predicates/verdicts untouched.
Lane source unchanged; no tools installed or updated.
