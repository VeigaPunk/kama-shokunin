VERDICT: refute - extension below round 10 is not honest as-is: `--rounds 1-9` exits 2 at round 3, and the 10 raw defects are 9 format/extractor artifacts plus 1 substantive omission
# AuditEarlyRounds: kama rounds 1-9 landing audit (read-only)

Setup: lane `master` = `HEAD` = a29bb84; lane script and errata are `cmp`-identical to a scratch clone at a29bb84 (exit 0). Fleet HEAD 7fd7c785. Python 3.14.8, git 2.56.0 (queried only). Nothing installed or updated; no lane edits; no processes started.

## Commands run (exit observed)
1. `python3 tools/report-landing-audit.py --rounds 1-9 --no-errata` -> 2; stdout empty; stderr `could-not-evaluate: round 3: cannot read .../round-3/kama.md`.
2. Same with `--json` -> 2; stdout empty.
3. `--rounds N --no-errata` (plus `--json`) for N=1..9 and `--rounds 1,2,4,6-9` -> 1 for N in {1,2,4,6,7,8,9} and for the set; 2 for N in {3,5}.
4. Default errata ledger: `--rounds 1` -> 1 (`errata_unmatched=9`); `--rounds 1-9` -> 2; `--rounds 1,2,4,6-9` -> 1 (`errata_unmatched=9`).
5. `git -C <fleet> log --diff-filter=A --format=%H%x09%ct -- .ufo/reports/round-N/kama.md` (N=1..9) -> 0; empty for N=3,5.
6. `git log --format=... a29bb84` (scratch) -> 0: 82 commits, 66 by kama-shokunin; 60 of 66 match the population subject rule.
7. `git ls-tree -r --name-only a29bb84 -- .ufo/reports` (scratch) -> 0; only `.ufo/reports/round-5/kama.md`.
8. `git show --stat` on 10 round commits -> 0; section extraction by `exec` of the script's own functions (no import, no bytecode written).
Outputs: `.ufo/waves/round-21/build/out/AuditEarlyRounds/` (per-run stdout/stderr, JSON, `official-rounds-1-9.exits.txt`, `classification.md`).

## Per-round outcome (`--no-errata`; text and JSON exits agree)
| round | fleet report | exit | raw defects | class |
|---|---|---|---|---|
| 1 | present, 2026-09-29T02:15:55Z | 1 | landed-section-missing; landed-omitted c6199a25 | heading-name convention; hash header-cited |
| 2 | present, 2026-09-29T04:36:12Z | 1 | landed-section-missing | heading-name convention; plus silent miss of 83bee7fa |
| 3 | absent | 2 | none | could-not-evaluate (correct) |
| 4 | present, 2026-10-15T00:24:03Z | 1 | landed-omitted 84a81304, 47f3aedd, 0505b718 | 2 hash-format; 1 substantive (47f3aedd) |
| 5 | absent in fleet | 2 | none | could-not-evaluate (correct); lane copy exists |
| 6 | present, 2026-10-18T18:35:59Z | 1 | landed-omitted f396b989 | extractor artifact |
| 7 | present, 2026-10-18T18:38:51Z | 1 | landed-omitted 4bcae65a | extractor artifact |
| 8 | present, 2026-10-18T18:40:53Z | 1 | landed-omitted d0f5a2d2 | extractor artifact |
| 9 | present, 2026-10-18T18:43:16Z | 1 | landed-omitted 35e9175f | extractor artifact |

## Findings
- **Exit 2 is correct and limited to rounds 3 and 5.** Round 3: lane commit `ea72c3ea` ("round-3: re-census ...") with no report in fleet or lane; round 4's `c390918f` is "record the round-3 report gap". Round 5: `15a733c0` adds `.ufo/reports/round-5/kama.md` to the lane repo only. The range form aborts at the first missing report (`audit_round` raises at script L106-109; `main` returns 2 at L394-398), so `1-9` yields no per-round data.
- **Ten raw defects, rounds 1-9:** extractor artifact 4 (r6-9); heading-name convention 2 (r1-2, `## What landed`); hash-citation convention 3 (r1 c6199a25 and r4 84a81304 are header-cited at L4; r4 0505b718 is uncited but its only file is named in Landed); substantive omission 1 (r4 47f3aedd changed `corpus/knowledge/endpoint-identity.md`, which the Landed list at L25-28 does not name; the file appears only as carried debt at L49).
- **Extractor artifact (r6-9):** the heading is `## Landed changes (lane repo, commit <sha>)`. `landed_section()` (L79-82) returns only the body, so the heading hash is never seen; JSON shows `cited_elsewhere=true`. Docstring rule (L15-19): "that `## Landed changes` does not cite by a >=7-hex prefix". [INFERENCE: heading-inclusive reading was intended, so these four are false positives.]
- **Silent false negative:** round 2's only landed commit `83bee7faf5a7...` has subject exactly `round-2`. Rule L88 `^(?:round-[0-9]+:|checkpoint\(r[0-9]+\))` misses it, so required=0 (true count 1; committed 1m56s before the r2 report; header-cited at L4). Other non-matching kama commits are non-round subjects, e.g. `117c4b20` "plans: WWKD re-census plan for this round" (2026-10-15T00:31:49Z) [INFERENCE: round-5 planning].
- **Blocked rounds without Landed:** not observed in 1-9. Rounds 6-9 are blocked-with-data and each has the heading; round 5's lane copy has one (L42). Only rounds 1-2 lack it, and neither is blocked.
- **Declared 10-20 headings** (grep `^## (Landed|What landed)`, 11 reports): all bare `## Landed changes` with no hash in the heading, so the heading artifact does not show there. Early rounds use other conventions. [Body-level check for 10-20 not done.]

## Is extending below round 10 honest? No, as-is.
- The official 1-9 run can never give a verdict (exit 2). Any honest 1-9 statement must say "could-not-evaluate for 3 and 5" and report the rest per round, as in the table, never as an aggregate defect count.
- Raw 1-9 failures would overstate misreporting: 9 of 10 defects are format or extractor artifacts; the one substantive omission is a 2-line corpus edit. [INFERENCE: weighting.]
- Subset runs need `--no-errata`: with the default ledger, the rows for rounds 10/18/20 are all errata-unmatched and every subset run fails.
- Any extension must disclose the round-2 subject blind spot and the heading exclusion.
- No change to the declared C1 population is proposed (per assignment).

## Lane note
`tools/__pycache__/report-landing-audit.cpython-314.pyc` exists (mtime 2026-10-21 10:45:27Z). My commands never imported the module, so I did not create it [INFERENCE: another process]. Not touched.

## Not done
No analysis of rounds 10-20 beyond headings; no selftest run; no C1 official count run; no installs. Scratch `/tmp/kama-r21-AuditEarlyRounds` removed (rm -rf, exit 0).
