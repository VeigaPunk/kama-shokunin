# X2Hist — C2 lane-history: the five mass-deletion events, explained

**Verdict: all five mass-deletion events are explained; the 8 deleted lines that never
returned are 8 intended, documented re-derivations — 0 undocumented, 0 unexplained loss.**
Frozen C2 counter: `tools/append-only-audit.py` (docstring = contract), audited at
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, threshold 20 → exit 1 with
`commits=294 events=5 restored=3 partial=2 unrestored=0` (the exit-1 is the two partials,
both re-derivations, see §3 and §4).

All commands are read-only. No git mutating command ran anywhere; no fixture repo was
created; no lane file was written outside this out directory.

## 1. Commands and receipts

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --json > audit-thr20.json ; echo $?
1                     # summary: commits=294 events=5 restored=3 partial=2 unrestored=0
$ python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --threshold 1 --json > audit-thr1.json ; echo $?
1                     # summary: commits=294 events=66 restored=11 partial=6 unrestored=49
```

Receipts in this directory: `audit-thr20.json`, `audit-thr1.json`. Both name
`"to": "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"`, so they are reproducible at that commit
even though the lane's working HEAD is now `96d329186e777080c03ac89fdd2366714d504dc3`
(read only for context; nothing below reads the working tree).

## 2. The five events (threshold 20, verbatim from `audit-thr20.json`)

| # | commit | file | deleted | restored_at_tip | status | restored_by |
|---|---|---|---|---|---|---|
| 1 | `dd9f5dc6c0e63d038bdd070094d7f38290eeee1b` | SCORECARD.md | 31 | 24 | partial | — |
| 2 | `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` | SCORECARD.md | 2417 | 2416 | partial | — |
| 3 | `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` | LOG.md | 2290 | 2290 | restored | `82b5e9d33a19734a1f33985acabe7021593e9199` |
| 4 | `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` | corpus/QUALITY.md | 375 | 375 | restored | `82b5e9d3…` |
| 5 | `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` | corpus/README.md | 663 | 663 | restored | `82b5e9d3…` |

Two commits produce them: `dd9f5dc6` (round-42 claim work, 2026-10-25 18:14:10 -0300) and
`0718b6ab` (round-45 claim work, 2026-10-26 07:46:53 -0300).

## 3. Events 3–5 (`0718b6ab` LOG/QUALITY/README, restored): the round-45 append bug, repaired byte-exactly

Cause, recorded by the lane itself: the L1's append idiom `open(p,'w').write(open(p).read()+…)`
truncates before it reads, so `0718b6ab` left LOG.md, corpus/QUALITY.md, corpus/README.md and
SCORECARD.md holding only the round-45 appendix. Lesson row:
`corpus/lessons/round-45.md:30` (class `stale-premise`, "(5) Commit `0718b6ab` landed
SCORECARD.md, LOG.md, corpus/QUALITY.md and corpus/README.md truncated to the round-45
appendix … fix: Restored from `21945c61` plus the appendix in `82b5e9d3`; read before opening
for write").

Repair commit `82b5e9d3` says so in its subject: "round-45: restore SCORECARD/LOG/QUALITY/README
bodies truncated by the previous commit (append bug) and re-append round-45 text; SKILL v2 row
flags; depth re-anchor".

The repair is an append, not a rewrite — `git diff --numstat 0718b6ab^1 82b5e9d3 -- SCORECARD.md
LOG.md corpus/QUALITY.md corpus/README.md`:

```
7   0   LOG.md
17  1   SCORECARD.md     <- one deletion: the depth row, §4
4   0   corpus/QUALITY.md
4   0   corpus/README.md
```

and a common-prefix check (lines of `82b5e9d3:<file>` compared with `0718b6ab^1:<file>`):
LOG.md 2296/2296 base lines identical (7 appended), corpus/README.md 667/667 identical
(4 appended), corpus/QUALITY.md 376/377 (5 appended; the 377th line is the file's trailing
empty line, so the KQ62–KQ65 rows are pure additions). So all three restored events are the
same accidental truncation, fully repaired in the next commit, and documented as a mistake.
Classification: **accident, repaired, documented; no content lost.**

## 4. Event 2 (`0718b6ab` SCORECARD, 2417 deleted / 2416 restored): the one line that did not come back was re-derived

Same truncation, same repair. The single deleted line absent at the tip is deleted-line #12 of
the diff:

```
| depth | **7** | `SKILL.md` sha256 `91440eb8ff4220d647b2b99378a48cb7dc93a3425aedd66ff4ae6f817db4c63b` (1420 lines); run `grep -c '^## ' SKILL.md` → `32`; `corpus/knowledge/endpoint-identity.md` sha256 `0100ac6d…` (218 lines) | score round 1; evidence re-anchored round 44 |
```

(`git -C <lane> diff --no-renames -U0 0718b6ab^1 0718b6ab -- SCORECARD.md`, line #12 of 2417
deleted; 494 of the 2417 are blank lines.)

**What replaced it:** the depth row re-derived in the same repairing commit, now
`SCORECARD.md:16`:

```
| depth | **7** | `SKILL.md` sha256 `3046955b2fd5140a9439dee7ff1c67d7d03432a4c4ca73870b1393d805ef7297` (1432 lines); run `grep -c '^## ' SKILL.md` → `33`; … | score round 1; evidence re-anchored round 45 |
```

**The replacement value re-derives, and the old value was true when written:**

```
$ git -C <lane> cat-file -p ef76777e:SKILL.md | sha256sum     # round-44 integration
91440eb8ff4220d647b2b99378a48cb7dc93a3425aedd66ff4ae6f817db4c63b  -
$ git -C <lane> cat-file -p ef76777e:SKILL.md | wc -l
1420
$ git -C <lane> cat-file -p 82b5e9d3:SKILL.md | sha256sum     # the repairing commit
3046955b2fd5140a9439dee7ff1c67d7d03432a4c4ca73870b1393d805ef7297  -
$ git -C <lane> cat-file -p 4a2a4d55:SKILL.md | sha256sum     # audited tip
3046955b2fd5140a9439dee7ff1c67d7d03432a4c4ca73870b1393d805ef7297  -
```

So the round-44 row was correct at round 44 and stale at round 45 (SKILL.md grew 1420 → 1432
lines inside `0718b6ab` itself), and the repair replaced a stale anchor with a measured one.

**Recorded?** Yes, twice: `LOG.md:2301` — "SCORECARD head re-anchored (banner, calibration row
spot-check count 31, **depth hash**)" — and the commit subject's "depth re-anchor"; the row's own
Last-change cell says "evidence re-anchored round 45" (`SCORECARD.md:16`).

Classification: **the mass deletion was an accident (documented, §3); the one non-returned line
is an intended re-derivation, documented.** No content lost.

## 5. Event 1 (`dd9f5dc6` SCORECARD, 31 deleted / 24 restored / 7 lost): round-42 claim C1 rewrote the head

`dd9f5dc6` is the round-42 claim-work commit: "round-42: claim work — SCORECARD head and
README/PROVINCE reconciled (C1); …". `git diff --numstat dd9f5dc6^1 dd9f5dc6 -- SCORECARD.md`
→ `98 31 SCORECARD.md`.

**The 24 "restored" lines are a move, not an append.** 22 content lines were re-added verbatim
inside the new `## Historical head sections (superseded in round 42)` block
(`SCORECARD.md:137`–`183`): the round-5 banner at `143-150`, §Planned text at `154-158`, the
declared-vs-served context note at `160-162`, §Retired text at `166-171`; the other two are the
`## Saturation` heading, back at its original place `133`, and one blank line at 2446
— 23 content + 1 blank = 24. `restored_at_tip` cannot tell
this move apart from an in-place append (§7 note 2).

**The 7 lines that never returned** are exactly the replaced head — deleted-lines #9–#15:

| deleted # | old line (head) | replaced by | classification | recorded at |
|---|---|---|---|---|
| 9 | "Reconciled in round 41 against the measured commit … claim C1 …" (484 ch) | the re-derived `## Axes` paragraph, `SCORECARD.md:10`, which prefixes `Round 43 re-anchors …` / `Round 42 added, to every row, one axis-specific run fact …` and **keeps the round-41 sentence verbatim as its suffix** (checked: the deleted line is a substring of tip line 10; its closing clause "its freshness 7 and coverage 8 predate the round-10 moves to 8 and 9" is intact) | intended re-derivation (documented) | `LOG.md:2267`, `SCORECARD.md:2253`, `corpus/lessons/round-42.md:50` |
| 10 | `\| **operability** \| **8** \| registry gate … test-snapshot pass=30 … report-landing-audit 79 … sources-append-only 42/42 …` (571 ch) | `SCORECARD.md:14`: score **8** unchanged, same `kama-probe.sh` sha256 `36b64978…` (1138 lines), same `test-snapshot.sh RESULT pass=30 fail=0`, same `report-landing-audit` 79 / `sources-append-only` 42/42, **plus** the new axis fact `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0` | intended re-derivation (documented) | same |
| 11 | `\| **freshness** \| **8** \| …` (399 ch) | `SCORECARD.md:15`: score **8**, same harness sha256 `236c23c1…` (194 lines), same `citation-provenance` 24 cases, **plus** the round-41 drift receipt and the recheck-cadence count | intended re-derivation (documented) | same |
| 12 | `\| depth \| **7** \| … 151023b9… (1375 lines) …` (291 ch) | `SCORECARD.md:16` at `dd9f5dc6`: same sha256 `151023b9…` (1375 lines, re-measured below), **plus** `grep -c '^## ' SKILL.md` → 30 | intended re-derivation (documented) | same |
| 13 | `\| coverage \| **9** \| … PROVINCE.md dbb5f4f7… (169 lines) …` (358 ch) | `SCORECARD.md:17` at `dd9f5dc6`: score **9**, `PROVINCE.md` re-anchored `dbb5f4f7…(169)` → `5abc9fdf…(181)`, **plus** knowledge-entry count 35 | intended re-derivation (documented) | same |
| 14 | `\| calibration \| **7** \| …` (398 ch) | `SCORECARD.md:18` at `dd9f5dc6`: score **7**, same two selftests, **plus** the verifier-spotcheck closure count 28 | intended re-derivation (documented) | same |
| 15 | `\| adjacency \| **7** \| …` (307 ch) | `SCORECARD.md:19` at `dd9f5dc6`: score **7**, same `cross-lane-scope.md` sha256 `1801cb7f…` (87 lines), **plus** table-pipe line count 14 | intended re-derivation (documented) | same |

No score moved in any of the six rows (8/8/7/9/7/7 before and after), so this is a re-anchor,
not a rescore. Every replacement value was **measured, not typed**: at `dd9f5dc6`,
`git cat-file -p dd9f5dc6:SKILL.md | sha256sum` → `151023b99bec115e…` and 1375 lines,
`PROVINCE.md` → `5abc9fdfcfb57640…` (181 lines), `tools/kama-probe.sh` → `36b64978ee3a3aa2…`
— each equal to the text of the row that replaced the deleted line.

**Recorded?** Yes, in four places:
- `LOG.md:2267` (round-42 C1 bullet): "The head sections were re-derived from the tree and the
  round-5 text moved verbatim under §Historical head sections; README names every top-level
  entry; PROVINCE names every instrument the capability list cites …; each axis row carries one
  axis-specific run fact" (routed defect R41A03).
- `SCORECARD.md:2253` (round-42 C1 claim row, `calibration 7 → 7`).
- `corpus/lessons/round-42.md:50` (mistake row, class `stale-premise`, fix "Head sections
  re-derived and the old text kept verbatim under §Historical head sections …; KQ52 widens KQ49
  to the whole head").
- Each row's own Last-change cell (`SCORECARD.md:14-19`, "evidence re-anchored round 42").

Classification: **all 7 intended re-derivation, documented.**

## 6. Lost-line tally

| event | lost lines | intended re-derivation (documented) | intended, undocumented | loss |
|---|---|---|---|---|
| `dd9f5dc6` SCORECARD.md | 7 | 7 | 0 | 0 |
| `0718b6ab` SCORECARD.md | 1 | 1 | 0 | 0 |
| `0718b6ab` LOG/QUALITY/README | 0 | — | — | 0 |
| **total** | **8** | **8** | **0** | **0** |

## 7. What the counter can and cannot say (semantics, not defects — the docstring fixes them)

1. **`restored_at_tip` is line-exact.** The round-41 paragraph survives as a substring of the
   re-derived `SCORECARD.md:10` but reads "lost" because the line text changed. Correct per the
   docstring ("deleted lines (exact text) occurring as some line"); a reader must not conclude
   text loss from a partial status alone.
2. **A verbatim move counts as restored.** `dd9f5dc6`'s 24 lines were relocated into
   §Historical head sections, not retained in place; the counter sees only "present at tip".
3. **`restored_by` is null for both partials** because no later commit re-holds the *superset*
   of the deleted text. Right by definition, but it means the field cannot name the replacing
   commit — the intent in §4/§5 had to come from `LOG.md`, the lesson rows and the diff.
4. **Consequence for the claim:** at the frozen threshold, `exit 1` on this lane history means
   "two heads to explain", not "two defects". Both are re-derivations with measurement and
   record. Any future reader that treats the exit code as an append-only violation would be
   wrong about this lane.

## 8. Threshold-1 census (`audit-thr1.json`) — context, outside the frozen claim

`commits=294 events=66 restored=11 partial=6 unrestored=49`. Deleted-line mass per status:
restored n=11 (sum 3353; dominated by `0718b6ab`'s 2290+375+663), partial n=6 (sum 2484; the
two above plus `ed135b3c` LOG 7/2, `e246c40e` README 2/1, `44fa5627` SCORECARD 9/1,
`ef76777e` SCORECARD 18/13), unrestored n=49 (sum **152** lines, min 1, max 18 —
`83bee7fa` SCORECARD.md 18, then `f1e755e0` corpus/SOURCES.md 11). Files: SCORECARD.md 23,
corpus/SOURCES.md 20, LOG.md 13, corpus/README.md 8, corpus/QUALITY.md 2.

The unrestored tail is ordinary in-place editing of append-only files (one row or line group
rewritten per commit, ≤ 18 lines, 152 lines across 49 commits — less than a tenth of a single
one of the five frozen events). That is the population the frozen threshold 20 deliberately
excludes. I did **not** classify those 49 line-by-line: they are outside C2's frozen predicate
("every commit deleting >= 20 lines"); doing so would be a new preregistration, not this
claim.

## 9. Evidence index (lane paths, tip `4a2a4d55`)

- `SCORECARD.md:10` re-derived §Axes paragraph (carries the round-41 sentence); `:14-19` the six
  re-derived rows; `:16` the depth row `3046955b…` (1432 lines); `:137-183` §Historical head
  sections; `:2253` round-42 C1 row.
- `LOG.md:2267` round-42 C1 bullet (head re-derived, rows given one run fact); `:2301` round-45
  "SCORECARD head re-anchored (banner, calibration row spot-check count 31, depth hash)".
- `corpus/lessons/round-42.md:50` stale-premise mistake row (head re-derivation, KQ52).
- `corpus/lessons/round-45.md:30` truncation mistake row (5) with the fix and the restore commit.
- Commits: `dd9f5dc6` (round-42 claim work), `0718b6ab` (round-45 claim work, truncated the four
  files), `82b5e9d3` (restore + depth re-anchor), `ef76777e` (round-44 integration; SKILL.md
  `91440eb8…`, 1420 lines), `4a2a4d55` (audited tip, the C2 tool commit).
