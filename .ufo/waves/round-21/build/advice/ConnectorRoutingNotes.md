VERDICT: confirm - Round 20 lost 15 original seats (13 falsify, 2 build) concentrated in reviewers (12) and critics (2) across ZAI and Codex rate limits.

## Evidence: Round 20 Dead Seat Accounting
Observed via `seat-failures.json`, `plan.json`, and `kama.md:56-58`:
- Command: `python3 -c 'import json; d=json.load(open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/falsify/seat-failures.json")); print(len(d["dead_original_seats"]))'` -> exit 0, output `13`.
- Command: `python3 -c 'import json; d=json.load(open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/build/out/ConnectorRoutingNotes/round20-failures-summary.json")); print(d["round_totals"])'` -> exit 0, output `{'total_spawned': 158, 'total_dead_original': 15, 'dead_by_role': {'critic': 2, 'reviewer': 12, 'scout': 1}}`.
- Falsify Wave (86 spawned, 13 dead = 15.1% loss):
  * By role: `reviewer` 11/60 (18.3%), `critic` 2/2 (100.0%). `mutation-tester` 0/17 (0%), `scout` 0/6 (0%), `connector` 0/1 (0%).
  * By error class:
    - 9 seats: `Retry budget exhausted after 5 retries: 429 Rate limit reached (type=1302)` [Provider: ZAI glm-5.3-flash; all 9 were `reviewer`].
    - 4 seats: `Retry budget exhausted after 5 retries: Codex at capacity (turn_rate_limit_exceeded)` [Provider: OpenAI Codex; 2 `critic` (C1ErrorCensus, C2GgufMeasure), 2 `reviewer` (CitationR18C1CheckpointExit, R18C2EvidenceScope)].
- Build Wave (72 spawned, 2 dead = 2.8% loss):
  * By role: `scout` 1/16 (SrcGateStandard), `reviewer` 1/13 (CellDesign).
  * By error class: 2 seats: `[zai/glm-5.3-flash] Retry budget exhausted after 5 retries: 429 Rate limit reached for requests (type=1302)`.
  * Continuation failure: `StaleCountSweep` (`scribe`): `[anthropic/claude-haiku-5-5] 429 rate_limit_error; retry-after-ms=8231000`.
- Wave Refusal: Both waves hit `Background job limit reached (100)` on attempt 1; resolved after >=180s cooldown without altering payload.

## Provider Vulnerability Analysis
1. ZAI (`type=1302`): 11 dead original seats (2 build, 9 falsify). Triggered by request burst when a single role (`reviewer`) dominated >69% of falsify wave.
2. Codex (`turn_rate_limit_exceeded`): 4 dead falsify seats. Wiped out 100% of critics (2/2), completely killing independent falsifier evaluation of both C1 and C2.
3. Anthropic (`retry-after-ms=8231000`): StaleCountSweep scribe continuation stalled due to excessive backoff window (~2.3 hours).

## Affected Axes
- Calibration (7 -> 7/8, C1 report landing audit): High risk if audit checks rely solely on `critic` (which saw 100% mortality under Codex in R20).
- Operability (8 -> 8, C2 symlink install identity): High risk if gate/grid verification lacks redundant role coverage.

## Proposed Move: Dual-Role Heterogeneous Shadowing in Wave 2 (Falsify)
To prevent provider capacity spikes from dropping critical falsifications in Round 21:
1. Shadow Core Claims Across Diverse Roles: Never route C1 or C2 falsification through a single role [INFERENCE]. Assign C1 audit check to both a `critic` and a `mutation-tester`; assign C2 receipt/grid check to both a `reviewer` and an `executor`.
2. Cap Single-Role Monoculture: Limit any single UFO role to <50% of the wave payload (avoiding R20's 60/86 reviewer burst that triggered ZAI type=1302 rate limits) [INFERENCE].
3. Leverage 0%-Failure Roles: In R20 falsify, `mutation-tester` (17/17) and `scout` (6/6) had zero deaths. Route high-priority probes through these roles.

## Risks & Verification
- Risks: Subagent tasks must match role tool capabilities (e.g., `executor` can run bash, `reviewer` evaluates text/diffs).
- Verification: JSON summary generated at `.ufo/waves/round-21/build/out/ConnectorRoutingNotes/round20-failures-summary.json`. R21 falsify dispatch plan can be validated against role distribution caps before execution.
- Tool installs/updates: none.
