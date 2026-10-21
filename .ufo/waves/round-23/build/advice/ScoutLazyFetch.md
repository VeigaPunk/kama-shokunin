# ScoutLazyFetch — promisor / partial-clone lazy fetch as a repo-local state channel

Base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, git 2.56.0-Linux.
Audited script: `tools/report-landing-audit.py` at that commit, extracted with
`git show 4fe9339f:tools/report-landing-audit.py` (sha256
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`).
Note: the lane worktree copy is currently modified (uncommitted `GIT_ISOLATION`
hunk, another seat's work); every audit number below is from the **committed
base blob**, run as `/tmp/kama-r23-lf/audit-base.py`.

## Verdict

**executes + affects-verdict (both directions).** In a repo whose local config
declares a promisor remote, the base audit runs `git fetch` against that remote
on ordinary audits and executes whatever command the repo's config names
(`remote.<name>.uploadpack`, `core.sshCommand`, `core.gitProxy`,
`credential.helper`); a repo-local URL repoint makes a fabricated citation
resolve -> **false clean (exit 0)**. `--no-lazy-fetch` suppresses the execution
and the false clean completely (0 marker invocations in every case tested), but
by itself turns a promisor-supplied legitimate object into a **false
`unresolved-full-hash` (exit 1)** and downgrades an exit-2 refusal to that
verdict. `--no-lazy-fetch` is necessary, not sufficient: the script needs a
promisor/partial-clone detection that raises `EvalError` (exit 2).

## Mechanism (observed, not inferred)

With `GIT_TRACE=1`, `git -C <repo> cat-file --batch-check` on a missing object
in a promisor repo spawns:

```
git -c fetch.negotiationAlgorithm=noop fetch origin --no-tags \
    --no-write-fetch-head --recurse-submodules=no --filter=blob:none --stdin
```

so the fetch is a full `git fetch` subprocess reading the audited repo's local
config. Demonstrated with a full clone plus only two local keys
(`remote.origin.promisor=true`, `remote.origin.uploadpack=<marker>`): a
fabricated 40-hex token produced `... missing` rc=0 and **one marker
invocation**. A real partial clone is not required — the promisor declaration
alone is.

Commands in the base audit that trigger it (all measured):

| line | call | triggers? |
|---|---|---|
| 114 | `cat-file --batch-check` (full tokens + `^{commit}` peel) | **yes** — for every token absent from that repo, incl. every lane commit absent from the fleet repo |
| 222 | `cat-file blob <SOURCES blob>` | yes (measured on `cat-file blob`) |
| 266 | `show HEAD:<report>` | **yes** (measured) |
| 339 | `show <branch>:<errata>` | same `show` path (inferred; not separately run) |
| 148 | `log --format=...` | no (commits present under `blob:none`) |
| 166 | `log --diff-filter=A` | no (trees present) |
| 211/381 | `ls-tree` | no with `blob:none`; would fetch trees under `--filter=tree:0` |
| 403/404 | `rev-parse --verify HEAD^{commit}` | no |

Interaction with the script's isolation comment: `git_env` (line 79) strips
`GIT_*` and disables user/system config, but **not repo-local config**. Verified:
running the base audit with caller `GIT_NO_LAZY_FETCH=1` still fired the marker
(`marker=1`) because `git_env` deletes the variable before every git call.
There is no config key that disables lazy fetch (`git help -c | grep -i lazy`
empty; `git-config(1)` documents only `promisor.quiet` as a fetch knob), so
inside the audit the only usable suppression is the global
`git --no-lazy-fetch`.

## Execution channels (all measured through a real lazy fetch)

| repo-local config | observed |
|---|---|
| `remote.origin.uploadpack=/tmp/.../upmark` (+ `file://` URL) | marker ran; `git fetch` fails/uses it as upload-pack |
| `core.sshCommand=/tmp/.../sshmark` (+ `ssh://example.invalid/x`) | ran **twice**: `sshmark ARGS=-G -o SendEnv=GIT_PROTOCOL example.invalid`, then `sshmark ARGS=example.invalid git-upload-pack '/x'` |
| `core.gitProxy=/tmp/.../proxymark` (+ `git://example.invalid/x`) | marker ran once |
| `credential.helper=!/tmp/.../credmark` (+ `http://127.0.0.1:PORT/repo`, local server answering 401) | `credmark get` ran; server saw `/repo/info/refs?service=git-upload-pack` |
| `protocol.ext.allow=always` + `remote.origin.url=ext::/tmp/.../extmark %S` | marker ran (`extmark git-upload-pack`); without the allow key git answers `fatal: transport 'ext' not allowed` |

Suppression completeness in git 2.56: global `--no-lazy-fetch` gave **0
invocations** for `cat-file -e`, `cat-file --batch-check`, `cat-file blob`,
`show`, over uploadpack/ssh/proxy/credential channels; `GIT_NO_LAZY_FETCH=1`
likewise (raw git). `--no-lazy-fetch` does not block an explicit
`git fetch origin` (rc 0), which is irrelevant to the audit.

## Audit runs at base (fixture repos under `/tmp`, never the real lane/fleet)

Fixtures: lane origin `A=0279ea14...`, `C=2d8e07d2...`; a foreign repo `evil`
holding commit `E=8576b8ec...` that neither audited repo contains; clean report
cites A, C; "evil" report also cites E in `## Notes`.
Command shape:

```
python3 audit-{base|fix}.py --lane-repo L --fleet-repo F --branch main \
        --rounds 1 --no-errata [--report 1=draft.md]
```

| # | scenario | base | no-lazy variant |
|---|---|---|---|
| S1 | full repos, clean draft | rc0 clean | rc0 clean |
| S2 | full repos, committed report cites foreign E | rc1 `UNCORRECTED unresolved-full-hash 8576b8ec...` | rc1 same (correct) |
| S3 | **partial lane clone, `remote.origin.url` repointed to `evil`, succeeding uploadpack marker** | **rc0 clean, marker=1; E written into the lane object store** | fresh clone: rc1 `UNCORRECTED unresolved-full-hash 8576b8ec...` |
| S4 | partial fleet clone, report blob missing, origin reachable | rc0 clean; fleet-p `in-pack: 5 -> 6` (blob fetched/written) | rc2 `could-not-evaluate: round 1: .ufo/reports/round-1/kama.md not committed in fleet HEAD`; blob still absent |
| S5 | partial fleet + failing uploadpack marker | rc2 refusal **after marker=1 execution** | rc2, marker=0 |
| S6 | clean committed report, *full* fleet repo + `remote.origin.promisor=true` | **rc0 clean, marker=8 lazy-fetch invocations** | rc0 clean, marker=0 |
| S7 | draft cites a real blob object `5626abf0...` (omitted by `blob:none`), promisor reachable | rc0 clean (object fetched) | **rc1 `UNCORRECTED unresolved-full-hash 5626abf0...`** |
| S8 | same blob token, promisor URL nonexistent | rc2 refusal (`cat-file --batch-check ... rc=128`) | **rc1 `UNCORRECTED unresolved-full-hash 5626abf0...`** |

Reading: S3 is a fabricated/foreign citation made to resolve by repo-local
config -> false clean. S4/S6 show silent network traffic and object-store
writes into the audited repo on a *clean* audit, 8 fetches per run even when
nothing is missing locally. S5 shows the execution point clearly (marker fires,
then the audit refuses). S7/S8 are the regression the single-flag fix
introduces: `--no-lazy-fetch` makes `cat-file --batch-check` print `missing`
rc=0 for an object the repo's own promisor would supply, and the audit turns
that unevaluable state into an `unresolved-full-hash` verdict instead of
`EvalError`.

## Governing documentation (accessed 2026-10-21)

- https://git-scm.com/docs/git#Documentation/git.txt---no-lazy-fetch —
  "Do not fetch missing objects from the promisor remote on demand." and
  "This is equivalent to setting the `GIT_NO_LAZY_FETCH` environment variable to `1`."
- https://git-scm.com/docs/git#Documentation/git.txt-GITNOLAZYFETCH —
  "Setting this Boolean environment variable to true tells Git not to lazily
  fetch missing objects from the promisor remote on demand."
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-remoteltnamegtpromisor —
  "When set to true, this remote will be used to fetch promisor objects."
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-remoteltnamegtuploadpack —
  "The default program to execute on the remote side when fetching."
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresshCommand —
  "If this variable is set, `git fetch` and `git push` will use the specified
  command instead of `ssh` when they need to connect to a remote system."
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-uploadpackallowFilter —
  "If this option is set, `upload-pack` will support partial clone and partial
  fetch object filtering."

(`git version 2.56.0`; the option is a **global** git option, placed before
`-C`, as in `git --no-lazy-fetch -C <repo> cat-file ...`.)

## Recommendation for the fix owner

1. Keep `git --no-lazy-fetch` as the first global argument (before `-C`); it is
   the only channel that works, because `git_env` strips `GIT_NO_LAZY_FETCH`.
2. Before evaluating, detect promisor/partial-clone state in each repo
   (`git config --local --get-regexp '^remote\..*\.promisor$'` and
   `extensions.partialClone`) and raise `EvalError` (exit 2) when present — or,
   more surgically, when any token comes back `missing` from a repo that has a
   promisor remote. Without this, S7/S8 become false `unresolved-full-hash`
   verdicts, contradicting "Errors are never verdicts."
3. Do not rely on `GIT_NO_LAZY_FETCH`, `GIT_ALLOW_PROTOCOL` or any config key
   for this; the environment is stripped and no config key exists.
4. The refusal message on a partial fleet repo currently reads
   `.ufo/reports/round-N/kama.md not committed in fleet HEAD` (S4) although it
   is committed but unavailable locally; wording is cosmetic, exit 2 is right.

## Not verified

- Real lane/fleet repos were only read for config keys (`--name-only`); no
  audited-repo fixture was run against them. Today both have **none** of
  `promisor|sshcommand|credential|uploadpack|partialclone|insteadof|hookspath`
  in local config, are not partial clones, and are not shallow.
- Hooks during the internal fetch: trace showed
  `git maintenance run --auto --no-quiet --detach` after `index-pack`; no hook
  (`pre-auto-gc` or other) was exercised.
- No real network host was contacted (`file://`, `ssh://example.invalid`,
  `git://example.invalid`, loopback HTTP only).
- git versions other than 2.56.0 were not tested (older git would reject
  `--no-lazy-fetch`; unmeasured).
- The errata `show branch:ERRATA` path was not run separately; it shares the
  measured `show HEAD:<path>` code path.
- Shallow clones (a different, adjacent channel) were not measured.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutLazyFetch.md` (this report)
- `.ufo/waves/round-23/build/out/ScoutLazyFetch/mk.sh` (fixture builder)
- `.ufo/waves/round-23/build/out/ScoutLazyFetch/matrix2.sh` (base-vs-no-lazy audit matrix)
- `.ufo/waves/round-23/build/out/ScoutLazyFetch/mk-markers.sh` (channel markers, 401 server)
- Scratch (not deliverables): `/tmp/kama-r23-lf/` incl. `audit-base.py` and the
  minimal `audit-fix.py` used only to model `--no-lazy-fetch`.
- No installs or upgrades.

## Addendum — consolidated runnable reproduction

`out/ScoutLazyFetch/repro.sh` rebuilds every fixture from scratch under
`/tmp/kama-r23-lf/repro` (extracting the base blob by commit SHA), and its output
`out/ScoutLazyFetch/repro.log` reproduces the S1–S8 table above exactly, plus the
config-only check: a **full** clone with only `remote.origin.promisor=true` and
`remote.origin.uploadpack=<failing marker>` answers
`0123456789abcdef0123456789abcdef01234567 missing` (rc 0) with `marker=1`.
`mk.sh`, `matrix2.sh`, `mk-markers.sh` are the incremental harness pieces used
during the investigation; `repro.sh` supersedes them for re-running.
No network host is contacted (`file://`, `example.invalid`, loopback only).

Classification detail: **no traceback/crash was observed** on this channel.
A failed lazy fetch surfaces as `EvalError` (exit 2) when the object is
known-missing (e.g. a blob referenced by a present tree), and as
`<token> missing` rc 0 when the token is unknown to the repo — the latter is
the path that turns an unevaluable state into a verdict.
