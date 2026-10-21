# Round 22 — explicit helper I/O refusal

Round start: branch master `10271460cc575fc2280aa831e442726385fc2319`.
R21 was admitted by the outside closure (fleet rounds[406], operator handoff).
Assigned axes: operability8 + calibration7; calibration is the lowest assigned
non-retired axis, below saturation8. No stagnation waiver. The L1 holds the
canonical planner seat; wave planning advice does not become a second judge.

## Declared claim

**C1 — calibration7→7: install_tree helper error/identity separation.** A raised
listing/stat/read OSError must never become a normal comparison result.
The frozen helper returns a null result on listing failure or a smaller map
and comparable digest on stat/read failure. The repaired helper explicitly
refuses at that API boundary. A fixed finite fault/control matrix measures
refusals before→after and successful digest/exception-propagation controls.
Counting command: `python3 tests/llamacpp-live/install-io-grid.py --arm both --json`;
`--arm frozen` is intentionally exit1; `--arm current` must exit0. Results and
measured commit are appended after the official committed-tree run.

This is the planned bare-helper debt from SCORECARD's R21 Planned row, not a
new serving capability or a score inflation. Capability window ends at 2 of4
since R20; no capability row is acquired. No producer-level red-before is
claimed: its existing install_links(server, tree) backstop already rejected
ordinary omitted regular files. The matrix separately records that two-helper
backstop after transient injections; it does not run the server CLI.

## Gate

Opened 2026-10-21; all quotes below are at most25 words. Raw page locations
are corroborated in build/advice/SrcOpen.md, SrcOsLstat.md and SourceReject.md.

| Candidate | Decision | URL, location and located quote |
|---|---|---|
| Visible file-open errors | admit S075 | https://docs.python.org/3.14/builtins/functions.html#open, Python3.14.8 Built-in Functions, open first paragraph: “If the file cannot be opened, an OSError is raised.” |
| Visible filesystem errors versus intentional nonregular skips | admit S076 | https://docs.python.org/3.14/library/os.html, Python3.14.8 module introduction Note: “All functions in this module raise OSError (or subclasses thereof) in the case of invalid or inaccessible file names and paths”; os.lstat first paragraph separately says “does not follow symbolic links.” |
| os.access-only repair establishes successful later hashing | reject S077 | https://docs.python.org/3.14/library/os.html#os.access, Python3.14.8 second Note: “I/O operations may fail even when access() indicates that they would succeed”; flip: actual errors already refuse and access is diagnostic only |
| New serving repertoire or producer-level escape | reject | Existing producer backstop is documented in R21 lesson lines134–138 and read by CritClaim/CritOracle/CritMistake; a helper-only red cannot establish a new producer acceptance defect. |
| Race-free/authenticated directory snapshot | reject | CritRace.md: lstat→open swap, FIFO blocking, in-place rewrite, post-hash/before-launch and post-launch replacement remain out of scope. Flip requires separately executed controls and a new declared claim. |

Python documents error signals, not kama's fail-closed policy. The policy and
matrix outcomes are own-work. Existing SOURCES rows S001–S074 are unchanged;
no status/recheck/used-by edits. Added S075/S076 mined and S077 rejected, all
scoped tierA. Four other opened page-level candidates (exceptions, mock,
hashlib, stat) are excluded as unnecessary to the admitted distinction;
scandir/listdir/lstat/access are sections of the same os page, not extra
page-level rows. No frontier ground is moved to core: this deepens an existing
identity capability. Corpus expansion is not source-row growth.

Outside non-author admit/reject spot-check remains the orchestrator's closure
duty. Build and residual reviewer seats are author-dispatched advice, never
promotion or outside discernment attestation.

## Mistakes

| ID | Class | Evidence | Captured-by | Fix / failure witness |
|---|---|---|---|---|
| M1 | Consumer backstop mistaken for reusable helper contract | R21 lesson's final Planned debt; frozen install_tree at10271460 lines178–202; build/advice/RevengeSkip.md and CritMistake.md | KQ29 barred skipped unreadable members but its implementation protected main through install_links, not the helper's own return contract | Raise SetupError at each of the three helper OSError catches; independent fixed fault set is intentionally red against frozen bytes and clean only after refusal; committed run records are appended below. KQ30 captures helper vs caller and null vs partial distinctions. |
| M2 | Scope inflation in initial draft would imply a producer-level escape | build/advice/CritClaim.md, CritOracle.md, CritExit.md | KQ14 semantic boundary and KQ27 measured attribution | Claim is explicitly function-level. Supplementary paired_problems exposes the existing backstop rather than taking credit for it. This wording correction is not claimed as a separate fail-capable fix. |
| M3 | L1 used incorrect line numbers in an uncommitted matrix edit | tool edit response for matrix snapshot491F showed malformed function; repaired before any execution/commit by replacing the displayed damaged region | hashline tool response, before execution | Corrected at snapshotD86C. Not a scored improvement or independently fail-capable fix; no broken bytes are credited as a passing measurement. |

## Integration and boundaries

All production edits are by the L1 integration owner. ApiFix, Matrix,
CallerRepair and Recipe died before delivering code (capacity errors). Several
read-only seats observed the L1's expected dirty integration tree and called
it a seat write-scope breach. This inference is rejected: those edits were
made by the L1's recorded edit/write calls, not an unidentified seat. Reports
are preserved byte-for-byte as evidence, never rewritten to hide the mistake.

Adopted advice: retain tuple/map/digest on success; catch only OSError; preserve
exception cause and useful stage/member/error detail; explicit null versus
partial counts; exact injected-fault activation; programming-error/interrupt
controls at every catch site; historical schema unchanged; both direct caller
adaptations; actual file-error handling rather than os.access-only repair.

Not adopted: a scandir rewrite, receipt-schema tightening, system-library
inventory, post-scan authentication or race hardening. These are outside C1.
The receipt gate's only edit is a legacy-null comment. Frozen scripts and all
prior lessons/receipts remain unchanged. The install-links grid still has its
pre-existing non-root chmod condition; C1's new matrix is permission-independent.
The e2e pristine identity failure maps to could-not-evaluate2; its existing
pristine link-problem behavior is unchanged.

C1 is scan-time error/identity separation, not an atomic snapshot. Unpinned
subdirectory contents, external libraries/loader configuration, mutable files,
and lstat→open/hashing→launch races remain named limitations. No registered
consumer endpoint was probed, repointed or restored; no model loaded or server
started for this round. No secret/config/environment values were inspected.

## Measurements and final review

Official results are appended below after the clean committed-tree run. This
initial lesson declares the falsification criterion; it does not claim an
unrun test passed.

## Prior outside closure and Gate supplement (D1–D4)

`MANIFEST.json` rounds[406] is the non-author R21 closure; no separate
`round-21-verifier-spotcheck.md` file was present. CloseKama21 independently
remeasured the clean R21 tree7054dba1 and agreed with one source admit and
one reject, while holding discernment unchanged. Routed feedback:

- D1: appended final7054dba1/33-command results to SCORECARD rather than
  presenting b76727f3/28 as final. Retained commands.json names7054dba1,
  33 rows,0 mismatches; no R21 live run is reexecuted here.
- D2: prose supersessions did not satisfy v1's correction-row representation.
  Reopened all nine sources below and added S078–S086, preserving S066–S074
  and filed prose. KQ31 makes prose-only corrections insufficient. This is
  record repair, not new technical ground or a capability.
- D3: R21 accounting correction: build86+falsify67=153; original terminal
  deaths RegressSkillGates (Haiku429) and ConnectorSiblingReports
  (Antigravity Gemini429 RESOURCE_EXHAUSTED), no replacements. At closure
  build85 reports/falsify66 reports. The filed still-running build description
  was stale. These are the outside closure's reconciled R21 counts, not R22.
- D4: report-audit Git-config/history trust and UTF-8/error-handling debt is
  not a hardening claim this round. Restricted guidance to trusted fleet/lane
  repos; KQ32 rejects extrapolation to untrusted repositories. Environment
  scrubbing does not suppress repository-local configuration. No exploit
  reproduction or untrusted-repo execution. Broader hardening remains
  explicit frontier because it is causally separate from C1. Existing
  selftest fallback/GIT_DIR assertion debt, prelaunch races, chain bound,
  JSON duplicate-key/Unicode limits remain unclaimed.

### Gate — reopened correction rows

All opened by the L1 on2026-10-21. Every quoted fragment is ≤25 words, located
at the named source/section; corrected scope enters new rows, not old cells.

| Row | Reopened URL | Revision/anchor and quote |
|---|---|---|
| S078 supersedes S066 | https://man7.org/linux/man-pages/man8/ldconfig.8.html | man-pages6.19 DESCRIPTION chain example: “where the middle file (libfoo.so.1 here) is the SONAME for the library” |
| S079 supersedes S067 | https://man7.org/linux/man-pages/man8/ld.so.8.html | man-pages6.19 DESCRIPTION step4: “From the cache file /etc/ld.so.cache, which contains a compiled list of candidate shared objects previously found” |
| S080 supersedes S068 | https://nix.dev/manual/nix/2.34/protocols/nix-archive/ | 2.34-series NAR EBNF: `symlink = str("target"), str(target);` |
| S081 supersedes S069 | https://go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go | tagv0.42.0 HashDir line76: `return os.Open(filepath.Join(dir, strings.TrimPrefix(name, prefix)))`; decoded source retained at `.ufo/waves/round-22/sources/dirhash-v0.42.0.go` |
| S082 supersedes S070 | https://git-scm.com/docs/gitrevisions | Git2.56.0 SPECIFYING REVISIONS sha1: “a leading substring that is unique within the repository”; type-peeling entry separately defines recursive dereferencing |
| S083 supersedes S071 | https://git-scm.com/docs/git-cat-file | Git2.56.0 BATCH OUTPUT ambiguous paragraph: “an ambiguous short sha”; emitted record `<object> SP ambiguous LF` |
| S084 supersedes S072 | https://docs.jj-vcs.dev/latest/cli-reference/ | latest generated reference, jj metaedit: “the committer name, email, and timestamp are also updated for all rebased commits.” Not an installed-version pin. |
| S085 supersedes S073 | https://git-scm.com/docs/git-log | Git2.56.0 PRETTY FORMATS percent-at: “author date, UNIX timestamp”; percent-ct: “committer date, UNIX timestamp” |
| S086 supersedes S074 | https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html | historical HOWTO3.1.1 installer paragraph: “installers must specifically modify symbolic links to update what the linker will use for a library.” Queued; no installer-role claim. |

Bounded ld.so terminology sweep: regex `(?i)symlink|symbolic` over the full
reopened page text returned no matches (read/grep tool evidence); the positive
claim rests on its search-order text. Nine identified/screened/included
correction candidates,0 exclusions. Added S078–S085 mined/S086 queued, old
cells unchanged. Together with S075–S077 this round adds twelve rows, not
the earlier three-row provisional source population.

## Build closure and candidate dispositions

Build spec+native assignments:64 unique seats. Role mix and command-derived
report count are in `build/completion-summary.json`; original first-turn
outcomes47 completed/17 failed. After peer-induced resumes of ApiFix,
CallerRepair and Matrix, latest outcomes50 completed/14 failed; all17 original
deaths remain recorded in `build/original-deaths.json`. No replacement seat
or model/routing change. Retained reports52 include partial ReadGone and
BadNameControl despite their provider deaths. The L1 did not request those
resumes; it froze the resumed writers and preserved their unintegrated
candidates under build/out before removing duplicate sandbox scaffolds.

This corrects the earlier blanket wording that code-writing seats died
before delivering code: original failures do not prove no partial artifact
existed. Matrix's claimed original-draft timing is self-reported, not needed
for the measured claim. Canonical stage/member-qualified producer and matrix
are L1-authored; bare-token sandbox candidates never landed. The receipt/e2e
prefix remains colon-qualified, matching canonical code without aliases.

Adopted final advice: guaranteed reverse enumeration control and a late-read
fault after one full1MiB chunk. Unadopted optional controls (additional names,
link types, vanished phantom membership) are not in the fixed measured set.
NullDigest's report contains an executed fixture witness despite its final
“No verification runs” sentence; that build-time witness is excluded from
official measurement. Build peer reports that mistake L1 edits for seat
writes, or candidate bare-token grammar for canonical code, remain preserved
but are not the integrated contract.

Residual inventory has60 bounded attack items (32 fixed cells,8 selftest
fixtures,12 source rows,3 consumers,4 routed records,1 trust restriction),
below64; no padded second swarm. Eight ordinary fresh falsifiers cover that
inventory after this integration commit. Their results are author-dispatched
advice, not the outside admit/reject spot-check.
