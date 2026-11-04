# EX01PreReportGate — round 71, C1 (pre-report gate)

Seat: EX01PreReportGate, kama r71 w1, leaf (no subagents). Lane base `f3ee44f4`, freeze `b43e71a8`.
Built: `tools/pre-report-gate.py` (new file, 22 919 bytes, 523 lines, mode 755; committed by the L1 at
`e2b860c8`, worktree identical to HEAD). This report, `commands.txt` and the two `landing-commit-*`
receipts were written after that commit and are uncommitted for the next evidence commit.
No edits to `SKILL.md`, `SCORECARD.md`, `LOG.md` or `corpus/`; no git/jj mutation in the lane.

## 1. What landed

`tools/pre-report-gate.py` implements the frozen C1 predicate. The predicate sentence is embedded
verbatim in the module docstring and in the `PREDICATE` constant. Five arms, fixed order, cwd = `--repo`:

| arm | command run inside the gate |
|---|---|
| `selfdesc` | `python3 <tools>/round42-selfdesc-reconcile.py --repo <repo> --tip <tip>` |
| `newest-closure` | `python3 <tools>/round69-newest-closure-counter.py --repo <repo> --rev <tip> --since-round 63` |
| `receipt-audit` | `python3 <tools>/round68-receipt-pointer-audit.py --repo <repo> --rev <tip>` |
| `worktree-landing` | `python3 <tools>/round67-worktree-landing-check.py --repo <repo>` |
| `round-clean` | `git -C <repo> status --porcelain -uall -- .ufo/waves/round-<N>` |

`<tools>` = `<repo>/tools` by default, or `--tools-dir DIR` (fixture/selftest knob, documented in the
docstring). Each child gets stdout+stderr captured, a 600 s timeout, the caller environment (so TMPDIR
is honoured) and `PYTHONDONTWRITEBYTECODE=1` so the gate does not grow a `__pycache__` in the graded repo.
Default mode prints one `PRE_REPORT_ARM <name> exit=<e> ok|FAIL <detail>` per arm, then exactly
`PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>`; exit 0 iff `failed==0 and uncommitted==0`,
else 1. `--json` emits one JSON document whose `line` field is the same verdict string; exit 2 is
reserved for CLI misuse (missing `--round`, `--repo` not a directory, non-int `--round`) and an
unevaluable selftest fixture. Exit 3 is reserved for re-entry: a scored gate whose
`PRE_REPORT_GATE_DEPTH` is >= 1 prints one `PRE_REPORT_RECURSION depth=<d> refused ...` line and
spawns nothing, because a SCORECARD `run` fact that executes the scored gate recurses
gate -> selfdesc reconciler -> round-41 run-fact harness -> gate; `--selftest` stays allowed at any
depth so a run fact can cite it (see D4). `failed` counts failing arms (arm 5 included): the L1 control fixture
(four green instruments, 26 uncommitted) prints `failed=1 uncommitted=26`, as the claim requires.
`uncommitted` is the count of non-empty porcelain records; `-uall` expands untracked directories, so
the round-start `.ufo/waves/round-70` reads 26 files (14 plain-status entries), matching the freeze.

## 2. Receipts (all under `.ufo/waves/round-71/w1/EX01PreReportGate/`)

| receipt | run | verdict |
|---|---|---|
| `selftest.out` | `--selftest --work <S>/selftest` | `PRE_REPORT_SELFTEST pass=6 fail=0`, exit 0 |
| `selftest-tmpdir.out` | `TMPDIR=<S>/tmpdir --selftest` (no `--work`) | pass=6 fail=0, TMPDIR honoured, tempdir removed |
| `round-start-lane-tree.out` | reconstructed `f3ee44f4` tree + 26 inherited files, `--round 70` | `failed=3 uncommitted=26`, exit 1 |
| `control-fixture.out` | `/fast/scratch/hyaku/kama-r71/l1/control-fixture/fixture`, `--round 70` | `failed=1 uncommitted=26`, exit 1 |
| `green-clone.out` | clone of the control fixture, 26 files committed (rebuild head `dac57377`), `--round 70` | `failed=0 uncommitted=0`, exit 0 |
| `json-and-defaults.out` | `--json`; and `cd clone; python3 <lane>/tools/pre-report-gate.py --round 70` | JSON, exit 0; defaults green |
| `cli-failclosed.out` | missing `--round`; nonexistent `--repo`; non-int `--round` | exit 2 / 2 / 2 |
| `before-tool-absent.out` | `python3 tools/pre-report-gate.py ...` in the `f3ee44f4` tree | exit 2, `No such file or directory` |
| `lane-head-live.out` | live lane at `b43e71a8`, `--round 70` | `failed=3 uncommitted=0`, exit 1 (see §4) |
| `round-71-parameter.out` | live lane, `--round 71` | `round=71 ... failed=4 uncommitted=102`, exit 1 |
| `registry-population.out` | `gate-registry-check.py` CLI + population regex | see §3 D2/D3 |
| `recursion-guard.out` | `PRE_REPORT_GATE_DEPTH=1` scored run, then selftest | exit 3 refused / pass=6 exit 0 |
| `scorecard-live-facts.out` | live SCORECARD run-fact + coverage extraction | see §3 D4/D5 |
| `coverage-count-snapshot.out` | pinned coverage glob + live row | 40 = 40 at snapshot |
| `landing-commit-check.out` | HEAD `e2b860c8` SCORECARD facts + coverage | closure re-anchored; 1 scored-gate run fact; 79→80 fix in worktree |
| `landing-commit-gate.out` | lane at `e2b860c8`, `--round 71` | `failed=4 uncommitted=3`, exit 1 (see §4) |

Key exact outputs (first occurrence line of each receipt is the `$` command):

```
# round-start tree (before state re-derived): exit 1
PRE_REPORT_ARM selfdesc exit=1 FAIL ... mismatches=1 met=False
PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=round-69 newest=round-70
PRE_REPORT_ARM worktree-landing exit=0 ok WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 ...
PRE_REPORT_ARM round-clean exit=0 FAIL files=26 first= M .ufo/waves/round-70/w1/out/CRT01ClaimC2.md
PRE_REPORT round=70 arms=5 failed=3 uncommitted=26
# L1 shortcut fixture af6eb6c2 (four instruments green, 26 uncommitted): exit 1
PRE_REPORT_ARM round-clean exit=0 FAIL files=26 first=?? .ufo/waves/round-70/measured/after/worktree-landing-final.out
PRE_REPORT round=70 arms=5 failed=1 uncommitted=26
# fully-green clone (26 files committed on top of af6eb6c2): exit 0
PRE_REPORT round=70 arms=5 failed=0 uncommitted=0
EXIT=0
```

The selftest drives the same `evaluate()` entry point over six fixtures covering all four frozen kill
rules: green; one uncommitted wave file (`round-clean`, `uncommitted=1`); red newest-closure stub
(`STALE_CALIBRATION`); deleted `PROVINCE.md` (`| MISSING PROVINCE.md`); byte-changed `SCORECARD.md`
and CRLF-translated `SKILL.md` (both `| DIRTY ...`). Arms (d)-(f) run the **real**
`round67-worktree-landing-check.py`; only arms 1-3 are stubs, so the landing detections are real.
A fixture that cannot be built or whose toplevel assertion fails is a could-not-evaluate (exit 2).

## 3. Frozen-claim disagreements (reported, freeze not edited)

**D1 — C1 counter's `--round` disagrees with its after-line.** The freeze's counter uses `--round 70`
while its after line says `PRE_REPORT round=71 ...`; the tool prints the N it is given, so `--round 70`
grades the inherited `.ufo/waves/round-70` and prints `round=70`, while `--round 71` grades this wave's
dir and prints `round=71`. Both are green at the tip only after the calibration row is re-anchored to
the round-70 closure (now done at `e2b860c8`). The L1 must record which N the counter uses.

**D2 — the populations command does not run.** `gate-registry-check.py --repo . --mode worktree` exits 2
(`unrecognized arguments: --mode worktree`); its options are `--repo`, `--rev`, `--selftest`, and
omitting `--rev` already means "worktree". Valid: `--repo .` → `registered 79 unregistered 0 defective 0`
(the "before" 79 reproduces).

**D3 — 79 → 82 is unreachable with the three frozen tool names.** The registry population regex is
`^(?:\.ufo/waves/round-[^/]+/count-[^/]+|tools/round[0-9]+-[A-Za-z0-9._-]+)\.py$`.
`tools/pre-report-gate.py` → False, `tools/census-waiver-boundary.py` → False,
`tools/round71-province-host-claims.py` → True. Committing all three yields `registered 80`, not 82
(and only the province tool needs a registry row for this gate to stay clean). The freeze row is
drifted relative to the instrument; flagging, not repairing. The live worktree's population-effects
line now reads `79 → 80` with this same explanation, so the repair is in flight.

**D4 — the landed calibration row cited the scored gate as an executed run fact (recursion).** The L1
integration commit `e2b860c8` carries `run \`python3 tools/pre-report-gate.py --repo . --round 71 --tip
master\` → \`PRE_REPORT ...\` (exit 0)` in the `## Axes` calibration row (`landing-commit-check.out`;
`b43e71a8` had no such fact). r41's `run_fact` executes that command with `bash -c` (300 s timeout) in
a tip clone, so the chain is gate -> selfdesc reconciler -> r41 -> gate with no base case: arm 1 can
never be green while the row exists, and each level spawns a clone plus four instruments. Hardening
landed in the tool: `_run` increments `PRE_REPORT_GATE_DEPTH` for every child and a scored invocation
at depth >= 1 prints `PRE_REPORT_RECURSION depth=<d> refused ...` and exits 3 before spawning anything
(`recursion-guard.out`); `--selftest` stays allowed at any depth. The tip run shows the guard firing
and r41 naming it: `r41 calibration run ... exit 3 != 0`, no clone storm (`landing-commit-gate.out`).
Bounded but still red: cite `--selftest` -> `PRE_REPORT_SELFTEST pass=6 fail=0` as the run fact, or
cite the after-receipt (the live worktree now does the latter) -- never the scored gate.

**D5 — coverage count (relayed from SCR01; live snapshot recorded).** The worktree row declares `40`
and the pinned glob prints `40`, while HEAD `b43e71a8` declared `39` with no knowledge entry — each
self-consistent because r41 runs the fact in a tip clone. Entry and cell must land together
(`coverage-count-snapshot.out`); the cell is still in flight.

## 4. Live-lane snapshot (context, not a claim receipt)

The live lane was graded mid-wave at `b43e71a8`: `failed=3 uncommitted=0`, exit 1 -- `round-clean`
green (the freeze landed the 26 inherited files) but `worktree-landing` `dirty=4 ... | DIRTY
SCORECARD.md`, because four declared paths were being edited by sibling seats (`M PROVINCE.md`,
`M SCORECARD.md`, `M SKILL.md`, `M corpus/SOURCES.md`; `lane-head-live.out`). That is the wave in
flight, not a defect. The isolated runs in §2 are authoritative. A `--round 71` snapshot printed
`round=71 ... failed=4 uncommitted=102`; both counts move every minute.

At the L1 integration tip `e2b860c8` the gate prints `failed=4 uncommitted=3`, exit 1
(`landing-commit-gate.out`): arm 1 the D4 recursion; arm 2 green (the calibration row now names the
round-70 closure); arm 3 `unresolved=3` -- three forward-referenced after receipts do not exist at
the tip (`.ufo/waves/round-71/measured/after/{pre-report-at-tip,boundary-at-tip,province-claims-at-tip}.out`,
exact lines in the receipt); arm 4 DIRTY SCORECARD.md from the in-flight repair
(`landing-commit-check.out` shows the re-anchored row and the 79->80 explanation); arm 5 3 files = this
report, `commands.txt`, `landing-commit-check.out` -- this seat's own uncommitted evidence, not a wave
defect. The forward references are existence checks in BOTH instruments (receipt audit; r41 grades a
cited path fact as `dead path` at the tip), so produce the three after receipts and commit them with
the SCORECARD: the first generation run is necessarily pre-commit, then re-run and overwrite.

Root cause of the tip's selfdesc red (and of census member `round42-selfdesc-reconcile selftest`): the
reconciler CLI at `e2b860c8` reports `mismatches=2` with two detail lines — `r41 depth sha256 SKILL.md
cited 0b61e118... observed aa61f109...` (the SKILL edit landed in the same commit but the depth row sha
was not re-derived) and the scored run fact (`exit 1 != 0`). The reconciler selftest's `ok` arm then
reads 2 (expects 0) and reports `pass=4 fail=1`; its stale arms still satisfy `m == ok_m+1`, so
`stale_incl` is not the defect and the instrument must not be edited: re-derive the depth sha last
(the worktree SKILL now hashes `e19708d2...`) and drop the executed run fact
(`reconciler-baseline-diagnosis.out`).

## 5. For the L1 to paste

Registry row (L1 adds it; five columns, same shape as the round-69 row at SKILL.md:1721):

```
| Round-71 pre-report gate | measurement: `python3 tools/pre-report-gate.py --repo DIR --round N --tip REV` (five arms, cwd = repo: `tools/round42-selfdesc-reconcile.py --repo DIR --tip REV`; `tools/round69-newest-closure-counter.py --repo DIR --rev REV --since-round 63`; `tools/round68-receipt-pointer-audit.py --repo DIR --rev REV`; `tools/round67-worktree-landing-check.py --repo DIR`; then `git -C DIR status --porcelain -uall -- .ufo/waves/round-N`; defaults repo `.`, tip `master`; `--json`; `--tools-dir DIR` selects the instrument directory; `--selftest` builds throwaway fixtures under `--work` or a fresh TMPDIR directory) | 0 iff the four instruments all exit 0 AND the round worktree is clean (`PRE_REPORT round=N arms=5 failed=0 uncommitted=0`); 1 naming every failed arm (`PRE_REPORT_ARM <name> exit=<e> ok|FAIL <detail>`); 2 CLI misuse (missing `--round`, `--repo` not a directory) or an unevaluable selftest fixture | selftest: six arms -- green, one uncommitted wave file, red newest-closure stub, missing declared path, byte-dirty declared path, CRLF-translated declared path -- prints `PRE_REPORT_SELFTEST pass=6 fail=0`; pinned: `arms=5`, `failed` counts failing arms including arm 5 (four green instruments + 26 uncommitted prints `failed=1 uncommitted=26`), `uncommitted` counts `-uall` porcelain records | writes nothing in the graded repo (`PYTHONDONTWRITEBYTECODE=1` for children); fixtures only under `--work`/TMPDIR |
```

Counter runs at the report tip (both forms recorded because of D1):

```
$ python3 tools/pre-report-gate.py --repo . --round 70 --tip master; echo EXIT=$?
PRE_REPORT round=70 arms=5 failed=0 uncommitted=0
EXIT=0
$ python3 tools/pre-report-gate.py --repo . --round 71 --tip master; echo EXIT=$?
PRE_REPORT round=71 arms=5 failed=0 uncommitted=0
EXIT=0
```

Selftest (also the run-fact citation):
`python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=6 fail=0` (exit 0).

Preconditions for the green after-line, owned by the L1: (i) SCORECARD.md `## Axes` calibration row
names `corpus/lessons/round-70-verifier-spotcheck.md` as the latest outside closure (both red arms 1-2
are exactly this pointer); (ii) every file under `.ufo/waves/round-71/` is committed (including this
seat's `EX01PreReportGate.md` and receipt directory) if the counter uses `--round 71`; (iii) the
declared self-record set is byte-clean at the report tip; (iv) the calibration row's executed run
fact must not be the scored gate — cite
`run \`python3 tools/pre-report-gate.py --selftest\` → \`PRE_REPORT_SELFTEST pass=6 fail=0\` (exit 0)`
(D4); (v) the coverage cell and `corpus/knowledge/pre-report-gate.md` land together (D5).

## 6. Not verified / limits

- The report-tip green state (§5) is not reachable during the editing wave; the isolated green clone is
  the only exit-0 receipt produced here.
- No host endpoint, credential, session or serving process was touched; all child runs are local git
  plumbing and Python. No tool was installed or upgraded (nothing was needed).
- `--json` on a red run was not recorded (green JSON shape is in `json-and-defaults.out`).
- The frozen D1-D5 items are reported as observed drift; no claim text was changed.
- The recursion guard was verified directly (`recursion-guard.out`), not as a selftest arm, so the
  pinned `pass=6 fail=0` count stays as the seat specified. All receipts were regenerated against the
  final 523-line/22 919-byte tool after the guard landed.
- Post-integration state: `e2b860c8` carries the tool and 14 receipts; uncommitted for the next
  evidence commit are this report, `commands.txt`, the two `landing-commit-*` receipts, the
  SCORECARD/SKILL repair set and `corpus/knowledge/pre-report-gate.md` (tool sha re-pinned to the
  working bytes `07cfc04f...`, guard described).
- Scratch `/fast/scratch/hyaku/kama-r71/EX01PreReportGate/` (selftest tree, two clone fixtures) was
  deleted on exit; every kept receipt is in this directory. The L1 control fixture was only read, and
  its post-run uncommitted count is unchanged (26); the green clone stayed at 0.
