# Round 72 C1 attack — RVW01RoundScopeAttack

Axes: calibration (primary), operability (command/receipt reproducibility).

## Findings, by severity

### P2 — A7: repository-configured submodule hiding produces a green result with uncommitted content

`tools/round72-round-scope.py:252-264` invokes `git status --porcelain -uall` without overriding submodule ignore configuration. `evaluate()` at line 282 calls this worktree-local function; no recursive submodule scan is performed. In A7sub2, a committed `.gitmodules` entry `submodule.sub.ignore=all` hides both modified tracked `sub/child.txt` and untracked `sub/leak.txt`. The counter exits **0**, `ROUND_SCOPE round=72 cases=3 findings=0`. Explicitly inspecting the submodule prints ` M child.txt` and `?? leak.txt`; forcing parent `--ignore-submodules=none` prints ` M sub` (supplemental-commands.json). Default-config A7sub is killed, exit 1, findings=1. Thus ignore configuration changes the cleanliness verdict while the dirty payload remains. Route as a recursive-scope defect; no frozen kill fixture explicitly names submodules. Overriding submodule ignore configuration is the minimal parent-status mitigation; exhaustive nested-path naming needs separate consideration.

### P2 scope gap — A5: linked-worktree dirt is invisible from the primary checkout

The same status call at line 253 scans only the resolved `--repo` worktree. A5 primary is clean while a linked worktree of that repository has modified `LOG.md` and untracked `stray-in-wt.txt`. Primary invocation exits **0**, findings=0; pointing the identical counter at the linked worktree exits **1**, findings=2. This is a routed scope survivor, not proof that the narrower supplied-worktree predicate was violated. The frozen kill rule does not require enumerating linked worktrees. Route caller ownership/round-worktree binding rather than silently extending the freeze.

### P3 scope gap — A6: a valid older-round label hides another round's ignored work

A6e commits a valid round-71 claims plan and a fleet prompt for round 71, while actual ignored work is `.ufo/waves/round-72/hidden.log`. `--round 71` exits **0**, `ROUND_SCOPE round=71 cases=3 findings=0`; the same fixture with `--round 72` exits **1**, findings=1, naming the ignored path. `_label_findings()` at line 229 binds the supplied number to its plan; `_ignored_findings()` at line 267 scans only that number's wave dir. There is no caller-intended-round binding. This is a routed valid-label mismatch survivor, not a failure of the amended plan-existence predicate. Missing plans and mislabelled headings are killed. The frozen kill rule does not name an existing, valid older-round anchor.

## A1–A7 disposition and frozen-kill coverage

| Attack | Observed disposition | Does the frozen kill rule explicitly name this variant? |
|---|---|---|
| A1 staged new/index-only modification (`A `, `M `) | Killed: exit 1, findings=2 | Root uncommitted-file class is named; staged column variants are not individually enumerated. |
| A2 staged deletion (`D `) | Killed: exit 1, findings=1 | No deletion-specific fixture; broader uncommitted-path predicate covers it. |
| A3 space+newline names, staged/untracked | Killed: exit 1, findings=2; ignored variant exit 1, findings=1 | Root-stray/ignored classes named, special path bytes not named. Human details flatten whitespace; receipts preserve original porcelain in fixtures-meta.json. |
| A4 tracked receipt followed by committed ignore rule | Exit 0, findings=0; **not a demonstrated ignored-path defect** | No tracked-pattern variant. Plain `git check-ignore -v` exits 1; `--no-index` exits 0. Pattern matching alone does not make the indexed path git-ignored. No pass credit for this attempted attack. |
| A4b same rule plus untracked ignored payload | Killed: exit 1, findings=1, naming ghost.ign | Untracked ignored-path class is named. |
| A5 linked worktree | Survives from primary, exit 0; killed when pointed at linked worktree, exit 1 | No. Routed scope gap, not a pass. |
| A6 existing older-round anchor with other-round wave work | Survives with round 71, exit 0; killed with round 72, exit 1 | No. Missing plan and heading-mismatch variants are killed, exit 1. |
| A7 default submodule | Killed: exit 1, findings=1 | No submodule-specific fixture. |
| A7 submodule ignore=all | Survives: exit 0, findings=0 | No. Routed defect, not a pass. |
| A7 broad allow-list/boundary probes | Prefix-adjacent backup remains a finding: all four mixed probes exit 1; trailing-slash directory permission suppresses only its intended nested path | Allow-listed records are explicitly permitted. No boundary bypass demonstrated. Globs are literal, not supported patterns. |

Survivors: **A5 (0), A6 valid older label (0), A7 ignore=all (0)**. Killed: **A1 (1), A2 (1), A3 stray/ignored (1/1), A4b (1), A6 absent-plan/misheading (1/1), A7 default submodule (1), A7 boundary probes (all 1)**. A4's exit 0 is neutral semantic evidence, not a discovered leak and not a gate pass claim.

## Commands and observed verdicts

Every exact final tool/base-arm command, cwd, stdout, stderr and exit is in the corresponding `receipts/*.out`; summary.json carries all 27 final invocations. Supplemental-commands.json contains the A6 commit/proof commands and the decisive submodule status commands with their observed outputs. Build scripts preserve the complete parameterized setup commands and fixtures-meta.json preserves observed porcelain outputs. Final tests use a byte-for-byte snapshot of the landed tool, not edited tool logic.

| Invocation | exit | observed line | exact-command receipt |
|---|---:|---|---|
| `b0-seed-clean` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/b0-seed-clean.out` |
| `b0-seed-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/b0-seed-basearm.out` |
| `b0-round99-wronglabel` | 1 | `ROUND_SCOPE round=99 cases=3 findings=1` | `receipts/b0-round99-wronglabel.out` |
| `a1-staged-new` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a1-staged-new.out` |
| `a1-staged-new-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/a1-staged-new-basearm.out` |
| `a2-staged-delete` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a2-staged-delete.out` |
| `a2-staged-delete-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/a2-staged-delete-basearm.out` |
| `a3-space-newline-stray` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a3-space-newline-stray.out` |
| `a3i-space-newline-ignored` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a3i-space-newline-ignored.out` |
| `a4-tracked-ignored` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/a4-tracked-ignored.out` |
| `a4b-tracked+untracked-ignored` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a4b-tracked+untracked-ignored.out` |
| `a4-tracked-ignored-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/a4-tracked-ignored-basearm.out` |
| `a5-worktree-primary` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/a5-worktree-primary.out` |
| `a5-worktree-linked` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a5-worktree-linked.out` |
| `a5-worktree-primary-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/a5-worktree-primary-basearm.out` |
| `a6-prompt+plan-clean` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/a6-prompt+plan-clean.out` |
| `a6b-prompt-yes-plan-gone` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a6b-prompt-yes-plan-gone.out` |
| `a6c-plan-no-prompt` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/a6c-plan-no-prompt.out` |
| `a6d-plan-mislabelled-heading` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a6d-plan-mislabelled-heading.out` |
| `a6e-round71-wronglabel` | 0 | `ROUND_SCOPE round=71 cases=3 findings=0` | `receipts/a6e-round71-wronglabel.out` |
| `a7sub-submodule-default` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a7sub-submodule-default.out` |
| `a7sub2-submodule-ignore-all` | 0 | `ROUND_SCOPE round=72 cases=3 findings=0` | `receipts/a7sub2-submodule-ignore-all.out` |
| `a7allow-prefix-dir` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a7allow-prefix-dir.out` |
| `a7allow-prefix-dir-slash` | 1 | `ROUND_SCOPE round=72 cases=3 findings=1` | `receipts/a7allow-prefix-dir-slash.out` |
| `a7allow-glob-star` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a7allow-glob-star.out` |
| `a7allow-glob-starstar` | 1 | `ROUND_SCOPE round=72 cases=3 findings=2` | `receipts/a7allow-glob-starstar.out` |
| `a7sub2-submodule-ignore-all-basearm` | 0 | `(no ROUND_SCOPE line: base porcelain command)` | `receipts/a7sub2-submodule-ignore-all-basearm.out` |

Supplemental counter command: `python3 tested-round72-round-scope.py --repo <a6e> --round 72 --tip master` -> exit 1, `ROUND_SCOPE_FINDING ignored .ufo/waves/round-72/hidden.log`, `ROUND_SCOPE round=72 cases=3 findings=1` (full absolute argv in supplemental-commands.json).

### Execution history and corrections

- Initial reconnaissance shell commands listed lane tools/waves, created the seat scratch directory and ran `git --version` -> git 2.56.0, SCRATCH_OK. Read-only lane commands `git rev-parse master`, `git status --porcelain -uall`, status count -> master a3cc39f08f4692e990921cf938d0269f6c25fc93, 15 status records at observation time. `cat` read freeze.txt and the old control: `SCOPE_CONTROL base_rev=d30a8696 cases=3 base_green=3 killed=0`. A shell search for `^## Ceiling` returned no output. Seed-tree `find ... -type f | sort` and `git log --oneline` showed the seed baseline.
- Poll loop checked for the target file at 60-second intervals, maximum 20 checks, exited 0 when it appeared. No A0 fallback needed. No instrument selftest was run by this seat.
- `python3 build_seed.py` -> exit 0, SEED_COMMIT_OK, empty status, seed master 3bb2c8d5942db634855ced3003eae657c2aa9ce0.
- First `python3 build_fixtures.py` -> exit 1: plain check-ignore on the tracked A4 path returned 1. Probe made non-fatal and paired with --no-index; second builder run -> exit 0, FIXTURES_BUILT, full observed state preserved in fixtures-meta.json.
- First `python3 run_attacks.py <landed-tool>` -> exit 0, RUN_COMPLETE 27. Its base-arm path accidentally appended a second round suffix; those initial comparison receipts were invalid and are **not evidence**. Corrected the comparison command to `git -C <fixture> status --porcelain -uall -- .ufo/waves/round-<N>` before the final pinned run. The final 27-invocation run exited 0 as a driver; this is not an aggregate gate pass (individual verdicts above include findings and survivors).
- Supplemental A6 setup: guarded toplevel check -> exact fixture dir; `git -C <a6e> add -A` -> 0; fixture-identity commit -> 0. Round-72 complementary check -> 1. Submodule direct and forced-parent status commands -> 0 with the dirty records described above.

## Binding and verification limitations

The claims file was read in full before scoring; no freeze bytes or lane tool bytes were edited. The wave-spec's pre-amendment fleet-prompt recipe is stale; the landed tool correctly implements the amended claims-plan anchor. Valid plan/no prompt yields exit 0; present prompt/absent plan yields exit 1. Freeze/base SHA descriptions observed in plan, freeze.txt and current master differ; this report does not adjudicate freeze provenance.

`xd://lsp` is unavailable (device not mounted), so definitions/callers were checked through source reads and literal searches, not semantic references/diagnostics. No LSP evidence is claimed. Tests grade Git state only; no serving/runtime, resume-continuity, rerouting identity or saturation claim is made. No round admission judgment is emitted.

Procedure deviations: initial fixture helpers used subprocess cwd for Git rather than the required explicit `-C` spelling, and multiple small shared seed clones were used rather than one worktree. All mutations were confined to this seat's scratch fixtures; no lane git mutation occurred. These are disclosed rather than retroactively claimed compliant. Seed and main fixture commit helpers assert toplevel, but the initial childrepo builder lacked that assertion. Supplemental mutations use explicit `-C` and a toplevel assertion. Raw outputs remain useful behavioral evidence with these provenance limitations.

No tool installations or updates. Self-evaluation: accuracy 4 (scope survivors distinguished from frozen-rule violations); completeness 4 (A1–A7 exercised, no semantic tooling); clarity 4 (full commands in raw receipts); actionability 4 (source lines and complementary checks supplied); conciseness 3 (mandatory command inventory is lengthy). Overall 3.8/5. Highest-impact improvement is a uniformly guarded fixture driver, not changing the frozen predicate. Scratch is removed after artifact preservation.

Tested landed source SHA-256: `45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4`.
