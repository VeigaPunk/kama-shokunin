# CRT01Claims — seat summary (kama r74 w1 critic)

Scoped findings: `.ufo/waves/round-74/w1/CRT01Claims/report.md`
Full attack log: `.ufo/waves/round-74/w1/CRT01Claims/attack.md`
Receipts: `.ufo/waves/round-74/w1/CRT01Claims/receipts-full.txt`

Headline: no claim refuted on its own terms — all three v2 modules survive all 11
constructed attack fixtures plus 5 randomized-path copies, verdict- and count-
consistent with the critic's oracle across the full matrix; the frozen scorer is
green on all three claims (c1 v2_killed=1, c2 v2_killed=2, c3 v2_killed=1, all
clean=True). The mixed-case arm is proven load-bearing (a case-sensitive strawman
fails c2_mixed_honest on exit code AND bound_revisions). Fixture-name gaming is
disproven for all three modules. Four freeze under-specifications are routed
report-only (F1b total semantics; F2b unbound-claim kind enumeration; F2c
context-free hex-mention binding; F2g finding path field) plus one semantics note
(F3c) and one process disclosure (F2h: the C2 live file rotated through ≥4 digests
under concurrent mutation testing after grading — every variant stayed
oracle-consistent on my matrix; L1 should re-run score-survivors.py once the
mutation-testing seats settle).
