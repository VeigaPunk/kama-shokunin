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

§Correction — round 17 (loading-gate scope, OPTIONS; routed by `lessons/round-16-verifier-spotcheck.md` defect 4).

Line 206's row says the llama.cpp loading gate answers "every non-frontend path 503 before the API key". At b11755 (704366d76) the gate exempts only the frontend set (`/` and embedded UI assets, `server-http.cpp:309-311`). OPTIONS requests return earlier, in the pre-routing handler at `server-http.cpp:347-352`, and are not 503'd. Every other path, including `/health` and `/v1/models`, gets the envelope while `is_ready` is false; the state gate (`:354`) runs before the API-key gate (`:357`). Envelope fields: message `:318`, type `:319`, code `:320`. Source: llama.cpp 704366d76 `tools/server/server-http.cpp`, accessed 2026-10-20.

## Round-17 graded fields and fail-capable live checks

| Entry | Covers | Round |
|---|---|---|
| `knowledge/llamacpp-loading-lifecycle.md` §Round 17 | the exact `/health` ready body in code (S042), the SIGINT/SIGTERM shutdown path and exit statuses (S043), Python returncode semantics (S044), three v2 live runs (S046); deepens the round-16 entry, no new ground | 17 |
| `lessons/round-17.md` | C1/C2 gate decisions, mined mistake M1 (S041 in-place edit) with the append-only guard, round-16 routed-defect and jj-risk dispositions | 17 |

Frontier disposition: "live grading of a loading server by the receipt" (round-16
paragraph above) is now held — receipt v2 grades every observed loading 503 body
(42–45 per run) and fails a run that observed none. Still open: router mode and
sleep, other engines, K05 declared-versus-served context, and the registered
consumers (still `DEAD`, not probed). No new coverage-map ground this round.

## Round-18 correction and loopback ownership

The round-17 coverage row at line 238 credits the SIGINT/SIGTERM path to S043
alone. **S047 supersedes S043's first-signal claim**: a post-install signal can be
overwritten by `start_loop()` resetting `running`; see the necessary-condition
scope and missing Gate row repaired in `lessons/round-18.md`. S043 still identifies
the registration and second-signal exit path; it is not a sufficient guarantee.

The v2 rule above, “fails a run that observed none”, is historical. V3 makes
zero observed loading 503s **not-evaluated** (tool 2; gate 3 / NOT-EVALUATED),
never pass and never an observed failure; another evaluated failure still wins.

| Entry | Covers | Round |
|---|---|---|
| `knowledge/loopback-listener-ownership.md` | newly held mechanism: Linux procfs socket-inode/child-fd ownership join; tcp6 host-word encoding of ::1 and mapped 127/8 (S048–S050); wildcard exclusion as harness policy | 18 |
| `knowledge/llamacpp-loading-lifecycle.md` §Round 18 | v3 tri-state receipt and schema floor, exact argv, loading-transition grading and retained control boundary; deepening, not another engine | 18 |
| `lessons/round-18.md` | R1–R7 dispositions, KQ23/KQ24, named-survivor calibration and falsification evidence | 18 |

Frontier advanced: loopback listener ownership mechanism (absent from the old
host census, whose attribution used privileged ss). Still open: other engines,
router/sleep mode, K05 declared-vs-served context and registered-consumer
reconciliation. No model-quality claim or consumer resampling occurred.

Round-18 source precision (falsify): S047 narrows **one first-signal ordering
path**, not every S043 observation. Handler install is server.cpp:534; task-loop
reset is server-queue.cpp:279. Between them the stop write can be overwritten,
leaving the server serving until a later signal follows the second-signal exit1
path. The ordinary post-start return0 path remains in code, subject to the
unexamined shutdown/locking assumptions; the lost-window consequence is static,
not reproduced. Health200/order alone did not exclude that window in the actual
runs; their recorded harness SIGTERM, no SIGKILL and returncode0 are the relevant
run evidence.

S056 supersedes S054's general duplicate-option wording: scalar port/host replace,
api-key/spec-type append, and spec-type is warning-exempt. Current exact argv is
lane policy in all cases. Four-pin VALID binds the launcher digest, not an
independent expected implementation-library digest; see the knowledge entry's
explicit consistent-swap limitation. New coverage remains ownership mechanism,
not full runtime attestation.

## Round-20 coverage — declared model identity and error evidence

| Entry | New held ground | Evidence |
|---|---|---|
| `knowledge/gguf-declared-identity.md` | offline declared GGUF architecture/context metadata versus captured per-slot and training-context fields | mined S058/S060; `tools/gguf-identity.py`; round-20 real-file oracle and malformed fixtures |
| `knowledge/error-is-not-a-verdict.md` | explicit distinction between a fail-closed subject error and credited mutation rejection; finite named regression repair | mined S061/S062/S064; S063 policy counterexample; `tools/error-verdict-census.py` |

Frontier advanced: offline model declarations now have an executable reader.
The old "declared-vs-served context is blocked" wording is narrowed: an old
fixture captures training2048 and served256, usable for historical comparison,
not a new live endpoint sample. K05 across real registered consumers, other
engines, loaded-weight authentication and model quality remain unclaimed.


## Round-22 deepening — helper errors are not smaller identities

`knowledge/llamacpp-loading-lifecycle.md` §Round-22 and
`lessons/round-22.md` distinguish the bare install helper's explicit I/O refusal
from the producer's already-existing install_links backstop. S075/S076 ground
the raised-operation signal; S077 rejects an access-only precheck.
`tests/llamacpp-live/install-io-grid.py` fixes the fault/control population and
compares frozen/current helper outcomes without a server or host permission
dependency. Successful encoding and historical receipt schema are preserved.

This repairs/deepens held identity ground, not a new knowledge/capability
surface. Frontier unchanged: external-system-library identity, receipt-header
minimization, historical crash-as-kill leaves, K05/other-engine serving, and
real registered-consumer reconciliation remain open. No new endpoint sample
or service restoration is asserted.

## Frontier disposition — round 23

Advanced (partially): **D4** report-audit repository trust. The auditor's
handling of repository-local git state is now a graded, mutant-checked grid
(26 fault, 4 contract and 13 control rows; frozen meets 0/26 faults, current
26/26; `lessons/round-23.md`), and `knowledge/error-is-not-a-verdict.md`
§Round-23 records the exit-class lesson. The 26 are not 26 independent
isolation wins: the falsify wave showed several rows pin current's own
refusal wording, and three were reclassified as contract changes. This is
not untrusted-repository safety: alternates and gitfile redirects
(O01/O02), the `--shared`-of-partial bypass, prefix-ambiguity overwrite,
duplicate Landed sections, errata CR splitting, an `--errata` FIFO, memory
ceilings, and the unisolated sibling tools `citation-provenance.py` and
`sources-append-only.py` stay open. Declared trade: a complete blobless
partial clone or paired promisor pack is refused where frozen gave a
verdict. Other frontier unchanged: external-system-library identity,
receipt-header minimization, historical crash-as-kill leaves,
K05/other-engine serving and real registered-consumer reconciliation. No
endpoint sample or service restoration is asserted.

## Frontier correction — round24

The round23 author quality-improved reading is superseded by outside
closure rounds[428]: operability and quality were harmed. A disclosed loss
of a correct runnable verdict is not an admissible trade.

D4 remains partial. Its promisor rule is now local-evidence-based:
metadata alone does not refuse a complete or locally sufficient repository;
actual unavailable required evidence does. A missing cited object already
referenced locally, or hidden behind an opaque dependency, is not a proved
absence. An unrelated historical blob does not become a completeness gate.
`lessons/round-24.md` and `knowledge/error-is-not-a-verdict.md` §Round24
explain the original/prospective oracle distinction and KQ35.

Correction to the previous paragraph's paired-marker wording: F23 is a
genuinely incomplete `--no-checkout` fixture, not the complete T01 witness.
The Git>=2.45 prerequisite remains open to operator disposition (R23-H2).
Other frontier unchanged: external-system-library identity, receipt-header
minimization, historical crash-as-kill leaves, K05/other-engine serving and
real registered-consumer reconciliation. No endpoint sample, service
restoration, new knowledge entry or new serving capability is asserted.

## Frontier correction — round24 (continuation)

Appended; the sections above stay as filed.

The round-23 claim rejected here is the one stated in the round-23 section
`## Frontier disposition — round 23`:

> Declared trade: a complete blobless partial clone or paired promisor pack is refused where frozen gave a verdict.

That trade is rejected, not carried: a disclosed loss of a correct runnable
verdict is not an admissible trade. The F23 sentence above corrects which
fixture witnesses that trade, not whether the trade is admissible.

The correction is local required availability. Promisor metadata alone does
not refuse a complete or locally sufficient repository; only evidence the
audit actually reads and cannot read locally is could-not-evaluate, with a
content-derived reason and never a guessed absence. Availability is judged
per required read, not over the whole store: no whole-store or
reachable-tree completeness precondition is introduced, and an unrelated
historical blob, an unselected branch or an unused file that is missing is
not a completeness gate. A missing cited object already referenced locally,
or hidden behind an opaque dependency, is not a proved absence.

The Git>=2.45 prerequisite remains open to operator disposition (R23-H2);
it is not closed here, no older-Git support is restored, and no approval of
the floor is claimed. No new frontier capability, no score promotion and no
admission claim are made here; no endpoint sample, service restoration or
new knowledge entry is asserted. Other frontier unchanged:
external-system-library identity, receipt-header minimization, historical
crash-as-kill leaves, K05/other-engine serving and real registered-consumer
reconciliation.

## Frontier advanced — round 25 (K05 declared versus served context)

| Entry | What it holds | Sources and evidence |
|---|---|---|
| `knowledge/context-capacity.md` | the KV pool versus the per-slot ceiling, fit raising an unset split context, the pool total bounding concurrent requests, and what the three endpoints cannot show, on the lane fixture (b11755, stories260K.gguf) | mined S106-S113 and S060; receipt `.ufo/waves/round-25/final/context-capacity-receipt.json`; `tools/kama-context-capacity.py` |

K05 is advanced on the lane-owned fixture only. Registered consumers, large
models (where free memory decides fit), other builds and other engines stay
open. The round-16 fixture scope is still pending L0 ratification; the L
cells used POST `/completion`, beyond the GET-only round-16 admission.

## Frontier disposition — round 26 (2026-10-23)

New core surface: SKILL.md "## Round-26 live error signatures" holds 17 live
llama-server b11755 error signatures with triggers, code meaning, next action
and sources S114-S130 (`registry/error-signatures-r26.json`; counter
`.ufo/waves/round-26/count-c1.py`). Frontier left open: router-mode model
errors (need a router launch), the confirmed but held-back signatures in
`lessons/round-26.md` §Gate, and the `--embeddings` server crash on
`/completion` seen once by a wave-1 seat (not yet reproduced by the lane).

## Frontier disposition — round 27 (2026-10-23)

| Entry | Covers | Round |
|---|---|---|
| `knowledge/echo-discriminating-counters.md` | method: an error-signature counter refuses JSON-decoded request echoes, credits one row per message frame and keeps the signature inside server-owned text; live b11755 echo at `server-common.cpp:1375` (S137), RFC 8259 §7 escapes (S136, S139) — not a new server error signature | 27 |

C1 (depth, new request-validation signatures) was not run on data and is a
miss. K05 beyond the lane fixture, router-mode model errors, other engines and
registered-consumer reconciliation remain open. X1 is exploratory; no
admission is claimed here.

## Frontier disposition — round 28 (2026-10-23)

New core surface: SKILL.md "## Round-28 request-field outcomes" — llama-server
b11755's request-field schema (`tools/server/server-schema.cpp` @704366d76) on
the lane fixture: hard-bound rejects, silent clamps and handler transforms for
`POST /completion` (registry `registry/request-field-outcomes-r28.json`,
sources S140-S173, counter `.ufo/waves/round-28/count-c1.py`). Before round 28
the surface was absent from PROVINCE.md and from every frontier list. Open:
the same fields through `/v1/chat/completions` and other endpoints, the
json_schema → grammar transform, launch-dependent bounds under other argv
(`n_parallel`), other builds and engines; K05 beyond the fixture and
registered-consumer reconciliation stay open.

## Coverage map — round 29 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/self-assessment-at-writing.md` | method: six checkable statement classes (P/H/N/C/T/Q) in SCORECARD.md/SHONEN.md each verified against the repo at the commit that wrote the line (`git blame --line-porcelain`, S174); calibration mismatch vs later drift distinguished (S175); frozen counter `.ufo/waves/round-29/count-c1.py`, sources S174-S177 — the lane's own self-assessment evidence record, not a serving/runtime surface | 29 |

## Frontier disposition — round 29 (2026-10-23)

No frontier row advanced and no core move: rounds 26-28 were rejected on
depth-claim shapes, so round 29 worked calibration (tied-lowest assigned axis)
on the self-assessment evidence record. The new knowledge entry rides the
calibration claim; the serving frontier stays as round 28 left it (chat
endpoint, json_schema → grammar, other argv/builds). Open calibration ground
named for round 30: the 72 extractor recall misses (2 false at W) and the
SCORECARD line-824 "5 cases" prose mismatch.

## Round-30 coverage — run agreement and the recall population

| Entry | New held ground | Evidence |
|---|---|---|
| `knowledge/instrument-run-agreement.md` | a lane capability: run one instrument N times over one tree, normalize only declared volatile fields, and report an agreement counter; the corpus guard refused as an agreement subject because its output embeds its own staging digest | `tools/instrument-agreement.py`; `.ufo/waves/round-30/c2/selftest.out` (`IA_SELFTEST pass=4 fail=0`), `receipt-a.json`, `receipt-b.json`; S178, S179 |
| SCORECARD §Round 30 | the round-29 census over its declared recall population: 72 previously-unseen statements classified at their writing revisions, the 2 that do not hold now carry observed values | `.ufo/waves/round-30/count-c1.py`; `c1/before/c1-base.out`; `final/c1-tip.out` |

Frontier disposition: round 29's disclosed recall gap (72 statements) is now a pinned population
with a per-item check, so the census's population is explicit rather than implied by the extractor.
Still open: the counter's extractor is unchanged (it still finds only 69 of the 141 by itself), so
a future statement outside both populations is invisible; the context-capacity frontier (K05)
remains operator-runtime dependent. No live endpoint was sampled this round.
