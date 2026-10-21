VERDICT: confirm - all five selftests exit 0 on a clean commit 37bd4c5b, with an empty porcelain before and after. 76 is the count for gate blob fe53e789 (7229fa95, 5b108c1a) and 77 for blob e90be78d (f1790e2 through 37bd4c5b).

## Deliverables (`.ufo/waves/round-20/build/out/SelftestsAtCommit/`, sha256)
- `final-selftests-37bd4c5b.txt` 0c719923…: the at-commit re-record (stdout, stderr, exit, wall time, blob per instrument, rev and porcelain before/after).
- `gate-selftest-by-rev.txt` a55e3540…: the gate selftest run in a detached worktree per revision. `gate-mutation-count.txt` 9ecd2a79…: static AST counts (its last line `exit=0` was appended by the invoking shell).
- Reusable scripts: `run-selftests-at-commit.sh` 82778843…, `gate-selftest-by-rev.sh` d141f484…, `count-gate-mutations.py` 863a233d… (stdlib, read-only `git show`).

## At-commit re-record (clone `/tmp/kama-r20-SelftestsAtCommit/lane`, since deleted)
`git clone -q` + `checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856` exit 0; `status --porcelain --ignored` 0 lines. The runner exited 0 (/usr/bin/python3 3.14.8, git 2.56.0, 07:26:00Z–07:26:03Z).

| command (python3 …) | blob | stdout | exit |
|---|---|---|---|
| `tests/llamacpp-live/check-receipt.py --selftest` | e90be78d | `selftest: 6 VALID and 1 NOT-EVALUATED receipts accepted; 77 mutations + unreadable case rejected` | 0 |
| `tests/llamacpp-live/install-tree-grid.py --selftest` | 5ebd9582 | `selftest: baseline, member rejection, absent member and bad receipt passed` | 0 |
| `tools/citation-provenance.py --selftest` | 9182e2c1 | `selftest: ok (15 cases)` (plus 1 stderr line; see Observations) | 0 |
| `tools/kama-llamacpp-live.py --selftest` | b9c5d023 | `selftest: ok; closed tcp6 listeners ::1:38019, ::ffff:127.0.0.1:45893` | 0 |
| `tools/sources-append-only.py --selftest` | cd26e6f7 | 41 `ok:` lines, then `42/42 selftest cases passed` | 0 |
| extra (the §C1 shape of the old file): `tools/citation-provenance.py` | 9182e2c1 | `required=4 docs_unreadable=0 found=4 verified=4 missing=0 mismatch=0 off_ref=0` | 0 |

`rev_after=37bd4c5b…`; `status --porcelain` after: 0 lines; `--ignored`: 0 lines. `git log 30ed378..37bd4c5 --` (all five instruments + `registry/required-citations.json`) prints nothing, so this tally also holds for 3389513f. At 028235e6 the gate, grid, live and sources blobs are identical; citation-provenance.py differs (bd3b31f3).

## 76 vs 77, settled
Static counts come from `count-gate-mutations.py <clone> 8bf99ca 7229fa9 5b108c1a f1790e2 028235e 3389513f 37bd4c5b` (exit 0). A first draft exited 1 because it flagged two runner loops as unresolved; the totals were identical. Dynamic counts come from `gate-selftest-by-rev.sh`: runner exit 0, every selftest exit 0, porcelain 0/0 per worktree.

| rev | gate blob | `grep -c 'mut('` | `mut(` call sites | static want==1 | printed mutations |
|---|---|---|---|---|---|
| 8bf99ca (r19 base) | 75ed7edb | 33 | 32 | 72 | 72 (5 VALID) |
| 7229fa95 | fe53e789 | 37 | 36 | 76 | 76 |
| 5b108c1a | fe53e789 | 37 | 36 | 76 | 76 |
| f1790e25 | e90be78d | 38 | 37 | 77 | 77 |
| 028235e6 | e90be78d | 38 | 37 | 77 | not run (same blob) |
| 3389513f / 37bd4c5b | e90be78d | 38 | 37 | 77 | 77 / 77 |

How 77 is made up: 37 `mut` + 13 `mut2` + 25 `mut3` (22 calls; one sits in a loop over a 4-tuple) + 2 `--require-schema` rejections in `cases.extend`. That gives 6 VALID and 1 NOT-EVALUATED. `git diff 5b108c1 f1790e2 -- check-receipt.py` adds 7 lines: the rule `bad("server.install_tree is empty")` and exactly one new case, `tree-empty-map-with-pin`.

Findings:
1. Fleet report `.ufo/reports/round-19/kama.md` (fleet ac9859f, sha256 925876f1…):
   - :91 "the gate's 76-mutation selftest" is correct for the commit its paragraph names (:87 "`7229fa95…`").
   - :112 "77 gate mutations" is correct for f1790e2..37bd4c5b, the final state.
   - Neither line names its blob. Proposed correction: "76 at blob fe53e789 (7229fa95/5b108c1a); 77 at blob e90be78d (f1790e2..37bd4c5b)".
2. `evidence/final-selftests.txt` (`measured_tree=working-tree-on-5b108c1a…`) printed 77, but committed 5b108c1a prints 76, so the bytes measured were not 5b108c1a's.
   - [INFERENCE] They were f1790e2's. `git show --stat f1790e2` shows that commit adds both the 77th case and final-selftests.txt itself (+10 lines), and its author time 03:41:27-03:00 equals 5b108c1a's.
   - Its §C1 `required=3` matches the registry row count at 7229fa9, 5b108c1 and f1790e2 (3, 3, 3); the count is 4 at 028235e and 37bd4c5.
3. Spot-check `corpus/lessons/round-19-verifier-spotcheck.md` (lane 37bd4c5):98 says "grew from 32 to 37 `mut(` cases (`grep -c` at base/tip)".
   - A literal `grep -c 'mut('` gives 33→38, because it also counts the `def mut(` line. 32→37 are the call sites (`grep -c 'mut("'`).
   - The printed mutation total went 72→77; `mut(` is only one of three helper families.

## Observations / risks
- The citation selftest only drives `check()` (lines 152-197). Its stderr line, `citation-provenance: cannot read /tmp/citation-provenance-…/lane/absent.md: [Errno 2] …`, is the expected diagnostic of the passing unreadable-doc case (:195), which asserts counts only. No case asserts the exit mapping in `main()` (:238-241). This is relevant to C1 "errors are not verdicts"; I read the code but did not run `main()` against it.
- The grid selftest passing says nothing about the C1 red cell (`install-tree-grid.py:110`, `code == 1`); that cell is out of scope here.
- This record binds 37bd4c5b bytes only. Any round-20 edit to these five files needs a new run: `run-selftests-at-commit.sh CLONE REV OUT`.

## Bounds and hygiene
- No tool installs or upgrades (none needed). No labrat spawned. `tools/kama-llamacpp-live.py` ran only in `--selftest` mode (no server: `main()` returns `_selftest()` before any launch code).
- After the runs: `pgrep -af` on the 5 tool names found none, and `ss -ltn` on 38019/45893 showed no listener. 0 selftest temp dirs were left in /tmp.
- Scratch removed (`ls` → "No such file or directory"). The lane was not modified: HEAD is still 37bd4c5b and the porcelain shows only `?? .ufo/waves/round-20/`.
- L1 next step: commit `final-selftests-37bd4c5b.txt` as the at-commit record. Append a correction (never rewrite) that points `evidence/final-selftests.txt` and report :91/:112 at the tables above.
