VERDICT: partial - S073's URL, 2.56.0 revision, anchors, quote, status/used-by and census hold; teaches clause 1 overstates the page (file-level text, and a re-added path has two add commits), the Gate's file pointer lacks the %at quote, and teaches clause 3 is lane-internal.
Attacked: corpus/SOURCES.md row S073 (line 85); round-21.md §Gate row (line 49); CORPUS.md "SOURCES.md — where a shokunin learns" against frozen .ufo/waves/kaika/SOURCES-CONTRACT-v1.md. Read-only on the lane. Evidence: falsify/out/ReopenS073/evidence.txt (E1–E17), experiment.py, rerun-output.txt. Installs/upgrades: none (git 2.56.0, curl, python3, man-db, col already present).

## Per-field: row S073 (contract v1)
| field | row says | verdict | basis |
|---|---|---|---|
| id | S073 | agree | next after S072; no duplicate (E12) |
| source | "git-log pretty formats and --diff-filter"; URL | partial (minor) | URL HTTP 200 (E1); title cell is a topic label, page title is "Git - git-log Documentation" |
| kind | docs | agree | |
| tier | A | agree | official manual; A covers the %at/%ct definitions and file-level --diff-filter text, not commit-level behavior |
| scope | %at/%ct, added-path selection, 2.56.0, not rewriting | agree | "last updated in 2.56.0" (E1, E2); page does not discuss rewriting |
| anchor | §PRETTY FORMATS %at/%ct; §DIFF FORMATTING --diff-filter; 2.56.0 | agree | sections and entries at E4, E5; versioned /docs/git-log/2.56.0 carries the same sentences (E2) |
| teaches 1 | "--diff-filter=A selects the commit that added a path" | disagree | page documents file-level selection only (E6); commit-level result is executed (E9), but a re-added path yields two add commits (c5, c1), so "the commit" is wrong |
| teaches 2 | "%at and %ct are distinct timestamps" | agree | page: author date / committer date, UNIX timestamp (E4, E5); E9 values differ |
| teaches 3 | "the audit's cutoff reads author time" | agree in fact; disagree as teaches | b76727f lines 134 and 152 use %at (E10); a lane fact, not a source benefit; contract: "one grounded learner benefit" |
| status | mined | agree | lesson cites S073 at lines 19, 49, 76 (E14); census mined=60 (E12) |
| opened | 2026-10-21 | agree | date -u (evidence header); matches Gate date |
| recheck | on-release | agree | versioned manual; cadence allowed by contract |
| used-by | corpus/lessons/round-21.md | agree | path exists; no corpus/knowledge entry cites S073 (E14) |

## Gate row (round-21.md line 49)
- Quote "author date, UNIX timestamp": verbatim (E4 line 1355; E5 line 5563), 4 words, located at §PRETTY FORMATS %at. Agree.
- File pointer SrcGitLogDiffFilter.md: disagree. It has no %at quote (E8, grep exit 1). It quotes %ct (line 8) and --diff-filter (line 9), and it is the superseded S066 draft whose basis was committer time.
- Coverage: the Gate grounds teaches 2 only. The %ct and --diff-filter quotes are absent from the Gate: partial.
- Attribution: the Gate credits the L1 manual reopen only to S071, yet its S073 location cites "L1 man git-log line 1355". Minor.

## Contract and census
- CORPUS.md section matches frozen contract v1 except the title line, a 3-line carry-over preface, and heading depth (E15): agree.
- Census with contract commands: rows 74; malformed 0; A70 B1 C3; mined60 queued7 rejected7; no duplicate, enum or used-by faults (E12). Matches the lesson's "after" census.
- Append-only, scratch clone at b76727f: "added S073 (allowed)", no violations, exit 0 (E16): agree.

## Other findings
1. SOURCES.md lines 6–7 say every row was opened in round 10 with its Gate in lessons/round-10.md. Wrong for S073 (opened 2026-10-21; Gate in round-21.md): disagree (header).
2. The worktree tools/report-landing-audit.py is not the measured blob: lines 169–177 read HEAD bytes when no path is given, and selftests were added at 453–472 and 531–536 (E11). The %at lines are unchanged, so teaches 3 holds. The measured artifact is b76727f.
3. report_cutoff takes out[-1], the oldest add in default order (E10). Teaches 1 hides that choice; merge-history behavior was not tested [INFERENCE].

## Recommended (L1 decides; nothing applied)
- Proposed teaches: "%at is the author date and %ct the committer date, both UNIX timestamps; --diff-filter=A keeps only added files, so a re-added path has more than one add commit." Move teaches 3 into the lesson's C1 text.
- Contract rule 2 allows only status, recheck and used-by to change in place. A teaches correction is a new row opening "supersedes S073 —", unless the L1 treats S073 as unsealed until the lane tip moves; v1 is silent on same-round rows.
- Gate: point the %at quote at the local man line 1355 and the web anchor; add verbatim %ct and --diff-filter quotes (advice lines 8–9) if those clauses stay.
- Header lines 6–7: replace "round 10" with a pointer to each row's Gate round.
- Optional: cite https://git-scm.com/docs/git-log/2.56.0 so the revision does not drift with the "latest" URL.

## Not tested / [INFERENCE]
- Rebase, amend and merge effects on %at/%ct: not tested; S073 claims none.
- Whether any other 2.56.0 sentence ties --diff-filter to commit selection: none found on this page (E6); the commit-level claim rests on E9.
