# ConfirmM08 — advice (C1 first falsifier: sid SCORECARD.md:Q:f1021c03db:0)

**Verdict: `confirmed-false`** (counter's `q:no-artifact` is correct; no counter defect).

- Statement: SCORECARD.md:833 at base 2aa46e24, written by W=`7229fa95eb122310e9e5334ad799ee3006293ebd`
  (round-19; confirmed via `git blame --line-porcelain`). Token `` `baseline=VALID members=3 rejected=0/3` ``.
- Independent check (counter not run): `git grep -F -n 'baseline=VALID members=3 rejected=0/3'
  7229fa95 -- ':!SCORECARD.md' ':!SHONEN.md' ':!LOG.md' ':!corpus'` → no matches (exit 1).
  At W the only occurrences are the statement's own line (excluded), SCORECARD.md:834
  (excluded), and the non-verbatim format template in `install-tree-grid.py:16`.
- Referent: no-pin run summary of `tests/llamacpp-live/install-tree-grid.py` (round-19 C2);
  real captured line `baseline=VALID members=3 rejected=0/3 tree_pin=off` was first committed in
  `5b108c1` (descendant of W), not at W. The quote truncates before `tree_pin=off` and was
  written from the tool's documented format.
- Suggested correction row observed value: `q:no-artifact`.

Full evidence: `.ufo/waves/round-29/w1/out/ConfirmM08/verdict.json` and `REPORT.md`.
