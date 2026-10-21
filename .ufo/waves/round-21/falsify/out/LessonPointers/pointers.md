# LessonPointers: every pointer in corpus/lessons/round-21.md at a6617149722c73d90e142fbdc8154d6967055f7e

Lane working-tree copy is byte-identical to the attacked commit (`cmp` rc 0). Lesson line numbers below are from `read` of that file. Status: OK = resolves/matches; FLAG = misstates, misattributes or does not resolve (see report P1–P9).

| # | line | pointer | status | evidence (command → rc; file:line) |
|---|---|---|---|---|
| 1 | 3 | 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d | OK | `git cat-file -t` rc 0; lane commit "round-20: log routed verifier tool registrations" |
| 2 | 4 | CloseKama20 | OK | fleet MANIFEST.json @221707d:10106 `"reviewer": "CloseKama20 (hyaku-closure, …)"` |
| 3 | 4 | 221707d (fleet) | OK | fleet `cat-file -t` rc 0; "rounds ledger: kama r20 closure (admitted)" |
| 4 | 5 | ../../../shokunin.conf (for "operability 8 + calibration 7") | FLAG P3 | path resolves (fleet root); line 52 gives axis names only; 8/7 scores are in lane SCORECARD.md (:213 "unchanged (8, 7, 7, 7)"; :132 saturation 8/10) |
| 5 | 14–16 | 9 defects (1 spliced, 8 landed-omitted) | OK | `--rounds 10-20 --no-errata --json` rc 1; by_kind {unresolved-full-hash 1, landed-omitted 8}; audit-noerrata.json |
| 6 | 16 | 11 scouts, 0 FP / 0 FN | OK (note) | AuditReport10–20.md (11 files, role scout); 9 confirm, 2 partial (AuditReport18, 19; tool blind spots, see report §Secondary) |
| 7 | 17, 104 | "the round-21 report passes it"; "plus the round-21 draft" | FLAG P1 | no fleet `.ufo/reports/round-21/kama.md` (glob; `cat-file -e master:…` rc 128); measured commands.json: 28 commands, audits `--rounds 10-20` only, no `--report 21=`; only draft build/out/ReportFormatDraft/r21-draft.md (17 lines, skeleton) |
| 8 | 19 | C1ClaimCritic | OK | build/advice/C1ClaimCritic.md verdict "refute … 'uncorrected 9 -> 0' is ledger bookkeeping" (agrees with L18–19) |
| 9 | 19, 27 | Sources S070–S073; S066–S069 | OK | corpus/SOURCES.md @a6617149 rows S066–S074 present |
| 10 | 20–27 | install_links, install_links_sha256, install_tree_sha256 | OK | tools/kama-llamacpp-live.py:213 `def install_links`; check-receipt.py `install_links_sha`, `install_tree_sha` |
| 11 | 24–26 | frozen link 0/13, subdir 0/1 → current 13/13, 1/1; controls 4/4; null quiet; install_tree_sha256 unchanged | OK | runs/b76727f3/c2-grid-frozen.stdout summary link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1; c2-grid-current.stdout link 13/13, subdir 1/1, regular 3/3, type 1/1, null 0/1; install_tree_sha256 6c216313… in both arms |
| 12 | 24 | real b11755 tree | OK | ~/.local/opt/llama-b11755 exists (`ls -d` rc 0) |
| 13 | 29–30 | tools/report-landing-audit.py; registry/report-landing-errata.tsv; producer, gate, grid | OK | all tracked at a6617149 (`git cat-file -t` blob); producer tools/kama-llamacpp-live.py, gate tests/llamacpp-live/check-receipt.py, grid tests/llamacpp-live/install-links-grid.py |
| 14 | 31 | C1C2Separability | OK | build/advice/C1C2Separability.md verdict "confirm - file-set separability holds both ways" |
| 15 | 36–37 | .ufo/waves/round-21/build/advice/ | OK | 82 tracked files; `comm` against worktree: 0 differences |
| 16 | 38 | installed git 2.56.0 | OK | `git --version` rc 0: 2.56.0 |
| 17 | 42 | ldconfig(8) URL; man-pages 6.19; §DESCRIPTION ¶3; quote | OK | curl rc 0 HTTP 200; footer "Linux man-pages 6.19 2026-08-03"; ¶3 = 3rd DESCRIPTION block (lines 95–100); quote verbatim (ldconfig.html:99–100) |
| 18 | 42 | SrcLdconfig.md | OK | build/advice exists |
| 19 | 43 | ld.so(8) URL; quote; "never mentions symlinks" | OK | ldso.html:102–103 quote verbatim; no "symlink" string in page |
| 20 | 43 | SrcLdSoNeeded.md | OK | exists |
| 21 | 44 | nix.dev NAR; nix 2.34.1 (26842787); index.md line 29 | OK | tag 2.34.1 → annotated 2c486b7c → commit 26842787496f2293c676fb36db38dacfd63497e0 (GitHub API); raw index.md:29 `symlink = str("target"), str(target);` |
| 22 | 44 | SrcNixNar.md | OK | exists |
| 23 | 45 | go zip.go line 42; hash.go line 76; tag v0.42.0 | OK | zip.go:42 "Symbolic links and other irregular files are not allowed." verbatim; sumdb/dirhash/hash.go:76 `os.Open(...)` in HashDir |
| 24 | 45 | SrcGoDirhash.md | OK | exists |
| 25 | 46 | revisions.adoc line 16 (v2.56.0); quote | OK | revisions.adoc:16 "a leading substring that is unique within the repository." verbatim |
| 26 | 46 | SrcGitRevisions.md | OK | exists |
| 27 | 47 | git-cat-file "§OUTPUT": quote | FLAG P4 | quote verbatim at git-cat-file.html:2707 (and local man text); under h2 BATCH OUTPUT (h2 at :2590); h2 OUTPUT holds only -e/-t/-s text (man :246–251) |
| 28 | 47 | "-e documents no missing-object status" | OK | OPTIONS -e: "exists and is a valid object"; OUTPUT -e: "no output, unless the <object> is malformed" |
| 29 | 47 | SrcGitCatFile.md | OK | exists (its own draft row was S066 for -e; L1 used batch-check) |
| 30 | 48 | jj metaedit ¶1 quote; same in jj 0.45.1 help | OK | jj-cli.html:10463 verbatim; `jj metaedit --help` rc 0 line 3 (wrapped) same sentence; tag v0.45.1 → 7c41cdeb… (GitHub API) |
| 31 | 48 | SrcJjRebaseTimestamps.md | OK | exists |
| 32 | 49 | git-log §PRETTY FORMATS %at "author date, UNIX timestamp"; man line 1355 | OK | git-log.html:5563 verbatim; local `man -P cat git-log` line 1355 same text (rc 0) |
| 33 | 49 | SrcGitLogDiffFilter.md | OK | exists (name vs content differs; covers %at/%ct and --diff-filter) |
| 34 | 50 | tldp shared-libraries.html §3.1.1; quote | OK | tldp.html:121 "3.1.1. Shared Library Names"; quote verbatim lines 174–175 |
| 35 | 50 | "v1.20" attached to that URL | FLAG P9 (minor) | "version 1.20, 11 April 2003" only on HOWTO index page (build/out/SrcTldpSoname/index.html:36); cited page has no version |
| 36 | 50 | SrcTldpSoname.md | OK | exists |
| 37 | 54–55 | existing rows S001–S065 unchanged | OK | `git diff 7a6bc911 a6617149 -- corpus/SOURCES.md` rc 0: 11 insertions, 0 deletions (sources.diff) |
| 38 | 55–56 | scout drafts all proposed S066 | OK | S066 drafts in SrcLdconfig, SrcLdSoNeeded, SrcNixNar, SrcGoDirhash, SrcGitRevisions, SrcGitLogDiffFilter, SrcTldpSoname, SrcPythonReadlink, SrcGnuTarSymlink, SrcReproducibleBuildsArchive (out/advice); SrcJjRebaseTimestamps and SrcGitCatFile advice propose S066 |
| 39 | 57 | census before: rows 65 (A 62, C 3; mined 52, queued 6, rejected 7) | OK | build/sources/census-before.txt: rows 65, tier.A 62, tier.C 3, mined 52, queued 6, rejected 7 |
| 40 | 63 | fleet r20 report:7 token 0957ce619789d13d894ef21bc863486bcb35b56c | OK | 04eb5d2 kama.md line 7 contains token; `cat-file -t` rc 128 in lane and fleet |
| 41 | 63 | splice composition: first 15 hex of 0957ce61 + last 25 hex of 33a67778 | OK | 0957ce619789d13 + d894ef21bc863486bcb35b56c (suffix of 33a6777866d0f63d894ef21bc863486bcb35b56c) |
| 42 | 63 | ErrataR20Splice.md | OK | exists; its 16+24 finding was corrected in committed TSV row 3 (now 15+25) |
| 43 | 63 | selftest `mashup-detected`; KQ28 | OK | report-landing-audit.py:423 `check("mashup-detected", …)`; corpus/QUALITY.md:151 KQ28 |
| 44 | 64 | r20 omitted 33a6777, 0957ce6, 92b1462, 846e366 | OK | all lane commits; tool landed-omitted for all four (audit-noerrata.json round 20) |
| 45 | 64 | r18 omitted 101f399, 1c325b2, c6dc46f ("relabelled 'reused'") | FLAG P5 | hashes OK; r18 report (23bdc3f) l.26–27 "Reused …: c6dc46f / 1c325b2" (labelled reused); l.19 "pushing checkpoint `101f3991…`" (101f399 not labelled reused) |
| 46 | 64 | RevengeOmissionCause.md | OK | exists; names 101f399 as the checkpoint at l.19 |
| 47 | 64 | raw run 8 omissions, exit 1 | OK | runs/b76727f3/c1-audit-raw.exit = 1; .stdout by_kind landed-omitted 8 |
| 48 | 65 | r10 4066035 at .ufo/reports/round-10/kama.md:114, absent from Landed | OK | b69b7ba blob l.114 "Lane commit **4066035**"; tool landed-omitted, cited_elsewhere true |
| 49 | 65 | ErrataR18R10.md "fair, minor" | OK | verdict "r10 4066035 is a fair defect, not a false positive (minor)" |
| 50 | 66 | ` M tools/kama-llamacpp-live.py` (one blank line in `_selftest`); flagged by C1C2Separability and AuditReport20 | OK | AuditReport20.md:5 and C1C2Separability.md:50 describe it; committed producer has no blank line at :1151–1152; `_selftest` at :1162 |
| 51 | 66 | bare `jj-lane.sh` | FLAG P8 | not tracked in lane at a6617149; resolves only as fleet scripts/hyaku/jj-lane.sh (fleet master blob, cat-file rc 0) |
| 52 | 67 | errata evidence corrected (15+25; measurement table; "absent from whole report") | OK | registry/report-landing-errata.tsv rows 3–5 at a6617149 match ErrataR20Splice/ErrataR20Omitted |
| 53 | 67 | ErrataR20Omitted.md | OK | exists |
| 54 | 69 | build seats: 86 | OK | build/spawn-result.txt "Spawned 86 background agents" |
| 55 | 71 | draft a29bb84; selftest 15 cases | OK | a29bb84 exists; its tool `--selftest` rc 0, cases=15 failed=0 (selftest-a29bb84.txt) |
| 56 | 74–76, 79 | AuditGitEnvExec, AuditGitEnvSentinel, AuditExitContract, AuditCutoffCritic, AuditHexWordFP, NoHarmCritic | OK | all exist in build/advice |
| 57 | 79 | AuditErrataMutants | FLAG P7 | not in build/advice/; exists only as build/out/AuditErrataMutants/ (AuditErrataMutants.md, M01–M10) |
| 58 | 78, 80 | SkillRowAudit; open range `--rounds 10-` | OK | SkillRowAudit.md exists; `--rounds 10-` run rc 0 (11 reports) |
| 59 | 81 | selftest 15 → 32 | OK | a6617149 `--selftest` rc 0, cases=32 failed=0 (selftest-a6617149.txt) |
| 60 | 83–84 | LinksDigestEncoding, LinksDigestFix | OK | exist; LinksDigestFix.md:8 documents install_links_sha256 ambiguity |
| 61 | 86–87 | LinksTreeDeterminism, LinksLoaderProof, LinksProducerReview, LinksProducerSelftestCase | OK | exist |
| 62 | 88–89 | LinksGateReview | OK | exists; F2 "optional for legacy" finding is in this file (:17) |
| 63 | 89 | LinksGateMutants | FLAG P7 | not in build/advice/; exists only as build/out/LinksGateMutants/LinksGateMutants.md |
| 64 | 90–92 | grid: five soname cells; hwcaps shadow; unreadable member; realpath; exit 2 boundary | OK | install-links-grid.py: sonames list has 5 (c2-grid stdout); cells subdir-hwcaps-shadow, regular-unreadable; realpath :198/:208; `except Exception` :377 → return 2 :383 |
| 65 | 92 | LinksNeededCensus, LinksGridSonameCells, LinksGridReview | OK | exist |
| 66 | 94 | schema v4 (LinksDigestEncoding F2) | FLAG P2 | LinksDigestEncoding.md has no "F2" and no "schema v4" (grep rc 0 for pattern set); schema v4 = LinksPolicyCritic.md:34 item 2; F2 = LinksGateReview.md:17 |
| 67 | 94–95 | gguf-identity.py and gate v3 paths accept only v3 | OK | tools/gguf-identity.py:44 RECEIPT_SCHEMA_V3 only (receipt schema; its GGUF file versions 2/3 are a separate axis) |
| 68 | 96 | NoHarmCritic (../ targets) | OK | exists; check-receipt.py "leaves the pinned directory" |
| 69 | 99 | "25 upstream commit hashes in corpus, none a lane or fleet commit" | FLAG P6 | AuditLaneDocHashes.md:1 (a29bb84): 25 unresolved = 24 upstream + 1 non-git hex (efb5099…). hashcount.py at a6617149 (rc 0) over corpus/**: 80 unique 40-hex, 42 lane, 10 fleet, 28 unresolved = 26 upstream (adds 26842787… S068 and 7c41cdeb… S072) + 1 non-git + spliced 0957ce61… (L63) |
| 70 | 104 | eleven reports of rounds 10–20 | OK | 11 fleet report add-commits b69b7ba…04eb5d2; --rounds 10-20 reports=11 |
| 71 | 105 | AuditEarlyRounds: exit 2 at round 3 | OK | `--rounds 3` rc 2 "cannot read …/round-3/kama.md"; AuditEarlyRounds.md:1 |
| 72 | 17 (cf. 104) | `--report 21=` audit of the round-21 report | FLAG P1 | no run among 28 measured commands (commands.json); no report exists to audit |
