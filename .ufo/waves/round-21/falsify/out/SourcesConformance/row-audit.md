# SourcesConformance — per-row audit

Lane: kama-shokunin at `a6617149722c73d90e142fbdc8154d6967055f7e` (worktree HEAD; only untracked round files present).
Contract: `/home/vgpnk/Projects/shokunin/CORPUS.md` lines 64–156 (SOURCES-CONTRACT-v1).
Run date: 2026-10-21. Sources re-opened by this seat (contract rule 1, non-author sample = all nine).
Registry lines: `corpus/SOURCES.md` 78–86. Search-log entry: line 105. Gate table: `corpus/lessons/round-21.md` 40–50.

| id | line | kind / tier / status / opened / recheck | used-by cites id | anchor revision | quote located (fetched 2026-10-21) | finding |
|---|---|---|---|---|---|---|
| S066 | 78 | docs / A / mined / 2026-10-21 / on-release | llamacpp-loading-lifecycle.md:335; lessons/round-21.md | man-pages 6.19, footer "2026-08-03" (ldconfig.8) | "where the middle file (libfoo.so.1 here) is the SONAME for the library" — match only after stripping `<b>` around `libfoo.so.1` | teaches clause "install state that a regular-file digest cannot see" is unmarked lane inference (F6) |
| S067 | 79 | docs / A / mined / 2026-10-21 / on-release | llamacpp-loading-lifecycle.md:335–336; lessons/round-21.md | man-pages 6.19, footer "2026-08-03" (ld.so.8) | preamble "If a shared object dependency does not contain a slash, then it is searched for in the following order" (char 1714) | teaches "re-resolved by directory search at every exec" omits step (4) `/etc/ld.so.cache` (F2); W04 with S057 acceptable |
| S068 | 80 | spec / A / mined / 2026-10-21 / 180d | llamacpp-loading-lifecycle.md:339; lessons/round-21.md | nix tag 2.34.1 peels to 26842787… (`git ls-remote --tags`); raw index.md line 29 | `symlink = str("target"), str(target);` line 29 of 55-line file at 26842787… | none |
| S069 | 81 | code / A / mined / 2026-10-21 / on-release | lessons/round-21.md | x/mod tag v0.42.0; hash.go:76 (`os.Open`), zip.go:42 | zip.go:42 "Symbolic links and other irregular files are not allowed." (line 42 exact) | premise "module zips forbid links" is producer-side only (F1); anchor omits hash.go:84–109 (DirFiles), which grounds "follows link targets" |
| S070 | 82 | docs / A / mined / 2026-10-21 / on-release | lessons/round-21.md | git.git v2.56.0 revisions.adoc:16; body of `<rev>^{<type>}` header line 173, text 174–177 (anchor cites 175–176) | "a leading substring that is unique within the repository." at adoc:16 (exact); online page char 3726; local man 2.56.0 line 62 | teaches "so a cited token must resolve uniquely to a commit" is lane policy (F6) |
| S071 | 83 | docs / A / mined / 2026-10-21 / on-release | lessons/round-21.md | installed git 2.56.0 manual: `<object> SP missing LF` lines 599, 667; sentence line 619; `<object> SP ambiguous LF` line 625 | "If a name is specified that might refer to more than one object (an ambiguous short sha)" (exact; online char 15121) | online URL rolling (`git-cat-file/2.56.0` returns 200) (F3); "a git failure" separability not in cited sections (F6); W04 with S033 acceptable |
| S072 | 84 | docs / A / mined / 2026-10-21 / on-release | lessons/round-21.md | installed jj 0.45.1 help; tag v0.45.1 = 7c41cdeb16b6b321c64e789a966b6adf723816a5 (`git ls-remote`) | "the committer name, email, and timestamp are also updated for all rebased commits." — on `docs.jj-vcs.dev/latest` (char 88321) and on `docs.jj-vcs.dev/v0.45.1/cli-reference/` (1 match, HTTP 200) | cited URL is the rolling `latest` alias with no version on the page (F3) |
| S073 | 85 | docs / A / mined / 2026-10-21 / on-release | lessons/round-21.md | git 2.56.0; rendered `man git-log \| col -b` line 1355 (matches lesson); `%ct` committer line also present | "author date, UNIX timestamp" (exact; online char 52959) | teaches "the audit's cutoff reads author time" is lane-internal (F6); rolling URL (F3) |
| S074 | 86 | docs / B / queued / 2026-10-21 / 365d | — (queued) | "HOWTO version 1.20, 11 April 2003": present on `.../Program-Library-HOWTO/index.html` (HTTP Last-Modified Fri, 11 Apr 2003); 0 matches on the cited `shared-libraries.html` | "installers must specifically modify symbolic links to update what the linker will use for a library" (exact; char 3613) | anchor revision lives on an uncited page (F4); recheck 365d vs advice 180d (SrcTldpSoname.md:28), change unrecorded; kind docs vs teaches "older community guide" (judgment) |

## Search log (line 105)
- Identified 12, screened 12, included 9 (S066–S073 mined, S074 queued), excluded 3 (Python os/stat, GNU tar §Symbolic Links, reproducible-builds.org). 9 + 3 = 12.
- The 12 build-advice files named in the entry all exist: SrcLdconfig, SrcLdSoNeeded, SrcNixNar, SrcGoDirhash, SrcTldpSoname, SrcPythonReadlink, SrcGnuTarSymlink, SrcReproducibleBuildsArchive, SrcGitRevisions, SrcGitCatFile, SrcGitLogDiffFilter, SrcJjRebaseTimestamps.
- Rule 5 ("a negative claim carries its sweep"): the entry carries no sweep. Sweeps exist only in build advice: SrcLdSoNeeded.md:8 and :19 (`symlink|symbolic` → No matches), SrcGitCatFile.md:15 (negative sweep of the 677-line manual). Lesson negatives: line 43 "the page never mentions symlinks", line 47 "`-e` documents no missing-object status" (F5).
- Stop rationale matches the rows: S067 carries the lookup half only, S069 is the counterexample.

## Census (contract awk one-liners on `git archive` blobs)
| tree | rows | malformed | tier | status | duplicate ids | enum violations |
|---|---|---|---|---|---|---|
| 7a6bc911 (before) | 65 | 0 | A=62 C=3 | mined=52 queued=6 rejected=7 | none | none |
| a6617149 (after) | 74 | 0 | A=70 B=1 C=3 | mined=60 queued=7 rejected=7 | none | none |
Lesson line 57 claims before = 65 (A 62, C 3; mined 52, queued 6, rejected 7). Matches. After = 74 (A 70, B 1, C 3; mined 60, queued 7, rejected 7). Matches.

## Census tool output (`scripts/sources-census.sh`)
- validate: exit 0; W04 only, eight lines: S031, S043, S056, S060, S064, S065, S067, S071; then `kama ok`. No E-codes.
- census: exit 0; FLEET rows 74, tier A 70, B 1, C 3; status mined 60, queued 7, rejected 7; invalid 0; missing 0.
- overdue (today 2026-10-21): exit 0; cadence lines only (no overdue ids).
- selftest: exit 0, `selftest ok`.
- W04 acceptability: S067 vs S057 share the ld.so URL; scopes and anchors differ (preamble and steps 4–5 vs step 3 RUNPATH and $ORIGIN). S071 vs S033 share the git-cat-file URL; scopes differ (batch-check vs raw OUTPUT). Contract E04 applies only to same URL plus same scope; W04 does not change status.

## used-by and citation checks (committed blobs at a6617149)
- `corpus/knowledge/llamacpp-loading-lifecycle.md`: S066 (line 335), S067 (lines 335–336), S068 (line 339). knowledge diff +40 lines.
- `corpus/lessons/round-21.md`: S066 3 lines, S067 1, S068 1, S069 2, S070 2, S071 3, S072 2, S073 3, S074 2.
- Contract mined-path awk run from the clone root: nothing printed (exit 0 pipeline).
- Knowledge sentence repeats F2: "the loader re-resolves a slash-less DT_NEEDED name by directory search at every exec (S067)".

## Append-only (`tools/sources-append-only.py`)
- `--from 7a6bc911… --to a6617149… --repo <clone>`: exit 0; "no append-only violations"; added S066–S074.
- `--json`: exit 0; violations []; ok true.
- `--selftest`: exit 0; 42/42.
- Diff of `corpus/SOURCES.md`: 11 insertions (rows 78–86; search-log lines 105–106), 0 deletions. Existing cells unchanged.

## Commands run (exit)
- `git clone -q <lane> /tmp/kama-r21-SourcesConformance/lane`: 0; `git checkout -q a6617149…`: 0; `git cat-file -t` on both commits: 0; `git show a6617149:corpus/SOURCES.md | cmp - corpus/SOURCES.md`: 0.
- `git ls-remote --tags` for jj-vcs/jj (refs/tags/v0.45.1*): 0; NixOS/nix (refs/tags/2.34.1*): 0.
- `curl -sS -L` (exit 0) with HTTP codes: ldconfig 200, ld.so 200, nix.dev 200, raw NAR index.md 200, go hash.go 200, go zip.go 200, gitrevisions 200, git-cat-file 200, jj latest 200, git-log 200, tldp shared-libraries 200; jj v0.45.1 200; jj /en/v0.45.1 404 (not cited); git-log/2.56.0, gitrevisions/2.56.0, git-cat-file/2.56.0 200; tldp index 200; git.git v2.56.0 revisions.adoc 200.
- `man -w` for gitrevisions, git-cat-file, git-log, ldconfig, ld.so: 0 each; `zcat` greps of local man pages: 0.
- `jj --version` 0 (`jj 0.45.1-7c41cdeb…`); `git --version` 0 (2.56.0); `python3 --version` 0 (3.14.8).
- No tool installed or upgraded by this seat.

## Lane state during run
- Four tracked lane files gained uncommitted edits during the run (not by this seat): SCORECARD.md, tests/llamacpp-live/check-receipt.py, tools/kama-llamacpp-live.py, tools/report-landing-audit.py (144 insertions, 13 deletions). Evidence inputs (corpus/SOURCES.md, lessons/round-21.md, corpus/knowledge/llamacpp-loading-lifecycle.md, tools/sources-append-only.py) remain identical to a6617149.
