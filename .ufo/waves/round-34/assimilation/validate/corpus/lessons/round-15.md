# Round 15 — executable duplicate-corpus admission repair

Steered round 15, 2026-10-20. Starting revision `6e348e28943849aceb08d6954dee92be48ce9ba8`; initial `git status --short` was empty. No inherited lane work. Outside `round-14-verifier-spotcheck.md` remains read-only.

## Declared claim

**C1 calibration: fail-closed duplicate-corpus measurement.** Calibration 7 is the lowest assigned axis versus operability 8; no stagnation waiver. Outside R1 found a real executable defect: the runner's minimum unique-name check does not reject duplicates when at least sixteen other distinct names remain. The existing documentation and receipt limits promised rejection before any child, but the implementation did not provide it. Repair the guard only; keep the same classifier and original literal corpus. Demonstrate the same child-CLI test matrix red against the frozen original runner and green against the corrected runner, including positive unique controls and an actual-classifier invocation marker. Calibration remains 7 → 7, delta 0; finite contract repair is not a mastery score.

This is a substantive executable lowest-axis repair, not another wording-only clarification. No new serving runtime, API fact, conceptual coverage or live endpoint is claimed. Existing 51 unique round-14 cases and their recorded results remain valid in the bounded scope independently admitted by CloseKamaR14. The newly discovered arbitrary-corpus guard guarantee was explicitly excluded from that admission.

## Gate

| Candidate | Decision | Grounding / limitation |
|---|---|---|
| Minimal duplicate-name preflight guard, exercised with at least sixteen unique names plus a duplicate and zero child invocations | admit conditional on measured red/green | Outside R1; existing runner's stripped-name policy; fixed new test expectations; no classifier-policy change |
| Minimum unique-name count alone proves corpus names are injective | reject | At least sixteen unique names and one duplicate satisfy the minimum while violating uniqueness |
| Re-label original round-14 51/51 as invalid because a more general runner promise was false | reject | Outside review independently recounted 51/51 unique names; actual denominator remains valid |
| Loaded metadata or green replay/guard tests prove present inference readiness | reject | Reopened S012's 200 description concerns models loaded into memory, alongside other metadata fields, not an inference-readiness guarantee; no real runtime sampled and readiness remains unknown |
| Failed provider seat implies no substantive partial output | reject | Outside R2 and committed round-14 advice/ExistingProbe.md; artifact presence is distinct from terminal success |

### Opened source

S012 https://docs.ollama.com/api/ps opened by L1 on 2026-10-20. OpenAPI 3.1.0, info.version 0.1.0, GET `/api/ps` responses `200` description: “Models currently loaded into memory” (5 words). Source supports the readiness-boundary rejection and retains the sourced domain constraint of C1; it does **not** establish the lane's duplicate-corpus policy. The sixteen-name minimum and stripped declared-name uniqueness are lane policy, not vendor requirements. C1's diagnosis is grounded in own-work S034, the actual committed runner and outside R1.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|
| vacuous | `round-14-verifier-spotcheck.md` R1; original `measure.py` corpus_problems checks unique count below sixteen but not declared count versus unique count | Existing KQ17 asserts fixed literal tests, but does not require the corpus-validator's rejection promise itself to have a discriminating pre-child test; new KQ18 records that gap | Minimal duplicate-name guard; same test matrix must fail against frozen original and pass after the guard, with original classifier unchanged and invalid-case invocation count zero |
| attribution | Outside R2; round-14 lesson's provider-failure wording versus committed substantive `advice/ExistingProbe.md` | Protocol claimed-versus-reexecuted and evidence attribution; outside verifier supplied the discovery | Append clarification below; no fabricated terminal completion or rerun of provider failure; this clarification earns no separate C1/axis credit |

### Named historical correction — R1

This corrects only the generalized duplicate-rejection promises in round-14 `measure.py` docstring/limits and the inherited `acceptance.json` limits. Those historical claims were false for duplicate-containing corpora with at least sixteen distinct stripped names. The receipt itself is preserved byte-for-byte; its actual unique 51-case results and fixed repertoire are not retracted. This round repairs the current runner and records new fail-capable evidence rather than rewriting the old receipt to appear previously correct.

### Named provenance clarification — R2

`KamaR14.ExistingProbe` was recorded with `Cursor RESOURCE_EXHAUSTED` and no replacement. Nevertheless, substantive partial normalization advice is committed at `.ufo/waves/round-14/advice/ExistingProbe.md`, and `integration-review.json` credits that bounded contract. Provider failure does not prove absent partial output. A committed advice file does not prove a successful terminal completion either. Both facts are retained; no forbidden session/history or credential access is used to infer anything further. Discovery and ruling belong to CloseKamaR14, not this lane's new measurement.

## Scope and initial measurements

Existing serving implementations, registry, histories, source expectations, promotion checklist and historical lesson/receipt bytes are unchanged. New checks use temporary isolated corpora and the actual domain classifier, not a replacement model. No generation, network acquisition, credential reading, consumer mutation, service action or routing changes.

Initial required source validation exit 0:

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; complete streams in `.ufo/waves/round-15/sources-before-validate.json`. Census command: same CLI with `census`; output receipt `sources-before-census.json`: rows33, A30/B0/C3, mined23/queued5/rejected5, invalid tier/status0, missing0. W04 is pre-existing scoped same-URL curation, not independent corroboration.

No operator teaching file was discovered by `glob /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/operator-*.md` (no matches). No installation is needed or claimed. Stale-lane: respawn-per-round; no other kama mission is open. Outside review is still required for this round; dispatched seats are author-side advice, not independent admission or promotion.

### Source curation — direct diagnosis versus domain boundary

New S034 was opened this round at
`.ufo/waves/round-15/frozen/measure-before.py` (2026-10-20), the original
`.ufo/waves/round-14/measure.py` at revision
`6e348e28943849aceb08d6954dee92be48ce9ba8`, `corpus_problems`:350–362.
Located quote at line358: `if unique < MINIMUM_UNIQUE_CASES:` (4 words).
This own-work A row supports the original implementation diagnosis only,
not a measured repaired outcome or independent source authority. C1 rests
on S034 plus the actual outside R1 and the new fail-capable measurements.
S012 supplies the separate sourced readiness-boundary rejection.

Rows added: A1/B0/C0, status mined. Existing S012 used-by old → new:
`corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md`
→ the same paths plus `corpus/lessons/round-15.md`.
No existing status/recheck changes; new S034 used-by
`corpus/lessons/round-15.md`. Immutable registry cells retain their original
values. Exact source-owner receipt: `build/advice/Sources.md`.

Bounded search: question whether the existing duplicate promise follows
from its implementation and whether loaded metadata implies readiness;
sources searched are the original runner blob and the official S012 URL.
Two identified, two screened, two included, zero excluded; no wider
discovery needed once predicate and documented loaded-memory boundary
are located. One new own-work row, not a new API concept or frontier
serving surface. New-row source URL is the repo-relative frozen code path
above; there is no external URL for own-work.

### Advisory safety and rejected scope expansion

AttackSentinel identified that a classifier-wrapper marker alone measures
wrapper entry, not every runner-created process. L1 requested an independent
CPython process-audit observer in the runner launcher and separate event/
classifier-entry counters, preserving the actual classifier. This is test
evidence hardening, not a claim of malicious-runner containment. Missing/
blank/non-string fixture-name validation, duplicate JSON-key validation,
Unicode normalization and semantic case diversity are explicitly outside
the declared R1 duplicate-declared-name repair; no such guarantees are added.

HostSafety disclosed a broad lane-local grep matching a historical
`.ufo/interactive-sessions/` log snippet despite the session-access
prohibition. No additional file open, host database/credential access or
write was reported. The match is excluded from all evidence and Main was
notified; later searches are bounded to explicit code/corpus paths. This
does not become hidden success evidence or authorize further access.

### Historical locator and control-execution precision

The false historical receipt promise lives inside
`.ufo/waves/round-14/acceptance.json` at
`records[0..2].parsed.limits[3]` and `causal_red.parsed.limits[3]`, with
the same statement embedded in their stdout JSON. It is not a top-level
`limits` field. The current runner's old promise is docstring lines13–14
and `LIMITS[3]`; its original implementation is the preserved baseline.
No receipt JSON is modified.

The original runner at measured revision
`e545ed99aaa519196a2a7779b0a293b2ce4c765c`, path
`.ufo/waves/round-14/measure.py`, is blob
`783004569af9072afdeb32c6eeacc462868eb76b` and SHA-256
`fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`.
Those literal expected values are independent of the newly written
manifest. L1's final acceptance checks direct git-blob correspondence
and the literal digest before admitting red-control measurements.
The preserved source is copied from the opened starting working file;
it is not claimed that a Git capture command originally created it.

Relocating that source changes its default path derivation, so the same
guard harness always supplies explicit `--tool` and `--cases` paths to
both runners. It must never mistake a missing-tool or wrong-default
failure for duplicate rejection. Original-corpus retention is measured
against the repaired runner at its original lane-relative location.
The guard matrix clones one already-held passing classifier payload;
its process counts are not additional semantic classifier coverage.

### R2 authority clarification after falsification

The R2 clarification relies on the outside
`round-14-verifier-spotcheck.md` §Routed defects item2 and its L2-floor
section, which explicitly record no replacement and substantive committed
advice despite provider failure. Those facts are not inferred merely from
the advice file or the `dead_seats` field. “Partial output” means output
not establishing successful terminal completion; it does not assert that
the Markdown file labels its own content incomplete or identify which
transport attempt wrote it.

`integration-review.json` credits the **normalization contract**, which is
also independently held in SKILL/crosswalk/rulings; it does not admit every
sentence in `ExistingProbe.md`. The build R2Partial draft's proposed rule
equating terminal completion with an accepted integration row is rejected:
integration dispositions and terminal task status are different evidence.
No new R2 discovery, successful-completion count or axis credit follows.

## Gate

Source-admission supplement to the initial Gate, appended after source-owner
and falsification review: **admit S034** as own-work tier A for the preserved
original code's minimum-only guard, not repaired behavior, new discovery or
independent provenance. Source opened 2026-10-20:
`.ufo/waves/round-15/frozen/measure-before.py`, original
`.ufo/waves/round-14/measure.py` at
`6e348e28943849aceb08d6954dee92be48ce9ba8`, `corpus_problems`:350–362.
Located line358 quote: `if unique < MINIMUM_UNIQUE_CASES:` (4 words).
Reject reading its A tier as a runtime authority or a green measurement.
The discovery remains CloseKamaR14's R1. `every round` means baseline/source
correspondence on reuse, not a mutable serving observation. S012 was reopened
for the separate metadata/readiness rejection; its quote/date/location are
in the initial Gate. No other new source row is admitted.

## Final falsification dispositions

- BoundaryVerdicts/LedgerR1 correctly noted that the runner's active
  docstring and limits still used broad “duplicated corpora” wording.
  L1 narrows those current strings to **declared nonblank string names**
  and explicitly excludes missing/blank/non-string names; no new
  validation policy is added. The earlier `70af36c` implementation had
  exactly two inserted predicate lines. Final code preserves that predicate
  and additionally qualifies its prose, so “only two added lines” is a
  claim about that earlier work revision, not the final file diff.
- FalsifyAudit identified Python 3.14's `_posixsubprocess.fork_exec`
  event as missing from the observation list. L1 includes it and narrows
  the event-list description; valid controls are graded on Popen count,
  not all-event count. No native/FFI, malicious-runner or grandchild
  completeness is claimed.
- `frozen/guard-only-red.py` is a **derived causal control**, not a
  historical source: final runner with exactly the two predicate lines
  removed, keeping the final prose identical. Its manifest pins source/
  derived digests and the removed fragment. Original frozen source stays
  untouched. Both controls must expose the same declared-name defect.
- FalsifyMeasurement's distinction is retained: outer corpus error,
  unmeasured records and process counters are different facts. L1 also
  inspects full retained records: rejected findings/exits null, passed
  false and reasons exactly the corpus error; valid clones' findings and
  exits match their literal held classifier oracle. The helper alone is
  not claimed to enforce every extra receipt assertion.
- Full-matrix results only, no `--only`, establish nonvacuity; a selected
  negative test alone does not defeat reject-all. Matrix counts are not
  classifier coverage. Advice count discrepancies are settled by actual
  committed-input parsing, never by counting report assertions.
- R1 was an outside **static** diagnosis, not an outside execution.
  The new L1 red/green observations are the first executed discrimination
  recorded here. Source/row growth is bookkeeping, not discovery credit.
- A scribe disclosed in-process evaluation of the committed guard despite
  its no-execution instruction; the harness owner performed AST syntax
  parsing despite the no-verification request. Neither is a lane gate,
  runner or classifier test receipt, and neither supplies the round
  measurement. L1 alone performs the recorded post-integration executions.

## Executed author disposition

Measured/pushed work revision:
`4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`.
All command/cwd/exit/full stdout/stderr and complete nested runner results
are committed under `.ufo/waves/round-15/run-*.json`; summary and additional
per-record assertions: `acceptance.json`, **ok true**, errors `[]`.
L1 ran these after both waves and final edits, not during seat implementation.

| Counting command, from lane root | Real exit | Observed |
|---|---:|---|
| `python3 tests/ollama-corpus-guard/check.py --runner .ufo/waves/round-15/frozen/measure-before.py` | 1 | 23 passed, 27 failed; each duplicate control actually measures instead of rejecting |
| Same command with `--runner .ufo/waves/round-15/frozen/guard-only-red.py` | 1 | Same23/50; final prose identical, predicate removed only |
| `python3 tests/ollama-corpus-guard/check.py` | 0 | clean,50 passed,0 failed |
| `python3 tests/ollama-corpus-guard/check.py --selftest` | 0 | clean,50 passed,0 failed; same oracle, not independent evidence |
| `python3 .ufo/waves/round-14/measure.py` | 0 | Original51/51 literal finding/exit/scope matches, unique names51 |

Fixed denominator: 12 committed matrix files,50 unique IDs,27 negative
controls and23 positive controls. Every negative has at least16 distinct
stripped nonblank names plus a real duplicate; every positive is all-distinct.
The matrix contains885 total declared case names:483 on negative controls,
402 on positives. These are repeated invocations of **one** held classifier
payload, not885 distinct classifier tests, new facts or API coverage.
Metadata counting and per-file digests: `fidelity.json`; reproducible command
above emits all fixed IDs and totals from the actual matrix.

Both red controls show classifier/Popen counts483/483 on negative cases,
402/402 on positives; every runner returns0 and every classifier clone
returns loaded_same_digest/0. After: negative controls show0 classifier
entries,0 Popen calls and0 process-audit events; all27 return exact
`corpus: duplicate case names`, runner exit1, all records unmeasured with
null findings/exits, passed false and the exact corpus reason.
Positive controls retain402 classifier entries and402 Popen calls.
Their804 total process events consist of402 Popen and402 private fork-exec
events: **two observed events per child, not804 children**. Original
red-control total is1770 events,885 children. Counters are never substituted
for outer verdicts or a classifier finding.

`fidelity.json` independently compares the frozen bytes with direct
`git --no-replace-objects -C <lane> cat-file blob
e545ed99aaa519196a2a7779b0a293b2ce4c765c:.ufo/waves/round-14/measure.py`,
the literal expected SHA and blob identity above; correspondence true.
Final runner equals that source plus the two-line guard and explicitly
narrowed docstring/limits. The derived causal control equals final source
minus only the two guard lines. Measured code and all12 matrix files match
the named work commit. Ten protected files equal their start blobs; six
existing instruction/knowledge/ledger files preserve their full prefixes;
all existing source cells except the recorded S012 used-by are unchanged.

Final required source validation uses exactly the start command and exits0:

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Final `census` also exits0: rows34, A31/B0/C3,
mined24/queued5/rejected5, invalid tier/status0, missing0.
Thus rows33→34, A30→31 and mined23→24; only new S034 plus S012 used-by.
Full streams/exits: `sources-final-{validate,census}.json`.
No new API/knowledge/capability/frontier ground is counted from those rows.

**Author claim:** C1 calibration improved, numeric7→7; other five axes
unchanged, no observed harm in this finite declared-name contract.
**Trends:** expansion unchanged, quality unchanged, discernment unchanged.
This repairs a measurement promise; it neither revalidates serving knowledge
nor independently spot-checks round15 admits/rejects. Outside15 review still
owns admission and promotion; author-side agreement is not that review.

Actual spawns: build64 then falsify32, total96. Build60 completed and4
provider-failed scouts (402 credits), none replaced; falsify32 completed,
none failed. Two refused build attempts spawned0 and are not extra seats.
Role mix/validated unchanged payloads, assignments and terminal summaries
are retained under `build/` and `falsify/`. L1 held the canonical planner
seat; PlannerWalk was bounded revenger work. Same-handle continuations do
not count as new seats. Tool installs/updates: none.

Cross-domain handoff: the observed background-job-limit100 refusals belong
to kumitate's dispatch mechanics; host scope/diagnosis was supplied by Main,
not inferred from model endpoint evidence. Main resolved admission timing;
no route or runtime mechanism was changed by kama. Credentials remain kagi's,
model evaluation kengaku's, and service/consumer actions operator-owned.
No new L0 question; pre-existing runtime disposition/cadence questions stay
with the operator. Stale-lane: respawn-per-round, no other kama mission open.
