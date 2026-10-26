# C1 D2: v1 vs v2 across eight audited tips (lane clone at /fast/scratch/.../X1Stable/lane)

Tips are the 8 revisions requested by item X1Stable, sampled across `git rev-list --topo-order --reverse 172b8ad0^~40..3a09a1d9`
(43 commits; column `#` is the 1-based index in that list) plus the two round-45 event boundaries (T6 = the 0718b6ab deletion event,
T7 = its restoration at 82b5e9d3). v1 = `git show bbcc6dc2:tools/append-only-audit.py` (sha256 793dab9f...);
v2 = lane `tools/append-only-audit.py` with `--contract registry/append-only-contract.tsv` (the build contract, passed as a file
because the contract does not exist at tips T1-T5). `-` = event absent at that tip.

| tip | # | rev | event commit | file | v1 deleted | v1 restored_at_tip | v1 status | v2 deleted | v2 restored_max | v2 status |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 1 | 45e6f1a9637f | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T2 | 7 | 596921fccd6a | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T3 | 13 | 372fc011f9dc | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T4 | 19 | ef76777e5fbd | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T5 | 25 | 85977699b4af | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T6 | 27 | 0718b6abbda6 | 0718b6abbda6 | LOG.md | 2290 | 280 | partial | 2292 | 0 | unrestored |
| T6 | 27 | 0718b6abbda6 | 0718b6abbda6 | SCORECARD.md | 2417 | 511 | partial | 2421 | 0 | unrestored |
| T6 | 27 | 0718b6abbda6 | 0718b6abbda6 | corpus/QUALITY.md | 375 | 102 | partial | 375 | 0 | unrestored |
| T6 | 27 | 0718b6abbda6 | 0718b6abbda6 | corpus/README.md | 663 | 138 | partial | 663 | 0 | unrestored |
| T6 | 27 | 0718b6abbda6 | dd9f5dc6c0e6 | SCORECARD.md | 31 | 1 | partial | 31 | 24 | partial |
| T7 | 28 | 82b5e9d33a19 | 0718b6abbda6 | LOG.md | 2290 | 2290 | restored | 2292 | 2292 | restored |
| T7 | 28 | 82b5e9d33a19 | 0718b6abbda6 | SCORECARD.md | 2417 | 2416 | partial | 2421 | 2420 | partial |
| T7 | 28 | 82b5e9d33a19 | 0718b6abbda6 | corpus/QUALITY.md | 375 | 375 | restored | 375 | 375 | restored |
| T7 | 28 | 82b5e9d33a19 | 0718b6abbda6 | corpus/README.md | 663 | 663 | restored | 663 | 663 | restored |
| T7 | 28 | 82b5e9d33a19 | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T8 | 43 | 3a09a1d93dcc | 0718b6abbda6 | LOG.md | 2290 | 2290 | restored | 2292 | 2292 | restored |
| T8 | 43 | 3a09a1d93dcc | 0718b6abbda6 | SCORECARD.md | 2417 | 2409 | partial | 2421 | 2420 | partial |
| T8 | 43 | 3a09a1d93dcc | 0718b6abbda6 | corpus/QUALITY.md | 375 | 375 | restored | 375 | 375 | restored |
| T8 | 43 | 3a09a1d93dcc | 0718b6abbda6 | corpus/README.md | 663 | 663 | restored | 663 | 663 | restored |
| T8 | 43 | 3a09a1d93dcc | dd9f5dc6c0e6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |

## Monotonicity of v2 across the same tips (per event)

| event | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | ever falls? |
|---|---|---|---|---|---|---|---|---|---|
| dd9f5dc6c0e6 SCORECARD.md | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | no |
| 0718b6abbda6 LOG.md | absent | absent | absent | absent | absent | 0 | 2292 | 2292 | no |
| 0718b6abbda6 SCORECARD.md | absent | absent | absent | absent | absent | 0 | 2420 | 2420 | no |
| 0718b6abbda6 corpus/QUALITY.md | absent | absent | absent | absent | absent | 0 | 375 | 375 | no |
| 0718b6abbda6 corpus/README.md | absent | absent | absent | absent | absent | 0 | 663 | 663 | no |

v1 by contrast (same table, `restored_at_tip`):
- `dd9f5dc6 SCORECARD`: 24 (T1-T5) -> **1** (T6, tip moved onto the 0718b6ab deletion event) -> 24 (T7-T8).
  Nothing deleted dd9f5dc6's content again between T5 and T6; only the audited tip moved and the SCORECARD head was re-anchored.
- `0718b6ab SCORECARD`: 2416 at T7 -> **2409** at T8 (7 lines) with no deletion event in between.
- `0718b6ab LOG/QUALITY/README`: 0 at T6 (tip = the event commit itself) -> 2290/375/663 at T7-T8.

v2 on the same events: 24/24/24/24/24/24/24/24 and 2420 at T7 == 2420 at T8 (never falls).
