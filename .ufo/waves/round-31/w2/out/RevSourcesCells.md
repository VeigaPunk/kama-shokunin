# RevSourcesCells — SOURCES.md S180–S191 cell-by-cell vs SOURCES-CONTRACT-v1

contract-clean: **yes**

| row | URL + line anchor | opened = round date | quote ≤25w | quote verbatim vs snapshot | kind/tier | status | used-by exists & cites | recheck |
|---|---|---|---|---|---|---|---|---|
| S180 | raw URL `#L1360`; anchor `L1360 @ 704366d` | 2026-10-23 ✓ | 7w | VERBATIM | code/A | mined | both exist; registry cites | on-release |
| S181 | `#L1375`; `L1375 @ 704366d` | ✓ | 15w | VERBATIM | code/A | mined | ✓ | on-release |
| S182 | `#L1390`; `L1390 @ 704366d` | ✓ | 7w | VERBATIM | code/A | mined | ✓ | on-release |
| S183 | `#L1395`; `L1395 @ 704366d` | ✓ | 7w | VERBATIM | code/A | mined | ✓ | on-release |
| S184 | `#L1399`; `L1399 @ 704366d` | ✓ | 9w | VERBATIM | code/A | mined | ✓ | on-release |
| S185 | `#L1411`; `L1411 @ 704366d` | ✓ | 10w | VERBATIM | code/A | mined | ✓ | on-release |
| S186 | `#L1517`; `L1517 @ 704366d` | ✓ | 9w | VERBATIM | code/A | mined | ✓ | on-release |
| S187 | `#L1519`; `L1519 @ 704366d` | ✓ | 5w | VERBATIM | code/A | mined | ✓ | on-release |
| S188 | `#L1521`; `L1521 @ 704366d` | ✓ | 9w | VERBATIM | code/A | mined | ✓ | on-release |
| S189 | `#L1530`; `L1530 @ 704366d` | ✓ | 3w | VERBATIM | code/A | mined | ✓ (6 registry cites) | on-release |
| S190 | server-schema.cpp `#L47`; `L47 @ 704366d` | ✓ | 1w | VERBATIM | code/A | mined | ✓ | on-release |
| S191 | `#L64`; `L64 @ 704366d` | ✓ | 9w | VERBATIM | code/A | mined | ✓ | on-release |

Placement: all 12 rows sit at SOURCES.md lines 192–203 inside `## Registry` (line 9) before `## Paths` (line 205); NF=13 → 11 well-formed cells each; ids contiguous S178→S191, no duplicates. Round date from `corpus/lessons/round-31.md` line 1 = 2026-10-23; `## Gate` records each row's URL, access date and the same quote. Snapshot quotes compared byte-exact (leading whitespace normalized) against `.ufo/waves/round-31/sources/llama.cpp-704366d/` whose sha256s match `SNAPSHOT.json` pins for commit 704366d76 — **no reconstruction**.

Cosmetic deviations (not contract violations): `teaches` cells hold a bare backticked code line instead of benefit prose; `#L<n>` fragment on `raw.githubusercontent.com` URLs is inert but redundant with the anchor cell.

Limits: verified against the pinned local snapshot, not live GitHub; `opened` honesty is asserted by the rows/lesson; did not run `scripts/sources-census.sh`. Full command log and receipts: `.ufo/waves/round-31/w2/out/RevSourcesCells/report.md` (+ `verbatim-receipt.txt`, `rows-S180-S191.txt`, `gate-records.txt`).
