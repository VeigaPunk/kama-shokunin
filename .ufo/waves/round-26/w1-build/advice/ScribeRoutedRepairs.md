Verdict: Defects 2, 4, and 6 are grounded; three append-only draft files with exact proposed text and line evidence are prepared. No corpus or SCORECARD source was edited.

## Findings and proposed behavior

- **Defect 2 — KQ36 / lesson row 2.** The KQ36 requirement at frozen `a23c0e042114016a909eb15173aa6df74b5b7eb0`, `corpus/QUALITY.md:203`, uses “landed tip” without a byte-identity qualification. The frozen `corpus/lessons/round-25.md:49` says the SKILL registry row says M17 survives. Searching frozen `SKILL.md` for `M17` returned only lines 883 and 889: line 883 says M17 follows the current local-store spelling; line 889 records the M17 re-anchor and M33's second call site. Neither says M17 survives. Draft: append a KQ36 landed-tip definition to QUALITY and an erratum correcting only the false SKILL attribution in lesson row 2.
- **Defect 4 — context-capacity.** Frozen `corpus/knowledge/context-capacity.md:55-56` calls a log warning the only trace. The opened K5 log also has the capping line at `.ufo/waves/round-25/final/raw/K5.server.log:1083`. Frozen entry line 137 counts each released slot at `n_tokens = 1025` as occupied cells; the L1 log lines 1852 and 1866 record 1025, which includes the token that could not be placed. Each slot held 1024 cells. No dedicated errata section/convention was found; the entry mentions external `errata-attempt-2.json` at line 42. Draft: append a new dated errata section correcting both statements.
- **Defect 6 — scorecard trend.** Frozen `SCORECARD.md:1306-1309` calls quality unchanged-to-improved and discernment improved. The fleet report says both unchanged (`.ufo/reports/round-25/kama.md:120-129`); the frozen closure says quality unchanged at line 187 and discernment unchanged at line 194, and identifies the contradiction at lines 200-201. Draft: append a round-26 heading to SCORECARD correcting the two trend verdicts while retaining expansion improved.

## Gates and evidence provenance

- Read the lane's round-26 preregistration and frozen counter as assigned context; no counter was run.
- Prepared the permitted output directory with `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs`; the shell tool returned normally with no output and exposed no separate numeric exit-code field.
- Extracted the required frozen files from `a23c0e042114016a909eb15173aa6df74b5b7eb0` with:

  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive --format=tar --output=/fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/a23c0e.tar a23c0e042114016a909eb15173aa6df74b5b7eb0 -- SKILL.md SCORECARD.md corpus/QUALITY.md corpus/lessons/round-25.md corpus/knowledge/context-capacity.md && tar -xf /fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/a23c0e.tar -C /fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/frozen`

  The command produced no output and returned without a reported error. A second archive extraction added the frozen closure:

  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive --format=tar --output=/fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/a23c0e-closure.tar a23c0e042114016a909eb15173aa6df74b5b7eb0 -- corpus/lessons/round-25-verifier-spotcheck.md && tar -xf /fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/a23c0e-closure.tar -C /fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/frozen`

  It also produced no output and returned without a reported error. The shell tool did not expose a separate numeric exit-code field; no code is inferred here.
- Frozen SKILL search result for `M17`: exactly the two hits at `SKILL.md:883` and `:889`; their text is quoted in the defect-2 draft.
- Errata search on the frozen context-capacity entry found only the line-42 reference to `.ufo/waves/round-25/errata-attempt-2.json`; the errata-heading search found no match.
- Raw-log observations: K5 capping line at `K5.server.log:1083`; L1 release lines at `L1.server.log:1852` and `:1866`. Exact quoted text is retained in the defect-4 draft.

## Gates, limits, and scope

- Checks were static reads/searches of the frozen corpus, round-25 report/closure, and supplied raw logs. No test, build, counter, or live server was run. No tool was installed.
- No product-source files were edited. The drafts are proposals only; append behavior and corrected source state remain unverified until the integrator applies them.
- No commits, pushes, or lane Git/JJ mutations were made. The only scratch output is under `/fast/scratch/hyaku/kama-r26/ScribeRoutedRepairs/`.

## Files written

- `.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs/Defect2-KQ36-and-lesson.md`
- `.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs/Defect4-context-capacity.md`
- `.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs/Defect6-scorecard-trend.md`
- `.ufo/waves/round-26/w1-build/advice/ScribeRoutedRepairs.md`

No unrelated or out-of-scope items were changed.