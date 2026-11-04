# EX01PreReportGate — round 71, C1 (pre-report gate)

Seat: EX01PreReportGate, kama r71 w1, leaf (no subagents). Lane base `f3ee44f4`, freeze `b43e71a8`.
Built: `tools/pre-report-gate.py` (new file, 21 192 bytes, 481 lines, mode 755, untracked at HEAD — the L1 commits it).
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
unevaluable selftest fixture. `failed` counts failing arms (arm 5 included): the L1 control fixture
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
| `green-clone.out` | clone of the control fixture, 26 files committed (`6883d174`), `--round 70` | `failed=0 uncommitted=0`, exit 0 |
| `json-and-defaults.out` | `--json`; and `cd clone; python3 <lane>/tools/pre-report-gate.py --round 70` | JSON, exit 0; defaults green |
| `cli-failclosed.out` | missing `--round`; nonexistent `--repo`; non-int `--round` | exit 2 / 2 / 2 |
| `before-tool-absent.out` | `python3 tools/pre-report-gate.py ...` in the `f3ee44f4` tree | exit 2, `No such file or directory` |
| `lane-head-live.out` | live lane at `b43e71a8`, `--round 70` | `failed=3 uncommitted=0`, exit 1 (see §4) |
| `round-71-parameter.out` | live lane, `--round 71` | `round=71 ... failed=4 uncommitted=70`, exit 1 |
| `registry-population.out` | `gate-registry-check.py` CLI + population regex | see §3 D2/D3 |

Key exact outputs (first occurrence line of each receipt is the `$` command):

```
# round-start tree (the freeze's before state, re-derived): exit 1
PRE_REPORT_ARM selfdesc exit=1 FAIL detail: closure_ptr: calibration row latest outside closure is round-69; newest at tip is round-70
PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=corpus/lessons/round-69-verifier-spotcheck.md newest=corpus/lessons/round-70-verifier-spotcheck.md newest_date=2026-11-03
PRE_REPORT_ARM receipt-audit exit=0 ok RECEIPT_POINTER_AUDIT files=2 cited=157 resolved=140 expanded=4 corrected=13 unresolved=0
PRE_REPORT_ARM worktree-landing exit=0 ok WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
PRE_REPORT_ARM round-clean exit=0 FAIL files=26 first= M .ufo/waves/round-70/w1/out/CRT01ClaimC2.md
PRE_REPORT round=70 arms=5 failed=3 uncommitted=26
EXIT=1

# L1 shortcut fixture at af6eb6c2 (four instruments green, 26 uncommitted): exit 1
PRE_REPORT_ARM round-clean exit=0 FAIL files=26 first=?? .ufo/waves/round-70/measured/after/worktree-landing-final.out
PRE_REPORT round=70 arms=5 failed=1 uncommitted=26
EXIT=1

# fully-green clone (26 files committed on top of af6eb6c2): exit 0
PRE_REPORT_ARM round-clean exit=0 ok files=0
PRE_REPORT round=70 arms=5 failed=0 uncommitted=0
EXIT=0
```

The selftest exercises all four frozen kill rules plus the two extra seat arms, driving the same
`evaluate()` entry point the CLI uses: (a) green; (b) one uncommitted wave file → `round-clean` FAIL,
`uncommitted=1`; (c) red newest-closure stub → `newest-closure` FAIL, detail carries
`STALE_CALIBRATION`; (d) `PROVINCE.md` deleted → `worktree-landing` FAIL,
`WORKTREE_LANDING_CHECK ... missing=1 ... | MISSING PROVINCE.md`; (e) `SCORECARD.md` byte-changed →
`... | DIRTY SCORECARD.md`; (f) `SKILL.md` CRLF-translated (same lines) → `... | DIRTY SKILL.md`.
Arms (d)-(f) run a copy of the **real** `round67-worktree-landing-check.py`; only arms 1-3 are stubs,
so the landing detections are real instrument verdicts. A fixture that cannot be built or whose
toplevel assertion fails is a could-not-evaluate (exit 2), never a pass.

## 3. Frozen-claim disagreements (reported, freeze not edited)

**D1 — C1 counter's `--round` and its after-line disagree.** The freeze says
`Counter (same command before and after): python3 tools/pre-report-gate.py --repo . --round 70 --tip master`
but the after line says `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0`. The tool prints the `<N>`
it is given, so the after verdict is reachable by exactly one of those two readings:
`--round 70` prints `round=70` (grading the inherited, already-committed `.ufo/waves/round-70`), while
`--round 71` prints `round=71` (grading this wave's dir, which the report-tip evidence commit must
clear). Both are green at the report tip only after the SCORECARD calibration row is re-anchored to
the round-70 closure. The L1 must record which N the counter uses; this seat did not choose.

**D2 — the populations command does not run.** `python3 tools/gate-registry-check.py --repo . --mode worktree`
exits 2: `error: unrecognized arguments: --mode worktree`; the instrument's only options are
`--repo`, `--rev`, `--selftest`, and `--rev`-omitted already means "evaluate the worktree". Valid
command: `python3 tools/gate-registry-check.py --repo .` → `registered 79 unregistered 0 defective 0`,
exit 0 (the "before" 79 reproduces).

**D3 — 79 → 82 is unreachable with the three frozen tool names.** The registry population regex is
`^(?:\.ufo/waves/round-[^/]+/count-[^/]+|tools/round[0-9]+-[A-Za-z0-9._-]+)\.py$`.
`tools/pre-report-gate.py` → False, `tools/census-waiver-boundary.py` → False,
`tools/round71-province-host-claims.py` → True. Committing all three yields `registered 80`, not 82
(and only the province tool needs a registry row for this gate to stay clean). The freeze row is
drifted relative to the instrument; flagging, not repairing.

## 4. Live-lane snapshot (context, not a claim receipt)

The live lane was graded mid-wave at `b43e71a8`: `failed=3 uncommitted=0`, exit 1. `round-clean` was
green (the freeze landed the 26 inherited files), but `worktree-landing` reported
`dirty=3 ... | DIRTY SCORECARD.md` because three declared paths were being edited by sibling seats at
that moment (`M PROVINCE.md`, `M SCORECARD.md`, `M corpus/SOURCES.md` in the porcelain snapshot inside
`lane-head-live.out`). That is the wave in flight, not a defect: the landing arm is doing exactly its
job. The authoritative receipts are the three isolated runs in §2. A `--round 71` snapshot on the same
live tree printed `PRE_REPORT round=71 arms=5 failed=4 uncommitted=70` (70 wave files uncommitted at
that instant), proving `--round N` reaches `.ufo/waves/round-<N>`.

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

Also paste:

```
$ python3 tools/pre-report-gate.py --selftest; echo EXIT=$?
PRE_REPORT_SELFTEST pass=6 fail=0
EXIT=0
```

Preconditions for the green after-line, owned by the L1: (i) SCORECARD.md `## Axes` calibration row
names `corpus/lessons/round-70-verifier-spotcheck.md` as the latest outside closure (both red arms 1-2
are exactly this pointer); (ii) every file under `.ufo/waves/round-71/` is committed (including this
seat's `EX01PreReportGate.md` and receipt directory) if the counter uses `--round 71`; (iii) the
declared self-record set is byte-clean at the report tip.

## 6. Not verified / limits

- The report-tip green state (§5) is not reachable during the editing wave; the isolated green clone is
  the only exit-0 receipt produced here.
- No host endpoint, credential, session or serving process was touched; all child runs are local git
  plumbing and Python. No tool was installed or upgraded (nothing was needed).
- `--json` on a red run was not recorded (green JSON shape is in `json-and-defaults.out`).
- The frozen D1-D3 items are reported as observed drift; no claim text was changed.
- Scratch `/fast/scratch/hyaku/kama-r71/EX01PreReportGate/` (selftest tree, two clone fixtures) was
  deleted on exit; every kept receipt is in this directory. The L1 control fixture was only read, and
  its post-run uncommitted count is unchanged (26); the green clone stayed at 0.
