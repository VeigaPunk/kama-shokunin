# W1S08 notes - unverified facts and limits for the three round-43 registry rows

Rows delivered in `rows.md` (one per line, order C1, C2, C3). Everything asserted in
a row was read from the blob at `895793e0b4c56bdcb939277b8ff0251b26306d4d` or from a
committed receipt; the following could not be verified and is therefore absent from
or softened in the rows.

1. **No measured line exists yet.** `.ufo/waves/round-43/preregistration.json` has
   `"measured_commit": null` for C1, C2 and C3, and `git ls-tree -r 895793e -- .ufo/waves/round-43/`
   lists only `controls/base.c{1,2,3}.out`, `controls/freeze.c{1,2,3}.out` and the
   `junk-*` controls. No frozen path for a measured receipt exists anywhere, so each
   row cites the base receipt only and says the measured line is "the same counter's
   summary at the measured commit". Naming an invented measured path would have
   created a `missing-path:` defect in `tools/gate-registry-check.py` and would be
   unverifiable today.

2. **Base/freeze receipt `tip=` is an object the lane remote does not hold.** All six
   receipts record `tip=4dc17978e184d5474f6b0ff3f3d9af608e06aac3`; `git -C
   /fast/scratch/kama-r43/clone cat-file -t 4dc17978...` prints
   `fatal: git cat-file: could not get object info`. By construction it is the
   throwaway clone commit made by `.ufo/waves/round-43/controls/build_controls.py`
   (`fresh()` clones at `--base` 6897ead5, `commit(d)`, `finally: shutil.rmtree(d)`).
   I could not independently verify that tip, and because the commit timestamp is
   not pinned the hash is not reproducible by re-running the builder either. What I
   could verify: `controls/base.cN.out` and `controls/freeze.cN.out` are byte-identical
   pairs (sha256 7c0847ce929afb34... c1, 74cf93220dbcfc05... c2, 02c2577ff3bbc155... c3),
   and their summary lines are the ones quoted in the rows.

3. **Exit 2 and the SIGTERM/143 path were never exercised.** Every committed receipt
   for the three counters ends `exit=1` (appended by `build_controls.py`). Codes 2 and
   143 in the rows are read from source
   (`tools/round43-registry-audit.py:236,243,88`;
   `tools/round43-hexrun-audit.py:406,414,93`;
   `tools/round43-health-audit.py:301,309,98`), not from a run.

4. **C2 contract/live/hygiene legs were never exercised.** `tools/hexrun-census.py`
   does not exist at the freeze commit (`git cat-file -e` fails), so `controls/base.c2.out`
   reads `tool=0 contract=0 live=0 hygiene=0 capability=0`. The row's description of the
   twelve fixtures (eleven dir cases + one git repo), the empty-private-TMPDIR hygiene
   check and the printed seed comes from `tools/round43-hexrun-audit.py:80-81,275-369,401`,
   not from an observed fixture run. The 73-row base census
   (`.ufo/waves/round-43/c2/base-unresolved.tsv`) was verified: 74 lines = header + 73
   data rows, length histogram 64x40, 7x32, 1x39, 1x65, matching the claim text.

5. **C3 rows/entry/gate legs have no object to read at the freeze commit.** `corpus/knowledge/runtime-health-surface-processes.md`,
   `corpus/lessons/round-43.md`, `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`,
   `.ufo/waves/round-43/c3/vllm-pr-58552.json` and `.ufo/waves/round-43/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice}`
   are all absent at `895793e` (`git cat-file -e` on each fails), which is why the row
   avoids naming them. `refetch=1 census=1` at base come from `controls/base.c3.out`;
   I did not re-run the live `gh api`/`curl` leg or the census leg. The census leg
   shells out to a host-absolute fleet-root path (finding F2 in the report), so
   `census=1` is host-dependent.

6. **Pin durability.** The `sha256` pins in the rows are the counter blobs at
   `895793e` (`git show 895793e:<path> | sha256sum` = 683c72c0de4b..., a455ba5522d5...,
   aa293a2519a0...). `tools/round43-registry-audit.py` recomputes them against the blob
   at the evaluated tip, so any later edit to a counter invalidates its row. I verified
   the pins clear at a tree that carries the counters unchanged (finding evidence in the
   report), but I did not verify that the landed tip keeps these blobs byte-identical.

7. **Row mechanics verified, one carried assumption.** On a seat clone at the freeze
   commit with these three rows appended under a five-column header,
   `tools/gate-registry-check.py --repo <clone>` prints
   `registered 15 unregistered 16 defective 0` (exit 1, the 16 pre-existing
   round-35..42 counters) and `tools/round43-registry-audit.py` prints
   `unreg=16 defect=0 flags=2 pins=16 ...` - i.e. the two `flags` mismatches are the
   pre-existing round-27/30 rows and the remaining 16 pins are the unregistered
   counters, none of them mine. Receipt: `verification-c1-counter.out` in this
   directory (its `tip=` is that throwaway seat commit, not a lane commit).
   Assumption not testable here: the rows will be inserted under a five-column table
   whose header satisfies `tools/gate-registry-check.py:registry_rows`; a different
   table shape would leave the three counters unregistered.
