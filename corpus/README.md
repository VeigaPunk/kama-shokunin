# kama-shokunin corpus — index

Proprietary memory for the local model serving & endpoint health domain. Every entry
cites its source (`path:line` or a command + its raw output). Coverage map and open
gaps grow with rounds.

## Live authority vs historical census

Every `knowledge/` and `lessons/` entry is a **dated census record** of what was
observed on its citation date — never proof that an endpoint serves today. Live
authority is one current authorized `bash tools/kama-probe.sh check` run. As of
2026-10-15 the admitted truth (3 registry rows, 0 `MODEL_OK`, drift 3, exit 2;
all rows `DEAD`) and the supersession boundary for September-era identity
samples are recorded in `lessons/round-1-relaunch-freshness.md`.

**Actual round-5 correction:** `lessons/round-5.md` completes the local runbook
cutover and records the interrupted relaunch as inherited, unverified work.
Its real command captures live in `.ufo/round-5/` at the lane root; neither a
dated corpus nor a prior successful probe substitutes for a new sample.
Historical references to installed runtimes, counts, aliases and paths retain
their observation dates. New admissions and corrections follow `QUALITY.md`.
Round admission is blocked by missing native role routes and receipt bindings;
the local documentation improvement is not a completed training round.

## Coverage map

| Entry | Covers | Round |
|---|---|---|
| `knowledge/listener-census.md` | every loopback TCP listener on this host + its identity verdict | 1 |
| `knowledge/consumer-registry.md` | every config surface that pins a local model baseURL (port, model id, live verdict, owning lane) | 1 |
| `knowledge/endpoint-identity.md` | classification/health decision table: identity vs liveness, readiness signals, probe commands, thresholds | 1 |
| `knowledge/served-model-identity.md` | served-model reconciliation (`/v1/models` vs `--alias` vs configured id) + the minimal proof procedure | 1 |
| `knowledge/drift-timeline.md` | dated reconstruction of the 8080→34113 port move and why consumers never followed | 1 |
| `knowledge/cross-lane-scope.md` | consumer ownership vs sibling lanes, contested scope, handoff lines | 1 |
| `knowledge/alias-endpoint-normalization.md` | canonical alias→endpoint table; whether any dispatch alias can land on a loopback endpoint | 1 |
| `lessons/round-1.md` | round-1 lessons + carry-forward rules | 1 |
| `lessons/round-1-critic.md` | falsification attempt on the round's central claim | 1 |
| `lessons/round-1-citations.md` | independent verification of every frozen fact | 1 |
| `lessons/round-1-safety.md` | adversarial audit: secret leakage, scope/authority, trust boundary | 1 |
| `lessons/probe-mutation-matrix.md` | mutation classes the probe must detect + the classes it misses | 1 |
| `knowledge/snapshot-history.md` | invocation-to-invocation endpoint state, transition semantics, persistence boundary, scheduling handoff | 2 |
| `lessons/round-2.md` | freshness claim boundary, implementation/review traps, persistence threat model | 2 |
| `lessons/round-1-relaunch-freshness.md` | gate: 2026-10-15 endpoint teardown admitted as current runbook truth; September cases as dated historical samples | 1 (relaunch) |
| `lessons/round-4-recensus.md` | October teardown, stale-prose/source-anchor errata, missing round-3 report debt | 4 |
| `lessons/round-5.md` | current-vs-historical runbook cutover, measured admit/reject decisions, blocked dispatch and continuation | 5 (blocked attempt) |
| `QUALITY.md` | domain admission bar: current sample, pin provenance, temporal/source authority, invocation limits, ownership | 5 (blocked attempt) |
| `knowledge/free-tier-provider-limits.md` | free-tier provider load-test (rounds 6–17): per-round dispatch telemetry, failure classes, concurrency ceilings, inferred-TPS methodology | 6–17 (in progress; loop 1 final) |

## Known gaps

- **Operator-dependent (historical):** the stale pins in `~/.config/opencode/opencode.json:158`,
  `~/.config/opencode/agents/janitor.md:21`, and `~/.local/bin/the-janitor:19` were
  *detected and reported*, never rewritten by kama (operator-owned files). As of the
  2026-10-14 re-census all three files are deleted or emptied — see
  `knowledge/consumer-registry.md` §Errata; the drift resolved by deletion, not repoint.
- Invocation comparison is automated, but invocation cadence is not:
  `tools/kama-probe.sh snapshot` records dated state and deltas only when called.
  Installing/enabling a systemd user timer remains operator-owned.
- Windows/Podman-style runtimes absent from the census (single-host, Docker only).
- Real-runtime reconciliation is proven for llama.cpp only. vLLM/Ollama-shaped
  fixtures pass, but neither runtime is installed; this is parser evidence, not
  runtime integration.
- Historical declared-vs-served context size (September: 32768 vs 16384) is not in the snapshot schema; no current runtime context is established.
- No coverage of *remote* endpoint health (that is kake/kumitate territory).

## Frontier

- Correct still-live source anchors through new cited correction entries;
  historical corpus samples stay immutable. Round-4 debt is not erased by a
  current-state banner.
- Reconcile declared-vs-served context size only as a separate feature move
  when an authorized serving runtime permits a real comparison.
- Non-author spot-check of at least one admitted and one rejected candidate;
  unavailable in round 5, so discernment and promotion remain unverified.
- Operator/integrator prerequisites, not corpus expansion: authorized native
  role bindings, a real receipt binding, serving-runtime disposition and
  historical verified-round reconciliation. See lane-root
  `.ufo/round-5/continuation.md`; no outside-repo repair is absorbed here.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A50): `6–17 (in progress; loop 1 final)` at line 47 is stale (nl -ba corpus/knowledge/free-tier-provider-limits.md | sed -n '26,57p' => the status board has rounds 6-9 only, with loops 2-3 pending); current anchor: `corpus/knowledge/free-tier-provider-limits.md:26-57`]*

## Coverage map — round 10 additions (2026-10-19)

Appended rather than inserted, so no existing line moves (`QUALITY.md` KQ7).

| Entry | Covers | Round |
|---|---|---|
| `knowledge/runtime-health-surface-matrix.md` | cross-engine `/health` semantics (llama.cpp, vLLM, SGLang, Ollama) vs separate identity routes — documentation, revision-pinned, not local integration | 10 |
| `knowledge/serving-metrics-crosswalk.md` | local engine exporter flags, metric names and TTFT/TPOT/queue/cache boundaries (llama.cpp, vLLM, SGLang, OTel GenAI) — never identity evidence | 10 |
| `knowledge/gguf-runtime-compatibility-boundary.md` | GGUF naming is not an identity parser or support certificate; per-engine/per-hardware GGUF load and quantization paths | 10 |
| `SOURCES.md` | where kama learns: tiered, revision-anchored source registry, study paths, search log (contract v1) | 10 |
| `lessons/round-10.md` | mistakes mined (rounds 1–10), source gate, stale-anchor corrections, closed plan claim | 10 |

## Corrections — round 11 (reviewed 2026-10-20 UTC)

- The blanket “dated census record” description at lines 9–10 applies to the
  historical host samples, not the vendor/spec documentation entries added in
  round 10. Each entry's provenance states which kind of evidence it contains;
  neither kind proves a present local responder.
- The line-32 index description overstates `served-model-identity.md`. Its
  original bytes contain a historical readiness/metrics output fragment
  (`/health`, `/props`, `/slots`, `/metrics`), not alias reconciliation or a
  minimal identity-proof procedure. Round 11 appends explicit provenance and
  limits without rewriting the fragment.
- The round-5 missing-review/binding statements above describe that attempt.
  The external round-10 disposition is recorded, without modification, in
  `lessons/round-10-verifier-spotcheck.md`. It does not verify round 11.
- Round-11 C1 has a fixed denominator of nine legacy **knowledge** entries.
  The old SCORECARD plan's eighteen included lessons; the knowledge provenance
  requirement does not turn those historical lessons into knowledge entries.
  Metadata review dates are 2026-10-20 UTC; the steered round label is unchanged.

## Coverage map — round 11 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/served-identity-crosswalk.md` | Extends the pre-existing tags/ps distinction with remote inventory, expiry, alias/digest inference limits, llama.cpp nullable loading metadata and router-state boundaries; documentation only | 11 |

## Frontier disposition — round 11

K02's documented served-identity crosswalk is now held at the path above. It
does not establish Ollama runtime integration, a live responder, or context
capacity. K05 remains deferred until an authorized serving runtime exists.
Independent round-11 admit/reject review remains pending outside this lane.

## Round-12 evidence correction and frontier disposition (2026-10-20)

The outside round-11 disposition is now recorded at
`lessons/round-11-verifier-spotcheck.md`: ok / admitted true, bounded to
historical provenance and documentation. Its D1 identified an auxiliary frozen
SOURCES snapshot that matched its shipped digest but not the declared git blob.
Round 12 preserves that evidence and adds exact-source corrective evidence at
`../.ufo/waves/round-12/frozen/`, with separate integrity/correspondence checks
and fail-capable controls. The lesson is `lessons/round-12.md`.

This is calibration repair, not an additional knowledge entry, covered surface,
serving capability or endpoint sample. K02 remains held by
`knowledge/served-identity-crosswalk.md`; its round-12 supplement explicitly
labels the S031 locality consequence as inference and lane-registry supersession
as distinct from an upstream change. K05 remains operator-runtime dependent.
SOURCES navigation/date prose and SKILL's complete-applicable-criteria pointer
are corrected by explicit supplements. Outside round-12 sampling remains
separate from author-dispatched advice; no promotion box is newly certified.

## Round-13 criterion precision and frontier disposition (2026-10-20)

Outside round-12 review is now held at
`lessons/round-12-verifier-spotcheck.md`: ok / admitted true. Its D1 becomes
an appended KQ16 erratum in `QUALITY.md`, distinguishing stable finding IDs
from numeric exit classes and capture from independent blob comparison.
`lessons/round-13.md` records the mistake, sourced method and bounded
measurement. Existing criterion/receipt bytes remain historical evidence.

The previous quality verdict is grounded in round-12 D4's stronger
`knowledge/served-identity-crosswalk.md` interpretation, not merely the
snapshot checker. This round adds no knowledge entry, covered serving
surface, capability or runtime sample. K02 remains held; K05 context capacity
remains dependent on an authorized serving runtime. Current criterion repair
does not erase those limits or claim they have been rechecked.

## Round-14 executable evidence replay — capability, not integration

| Entry | Covers | Round |
|---|---|---|
| `knowledge/ollama-evidence-replay.md` | Runnable offline `/api/tags` and `/api/ps` capture reconciliation: exact selected names/digests, remote and malformed evidence, explicit unknown readiness; operational workflow newly held beyond the conceptual crosswalk | 14 |
| `lessons/round-14.md` | Fixed-corpus capability measurement, source/policy separation, historical outer-verdict/count clarification requested by outside round-13 D2 | 14 |

The conceptual available/running/remote distinction and candidate digest join
were already held in `knowledge/served-identity-crosswalk.md`; this is executable
repertoire, not newly discovered API semantics. Existing Ollama integration,
live context-capacity and service-restoration gaps remain open. K05 is still
operator-runtime dependent. Outside round-13 review admitted that bounded
criterion repair (`lessons/round-13-verifier-spotcheck.md`); its D2 is clarified
by appended round-14 prose, not by rewriting old receipts. This round still
needs its own independent non-author admit/reject sample.

## Round-15 executable corpus-guard repair — reliability, not repertoire growth

Outside `lessons/round-14-verifier-spotcheck.md` admitted the original unique
offline repertoire and routed R1 (minimum cardinality did not enforce
duplicate-name rejection) plus R2 (partial seat output versus terminal
provider failure). `lessons/round-15.md` learns both without rewriting
the old receipt or lesson.

`knowledge/ollama-evidence-replay.md` now carries a named correction and
`QUALITY.md` KQ18 requires a discriminating duplicate corpus above the
minimum-unique threshold, a positive unique control, real CLI invocation
and observable pre-child rejection. The current runner is repaired;
the baseline stays at `.ufo/waves/round-15/frozen/measure-before.py`.
Runnable evidence: `python3 tests/ollama-corpus-guard/check.py`.
The final measured revision/results are recorded in the round15 lesson.

No new knowledge entry, API surface or capability row is added. Expansion
is unchanged; the operational correction is not rediscovered tags/ps
semantics. Existing live integration, context-capacity and service-
restoration frontier gaps remain open. No authorized serving runtime was
sampled or restored. New own-work S034 supports the actual guard diagnosis;
S012 remains a separate loaded-metadata boundary, not a readiness test.

## Round-16 loading-envelope verdict and live llama.cpp lifecycle

| Entry | Covers | Round |
|---|---|---|
| `knowledge/llamacpp-loading-lifecycle.md` | llama.cpp b11755 loading gate in code (every non-frontend path 503 before the API key), single-model versus router readiness, the probe's `MODEL_LOADING` mapping and limits, one live lane-owned run | 16 |
| `lessons/round-16.md` | C1/C2 gate decisions, mined mistake M1 (round-1 overreach), round-15 routed-defect dispositions | 16 |

The `/health` 503 body was already held at `knowledge/runtime-health-surface-matrix.md:14`
(round 10); credit here is the code path onto `/v1/models`, the corrected
probe verdict and the live capability, not the body itself. Appended
corrections for the vocabulary and the loading state: `endpoint-identity.md`,
`consumer-registry.md`, `listener-census.md`, `served-identity-crosswalk.md`,
`runtime-health-surface-matrix.md`; plus `snapshot-history.md` (harness count)
and `ollama-evidence-replay.md` (round-15 routed defect 5).

Frontier disposition: the gap "real-runtime proof exists for llama.cpp only, and
the last sample is stale" (lines 60-62) now has a re-runnable lane-owned sample
on the current build. Still open: live grading of a loading server by the
receipt (the tiny model loads in a few milliseconds; see the round-16 lesson for
what the falsify wave captured), router mode and sleep (source reads only), other
engines (source reads only), K05 declared-versus-served context, and the
registered consumers, which stay `DEAD` and were not probed. A lane-owned
fixture was sampled; nothing was restored.

Line 119's "llama.cpp nullable loading metadata" names a README sentence that
the direct-mode code does not serve; see `served-identity-crosswalk.md`
§Correction — round 16.
