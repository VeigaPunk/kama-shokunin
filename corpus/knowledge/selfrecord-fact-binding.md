source: S548 — kama round-76 self-record fact harness, `python3 tools/round76-selfrecord-facts.py`; own re-runnable instrument, receipts under `.ufo/waves/round-76/w1/EX02SelfrecordFacts/`. Revision semantics cited from the existing `gitrevisions` rows (S070/S082).
verified-at: 2026-11-04 — the harness ran at the round-76 base `b06cc612711560c53eef3ec21484c6963601262f` and printed `SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0`, exit 1 (`.ufo/waves/round-76/w1/EX02SelfrecordFacts/before.out`).
recheck: `python3 tools/round76-selfrecord-facts.py --repo .` — expect exit 0 and `mismatches=0` while the record is current; re-open the cited rows if the harness's fact list changes.

# A self-record fact is graded at the revision it names

## Rule

A number, digest or pointer a round files about its own work is a **claim about a
revision**. It is graded by re-deriving the value from the committed blob at the revision
the sentence names — `git show <rev>:<path>` — never from the worktree, never from memory,
never from the prose that surrounds it.

Two consequences the lane learned the hard way (round 75's population sentence filed
`PROVINCE.md` sha256 `0e8dc562…` for a blob that is `af459acf…` at the same revision;
`LOG.md` filed a work tip one commit behind the last non-record commit):

1. A fact that is not re-derived is a fact in name only. The filing writer's intent ("it is
   unchanged") is not evidence; the blob is.
2. A correction is a *new* entry, and it counts only when the value it states re-derives at
   the revision it names. A correction that restates the old sentence with softer wording
   leaves the mismatch in place, which is exactly what the harness grades.

## Why the revision, not the tip

A revision names an immutable object graph state; `<rev>:<path>` resolves to the exact blob
bytes that existed there (the `gitrevisions` rows S070/S082 hold that rule). A fact filed
about revision R must be graded at R even when the tip has moved: grading at the tip would
report the *later* work as the earlier round's error. The tip matters only for facts that
are stated about the tip.

## Boundary

This is a self-assessment instrument, not a truth oracle. It grades the eight declared
facts it knows how to derive; a fact outside that list is out of population, not "clean".
The harness never edits the record — it prints `SELFRECORD_FACT <id> filed=<v> derived=<v>`
and exits 1, and the round's writer files the correction.
