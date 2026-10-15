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