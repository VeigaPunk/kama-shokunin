# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

Current authority: the single `**Current authority (round N):**` line of `## Current authority` below. This paragraph is constant; a round re-derives that one line and never removes it. The `## Axes` table, `## Planned`, `## Retired`, `## Saturation` and `## Capabilities` are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1); the round-5 banner and the head sections they replace are kept verbatim under `## Historical head sections`.

## Current authority

**Current authority (round 47):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 47. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

## Axes
