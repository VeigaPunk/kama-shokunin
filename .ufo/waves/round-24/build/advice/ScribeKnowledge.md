# ScribeKnowledge — round-24 `error-is-not-a-verdict` append (draft)

Role: leaf scribe. No subagent dispatch. No production, corpus, fleet, config
or `.jj` write. No installs. No build/test/formatter run. Draft only.

## Behavior

Drafted the append-only round-24 deepening of
`corpus/knowledge/error-is-not-a-verdict.md` — the principle that a refusal
is not a verdict either, and that safe isolation is not availability proof.
The appended section states three states instead of two (supported complete
state / unsupported input / same state as the un-marked twin), names the
isolation measures as containment rather than evidence, requires every exit-2
refusal reason to name the unavailable object instead of the metadata,
requires a refusal to be killable by a paired full-clone/metadata-marked
population plus a blanket-refusal mutant, and records that a green
`git fsck` is not an availability oracle.

The section is written against the **prospective** policy of
`.ufo/waves/round-24/oracle-amendment-1.json` (landed `123640b`), which
supersedes `preregistration.json` `expected_after[3]`. My first draft stated
that withdrawn expectation as policy; it was rewritten and the change is
marked `[amended]` in the section so the difference is auditable.

Nothing was edited in the repository. The deliverables are a draft section, a
patched **copy** of the knowledge file, a unified diff and a source-dependency
ledger, all under my out directory.

## Gates

- No gate was run (leaf scribe; the wave's single post-integration
  measurement is L1's).
- `git apply --check` on the candidate diff →
  `Checking patch corpus/knowledge/error-is-not-a-verdict.md…`
  → **APPLY-CHECK OK** (check only; nothing applied).
- Byte relation verified: base file 4704 characters / 4716 bytes; patched
  copy 15851 characters and exactly `base + "\n" + section`, so the earlier
  80 lines are unchanged.

## Touched surfaces

- Written: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.round24-append.md`
  (the draft section, with placement, append-only and amendment rationale)
- Written: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.with-round24.md`
  (patched *copy* of `corpus/knowledge/error-is-not-a-verdict.md`; the
  production file is untouched)
- Written: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.round24.patch`
  (unified diff, 192 lines, `git apply --check` OK)
- Written: `.ufo/waves/round-24/build/out/ScribeKnowledge/source-dependencies.md`
  (which sources the append cites, which two it declines to cite, what the
  working tree admitted during this wave, and what is still awaiting an
  opening)
- Written: `.ufo/waves/round-24/build/advice/ScribeKnowledge.md` (this file)
- Read only: `corpus/knowledge/error-is-not-a-verdict.md`,
  `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/README.md`,
  `corpus/lessons/round-23.md`, `corpus/lessons/round-24.md`,
  `SKILL.md`, `tools/report-landing-audit.py`,
  `tests/report-audit/repo-state-grid.py`,
  `.ufo/waves/round-24/preregistration.json`,
  `.ufo/waves/round-24/oracle-amendment-1.json`,
  `.ufo/waves/round-24/build/{spec.json,dispatch.json,assignments.json}`,
  `.ufo/waves/round-24/build/advice/{ScribeFrontier.md,SrcGlobalGit.md}`,
  `.ufo/waves/round-24/build/out/{ScribeQuality,SrcPromisorCode,SrcCatFile,SrcRevList,SrcFsck,SrcRepoLayout,CaseCompleteLane,CaseMarkerLane,CaseCompleteFleet,CaseHydratedLane}/`
  (peer artifacts, read)

## Findings (exact evidence)

1. **The principle's target is real and unconditional in code.**
   `tools/report-landing-audit.py:438-465` `check_history_repo(repo)` raises
   `EvalError(f"{repo}: partial clone (promisor pack)")` at `:457` for a
   `.promisor` marker whose `.pack` sibling exists, and
   `EvalError(f"{repo}: partial clone ({key})")` at `:465` for
   `extensions.partialclone` or a boolean-true `remote.*.promisor`. It runs
   before any object check: `run()` calls `check_history_repo` for both
   repos at `:514-515`, before `resolve_branch` (`:516`) and before any
   `audit_round` (`:519`). `EvalError` prints
   `could-not-evaluate: …` and returns 2 at `:948-949`.
2. **The function's own docstring states the rule the code does not apply.**
   `tools/report-landing-audit.py:440-441`: "whose missing objects belong to
   a promisor remote (absence is not evidence there)". The code refuses on
   the declaration, i.e. it treats the declaration as the evidence.
3. **The r23 outcome is documented as a trade, not a defect.**
   `corpus/lessons/round-23.md:83-84` ("Declared tradeoffs: partial clones
   and shallow clones are refused even when every cited object is local")
   and `:206-209`; `corpus/README.md:330-331`; `SKILL.md:811-813`. The
   round-24 preregistration and `corpus/lessons/round-24.md` §Mistakes
   reclassify that as operability harm, not a disclosed trade.
4. **Measured base behaviour on paired offline fixtures (peer lanes, this
   wave, base auditor sha256 `da5041a8191e0e6e…`):**
   - `build/out/CaseCompleteLane/base-observation.json` — `PROM-CLEAN`:
     full clone exit 0 / no defects; promisor-marked twin exit 2, stderr
     `could-not-evaluate: … partial clone (remote.origin.promisor)`;
     premise `missing_objects: []`. `PROM-OMIT`: full clone exit 1 with
     `landed-omitted 29e8ea69…`; promisor-marked twin exit 2; premise
     `missing_objects: []`.
   - `build/out/CaseCompleteFleet/base-run.json` — `full` exit 0 (0
     defects), `promisor` exit 2 `partial clone (remote.origin.promisor)`;
     the case's own discriminator arm exits 1 with
     `landed-omitted 4cd5a78e…`.
   - `build/out/CaseMarkerLane/evidence.json` — `A_full_clone_clean` exit 0,
     `B_marker_lane_clean` exit 2 `partial clone (promisor pack)` with
     premise `all_reachable_objects_local: true`, `no_missing_objects:
     true`, `no_promisor_config: true`; `C_full_clone_omission` exit 1
     `landed-omitted`, `D_marker_lane_omission` exit 2;
     `F_marker_removed_ablation` exit 0 after removing **only** the
     `.promisor` marker file, every other byte unchanged.
   These are the observations the draft's three-state table and its
   "metadata decided, content did not" sentence rest on.
5. **Isolation is named channels, not a general statement.**
   `tools/report-landing-audit.py:93-99` `GIT_ISOLATION` =
   `--no-replace-objects`, `--no-lazy-fetch`,
   `i18n.logOutputEncoding=UTF-8`, `log.follow=false`, `log.showRoot=true`,
   `log.showSignature=false`, `log.mailmap=false`; `:108` `GIT_TIMEOUT = 20`.
   S089 (`corpus/SOURCES.md:101`) records that the two global options
   "neither cover info/grafts or shallow". The `--no-lazy-fetch` page quote
   "Useful together with git cat-file -e `<object>` to see if the object is
   locally available" was reopened this wave
   (`build/out/SrcGlobalGit/pins.json` → `quotes.no_lazy_fetch_use`) and is
   *not* yet in the S089 `teaches` cell; the draft attributes it to the
   reopened page with its evidence path instead of to the row.
6. **The exit-2 reason pins are metadata reasons and must change.**
   `tests/report-audit/repo-state-grid.py:697` pins `F06-lazy-fetch-command`
   → `"partial clone"`; `:704` pins `F23-promisor-pack-without-config` →
   `"promisor pack"`. Both rows keep exit 2 under the round-24 policy
   (the cited object is genuinely absent in both fixtures:
   `f_lazy_fetch` at `:272-287`, `f_promisor_pack` at `:195-212`), but the
   reason must name the unavailable object, else a justified refusal and the
   blanket one are indistinguishable.
7. **The round-23 grid cannot kill a blanket-refusal mutant, so a paired
   population is required for credit.** `tests/report-audit/repo-state-grid.py:13-15`
   ("`open` rows … and `tradeoff` rows (declared new refusals) are reported,
   never graded"), `:689` `T01-blobless-partial-clone` is a `tradeoff` row
   expecting exit 0 (never graded), `:679-680` `C09`/`C10` carry no promisor
   metadata, `:670` `F23` refuses in both arms. KQ34
   (`corpus/QUALITY.md:177`) and KQ25 (`:142`) forbid crediting a promise
   the gate cannot violate; the r24 credit comes from the complete-local
   paired row and a killed mutant, with kill credit only on grid exit 1.
8. **`git-fsck` cannot be used as a completeness oracle.** `build/out/SrcFsck/evidence.md`:
   the web rendering, the installed 2.56.0 man page and the v2.56.0 adoc all
   contain zero occurrences of promisor/promise/partial clone; git's
   `builtin/fsck.c` `mark_object` returns early for a promisor object
   (`:143-149`). The working tree records this as **S104, rejected**, with
   the flip "use a separately demonstrated required-object availability test
   instead of claiming this fsck result establishes local availability"
   (`corpus/SOURCES.md:116`, `corpus/lessons/round-24.md` §Gate).
   `gitrepository-layout(5)` has zero `promisor` hits
   (`build/out/SrcRepoLayout/evidence.md`), so it cannot arbitrate either.
9. **The initial registration is not the policy.** `.ufo/waves/round-24/oracle-amendment-1.json`
   supersedes only `preregistration.json` `expected_after[3]` ("a missing
   citation in any promisor-backed repository is unknown, not proved absent:
   exit2 unless resolved locally by another audited repository"), prospectively
   and without relabelling the initial registration as passed: "a whole
   pinned-root reachable-tree precondition is broader than availability of
   objects actually required by the audit; do not introduce it merely to
   retain refusal". The amended policy keeps a locally unresolved citation
   on the twin's ordinary finding path, and reserves exit 2 for content the
   audit actually must read and cannot. My draft states the amended rule and
   marks the change `[amended]`.
10. **Two candidate source rows the principle would like to lean on are not
    admitted.** `SrcPromisorCode`'s `promisor-remote.c`
    `partialclonefilter`-only registration, and `SrcCatFile`'s `cat-file -e`
    exit-status row — the latter's proposed supersession of S083 is recorded
    in `corpus/lessons/round-24.md` §Gate as having no premise. The draft
    names both gaps instead of inventing citations; the ledger records them.
11. **Two files carry the r23 "declared trade" reading and will disagree if
    only the knowledge file is appended.** `corpus/README.md:330-331` and
    `SKILL.md:788-796` + `:811-813` list the promisor refusal among the
    exit-2 reasons and the declared trades. `ScribeFrontier` owns the README
    half and flagged the SKILL half as not its own (`advice/ScribeFrontier.md`
    finding 7). The knowledge append deliberately does not restate the
    trade as current policy, only as the base behaviour the round-24 policy
    replaces.

## Out of scope (not drafted, not claimed)

- Any edit to `corpus/knowledge/error-is-not-a-verdict.md`,
  `corpus/QUALITY.md`, `corpus/lessons/round-24.md`, `corpus/SOURCES.md`,
  `corpus/README.md`, `SKILL.md`, `README.md`, `SCORECARD.md`, `LOG.md`,
  `tools/report-landing-audit.py` or `tests/report-audit/*`.
- The auditor implementation, the availability probe, the reason re-pinning
  and the new `tests/report-audit/promisor-grid.py` (executor lanes).
- The KQ35 criterion row (`build/out/ScribeQuality/KQ35.md` is the peer's
  draft; the working tree already carries an L1-written KQ35 — this seat
  neither reviewed nor changed it); the knowledge append and that criterion
  are complementary, and the append claims no criterion of its own.
- No page was fetched by this seat, so no new source row and no new quote is
  introduced; the only quoted sentence not already inside an admitted row is
  attributed to the page reopen with its evidence path.
- No serving, endpoint, model or consumer claim; no endpoint sample and no
  service restoration is asserted.

## Not verified

- The round-24 measurement itself: `python3 tests/report-audit/promisor-grid.py
  --arm both --json` against frozen `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
  was not run and did not exist at drafting time. The append states the
  policy, not an observed repair.
- Whether the landed implementation keeps exit 2 for `F06`/`F23` with
  content reasons, and which exact reason strings L1 re-pins: unrun.
- The availability measurement mechanism (`git cat-file -e`,
  `cat-file --batch-check`, `rev-list --missing=print`): the append
  constrains the outcome and the evidence, not the mechanism.
- The `CaseHydratedLane` base evidence file
  (`build/out/CaseHydratedLane/evidence-base.json`) shows every arm exit 2
  with a *harness* error (`can't open file …/candidate/…/report-landing-audit.py`),
  so it proves nothing about the base auditor and is not relied on here.
- Line anchors cited are pre-append and refer to base `0df800e8`; the
  knowledge file grows by the appended section, and the production file is
  currently 80 lines.

## Tools installed or updated

None. No install, upgrade or package transaction was performed in this lane.

## Report

- Draft section: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.round24-append.md`
- Patched copy: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.with-round24.md`
- Candidate diff: `.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.round24.patch`
- Source ledger: `.ufo/waves/round-24/build/out/ScribeKnowledge/source-dependencies.md`
- This report: `.ufo/waves/round-24/build/advice/ScribeKnowledge.md`

---

## Appended — round-24 refusal-semantics continuation (W1 resumption)

Same writer, no new seat. Scope: a **short** append-only continuation of
`corpus/knowledge/error-is-not-a-verdict.md`, drafted only. No production
edit, no source row, no test, no full suite, no network.

### Artifacts

- `.ufo/waves/round-24/fixes/doc/ScribeKnowledge/append.txt` — the
  continuation text (5,462 bytes), paste-ready.
- This file — appended advice, not rewritten.

### What the continuation states (five points, each anchored)

1. **Presence is per store; the proof is per canonical object.** The
   selected core proposal takes each store's *own* bare answer
   (`fixes/StoreLocalPresence/report-landing-audit-v9.py:246`, helper
   `bare_objects` at `:190`) and reconciles a conclusive non-commit outcome
   only against the **same canonical object id** behind the token
   (`:294-310`); different objects behind one abbreviated name are not
   reconciled. The pinned production still merges the stores for that
   question (`tools/report-landing-audit.py:204`, used at `:221`), so the
   draft marks the per-store rule as the *proposal's* correction, not a
   filed production fact.
2. **Known unavailable ids from all present roots; opaque boundary only
   from the pinned root.** Two walks, two root sets: `missing = walk((),
   roots)` over every present local commit/tree/tag root (v9 `:752`, `:762`),
   `opaque = walk(("--filter=blob:none",), [root])` from the pinned audit
   root only (v9 `:763`). The pinned production walks both from the same
   all-present roots (`tools/report-landing-audit.py:666-677`); the split is
   the proposal's correction.
3. **No whole-store / reachable-tree completeness precondition.** The root is
   the audit's context, not a completeness gate; the store-wide diagnosis
   runs only for a citation no audited repository resolves (v9 `:767-774`).
4. **A failed required read is a refusal; a runtime fault is not.** Typed
   could-not-evaluate with a content-derived reason (v9 `required_read`
   `:343`); a fatal timeout/OS cause is marked `fatal` and spends no second
   diagnostic timeout (v9 `:167-178`; `root_tree` skips the call `:326-341`).
   The grid reads the catch-all identity `could-not-evaluate: internal:`
   from the **full** stderr and treats it as an error, not a refusal
   (grid `:912`, graded `:883-887`); tracebacks and internal errors are unmet
   observations and can never earn a mutant kill.
5. **A diagnostic difference is not an acceptance.** Mutation classes
   `fixes/MutationEvidenceV6/rationale-v6.md:58-67`: `refusal-2` is an
   over-refusal signal and explicitly *not* availability credit;
   `actual-verdict` is the availability credit; `diagnostic-only` and
   `unclassified` earn none; a refusal is never labelled an availability
   acceptance and a same-exit diagnostic sensitivity is not an
   unavailable-evidence acceptance witness. KQ35 obligations are read from
   those class rows, not a raw kill count. Plus: the shape of a current-arm
   refusal is graded (typed CNE, no verdict document, content-derived reason
   naming the object, never the r23 metadata refusal — grid
   `check_exit2_form` `:840-858`, forbidden strings `:88`).

### Boundaries honoured

- **No source duplication.** The continuation introduces no source row, no
  quote, no facet and no used-by cell, and restates none of the
  `ConnSources` packet's S095/S097/S098 mutable-cell corrections or its
  appendix blocks. It cites only the already-filed rows by their existing
  role in the sections above.
- **No measurement claimed.** No candidate count, verdict, numerator or
  landed hash; production stays pinned at `2e254a1763a9c08aa07fc53081287f506c447d84`
  and the pinned auditor is `tools/report-landing-audit.py` sha256
  `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`.
- **No duplicate ownership.** Fixture/evidence corrections, the grid's
  comparison-method labels and the mutator's pending output-field names are
  named as other lanes' scope and left alone.
- **No production write.** `git diff -- corpus/knowledge/error-is-not-a-verdict.md`
  is empty; `corpus/knowledge/error-is-not-a-verdict.md` is 127 lines
  (base `0df800e8` plus the landed round24 sections) and is untouched.

### Not verified

- No grid, mutant, selftest or probe was run; the anchors are read from the
  proposal files and the pinned production only.
- Whether L1 adopts these exact wordings, and where they land relative to
  the already-landed round24 section (`corpus/knowledge/error-is-not-a-verdict.md:89-127`),
  is L1's call.

---

## Appended — round-24 refusal semantics, integration-ready v2 (W1 resumption)

Same writer, no new seat. **New payload:**
`.ufo/waves/round-24/fixes/doc/ScribeKnowledge/append-v2.txt` (5,809 bytes).
This is the integration-ready text for `corpus/knowledge/error-is-not-a-verdict.md`;
`append.txt` (v1) stays on disk byte-identical as the earlier draft, and
**v2 supersedes v1** — the five principles and the scope are preserved, the
framing is what changed. No production edit, no source row, no test, no
full suite, no network.

### What changed from v1 to v2 (the IRC requirements)

1. **Canonical cutover in present tense.** v2 states what the audit, grid
   and mutator *hold from the round-24 cutover onward*, not what a
   proposal suggests. No sentence presents a prototype or a pinned
   production state as the current claim.
2. **The historical contrast is by commit, not by a moving path line.**
   The two pre-cutover behaviours are named as "Before the cutover (lane
   commit `2e254a1`)", verified against `git show
   2e254a1:tools/report-landing-audit.py`: `lookup()` answered presence
   from the merge of all audited stores (`:204`, used at `:221`) and
   `missing_reachable()` walked both sets from the same all-present roots
   (`:666-677`).
3. **Current anchors are function names in canonical paths** —
   `tools/report-landing-audit.py`: `bare_objects()`, `lookup()`,
   `present_roots()`, `missing_reachable()`, `build_store()`,
   `required_read()`, `root_tree()`; `tests/report-audit/promisor-grid.py`:
   `check_exit2_form()`, `grade()`, `run_case()`, `REASON_CLASSES`,
   `METADATA_REFUSAL`; `tests/report-audit/promisor-mutants.py`:
   `classify_row()`. The grid and mutator names are the ones the
   integrated/V4/V6 files carry, so the text stays valid after the cutover
   lands them in the same commit.
4. **Prototype paths only in the provenance footnote.** The filed
   `.ufo/waves/round-24/fixes/…` prototypes are named once, at the end, as
   the provenance of the wording.
5. **No final metrics, hashes, placeholders, source curation, tests or
   production claims.** `grep -c sha256 append-v2.txt` → 0; no `⟦…⟧`
   placeholder, no count, no numerator, no landed hash; the source packet
   is neither restated nor altered.

### The five principles, preserved in v2

1. Presence is **per store** (`bare_objects()`), and a conclusive
   non-commit outcome is reconciled only against the **same canonical
   object id** behind the token.
2. Known unavailable referenced ids are encountered from **all present**
   local commit/tree/tag roots; the **opaque** missing-name boundary comes
   only from the pinned audit root.
3. **No whole-store or reachable-tree completeness precondition** — the
   root is the audit's context, and availability is judged per required
   read.
4. A failed **required read** is a typed refusal with a content-derived
   reason; a **runtime fault** (timeout, broken git, catch-all
   `could-not-evaluate: internal:`, traceback) is an error, not a refusal,
   and never earns a credit.
5. A **diagnostic difference is not an acceptance**: the mutator's class
   rows carry the credit, and a refusal is never labelled an availability
   acceptance.

Plus the refusal-shape rule: a current-arm refusal is graded (typed
could-not-evaluate, no verdict document, content-derived reason naming the
object, never the r23 metadata refusal), and the grid's own controls are
behavioural — a legitimate content-derived refusal must be accepted and the
same refusal carrying the internal identity must not be.

### Boundaries held

- No source row, quote, facet or used-by cell introduced; the
  `ConnSources` packet is untouched and not restated.
- No count, verdict, numerator or landed hash claimed.
- No production write: `git diff -- corpus/knowledge/error-is-not-a-verdict.md`
  is empty.
- Fixture/evidence corrections, the grid's comparison-method labels and the
  mutator's pending output-field names remain other lanes' scope.

### Not verified

- No grid, mutant, selftest or probe was run; the anchors were read from
  the canonical and prototype files and from `git show 2e254a1:…` only.
- Where L1 lands this text relative to the already-landed round24 section
  (`corpus/knowledge/error-is-not-a-verdict.md:89-127`) is L1's call.

---

## Appended — round-24 refusal semantics, v3 (taxonomy qualification + dead-constant drop)

Same writer, no new seat. **New payload:**
`.ufo/waves/round-24/fixes/doc/ScribeKnowledge/append-v3.txt` (6,272 bytes).
`append.txt` (v1) and `append-v2.txt` (v2) are preserved byte-identical; v3
is the live payload. No production edit, no source row, no test, no full
suite, no network, no new policy or data.

### Change 1 — mutator taxonomy, now V7 (sha256 `7ba30ccc…`)

v2 stated the class list but did not qualify the same-normal-exit case, and
it named the V6 prototype as the provenance. v3 states the taxonomy the way
V7 fixes it (`fixes/MutationEvidenceV7/rationale-v7.md:32-37`,
`promisor-mutants.py:592-624`, `classify_row()`):

| exit pair | class | meaning |
|---|---|---|
| `0`/`1` → `2` | `refusal-2` | over-refusal signal, **not** an availability credit |
| `2` → `0`/`1` | `actual-verdict` | the availability credit |
| `0` ↔ `1` | `verdict-change` | only this pair is a verdict change |
| `0` → `0`, `1` → `1` | `same-verdict-exit` | same exit, detail may differ; no substantive exit change, no availability claim |
| `2` → `2` | `diagnostic-only` | the refusal stayed a refusal; only diagnostics can differ |
| missing/outside `0`/`1`/`2` | `unclassified` | no class credit is guessed |

The V6 overstatement was that `0`→`0` and `1`→`1` were labelled
`verdict-change`; V7 separates them into `same-verdict-exit`, and
`diagnostic-only` now means exclusively `2`→`2`. v3 says exactly that, and
the provenance footnote names V7 only.

### Change 2 — the dead `METADATA_REFUSAL` anchor is dropped

`METADATA_REFUSAL` was an unreferenced constant in the grid (`grep -c` → 1
occurrence, the definition itself) and `DocQuality` flagged it: the live
metadata guard is the per-cell `reason_forbidden` list in the committed
expectation manifest, not that constant. Verified on the committed manifest
`tests/report-audit/promisor-grid-expectations.json`: 30 of 47 cells carry
`reason_forbidden`, and exactly those 30 carry the frozen
`reason_class: "metadata"` — so the active current-arm check is the
per-cell list, and `REASON_CLASSES["metadata"]` grades the frozen history.

v3 therefore anchors `check_exit2_form()` plus the manifest's per-cell
`reason_forbidden`, and states that `REASON_CLASSES` grades the historical
frozen refusals. `grep -c METADATA_REFUSAL append-v3.txt` → 0.

### The five principles and the refusal-shape rule are otherwise unchanged

Per-store presence with same-canonical-object proof · known-missing from
all present roots vs opaque boundary only from the pinned root · no
whole-store or reachable-tree completeness precondition · failed required
read = typed content-derived refusal vs runtime fault = error, never a
credit · diagnostic difference ≠ acceptance. Plus the graded refusal shape
and the behavioural grid controls.

### Boundaries held

- No source row, quote, facet or used-by cell introduced; the
  `ConnSources` packet is untouched and not restated.
- No count, verdict, numerator or landed hash claimed.
- No production write: `git diff -- corpus/knowledge/error-is-not-a-verdict.md`
  is empty.
- Earlier bytes preserved: `append.txt` and `append-v2.txt` unchanged on
  disk.

### Not verified

- No grid, mutant, selftest or probe was run; the anchors were read from
  the canonical files, the V7 proposal and the committed manifest only.
- Where L1 lands this text relative to the already-landed round24 section
  (`corpus/knowledge/error-is-not-a-verdict.md:89-127`) is L1's call.
