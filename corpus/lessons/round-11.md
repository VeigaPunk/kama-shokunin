# Round 11 — explicit provenance and served-identity limits

Steered round 11; actual continuation and documentation review 2026-10-20 UTC.
Baseline source revision: `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
Round claim declaration: `.ufo/waves/round-11/claims.json` supersedes the inherited
`spec.json` and `baseline-revision.json` claim wording, not their historical bytes.

## Claims and fixed denominators

- **C1 calibration:** nine legacy knowledge files, 27 missing column-zero
  provenance fields, become explicitly sourced/dated/recheckable records by appended
  supplements, preserving their original byte prefixes. This is calibration of
  historical evidence, **not endpoint freshness or serving recovery**. The old plan's
  eighteen entries included lessons; lessons are not the nine-file knowledge denominator.
- **C2 coverage:** `knowledge/served-identity-crosswalk.md` extends existing
  tags/ps coverage with remote-inventory caveats, expiry, nullable loading metadata,
  router-state boundaries and alias/digest inference limits. A new filename alone is
  not expansion. It cites reopened S001/S010/S011/S012/S016 and new S031.
- Numeric axis assessments remain calibration 7 and coverage 9 (delta 0 each).
  A metadata-field or entry count does not objectively re-derive a global 0–10 score.
  Operability, freshness, depth and adjacency are not claimed improvements.

## Gate

### Decisions

| Candidate | Decision | Reason / criterion |
|---|---|---|
| Nine legacy provenance supplements | admit, scoped to historical evidence calibration | KQ11: preserve original prefixes; distinguish observation from review; bounded rechecks; no present endpoint assertion |
| Served-identity crosswalk | admit, documentation-only coverage | KQ6/KQ13: actual per-route statements and explicit source revisions; prior overlap credited; inventory/residency/readiness separated |
| `/v1/models` match guarantees loaded weights/readiness | reject | S001 allows null `meta` while loading; S012 loaded-state evidence is time-bounded; KQ1/KQ13 |
| `/api/tags` membership proves local weights | reject | S031 remote fields contradict that inference; KQ13 |
| Documentation proves local Ollama integration/context capacity | reject/defer | KQ4; no local runtime contacted; K05 remains operator-runtime dependent |
| Basename-normalized name equality is cross-engine artifact identity | reject | local convention is not documented content identity; digest joins remain inference |

### New row opened this round

| Row | URL | Access date | Located quote (≤25 words) |
|---|---|---|---|
| S031 | https://docs.ollama.com/api/tags | 2026-10-20 | OpenAPI `ModelSummary.remote_model.description`: “Name of the upstream model, if the model is remote” |

L1 reopened this exact page in-session. It includes `remote_host` as well as
`remote_model`; tier A is limited to those documented inventory fields, not live
residency or behavior of an installed engine. Duplicate-URL/different-scope W04
is intentional: S031 is an append-only scoped correction, not a second independent source.

### Reopened rows and status changes

Every old→new cell change is listed here; unchanged `opened` and `recheck` cells
retain their original dates/cadences. Earlier source-curator advice is historical
advice, not a current file-existence verdict.

| Row | Cell | Old → new |
|---|---|---|
| S001 | used-by | `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/serving-metrics-crosswalk.md` → same plus `corpus/knowledge/served-identity-crosswalk.md` |
| S010 | used-by | `corpus/knowledge/runtime-health-surface-matrix.md` → same plus `corpus/knowledge/served-identity-crosswalk.md` |
| S011 | status | queued → mined |
| S011 | used-by | `—` → `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md` |
| S012 | status | queued → mined |
| S012 | used-by | `—` → `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md` |
| S016 | status | queued → mined |
| S016 | used-by | `—` → `corpus/knowledge/served-identity-crosswalk.md` |
| S031 | new row | absent → mined, docs/A, opened 2026-10-20, recheck 90d, used-by `corpus/knowledge/served-identity-crosswalk.md` |

Reopen evidence: `.ufo/waves/round-11/advice/SourceCurator.md` and the continuation
wave's per-source reports under `.ufo/waves/round-11/verification/`. S001 is
pinned to `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` for the expanded claims;
moving-master snippets do not establish that revision's contents. The original
health matrix already held the tags/ps distinction, but its S009/S010 attribution
was insufficient for those two native routes: its appended correction names S011/S012.

### Independent review boundary

All seats dispatched by Kama are author advisors, not outside non-author reviewers.
The external round-10 disposition at `round-10-verifier-spotcheck.md` remains
unchanged and does not verify this round. Round-11 outside admit/reject sampling
is requested from the orchestrator; no promotion check is marked `[x]` here.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix and demonstrated failure criterion |
|---|---|---|---|
| reference-drift | Original nine files at baseline revision; `.ufo/waves/round-11/legacy-baseline.json` | CORPUS provenance-trio contract; KQ3, now KQ11 | Appended supplements preserve original bytes; same gate must fail for original missing fields, removal of one added field, and mutation of the original prefix. Exact results are committed in round evidence. |
| stale-premise | Inherited `spec.json`/`baseline-revision.json` call C1 freshness; `axis-binding-before.json` versus `axis-binding-after.json`; current `../shokunin.conf` kama row | MISSION Fleet shape, now KQ12 | Current roster assigns operability+calibration; C1 targets lowest assigned calibration (7 vs 8), not historical MISSION example. Earlier declaration retained and superseded by `claims.json`. |
| survivor | `advice/AttackCoverage.md`; original `runtime-health-surface-matrix.md:17` already distinguishes tags/ps | AXES counting/evidence standard, now KQ12/KQ13 | Credit prior distinction and claim only new sourced remote/expiry/loading/router/alias limits. Counterexample: an entry repeating only tags/ps would fail this claim even if metadata checker prints clean. Human semantic review is required. |
| reference-drift | Original health matrix Ollama row cites S009/S010 for native routes | KQ6, now KQ13 | Append explicit S011/S012 correction; retain S009/S010 for base URL/compatibility claims, not `/api/ps`. |
| landing | Earlier headless attempt terminated without report, watchdog `lane-dead-no-report kama round=11` | PROTOCOL inherited-state rule | Reuse only reviewed source/corpus evidence; retain obsolete declaration/advice as history; lane commit and push precede fleet report. `.ufo/round-10/plan.json` and `SEAT-PROTOCOL.md` remain undelivered historical plans, never executed now. |

KQ11–KQ13 in `QUALITY.md` capture these mistakes. The earlier round-10 external
review admitted only after fixes; its retired substring count is not revived.
Resolved 48 versus terminal 2 anchors remains the round-10 result, not “50
re-anchored.” No new source-anchor audit or endpoint integration is asserted.

## Inheritance and scope

Inherited: nine legacy supplements, crosswalk draft, source edits, KQ11–KQ13,
README corrections, measurement implementation, source snapshots and one validated
32-seat build wave. This continuation performs a second validated 32-seat review
wave, integrates its findings, and records fresh acceptance evidence. L1 holds the
canonical planner seat; the `revenger` items are bounded data-walk advisors, not
an unsupported `planner` swarm role. Earlier role-model assumptions are not
re-executed; seat routing comes from the host configuration, with no model argument.

No runtime/config/service mutation, context-capacity acquisition, scheduler,
credential/env read or remote source-tree push is part of the round. No tool
installation was needed. Stale-lane: respawn-per-round continuation; no other
mission for this lane is open.

## Prior outside feedback

`round-10-verifier-spotcheck.md` is the outside adjudication of record: ADMITTED
after post-review fixes. Its score/table correction, retired substring count,
resolved-versus-terminal distinction and coverage restatement are retained, not
reopened as new round-11 claims. KQ14 now makes the earlier counter limitation
durable: bounds and a zero ledger count do not prove content correspondence.
The A20 shape-only inference is narrowed by an appended consumer-registry note.

`verification/PriorDisagreement.md` also raises historical dissent. The final
orchestrator ruling, not that advisor's reinterpretation, governs round 10's
in-province gate-run disposition. S030 stays rejected; no flip is used for a
round-11 admission. The sources-registry capability/coverage dissent remains
recorded in the round-10 lesson and this round claims no replacement capability.
ASCII-versus-rendered-apostrophe differences are presentation-channel facts,
not a new serving claim. Old SCORECARD “no outside review” prose is explicitly
superseded by the round-11 authority entry; round-10 review never verifies round 11.
The proposed extra round-10 criteria are not mechanically adopted: KQ11–KQ14
capture the observed provenance, source/claim correspondence, overlap and
counter defects without a second general research or admission method.

## Continuation review dispositions

- `Provenance2`, `Provenance4`, `Provenance6`, `Provenance9`, `TemporalRisk`:
  remove blanket host-absence/retirement assertions, correct DELTA's baseline
  anchor to line 6, separate missing JSON from retained prose, and make historical
  probe outcomes conditional rather than expected current results.
- `Safety`, `Provenance5`: remove obsolete config-body replay and implicit
  privilege/process-command-line authorization. Future snapshots require an
  isolated explicit history root; no snapshot or probe ran here.
- `CodeSelftest`, `CodeFields`, `Simplify`: faithful prefix mutant, truncated/
  absent-file controls, actual CLI assertions, and a clause-bounded negation
  check. The literal wording guard remains explicitly incomplete; human review,
  not a green regex, establishes temporal honesty. Retaining the small measurement
  tool is necessary for re-runnable evidence; deleting it was rejected.
- `CodeBaseline`: clarify that the baseline lands in round 11 while its source
  files are from `2f7303c`; pin all frozen input hashes in `frozen/expected.json`
  and have `reproduce.py` verify them before comparing expected verdicts.
- `CodeCrosswalk`, `PriorCoverage`: label automated output existence/provenance
  only, label QUALITY clearance an author self-check, credit prior alias/expiry/
  catalog facts, count one new entry rather than its accompanying corrections.
- `SourceContract`: source cells obey allowed changes; preserve the original
  header and four-section shape, without an unnecessary extra clarification
  section. The new S031 locality consequence is [INFERENCE] from documented
  remote fields, not a quotation. S001/S010 anchor-cell expansion suggestions
  were not applied: those existing nonmutable cells remain intact; the new entry
  names the additional exact sections/revision itself.
- Source scouts reopened OpenAI, pinned llama.cpp, Ollama compatibility, tags
  and ps. Their moving-master reads do not replace pinned claims. Advisor
  “missing lesson/registry/report” observations taken mid-integration are not
  final-tree verdicts.

Additional mined mistakes: `scope` — three verification advisors first wrote
relative reports into fleet `.ufo/waves/round-11/verification/`; captured-by the
absolute lane write contract; fixed by byte-preserving copies into the lane,
with fleet-original cleanup routed to Main, never swept into this lane's commit.
`reference-drift` — a provenance recheck revived F6/F7/F11/F12 config-body reads;
captured-by KQ5/KQ11; fixed before landing by historical-only treatment and
bounded future authorization. `survivor` — a missing-field counter could pass
metadata whose value is false; captured-by KQ11/KQ14; human/source review
narrows host-presence, baseline and attribution claims independently of the tally.

Author-advisor reports sometimes include read-only digest/diff inspections
despite “no checks” summaries. These are advisory inspections, not the L1's
acceptance run or an outside verdict. Main's post-integration reproduction is
the sole fresh claim measurement in the continuation.
