# SrcGitLogFollow — git-log `--follow`, `--diff-filter`, `--encoding` (round 23, C1 calibration)

Seat: `CloseKama22.SrcGitLogFollow` (leaf member, no dispatch). Scope: draft candidate registry rows only. `corpus/SOURCES.md` was NOT edited. No knowledge or lesson files were written.

## 1. Source opened

- URL: https://git-scm.com/docs/git-log
- Access date: 2026-10-21 (opened with `read`, reader text).
- Page title shown: `Git - git-log Documentation`. Version line: `git-log last updated in 2.56.0`; version list entry `2.56.0 … 2026-09-28` is the latest.
- Located text used (rendered page lines in the read artifact `artifact://65772`):
  - `--follow` (line 326): "Continue listing the history of a file beyond renames (works only for a single file)."
  - `--encoding=<encoding>` (lines 1329–1338): see Gate for S089.
  - `--diff-filter` (lines 2835–2848): see §3 (no new row).
  - `i18n.logOutputEncoding` (lines 3457–3460) and Discussion item 2 (lines 3433–3441).
  - `log.follow` (lines 3519–3523).
- A `web_search` snippet also surfaced git(1) text about `git clone` and untrusted repositories; it was not opened and is recorded only as a lead in §5.

## 2. Contract and header observations

- The assignment says "12-column row contract". `corpus/CORPUS.md` §SOURCES.md and the registry header in `corpus/SOURCES.md:11` both define **11 columns** (`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`). The census in CORPUS.md checks `NF==13` (11 cells plus two edge pipes). The drafts below use the 11-column shape; the "12" in the assignment appears to be a miscount.
- Registry state: rows S001–S088 are present (`corpus/SOURCES.md:13`–`100`). The next unused id is **S089**. Ids are provisional: parallel seats may draft the same number, so L1 must assign the final id at admission.
- Status vocabulary: drafts are `queued` (opened, not yet cited). `mined` requires a `used-by` path, which does not exist yet.

## 3. Duplicate check against existing rows

- Same URL already registered: `S073` (git-log `%at`/`%ct`/`--diff-filter=A`; superseded by `S085`) and `S085` (live row; "Git log field-source correction"). Both are on `https://git-scm.com/docs/git-log`. The drafts below reuse that URL with **different scope and claims**, so they are new rows, not supersessions. Round-21 and round-22 lessons cite S073 and S085 (`corpus/lessons/round-21.md:49`, `corpus/lessons/round-22.md:139`).
- `--diff-filter`: **no new row.** S085 already covers `--diff-filter=A`. The rest of the diff-filter text (`*` all-or-none, lowercase exclusion, status letters) maps to no C1 fault case, so drafting it would be an unneeded row.
- `--follow` / `log.follow`: **not in registry** (grep of `corpus/SOURCES.md` for `follow`, `logOutputEncoding`, `commitEncoding`, `i18n` returns only S073/S085 text).
- `--encoding` / `i18n.logOutputEncoding`: **not in registry**.
- `log.follow` duplicate: `SrcGitConfig` (`CloseKama22.SrcGitConfig`) drafted the same key as candidate S089 on the git-config manual (`https://git-scm.com/docs/git-config`, §log.follow, quote of 18 words). The git-log page reproduces the same CONFIGURATION entry (19-word quote, §4 S090 Gate), so S090 duplicates that claim on a second URL. L1 keeps one row for the claim; S090 is retained here only as the git-log-page variant. Do not count `log.follow` as a fixed fault (per SrcGitConfig's note).

## 4. Candidate registry rows (11-column shape, NOT written to SOURCES.md)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S089 | git-log `--encoding` and `i18n.logOutputEncoding` recoding — https://git-scm.com/docs/git-log | docs | A | git log message recoding at Git 2.56.0: when recoding to the display encoding fails, git outputs the original bytes; not the consumer's decoder, not commit-object validity | §OPTIONS `--encoding=<encoding>`; §CONFIGURATION `i18n.logOutputEncoding` and its Discussion item 2; page "git-log last updated in 2.56.0" (2.56.0, 2026-09-28) | A log consumer can receive original, non-UTF-8 bytes from git: a failed conversion passes through quietly, so the reader must own its decode policy. | queued | 2026-10-21 | on-release | — |
| S090 | git-log `--follow` and `log.follow` — https://git-scm.com/docs/git-log | docs | A | single-path history at Git 2.56.0: `--follow` crosses renames for one file and the config key `log.follow` enables it for single-path logs; not rename-detection thresholds, not multi-path history | §OPTIONS `--follow`; §CONFIGURATION `log.follow`; page "git-log last updated in 2.56.0" (2.56.0, 2026-09-28) | Repository config can change the commit set of a single-path log, so an audit that reads history must not assume the default. | queued | 2026-10-21 | on-release | — |

### Gate lines

- **S089 Gate**
  - URL: https://git-scm.com/docs/git-log · access date 2026-10-21 · page title "Git - git-log Documentation", "git-log last updated in 2.56.0".
  - Quote 1 (§OPTIONS `--encoding`, 15 words): "if iconv(3) fails to convert the commit, we will quietly output the original object verbatim."
  - Quote 2 (§OPTIONS `--encoding`, 15 words): "this means that invalid sequences in the original commit may be copied to the output."
  - Quote 3 (§CONFIGURATION `i18n.logOutputEncoding`, 11 words): "Defaults to the value of i18n.commitEncoding if set, and UTF-8 otherwise."
  - Fault support: (a) `i18n.logOutputEncoding=ISO-8859-1` changes the display recode, and a failed recode is passed through to the consumer (quote 1); (b) invalid UTF-8 committed bytes may reach output verbatim (quote 2). Candidate direction `-c i18n.logOutputEncoding=UTF-8` is the documented override of quote 3's default. Does not support (c), (d) or (e).
- **S090 Gate**
  - URL: https://git-scm.com/docs/git-log · access date 2026-10-21 · same page title and version line as S089.
  - Quote 1 (§CONFIGURATION `log.follow`, 19 words): "If true, git log will act as if the --follow option was used when a single <path> is given."
  - Quote 2 (§OPTIONS `--follow`, 15 words): "Continue listing the history of a file beyond renames (works only for a single file)."
  - Fault support: a repo-local `log.follow` silently changes the commit set of a single-path log. This is **not one of the five frozen C1 faults (a)–(e)**. It supports only the candidate `-c log.follow=false` override. L1 decides whether it enters the grid; the grid is frozen at 4fe9339f, so adding it is a scope decision, not a drafting choice.

## 5. Fault-case mapping and leads

| C1 fault | Supported by this page? |
|---|---|
| (a) ISO-8859-1 `logOutputEncoding` + non-ASCII subject → UnicodeDecodeError | Yes, mechanism: S089 quotes 1 and 3 |
| (b) invalid UTF-8 bytes in a committed report → traceback | Yes, mechanism: S089 quote 2 |
| (c) `git replace` of an omitted commit → false clean | No. Not on this page. |
| (d) `refs/replace/<40-hex>` fabricated citation → false clean | No. Not on this page. |
| (e) promisor remote + `core.sshCommand` → lazy fetch executes | No. Not on this page. |
| (f, not in grid) repo-local `log.follow` changes single-path log | Yes: S090, candidate only |

Leads (unopened; NOT rows, NOT evidence; for the replace and lazy-fetch seats or L1):
- git(1) manual: `--no-replace-objects` / `GIT_NO_REPLACE_OBJECTS`, for faults (c)/(d).
- git(1) manual: `--no-lazy-fetch` and the promisor/`core.sshCommand` behaviour, for fault (e).
- git(1) manual: a web-search snippet (not opened) reads "configuration and hooks are not copied using git clone". Its scope is clone, not local config, so it cannot be cited for the audited-repo threat model without opening it.

Not claimed by this seat: no fault was reproduced, no `git log` command was run, and no fixture was built. The `--encoding` quotes are documentation text, not observed behaviour; the probe results (a)–(e) are the L1 probe's, not this seat's.

## 6. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitLogFollow.md` (this report only).
- Not written: `corpus/SOURCES.md`, any `corpus/knowledge/` or `corpus/lessons/` file, any code, any out/ artifact.

## 7. Checks for the main agent

- Column check on the two drafted rows: NF must equal 13 for each row (see `awk` note in CORPUS.md census). Run after L1 admits the rows, not on this report.
- Reconcile the "12-column" vs 11-column discrepancy in the assignment before admission.
- Decide whether fault (f) (`log.follow`) enters the frozen grid.
