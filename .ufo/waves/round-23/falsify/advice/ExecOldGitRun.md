# ExecOldGitRun: committed auditor on grid C01-clean under official git 2.44.0-1 and 2.45.0-1

**Verdict: holds.** With `PATH` set to only the extracted 2.44.0-1 bin dir, `tools/report-landing-audit.py` exits 2 with `could-not-evaluate: ... unknown option: --no-lazy-fetch` and no traceback. With `PATH` set to only the 2.45.0-1 bin dir it exits 0 with zero defects. strace confirms the PATH-selected binaries were the ones that executed.

Base: lane master `245a37f69628c2c6bb29bbf17897d8fb5946c857`, verified in my clone `/tmp/kama-r23w2/ExecOldGitRun`. Auditor blob `f10d811eafcc5bc853abdf75c4a05ec2374cd579`, sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.

## Commands

```
bash .ufo/waves/round-23/falsify/out/ExecOldGitRun/fetch-old-git.sh        -> fetch-ok
python3 .ufo/waves/round-23/falsify/out/ExecOldGitRun/c01_old_git_driver.py -> 12 PASS lines, driver_rc=0
```

The driver builds C01 with the grid's own `c_clean` (system git 2.56.0, as the grid does) in fresh `/tmp/execoldgit-c01-yvs3v_5u`. Fixture HEADs (synthetic repos, not the real lane): lane `db796f8b820bf3825c58832419138cdba23206a7`, fleet `ebcb436228cc3c28fd415f5afcce3312e1151be4`. Each auditor run uses the grid's argv (`--lane-repo --fleet-repo --json --rounds 1 --no-errata`) and env (`grid.env()`).

## Results (`out/ExecOldGitRun/summary.json`, `runs/*/`)

| run | PATH | git resolved / version | exit | strace-run exit | stdout | stderr | git execs |
|---|---|---|---|---|---|---|---|
| system control | host PATH | /usr/bin/git, 2.56.0 | 0 | 0 | JSON, 0 defects | empty | /usr/bin/git only |
| git-2.44.0-1 | `.../old/2.44.0/usr/bin` | 2.44.0 | **2** | 2 | empty | `could-not-evaluate: git rev-parse --show-object-format in /tmp/execoldgit-c01-yvs3v_5u/lane: rc=129 unknown option: --no-lazy-fetch` + git usage | 1 exec, argv has `--no-lazy-fetch`, child status 129 |
| git-2.45.0-1 | `.../old/2.45.0/usr/bin` | 2.45.0 | **0** | 0 | JSON, 0 defects | empty | 24 execs, all 2.45.0 binary |
| mutant: 2.44.0, flag removed (/tmp copy) | `.../old/2.44.0/usr/bin` | 2.44.0 | 0 | 0 | JSON, 0 defects | empty | 2.44.0 only |

Gates (all PASS): 2.44 exit 2; 2.44 stderr starts `could-not-evaluate:` and names `--no-lazy-fetch`; 2.44 no traceback and empty stdout; 2.45 exit 0 with zero defects and empty stderr; system control exit 0; traced runs match plain runs; every git exec is the PATH-selected binary; fixture tree digest unchanged by every run.

Grid harness, same PATHs (`repo-state-grid.py --arm current --case C01-clean --json`):
- 2.44: row exit 2, `met` false, traceback false, executed false. Grid exit 1 (one violation).
- 2.45: `met` true. Grid exit 0.
- System: `met` true.

Trace evidence, `runs/git-2.44.0-1/execve-trace.txt` line 2:
`execve("/tmp/kama-r23w2/ExecOldGitRun/old/2.44.0/usr/bin/git", ["git", "--no-replace-objects", "--no-lazy-fetch", "-c", ..., "rev-parse", "--show-object-format"], ...) = 0`, then `si_status=129`.

## Code at 245a37f6 (`tools/report-landing-audit.py`)

- `:92-93`: comment "Old git (< 2.45) rejects --no-lazy-fetch, which is an EvalError." and `GIT_ISOLATION` containing `--no-lazy-fetch`.
- `:114`: every git call is `["git", *GIT_ISOLATION, "-C", str(repo), *args]`.
- `:119-121`: non-zero rc raises `EvalError` carrying git's stderr.
- `:403-404`: a bare round number makes no git call. The first git call is the lane's `rev-parse --show-object-format` at `:431`, reached via `:475-476`.
- `:909-911`: `EvalError` prints `could-not-evaluate:` to stderr and returns 2.
- `:55`: docstring "git >= 2.45 is required."

Grid, `tests/report-audit/repo-state-grid.py`: `:128-130` (`c_clean`), `:528` (C01 expects exit 0, no kinds), `:600-612` (run argv/env), `:627-630` (`met`, which tests the full stderr for reasons).

## Observations

1. The 2.44 refusal is fail-closed. There is no traceback, no stdout and no verdict. It refuses the clean control too, so under 2.44 the grid's C01 row is NOT-MET. This is the declared git >= 2.45 floor, not a crash.
2. The mutant isolates the cause on this fixture. Deleting only `"--no-lazy-fetch",` from `GIT_ISOLATION` turns exit 2 into exit 0 with zero defects. The committed file is untouched. The mutant and its diff are in `out/ExecOldGitRun/mutant/`.
3. Display-only nuance: the grid row's `stderr_tail` (last 200 chars) for 2.44 shows only git usage text, because the reason token is on the first stderr line. The `met` test uses full stderr, so pass/fail is unaffected.
4. Both old binaries compile `/usr/lib/git-core` as their exec path. No helper program executed in any run, so the host's 2.56 helpers were never used.

## Not verified

- The full grid (26 faults, 8 controls) under 2.44 or 2.45. Only C01 was in scope.
- `--selftest` under either old git. The frozen arm under old git.
- Other old-git versions. Only 2.44.0-1 was refused; the claim that every version below 2.45 refuses was not tested. The archive also lists 2.45.1 and 2.45.2, which were not run.
- Upstream source builds. Only Arch-built binaries were used.
- Keyring trust. gpg reports `GOODSIG` for key `0429897DE5F3BDAC537A30696D42BDD116E0068F` with `TRUST_UNDEFINED`, since no ownertrust is set. Integrity was checked against the Arch keyring; the trust chain was not established.
- Helper-program behavior under the old binaries (none ran).

## Tooling and installs

- No installs. No pacman. No system changes.
- Downloaded official Arch archive packages and extracted them under `/tmp/kama-r23w2/ExecOldGitRun/old/`:
  - `https://archive.archlinux.org/packages/g/git/git-2.44.0-1-x86_64.pkg.tar.zst`, sha256 `8217cf3d618da85b8671f0849d349a5d5b1f0e9bc6cbead279391dfa41771ecd`
  - `https://archive.archlinux.org/packages/g/git/git-2.45.0-1-x86_64.pkg.tar.zst`, sha256 `122f310b029d4c0057dab7f1138174826d72a4f2d15d19e86d22740a53728b96`
  - Signatures checked with gpg 2.4.9 against `/usr/share/pacman/keyrings/archlinux.gpg` in a throwaway homedir. Extracted with zstd 1.5.7 and tar.
- Host tools used unchanged: curl 8.23.0, gpg 2.4.9, strace 7.2, Python 3.14.8.

## Files written

- `.ufo/waves/round-23/falsify/advice/ExecOldGitRun.md` (this report)
- `.ufo/waves/round-23/falsify/out/ExecOldGitRun/`: `fetch-old-git.sh`, `c01_old_git_driver.py`, `summary.json`, `tools.txt`, `packages.sha256`, `gpg-verify-{2.44.0,2.45.0}.txt`, `pkginfo-*.txt`, `ldd-*.txt`, `old-git-*.txt`, `runs/*/` (argv, PATH, stdout, stderr, exit, traced-exit, execve-trace.txt), `grid-harness/*/`, `mutant/report-landing-audit.no-lazy-fetch-flag-removed.py`, `mutant/diff.txt`
- Scratch outside the lane: `/tmp/kama-r23w2/ExecOldGitRun/` (clone at 245a37f6; untracked `pkgs/`, `old/`, `gnupg/` added), fixture `/tmp/execoldgit-c01-yvs3v_5u/`
- Lane checkout: no tracked-file, index or `.jj` writes. The lane was only read by `git clone --no-hardlinks`.
