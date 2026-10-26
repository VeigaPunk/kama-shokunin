# W1S03 — facts I could not verify

1. **Row placement / heading.** `rows.md` holds the two bare table rows only. I did not
   insert them under a `### Round-37 instrument registry rows` heading with its own
   `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`
   header row, so the delivered bytes do not check that the heading text or a repeated
   header is accepted; I only checked that the rows themselves register. I appended the
   two rows verbatim to the tail of a seat clone's `SKILL.md` (no heading, no header row)
   and ran the lane gate in working-tree mode: `registered 14 unregistered 17 defective 0`
   versus `registered 12 unregistered 19 defective 0` at `895793e0`, with no
   `round37` line in either the unregistered or defective output
   (`/fast/scratch/kama-r43/seats/W1S03/gate-wt.out`, `gate-base.out`).
2. **Exit-2 arm of the statement counter for an unreadable out-of-repo input.** The
   counter reads `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` at
   `tools/round37-statement-audit.py:32,208` and the fleet round-36 report at
   `:222`. The `error: <exc>` / exit 2 path (`:285-290`) was read in source, not
   exercised: the staged append exists (196639 bytes) and the fleet HEAD blob is
   `8b7408e6…`, equal to `REPORT_BLOB` (`:31`), so the failure was not reproducible
   without moving files I am not allowed to touch.
3. **Receipt exit lines.** `.ufo/waves/round-37/c1/after.out`,
   `controls/c1-noop.out`, `c2/after.out` and `controls/c2-base.out` each carry an
   appended `…_exit=<n>` line that the counters themselves never print (they print only
   the summary line; `round37-statement-audit.py:281`, `round37-coverage-audit.py:163`).
   Those exit values are wrapper records; I re-observed the same codes by running both
   counters in a seat clone at `895793e0` (selftest 0/0, measured 0, usage 2).
4. **Base-arm receipts for the statement counter.** There is no committed
   base-revision receipt for `round37-statement-audit.py` other than the
   `--selftest` empty arm and the do-nothing control in `controls/c1-noop.out`
   (`uncorrected 4 … met False`, exit 1). I did not reconstruct a base-revision run at
   `6a4afdfe`; the row cites the control that exists.
5. **Claims themselves.** I did not verify the round-37 C1/C2 score transitions or the
   round-43 base-mismatch count of 42; I only confirmed that both counters reproduce
   their met lines at `895793e0` and that both are `unregistered` there.
6. **`defective 0` scope.** The gate reports defects across all registered rows, not
   per row; with my rows present the total was still `defective 0`, which covers my two
   rows only insofar as no defect line named them (none did). The gate exits 1 in both
   runs for the 17 other unregistered counters, so its exit code alone is not evidence
   about these two rows.
