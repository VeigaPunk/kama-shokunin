# ScribeFrontier — round-24 README frontier correction (draft, reading B)

Role: leaf scribe. No subagent dispatch. No production, corpus, fleet, config
or `.jj` write. No installs. No build/test/formatter run. Draft only.

## Behavior

Drafted the append-only round-24 frontier correction for the lane README
(`corpus/README.md`, the file that carries `## Frontier disposition — round
23`), in three wordings plus a landing checklist, a policy matrix and the
evidence it rests on. The correction (a) withdraws the round-23 reading that
a partial clone / paired promisor pack is refused as such — so a *complete*
local promisor-marked repository can only return could-not-evaluate;
(b) keeps **D4 partial**; (c) keeps the "no new serving capability"
non-claim and the unchanged other-frontier list.

The wording follows the **B** reading decided by L1: availability is
**per required read**, not a whole-root precondition; promisor metadata
never changes local-object resolution or a clean/failed verdict; a locally
unresolved citation keeps the ordinary failed verdict (exit 1, the same
finding kinds as the identical unmarked twin, authorized errata still
applying) unless it names referenced but unavailable local content, which
is exit 2 with a content-derived reason. One preregistered expectation
(`expected_after[3]`, unknown-citation⇒exit2) is **withdrawn prospectively**
by `.ufo/waves/round-24/oracle-amendment-1.json` and is stated in the draft
as **not met, not passed**. Nothing was edited in the repository; the only
artifacts are the draft, a patched copy of the README, a unified diff and a
policy matrix under my out directory.

## Gates

- No gate was run (leaf scribe, no measurement assignment; the wave's single
  post-integration measurement is L1's).
- `git apply --check` on the candidate patch: `Checking patch corpus/README.md…`
  → **APPLY-CHECK OK** (check only, no write applied).
- Byte-equality check: the appended tail of the patched copy is identical to
  "variant A" in the draft file (`variantA == appended tail: True`).

## Touched surfaces

- Written: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-frontier-correction.md`
  (sha256 `a5049d91e3bd595c00203c348c36b06fbe50749b50339b86e5d487160bc2496a`)
- Written: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README.with-round24-frontier.md`
  (patched *copy* of `corpus/README.md`; the production file is untouched;
  sha256 `e07099535ba739f923648bda2fa95474fb3885955a2320926000f8ace799c8cc`)
- Written: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-frontier.patch`
  (unified diff, sha256 `2b1ae5b3f97c94fc0e7ff6fd57fcc3ced3b2724c1081f62db995b8fb6210e4cf`)
- Written: `.ufo/waves/round-24/build/out/ScribeFrontier/promisor-policy-matrix.md`
  (preregistration/amendment item ↔ README sentence ↔ code anchor, plus the
  retained-grid rows the B reading touches; sha256
  `f0665febf6bc4a5ee5c25471d7db1e16c6f3e72d5e116f92a495668dd8de7c46`)
- Written: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-append-text.md`
  (copy-paste-ready section body, byte-equal to the patch tail; sha256
  `a089aa074966e580c368ecb44cf9bb44f97b7b4405ac90658867be0b1ddb8465`)
- Written: `.ufo/waves/round-24/build/advice/ScribeFrontier.md` (this file)
- Read only: `corpus/README.md`, `corpus/lessons/round-23.md`, `SKILL.md`,
  `tools/report-landing-audit.py`, `tests/report-audit/repo-state-grid.py`,
  `.ufo/waves/round-23/final/grid-both.json`,
  `.ufo/waves/round-24/preregistration.json`,
  `.ufo/waves/round-24/oracle-amendment-1.json`,
  `.ufo/waves/round-23/build/advice/ScribeLessonDraft.md` (house format),
  `.ufo/waves/round-24/build/out/{CritNoTrade,SrcPromisorCode,ScribeSkill}/`
  (peer artifacts, read)

## Findings (exact evidence)

1. **The reading to remove is in this scoped file, and only here.**
   `corpus/README.md:330-331` — "Declared trade: a complete blobless partial
   clone or paired promisor pack is refused where frozen gave a verdict."
   The correction withdraws that *policy reading*; the round-23 section
   itself stays as filed.
2. **The refusal that produced it is real and unconditional.**
   `tools/report-landing-audit.py:457` raises `partial clone (promisor pack)`
   for any `.promisor` marker paired with its `.pack`;
   `tools/report-landing-audit.py:462-465` raises `partial clone ({key})` for
   `extensions.partialclone` or a true `remote.*.promisor`. Neither consults
   object availability, so metadata alone decides exit 2.
3. **Round-23 measurements the correction supersedes (r23 evidence,
   unchanged).** `.ufo/waves/round-23/final/grid-both.json`, current arm
   (auditor sha256 `da5041a8…5af1`, population `f29fab8d…d55364a`):
   `F06-lazy-fetch-command` exit 2, stderr `could-not-evaluate: …
   partial clone (extensions.partialClone…)`;
   `F23-promisor-pack-without-config` exit 2, `promisor pack`;
   `T01-blobless-partial-clone` exit 2 with `expected_exit 0`, `met false`;
   frozen arm (`4fe9339f`, sha256 `09ecd63b…b3b3f`) `T01` exit 0,
   `met true`; `C09` (promisor=false) and `C10` (orphan marker) exit 0 in
   both arms.
4. **The retained-grid rows the B reading moves.**
   `tests/report-audit/repo-state-grid.py:651` F06 (graded fault) → exit 1
   with the same findings as its unmarked twin, reason pin `:697`
   ("partial clone") **dropped**; `:670` F23 (graded contract) → **stays
   exit 2**, reason pin `:704` ("promisor pack") must become
   **content-derived** (the cited blob unreadable locally); `:674-675` F27
   (filter-only promisor remote) → **keeps exit 1** with `landed-unresolved`
   + `unresolved-full-hash`, because a locally unresolved citation keeps the
   ordinary failed verdict; `:689` T01 → audits **clean under B**, so the
   declared trade is withdrawn; `:679-680` C09/C10 unchanged at exit 0.
5. **The B reading's own authority, from the amendment file.**
   `.ufo/waves/round-24/oracle-amendment-1.json`:
   `supersedes_expectation_only` = "preregistration.json expected_after[3]
   (unknown citation in any metadata-marked repository necessarily exit2)";
   `chronology` = "Appended before L1 has inspected, measured, or integrated
   the AuditRepair candidate. Initial registration remains immutable and must
   be reported separately, not relabelled passed."; `authority` cites the
   base audit contract `tools/report-landing-audit.py:12-19` ("object in lane
   or fleet repo; no remote-universe existence guarantee"), an outside
   closure control on a complete promisor-marked real lane for rounds 10-22
   including an errata-corrected locally missing hash, an independent
   preimplementation witness analysis, and the instruction that a whole
   pinned-root reachable-tree precondition is broader than the availability
   of objects the audit actually requires. `prospective_expected` lists the
   B rules the draft now states (metadata never changes resolution or a
   clean/failed verdict; required-but-unavailable content is exit 2 with a
   content-derived reason; marked/unmarked twins keep identical substantive
   verdicts; locally sufficient repositories are not refused for unrelated
   missing content; no remote completeness or remote abbreviation-uniqueness
   claims). `original_expectation_verdict` = the initial requirement "is
   withdrawn prospectively, not counted as achieved."
6. **The local-object contract the amendment points at, in the base file.**
   `tools/report-landing-audit.py:12-19` at base `0df800e` — `unresolved-full-hash`
   is "a 40-hex token in the report that is no git object in the lane or
   fleet repo…"; `landed-unresolved` is "a 7..40-hex token inside `## Landed
   changes` … and is no commit in either repo". Neither asserts existence in
   any remote, which is why "unknown ⇒ exit 2" conflicted with it.
7. **D4 stays partial; the open items must not be closed by this
   correction.** `corpus/README.md:326-330` — alternates and gitfile
   redirects (O01/O02), the `--shared`-of-partial bypass, prefix-ambiguity
   overwrite, duplicate Landed sections, errata CR splitting, an `--errata`
   FIFO, memory ceilings, and the unisolated sibling tools
   `citation-provenance.py` / `sources-append-only.py`.
8. **Isolation to preserve is already pinned in code and must be restated as
   unchanged.** `tools/report-landing-audit.py:93-99` `GIT_ISOLATION`
   (`--no-replace-objects`, `--no-lazy-fetch`, `i18n.logOutputEncoding=UTF-8`,
   `log.follow=false`, `log.showRoot=true`, `log.showSignature=false`,
   `log.mailmap=false`), `:108` `GIT_TIMEOUT = 20`; `git_env` drops
   inherited `GIT_*` and points `GIT_CONFIG_GLOBAL` at `/dev/null`.
9. **A second file carries the same reading — not mine to edit.**
   `SKILL.md:792` (refusal list) and `SKILL.md:811-813` ("Declared trades
   (frozen 0 → current 2 on complete repositories): a blobless partial clone
   (T01) and a paired promisor pack without promisor config (F23)"). The
   SKILL half is owned by ScribeSkill, who has rewritten it to B; the two
   documents now state one rule.
10. **The r23 count corrections do not touch this scoped file.**
    `corpus/README.md` contains no falsify-wave report count and no
    killed-process count. Those numbers live in `corpus/lessons/round-23.md:178`
    ("73 seats dispatched (68 reports…") and `:174` (M7, "56 blocked `git`
    processes"), i.e. the lesson/log scribes' scope.
11. **Target-file disambiguation.** The top-level `README.md` is 14 lines
    ("What's here" list only) and holds no frontier section; the README with
    the frontier disposition is `corpus/README.md` (335 lines, section at
    `:317-335`).
12. **Peer-measured evidence (round-24 SKILL scribe, base auditor blob
    `cf706c52`, synthetic offline fixtures; quoted as peer data, not re-run
    by this lane).** Identical complete lane+fleet content: no promisor
    metadata → exit 0 clean; `remote.origin.promisor=true` → exit 2
    "partial clone (remote.origin.promisor)"; paired `.promisor` marker →
    exit 2 "partial clone (promisor pack)" — **zero missing objects in all
    three**, so the refusal is metadata-driven. A genuine uncited lane
    commit: exit 1 `landed-omitted` without metadata, exit 2 with it — the
    metadata refusal masks the omission. Removing only the two metadata
    refusals (scratch copy) turns genuinely-incomplete cases into exit 1
    `unresolved-full-hash` / `landed-unresolved` (the frozen arm's
    false-defect verdict): **refusal removal without the availability rule
    is a regression**, which is why the draft states the two halves land
    together. Availability probes: under `--no-lazy-fetch` with the promisor
    remote at `file:///nonexistent`, `cat-file --batch-check` reports
    "<sha> missing" (rc 0, no fetch) and `rev-list --objects
    --missing=print` reports "?<sha>"; `rev-list --all --missing=print`
    *without* `--objects` does not list the missing blob, so a missing-object
    probe must use the `--objects` form and must stay bounded to the audit's
    required reads.

## Cross-lane alignment (README half ↔ SKILL half)

Divergence check against `.ufo/waves/round-24/build/out/ScribeSkill/SKILL-round24-promisor-correction.md`
(97 lines, peer artifact) and the L1's B decision: the two drafts state one
policy on every point that matters —

- metadata never changes local-object resolution or a clean/failed verdict;
- availability is judged per required read, and the required reads are
  named identically (pinned lane tip, the round's lane commits, the cited
  objects, the committed fleet report, the committed `corpus/SOURCES.md`,
  the errata rows); a whole-root precondition is deliberately not
  introduced;
- a locally unresolved citation keeps the ordinary failed verdict with the
  same finding kinds as the identical unmarked twin and authorized errata
  still applying, unless it names referenced-but-unavailable local content,
  which is exit 2 with a content-derived reason and never a guessed
  absence;
- a locally sufficient repository is not refused for an unrelated missing
  blob, unselected branch or unused file;
- the metadata-refusal withdrawal and the availability rule travel
  together;
- no remote completeness and no remote abbreviation-uniqueness claim;
  abbreviation uniqueness over the audited local object set only;
- the withdrawn preregistered expectation is reported as not met, not
  passed;
- D4 remains partial, no new serving capability, unchanged other frontier.

No contradiction found. The only difference is granularity: the README half
names the required-read scope explicitly (the SKILL half states the same
scope in prose in its table preamble). Both keep the round-23 refusal list
minus its two promisor sentences, the trusted-use restriction, the git
isolation string, strict UTF-8, the 20 s deadline and git ≥ 2.45.

## Out of scope (not drafted, not claimed)

- Any edit to `corpus/README.md`, `SKILL.md`, `corpus/lessons/round-24.md`,
  `LOG.md`, `SCORECARD.md`, `corpus/knowledge/*`, `tools/*` or
  `tests/report-audit/*`.
- The auditor implementation, the new `tests/report-audit/promisor-grid.py`
  and any mutant runner (executor lanes).
- The lesson, log, scorecard and knowledge appends (other scribes).
- The formal "not met" report of the withdrawn expectation: that belongs in
  the wave evidence and the lesson, not in the README draft.
- Source rows / gate content; no page was opened in this lane, so the draft
  cites no new source and quotes none.
- Any serving, endpoint, model or consumer claim; no endpoint sample and no
  service restoration is asserted by the draft.

## Not verified

- The round-24 measurement itself: `promisor-grid.py --arm both --json`
  against frozen `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` was not run and
  did not exist at drafting time. The draft leaves `⟦MEASUREMENT⟧` and
  `⟦POLICY-ROWS⟧` unfilled rather than inventing counts.
- Whether the landed implementation reaches the B verdicts (marked/unmarked
  twins identical, F06 exit 1, F23 exit 2 content-derived, T01 clean):
  unrun, so the draft asserts the preregistered/amended policy, not an
  observed outcome.
- The exact set of retained-grid rows L1 will re-pin; the draft names the
  mechanism (promisor policy rows only) and leaves the list to L1.
- Whether the reviewer prefers wording variant A, B or C; A is recommended,
  B and C are supplied as fallbacks.
- `corpus/README.md` line numbers after the append shift by the appended
  block; the cited anchors are pre-append (base
  `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`).
- The peer measurements in finding 12 were **not re-run by this lane**; they
  are quoted as peer-reported data (round-24 SKILL scribe, base auditor blob
  `cf706c52`) and are labelled as such in the draft's evidence section.
- Concurrent L1/peer edits in the lane repo during drafting (`corpus/SOURCES.md`,
  `LOG.md` modified; `corpus/lessons/round-24.md` untracked) are **not mine**
  — this lane made no tracked-file change. The candidate patch was
  re-verified with `git apply --check` against the current working tree
  after those edits appeared: **APPLY-CHECK OK** (`corpus/README.md` itself
  was untouched by them).

## Tools installed or updated

None. No install, upgrade or package transaction was performed in this lane.

## Report

- Draft: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-frontier-correction.md`
- Patched copy: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README.with-round24-frontier.md`
- Candidate patch: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-frontier.patch`
- Policy matrix: `.ufo/waves/round-24/build/out/ScribeFrontier/promisor-policy-matrix.md`
- Append-ready text: `.ufo/waves/round-24/build/out/ScribeFrontier/corpus-README-round24-append-text.md`
- This report: `.ufo/waves/round-24/build/advice/ScribeFrontier.md`

---

## Append — round-24 frontier continuation (W1 doc cutover)

Seat: ScribeFrontier. Append-only draft text only; production untouched
(production pinned at `2e254a1763a9c08aa07fc53081287f506c447d84` per
`.ufo/waves/round-24/fixes/docs-contract.txt`).

### What was drafted

`.ufo/waves/round-24/fixes/doc/ScribeFrontier/append.txt` — 31 lines, 250
words, sha256 `503789fa69c7ce21dce28bf921b7256e80e588987efd424f68d738b4fc296e31`.
A short, paste-ready continuation of the lane README frontier disposition,
meant to follow the landed `## Frontier correction — round24` section
(`corpus/README.md:337-357`). No placeholder, no numeric claim, no source
row.

### Required elements, and where each is satisfied

1. **The rejected round-23 declared-trade claim is named explicitly**, not as
   "the previous paragraph": the text quotes the round-23 section's own
   sentence — "Declared trade: a complete blobless partial clone or paired
   promisor pack is refused where frozen gave a verdict."
   (`corpus/README.md:330-332`) — and states the trade is rejected, not
   carried, because a disclosed loss of a correct runnable verdict is not an
   admissible trade. It also states that the F23 sentence above corrects
   *which fixture witnesses* the trade, not whether the trade is admissible.
   Observation: the landed round-24 section reaches the same conclusion
   through a vaguer route — "Correction to the previous paragraph's
   paired-marker wording" (`corpus/README.md:351-352`) names no claim —
   so the round-23 trade sentence otherwise stands un-rejected in the file.
2. **Local required availability, no whole-completeness precondition:**
   promisor metadata alone does not refuse a complete or locally sufficient
   repository; only evidence the audit actually reads and cannot read
   locally is could-not-evaluate, with a content-derived reason and never a
   guessed absence; availability is judged per required read, not over the
   whole store; no whole-store or reachable-tree completeness precondition is
   introduced; an unrelated historical blob, an unselected branch or an
   unused file that is missing is not a completeness gate; a missing cited
   object already referenced locally, or hidden behind an opaque dependency,
   is not a proved absence. (Consistent with the landed section
   `corpus/README.md:341-347` and with the contract's "No whole-store or
   reachable-tree completeness precondition".)
3. **The H2 floor is still open:** "The Git>=2.45 prerequisite remains open
   to operator disposition (R23-H2); it is not closed here, no older-Git
   support is restored, and no approval of the floor is claimed." Ground:
   `corpus/README.md:353-354`, `SCORECARD.md:1212-1213` ("remains an
   unresolved R23-H2 operator decision, not older-Git restoration").
4. **No new frontier capability, score or admission:** "No new frontier
   capability, no score promotion and no admission claim are made here; no
   endpoint sample, service restoration or new knowledge entry is asserted."
   plus the unchanged other-frontier list, matching the landed section's own
   closing paragraph (`corpus/README.md:354-357`).

### Boundaries honored in this step

- No production edit; no tracked file changed by this seat in this step
  (the file is a draft under `fixes/doc/ScribeFrontier/`).
- No final metrics, counts, grid results, cell tallies or landed hash
  claimed; the text contains no numbers and no placeholders.
- No new source row and no new quotation of external material; the only
  quoted sentence is the repository's own already-filed round-23 trade
  claim.
- No test, no grid, no full-suite run, no install in this step.
- No self-admission: the continuation withdraws a *reading* and states
  boundaries; it claims no new capability, no score and no admission.

### Observation for the integrator

Append-only discipline is preserved: the round-23 trade sentence stays in
the file as filed, and the continuation withdraws its reading the same way
the landed round-24 section withdraws the round-23 refusal wording. The
continuation is narrower than the landed section — it names the rejected
claim and restates the per-required-read boundary — so it adds no new
reading, only the missing name and the explicit absence of a
whole-completeness precondition.

### Artifacts for this step

- Append text: `.ufo/waves/round-24/fixes/doc/ScribeFrontier/append.txt`
- This advice append: `.ufo/waves/round-24/build/advice/ScribeFrontier.md`
