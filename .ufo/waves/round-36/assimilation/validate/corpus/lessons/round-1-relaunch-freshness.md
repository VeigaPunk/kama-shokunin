# round-1 relaunch — freshness: admit current endpoint teardown as runbook truth

2026-10-15. Relaunch lane, freshness axis (mission AXES operability+freshness,
`MISSION.md:29`; `SCORECARD.md` freshness 7 vs operability 8 — freshness selected).
Lane baseline commit `c390918f8f6d5d1b52787e4720c8642377fdcb8c`. One move:
reconcile authoritative operational documentation with the current endpoint/
consumer teardown. No runtime behavior, no config mutation, no endpoint
restoration, no historical-corpus rewrite.

Live authority, one parent-authorized run 2026-10-15 (shared round-1 evidence):
`bash tools/kama-probe.sh check` → exit `2`;
`registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`;
all three registry rows `DEAD` (connection-refused):
`omp-llama-cpp-default@8080` (`file=inherited`, `resolver_kind=raw`),
`ufo-fsd-thetick@34113` (`file=yes`, url), `ufo-fsd-local-helper@34113`
(`file=yes`, url). UFO source root current at `~/Projects/ufo-fsd-alpha`;
no operator configs written.

## Gate: admit current endpoint teardown as runbook truth

### Candidates

1. Admit the 2026-10-15 `check` output (3 rows, 0 `MODEL_OK`, drift 3, exit 2)
   as current runbook truth; supersede the baseline `SKILL.md:213` summary and
   checklist claims at `SKILL.md:216-223` (both at `c390918f8f6d5d1b52787e4720c8642377fdcb8c`);
   keep historical corpus entries byte-frozen as dated samples.
2. Restore/restart the serving unit on 34113/8080.
3. Install/enable a systemd user timer so `snapshot` becomes a cadence.
4. Extend the snapshot schema with declared-vs-served context size
   (historical September observation: 32768 declared vs served 16384).

### Admitted

- Candidate 1. Current truth: **the registered endpoints at 8080 and 34113 do
  not answer**; the gate exits `2` with three `DEAD` rows. Prior statements
  that 34113 serves Qwen3-Coder-30B, pid 1299 is active, or eleven consumers
  remain registered are historical samples, not live authority.
- September identity cases retained **only as dated historical samples**, bytes
  unchanged: `corpus/lessons/round-1.md:4-5` (all commands run 2026-09-28); the
  `MODEL_OK` smoke at 34113 (`corpus/knowledge/endpoint-identity.md:26-30`,
  `:80`); the 20260929 snapshot tallies
  `corpus/knowledge/snapshot-history.md:61-64` (`rows=11 model_ok=3 drift=8`).
  They prove historical reconciliation and the normalization rules; they never
  assert present `MODEL_OK`. The stale-live-prose hazard is the same one already
  recorded in `corpus/lessons/round-4-recensus.md:29-31`.
- Scope of supersession: the current-live reading of the baseline summary
  (`SKILL.md:213`) and checklist items 6–13 (`SKILL.md:216-223`), at
  `c390918f8f6d5d1b52787e4720c8642377fdcb8c`. The runbook changes are the
  other documentation part of this same cutover; this new lesson preserves
  the corpus history and records why the stale readings were rejected.

### Rejected

- Candidate 2 (server restart): operator-owned. Endpoint restoration is outside
  this lane and was excluded from the move by the shared evidence; the
  round-4 named debt states the unblock as "operator restores a serving unit"
  (`corpus/lessons/round-4-recensus.md:25-27`). Dated 2026-10-15 narrow-scope
  unprivileged corroboration only: `systemctl --user show qwen-coder.service`
  → `LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`,
  `MainPID=0`; `ss` socket filter empty; former-path files absent. The broad
  `$HOME`/global-absence claim and any privileged survey were withdrawn — not
  required and not admitted here.
- The L0 question `kama | round-1 | 2026-10-15 freshness addendum…` asks the
  operator to choose an operator-selected serving runtime or explicit
  retirement; neither is performed here. The lane continues without an
  answer and keeps its current domain and registry.
- Candidate 3 (scheduler installation): operator-owned and province-forbidden —
  `PROVINCE.md` forbids kama from installing or enabling units
  (`corpus/knowledge/snapshot-history.md:78-81`); the honest claim stays
  **invocation history**, not periodic monitoring
  (`corpus/lessons/round-2.md:5-9`).
- Candidate 4 (context-size feature): out of scope for one freshness doc move;
  it is a documented open gap (`corpus/knowledge/snapshot-history.md:83-84`;
  corpus index Known gaps). A schema change is not endpoint/teardown
  reconciliation.

### Spot-check

- Not performed. The L2 spot-check role lands in this same lane (this
  executor), so it is not an independent promotion review; no `[x]` promotion
  is asserted here. Self-attestations in this lane remain `[~]`.

## Before/after ledger

Before — measured 2026-10-15 at the lane baseline
`c390918f8f6d5d1b52787e4720c8642377fdcb8c`:
**four documented summary fields, three mismatches** against the observed
teardown. Exact counting command, also used for the committed after-state:

```sh
bash tools/kama-probe.sh check --json | python3 -c 'import json,re,sys,pathlib; actual=json.load(sys.stdin)["summary"]; text=pathlib.Path("SKILL.md").read_text(); expected=json.loads(re.search(r"`summary` = `([^`]+)`",text).group(1)); mismatches={k:{"documented":v,"observed":actual[k]} for k,v in expected.items() if actual[k]!=v}; print(json.dumps({"fields_checked":len(expected),"mismatches":len(mismatches),"details":mismatches},sort_keys=True))'
```

Output: `fields_checked=4 mismatches=3`. Per-field rows:
`registry_rows_evaluated` doc=11 vs observed=3, `model_ok` doc=3 vs observed=0,
`drift` doc=8 vs observed=3; `exit` doc=2 vs observed=2 is the only match.
The original L1 measurement used live `check --json`, not a substituted
observed-value literal. Fields are dependent summary counters, not independent
runtime tests. This comparison says nothing about continuous monitoring.

At this implementation-stage entry, no committed after-measurement exists.
The delivery entry is appended after the implementation commit: use the same
command, retain `fields_checked=4`, and require `mismatches=0`; record any
residual mismatch rather than inventing a pass. Expected `check` exit `2`
records the current drift, not restored endpoint readiness.
