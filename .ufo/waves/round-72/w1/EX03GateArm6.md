# EX03GateArm6 — C1 integration: arm 5/6 `round-scope` in `tools/pre-report-gate.py`

Seat: EX03GateArm6, kama r72 w1, leaf (no subagents, no `ask`, no broadcast). Lane
`/home/vgpnk/Projects/shokunin/kama-shokunin`, `HEAD` == `master` ==
`a3cc39f08f4692e990921cf938d0269f6c25fc93` before and after every command below (asserted by
`git rev-parse HEAD` in `live-scored.out`). No git/jj mutation in the lane or anywhere else.
Read first, in full: `plans/round-72-claims.md` and `tools/pre-report-gate.py`.

## 1. What changed — `tools/pre-report-gate.py` only

New arm spec, verbatim:

```python
("round-scope", ("round72-round-scope.py", "--repo", "{repo}", "--round", "{round}",
                 "--tip", "{tip}")),
```

- `ARM_ORDER` is unchanged (`"ARM_ORDER = [name for name, _ in ARM_SPECS] + ["round-clean"]"`),
  so it is still derived from the specs; the six-arm order is self-consistent and the
  selftest asserts it on every case (`[a["name"] for a in result["arms"]] != ARM_ORDER`).
- `evaluate()` substitution extended: `token.replace("{repo}", repo_path).replace("{tip}", tip).replace("{round}", str(round_no))`.
- `VERDICT_RE["round-scope"] = r"ROUND_SCOPE "` (the trailing space keeps
  `ROUND_SCOPE_FINDING` from matching the verdict line).
- `PREDICATE` amended to `arms=6` and to the five reconciled instruments, the fifth being the
  round-scope counter. Module docstring amended in the same terms: arm list, `failed`/
  `uncommitted` accounting, output block, instrument wiring, selftest case list, receipts line.
- The historical five-arm receipt is preserved in the docstring as a round-71 measurement:

  > The round-71 receipt -- `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` -- is that
  > round's five-arm measurement and stays readable as one: five arms is the population round
  > 71 had. From round 72 on the gate prints `arms=6`; a five-arm line can only be a round-71
  > record.

- Sixth arm's meaning (docstring): it grades the round's own scope, not only its wave dir —
  `plans/round-<N>-claims.md` exists at `<tip>` with a first heading naming round `<N>`, no
  uncommitted path outside the declared record allow-list, no git-ignored path under
  `.ufo/waves/round-<N>/`; it prints `ROUND_SCOPE round=<N> cases=3 findings=<f>` and names
  each `ROUND_SCOPE_FINDING <case> <detail>`; the wave-dir porcelain check alone is vacuously
  green for a wrong `--round` label, for round work outside the wave dir, and for an ignored
  file inside it (cites the frozen before-measurement `SCOPE_CONTROL cases=3 base_green=3
  killed=0`, exit 1).
- Selftest fixture builder now writes a fourth stub `tools/round72-round-scope.py` into the
  fixture tools dir (inside the builder only — the lane's `tools/round72-round-scope.py` was
  not created or touched). The stub honours the existing `tools/red-arms.txt` mechanism and
  prints `ROUND_SCOPE round=<N> cases=3 findings=<0|1>`, plus one `ROUND_SCOPE_FINDING` line
  when red. `check()` gained an optional `render_has` assertion so the red case asserts the
  literal `round-scope exit=1 FAIL` status word, not just `ok=False`.

Measured on the bytes written: `sha256sum tools/pre-report-gate.py` →
`2c141b516fb8348d50db45b5934e4f4d1681aee46cfc6508924a0ee64727565c`; `wc -l` → `590`;
`git diff --stat -- tools/pre-report-gate.py` → `1 file changed, 98 insertions(+), 31 deletions(-)`.

## 2. Ordering: claim wording vs derived order (reported, freeze not edited)

`plans/round-72-claims.md` §C1 says "The arm enters the pre-report gate as arm 6
`round-scope`". With `ARM_ORDER` derived exactly as instructed (`<ARM_SPECS> + ["round-clean"]`),
`round-scope` executes **fifth** and `round-clean` **sixth**; the count and verdict string are
the frozen `arms=6`, and `round-scope` is the sixth arm the gate has ever had. The docstring
states this explicitly rather than mislabelling the list. If the L1 wants `round-scope`
literally in position 6, `round-clean` would have to move into `ARM_SPECS` (or `ARM_ORDER`
would have to stop being derived) — not done, because the seat brief pins the derivation.
This is a wording/ordinal disagreement only; nothing in the predicate, counter or kill rule
depends on it.

## 3. Selftest — run, observed

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tools/pre-report-gate.py --selftest --work /fast/scratch/hyaku/kama-r72/EX03GateArm6/work --keep
PRE_REPORT_SELFTEST_WORK /fast/scratch/hyaku/kama-r72/EX03GateArm6/work
...
  PRE_REPORT_ARM round-scope exit=1 FAIL ROUND_SCOPE round=70 cases=3 findings=1
  PRE_REPORT round=70 arms=6 failed=1 uncommitted=0
PASS round-scope-red
  PRE_REPORT_ARM round-scope exit=0 ok ROUND_SCOPE round=70 cases=3 findings=0
  PRE_REPORT round=70 arms=6 failed=0 uncommitted=0
PASS round-scope-green
PRE_REPORT_SELFTEST pass=8 fail=0
EXIT=0
```

All six pre-existing cases still pass (`green`, `wave-uncommitted`, `stale-newest-closure`,
`missing-declared-path`, `dirty-declared-path`, `crlf-declared-path`); each now renders
`arms=6`. Full 66-line transcript: `selftest.out`. The trailing `--keep` exists only to
permit §5; it does not change any assertion.

## 4. Live scored run — run, observed, not chased

```
$ git rev-parse HEAD
a3cc39f08f4692e990921cf938d0269f6c25fc93
$ ls tools/round72-round-scope.py
ls: cannot access 'tools/round72-round-scope.py': No such file or directory
$ python3 tools/pre-report-gate.py --repo . --round 72 --tip master
PRE_REPORT_ARM selfdesc exit=1 FAIL detail: closure_ptr: calibration row latest outside closure is round-70; newest at tip is round-71
PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=corpus/lessons/round-70-verifier-spotcheck.md newest=corpus/lessons/round-71-verifier-spotcheck.md newest_date=2026-11-03
PRE_REPORT_ARM receipt-audit exit=0 ok RECEIPT_POINTER_AUDIT files=2 cited=167 resolved=150 expanded=4 corrected=13 unresolved=0
PRE_REPORT_ARM worktree-landing exit=0 ok WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
PRE_REPORT_ARM round-scope exit=2 FAIL /usr/bin/python3: can't open file '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round72-round-scope.py': [Errno 2] No such file or directory
PRE_REPORT_ARM round-clean exit=0 FAIL files=17 first=?? .ufo/waves/round-72/measured/before/populations.out
PRE_REPORT round=72 arms=6 failed=4 uncommitted=17
EXIT=1
```

`HEAD` and the module's absence were re-checked after the run: unchanged. The two red
instruments are round-71 carry-over (closure pointer still names round-70 as the latest
outside closure; round-71's lesson is the newest file) and the 17 uncommitted round-72 wave
files are this round's in-flight work; the round-scope arm fails closed on the module EX01
owns, which is the correct six-arm behaviour before that module lands. No chasing, no edit
outside the assigned file. Full receipt incl. pre/post state: `live-scored.out`.

## 5. Stub red/green, invoked directly (same bytes the fixture injects)

```
$ cat tools/red-arms.txt
$ python3 tools/round72-round-scope.py --repo repo --round 70 --tip master
repo=repo round=70 tip=master
ROUND_SCOPE round=70 cases=3 findings=0
EXIT=0

$ printf "round-scope\n" > tools/red-arms.txt
$ python3 tools/round72-round-scope.py --repo repo --round 70 --tip master
repo=repo round=70 tip=master
ROUND_SCOPE round=70 cases=3 findings=1
ROUND_SCOPE_FINDING label plans/round-70-claims.md missing at master
EXIT=1
```

Receipt: `stub-red.out` (run inside the kept fixture work dir; that dir died with §8).

## 6. Files written (exact)

- `tools/pre-report-gate.py` (the only lane file edited; not committed)
- `.ufo/waves/round-72/w1/EX03GateArm6/selftest.out`
- `.ufo/waves/round-72/w1/EX03GateArm6/live-scored.out`
- `.ufo/waves/round-72/w1/EX03GateArm6/stub-red.out`
- `.ufo/waves/round-72/w1/EX03GateArm6.md` (this report)

Nothing else in the lane was created, modified or deleted; `git status --porcelain -uall --
tools/` lists only ` M tools/pre-report-gate.py`.

## 7. Risks and flags for the L1

1. **Stale current-tense registry rows (outside my write scope, not edited).**
   `SKILL.md:309` still says the gate has "five arms ... 0 iff all five arms green" and cites
   `PRE_REPORT_SELFTEST pass=6 fail=0`; it is now six arms and `pass=8 fail=0`.
   `SCORECARD.md:136` and `SCORECARD.md:3757` (capability `pre-report-gate`) still say "all
   five arms". `SCORECARD.md:3770` is a *historical* round-71 row whose `arms=5` stays correct
   as a round-71 measurement, but its "six selftest arms" is now eight.
2. **The five-arm historical line is only readable, not reproducible**: the gate no longer
   prints `arms=5` for any input, by design (§1). Any counter that greps `arms=5` as a
   *current* assertion would now fail; the round-71 receipts that contain it are unaffected.
3. **Live lane is red for four arms** for reasons owned elsewhere (EX01's module absent,
   closure-pointer lag, round-72 work uncommitted). This receipt must not be read as a gate
   defect.
4. **Not verified by me**: nothing beyond the two runs above — no build/lint/test suite exists
   for this tool, and post-integration gate execution belongs to the parent. I did not run the
   gate against a fixture where `round72-round-scope.py` exists but is *broken* mid-execution;
   the arm's fail-closed path there is covered only by the fixture's red stub (exit 1) and the
   live spawn failure (exit 2), both recorded.
5. **Disagreement recorded, freeze untouched**: §2.

## 8. Scratch

`/fast/scratch/hyaku/kama-r72/EX03GateArm6/` held the selftest fixture (`work/`, kept from §3
to capture §5) and was removed before yield; every receipt was copied into this directory
first. `tools/__pycache__` in the lane pre-dates this seat (newest `.pyc` 22:02:43 vs edits
22:44) and is gitignored; the gate sets `PYTHONDONTWRITEBYTECODE=1` for children and created
no `.pyc` of its own.
