# W1S07 notes — facts not verified (round 43, C1 registry rows)

Seat: W1S07. Rows delivered in `rows.md`. Everything below is a limit of this seat's
evidence, not an inference.

1. **Counter exit codes are source-derived, not observed.** I did not execute
   `tools/round42-capacity-audit.py`, `tools/round42-digest-audit.py` or
   `tools/round42-selfdesc-reconcile.py`. The capacity counter shells out to the
   fleet-root `sources-census.sh` and the digest counter runs the round-41 counters and
   re-hashes host files; running them is the C1 executor's evidence, not this seat's.
   Every exit-map clause in `rows.md` cites a line in the frozen source instead.
2. **Pinned prefixes are verified at the freeze commit only.** `sha256` prefixes
   `964f12e0f99e`, `c064ddb2050e`, `9736923ec308` were computed from the blobs at
   `895793e0b4c56bdcb939277b8ff0251b26306d4d` and are byte-identical at the lane clone's
   HEAD `1af8d5163163d8cf413887123d7b09beb14c6b75`. The landing tip is unknown; any edit
   to the counters after the freeze breaks the round-43 `pins` leg.
3. **The digest counter's `live` leg needs four host files** (the b11755 release archive,
   its `libllama-server-impl.so`, the shokuknow staged package, the round-35 Dockerfile
   fetch, per its docstring). I did not stat those host paths, so `external_ok >= 4` is
   unverified here; the rows do not name them because they are not repo-relative paths.
4. **The capacity counter's `census` leg depends on a file outside the evaluated repo**:
   `CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"`
   (`tools/round42-capacity-audit.py:76`). The file exists (35466 bytes, mtime 2026-10-19)
   but I did not run it, so the exit semantics of its `validate` mode are inherited from the
   counter's code (`legs["census"] = int(p.returncode == 0)`), not observed.
5. **The round-43 `selftest` / `dc` / `spot` / `hidden` legs are out of scope here.** I did
   not run `tools/gate-registry-check.py --selftest`, so `GATE_SELFTEST pass=N fail=0` is
   not claimed and not checked by this seat.
6. **Rows were validated by replaying the graders' own regexes, not through a landed
   commit.** The evidence is `gate-baseline-at-freeze.out` and `gate-with-rows.out` (gate
   runs on my own seat clone, working-tree mode) plus a replay of
   `tools/round43-registry-audit.py`'s `FLAG_RE`/`ADD_RE`/`SHA_RE` and its `cells[1]`,
   `cells[2]`, `cells[3]` tests against `rows.md` — all three rows pass `flags` and `pins`.
   I did not run the round-43 counter itself (it needs a commit-ish tip and runs the gate's
   selftest clone).
7. **Receipt `exit=` lines are harness wrappers, not counter output.** No counter prints an
   `exit=` line (`main()` prints only `tip=`/summary/`detail:` lines and returns the code).
   The trailing `exit=N` in `base.c1.out:43`, `base.c2.out:7`, `base.c3.out:16` and the
   measured receipts was appended by the round-42 runner. The rows therefore cite the
   summary lines as receipt content and derive exit codes from source.
8. **Collateral registration is real and was measured, not guessed.** Naming
   `tools/round41-scorecard-reconcile.py` / `tools/round41-pinwatch-audit.py` inside a row
   registers them (population regex `tools/round<N>-*.py`), which hands them to the
   round-43 `flags` leg; `round41-scorecard-reconcile.py` declares no `--seed`
   (`tools/round41-scorecard-reconcile.py:221-223`), so the digest row's `--seed` would be a
   mismatch for it. Measured: with full paths the gate printed
   `registered 17 unregistered 14 defective 0`; with bare filenames it prints
   `registered 15 unregistered 16 defective 0` (baseline `registered 12 unregistered 19`).
   The rows use bare filenames so this seat's delta is exactly +3 registered / -3
   unregistered.
9. **Insertion mechanics not applied to any lane file.** `rows.md` holds the three rows
   only. They are rows of a five-column table and must be appended under the header
   `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`
   plus a separator line. `SKILL.md` at the freeze ends at line 1375 with the round-34 rows
   (`SKILL.md:1364`); no round-35..round-43 registry section exists, so the natural
   insertion point is after `SKILL.md:1374`.
10. **Observation, not my write.** The read-only lane clone
    `/fast/scratch/kama-r43/clone` carries two untracked files
    (`corpus/knowledge/runtime-health-surface-processes.md`, `corpus/lessons/round-43.md`)
    that predate this seat; I wrote nothing inside it (only `git show`, `git cat-file`,
    `git rev-parse`, `git ls-tree`, `git status`).
