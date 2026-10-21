# Evidence — RevengeOmissionCause (kama round 21)

Commands run by this seat, absolute paths; exit as observed. Read-only: no lane or fleet writes. Tool calls (`_read`, `_grep`) are listed without an exit code.

| # | Command (abridged) | Exit | Observed |
|---|---|---|---|
| 1 | `git -C /home/vgpnk/Projects/shokunin log -p -- .ufo/reports/round-20/kama.md` | 0 | One commit, 04eb5d2 "round-20: kama report" (+67). Full diff in session artifact 41652. |
| 2 | `git -C /home/vgpnk/Projects/shokunin log --format='%h %ad %s' -- .ufo/reports/round-{18,20}/kama.md` | 0 | 23bdc3f 2026-10-21 02:39:12; 04eb5d2 07:13:14. |
| 3 | `git -C /home/vgpnk/Projects/shokunin show --stat --format=fuller 04eb5d2` and `23bdc3f` | 0 | Single added report file each (+67; +163). |
| 4 | `git -C …/kama-shokunin log -n 90 --date=iso --format='%H %h %ad %an <%ae> \| %s'` | 0 | Round commits in order; checkpoint 101f399 "…; unadmitted"; 33a6777 04:05:09; 7a6bc911 07:10:48; a29bb84 07:24:53 (round 21). |
| 5 | `git log --no-walk=unsorted --shortstat` on 16 r18/r20 commits | 0 | Parents form one linear chain. Files: 33a6777 377; 0957ce61 13; 92b1462 72; 846e366 4; c7311039 84; 04de7a8 68; 9add96e 68; 3ec5ea6 67; 7a6bc91 1; c6dc46f 169; 1c325b2 116; 101f399 96; 0c75c61 8; 888cd38 10; eb78788 1; 1b85a24 27. |
| 6 | `git show --name-only` per commit, `cut`/`sort`/`uniq -c` | 0 | 33a6777: build 323 of 377. 0957ce61: SKILL.md 1, build 7, c1 1, c2 2, recipe.json 1, evidence 1. 92b1462: runs 64 (runs/0957ce61), falsify 5, lesson/SCORECARD/LOG 1 each. c7311039: falsify 77 (73 reports + 4 accounting JSON), gguf fixture script and expected.json 1 each, corpus 3 (lesson, knowledge entry, SOURCES), SCORECARD/LOG 1 each. 04de7a8: runs 64 (runs/c7311039), c2 1, lesson/SCORECARD/LOG 1 each. 9add96e: runs 64 (runs/04de7a87), c2 1, lesson/SCORECARD/LOG 1 each. 3ec5ea6: runs 64 (runs/9add96e4), lesson/SCORECARD/LOG 1 each. 7a6bc91: LOG.md 1. |
| 7 | `git log --diff-filter=A -- .ufo/waves/round-20/falsify/{dispatch-attempts,completion-summary,seat-failures,verdict-count}.json` | 0 | All four first added by c731103. |
| 8 | `git log -- .ufo/waves/round-20/falsify` and `round-18/falsify` | 0 | r20: 92b1462, 846e366, c731103. r18: c6dc46f (first), 101f399 (advice files AppendCells.md … ReopenS049.md). |
| 9 | `git log -- .ufo/waves/round-20/runs/{c7311039,04de7a87,9add96e4,0957ce61}` | 0 | First added by 04de7a8, 9add96e, 3ec5ea6, 92b1462 respectively. |
| 10 | `git log --format='%h %s' -S'<phrase>' -- LOG.md` (six phrases) | 0 each | "landed implementation and committed measurement" → 33a6777; "corrections to round-19 records" → 33a6777; "measured c6dc46f and counter-interface" → 1c325b2; "recovery attempt 2" → 1b85a24; "Wave-2 integration" → c731103; "R20 falsify wave" → c731103. |
| 11 | python: extract 40-hex tokens from both reports; `git cat-file -e <h>^{commit}`; `git merge-base --is-ancestor <h> HEAD` | script ran | r18 l.75, 78, 80, 82, 90 exist and are ancestors. r20 l.7 MISSING (cat-file exit 128). r20 l.10, 15-19, 25, 26 exist and are ancestors. Splice: `0957ce619789d13d894ef21bc863486bcb35b56c`[:15] == 0957ce61[:15]; [15:] == 33a6777[15:] (True). |
| 12 | `python3 -B /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py` | 0 | reports=11 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 status=clean. |
| 13 | `python3 -B …/tools/report-landing-audit.py --no-errata` | 1 | defects=9 uncorrected=9 status=failed. Per round: r10 1, r18 3, r20 5 (r19 0, post_report 4). |
| 14 | `git show 5434376:.ufo/reports/round-17/kama.md`; `git show ac9859f:.ufo/reports/round-19/kama.md` (headers) | 0 | r17 header: build 54a29268 (measured) and falsify evidence 5e9ae6e. r19: "(attempt 1)". Landed lists for r17 and r19 were read from the fleet working copy. |
| 15 | `_grep` on `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log` for `complete kama\|launch kama` | tool | 536-537 "lane-dead-no-report kama round=18; retry same round" then "launch kama round=18 attempt=2"; 542 "complete kama round=18; attempt=2" at 02:39:37; 562 "launch kama round=20 … attempt=1" at 04:06:01; 583 "launch kama round=21" at 07:17:03; no "complete kama round=20" through line 585. |
| 16 | `_grep` on r20 report for `92b1462\|846e366\|33a6777\|0957ce6\|c7311039\|3ec5ea6\|7a6bc91` | tool | No hits for 92b1462, 846e366, 33a6777. 0957ce6 at l.7 (splice) and l.10. Landed hashes at l.15-19. |
| 17 | `_grep` on LOG.md, SCORECARD.md, corpus/lessons/round-18.md, round-20.md for the omitted and landed hashes | tool | 92b1462, 846e366, 3ec5ea6 and 7a6bc91 have no hits. 33a6777, 0957ce61, c6dc46f, 1c325b2, 101f399 and the r18 closure hashes do. |
| 18 | `_read` PROTOCOL.md:109-137 and 145-203; templates/round-prompt.md (grep l.107-108); PROTOCOL-APPENDIX.md (grep) | tool | Landed rules quoted in the report. |
| 19 | `_read` LOG.md:1084-1135 and 1170-1252; corpus lesson round-18 l.263-266 and round-20 l.3, 86, 93-98 | tool | "Attempt 1 died…"; "Re-verified and reused"; "No earlier round-20 attempt inherited". |
| 20 | `_read` round-10 report 1-43, 107-125; registry/report-landing-errata.tsv; watchdog.log:527-545 | tool | r10 l.30 "All changes are in lane commit 1e41928"; l.114 post-review 4066035. Errata row 3 "first 16 hex … last 24 hex" (exact 15 + 25). |
| 21 | python: read `git show 0957ce61:SKILL.md` lines 649-660 | 0 | Table rows at 652-658. Report l.10 says 652-656; LOG.md:1251 says 652-654 for the same routed rows (descriptive drift only). |

Not run: any build, test, live server, model download, or lane/fleet mutation. Tools installed: none.
