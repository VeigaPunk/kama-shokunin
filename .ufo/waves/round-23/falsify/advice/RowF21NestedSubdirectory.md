# Row F21 — nested-subdirectory-lane (fault)

Verdict: **partially falsified.** The fixture premise is real, the expected
exit-2 refusal is the correct contract for this exact row — but the fix guards
only `git rev-parse --show-prefix`, and three live near variants of the same
channel still silently audit the *enclosing* repository, including a
**clean exit-0 verdict on the wrong repo**.

Auditor under test: `tools/report-landing-audit.py` @
245a37f69628c2c6bb29bbf17897d8fb5946c857, frozen blob
4fe9339f8fc3a4a4a479d9c938a850da12f1124d. git 2.56.0. Fixture rebuilt by hand
at `/tmp/kama-r23w2/fix-f21` (no grid import; mirrors `pair()`/`base()`/`commit()`
semantics: `init -q -b master`, `@{ts} +0000` stamps, `-c commit.gpgsign=false`).

## 1. Fault premise: REAL and observed in the frozen arm

Builder `f_nested_subdir` (`tests/report-audit/repo-state-grid.py:501-512`):
`outer` repo with a plain `outer/lane` subdirectory (no `.git`); `--lane-repo`
names `outer/lane`, so every `git -C` resolves to `outer/.git` — the enclosing
repo whose history lacks the lane's round-1 commits. Premise check
(`--show-prefix == "lane/"`) observed:

    $ env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
        git -C /tmp/kama-r23w2/fix-f21/outer/lane rev-parse --show-prefix
    lane/
    $ git -C ... rev-parse --absolute-git-dir
    /tmp/kama-r23w2/fix-f21/outer/.git        ← silently discovers upward

Frozen arm (hand-built fixture, same argv as `run_case`: `--lane-repo
outer/lane --fleet-repo fleet --json --rounds 1 --no-errata`, cwd=fixture dir):

    frozen exit=1  stderr=(empty)
    kinds = ['landed-unresolved', 'unresolved-full-hash']
    round_commits = 0   ← outer's log filtered out every lane commit

Frozen audited the *enclosing* repository and emitted a false-defect verdict —
exactly the silent-wrong-repo failure the grid claims. Grid cross-check agrees:
`python3 tests/report-audit/repo-state-grid.py --arm both --case
F21-nested-subdirectory-lane` → `frozen ... exit=1 kinds=['landed-unresolved',
'unresolved-full-hash'] NOT-MET`, grid exit 1.

## 2. Expected outcome (exit 2, "not a repository top level"): CORRECT

`check_history_repo` (`tools/report-landing-audit.py:434-435`) refuses when
`--show-prefix` is non-empty. Current arm on my fixture:

    current exit=2
    could-not-evaluate: /tmp/kama-r23w2/fix-f21/outer/lane: not a repository top level

Is refusal the right contract, vs. resolving to the toplevel and continuing?
Yes: `--lane-repo` is a caller assertion of *which repository* holds the lane
history. Upward discovery substitutes a different history silently — the
alternatives are a wrong-repo defect list (observed: false unresolved-* on
outer) or a wrong-repo clean (see §3). Both are materially false evidence.
Exit-2 refusal is the honest answer; both lane and fleet sides are guarded
(symmetry verified: `--fleet-repo fleet/subdir` → exit 2, same reason).
Grid expectation `fault, 2, None` + `REASONS[...] = "not a repository top
level"` matches observed behavior. ✔

## 3. Near variants current STILL gets wrong — all bypass `--show-prefix`

`--show-prefix` is only non-empty when the resolved repo has a worktree and
the path lies *inside* it. Repository-local state and `.git`-interior paths
sidestep that. Each of the following exits **1** on the omission fixture
(audits `outer`, not the intended lane) and exits **0 clean** on a fixture
whose cited commit lives in `outer` — a full silent-verdict flip, the exact
harm F21's refusal exists to prevent. All driven through the auditor's own
`git()` (isolated env, `-C` path only):

| variant | setup | `--show-prefix` at `outer/lane` | current verdict |
|---|---|---|---|
| gitdir-interior | `--lane-repo outer/.git/refs` | `''` (empty — path is inside GIT_DIR, no worktree prefix) | exit 0 **clean** on outer |
| core.bare | `git -C outer config core.bare true` (repo-local config) | `''` | exit 0 **clean** on outer |
| core.worktree | `git -C outer config core.worktree /tmp/wt` | `''` (path outside redirected worktree) | exit 0 **clean** on outer |

Observed (hand-built `fix-f21v2`: `outer2` owns cited `round-1:` commit OC,
`outer2/lane` plain subdir):

    baseline lane=outer2 (top level)        rc=0 clean   (control)
    V-core-bare   lane=outer2/lane          rc=0 clean   ← FLIP: refused input audited wrong repo
    V-core-worktree lane=outer2/lane        rc=0 clean   ← FLIP
    V-gitdir-interior lane=outer2/.git/refs rc=0 clean   ← FLIP

On the omission fixture all three return `kinds=['landed-unresolved',
'unresolved-full-hash']` — the frozen arm's signature wrong-repo verdict.
`core.bare`/`core.worktree` are *repository-local* state (`.git/config`),
squarely inside the declared axis-7 scope "repository-local git state must
not crash, flip, hang or run programs" — this is a **flip** current still
produces. The guard needs `--is-inside-git-dir` and a check insensitive to
bare/worktree indirection (e.g. compare resolved `--git-dir` worktree root,
or `--show-toplevel` + `--is-inside-git-dir`), not `--show-prefix` alone.

Variants probed that ARE handled (no finding):
- deeper nesting `outer/lane/sub/deep` → exit 2 refused
- `--fleet-repo` subdirectory → exit 2 refused (symmetric guard)
- symlink `outer/link2lane -> lane` → resolved path refused, exit 2
- bare-repo subdir `bare.git/objects/xx` → audits `bare.git` (silent upward
  walk inside GIT_DIR, same hole as `.git/refs`) but dies at
  `master^{commit}` → exit 2; same wrong-repo channel, no verdict emitted.
- `outer/x/../lane` path-normalized → refused; trailing slashes fine.
- `GIT_DIR`/`GIT_DIR`-style env redirection → scrubbed by `git_env()`
  (tools/report-landing-audit.py:103), not exploitable through argv.

## 4. What I did NOT verify

- `.git` file (gitdir redirect) at the subdirectory — O02, declared open.
- `alternates`-style object borrowing — O01, declared open.
- Whether `.git` itself as `--lane-repo` *should* be refused (arguably a
  legitimate gitdir spelling); I flag the silent-flip hazard, not the UX.
- Non-sha1 + subdir interaction: refusal reason would be "object format"
  before the prefix check — still exit 2, different reason (unrun; the
  reason string is order-dependent at tools/report-landing-audit.py:431-435).

## Evidence artifacts

- Fixture builders/runs: `/tmp/kama-r23w2/build-f21.sh`,
  `/tmp/kama-r23w2/fix-f21`, `/tmp/kama-r23w2/fix-f21v2` (all /tmp, GIT_* scrubbed)
- Frozen auditor extract: `/tmp/kama-r23w2/frozen-auditor.py` (cat-file of
  4fe9339:tools/report-landing-audit.py)
- Grid row: `tests/report-audit/repo-state-grid.py:501-512,564,587`
- Guard: `tools/report-landing-audit.py:426-448` (`--show-prefix` at :434)

Files written: this report only.
