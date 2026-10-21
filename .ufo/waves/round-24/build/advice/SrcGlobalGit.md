# SrcGlobalGit — git(1) global options (round 24)

**Verdict: REOPENED-USED SOURCE — no new scope, no correction, no SOURCES edit.**
`corpus/SOURCES.md:101` (S089) already cites this exact page for these exact two
options and its teaches cell is accurate at the reopened text. The one claim the
page does **not** support is "prevents remote operations" in general: it documents
only suppression of the implicit on-demand promisor fetch. The audit's argv
placement matches the page's SYNOPSIS.

Axes: operability harm repair (C1 calibration) — narrows an isolation claim to its
source; no freshness or coverage movement. No tools installed or upgraded.

## Observations (path:line / command)

| # | Observation | Evidence |
|---|---|---|
| 1 | Fetched `https://git-scm.com/docs/git` → HTTP 200, 244359 bytes, final URL unchanged | `curl -sS -L -o git.html -w '%{http_code} %{size_download} %{url_effective}'`, 2026-10-21T17:53:47Z |
| 2 | Page version: "git last updated in 2.56.0" | `git.html:1359` (raw HTML) |
| 3 | Version-pinned `https://git-scm.com/docs/git/2.56.0` → HTTP 200, 244230 bytes; tag-stripped text identical to latest (difflib: 0 diff lines) | fetch 2026-10-21T17:54:06Z; `git-2.56.0.html` |
| 4 | Local git matches the page | `git --version` → `git version 2.56.0` |
| 5 | SYNOPSIS places both flags in the global option list **before** `<command> [<args>]` | `git.html:3835-3840`, anchor `#_synopsis` |
| 6 | `--no-replace-objects` OPTIONS entry | `git.html:4042-4048`, anchor `#Documentation/git.txt---no-replace-objects` |
| 7 | `--no-lazy-fetch` OPTIONS entry | `git.html:4049-4056`, anchor `#Documentation/git.txt---no-lazy-fetch` |
| 8 | S089 row exists and is used | `corpus/SOURCES.md:101`; status `mined`, opened `2026-10-21`, used-by `corpus/lessons/round-23.md, tools/report-landing-audit.py` |
| 9 | Audit places the flags before `-C` and the subcommand | `tools/report-landing-audit.py:93` (`GIT_ISOLATION`), `:111-118` (`["git", *GIT_ISOLATION, "-C", str(repo), *args]`) |
| 10 | No other SOURCES row cites `git(1)`; other git rows are different pages/claims (S032, S033, S070, S071, S073, S082, S083, S085, S090–S094) | `grep -n 'git-scm.com/docs/git |' corpus/SOURCES.md` → line 101 only |

Artifact digests: `git.html` sha256 `0dd80d87d78dd275e1e26cad29064a7594b7bc4518fbcebf5ec2474e587ab8e6`;
`git-2.56.0.html` sha256 `336f7842f6015f12fa5fd9f2ed788d4c6d91fc19375a4b50424b5958dfd97f94`.
Latest and pinned pages differ only in wrapper bytes; every tag-stripped line is equal.

## Quote (each ≤ 25 words)

| Anchor | Quote | Words |
|---|---|---|
| `#Documentation/git.txt---no-lazy-fetch` | "Do not fetch missing objects from the promisor remote on demand." | 11 |
| `#Documentation/git.txt---no-lazy-fetch` | "Useful together with git cat-file -e <object> to see if the object is locally available." | 15 |
| `#Documentation/git.txt---no-replace-objects` | "Do not use replacement refs to replace Git objects." | 9 |
| `#Documentation/git.txt---no-lazy-fetch` | "This is equivalent to setting the GIT_NO_LAZY_FETCH environment variable to 1." | 11 |
| `#Documentation/git.txt---no-replace-objects` | "This is equivalent to exporting the GIT_NO_REPLACE_OBJECTS environment variable with any value." | 12 |

Version: **2.56.0**. Access date: **2026-10-21** (17:53:47Z latest, 17:54:06Z pinned).

## Claim-vs-source limits

| Claim | Source support | Limit |
|---|---|---|
| "`--no-lazy-fetch` prevents remote operations" | **Not supported as stated.** Only "Do not fetch missing objects from the promisor remote on demand." | Explicit `fetch`/`push`/`ls-remote`/`clone`, hooks, and repo-configured transports are not addressed. Cite this page only for suppressing the *implicit on-demand promisor fetch*. |
| "No network transport can run under the audit" | Not established here | The page says nothing about explicit network commands or subprocess transports. Any such invariant is a composition of isolations plus fault rows, not this sentence. |
| "A missing required object is detectable with `cat-file -e`" | Supported only as a recommended pairing ("Useful together with … to see if the object is locally available") | The page does not define `cat-file -e` exit status, stderr, or missing-vs-ambiguous. Exit-2 classification is audit policy plus the git-cat-file rows (S071/S083), not this page. |
| "`--no-replace-objects` disables replacement refs" | Supported ("Do not use replacement refs to replace Git objects"); details deferred to git-replace(1) | Covers replacement refs only. `info/grafts`, `shallow`, and `objects/info/alternates` are absent from this page and come from S094. S089's "Neither covers info/grafts or shallow" is therefore a cross-row [INFERENCE], true but not a sentence here. |
| Env equivalence | Supported | `GIT_NO_REPLACE_OBJECTS` is documented "with any value"; `GIT_NO_LAZY_FETCH` is documented "to 1". Do not generalise "any value" to the latter. |
| Placement before the subcommand | Supported by SYNOPSIS only | The OPTIONS entries do not restate placement, and the page does not say what happens if the flag follows the subcommand. The audit's `git <flags> -C <repo> <cmd>` order is consistent; post-subcommand rejection is unverified here. |
| Version floor | Not supported | The page is 2.56.0 and says nothing about older git. The audit's "git ≥ 2.45" floor for `--no-lazy-fetch` (`tools/report-landing-audit.py:92`) is probe/lesson-derived, not sourced here. |
| Signature/log config isolation | Not supported here | `log.showSignature`, `log.follow`, `log.mailmap`, `i18n.logOutputEncoding` are S091/S093 claims; this page does not mention them. |

## Reopened-used vs new scope

- `corpus/SOURCES.md:101` S089 is the existing row: same URL, both options, mined,
  used by the round-23 lesson and the production auditor. This reopen confirms the
  row rather than adding scope; a new row would duplicate it.
- The row's existing wording ("Both are global options placed before the subcommand;
  `--no-lazy-fetch` stops on-demand fetches of missing objects from the promisor
  remote, `--no-replace-objects` stops replacement refs. Neither covers info/grafts
  or shallow.") stays within the page plus S094. **No appended correction is
  required**; in particular, do not strengthen it to "prevents remote operations".
- No registry or production file was edited by this seat. No candidate patch is
  needed; the only deliverable is this narrowed citation guidance.

## Unverified / not run

- No git transport was executed (no `fetch`, `push`, `clone`, `ls-remote`), and no
  fixture was built: the "explicit remote commands are outside this page" limit is a
  text-scope observation, not a runtime result.
- `tools/report-landing-audit.py` was read statically; its argv placement was not run.
- git < 2.45 rejection of `--no-lazy-fetch` was not reproduced.
- No build, test, linter, formatter, or full-suite check was run (lane rule).
- The unversioned page can change after 2026-10-21; the pinned `/docs/git/2.56.0`
  page is the reproducible citation, with the unversioned page text-identical today.

## Files written

- `.ufo/waves/round-24/build/advice/SrcGlobalGit.md` (this report)
- `.ufo/waves/round-24/build/out/SrcGlobalGit/pins.json`
- `.ufo/waves/round-24/build/out/SrcGlobalGit/git-options-excerpt.txt`

Scratch (not in repo): `/fast/scratch/hyaku/kama-r24/SrcGlobalGit/{git.html,git-2.56.0.html,git.txt}`.
