# SrcPartialClone — candidate SOURCES rows for C1 lazy-fetch and replace-ref faults

Scope: partial-clone / promisor lazy fetch (C1 fault e), with git(1) and git-replace pages as the mitigation and replace-ref sources (faults c, d). Read-only draft. `corpus/SOURCES.md` was NOT edited. No installs. No other lane file was written.

## Contract check (CORPUS.md §SOURCES.md, contract v1)

- The assignment says "12-column". The contract's header is **11 named columns**: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`. The census awk expects `NF==13` (11 cells plus leading and trailing pipe). Rows below use the 11-column shape.
- Next unused id after S088 is S089. Provisional ids below (S089–S091) may collide with SrcGitConfig's draft. **The integrator assigns final ids.**
- Status for all new rows: `queued` (opened, no path or knowledge entry cites them yet). Status `mined` would need a cited `used-by` path.

## Sources opened 2026-10-21

| # | URL | Version and title as shown | Opened |
|---|---|---|---|
| 1 | https://git-scm.com/docs/partial-clone | Page title "Git - partial-clone Documentation"; "partial-clone last updated in 2.56.0"; 2.56.0 dated 2026-09-28 | 2026-10-21 |
| 2 | https://git-scm.com/docs/git | Page title "Git - git Documentation"; "git last updated in 2.56.0"; 2.56.0 dated 2026-09-28 | 2026-10-21 |
| 3 | https://git-scm.com/docs/git-replace | Page title "Git - git-replace Documentation"; "git-replace last updated in 2.55.0"; version list shows 2.56.0 "no changes" | 2026-10-21 |
| 4 | https://git-scm.com/docs/git-config | Page title "Git - git-config Documentation"; "git-config last updated in 2.56.0"; 2.56.0 dated 2026-09-28. Opened by SrcGitConfig; not drafted here | 2026-10-21 |
| — | https://git-scm.com/docs/gitprotocol-partial | HTTP 404 on fetch. Not used. Partial-clone page covers the protocol-level text | 2026-10-21 |

Line numbers are of the rendered page text as fetched (not the HTML source).

## Candidate rows

**S089** (provisional)

`| S089 | Git partial-clone design — https://git-scm.com/docs/partial-clone | docs | A | lazy fetch of missing objects from promisor remotes: which object lookups fall back to a fetch, and whether the remote is checked first | §Handling Missing Objects, bullets 3–4 (page lines 308–314) and the fetch-subprocess bullet (line 344); page "Git - partial-clone Documentation", "partial-clone last updated in 2.56.0" (2026-09-28); opened 2026-10-21 | A missing-object lookup falls back to promisor fetching with no check that the object is a promisor object, so an ordinary object read can start a fetch from a configured promisor remote. | queued | 2026-10-21 | on-release | — |`

Gate:
- URL: https://git-scm.com/docs/partial-clone
- Access date: 2026-10-21. Version and title as shown: "Git - partial-clone Documentation", "partial-clone last updated in 2.56.0".
- Quote (line 308–314, §Handling Missing Objects): "When the normal object lookup fails to find an object, Git invokes promisor_remote_get_direct() to try to get the object from a promisor remote" (23 words). Second quote (line 313): "For efficiency reasons, no check as to whether the missing object is actually a promisor object is performed." (19 words).
- Fault case: **(e)**. Supports that a lookup of a missing object triggers the lazy fetch with no promisor gate. The mechanism that executed `core.sshCommand` is not on this page; see S090-equivalent note below.

**S090** (provisional; git(1) page)

`| S090 | Git global options --no-replace-objects and --no-lazy-fetch — https://git-scm.com/docs/git | docs | A | per-invocation global switches that disable replacement refs and on-demand promisor fetching; not a sandbox for hostile repositories | OPTIONS --no-replace-objects (page lines 454–456) and --no-lazy-fetch (lines 460–465); page "Git - git Documentation", "git last updated in 2.56.0" (2026-09-28); opened 2026-10-21 | --no-lazy-fetch stops on-demand fetching of missing objects from the promisor remote, and --no-replace-objects stops replacement refs from substituting objects, each for one invocation. | queued | 2026-10-21 | on-release | — |`

Gate:
- URL: https://git-scm.com/docs/git
- Access date: 2026-10-21. Version and title as shown: "Git - git Documentation", "git last updated in 2.56.0".
- Quote (line 460–463): "Do not fetch missing objects from the promisor remote on demand." (12 words). Quote (line 454–456): "Do not use replacement refs to replace Git objects." (9 words).
- Fault cases: **(c), (d), (e)** as mitigations. The page does not state that `--no-lazy-fetch` prevents execution of `core.sshCommand`. That effect is **[INFERENCE]** until the grid run measures it. Env equivalent: `GIT_NO_LAZY_FETCH=1` and `GIT_NO_REPLACE_OBJECTS` (same page).

**S091** (provisional; git-replace page)

`| S091 | Git git-replace manual — https://git-scm.com/docs/git-replace | docs | A | replacement refs under refs/replace/ and their default use by Git commands, not a repository-trust policy | §DESCRIPTION, paragraphs on the refs/replace/ namespace and default use (page lines 212–214); page "Git - git-replace Documentation", "git-replace last updated in 2.55.0"; version list shows 2.56.0 "no changes"; opened 2026-10-21 | A replace reference is used by default by every Git command except reachability traversal (prune, pack transfer, fsck), so a replaced object reads back as its replacement. | queued | 2026-10-21 | on-release | — |`

Gate:
- URL: https://git-scm.com/docs/git-replace
- Access date: 2026-10-21. Version and title as shown: "Git - git-replace Documentation", "git-replace last updated in 2.55.0", 2.56.0 "no changes".
- Quote (line 212–214, §DESCRIPTION): "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)." (21 words). Namespace sentence from the same section: "Adds a *replace* reference in `refs/replace/` namespace." (9 words).
- Fault cases: **(c)** and **(d)**. The page does not say that a fabricated `refs/replace/<40-hex>` ref can satisfy a citation. That step is the probe observation, not a page claim.

**git-config row (not drafted here)**: owned by SrcGitConfig. Quotes I verified for that row, if it needs them:
- core.sshCommand (line 2780–2784): "If this variable is set, git fetch and git push will use the specified command instead of ssh" (18 words). Scope is fetch and push, not lazy object fetch.
- remote.<name>.promisor (line 7481–7484): "When set to true, this remote will be used to fetch promisor objects." (14 words).
- partialClone extension (line 3819–3824): "When enabled, indicates that the repo was created with a partial clone" (13 words).
- i18n.logOutputEncoding (line 5525–5527), fault case **(a)**: "Character encoding the commit messages are converted to when running git log and friends." (15 words).

## Duplicate check against existing rows

- Existing git-scm rows: S032 (git-show), S033 / S071 / S083 (git-cat-file), S070 / S082 (gitrevisions), S073 / S085 (git-log). None cites partial-clone, git(1) global options, git-replace or git-config.
- Not duplicates, but adjacent: the git(1) text at line 460–463 mentions `cat-file -e`. Existing S033 and S083 cover cat-file output, not `--no-lazy-fetch`. No row needed for cat-file.
- No duplicate of S089, S090 or S091 exists in SOURCES.md.

## Not verified, and gaps

- Fault (e) mechanism: which subprocess reads `core.sshCommand` during a `cat-file --batch-check` lazy fetch is not stated by any opened page. The partial-clone page says only that fetching is "done by invoking a 'git fetch' subprocess" (line 344). The rest is measured by the probe, not sourced.
- Faults (b) (invalid UTF-8) is not covered by any opened page; no row drafted.
- The `--no-lazy-fetch` page text does not say it blocks `core.sshCommand`; do not admit that claim from S090.
- No row cites a page version pin other than the "last updated" label; the git-scm pages float across releases, so `recheck: on-release` is used.

## Changed files

- Wrote: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcPartialClone.md` (this file).
- Sent peer messages to `CloseKama22.SrcGitConfig` and `CloseKama22.SrcGitReplace` (coordination only).
- Did not edit `corpus/SOURCES.md`, `CORPUS.md`, or any tracked file. No commits. No installs.
