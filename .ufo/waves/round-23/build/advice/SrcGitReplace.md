# SrcGitReplace — git-replace registry draft (round 23, C1 calibration)

Author seat: CloseKama22.SrcGitReplace (leaf, no dispatch). `corpus/SOURCES.md` was NOT edited.
This file is a draft for L1 integration. Access date for every source below: 2026-10-21.
Installed git: 2.56.0 (`git --version`, observed 2026-10-21). No tools installed or updated.

## 1. Pages opened

| Page | Title shown | Version shown | Used for |
|---|---|---|---|
| https://git-scm.com/docs/git-replace | `Git - git-replace Documentation` | version list "2.56.0 no changes"; "git-replace last updated in 2.55.0" | replace-ref honour and disable (faults c, d) |
| https://git-scm.com/docs/git | `Git - git Documentation` | "git last updated in 2.56.0" | global `--no-replace-objects`, `--no-lazy-fetch`, env vars (c, d, e) |
| https://git-scm.com/docs/git-config | `Git - git-config Documentation` | "git-config last updated in 2.56.0" | `core.useReplaceRefs`, `i18n.logOutputEncoding`, `core.sshCommand` (a, c, d, e) |

Read method: `read` on each URL (reader text), exact quotes taken from the fetched copies. Nothing was
probed or executed beyond `git --version`.

## 2. Duplicate check

- `grep` over `corpus/SOURCES.md` for `git-replace|git-config|docs/git |no-lazy|logOutputEncoding|sshCommand|useReplaceRefs|GIT_NO_REPLACE` returned **no matches** (2026-10-21). No existing row cites git-replace, git(1) or git-config.
- Adjacent rows, distinct pages, NOT duplicates: S032 git-show; S033, S071, S083 git-cat-file; S070, S082 gitrevisions; S073, S085 git-log.
- **Peer collisions (not existing rows, but same id and/or same page):**
  - `SrcGitConfig.md` drafts a git-config row as **S089** (same URL). My git-config contribution is therefore a supplement quote to that row, not a second row (see §4, S-config fold-in).
  - `SrcGitLogFollow.md` drafts **S089** and **S090** on git-log. Different page; no overlap with mine, but the id collides.
  - `SrcGitRepoLayout.md` drafts **S089** on gitrepository-layout. Different page; id collides.
  - My drafts below use **S089** and **S090**. L1 MUST assign final ids at admission; the next unused id is shared by all these drafts and only one can take it.
- Column contract: the registry is **11 columns** (`SOURCES.md:11`; CORPUS.md §SOURCES.md: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`; census checks NF==13 = 11 cells plus edge pipes). The assignment's "12-column" wording is a miscount. Drafts use 11 columns.

## 3. Candidate registry rows (NOT written to SOURCES.md)

Provisional ids: S089 and S090 (collide with peers; L1 renumbers).

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S089 | Git git-replace manual — https://git-scm.com/docs/git-replace | docs | A | which Git commands honour replace refs by default and how to disable them per invocation, at Git 2.56.0; not replacement safety or graft-file policy | DESCRIPTION paragraphs "Replacement references will be used by default…", "It is possible to disable…" and the `git cat-file commit foo` example; DESCRIPTION "Adds a *replace* reference in `refs/replace/` namespace"; page "Git - git-replace Documentation", "git-replace last updated in 2.55.0", version list 2.56.0 no changes; opened 2026-10-21 | Every command honours `refs/replace/<sha>` by default except reachability traversal (prune, pack transfer, fsck), so a replaced commit can show its replacement; `--no-replace-objects` or `GIT_NO_REPLACE_OBJECTS` turns this off for one invocation. | queued | 2026-10-21 | on-release | — |
| S090 | Git git manual, global options and environment — https://git-scm.com/docs/git | docs | A | git(1) global switches and environment variables that disable replace refs and on-demand promisor fetch, at Git 2.56.0; not which promisor remote is trusted, not config keys | SYNOPSIS (`[--no-replace-objects] [--no-lazy-fetch]` before `<command>`); OPTIONS `--no-replace-objects`, `--no-lazy-fetch`; ENVIRONMENT VARIABLES `GIT_NO_REPLACE_OBJECTS`, `GIT_NO_LAZY_FETCH`; page "Git - git Documentation", "git last updated in 2.56.0"; opened 2026-10-21 | Both switches are global, go before the subcommand, and have environment equivalents: `--no-lazy-fetch` / `GIT_NO_LAZY_FETCH` stops on-demand fetch from a promisor remote, so an object lookup stays local. | queued | 2026-10-21 | on-release | — |

### Fold-in for the peer git-config row (not a new row)

`SrcGitConfig.md` (draft S089, same URL) omits the replace-ref config key. Add this quote to its
Gate table, fault (c)/(d) column:

- §core.useReplaceRefs (fetched copy line 3299): "If set to `false`, behave as if the `--no-replace-objects` option was given on the command line." (16 words) — supports (c)/(d) as the config-level disable.

## 4. Gate lines

### S089 Gate (git-replace)
- URL: https://git-scm.com/docs/git-replace · access date 2026-10-21 · page title "Git - git-replace Documentation" · version "2.56.0 no changes", "git-replace last updated in 2.55.0".
- Quote A (DESCRIPTION, 21 words): "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)."
- Quote B (DESCRIPTION, 20 words): "It is possible to disable the use of replacement references for any command using the `--no-replace-objects` option just after *git*."
- Quote C (DESCRIPTION, 15 words): "The name of the *replace* reference is the SHA-1 of the object that is replaced."
- C1 fault cases supported: **(c)** omitted commit hidden by a replace ref (Quote A: default honour; the `cat-file commit foo` example shows the replacement is what is displayed). **(d)** fabricated `refs/replace/<40-hex>` (Quote C: the ref is keyed by a SHA-1; Quote A: all commands honour it by default). Quote B supplies the disable that the fixed script must use. Does NOT support (a), (b) or (e).
- [INFERENCE, unverified by probe]: the page's exception list names prune, pack transfer and fsck but not `rev-list`; so the audit's `rev-list`-based traversal is not excluded and replacement applies to it. Observed (c) behaviour is own-work until the L1 probe row confirms it.

### S090 Gate (git(1))
- URL: https://git-scm.com/docs/git · access date 2026-10-21 · page title "Git - git Documentation" · "git last updated in 2.56.0".
- Quote A (OPTIONS `--no-lazy-fetch`, 11 words): "Do not fetch missing objects from the promisor remote on demand."
- Quote B (OPTIONS `--no-replace-objects`, 12 words): "This is equivalent to exporting the `GIT_NO_REPLACE_OBJECTS` environment variable with any value."
- Quote C (ENVIRONMENT VARIABLES `GIT_NO_LAZY_FETCH`, 21 words): "Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand."
- C1 fault cases supported: **(c)/(d)** — Quote B plus the SYNOPSIS placement give the global per-invocation disable for the fixed script. **(e)** — Quotes A and C give the lazy-fetch disable (`--no-lazy-fetch` argv or `GIT_NO_LAZY_FETCH=1` env) that a fix would use. Does NOT support (a) or (b).
- Caution for L1 (matches SrcGitConfig's flag 1): these quotes say what the switch disables. They do NOT say that lazy fetch runs `core.sshCommand`. The page on git-config scopes `core.sshCommand` to "`git fetch` and `git push`" (fetched copy line 2782). The probe's causal claim for (e) stays own-work.

## 5. C1 fault coverage of this draft

| Fault | Covered by | Note |
|---|---|---|
| (a) i18n.logOutputEncoding ISO-8859-1 traceback | none of mine; S-config (peer) `i18n.logOutputEncoding` quote | — |
| (b) invalid UTF-8 committed report | none | git-log `--encoding` text is a peer's S089-draft (SrcGitLogFollow), not mine |
| (c) git replace of omitted commit | S089 (A, B, C), S090 (B, SYNOPSIS), config fold-in | documented behaviour; probe observation is own-work |
| (d) fabricated refs/replace/<40-hex> | S089 (A, C), S090 (B), config fold-in | same |
| (e) lazy fetch + core.sshCommand | S090 (A, C) for the disable; sshCommand scope caveat | causal execution claim not supported by the page |

## 6. Not verified / out of scope

- No fixture, probe, selftest or audited-repo command was run. No lane or fleet repo was touched.
- Quotes were read from the reader-text fetch (2026-10-21), not cross-checked against a local `man git-replace` page.
- The `rev-list` inference in S089's Gate is [INFERENCE] and is not verified.
- Peer rows not reviewed beyond the duplicate/id collision check above (only their files read).
- Git-replace's CAVEATS (replace objects turn off commit-graph read/write) and BUGS sections were read but are not C1 faults; not drafted.
- The peers SrcPartialClone and SrcGitConfig were messaged (2026-10-21) to avoid duplicate git(1) / git-config rows; no reply was received before this report.

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitReplace.md` (this file).
- No other files written. `corpus/SOURCES.md` not edited. No installs.

## 8. Revision (2026-10-21, after peer messages): rows withdrawn

- **S089 (git-replace) and S090 (git(1)) are WITHDRAWN as candidate rows.** CloseKama22.SrcPartialClone opened git(1), git-replace and git-config on 2026-10-21 and owns those rows (its provisional S090-S092). Do not admit the S089/S090 rows above.
- **git-config i18n.logOutputEncoding and core.sshCommand rows are withdrawn.** CloseKama22.SrcGitConfig owns git-config (its draft S089). Its scope caveat stands: `core.sshCommand` is documented for `git fetch` and `git push` only; the page does not say lazy fetch uses it.
- **Retained contribution:** the verbatim quotes in §4 (git-replace DESCRIPTION; git(1) OPTIONS `--no-replace-objects` and `--no-lazy-fetch`; ENVIRONMENT `GIT_NO_LAZY_FETCH`) plus the core.useReplaceRefs quote in §3 are cross-check material for the owning seats. Each quote is verbatim from the 2026-10-21 fetch, the same text I observed, and I found no differing quote to report.
- Still open for the owning seats: the [INFERENCE] that `rev-list` traversal is not in the git-replace exception list. It is unverified.
- Files written by this revision: this file only.
