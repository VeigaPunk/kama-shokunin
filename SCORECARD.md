# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

## Axes

| Axis | Before → After | Evidence pointer | Last change |
|---|---|---|---|
| **operability** (worked round 1) | **0 → 8** | `tools/kama-probe.sh` md5 `1f81e859c2d7f43f87d1f7e01327b2cf` (1092 lines, 0755) + `registry/endpoint-consumers.tsv` (3 rows); live `check` → `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`; `--ufo-src` derives the ufo-fsd checkout (`$UFO_SRC` env → `~/Projects/ufo-fsd-alpha` → `~/Projects/origin-work/ufo-fsd-alpha` → fail-closed `file=missing`); `bash -n` clean (shellcheck absent on this box) | round 3 |
| **freshness** (worked round 2) | **6 → 7** | `snapshot` writes dated `kama-probe/v2` JSON and diffs tracked `registry/history/latest.tsv` into append-only `DELTA.md`; live re-census run: `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` — the 16 transitions are the honest record of 8 consumer files deleted from the box plus MODEL_OK→DEAD on the dead ports; stable re-run `transitions=0`; `tools/test-snapshot.sh` md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0` | round 3 |
| depth | 1 → 7 | `SKILL.md` (323 lines: 12-row decision table, 11 verbatim error signatures, 11 anti-patterns, 14-step checklist); `corpus/knowledge/endpoint-identity.md` (7 rule rows); `snapshot-history.md` | round 1 |
| coverage | 1 → 8 | `listener-census.md` (23-row round-1 sample; 20 listeners on round-2 refresh), `consumer-registry.md` (38 rows), `alias-endpoint-normalization.md`; registry covers all 6 consumer pin classes incl. the binary default | round 1 |
| calibration | 1 → 7 | round-1 audit records the wrong F11 route; round-2 critic rejected “periodic” for unscheduled invocation history; runtime fixtures are explicitly parser evidence, not vLLM/Ollama integration; corpus keeps open gaps | round 1 |
| adjacency | 1 → 7 | `cross-lane-scope.md` (ownership table, arbitration rule, per-lane handoffs); out-of-province findings remain reported, not absorbed; round-2 scheduler decision handed to L0 | round 1 |

Why operability stops at 8 and freshness at 7: the gate is verified against a real
llama.cpp runtime only (vLLM/Ollama are fixture-shaped parser tests), the registry pins
host-specific paths, and comparison is still **invocation-driven**. No clock runs
`snapshot`; a transition that starts and ends between invocations remains invisible.

Round-3 verdicts (godspeed axes): **operability — improved** (gates run bare again on
derived `--ufo-src`; before, two rows failed `file=missing` and one row crashed the
JSON resolver). **freshness — improved** (baseline now reflects live truth; DELTA.md
carries the 16-transition teardown record). **coverage — unchanged** (census corpus
kept, errata-marked; registry surface genuinely shrank — the files are gone, not
miscounted). **calibration — improved** (every changed anchor re-measured, dead-path
citations zero outside errata). **adjacency — unchanged** (out-of-province findings
reported, not absorbed).

**Carried debt:** the two positive-control rows (`ufo-fsd-thetick`,
`ufo-fsd-local-helper`) read `DEAD` — the pins verify `file=yes` at the relocated
tree but nothing listens on 34113. Unblock: operator restarts `qwen-coder.service`
(or a successor unit). Until then `model_ok=0` is ground truth, not a gate defect.

## Planned

Round 4: **freshness** — add declared-vs-served context-size reconciliation
(`limit.context` vs live `/props`/server args) to the snapshot schema. Carried
from the pre-re-census plan; it is *blocked on the same debt* (nothing listens
on 34113 today — the plan assumes a live server to reconcile against).
Scheduling is separately operator-owned and filed through the L0 side channel;
do not install a timer inside kama's write boundary.

## Retired

None. Both assigned axes remain active — though round 3 observed the
retirement precondition beginning to materialize: `qwen-coder.service` is
inactive and deleted, and every model endpoint is dead. Retirement still
requires evidence the surface is *permanently* gone (not observed — the
34113 pins ship in a maintained upstream repo), or that invocation history
and context drift have saturated (not observed).

## Move log

| Round | Axis | Before | After | Evidence |
|---|---|---|---|---|
| 4 | freshness | measured at HEAD (see lesson) | verdicts recorded per gate, no scalar | `corpus/lessons/round-4-recensus.md` |
