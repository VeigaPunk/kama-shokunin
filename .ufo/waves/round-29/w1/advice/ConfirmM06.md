# ConfirmM06 — C1 first-falsifier review (base receipt)

**sid:** `SCORECARD.md:Q:0ccd533544:0` — SCORECARD.md line 823 at base 2aa46e24, class Q, token `` `required=3 found=0 verified=0 missing=3` ``, counter observed `q:no-artifact`.

**W (writing revision):** `7229fa95eb122310e9e5334ad799ee3006293ebd` (round-19 "citation provenance, install-tree pin, r18 defect corrections"), confirmed by `git blame -L 823,823 --line-porcelain 2aa46e24 -- SCORECARD.md`.

## Verdict: confirmed-false

Independent hand-application of the frozen Q rule (counter not run) confirms the statement does not hold at W: the quoted span occurs verbatim in **no** committed blob at W outside SCORECARD.md/SHONEN.md/LOG.md/corpus. Counter observation `q:no-artifact` is correct.

## Evidence

1. **Blame** → W = 7229fa95 (line 823).
2. **Line/sid binding**: `sha256("before `required=3 found=0 verified=0 missing=3` exit 1; after")` → `0ccd533544…` matches sid hash; single backticked span on the line → k=0.
3. **Q rule by hand**: span 36 chars, contains digit and `=`, no blocked prefix.
   - `git grep -F 'required=3 found=0 verified=0 missing=3' 7229fa95 -- ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'` → exit 1, no match.
   - Without exclusions → only `SCORECARD.md:823` itself matches.
4. **Referent**: the span is the truncated "before" stdout of `python3 tools/citation-provenance.py` at the base state; actual full line per post-W evidence was `` `required=3 found=0 verified=0 missing=3 mismatch=0` `` plus three `missing:` detail rows (cf. C1UnreadableDoc.md:11, CritSeparability.md:31, DraftScorecard.md:14/23, .ufo/waves/round-19/evidence/c1-counting.txt:2 at 5b108c1). At W the run was uncommitted; the verbatim span first enters committed non-excluded history after W (round-19 build advice, e.g. CritC1Inflation.md:7 at 84cf2f7+). Fleet reports: no match.

## Cause (≤25 words, for correction row)

Q span appears only in SCORECARD.md itself at W; actual output runtime, uncommitted at W.

## Residual risk / gaps

- The statement's underlying substance (before count 3/0/0/3, exit 1) is corroborated by post-W committed runs; failure is missing committed evidence at writing, not fabrication.
- Exact pre-fix tool output variant not re-run (counter not executed per assignment); reconstructed from tool source at W and post-W receipts.
- No counter defect found: extraction, exclusions, and absence check reproduce by hand.

Outputs: `.ufo/waves/round-29/w1/out/ConfirmM06/verdict.json` (full command log + report). No lane files touched.
