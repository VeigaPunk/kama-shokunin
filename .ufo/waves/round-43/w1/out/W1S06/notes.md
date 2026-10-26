# W1S06 notes — round-43 C1 registry rows (round-41 counters)

Facts I could not verify, or verified only in a qualified form. Everything else in
`rows.md` is backed by committed bytes at `895793e0`, by a command output recorded in
the report, or by the counter source line cited in the report.

1. **No committed receipt exercises the frozen counter blobs.**
   The pinned digests are of `tools/round41-pinwatch-audit.py` at `895793e0`
   (`4ca5ddee1b42…`) and `tools/round41-scorecard-reconcile.py` (`eff934a27b3e…`).
   The receipts I cite were produced by earlier blobs (`93e28440ce29…` and
   `1134768434db…`, tips `24aa1d34` and `4fe239a4`). Between those blobs and the
   frozen blobs the diff is exactly 2 files, 10 insertions, 0 deletions
   (`atexit`/`shutil`/`signal` imports plus the export-cleanup and SIGTERM lines,
   marked "round 42"). So the observed exit behaviour and summary lines carry over,
   but the frozen blob itself has no replay receipt. I did not run either counter.

2. **The round-41 "base" receipts were produced by counters that do not exist at
   their recorded tip.** `git cat-file -e 8893b894:tools/round41-pinwatch-audit.py`
   (and the scorecard counterpart) fails. The base lines therefore describe the
   state of revision `8893b894`, not a counter revision; the rows say "at tip
   8893b894" without implying the tool was committed there.

3. **The round-43 C1 base receipt records a tip that resolves nowhere I can read.**
   `.ufo/waves/round-43/controls/base.c1.out:1` says
   `tip=4dc17978e184d5474f6b0ff3f3d9af608e06aac3`. `git cat-file -t` on it fails in
   the frozen clone and in the parked lane worktree. Its numbers are reproduced
   exactly from the prereg's base `6897ead5` (see report §F1), so I can vouch for the
   counts but not for the recorded revision.

4. **The frozen "base mismatches=42" is not the freeze tree's count.**
   At `895793e0` the same audit reads `unreg=19 … mismatches=45`, because the three
   round-43 counters joined the gate population and no row names them yet. I could
   not find any committed round-43 receipt that prints the gate/audit line at the
   freeze revision. Frozen artifacts: reported, not edited.

5. **Network legs unverified.** The pinwatch `live` leg recomputes the reference with
   its own `git ls-remote --tags` (source `:256-261`) and compares; the recorded
   `live-reference` line in `c2/after.out` names external tag state I did not
   re-fetch. Byte-replay of `seed=788600741` is likewise unverified by me.

6. **Exit-code arm stated from code reading, not observed.** Both counters can exit 1
   through an uncaught traceback: `subprocess.run([... "tar" ...], check=True)`
   (pinwatch `:214-215`, scorecard `:190-191`) and an uncaught 120 s
   `git ls-remote` timeout (pinwatch `:257-258`). No committed receipt shows that
   arm. My Exit-map cells state it as a code fact.

7. **Placement unverified by construction.** SKILL.md at `895793e0` ends at line 1375
   with the round-34 table, so there is no existing table for round-41 rows. I
   validated the rows inside a new `### Round-41 instrument registry rows` section
   with the standard five-column header. Where the section finally lands is L1's
   call; the gate only needs the row to sit in a table whose header matches, and the
   audit only needs a line that starts with `|` and has ≥5 cells.

8. **Trailing `exit=` lines in the receipts are harness lines.**
   `.ufo/waves/round-41/controls/build_controls.py:73` writes `exit={returncode}`.
   The counters themselves print `tip=` + summary + `detail:` lines only.

9. **Row text is a draft, not a landed edit.** No lane file was modified; the rows
   were exercised only in my own throwaway clone.
