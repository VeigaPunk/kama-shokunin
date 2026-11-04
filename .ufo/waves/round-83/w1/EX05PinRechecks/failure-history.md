# EX05 intermediate failures (transcript excerpts, not replacement raw receipts)

The final receipts supersede these runs. Earlier output was overwritten during authoring;
these exact excerpts are retained from the observed tool transcript. No initial failure is
claimed green retrospectively. Final hashes and commands are in receipt-index.json.

1. Initial `python3 <seat>/round83-pin-rechecks.py --selftest`, exit 1:
   `PIN_RECHECK_SELFTEST pass=1 fail=10`.
   Findings were present, but the in-process harness always assigned exit=0.
   Fixed by deriving the harness exit from findings.
2. Repeated fixture-dump invocation, exit 1:
   `FileExistsError: [Errno 17] File exists: '/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/fixtures/green-fixture/extracts'`.
   Made fixture construction idempotent; ultimately removed the unnecessary dump CLI.
3. Initial lane run with strict ref equality, exit 1:
   `PIN_RECHECK rows=5 graded=3 holds=3 reworded=0 moved=0 drifted=0 ungraded=1 bad=1`.
   `PIN_RECHECK_FINDING ref-mismatch engine=llama.cpp ref=39febd2adb947b70da35e95f9351b3bf58ad170a pin extract header ref=39febd2a disagrees with the row's ref cell 39febd2adb947b70da35e95f9351b3bf58ad170a`.
   Implemented documented >=7-hex prefix agreement; tags still compare exactly.
4. Initial scratch-clone driver, exit 1:
   `AssertionError: rows not committed at tip`.
   The file existed only in the lane worktree at that instant. Final proof uses a fresh
   clone of a later committed tip, without copying uncommitted data.
5. Added attack regression initially had 13 cells; selftest exit 1:
   `PIN_RECHECK_SELFTEST_FAIL ungraded-with-extract exit=1 want=1 want_class=ungraded-with-extract findings=[('bad-row', 'engine=engone ref=b1 rows.tsv: 13 cells, want 12')]`.
   `PIN_RECHECK_SELFTEST pass=11 fail=1`.
   Removed the extra placeholder; final regression is red with its intended finding.
6. A subsequent clone driver copied into an already-present anchor directory, exit 1:
   `FileExistsError: [Errno 17] File exists: '/fast/scratch/hyaku/kama-r83/EX05PinRechecks/clone/corpus/anchors'`.
   Final proof uses the clone's committed anchors directly.
7. RV02 reported two escapes on an intermediate revision: laundering a documented ref as
   ungraded with erased extract cells; changing extract bytes plus a valid digest without
   committing. Final code uses an independent first-line HEAD anchor inventory and requires
   extract bytes to equal HEAD; both have named red regression arms.
8. MT01 reported its initial-draft baseline was red, its probes inconclusive, and its scratch
   already deleted when the ready revision arrived. No final independent MT01 pass is claimed.

No build, formatter, linter, scored pre-report gate, production edit, or lane commit was run.
