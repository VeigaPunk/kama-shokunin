# Free-tier provider limits — kama load-test (rounds 6–17)

Dated measurement record for the operator goal "free-tier provider
load-test" (2026-10-18). This entry is a **dated census of dispatch
outcomes**, never a promise of provider availability. Sources: per-round
telemetry `.ufo/round-<N>/telemetry.json` and fleet reports
`.ufo/reports/round-<N>/kama.md` (fleet root); both are resolvable evidence.

## Methodology

- Per round: ONE batched AgentSwarm call, 64 `coder` seats, wire-default
  thinking effort (the dispatch surface exposes no per-seat effort pin).
- Telemetry levels: dispatch-level (recorded by L1: timestamps, wall time,
  launch/completion/failure counts, failure class verbatim) and seat-level
  (each seat self-measures t_start/t_end and its deliverable's byte size
  when it executes).
- **Inferred TPS proxy** (only when ≥1 seat completes): per-seat
  deliverable_bytes ÷ (t_end − t_start), pooled to a median and an aggregate
  (Σbytes ÷ round wall time). This measures end-to-end seat throughput
  including tool calls — NOT provider decode tokens/sec. Labeled inferred
  everywhere it appears.
- Failure classes are kept distinct: **upstream-unavailable** (alias valid
  locally, provider gateway rejects) vs **host-catalog-gap** (runtime
  rejects the alias locally, no upstream contact).

## Status board

| Round | Loop | Model | Launched | Completed | Failed | Failure class | Wall s | Peak conc. | Inferred TPS |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 1 | deepseek-v4.1-flash-free | 64 | 0 | 64 | upstream 400 Model is unavailable | 41.6 | 0 | n/m |
| 7 | 1 | deepseek-v4.1-flash-free | 64 | 0 | 64 | upstream 400 Model is unavailable | 41.5 | 0 | n/m |
| 8 | 1 | glm-5.3-flash-free (opencode-go) | 0 | 0 | 0 | host catalog rejection (pre-spawn) | 0.0 | 0 | n/m |
| 9 | 1 | glm-5.3-flash-free (opencode-go) | 0 | 0 | 0 | host catalog rejection (pre-spawn) | 0.0 | 0 | n/m |

n/m = not measurable (zero completing seats in the round).

## Loop 1 (rounds 6–9) — FINAL 2026-10-18T18:42Z

- **deepseek-v4.1-flash-free (opencode-go free tier):** three probes within
  ~25 min (waves at 18:32Z and 18:37Z, single-seat re-probe 18:33Z);
  128/128 catalog-valid spawns fast-failed upstream with the identical
  `400 Upstream request failed: Model is unavailable.` Effective free-tier
  concurrency ceiling for the window: **0 usable seats** — a sustained
  provider-side outage of the free wire id, not a transient rate limit.
- **glm-5.3-flash-free (opencode-go):** wire id **absent from this host's
  dispatch catalog**. Two attempts (18:39Z, 18:41Z) rejected locally before
  any seat creation; the 29-alias catalog listing was identical both times.
  Ceiling: **not dispatchable on this host**. glm-5.3-flash exists only as
  `zai-coding-plan/glm-5.3-flash[-low]` and `devin/glm-5-3-flash-*`
  (different providers — not the opencode-go free tier under test).
  Operator decision pending at fleet `.ufo/l0-questions.md` (kama | round-8).
- **Loop 1 totals:** tokens generated 0; inferred TPS n/m; wall-clock
  evidence ~9 min across 4 rounds.

## Loop 2 (rounds 10–13) — pending

## Loop 3 (rounds 14–17) — pending

## Conclusion (updated each loop)

Loop 1: both free providers yielded zero usable concurrency — deepseek-free
via sustained upstream outage, glm-free via host catalog gap. As of
2026-10-18T18:42Z no free-tier token has been generated in this test; the
"effective free-tier concurrency limit" for both providers in this window
is **0 seats**, pinned by `.ufo/round-6..9/telemetry.json`.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A39): `rounds 6–17` at line 1 is stale (nl -ba corpus/knowledge/free-tier-provider-limits.md | sed -n '26,57p' => the status board contains rounds 6-9 only, and loops 2-3 remain pending); current anchor: `corpus/knowledge/free-tier-provider-limits.md:26-57`]*

## Provenance supplement — round 11 (2026-10-19)

source: retained historical evidence — `.ufo/round-6/telemetry.json`, `.ufo/round-7/telemetry.json`, `.ufo/round-8/telemetry.json`, `.ufo/round-9/telemetry.json` and the corresponding fleet `.ufo/reports/round-6/kama.md` through `round-9/kama.md`; this file also contains earlier pointers and appended A39 correction. No claim that these are the only in-file pointers is made.
verified-at: original observations 2026-10-18; metadata review 2026-10-20 only. Retained telemetry/report records were reopened. The board's counts are historical; observation/recording dates come from the telemetry records, not a date column in that board. No endpoint, provider, dispatch catalog or wire id was contacted, and those observations are not refreshed.
recheck: run from the lane root, retained-metadata check (no network): `for n in 6 7 8 9; do python3 -c "import json;d=json.load(open(f'.ufo/round-$n/telemetry.json'));print(d['round'],d['recorded_utc'],d['seats_dispatched'],d['seats_completed'],d['seats_failed'])"; test -f /home/vgpnk/Projects/shokunin/.ufo/reports/round-$n/kama.md && echo "round-$n fleet report present"; done`; live availability revalidation needs a new operator-authorized single-seat probe of the exact wire id `opencode-go/deepseek-v4.1-flash-free` plus a fresh dispatch-catalog listing for the glm arm `opencode-go/glm-5.3-flash-free` — dispatch-surface work, not a documentation-round action.

*[provenance supplement appended 2026-10-20 (round-11 wave; steered label 2026-10-19): no byte above is rewritten and no observation above is refreshed by this supplement.]*
