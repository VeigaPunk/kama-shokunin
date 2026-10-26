# R1Decl — round-47 W1 report (pointer check, registry/append-only-contract.tsv)

VERDICT: 3 of 7 contract rows have weak `declared_at` pointers (rows 2, 3, 6) and row 2's rule letter `A-corr` contradicts the file's own governing declaration (SCORECARD.md:6 declares in-place head re-derivation); rows 5 and 7 are exact, row 1 is adequate with a dangling note citation (PROTOCOL.md does not exist at the checked tip); all 7 rows pass the C1 counter's `contract` leg, so every finding is semantic.

Scope: per-row `declared_at` line at 3a09a1d93dcc16799cf6c4b48786e6440af134c4 + lane-wide/`grep -i 'append-only'`/`'append'` search for stronger declaring lines; rule-letter consistency against the declaring text. Read-only git on the lane; no clone, no counter run, no tools installed (none needed).

## Findings (by severity)

1. **MEDIUM — row 2 letter contradiction (SCORECARD.md / A-corr / corpus/README.md:521).** SCORECARD.md:6 (current authority) declares the `## Axes`, §Planned, §Retired, §Saturation, §Capabilities head sections "re-derived from the tree … and kept current" in place each round; the contract's own note concedes "a head re-anchor is an expected partial". `A-corr` means corrections land appended, old text intact — the letter overstates for half the file and the truth lives only in the note. Command: `git -C <lane> show 3a09a1d…:SCORECARD.md | sed -n 6p`. Fix (frozen contract → proposed text only, in rows.md): note-first rewording or a new rule letter (e.g. `A-corr-head`).

2. **MEDIUM-LOW — row 6 pointer declares nothing for its glob (corpus/lessons/*.md / corpus/lessons/round-23.md:100).** The declared line is the two-word fragment "are append-only." — the tail of a round-23-specific sentence about that one file; the pattern expands to 79 files (`ls-tree -r --name-only <tip> -- corpus/lessons/ | wc -l` = 79, 0 non-`.md`). The counter passes it on the fragment alone. Better line: `corpus/QUALITY.md:143` (KQ26, "Corrections to filed lessons … are appended with the superseded text/revision named").

3. **LOW — row 2 pointer weak (corpus/README.md:521).** It is the round-33 disposition remark "…are corrected by append-only records in `corpus/lessons/round-33.md` and `SCORECARD.md`." — history, not a standing rule. Better: `corpus/README.md:759-761` ("the five files the lane treats as append-only (SCORECARD.md, …)") or `SCORECARD.md:130`.

4. **LOW — row 3 pointer weaker than its own note's citation (corpus/QUALITY.md:24).** The note cites "(QUALITY.md:4-5)" — "Criteria are added as new rows; supersession names the old criterion instead of erasing it" — while `declared_at` points at the round-10 block's incidental line 24. KQ7 (`corpus/QUALITY.md:29`) is equally strong. Proposed: declared_at `corpus/QUALITY.md:4`.

5. **LOW — row 1 note cites a missing file (LOG.md / README.md:16).** `git cat-file -e 3a09a1d…:PROTOCOL.md` → exit 128, and no deletion record exists — PROTOCOL.md never existed in lane history; the live rule is `AGENTS.md:4` ("Every change appends a LOG.md entry"). The declared_at line itself is adequate. Proposed full row text in rows.md.

6. **INFO — row 4 borderline (corpus/README.md:86).** States the discipline ("Appended rather than inserted, so no existing line moves") but scoped to the round-10 coverage map; the standing declaration is `corpus/README.md:759-761`. Optional improvement; no contradiction.

**Pass rows:** 5 (corpus/SOURCES.md / A-row / SKILL.md:578 — the gate row states the exact rule: "removed row or a changed cell outside `status`/`recheck`/`used-by`"; KQ22 at `corpus/QUALITY.md:123` restates it; tool exists at tip) and 7 (registry/history/DELTA.md / A / self-header :3-4 "Append-only; … never hand-edited").

## Context recorded
- The contract file does not exist at the freeze commit bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba (`cat-file -e` exit 128; `diff --stat` shows 8 insertions into 3a09a1d) — created at the build commit, consistent with the names-frozen/content-at-build model; worktree identical to 3a09a1d. Not scored.
- The lane-wide `append-only` grep (201 hits) is dominated by `.ufo/` wave archives; no standing declaration for any of the 7 paths beyond those cited above.

## Residual risk / verification gaps
- "Declares the rule" judgments are textual readings of the cited lines (quoted verbatim in rows.md/evidence.txt); no counter was run (not required for a pointer check; the `contract` leg passes for all rows by construction).
- Contract frozen: all fixes are proposed text in `out/R1Decl/rows.md`, nothing applied to the lane.

Full per-row table with verbatim lines: `.ufo/waves/round-47/w1/out/R1Decl/rows.md`; raw evidence: `.ufo/waves/round-47/w1/out/R1Decl/evidence.txt`.
