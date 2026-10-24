# Round 15 — independent verifier spot-check

author: hyaku closure (non-author integrator, @m_strong)

Reviewed 2026-10-20 UTC by CloseKamaR15, dispatched by the orchestrator, not kama. Read-only reviewer seats GateEvidence, WaveFloor and Discernment supplied bounded second looks; the integrator owns these rulings. No lane-owned gate, harness, selftest or serving probe was executed. Only the required fleet source-census validation and plain committed-byte measurements were run. No lane-authored file was edited. Tools installed or updated: none.

**Closure: status `ok`, admitted `true`.** C1 calibration verifies as **improved**, numeric **7 → 7, delta 0**. Repairing a falsified executable assessment promise is a bounded improvement, not evidence of a higher mastery score. Other five axes are unchanged. Admission covers the declared nonblank-string-name guard and fixed offline corpus only; no runtime readiness, classifier-policy expansion, arbitrary-schema correctness, malicious-runner containment, promotion or mint is certified.

## Dispatch and completion digest

Copied verbatim from the closure prompt; this committed digest, not mutable watchdog line numbers, preserves termination evidence:

```text
2026-10-20T04:58:56-03:00 launch kama round=15 pgid=2461431 driver=hyaku-inline attempt=1
2026-10-20T05:44:34-03:00 complete kama round=15; hyaku-inline attempt=1
```

Report: fleet `.ufo/reports/round-15/kama.md`.
Prompt: fleet `.ufo/prompts/kama-round-15.md`.
Start: `6e348e28943849aceb08d6954dee92be48ce9ba8`.
Author-delivered revision: `b8bdc56efc43fe6baad9415d0ca75b7b81ffa952`.
Measured implementation: `4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`.
All measurements below end at the author-delivered revision, not this verifier commit.

## Step-1 conformance

Executed before writing this file:

```sh
git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %aI' -- .ufo/reports/round-15/kama.md
git -C /home/vgpnk/Projects/shokunin log --format='%an %H' -- .ufo/prompts/kama-round-15.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-list --count '@{u}..HEAD'
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 6e348e28943849aceb08d6954dee92be48ce9ba8 b8bdc56efc43fe6baad9415d0ca75b7b81ffa952 -- SCORECARD.md
```

Observed report commit: `kama-shokunin <kama@shokunin.local> 402b93b58868976096a3c58e3ed8f32ea8dd8f0c 2026-10-20T05:43:51-03:00`. Prompt is committed as kama in fleet `2f3b8fef35260e7b4a3ab563f3b8a10545c4f85c`. Lane status output was empty and ahead count was `0`; HEAD equaled the delivered revision. Implementation, integration and receipt commits `70af36c2b15b46d3b4b3c15ef20459cff640dfaf`, `4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`, and `b8bdc56efc43fe6baad9415d0ca75b7b81ffa952` all carry kama identity. Their timestamps 05:29:11, 05:35:31 and 05:40:59 -03:00 precede report authorship.

Ran `git -C <lane> merge-base --is-ancestor HASH HEAD` for all three round commits plus historical measured source `e545ed99aaa519196a2a7779b0a293b2ce4c765c`: all exited `0`. The start revision is also the parent baseline of the verified round range. Report contains real committed work, evidence and LOG bindings, all six required sections in order, and exactly four `[~]` lines under `## SHONEN`: it is not a marker.

Rendered fleet `templates/round-prompt.md` with lane, round, fleet root, assignment and repo substitutions; `prompt.startswith(rendered_template.rstrip() + '\n')` returned **True**. The canonical mission/axes, claim, frontier, L2, report, commit ordering, push and L0 clauses are present. The host addendum explicitly maps canonical planner to L1 and leaves models to session routing. Current `shokunin.conf` assigns kama operability + calibration; calibration7 is the lowest versus operability8. No stagnation waiver is asserted. SCORECARD diff is **83 additions / 0 deletions**, an append, with no score increase or new capability row.

### L2 floor and disclosed process deviations

Independent JSON counts over committed build/falsify spec, dispatch, assignments and registry agree:

| Wave | Actual dispatched | Role mix | Terminal summary | Committed advice files |
|---|---:|---|---|---:|
| build, v2 | 64 | executor17, scout20, reviewer9, critic6, connector4, scribe4, sentinel2, revenger2 | completed60 / failed4 | 60 |
| falsify, v1 | 32 | reviewer12, critic6, scout4, connector4, scribe2, sentinel2, revenger2 | completed32 / failed0 | 32 |

Evidence: `.ufo/waves/round-15/{build,falsify}/{spec,dispatch,assignments,completion-summary}.json`, registries and validation receipts. Validated build `taskCall` equals the dispatched payload; falsify `validation-final.json` equals its dispatched payload, while its earlier preliminary validation was not dispatched. No submitted task has a `model` parameter. Registry and grouped spawn results corroborate the batched calls; these committed records do not prove the absence of unrecorded transport attempts.

**96 dispatched seats, 92 reported completed, 4 failed; not 96 completed.** Build `provider-failures.json` lists CaseAudit00/04/14/19, all scouts, with provider402 credit failures and no replacements. Even excluding all four, build retains **60** seats, scout16, executor17, connector4, scribe4, reviewer9 and critic6: the ≥8 one-batch floor and required split still hold. L1 holds the canonical planner seat under the explicit addendum; PlannerWalk is a bounded revenger data-walk. Revenger2 per wave stays below the ≤4 cap. Provider failure is not proof of absent partial output and advice presence alone is not terminal completion. The summaries, rather than file presence alone, supply the reported terminal tallies.

Build `spawn-result.json` and `spawn-result-retry.json` each contain **64 refused / 0 spawned**, `results: []`, with `Background job limit reached (100)`; `direct-spawn-result.json` contains **64 spawned**. The two refusals add zero seats, so neither the campaign's 64–128 round band nor the ≤128 cap is violated. Refused payload bytes and retry timing are not independently established by the retained refusal results; do not inflate these into extra completed waves or certify an unrecorded identical-payload assertion.

The following are **status-neutral conformance incidents**, not C1 evidence and not grounds to call this real report a marker:

- HostSafety's broad lane-local grep matched an old ignored `.ufo/interactive-sessions/` snippet, contrary to the session-access restriction. SiblingBoundary also disclosed a name-only directory listing. This was a real scope breach, not authorized by its being lane-local. The lane disclosed it, excluded snippet-derived material and notified Main. This closure did not open those logs or use their content. Committed code, independent receipt census and public docs establish every material ruling without them. No additional session/database/credential access or write is established by the reviewed artifacts; that is not a certification of unseen activity.
- Falsify scribe LedgerR1 evaluated the guard in-process despite a no-execution instruction, and build GuardHarness used AST parsing despite the no-verification request. Their results are excluded as measurements. The retained gate executions are L1's separate post-integration runs on the named implementation. These instruction violations remain incidents even though they do not falsify those receipts.
- Validation receipts record effective v2/v1 policy bands but their argv does not retain the required environment bindings. Effective policy is corroborated; exact environment-command provenance remains incomplete. Preserve it next round.

## C1 — remeasured data versus evidence-verified gate executions

**Remeasured by this integrator:** fixed matrix cardinality/labels, raw receipt record tallies and process counters, source/control digests and byte correspondence, retained corpus counts, protected-file/prefix equalities, source census and cells. **Evidence-verified only:** the author-executed CLI, red/green, selftest and retention verdicts. Gate standard forbids executing a sibling gate; none was executed.

Plain measurement used Python stdlib `subprocess`, `json`, `hashlib` and `collections` over `git --no-replace-objects -C <lane> cat-file blob REV:PATH` and `git ls-tree`; no lane module was imported or evaluated. Core reproducible counting form (set `lane` to this repo and `after` to the delivered revision above):

```python
import subprocess, json, hashlib

def blob(rev, path):
    return subprocess.check_output([
        'git', '--no-replace-objects', '-C', lane,
        'cat-file', 'blob', rev + ':' + path])

paths = subprocess.check_output([
    'git', '-C', lane, 'ls-tree', '-r', '--name-only', after,
    'tests/ollama-corpus-guard/']).decode().splitlines()
files = [p for p in paths if p.endswith('.json')]
matrix = [t for p in files for t in json.loads(blob(after, p))]
print(len(files), len(matrix), len({t['name'] for t in matrix}),
      sum(t['expected_rejected'] for t in matrix))
for name in ['before', 'causal_red', 'after', 'selftest']:
    r = json.loads(blob(after, '.ufo/waves/round-15/run-' + name + '.json'))
    rows = r['parsed']['records']
    print(name, r['exit'], sum(x['passed'] for x in rows),
          sum(not x['passed'] for x in rows))
    for negative in [True, False]:
        group = [x for x in rows if x['expected']['rejected'] == negative]
        print(negative, len(group), *[
            sum(x['observed'][k] for x in group) for k in
            ['classifier_invocations', 'runner_popen_events',
             'runner_process_events']])
```

Observed **12 files, 50 tests, 50 unique IDs, 27 negatives / 23 positives**. Every negative has ≥16 distinct stripped nonblank names plus a duplicate; every positive is all-distinct. Total cloned names **885 = 483 negative + 402 positive**, not 885 new semantic facts. Full retained runs have `only: null`; JSON-decoded stdout equals the stored parsed object, and each process exit equals parsed `verdict_exit`.

| Committed author run | Exit | Recounted passes / failures | Negative classifier / Popen / audit events | Positive classifier / Popen / audit events |
|---|---:|---:|---|---|
| original before | 1 | 23 / 27 | 483 / 483 / 966 | 402 / 402 / 804 |
| predicate-only causal red | 1 | 23 / 27 | 483 / 483 / 966 | 402 / 402 / 804 |
| final after | 0 | 50 / 0 | 0 / 0 / 0 | 402 / 402 / 804 |
| selftest | 0 | 50 / 0 | 0 / 0 / 0 | 402 / 402 / 804 |

All 27 final rejected controls have exact `corpus: duplicate case names`, exit1, tool present, null observed findings/exits, false record passes and exactly that reason, with zero runner process events. Positive controls defeat reject-all. The 804 positive audit events are 402 Popen plus 402 private fork-exec observations, not 804 children. Retention receipt has **exit0, 51 passes / 0 failures / 51 unique names**; independently recounted findings: loaded_same_digest10, available_not_loaded3, unknown10, identity_conflict5, remote_inventory5, invalid_input18.

`acceptance.json` reports `ok: true`, errors `[]`, measured revision `4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`. All **five** receipt SHA256 values match the actual committed run bytes. Its timestamp 08:38:37 UTC precedes shipping at 08:40:59 UTC. Frozen original equals the start commit's actual `.ufo/waves/round-14/measure.py` bytes, SHA256 **fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d**, blob **783004569af9072afdeb32c6eeacc462868eb76b**. Final runner SHA256 **cf078f1deef5f180fb051e29591eccd799f2b8f3af5724277f04cfc5a42386c8** matches measured and delivered code. Final source minus the single two-line `if len(declared) != unique` block exactly equals committed `guard-only-red.py`; the causal control retains final prose. Thus original provenance and derived causal control are distinct, verified constructions.

Static diff confirms two behavioral guard lines plus qualified docstring/LIMITS, with the duplicate problem collected before the child branch. `SKILL.md:493–505` registers gate/entry, 0 clean / 1 failed, selftest, literal matrix, temporary write scope and owner. Isolated literal fixtures and a separate measured receipt satisfy the relevant evidence requirements; this gate does not grade a mutable fleet artifact. After and selftest share one oracle and are not independent corroboration. The fixed 50 denominator was remeasured for this delivered revision; the harness dynamically enumerates matrix files and does not itself pin that future file count.

## Discernment sample and source reopens

Outside review on 2026-10-20, from round15 lesson `## Gate` and its appended source-admission supplement:

| Item | Author decision | Re-opened source | Outside judgment | Reason |
|---|---|---|---|---|
| Minimal duplicate-name guard with red/green and zero children | admit conditional on measurements | committed final guard:351–365; original:350–362; raw before/causal/after receipts | agree | Evidence satisfies the condition: duplicate controls fail before and reject after; valid controls still execute. Scope is declared nonblank strings only. |
| Minimum unique-name cardinality alone proves injectivity | reject | frozen original:350–362; literal AppendDuplicate matrix | agree | Sixteen distinct names plus a repeated name retain cardinality16 but violate uniqueness. Original guard lacks the count comparison. |
| Loaded metadata or green replay proves inference readiness | reject | https://docs.ollama.com/api/ps, OpenAPI3.1.0/info.version0.1.0, GET /api/ps responses200 | agree | “Models currently loaded into memory” describes inventory; no current inference was exercised and no readiness guarantee follows. |
| Relabel original round14 51/51 as invalid | reject | unchanged original cases and retained 51-record receipt; outside round14 ruling | agree | The generalized guard was false but the original corpus is actually 51/51 unique; distinguish a false general promise from the bounded measured result. |
| S034 own-work tier A for original guard diagnosis | admit, scoped | new SOURCES row46; frozen code:350–362; actual start Git blob | agree | Exact original source is authoritative for its own code, not for repaired behavior, vendor requirements or runtime health. |

New **S034** quote reopened at frozen line358: `if unique < MINIMUM_UNIQUE_CASES:` — **4 whitespace-delimited words**, matching the lesson's date/location and ≤25-word limit. This source equals both the actual start bytes and original historical source; it establishes minimum-only preflight, not discovery credit. Existing **S012** was reopened publicly by this integrator and reviewer: responses200 description “Models currently loaded into memory” — **5 words**, same OpenAPI version and exact location. Its digest, context length, VRAM and expiry fields do not establish readiness. No live `/api/ps` endpoint was called.

Independent committed-row census: **33 → 34**, A30→31/B0/C3, mined23→24/queued5/rejected5. Added IDs exactly `[S034]`; only existing changed cell is S012.used-by, appending `corpus/lessons/round-15.md` to the three existing paths. No status/recheck or immutable-cell rewrite. This agrees with the lesson's logged old→new change.

Executed the specifically required fleet command:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Exit **0**, observed output (tabs displayed as spaces):

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

W04 is existing scoped same-URL curation, not new independent support. Source-registry validation conforms.

## Axis and trend verdicts

Executed byte comparisons: **10/10** protected paths in fidelity receipt unchanged between start and delivery (serving tools, classifier, original cases/receipt, endpoint registry, province, SHONEN and round14 lesson/verifier). All **6/6** start prefixes are retained in SKILL, LOG, SCORECARD, QUALITY, corpus README and replay entry. Review spot reads confirm no operator-runtime, credential, routing or sibling-domain absorption.

| Axis | Verdict | Evidence / limit |
|---|---|---|
| calibration | improved | C1 actual minimum-versus-injectivity promise repaired and discriminated; score7→7 explicitly bounded |
| operability | unchanged | Existing serving tools preserved; no double credit for regression machinery |
| freshness | unchanged | No present serving-state verification |
| depth | unchanged | No new engine semantics or domain fact |
| coverage | unchanged | No new knowledge entry, API ground or capability |
| adjacency | unchanged | Province unchanged; runtime/services, credentials, routing and model evaluation remain owner-bound; process incidents disclosed above |

- **expansion: unchanged.** S034 is bookkeeping of a known outside diagnosis; no new knowledge/capability ground or frontier entry.
- **quality: unchanged.** The false historical promise is explicitly corrected, not silently retained as current truth; no serving knowledge was reverified against a fresh domain surface. Guard repair is credited under C1, not inflated into a separate quality move.
- **discernment: improved.** The author's `unchanged` correctly described pending outside review. This closure supplies an actual non-author sample agreeing on an admit and multiple rejects, plus reopened sources and grounded KQ18 linked to the prior outside mistake. Credit belongs to this completed sample, not author-dispatched seat advice or rediscovery of R1.

No exploratory claim needs a taste-only ruling. No owned axis is harmed in the admitted scope. Four SHONEN boxes remain author assertions: this bounded offline closure does not certify all promotion boxes, especially real end-to-end serving work. Do not promote or write `[x]` from these receipts.

## Routed defects and next-round precision

1. **Prior R1 → resolved.** Missing count comparison repaired; actual-original and predicate-only red controls fail, after/positive controls and original repertoire pass in committed evidence. Named lesson/knowledge corrections preserve old receipt bytes. KQ18 supplies a grounded fail-capable criterion.
2. **Prior R2 → resolved.** Named lesson clarification distinguishes substantive committed partial advice from successful terminal completion, preserving provider failure/no replacement and outside discovery attribution.
3. **Process incidents → kama next steered round / operator awareness.** Keep code/corpus searches explicitly bounded away from historical session directories; do not run advisory execution or verification contrary to seat instructions. Retain the disclosed grep/name-listing and scribe/AST incidents as incidents, not evidentiary wins. No retrospective rerun of prohibited access is requested.
4. **Dispatch provenance → kama next round.** Preserve environment bindings and refused-attempt payload identity/timing with wave evidence. Current policy bands, actual 96-seat count and L2 split verify; exact omitted refusal payload/environment provenance is not certified.
5. **Nonblocking prose precision → kama.** Replay entry:332–334 says rejection occurs “before the minimum-unique check”; implementation first appends a duplicate problem, then still checks the minimum, and rejects before children. Append precision rather than imply short-circuiting or rewrite history. This does not change the admitted outcome.
6. **Source wording precision → kama.** Existing S012.teaches summarizes a separation from the available list, while the reopened ps page alone describes the running list. Keep that distinction explicitly marked as cross-source synthesis if revisited; immutable registry cells are corrected by an appended superseding row, never rewritten. No readiness inference was admitted and this pre-existing wording does not falsify C1.

No new L0 decision is needed for this closure; standing serving-runtime/cadence questions remain operator-owned and unassessed. No promotion/mint, host transaction, service restart, new tool installation, sibling gate run or lane-authored-file edit was performed.
