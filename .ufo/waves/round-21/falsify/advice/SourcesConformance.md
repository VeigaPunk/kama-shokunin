VERDICT: partial - S066-S074 and the round-21 search-log entry pass every mechanical contract-v1 check, but S069 and S067 teaches overstate their sources, S072 and S074 cite pages lacking the anchored revision, and the log omits negative-claim sweeps.
Attacked: corpus/SOURCES.md rows S066-S074 (lines 78-86) and the round-21 search-log entry (line 105) at lane a6617149, against CORPUS.md:64-156; plus W04 pairs, used-by targets, lesson Gate quotes (lessons/round-21.md:40-50), and the census and append-only tools.
Evidence: .ufo/waves/round-21/falsify/out/SourcesConformance/ (row-audit.md per-row table and command log; census-validate.tsv, census-census.tsv, append-only.txt, append-only.json, append-only-selftest.txt, census-selftest.txt).

## Findings (severity order)
Fix rule: any teaches or anchor change is a new `supersedes S0NN —` row (contract rule 2); used-by, status and recheck change in place only.

F1 moderate - S069 (line 81): teaches "module zips forbid links" states a producer-side restriction as a zip property. zip.go:42 documents it; producers skip links (zip.go:323-328, reached via Create at zip.go:534); CheckZip -> checkZip (zip.go:405-505) has no mode check. Advice probe C1 (build seat, not re-run here) says CheckZip accepts a link-mode entry. The conclusion survives (advice probe C2: link-mode entry hashes equal to the regular entry with the same text). The anchor omits hash.go:84-109 (DirFiles), which grounds "follows link targets".

F2 moderate - S067 (line 79): teaches "re-resolved by directory search at every exec". Fetched ld.so(8): steps (1)-(3) and (5) search directories; step (4) reads /etc/ld.so.cache, "a compiled list of candidate shared objects previously found in the augmented library path". The anchor names step (4). The live-state conclusion holds; the mechanism sentence does not match the anchor. The same sentence stands at corpus/knowledge/llamacpp-loading-lifecycle.md:335-336 (committed).

F3 minor - S072 (line 84) cites the rolling docs.jj-vcs.dev/latest/cli-reference/, which carries no version; the anchor's jj 0.45.1 revision belongs to the installed binary. docs.jj-vcs.dev/v0.45.1/cli-reference/ returns 200 and contains the quoted sentence once. S070, S071, S073 cite rolling git-scm.com/docs/<cmd>; the /2.56.0 URLs return 200. S032/S033 set the rolling precedent, so this is a pattern, not a new breach.

F4 minor - S074 (line 86): the anchor's "HOWTO version 1.20, 11 April 2003" is on .../Program-Library-HOWTO/index.html, not on the cited shared-libraries.html (0 matches). Advice drafted recheck 180d (SrcTldpSoname.md:28); the registry has 365d and the lesson records no reason. Kind docs versus teaches "older community guide" is a judgment call.

F5 minor - search-log line 105, contract rule 5 ("a negative claim carries its sweep"): lesson lines 43 ("the page never mentions symlinks") and 47 ("-e documents no missing-object status") rely on sweeps that exist only in build advice (SrcLdSoNeeded.md:8,19; SrcGitCatFile.md:15). I re-ran the ld.so sweep: symlink|symbolic gives 0 matches.

F6 minor - teaches cells carry lane-internal or unmarked inference, against "one grounded learner benefit": S066 ("install state that a regular-file digest cannot see"), S069 ("the R19 TreeCap shape"), S070 ("a cited token must resolve uniquely"), S071 ("a git failure" separable; not in the cited sections), S073 ("the audit's cutoff reads author time"). Precedent: S034, S046. S033 shows the [INFERENCE] marker, not applied here.

F7 pre-existing, outside target, not charged to round 21: S057 anchor (line 69) has no revision; S067 is its W04 partner and carries one. The "## Leads (unopened)" heading (line 107) is followed by the round-12 to round-19 search-log supplements (lines 112-240), so they sit outside "## Search log"; the round-20 correction is a separate "## Round-20 source correction — S065" heading (line 242). Intro lines 6-7 still say every row was opened in round 10.

## Verified, no defect
- Census: validate exit 0 (W04 only, 8 lines: S031, S043, S056, S060, S064, S065, S067, S071; no E-codes; kama ok); census exit 0 (74; A70 B1 C3; mined 60, queued 7, rejected 7); overdue exit 0 (cadence lines only); selftest exit 0.
- Before/after from git-archive blobs with the contract awk: 65/A62/C3/mined52/queued6/rejected7, then 74/A70/B1/C3/mined60/queued7/rejected7. Both match lesson line 57 and the claimed counts.
- Append-only exit 0: S066-S074 added, 0 violations; SOURCES diff = 11 insertions, 0 deletions, no existing cell changed.
- used-by: all paths exist at a6617149; contract mined-path awk prints nothing; each cites its id (llamacpp S066 l.335, S067 l.335-336, S068 l.339; lesson 1-3 lines per id).
- Search log: identified 12 = included 9 (S066-S073 mined, S074 queued) + excluded 3; all 12 named advice files exist.
- Fields and enums: 11 cells per row (awk NF=13) in every row; ids unique; kind, tier, status valid; opened 2026-10-21; recheck valid; no community at tier A; S074 queued with used-by "—".
- W04 acceptable: S067/S057 share the ld.so URL with different scopes and anchors; S071/S033 share the git-cat-file URL with different scopes.
- Quotes: 9/9 located in re-fetched sources (S066 after stripping one <b> tag), at most 19 words. Anchors confirmed: man-pages 6.19 with 2026-08-03 footers; nix tag 2.34.1 = 26842787 (ls-remote); jj v0.45.1 = 7c41cdeb (ls-remote); revisions.adoc:16; zip.go:42; hash.go:76; NAR index.md:29; #AEN49.
- No credential, session, or op:// material in the new rows or lesson.

## Commands (exit)
- sources-census.sh validate / census / overdue / selftest: 0 / 0 / 0 / 0.
- sources-append-only.py default / --json / --selftest: 0 / 0 / 0 (42/42).
- contract awk on git-archive of 7a6bc911 and a6617149: counts printed; mined-path loop in the clone at a6617149: nothing printed.
- git ls-remote jj v0.45.1 and nix 2.34.1: 0 / 0; curl of 20 requests: 404 only for docs.jj-vcs.dev/en/v0.45.1 (not cited); quote bodies checked per URL. Full log in row-audit.md.

## Residual risk and gaps
- F1 rests on static reading of zip.go plus build-seat probes C1-C2, which I did not re-run [INFERENCE for the probe results].
- Live pages can drift; quote checks reflect fetches made 2026-10-21.
- No tool installed or upgraded by this seat.
- Lane worktree gained uncommitted edits to SCORECARD.md, tests/llamacpp-live/check-receipt.py, tools/kama-llamacpp-live.py and tools/report-landing-audit.py during this run (144 insertions, 13 deletions; not by me). None of my inputs (corpus/SOURCES.md, lessons/round-21.md, corpus/knowledge/llamacpp-loading-lifecycle.md, tools/sources-append-only.py) differs from a6617149 (git diff --quiet: exit 0).
- Read-only git commands on the lane (status, log, show, diff, cat-file); git status can refresh the index stat cache. No lane content written.
