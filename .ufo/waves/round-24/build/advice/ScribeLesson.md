# ScribeLesson — round-24 Gate/Mistakes lesson draft (scoped findings)

Seat: `KamaR23-2.ScribeLesson-2` (leaf member; no subagent dispatch).
Date: 2026-10-21. Round base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(git 2.56.0, Python 3.14.8).
Assignment: draft the round-24 lesson Gate/Mistakes structure from the
rejected-harmed r23, keeping the honesty of the fixed known harms and of the
source scope; draft only in the out directory; no production edits.

## Behavior

Read the round-24 preregistration, the committed round-23 lesson
(`corpus/lessons/round-23.md`), the base auditor, the round-23 grid and the
round-23 wave advice that recorded the harm. Drafted a round-24 lesson
skeleton with the four sections the corpus format uses — Declared claim, Gate,
Mistakes, Integration and boundaries — with:

- a **Gate** that carries the r23 rows forward unchanged (S089, S090, S093,
  S094, S096–S101), names the superseded rows that stay superseded (S091, S092,
  S095), and adds four **candidate** new rows opened by this scribe on the
  official git manuals (S102 git-rev-list `--missing=print`, S103 git-cat-file
  `--batch-check`, S104 git-config promisor/partial-clone keys, S105
  partial-clone promisor-remote key list), each with the located quote, the
  page digest and the "last updated in 2.56.0" version;
- a **Mistakes** section that carries r23 M1–M7 forward as *fixed* with their
  existing pointers, adds M8 (metadata-only refusal shipped as isolation),
  M9 (refusal-scope inversion after the repair) and M10 (the repair must not
  re-open the transport channel), and records the two preregistration
  corrections (C-1 69 reports not 68; C-2 40 of 56 killed FIFO-process
  identities retained) as append-only items for the L1;
- an **Integration and boundaries** section stating the claim, the trades
  (git ≥ 2.45), what stays open from r23, and what this scribe did not verify.

No corpus, tool, grid, config or Git-index file was written. No commit, no
push. No build, test, formatter, grid or selftest run was executed.

## Gates

- Gate rows opened by this scribe (plain HTTPS docs, 2026-10-21):
  `https://git-scm.com/docs/git-rev-list` (page sha256 `6eca09d9ef21dd42…`),
  `https://git-scm.com/docs/git-cat-file` (`539830429faea901…`),
  `https://git-scm.com/docs/git-config` (`5a63888b1c15a172…`),
  `https://git-scm.com/docs/partial-clone` (`8a6493225f76dba8…`).
  Each page reports "last updated in 2.56.0"; the host git is 2.56.0.
- No pass/fail gate was run, and no exit or finding expectation is claimed
  from this seat.

## Touched surfaces

Written (lane, untracked, inside the wave's own build tree):

- `.ufo/waves/round-24/build/out/ScribeLesson/round-24-lesson-draft.md` — the
  draft lesson (Gate/Mistakes structure).
- `.ufo/waves/round-24/build/advice/ScribeLesson.md` — this report.

Scratch only (own clone, no production file, no commit):

- `/fast/scratch/hyaku/kama-r24/ScribeLesson` — `git clone --no-hardlinks` of
  the lane at base `0df800e`.
- `/fast/scratch/hyaku/kama-r24/ScribeLesson/.docs-cache/` — the four fetched
  manual pages.
- `/fast/scratch/hyaku/kama-r24/ScribeLesson/.scratch/` — two throwaway local
  repositories used for the two offline observations below.

Read only: `.ufo/waves/round-24/preregistration.json`,
`.ufo/waves/round-24/build/{spec,assignments,dispatch}.json`,
`corpus/lessons/round-23.md`, `corpus/SOURCES.md` (rows S089–S101),
`corpus/QUALITY.md` (KQ30–KQ34), `tools/report-landing-audit.py` (lines
39–133, 430–503, 468–482), `tests/report-audit/repo-state-grid.py` (lines
195–300, 482–700), and the round-23 advice files cited below.

## Findings (exact evidence)

1. **The harm is in the base auditor, at three named lines.**
   `tools/report-landing-audit.py:438` `check_history_repo` raises
   `partial clone (promisor pack)` at `:457` for any `*.promisor` file that has
   a sibling `.pack`, and `partial clone (<key>)` at `:465` for
   `extensions.partialclone` or any `remote.*.promisor` key. Both are
   *metadata* conditions: no object is inspected.
2. **The r23 wave already measured the flip, in both directions.**
   `.ufo/waves/round-23/build/advice/RevCalibrationAxis.md:57` — "TRADE:
   partial clone, every cited object local | exit 0, clean, req 1 | exit 2,
   'partial clone (extensions.partialclone)' | clean input flips to refusal
   (H2)"; `:72` names `L445–448` as the refusing lines of that revision.
   `RevSkillText.md:51` — committed `e0f0434` gives exit 2
   `could-not-evaluate: … partial clone (promisor pack)` where frozen
   `4fe9339` gives exit 0 clean; `:323` — T01 candidate exit 2, frozen exit 0.
   `RevLookup.md:75` — "a benign `file://` partial clone was `found` in base
   and is now refused".
3. **The r23 grid could not detect the harm, because the harm was the
   expectation.** `corpus/lessons/round-23.md:207-208` records T01 and F23 as
   *declared trades*; `tests/report-audit/repo-state-grid.py:670,689` register
   F23 (contract) and T01 (tradeoff) with exit 2 as the expected outcome. The
   lesson drafted here therefore treats the r23 grid numbers
   (`corpus/lessons/round-23.md:112-121`: current `faults 26/26, tracebacks 0,
   executed 0, timeouts 0`; mutants `31, 30 killed`; selftest `50/50`) as
   evidence about the *r23 isolation mechanisms only* — not as evidence that
   refusing a complete promisor-marked repository was correct.
4. **The manual supports the round-24 discrimination directly.** git-config(1)
   `extensions.partialClone`: "Such a remote is called a "promisor remote" and
   it promises that all such omitted objects can be fetched from it in the
   future." (24 words) and `remote.<name>.promisor`: "When set to true, this
   remote will be used to fetch promisor objects." partial-clone(1) lists the
   promisor-remoteness keys as configuration variables. git-rev-list(1)
   `--missing=print`: "will also print a list of the missing objects. Object
   IDs are prefixed with a "?" character." git-cat-file(1) `--batch-check`:
   a name that "cannot be resolved to an object in the repository" is reported
   as `<object> SP missing LF`. These are the four candidate rows S102–S105.
5. **The availability mechanism works offline, without a fetch.**
   In a throwaway promisor-marked repository whose blob loose object was
   deleted, `git --no-lazy-fetch rev-list --objects --missing=print HEAD`
   printed `?ce013625030ba8dba906f756967f9e9ca394464a` and returned
   immediately; `git --no-lazy-fetch cat-file --batch-check` printed
   `ce013625030ba8dba906f756967f9e9ca394464a missing`; `git --no-lazy-fetch
   cat-file -e <oid>` exited 1. No remote was contacted (`example.invalid` was
   an inert URL). These are scribe-side observations of the documented
   mechanism, not a lane measurement.
6. **A citation trap avoided.** git-config(1) renders `extensions.partialClone`
   with its section and variable in separate markup, so a literal search for
   the joined key misses it; the draft anchors S104 on the rendered entry.
   Separately, `git config --list` prints the key lower-cased
   (`extensions.partialclone=origin` for a repository configured with
   `extensions.partialClone=origin`), so the auditor's lower-case comparison
   at `:462` does match git's own output — recorded as a local observation, not
   as a Gate row.
7. **The two preregistration corrections anchor to exact filed text.**
   `corpus/lessons/round-23.md:178` — "73 seats dispatched (68 reports; dead:
   RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty…)";
   73 seats − 4 dead = 69. `corpus/lessons/round-23.md:174` (M7) — "56 blocked
   `git` processes … (12:18–13:29 -03)"; the preregistration states 40 of the
   56 killed identities were retained, so "56" is a process count, not full
   identity evidence. A repository-wide search of the round-23 wave tree and
   the lesson found no other record of the 40, so both corrections are
   recorded as **declared, not re-derived**.

## Out of scope (not done)

- No edit to `corpus/lessons/round-23.md`, `corpus/lessons/round-24.md`,
  `corpus/SOURCES.md`, `corpus/QUALITY.md`, the auditor, the grids, the
  knowledge files or any operator/sibling/fleet file.
- No grid, mutant, selftest, historical-ledger or no-harm run; no exit or
  finding oracle of my own.
- No design of the repair itself (the availability algorithm, the per-object
  policy and the reason strings are the L1's and the executor seats').
- No KQ rule added or edited; KQ30–KQ34 were read only, to name the rule a
  mistake is captured by.
- No dispatch: leaf member, no subagents.

## Not verified

- The round-24 exit/finding expectations themselves (the preregistration's
  oracle, owned by the L1).
- The 69-report count and the 40-of-56 identity retention, beyond the filed
  text they attach to.
- Whether the repaired auditor keeps the r23 numbers `faults 26/26, tracebacks
  0, executed 0, timeouts 0`, `mutants 30/31`, `selftest 50/50`, and the
  historical ledger parity.
- The frozen-arm behaviour of the new grid rows, and the r23 F23/T01 rows
  under repaired code.
- Whether the candidate Gate rows are adopted; the ids S102–S105 are
  provisional and the L1 appends the rows under KQ22/KQ31.

## Tools installed or updated

None. `git` 2.56.0 and `curl` were already present; `curl` was used for four
plain HTTPS reads of git-scm.com manual pages into the scratch clone's
`.docs-cache/`. No pacman transaction, no `uv`/`cargo`/`npm` install, no
service or host configuration change.

## Artifacts

- Draft lesson: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ScribeLesson/round-24-lesson-draft.md`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/ScribeLesson.md`
- Scratch clone and fetched pages: `/fast/scratch/hyaku/kama-r24/ScribeLesson/`
  (`.docs-cache/`, `.scratch/`)

---

# ScribeLesson — round-24 falsify-wave lesson continuation (second task, same seat)

Same seat, resumed (`KamaR23-2`, no new seat). Task: draft a **short
append-only** round-24 lesson continuation from the round-24 wave-2 proposals;
no production edits; no tests or full suite; the L1 adds the final
measurements.

## Behavior

Read the cutover contract `.ufo/waves/round-24/fixes/docs-contract.txt`, the
source proposals (not assumptions) and the two falsify-wave critiques named by
the contract, then drafted paste-ready continuation text covering: the wave-2
generic bugs and their repairs, the three masked/stale-premise distinctions,
the strict-14/loose-16 method correction, the PM08 removal and the PM07 V4
retarget decline, and the withdrawn-original-unknown / open-H2 disclosure
status. The draft introduces no source row, no final number, no candidate
numerator and no landed hash, and it does not repeat the ConnSources
used-by / facet / raw-quote append blocks.

## Touched surfaces

- Written: `.ufo/waves/round-24/fixes/docs/ScribeLesson/append.txt` (the
  continuation draft text).
- Appended: this advice file.
- Read only: `.ufo/waves/round-24/fixes/docs-contract.txt`,
  `fixes/StoreLocalPresence/README.md`, `fixes/GridAttestation/README.md`,
  `fixes/GridAttestationV2/README.md`, `fixes/GridAttestationV3/README.md`,
  `fixes/MutationEvidenceV4/rationale-v4.md`,
  `fixes/MutationEvidenceV5/rationale-v5.md`,
  `fixes/MutationEvidenceV6/rationale-v6.md`,
  `fixes/MutationEvidenceV6/inventory-v6.json`,
  `.ufo/waves/round-24/proposal-evidence-dispositions.json`,
  `falsify/advice/CritOriginalWithdrawn.md`, `falsify/advice/CritGitFloor.md`,
  `corpus/lessons/round-24.md`.
- Production untouched: `git status --short` in the lane shows only untracked
  wave files; no tracked file was modified, no commit, no push.

## Findings (source-linked)

1. **Seven generic wave-2 defects and their repairs**, each from a proposal
   README: cross-store presence (`StoreLocalPresence/README.md` §"The
   defect", `CodeLookupMerge`); unknown outranking a known wrongtype for the
   same canonical object (§"Second defect"); the unselected-round errata row
   deciding the verdict (§"Third proposal" §1, `CodeErrataBoundary F1`); the
   bare-git-error required reads (§"Third proposal" §2, `CodeRequiredReads`;
   §"Fifth proposal", `CaseFleetTree M1`); the store-wide opaque fallback
   (§"Seventh artifact", `CodePerRunCache F2`); the grid scoring an internal
   error as a legitimate refusal (`GridAttestationV3/README.md` §"The gap",
   `DocQualityF1`); and the mutator crediting a crash as a kill
   (`MutationEvidenceV6/rationale-v6.md` §1–§2).
2. **The three masked/stale premises** are exactly the three dispositions in
   `proposal-evidence-dispositions.json`: the v5 blob hole (already green
   before; renamed blob positive control, real regression from v6), the
   replay-v1 errata consumer (same fleet blob in body and ledger, so the red
   was the body-root bug; isolated by v7 + replay-v2 with lane blob A and
   fleet-only blob B plus a no-errata control), and the v7 same-tag test
   (target in both stores; v8 adds the target-only-in-fleet regression, its
   mirror and the both-missing control). The draft states the rule: keep every
   older file and receipt; a stale premise is not a red regression.
3. **The method correction.** `GridAttestation/README.md` §"Correction to the
   amended comparison": the frozen arm had been scored `form_check=False`
   without the names pin; under identical strong rules the strict comparable
   baseline is 14/47, the earlier 16/47 is the weaker exit/reason-only score
   kept under its own label, and PG16/PG20 are the two differing cells (the
   r23 base names the required path, not the tree object id). The draft states
   this is a method correction, not two extra product wins, and that the frozen
   47/47 historical reproduction is separate.
4. **PM08 and PM07.** `proposal-evidence-dispositions.json` disposition 4:
   the static/AST PM08 proposal is "Declined, not repinned"; the live shape is
   ten executable operators plus one manual review-only note (`inventory-v6.json`
   PM08 entry: `"execution": "review-only"`, no alternatives, no kill credit).
   `MutationEvidenceV4/rationale-v4.md` §1 describes the V4 PM07 retarget and
   `MutationEvidenceV5/rationale-v5.md` §1 restores the V3 recipe; the docs
   contract states the V4 opaque-all-present retarget "is NOT the canonical
   operator". The draft records the canonical operator, the decline, "no kill
   presumed", static anchors authenticating applicability only, and that
   `expect_rows` is an attribution envelope.
5. **Withdrawn original unknown and open H2.** `CritOriginalWithdrawn.md`
   (PARTIAL): the headline holds — no committed summary relabels the original
   unknown-citation expectation as passed — but disclosure completeness is
   falsified: nine original-reading red cells exist at the pinned base, the
   summaries name one rule without count or identities, and the runner's
   `withdrawn_original_failures` bucket labels live failures as "withdrawn",
   so GridOracle's filed count of withdrawn original-view failures inherits
   that provenance. `CritGitFloor.md` (HOLDS): R23-H2 is still open at L0 and
   not operator-approved; the new commands do not raise the floor above 2.45,
   and `--missing=print-info` / `--missing-only` appear only in the
   prohibition text.
6. **Non-duplication.** The used-by transitions, the facet qualifications and
   the raw-quote append blocks belong to the ConnSources packet
   (`falsify/out/ConnSources/integration-patch-3cell-ledger-plus-3-appendix-blocks.diff`);
   the draft references them only as "not repeated here" and adds no S-row.

## Out of scope / not done

- No edit to `corpus/lessons/round-24.md`, `corpus/SOURCES.md`,
  `corpus/QUALITY.md`, the auditor, the grid, the mutants or any other
  production file; the append text is a draft under this seat's own
  `fixes/docs/` path.
- No grid, mutant, selftest, ledger or no-harm run; no suite of any kind.
- No final measurement, candidate numerator, exit count, landed hash, score
  promotion or self-admission.
- No new source row, no re-opening of S095/S097/S098, no change to any
  immutable row cell.

## Not verified

- The final candidate numbers, the amended-view score of the committed
  producer, and any kill count — the L1 measures these.
- The exact identity of the "opaque-all-present" V4 retarget inside the
  operator inventory beyond the V4 rationale's description.
- Whether the ConnSources packet's blocks land before or after this
  continuation in the lesson file; the continuation is written to be appended
  after them and to remain valid if their order changes.

## Tools installed or updated

None. No installs, no pacman transaction, no network access, no commits or
pushes.

---

# ScribeLesson — qualification of the "nine original-reading red cells" wording (third task, same seat)

Same seat, resumed. Task: qualify the count precisely from the seat's own
receipt, without re-running tests; distinguish the original **prose clause**
from the encoded **original cell view**; keep the old text filed. Result: a new
versioned addendum; the v1 continuation text is unchanged.

## Behavior

Inspected the four falsify-wave receipts of the critique I had cited
(`falsify/out/CritOriginalWithdrawn/m1-…json`, `m2-…json`,
`m3-frozen-as-current-amended7.json`, `m4-open-PG40.json`) and the critique's
own enumeration table (`falsify/advice/CritOriginalWithdrawn.md:252-262`,
`:180-240`), and wrote a versioned addendum. No test, grid, mutant or suite was
run; no production file was edited; the v1 continuation text stays filed
unchanged.

## Touched surfaces

- Written: `.ufo/waves/round-24/fixes/docs/ScribeLesson/append-v2.txt` (the
  qualification addendum).
- Appended: this advice file.
- Read only: `falsify/out/CritOriginalWithdrawn/*.json` (four receipts),
  `falsify/advice/CritOriginalWithdrawn.md`, `build/advice/ConnClosure.md:179`
  (referenced by the critique), `fixes/docs/ScribeLesson/append.txt`.

## Findings (exact, from the receipts)

1. **The encoded original cell view differs from the amended view on exactly
   seven cells: PG22, PG23, PG24, PG28, PG30, PG34, PG41.** Two receipts
   confirm the set: `m3-frozen-as-current-amended7.json` runs the frozen
   producer (`0df800e`, auditor sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`)
   over exactly those seven cells; `m1-current-amended-subset.json` runs the
   integrated producer at `2e254a1` (auditor sha256
   `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`) over a
   ten-case subset and reports `met_original: false` on exactly those seven,
   with PG13, PG25, PG37 `met_original: true`. Manifest
   `d86b7bea…14cd1`, population 47 (`612b0a74…2ed88`), `frozen_revision
   0df800e…`, `timeout_seconds: 30` in both receipts.
2. **The L1's constraint is therefore confirmed by the receipts:** under
   identical grading, a fully met amended view implies **seven** encoded
   original-view failures, not nine. "Nine" is a mixed-method total — seven
   encoded graded cells **+ one open row (PG40)** that is not a graded cell of
   the 47-cell manifest (`m4-open-PG40.json`: `exit 1`, `met_original false`,
   `met_amended true`, the row listed under `open_rows`) **+ one row of the
   retained r23 legacy grid (F06, `repo-state-grid.py` `f_lazy_fetch`)**, a
   table the `d86b7bea…` manifest does not contain, whose exit-1 observation
   the critique **inferred** from `build/advice/ConnClosure.md:179` and did not
   execute. My v1 sentence "nine original-reading red cells" is therefore
   ambiguous and is qualified in addendum-v2 rather than left standing as a
   matrix count.
3. **Withdrawal classification, per item.** Withdrawn under the original
   clause: PG22, PG23, PG24, PG30, PG41, PG40, F06. **Not** withdrawn: PG28
   (its amended expectation comes from the amendment's prospective expectation
   for the unhydrated blobless lane) and PG34 (a non-promisor no-harm twin
   whose amended expectation differs from its original one — an expectation
   change). Ordinary live failures remain live failures and are never named
   withdrawn; the runner's `withdrawn_original_failures` bucket labels live
   failures as withdrawn, so the count GridOracle filed under that name
   inherits that provenance and is read as *original-view failures*. That
   count was not re-enumerated here and no share of it is claimed.
4. **PG34's direction depends on the producer, and the receipts show both
   sides:** under the frozen producer (m3) it exits 1, meeting the original
   expectation (1) and failing the amended one (2); under the integrated
   producer (m1) it exits 2, meeting the amended expectation and failing the
   original one.

## Out of scope / not done

- No re-run of any grid, mutant, selftest, ledger or suite; the receipts were
  read, not regenerated.
- No edit to `corpus/lessons/round-24.md`, `corpus/SOURCES.md`, the auditor,
  the grid, the mutants or the critique's own advice file; the v1 continuation
  text (`fixes/docs/ScribeLesson/append.txt`) is unchanged and stays filed.
- No final measurement, candidate numerator, exit count, landed hash, score
  promotion or self-admission; no new source row.

## Not verified

- The candidate's amended-view score on all 47 graded cells — the L1 measures
  it; the addendum only states the arithmetic consequence for the encoded
  original view.
- How many of GridOracle's filed withdrawn-bucket entries are live rather than
  withdrawn (not re-enumerated; the critique's own estimate is inference).
- The live expectation of F06 (the critique did not execute it).

## Tools installed or updated

None.

---

# ScribeLesson — unified append-v3 continuation (fourth task, same seat)

Same seat, resumed. Task: produce **one** unified paste-ready continuation
(v1 + v2 qualified, older drafts filed, not two contradictory current claims),
with the corrected terminology on the original view and the withdrawn bucket.
Result: `fixes/docs/ScribeLesson/append-v3.txt`; the two earlier drafts are
marked as superseded drafts with their text preserved.

## Behavior

Read the current grid proposal (`fixes/GridAttestationV4/`) and its bucket
code, then wrote a single unified continuation text that carries the generic
fixes, the three stale premises, the strict-14/loose-16 method correction,
PM08/PM07 and R23-H2 unchanged, and replaces the v1/v2 wording on the original
view with the qualified, three-way distinction. No test, grid, mutant or suite
was run; no production file was edited; no policy introduced; no final
candidate count claimed.

## Touched surfaces

- Written: `.ufo/waves/round-24/fixes/docs/ScribeLesson/append-v3.txt` (the
  unified paste-ready continuation).
- Edited (headers only, text preserved below them):
  `.ufo/waves/round-24/fixes/docs/ScribeLesson/append.txt` and
  `append-v2.txt` — each now opens with "SUPERSEDED DRAFT — superseded by
  append-v3.txt … do not paste this file".
- Appended: this advice file.
- Read only: `fixes/GridAttestationV4/README.md`,
  `fixes/GridAttestationV4/promisor-grid.py` (header `:1-45`, bucket code
  `:1370-1400`), `build/advice/GridOracle.md:482-498`, and the earlier
  receipts already cited.

## Findings (source-linked)

1. **The current runner's bucket semantics, read from the proposal code**
   (`fixes/GridAttestationV4/promisor-grid.py:1381-1391`): `changed` = cases
   whose `original` differs from their `amended` expectation (JSON compare);
   `original_unmet` = every current-arm row with `met_original is False`;
   `withdrawn = [c for c in original_unmet if c in changed]`. So
   `withdrawn_original_failures` means **unmet superseded original
   expectations** — all seven amendment-changed cases (PG28 and PG34
   included), *not* only the literal unknown clause — and it **excludes**
   ordinary unchanged live/amended failures, which remain ordinary failures.
   `original_view_unmet` is the all-failures list; `amendment_changed_cases`
   names the restricted set. The runner header states the original view is
   "Reported; withdrawn for the rows the L1 amendment changes; never counted as
   achieved".
2. **The 2e-era bucket bug is historical and fixed**, so my v1/v2 sentence
   "the runner's `withdrawn_original_failures` bucket labels live failures as
   withdrawn" is corrected in v3: that described the old bucket (critique F2,
   GridOracle correction (b)); the current runner does not do it. v3 says so
   explicitly and does not describe the current runner as labelling live
   failures withdrawn.
3. **Seven encoded changes, exact:** PG22, PG23, PG24, PG28, PG30, PG34,
   PG41 — confirmed by `m3-frozen-as-current-amended7.json` (frozen producer
   `da5041a81…65af1` run over exactly those seven) and
   `m1-current-amended-subset.json` (integrated producer `ea51bc35…dd220`,
   `met_original: false` on exactly those seven; PG13/PG25/PG37 `true`).
4. **The historical "nine" is a mixed total, stated as such:** 7 encoded graded
   cases + **PG40** (open row, `m4-open-PG40.json`: exit 1, `met_original
   false`, `met_amended true`) + **F06** (retained r23 legacy grid row
   `repo-state-grid.py` `f_lazy_fetch`; its exit-1 observation **inferred**
   from `build/advice/ConnClosure.md:179`, never executed). It is not nine
   encoded matrix failures and v3 says it must never be quoted as such.
5. **Literal clause separated:** the registered reading of
   `preregistration.json` `expected_after[3]` is the five graded cases PG22,
   PG23, PG24, PG30, PG41; PG28 and PG34 are amendment-changed but not
   literal-clause cases (PG28 from the amendment's prospective expectation for
   the unhydrated blobless lane; PG34 a non-promisor no-harm twin whose
   expectation changed). PG40 and F06 stay outside the graded matrix as
   separate counterexamples.
6. **The arithmetic is conditional:** v3 states that *if* the amended view is
   met on all 47 graded cases, the encoded original-view failures number
   seven — explicitly as a conditional on the L1's actual measurement, which
   the draft does not claim.
7. **Kept unchanged from v1:** the seven generic fixes, the three masked/stale
   premises, the strict-14/loose-16 method correction (not two extra product
   wins; frozen 47/47 separate), PM08 as a manual review-only note with no
   assertion, PM07's V4 opaque-all-present retarget declined with the V3
   recipe canonical, and R23-H2 open and unapproved.

## Out of scope / not done

- No edit to `corpus/lessons/round-24.md`, `corpus/SOURCES.md`, the auditor,
  the grid, the mutants or any other production file; no new policy; no
  source row; no ConnSources used-by/facet/raw-quote duplication.
- No test, grid, mutant, selftest, ledger or suite run; the grid proposal was
  read, not executed.
- No final candidate count, numerator, exit count, landed hash, score
  promotion or self-admission.

## Not verified

- The current runner's actual bucket contents on the final committed producer
  (the L1 measures); v3 states the semantics from the proposal code and the
  conditional arithmetic only.
- How many entries of GridOracle's earlier filed count under the old bucket
  name are live rather than superseded (not re-enumerated; v3 does not quote
  that count).
- F06's live exit (inferred by the critique, not executed).

## Tools installed or updated

None.

---

# ScribeLesson — correction of the supersession marking (fifth task, same seat)

Same seat, resumed. L1 ruling: append-only means **byte preservation**, not
"original text below a new header". This seat had inserted a `SUPERSEDED
DRAFT` header into `append.txt` and `append-v2.txt`; the correction below
removes only those inserted bytes, preserves the header-prefixed versions
under new names, and records the supersession in a separate index that edits
no old file.

## Behavior

1. Copied the current (header-prefixed) files byte-for-byte to
   `append-v1-labelled.txt` (sha256 `5421ad5c9cefd4f74380af52f0a86075372ea26cbd8a20e88346143b767cf272`,
   10912 bytes) and `append-v2-labelled.txt` (sha256
   `f514989789deaa2a645879d7b04582cff37ebefb97c87d1f1fd2e4eff674b9b3`, 6144
   bytes); each copy was confirmed identical to its source by sha256 before
   any edit.
2. Removed **only** the inserted 185-byte header block from `append.txt` and
   `append-v2.txt` (no other byte touched).
3. Verified the restoration (read-only checks, no test or suite run):
   - `append.txt` restored = 10727 bytes, sha256
     `8f5cbd769c73b0e4400e53da58788e68ce53cecf1f28932b76c9351449e1f9c8`;
     `append-v2.txt` restored = 5959 bytes, sha256
     `0201858d5f1b095c30d6d05f822fbc5388238a3df9875686b1e89093ce50094a`;
   - in both files the restored bytes equal the labelled copy minus exactly
     the 185 inserted header bytes (byte comparison: true);
   - the restored byte lengths equal the lengths the write tool recorded at
     creation (10727 and 5959);
   - the two re-emitted original lines are byte-exact against the original
     payload text;
   - no `SUPERSEDED` marker remains in either restored file.
   **Not verified:** no sha256 was recorded at creation time, so the
   restoration is verified by the recorded creation byte length, byte-exact
   re-emission of the two lines the edit had matched, and exact removal of the
   inserted header bytes — not by a pre-edit digest. Until the restoration
   above, this seat did **not** claim that v1/v2 were byte-unchanged; that
   claim is made now, with the method stated.
4. Wrote `fixes/docs/ScribeLesson/supersession-index.json`: it names
   `append-v3.txt` as the current text and lists the two restored drafts with
   their digests, byte lengths and labelled copies, plus the correction record
   and its limits. No old file was edited by the index.

## Touched surfaces

- Written: `.ufo/waves/round-24/fixes/docs/ScribeLesson/append-v1-labelled.txt`,
  `append-v2-labelled.txt`, `supersession-index.json`.
- Edited (removal of this seat's inserted header only): `append.txt`,
  `append-v2.txt` — restored to their original bytes.
- Unchanged: `append-v3.txt` (sha256 `8c25552e65ffe150893a3e49346a270609c879942081f040bda6974d1cb729a9`).
- Appended: this advice file. No production file, no corpus file, no source
  row, no other seat's file; no tests, no suite, no commits.

## Out of scope / not done

- No edit to `corpus/lessons/round-24.md` or any production file.
- No re-run of any grid, mutant, selftest, ledger or suite; the verification
  above is byte and digest arithmetic on this seat's own draft files.
- No final candidate count, numerator, exit count, landed hash, score
  promotion or self-admission.

## Not verified

- A pre-edit sha256 for `append.txt` and `append-v2.txt` (none was recorded
  at creation); the restoration is evidenced as described above, not by a
  before/after digest pair.

## Tools installed or updated

None.
