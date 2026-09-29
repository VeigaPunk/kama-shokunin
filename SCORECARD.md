# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

## Axes

| Axis | Before → After | Evidence pointer | Last change |
|---|---|---|---|
| **operability** (worked axis) | **0 → 8** | `tools/kama-probe.sh` md5 `932ea3dc365e066e740731cf6a939506` (788 lines, 0755) + `registry/endpoint-consumers.tsv` (11 rows); gate `check` → `registry_rows_evaluated=11 model_ok=3 drift=8 exit=2`; six verdict classes exercised live (M2–M7 in `LOG.md`); `check --json` valid, stderr empty; `listeners` exit 0 | round 1 |
| **freshness** | **0 → 6** | every round-1 claim re-derived on-box: 41–47 cited `path:line` re-read (0 failures) per `corpus/knowledge/consumer-registry.md`; F1–F12 audited in `corpus/lessons/round-1-citations.md` (1 stale fact caught and corrected); drift measured live, and the 8080-family verdict is re-derived from the file itself, not from the registry's claim | round 1 |
| depth | 1 → 7 | `SKILL.md` (315 lines: 12-row decision table, 11 verbatim error signatures, 11 anti-patterns, 47 citations); `corpus/knowledge/endpoint-identity.md` (7 rule rows); `served-model-identity.md` | round 1 |
| coverage | 1 → 8 | `listener-census.md` (23 listeners, 1 row each), `consumer-registry.md` (38 rows), `alias-endpoint-normalization.md`; registry covers all 6 consumer pin classes incl. the binary default | round 1 |
| calibration | 1 → 7 | `corpus/lessons/round-1-citations.md` records the L1 fact that was **wrong** (F11 `m_flash`); `probe-mutation-matrix.md` names the holes the probe had; critic forced re-wording of the round's headline claim; `corpus/README.md` lists 5 open gaps | round 1 |
| adjacency | 1 → 7 | `cross-lane-scope.md` (ownership table, arbitration rule, per-lane handoffs); out-of-province reports in `LOG.md` (bench-arena `:8080/metrics`, `0.0.0.0:40993` LAN `/tmp` listing, `:9222` DevTools, 8790/8791 credential brokers) | round 1 |

Why operability stops at 8 and freshness at 6: the gate is verified runnable on the
llama.cpp runtime only (vLLM/ollama classified by rule, never measured), the registry
pins host-specific absolute paths (correct for a single-host endpoint gate, not portable),
and freshness is **manual** — nothing yet runs the gate on a schedule, so a pin that goes
stale is still only caught when someone runs it.

## Planned

Round 2: **freshness** — make the gate periodic (timer/wrapper that writes a dated result
and flags delta), so `MODEL_OK`→`FOREIGN_SERVICE` transitions are recorded by the lane
instead of being discovered by accident (the mint cause). Secondary: extend the runtime
matrix beyond llama.cpp (a vLLM/ollama row would turn rule 6 from [inference] to measured).

## Retired

None. Both assigned axes (operability, freshness) were unstarted at round 1. Retirement
would require evidence that the local-endpoint surface no longer exists (e.g. the local
model server is decommissioned) — not observed; `qwen-coder.service` is enabled and active.