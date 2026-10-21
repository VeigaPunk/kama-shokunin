VERDICT: partial - 61 of 72 checked pointers resolve or match; 9 items (P1–P9) misstate, misattribute or fail to resolve; P1 is an unmeasured claim
Attacked: every path, advice name, hash, line number, count and source quote in corpus/lessons/round-21.md at a6617149722c73d90e142fbdc8154d6967055f7e (lane working-tree copy is byte-identical), plus the SOURCES rows it cites.
Table of all 72 checks (lesson line, status, command→rc or file:line): .ufo/waves/round-21/falsify/out/LessonPointers/pointers.md. Commands with exit codes: out/LessonPointers/commands.log.

## Does not resolve or misstates (lesson line)
P1 L17, L104 — "the round-21 report passes it" / "plus the round-21 draft": UNRESOLVED and UNMEASURED. No round-21 kama report exists (fleet master and worktree lack .ufo/reports/round-21/kama.md; `cat-file -e master:…` rc 128). The only round-21 draft is build/out/ReportFormatDraft/r21-draft.md (17-line skeleton). The 28 measured commands audit `--rounds 10-20` only; none uses `--report 21=`.
P2 L94 — "schema v4 (LinksDigestEncoding F2)": LinksDigestEncoding.md has no "F2" and no "schema v4". Schema v4 is LinksPolicyCritic.md:34 item 2; F2 is LinksGateReview.md:17.
P3 L5 — `../../../shokunin.conf` cited for "operability 8 + calibration 7": the file resolves and names the axes (line 52) but carries no scores. Scores: lane SCORECARD.md:213 "(8, 7, 7, 7)"; saturation 8/10 at :132.
P4 L47 and SOURCES.md S071 row — "§OUTPUT": the quote is verbatim (git-cat-file.html:2707) but sits under h2 BATCH OUTPUT (h2 at :2590). Section should read BATCH OUTPUT.
P5 L64 M2 — "(relabelled 'reused')" covers 1c325b2 and c6dc46f only (r18 report l.26–27). 101f399 is cited at l.19 as the recovery checkpoint, not as reused.
P6 L99 — "25 upstream commit hashes in corpus": the advice (AuditLaneDocHashes.md:1, scanned at a29bb84) gives 24 upstream commits + 1 non-git hex (efb5099…, a Hyprland socket path). At a6617149, corpus/** has 28 unresolved 40-hex tokens (hashcount.py rc 0): 26 upstream (adds 26842787… from S068 and 7c41cdeb… from S072), 1 non-git, and the spliced 0957ce61… quoted at L63. "None a lane or fleet commit" holds for all 28.
P7 L79, L89 — "AuditErrataMutants", "LinksGateMutants": not in build/advice/ (82 tracked files; worktree equal). They exist only as build/out/<name>/ directories.
P8 L66 — bare `jj-lane.sh`: not tracked in the lane; resolves only as fleet scripts/hyaku/jj-lane.sh.
P9 L50 (minor) — "v1.20" is attached to the shared-libraries.html citation; "version 1.20, 11 April 2003" appears only on the HOWTO index page (build/out/SrcTldpSoname/index.html:36).

## Verified (executed)
- Hashes: 10 lane commits (7a6bc911, a29bb84, 4066035, 33a6777, 0957ce6, 92b1462, 846e366, 101f399, 1c325b2, c6dc46f) and fleet 221707d resolve (cat-file rc 0). Splice 0957ce619789d13d894ef21bc863486bcb35b56c: rc 128 in both repos; = 15 hex of 0957ce61… + 25 hex of 33a67778… (checked).
- Lines: fleet r20 report:7 holds the splice (blob at 04eb5d2); report:10 holds 0957ce61…; r10 report:114 cites 4066035; r18 l.19/26/27 as stated; SCORECARD.md:891 names 33a6777.
- Quotes: 9 of 9 sentences verbatim in the fetched sources (curl HTTP 200): ldconfig ¶3 (footer "man-pages 6.19"); ld.so; nix index.md:29 (tag 2.34.1 peels to 26842787…); zip.go:42; hash.go:76 (v0.42.0); revisions.adoc:16 (v2.56.0); jj metaedit ¶1 and `jj metaedit --help`; git-log %at (man line 1355); tldp §3.1.1. Only the S071 section label is wrong (P4).
- Census: before rows 65 (A 62, C 3; mined 52, queued 6, rejected 7); after 74 (A 70, B 1, C 3; mined 60, queued 7, rejected 7); validate rc 0 (W04 warnings on S067, S071). S001–S065 unchanged (sources diff: 11 insertions, 0 deletions).
- Counts: 9 defects (1 + 8); required 42; post-report 4; 11 reports; selftest 15 (a29bb84) → 32 (a6617149), both rc 0; `--rounds 3` rc 2; 86 seats (build/spawn-result.txt).
- Raw streams (runs/b76727f3): C1 exit 1, 9 defects. C2 frozen: link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1; current: 13/13, 1/1, 3/3, 1/1, 0/1; install_tree_sha256 6c216313… in both arms.
- Names resolve: CloseKama20 (MANIFEST.json:10106 at 221707d); KQ28 (corpus/QUALITY.md:151); mashup-detected (tool :423); _selftest (producer :1162); install_links (:213); install_links_sha256, install_tree_sha256, install-tree-unpinnable, --require-install-links, --expect-install-links-sha256, glibc-hwcaps. 35 of 37 advice names resolve to build/advice/ (P7 covers the other two).
- Tool at a6617149: `--rounds 10-20 --no-errata` rc 1; `--rounds 10-20 --json` (ledger) rc 0, corrected 9; open range rc 0; `--rounds 14` and `16` (ledger) rc 0; `--report 19=<committed>` rc 0.
- M3, M4, M5 hold: r10 l.114; committed producer has no blank line at :1151–1152; committed ledger rows 3–5 carry the corrected evidence.

## Secondary (not pointer errors)
- AuditReport18 §4 and AuditReport19 §3 (both "partial") list tool blind spots that the lesson's Limits omit: uppercase hex and ≤6-hex tokens are invisible; object type is not checked; a committed report audited with --report had cutoff=now (fixed at a6617149).
- LinksDigestEncoding (verdict partial): the gate still accepts removal-only decoys that drop DT_NEEDED sonames under both pins; the lesson's Limits do not state this.

## Method and installs
- Scratch /tmp/kama-r21-LessonPointers (lane clone at a6617149, fleet mirror, fleet worktree at 9881be6) removed at end. Written: this report and out/LessonPointers/ only (new files). No lane, fleet, index, MANIFEST, ~/.config or ~/.omp writes.
- Installs/updates: none. Tools used (already present): git 2.56.0, jj 0.45.1, python3, curl, man-db.
- Every status above was executed or read from a recorded artifact; no unexecuted reasoning is presented as fact.
