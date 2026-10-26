# W1S05 notes — facts I could not verify

Scope: two registry rows (round-40 C1 calibration, round-40 C2 operability). Everything
below was reachable only as stated; nothing else in the assignment was left unchecked.

1. **Lane remote vs. provided clone.** I never fetched `https://github.com/VeigaPunk/kama-shokunin.git`.
   All reads are against `/fast/scratch/kama-r43/clone` at `895793e0b4c56bdcb939277b8ff0251b26306d4d`.
   That the clone equals the remote at that commit is taken from the assignment, not re-verified.
2. **Round-40 `after.out` provenance.** `.ufo/waves/round-40/c1/after.out` and `c2/after.out` were
   produced by round 40 at tip `2429f48e2c679048d94566a9f3e800d5278b23eb` (SCORECARD.md:2196-2197).
   I reproduced byte-identical lines at `895793e0` but did not re-run at `2429f48e`.
3. **The `row[6]` correction is inference, not a run.** The frozen counter reads `s474[7]`. I verified
   the schema (SOURCES.md header, 11 columns; `row[6]` = `teaches` = "supersedes S472 — correct digest …
   5585f6027df2…e50f2"; `row[7]` = `status` = "mined") and I did **not** patch the frozen counter to
   prove the leg would flip to 1 — patching a frozen instrument is a finding, not a fix. The flip is
   `[INFERENCE]` from the parse.
4. **Row placement.** `rows.md` is unattached. I validated it inside a fixture that appends a new
   `### Round-40 instrument registry rows` section (5-column header + separator, copied from
   SKILL.md:1325-1327) at the end of SKILL.md. Any placement that keeps those two rows inside a
   five-column registry-format table registers the counters equally; L1 decides the final position.
5. **Five of the eight r43 C1 legs remain non-zero** across my fixture measurement
   (`selftest=1 dc=1 spot=1 hidden=2 flags=2`, plus 15 still-unregistered counters and
   `pop=31 < registered≥28`). Those legs belong to other seats; I did not touch them and cannot say
   whether round 43 will reach `mismatches=0`.
6. **`GATE_SELFTEST` in my fixture.** `selftest=1` in both the before and the after run
   (`GATE_SELFTEST pass=5 fail=1` vs. the documented `pass=6 fail=0`) is pre-existing at the freeze
   tree and unchanged by my rows; I did not investigate its cause.
7. **No tool installs.** Nothing was installed or upgraded; no `pacman` transaction was attempted.
8. **Fixture repos.** Two ephemeral fixture repos under `/fast/scratch/kama-r43/seats/` (one from
   `git archive` of the freeze tree, committed with `-c user.name=w1s05-fixture -c
   user.email=w1s05@fixture.invalid`; each verified with `git rev-parse --show-toplevel` before the
   first commit). No commit was made in the lane clone, the parked worktree, or the fleet repo.
