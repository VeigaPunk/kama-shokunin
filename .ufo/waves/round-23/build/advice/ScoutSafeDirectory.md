# Scout — `safe.directory` ownership and GIT_DIR/GIT_WORK_TREE discovery

Channel: repository selection/ownership as probed by `tools/report-landing-audit.py`.
Base blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`, sha256
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`). Also re-ran the
whole grid against the current lane working-tree snapshot (sha256
`b6064767b1ce6b8833f977bb9fdfb45702c70427a9a792961ed3cc2636d89bda`, the
`GIT_ISOLATION` candidate): every probe rc/observation was identical
(`diff base-probe*.log cand-probe*.log` empty), so this channel is not touched by
that direction.

All fixtures ran only under `/tmp/kama-r23/ScoutSafeDirectory` (fresh repos,
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, git 2.56.0, Python 3.14.8,
no network, `example.invalid` not needed). No lane/fleet write, no pacman, no
tool installs. `sudo` was used only to chown throwaway `/tmp` repos to root for
the ownership probes.

## Verdict

**Split.** Foreign ownership is *already* a typed refusal. Discovery is **not**:
a lane/fleet path that is not itself a repository but lies inside an enclosing
repository is silently substituted for that repository and produces a verdict;
a `.git` gitfile redirects discovery to an arbitrary repository and flipped a
failed audit to clean. No crash and no repository-configured command execution
was observed in this channel.

| Sub-channel | Verdict |
|---|---|
| path not a repo, outside any repo | **no-effect**: EvalError -> exit 2 |
| path not a repo, nested inside another repo (lane) | **affects-verdict**: silent enclosing-repo audit, observed clean where the real lane fails |
| path not a repo, nested inside another repo (fleet) | **affects-verdict** when a nested report path exists in history; otherwise EvalError "no fleet commit" |
| lane/fleet owned by another user | **no-effect**: EvalError -> exit 2 ("dubious ownership") |
| repo-local `safe.directory = *` | **no-effect**: ignored (not protected config) |
| inherited `GIT_DIR` / `GIT_WORK_TREE` / `GIT_*` | **no-effect**: stripped, decoy object store untouched |
| `.git` gitfile pointing at another repo | **affects-verdict**: failed -> clean, no EvalError |
| repo-local `core.worktree` | **no-effect** (all reads are object-level) |
| crash / execution | none observed in this channel |

## 1. Foreign ownership / `safe.directory` — already EvalError (no-effect)

Base mechanism: `git_env()` (`tools/report-landing-audit.py:79-84`) strips every
`GIT_*` variable and sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`;
`git()` (`:87-97`) raises `EvalError` on any rc != 0; `main()` maps it to exit 2
(`:835-837`). The first access is `rev-parse --verify` (`:403-404`), before any
verdict is computed.

```
$ env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 report-landing-audit-base.py \
    --lane-repo fx/foreign --fleet-repo fx/fleet --rounds 1 --no-errata
could-not-evaluate: git rev-parse --verify master^{commit} in /tmp/.../fx/foreign: rc=128
fatal: detected dubious ownership in repository at '/tmp/.../fx/foreign'
To add an exception for this directory, call:
        git config --global --add safe.directory /tmp/.../fx/foreign
rc=2
```

Observed variants (all exit 2, same `could-not-evaluate:` refusal, no traceback):

- foreign **fleet** repo (valid lane) — same refusal at `rev-parse HEAD^{commit}`;
- path nested inside a foreign repo — refusal names the enclosing foreign root;
- only the worktree top directory chowned root (`.git` still mine) — refused;
- only `.git` chowned root (worktree top still mine) — refused. Both owners are checked.
- repo-local self-whitelist: `git config --file fx/foreign/.git/config --get-all
  safe.directory` returns `*`, and git still refuses — the setting is not honoured
  in repository scope.
- a temp *global* config with `safe.directory = *` makes raw git succeed
  (`git -C fx/foreign rev-parse HEAD` -> rc 0), but the audit still refuses,
  because `git_env()` replaces the global config with `/dev/null`.
- command scope does work: `git -c safe.directory='*' -C fx/foreign rev-parse HEAD`
  -> rc 0. The script never passes it. **Do not add it** — it would re-enable
  foreign/untrusted repositories instead of refusing them.

Doc, git v2.56.0, accessed 2026-10-21
(https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/safe.adoc):
"By default, Git will refuse to even parse a Git config of a repository owned by
someone else" (18 words); and "This config setting is only respected in protected
configuration (see SCOPES). This prevents untrusted repositories from tampering
with this value." (22 words). Git's suggested global-config remedy is exactly the
config this audit suppresses.

Operability consequence (not a defect): an intentionally shared/root-owned CI
checkout can never be audited; it exits 2. That is a refusal, not a verdict.

## 2. Inherited `GIT_DIR` / `GIT_WORK_TREE` — no-effect

`git_env()` drops all `GIT_*` (`:82`). All runs below used the base script and the
same lane/fleet as the control (`control-lane-fleet` rc=1, one `landed-omitted`
defect):

| Parent env | rc / observation |
|---|---|
| `GIT_DIR=<decoy>/.git`, `GIT_WORK_TREE=<decoy>` | rc=1, identical defects; decoy `objects/` file+size+mtime hash unchanged |
| `GIT_DIR=<missing>` | rc=1, identical |
| `GIT_DIR=<decoy>`, non-repo lane path | rc=2 `not a git repository`, not a decoy verdict |
| `GIT_CONFIG_COUNT=1` + `GIT_CONFIG_KEY_0=core.repositoryFormatVersion` `=99` | rc=1, identical |
| `GIT_CEILING_DIRECTORIES=<enclosing>` with lane=`<enclosing>/sub` | rc=0 clean (ignored), see §3 |

Doc (git v2.56.0 `git.adoc:540-543`, accessed 2026-10-21,
https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git.adoc):
"If the `GIT_DIR` environment variable is set then it specifies a path to use
instead of the default `.git` for the base of the repository." (25 words).
Because the script explicitly does not set `GIT_DIR`, git keeps doing upward
discovery — the subject of §3.

## 3. Upward discovery of a non-repo path — affects-verdict

`git -C` walks up until it finds a `.git`. `--lane-repo` / `--fleet-repo` are only
`Path.resolve()`d (`:391-392`); nothing checks that the resolved path *is* a
repository root.

Observed grid (same fleet, same report in every row; lane has one
`round-1:` commit by `kama-shokunin`, so the honest verdict is rc=1):

| Case | rc | JSON summary |
|---|---|---|
| control: `--lane-repo=<real lane>` | 1 | `status=failed`, `required=1`, `landed-omitted 9f63db55...` |
| `--lane-repo=<plain dir outside any repo>` | 2 | `fatal: not a git repository (or any parent up to mount point /)` |
| `--lane-repo=<enclosing>/sub` (plain dir inside repo `enclosing`) | **0** | `status=clean`, `required=0` — enclosing repo audited, false clean |
| `--lane-repo=<symlink to enclosing/sub>` | **0** | same false clean (`resolve()` follows the link) |
| `--lane-repo=<dir with an empty .git dir>` | 2 | `not a git repository` (discovery stops at the empty `.git`) |
| `--lane-repo=<file>` | 2 | `cannot change to '...': Not a directory` |
| `--lane-repo=<nonexistent>` | 2 | `cannot change to '...': No such file or directory` |

Fleet side: `git -C fleet-sub log -- <rel>` interprets the pathspec under the cwd
prefix (`report_cutoff`, `:165-168`); `ls-tree` pathspecs (`:208-222`, `:381`) are
also prefix-relative, and `ls-tree` output is prefix-stripped unless `--full-name`
(observed: inside `sub`, `ls-tree master -- corpus/SOURCES.md` is empty when only
the root has that file, and `--full-name` shows `sub/.ufo/reports/...`). `git show
HEAD:<rel>` (`:266`) is root-relative and unaffected by cwd. Two observed shapes:

- `--fleet-repo=<decoy>/sub` with no `sub/.ufo/reports/...` in history -> rc=2
  `round 1: .ufo/reports/round-1/kama.md has no fleet commit` (safe, though for a
  prefix reason rather than "path is not the repo root").
- synthetic repo with root report added at t=500 and `sub/.ufo/reports/round-1/kama.md`
  added at t=1200, same lane: `--fleet-repo=<repo>` -> **rc=0 clean cutoff=500**;
  `--fleet-repo=<repo>/sub` -> **rc=1 failed cutoff=1200**, and the audited bytes
  come from the *root* blob (`git -C <repo>/sub show HEAD:.ufo/reports/round-1/kama.md`
  -> `## Landed changes\nnone`). JSON `results[0].report` names
  `.../sub/.ufo/reports/round-1/kama.md`, i.e. the object reports a path it did not
  read. The grid is not flagged: no repo-identity field exists in JSON.

Lane prefix side effects from the same substitution: `load_source_urls` (`:208-222`)
runs `ls-tree <branch> -- corpus/SOURCES.md`; from `lane/sub` that misses the root
file and returns `None` (URL-hash exemption silently off), or reads
`sub/corpus/SOURCES.md` if present. `--rounds 1-` (`parse_rounds`, `:381`) lists
`sub/.ufo/reports` and its prefix-stripped output (`.ufo/reports/round-N/kama.md`)
still matches the regex, scoping the open range to the nested directory.

The pattern is a pure caller-path mistake/side effect (exported copy, build dir,
symlink), not something an untrusted audited repository can force; but it silently
converts "cannot evaluate" into a clean/failed verdict. `GIT_CEILING_DIRECTORIES`
cannot bound it because the script strips it (last row of §2).

## 4. `.git` gitfile redirect — affects-verdict (failed -> clean)

A directory whose `.git` is a *file* (`gitdir: <target>/.git`) is accepted and the
target repository is audited. Fixtures: real lane has `round-1: work`
(`9f63db55...`); decoy has `round-1: decoy work` (`1a7a3494...`); fleet report
cites only the decoy commit at t=1200.

| `--lane-repo` | rc | result |
|---|---|---|
| real lane | 1 | `landed-unresolved 1a7a3494b`, `landed-omitted 9f63db55...` |
| decoy directly | 0 | clean, `required=1` |
| `hijack/` with `.git` file -> `decoy/.git` | **0** | clean |
| copy of lane with `.git` replaced by that gitfile | **0** | clean |

`--show-prefix` is `""` for a gitfile worktree, so the prefix pin proposed
above (fix sketch item 1) would not catch this; `--show-toplevel` = the gitfile directory, `--absolute-git-dir` = the
target (`prefixrepo/.git`). Precondition: filesystem write to the repo root
(a gitfile cannot be tracked/committed), which is the same class as
`refs/replace`, not a clone-only attack. It flips a verdict, it does not execute
anything for the commands the audit uses.

## 5. Repo-local `core.worktree` — no-effect

`git -C fleet config core.worktree <nonexistent>`: verdict identical to control
(rc=1, cutoff=1200, required=1, `landed-omitted 9f63db55...`). Every audit read is
`rev-parse` / `log` / `cat-file` / `ls-tree` / `show` against the object store, so
a worktree redirection changes nothing.

## Cheap fix sketch (advice only; I wrote no code)

1. After `Path.resolve()` (`:391-392`, or next to the probes at `:403-404`), per
   repo: `prefix = git(repo, "rev-parse", "--show-prefix")`; if
   `prefix.strip()` -> `EvalError`. Valid roots return `""`; a nested path returns
   `"sub/"`. This closes §3 for lane and fleet, including the report-cutoff
   mismatch. Bare repos fail `--show-prefix`; gate on `--is-bare-repository` or
   refuse bare roots.
2. §4 is not caught by (1). Pinning `realpath(--absolute-git-dir) == realpath(repo/.git)`
   refuses gitfile redirection but also refuses legitimate linked worktrees
   (`<main>/.git/worktrees/<name>`); that is a product decision, not a clear bug.
3. Keep `GIT_CONFIG_GLOBAL=/dev/null` + `GIT_CONFIG_NOSYSTEM=1`; never add
   `-c safe.directory` (measured: it re-enables foreign repos, rc 0).
4. Optional transparency: record `--show-toplevel` / `--absolute-git-dir` per repo
   in `--json`, so a substituted repository is visible even if not refused.
5. Controls: selftest lane/fleet are `git init` roots (prefix `""`), so (1) is a
   no-op for them. I did not run the selftest, base or candidate.

## Not verified

- selftest 50/50 not run; no historical-ledger run.
- The real lane and fleet repos were never audited (fixtures only).
- Linked worktrees/submodules as lane/fleet; root/sudo execution and git's
  `SUDO_UID` exception; `.git` as a symlink; bare-repo lane; `objects/info/alternates`
  (sibling scout covers it), mailmap, objectFormat, logFollow.
- The full dispatch/scorecard consequences beyond rc and JSON summary fields.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutSafeDirectory.md` (this report)
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/probe.py`
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/probe2.py`
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/probe3.py`
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/probe4.py`
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/base-probe{,-2,-3,-4}.log`
- `.ufo/waves/round-23/build/out/ScoutSafeDirectory/cand-probe{,-2,-3,-4}.log`
