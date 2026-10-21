# RevengeGitfile: O02 gitfile redirect and linked worktrees (round 23, FALSIFY)

Subject: `tools/report-landing-audit.py` at `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
Clone HEAD verified equal in `/tmp/kama-r23w2/RevengeGitfile`. Lane `master` verified equal
to 245a37f at check time. Git 2.56.0 (system, Arch). Findings only: nothing applied to the auditor.

## Verdict: partially falsified

- **Flip: falsified.** O02 is live. A `.git` gitfile (absolute or relative) or a `.git` symlink
  pointing at a foreign repository that holds one extra pre-cutoff commit the report cites turns
  `failed` (exit 1) into `clean` (exit 0), in every form tested (T2). The verdict record carries
  no lane identity (T5).
- **Hang: falsified, and not linked-specific.** A FIFO `HEAD` in the audited git dir blocks the
  auditor with no timeout: plain `.git/HEAD` (control), a linked worktree's admin `HEAD`, and its
  admin `commondir` (probe3 C1, probe2 F2). Harness kill at 10 to 20 s leaves zero orphan git
  processes (probe3 C3, `pgrep` pattern validated by a positive control).
- **Crash: held.** Every gitfile failure that returned exited 2 with a reason. No traceback.
- **Programs: held on the auditor's read path.** strace of the hostile-config redirect (`front_h`)
  and of the plain baseline shows only `git` and `python3` executed. Positive controls (probe2 F1)
  show git DOES import and run foreign `core.fsmonitor` (via `status`) and `diff.external` (via
  `diff`, or `log -p --ext-diff`) through a gitfile. The auditor is exposed the moment a call
  refreshes the index or uses `--ext-diff`.
- **Assigned question.** A legitimate linked worktree is distinguished from a foreign redirect by a
  two-way, enumerated relation to its common repository (section 3). A single
  `--git-common-dir` versus path comparison cannot make that distinction (section 6). The proposed
  check (sections 4 and 5) accepts every legit class tested except `clone --separate-git-dir`
  (refused: tradeoff), and refuses every foreign class tested. It is consistency-only (section 7).

Axes named: A mechanism; B auditor verdict and side effects per channel; C discrimination of legit
versus foreign (ablation); D authenticity; E no-harm on the production pair.

## 1. Mechanism (A, git 2.56.0, observed in probe.out T1, T1b)

- M1 Gitfile: a regular `.git` file with `gitdir: <path>`. Relative paths resolve against the
  file's directory (`gitdir: ../main/.git/worktrees/wtrel`; `relfront` with `gitdir: ../decoy/.git`).
  Git docs, gitrepository-layout, https://git-scm.com/docs/gitrepository-layout: "Also you can have
  a plain text file `.git` at the root of your working tree, containing `gitdir:` <path> to point
  at the real directory that has the repository."
- M2 Linked admin dir `C/worktrees/<name>` holds `commondir` (`../..`), back-link `gitdir`
  (absolute for `wt`, relative `../../../../wtrel/.git` for `wtrel`), and per-worktree `HEAD`.
  Local man, git-worktree(1): to repair a moved linked worktree, "run git worktree repair to
  reestablish the connection automatically" (the auditor must never run `repair`: it writes).
- M3 `git worktree list` run against the common dir enumerates admin dirs and prints their
  back-links: main lists `main`, `wt`, `wtrel`; it does not list `wt-copy` or `atk-wt`.
- M4 Raw `--git-dir`/`--git-common-dir` are relative (`.git`) in the main worktree and absolute in
  linked ones. `--path-format=absolute` gives "absolute and canonical" paths (local man,
  git-rev-parse(1)).
- M5 `clone --separate-git-dir` writes a gitfile and NO `core.worktree` (`git config --get
  core.worktree` returns rc 1, empty). Submodule module dirs carry `core.worktree = ../../../sub`.
- M6 A `.git` symlink is followed; `--path-format=absolute --git-dir` prints the resolved target
  (`/…/decoy/.git`), not the symlink path.
- M7 Git 2.56 refuses a non-regular gitfile (FIFO: `fatal: not a regular file`, rc 128, no hang)
  and a dangling one (rc 128).
- M8 Git blocks reading a FIFO `HEAD` or `commondir` (per-worktree or plain): see Verdict.
- M9 Foreign repo config is honored through a gitfile (positive controls: probe2 F1, `status` runs `/bin/sh` and `touch` via the gitfile; `diff` and `log -p --ext-diff` run `diff.external`).
  `log -p` runs `diff.external` only with `--ext-diff` (local man, git-log(1): "you need to use
  this option with git-log(1) and friends"; observed: plain `log -p` marks=[]).

## 2. Auditor under each channel (B; file:line at 245a37f)

- `tools/report-landing-audit.py:99-105` `git_env` strips `GIT_*`; `:93-96` `GIT_ISOLATION` has no
  discovery control; `:108-116` `git()` runs `git -C <repo>`. Env redirects are neutralized; file
  redirects are not.
- `:426-448` `check_history_repo` checks object format, top-level prefix, shallow, `--git-path
  info/grafts` and `objects/pack`, and promisor config. These go through discovery, so they DO
  follow a gitfile (observed: `front_g` refused, exit 2, "rewrites history"). It never classifies
  the `.git` entry's kind or target.
- `:52-55` declares: "Objects borrowed through objects/info/alternates or a .git gitfile still
  resolve as local, and other repository-local channels are not claimed." O02 is therefore a
  declared open channel. The flips sit inside that declaration, but nothing in the record
  (`:502-503`; keys in T5) tells a reader which repository was audited.
- `:888-891` defaults: `--lane-repo` is the script's own repo, `--fleet-repo` its parent. Both are
  positional and unclassified. Code-read only, not run.

## 3. What distinguishes a legitimate linked worktree from a foreign redirect

Legit linked worktree at path `P`, with `P/.git` a gitfile to `A`, and `C` = absolute
`--git-common-dir`:

- I1 `P/.git` is a regular file whose `gitdir:` resolves to `A`.
- I2 `realpath(dirname(A)) == realpath(C/worktrees)`: the admin dir lives under the common repo.
- I3 `A/gitdir` (back-link, absolute or relative) resolves to `P/.git`.
- I4 `realpath(P)` is listed by `git --git-dir C worktree list --porcelain`.

Standalone gitfile (`A == C`): legit only with a `core.worktree` back-link naming `P` (submodules).
`clone --separate-git-dir` has none, so git metadata alone cannot tell it from a foreign repo.
Symlinked `.git`: refused whatever its target.

Why I2 and I4 and not I3 alone: I3 is satisfiable by whoever writes the admin dir, and the forged
`atk-wt` satisfies it (ablation, section 5). I2 and I4 bind the admin dir to the common repo's own
enumeration. A copy fails I3 and I4. A forged admin fails I2 and I4.

## 4. Proposed check (tested in /tmp; NOT applied to the auditor)

Condensed from `out/RevengeGitfile/probe.py` `classify()` and `probe2.py` `classify_pre()`:

```python
def classify(lane):
    dotgit = os.path.join(lane, ".git")
    kind = lstype(dotgit)                       # lstat BEFORE any git call
    if kind not in ("dir", "file"):             # missing / symlink / fifo / other
        return refuse(f".git is {kind}")
    if kind == "file":
        target = gitdir_target(dotgit)          # realpath of gitdir:, must be a directory
        if any(lstype(Path(target, n)) not in ("missing", "file")
               for n in ("HEAD", "commondir", "gitdir")):
            return refuse("admin entry is not a regular file")   # FIFO HEAD would hang git
    top = realpath(git("rev-parse", "--show-toplevel"))
    gd = realpath(git("rev-parse", "--path-format=absolute", "--git-dir"))
    cd = realpath(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
    if top != realpath(lane):
        return refuse("not a worktree root")
    if kind == "dir":
        return PLAIN if gd == cd == realpath(dotgit) else refuse("dir .git: git-dir != common")
    if target != gd:
        return refuse("gitfile target is not the git-dir git resolved")
    if gd == cd:                                # standalone via gitfile
        wt = git("--git-dir", gd, "config", "--get", "core.worktree")   # rc!=0 -> refuse
        return STANDALONE if realpath(join(gd, wt)) == realpath(lane) else refuse("core.worktree elsewhere")
    if realpath(dirname(gd)) != realpath(join(cd, "worktrees")):
        return refuse("admin dir not under common worktrees/")
    if backlink(gd) != realpath(dotgit):       # readline of gd/gitdir, resolved
        return refuse("back-link names another .git")
    if realpath(lane) not in worktree_list(cd):
        return refuse("common repository does not list this worktree")
    return LINKED(cd)
```

Choice of checks: `rev-parse --git-common-dir` is used, but compared with the path only for the
plain-directory case. For linked lanes it is compared through the admin structure (I2 to I4).

## 5. Test results (classify and auditor; same fixtures; `probe.out` T2/T3, `probe2.out` F1 to F5)

| lane (fixture) | proposed result | auditor (rc) |
|---|---|---|
| main (plain dir) | PLAIN | 0 clean |
| wt (linked, absolute gitfile) | LINKED(main/.git) | 0 clean |
| wtrel (linked, relative gitfile) | LINKED(main/.git) | 0 clean |
| wt via symlinked dir (`wt-alias`) | LINKED(main/.git) | 0 clean |
| submodule `super/sub` (core.worktree back-link) | STANDALONE accepted | 0 clean |
| sepwt (`clone --separate-git-dir`) | REFUSE, no back-link (tradeoff) | 0 clean today |
| front to decoy (gitfile, superset) | REFUSE | 1 to 0 flip (fleet_e) |
| relfront (relative gitfile to decoy) | REFUSE | 1 to 0 flip |
| symrepo (`.git` symlink to decoy) | REFUSE, symlink | 1 to 0 flip |
| front2 to decoy2 (subset, lacks B) | REFUSE | 1 (`landed-unresolved`) |
| front_same to identical clone | REFUSE | 0, JSON byte-identical to plain |
| wt-copy (copied linked worktree) | REFUSE, back-link names `wt` | 0 clean (audits main's history) |
| atk-wt (forged admin under attacker repo, `commondir` to main) | REFUSE, admin not under common | 0 clean (audits main's history) |
| front_g to grafted decoy | REFUSE | 2 "rewrites history" |
| front_h to decoy with hostile config | REFUSE | 0; no foreign program ran (marks=[]) |
| dangling gitfile | REFUSE | 2 (git rc 128) |
| `.git` is FIFO | REFUSE, no git call | 2 (git "not a regular file") |
| plain `.git/HEAD` FIFO (control) | REFUSE, preflight | TIMEOUT (hang) |
| linked admin `HEAD` FIFO | REFUSE, preflight | TIMEOUT (hang) |
| linked admin `commondir` FIFO | REFUSE, preflight | TIMEOUT (hang) |
| production `kama-shokunin` and fleet root | PLAIN, PLAIN | 0 clean (13 reports, 9 defects all corrected, 0 uncorrected) |

Ablation (probe2 F3; `True` means the check passes):

| worktree | back-link names this `.git` | admin under common `worktrees/` | common lists this worktree |
|---|---|---|---|
| wt (legit) | True | True | True |
| wtrel (legit) | True | True | True |
| wt-copy (copy) | False | True | False |
| atk-wt (forged) | True | False | False |

So the back-link alone is insufficient (forged passes it). The membership check alone rejects both
the copy and the forged admin. The admin-under-common check is a cheap additional gate.

## 6. The naive `--git-common-dir` versus path check, and what it gets wrong

- Equality of `--git-common-dir` (absolute) with `<top>/.git` holds only for plain directories.
  Every legit linked worktree fails it (observed: common `/…/main/.git`, path `/…/wt/.git`), which
  is a false refusal.
- String versus realpath, for the symlink (`symrepo`): string comparison refuses it (correct), but
  `realpath(symrepo/.git)` equals `--git-common-dir` (both `/…/decoy/.git`), so a realpath-only
  equality ACCEPTS a symlink to a foreign repo. The lstat gate is required.
- Raw (non-absolute) outputs compare equal in the main worktree (`.git` and `.git`) and mix forms
  elsewhere. Use `--path-format=absolute`.

## 7. Authenticity: consistency is not identity

- F5: a foreign repo with a forged `core.worktree` pointing at the lane path passes the standalone
  check (`GITFILE-STANDALONE`), and the forged lane's top-level resolves to the lane path.
- F5: an attacker-owned linked worktree (its own `am` repo with its own admin dir) passes the
  linked check (`LINKED: worktree of …/am/.git`).
- Consequence: the structural checks cannot establish WHICH repository a lane is. The auditor needs
  an expected common-dir pin for any linked lane (for example the fleet's `.git`), or it must refuse
  linked lanes. Production needs no pin today because both repos are plain.

## 8. No-harm on the production pair (E)

- Lane `kama-shokunin/.git` and fleet `shokunin/.git` are plain directories. Both classify PLAIN.
  The proposed check changes no production verdict (probe.out T3).
- Production audit with the 245a37f auditor, default `--rounds 10-`, against the lane master: rc 0,
  `status=clean`, 13 reports, 9 defects (all corrected), 0 uncorrected, 54 required commits (T6).
- Tradeoffs if adopted: `clone --separate-git-dir` lanes would be refused (today accepted); submodule
  gitfiles accepted only with the `core.worktree` back-link; linked lanes need the pin (section 7).

## 9. Lane working-copy drift (not tested)

The lane working tree carries 72 uncommitted diff lines in `tools/report-landing-audit.py` (and
`tests/report-audit/*.py` are modified). In the drift: `check_history_repo` promisor and config
handling change, `resolve_branch` changes, errata hex folding changes. `git_env`, `GIT_ISOLATION` and
the four discovery rev-parse calls (working copy lines 434 to 442) are unchanged. O02 behavior is
expected to carry over. Not tested on the working copy.

## 10. Adjacent finding, control-scoped (outside the assigned surface)

Recorded because it falsifies the C1 "must not hang" wording inside `$GIT_DIR`: a FIFO `.git/HEAD`
in a plain repository hangs the auditor (probe3 C1, TIMEOUT at 15 s). The round-23 grid has no FIFO
row. The proposed preflight refuses it without a git call (probe3 C2). Severity: low (needs a FIFO
in your own git dir), but it sits inside the stated claim.

## 11. Recommendations for L1 (findings; not applied, not implemented)

1. Add the lstat plus admin-entry preflight and the plain, linked, standalone classification before
   the first git call in `check_history_repo`. Refuse foreign classes with exit 2 and a pinned reason.
2. Decide the identity policy for linked lanes: pin the expected common dir, or refuse linked lanes.
   Record `lane_kind`, `lane_git_dir`, `lane_common_dir` (and the fleet's) in the JSON summary. This is
   provenance only; no verdict change.
3. Grid: O02 currently expects exit 1 `landed-omitted` as an `open` row. Under the check, the
   redirect rows (front, relfront, symrepo, front_same, wt-copy, atk-wt) become exit 2 with a pinned
   reason; wt, wtrel and submodule stay 0; FIFO `HEAD` becomes exit 2, not a timeout.
4. Document `clone --separate-git-dir` as refused (or add a pinned allow). Document the admin FIFO
   hang as a stated limit if not fixed.

## 12. Confidence, and what I did NOT verify

- High: sections 1, 2, 5 and 6 (direct runs on git 2.56.0, with strace and marker controls).
- NOT run: git versions other than 2.56.0. The auditor's floor (2.45) is unverified. The
  `--path-format` option is used by the proposed check; its availability below 2.56 is not verified here.
- NOT run: the round-23 grid and selftest; the lane working copy (section 9).
- NOT tested: `extensions.worktreeConfig` and per-worktree `config.worktree` as a channel;
  per-worktree `refs/worktree/*`; `objects/info/alternates` (O01).
- Inference, not tested: a FIFO `shallow` file would block like `HEAD`. `info/grafts` uses lexists
  only, so a FIFO there is refused without opening it.
- Not exercised: signature/gpg knobs (no signed commits; grid F09 covers the path) and pager (no
  tty). `filter.*.process` and `alias.*` are configured but no command in the auditor triggers them.
- The pin is a design proposal; the classifier is consistency-only and I did not implement pinning.
- My O02 fixtures are my own constructions. They are not the grid's `o_gitfile`, and I did not run the grid.
- Default fleet by position (`:891`) is code-read only.

## 13. Files written and installs

- Report: `.ufo/waves/round-23/falsify/advice/RevengeGitfile.md` (this file; lane checkout, untracked
  seat output).
- Out: `.ufo/waves/round-23/falsify/out/RevengeGitfile/` with `probe.py`, `probe2.py`, `probe3.py`,
  `probe.out`, `probe2.out`, `probe3.out` (copies of the scripts and transcripts run).
- Scratch outside the lane: `/tmp/gitfile-r23-run/` (fixture roots `fx`, `fx2`, `fx3`; strace traces
  under `fx*/out`). Clone `/tmp/kama-r23w2/RevengeGitfile`, not modified.
- Lane checkout: no tracked-file writes and no index writes by me. One early `git status --short`
  ran before I set `GIT_OPTIONAL_LOCKS=0`, so git may have refreshed the index stat cache. Later
  status with optional locks off shows the same pre-existing modifications.
- Installs or upgrades: none. Used system git 2.56.0, python 3.14.8, strace 7.2, and the installed
  man pages.
