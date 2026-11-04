# EX01ScopeV2 — round 73 C1 build: round-scope v2 cases

Seat: EX01ScopeV2, executor, axes calibration (+ operability of the command).
Round: kama r73 w1. Claim: C1 (`plans/round-73-claims.md` §C1, frozen before any seat scored).
Observed lane revision while writing: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`
= `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (the freeze base is `6e961996`; later commits landed the
plan, controls and the other round-73 seats' files before this wave started). No freeze byte was edited.

## What I built

`tools/round73-round-scope-cases.py` (new, 1 file; sha256
`65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577`). It is the round-73 round-scope
counter: six cases, the three inherited r72 cases plus the three survivor classes, one summary line,
and a fixed exit map (`0` clean, `1` findings, `2` could-not-evaluate). `PREDICATE` is one line,
658 bytes, byte-equal to the plan's C1 blockquote minus its `>` marks and line breaks (checked
against `master:plans/round-73-claims.md`, not the working copy):

```
PREDICATE_EQUALS_PLAN=True len_constant=658 len_plan=658 one_line=True
CASE_ORDER=('label', 'stray', 'ignored', 'worktree', 'ignored-older-label', 'submodule')
```

CLI is exactly the assigned surface: `--repo` (default `.`), `--round` (required), `--tip` (default
`master`), `--allow` (repeatable, r72 validation), `--work`, `--selftest`, `--json`.

### Cases

| order | case | mechanism |
|---|---|---|
| 1 | `label` | inherited `_label_findings`: plan blob at `--tip`, first heading names round N |
| 2 | `stray` | inherited `_stray_findings`: primary `status --porcelain -uall`, paths minus `--allow` |
| 3 | `ignored` | inherited `_ignored_findings`: `!!` records under `.ufo/waves/round-<N>` |
| 4 | `worktree` | `git worktree list --porcelain`; every non-primary worktree runs its own `status --porcelain -uall`, each record graded like `stray` against `--allow`; an unreadable linked worktree is a finding naming it |
| 5 | `ignored-older-label` | every present `.ufo/waves/round-<M>` dir parsed from its name with `M >= N`, each probed with `status --porcelain -uall --ignored -- <dir>`; every `!!` record is a finding; `M < N` rounds are outside the population |
| 6 | `submodule` | every `.gitmodules` path whose directory exists runs its own `status --porcelain -uall` (every record a finding, named `<sub> <path> status=<s>`), plus the parent at `--ignore-submodules=none` (each record naming a configured submodule path is a finding `<sub> parent-record=<record> status=<s>`); an uninitialised submodule is named on a `ROUND_SCOPE_V2_SKIP submodule <path> reason=<no-worktree|not-initialised>` line |

Findings are printed as `ROUND_SCOPE_V2_FINDING <case> <detail>` sorted by case order then detail,
skips after findings, then the pinned `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` line (always the
last line). `--json` emits the same document fields (`repo`, `rev`, `cases`, `case_order`,
`findings`, `count`, `skipped`, `line`, `exit`).

### Inherited graders

The module loads `tools/round72-round-scope.py` with
`importlib.util.spec_from_file_location` (one lazy `_inherited()` loader) and calls
`_label_findings`, `_stray_findings`, `_ignored_findings`; it also reuses that module's helpers
(`resolve_repo`, `_git`, `_normalize_allow`, `_allowed`, `_record_paths`, `_finding`, `_one_line`)
so `--allow` validation and porcelain path decoding are the inherited code, not a copy. Nothing in
`tools/round72-round-scope.py` was edited: `git diff --quiet -- tools/round72-round-scope.py` exits
`0` and its sha256 is `45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4`, the same
hash the r72 attack recorded for the landed tool. The import is guarded with
`sys.dont_write_bytecode = True` so it never writes a `__pycache__` beside the inherited tool, and
internal subprocesses run with `PYTHONDONTWRITEBYTECODE=1`.

## Verification (every command below was run; receipts in `EX01ScopeV2/`)

All python runs used `PYTHONDONTWRITEBYTECODE=1`; no `__pycache__` exists under
`.ufo/waves/round-73` after the runs (`find .ufo/waves/round-73 -name '__pycache__' -o -name '*.pyc'`
prints nothing).

### Selftest — 26 arms, all pass (`selftest.out`)

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-round-scope-cases.py --selftest --repo . --work $S/st
...
ROUND_SCOPE_V2_SELFTEST pass=26 fail=0          # exit 0
```

Arms: `clean`; `label-missing` / `label-wrong-round` / `label-no-heading`; `stray-root`;
`stray-renamed`; `ignored-in-wave`; `allow-exact`; `allow-dir`; `subdir-repo`; `worktree-red`;
`worktree-allow`; `worktree-green`; `older-label-red` (round 71, `.ufo/waves/round-72/hidden.log`);
`older-label-green` (ignored `.ufo/waves/round-71/old.log` stays green at round 73);
`submodule-red` (modified tracked + untracked content); `submodule-green`; `submodule-ignore-all`;
`submodule-uninitialised-skip`; `tip-unresolvable`; `bad-allow`; `not-a-git-repo`; `cli-misuse`;
`json-roundtrip`; `predicate`; `shim-does-nothing`. The successful run removes its work dir.

The three survivors the shim arm builds are the same classes as the committed fixtures: linked
worktree dirt, a valid older-round label over ignored later work, `submodule.sub.ignore=all`.

### r72 selftest stays green (`selftest.out`, second command)

```
PYTHONDONTWRITEBYTECODE=1 python3 tools/round72-round-scope.py --selftest --repo . --work $S/rv72st
ROUND_SCOPE_SELFTEST pass=16 fail=0             # exit 0
```

### Committed survivor fixtures (`kill-a5.out`, `kill-a6.out`, `kill-a7.out`, `clean.out`)

```
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-73/controls/build-survivors.py --work $S/ctrl
FIXTURE c1_clean ...  FIXTURE c1_a5 ...  FIXTURE c1_a6e ...  FIXTURE c1_a7sub2 ...   # exit 0
```

```
python3 tools/round73-round-scope-cases.py --repo $S/ctrl/fixtures/c1_a5 --round 73 --tip master
ROUND_SCOPE_V2_FINDING worktree <c1_a5-wt> LOG.md status= M
ROUND_SCOPE_V2_FINDING worktree <c1_a5-wt> stray-in-wt.txt status=??
ROUND_SCOPE_V2 round=73 cases=6 findings=2      # exit 1
```

```
python3 tools/round73-round-scope-cases.py --repo $S/ctrl/fixtures/c1_a6e --round 71 --tip master
ROUND_SCOPE_V2_FINDING ignored-older-label .ufo/waves/round-72/hidden.log
ROUND_SCOPE_V2 round=71 cases=6 findings=1      # exit 1
```

```
python3 tools/round73-round-scope-cases.py --repo $S/ctrl/fixtures/c1_a7sub2 --round 73 --tip master
ROUND_SCOPE_V2_FINDING submodule sub child.txt status= M
ROUND_SCOPE_V2_FINDING submodule sub leak.txt status=??
ROUND_SCOPE_V2_FINDING submodule sub parent-record=M sub status= M
ROUND_SCOPE_V2 round=73 cases=6 findings=3      # exit 1
```

```
python3 tools/round73-round-scope-cases.py --repo $S/ctrl/fixtures/c1_clean --round 73 --tip master
ROUND_SCOPE_V2 round=73 cases=6 findings=0      # exit 0
```

Each survivor exits 1 naming its new case (`worktree`, `ignored-older-label`, `submodule`); the
clean reference exits 0. The do-nothing shim (a counter that only greps the plan heading at
`master`) accepts all three — shim exit 0 where the required verdict is 1 — so the fixture set
scores it red on all three; the v2 counter kills all three (`shim.out`):

```
# fixture=c1_a5     shim_exit=0 required=1 shim_verdict=RED   real_round73_exit=1 KILLED
# fixture=c1_a6e    shim_exit=0 required=1 shim_verdict=RED   real_round73_exit=1 KILLED
# fixture=c1_a7sub2 shim_exit=0 required=1 shim_verdict=RED   real_round73_exit=1 KILLED
# SHIM_SCORE red=3 real_killed=3 of=3
```

### Exit-2 surface

Observed inside the selftest: `--tip deadbeefdeadbeef` (unresolvable), `--allow /etc/passwd`
(absolute allow entry), a plain non-git directory, and `--repo ... --tip master` without `--round`
all return 2. `--round 0` independently returns 2 with
`ROUND_SCOPE_V2 could-not-evaluate round=0 (round must be >= 1)`.

### Live lane, informational only

`python3 tools/round73-round-scope-cases.py --repo . --round 73 --tip master` currently exits 1 with
55 `stray` findings. That is the mid-wave state of the shared lane (other seats' uncommitted wave
files plus `SKILL.md`, `PROVINCE.md`, `corpus/*` and `tools/pre-report-gate.py` edits by their
owners), not a defect in the counter: the same run reports the round-73 plan as present and the
`worktree`/`ignored-older-label`/`submodule` cases are clean on the lane. No live-lane pass is
claimed by this seat; the claim's green target is `c1_clean` plus the round's own record tip.

## Files written (exact)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round73-round-scope-cases.py` (new)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/kill-a5.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/kill-a6.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/kill-a7.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/clean.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2/shim.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/EX01ScopeV2.md` (this report)

Every `.out` receipt starts with `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec` and records the
exact `cd`/argv, captured stdout+stderr, and the observed exit for every block. Nothing under
`MANIFEST.json`, the fleet repo, `.ufo/state/`, `.ufo/watchdog.log`, sibling lanes,
`plans/round-73-claims.md`, `tools/round72-round-scope.py`, `tools/pre-report-gate.py` or `SKILL.md`
was written by this seat. No tool was installed or upgraded. Scratch
`/fast/scratch/hyaku/kama-r73/EX01ScopeV2` was used for all fixtures and removed after the receipts
were copied into the wave dir.

## Notes, risks, and hand-off

- **Gate wiring is EX04's file, not mine.** `tools/pre-report-gate.py` still invokes
  `tools/round72-round-scope.py` and its arm-line regex is `"round-scope": r"ROUND_SCOPE "`.
  The v2 module's summary line is `ROUND_SCOPE_V2 round=...`, which that space-anchored pattern does
  not match. EX04 must point arm 6 at this module and match the `ROUND_SCOPE_V2 ` prefix while
  keeping the arm name and the `PRE_REPORT round=<N> arms=6 failed=<f> uncommitted=<u>` verdict
  shape. I did not edit the gate or its selftest stubs (explicitly out of my scope).
- `ignored-older-label` deliberately includes `M == N`, so an ignored path under
  `.ufo/waves/round-<N>` is reported twice — once by inherited `ignored`, once by
  `ignored-older-label`. That is the frozen `M >= <N>` population read literally; the two case
  labels stay distinguishable and sorting is deterministic.
- An uninitialised submodule is named as skipped in two shapes: `reason=no-worktree` when the
  directory is absent, `reason=not-initialised` when the directory exists but `git -C <path>
  rev-parse --show-toplevel` fails (a plain clone leaves empty submodule directories). Neither is a
  pass and neither is graded content.
- The parent `--ignore-submodules=none` probe runs whenever `.gitmodules` declares at least one
  path (a declaration with no parent record can still be skipped and named); with no `.gitmodules`
  the submodule case is green without a redundant full-tree status.
- The `worktree` detail prefixes each record with that worktree's path; `--allow` matching uses the
  record path relative to that worktree, exactly like `stray`. An unreadable linked worktree
  (deleted/prunable path) is a finding, never a pass.
- No disagreement with the frozen claim was found; no freeze byte was edited. The only wrinkle is
  procedural for EX04 (line-prefix change), recorded above rather than patched here.
