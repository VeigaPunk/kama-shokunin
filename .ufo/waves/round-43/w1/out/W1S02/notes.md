# W1S02 notes — unverified facts and limits for the two round-36 registry rows

Rows delivered: `.ufo/waves/round-43/w1/out/W1S02/rows.md` (C2 coverage, then C1 statement).

## Observed (not merely read)
- Both counters' flags (`--repo`, `--tip`, `--selftest`) are the only flags their `add_argument` calls declare
  (`tools/round36-coverage-audit.py:98-100`, `tools/round36-statement-audit.py:231-233`).
- Exit 1 reproduced byte-for-byte at base `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`:
  `named 0 file_exists 0 cited_new 0 met False` and
  `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, each `exit=1`.
- Exit 0 reproduced at the landed claim commit `2e8beda5b2a2dcc62d6782838ee6e47cda04df55`:
  `named 1 file_exists 1 cited_new 1 met True` and
  `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`, each `exit=0`.
- `--selftest` at freeze `895793e0`: `SELFTEST base_met=False outside_met=False old_id_met=False pass=1`
  and `SELFTEST empty_met=False bad_met=False words=20 pass=1`, each `exit=0`; second lines match
  `controls/c2-base.out` and `controls/c1-noop.out` byte-for-byte.
- Exit 2 observed for both counters when `--tip` is omitted (argparse exits 2).
- `sha256 d2f8965b067f` / `sha256 886e4598269f` computed with
  `git show 895793e0…:<path> | sha256sum`.

## Limits / facts I did not verify
1. **Exit-2 `error: <exc>` text is read, not observed.** The only exit-2 path I exercised was the
   argparse usage error (prints usage, not `error:`); the `except Exception` branch
   (`tools/round36-coverage-audit.py:138-142`, `tools/round36-statement-audit.py:286-290`) was not triggered.
2. **An unreadable `--tip` exits 1, not 2** (observed with an all-zero oid: C2 `met False` exit 1,
   C1 `lesson_unchanged 0` exit 1). Both `git_show`/`git_blob` helpers swallow git failure, so the
   rows say "1 any leg fails" rather than "2 could not evaluate" for a missing revision.
3. **The C1 counter depends on a mutable repo outside `--repo`.** `FLEET` is hard-coded to
   `/home/vgpnk/Projects/shokunin` and `report_blob` is read at that repo's `HEAD`
   (`tools/round36-statement-audit.py:28,216,223`). Today that blob is `6d8f317378ba6048d8a3dfb4944adaf24f341eea`,
   equal to the pin, so the C1 row's `met True` line is reproducible now — but any fleet commit touching
   `.ufo/reports/round-35/kama.md` will flip C1 to `met False` without any lane change. Not a defect, a
   reproducibility limit stated in the row's Write scope.
4. **Base receipts carry no argv/revision header.** `controls/c2-base.out` and `controls/c1-noop.out` are
   one line each. Their identification as base-state output rests on `corpus/lessons/round-36.md:13`
   (both are named there as the do-nothing controls) and on my base replays reproducing their bytes exactly.
   I did not find a separate committed base run with a recorded command line.
5. **`round43-registry-audit.py` base figure.** `mismatches=42` is produced at `6897ead55c24ba08c9ac0b09466d4fbfe005a459`
   (`unreg=16 … pop=28 registered=12`), not at the freeze commit: at `895793e0…` the same counter prints
   `unreg=19 … pop=31 registered=12 mismatches=45` because the three round-43 counters are tracked and
   unregistered there. I did not verify which revision the claim's phrase "base mismatches=42" intends;
   only `6897ead5` yields 42.
6. **Row placement in SKILL.md is not verified as final.** I verified the two rows inside a registry table
   (a new `### Round-36 instrument registry rows` section appended after the round-34 table) in a
   throwaway clone; the L1 decides where they land.
7. **Fixture clone removed.** The verification commit `2039eeea3208e81375570e9c7f314878bf0be8c7` lived only in
   `/fast/scratch/kama-r43/seats/W1S02/clone`, which was removed after capturing the receipts. Rebuilding:
   clone the lane clone at `895793e0`, append `rows.md` under a five-column header, commit, then run
   `python3 tools/gate-registry-check.py --repo . --rev HEAD` and
   `python3 tools/round43-registry-audit.py --repo . --tip HEAD`.
