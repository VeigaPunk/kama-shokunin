VERDICT: confirm — 13 reconstructed material citation instances are pinned and verify in the scratch lane.

Scope: scratch clone at `37bd4c5bd456a2f8a54d3312c28495c321715856`; no lane checkout, index, or git state was edited. Preserved the four existing registry rows and added the exact 13-instance population supplied by R18CitationsFind (12 distinct path strings; `runs/c2-survivors.json` has two generations). Registry rows are doc-bound to `corpus/lessons/round-18.md`.

Deliverables under `.ufo/waves/round-20/build/out/R18CitationRows/`:
- `required-citations.json` — base four plus 13 rows.
- `required-citations.patch` — registry-only patch against the fixed scratch base.
- `tokens-fragment.md` — append-only fragment, separate from the full lesson (for integration after the parent’s newer lesson corrections).
- `transcript.txt` — command result and full C2 comparison details.

| Citation path | Source location | Revision | SHA-256 |
|---|---|---|---|
| `.ufo/waves/round-18/live/receipt-1.json` | round-18.md:53 | `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` | `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75` |
| `.ufo/waves/round-18/build/validation-supplement.json` | round-18.md:215 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `b081d09c0c89c8b463610b6b2523a19e1934d36543897284b6b3310412511f03` |
| `.ufo/waves/round-18/build/terminal-evidence.json` | round-18.md:216 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `44b0694d00c03c2b7af9c0f93e7e83aef073be115bb37fc5d8a33051fd2e371f` |
| `.ufo/waves/round-18/falsify/validation.json` | round-18.md:252 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c` |
| `.ufo/waves/round-18/falsify/spec.json` | round-18.md:261 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `ecf2668ad0829c09c27d318bbc5046513254392b15ce4aa9d8834632f3d904df` |
| `.ufo/waves/round-18/build/advice/swarm-registry.json` | round-18.md:270 | `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` | `a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0` |
| `.ufo/waves/round-18/build/dispatch-95.json` | round-18.md:111,270 | `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` | `59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744` |
| `.ufo/waves/round-18/runs/c2-survivors.json` (pre-repair) | round-18.md:272 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829` |
| `.ufo/waves/round-18/runs/c1-measure.exit` | round-18.md:308 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985` |
| `.ufo/waves/round-18/runs/c2-survivors.exit` | round-18.md:308 | `101f3991d3570bc9350fbf9c5561f4be1185699d` | `5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985` |
| `.ufo/waves/round-18/runs/c1-measure.json` | round-18.md:373; SCORECARD:781 | `1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e` | `83e8a1ed95d0c71739aef9f5e1295e14f05d9cc004b56ad19c796ebe1864e1b3` |
| `.ufo/waves/round-18/residual/assignments.json` | round-18.md:394 | `7229fa95eb122310e9e5334ad799ee3006293ebd` | `8d3a9aee251e700319f93210de7bdd945730fdb3d83fc17e5f109451ef389226` |
| `.ufo/waves/round-18/runs/c2-survivors.json` (corrected pre-official) | round-18.md:407; SCORECARD:812 | `1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e` | `8cc59a65d1a23119479354a1a370f29dbc95ed204135761781ae8cf095582f13` |

Executed official argv from scratch lane root: `python3 tools/citation-provenance.py` — exit 0; `required=17 docs_unreadable=0 found=17 verified=17 missing=0 mismatch=0 off_ref=0`. The 13 candidate blob reads and SHA-256 calculations all succeeded (Python Eval returned successfully, exit 0).

C2 comparison: result trees match after normalizing explicit path/time/temporary-PID and captured-stream provenance while retaining all verdicts, arms, witnesses, counts and run statuses. Both docs report 15 named (a6/b3/c2/d1/e3), before survived 11/miscount 1/accepted 3, after killed 11/correct 1/handled 3, inconclusive 0/0; all 15 frozen witnesses match; 42 run-status tuples agree (23 exit 0, 17 exit 1, 2 exit 2). They are not identical full documents: tool SHA differs (`87cad1ca…` pre-official vs `ac934794…` official), run metadata/stream hashes and tails differ, and `bind_guard.summary` has `distinct_ports` 1382 vs 1376, min/max 49154/60999 vs 49176/60991 (binds=1464 both). The frozen escaped-sleep PID differs (one recorded PID in each); two 600-character FC selftest tails differ at their first clipped character. Therefore only outcome-level agreement is supported, not full-document identity.

Provenance caveat: `.ufo/waves/round-18/residual/assignments.json` is absent from all round-18 revisions and first appears at round-19 revision `7229fa9`; the row authenticates those later bytes only. The text labels it retrospective, not contemporaneous round-18 evidence. No selected blob is absent at its specified revision. [INFERENCE] The original `material-citations` scanner is not tracked, so this is the requested reconstructed 13-instance population, not an exhaustive scan of every possible material citation. No tool installs or updates.