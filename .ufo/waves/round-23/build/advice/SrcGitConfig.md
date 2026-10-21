# SrcGitConfig — git-config registry draft (round 23, C1 calibration)

Author seat: CloseKama22.SrcGitConfig (leaf, no dispatch). Read-only on the lane:
`corpus/SOURCES.md` was NOT edited. This file is a draft for L1 integration.

## 1. Opened source

- URL: https://git-scm.com/docs/git-config
- Page title shown: `Git - git-config Documentation`
- Version shown: `git-config last updated in 2.56.0`, 2.56.0 dated 2026-09-28 (latest listed)
- Access date: 2026-10-21
- Fetched copy: tool artifact `artifact://65765` (backing file under the omp session log).
  Line numbers below refer to that fetched copy as corroboration; the anchors are section names.

## 2. Row-contract check (CORPUS.md §SOURCES.md, SOURCES.md header)

- The contract is **11 cells**, not 12: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.
  The census awk (`NF!=13`, CORPUS.md lines 137-147) counts 11 cells plus leading/trailing pipes.
- Next unused id: **S089**. `grep` for `S089` in `corpus/SOURCES.md` returns nothing; registry ends at S088.
- Status rule: `mined` requires a non-empty `used-by` path (census line 147 checks each path). No
  knowledge entry or lesson cites git-config yet, so the draft is `queued` with `used-by` `—`.
  It becomes `mined` only when a cited path lands.
- Last rows read: S075–S088 (S087/S088 supersede S075/S076 for Python version scope; no git-config rows there).

## 3. Duplicate check

- `grep` for `git-config|logOutputEncoding|sshCommand|includeIf` over `corpus/SOURCES.md` and `corpus/`: **no matches**.
  No existing row cites git-config. No duplicate.
- Adjacent, NOT duplicates (different pages):
  - S032 git-show; S033 / S071 / S083 git-cat-file (batch and raw output); S070 / S082 gitrevisions; S073 / S085 git-log.
  - S085 covers git-log `%at`/`%ct` and `--diff-filter`. It does not define `log.follow`, which is a git-config
    key. Do not conflate `log.follow` with `git log --follow`.

## 4. Draft candidate row (do not paste into SOURCES.md until L1 integrates)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S089 | Git git-config manual — https://git-scm.com/docs/git-config | docs | A | git-config key semantics and config versus `-c` precedence for kama's C1 fault grid at Git 2.56.0; not fault reproduction, not promisor or lazy-fetch behaviour, not replace-ref or UTF-8 decoding | §i18n.logOutputEncoding; §log.follow; §core.sshCommand; §Includes and §Conditional includes; §CONFIGURATION FILE precedence paragraph; §ENVIRONMENT GIT_CONFIG_COUNT paragraph; §remote.<name>.promisor; page "Git - git-config Documentation", latest version 2.56.0 dated 2026-09-28 | A command-line `-c` outranks GIT_CONFIG_COUNT pairs, which outrank config files, so a fixed `-c` can pin a key such as `i18n.logOutputEncoding`; `core.sshCommand` is documented only for `git fetch` and `git push`, and the page says nothing about lazy promisor fetch. | queued | 2026-10-21 | on-release | — |

Scope note: one distinct page, so one row. If L1 prefers per-claim scope, split into S089–S093 with the
same URL; the census accepts scoped duplicate URLs (its W04 warning class, not a failure). The one-row form is recommended.

## 5. Gate (URL, access date, located quotes ≤25 words, C1 mapping)

Source: https://git-scm.com/docs/git-config — "Git - git-config Documentation", 2.56.0 (2026-09-28), accessed 2026-10-21.

| Anchor (section) | Located quote (≤25 words) | C1 fault case supported |
|---|---|---|
| §i18n.logOutputEncoding (fetched copy 5525-5527) | "Character encoding the commit messages are converted to when running git log and friends." (15 words) | (a) only as the lever. The page does **not** document the ISO-8859-1 decode traceback; that remains a probe observation. |
| §core.sshCommand (2780-2786) | "git fetch and git push will use the specified command instead of ssh" (13 words) | (e) config reachability only. The page does **not** say lazy promisor fetch runs `core.sshCommand`; that claim is unsupported by this source. |
| §remote.<name>.promisor (7481-7484) | "When set to true, this remote will be used to fetch promisor objects." (13 words) | (e) precondition: repo config can make a remote a promisor. Does not establish the sshCommand link. |
| §ENVIRONMENT, GIT_CONFIG_COUNT (838-848) | "These environment variables will override values in configuration files, but will be overridden by any explicit options passed via git -c." (21 words) | Candidate fix mechanism (`-c i18n.logOutputEncoding=UTF-8`). Not a fault. |
| §log.follow (5756-5759) | "If true, git log will act as if the --follow option was used when a single <path> is given." (18 words) | Candidate control (`-c log.follow=false`). **No observed fault in the (a)–(e) grid**; needs its own probe row before it counts. |
| §CONFIGURATION FILE, precedence (755-756) | "with last value found taking precedence over values read earlier." (10 words) | Background for the `-c` ordering above. Not a fault. |
| §Includes (1064-1078) | "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." (22 words) | No fault case. Design-boundary note only: repo-local include paths resolve relative to the including file. |

Not supported by this page (do not cite it for these):
- (b) invalid UTF-8 in a committed report: no UTF-8 decode behaviour is documented here.
- (c) `git replace` of an omitted commit; (d) `refs/replace/<40-hex>`: replace refs and `--no-replace-objects` are not in git-config. Peer scouts ScoutReplaceRefs and ScoutSafeDirectory cover them (roster).
- (e) lazy-fetch execution of sshCommand: peer ScoutLazyFetch / LazyFetchFix cover it; the link needs a source that names lazy fetch, or an own-work receipt.

## 6. Flags for L1

1. **Overclaim risk on fault (e).** The probe's sentence "lazy fetch EXECUTED a repo-configured command" goes beyond
   the git-config text, which scopes `core.sshCommand` to fetch and push. Teach the narrow statement, or cite a
   partial-clone/lazy-fetch source before admitting the causal link.
2. **`log.follow` has no fault row.** Keep `-c log.follow=false` as a control. Do not count it as a fixed fault until a probe shows the repo-level setting changing `git log -- <path>` output.
3. **`i18n.logOutputEncoding` teaches the lever, not the failure.** The UnicodeDecodeError mechanism is a probe result, not a documented behaviour.
4. **Status discipline.** `queued` until a lesson or knowledge `used-by` path exists; then `mined` with that path.
5. **ID collision.** S089 is the next free id for every draft in this wave. Peers SrcGitLogFollow and SrcPartialClone may draft
   overlapping rows; L1 assigns the ids on integration.

## 7. Not verified / not run

- Did not run any probe, `git` command, or fixture. Access was to the live page only (fetched copy, not local `git help config`).
- Did not open git(1), git-replace, git-fetch, or partial-clone pages; out of target scope and covered by peers.
- Did not verify the installed git 2.56.0 against the page's `-c` and `log.follow` behaviour. These are doc claims only.
- No tools installed or updated.

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitConfig.md` (this file).
- No other file written. `corpus/SOURCES.md` was not edited.

## 9. Amendment (appended; earlier sections unchanged as record)

- Per agreement with CloseKama22.SrcGitLogFollow, `log.follow` is removed from the S089 anchor and gate. It stays on the git-log row (their S090), which cites the git-log CONFIGURATION entry (fetched copy line 3519).
- Corrected S089 anchor: §i18n.logOutputEncoding; §core.sshCommand; §remote.<name>.promisor; §Includes and §Conditional includes; §CONFIGURATION FILE precedence; §ENVIRONMENT GIT_CONFIG_COUNT. The gate row for §log.follow is dropped; the §CONFIGURATION FILE precedence quote is unchanged.
- Open overlap for L1: the peer reports its own S089 is the git-log `--encoding` / `i18n.logOutputEncoding` row. My S089 also anchors §i18n.logOutputEncoding. The same key on two pages needs one owner, and the id S089 is claimed twice. L1 assigns ids and resolves the key's owner at admission.

## 10. Amendment: single owner for i18n.logOutputEncoding (appended)

- Agreed with CloseKama22.SrcGitLogFollow: the git-log row owns `i18n.logOutputEncoding` (fault display recoding in `git log`). It is removed from this git-config draft's anchor, teaches and gate.
- This row cites it only as a cross-reference to the git-log row. It is not a located quote here.
- Corrected git-config draft row content (provisional id; L1 assigns the final id at admission; this draft claims none):
  - anchor: §core.sshCommand; §remote.<name>.promisor; §Includes and §Conditional includes; §CONFIGURATION FILE precedence; §ENVIRONMENT GIT_CONFIG_COUNT
  - teaches: A command-line `-c` outranks GIT_CONFIG_COUNT pairs, which outrank config files, so a fixed `-c` can pin a repository key; `core.sshCommand` is documented only for `git fetch` and `git push`, and the page says nothing about lazy promisor fetch. Cross-reference: `i18n.logOutputEncoding` lives on the git-log row.
  - gate: §i18n.logOutputEncoding and its quote are dropped from this row; §core.sshCommand, §remote.<name>.promisor, §ENVIRONMENT GIT_CONFIG_COUNT and §Includes quotes stand as in §5.

## 11. Fold-in: core.useReplaceRefs (appended)

- Offered by CloseKama22.SrcGitReplace. I opened the fetched git-config copy and verified the entry at line 3299: "If set to `false`, behave as if the `--no-replace-objects` option was given on the command line."
- Anchor addition: §core.useReplaceRefs.
- Scope change: the earlier scope said "not replace-ref". With this fold-in the row covers one replace-ref control key, and still does not claim that any replace-ref fault occurs. Its use for fault (c)/(d) is a candidate control only, pending a probe row.
- Ownership note (correcting the peer's message): i18n.logOutputEncoding is NOT in this row. Per §10 it sits only on the git-log row (SrcGitLogFollow). SrcGitReplace had already withdrawn its i18n row, so no second owner remains.
- Withdrawn by SrcGitReplace: its i18n.logOutputEncoding and core.sshCommand rows. core.sshCommand remains in this row (§5 gate, scope: fetch and push only).
