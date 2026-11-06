# EX01HarmSweep — harm sweep, base B vs measured M (round 88)

## Scope

Read-only sweep of the lane's runnable tests at three revisions in one shared scratch clone
(`/fast/scratch/hyaku/kama-r88/EX01HarmSweep/wt`, detached checkout per rev, removed before yield):
B `9b4c7af16fdd4bba9e4815f4615f4b003f340747`, M `138a75437bcd11b72446087e970f5dfc5abf9ccd`, plus
T `f77d2ae9f2797a19e7548989fb9e64d8f9411d3f` (extra point). Checks: the two harm-conjunct suites,
the probe-verdicts selftest, the gate's 16 composed arm selftests (arms 9–14 at
`tools/pre-report-gate.py:91-114`), `census/live-reconcile/pin-watch` selftests, the gate's own
`--selftest`, and two targeted probes I wrote for the changed-but-ungraded branches. No lane file
written; no commit/pacman/tool install; nothing sent to 127.0.0.1:1234. Fixtures are lane-owned
loopback stubs on ephemeral ports, torn down per cell; `TMPDIR` and `--work` under scratch only.

## Commands and outputs (rc are the real ones)

`run-harm.sh <rev> <label>`: `git checkout --detach <rev>` in the scratch clone, then per check
`timeout 600` with `TMPDIR=<scratch>/tmp-<label>`. Legend: `n/n` = pass/fail the tool printed.

| # | Check | B | M | T | Delta |
|---|---|---|---|---|---|
| 1 | `tests/probe-verdicts/check.py` | e0 72/72 | e0 72/72 | e0 72/72 | same |
| 2 | `… check.py --selftest` | e0 5/5 | e0 5/5 | e0 5/5 | same |
| 3 | `bash tools/test-snapshot.sh` | e0 30/0 | e0 30/0 | e0 30/0 | same |
| 4 | `round79-unregistered-census.py --selftest` | e0 4/0 | e0 4/0 | e0 4/0 | same |
| 5 | `round78-live-reconcile.py --selftest` | e0 4/0 | e0 4/0 | e0 4/0 | same |
| 6 | `pin-watch.py selftest` | e0 9/0 | e0 9/0 | e0 9/0 | same |
| 7 | `round77-citation-baseline.py --selftest` | e0 7/0 | e0 7/0 | e0 7/0 | same |
| 8 | `round77-append-registers.py --selftest` | e0 7/0 | e0 7/0 | e0 7/0 | same |
| 9 | `round77-selfrecord-round76.py --selftest` | e0 4/0 | e0 4/0 | e0 4/0 | same |
| 10 | `round78-selfrecord-round77.py --selftest` | e0 8/0 | e0 8/0 | e0 8/0 | same |
| 11 | `round78-append-registers.py --selftest` | e0 7/0 | e0 7/0 | e0 7/0 | same |
| 12 | `round81-append-debt.py --selftest` | e0 34/0 | e0 34/0 | e0 34/0 | same |
| 13 | `round82-selfrecord-round81.py --selftest` | e0 23/0 | e0 23/0 | e0 23/0 | same |
| 14 | `round82-late-delta.py --selftest` | e0 13/0 | e0 13/0 | e0 13/0 | same |
| 15 | `round83-pending-falls.py --selftest` | e0 7/0 | e0 7/0 | e0 7/0 | same |
| 16 | `round83-pin-rechecks.py --selftest` | e0 14/0 | e0 14/0 | e0 14/0 | same |
| 17 | `round86-rendered-cells.py --selftest` | e0 17/0 | e0 17/0 | e0 17/0 | same |
| 18 | `round86-mutant-owners.py --selftest` | e0 13/0 | e0 13/0 | e0 13/0 | same |
| 19 | `round86-pin-origin.py --selftest` | e0 7/0 | e0 7/0 | e0 7/0 | same |
| 20 | `pre-report-gate.py --selftest --work <tmp>` | e0 43/0 | e0 43/0 | not run | same |

Tail lines verbatim in `out/*/<check>.out`; `out/harm-table.tsv` carries
`SUMMARY checks=20 changed=0`; `out/{base,measured,tip}/summary.tsv` are the machine-readable rows.
Worktree porcelain after every run: 0 lines (`out/*/worktree-dirty.txt`); no process of mine
survived (`pgrep -af kama-r88/EX01HarmSweep` → rc 1). Gate scored run not executed (L1 owns it).
Blob hashes B→M (`git ls-tree -r <rev>`): `check.py` `3e17c334…`, `test-snapshot.sh` `0e776313…`,
`pin-watch.py` `2272273e…`, `round78-live-reconcile.py` `74a0b3be…` all identical; `kama-probe.sh`
`74ce51b1…` → `f2dab797…` and `round79-unregistered-census.py` `1764552e…` → `07903e98…` changed.

**Pinned-model dependency per B run.** Both pinned paths are `$HOME`-rooted
(`round78-live-reconcile.py:43-44`); model present (1185376 B) and binary present (17864 B).
Rerun with `HOME=<scratch>/fakehome`, same result at B and M: #1 e0 72/72, #2 e0 5/5, #3 e0 30/0 —
model-independent; #5 **e1 0/4**, each arm `prerequisite absent: …/fakehome/.local/opt/llama-b11755/llama-server`.
So 19 of 20 checks are model-independent and only `round78-live-reconcile --selftest` needs the pinned
prerequisites; its 4/0 rides the present model, not the revision (`controls/r78-selftest-before.out`,
binary present + model absent, is `pass=0 fail=4`).

**Targeted branch probe** (`run-branch-probe.sh <rev> <label>`; 5 hermetic cells, one stub each:
`/v1/models` entry `stories260K` with `status.value` unloaded+failed / loading / loaded / sleeping,
plus a status-less single-model body; registry row declares the port):

| cell | B `check` | M `check` | M `listeners` | M `snapshot` 1st/2nd |
|---|---|---|---|---|
| unloaded+failed | e0 `MODEL_OK/matched` | e2 `MODEL_UNLOADED/router-unloaded-failed` | `MODEL_UNLOADED` `model_endpoints=1` | e2 / e2, no malformed warn |
| loading | e0 `MODEL_OK/matched` | e2 `MODEL_LOADING/router-loading` | `MODEL_LOADING` `model_endpoints=0` | e2 / e2 |
| loaded | e0 `MODEL_OK/matched` | e0 `MODEL_OK/matched` | `MODEL_OK` `model_endpoints=1` | e0 / e0 |
| sleeping | e0 `MODEL_OK/matched` | e2 `MODEL_UNLOADED/router-sleeping` | `MODEL_UNLOADED` `model_endpoints=1` | e2 / e2 |
| no `status` | e0 `MODEL_OK/matched` | e0 `MODEL_OK/matched` | `MODEL_OK` | e0 / e0 |

**Rollback probe.** Baseline row `probe-row MODEL_UNLOADED router-unloaded` replayed through the B and
M probe bytes (`git show <rev>:tools/kama-probe.sh`, closed port 9): B e2 prints
`dropping malformed baseline row for id='probe-row'` + `no usable baseline rows — rebaselining`;
M e2, no warning, `transitions=3`. Receipts `out/base/rollback-snap-b.out`, `out/measured/rollback-snap-m.out`.

## Findings

1. **NOTE — no harm conjunct regression.** All 20 checks equal in rc and tail line at B, M and T
   (`changed=0`, `out/harm-table.tsv`). No B-pass/M-fail exists, so nothing is BLOCKER on this axis.
2. **NOTE — the conjunct does run the changed bytes.** `check.py` drives
   `DEFAULT_PROBE = LANE/tools/kama-probe.sh` and `test-snapshot.sh` sets
   `PROBE=${KAMA_PROBE:-…/kama-probe.sh}`, so 72 + 30 cells exercise the M probe, not a Python
   reimplementation; both hold, i.e. the single-model path is undisturbed.
3. **DEFECT (coverage, not a regression) — neither harm suite can see inside the new router branch.**
   No fixture under `tests/probe-verdicts/` carries a router `status` object with `value`
   (`grep '"value"' tests/probe-verdicts/*.json` → no match), and `test-snapshot.sh` has 0 occurrences
   of `MODEL_UNLOADED`. The landed differences at `tools/kama-probe.sh:460-517` (router refine),
   `:609-613`, `:812`, `:844` (`listeners` bucket) and `:1060` (`diff_baseline` whitelist) are graded
   only by the 17-cell counter; my five-cell probe is the only independent observation of the
   `snapshot`/`listeners` halves. `controls/harm-base-*` would have stayed green through a total
   breakage of them.
4. **NOTE — M matches the frozen rule on all five probe cells** (unloaded→`MODEL_UNLOADED/…-failed`
   e2; loading→`MODEL_LOADING/router-loading` e2; sleeping→`MODEL_UNLOADED/router-sleeping` e2 without
   `-failed`; loaded and status-less→`MODEL_OK/matched` e0), while B is `MODEL_OK/matched` e0 on all
   five — the false green C1 targets, reproduced from base bytes (`out/base/branch-probe.txt` vs
   `out/measured/branch-probe.txt`). M's second `snapshot` run re-reads its own `MODEL_UNLOADED`
   baseline with no malformed warning, reaching `kama-probe.sh:1060` that no suite touches.
5. **NOTE — rollback asymmetry is loud, not silent.** A baseline written at M is dropped as malformed
   (warned, audited in `DELTA.md`, then rebaselined) by B's probe, so a downgrade costs one rebaseline;
   forward direction is clean.
6. **NOTE — `listeners` summary counts a loading router model as `model_endpoints=0`** while an
   unloaded one counts 1 (`out/measured/branch-*-listeners.json`), whereas the census consumer treats
   both alike (`tools/round79-unregistered-census.py:153`). The `MODEL_LOADING` exclusion predates M
   (`kama-probe.sh:844` at B lists only `MODEL_OK|MODEL_MISMATCH`): inherited, newly visible wording —
   one sentence belongs in `corpus/knowledge/router-mode-readiness.md`.
7. **NOTE — scratch hygiene.** One clone for all three revisions, detached checkouts, `rm -rf` of the
   scratch dir before yield (verified gone); no mutating git in lane/fleet/fixtures; no host service,
   sysctl or live endpoint touched; no tool installed or upgraded (no pacman/uv/npx), none needed.

## Deliverables

`.ufo/waves/round-88/w1/out/EX01HarmSweep/`: `harm-table.tsv`; drivers `run-harm.sh`,
`run-branch-probe.sh`; `base/`, `measured/`, `tip/` with per-rev `summary.tsv`, `head.txt`,
`checkout.out`, `worktree-dirty.txt`, one `.out` per check, `gate-selftest.out`, `*-nohome.out`
dependency reruns, `branch-probe.txt` + per-cell `branch-*-{check,listeners}.json`,
`branch-*-latest.tsv`, `branch-*-DELTA.md`, `snap{1,2}-*.out`; rollback receipts
`base/rollback-snap-b.out`, `measured/rollback-snap-m.out`.

VERDICT: holds — all 20 checks identical at B, M and T (no pass→fail anywhere); router verdicts propagate per the frozen rule and the pinned-model dependency is confined to `round78-live-reconcile --selftest`.
