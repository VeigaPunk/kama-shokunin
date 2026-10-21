# SrcGitRepoLayout — candidate SOURCES row for gitrepository-layout(5)

Seat: CloseKama22.SrcGitRepoLayout (leaf, no dispatch). Lane: kama-shokunin, base master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d. SOURCES.md was NOT edited; the row below is a draft for L1 to admit.

## Opened source

- URL: https://git-scm.com/docs/gitrepository-layout
- Access date: 2026-10-21
- Page title shown: "Git - gitrepository-layout Documentation"
- Version shown: page footer "gitrepository-layout last updated in 2.49.0"; version table "2.49.1 → 2.56.0 no changes" (unchanged through 2.56.0). Local git is 2.56.0.
- Local cross-check: `zcat /usr/share/man/man5/gitrepository-layout.5.gz` (git 2.56.0 man page) carries the same text for objects/info/alternates (line 141) and the info/grafts sentence "Note that the grafts mechanism is outdated..." (line 286). refs/replace and shallow were read on the web page only.

## Candidate registry row (one distinct page → one row)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S089 | Git gitrepository-layout(5) — https://git-scm.com/docs/gitrepository-layout | docs | A | on-disk `objects/info/alternates`, `info/grafts`, `shallow` and `refs/replace/*` semantics at Git 2.56.0; not clone policy, replacement safety, or lazy-fetch behaviour | §objects (item 2), §objects/info/alternates, §info/grafts, §shallow, §refs/replace/*<obj-sha1>; page "Git - gitrepository-layout Documentation", version table "2.49.1 → 2.56.0 no changes"; opened 2026-10-21 | `refs/replace/<obj-sha1>` records a replacement object's SHA-1, is maintained by git-replace and, unlike info/grafts, can be exchanged between repositories; the page calls grafts outdated. | queued | 2026-10-21 | on-release | — |

Column notes: id S089 is the next unused id (S088 is the last row). Status `queued` because no path cites it yet; L1 flips to `mined` when a lesson or knowledge entry cites it.

## Gate

- URL: https://git-scm.com/docs/gitrepository-layout ; access date 2026-10-21.
- Quote 1, §objects item 2, supports the alternates/incomplete-store control (alternates and clone --shared stay legitimate): "not suitable to be published for use with dumb transports but otherwise is OK as long as" (17 words).
- Quote 2, §info/grafts, supports fault (c) (`git replace`/grafts-based false clean): "Note that the grafts mechanism is outdated and can lead to problems transferring objects between repositories" (16 words).
- Quote 3, §refs/replace/*<obj-sha1>, supports faults (c) and (d) (a fabricated `refs/replace/<40-hex>` makes a citation resolve): "records the SHA-1 of the object that replaces <obj-sha1>. This is similar to info/grafts" (14 words); and "Such refs can be exchanged between repositories while grafts are not." (13 words).
- Quote 4, §shallow, supports the shallow-history side of the fault grid (a truncated history is a documented local state): "This is similar to info/grafts but is internally used and maintained by shallow clone mechanism." (15 words).
- Fault mapping: (c) omitted commit hidden by replace → quotes 2–3; (d) fabricated replace ref → quote 3; control (alternates) → quote 1. Faults (a) and (b) (i18n encoding, invalid UTF-8) are NOT covered by this page. Fault (e) (`core.sshCommand` via lazy fetch / promisor) is NOT covered by this page; it needs the lazy-fetch and git-config sources from the sibling scouts.
- Quote verification: all four quotes are verbatim from the 2026-10-21 page read. Quote 2 also matches the local man page (line 286).

## Duplicate check

- `grep -rE 'gitrepository-layout|info/grafts|refs/replace|objects/info/alternates|shallow clone' corpus/` returned no matches (2026-10-21). No existing row or lesson cites this page; no duplicate.
- Adjacent existing rows are distinct pages and are NOT duplicates: S032 git-show, S033 git-cat-file, S070/S082 gitrevisions, S071/S083 git-cat-file batch, S073/S085 git-log. S082/S083/S085 are correction rows; S089 supersedes nothing.

## Not verified / out of scope

- git-replace(1), git(1) (`--no-replace-objects`, `--no-lazy-fetch`) and git-config (`core.sshCommand`, `i18n.logOutputEncoding`) were NOT opened by me. They are other faults' authorities and belong to sibling scouts (ScoutReplaceRefs, ScoutLazyFetch, ScoutSafeDirectory). The grafts sentence points to git-replace; I did not open it.
- No probe, selftest, or audited-repo fixture was run (outside this seat's brief).
- The refs/replace and shallow quotes were read from the web page only, not cross-checked against the local man page.

## Installs / updates

None. Tools used: `read` (web page and local corpus), `grep`, one `bash` call (`git --version`; `zcat` of the local man5 page). No package or tool installed or updated.

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitRepoLayout.md (this report).
- No other file written. SOURCES.md, CORPUS.md, and the probe were not modified.
