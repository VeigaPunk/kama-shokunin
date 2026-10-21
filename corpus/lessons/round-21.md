# Round 21 — report landing audit and soname-aware install identity

Round start: lane tip `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d` (round 20
admitted by the non-author closure CloseKama20, fleet `221707d`). Assigned axes
operability 8 + calibration 7 (`../../../shokunin.conf`); calibration is the
lowest non-retired assigned axis and below saturation 8, so no stagnation waiver.

## Declared claims

- **C1 — calibration (7 → 7): report landing audit.** The closure's two
  follow-ups (round-20 report line 7 cites a nonexistent hash; Landed changes
  omitted four round commits) had no mechanical check. `tools/report-landing-audit.py`
  detects four finite defect kinds over the fleet kama reports. The measured
  claim is the **detector**: on rounds 10–20 it finds 9 defects (1 spliced full
  hash, 8 landed omissions), each confirmed by an independent per-report hand
  recount (11 scouts, 0 false positives, 0 false negatives on those kinds), and
  the round-21 report passes it before its fleet commit. The ledger's
  "uncorrected 9 → 0" is bookkeeping, reported but not counted as the
  improvement (C1ClaimCritic). Sources S070–S073.
- **C2 — operability (8 → 8): soname-aware install identity.** R19 TreeCap
  debt: a retargeted soname link left every pin unchanged. The producer now
  records `install_links` + an injective `install_links_sha256` and refuses
  unpinnable directories; the gate checks chains and accepts a links pin. The
  measured claim: on the real b11755 tree, frozen detection link 0/13 and
  subdir 0/1 → current 13/13 and 1/1, with regular/type controls 4/4 in both
  arms, the null cell quiet and `install_tree_sha256` unchanged (back-compat).
  It is not execution authentication. Sources S066–S069.

Separability: C1 touches `tools/report-landing-audit.py` and
`registry/report-landing-errata.tsv`; C2 touches the producer, gate and grid.
C1C2Separability reverted each file set in turn and reproduced the other's
counting outputs (identical stdout and exit).

## Gate

All sources opened 2026-10-21 by named build seats (advice under
`.ufo/waves/round-21/build/advice/`) and, for S071, reopened by the L1 in the
installed git 2.56.0 manual. Quotes are located and at most 25 words.

| Candidate | Decision | URL, revision, location and quote |
|---|---|---|
| The soname is a link in a maintained chain | admit S066 | https://man7.org/linux/man-pages/man8/ldconfig.8.html, man-pages 6.19, §DESCRIPTION ¶3: "where the middle file (libfoo.so.1 here) is the SONAME for the library" (`SrcLdconfig.md`) |
| A slash-less dependency is searched at load time | admit S067 | https://man7.org/linux/man-pages/man8/ld.so.8.html, man-pages 6.19, §DESCRIPTION: "If a shared object dependency does not contain a slash, then it is searched for in the following order" (`SrcLdSoNeeded.md`); the page never mentions symlinks, so S067 carries only the lookup half |
| A directory identity records symlinks as target text | admit S068 | https://nix.dev/manual/nix/2.34/protocols/nix-archive/, nix 2.34.1 (26842787), index.md line 29: `symlink = str("target"), str(target);` (`SrcNixNar.md`) |
| A content-only directory hash sees link identity | reject that claim; admit S069 as counterexample | https://go.googlesource.com/mod/+/refs/tags/v0.42.0/zip/zip.go line 42: "Symbolic links and other irregular files are not allowed." (`SrcGoDirhash.md`; h1 opens each file by content, hash.go line 76) |
| A short hash names an object only if unique | admit S070 | https://git-scm.com/docs/gitrevisions, git.git v2.56.0 revisions.adoc line 16: "a leading substring that is unique within the repository." (`SrcGitRevisions.md`) |
| `cat-file -e` separates missing from error | reject `-e` as the mechanism; admit S071 batch-check | https://git-scm.com/docs/git-cat-file, git 2.56.0 §OUTPUT: "If a name is specified that might refer to more than one object (an ambiguous short sha)"; `-e` documents no missing-object status (`SrcGitCatFile.md`) |
| Rebasing keeps commit timestamps | reject; admit S072 | https://docs.jj-vcs.dev/latest/cli-reference/ §`jj metaedit` ¶1 (same in jj 0.45.1 help): "the committer name, email, and timestamp are also updated for all rebased commits." (`SrcJjRebaseTimestamps.md`) |
| `%at` and `%ct` are different timestamps | admit S073 | https://git-scm.com/docs/git-log, Git 2.56.0 §PRETTY FORMATS `%at`: "author date, UNIX timestamp" (`SrcGitLogDiffFilter.md`, L1 `man git-log` line 1355) |
| Older soname/real-name guide | queue S074 (tier B) | https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html §3.1.1, v1.20: "installers must specifically modify symbolic links to update what the linker will use for a library" (`SrcTldpSoname.md`) |

Excluded after opening (no row): Python 3.14.8 os/stat docs, GNU tar 1.35
§Symbolic Links and reproducible-builds.org stable inputs/archives — each was
accurate but no C1/C2 statement rests on it. Existing rows S001–S065 are
unchanged (no status, recheck or used-by cell edited). Scout drafts all
proposed the id S066; the L1 renumbered them S066–S074 in table order.
Census before: rows 65 (A 62, C 3; mined 52, queued 6, rejected 7).

## Mistakes

| ID | Class | Evidence | Captured-by | Fix (shown able to fail) |
|---|---|---|---|---|
| M1 | Hand-spliced full hash in a report | fleet `.ufo/reports/round-20/kama.md:7` token `0957ce619789d13d894ef21bc863486bcb35b56c` = first 15 hex of `0957ce61…` + last 25 hex of `33a67778…`; resolves in neither repo (`ErrataR20Splice.md`) | none before R21: the closure's existence/ancestry checks only test hashes that resolve | `report-landing-audit.py` kind `unresolved-full-hash`; raw run exit 1 names the token; selftest `mashup-detected`; KQ28 |
| M2 | Landed changes scoped to "this attempt", dropping build/attempt-1 commits | r20 omitted `33a6777`, `0957ce6`, `92b1462`, `846e366`; r18 omitted `101f399`, `1c325b2`, `c6dc46f` (relabelled "reused"; `RevengeOmissionCause.md`) | none: no check tested Landed coverage | kind `landed-omitted`; raw run 8 omissions, exit 1; the round-21 report's Landed list is generated from `git log` and audited with `--report 21=` |
| M3 | Commit cited only in an appended post-review section | r10 `4066035` (`.ufo/reports/round-10/kama.md:114`), absent from Landed (`ErrataR18R10.md`: fair, minor) | none | same detector; ledger row names the commit itself |
| M4 | A build seat wrote into the lane checkout | `git status` after wave 1 showed ` M tools/kama-llamacpp-live.py` (one inserted blank line in `_selftest`), flagged by C1C2Separability and AuditReport20; the wave context forbade lane edits | the L1's pre-integration `git status --porcelain` | reverted by rewriting the file from `master`; integration commits name explicit paths through `jj-lane.sh`, and the porcelain check before each commit is the fail-capable step (it failed here, exposing the write) |
| M5 | Ledger evidence prose misstated the report | errata rows for the splice (16+24 vs 15+25 hex) and `0957ce6` ("measurement table") were wrong; `33a6777` "absent from the whole report" ignored the splice tail (`ErrataR20Splice.md`, `ErrataR20Omitted.md`) | non-author build reviewers | evidence cells corrected before the official measurement (the ledger was created this round; append-only applies after measurement); the tool never reads evidence prose |

## Wave-1 integration (build, 86 seats)

Adopted into the audit after the draft `a29bb84`: scrubbed git environment and
config for every git call, exit 2 for missing git / empty or reversed round
selection / irregular or empty report paths / output failure / selftest abort
(AuditGitEnvExec, AuditGitEnvSentinel, AuditExitContract); `cat-file
--batch-check` separating missing, ambiguous and git failure (S071); author-time
cutoff instead of committer time (AuditCutoffCritic, S072/S073); hex words and
pure numbers not checked as citations (AuditHexWordFP); ledger rows for
unselected rounds ignored, `landed-omitted` corrections must equal the omitted
commit, blobs are not corrections (NoHarmCritic, AuditErrataMutants); ledger read
from the committed branch blob; open range `--rounds 10-` (SkillRowAudit);
selftest 15 → 32 cases covering the surviving regex/errata mutants.

Adopted into C2: canonical-JSON links digest (LinksDigestEncoding,
LinksDigestFix: the line encoding collided by construction); fail-closed
problems for unreadable members, failed lstat/readlink, control-character
names and non-regular/non-link entries such as `glibc-hwcaps/` (LinksTreeDeterminism,
LinksLoaderProof, LinksProducerReview); producer selftest for install identity
(LinksProducerSelftestCase); gate `--require-install-links` and an independent
canonical-digest literal (LinksGateReview, LinksGateMutants); grid cells on the
five DT_NEEDED sonames plus a dev link, a hwcaps shadow and an unreadable
member, realpath tree/server resolution, exit 2 at the evaluation boundary
(LinksNeededCensus, LinksGridSonameCells, LinksGridReview).

Not adopted, with reason: schema v4 (LinksDigestEncoding F2) — `gguf-identity.py`
and the gate's v3 paths accept only v3; the opt-in flag closes stripping without
breaking those consumers. Following `../` targets (NoHarmCritic) — rejecting
keeps the pin inside the directory it hashes. Simplifier patches — written
against `a29bb84` and superseded by the rewrite. Lane-document unresolved
hashes (AuditLaneDocHashes: 25 upstream commit hashes in corpus, none a lane or
fleet commit) — outside C1's declared population.

## Limits

C1's population is the eleven reports of rounds 10–20 plus the round-21 draft;
earlier reports use other formats (AuditEarlyRounds: exit 2 at round 3,
format artifacts). The cutoff assumes comparable author clocks across repos.
Prose correctness, cross-round citations and unlabelled non-commit hashes are
not judged. C2 binds bytes and link text present when the receipt was written;
it does not authenticate execution or provenance, and a consistent retarget
onto another pinned member is detected only with the pin.

## Falsify-wave integration (67 seats; appended after the b76727f3 measurement)

Corrections to the text above (append-only; earlier lines stay): C1 has **five**
defect kinds, not four; "schema v4 (LinksDigestEncoding F2)" is LinksPolicyCritic
item 2 / LinksGateReview F2; scores come from SCORECARD, not `shokunin.conf`;
S071's section is §BATCH OUTPUT; M2's "relabelled reused" covers `1c325b2` and
`c6dc46f` (`101f399` is the recovery checkpoint); AuditErrataMutants and
LinksGateMutants reports live under `build/out/`; `jj-lane.sh` is the fleet
`scripts/hyaku/jj-lane.sh`; AuditLaneDocHashes counted 24 upstream commits + 1
non-git hex (LessonPointers P1–P9). M5's fix has no failure witness (MistakesFailCapable):
it is a record correction, not a fail-capable fix. M4's writer was not identified.

Code changes after b76727f3 (all re-measured at the final commit):
- C1: committed fleet report bytes are read (`git show HEAD:`), not the working tree;
  the open range lists committed reports via `ls-tree`; ASCII-only digit parsing;
  ambiguous short names are asked unpeeled first, because a `^{commit}` peel makes
  git answer `missing` (Recheck10/13/16/18/19, C1ExitReprobe — `landed-ambiguous`
  was unreachable); selftest 32 → 36 (fleet author vs committer time, first-add vs
  re-add, commit at the cutoff, 40-hex exemption, ambiguity). Known limits kept:
  a citation is any ≥7-hex mention in Landed (C1DraftDryRun FN-1), hex words and
  all-digit/all-letter short tokens are not checked as citations (C1HexFilterFN),
  closed stdout still exits 0.
- C2: the producer refuses (`install-tree-unpinnable`) a `glibc-hwcaps` entry of any
  type, symlinks not resolving to a regular member of the directory, special files,
  control-character names, unreadable members and regular members `install_tree`
  failed to hash; other subdirectories (OpenVINO `openvino-licensing/`, C2ClaimCritic)
  are recorded in `install_unpinned` instead of refused, so those layouts still run.
  Gate: links digest required whenever the block exists, orphan digests and
  non-basename link keys rejected, `install_unpinned` type-checked, Unicode
  canonical literal (C2GateMutants survivor); selftest 12 VALID + 1 NE, 99 mutations.
  Grid: two more subdir cells (hwcaps symlink, recorded other subdir); new
  `tests/llamacpp-live/unpinnable-e2e.py` proves pre-launch refusal end to end.
- Wave-1 seat fixtures under `build/out/` that used the draft line encoding no
  longer verify (C2BackCompatRegrade: 16); they were never measured evidence.
- SOURCES S066–S074 wording corrections are appended in `corpus/SOURCES.md`
  §Round-21 falsify corrections; rows unchanged.

Claim wording after falsification: C1 is a **detector** move (instrument absent →
9 hand-confirmed defects over rounds 10–20, 0 FP/FN in 11+11 recounts); ledger 9→0
is bookkeeping (C1ClaimCritic, C1ClaimAdmissibility). C2 is integrity coverage on
the measured flat b11755 install; 0/N → N/N is detection by construction against a
regular-file-only frozen arm (C2ClaimCritic). Neither moves a score.
