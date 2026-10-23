# ConfirmM07 — sid `SCORECARD.md:Q:4c5d902830:0`

**Verdict: `confirmed-false`.** The counter's observed value `q:no-artifact` is correct; the base statement did not hold at the revision that wrote it.

## Statement and W

- Base 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d, SCORECARD.md line 824 (Round 19 section):
  `` `required=3 found=3 verified=3 missing=0 mismatch=0` exit 0, selftest 5 cases.``
- `git blame -L 824,824 --line-porcelain 2aa46e24 -- SCORECARD.md` names W =
  **7229fa95eb122310e9e5334ad799ee3006293ebd** ("round-19: citation provenance, install-tree pin, r18 defect corrections", committed 2026-10-21 03:34:47 -0300).

## Q rule applied by hand (counter not executed)

Rule (count-c1.py docstring, frozen sha256 verified `fe11d599…`): a backticked span of 6–200 chars containing a digit and `=` (or a listed word), not starting with a command prefix, must occur **verbatim in at least one blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md and corpus/\*\***.

- Extraction: span is 49 chars, contains `=`, starts with `required` — it is a legitimate quoted measurement output. ✓
- Artifact search at W: `git --no-replace-objects grep -F` over the **entire** tree at W (no pathspec) finds the contiguous span exactly once — the statement line itself (SCORECARD.md:824). No `.ufo/**`, no tool output, no registry blob carries it. ✗
- Nearest committed text at W is corpus/lessons/round-19.md:11-12, where the span is split by a line wrap (`…verified=3` ⏎ `missing=0 mismatch=0`); it is not a verbatim occurrence there, and corpus is excluded by the rule regardless. A partial `-E 'required=3|mismatch=0'` sweep of the whole tree at W confirms there is no reformatted variant anywhere else.
- Conclusion: check fails exactly as the counter observed → **q:no-artifact confirmed**.

## Where the quoted output came from

- `python3 tools/citation-provenance.py` (tool + `registry/required-citations.json` introduced by W itself) prints `" ".join(f"{k}={v}" for k, v in counts.items())` — with 3 registry rows all `ok` this is byte-identical to the quoted span, exit 0. The line quotes **genuine terminal stdout that was never committed at W**.
- The verbatim span first reaches committed non-excluded paths at **5c0b475 / 5b108c1** (2026-10-21 03:41:27, ~7 min after W): round-19 wave advice and `.ufo/waves/round-19/evidence/c1-counting.txt:8`. So this is the "artifact committed later" branch — the evidence trail exists, but not at the writing revision.
- No fleet report under /home/vgpnk/Projects/shokunin/.ufo/reports/ contains the span (grep: no matches).
- Corroborating signal (outside the assigned token): SCORECARD:824 also says "selftest 5 cases" while the tool committed at W prints `selftest: ok (12 cases)` (tools/citation-provenance.py:166), and round-19 build advice at 5c0b475 records selftest "(5 cases)". The SCORECARD text was drafted from an earlier iteration's runtime observations, and W shipped a further-evolved tool — consistent with the counts line likewise being uncommitted-at-W runtime output.

## Correction-row material for the L1

- sid: `SCORECARD.md:Q:4c5d902830:0`; observed value (counter's string): `q:no-artifact`.
- Cause (≤25 words): "Quoted citation-provenance stdout was never committed at W; nearest committed text (corpus/lessons/round-19.md) wraps the span, and corpus is excluded."

## Verification status and residual risk

- All commands read-only; outputs quoted verbatim in verdict.json (long `5c0b475` grep trimmed with mid-line ellipses, marked in place).
- The counter was never run; its sha256 was verified instead (`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`).
- Exhaustiveness: the full-tree `grep -F` at W covers every blob of W's single root tree with `--no-replace-objects`; a verbatim occurrence is byte-contiguous, so a line-wrapped instance cannot hide from it. Residual risk: only objects outside W's tree (irrelevant — the rule checks W's tree alone) and any environment-injected object stores, which the seat shell did not set.
