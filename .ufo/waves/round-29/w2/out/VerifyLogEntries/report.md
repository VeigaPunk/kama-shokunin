# VerifyLogEntries — round 29 w2

## Findings

- **Low — LOG.md says timing transcript excerpts were committed, but they are not in the referenced data commit.** `LOG.md:1847–1848` says DataG01/DataG15 timing transcript excerpts were “committed with sha256” at `w1/out/ExecTimingTranscript/`. The directory and files exist in the working tree, but at `HEAD` / data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, `git ls-tree -r --name-only HEAD -- .ufo/waves/round-29/w1/out/ExecTimingTranscript/` returned no paths, while `git status --porcelain -- .ufo/waves/round-29/w1/out/ExecTimingTranscript/` returned `?? .ufo/waves/round-29/w1/out/ExecTimingTranscript/`. The on-disk evidence is therefore untracked, not committed at that revision.

## Checks requested

- Read the working-tree round-29 entry at `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:1835–1860`.
- Checked every explicit path in that entry (and the corpus locations implied by its KQ references) with `test -e`; all were present: `.ufo/waves/round-29/count-c1.py`, `SCORECARD.md`, `SHONEN.md`, `.ufo/waves/round-29/final/c1-513eba3b.out`, `.ufo/waves/round-29/w1/out/ExecTimingTranscript/`, `.ufo/waves/round-29/repairs/echo-exit2/receipt.txt`, `tools/prereg-time-check.py`, `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/lessons/round-28.md`, and `corpus/lessons/round-29.md`.
- Census commands returned the requested counts:
  - `git show 2aa46e24:corpus/SOURCES.md | grep -c '^| S'` → `173`.
  - `grep -c '^| S' corpus/SOURCES.md` → `177`.
- Re-verification commands all exited 0:
  - `python3 tools/prereg-time-check.py --selftest --scratch /tmp/kama-r29-w2-VerifyLogEntries/ptc-scratch` → `SELFTEST PASS`; 13 case-level `[PASS]` lines. The LOG’s “14 PASS” corresponds to those 13 plus the aggregate `SELFTEST PASS` line, not 14 individual cases.
  - `python3 tools/citation-provenance.py --selftest` → `selftest: ok (24 cases)`, exit 0. It prints an expected missing-fixture diagnostic during the selftest.
  - `python3 tools/report-landing-audit.py --selftest` → `selftest cases=79 failed=0`, exit 0.
  - `python3 tools/sources-append-only.py --selftest` → `42/42 selftest cases passed`, exit 0.

## Scope / residuals

An initial prereg-time-check selftest was accidentally run with its default scratch before the steering correction; its output identified `/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck/ptc-selftest-ywq_7og0`. A two-run PASS-count command had also started before the correction and used the default scratch; its captured output did not identify those generated directory names. No files were deleted outside the permitted output directory or `/tmp`. The final prereg selftest used the seat-unique `/tmp` scratch. No tools were installed.

No other path-existence or census mismatch was found. The transcript commit-status discrepancy above is the remaining actionable finding for this slice.