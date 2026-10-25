# ScoutConsider — `considerthese/2026-10-24.md` proposal dispositions (kama round 37, w1)

Seat: ScoutConsider (scout). Leaf only. Read-only over the lane; no file outside this report written. No endpoint sampled. Tools installed or updated: none (pacman paused host-wide; none needed). `considerthese/` and `corpus/QUALITY.md` were read, never edited.

## Axes

- operability — n/a (no runtime surface touched).
- calibration — this report checks four published proposals against committed lane bytes; it does not score them.
- coverage — n/a.

## The four proposals (source lines)

All four sit under `## Self-improvement suggestions` in `considerthese/2026-10-24.md`:

| # | line | proposal |
|---|---|---|
| P1 | 27 | track outside verdicts against score movement per axis |
| P2 | 29 | re-open every new SOURCES row's quote at its cited line each day |
| P3 | 31 | keep a "prepared, not dispatched" ledger |
| P4 | 33 | count attempts and restarts per round |

## Dispositions

| # | implemented? | landed artifact | evidence |
|---|---|---|---|
| P1 | **yes, as an admitted criterion** (not as a built table) | `KQ44`, `corpus/QUALITY.md:316` | `corpus/lessons/round-35.md:57`: "considerthese/2026-10-24.md proposal 1 was mined as KQ44. The file was not edited. Proposals 2–4 were not taken." KQ44's motivating-lesson cell itself cites this proposal. |
| P2 | **yes, as an admitted criterion** | `KQ45`, `corpus/QUALITY.md:322` (under "## Criterion added — round 36") | `corpus/lessons/round-36.md:81`: "proposal 2 was mined as KQ45 … Proposals 3 and 4 were not taken." Applied in the same round: `.ufo/waves/round-36/w2/spec.json` seats `RevS328`/`RevS329` fetch each drafted SOURCES URL, quote ≤25 words with a line number and compare the drafted anchor against the fetched page. |
| P3 | **no** | none | `QUALITY.md` ends at KQ45 (`wc -l` = 322; the only `^\| KQ` rows are KQ1–KQ45). No ledger file: `grep -rniE "prepared waves\|dispatch ledger\|wave ledger\|prepared-not"` over `corpus/`, `tools/`, `SCORECARD.md`, `LOG.md` returns only prose about the *host mapping* dispatching prepared waves (e.g. `corpus/lessons/round-31.md:150`, `round-32.md:47`, `SCORECARD.md:1736`), never a ledger of them. Both mining rounds record it as not taken (`round-35.md:57`, `round-36.md:81`). |
| P4 | **no** | none | No attempts/restarts line or table anywhere: attempts exist only as section headings and prose — `LOG.md:1864` ("Round 29 attempt 2"), `1968`, `2021`, `2050`, `2082`, `2101`, `2128`, `2132`; `SCORECARD.md:1650`, `1709`, `1750`, `1779`; `corpus/lessons/round-36.md:3` ("attempt 2; attempt 1's L1 died on a provider-route failure"). No per-round attempt count, no reason class, no instrument. |

P1 caveat (observed): the criterion landed, the "small table of closure verdicts per axis per round next to the actual score" did not. `SCORECARD.md` §Round 35 (1940–1962) and §Round 36 (1964–2005) carry a per-claim row with `axis, score` = `calibration 7 → 7 (delta 0)` plus the sentence "Both scores are held"; `grep -niE "outside verdict|promoter"` over `SCORECARD.md` returns nothing, and the only file in the tree holding the word `promoter` is `QUALITY.md:316` (KQ44 itself).

## P3's named evidence — what is actually committed

### Round-32 wave 1 — prepared, never dispatched (proposal's claim holds)

- Spec path: `.ufo/waves/round-32/w1/spec.json`
- Seat count: **32** (`maxLanes: 32`, `items` length 32, `counts.spawn: 32` in `validate.json` and in `run-render.json`)
- Committing commit: `907cdcc0a76f8656fde4574c0a50725fcea42fa9` (2026-10-24 03:20:13 -0300), subject "round-32: wave-1 prepared (32 seats, policy v1 validator exit 0, build+attack for r33 candidates and r32 claim falsification) — NOT dispatched; orchestrator dispatches prepared waves"; six files added (spec, taskCall, validate.json, validate.err, run-render.json, run.err)
- `validate.err` is **0 bytes** (validator wrote no stderr); the `exit 0` claim exists only in the commit subject — no exit-code file (inference: the validator exit is asserted, not receipted)
- `out/` directory: **absent** (`ls -d .ufo/waves/round-32/w1/out` → "No such file or directory"). Zero of 32 seat artifacts. Still unrun at the 2026-10-25 tip.
- `run-render.json` is a dispatch payload render (`"schema": "ufo-swarm-wave-dispatch-v1"`, `"wave": null`), not evidence of a run.

### Round-33 wave 1 — the proposal's claim does NOT hold

- Spec path: `.ufo/waves/round-33/w1/spec.json`, **33** seats (`maxLanes: 33`, `items` 33, `counts.spawn: 33`)
- Committed at `4fdd4e66` ("round-33: freeze claims, controls, and prepared wave"); the spec's own context says "PREPARED, NOT DISPATCHED … Do not start until the orchestrator dispatches this exact wave."
- `corpus/lessons/round-33-verifier-spotcheck.md:70` (the closure's routed item 3 the proposal cites) records it as "Prepared-but-undispatched … `swarm-registry.json` carries no agent IDs … question is for the operator/orchestrator".
- Observed at the tip, contradictory: `.ufo/waves/round-33/w1/out/swarm-registry.json` has 33 members with **33/33 non-null `agentId`**, `createdAt 2026-10-24T06:52:20.558Z`, `updatedAt 2026-10-24T07:42:46.931Z` — i.e. the wave **was dispatched** at 06:52Z on 2026-10-24, roughly 2.5 h before the reflection pass.
- Seat artifacts under `out/`: 24 entries; **18 of the 33 seats** produced any artifact (15 `.md` reports plus 3 seat-named evidence directories: `ExecGateReplay-evidence`, `MutReceiptRevision-evidence`, `ReviewerC2Reproduction-evidence`). **15 seats silent**: ConnAuditBoundary, CriticC1Shortcut, CriticC2FakeReceipt, CriticClaimIndependence, CriticLineageWording, RevengerReceiptLineage, ReviewerC1KQ39, ReviewerC1Noop, ReviewerC2ReceiptSet, ReviewerFiledReport, ReviewerNoTrade, ReviewerSourceTier, ScoutScorecardAtWrite, ScribeMistakes, SentinelWriteScope.
- Why the closure's test failed (observed mechanism): `validate.json`'s embedded registry is the spec-time **template** — `.ufo/waves/round-33/w1/validate.json` `registry.path = .ufo/waves/round-33/w1/out/swarm-registry.json` with 33/33 `agentId: null`, exactly the pre-dispatch state. The dispatched registry that replaced it under `out/` carries the ids. So "carries no agent IDs" tested the template, not the run.
- Output commit lag: those `out/` files were first committed in `82886c28` ("round-35: scorecard, log, inherited-path disposition", 2026-10-24 21:28:08 -0300) — uncommitted for ~17 h while the 2026-10-24 pass ran; `SCORECARD.md:1934` calls them "the round-33 wave's late-arriving seat outputs".
- Correspondence: each report header names its wave ("# ConnSiblingScope — sibling-overlap scan (kama round 33, wave 1)"), and the 15 `.md` names are all members of the 33-item spec set.

### Also never run, and not named by the proposal (observed)

`.ufo/waves/round-31/w3/spec.json` — **32** seats (`maxLanes: 32`, 32 items), "WAVE 3 — PREPARED, NOT YET DISPATCHED", committed `c16fe3e5` (2026-10-24 02:41:32 -0300), no `out/` directory. The r32 wave-1 spec is its successor. A ledger built only from the proposal's two named rounds would miss it.

Wave census at the tip (specs with declared seats vs seat artifacts in their `reportDir`): round-27/w1-controls 37/0, round-31/w3 32/0, round-32/w1 32/0 → three prepared-never-run waves; round-33/w1 33/18 → partial.

## Proposed criterion text (P3 — still unimplemented)

Grounded in the two cases above: a spec's own context string says "PREPARED, NOT DISPATCHED" for a wave that ran, and a closure read a pre-dispatch registry template as proof of non-dispatch. Draft, KQ46 candidate:

> | KQ46 | A prepared wave's dispatch status is recorded in a ledger keyed by its spec path and declared seat count, and is re-derived from the wave's own report directory rather than from the spec's context text or its spec-time registry: `out/swarm-registry.json` with at least one non-null `agentId` is dispatch evidence, and the number of seat artifacts under the spec's `reportDir` is stated as a count — zero (never dispatched), fewer than the declared seats (partial, with both numbers), or equal (run). A spec committed with an absent or empty `reportDir` is listed as prepared-never-dispatched, naming the commit that committed it and the elapsed time at the tip. | The status is taken from a `PREPARED, NOT DISPATCHED` context string, from `validate.json`'s registry template (all `agentId: null` before dispatch), or from a validate exit alone; a partial wave is recorded as run; a wave whose outputs were committed a later round is dated by the committing round without naming the run date its registry timestamps carry. |

Falsifier the entry would have to survive (both sides, from committed bytes): for `.ufo/waves/round-32/w1/spec.json` the ledger must print `seats=32 artifacts=0 status=never-dispatched`; for `.ufo/waves/round-33/w1/spec.json` it must print `seats=33 artifacts=18 status=partial`, and a reader-side mutant that substitutes the validate-template check must flip the second to `never-dispatched` (the closure's actual error, `round-33-verifier-spotcheck.md:70`).

## Confidence

- P1/P2 dispositions and KQ ids: **high** — `QUALITY.md:316,322` plus both mining rounds' own statements.
- P3/P4 unimplemented: **high** — no row past KQ45, no artifact found by keyword sweep of `corpus/`, `tools/`, `SCORECARD.md`, `LOG.md`; both mining rounds say "not taken".
- Round-32/w1 never run: **high** — absent `out/`, no registry with ids, commit subject says NOT dispatched.
- Round-33/w1 dispatched and partial: **high** for "artifacts exist and registry ids are set"; **medium** for "produced inside the round-33 dispatch window" — the registry timestamps (06:52–07:42Z on 2026-10-24) place creation 2.5 h pre-reflection, but no per-seat start receipt was found.

## Remaining unknowns

- Whether any r32/w1 seat ran outside the lane (`out/` absent means no lane-side artifact, but a dispatch routed elsewhere would leave no lane trace).
- Why 15 of 33 r33 seats produced nothing (no seat-exit file analogous to round-36's `seat-exit-codes.json` was committed for that wave).
- The validator's numeric exit for r32/w1 — only the commit subject asserts 0; `validate.err` being empty is corroborating, not a receipt.

## Bounds honoured

Read-only `git log/show`, `read`, `grep`, and `python3` JSON parsing only; no edit to `considerthese/`, `QUALITY.md`, `MISSION.md`, `corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md`, lessons, or sibling trees; no git/jj mutation; no subagent spawned.
