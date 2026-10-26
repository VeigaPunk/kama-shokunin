# What happened to the lane's own proposals — considerthese 2026-10-22 … 2026-10-26

Draft for the round-47 lesson (considerthese/2026-10-26.md:31 proposal 2). Read-only: `considerthese/` was not edited; every cell carries `file:line` in the lane repo.

**Tally: 20 numbered proposals. 8 landed (3 as QUALITY criteria, 3 as capabilities in admitted rounds, 1 as a tool registered in a rejected round, 1 as a registry in an admitted round), 2 were adopted only in the reflection series, 1 is a pointer that was never implemented, 1 was deferred by name and is still open, 6 were never named by any round, 2 are in flight in round 47.**

## 1. Table

| # | Proposal (file:line) | Round that took it up / deferred it (file:line) | Closure verdict (file:line) |
|---|---|---|---|
| 1 | 2026-10-22.md:20 — separate author verdict from outside admission in every reflection | no round; adopted inside the reflection series itself: `considerthese/2026-10-23.md:5-10`, `2026-10-24.md:5-10`, `2026-10-25.md:5-11`, `2026-10-26.md:5-13` | no closure verdict; 0 occurrences of `considerthese/2026-10-22.md` in any preregistration or lesson (`refs-listing.txt`, count=0) |
| 2 | 2026-10-22.md:22 — daily calibration-candidate scouting (SCORECARD/SHONEN statements false at master) | no round by name; the practice exists as the C1 statement-audit relay: `tools/round35-statement-audit.py` … `tools/round38-statement-audit.py`, criterion `corpus/QUALITY.md:289` (KQ39) | no verdict on the proposal; nearest outside reading `corpus/lessons/round-35-verifier-spotcheck.md:73` (calibration improved, C1) |
| 3 | 2026-10-22.md:24 — between-round drift watch for registered instruments | no round; nearest instrument predates the proposal (`corpus/QUALITY.md:203`, KQ36, round 25) and fires only at landing | no verdict; 0 occurrences (`refs-listing.txt`, count=0) |
| 4 | 2026-10-22.md:26 — split infrastructure friction from lane learning | no round; fleet-side faults are recorded ad hoc, not as an operator-side note: `corpus/lessons/round-34.md:102` (provider spawn failure), `corpus/lessons/round-46.md:36` (wave-stall-blind, round-45 wave 64 seats / 0 turns) | no verdict; 0 occurrences (`refs-listing.txt`, count=0) |
| 5 | 2026-10-23.md:29 — shortcut-class ledger across rounds | round 34, carried only as a frontier pointer, explicitly not implemented: `corpus/lessons/round-34.md:107-111`; `.ufo/waves/round-34/preregistration.json:54` | `corpus/lessons/round-34-verifier-spotcheck.md:69` — "present in the file and is carried as lesson frontier item 1, explicitly not implemented … Disposition is grounded, not a silent drop"; the round's claims were verified at `:40`, `:51` |
| 6 | 2026-10-23.md:31 — check scoring-before-amendment timing from git and seat logs | no round took it; named as a round-43 candidate in `corpus/lessons/round-42.md:74` and not taken in round 43 (`corpus/lessons/round-43.md:60-62` names other items) | no verdict; nearest instrument `tools/prereg-time-check.py` (statement timestamps, not score ordering) |
| 7 | 2026-10-23.md:33 — track true-but-unadmitted knowledge separately from scores | no round; the two later ledgers measure agreement and claim outcomes, not true-but-unadmitted rows (`corpus/lessons/round-44.md:11`, `corpus/lessons/round-45.md:11`) | no verdict; 0 occurrences in preregs/lessons (`refs-listing.txt`, count=0) |
| 8 | 2026-10-23.md:35 — mark in-flight rounds and the tip read | no round; adopted in the reflection series: `considerthese/2026-10-24.md:3`, `2026-10-25.md:3`, `2026-10-26.md:3` ("Tip read for this pass: …") | no verdict; 0 occurrences (`refs-listing.txt`, count=0) |
| 9 | 2026-10-24.md:27 — track outside verdicts against score movement per axis | round 35 → criterion KQ44: `corpus/lessons/round-35.md:57`; `corpus/QUALITY.md:316` | not a claim; `corpus/lessons/round-35-verifier-spotcheck.md:73` records calibration improved for C1, and the closure does not rule on KQ44 |
| 10 | 2026-10-24.md:29 — re-open every new SOURCES row's quote at its cited line | round 36 → criterion KQ45: `corpus/lessons/round-36.md:81`; `corpus/QUALITY.md:322`; re-applied round 39 (`corpus/lessons/round-39.md:33`) | `corpus/lessons/round-36-verifier-spotcheck.md:196` "**Admitted**" (`:146-147` calibration/coverage unchanged); round-39 re-application admitted at `corpus/lessons/round-39-verifier-spotcheck.md:86` |
| 11 | 2026-10-24.md:31 — "prepared, not dispatched" ledger | deferred twice by name and never taken: `corpus/lessons/round-37.md:84`, `corpus/lessons/round-38.md:98`; the underlying question is filed operator-side at `corpus/lessons/round-33-verifier-spotcheck.md:70` | no verdict (no ledger and no claim exists) |
| 12 | 2026-10-24.md:33 — count attempts and restarts per round | round 38 → criterion KQ47: `corpus/lessons/round-38.md:98` ("taken as KQ47 — this round runs as attempt 2"); `corpus/QUALITY.md:334` | `corpus/lessons/round-38-verifier-spotcheck.md:69` "KQ47 criterion added with its lesson/evidence"; `:43` calibration improved |
| 13 | 2026-10-25.md:27 — recompute every digest and S-id a new lesson or row cites | r40 C1 (`.ufo/waves/round-40/preregistration.json:36`; `corpus/lessons/round-40.md:30` "applied in bounded form") → r42 C2 digest half (`.ufo/waves/round-42/preregistration.json:34`) → r43 C2 65-char/abbrev class (`.ufo/waves/round-43/preregistration.json:33`) | r40 **rejected-honest-stop** (`corpus/lessons/round-40-verifier-spotcheck.md:105`); r42 admitted (`round-42-verifier-spotcheck.md:7`) with operability improved (`:74`); r43 admitted (`round-43-verifier-spotcheck.md:7`) with operability improved (`:73`) |
| 14 | 2026-10-25.md:29 — watch version pins for upstream releases | r40 deferred (`corpus/lessons/round-40-verifier-spotcheck.md:80` "reject (defer)"); r41 C2 (`.ufo/waves/round-41/preregistration.json:34,50`; `corpus/lessons/round-41.md:12,123`); r44 as the consumer of a `behind` result (`.ufo/waves/round-44/preregistration.json:165`; `corpus/lessons/round-44.md:41`) | r41 admitted (`round-41-verifier-spotcheck.md:7`) with operability improved (`:55`); r44 admitted (`round-44-verifier-spotcheck.md:7`) with freshness improved (`:75`) |
| 15 | 2026-10-25.md:31 — ledger of staged items the lane keeps rejecting | r42 deferred (`.ufo/waves/round-42/preregistration.json:67` "proposals 3 and 4 remain unimplemented"); r43 implemented as `registry/staged-refusals.tsv` (`.ufo/waves/round-43/preregistration.json:64`; `corpus/lessons/round-43.md:62`; criterion `corpus/QUALITY.md:365` KQ57) | round-43 closure admitted (`round-43-verifier-spotcheck.md:7`); the registry is not a claim, so no verdict names it |
| 16 | 2026-10-25.md:33 — report seat yield per wave | r45, as a lane tool: `.ufo/waves/round-45/preregistration.json:65`; `corpus/lessons/round-45.md:21` → `tools/seat-yield.py` | `corpus/lessons/round-45-verifier-spotcheck.md:115` operability unchanged, "two new checks with selftests (`tools/seat-yield.py`, …) are registered"; the round's own verdict is rejected-honest-stop on C2, a different claim (`:7`) |
| 17 | 2026-10-26.md:29 — flag deletions in append-only files the morning after | r46 C2 (`.ufo/waves/round-46/preregistration.json:129,150`; `corpus/lessons/round-46.md:11`) | `corpus/lessons/round-46-verifier-spotcheck.md:13` "**admitted**"; `:108` calibration improved |
| 18 | 2026-10-26.md:31 — track what happens to my own proposals | r47, frontier seat `S8Proposals` (`.ufo/waves/round-47/w1/build_spec.py:166-167`; this file) | pending — `.ufo/waves/round-47` has no closure yet (`corpus/lessons/round-47-verifier-spotcheck.md` absent) |
| 19 | 2026-10-26.md:33 — running count of counters a shortcut can satisfy | r47, mined as a lesson row/script from the round-46 closure's D3 (`.ufo/waves/round-46-verifier-spotcheck.md:139`): `.ufo/waves/round-47/preregistration.json:56,62`; `.ufo/waves/round-47/w1/build_spec.py:133-134` (`X9Tally`) | pending — round-47 closure absent |
| 20 | 2026-10-26.md:35 — report the pin gap every morning | no round; `grep -rn "pin gap" corpus/lessons/ .ufo/waves/round-4*/preregistration.json` returns no tracking artifact (only an unrelated `round-24.md:579` phrase) | no verdict; 0 occurrences of `considerthese/2026-10-26.md proposal 4` (`refs-listing.txt`, count=4 lines for the file, none for proposal 4) |

## 2. Negative checks (how the "no round" cells were established)

All run at the lane root, read-only; full output in `refs-listing.txt`.

```
grep -rn "considerthese/2026-10-22.md" .ufo/waves/round-*/preregistration.json corpus/lessons/round-*.md   # 0 hits
grep -rn "considerthese/2026-10-23.md" …                                                                    # 4 hits, all round 34
grep -rn "considerthese/2026-10-24.md" …                                                                    # 7 hits, rounds 34–39 (lessons only)
grep -rn "considerthese/2026-10-25.md" …                                                                    # 16 hits, rounds 40–45
grep -rn "considerthese/2026-10-26.md" …                                                                    # 4 hits, rounds 46–47
```

`grep` exits 2 on the 14 round directories that have no `preregistration.json` (rounds 11–23 and 39); those errors are why the command is quoted with `2>/dev/null` in `refs-listing.txt`.

## 3. Coverage of the tracking mechanism itself

- 23 rounds carry a `preregistration.json`; 9 carry a `considerthese` field — rounds 34, 40, 41, 42, 43, 44, 45, 46, 47 (`refs-listing.txt`, census block).
- Rounds 35, 36, 37 and 38 have a preregistration with **no** `considerthese` field; round 39 has no preregistration at all. For proposals 10 and 12 the only pointer from round artifact to proposal is lesson prose (`round-35.md:57`, `round-36.md:81`, `round-38.md:98`).
- Two preregistrations name a proposal without the file path and are invisible to the grep above: `.ufo/waves/round-43/preregistration.json:64` (2026-10-25 proposal 3) and `.ufo/waves/round-44/preregistration.json:165` (2026-10-25 proposal 2).

## 4. Findings

**F1 — the tracking field is new and partial.** 9 of 23 preregistrations carry `considerthese`; the field appears only from round 40 onward except round 34. Command: the census block in `refs-listing.txt`. Proposed fix (next round, not this one): add `considerthese` to the preregistration template and make a round that takes up no proposal write `"considerthese": "none"`, so silence becomes distinguishable from an unrecorded uptake.

**F2 — the reflection's own count of its 2026-10-25 proposals is one short.** `considerthese/2026-10-26.md:31` says "three of the four 2026-10-25 proposals became rounds 41 to 43"; proposal 4 landed in round 45 as `tools/seat-yield.py` (`corpus/lessons/round-45.md:21`, `.ufo/waves/round-45/preregistration.json:65`), which round 45's closure records at `corpus/lessons/round-45-verifier-spotcheck.md:115`. Four of four were taken up. Proposed fix: state 4/4 in the lesson row with the round-45 cite.

**F3 — pointer decay.** Proposal 5 (10-23 P1, the shortcut-class ledger) is carried as round 34's frontier item 1 (`corpus/lessons/round-34.md:107-111`) and the string `considerthese/2026-10-23.md` never appears again in any preregistration or lesson after round 34 (4 hits, all round 34). A frontier pointer is not a durable tracker. The nearest later artifact is the round-47 shortcut tally, which answers the different question of 10-26 P3 (`build_spec.py:133-134`). Proposed fix: give each frontier-carried proposal a line in a registry TSV so it ages visibly.

**F4 — oldest open item.** Proposal 11 (10-24 P3, prepared-not-dispatched ledger) has been deferred by name in rounds 37 and 38 (`round-37.md:84`, `round-38.md:98`), filed operator-side at `round-33-verifier-spotcheck.md:70`, and is still absent from `registry/` at the tip. It is the only proposal with an explicit, repeated deferral and no artifact.

**F5 — "mined" in a preregistration does not mean admitted.** Round 40's preregistration says C1 "also implements" 10-25 P1 (`.ufo/waves/round-40/preregistration.json:36`), while the closure rejects that claim (`round-40-verifier-spotcheck.md:105`). Counting landed proposals from preregistrations alone therefore overcounts by one. The proposal only truly landed at round 42 (`round-42-verifier-spotcheck.md:7`).

**Observation (not a defect) — re-consumption happens.** A proposal already landed can be re-applied: 10-24 P2 (KQ45, round 36) is exercised again in round 39 (`corpus/lessons/round-39.md:33`) against a new row, and 10-25 P2 is re-read in round 44 as the consumer of a `behind` result (`corpus/lessons/round-44.md:41`). A tracker keyed only on "first round" would miss both.
