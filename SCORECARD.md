

### Round-45 measured results

Measured commit: `21945c6125c2fae531be94d7652ee058c68e5f83` (fresh clone of the lane remote). Base `6b8ccfb3`. Counters: frozen bytes of `1641aa07`; C2 v2 of `85977699`.

| Claim | Base | Measured `21945c61` | Command | Receipt |
|---|---|---|---|---|
| C1 freshness 8 → 8 | `unverified=11 met=False` (exit 1) | `pop=11 rows=11 valid=11 unverified=0 unchanged=3 holds=8 reworded=0 drifted=0 removed=0 flags_missing=0 section=1 newrows=2 fetch=1 fetch_bad=0 met=True` (exit 0) | `python3 tools/round45-recheck-audit.py --repo <clone> --tip <commit> --fetch` | `.ufo/waves/round-45/controls/base.c1.out`; `.ufo/waves/round-45/c1/after.out` |
| C2 calibration 7 → 7 | `missing=126 met=False` (exit 1) | v1 `valid=91 bad=35 agree=34 overclaim=1 underclaim=2 other=1 absent=0 consistency_bad=1 summary=0 axes=1 met=False` (exit 1); v2 `valid=103 bad=23 agree=40 … consistency_bad=1 summary=0 met=False` (exit 1) | `python3 tools/round45-claim-outcome-audit[-v2].py --repo <clone> --tip <commit> --fleet <fleet>` | `.ufo/waves/round-45/c2/c2-v1.out`, `c2-v2.out` |

C2 is **not achieved** under the frozen counter or the amendment: an honest stop. The ledger and its reading (`agreement=58/61`) stand as evidence; the counters cannot certify them (lesson §Mistakes row 2, KQ65). Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. The planned wave did not run (dispatch stalled at 32 of 64 spawned), so neither claim was attacked by a seat.

### Planned (round 46)

1. Calibration: re-freeze a claim-outcome counter that reads a hand-picked sample of true outcome lines (KQ65) and re-score `registry/claim-outcome-ledger.tsv` unchanged; route the 23 unreadable rows as the sample.
2. Freshness: llama.cpp releases after b11889 (b11897 at the round-45 sample) for the 91 round-44 rows and S484/S485, and the floating-series rows S013, S022.
