# W1S04 notes — facts not verified

Scope: three SKILL.md registry rows for tools/round38-{coverage,operability,statement}-audit.py at
freeze 895793e0b4c56bdcb939277b8ff0251b26306d4d. Everything below is a fact I could NOT establish from
committed bytes, or a limit of the evidence I did establish.

1. Receipt provenance. `.ufo/waves/round-38/{c1,c2,c3}/after.out` and
   `.ufo/waves/round-38/controls/{c1-noop,c2-base,c3-base}.out` contain only the measurement line (plus
   the optional `new ids:`/`note:` line). They record no argv, evaluated revision, timestamp, exit code or
   counter digest. I therefore cannot verify from the files themselves that they were produced by the
   freeze blobs, or against which tip each was run.

2. Receipt exit codes are inferred, not recorded. No `.exit` sidecar exists in
   `.ufo/waves/round-38/` or its `controls/`. The "exit 1" on the three controls comes from the
   preregistration text (`.ufo/waves/round-38/preregistration.json`, `do_nothing_control` per claim) and is
   consistent with `return 0 if met else 1`; the "exit 0" on the measured after.out files follows only from
   `met True` plus the same return statement. I did not execute the counters to observe exits.

3. Unprinted legs. `tools/round38-coverage-audit.py` computes `files_absent_base` (:123) and `entry_new`
   (:126-140) and folds five conjuncts into `met` (:142-148) but prints only `named`, `files_exist`,
   `cited_new`, `met` (:161-164). The
   receipts therefore cannot show those two legs separately; I verified only that the code checks them and
   that the measured line's `met True` implies all five conjuncts held in that run.

4. Control tip for `c1-noop.out`. Whether the C1 do-nothing control was run at base 2a4a97dc or at the data
   tip with the correction row absent is not recorded; the preregistration calls it a do-nothing control
   only. The row says "do-nothing control", not "base run".

5. Whether the three round-38 counters were repaired between the round-38 freeze (41e149ce) and the
   round-43 freeze blob. The counter docstring (lines 19-27) and `corpus/lessons/round-38.md` ("Instrument
   repair (C2, wave 1)") state the C2 repair happened before data and that `PREDICATE` was unchanged; the
   blobs I pinned are the ones at 895793e0, and they are byte-identical at the clone tip
   1af8d516. I did not verify the repair commit's own history claim (no `git log -S` comparison was run).

6. Predicate wording. `tools/round38-coverage-audit.py:41-48` `PREDICATE` spells the two artifacts as
   `knowledge/...`, while `ENTRIES` at :49-51 spells them `corpus/knowledge/...` (and the round-38
   preregistration uses the `knowledge/` spelling). The lesson documents the `knowledge/`-at-root lookup as
   the repaired defect. I could not decide from committed bytes alone which spelling the frozen predicate
   "meant"; the rows avoid restating it.

7. Statical reading only. I did not run `tools/round38-*.py`, `--help`, or any git write. Every value in the
   rows is either a committed receipt line, a hash of a committed blob, or a code path read at
   895793e0b4c56bdcb939277b8ff0251b26306d4d. The gate and the round-43 flags/pins simulation in the report
   were run in my own throwaway clone, never in `/fast/scratch/kama-r43/clone`.
