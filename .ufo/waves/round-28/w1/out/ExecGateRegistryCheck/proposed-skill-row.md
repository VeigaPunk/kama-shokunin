# Proposed SKILL.md row for tools/gate-registry-check.py

Proposed by the round-28 ExecGateRegistryCheck seat; the L1 integrates. Cell
count matches the 5-column header of "## Local gate/probe registry".

| Counter registry check | gate: `python3 tools/gate-registry-check.py [--rev REV] [--repo DIR]` | 0 every tracked `.ufo/waves/round-*/count-*.py` is named in SKILL.md; 1 at least one is not named; 2 could not evaluate (not a git tree, bad revision, unreadable SKILL.md) | Round-28 evidence: at `4179301f` exits 1 naming `.ufo/waves/round-25/count-c2.py` and `.ufo/waves/round-27/count-c1.py`; a scratch clone with both paths appended exits 0 (`--rev HEAD`) and exits 1 again at the unpatched base revision | read-only `git ls-tree`, `git ls-files`, `git show`; none |

Integration notes:

- This row only registers the check. The round-27 counter still needs its own
  row for repair 3 (entry command, verdict map, self-test, pinned values).
  Source-read interface of `.ufo/waves/round-27/count-c1.py`
  (lines 601-603, 720-745): entry
  `python3 .ufo/waves/round-27/count-c1.py --out <receipt.json>`
  (`--lane`, `--repo` optional); exit 0 after a completed evaluation even when
  `met False` (the count is in stdout and the receipt), exit 2 on
  `could-not-evaluate`. It has no exit 1.
- The check is an occurrence test, not a table-row test: a path named anywhere
  in SKILL.md passes, and a row's columns are not inspected. Do not present it
  as grading row completeness.
- At lane tip 5ebe7b1 it already exits 1 because `.ufo/waves/round-28/count-c1.py`
  is tracked and unnamed; a landed round 28 without a row for that counter
  leaves the check red.
