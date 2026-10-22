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

## Gate consumer reconciliation — completion annex (falsify ConnSources)

The table above was written in commit `f1e755e`, which also added three
citations in the same commit without listing the citing file in the affected
`used-by` cells. This annex completes the log; only mutable `used-by` cells
change, and no immutable row data, status or recheck value moves.

| ID | used-by old | used-by new | citing path added |
|---|---|---|---|
| S095 | corpus/lessons/round-23.md, corpus/lessons/round-24.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/knowledge/error-is-not-a-verdict.md:124 |
| S097 | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md | corpus/lessons/round-24.md:101 |
| S098 | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md | corpus/lessons/round-24.md:101 |

Citations: `corpus/knowledge/error-is-not-a-verdict.md:124` names S095 ("S105
records the explicit rejection rationale for S095's cross-API inference without
rewriting that filed row"); `corpus/lessons/round-24.md:101` names S097 and
S098 ("This page cannot document those different APIs; S097/S098 anchor them.").
Both citations are new in `f1e755e` — `git log -S` on each string returns that
commit alone.

### S105 quote rendering qualification (falsify ConnSources)

The S105 quote as recorded in `corpus/SOURCES.md:117` and
`.ufo/waves/round-24/sources/S105.json:8` is the **rendered** form of the
sentence. The pinned reader snapshot
`.ufo/waves/round-24/sources/python-bytes-decode-reader.txt`
(sha256 `54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80`)
stores it in Markdown markup, at **two** raw lines:

```
1397: If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.
2943: If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.
```

Raw occurrence counts over the whole pinned file: the Markdown form **2**, the
recorded plain form **0**, the display-equivalent plain form (markup stripped)
**2**. Line 2943 sits in the `bytes.decode` / `bytearray.decode` errors
paragraph (heading `bytes.decode(*encoding='utf-8'*, *errors='strict'*)` at
:2933, `bytearray.decode(...)` at :2935); line 1397 is the same sentence in the
`bytes.encode` errors paragraph. The recorded quote is the reader-visible
sentence and is byte-accurate against the live page's visible text
(`https://docs.python.org/3.14/builtins/stdtypes.html`, plain form 2x), so the
row's teaching is unchanged; only the byte-locatability of the quote inside the
pinned artifact differs. The row's evidentiary load is unchanged and does
reproduce exactly: case-insensitive counts over the same pinned file give
subprocess 0, TextIOWrapper 0, "text mode" 0, "text-mode" 0, text_mode 0.

### S096/S105 authority split — facet qualification (falsify ConnSources)

Two rows open `supersedes S095 —` and they are **distinct facets of one filed
row**, not rival corrections:

- **S096** (`corpus/SOURCES.md:108`, mined) carries the **positive** fact that
  survives: its scope is "Python 3.14-series `bytes.decode` default error
  handler only; a series URL", and its teaching is that `bytes.decode` with the
  default `strict` handler raises `UnicodeError` on invalid bytes — which the
  current auditor's bytes-mode `git()` decode relies on.
- **S105** (`corpus/SOURCES.md:117`, rejected) is the **explicit rejection
  record** for the cross-API inference S095 filed: its scope says "not a new
  decoder fact", and its teaching rejects the claim that `bytes.decode`'s
  strict-default documentation establishes subprocess text-mode or
  `TextIOWrapper` defaults, flipping to the separately opened S097/S098 anchors.

So the authority for the positive decoder fact is S096 alone; S105 records only
the rejection and points at S097/S098 for the different APIs. `CORPUS.md` rule 2
(`/home/vgpnk/Projects/shokunin/CORPUS.md:116–118`) requires a correction to be a
new row whose `teaches` opens `supersedes S0NN —`; it states no single-successor
rule, and rule 4 sets no row quota. The census agrees: the S096/S105 same-URL
pair is a `W04` "duplicate url … across scopes" notice
(`scripts/sources-census.sh:644–649`), not an `E04` "within scope" error, and
validate exits 0 with no E-codes. Both immutable claims are preserved as filed;
this paragraph records which facet each row carries so a reader does not treat
the two `supersedes S095 —` openings as a contradiction.

## Gate consumer reconciliation — S093 completion (falsify ConnSources)

This annex adds the one remaining row whose citation the current corpus
records but whose `used-by` cell did not name. The correction is justified by
the current documents, not by re-opening round 23: `corpus/lessons/round-24.md`
and `corpus/knowledge/error-is-not-a-verdict.md` each assert, in the files as
they now stand, that their recorded consumer set is reconciled
(`corpus/knowledge/error-is-not-a-verdict.md:126–127`, "The registry's mutable
consumer cells and the round24 lesson's old→new table reconcile these actual
uses."; `corpus/lessons/round-24.md:104`, "Each consumer transition is
logged"). While S093's cell omitted the knowledge entry that cites it
(`corpus/knowledge/error-is-not-a-verdict.md:62` and its source line `:79`,
`source: S093, S096, S097, S098, …`), those claims were false for S093 — the
same false completeness the annex above removes for S095, S097 and S098. Only
the mutable `used-by` cell changes; no immutable row data, status or recheck
value moves, and no row is added.

| ID | used-by old | used-by new | citing paths added |
|---|---|---|---|
| S093 | corpus/lessons/round-23.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/knowledge/error-is-not-a-verdict.md:62, :79; corpus/lessons/round-24.md (this annex) |

`corpus/knowledge/error-is-not-a-verdict.md` is listed as a consumer of S093
because its round-23 section already relied on S093's teaching ("git may emit
non-UTF-8 log text verbatim (S093)", `:62`) and named it in its own source
line (`:79`). `corpus/lessons/round-24.md` is listed because this annex names
the row. The lesson's earlier mention of S001 (`:83`, "No S001–S101 field
changed") is a range reference over the ledger, not a citation of S001's
teaching, so S001's cell is deliberately left unchanged.

## Mistakes — round24 falsify-wave continuation

| Class | Evidence | Captured-by | Fix / demonstrated boundary |
|---|---|---|---|
| cross-store presence: the "this store holds the object" fact was taken from the merge of every audited store while the classification was per store, so an object living in the fleet only looked present in the lane and the lane's own probe turned it into `unknown` (exit 2 `unknown: unavailable required object: 28d34a63…`) where the contract wants the proved mismatch (exit 1 `landed-unresolved`) | StoreLocalPresence README §"The defect"; CodeLookupMerge | falsify wave at parent 2e254a1, before the repair cutover | presence is the store's own bare answer, never the merge of all stores; no reverse-order workaround, no metadata classifier, no completeness gate, no weakening of the unreadable-tag case |
| unknown outranked a known wrongtype for the same canonical object: a tag present in both stores whose target only one store can serve merged to `unknown` (exit 2) although another store had proved the mismatch | StoreLocalPresence README §"Second defect" (target in the fleet only / lane only → `wrongtype`, exit 1; in neither → `unknown`, exit 2) | falsify wave | reconciliation is per canonical object id; objects behind one abbreviated name are not reconciled, so the round-23 ambiguity behaviour stands |
| an unselected round's ledger row could decide the verdict: every hex correction was read and every unresolvable row counted, so a row of an unaudited round made a clean selected-round audit fail (exit 1) | StoreLocalPresence README §"Third proposal" §1 (CodeErrataBoundary F1) | falsify wave | the correction lookup inputs and the invalid-row comprehension are both restricted to the selected rounds; no object of an unselected round is read at all |
| required reads failed as bare git errors: the committed errata read and the open-range fleet listing returned a raw git message instead of the required-read class | StoreLocalPresence README §"Third proposal" §2 (CodeRequiredReads) and §"Fifth proposal" (CaseFleetTree M1) | falsify wave | required reads carry the cause and the path inside the message and add the `unavailable required object:` class; a fatal cause (timeout/OS) does not spend a second diagnostic timeout; the 20 s per-call deadline is unchanged |
| the opaque (name-hiding) fallback was computed over the whole store, so unrelated unreachable garbage in a repository made an ordinary audit refuse where the original local contract wants the ordinary finding (the reported 1 → 2 → 1) | StoreLocalPresence README §"Seventh artifact" (CodePerRunCache F2) | falsify wave | two root sets: known unavailable referenced ids are encountered from all present local commit/tree/tag roots, while opaque missing-name boundaries come only from the pinned audit root; no whole-store or reachable-tree completeness precondition; all-resolved inputs stay runnable despite unused holes |
| a harness fault could be scored as a legitimate refusal: the grid kept only a 300-character stderr tail, so an internal-error identity could be truncated away and an exit 2 could earn a mutant kill | GridAttestationV3 README §"The gap" (DocQualityF1) | falsify wave | the internal-error identity is captured from the full stderr as the boolean row field `internal_error`; such a row is never met — an internal error or traceback is an unmet observation and cannot earn a kill |
| a crash was credited as a kill: the mutator ignored `row.traceback` and any internal-error marker, and a violated row outside the mutant's attribution could be credited | MutationEvidenceV6 rationale §1–§2 | falsify wave | a harness fault is could-not-evaluate (exit 2, zero kills) for a traceback, an internal error, an exit outside 0/1/2 or a malformed verdict; a violated row outside `expect_rows` is preserved and reported, earns no kill, and the allowlist is not widened; credited violations are classified from the row's own fields, and a reason-only change is never an acceptance or availability credit |

## Masked and stale premises: three distinctions that are not red regressions

1. The v5 "opaque" fixture deleted a **blob**, not a non-leaf tree or commit, and
   that shape already passed on the pinned tool: it proved nothing about the
   fallback scoping. It is retained, renamed, as an unrelated-blob positive
   control; the real deleted-tree / dangling-commit regression starts at v6
   (a dangling **present** commit naming a real tree the store cannot serve,
   with its blob present).
2. The replay-v1 errata case cited the **same** fleet blob in the report body
   and in the ledger, so the pinned tool aborted at the report lookup: that red
   was evidence of the report-lookup defect, not of the correction consumer.
   v7 and the v2 replay driver isolate it — the report cites a known **lane**
   blob A and the ledger corrects A with a distinct **fleet-only** blob B, with
   an explicit no-errata control showing the body's own ordinary finding.
3. The embedded v7 same-tag test put the target in **both** stores, so the case
   was already green on the pinned tool: it is retained as a positive control.
   v8 adds the actual target-only-in-fleet regression, its lane mirror and the
   both-missing control.

Rule carried into the lesson: every older file and receipt is kept, and a stale
premise is not a red regression; a masked red is evidence for the masking defect
only. A fixture's premise must be asserted where it is established (for the
blobless contract: immediately after the clone, before any optional hydration),
and hydration changes the input state — it is not a detector repair.

## Method correction: the strict comparable baseline is 14/47; the loose 16/47 is retained under its own label

The amended-view comparison was not comparable between the arms: the frozen arm
had been scored with `form_check=False` and without the names pin, the current
arm with the strict rules. Graded with identical strong rules in both arms
(same exit, defect set, reason class, `names_any_of` pin, no-verdict rule and
acquisition rule), the strict comparable frozen baseline is **14/47**; the
earlier **16/47** is the weaker exit/reason-only score, kept under its own
label and never conflated with the strict one. The two cells that differ are
PG16-missing-lane-tree-plain and PG20-missing-fleet-tree-plain, where the r23
base names the required path rather than the tree object id that the strict
names pin rejects. This is a method correction, **not** two additional product
wins. The frozen historical reproduction (47/47) is a separate measurement,
and the final candidate numerator is for the L1 to measure.

## Mutation-contract corrections: PM08 carries no assertion; PM07's V4 retarget is declined

- **PM08** — the static/AST/source-text/wiring assertion proposal is
  **declined, not repinned**. PM08 remains a manual review-only note: no
  alternatives, no assertion of any kind, no construction, no execution, no
  kill credit, skipped by the anchor check (which covers the ten executable
  mutants only); the inventory reads 11 = 10 executable + 1 manual note. Its
  wording is scoped to the candidate's repository-reading wrappers and states
  that it is a manual reading of the isolation flags, not a proof about every
  git call.
- **PM07** — the canonical operator is the restored V3 recipe (the recipe that appends `--all` to the store-wide missing-ID roots).
  It does not broaden the selected-root opaque walk, and no global
  equivalence is presumed.
  The V4 retarget that rooted the opaque, name-hiding walk at every present
  root is **declined** and is not the canonical operator. No kill is presumed
  for PM07; static anchors authenticate mutation applicability only; a valid
  finite survival stays a completed run (exit 0) and is not global equivalence;
  `expect_rows` is an attribution envelope, not a promise that every row
  discriminates; a same-exit diagnostic sensitivity is not an
  unavailable-evidence acceptance witness.
- The legacy empty-selection guard is unchanged; only its attribution is
  corrected — the short-id selector hazard pre-existed the round-24
  retirement, which changed the id set and exposed the staleness of a
  hard-coded short id.

## Disclosure and terminology: the original view, the encoded cells and the withdrawn bucket

**Three different objects are named here and must not be conflated.**

1. **The encoded original cell view** — the expectation manifest's per-case
   `original` column (sha256
   `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`, 47 cases,
   population sha256 `612b0a74…2ed88`). Exactly **seven** cases carry an
   original expectation that differs from the amended one:
   **PG22, PG23, PG24, PG28, PG30, PG34, PG41**. Two falsify-wave receipts
   confirm the set: `m3-frozen-as-current-amended7.json` runs the frozen
   producer (`0df800e`, auditor `da5041a81…65af1`) over exactly those seven
   cases, and `m1-current-amended-subset.json` runs the integrated producer at
   `2e254a1` (auditor `ea51bc35…dd220`) over a ten-case subset and reports
   `met_original: false` on exactly those seven (PG13, PG25, PG37 are
   `met_original: true`).
2. **The literal original clause** — the rule in `preregistration.json`
   `expected_after[3]` (an unknown citation in a promisor-backed repository is
   unknown). Among the graded cases it is the registered reading of **five**:
   PG22, PG23, PG24, PG30, PG41. PG28 and PG34 are amendment-changed but are
   **not** literal-clause cases (PG28's amended expectation comes from the
   amendment's prospective expectation for the unhydrated blobless lane; PG34
   is a non-promisor no-harm twin whose amended expectation differs from its
   original one — an expectation change, not a withdrawal).
   Two counterexamples to the clause live outside the graded matrix and are
   kept separate from it: **PG40**, an *open row* (the runner's `open_rows`,
   not one of the 47 graded cases; `m4-open-PG40.json` records exit 1,
   `met_original: false`, `met_amended: true` under the integrated producer),
   and **F06**, a row of the *retained r23 legacy grid*
   (`tests/report-audit/repo-state-grid.py`, `f_lazy_fetch`), a table the
   `d86b7bea…` manifest does not contain, whose exit-1 observation is
   **inferred** from `build/advice/ConnClosure.md:179` and was not executed.
   The historical "nine" is therefore **7 encoded graded cases + 1 open row +
   1 legacy-grid row (inferred)** — a mixed-method total. It is not nine
   encoded matrix failures and must never be quoted as such.
3. **The withdrawn bucket in the current runner** — `main()` in the canonical
   `tests/report-audit/promisor-grid.py`: `changed` is the set of cases whose `original`
   differs from their `amended` expectation; `original_view_unmet` lists **all**
   original-view failures of the current arm; `withdrawn_original_failures` is
   that list restricted to `changed`, and `amendment_changed_cases` names the
   restricted set. So the bucket means **unmet superseded original
   expectations** — all seven amendment-changed cases, PG28 and PG34 included,
   not only the literal unknown clause — and it **excludes** ordinary
   unchanged live or amended failures, which stay ordinary failures. The
   runner's own header states the original view is "Reported; withdrawn for the
   rows the L1 amendment changes; never counted as achieved". The behaviour
   that listed every current-arm original-view failure under the withdrawn name
   was the 2e-era bucket and is fixed in the current runner; this lesson does
   **not** describe the current runner as labelling live failures withdrawn.

**Status.** The original blanket unknown requirement stays
**withdrawn / not-achieved**, with its original cells and history retained;
the prospective amendment is graded separately. If the amended view is met on all 47 graded cases, the encoded original-view
failures number seven; that arithmetic is stated as a **conditional on the L1's actual
measurement**, which this text does not claim. No summary may present a live
failure as a withdrawal, and no live failure is renamed here.

**R23-H2** — the git ≥ 2.45 prerequisite is explicitly not approved or
repaired; it is carried as the round-24 L0 question, pending the operator
ruling. The floor itself was checked statically (CritGitFloor, HOLDS): the
new commands do not raise it above 2.45, and the forbidden newer flags
(`--missing=print-info`, `--missing-only`) appear nowhere in `tools/` or
`tests/` except in the prohibition text. No score promotion, no new frontier
capability, no self-admission, and no final count is claimed in this
continuation.

## Observer qualification — full expectations, not an exit-only green

The filed replay-v1/v2 match flags compared only exits even though their
expectations named kinds and errata-invalid counts. Their first five drafts
also omitted the valid work commit, allowing an unrelated landed-omitted
finding to keep exit1 when the finding under test was lost. Those raw
receipts remain evidence, not complete expectation credit. The selected
replay-v3 cites the valid work commit, compares every declared field,
keeps separate no-ledger expectations, binds the full2e parent/source hash,
and requires an explicit after-tool. The selected opaque-garbage-proof-v2
likewise compares its full declared expectation on the genuine non-leaf
fixture; its earlier exit-only observer remains filed and qualified.
Observer exit0 means measurement completed, not that the measured facts met
the expectation or that this round is admitted. No primary 47 byte changed.

The mutation observer also separates unchanged normal exits from0↔1: a
same normal exit may hide different detail and is not, by itself, a
substantive exit change. Same2→2 reason sensitivity is not acceptance of
unavailable evidence. The only agreed internal-error field is
internal_error; speculative alternative spellings are not an interface.


## Interface review corrections — no experiment on an ignored mutant

ConnInterfaces found that the sensitivity runner's frozen arm did not run
the supplied mutant at all. That green is invalid, not a survivor: only
current-arm sensitivity is accepted, with other arms refused before the
pristine call. It also exposed duplicate twin/individual failure counting;
violations now count unique graded case IDs for the selected arm, while
all grade problems stay recorded per view. Named candidate, grid, population,
expectation and observed mutant-auditor digests preserve what actually ran.

A hard-coded wave scratch path ignored caller TMPDIR outside that root.
The portable runner honors the caller's existing root and refuses an
unavailable requested root before any fixture/auditor, in both CLI modes.
The overwritten kind translation was removed without changing emitted
policy/control/open values. Exact IDs remain intentional, not compatibility
aliases; expect_rows remains an attribution envelope, not a claim every
allowed row must break. No primary 47 expectation or twin link is rewritten.

The last documentation reader retained private2e authority. A DocKnowledge
write nevertheless appended 80 lines directly to canonical documentation
outside OWNout scope. Those bytes are VOID incident evidence, not accepted
teaching; no continuous canonical freeze is claimed. They are archived and
excluded from author-owned knowledge at one post-barrier cutover. Any new
historical correction here comes from the L1's independently inspected
primary code/records, not the VOID prose.

## L1 primary re-derivation — historical counts and legacy proof scope

The outside-OWNout canonical 80-line append is VOID scope evidence, not accepted teaching or erratum credit. Its exact 42/38-line blocks and insertion patch remain incident evidence; no continuous canonical-freeze conformance is claimed. This new correction rests on the L1's independent committed-source/record inspection in `postfix/primary-rederivation/receipt.json`, with no replacement seat and no reuse of the VOID prose as authority.

- The committed legacy grid at 2e maps F17/F24 to `contract`. A result on them is not a fault-domain coverage count. F24's generic internal-ValueError pin concerns the error boundary, not the semantic cause of a domain refusal. No new ablation count is claimed.
- The same primary code has no `REASONS` pin for F28/F29, and its predicate skips reason matching when the pin is absent. These rows do not justify a global assertion that unrelated failures cannot be laundered into a met row. Their content-derived-reason coverage remains OPEN; this round does not retrofit the legacy oracle after observing a candidate.
- The primary tree at 245 already includes F26. Both retained round23 CritAxisScore JSON records independently contain 9 frozen traceback rows: F01,F02,F16,F18,F19,F20,F22,F24,F26. The published 8 is a discrepancy relative to those named observations, not explained by omitting F26 from that named tree. Any earlier private producer remains unestablished. Filed round23 text is retained, not rewritten.

Evidence method: read the code blobs with `git --no-replace-objects --no-lazy-fetch show`; inspect literal case/reason declarations without executing the module; count the existing JSON traceback flags. Exact argv, source revisions/digests, case kinds, predicate and counts are preserved in `.ufo/waves/round-24/postfix/primary-rederivation/receipt.json`. This is fresh authorized source/metrology analysis, not a rerun of a timed-out legacy suite or a claim that the original unknown requirement was achieved.

The open-only sensitivity path was another vacuous green: no graded
oracle cell means no comparison, so the observer now refuses that
experiment rather than report surviving mutants. The open row is not
promoted into the primary population, and ordinary finite survival with
a real graded sample remains a completed measurement.

An exit-only pristine was also insufficient: exit0 with an unmet graded
row contradicts the grid's own comparison. Pristine validation now requires
both success and no failed graded constraint before experiments; the mirror
mutant contradiction earns no kill. This is protocol validation of the
existing comparison, not a changed oracle or a new admission gate.


## Oracle custody qualification — value preservation is not a proved chronology

DocLesson's final private2e review does not support the earlier combined
“before L1 inspection” characterization. Candidate measurements existed
before the44-case freeze; CritUnknown is candidate-informed and cannot be
called an independent pre-candidate reviewer. The semantics amendment
preceded the freeze, which also does not itself prove an absence of L1
inspection. CritScores and CritNoTrade have their own pre-candidate records;
no stronger combined chronology is claimed. Exact reported times, files
and limits are in `postfix/oracle-chronology-qualification.json`.

What is retained is the observable value preservation:44 shared cells are
byte-identical, the shipped47 adds only the three disclosed supplement
cells, the frozen auditor source identity is pinned, and the supplement
probe uses the frozen auditor. This is not a retroactive pre-observation
registration claim, and the original unknown clause remains not achieved.
No snapshot metadata, original field or expected byte is rewritten.

For S103's independent opening, the valid receipt is
`build/advice/SrcPartial.md`; the rejected SrcRepoLayout Design Details
attribution is not authority for that opening. S105's quote has the
rendered/raw qualification above. PM02 remains a designated negative
control, not a credited measured kill from the old relaxed-grid,
failed-pristine baseline receipt; only a later actual pinned-pair
measurement may support its sensitivity claim.

## Final fixed-epoch record — judge the whole original claim

The actual fixed source epoch is
`92063cfc60e217fa7e2098c568578119b16a1b95`. This later documentation append
does not repair its algorithm, alter expected bytes, or retroactively
measure it. The one held C1 remains calibration7→7, with no author
admission. The entire original after claim is NOT ACHIEVED / unprovable in
full; a corrected policy is not permission to narrow that claim.

| Original after obligation | Final bounded judgment |
|---|---|
| Complete local promisor-marked lane/fleet clones retain the full-clone clean/failed findings, not2 | Supported only on recorded finite metadata/complete-control comparisons, not universally. |
| Genuine omitted pre-cutoff commits remain landed-omitted1 | Supported on recorded PG09/10/11/12 controls. |
| Unavailable required commit/tree/blob/report evidence returns CNE2, never a verdict | Supported on14 registered primary unavailable cells, without a broader generalization certificate. |
| Any missing citation in a promisor-backed repo is unknown2 unless another audited repo resolves it | NOT ACHIEVED, expressly withdrawn. PG22/23/24/30/41 contradict the literal clause; no original field is rewritten. |
| No lazy fetching, transport, signature/replace/config side effects or hangs, preserving global isolation/deadlines | FULL CLAUSE UNPROVABLE. Finite flags/options/deadlines are not global no-effects or absence-of-chain proof; manual PM08 earns no behavioral credit, and legacy/parser/redirect/size/deadline residuals remain open. |
| Metadata alone is not incompleteness; audit-required local evidence determines outcome | Supported on finite sufficient/unused/unselected-hole and genuine non-leaf controls. No all-reachable-tree precondition was added. |
| Preserve r23 evidence and append the69-not68 and40-of56 identity corrections | Filed history retained and corrections appended. Forty is the retained process-row count, not proof all40 are FIFO-tied; only19 are explicitly tied, and16 identities remain missing. R24's own conformance incidents are separate, not erased. |

### What was counted, and what was not executed

`final/distributed-primary-count-v2.json` inventories existing raw W3
captures for47 assigned primary cells bound to the fixed auditor, grid and
manifest identities. All amended cells match; seven original expectations
do not (PG22/23/24/28/30/34/41). PG28/34 are separate prospective corrections,
not additional literal-unknown-clause cases. The primary47, open PG40,
supplements and legacy cells are never mixed into a larger success count.
Earlier loose16/47 and strict14/47 used different prior producers; their
two-cell difference is not two additional algorithm wins. The distributed
record inventory is not a fresh whole both-arm grid, an identical-producer
before/after comparison, the full registered measurement plan or admission.

`final/recorded-consumers.json` counts six existing replay-v3 consumers:
all six are red before at2e and match every declared exit/kinds/invalid
field after at92063, with no-ledger controls separate. They exercise the
generic fixes without reclassifying them as extra primary cases.
`final/bounded-mutation-record.json` records named graded failures for nine
of ten sampled executable operators, not a full10×47 sweep. PM07's
canonical finite sample survives; a changed missing-object set disproves
“universally no-op,” while the separate opacity-allrefs recipe is not a
canonical PM07 primary kill. PM08 is merely a FILED, manual, unexecuted,
uncredited note, not “settled” behavioral evidence. No permanent source/
AST/text/wiring assertion remains; historical static notes and legacy M02
cannot be promoted into a present PM08 kill.

Manual-only inventory completion with explicit executable/evaluated0 and
killfalse is not a behavioral pass or valid survivor. An unexecuted static
prediction of vacuous success is not an observed algorithm failure.
Unknown-ID inefficient ordering is not a false-green outcome. The grid's
frozen/both arms remain legitimate; current-only is the mutation runner's
restriction, not a grid restriction.

### Preserve the input state and the evidence's actual strength

- Raw PM04 pristine twin/document fields are null, despite its report's
  “true” table. Its graded2→1 failure remains evidence, but two null
  documents are not equality proof. Case18/19's2→2 outcomes are preserved
  refusals, not normal0/1→2 over-refusal. PM09's1→1 changed defect set is
  same-verdict-exit; PM11's2→2 reason loss is diagnostic-only.
- Case42's later clean observation came after a stray forensic Git read
  hydrated the missing blob. This is a changed-input verdict, not an
  unchanged-fixture false clean or repair. Prehydration graded2 remains
  the recorded observation. Connected-origin controls stay connected;
  missing-object forensics must use fresh isolated states/no-lazy-fetch.
- Five new outside47 plain-metadata companions do not expand the primary
  population: PG21/43/46/47 compare2/2 without verdict documents; PG48's
  normal0/0 documents compare. The26 manifest pointers are25 unordered
  links covering42 cases, not47 independent comparable document pairs.
- Case31 exceeded its primary-plus-one-supplement bound; Case11 also ran
  a frozen program outside the current-arm request. Other recorded extra
  probes/repeats and unisolated forensic reads remain deviations, not a
  certificate that every completed seat complied.
- The canonical VOID80 append, private evidence-edit/restoration limits,
  source/quote facets, legacy reason-pin gaps and oracle chronology limits
  remain as filed above. No retroactive freeze or pre-observation authority
  is manufactured. FinalCase15's scratch-only raw files were copied and
  compared into durable custody; no target was replayed to fill them.

All192 author seats completed, but terminal counts/grants are not a
continuous concurrency-floor or global no-effects certificate. No fresh
final-epoch full grid/legacy/selftest/parity/default sensitivity replay
was performed; an attempted old full isolation run timed out and produced
no usable JSON, rather than never being attempted. Current source census
is105 rows (A100/B2/C3; mined86/queued8/rejected11), with four new A rows,
eleven old used-by-only edits and no immutable old-cell change. H2 remains
unapproved, no serving readiness is claimed, and only fresh outside Main
closure may admit or reject the full original claim.
