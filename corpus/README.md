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

## Coverage map — round 31 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/chat-adapter-outcomes.md` | the `POST /v1/chat/completions` conversion layer on b11755: alias resolution through the schema, the adapter's own validation messages and the 400/500 split, `logprobs` → `n_probs`, undeclared OpenAI-standard keys copied then pruned, and the observability boundary of `/slots`; 19 live rows in `registry/chat-param-outcomes-r31.json` | 31 |
| SKILL.md §Round-31 chat-completions parameter outcomes | the counted table (19 rows, 18 counted at the landed tip), each with a pinned `server-common.cpp` / `server-schema.cpp` line and the exact live outcome; the four outcome classes and their limits | 31 |

## Frontier disposition — round 31 (2026-10-23)

Advanced: the chat-completions adapter surface named by round 28's frontier is now
held in the committed corpus (19 measured rows, 13 pinned source rows S180-S192), and
the `/v1` conversion layer is listed as a PROVINCE surface. Still open: the
`json_schema`/`response_format` → grammar transform as a compiled-grammar row
(`/slots` does not expose session grammar), the same fields through `/v1/completions`,
`n_cmpl`'s launch-dependent bound, other builds and engines, K05 beyond the lane
fixture, and registered-consumer reconciliation.

Both round-31 claims land as honest non-admissions: C1's frozen counter is met at the
landed tip but a do-nothing registry of twelve duplicate rows also meets it
(`.ufo/waves/round-31/controls/`), and C2's frozen predicate is unreachable because its
correction key is not unique in its population. The counters are frozen bytes; the fixes
are routed to round 32.

*Appended correction, round 31 attempt 2 (2026-10-23).* Three counts in the paragraphs
above are wrong and the no-op citation points at the wrong directory. Measured at tip
`addeb57c`: `registry/chat-param-outcomes-r31.json` holds **18** rows (not 19; K31-14 was
dropped by the remap at `54c6f4fe`), the SKILL table has **18** rows of which **17** count
(`count-c1.py` → `registered 18 counted 17`), and the opened source rows are **S180-S191**
(12 rows, not 13, and no S192 exists). The no-op shortcut evidence is
`.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json` and, independently reproduced,
`.ufo/waves/round-31/w2/out/CriticNoop/` (`registered 12 counted 12 target 12 met True`);
the `controls/` directory holds the twelve-arm pre-data control call, not the no-op.
C2's predicate is better described as non-injective than unreachable: one collapsed
correction flips `met` False→True while two dispositions stay uncorrected
(`w2/out/MutC2Key/`), which is worse than unreachable. `rows 30` is the counter's correct
population; attempt 1's SCORECARD C2 cell says 28 and cites an absent
`.ufo/waves/round-31/c2/c2-tip.json` (the receipts are `c2-b4f3edc0.json` and
`c2-bda324bb.json`).

## Round-32 disposition — instrument repairs, no new knowledge ground

The round-32 claims are lane-internal instrument repairs: the round-qualified claim-row
counter `.ufo/waves/round-32/count-c2r.py` (calibration) and the meaning-grading
instrument-registry gate `tools/gate-registry-check.py` v2 (operability; S193). The gate's
repair exposed two prose-only registrations now fixed by SKILL's round-32 registry block.
No `knowledge/` entry is added and no coverage-map ground moves; the serving frontier
(`response_format`/`json_schema` → grammar via S192, `/v1/completions`, other engines,
K05) is unchanged and is carried by the prepared wave under `.ufo/waves/round-32/w1/`.
The round-31 errata above about `rows 30` and the absent `c2-tip.json` stand; the
round-32 section of SCORECARD records the reconciliations (RefRepair pointer, w2 seat
census) routed by the round-31 closure.

## Round-33 disposition — receipt lineage and gate evidence

The round-32 report's c2r lineage sentence, three stale v2 control filenames,
S193 quote location/count, and gate-receipt metadata are corrected by
append-only records in `corpus/lessons/round-33.md` and `SCORECARD.md`.
S194 is a scoped own-work source correction for the gate's exact docstring
anchor; it does not add a `knowledge/` entry or serving surface. The first
round-33 gate capture exposed an extra `missing-path` in its synthetic
empty-exit-map fixture; the committed diagnostic preserves that output and
the corrected fixture is isolated in the final replay set. No knowledge
coverage-map ground or endpoint sample advanced. The serving frontier remains
as recorded by round 32: `response_format`/`json_schema` grammar, `/v1/completions`,
other engines, K05, and registered-consumer reconciliation.

## Coverage map — round 35 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/endpoint-health-probe-conventions.md` | a vLLM HTTP 503 can be an admission rejection, distinct from a dead endpoint and from llama.cpp loading 503 | 35 |

## Round-35 correction of the round-34 map sentence

The filed round-34 report says the coverage map gains `serving-alias-contract.md` and `served-model-id-resolution.md`. At `719655f12517a9ce6b1a5ca44316897fed8420b0` those names are absent from this file. That sentence is false. It is not rewritten. The two names are recorded here as round-35 pointers, which does not make the round-34 sentence true.

| Entry | Covers | Round |
|---|---|---|
| `knowledge/serving-alias-contract.md` | served-name and alias resolution; absent from this map at the round-34 tip | 35 |
| `knowledge/served-model-id-resolution.md` | served model id read from a local OpenAI-compatible listing; absent from this map at the round-34 tip | 35 |

## Coverage map — round 36 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/sglang-native-route-deprecation.md` | at tag v0.5.22 the published SGLang native route list still names `/get_model_info` while the engine's own handler warns that the route is deprecated and names `/model_info` as the replacement | 36 |

The frontier step of round 36 is the corpus-expansion-1 package under
`/home/vgpnk/Projects/shokuknow`, read only. One theme, one entry, two registry
rows: S328 and S329, both opened on 2026-10-24 by this lane and re-opened by
wave-2 seats. The package's staged ids (S325 to S458) collided with this lane's
own registry on S327; the adopted ids follow the lane's registry, and no
adopted row re-points a staged citation by arithmetic. Quarantine verdicts for
the seven kama rows of the campaign absent-defect register, the rejects with
their flip conditions, and the id-collision record are in
`corpus/lessons/round-36.md`.

## Coverage map — round 37 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/kv-cache-reclamation-models.md` | vLLM V1's per-request token budget spans prompt and output with chunked prefill on by default; SGLang's radix tree evicts only evictable leaves by lowest score, and a session reference is soft protection, not a memory pin | 37 |
| `knowledge/prefix-cache-reuse-models.md` | vLLM hashes each kv-cache block by its own tokens plus its prefix ancestry, caches only full blocks, and advises SHA256 for multi-tenant use; reuse requires an exact full-block prefix match | 37 |
| `knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md` | the hashing default changed at v0.11: sha256 is now the default and is selectable via --prefix-caching-hash-algo, so the v0.9.0 collision caveat is historical | 37 |

The frontier step of round 37 is the corpus-expansion-1 package under
`/home/vgpnk/Projects/shokuknow`, read only. One theme, three entries, seven
registry rows: S330, S333, S334, S335, S346, S347 and S363, all opened on
2026-10-25 by this lane and re-opened by wave-1 seats. The adopted ids follow
the lane's registry; no adopted row re-points a staged citation by arithmetic.
Quarantine verdicts, rejects with flip conditions, and the id-collision record
are in `corpus/lessons/round-37.md`.

## Coverage map — round 38 addition

| Entry | Covers | Round |
|---|---|---|
| `corpus/knowledge/sglang-docs-version-pinning.md` | the published SGLang docs pages carry no version marker; their sources are contained unchanged in release tag v0.5.22, so content can be anchored to a released version rather than a branch commit | 38 |
| `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md` | v0.5.22 is the highest release tag (git ls-remote --tags), so the release pin is also the current release; the GitHub REST API rate-limit is bypassed by the read-only git protocol | 38 |

The frontier step of round 38 is the corpus-expansion-1 package under
`/home/vgpnk/Projects/shokuknow`, read only. One theme, two admitted entries,
three registry rows: S352, S353 (admitted) and S472 (own-work, verifies the
tag inventory via git ls-remote). Staged row S360 (GitHub tags API) is
rejected: the API is rate-limited at HTTP 403 on this host, and the lane's own
reproducible git ls-remote row supersedes it. Quarantine verdicts, rejects
with flip conditions, and the id-collision record are in
`corpus/lessons/round-38.md`.

## Coverage map — round 39 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` | OpenAI model-card `created` is creation-time catalog metadata rather than local served-artifact identity; S473 | 39 |

## Frontier disposition — round 39

The OpenAI model-list `created` field is catalog creation-time metadata rather than a local serving-identity signal. The distinction is held in `knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` (S473). No registered endpoint or live runtime was sampled; serving/runtime gaps remain open.

The row was staged by attempt 1 as S472, which round 38 already holds for the SGLang tag inventory; attempt 2 renumbered it to S473 by document and re-pointed every live citation. Attempt-1 receipts under `.ufo/waves/round-39/assimilation/` keep the old id and are superseded, not edited; the replay receipts are `claim-after-replay.out`, `census-replay.out` and `renumber-map.md`.

## Coverage map — round 41 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/engine-pin-watch.md` | Newer-release triggers for version-pinned entries: release-tag listing with `git ls-remote --tags`, peeled `^{}` lines skipped, numeric version order; per-pin status for SGLang v0.5.22, vLLM v0.32.0 and llama.cpp b11755; S475, S476, S477 | 41 |

## Frontier disposition — round 41

Advanced: newer-release triggers for row-backed version pins. `tools/pin-watch.py` over `registry/engine-pins.tsv` gave this result at 2026-10-25T20:03Z: SGLang v0.5.22 current, vLLM v0.32.0 current, llama.cpp b11755 behind by 115 builds (newest b11887). Entry: `knowledge/engine-pin-watch.md` (S475, S476, S477).

Still frontier:
- Whether the llama.cpp server surfaces the b11755 entries describe changed by b11887 (S038 recheck trigger). The L1 has not verified this. Seat R41F09 read the b11755→b11887 server sources and reports the `/health` loading envelope, the `Loading model` text and `/v1/models` handling unchanged (`.ufo/waves/round-41/w1/out/R41F09.md`). That reading is a lead, not an admitted entry.
- Four engine versions cited from round-16 lead files with no registry row: Ollama v0.40.6, TGI v3.3.7, KoboldCpp 1.123.1, LocalAI v4.11.0. They are not watched until a sourced row backs them.
- Entries pinned to older vLLM docs lines (v0.9.0, v0.17.0, v0.19.1, v0.25.0). They are not watched as separate pins.

No endpoint was sampled and no serving runtime was started. Registered consumers still sample DEAD, and that stays operator-owned.

## Coverage map — round 42 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/context-capacity-engine-sides.md` (`corpus/knowledge/context-capacity-engine-sides.md`) | Engine-side half of declared versus served context capacity (K05), as source readings: vLLM v0.32.0 derives its served KV-cache token figure from the block pool and `max_model_len` and prints it beside the declared length on one startup log line; llama.cpp 704366d7's router model listing publishes the declared training context as `context_length` (not `max_model_len`); S478, S479 | 42 |

## Frontier disposition — round 42

Advanced: the engine-side sources for K05 (vLLM, llama.cpp router listing), as source readings only. K05 itself stays runtime-blocked: the served side on a registered endpoint needs an authorised serving runtime, and no endpoint was sampled this round.

Still frontier:
- SGLang, Ollama, TGI and the llama.cpp single-model `/v1/models` body for the declared and served capacity (the staged round-8 and round-11 context-capacity amendments name llama-cpp-python settings and an own-work receipt, both refused this round with flips in `lessons/round-42.md` §Gate).
- Cross-check of S-ids named in lesson prose against the rows they name (`considerthese/2026-10-25.md` proposal 1, second half); round 42's `tools/digest-ledger.py` covers digests only.

Correction to the `## Frontier` list above (seat R42A11, round-42 wave): its third bullet says "discernment and promotion remain unverified" because a non-author spot-check was "unavailable in round 5". That is stale for discernment: 28 outside closures are committed (`python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → 28 at the round-42 tip) and `lessons/round-41-verifier-spotcheck.md` §4 samples one admitted and one rejected candidate. Promotion stays unverified: `SHONEN.md` holds four `[~]` boxes and no named non-author verifier. The bullet above is left as written (append-only).


## Coverage map — round 43 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/runtime-health-surface-processes.md` (`corpus/knowledge/runtime-health-surface-processes.md`) | Which vLLM process answers `/health`: the v0.31.0 release notes list a `/health` endpoint and a readiness wait under "Fast restart" (`vllm preload`, the weight cache daemon), and pull request 58552 states the endpoint was added to the weight cache daemon parent process with `starting`, `ready` and `failed` states — a different process from the inference server whose one `/health` route the lane already holds (S004); S480, S481 | 43 |

## Frontier disposition — round 43

Advanced: the process map of vLLM's `/health` surface. The endpoint the v0.31.0 release notes announce is the weight cache daemon's (`vllm preload`), not the inference server's; the pull request behind it names the three states and the reason for them, "distinguish daemon startup from readiness". Entry: `knowledge/runtime-health-surface-processes.md` (S480, S481).

Still frontier:
- K05 (declared versus served context capacity): the served side on a registered endpoint still needs an authorised serving runtime. No endpoint was sampled this round; round 42's engine-side source readings (`knowledge/context-capacity-engine-sides.md`, S478, S479) stand and nothing here widens them.
- Where the endpoint is served from today. The pull request's own commit list carries "Move daemon health endpoint to preload CLI" and the diff registers the route in `vllm/entrypoints/cli/preload.py` (S481); the entry reads that diff, not the merged file at the v0.31.0 tag, so a later move is outside it.
- Shipped readiness for the inference server: pull requests 46811 and 59179 remain open proposals, and the shipped server route set is still the single `/health` of S004.

No endpoint was sampled, no serving runtime was started, and registered consumers still sample DEAD; that stays operator-owned.


## Frontier disposition — round 44

Advanced: release freshness of the llama.cpp-pinned ground. The 91 `on-release` rows pinned to a llama.cpp commit were re-verified at release b11889 (S482) and all still hold there (`registry/release-recheck-b11889.tsv`); the `server.cpp` entrypoint refactor (commit f3269ef96) moved three rows' anchors without changing their statements. One statement outside that population is now b11755-only (`SKILL.md` §Round-28, `dry_sequence_breakers`).

Still frontier:
- Rows that depend on the b11755 pin but sit outside the round-44 population: S038, S477, the own-work live receipts S041/S046/S055, and the `ggml-org/ggml` rows S014/S058 (lesson §Gate). The installed runtime is still b11755; b11889 verdicts say nothing about endpoint behaviour on this host.
- Other pinned projects (seat U9Pins, `.ufo/waves/round-44/w1/out/U9Pins/pins.tsv`): S010, S019 and S048 changed upstream; S013 and S022 likely changed.

No endpoint was sampled and no serving runtime was started this round.

## Frontier disposition — round 45

Re-verified this round (`registry/recheck-r45.tsv`): S010, S014, S019, S048 (two files), S058 against current upstream, S041/S046/S055 by live b11889 runs (S484, S485), S038 and S477. Still frontier: S013, S022, the Python/man7/jj/llm-d/pytest series rows, the unpinned vLLM pages S002–S004, and llama.cpp releases after b11889 (b11897 at the 2026-10-26 ls-remote).

## Frontier disposition — round 46

Re-verified this round (`registry/release-recheck-b11906.tsv`): the 91 `on-release` rows of
`corpus/SOURCES.md` pinned to a `ggml-org/llama.cpp` file at a commit (the round-44 population,
unchanged at base `0163fea2`) were re-checked at release b11906 =
`4d71b42fd87db24b8b7c808c151b713aa4459cfd`, 17 commits after b11889
(`git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-list --count
d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd` →
`17`): unchanged-file 6, holds 81, holds-reworded 4, drifted 0, removed 0 (S121 filed `holds-reworded` on its full anchored range after critic K1R07; lesson §Gate). 73 rows sit on
files byte-identical between the two releases (`git rev-parse <rev>:<path>` at b11889 and
b11906): 6 of them are the pin-equals-release rows S015, S059, S106, S128, S129, S131 and 67
carry their b11889 reading to the same bytes; the three `holds-reworded` rows are S037, S043
and S108 on the byte-identical `server.cpp` and keep their b11889 pin-only/release-only
witnesses. The 18 rows whose file changed are 17 on `tools/server/server-context.cpp` (S042,
S060, S109, S114–S125, S133, S138) and S479 on `tools/server/server-models.cpp`; every hunk
of the one commit that touches these files between the releases (c6fb3b5be, "mtmd: add
mtmd_helper_get_capabilities", net +3 lines, 6 hunks) lies outside every pinned range, so each anchored range is text-equal at
b11906 after the +3 shift and S479's ranges are unshifted — no row drifted, no row was
removed, and no used-by entry needs a flag. One note-level citation is stale wording, not a
claim: S125's b11889 note still quotes `chat_params.allow_audio` as the pre-refactor
expression; the b11906 row cites 1712/1401 and the statement stands. b11906 is registered as a
source opened this round (release identity row, S486 as drafted) and
`corpus/SOURCES.md` §Round-46 release re-verification carries the population, the release and
the machine-witness rule.

The same official binary was re-run on the unchanged stories260K fixture with the unchanged
harness (`tools/kama-llamacpp-live.py` sha256 `8c0dbb2b…`): three `kama-llamacpp-live/v3`
receipts, each 11/11 checks, `build_info b11906-4d71b42fd`, ready `/health` body exactly
`{"status":"ok"}`, every loading 503 the exact envelope, `/metrics` 501, one SIGTERM with
`returncode 0`, `sigkill_sent false` (row S487 as drafted; a second, install-independent
replication reports the same). So the lifecycle propositions S041, S046 and S055 assert hold
unchanged 17 commits later; S485's b11889 receipts stay the b11889 sample, and the b11906
receipts are a new sample of the same instrument at a new build, not a re-verification of
S485's bytes. The boundary is unchanged: these are unregistered loopback ports at sampled
instants, not registered-consumer health; no registered endpoint was sampled this round, and
their last admitted sample (2026-10-15: 3 rows, all `DEAD`) is not re-opened by it.

Still frontier:
- S013 (Ollama importing a model): the live page still teaches the row, but the cited
  revision contradicts it — `docs/import.md` is 404 at `6d02a43a` (the page became
  `docs/import.mdx` in that commit), so the row needs a re-pin, not a re-read; proposed pin
  `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (blob `8a8778ce`, equal to `main` at the sample).
- S022 and the unpinned vLLM stable pages S002–S004: all four teaches hold on today's live
  pages (footer dates still match the rows; S022's stable alias is now dated 2026-09-16 and
  adds Responses API and spec-decode acceptance sections without contradicting the row), but
  they remain frontier because the anchor is a floating `stable` alias and S022 is still
  `queued` with no used-by — no revision pin, no release trigger.
- The floating-series rows: 178 rows carry `on-release`; 91 are the llama.cpp population
  above, 5 are llama.cpp release/receipt rows (S026, S038, S482, S484, S485) and 82 cite
  other sources — 66 documentation pages, mostly anchored to a floating `stable`, `latest`,
  `main` or version-less address or a dated page footer (the Python 3.14, git-scm, man7, jj,
  pytest, llm-d and Ollama/vLLM/SGLang doc series), 3 spec rows (S014, S019, S058), 9
  code-file rows pinned to tags or commits outside llama.cpp, and the lane's own instrument
  rows; 7 of the 82 are rejected and 5 queued. They change on a docs deploy or a tag outside
  the llama.cpp feed, not on a llama.cpp release, so only a live page read dates them — the
  round-46 read holds S002–S004 and S022. The two `ggml-org/ggml` spec rows S014 and S058 were
  re-verified at their pins in round 45.
- Rows that cite llama.cpp but fall outside the population rule (the rule selects exactly 91;
  the llama.cpp-citing rows outside it are exactly 10): S026 (PR #18001, rejected) and S028 (issue #4746, rejected) are untouched
  by 17 commits — `git grep 'v1/metrics' 4d71b42f` still exits 1; S038, S482 and S484 are
  release-asset identity rows and b11906 says nothing about the b11755/b11889 bytes they
  name; S041, S046, S055 and S485 are historical receipts, now backed by the b11906 run
  rather than re-verified by it; S477's tag-inventory figure is stale — it records the highest
  `bN` tag as b11887 and 115 tags above b11755 at 2026-10-25T20:03Z, while the b11906 clone
  re-derives 130 and `git ls-remote --tags` at 2026-10-26T19:57:59Z lists b11907 as the
  highest (7,461 `bN` tags; 1 above b11906), and its 30d recheck is not due until 2026-11-24.
  The release identity the population assumes is a counter constant, not a re-derived fact
  (`RELEASE_COMMIT` is never checked against `git rev-parse b11906^{commit}`), so a
  tag-versus-constant guard is the next counter's work; today they agree.
- Next release trigger: the next `bN` tag above b11906. b11907 =
  `4b851fbee8867136a0c561c8a3521f2fe7d53252` was already tagged at the sample, but
  `releases/tags/b11907` answered 404 — a tag runs ahead of its release by hours, and an
  asset-digest row such as S038/S484 cannot cite it until the release lands. The lane's own
  pin is still b11755 (`registry/engine-pins.tsv`), which `tools/pin-watch.py check` reports as
  `engine=llama.cpp pin=b11755 newest=b11907 newer=131 status=behind` (exit 1), so the
  on-release trigger has been live for many builds. llama.cpp also publishes a semver stream:
  `releases/latest` returns v0.7.0 = commit `620d2225` = the b11669 commit, 86 commits behind
  b11755 and 237 behind b11906, and every `bN` release is a prerelease, so `releases/latest`
  is not a freshness oracle; v0.8.0 (a ~10-day milestone, none tagged at the sample) is a
  coarse second axis, never a replacement for the `bN` row.
- K05 (declared versus served context capacity): still no authorised registered-endpoint
  sample; this round's run is an unregistered fixture at `--ctx 256`, which the
  context-capacity rows' scope already excludes.
- Round-45 D1 (KQ65 hand-read sample for a future claim-outcome reader): the hand-read sample
  control is being produced this round (hand labels on both sides, byte-verified against each
  cited revision) and no reader is frozen, so the deferred item stays open.

Append-only self-description is now audited, not assumed: `tools/append-only-audit.py` (round-46
C2, capability table row `append-only-audit`) sets the five files the lane treats as
append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)
against its git history and exits 1 on a partial or unrestored mass deletion. At
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` it reports `commits=294 events=5 restored=3
partial=2 unrestored=0` (exit 1): 0718b6ab truncated LOG.md, corpus/QUALITY.md and
corpus/README.md and 82b5e9d3 restored them byte-exactly; the two SCORECARD events are the
head re-derivations the file itself documents (`SCORECARD.md:6`: the head sections are
re-derived from the tree by `tools/round42-selfdesc-reconcile.py`) — 0718b6ab deleted 2417
lines and 2416 are back at the audit revision, dd9f5dc6 deleted 31 and 24 are back — so the
exit-1 is a signal to read, not a loss. What stays
frontier is the instrument's edge: the 20-line threshold hides smaller deletions by design and
the default five-file set is the tool's, not yet the lane's full declared contract.

## Frontier disposition — round 47

Two claims were built at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (freeze
`bbcc6dc2`, base `172b8ad0`): append-only-audit v2 with a declared contract (C1,
calibration) and live receipts that a fresh session can replay (C2, operability). The
figures below are measured at that build commit; the capability rows, the scorecard
sections and the b11909 registry row are integration work, not part of this commit, and
are not pre-empted here.

**What is now audited.** `tools/append-only-audit.py` (schema `append-only-audit/v2`)
reads its file set from `registry/append-only-contract.tsv`, whose seven rows each name
the lane line that declares the rule: `LOG.md` (`README.md:16`), `SCORECARD.md`
(`corpus/README.md:521`), `corpus/QUALITY.md` (`corpus/QUALITY.md:24`), `corpus/README.md`
(`corpus/README.md:86`), `corpus/SOURCES.md` (`SKILL.md:578`), `corpus/lessons/*.md`
(`corpus/lessons/round-23.md:100`) and `registry/history/DELTA.md`
(`registry/history/DELTA.md:3`). At `3a09a1d9` that contract expands to 85 files — the
five self-description files, 79 lesson files and `DELTA.md` — over 303 commits.
`python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9` reports
`commits=303 files=85 events=5 restored=3 partial=2 unrestored=0`, exit 1; its selftest
is `AOA_SELFTEST pass=15 fail=0` at the build and `pass=19 fail=0` after the wave's hardening
(lesson §Wave). Three things changed from v1. Deleted counts are the
numbers `git diff --numstat --no-renames 0718b6ab^1 0718b6ab` prints — 2292 `LOG.md`,
2421 `SCORECARD.md`, 375 `corpus/QUALITY.md`, 663 `corpus/README.md` — where v1 read
2290 and 2417 because it dropped every deleted line starting with `--` (round-46 closure
D1). Lines compare byte-exact, CRLF and a missing final newline included, and restoration
is a multiset measure maximised over the event's own window (D2): `82b5e9d3` restored
`LOG.md`, `corpus/QUALITY.md` and `corpus/README.md` exactly, and the two `SCORECARD.md`
events read 2420/2421 and 24/31 at `172b8ad0` *and* at `3a09a1d9`, so the tip moving no
longer lowers a restoration (the round-46 spot-check measured v1 falling 2416→2409 on a
head re-anchor). `corpus/lessons/` (79 files, previously unguarded) is inside the audited
set. The round-47 counter recomputes every field on its own code path and reads
`selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0
fixture_mismatch=0 met=True`.

**What is still not audited.** The audit is file-scoped: the tool expands each contract
row's path pattern and never reads its `rule`, `declared_at` or `note` cell
(`tools/append-only-audit.py:184`), so the contract's prose is documentation, and the
declaring-line check lives only in the round-47 counter. Three consequences. (1) The
`SCORECARD.md` carve-out is declared but not applied: the contract row says the head
sections named at `SCORECARD.md:6` are re-derived in place and a head re-anchor is an
expected partial, yet the two partial events above are indistinguishable from a real
loss of 7 and 1 lines — the exit 1 is a signal to read the contract row, not a verdict.
(2) Only one knowledge file's heading calls its errata region append-only —
`corpus/knowledge/consumer-registry.md:30` (`## Errata — 2026-10-14 re-census
(append-only; rows below keep their round-1 text)`); `corpus/knowledge/context-capacity.md:245`
(`## Errata — round 26`) carries the same semantics without the word ("the round-25
wording above stays") — and no contract row covers `corpus/knowledge/*.md`; whole-file
inclusion would be wrong because the body of those entries is a dated census that may be
edited, so the region needs its own scoping before it can be audited. (3) The 20-line
threshold is a policy, not the rule: at `--threshold 1` the same tip reports 91 events —
12 restored, 8 partial, 71 unrestored —
26 in `SCORECARD.md`, 20 in `corpus/SOURCES.md`, 13 in `LOG.md`, 8 in `corpus/README.md`
and 26 across 15 lesson files, so deletions below 20 lines in files the lane calls
append-only are unwatched. `corpus/SOURCES.md` is declared `A-row`, whose mutable cells
(`status`, `recheck`, `used-by`) are enforced by `tools/sources-append-only.py`
(`SKILL.md:578`, `--selftest` 42/42), not by this audit.

**Live receipts that replay.** The three b11909 receipts
(`.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`) are `kama-llamacpp-live/v4`: each
records an `outcome` of pass with 11/11 evaluated checks on unregistered loopback ports
37903, 44883 and 39739 (alias `kama-r47-live`, `--ctx 256`, `-t 1`), `build_info
b11909-caa8191df`, ready body `{"status":"ok"}`, `/metrics` 501, one graceful SIGTERM
with `returncode 0`, and a `provenance` block that names where each input came from —
the release asset `llama-b11909-bin-ubuntu-x64.tar.gz` at its URL with sha256
`bf94332a…8695b` and archive member `llama-b11909/llama-server`, and the model
`stories260K.gguf` at `https://huggingface.co/…` with sha256 `270cba1b…bd256d` — so a
replay no longer depends on the host cache paths the same receipts still record
(`server.realpath`, `model.path`), and `teardown.log_path` is null because the temp log is
deleted, its kept lines inlined in `teardown.log_lines`. `tools/kama-live-replay.py`
re-acquires both recorded URLs into `--work`, verifies each sha256 *before* anything is
extracted or executed, re-runs the lifecycle with the receipt's alias, ctx and threads and
compares check by
check, and refuses a receipt whose recorded digest is wrong (`KLR_SELFTEST pass=10
fail=0` at the build, `pass=12 fail=0` after the wave's hardening). The round-47 C2 counter at `3a09a1d9` reads `receipts=1 replay=1 tamper=1
newrow=0 rerun_checks=11 met=False` (exit 1): the replay runs from `git archive` under a
fresh `HOME`, reproduces all 11 checks, both tampered copies are refused, and the only
unmet leg is the `corpus/SOURCES.md` row naming `b11909` and `caa8191d…`, which the C2
predicate needs and this build does not yet carry. The boundary is unchanged: three
sampled instants on one tiny model, unregistered ports, per-check pass/fail agreement
rather than byte equality, and a replay needs network to github.com and the model host.
b11909 is a third build of the same instrument, so it backs the lifecycle propositions of
S041, S046 and S055 at a new build; it does not re-verify their b11889/b11906 bytes, and
no registered endpoint was sampled.

Still frontier:
- The b11906 ledger population re-verified at b11909+. `registry/release-recheck-b11906.tsv`
  is still the b11906 readout: 91 rows on 16 pinned files. b11909 =
  `caa8191df159f764fb0160e3d2fc6be008948aee` is 3 commits after b11906
  (`gh api repos/ggml-org/llama.cpp/compare/b11906...b11909` → `total_commits 3`, 38
  files changed) and two pinned files moved — `src/llama-context.cpp` (S107, S130, S132)
  and `src/llama-kv-cache.cpp` (S113, S135) — so at least those five rows need a re-read
  at b11909+ before the population can be restated at the new release. This build
  re-reads no row, and the b11909 live receipts do not stand in for it. S477's
  tag-inventory figure stays stale as round 46 measured it (highest `bN` tag b11887 there,
  b11907 at the round-46 sample), and its 30d recheck is not due until 2026-11-24; the
  release identity the population assumes is still a counter constant rather than a
  re-derived fact.
- S013 (Ollama importing a model): still `mined`/`on-release`, used by
  `corpus/knowledge/gguf-runtime-compatibility-boundary.md`, and round 46's measurement
  still stands — `docs/import.md` is 404 at the cited `6d02a43a` (the page became
  `docs/import.mdx` there) — so the row needs the re-pin proposed in round 46
  (`98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18`), not a re-read.
- S022 and the unpinned vLLM stable pages S002–S004: S022 is still `queued` with no
  used-by and a floating `stable` alias, and the build takes no new page read for any of
  the four. They remain frontier because no revision pin and no release trigger dates
  them.
- The rows that cite llama.cpp but fall outside the 91-row population. Round 46 named ten
  (S026, S028, S038, S041, S046, S055, S477, S482, S484, S485); S486 (b11906 binary) and
  S487 (b11906 receipts) sit in the same family and are not in that list, so the family is
  at least twelve and its count needs re-deriving under its own stated rule before it is
  quoted as a number. S026 (PR #18001) and S028 (issue #4746) stay rejected and untouched;
  S038, S482, S484 and S486 are release-asset identity rows that a new release says
  nothing about; S041, S046, S055 and S485 are historical receipts, backed by the b11909
  sample at a new build, not re-verified by it.
- The `hexrun-census` unknowns. `python3 tools/hexrun-census.py scan --repo <clone> --rev
  3a09a1d9` reads `tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68
  unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22`, exit 1, against 21 at the
  round-46 measured tips (`42ea1204`, `e8fa87ef`); the additional token
  `8bca0cf333e7ceab5e734b354c87075c6efec86c` is cited in
  `corpus/lessons/round-46-verifier-spotcheck.md:23`, so round-46 D4 (ledger or close the
  unknowns) is still open and this round's red gate is pre-existing, not raised by the
  build.
- The instrument's edges: region scoping for the two knowledge `## Errata` blocks, the
  `SCORECARD.md` head carve-out that the tool cannot apply, the 20-line threshold (91
  events at 1), and contract coverage that is only as good as the rows it carries — a lane
  file declared append-only but missing from the contract is not detected.
- K05 (declared versus served context capacity): unchanged. No authorised
  registered-endpoint sample exists, and this round's fixture run at `--ctx 256` is
  excluded by the context-capacity rows' scope.
- Registered consumers: still no sample this round. The last admitted sample
  (2026-10-15: 3 rows, all `DEAD`) is not re-opened by an ephemeral replay server, and the
  replay instance was torn down with the port refused.

## Frontier disposition — round 48

Two claims were built at `380bcdff9c8af06997c482f6eb03db926a794a2b` (base
`33e005827742b29772b153cda036ec9f27f653be`, the round-47 closure; counters frozen at
`12284ba3`): append-only-audit v3 under a bound contract (C1, calibration) and live
receipts a fresh session can replay with record-time provenance (C2, operability). The
figures below are measured at that build commit with the frozen counters; the capability
rows, scorecard sections and registry rows are integration work and are not pre-empted
here.

**What v3 now audits.** `tools/append-only-audit.py` (schema `append-only-audit/v3`) takes
a `region` cell for every contract row: `*` grades every line, `exempt=<T1>|…@path:line`
leaves the named `## ` sections ungraded while a section is not gutted, `only=<prefix>@path:line`
grades only the sections whose title starts with the prefix. At `380bcdff` the nine rows of
`registry/append-only-contract.tsv` expand to **89 files** — the five self-description files,
81 lesson files, `corpus/knowledge/consumer-registry.md`, `registry/history/DELTA.md` and
`registry/report-landing-errata.tsv` — over 311 commits.

The two carve-outs the lane declared but could not previously apply are applied:

- **SCORECARD's head.** The five titles `SCORECARD.md:6` names as re-derived —
  `## Axes`, `## Planned`, `## Retired`, `## Saturation`, `## Capabilities` — are ungraded
  *while the section is not gutted*: an exempt title T is eligible for an event when the
  maximum of its line count over the event window is at least its line count at the parent.
  An in-place head rewrite is therefore an event with its deletions ungraded, and a head
  collapsed and never regrown is graded and unrestored.
- **The consumer-registry Errata region.** `corpus/knowledge/consumer-registry.md:30`
  declares its `## Errata` region append-only while the dated census body above may be
  edited; the row is `only=## Errata`, so only deletions inside an `## Errata` section are
  graded. At `--threshold 1` the file's four events are all `ungraded` (0 graded lines of
  1, 15, 1 and 2 deleted) — body edits are outside the rule, as declared.

Every declaration must bind, and the exit code now carries the regression signal:

- binding: the `declared_at` line must say `append-only` (or `append only`) for that path,
  contain none of four listed negations, and name the row's path token or sit in a file the
  row's pattern covers; an `exempt` pointer must call every title re-derived, an `only`
  pointer must declare its prefix. An unbound or malformed row exits 1.
- `regressed` exits 1: an event whose file holds fewer graded lines at the audited revision
  than at its best window commit. This is the round-47 X1Stable finding and it is what the
  build hit first. At the base `33e00582`, v3 with the round-48 contract reports
  `regressed=1`, exit 1: the `0718b6ab` SCORECARD event holds **2348** of its 2349 graded
  lines, and the one missing line is the round-45 authority banner at line 6 — text rounds
  46 and 47 rewrote in place. Line 6 sits before the first `## ` heading, so no exempt title
  can cover it. The build appended the round-45 and round-46 banners byte-exact under
  `### Superseded head banners (kept verbatim; round 48)` (`SCORECARD.md:2736`); the same
  event then holds 2349 and is `restored`.

At `380bcdff` the tool reports `commits=311 files=89 events=5 restored=5 partial=0
unrestored=0 ungraded_lines=89 regressed=0 vanished=0 bad_declarations=0`, exit 0: `LOG.md`
2292/2292 graded lines restored, `SCORECARD.md` 2349/2349 with 72 ungraded, `corpus/QUALITY.md`
375/375, `corpus/README.md` 663/663, and the `dd9f5dc6` SCORECARD event 14/14 with 17
ungraded. The frozen C1 counter reads
`selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5
lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0.

**What v3 still does not audit.**

- *The line-6 banner has no region vocabulary.* Region titles and prefixes must begin
  `## ` (`tools/append-only-audit.py:147-151`), and a line before the first `## ` heading has
  no section at all (`tools/append-only-audit.py:231-239`). The banner the lane rewrites
  every round is therefore always graded, and the carve-out covers the five head sections,
  not the preamble block that announces them. Round 48 keeps exit 0 by *appending* the
  superseded banner, not by exemption; a round that rewrites line 6 without appending the
  old text exits 1 — correctly, but as the instrument's law rather than as the lane's
  declared practice.
- *Eligibility is content-blind.* A declared title is ungraded whenever its line count over
  the window reaches the parent's, whatever the text. The tool's own `exempt-rewritten`
  case replaces 24 head lines with 24 unrelated ones and grades 0 lines, exit 0; the
  `exempt-gutted-then-regrown` case does the same when the section returns later in the
  window. `## Axes` could be replaced wholesale by same-length junk and no event would carry
  a graded line.
- *Sub-threshold deletions.* The threshold is 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:396`), a policy constant the contract does not derive; a
  19-line deletion is not an event. At `--threshold 1` the same revision reports 98 events
  (14 restored, 4 partial, 62 unrestored, 18 ungraded, 186 ungraded lines, exit 1), so the
  instrument grades 5 of the 98 deletion events a one-line threshold surfaces.
- *Binding is a lexical tripwire, and the counter shares it.* The negation list is four
  contiguous phrases (`tools/append-only-audit.py:119`) and the path token is a bare
  substring match (`:180-199`). A fixture whose declaring lines read `LOG.md isn't
  append-only.` and `The changelog is not really append-only.` binds both rows — the `log`
  inside `changelog` supplies the token — with `bad_declarations=0`, exit 0, and the frozen
  counter's `binds()` (`tools/round48-append-audit-v3-check.py:147,226-233`) returns the same
  answer, so no leg of it can catch a false bind.
- *The `A-row` rule is not expressible.* The `rule` cell is parsed and validated
  (`tools/append-only-audit.py:171-174`) but grading reads only the region; `corpus/SOURCES.md`
  is `A-row` with region `*`, so the cells the row calls mutable (`status`, `recheck`,
  `used-by`) are graded whole-file like any other line.
- *Restoration is a multiset over the whole file, not by position.* Identical text anywhere,
  in any section, counts; an appended copy of a deleted banner is a restoration, and so is a
  duplicate line standing in for a different one.
- *Coverage is only as good as the rows.* A lane file declared append-only but missing from
  the contract is invisible, and a `## ` inside a fenced block is a section boundary
  (preregistration limits).

**What the v5 receipts and the replay now prove.** The three receipts
(`.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`) are `kama-llamacpp-live/v5`, `outcome
pass`, 11/11 evaluated checks each, on unregistered loopback ports 33779, 41891 and 45023
(alias `kama-r48-live`, `--ctx 256`, `-t 1`), `build_info b11909-caa8191df`, with `props`,
`slots`, `health`, `models` and `metrics` captures and the loading 503 observed. Their
provenance is checked when it is recorded, not when it is read: the model is pinned to
Hugging Face revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` (sha256 `270cba1b…bd256d`),
the server asset is `llama-b11909-bin-ubuntu-x64.tar.gz` (sha256 `bf94332a…e695b`, member
`llama-b11909/llama-server` sha256 `35ac50fb…d7ff0`), and `provenance.verified.at` is
`record`: the live tool hashed the archive, the archive member and the model *before*
starting the server. The counter's `recordcheck` leg therefore passes only if the tool exits
2 with no server executed and no pass receipt for an unpinned `resolve/main` URL, a wrong
archive digest, an `http://` asset URL, a partial flag set and a non-server member — with a
marker file proving non-execution — and executes a stub with every flag right.

Each receipt replays from committed bytes: the replay re-acquires both recorded URLs into
scratch, the counter hashes the rerun's `server.realpath`, `model.path` and archive itself
against the frozen digests, requires the rerun's `started_utc` not to precede the counter's
start and its model commit to be the frozen one, and compares every evaluated check plus a
stable projection of the captured surfaces (props fields, slots count and body digest,
health status and body digest, models ids and `owned_by`, metrics status, loading envelope,
teardown outcome, listener ownership). `replayed=3/3`. `--compare` separates instance facts
(port, pid, times, log text, `models.created`) from those surfaces: a copy with only instance
fields changed exits 0, each of five copies with one stable surface changed exits 1. Wrong
digests and swapped URLs (the b11906 asset, another HF revision) are refused with a
digest-mismatch and no rerun. The frozen C2 counter reads `receipts=1 recordcheck=1 replay=1
compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 — and round 47's one
unmet leg is closed: `corpus/SOURCES.md:245` (S492) carries the pinned revision URL.

**What they still do not prove.**

- *That a server ran at replay time.* The replay leg hashes the re-acquired files and
  compares projections, but witnesses no process: no marker, pid, log freshness, port
  binding or loading observation is required of the rerun
  (`tools/round48-live-replay-v5-audit.py:401-435`; the marker lives only in `recordcheck`,
  `:289-333`). A replay tool that downloads the archive and the model, extracts the binary,
  and synthesises a rerun receipt from the receipt's own captures with a fresh `started_utc`
  would satisfy every replay condition. What holds the chain up is the lane's own live tool,
  not the counter; the counter's independent parts are the digests and the projection.
- *That the evidence outlives its hosts.* b11909 is a GitHub **prerelease** (`prerelease:
  true`, target `caa8191d`, published 2026-10-26T21:00:58Z, about 86 minutes before the
  receipts), and `releases/latest` is v0.7.0 (`prerelease: false`, target `620d2225`) — a
  semver release far behind, so the newest-release API is not a freshness oracle. A `bN` tag
  can exist before its release (round 46's b11907 answered 404), and a release asset can be
  deleted or re-uploaded: the replay then fails closed on the digest and the evidence stops
  being replayable rather than becoming wrong. The only retained copy is host-local
  (`~/.local/opt/llama-b11909*/…`), not committed. The model side pins a revision of a repo
  named `models-moved`: stable while the repo and revision exist.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, unregistered loopback ports, one platform (ubuntu-x64) and a replay
  that needs network to github.com and huggingface.co. No registered consumer was sampled
  and no K05 declared-versus-served context comparison is in scope.

**Still frontier:**

- A declared region for the SCORECARD preamble banner (region grammar is `## `-only), or an
  explicit lane rule that the banner is append-kept and the instrument says so.
- Content-aware eligibility for the five exempt head sections; today a wholesale
  same-length replacement is invisible.
- The 20-line threshold as a derived rather than a constant policy, and the 93
  sub-threshold deletion events one-line grading surfaces.
- A binding test a denial cannot pass, and a counter leg that does not reuse the tool's own
  `binds()`.
- Expressing an `A-row`'s mutable cells as a region rather than grading the whole file.
- An execution witness in the replay leg (marker or pid/liveness join) so that "replayed"
  means a server ran, and a retention answer for the prerelease asset the receipts name.
- Carried over unchanged from round 47 and not re-measured here: the b11906 ledger population
  at b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the llama.cpp-citing family count outside the 91-row
  population, the `hexrun-census` unknowns, K05, and the registered consumers (last admitted
  sample 2026-10-15, all `DEAD`, not re-opened by an ephemeral replay server).

**Integration addendum (round-48 L1).** The disposition above was drafted by wave seat S9Readme at the build `380bcdff`. At integration the contract gained a tenth row, `corpus/knowledge/error-is-not-a-verdict.md` with region `only=## Round24` (its line 173 declares the round24 sections append-only; seat K1Contract), and the `corpus/lessons/*.md` row was re-anchored from a one-lesson self-declaration to `corpus/QUALITY.md:143` (KQ26, which names lessons; seat K1Binding): 90 files, the same five events, exit 0. The round-42, round-43 and round-44 authority banners, lost below the 20-line threshold, were appended byte-exact under §Superseded head banners (seat X1Banner). `tools/sources-append-only.py` grades SOURCES transitions again (seat X9SourcesGuard; round-47 closure D8), and `tools/shortcut-tally.py` (considerthese/2026-10-26.md proposal 3) is a lane tool. Measured values: SCORECARD §Round-48 measured results.

## Frontier disposition — round 49

Two claims were built at `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (base
`438127bc01ff3b99f98468549d58046f932490ef`, the round-48 closure; counters frozen at
`36d5ed2681111b68c180f8ab1646d8dc9beaedee`, digests `86b4a40d…f0d6c1` and
`26c465a9…066945`): operability 8 → 8 under an execution witness for live-receipt replay
plus a bounded archive-member verification (C1), and calibration 7 → 7 under
append-only-audit v4's line origin and binding (C2). The figures below are measured at
that build commit with the frozen counters (`.ufo/waves/round-49/measured/c1-build.out`,
`c2-build.out`): C1 `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0; C2
`fixture=1 lane=1 scenarios=8/8 met=True`, exit 0. Capability rows, scorecard sections,
the instrument-registry entries and `corpus/lessons/round-49.md` are integration work and
are not pre-empted here.

**What the witness now proves.** `tools/kama-live-replay.py --witness-dir D` passes
`--witness-dir`/`--witness-timeout` to the live child (`tools/kama-live-replay.py:275-281`;
the child's bound grows by the witness timeout). Once the rerun server is ready and its
checks have run, `hold_for_witness()` (`tools/kama-llamacpp-live.py:280-296`) writes
`D/ready.json` {schema `kama-live-witness/v1`, port, the llama-server child's pid,
`written_utc`} atomically and holds the server until `D/release` exists, the child exits
or `--witness-timeout` (default 120 s) passes; the rerun receipt gains `witness`
{schema, dir, port, pid, released, waited_ms} (`:1860-1867`).

For each of the three committed round-48 v5 receipts the counter
(`tools/round49-replay-witness-audit.py`) runs that replay from the tip's `git archive`
with HOME/XDG_CACHE_HOME/TMPDIR under scratch and a witness dir, and while the replay
waits it checks from outside, with a model it downloaded and hashed itself:
`sha256(/proc/<pid>/exe)` equals the frozen server member digest `35ac50fb…d7ff0`
(`:258-262`); a LISTEN socket on `127.0.0.1`/`::1:<port>` has an inode among
`/proc/<pid>/fd` (`:193-228`, `:263-265`); the `-m` argument hashes to the frozen model
`270cba1b…bd256d` (`:266-275`); and a fresh `kama witness <16 hex>` nonce posted to
`POST /tokenize` (`with_pieces`) and `POST /detokenize` comes back with every piece equal
to the counter's own decode of `tokenizer.ggml.tokens[id]` (U+2581 read as a space) and
the detokenized text equal to the nonce, one leading space allowed (`:276-289`). It then
writes `release`; the replay must exit 0 with `match` true and the rerun receipt must
record `witness.released` true; afterwards the pid is gone and the port refuses
(`:292-339`). At the build, 3/3. A replay that starts no server at all — the round-48
K2Cheat/K2Urlswap class — can no longer reach `met=True`.

Both surfaces are sourced rows: S494, the llama.cpp server README at `caa8191d`
(§POST `/tokenize` … §POST `/detokenize`, `corpus/SOURCES.md:247`; lines 686–735 of the
committed copy `.ufo/waves/round-49/c1/server-README-caa8191d.md`), and S495,
`proc_pid_exe(5)` (`corpus/SOURCES.md:248`). Neither row exists at the base, and the
counter's `newrow` leg sees S494.

**What the archive bound now refuses.** `verify_archive_member()`
(`tools/kama-llamacpp-live.py:212-272`) refuses, before hashing a member byte: an archive
that is not a regular file (`provenance-archive-not-regular`), larger than 1 GiB
(`provenance-archive-too-large`, `:208`), or holding more than 4096 index entries walked
streaming (`provenance-archive-too-many-members`, `:209`); and a member that is absent,
not a regular file, sparse (`provenance-member-sparse`) or whose declared size differs
from the `--server` file's size (`provenance-member-size-mismatch`) (`:258-267`; called
with `os.path.getsize(server_real)` at `:1664-1666`). The counter's `cap` leg
(`:343-390`) builds a one-byte-member archive whose PAX header declares a 10^15-byte GNU
sparse member: the tool exits 2 in 0.1 s with `provenance-member-sparse` and a marker
proving the stub never ran, while the positive control, whose member is the stub's own
bytes, executes it. The live tool's own selftest exercises the same refusal.

**What v4 now audits.** `origin(l)` (`tools/append-only-audit.py:423-441`) is the set of
`## ` titles (`None` before the first heading) holding the line text at its first
appearance in the file's blob over `git rev-list --topo-order --reverse`; a deleted line
in an eligible exempt section stays ungraded only when its parent section is eligible
*and* its origin includes one of the file's exempt titles (`:465-478`). Binding
(`:216-233`) needs the row token as a whole word (`[a-z0-9_]` excluded on both sides),
treats a negation within three words before `append-only`/`append only` as unbinding
(`not|never|no|nor|neither|non|isn't|aren't|no longer`; v3's four fixed strings still
apply), and never lets a wildcard row bind through a line of a covered file merely saying
append-only. The JSON keeps `"schema": "append-only-audit/v3"` and adds
`"definition": "v4"`.

On the lane at the build the tool exits 0: the ten contract rows expand to 92 files over
319 commits, 5 events all restored, `regressed=0 vanished=0 bad_declarations=0`, and
`ungraded_lines` 82 (round 48: 89). The `0718b6ab` SCORECARD event grades 2356 of 2421
deleted lines and holds 2356 — ungraded 72 → 65 — and stays restored; the `dd9f5dc6`
event is 14/31 with 17 ungraded. The seven newly graded lines are the six round-34
capability rows and the round-41 `pin-watch` row of the head `## Capabilities` table
(`SCORECARD.md` parent lines 121–127 at `21945c61`): born under dated round headings,
carried into the head and deleted there in that rewrite, so v3's title carve-out hid
them; they are held at the tip. All eight fixtures hold: `launder` graded
25/unrestored/exit 1 (v3: ungraded/exit 0), `native-head` 25 ungraded/exit 0,
`dated-loss` unrestored, `substring`/`negated`/`wildcard-self` unbound exit 1,
`word-token`/`wildcard-named` bound exit 0.

The round-48 v3 counter is frozen at its old expectation and now disagrees by
construction: at the build its lane leg reads the v4 tool's 2356 graded / 65 ungraded
against its 2349 / 72 and exits 1 (`.ufo/waves/round-49/measured/r48c1-build.out`). It is
superseded, not regressed.

**What they still do not prove.**

- *That the observed server is the replay's server, or the source of its captures.* The
  counter observes `ready.json`'s pid and never joins it to the rerun receipt's
  `child_pid` (no `child_pid` in the counter; the acceptance at `:306-329` checks only
  `witness.released`), and `--compare` deliberately treats `child_pid`/`port` as instance
  facts (`tools/kama-live-replay.py:198`, `:291`). A harness can run the capture session,
  stop it and start a fresh b11909 server for the witness window, or skip the capture
  session and copy the original captures; every leg passes (round-49 seat K1Design F1).
  Round-49 seat K1Cheat built both a decoy replay that never executes the live tool and a
  `PYTHONPATH`/`sitecustomize` hijack of the pristine tree, each reaching
  `witness=1 cap=1 newrow=1 met=True` at this build; the counter builds the child
  environment from `os.environ` and overrides only HOME/XDG_CACHE_HOME/TMPDIR
  (`:431-434`).
- *That the binary came from the downloaded archive at replay time.* The witness hashes
  the running image, not where it was extracted from; a replay that runs the host copy
  `~/.local/opt/llama-b11909/llama-server` passes (preregistration limits[0]; K1Cheat).
- *That the bytes the server loaded are the hashed bytes.* The `-m` path's on-disk
  contents are hashed after start (`:266-275`); nothing binds the mapping the process
  actually holds.
- *Anything signed, or with build provenance.* The check is local kernel observation
  only: no signed Evidence, no exec-time measurement log (IMA), no SLSA/in-toto
  provenance; it is Linux `/proc` only and fails closed for a process it cannot read
  (round-49 seat U1Prior, reading RFC 9334 §10.2).
- *Content-aware eligibility.* v4 narrows the carve-out by origin, but 25 lines born in
  `## Axes` and rewritten in place are still 25 ungraded lines, exit 0 (`native-head`);
  a same-length replacement of exempt-born text stays invisible.
- *Binding beyond a lexical tripwire.* The window looks only before `append-only` and
  accepts only dashes as separators, so `append-only? No.` and `not, as of round 40,
  append-only` bind, while a rule-declaring `no edits append-only` is unbound (round-49
  seat K2Negation F1/F2; the `cannot`/`can't`/curly-apostrophe/em-dash escapes it also
  found are routed and narrowed by an integration edit). The whole-word class excludes
  only `[a-z0-9_]`, so `co-log`, `log's`, `a/b/log` and non-ASCII neighbours bind
  (K2Negation F3). The lane's 384 flagged lines are all judged correctly, so no contract
  row is mis-bound today.
- *Origin as provenance.* Origin is first appearance, not history: text born in the head,
  carried in a dated section and deleted from the head again stays ungraded, and identical
  text born in both places counts as exempt-born (preregistration limits[2]). Held text is
  still a multiset over the whole file, not by position.
- *The sub-20 boundary.* The threshold is still 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:452`), a policy constant the contract does not derive; the
  round-48 count of 66 graded sub-threshold events and the real `LOG.md` loss at
  `ed135b3c` predate this window, and round 49 did not decide it. Coverage is still only
  as good as the rows, and a `## ` inside a fenced block is a section boundary.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, one ubuntu-x64 asset, unregistered loopback ports, and a replay
  that needs github.com and huggingface.co.

**Still frontier:**

- A pid-continuity join in the witness (ready.json's pid equals the rerun receipt's
  `child_pid`, or the exe lies under the replay's work dir) and a child environment that
  is not inherited, so "witnessed" also means the replay's own lifecycle ran.
- An archive-origin binding at witness time, or an explicit statement that the record-time
  digest checks carry binary origin rather than the witness.
- A binding of the model the server actually loaded, not the file named at `-m`.
- Exec-time measurement and build provenance for the witness, or honest naming of it as a
  local, unsigned observer-nonce check.
- Content-aware eligibility for the five exempt head sections, and a region for the
  SCORECARD preamble (the grammar is still `## `-only, so the line-6 banner stays graded —
  selftest case `preamble-graded`), the `A-row` mutable cells, and position-aware
  restoration; v4 changes none of them.
- The negation window's punctuation and trailing forms and the whole-word class'
  apostrophe/hyphen/slash/non-ASCII edges, and a binding test a denial cannot pass.
- A derived rather than constant sub-20 threshold, and a disposition of the 66 graded
  sub-threshold events.
- The prerelease cliff: b11909 is a GitHub prerelease, the only retained copy is
  host-local, and a deleted or re-uploaded asset makes the replay fail closed rather than
  wrong.
- Carried over unchanged and not re-measured here: the b11906 ledger population at
  b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the `hexrun-census` unknowns, K05 (declared versus served
  context), and the registered consumers (last admitted sample 2026-10-15, all `DEAD`).

Integration (round 49, L1): drafted by wave-1 scribe S9Readme (`.ufo/waves/round-49/w1/out/S9Readme/frontier.md`) at the build; the measured values are in SCORECARD §Round-49 measured results. The `corpus/lessons/*.md` contract row had bound by coincidence to the KQ26 criterion at `corpus/QUALITY.md:143` (seat K2Binding); the line below declares the rule and the row is re-anchored to it.

Lesson files under `corpus/lessons/` are append-only as the `A-corr` contract row declares: filed lessons stay, and corrections are appended with the superseded text named (KQ26).

## Frontier disposition — round 50 (appended)

Two claims were built at `97c864bead3ee4a2f629574e77263d33834ec98a` (base
`26ecba64ad6fb571d09074b07202d1618a46ecd1`, the round-49 closure; counters frozen at
`601c8889f33d1797c712feb753974c20cf891264`, digests `ff6ac2ac…9c5e89` and
`925f07a4…48ca46`): operability 8 → 8 under a process-bound execution witness for
live-receipt replay (C1), and calibration 7 → 7 under append-only-audit v5's birth-DAG
origin, fence-aware sections and CRLF-normalized keys (C2). The figures below are
measured at that build commit with the frozen counters
(`.ufo/waves/round-50/measured/c1-build.out`, `c2-build.out`): C1
`bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0; C2
`fixture=1 lane=1 scenarios=12/12 met=True`, exit 0, lane `ungraded_lines 89`,
`bad_declarations 0`, `regressed 0`. Both base controls are met=False
(`.ufo/waves/round-50/controls/base.c1.out`: `bind=0 teardown=0 newrow=0 bound=0/3`;
`base.c2.out`: `fixture=0 lane=1 scenarios=9/12`). Capability rows, scorecard sections,
the instrument-registry entries and `corpus/lessons/round-50.md` are integration work and
are not pre-empted here.

**What the process-bound witness now proves.** The counter
(`tools/round50-replay-bind-audit.py`) starts each replay from a `python3 -I -c` invoker
(`:402-404`) with an environment it builds itself — PATH, LANG, the proxy variables, and
HOME/XDG_CACHE_HOME/TMPDIR under scratch (`:376-393`) — plus two canaries: a fresh
`KAMA_R50_CANARY` and a `PYTHONPATH` whose `sitecustomize.py` records every interpreter
that imports it. While `ready.json` names the server it checks from outside: the replay
runs the tip's `git archive` tree, the server pid descends from the replay's
pid through the ppid chain (`:450-453`, `:297-308`), `sha256(/proc/<pid>/exe)` is the
frozen binary (`:345`), a LISTEN inode on the port belongs to that pid (`:348-350`),
neither the server nor its parent carries the canary (`:351-358`), a mapping of that pid
hashes to the frozen model (`:359`, `:309-340`), and a fresh nonce round-trips through
`POST /tokenize` (`with_pieces`) and `POST /detokenize` against the counter's own
`tokenizer.ggml.tokens` decode (`:360-373`). After it writes `release`: the replay exits 0
with `match` true, the rerun receipt records `witness.released` true, its `child_pid`
equals the observed pid (`:470`), and its `model_mapping` sha256/dev/inode equal the
mapping the counter observed (`:473-476`); the pid is gone, the port refuses, and the
planted sitecustomize marker is empty (`:479-485`).

The isolation is the replay's own, not only the witness's. It starts the live child with
`python -I` and only `LIVE_ENV_KEYS` (PATH, HOME, LANG, LC_ALL) plus a TMPDIR under the
work dir (`tools/kama-live-replay.py:88`, `:112-115`, `:309-311`, `:319-333`); the child's
`preexec_fn` sets `PR_SET_PDEATHSIG` to SIGTERM and exits at once if the parent already
changed (`:314-318`); the replay sets the same signal on itself (`:100-108`, called at
`:587`). So killing whatever started the replay takes replay, live tool and server down.
`model_mapping()` in the live tool (`tools/kama-llamacpp-live.py:678-727`) reads
`/proc/<pid>/maps`, keeps only a mapping whose `pathname` stats to the same dev and inode
as the maps line, re-opens it `O_NOFOLLOW`, `fstat()`-checks it again and hashes that same
file; the receipt gains `model_mapping` with `mapped` true or a reason
(`:1999-2005`), and the replay refuses a rerun whose mapping is absent, unmapped or hashes
to another model (`tools/kama-live-replay.py:343-348`). At the build the counter kills the
invoker during the hold and requires every snapshotted descendant gone within 30 s with
the port refusing (`:497-521`; `KILL_WAIT` `:112`), and C1 adds source rows S496
(`proc_pid_maps(5)`, `corpus/SOURCES.md:249`), S497 (`PR_SET_PDEATHSIG(2const)`,
`:250`) and C2 S498 (CommonMark 0.31.2 §4.5, `:251`).

**What v5 now audits.** `tools/append-only-audit.py` keeps the JSON shape (`schema
append-only-audit/v3`) and declares `definition: v5` (`:573`): `key(l)` drops one trailing
carriage return (`:275-280`); `sections()` skips fences, opened by
`fence_open()`/closed by `fence_close()` per CommonMark 0.31.2 §4.5 (`:282-325`); and
`origins()` is the union, over every birth of a key among the commits reachable from
`<to>`, of the `## ` title holding it in that commit's blob — a birth being a commit whose
blob holds the key while no parent's blob does (`:480-509`). The carve-out keeps a deleted
line ungraded only when its parent section is an eligible exempt title *and* its origin
intersects the file's exempt titles (`:531-546`), so v4's dependence on rev-list order
(`F3`), on fake headings inside fences (`F4`) and on byte-exact keys (`F5`) is gone. Every
event's deleted count is pinned to `git diff --numstat` (`:520-524`), and ungraded is
defined as deleted minus graded, so `graded + ungraded == deleted` cannot drift; the C2
counter recomputes both independently for every lane event.

Twelve fixtures hold (`c2-build.out`): `order-a`/`order-b` build the same trees with the
merge parents swapped and both read `deleted 25 graded 0 ungraded 25`, exit 0; `fence`
(`## Axes` inside a fenced block, then 25 dated lines deleted) reads 25 graded,
unrestored, exit 1 — v4 read it ungraded, exit 0; `crlf-launder` (25 dated LF lines moved
under `## Axes` as CRLF, then deleted there) reads 25 graded, unrestored, exit 1 — v4
read it ungraded. The round-49 eight are kept unchanged: `launder` 25 graded unrestored
exit 1, `native-head` 25 ungraded exit 0, `dated-loss` unrestored, and
`substring`/`negated`/`wildcard-self` unbound versus `word-token`/`wildcard-named` bound.
A move never re-births a key — `launder` moves the dated lines under `## Axes` without the
key ever leaving the parent blob (`tools/round50-append-audit-v5-check.py:230-237`) —
which is why the laundering direction stays graded.

On the lane the tool exits 0: five events, `bad_declarations 0`, `regressed 0`,
`vanished 0`, `ungraded_lines 89` (v4: 82). The `0718b6abbda6` SCORECARD event keeps 2349
graded of 2421 deleted and 72 ungraded (v4: 65); `dd9f5dc6c0e6` is 14/31 with 17 ungraded
against the counter's own v5 count of 23; the LOG, QUALITY and README events grade
everything. The seven extra ungraded lines are the `## Capabilities` mirror rows of
`SCORECARD.md:121-127` at `21945c61` (six round-34 rows and the round-41 `pin-watch`
row): under v5 each has a birth at `82b5e9d3` — the round-45 restore of the truncated
SCORECARD, whose blob holds all seven under `## Capabilities` while the truncated parent
held none — so their origin intersects the exempt head title and they are ungraded; v4
took only the first blob in rev-list order (`29f9d1e1` for the six, `24aa1d34` for
`pin-watch`) and graded them. That is round-49 seat K2Origin's F6 (mirror rows falsely
graded) closed by origin, not by the "text still present in a dated section" rule that
seat proposed; the counter's own v5 count and the tool's now agree exactly (72 = 72).

**What they still do not prove.**

- *That the server's mapped pages are the bytes the check hashed.* `model_mapping()` and
  the counter both hash the file through its pathname now and compare that path's
  `stat()` dev/inode with the maps line; neither reads `/proc/<pid>/pagemap`, smaps or the
  resident pages, so a rewrite after the mapping is invisible whenever the file hashes
  the same at check time (identical content, or the original bytes restored)
  (preregistration limits[0]). On a filesystem whose maps `dev` differs from
  `stat.st_dev` (btrfs subvolumes) both checks fail closed: the tool's own compare
  (`tools/kama-llamacpp-live.py:710-713`) and the counter's (`:333`); the counter's
  scratch is xfs (`dev 103:05` in `c1-build.out`).
- *That the binary came from the downloaded archive at replay time.* The witness hashes
  the running image (`:345`) and never requires the exe path to lie under the replay's
  work dir or match the archive member, so a replay executing the host copy
  `~/.local/opt/llama-b11909/llama-server` still passes (limits[0]; the round-49 K1Cheat
  class).
- *Environment cleanliness beyond two channels.* The canaries are one environment
  variable and one `PYTHONPATH` sitecustomize (limits[1]); `LD_PRELOAD` into the server or
  a modified `python` on PATH are not planted, and the replay→live edge is protected by
  `-I`, not by a measured environment.
- *Teardown beyond one instant.* The invoker is killed once, during the witness hold
  (limits[2]), against a descendant snapshot taken at that moment; a child spawned after
  the snapshot is not tracked, and a kill during download or before readiness is not
  exercised.
- *The pid join's edges.* Both joined records are written by the live tool for the same
  process: the join is `ready.json`'s pid against the rerun receipt's `child_pid`, read
  after release (`:470`), with descent checked at hold time only and no start time bound
  to `child_pid`. It proves the observed pid is the server the receipt describes, not that
  the receipt's captured check outputs were re-derived at the witnessed instant — the
  counter observes the server live, it does not replay the captures.
- *Anything signed, or with build provenance.* Still local `/proc` observation and a
  counter-chosen nonce: no IMA exec measurement, no signed evidence, no SLSA/in-toto
  provenance; a process it cannot read fails closed.
- *Content-aware eligibility, and what a restore does to origin.* v5 still exempts a
  deletion purely by section and origin: the five head sections the contract exempts
  (`registry/append-only-contract.tsv:3`: `## Axes`, `## Planned`, `## Retired`,
  `## Saturation`, `## Capabilities`) leave 25 head-born lines ungraded in `native-head`,
  exit 0, and a same-length replacement of exempt-born text stays invisible. Birth is
  first appearance in the graph, not history: a truncation-and-restore re-births every
  line of the file, so text that sits in an exempt section at the restore keeps an exempt
  origin afterwards — the lane's own seven rows are exactly this case, and no fixture
  covers "delete a dated line, restore it into the head, delete it from the head".
- *The lexical binder.* The binding rule is v5's v4 copy unchanged (preregistration
  limits[3]): the negation window looks only before `append-only`, accepts only dashes as
  separators, and the whole-word class excludes only `[a-z0-9_]`, so `co-log`, `log's`,
  `a/b/log` and non-ASCII neighbours bind. The counter re-implements the binder rather
  than calling the tool. The lane's flagged lines are all judged correctly, so no contract
  row is mis-bound today.
- *The sub-20 boundary.* The threshold is still 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:448`), a policy constant the contract does not derive; the
  66 graded sub-threshold events and the real `LOG.md` loss at `ed135b3c` predate this
  window and round 50 did not decide them. Restoration is still a multiset over the whole
  file, not by position.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, one ubuntu-x64 asset, an ephemeral unregistered loopback port, and
  a replay that needs github.com and huggingface.co.

**Still frontier:**

- An archive-origin binding at witness time (the exe under the replay's work dir, or the
  archive member hash compared at exec), or an explicit statement that the record-time
  digest carries binary origin and the witness does not.
- The mapping the server actually holds — pagemap/smaps or a resident-page digest — and a
  dev comparison that survives a filesystem whose maps dev differs from `stat.st_dev`.
- Exec-time measurement and build provenance for the witness, or honest naming of it as a
  local, unsigned observer-nonce check.
- Injection channels beyond the two canaries, and a `child_pid` record bound to a pid start
  time so the join cannot alias.
- Content-aware eligibility for the five exempt head sections; a fixture for
  delete-restore-into-head laundering (today ungraded by the birth rule); position-aware
  restoration; the negation window's punctuation and trailing forms; the whole-word
  class' apostrophe/hyphen/slash/non-ASCII edges; and a binding test a denial cannot pass.
- A derived rather than constant sub-20 threshold, and a disposition of the 66 graded
  sub-threshold events.
- The prerelease cliff: b11909 is a GitHub prerelease the replay refetches from
  github.com each run; a deleted or re-uploaded asset makes the replay fail closed rather
  than wrong.
- Carried over unchanged and not re-measured here: the b11906 ledger population at
  b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the `hexrun-census` unknowns, K05 (declared versus served
  context), and the registered consumers (last admitted sample 2026-10-15, all `DEAD`).

Integration (round 50, L1): drafted by wave-1 scribe T7Readme
(`.ufo/waves/round-50/w1/out/T7Readme/frontier.md`) at the build; the measured values are
in SCORECARD §Round-50 measured results. S496/S497 name `corpus/lessons/round-50.md` as a
consumer, and S498 names it alone; that lesson lands at integration.
