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
