# X2Hist — C2 lane-history findings (round 46, w1)

**Verdict: all five frozen-threshold mass-deletion events are explained; the 8 deleted lines that never returned are 8 intended, documented re-derivations — 0 undocumented re-derivations, 0 unexplained loss.** No defect found in `tools/append-only-audit.py` or in the lane's records; two calibration notes on what the counter's predicate can say (below) and one output-correctness note on the "restored" line that is a move.

## Evidence

### Commands and exit codes

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --json > …/X2Hist/audit-thr20.json ; echo $?
1
    → {"to":"4a2a4d55…","threshold":20,"commits":294,"events":5,
       "summary":{"commits":294,"events":5,"restored":3,"partial":2,"unrestored":0}}
$ … same with --threshold 1 --json > …/X2Hist/audit-thr1.json ; echo $?
1
    → {"threshold":1,"summary":{"commits":294,"events":66,"restored":11,"partial":6,"unrestored":49}}
```

Both receipts name `"to": "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"`; the lane's working HEAD is now `96d329186e777080c03ac89fdd2366714d504dc3`, which the audit does not read. All git calls were read-only (`git -C <lane> show|cat-file|diff|rev-list|log`); no git mutating command ran anywhere, no fixture repo was created, and no lane file was written outside this out directory.

### The five events (threshold 20)

| commit | file | deleted | restored_at_tip | status | restored_by |
|---|---|---|---|---|---|
| `dd9f5dc6c0e63d038bdd070094d7f38290eeee1b` | SCORECARD.md | 31 | 24 | partial | — |
| `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` | SCORECARD.md | 2417 | 2416 | partial | — |
| `0718b6ab…` | LOG.md | 2290 | 2290 | restored | `82b5e9d3…` |
| `0718b6ab…` | corpus/QUALITY.md | 375 | 375 | restored | `82b5e9d3…` |
| `0718b6ab…` | corpus/README.md | 663 | 663 | restored | `82b5e9d3…` |

### Explanations (detail and per-line ledger in `X2Hist/events.md`)

**`0718b6ab` LOG/QUALITY/README (restored) and SCORECARD 2417/2416 — the round-45 append bug.**
`0718b6ab` is round-45 claim work; the L1's `open(p,'w').write(open(p).read()+…)` idiom truncated before reading, leaving four declared files holding only the round-45 appendix. Recorded as a mistake by the lane: `corpus/lessons/round-45.md:30` (class `stale-premise`, "(5) Commit `0718b6ab` landed SCORECARD.md, LOG.md, corpus/QUALITY.md and corpus/README.md truncated to the round-45 appendix … fix: Restored from `21945c61` plus the appendix in `82b5e9d3`"). Repair commit `82b5e9d3` says so in its subject. The repair is an append, verified: `git diff --numstat 0718b6ab^1 82b5e9d3 -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md` → `7/0 LOG.md`, `17/1 SCORECARD.md`, `4/0 corpus/QUALITY.md`, `4/0 corpus/README.md`; common-prefix check → LOG.md 2296/2296 base lines identical, corpus/README.md 667/667 identical, corpus/QUALITY.md 376/377 (the 377th base position is the trailing empty line; KQ62–KQ65 are pure additions). The single SCORECARD deletion is the depth row.

**`0718b6ab` SCORECARD, the one line that did not return — re-derived, documented.** Deleted-line #12 of 2417 (494 are blanks) is the depth row citing `SKILL.md` sha256 `91440eb8…` (1420 lines), "evidence re-anchored round 44". At the repairing commit it is replaced by the row now at `SCORECARD.md:16`, `SKILL.md` sha256 `3046955b…` (1432 lines), `grep -c '^## '` → 33, "evidence re-anchored round 45". Both values are true at their commits: `cat-file -p ef76777e:SKILL.md | sha256sum` → `91440eb8…`, `wc -l` → 1420; `cat-file -p 82b5e9d3:SKILL.md | sha256sum` → `3046955b…`, 1432; `4a2a4d55` → `3046955b…`, 1432. Recorded at `LOG.md:2301` ("SCORECARD head re-anchored (banner, calibration row spot-check count 31, depth hash)") and in the commit subject ("depth re-anchor"). Classification: accident (documented) whose single non-returned line is an intended re-derivation (documented).

**`dd9f5dc6` SCORECARD 31/24 — round-42 claim C1 rewrote the head.** `git diff --numstat dd9f5dc6^1 dd9f5dc6 -- SCORECARD.md` → `98 31`. The 24 "restored" lines are a **move**: 22 content lines re-added verbatim inside the new `## Historical head sections (superseded in round 42)` block (`SCORECARD.md:143-150` banner, `154-158` planned, `160-162` context note, `166-171` retired), plus the `## Saturation` heading back at `133` and one blank = 24. The 7 non-returned lines are deleted-lines #9–#15: the round-41 reconciliation paragraph and the six `## Axes` rows, each replaced in the same commit:

- #9 → the re-derived §Axes paragraph at `SCORECARD.md:10`, which **carries the round-41 sentence verbatim as its suffix** (verified as a substring of tip line 10; its closing clause "its freshness 7 and coverage 8 predate the round-10 moves to 8 and 9" is intact). Line-exact scoring reads it as lost.
- #10–#15 → the six rows at `SCORECARD.md:14-19`. **No score moved** (8/8/7/9/7/7 before and after); each old evidence pointer is kept and extended with one axis-specific run fact (round-42 C1, routed defect R41A03) and re-anchored where the tree moved (`PROVINCE.md` `dbb5f4f7…(169)` → `5abc9fdf…(181)`, closure count 24 → 28, adjacency pipe lines 14). The replacement values were measured, not typed: at `dd9f5dc6`, `cat-file -p dd9f5dc6:SKILL.md | sha256sum` → `151023b99bec115e…` / 1375 lines, `PROVINCE.md` → `5abc9fdf…` / 181 lines, `tools/kama-probe.sh` → `36b64978…` — each equal to the text of the row that replaced the deleted line.

Recorded in four places: `LOG.md:2267` (round-42 C1: "The head sections were re-derived from the tree and the round-5 text moved verbatim under §Historical head sections; … each axis row carries one axis-specific run fact"), `SCORECARD.md:2253` (round-42 C1 claim row), `corpus/lessons/round-42.md:50` (stale-premise mistake row, KQ52), and each row's Last-change cell (`SCORECARD.md:14-19`).

### Tally

| event | lost | intended re-derivation (documented) | intended, undocumented | loss |
|---|---|---|---|---|
| `dd9f5dc6` SCORECARD.md | 7 | 7 | 0 | 0 |
| `0718b6ab` SCORECARD.md | 1 | 1 | 0 | 0 |
| `0718b6ab` LOG/QUALITY/README | 0 | — | — | 0 |
| **total** | **8** | **8** | **0** | **0** |

### Counter semantics (notes, not defects — the docstring fixes them)

1. `restored_at_tip` is **line-exact**, so a reworded/superseded line reads "lost" even when its sentence survives inside the new line (the #9 case). Not text loss.
2. It cannot distinguish an in-place append from a **verbatim move** — `dd9f5dc6`'s 24 were relocated into §Historical head sections.
3. `restored_by` is null for both partials by definition (no later commit re-holds the superset); it therefore cannot name the replacing commit, and intent must come from `LOG.md` / lessons / the diff.
4. Consequence: at the frozen threshold, `exit 1` on this lane means "two heads to explain", not "two violations". Both are measured re-derivations.

### Threshold-1 census (context, outside the frozen predicate)

66 events, 11 restored (sum 3353, dominated by `0718b6ab`'s 2290+375+663), 6 partial (sum 2484; adds `ed135b3c` LOG 7/2, `e246c40e` README 2/1, `44fa5627` SCORECARD 9/1, `ef76777e` SCORECARD 18/13), 49 unrestored (sum **152** lines, min 1, max 18 — `83bee7fa` SCORECARD.md 18, `f1e755e0` corpus/SOURCES.md 11). Files: SCORECARD.md 23, corpus/SOURCES.md 20, LOG.md 13, corpus/README.md 8, corpus/QUALITY.md 2. The unrestored tail is ordinary in-place row editing, ≤ 18 lines per commit, 152 lines total across 49 commits — the population the frozen threshold 20 deliberately excludes. I did not classify those 49 line-by-line; that would be a new preregistration, not C2.

## Risks / limits

- The classification rests on the *replaced* text being a superset/re-derivation of each lost line; for #10–#15 I compared pointer-by-pointer and re-measured the hashes at `dd9f5dc6`, and for #9 on substring survival at the tip. I did not exhaustively diff every clause of the six replaced rows.
- The 49 sub-threshold unrestored events are unexamined beyond their census (stated above). Two of them exceed 10 lines (`83bee7fa` SCORECARD.md 18, `f1e755e0` corpus/SOURCES.md 11) but are below the frozen threshold.

## Blockers

None. No tool was installed or upgraded; no pacman transaction; no scratch clone (git reads went straight to the lane's own object store, which is read-only by construction here). Scratch `/fast/scratch/hyaku/kama-r46/X2Hist` removed.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Hist.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Hist/events.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Hist/audit-thr20.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Hist/audit-thr1.json`
