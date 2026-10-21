# AuditEarlyRounds: per-round classification (`--no-errata`; text and JSON exits agree)

Lane a29bb84 (= master). Fleet reports `/home/vgpnk/Projects/shokunin/.ufo/reports/round-N/kama.md`.

| round | fleet report (first add, UTC) | exit | raw defect (kind, token) | class |
|---|---|---|---|---|
| 1 | present, 2026-09-29T02:15:55Z | 1 | landed-section-missing `-`; landed-omitted c6199a2542440db77d69918599e5a378ee116337 | heading-name convention; hash cited in header L4, no Landed section |
| 2 | present, 2026-09-29T04:36:12Z | 1 | landed-section-missing `-` | heading-name convention (`## What landed`); population miss: 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 (subject `round-2`) not counted |
| 3 | absent | 2 | none (could-not-evaluate) | correct; lane commit ea72c3ea exists, no report in fleet or lane |
| 4 | present, 2026-10-15T00:24:03Z | 1 | landed-omitted 84a81304d7b0c77c84fe495f3bb728e8729faaff; 47f3aedd6fa3ccfdde47a03c11f9e1342a7d8f7f; 0505b718dde47f7a85088795626d494619d30198 | 84a81304 header-cited, 0505b718 uncited with its sole file named (hash-format x2); 47f3aedd substantive (endpoint-identity.md not named in Landed) |
| 5 | absent in fleet (lane copy at 15a733c0) | 2 | none (could-not-evaluate) | correct on declared path; path-level gap |
| 6 | present, 2026-10-18T18:35:59Z | 1 | landed-omitted f396b98945407374ee116e93453b04b0c396c200 | extractor artifact: hash only in heading `## Landed changes (lane repo, commit ...)` |
| 7 | present, 2026-10-18T18:38:51Z | 1 | landed-omitted 4bcae65a23f58186c826ef2f793b029f3f9f8405 | extractor artifact (same heading form) |
| 8 | present, 2026-10-18T18:40:53Z | 1 | landed-omitted d0f5a2d2b2e5cbfd9674e57fd3d90970df92ab92 | extractor artifact (same heading form) |
| 9 | present, 2026-10-18T18:43:16Z | 1 | landed-omitted 35e9175fc543b8090ba436a5f8c6b8b1c768339a | extractor artifact (same heading form) |

Range `--rounds 1-9 --no-errata` (text and `--json`): exit 2, stdout empty, stderr `could-not-evaluate: round 3: cannot read ...`.
Raw totals for rounds 1-9 (seven evaluable reports): 10 defects; landed-section-missing 2, landed-omitted 8, landed-unresolved 0, unresolved-full-hash 0.
