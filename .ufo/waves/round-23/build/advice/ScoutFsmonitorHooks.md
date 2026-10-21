# Scout — repo-local execution channels: fsmonitor / hooksPath / diff.external / textconv / filters / alternateRefsCommand

Channel: repository-local **configuration** that names a program (hook, fsmonitor
hook, external diff, textconv, filter driver, alternate-refs command), asking
whether any runs while `tools/report-landing-audit.py` invokes git. Probed
against the frozen base blob, not the moving worktree:

- `git show 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
  → `/tmp/kama-r23-scout-fs/audit_base.py`,
  sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`
  (base blob line numbers below; the lane worktree already differed at probe
  time — it carries the `GIT_ISOLATION` candidate — so all runs used the frozen
  bytes). git 2.56.0, Linux, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, fixtures only under `/tmp/kama-r23-scout-fs`.

## Verdict

**no-effect** — for all six channels, on every git invocation the auditor
actually makes at base: no execution, no crash, no verdict flip. All six are
demonstrably live under their triggering commands (positive controls below), but
none of those triggers occurs here: `core.hooksPath`/fsmonitor/filters need index
refresh or checkout; `diff.external`/textconv need patch output (and `--ext-diff`
for `log`); `alternateRefsCommand` needs alternate-ref advertisement. The auditor
requests none of these, so no repo-configured program is reached.

All repeated-run output was byte-identical to the no-channel baseline; a
deliberately defective draft stayed `failed` (exit 1) with identical stdout under
all channels. Repo-local config that is *malformed* is a typed refusal
(`could-not-evaluate`, exit 2, no traceback), never a verdict.

## Exact invocations the auditor makes (observed)

`GIT_TRACE` is stripped by `git_env()` (`:79-83`), so I logged argv with a
pass-through shim (`PATH=/tmp/kama-r23-scout-fs/shim:$PATH`, script execs
`/usr/bin/git`). Audit run over a clean fixture with every channel configured:

```
-C <lane> rev-parse --verify master^{commit}
-C <fleet> rev-parse --verify HEAD^{commit}
-C <lane> ls-tree master -- corpus/SOURCES.md
-C <lane> cat-file blob 1939db43...
-C <fleet> show HEAD:.ufo/reports/round-23/kama.md
-C <fleet> log --diff-filter=A --format=%at -- .ufo/reports/round-23/kama.md
-C <lane> cat-file --batch-check        (x3, full + bare + peeled lookups)
-C <fleet> cat-file --batch-check       (x3)
-C <lane> log --format=%H%an%at%s master
-C <lane> show master:registry/report-landing-errata.tsv
```

`--rounds 23-` prepends `-C <fleet> ls-tree -r --name-only HEAD -- .ufo/reports`
and changes nothing else. No `status`/`diff`/`add`/`commit`/`checkout`, no `-p`,
no `--ext-diff`, no `--textconv`, no `cat-file --filters`, no
`--alternate-refs`. Base call sites: `git()` `:87-97`; `cat-file --batch-check`
`:114`; `log` `:148`; `log --diff-filter=A` `:166`; `ls-tree` `:211`;
`cat-file blob` `:222`; `show HEAD:<rel>` `:266`; `show <branch>:<errata>`
`:339`; `ls-tree -r` `:381`; `rev-parse --verify` `:403-404`. `git add`/`commit`
exist only in `_commit()` for selftest temp repos (`:456-467`).

## Fault/probe grid (base blob)

Harness: `out/CloseKama22.ScoutFsmonitorHooks/probe.sh`; raw
`results.tsv`, `controls-markers.txt`, `git-argv.log`. Every fixture: lane commit
authored `kama-shokunin` / subject `round-23: …`, fleet report
`.ufo/reports/round-23/kama.md` with a resolvable `## Landed changes` citation,
committed empty errata. Baseline:
`python3 audit_base.py --lane-repo run/base/lane --fleet-repo run/base/fleet --rounds 23`
→ rc 0, `summary reports=1 defects=0 … status=clean`.

| channel (repo-local) | setting used | audit rc / status / markers | positive control on same fixture |
|---|---|---|---|
| fsmonitor (pathname) | `core.fsmonitor=<abs>/fsmon-legacy.sh` | 0 / clean / **0** | `git status --porcelain` → 2 calls: `fsmon-legacy\|2 <token>`, `fsmon-legacy\|1 <timestamp>` (v2 then v1) |
| fsmonitor (`true`) | `core.fsmonitor=true`, exec `hooks/fsmonitor-watchman` via `core.hooksPath` | 0 / clean / **0** | `git status` → only `hook-post-index-change\|0 0`; fsmonitor hook not called in this Linux fixture |
| hooksPath | 7-hook set: pre-commit, post-commit, post-checkout, post-index-change, reference-transaction, post-merge, pre-push | 0 / clean / **0** | `status` 1 marker; `commit --allow-empty` 9 markers; `checkout -b` 16 markers |
| diff.external | `diff.external=<abs>/extdiff.sh` | 0 / clean / **0** | `git diff HEAD~1 HEAD` 1; `git log -p -1` **0**; `git log -p -1 --ext-diff` 1; `git show --ext-diff HEAD` 1 |
| textconv | `diff.tcdrv.textconv=<abs>/textconv.sh` + committed `*.md diff=tcdrv` | 0 / clean / **0** | `git log -p -1 -- .ufo/reports/round-23/kama.md` 1; `git diff --textconv -- note.md` 2; blob `git show HEAD:…kama.md` **0** |
| filter (clean/smudge) | `filter.evil.clean/.smudge`, `required=true` + committed `*.md filter=evil` | 0 / clean / **0** | `git add note.md` 2 (clean); `git cat-file --filters HEAD:note.md` 1 (smudge); `rm`+`git checkout -- note.md` 2 (one smudge, one clean) |
| filter (process) | `filter.evil.process=<abs>/filter-process.sh`, `required=true` | 0 / clean / **0** | `git add note.md` → 1 `filter-process\|` marker, then rc 128 |
| alternateRefsCommand | alternates present + `core.alternateRefsCommand=<abs>/altrefs.sh` | 0 / clean / **0** | `git rev-list --alternate-refs HEAD` 1; `git log --alternate-refs` 1; `rev-parse --all` 0; `upload-pack --advertise-refs` 0 |
| all channels, fleet | all of the above on the fleet repo | 0 / clean / **0**, stdout identical to baseline | `status` 5 markers |
| all channels, fleet+lane | all of the above also on the lane repo (incl. lane `core.hooksPath`, filter, alternateRefsCommand, alternates, `.gitattributes`) | 0 / clean / **0**, stdout identical to baseline | — |
| open range | all channels, fleet+lane, `--rounds 23-` | 0 / clean / **0** (marker count unchanged) | — |
| defective draft parity | draft with fabricated 40-hex, `--report 23=…` | base rc 1 `status=failed`, 2 defects; all-channels rc 1, identical stdout | `diff` empty |
| malformed local config | appended `[bad-section` to fleet `.git/config` | **rc 2**: `could-not-evaluate: git rev-parse --verify HEAD^{commit} … rc=128 fatal: bad config line 6 in file .git/config`; 0 `Traceback` | — |
| missing-command edges | hooksPath→regular file; `core.fsmonitor`→missing; `alternateRefsCommand`→missing (alternates present); `diff.external`→missing; textconv→missing; filter clean→missing `required=true` | each 0 / clean / **0** | — |

Combined fixture audit output (byte-identical to baseline):

```
round=23 required=1 post_report=0 defects=0
summary reports=1 defects=0 corrected=0 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean
```

## Why (governing doc text, fetched 2026-10-21)

- fsmonitor — https://git-scm.com/docs/git-config :
  "the built-in file system monitor can speed up Git commands that need to refresh the Git index (e.g. git status)"
- githooks fsmonitor-watchman — https://git-scm.com/docs/githooks :
  "This hook is invoked when the configuration option core.fsmonitor is set to .git/hooks/fsmonitor-watchman"
- hooksPath — https://git-scm.com/docs/git-config :
  "By default Git will look for your hooks in the $GIT_DIR/hooks directory."
- diff.external — https://git-scm.com/docs/git-config :
  "If this config variable is set, diff generation is not performed using the internal diff machinery, but using the given command."
- textconv — https://git-scm.com/docs/gitattributes :
  "only git diff and the git log family of commands (i.e., log, whatchanged, show) will perform text conversion."
- filter — https://git-scm.com/docs/gitattributes :
  "Upon checkout, when the smudge command is specified, the command is fed the blob object from its standard input"
- alternateRefsCommand — https://git-scm.com/docs/git-config :
  "When advertising tips of available history from an alternate, use the shell to execute the specified command instead of git-for-each-ref."

The shipped git 2.56.0 man pages (`man 1 git-config`, `man 5 gitattributes`,
`man 5 githooks`) match these sentences; docs were fetched from git-scm.com the
same day.

## Implications for the round-23 candidate

- None of the six needs an isolation flag for the current command set: the
  candidate `GIT_ISOLATION` (`--no-replace-objects --no-lazy-fetch
  -c i18n.logOutputEncoding=UTF-8 -c log.follow=false`) neither covers nor needs
  to cover them, because they never engage.
- They become live only if the auditor grows an index/ref-refresh command
  (`status`, `add`, `commit`, `checkout` → hooks, fsmonitor, filters),
  patch output (`-p`/`--stat` plus `--ext-diff`/textconv), `cat-file --filters`,
  or `--alternate-refs` (alternateRefsCommand). The selftest already runs
  `git add`/`commit`, but only inside its own `TemporaryDirectory` repos
  (`:474-505`), so audited-repo hooks/filters cannot reach it.
- `objects/info/alternates` object borrowing is a separate, real channel
  (`advice/ScoutAlternates.md`); my alternateRefs fixture used an alternate only
  to make `core.alternateRefsCommand` applicable.

## Not verified

- Did not run `--selftest`; read base `:456-505` only (selftest commits in its
  own temp repos).
- `core.fsmonitor=true` built-in-daemon behavior beyond marker absence on Linux
  (doc says built-in daemon is Windows/macOS only; only the pathname hook form
  was proven live).
- `upload-pack --advertise-refs` did not invoke `alternateRefsCommand` in my
  fixture; `rev-list/log --alternate-refs` did. Not needed for the audit.
- Only representative filter/textconv options (`clean`, `smudge`, `process`,
  `required`, single `textconv`); no `cachetextconv`, no filter-protocol success
  path, no relative `core.hooksPath`, no bare/worktree-odd repos.
- git 2.56.0 on Linux only; hook/filter/fsmonitor platforms and versions vary,
  but the auditor's commands have no hook/diff/filter triggers on any platform.

No tools installed. No subagents, no REA. No writes to the lane, fleet, sibling
lanes, or config. Files written:
`.ufo/waves/round-23/build/advice/ScoutFsmonitorHooks.md`,
`.ufo/waves/round-23/build/out/CloseKama22.ScoutFsmonitorHooks/{probe.sh,results.tsv,controls-markers.txt,git-argv.log,combined.shim.out,environment.txt}`;
scratch under `/tmp/kama-r23-scout-fs/`.
