# SrcGitEnv — round-23 candidate SOURCES rows for the C1 git-environment claim

Scribe scope: draft only. `corpus/SOURCES.md` was NOT edited. No row is admitted until the L1 integrator copies it under the round-23 Gate.

Access date for every source below: **2026-10-21**.

## Contract check (discrepancy)

- The brief says "12-column row contract". The live contract has **11 columns**: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by` (`corpus/SOURCES.md` lines 11–12; `CORPUS.md` §SOURCES.md, Shape table line 86–87). The drafts below use those 11 columns. Flagged for L1.
- Rule 2 (CORPUS.md): new rows take the next unused id. Last used id is S088, so drafts use S089–S091.
- Rule (CORPUS.md, `status`): `mined` requires ≥1 citing `used-by` path. No knowledge entry or lesson cites these rows yet, so drafts are `queued` with `used-by` `—`. The integrator sets `mined` when a lesson cites them.

## Sources opened this run

| URL | Page title shown | Version shown |
|---|---|---|
| https://git-scm.com/docs/git | "Git - git Documentation" | "git last updated in 2.56.0"; 2.56.0 dated 2026-09-28 |
| https://git-scm.com/docs/git-replace | "Git - git-replace Documentation" | "git-replace last updated in 2.55.0"; 2.56.0 "no changes" |
| https://git-scm.com/docs/git-config | "Git - git-config Documentation" | "git-config last updated in 2.56.0"; 2.56.0 dated 2026-09-28 |

Also read: `corpus/SOURCES.md` header (lines 1–12), rows S075–S088 (lines 87–100), contract tail (lines 299–318); `CORPUS.md` lines 63–133.

## Candidate rows (draft, not written to SOURCES.md)

Row S089
```
| S089 | Git git(1) manual — https://git-scm.com/docs/git | docs | A | git(1) global switches that disable replacement refs, lazy promisor fetch and config-file reads at Git 2.56.0; not a sandbox guarantee | §--no-replace-objects and §--no-lazy-fetch (options); environment-variable entries GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM, GIT_NO_REPLACE_OBJECTS, GIT_NO_LAZY_FETCH; page "Git - git Documentation", "git last updated in 2.56.0" (2.56.0 dated 2026-09-28); opened 2026-10-21 | Each switch has a documented env equivalent: --no-replace-objects equals GIT_NO_REPLACE_OBJECTS, --no-lazy-fetch equals GIT_NO_LAZY_FETCH=1, and GIT_CONFIG_GLOBAL or GIT_CONFIG_NOSYSTEM skip user or system config files. | queued | 2026-10-21 | on-release | —
```

Row S090
```
| S090 | Git git-replace manual — https://git-scm.com/docs/git-replace | docs | A | which Git commands honour refs/replace/ by default, and how to disable it, at Git 2.56.0; not a claim about other replace mechanisms | §DESCRIPTION paragraphs "Replacement references will be used by default" and "It is possible to disable the use of replacement references", with the git --no-replace-objects cat-file example; page "Git - git-replace Documentation", "git-replace last updated in 2.55.0" (2.56.0 "no changes"); opened 2026-10-21 | Replacement refs apply to every command except reachability traversal (prune, pack transfer, fsck), so a replaced commit shows through cat-file and log until --no-replace-objects is given. | queued | 2026-10-21 | on-release | —
```

Row S091
```
| S091 | Git git-config manual — https://git-scm.com/docs/git-config | docs | A | repository-settable config keys that change the fetch or push transport command and the decoding of git log output, at Git 2.56.0; not a claim about lazy fetch | §core.sshCommand, §i18n.logOutputEncoding and §log.follow entries; page "Git - git-config Documentation", "git-config last updated in 2.56.0" (2.56.0 dated 2026-09-28); opened 2026-10-21 | core.sshCommand replaces ssh for fetch and push, and i18n.logOutputEncoding sets the encoding commit messages are converted to for git log; both are config keys a repository can set. [INFERENCE] The page does not say lazy fetch runs sshCommand; that is the L1 probe's observation. | queued | 2026-10-21 | on-release | —
```

## Gate (URL, access date, located quote ≤25 words, C1 fault supported)

**S089** — https://git-scm.com/docs/git — 2026-10-21
- Quote (§--no-lazy-fetch, option text): "This is equivalent to setting the `GIT_NO_LAZY_FETCH` environment variable to `1`." (12 words). Supports: fault (e) control; GIT_NO_LAZY_FETCH stops lazy fetch.
- Quote (§GIT_NO_LAZY_FETCH entry): "Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand." (21 words). Supports: fault (e).
- Quote (§GIT_NO_REPLACE_OBJECTS entry): "Setting and exporting this environment variable tells Git to ignore replacement refs and do not replace Git objects." (18 words). Supports: faults (c) and (d).
- Quote (§GIT_CONFIG_GLOBAL entry): "Can be set to `/dev/null` to skip reading configuration files of the respective level." (14 words). Supports: the isolation control the brief requires (GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM); no observed fault itself.

**S090** — https://git-scm.com/docs/git-replace — 2026-10-21
- Quote (§DESCRIPTION): "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)." (21 words). Supports: faults (c) and (d). Note: the boundary means the replaced-commit fault reaches cat-file and log, not reachability walks.

**S091** — https://git-scm.com/docs/git-config — 2026-10-21
- Quote (§core.sshCommand): "If this variable is set, git fetch and git push will use the specified command instead of ssh" (18 words). Supports: fault (e) only as the key that redirects transport. The page does not document that lazy fetch runs it; that remains L1 probe evidence.
- Quote (§i18n.logOutputEncoding): "Character encoding the commit messages are converted to when running git log and friends." (14 words). Supports: fault (a).
- Quote (§log.follow): "If `true`, `git` `log` will act as if the `--follow` option was used when a single <path> is given." Supports: candidate control `log.follow=false` only. It is NOT an observed fault in the L1 grid, so it is not sole support for any admitted C1 case.

## Fault-case map

| Case | Observed fault (L1 probe) | Registry support |
|---|---|---|
| (a) | i18n.logOutputEncoding=ISO-8859-1 plus non-ASCII subject → UnicodeDecodeError | S091 (encoding key and its scope) |
| (b) | invalid UTF-8 in committed report → traceback | none. No git-docs row covers it; it is Python decode behaviour. Gap. |
| (c) | git replace of omitted round commit → false clean | S089, S090 |
| (d) | refs/replace/<fabricated 40-hex> resolves → false clean | S089, S090 |
| (e) | promisor remote + core.sshCommand → lazy fetch executed command | S089 (--no-lazy-fetch), S091 (sshCommand key; lazy-fetch link is not documented there) |
| control | GIT_CONFIG_GLOBAL / GIT_CONFIG_NOSYSTEM isolation | S089 |
| candidate | log.follow=false | S091 anchor only; no observed fault |

## Duplicate check against existing rows

- https://git-scm.com/docs/git-log: already S073 (superseded by S085). No new row. Its `--diff-filter`/`%at` claims are not used here.
- https://git-scm.com/docs/git-cat-file: already S033, S071, S083. The `--no-lazy-fetch` cat-file sentence sits on the git(1) page, so it is covered by S089. No new cat-file row.
- https://git-scm.com/docs/gitrevisions: already S070, S082. Not used here.
- https://git-scm.com/docs/git-show: already S032. Not used here.
- No existing row cites the git(1) page, git-replace, or git-config. S089–S091 are not duplicates.
- Overlap note: S089 partly restates the cat-file lazy-fetch sentence. Keep S089 as the canonical row for the option and env pair; S033/S083 stay as cat-file mechanics rows.

## Did NOT verify

- No fixture was run; no git command was executed for this report. C1 fault observations come from the L1 probe as briefed.
- The glossary "promisor remote" definition was not located. The grep of the glossary artifact returned only "reachability bitmaps". No row for the glossary is drafted.
- That lazy fetch executes core.sshCommand is not documented on the git-config page. It is L1 probe evidence only.
- Fault (b) has no git-docs support; it needs a Python-decoding source (not drafted).
- Every quote above was read from the fetched web HTML of git-scm.com (2.56.0 manuals), not from an installed `git` binary's man pages; the local git manual was not compared.

## Tools

No tools installed or updated.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitEnv.md` (this report).
- `corpus/SOURCES.md` was not modified.
