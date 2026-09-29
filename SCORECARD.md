# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

## Axes

| Axis | Before → After | Evidence pointer | Last change |
|---|---|---|---|
| **operability** (worked round 1) | **0 → 8** | current `tools/kama-probe.sh` md5 `61e82ee22dc89292175c5431f1ed6dc1` (1051 lines, 0755) + `registry/endpoint-consumers.tsv` (11 rows); live `check` → `registry_rows_evaluated=11 model_ok=3 drift=8 exit=2`; `bash -n` and `shellcheck -S warning` clean | round 1 (artifact evidence refreshed round 2) |
| **freshness** (worked round 2) | **6 → 7** | `snapshot` writes dated `kama-probe/v2` JSON and diffs tracked `registry/history/latest.tsv` into append-only `DELTA.md`; live baseline/stable runs: 11 rows, 3 ok, 8 drift, 0 transitions, exit 2; unchanged state leaves both tracked files byte-stable; `tools/test-snapshot.sh` md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0`; reviewer re-derived live domain facts and caught one bad line citation, one moved path, and transient listener-count drift | round 2 |
| depth | 1 → 7 | `SKILL.md` (323 lines: 12-row decision table, 11 verbatim error signatures, 11 anti-patterns, 14-step checklist); `corpus/knowledge/endpoint-identity.md` (7 rule rows); `snapshot-history.md` | round 1 |
| coverage | 1 → 8 | `listener-census.md` (23-row round-1 sample; 20 listeners on round-2 refresh), `consumer-registry.md` (38 rows), `alias-endpoint-normalization.md`; registry covers all 6 consumer pin classes incl. the binary default | round 1 |
| calibration | 1 → 7 | round-1 audit records the wrong F11 route; round-2 critic rejected “periodic” for unscheduled invocation history; runtime fixtures are explicitly parser evidence, not vLLM/Ollama integration; corpus keeps open gaps | round 1 |
| adjacency | 1 → 7 | `cross-lane-scope.md` (ownership table, arbitration rule, per-lane handoffs); out-of-province findings remain reported, not absorbed; round-2 scheduler decision handed to L0 | round 1 |

Why operability stops at 8 and freshness at 7: the gate is verified against a real
llama.cpp runtime only (vLLM/Ollama are fixture-shaped parser tests), the registry pins
host-specific paths, and comparison is still **invocation-driven**. No clock runs
`snapshot`; a transition that starts and ends between invocations remains invisible.

## Planned

Round 3: **freshness** — add declared-vs-served context-size reconciliation
(`limit.context` vs live `/props`/server args) to the snapshot schema. Scheduling is
separately operator-owned and filed through the L0 side channel; do not install a timer
inside kama's write boundary.

## Retired

None. Both assigned axes remain active. Retirement would require evidence that the
local-endpoint surface no longer exists (not observed: `qwen-coder.service` is active)
or that invocation history and context drift have saturated (also not observed).