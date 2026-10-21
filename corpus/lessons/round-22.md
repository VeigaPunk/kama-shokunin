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

## Residual source-review integration

FinalSources reopened all twelve rows S075–S086, finding their quotes/scopes
sound (`residual/FinalSources.md`, receipts/pages beneath FinalSources/).
It found two record issues, both learned without rewriting immutable cells:

- S075–S080 `used-by` old `corpus/lessons/round-22.md` → new
  `corpus/lessons/round-22.md, corpus/knowledge/llamacpp-loading-lifecycle.md`.
  Their status/recheck remain unchanged; every other existing cell is intact.
- The Python `/3.14/` pages changed title3.14.8→3.14.9 during the round,
  with unchanged quotes. The L1 reopened both and appended S087/S088:
  opening-time3.14.8 is historical, not a micro-version URL pin. These new
  correction rows avoid repeating D2's prose-only pattern. Source population
  is now fourteen added rows, superseding the earlier twelve-row forecast.

### Gate — micro-version clarification

Both opened2026-10-21 by FinalSources and the L1; page titles3.14.9:

| Row | URL and location | Located quote (≤25 words) |
|---|---|---|
| S087 supersedes S075 | https://docs.python.org/3.14/builtins/functions.html#open, Built-in Functions open first paragraph | “If the file cannot be opened, an OSError is raised.” |
| S088 supersedes S076 | https://docs.python.org/3.14/library/os.html, introduction Note and os.lstat first paragraph | “All functions in this module raise OSError (or subclasses thereof) in the case of invalid or inaccessible file names and paths”; lstat “does not follow symbolic links.” |

Two identified/screened/included correction candidates, zero exclusions.
S077's opening-time version label remains a historical access observation,
not an exact-micro URL pin. Durable ld.so negative-sweep input and command are
`sources/ld.so-man-pages-6.19.txt` and `sources/ldso-sweep.json`; no-matches
was rerun over the complete reader text. The read tool's raw slice UI-footer
defect was reported, and structured displayContent text preserved the source
without the footers; no partial capture is credited.

## Residual verdicts before official measurement

Eight ordinary falsifiers: FinalMutations, FinalSources and FinalClaim
completed; five reviewers died immediately on Devin free-model rate limits.
Exact last errors and traces are retained in
`residual/completion-summary.json`; no replacement or retry identity.
Round total72 unique seats,22 original provider deaths (19 latest failures
after the three same-identity build resumes),55 retained reports.

- FinalMutations: five actual-producer mutants killed with emitted
  `incomplete-install-identity`/exit1; deleted list/stat/read refusals produce
  3/6/9 failed rows, broad Exception/BaseException catches3/6. Pristine and
  each byte-restored source pass all32 rows. Patches, digests, exact failed
  names and raw streams are retained under `residual/FinalMutations/`.
  Broad catches yield AttributeError instead of preserving the injected
  exception: the completed matrix grades that specific propagation mismatch,
  not a crash exit alone.
- FinalClaim: no blocking issue at971d4549, pending official clean-tree run.
  Independent matrix0/18→18/18, controls14/14;13 real-tree successes identical,
  five real-errno helper failures refused by both old/new producer blocks,
  real install-tree digest unchanged. Actual receipts are at
  `residual/FinalClaim/FinalClaim/receipts.json` (the final chat summary
  omitted the nested directory; the filed seat report cites it correctly).
- Detail-erased mutant survives: the trailing error description is
  informational, not measured. Stage/member/refusal/cause are measured.
  Producer stat/read text now describes the first failing file/operation,
  rather than the old later-scan unreadable/not-hashed list; stable prefix
  unchanged. No exact diagnostic text or aggregation claim.

Source review findings were integrated above. Residual attack inventory
grew60→62 when two micro-version correction rows were added; still below64.
Fresh primary reopens ground those rows; outside non-author sampling remains
the closure's duty. The official recipe follows after the next clean commit.

## Official measured outcome — 6433390a

The L1 ran once after all build/residual seats settled:

`python3 .ufo/waves/round-22/run.py --recipe .ufo/waves/round-22/recipe.json --out .ufo/waves/round-22/runs/6433390a`

Measured clean committed branch tip
`6433390a5c8f4412c2410c114309ffced5c0572f`:29/29 expected exits,0
timeouts/mismatches, harness0. `runs/6433390a/commands.json` preserves actual
argv, UTC starts, exits and stream digests; output publication is a later
commit, not a claim the outputs existed inside the measured input tree.

| C1 finite measure | Frozen10271460 | Current6433390a |
|---|---:|---:|
| Activated OSError fault rows | 18 | 18 |
| Explicit helper refusals | 0 | 18 |
| Null results returned under fault | 3 | 0 |
| Partial digests returned under fault | 15 | 0 |
| Unchanged success/propagation controls passed | 14/14 | 14/14 |
| Contract violations | 18 | 0 |

Counting command `python3 tests/llamacpp-live/install-io-grid.py --arm both
--json` exits1 because the frozen arm is intentionally red; selected current
arm exits0, frozen1. Selftest8/8, including always-refuse/empty CNE controls
and refusal-deletion/broad-catch fixtures. Population SHA
`5b38422c32c5fb8bdfe1b69ed003f260914c339a2c12abf0f984790f4ca9833d`;
frozen sourcecec67949…, current8c0dbb2b…. The old two-helper backstop's
18/18 refusals remain separate from the helper improvement.

No-harm recipe meets every declared exit: links grid/current21 cases and
its selftest, producer selftest, receipt gate12 VALID+1 NOT-EVALUATED and99
mutations+unreadable, three old receipts, error census current misclassified0
and unrun0, GGUF23/23 with oracle/receipt agreement, citation17/17,
snapshot30 pass0 fail, prelaunch unpinnable3/3 with child_pid/argv null.
No live model server or registered-consumer probe ran; isolated ownership
socket/stub selftests are not new serving evidence.

Source census/validate commands are the exact absolute argv in the recipe.
Rows74→88, A70→83/B1→2/C3; mined60→72/queued7→8/rejected7→8,
missing0. Validate/census exit0;20 W04 warnings are scoped duplicate URLs,
not enum/shape failures. Source-pair guards base10271460→971d4549
(12 additions) and971d4549→6433390a (2 additions, permitted used-by
changes) both exit0; aggregate14-addition guard also0. Streams retained.

Author verdict: C1 verified narrow calibration improvement, score7→7,
no other observed axis harmed. Expansion unchanged; quality improved;
discernment improved through learned prior outside D2/D4 criteria, not
self-attested current outside review. No capability or promotion row added.
Non-author round22 admission/sample remains the orchestrator's next act.

## Final-report conformance discovery — same calibration axis

While preparing the required verbatim validation outputs, the L1 found a
second calibration distinction within this same round claim: an upstream
revision inside a curated source URL is not a lane/fleet commit citation.
Both actual repos returned128 for that upstream object (observed once, not
rerun); the old auditor's unconditional FULL scan would misclassify the
mandatory census text. No errata row or hash-specific whitelist is added.

| ID | Class | Evidence | Captured-by | Fix / discriminating witness |
|---|---|---|---|---|
| M4 | Untyped source-URL hash treated as owned commit citation | required `fr-sources-validate.stdout` at6433390a; old auditor atcc9f8d3; `report-source-fix/ReportSourceCritic.md` | KQ28's all-token wording missed the source-reference type | Exact committed Registry URL occurrences outside Landed get their own classification; bare/superset/unregistered/Leads/worktree-only cases stay checked. `report-source-fix/ReportSourceFix/out/red-green-witness.py` pins the same census report and expected old-red/current-green finding; actual results appended after its committed-tree run. KQ33 qualifies only the full-token rule. |
| M5 | Proposed final audit command used lane rather than fleet report path | ReportSourceFix.md proposed command and L1 addendum | round contract's absolute report path | corrected before execution; no misroot write occurred. Record correction only, not a scored fail-capable fix. |

This is a report-conformance repair on calibration, coalesced with C1 under
the one-claim-per-axis rule, not a new serving capability or another axis.
The original29-command helper measurement stays intact. Each repair is
independently measurable: helper32-cell comparison does not need the auditor,
and source-URL recognition does not need the helper.

Two fresh ordinary seats (ReportSourceFix executor, ReportSourceCritic)
completed this newly discovered bounded followup; no replacement of any dead
seat. Total74 unique seats,22 original deaths,57 retained seat reports.
The two-seat ordinary reservation was obtained immediately after dispatch,
not before (roster.json records grant/live/cap); the64-seat wave had proper
pre-dispatch reservation. No cap refusal, route/model change or new L0.

The candidate was statically reviewed against nineteen discriminating
cases; the L1 additionally blocked nested full-URL substring matches, removed
an unused private wrapper, and made the witness independent of its disposable
clone. It now has a code-pinned manifest and CLI positive/tamper/error controls.
No new followup check is called passed here before execution.

Boundaries: classification uses only structurally valid Registry source
cells from committed --branch data; exact full HTTPS and census-normalized
forms are recognized. It is occurrence-scoped, never hash-value-scoped.
Landed checks are unchanged. Missing legacy registry supplies no exemptions;
Git/type/decoding errors are CNE. Source URL classification is neither source
truth/provenance validation nor D4 untrusted-repository hardening.

## Final conformance measurement — 80a6d07c

The static M4 prediction is now observed, not merely inferred. On clean
committed input `80a6d07c09593191b7a6f86d92851fe3cc0619c2`:

`python3 .ufo/waves/round-22/run.py --recipe .ufo/waves/round-22/report-source-fix/recipe.json --out .ufo/waves/round-22/report-source-fix/runs/80a6d07c`

All10 declared exits met, harness0, no timeout/mismatch. The pinned witness
returns red-green-match0: old script1 with one false owned-hash finding,
current0 with no defects and explicit source-URL classification. Manifest,
old script, registry, census and report fixture digests are checked before
comparison; actual lane/fleet Git writes false. Audit selftest50/50; witness
selftest6/6, including snapshot tamper and child-error-not-verdict controls.

Historic rounds10–21 remain9 raw defects/all9 corrected,49 required and5
post-report commits over12 reports; invalid/unmatched/uncorrected0. The
current helper remains18/18 refusals,14/14 controls,0 returned null/partial
identities; citation17/17 clean. Final source census/validate0 at88 rows;
no immutable-source violation. No upstream validity or untrusted-repository
security guarantee is inferred from URL classification.

Receipts under `report-source-fix/runs/80a6d07c/` are published after the
measured input, not claimed present inside it. The original29-command input
6433390a and the later10-command input80a6d07c are separate evidence.
Final C1 author verdict verified (calibration7→7); no observed axis harmed.
Expansion unchanged; quality improved; discernment improved via learned
prior outside feedback. Independent non-author admission remains pending.
