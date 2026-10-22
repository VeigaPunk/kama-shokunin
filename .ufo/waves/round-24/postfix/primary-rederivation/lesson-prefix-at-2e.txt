# kama — round 24 lesson (2026-10-21)

Round base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Preimplementation registration: `.ufo/waves/round-24/preregistration.json`,
landed `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`.
Motivation: `LOG.md` §round 24; outside closure MANIFEST rounds[428]
(`rejected-harmed`, CloseMori22). Numeric score calibration7→7 is not an
admission or claim that operability harm was waived.

## Gate

Opened 2026-10-21 by this lane; cited locations and scoped conclusions only:

- **S102, admit**: https://git-scm.com/docs/git-rev-list (last updated
  2.56.0), `--missing=<missing-action>`:
  “The form --missing=print is like allow-any, but will also print a list of
  the missing objects.” This documents encountered-missing output, not a
  numeric exit policy, proof of remote absence, or completeness theorem.
  `--objects` and `--no-object-names` select traversal output and its format.
  Independent opening: build/advice/SrcRevList.md.
- **S103, admit narrowly**:
  https://git-scm.com/docs/partial-clone#_handling_missing_objects
  (last updated2.56.0), §Handling Missing Objects:
  “These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary
  contents”. A paired marker records packaging provenance; its presence
  does not prove every object needed by an audit is absent. This last
  sentence is a lane inference tested by complete-state twins, not a quote.
  Independent opening: build/advice/SrcRepoLayout.md and SrcPartial.md.
- **S104, reject as a proposed completeness oracle**:
  https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c,
  `mark_object`, lines143–149:
  “if (is_promisor_object(options->repo, &obj->oid))” … “return 0;”.
  It returns before checking HAS_OBJ for that promisor object. A green fsck
  is not proof every promised object is locally present. Flip: use a
  separately demonstrated required-object availability test instead of
  claiming this fsck result establishes local availability.
  Independently opened code: build/out/SrcFsck/fsck-builtin.c.

Reopened sources: S089 Git global no-lazy-fetch/no-replace-objects;
S083 batch records; S099 missing-object handling; S094 alternates. No prior
status, recheck or used-by fields changed. Rejected proposed source
correction: SrcCatFile's suggestion that S083 says “absence”; the actual
S083 row says “unresolvable object” and explicitly limits peel-specific
semantics, so that proposed supersession has no premise.

## Mistakes

| Class | Evidence | Captured-by | Fix / demonstrated boundary |
|---|---|---|---|
| scope: metadata-only refusal treated as isolation | r23 closure rounds[428], T01 complete filtered clone correct clean→exit2 | no-trade admission rule, applied by outside closure | r24 preregisters complete-local twin controls independently of candidate; blanket refusal must fail those controls, not be excused as a declared trade |
| number-drift / attribution | r23 lesson:178 says68 reports; actual69 durable reports; filed fleet report itself gives73 seats/4 missing | CritEvidence and ScribeLog | named appended correction in LOG; do not rewrite filed r23 bytes or attribute the erroneous literal to the wrong file |
| scope: process evidence overstated | r23 process-count56 came from a different pattern than the40 truncated identity rows; only19 retained rows tied to FIFO fixtures | CritEvidence | appended provenance qualification in LOG; do not call all56 independently identified FIFO-blocked git processes |
| stale-premise: confusing T01 with F23 | T01 clones with checkout (hydrates its single blob); F23 uses --no-checkout and asserts a real reachable blob is absent | independent outside T01 measurement; base fixture source:195–213,596–602 | retain distinct complete/incomplete oracles; never repin T01 to a refused ungraded trade by assuming all blobless clones are incomplete |

## Outside judgment carried forward

The outside r23 admit/reject source spot-check agreed with admitting S101
and rejecting S095 (rounds[428].verification.spotcheck). Its quality trend
was harmed because a correct runnable workflow regressed; the author's
quality-improved reading is superseded. Source curation and an honestly
disclosed trade do not cancel that operability loss.

## Mistakes — round24 integration continuation

| Class | Evidence | Captured-by | Fix |
|---|---|---|---|
| scope: the initial registration's blanket unknown rule contradicts the supported local-object contract | `preregistration.json` expected_after[3]; CritScores' exact historical spliced-hash/errata witness; original tool contract:12–19 | independent CritScores/CritUnknown/CritNoTrade review before L1 candidate source inspection | retain the initial expectation as withdrawn/not-achieved, append `oracle-amendment-1.json`, freeze the independent44 before L1 inspection, and grade prospective behavior separately; PM02 is the negative control for the rejected blanket rule |
| vacuous fixture: ledger not exercised and a spliced token only39 hex | GridOracle Correction2; `extra=[]` always added --no-errata; mistyped HIST_TAIL | L1 static runner review, then explicit fixture premise checks | enable ledger only for the declared errata cases; assert40-hex and local absence; report raw versus uncorrected defects separately; original expectation bytes remain filed |
| survivor / indistinct cross-repository fixture | GridOracle Correction3; cross_repo=True accepted but ignored; PM05 initially survived | MutationOracle's sensitivity probe | put a fleet-only commit in Landed and assert it is absent from the lane and present in the fleet; no expected exit/token rule changed |
| stale premise: hidden cited blob remained locally present | GridOracle Correction4; PG46 deleted only its parent subtree, so correct lookup returned found | L1 source inspection of the five reported pristine mismatches | remove both subtree and cited blob and assert absence in both repositories; preserve the fixed outcome rather than altering the candidate to misclassify a present object |
| gate sensitivity: twin mismatch computed after failure lists | GridOracle Correction2 source review | L1 static review | compute mismatch failures after twin comparisons; a substantive document mismatch must make the gate fail |

L1 deliberately declined the later proposed path-expression relaxation
of the grid's strong `names_any_of` refusal pins. Instead, the tool names
the actual root-tree OID on a failed required read, and the fixture-only
PG46 repair is composed onto the previous strong grader. This is not an
oracle adjustment to make a candidate green; the47 expected cells remain
byte-identical to the frozen44 plus the independently filed3-cell supplement.

Consumer change within the newly added rows S102/S103/S104:
used-by `corpus/lessons/round-24.md` →
`corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md`.
No S001–S101 field changed. The Git>=2.45 prerequisite is explicitly not
approved or repaired: R23-H2 is carried as the round24 L0 question.

## Gate consumer reconciliation (after build source review)

ConnPriorSources found two ledger-level support defects, not a failed repair.
S095 was already rejected but still named the current auditor; that consumer
now points at the supported bytes-mode row S096. The immutable rejected
S095 teaches cell is not rewritten: S105 is the explicit superseding
rejection record, while S096 remains its narrowed positive replacement.

- S105, reject: https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode,
  accessed2026-10-21, opening titlePython3.14.9 (series URL). Located quote
  in bytes.decode errors: “If 'strict' (the default), a UnicodeError exception
  is raised.” The retained reader snapshot has zero matches for subprocess,
  TextIOWrapper, or text mode; command: regex case-insensitive counts over
  `.ufo/waves/round-24/sources/python-bytes-decode-reader.txt`; observed
  counts0/0/0. `.ufo/waves/round-24/sources/S105.json` pins that snapshot.
  This page cannot document those different APIs; S097/S098 anchor them.

Only mutable used-by cells changed below; all immutable data of S001–S104
is preserved. Status/recheck unchanged. Each consumer transition is logged:

| ID | used-by old | used-by new |
|---|---|---|
| S083 | corpus/lessons/round-22.md | corpus/lessons/round-22.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md |
| S089 | corpus/lessons/round-23.md, tools/report-landing-audit.py | corpus/lessons/round-23.md, tools/report-landing-audit.py, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md |
| S094 | corpus/lessons/round-23.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md |
| S095 | corpus/lessons/round-23.md, tools/report-landing-audit.py | corpus/lessons/round-23.md, corpus/lessons/round-24.md |
| S096 | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, tools/report-landing-audit.py, corpus/lessons/round-24.md |
| S099 | corpus/lessons/round-23.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md |
| S100 | corpus/lessons/round-23.md, tools/report-landing-audit.py, tests/report-audit/repo-state-grid.py | corpus/lessons/round-23.md, tools/report-landing-audit.py, tests/report-audit/repo-state-grid.py, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md |
| S101 | corpus/lessons/round-23.md, tools/report-landing-audit.py | corpus/lessons/round-23.md, tools/report-landing-audit.py, corpus/lessons/round-24.md |
| S102 | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md, tools/report-landing-audit.py, tests/report-audit/promisor-grid.py, SKILL.md |
| S103 | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md, tests/report-audit/promisor-grid.py, SKILL.md |
| S104 | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md, SKILL.md |

This final consumer reconciliation supersedes the earlier
“No S001–S101 field changed” statement only for the mutable used-by
column. No immutable row data, status or recheck value was changed.

## Named residual debt carried, not discharged

ConnClosure's final build review routes the old identifiers explicitly:
RowF12, RowF21, RowF22, RowF23, RowF26, RowC04, ExecSecondLanded,
ExecAmbiguityFixture, RevengeGitfile, CritTradeoffHarm H2, SentinelDoSW2,
ConnSiblingTools, and supplementary surviving detector variants
N01/N02/N03/D02/D03 remain the historical r23 near-variant/coverage debt.
Their original evidence is `.ufo/waves/round-23/falsify/advice/` and
`corpus/lessons/round-23.md` §Falsify-wave disposition. This round does not
claim those classes closed merely because the primary local-evidence
contract was repaired. The weak historical assertions
`uncommitted-draft-uses-now` and `inherited-GIT_DIR-untouched` remain outside
the declared repair, not silently fixed.

An additional bounded coverage limitation is preserved: the47-cell grid
does not distinguish refs-only traversal from all present-object roots
for a dangling commit that names a missing cited blob. The implementation
uses present commit/tree/tag roots and ConnClosure's independent probe
holds; fresh falsification is asked to attack that distinction. The47
registered expectations are not rewritten to add headline credit.
R23-H2 remains carried, not discharged, pending the operator ruling.

## Gate

Continuation after final build-source review; this adds the late rejection
record to the initial Gate without rewriting its filed entries.

- S105, rejected: https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode,
  opened2026-10-21, titlePython3.14.9 (series URL), bytes.decode errors
  paragraph: “If 'strict' (the default), a UnicodeError exception is
  raised.” This does not document subprocess/TextIOWrapper text mode;
  the retained public reader snapshot's searches give0/0/0, pinned in
  `.ufo/waves/round-24/sources/S105.json`.

The final consumer-reconciliation table above supersedes every earlier
no-used-by-change reading in this lesson; only mutable consumer cells
changed, with their old→new values retained. No old immutable teaches
claim was silently repaired.
