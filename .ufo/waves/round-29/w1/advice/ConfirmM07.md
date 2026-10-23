# ConfirmM07 advice — SCORECARD.md:Q:4c5d902830:0 (kama round 29, WAVE 1)

Verdict: **confirmed-false** (counter observation `q:no-artifact` independently reproduced by hand; the counter was not executed — its sha256 was verified as fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383).

- W = 7229fa95eb122310e9e5334ad799ee3006293ebd (blame at base 2aa46e24, line 824), "round-19: citation provenance, install-tree pin, r18 defect corrections".
- At W the span `required=3 found=3 verified=3 missing=0 mismatch=0` occurs verbatim only in SCORECARD.md:824 (the statement itself). corpus/lessons/round-19.md:11-12 wraps it across a newline and corpus/** is excluded by the rule anyway. No other blob at W matches, even partially.
- Referent: uncommitted stdout of `python3 tools/citation-provenance.py` (introduced at W). The verbatim span is first committed ~7 min later at 5c0b475/5b108c1 (.ufo/waves/round-19/evidence/c1-counting.txt:8 and round-19 build advice).
- Corroboration: SCORECARD:824 says "selftest 5 cases" but the tool at W prints "selftest: ok (12 cases)" — the text was drafted from an earlier iteration's terminal output, not from W's tree.

Correction row for the L1: sid `SCORECARD.md:Q:4c5d902830:0`, observed value `q:no-artifact`,
cause: "Quoted citation-provenance stdout was never committed at W; nearest committed text (corpus/lessons/round-19.md) wraps the span, and corpus is excluded."

Full evidence: .ufo/waves/round-29/w1/out/ConfirmM07/verdict.json (commands + exact outputs) and REPORT.md.
