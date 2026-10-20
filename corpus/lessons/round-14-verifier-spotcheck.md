# Round 14 — independent verifier spot-check

author: hyaku closure (non-author integrator, @m_strong)

Reviewed 2026-10-20 UTC by CloseKamaR14, dispatched by the orchestrator, not the lane. Read-only reviewer ReviewCommittedGate and critic ReviewWaveFloor supplied bounded second looks; the integrator owns these rulings. No lane-authored file was edited and no lane gate, harness, selftest, validator or serving probe was executed. The required fleet source-census command alone was executed.

**Closure: status `ok`, admitted `true`.** C1 calibration / capability verifies as `improved`, numeric score 7 → 7. Other five axes are unchanged. Admission is limited to the fixed offline repertoire, not arbitrary-input correctness, current Ollama serving, origin/authenticity of captures, or readiness. A runner guard/prose defect is explicitly excluded and routed below; it does not invalidate the actually unique fixed corpus or its results. No promotion or mint.

## Dispatch and completion digest

Copied from the closure prompt; this committed digest, not mutable watchdog line numbers, preserves the status evidence:

```text
2026-10-20T03:24:22-03:00 launch kama round=14 pgid=2013684 driver=hyaku-inline attempt=1
2026-10-20T03:42:33-03:00 complete kama round=14; hyaku-inline attempt=1
```

Report: fleet `.ufo/reports/round-14/kama.md`.
Prompt: fleet `.ufo/prompts/kama-round-14.md`.
Round start: `e1b3d746dbfd2100b61c67b6389217252592460f`.
Author-delivered HEAD: `06cc6dbea42b88849fb1808d40ae38a08dced21c`.
Measured implementation: `e545ed99aaa519196a2a7779b0a293b2ce4c765c`.
All comparisons end at the author-delivered revision, not this verifier commit.

## Step-1 conformance

Executed these explicit closure checks before writing this file:

```sh
git -C /home/vgpnk/Projects/shokunin log -1 --format='%an %ae %H %cI' -- .ufo/reports/round-14/kama.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-list --count '@{u}..HEAD'
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff e1b3d746dbfd2100b61c67b6389217252592460f 06cc6dbea42b88849fb1808d40ae38a08dced21c -- SCORECARD.md
```

Observed report author/commit: `kama-shokunin kama@shokunin.local 52c833d19cf2429c47ccd57623470833e66e1484 2026-10-20T03:42:14-03:00`. Status output was empty; ahead count `0`. Both author round commits carry `kama-shokunin <kama@shokunin.local>`; measured commit time 03:38:12-03:00 and final commit time 03:41:03-03:00 precede the report. The report names real work, LOG bindings, all six required sections, and four `[~]` lines under SHONEN. It is not a completion marker.

Extracted all standalone 40-hex citations from the committed report and ran `git -C <lane> merge-base --is-ancestor HASH HEAD`: start, measured and delivered hashes above all returned `0` and resolve in the lane object store. Round-14 LOG contains both named implementation and measurement entries.

Rendered committed `templates/round-prompt.md` by substituting lane, round, fleet root, assignment and lane repo. `prompt.startswith(rendered_template)` was `True`; both canonical portions are 8295 characters. The full mission/axes, 1–3 distinct claims, frontier, L2, report, commit-before-report, push and L0 clauses are present. Host addendum supplies the explicit routing and L1-planner ruling; no stale legacy route map is substituted. Calibration 7 is selected as lowest assigned axis versus operability 8; no stagnation waiver. SCORECARD diff appends 76 lines and removes none.

### One failed provider seat: L2 floor still holds

Independent JSON census over committed `.ufo/waves/round-14/dispatch.json` `taskCall.tasks` found **32** spawns, zero resumes; role histogram: executor6, revenger2, scout5, connector3, reviewer7, critic4, sentinel2, scribe2, simplifier1. `taskCall` keys are only `context,tasks`; task keys are only `name,agent,task`. Validation receipt records exit0/stderr empty. Registry, assignments and spawn-result carry the same 32 identities; the single grouped spawn result corroborates one batch. These are committed dispatch artifacts, not proof that no unrecorded transport call occurred; no per-call model override appears in the payload.

`integration-review.json` records ExistingProbe (scout) failed with `Cursor RESOURCE_EXHAUSTED`, no replacement. Even excluding it, **31** nonfailed seats remain and the split still has executor6, scout4, connector3, reviewer7, critic4, scribe2 (plus revenger2, sentinel2, simplifier1). Thus both ≥8 L2 floor and required roles hold. L1 is canonical planner under the addendum; PlannerWalk is a bounded revenger data-walk, not an invalid submitted planner role. The campaign band concerns dispatch: the 32-seat batch meets it despite one provider failure.

There are 32 committed Markdown advice files, including a 14786-byte `advice/ExistingProbe.md` with its seat header and substantive normalization analysis. A provider failure does not imply no partial output. Spawn-result is an initial pending snapshot, not a terminal completion tally; I do not certify “31 completed” from it. Floor admission does not depend on that stronger claim. See provenance clarification R2 below.

## C1 — independent measurement versus committed gate evidence

**Remeasured by the integrator:** immutable start-tree absence, fixed denominator and finding histogram, receipt record tallies/identity, source-row/prefix preservation, delivered-versus-measured equality, and causal-control byte construction. **Evidence-verified only:** all recorded CLI/harness/selftest verdicts. Never executed the sibling's commands.

The executed plain Python measurement used `subprocess.check_output` for `git --no-replace-objects -C <lane> cat-file blob REV:PATH`, `ls-tree` and `diff`, then stdlib JSON, hashlib, collections and AST parsing. No lane module was imported or executed. Core census:

```python
cases_bytes = blob(after, 'tests/ollama-evidence/cases.json')
cases = json.loads(cases_bytes)
print(len(cases), len({c['name'] for c in cases}))
print(hashlib.sha256(cases_bytes).hexdigest())
print(collections.Counter(c['expected_finding'] for c in cases))
for r in receipt['records'] + [receipt['causal_red']]:
    rows = r['parsed']['records']
    print(r['name'], len(rows), sum(x['passed'] for x in rows),
          sum(not x['passed'] for x in rows))
```

Observed **51 cases / 51 unique names**; SHA-256 `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`. Literal histogram: loaded_same_digest10, available_not_loaded3, unknown10, identity_conflict5, remote_inventory5, invalid_input18. Constant-answer maximum18/51 agrees with receipt. Capability row count in SCORECARD **0 → 1**; `git ls-tree <start> -- tools/kama-ollama-evidence.py` returned exit0 and empty output. This proves absent starting capability, not prior misclassification. The new workflow is the only changed `corpus/knowledge/` path.

Committed `.ufo/waves/round-14/acceptance.json` names measured revision `e545ed99...`, `ok: true`, errors `[]`; recorded_at 06:38:39.980974+00:00 precedes its final shipping commit. Its recorded runs:

| Author observation, not a closure execution | Real exit | Independently recounted receipt rows | Finding/result |
|---|---:|---|---|
| absent-tool baseline | 1 | 0 passed / 51 failed | all unsupported, not fallback classifications |
| preserved actual same-round draft | 1 | 49 passed / 2 failed | remote_missing_digest; tags_none_ps_duplicates |
| final fixed corpus | 0 | 51 passed / 0 failed | all literal exits/findings and scope invariants |
| child-CLI selftest | 0 | 51 passed / 0 failed | clean |
| causal precedence-only red | 1 | 49 passed / 2 failed | same two draft failures |

For every receipt, parsed stdout equals stored JSON, record names equal the fixed corpus names, expected exits/findings equal literal fixture values, and outer process exit equals parsed verdict_exit. For all 51 final rows, observed exit equals expected and reported exit, finding equals expected, schema is `kama-ollama-evidence/v1`, readiness is `unknown`, and scope is `offline-captures-not-runtime`.

Tool, cases and measure.py blobs at the measured revision equal delivered blobs. Final source SHA-256 is `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02`; draft `6e1c4ba57cadef0ce1704eaa5dde5a1564bb61c237e5dadd451c664644ee42d4`; causal red `e3123a94437ee5f206397c4b68be042bff9bfcff88db1e1e19190bc78a124536`. All match committed manifests. AST-locating top-level `classify()` and replacing that final span with the draft span reproduces causal-red bytes exactly. This calculation does not execute either function.

The two recorded red results distinguish stable findings, not just digits: remote_missing_digest expected unknown/2 but draft remote_inventory/1; tags_none_ps_duplicates expected invalid_input/2 but draft unknown/2. Final static `classify():218–264` checks duplicates before no-tags and digest presence before remote; its order agrees with rulings/workflow. Final explicit scope and no-normalization semantics are grounded and bounded. Reviewer independently traced the literal fixtures and found no mismatch with classification policy.

Registry home `SKILL.md:438–476` declares gate, owner, entry, 0 clean/1 failed/2 could-not-evaluate mapping, child selftest, committed literal values and temporary-write scope. Nonzero inventory policy results are not runtime faults. Fixed offline inputs do not depend on a mutable fleet artifact; snapshot pinning of a mutable fleet verdict is not asserted. The same separately authored same-round oracle feeds harness and selftest: two runs are not independent external corroboration. Neither asserts explanatory reasons; no arbitrary-input/crash-absence guarantee is admitted.

## Discernment sample and reopened sources

| Item from round-14 Gate | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| Runnable offline classifier with literal cases / child CLI selftest | admit conditional on final cases | delivered tool:218–276; fixed cases; acceptance final/selftest; S012/S031 vendor fields | agree | Final committed receipt satisfies all 51 actual unique cases; metadata-only scope is explicit. Conditional author admission is now independently reviewed, not self-certified. |
| Available name alone proves loaded/ready/local weights | reject | https://docs.ollama.com/api/ps responses200; https://docs.ollama.com/api/tags ModelSummary | agree | Available and running lists are distinct and tags exposes remote markers. Neither name presence nor a fixture run establishes readiness or local weights. |
| Equal name/digest proves current readiness or simultaneous capture | reject | both reopened OpenAPI pages; workflow:18–28,178–188; classify_payload | agree | Schema fields do not authenticate caller files, acquisition time/origin or liveness. Matching captures still report readiness unknown. |
| Apply GGUF basename normalization to Ollama names | reject | actual _matching:190–192; workflow:143–146; fixed exact-name controls | agree | Exact name/model equality is the chosen bounded lane policy; no vendor equivalence rule authorizes that normalization. |

There were **zero newly added SOURCES rows**, independently confirmed from committed row IDs. Thus a newly written row cannot be sampled; reopened both newly touched existing rows S012 and S031 instead, without inventing a row requirement. URLs accessed read-only on 2026-10-20:

- S012 https://docs.ollama.com/api/ps, OpenAPI3.1.0/info.version0.1.0, GET /api/ps responses200 description: “Models currently loaded into memory” — **5 whitespace-delimited words**, matches lesson quote and location.
- S031 https://docs.ollama.com/api/tags, same version, ModelSummary remote_model.description: “Name of the upstream model, if the model is remote” — **10 words**, matches lesson quote/location. responses200 also says “List available models”.

Quotes are ≤25 words and ground the source fields/distinction, not the lane's join/precedence inference. SOURCES S031's local-residency conclusion is correctly qualified by its appended inference clarification; no vendor policy change is inferred.

Independent row census selected `r'^\|\s*S\d{3,}\s*\|'`, parsed pipe cells and counted tier/status: **33 → 33**, A30/B0/C3, mined23/queued5/rejected5 both times. Added IDs `[]`; only S012/S031 used-by cells changed (column10 in zero-based cell lists). All immutable cells remain identical and both changes append replay workflow to existing paths. No row/status/recheck inflation.

Executed required command:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Exit **0**, observed output (tabs displayed as spacing):

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

W04 is existing scoped curation, not independent support. Corpus conformance has the explicit R1 guard/prose exception below; registry census itself passes.

## Per-axis and trend verdicts

All **25** start-tracked protected paths under lessons/, registry/, tools/ plus PROVINCE/SHONEN were byte-equal to delivered objects. All five active ledger/instruction files QUALITY, corpus README, SKILL, LOG, SCORECARD preserve their entire start prefixes. These are executed Git-object comparisons, not inferred from ignored history. No previous serving implementation, source expectation or boundary is replaced.

| Axis | Verdict | Evidence / boundary |
|---|---|---|
| calibration | improved | C1 new bounded offline replay, actual 51-case evidence verified; score7→7, not a mastery score increase |
| operability | unchanged | Old serving tools/expectations unchanged; repertoire credited once under C1 calibration |
| freshness | unchanged | No current serving endpoint or live state sampled |
| depth | unchanged | No new engine fact; documentation operationalizes prior conceptual distinction |
| coverage | unchanged | No conceptual/API surface expansion; new executable capability separately credited |
| adjacency | unchanged | Credentials/routing/model quality/service mutation remain with owners |

- **expansion: improved.** One demonstrated capability enters SCORECARD and the sourced replay workflow enters the explicit round-14 coverage-map supplement. Credit is executable repertoire, not additional source rows or rediscovered tags/ps concepts.
- **quality: unchanged.** No old serving-knowledge entry is reverified/deepened/superseded. R1 is newly found and marked/routed here, not a silently retained false guarantee; it does not undermine the actual fixed unique corpus. No quality improvement is claimed from the gate alone.
- **discernment: improved.** Unlike the author's pending-outside-review `unchanged` baseline, this new round now has an actual non-author sample agreeing on a conditional admit and multiple rejects, with source reopening and reasons above (LEARNING trend criterion). This credits the new outside sampling, not author-side advice or the already-credited historical D2 correction. R1 narrows an ancillary guard guarantee rather than rejecting the sampled capability.

No exploratory claim requires a taste-only ruling. No axis harm is observed in the admitted finite scope. SHONEN remains four author assertions; this bounded offline review does not independently certify all promotion boxes, especially fresh end-to-end real serving work. Do not promote from this artifact.

## Routed defects, clarifications and review incident

1. **R1 → kama, next steered round: measurement runner duplicate-name promise is false.** `measure.py:13–14,77` and inherited receipt `limits` say duplicated corpora fail before children. `corpus_problems():350–362` only tests unique-name count `<16`; it never compares total names with unique names. Thus a duplicate-containing corpus with ≥16 distinct names is not rejected by this guard [INFERENCE from static code]. Tool selftest independently checks duplicates at :359–365. Actual committed cases are 51/51 unique (independently recounted), so C1's fixed result and denominator remain verified; duplicate-rejection generality is not admitted. Add the missing runner guard with fail-capable evidence and append a named correction to the false historical receipt/prose claim; do not rewrite this round's receipt. This is status-neutral conformance debt, not a demonstrated failure of the fixed capability claim. Quality of arbitrary caller corpora is not certified.
2. **R2 → kama, nonblocking provenance clarification:** append that failed ExistingProbe nevertheless left substantive committed `advice/ExistingProbe.md`; integration-review credits its normalization contract while listing the provider failure. “Died” does not establish absent partial output. Preserve the failure/no-replacement record and distinguish committed advice from a successful terminal completion. There is no evidence of forged output or a floor shortfall. No forbidden session transcript is used for this ruling.
3. **Prior D2 → resolved.** Round-14 lesson's named historical clarification explicitly distinguishes source-only mismatch count1 under a verified anchor from outer manifest_invalid/exit2, exactly as outside round-13 requested. KQ17 preserves that distinction and prior bytes are unchanged. Discovery/improvement credit stays with prior review; not a second C1 claim.
4. **Review-side host-safety incident → operator:** ReviewWaveFloor disclosed one prohibited `history://KamaR14.ExistingProbe` access, which resolves beneath `~/.omp/agent/sessions`. The assignment expressly forbade that. No writes/further such access were reported; the integrator did not repeat it and excluded transcript-derived claims. Main was notified. All material rulings here were independently checked against committed lane bytes or public sources; this incident does not become lane-authored fault or a fabricated terminal receipt. Future closure seats must not use history/session access to investigate provider failures.

No new L0 question found for kama rounds13/14. No service/config/credential action, operator promotion, sibling gate execution or protocol edit. Tools installed/updated by integrator or review seats: **none**.
