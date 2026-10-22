# Bounded required-read probe cells (current arm, pinned 2e254a1763a9c08aa07fc53081287f506c447d84)

| cell | builder | exit | expected | met | problems | stderr (first line) | traceback | timeout | leak | acquired |
|---|---|---|---|---|---|---|---|---|---|---|
| PG07-complete-lane-plain | c_complete_lane_plain | 0 | 0 | True | [] |  | False | False | False | {"fleet": [], "lane": []} |
| PG13-missing-lane-blob-promisor | c_missing_lane_blob_promisor | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in /fast/scratch/hyaku/kama-r24/falsify/CodeRequi | False | False | False | {"fleet": [], "lane": []} |
| PG14-missing-lane-blob-plain | c_missing_lane_blob_plain | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in /fast/scratch/hyaku/kama-r24/falsify/CodeRequi | False | False | False | {"fleet": [], "lane": []} |
| PG15-missing-lane-tree-promisor | c_missing_lane_tree_promisor | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (tip tree 1c13e47ce9f8088dc933a80123cf6a8ee2fa701d) in /fast/scratch/hyaku/kama-r24/falsify/ | False | False | False | {"fleet": [], "lane": []} |
| PG16-missing-lane-tree-plain | c_missing_lane_tree_plain | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: 58866b563cd900df310588effe79028efc104c33:corpus/SOURCES.md (tip tree 1c13e47ce9f8088dc933a80123cf6a8ee2fa701d) in /fast/scratch/hyaku/kama-r24/falsify/ | False | False | False | {"fleet": [], "lane": []} |
| PG45-missing-unused-tree-plain | c_missing_unused_tree_plain | 0 | 0 | True | [] |  | False | False | False | {"fleet": [], "lane": []} |
| PG17-missing-fleet-report-promisor | c_missing_fleet_report_promisor | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, /fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/p | False | False | False | {"fleet": [], "lane": []} |
| PG18-missing-fleet-report-plain | c_missing_fleet_report_plain | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, /fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/p | False | False | False | {"fleet": [], "lane": []} |
| PG21-missing-ancestor-promisor | c_missing_ancestor_promisor | 2 | 2 | True | [] | could-not-evaluate: unavailable required object: the kama history of daf9cd57385ab48dcfd6e72042aa5359885c95c9: git log -z --format=%H%x00%an%x00%at%x00%s daf9cd57385ab48dcfd6e72042aa5359885c95c9 in /f | False | False | False | {"fleet": [], "lane": []} |
| PG25-unknown-citation-plain | c_unknown_citation_plain | 1 | 1 | True | [] |  | False | False | False | {"fleet": [], "lane": []} |
| PROBE-errata-blob-missing | None | 2 | 2 | True | [] | could-not-evaluate: git show 51f8d61968405f9a32de2b1f72673aad3f2a94ab:registry/report-landing-errata.tsv in /fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/probe-3a152jiw/010-PROBE-errata-blob- | False | False | False | {"fleet": [], "lane": []} |

cells: 11; all met: True

Fixture root was removed after the run; the raw evidence is required_reads_probe.json.
