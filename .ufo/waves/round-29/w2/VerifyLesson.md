# VerifyLesson — round-29 lesson verification (seat kama-r29-w2-VerifyLesson-4, wave w2)

Scope: `corpus/lessons/round-29.md` (untracked, attempt-1 artifact) — commit hashes, counts
(69 statements / 11 mismatches / 14 controls / 32 wave-1 seats), Gate rows S174–S177 vs
`corpus/SOURCES.md`, Mistakes row completeness, repairs-table evidence paths.

Method: fresh clone `/tmp/kama-r29-w2-verifylesson-4/lane` (cloned from the lane repo, checked out
at `513eba3b`); frozen counter rerun independently at base and tip; git metadata read in the clone;
working-tree artifacts read in place. Read-only throughout — no lane file, index, or jj state
touched. No tools installed (used preinstalled git 2.56.0, python3, man-db); no pacman run.

## Verified (with evidence)

**Commit hashes — all correct.**
- `827d136546b85059a984b34970f5b493d9a71290` "round-29: C1 freeze (calibration)…", adds exactly
  the four artifact classes the lesson names: `.ufo/waves/round-29/count-c1.py` (368 lines),
  `preregistration.json`, `before/c1-base.json`+`before/c1-base.out`, `before/census-start.out`.
- `35b90184f638ab6a4149092b93143c7a2b873787` "pre-freeze control call receipts (14 seats…)…before
  any correction row".
- `513eba3ba51a142c9936553e3a85918345eb5c4c` "C1 data (11 appended self-assessment correction rows)…".
- Linear order 827d1365 → 35b90184 → 513eba3b; base `2aa46e2481d2…` exists.
- Counter identity: `sha256sum .ufo/waves/round-29/count-c1.py` =
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` ✓ frozen value.

**Counts 69 / 11 — reproduced by independent rerun.**
- Base run: `python3 .ufo/waves/round-29/count-c1.py --repo <clone> --tip 2aa46e24…` →
  `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0
  unresolved 11 met False tip 2aa46e2481d2`, exit 0 — byte-identical to the committed
  `.ufo/waves/round-29/before/c1-base.out` and matches the lesson's quoted base receipt.
- Tip run (fresh clone at 513eba3b) → `statements 69 mismatched_at_base 11 append_only True
  valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`, exit 0 —
  matches `.ufo/waves/round-29/final/c1-513eba3b.out` exactly. by_class 27+2+2+10+25+3 = 69;
  11 mismatches = 7 Q + 4 P.

**14 control seats at 35b90184.** Tree has 13 `Ctl*` dirs + `RefPaste` = 14 seat dirs;
`controls/SUMMARY.md` lists 14 rows; the lesson's quoted shortcut numbers match it verbatim
(CtlSourceBounds valid 9 / false 7 / unresolved 9; CtlBaseTree 6/4/9; RefPaste met True as the
reference policy). Lesson wording ("14 seats … no control meets … RefPaste meets by design") is
accurate. (The assignment's phrase "14 pre-data controls all fail" loosely counts RefPaste among
controls; the repo distinguishes them.)

**32 wave-1 seats.** `.ufo/waves/round-29/w1/out/` contains exactly 32 seat dirs;
`w1/dispatch.json` `counts.spawn = 32`; `w1/first-try-dispatch.json` `counts.spawn = 37` confirms
the lesson's 37-seat first send.

**Gate rows S174–S177 vs SOURCES rows — match.**
- URLs: identical in lesson and `corpus/SOURCES.md` rows (S176 carries both git-grep and
  gitglossary URLs in both).
- Dates: SOURCES `opened` = 2026-10-23 for all four; lesson accessed times match the scribes'
  recorded times exactly — ScribeSrcGitBlame 12:02:48Z, ScribeSrcMergeBase 12:03:03Z,
  ScribeSrcGitGrep 12:02:41Z + 12:02:57Z, ScribeSrcPrettyFormats 12:02:47Z
  (`w1/out/Scribe*/` artifacts, each with `page.html` + `quote.txt` + `row.md`).
- Quotes: verbatim against the installed Git 2.56.0 manuals (wrap-tolerant check;
  `man git-blame|git-merge-base|git-grep|gitglossary` flattened text):
  - "last modified the line" ✓ and "output commit information for each line, not just the first
    time a commit is referenced" ✓ (man justification inserts a tab inside "is referenced";
    naive line grep misses it).
  - "and exit with status 0 if true, or with status 1 if not." ✓ (same tab effect at "if true").
  - "Instead of searching tracked files in the working tree, search blobs in the given trees." ✓;
    "If it matches, the path is ignored." ✓.
  - S177 "committer date, UNIX timestamp" ✓ present in the scribe's saved `page.html` (no local
    pretty-formats man page exists on this host — `man pretty-formats` and `man gitpretty-formats`
    produce nothing; the lesson's "where available" preamble covers this).
- SOURCES diff is append-only: `git diff -- corpus/SOURCES.md` = 4 insertions, 0 deletions;
  S174–S177 status `mined`, used-by `corpus/knowledge/self-assessment-at-writing.md,
  .ufo/waves/round-29/count-c1.py` exactly as the lesson states.

**Mistakes rows — complete.** Exactly 2 rows; both fill class / evidence pointer / captured-by /
fix. Evidence verified:
- `mined/orig-75b78bb4.out` contains "no ISO-8601 UTC timestamps found" ✓;
  `mined/patched-75b78bb4.out` contains "FLAG line 41: 2026-10-23 ~08:45Z (later than commit by
  404s)" and `exit=1` ✓; `mined/patched-selftest-v2.out` has 14 PASS ✓; worktree
  `tools/prereg-time-check.py` carries the `(T| | ~)` parser fix ✓.
- `w1/out/ConfirmM02/verdict.json`, `ConfirmM04/verdict.json` exist ✓.

**Repairs table — 9 items, 8 of 9 evidence paths exist with matching content.**
1. `corpus/QUALITY.md:283` KQ38 ✓; `w1/out/ScribeDepthCriterion/` ✓.
2. `w1/out/ScribeA1TimeCorrection/evidence.txt` ✓; `git log -1 --format=%cI 75b78bb4` =
   `2026-10-23T05:38:16-03:00` — exact match to the lesson.
3. `w1/out/ExecTimingTranscript/provenance.json` ✓; excerpt-DataG01-2.jsonl contains
   08:35:53.929Z and 08:35:54.037Z; excerpt-DataG15-2.jsonl contains 08:36:53.343Z and
   08:36:53.398Z — all four quoted timestamps present.
4. `w1/out/ExecGateRegistryV2/` ✓. 5. `w1/out/ScribeInstrumentRegistry/` ✓.
6. `.ufo/waves/round-29/repairs/echo-exit2/receipt.txt` ✓ ("routed item 6 … refuses an existing
   --out path", lane_tip 35b90184, sentinel sha256 recorded).
7. `.ufo/waves/round-28/final/quote-check.out:9` = "seat quotes 34 not-verbatim 8; gate quotes 34
   not-verbatim 0" — exact match to the lesson's appended correction.
8. **DANGLING — see Finding V1.**
9. `w1/out/ScribeShonenBox2/evidence.md` ✓; `.ufo/waves/round-17/runs/controls-frozen.json` ✓;
   SHONEN.md worktree diff is exactly 1 line changed, box `[~]` at line 7 unchanged ✓.

## Findings

**V1 (medium) — repairs row 8 cites an absent document.** Evidence cell is "report §Work
performed", but no round-29 report exists in the tree: `.ufo/reports/` contains only `round-5`;
`.ufo/waves/round-29/final/` holds only c1 receipts (`c1-513eba3b.{json,out}`,
`c1-513eba3b-cleanenv.{json,out}`); lane-wide grep "Work performed" hits only
`.ufo/reports/round-5/kama.md`. The substance does exist in a wave-1 seat artifact
(`.ufo/waves/round-29/w1/advice/ScribeDepthCriterion.md:5`: "post-data declared-bounds projection
20/20 (target 18, met true)"), so the L1 can satisfy row 8 by landing the report or re-pointing
the evidence; today the pointer does not resolve.

**V2 (low) — lesson commit times are +2 s off git metadata.** Lesson: freeze "(10:55:45Z)", data
"(12:02:54Z)". Git: 827d1365 author 09:55:34Z, committer 10:55:43Z; 513eba3b author=committer
12:02:52Z (`git log -1 --format='%aI %cI'`, clone). No repo artifact carries :45/:54 (grep over
`.ufo/waves/round-29/` + LOG.md; only `controls/SUMMARY.md:4` repeats 10:55:45Z). Already found
for the freeze by w1 `CriticPredicateIdentity` (`w1/out/CriticPredicateIdentity/findings.md:95`:
"the immutable commit metadata says 10:55:43Z"). Order unaffected; recommend L1 quote `%cI` values
or name the offset source.

**V3 (low) — wave-1 dispatch seconds wrong.** Lesson §Claims 3: "dispatched 12:02:5xZ";
`w1/dispatched-at.txt` = `2026-10-23T12:02:03.361941+00:00` (also CriticPredicateIdentity's
timing evidence: call 12:02:03.361941Z). Should read ~12:02:03Z. Chronology dispatch → data commit
(12:02:52Z) still holds.

**V4 (low) — mutant count mismatch in Mistakes row 1.** Lesson: "MutateTimeCheck's 3 surviving
mutants … are killed by the added 7-second case (`mined/survivor-recheck.out`)"; the cited receipt
records 2 mutants ("mutant no-plain-space … (killed)", "mutant no-seconds … (killed)"; `grep -c
'^mutant'` = 2) and the lesson's own parenthetical names 2 forms. Either a third mutant line is
missing from the receipt or the prose count is wrong.

**Nits.** (a) `w1/out/ScribeSrcPrettyFormats/quote.txt` location note says placeholder "`#ct`"
(should be `%ct`); the lesson Gate row and SOURCES S177 both say `%ct` correctly — artifact-internal
typo only. (b) S177's queued→mined flip and used-by rewrite are asserted by the lesson but not
independently verifiable (untracked working-tree file, no history); current end state matches the
claim.

## Residual risk / verification gaps
- I verified lesson-vs-repo consistency, not upstream git-scm.com pages (saved `page.html`
  fingerprints were not re-fetched; S177's quote was confirmed against the scribe's saved page
  only, since no local pretty-formats man page exists).
- SCORECARD row-level correctness (11 correction rows' contents) and the ConfirmM01–M11 hand-check
  verdicts are other seats' slices; I verified only the counter-level counts.
- Scratch clone kept at `/tmp/kama-r29-w2-verifylesson-4` (no lane writes anywhere).
