# EX04GateArm — C1 wiring: pre-report gate arm 6 → `tools/round73-round-scope-cases.py`

Scope: one lane file, `tools/pre-report-gate.py`, plus this report directory. The round-73
module, `tools/round72-round-scope.py`, `SKILL.md` and `plans/round-73-claims.md` were not
edited. No tool installs. No frozen-plan disagreement: the wiring matches C1's "wiring"
sentence (arm 6 calls this module; the gate's verdict stays
`PRE_REPORT round=<N> arms=6 failed=<f> uncommitted=<u>`; the arm name does not change).

Evidence base: `git -C L rev-parse master` =
`bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (read at every receipt write). The gate and the
module are uncommitted at that rev, so each receipt also pins the tested bytes:

- `tools/pre-report-gate.py` sha256 `59842d4604a2d0b85db428b7b79a6758ca0dd1ffdbdc651a31a53bfbd94893e9`
- `tools/round73-round-scope-cases.py` sha256 `65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577`

## 1. What changed — one file, `tools/pre-report-gate.py` (+126/−34)

| element | before | after |
|---|---|---|
| `ARM_SPECS[4]` (`round-scope`) | `round72-round-scope.py --repo {repo} --round {round} --tip {tip}` | `round73-round-scope-cases.py --repo {repo} --round {round} --tip {tip}` |
| `VERDICT_RE["round-scope"]` | `ROUND_SCOPE ` | `ROUND_SCOPE_V2 ` |
| `_detail()` | first `DIRTY/MISSING/UNTRACKED/UNREADABLE` appended for `worktree-landing` only | same, plus the first `ROUND_SCOPE_V2_FINDING` appended for `round-scope` (`SCOPE_FINDING_RE`, `_DEFECT_ARMS`) |
| docstring | five-arm / round-72 text | six-case arm-5 paragraph, six-script wiring, selftest arms (a)–(l), receipts line |

Arm name `round-scope` and `ARM_ORDER` are unchanged (arm 5 = first instrument after the
four older ones, arm 6 = built-in wave-dir cleanliness).

Unchanged on purpose (frozen): the gate's `PREDICATE` constant — the round-71 sentence as
amended in round 72 — and the verdict format. Round-73 C1 only re-points the arm; it does
not amend the gate's predicate. Historical measurements stay readable in the docstring:
`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` (five-arm round-71 receipt), "From round
72 on the gate prints `arms=6`", the round-72 control
`SCOPE_CONTROL cases=3 base_green=3 killed=0`, and the round-72 counter's own
`ROUND_SCOPE round=<N> cases=3 findings=<f>` (that module stays byte-frozen and its line is
never re-issued by this gate).

The appended-finding detail is a small addition beyond the minimum re-point: the arm failure
now names the case/path that broke it (e.g.
`ROUND_SCOPE_V2 round=70 cases=6 findings=1 | ROUND_SCOPE_V2_FINDING worktree <path> ...`)
instead of only the summary line. Verdict string, exit map and arm order are untouched.

## 2. Selftest fixtures updated (same file)

- The arm-6 stub is written as `<work>/tools/round73-round-scope-cases.py`; if `ARM_SPECS`
  still named the round-72 script, arm 5 would spawn-fail in the fixture and check (a) would
  go red. The stub prints `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` and, when red, one
  `ROUND_SCOPE_V2_FINDING worktree ...`.
- The stub checks its own argv against `<work>/tools/scope-expect.txt` (`70 master`), so an
  `ARM_SPECS` token regression (e.g. dropping `--tip`) turns the green fixture red instead of
  passing on argparse defaults.
- The fixture repo gains `plans/round-70-claims.md` (`# kama round 70 — frozen claims`), which
  the real counter's `label` case reads at the tip.
- New checks (i)–(l) run the **real** counter through the same arm-5 wiring:
  - (i) clean fixture → `arms=6 failed=0`, `ROUND_SCOPE_V2 round=70 cases=6 findings=0`;
  - (j) A5 survivor — `git worktree add --detach <work>/linked-worktree master` plus one
    uncommitted file → `arms=6 failed=1`, detail names `ROUND_SCOPE_V2_FINDING worktree`;
  - (k) A6 survivor — `.ufo/waves/round-71/scratch.log` ignored via `.git/info/exclude` (the
    primary worktree stays clean) → `arms=6 failed=1`, detail names
    `ROUND_SCOPE_V2_FINDING ignored-older-label`;
  - (l) selector probe: `_detail("round-scope", …)` must choose `ROUND_SCOPE_V2 ` over a later
    diagnostic line.
- The real module is now required: if it is absent the selftest prints
  `PRE_REPORT_SELFTEST could-not-evaluate …` and exits 2, never a pass. No A0 case occurred —
  the module appeared at 23:37 and stayed present for every run below.
- Existing arms (a)–(h) still assert `arms=6 failed=1` (red stub) and `arms=6 failed=0` (green
  stub) and stay green.

## 3. Commands run and observed output

Primary evidence commands (all with `PYTHONDONTWRITEBYTECODE=1`):

| # | command | observed |
|---|---|---|
| 1 | `git -C L rev-parse master` | `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` |
| 2 | `python3 -c "compile(open('tools/pre-report-gate.py').read(), …, 'exec')"` | `SYNTAX_OK` |
| 3 | `python3 tools/pre-report-gate.py --selftest` | 12 × `PASS`, `PRE_REPORT_SELFTEST pass=12 fail=0`, `# exit=0` → `selftest.out` |
| 4 | `python3 tools/pre-report-gate.py --repo <fixture>/repo --round 70 --tip master --tools-dir <fixture>/tools` (clean fixture) | `PRE_REPORT_ARM round-scope exit=0 ok ROUND_SCOPE_V2 round=70 cases=6 findings=0`; `PRE_REPORT round=70 arms=6 failed=0 uncommitted=0`; `# exit=0` → `arm-green.out` |
| 5 | same command, fixture with A5 dirt (`git worktree add --detach <S>/linked-cli master` + uncommitted `dirty.txt`) | `PRE_REPORT_ARM round-scope exit=1 FAIL ROUND_SCOPE_V2 round=70 cases=6 findings=1 \| ROUND_SCOPE_V2_FINDING worktree /fast/scratch/hyaku/kama-r73/EX04GateArm/linked-cli dirty.txt status=??`; `PRE_REPORT round=70 arms=6 failed=1 uncommitted=0`; `# exit=1` → `arm-red.out` |
| 6 | in-process mutation probe over the loaded gate module (no file written) | `ARM_SPECS[4] = ('round-scope', 'round73-round-scope-cases.py')`; old `ROUND_SCOPE ` regex ⇒ selected `later diagnostic line`, `killed: True`; reverted `ARM_SPECS` ⇒ `ROUND_SCOPE round=70 cases=3 findings=0`, `killed: True` → `mutant-probe.out` |
| 7 | `python3 tools/round72-round-scope.py --selftest` | `ROUND_SCOPE_SELFTEST pass=16 fail=0` (cross-check that the byte-frozen r72 counter still passes; it is not re-pointed by this gate) |

Selftest PASS labels in `selftest.out`, in order: `green`, `wave-uncommitted`,
`stale-newest-closure`, `missing-declared-path`, `dirty-declared-path`,
`crlf-declared-path`, `round-scope-red`, `round-scope-green`, `round-scope-v2-clean`,
`round-scope-v2-a5-red`, `round-scope-v2-a6-red`, `verdict-selector` (12 ≥ 8).

Scratch / exploratory runs (kept for honesty; not receipts):

- First selftest run with `--work $S/st-work --keep` produced the same
  `PRE_REPORT_SELFTEST pass=12 fail=0`; `$S/st-work2` (built by the second such run) is the
  fixture the two CLI receipts ran against. Both work dirs are deleted before yield.
- Lane status `git -C L status --porcelain -uall` showed my `M tools/pre-report-gate.py` plus
  other seats' edits (`M PROVINCE.md`, `M SKILL.md`, `M corpus/QUALITY.md`,
  `M corpus/README.md`, untracked receipts under `.ufo/waves/round-73/w1/`); I wrote none of
  those.
- `find .ufo/waves/round-73 -name __pycache__ -o -name '*.pyc'` printed nothing (the module
  and the gate both keep `__pycache__` out of the wave dir).
- The first version of the mutation-probe harness passed a 7-tuple where `ARM_SPECS` expects
  `(name, template)` and raised `ValueError: too many values to unpack (expected 2, got 7)`;
  it was corrected and re-run into `mutant-probe.out`. The gate file was not involved.

The scored gate was **not** run against the lane: that is the L1's pre-report run, and the
lane currently carries other seats' uncommitted work, so such a run would report their edits,
not this arm.

## 4. Receipts (all under `.ufo/waves/round-73/w1/EX04GateArm/`)

| file | first line | verdict line |
|---|---|---|
| `selftest.out` | `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec` | `PRE_REPORT_SELFTEST pass=12 fail=0`, `# exit=0` |
| `arm-green.out` | `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec` | `PRE_REPORT round=70 arms=6 failed=0 uncommitted=0`, `# exit=0` |
| `arm-red.out` | `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec` | `PRE_REPORT round=70 arms=6 failed=1 uncommitted=0`, `# exit=1`, finding `worktree` |
| `mutant-probe.out` | `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec` | both wiring mutants killed, `# exit=0` |

Each also carries `# gate_sha256=` and (except `arm-red.out`, which names its fixture instead)
`# scope_module_sha256=`, and the exact command line that produced it.

Reproduction of the two CLI receipts: run
`python3 tools/pre-report-gate.py --selftest --work <dir> --keep` (builds
`<dir>/repo` + `<dir>/tools` with the real module copied in), then
`python3 tools/pre-report-gate.py --repo <dir>/repo --round 70 --tip master --tools-dir <dir>/tools`
for the green arm; for the red arm add
`git -C <dir>/repo worktree add --detach <dir>/linked-cli master` and write any file inside
`<dir>/linked-cli` before running the same command, then
`git -C <dir>/repo worktree remove --force <dir>/linked-cli`.

## 5. Risks and limits

1. The gate's `--selftest` now hard-depends on `tools/round73-round-scope-cases.py` (exit 2
   if absent). Intentional: a stub-only selftest could pass while the instrument the gate
   actually ships with is missing — exactly the vacuity class C1 targets. Consequence: this
   gate's selftest cannot run in a checkout that lacks the round-73 module.
2. The receipt `rev` (`master`) does not pin the gate or module bytes because both are
   uncommitted at that rev; the `sha256` header lines do. If the L1 lands further edits
   before the record is cut, re-running the selftest is the discriminator.
3. `arm-red.out` and `arm-green.out` ran on a scratch fixture that is deleted before yield;
   the selftest receipt is the self-contained reproduction, and section 4 gives the two-step
   recipe.
4. The A6 fixture ignores its round-71 file through `.git/info/exclude` rather than a
   committed `.gitignore`; this exercises the same `--ignored` code path while keeping the
   primary worktree clean (a `.gitignore` would itself be a `stray` record).
5. The real module's own coverage (A7 `submodule.<name>.ignore=all`, uninitialised-submodule
   skip, exit-2 classes) is `EX01ScopeV2`'s; this seat only proves the gate reaches the module
   and surfaces its new-case findings. Mutation coverage of the module beyond the two wiring
   mutants is `MT01Mutants`' scope.

## 6. Files written

- `tools/pre-report-gate.py` (modified; the only lane file touched)
- `.ufo/waves/round-73/w1/EX04GateArm/selftest.out`
- `.ufo/waves/round-73/w1/EX04GateArm/arm-green.out`
- `.ufo/waves/round-73/w1/EX04GateArm/arm-red.out`
- `.ufo/waves/round-73/w1/EX04GateArm/mutant-probe.out`
- `.ufo/waves/round-73/w1/EX04GateArm.md` (this report)
