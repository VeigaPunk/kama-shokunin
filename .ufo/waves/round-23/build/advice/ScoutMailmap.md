# ScoutMailmap — repo-local `.mailmap` / `log.mailmap` / `%an` vs `%aN`

Base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, git 2.56.0, tested 2026-10-21.
Target: `tools/report-landing-audit.py` author-name match in `round_commits`.

## Verdict

**no-effect** on the author name the auditor matches. `round_commits` formats
`%an` (raw author name), not `%aN` (mailmap-canonical), so no repo-local
`.mailmap`, `mailmap.file`, `mailmap.blob`, or `log.mailmap` value can change
which commits are treated as `<lane>-shokunin` commits. The counterfactual is
real (`%aN` flips in both directions) but the base code does not use it.

Separate, adjacent fault (not a verdict flip): a FIFO named `.mailmap` in either
audited repo's worktree, or repo-local `mailmap.file` pointing at a FIFO or
`/dev/zero`, makes `git log`/`git show` block; the base audit then hangs with no
verdict at all (no `subprocess.run` timeout). A repo-local
`log.mailmap=banana` makes git exit 128; base turns that into a typed
`could-not-evaluate` exit 2, not a verdict. Neither crashes into a false verdict.

## Contract at base (blob 4fe9339f, 40390 bytes)

- `git_env` base:79-85 strips inherited `GIT_*` and sets
  `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`. It does **not**
  neutralize repo-local `.git/config` (proved below).
- `git()` base:87-98 runs `subprocess.run(..., capture_output=True, text=True)`
  (base:90), no timeout, raises `EvalError` on rc != 0.
- `round_commits` base:147-162; format string base:148:
  `--format=%H{SEP}%an{SEP}%at{SEP}%s{END}`; comparison base:160:
  `if author == f"{lane}-shokunin" and pat.match(subject)`.
- This is the only author-name comparison in the file (grep for `%an|author|mailmap`).
- Other `git log`/`show` calls exposed to the eager mailmap read described below:
  `report_cutoff` base:165-168 (`git log --diff-filter=A --format=%at`),
  report read base:266 (`git show HEAD:<rel>`), errata read base:339
  (`git show <branch>:registry/report-landing-errata.tsv`).

## Governing documentation (git-scm, 2.56.0 pages, accessed 2026-10-21)

- https://git-scm.com/docs/git-log#Documentation/git-log.txt-an — `%an`:
  "author name"
- https://git-scm.com/docs/git-log#Documentation/git-log.txt-aN — `%aN`:
  "author name (respecting .mailmap, see git-shortlog[1] or git-blame[1])"
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-logmailmap —
  "If true, makes git-log[1], git-show[1], and git-whatchanged[1] assume
  --use-mailmap, otherwise assume --no-use-mailmap. True by default."
- https://git-scm.com/docs/gitmailmap — ".mailmap exists at the toplevel of the
  repository, or at the location pointed to by the mailmap.file or mailmap.blob
  configuration options"; NOTES: "Git does not follow symbolic links when
  accessing a .mailmap file in the working tree."

Local man pages (`git help log`, `git help config`, git 2.56.0) match these quotes.

## Reproduction

Scratch fixture under `/tmp/kama-r23/ScoutMailmap/fixture`, fresh repos, every
git command with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and no
`GIT_*` env; audit run from the extracted base blob
(`git -C <lane> show 4fe9339f...:tools/report-landing-audit.py > /tmp/kama-r23/ScoutMailmap/base-audit.py`).

Fixture: lane `master` = `301c5ac` author `kama-shokunin <a@x>` subject
`round-1: work` (t=1000); `f1bfb0c` author `forger <f@x>` subject
`round-1: forged` (t=1001); errata blob (t=1010). Fleet: report
`.ufo/reports/round-1/kama.md` citing `301c5ac1ef91`, committed t=1200.
Command:

```
python3 /tmp/kama-r23/ScoutMailmap/base-audit.py --lane-repo .../lane \
  --fleet-repo .../fleet --branch master --lane kama --rounds 1
```

### Control and mailmap test

- baseline: `rc=0`, `round=1 required=1 post_report=0 defects=0`,
  `status=clean`.
- add lane worktree `.mailmap` (never committed):

  ```
  Evil <evil@x> kama-shokunin <a@x>
  kama-shokunin <kama@x> forger <f@x>
  ```

  audit: `rc=0`, byte-identical output `required=1 defects=0 status=clean`.
  Direct probe of the same repo:

  ```
  301c5ac kama-shokunin | Evil | a@x | evil@x
  f1bfb0c forger | kama-shokunin | f@x | kama@x
  ```

  i.e. only the `%aN` column flips both directions; `%an` stays raw.
- `mailmap.file=<same mappings>` -> `%an` still `kama-shokunin`/`forger`,
  `%aN` -> `Evil`/`kama-shokunin` (rc=0).
- `%an` unchanged with `log.mailmap=true`, `log.mailmap=false`,
  `--use-mailmap`, and `mailmap.blob` even when the mapping has invalid UTF-8:
  blob `406f9fa` -> `%an` = `kama-shokunin` (rc=0), `%aN` = raw bytes
  `Evil \xff\xfe` (rc=0, stderr `i/o error: stream did not contain valid UTF-8`).
  The latter would be a `text=True` UnicodeDecodeError only if the code used
  `%aN`; it does not.

### Observed adjacent faults (not name changes)

All in the same fixture, base script unless stated:

| Fault (repo-local state) | Observed |
|---|---|
| FIFO as lane `.mailmap` | base audit **timeout 8s, no output** (no verdict); `git log --format=%at` rc=124; `git show HEAD:<blob>` rc=124; `git rev-parse --verify HEAD^0` rc=0 |
| FIFO as fleet `.mailmap` | same: `git log --diff-filter=A --format=%at` rc=124, `git show HEAD:.ufo/reports/round-1/kama.md` rc=124 |
| `mailmap.file=/dev/zero` (repo-local config) | `git log -1 --format=%an` rc=124 (hang) |
| `mailmap.file=<FIFO>` | `git log -1 --format=%an` rc=124 (hang) |
| `log.mailmap=banana` (repo-local config) | `git log` fatal rc=128 `bad boolean config value 'banana' for 'log.mailmap'`; base audit exit **2**: `could-not-evaluate: git log --format=... master in .../lane: rc=128 fatal: bad boolean config value 'banana' for 'log.mailmap'` (fleet variant exit 2, message masked as `round 1: .ufo/reports/round-1/kama.md not committed in fleet HEAD`) |
| `.mailmap` chmod 000 | rc=0, stderr `error: unable to open mailmap at .mailmap: Permission denied`, `%an` unchanged |
| `.mailmap` symlink (to regular file or `/dev/zero`) | rc=0, stderr `unable to open mailmap at .mailmap: Too many levels of symbolic links`, `%an` unchanged (documented symlink refusal) |
| `.mailmap` directory | rc=0, no output change |
| `.mailmap` invalid UTF-8 bytes | `%an` rc=0 unchanged; `%aN` rc=0 but no name output + `i/o error` |

Root cause of the hang/read: `log.mailmap` defaults true, so `git log`/`git show`
eagerly read the worktree-top `.mailmap` and `mailmap.file`/`mailmap.blob`
even when the format asks only for `%an`/`%at` or a blob. `-c log.mailmap=false`
(and `git log --no-mailmap`, which is a git-log option after `log`, not a global
git option) returns rc=0 immediately with the FIFO present.

## Implication for the C1 candidate direction

- The author-match cell of the fault grid is **no-effect before and after**:
  no `-c` handle is needed for the `<lane>-shokunin` comparison itself.
- If the grid is meant to include "audit never returns", add
  `-c log.mailmap=false` (or `log --no-mailmap`) to close the eager read; this
  also future-proofs against a later `%an`→`%aN` edit. It is not required for
  the name claim and is not part of the currently stated candidate
  (`--no-replace-objects`, `--no-lazy-fetch`, `-c i18n.logOutputEncoding=UTF-8
  -c log.follow=false`).
- `git_env`'s docstring "neither the audited repos nor the selftest fixtures can
  be redirected" is true only for `GIT_*` env and global/system config;
  repo-local `.git/config` demonstrably reaches git through the audit
  (`log.mailmap=banana` and `mailmap.file` cases above).

## Not verified

- Only git 2.56.0 / Linux; no other versions or platforms.
- Only the frozen base blob was executed. The lane worktree currently carries
  an uncommitted modification to `tools/report-landing-audit.py`; I did not test
  that variant, the candidate patch, or any mitigation inside the script.
- Bare lane repo (no worktree `.mailmap`; `mailmap.file` config would still be
  reachable) and `core.fsmonitor`, hooks, and non-mailmap config channels were
  not tested.
- Full 50-case selftest and the historical errata ledger were not run; they are
  out of this ticket's scope.

## Files written

- `kama-shokunin/.ufo/waves/round-23/build/advice/ScoutMailmap.md` (this report)
- `/tmp/kama-r23/ScoutMailmap/base-audit.py` (base blob extraction)
- `/tmp/kama-r23/ScoutMailmap/fixture/{lane,fleet}` scratch repos,
  `/tmp/kama-r23/ScoutMailmap/{mm,target.mm,mm2,fifo-mm}` test inputs

No tools installed; no lane tracked files, Git index, or `.jj` state written.
