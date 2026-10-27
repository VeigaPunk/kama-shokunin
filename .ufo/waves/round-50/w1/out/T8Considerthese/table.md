# What happened to the lane's own proposals — considerthese 2026-10-22 … 2026-10-26 (updated through round 50)

Round-50 wave seat `T8Considerthese` (`.ufo/waves/round-50/build_spec.py:182-183`), leaf, read-only on the lane.
Snapshot **2026-10-26** (pass written during the round-50 w1 wave). Lane tip read: `3b79eaddf38246c637cc7ba1a94ab363422876b6`
(`git log --oneline -1`). Round-50 build `97c864bead3ee4a2f629574e77263d33834ec98a`, freeze
`601c8889f33d1797c712feb753974c20cf891264`, base `26ecba64ad6fb571d09074b07202d1618a46ecd1`. The wave is **in flight**:
`find .ufo/waves/round-50/w1/out -name '*.md'` → 3 files, 29 seat dirs, no `w1-results.json`
(`python3 tools/seat-yield.py .ufo/waves/round-50/w1` → `could-not-evaluate`, exit 2); round-50 SCORECARD/LOG/QUALITY/lesson
entries do not exist yet (`grep -n "^## Round 50" LOG.md` → 1 hit at `:2331` = round 49; `SCORECARD.md:2813` is still
`## Round 49`; `ls corpus/lessons/` has no `round-50.md`).

Base: `.ufo/waves/round-49/w1/out/S8Considerthese/table.md` (`R49T:<line>`). Rounds ≤ 49 columns are **inherited** from
that table (which inherited rounds ≤ 48); they were re-checked here only where a round-50 artifact contradicts or
extends them (rows 3, 10, 14, 16, 17, 19, and every R50 cell). Evidence commands with exit codes: `commands.txt`
in this directory.

**Tally, 20 numbered proposals.** After round 50: **3 landed lane artifacts** (rows 13, 15, 17 — row 17's daily half still
missing), **1 landed-but-regressed** (row 19, frozen population), **1 landed-but-not-run** (row 14), **1 landed-but-dropped
from the measured set** (row 16), **3 criterion-only** (rows 9, 10, 12), **2 practice-only** (rows 1, 8), **2 delivered as a wave
artifact only** (rows 18, 20), **1 partial** (row 2), and **6 unimplemented** (rows 3, 4, 5, 6, 7, 11 — §3). Round 50 takes up
**no proposal by name** (§0) and, for the second round running, leaves no machine-readable pointer to what it mined.

## 0. What round 50 takes up

| Where round 50 would say it | Observed at the snapshot |
|---|---|
| Preregistration `frontier.considerthese` | **absent.** `.ufo/waves/round-50/preregistration.json` keys are `['lane','round','attempt','author','frozen_at_utc','base','authority','separability','claims','controls','limits']` (`commands.txt` §2). Rounds 46, 47, 48 carry it (`.ufo/waves/round-46/preregistration.json:150`, `round-47:56`, `round-48:55`), rounds **49 and 50 do not** |
| Lesson line (`## Claims` tail) | **absent and not requested.** Round 50's lesson seat asks for `## Claims` / `## Gate` / `## Mistakes` with columns `Class, evidence, captured-by, fix` and says nothing about proposals (`.ufo/waves/round-50/build_spec.py:174-175`); `corpus/lessons/round-49.md` has 0 `considerthese|proposal` hits, so the pointer has now been missing for rounds 48 and 49 |
| `LOG.md ## Round 50` | **absent.** `grep -n "^## Round 49\|^## Round 50" LOG.md` → `2331` only (round 49) |
| `SCORECARD.md` round-50 section | **absent.** Latest canonical heading is `SCORECARD.md:2813` (`## Round 49 — the replay execution witness …`); the authority banner still reads "Latest measured round: 49" (`SCORECARD.md:6`) |
| Wave spec | only two seats touch a proposal's substance, neither by name: `S1Rows2` (`.ufo/waves/round-50/build_spec.py:164`, re-open the new SOURCES rows = row 10) and this seat (`:182-183`); `X6Sao2` (`:153`) exercises the SOURCES append guard |
| Counter/receipt instruments re-run | the measured set (`measure.sh:20-39`, 20 runs) re-runs rows 13 (`:28-29`), 17 (`:31-32`) and 19 (`:36`); **rows 14 and 16 are absent from it entirely** |

Round 50's two claims are routed from the **round-49 outside closure** (`.ufo/waves/round-50/preregistration.json` C1
statement cites "closure R2, seat X1Kill" / "closure R1, seats K1Design, R0Controls"; C2 cites "round-49 seats K2Origin
F3-F5, K2Cheat; closure R3"), i.e. from `corpus/lessons/round-49-verifier-spotcheck.md` — a legitimate non-author route, and
again **not** from `considerthese/`. Proposal uptake is therefore zero and unrecorded, exactly as in round 49.

## 1. Table

Abbreviations: `R49T:<line>` = `.ufo/waves/round-49/w1/out/S8Considerthese/table.md`; `W:` = `.ufo/waves/round-50/`;
`C:` = this directory (`commands.txt` section quoted).

| # | Proposal (file:line) | ≤46 (inherited) | R47 | R48 | R49 (inherited) | **R50** | Status after round 50 |
|---|---|---|---|---|---|---|---|
| 1 | `considerthese/2026-10-22.md:20` — separate author verdict from outside admission in every reflection | no round by name; adopted inside the reflection series (`considerthese/2026-10-26.md:5-13`); `R49T:32` | not named (`R49T:32`) | not named | not named, no artifact (`R49T:32`) | **practice only, still no join.** The daily file carries the two-verdict table (`considerthese/2026-10-26.md:5` header `\| Round \| Author claims \| Outside verdict (spot-check file) \|`, rows `:7-13`), but round 50's own record keeps the author's claim (`W:preregistration.json:5` `"author"`, `:10-37` claims) and the outside verdict in different files with no field tying them; the only outside verdict at the tip is `corpus/lessons/round-49-verifier-spotcheck.md:11` (`Verdict: **admitted**`) | **partial** (reflection series only; no lane artifact) |
| 2 | `considerthese/2026-10-22.md:22` — daily calibration-candidate scouting (SCORECARD/SHONEN statements false at master) | no round by name; practice exists as frozen relays `tools/round35-statement-audit.py` … `round38-statement-audit.py`; `R49T:33` | not named | not named | not named, no artifact (`R49T:33`) | **not named, no artifact, and the relay family did not grow.** `ls tools/round*-statement-audit.py` → `round35`…`round38` only (nothing since round 38); `grep -n "pin-watch\|seat-yield\|statement" W:measured/measure.sh` → 0 (`C:` §3). The only calibration-candidate check that runs is the planned-pointer scan (`W:measured/measure.sh:27`), receipt `W:measured/pointer-build.out:6` `met=True`, which checks that a pointer names an existing section — not that a statement is false | **unimplemented** (§3.2) |
| 3 | `considerthese/2026-10-22.md:24` — between-round drift watch for registered instruments | no round; nearest instrument KQ36 fires only at landing; `R49T:34` | not named | not named | not named; drift found *after* it existed (`R49T:34`) | **not named; three live drift instances found at the build again.** `W:measured/r41-build.out:3` `mismatches=1 met=False` and `W:measured/r42-build.out:3-4` (calibration run expects stdout `35`, `no stdout line == '35'`); `W:measured/r43-build.out:3-6` `mismatches=4 met=False`, `selftest=1` because "documented `GATE_SELFTEST pass=6 fail=0`, run printed `pass=5 fail=1`". A between-round watcher would have flagged all three before the build; today they surface only because `W:measured/measure.sh:24-26` happens to re-run them | **unimplemented** (§3.1) |
| 4 | `considerthese/2026-10-22.md:26` — split infrastructure friction from lane learning | no round; fleet faults recorded ad hoc; `R49T:35` | not named | not named | not named, and one instance of the mixing (`corpus/lessons/round-49.md:36`) | **not named; round 50 will add another ownerless row.** The Mistakes schema has no owner column — `corpus/lessons/round-49.md:32` header is `\| # \| Class \| Evidence \| Captured-by \| Fix (shown able to fail) \|` — and round 50's lesson seat requests exactly that shape (`.ufo/waves/round-50/build_spec.py:174-175`), while the last round's row 3 is orchestrator/operator-owned with nothing in the row saying so (`corpus/lessons/round-49.md:36`) | **unimplemented** (§3.2) |
| 5 | `considerthese/2026-10-23.md:29` — shortcut-class ledger across rounds | round 34 declined it as not a measurement (`corpus/lessons/round-34.md:107-111`); `R49T:36` | not named | not named | not named; nearest artifact is the promoted per-round tally (`R49T:36`) | **not named; still per-round, not per-class.** `grep -n -- '--classes' tools/shortcut-tally.py` → 0 hits; the receipt's columns are rounds (`W:measured/tally-build.out:3` `round  shortcuts  ids  counters  cheats  mutants  falsify  status`), and its population stops before the two rounds that carry the most attack seats (`:4-11`, ends at `47`) | **unimplemented** (§3.3) |
| 6 | `considerthese/2026-10-23.md:31` — check scoring-before-amendment timing from git and seat logs | no round; named a round-43 candidate and not taken; `R49T:37` | not named | not named | not named; nearest instrument compares a file to its own commit (`R49T:37`) | **not named; the existing leg passes and still cannot answer the question.** `W:freeze/prereg-time-check.out:3-4` `ok line 6: 2026-10-27T00:20:47Z (at/before commit)` / `RESULT pass`; there was no amendment to test (`git log --oneline -- .ufo/waves/round-50/preregistration.json` → one commit, `601c8889`). Nothing joins the dispatch wall-clock (`W:w1.ready.dispatched:1` = `2026-10-26T21:54:00`) with the first seat evidence it produced | **unimplemented** (§3.4) |
| 7 | `considerthese/2026-10-23.md:33` — track true-but-unadmitted knowledge separately from scores | no round; the two later ledgers measure agreement/claim outcomes; `R49T:38` | not named | not named | not named, no artifact (`R49T:38`) | **not named, no artifact, and both nearest ledgers are now stale.** `grep -rln "unadmitted" tools/ registry/ SKILL.md` → only `registry/report-landing-errata.tsv`; `registry/verdict-ledger.tsv` mtime `2026-10-26T05:10` and `registry/claim-outcome-ledger.tsv` `07:45` both predate rounds 49-50, and neither is in `W:measured/measure.sh:20-39` | **unimplemented** (§3.5) |
| 8 | `considerthese/2026-10-23.md:35` — mark in-flight rounds and the tip read | no round; adopted in the reflection series; `R49T:39` | not named | not named | practice (`corpus/lessons/round-49.md:3-7`), wave state in files (`R49T:39`) | **practice, and the wave state is no longer durable.** Round-50 prereg pins `base` and `frozen_at_utc` (`W:preregistration.json:6-7`); the dispatch state lives in `W:w1.ready:1` and `W:w1.ready.dispatched:1` (`2026-10-26T21:54:00` + 66-seat map), but `git status --porcelain` prints `?? .ufo/waves/round-50/w1.ready` and `?? .ufo/waves/round-50/w1.ready.dispatched` — untracked, unlike round 49's pair (`git ls-files` → both tracked) | **practice**; this snapshot is the only record |
| 9 | `considerthese/2026-10-24.md:27` — track outside verdicts against score movement per axis | round 35 → criterion KQ44 (`corpus/QUALITY.md:316`); `R49T:40` | not named | not named | not named; instrument absent from the measured set (`R49T:40`) | **not named; instrument exists and did not run for the third round.** `ls tools/ \| grep -i verdict` → `round44-verdict-ledger-audit.py`; `W:measured/measure.sh:20-39` has no line invoking it, and `registry/verdict-ledger.tsv` (mtime `2026-10-26T05:10`) carries no round-49 or round-50 row | **criterion landed round 35**; instrument idle since round 44-45 |
| 10 | `considerthese/2026-10-24.md:29` — re-open every new SOURCES row's quote at its cited line | round 36 → KQ45 (`corpus/QUALITY.md:322`); re-applied round 39; `R49T:41` | not named | not named | re-applied unnamed (`R49T:41`) | **re-applied, unnamed, and this round's population is three rows.** Seats `S1Rows2` (`.ufo/waves/round-50/build_spec.py:164`) and `N5Sources2` (`:138`) re-open S496-S498 (`corpus/SOURCES.md:249,250,251`); the append oracle passes **at the tip** (`sources-append-only.py --from 26ecba64 --to 3b79eadd` → `added S496 (allowed)`, `added S497 (allowed)`, `added S498 (allowed)`, `no append-only violations`, exit 0) but the committed build receipt fails (`W:measured/sao-build.out:2` `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row`, exit 2) because it predates the tick-parity fix `3d42897b` | **criterion landed round 36**; re-applied |
| 11 | `considerthese/2026-10-24.md:31` — "prepared, not dispatched" ledger | deferred twice by name; `R49T:42` | not named | not named | not taken, but its inputs materialised (`R49T:42`) | **not taken, and its inputs are now durable for one round and not the other.** `ls registry/` → no `prepared-waves.tsv`; round 49's `w1.ready` + `w1.ready.dispatched` are tracked (`git ls-files`), round 50's are untracked (`git status --porcelain`). `W:w1/spec.json` carries 66 items and `W:w1/dispatch.json` the seat map, so a row per wave is a join, not a new measurement | **unimplemented** (§3.6) |
| 12 | `considerthese/2026-10-24.md:33` — count attempts and restarts per round | round 38 → KQ47 (`corpus/QUALITY.md:334`); `R49T:43` | not named | not named | substance present, unnamed (`R49T:43`) | **substance present, unnamed, and only one datum exists.** `W:preregistration.json:4` `"attempt": 1`; no round-50 lesson or report exists yet to carry it, and KQ47 asks the report to (`corpus/QUALITY.md:334`) | **criterion landed round 38** |
| 13 | `considerthese/2026-10-25.md:27` — recompute every digest and S-id a new lesson or row cites | r40 C1 → r42 C2 → r43 C2; `R49T:44` | not named | not named | in continuous use (`R49T:44`) | **in continuous use, unnamed, and red on one leg.** `W:measured/measure.sh:28` digest → `W:measured/digest-build.out:2` `unknown=0`, exit 0; `:29` hexrun → `W:measured/hexrun-build.out:2-3` `unknown=1`, exit **1**, and the receipt does not name the token. Re-run at the tip with `--details`: `f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 class=unknown`, which is the round-49 report commit in the **fleet** repo, cited at `corpus/lessons/round-49-verifier-spotcheck.md:21`; `git cat-file -t` → fatal (not a lane object) and `registry/hexrun-ledger.tsv` has no row (`grep -c` → 0), though a fleet-repo precedent row exists (`registry/hexrun-ledger.tsv:2`) | **landed (r40/r42/r43)**; one leg red since round 49 (F4) |
| 14 | `considerthese/2026-10-25.md:29` — watch version pins for upstream releases | r40 deferred; r41 C2; r44 consumer; `R49T:45` | re-consumed (seat `U2Pins`) | re-consumed (seat `U2Pins`) | re-consumed a third time (seat `U2Pins`, `W:w1/out/U2Pins.md`) | **regressed: `pin-watch` did not run at all in round 50.** `grep -c "pin-watch" W:measured/measure.sh` → 0; the wave has **no pin seat** — `spec.json` U-names are `['U1Fresh']` (`.ufo/waves/round-50/build_spec.py:82`), and `grep -n "pin-watch" .ufo/waves/round-50/build_spec.py` → 0 hits. Last artifact: `.ufo/waves/round-49/w1/out/U2Pins.md` (mtime 20:34). `registry/engine-pins.tsv:4` still pins llama.cpp `b11755 S038` and `grep -c b11909 registry/engine-pins.tsv` → **0**, while C1's three replays all rest on b11909 (`W:preregistration.json:16`) | **landed round 41**; instrument dark in round 50 |
| 15 | `considerthese/2026-10-25.md:31` — ledger of staged items the lane keeps rejecting | r42 deferred; r43 implemented `registry/staged-refusals.tsv` (KQ57); `R49T:46` | not named | not named | landed, untouched (`R49T:46`) | **landed, untouched, and still unread.** `registry/staged-refusals.tsv` mtime `2026-10-26T01:03`, 20680 bytes — older than rounds 49 and 50; `grep -rn "staged-refusals" .ufo/waves/round-50/ tools/*.py` → 0 hits | **landed round 43** (closure admitted `corpus/lessons/round-43-verifier-spotcheck.md:7`); registry, not a claim |
| 16 | `considerthese/2026-10-25.md:33` — report seat yield per wave | r45 → `tools/seat-yield.py`, KQ62 (`corpus/QUALITY.md:377`), `SKILL.md:1431`; `R49T:47` | in use (`SCORECARD.md:2721`) | dropped from the regression set (`R49T:47`) | dropped again; ran only as a late finding in round 49 (`R49T:47`) | **still absent from the measured set, and now unrunnable at build.** `grep -c "seat-yield" W:measured/measure.sh` → 0; `python3 tools/seat-yield.py .ufo/waves/round-50/w1` → `could-not-evaluate: no *-results.json or results.json`, exit 2; the wave is 66 seats (`W:w1/spec.json` items: executor 22, reviewer 10, scribe 10, critic 6, connector 5, mutation-tester 4, scout 4, sentinel 3, revenger 1, simplifier 1) and at the snapshot holds 3 reports / 29 seat dirs. Round 49's receipt recorded `wave=w1 seats=71 status=unknown:71 reports=71 missing=0` (`.ufo/waves/round-49/measured/seat-yield-w1.out:1`), so the instrument worked one round ago and is not wired now | **landed round 45**; dropped from the measured set two rounds running (F3) |
| 17 | `considerthese/2026-10-26.md:29` — flag deletions in append-only files the morning after | r46 C2 → r47 promotion attempt → r48 C1 v3 → r49 C2 v4; `R49T:48` | not named | not named | extended again (v4) (`R49T:48`) | **extended to v5, unnamed, and the daily-pass half is still missing.** `tools/append-only-audit.py:2,4` announce the v5 definitions and `:573` emits `"definition": "v5"`; round 50's C2 (`W:measured/c2-build.out:2` `fixture=1 lane=1 scenarios=12/12 met=True`) closes F3-F5 of the round-49 closure. `grep -n -- '--since' tools/append-only-audit.py` → **0 hits**, so "the morning after" still has no windowed mode; the lane receipt is whole-history (`W:measured/aoa-build.out` summary `commits=327 … ungraded_lines=89`) | **landed round 46**; v5 rounding at round 50 |
| 18 | `considerthese/2026-10-26.md:31` — track what happens to my own proposals | r47 seat `S8Proposals`; `R49T:49` | taken up | taken up | taken up a third time (`R49T:49`) | **taken up a fourth time, and the lane's machine-readable record of it is gone again.** Seat `T8Considerthese` `.ufo/waves/round-50/build_spec.py:182-183`; output is this file. No closure has ever ruled it (F5): `grep -cE "considerthese\|proposal\|tally" corpus/lessons/round-49-verifier-spotcheck.md` → 0, on the closure that admitted the round carrying round 49's table (`:11`). Uptake itself is unrecorded (§0) | **delivered as a wave artifact each round** |
| 19 | `considerthese/2026-10-26.md:33` — running count of counters a shortcut can satisfy | r47 mined (round-46 closure D3), seat `X9Tally`; `R49T:50` | taken up | taken up (promoted to `tools/` with `--check`) | instrument runs, population frozen at round 47 (`R49T:50`) | **instrument runs, population still frozen — third round.** `W:measured/measure.sh:36` calls it with no `--rounds`; the default is `tools/shortcut-tally.py:895` `default="40-47"`; the receipt prints `rounds=40-47` (`W:measured/tally-build.out:2`) and its last data row is `47` (`:20`). Re-run at the tip: `rounds=40-47`. Rounds 48 (69 seats, 34 attack seats), 49 and 50 are never tallied, so the proposal cannot answer its own question two rounds after promotion | **landed round 47**; population stale (F3) |
| 20 | `considerthese/2026-10-26.md:35` — report the pin gap every morning | round-47 table said "no round"; seat `U2Pins` already ran; `R49T:51` | taken up in substance, unnamed | named for the first time (`fleet .ufo/reports/round-48/kama.md:73`) | taken up by seat again, unnamed (`R49T:51`) | **not taken in round 50, and the instrument it depends on did not run** (row 14). `considerthese/2026-10-26.md`'s proposal block is `:29-35` and none of the four is a pin line; no artifact in `W:` prints a newest-tag / releases-above-pin figure (`grep -rn "pin-watch\|newest" W:measured/*.out` → 0). The gap it would report is now material: C1 rests on b11909 while `registry/engine-pins.tsv:4` pins b11755 | **not taken this round** |

## 2. Evidence and counts

### 2.1 Proposal pointers per round (preregistration `frontier.considerthese`)

```
round 46  present  "…proposal 1 (flag deletions…), implemented as C2."
round 47  present  "…proposal 3 (running count…) mined as the lesson's sufficiency-family row"
round 48  present  "…proposal 3 …: the round-47 shortcut tally is promoted to tools/ with its --check"
round 49  ABSENT
round 50  ABSENT
```
Command: `python3 -c "…for r in (46,47,48,49,50)…"` (`commands.txt` §2), exit 0.

### 2.2 Instrument coverage of the 20 proposals in the round-50 measured set

`W:measured/measure.sh` has 20 `run` lines (`:20-39`). Mapping to proposal rows:

| Proposal row | Instrument | Line in `measure.sh` | Receipt at the build | Live at the tip? |
|---|---|---|---|---|
| 13 | `digest-ledger.py` | `:28` | `unknown=0`, exit 0 (`digest-build.out:2`) | yes |
| 13 | `hexrun-census.py` | `:29` | `unknown=1`, exit 1 (`hexrun-build.out:2-3`) | yes, red (F4) |
| 17 | `sources-append-only.py` | `:30` | exit 2 (`sao-build.out:2`) | passes at tip (`added S496-S498`, exit 0) |
| 17 | `append-only-audit.py` | `:31-32` | `ungraded_lines=89 regressed=0`, exit 0; selftest `pass=36 fail=0` | yes |
| 19 | `shortcut-tally.py` | `:36` | `rounds=40-47`, exit 0 (`tally-build.out:2`) | runs, population stale |
| 1, 9 | `round44-verdict-ledger-audit.py` | **absent** | — | ledger mtime `2026-10-26T05:10` |
| 14 | `pin-watch.py` | **absent** | — | not run in round 50 at all (no seat either) |
| 16 | `seat-yield.py` | **absent** | — | exit 2 at the snapshot (no `*-results.json`) |
| 2 | statement-audit relays | **absent** | — | newest is `round38-statement-audit.py` |
| 5 | `shortcut-tally.py --classes` | **absent (no such flag)** | — | no |

### 2.3 Registry surfaces a ledger proposal would write to

`ls registry/` → no `prepared-waves.tsv` (row 11), no `per-round-instruments.tsv` (round-49 F7's proposed fix); present and
stale: `verdict-ledger.tsv` (05:10), `claim-outcome-ledger.tsv` (07:45), `staged-refusals.tsv` (01:03), `engine-pins.tsv`
(01:03), `hexrun-ledger.tsv` (no row for `f8cdb853…`).

## 3. Still unimplemented — six proposals and what one round would need

The six are unchanged from `R49T:§3` (rows 3, 4, 5, 6, 7, 11). Each sketch is updated with what round 50 now provides as
free input; none requires a new capability in the SCORECARD sense, and all six are read-only over data the lane already
commits.

**3.1 Proposal 3 — between-round drift watch for registered instruments** (`considerthese/2026-10-22.md:24`). What one round
needs: `tools/anchor-drift-watch.py` that (a) reads each `SKILL.md` registry row and each `SCORECARD.md` capability row,
(b) derives the anchor paths from the row's command (`--pins registry/engine-pins.tsv`, `--receipt …`, `--files …`),
(c) finds the last commit with a receipt for that instrument under `.ufo/waves/round-*/measured/`, and (d) exits 1 when any
anchor was touched after that receipt. Round 50 supplies the fixtures for free: the three real drifts it caught at build
(`r41-build.out:3-4` stale `35`, `r42-build.out:3-4` same, `r43-build.out:3-6` documented `pass=6 fail=0` vs run
`pass=5 fail=1`) are three fails the watcher must reproduce, and the frozen `measure.sh:24-26` is the passing case.

**3.2 Proposal 4 — split infrastructure friction from lane learning** (`considerthese/2026-10-22.md:26`). What one round
needs: an **owner column** on every routed defect and every Mistakes row (`lane` / `orchestrator` / `operator`), plus a
checker that classifies each row from the closure's own `**R4 (orchestrator/operator, …)**` prefix
(`corpus/lessons/round-48-verifier-spotcheck.md:113`), fails when an `orchestrator`/`operator` defect sits under
`## Mistakes`, and counts lane-owned rows per round. Round 50 is the round to do it: the lesson seat's row schema is being
written right now (`.ufo/waves/round-50/build_spec.py:174-175` requests `Class, evidence, captured-by, fix`, no owner), and
`corpus/lessons/round-49.md:36` is the standing failing fixture.

**3.3 Proposal 5 — shortcut-class ledger across rounds** (`considerthese/2026-10-23.md:29`). What one round needs: a
`--classes` view of `tools/shortcut-tally.py` whose rows are classes (echo literal, help text, type conversion, projected
bounds, relabel, dropped row, fake witness, stub server) and whose columns are first-seen round, rounds repeated, and
whether a later counter refused it. The input is already machine-read: `tools/shortcut-tally.py:656` prints per-round
disclosure provenance, and rounds 48-50 carry the attack seats (`W:w1/spec.json` has 4 mutation-testers, 6 critics, 10
reviewers). Prerequisite: row 19's frozen population must move first, or the ledger inherits the same truncation.

**3.4 Proposal 6 — scoring-before-amendment timing** (`considerthese/2026-10-23.md:31`). What one round needs: a second leg
on `tools/prereg-time-check.py` (today file-vs-commit only, `:2-13`) that reads, per round, the dispatch wall-clock
(`W:w1.ready.dispatched:1` = `2026-10-26T21:54:00`), the first seat-evidence mtime, and any later commit to
`.ufo/waves/round-N/preregistration.json`, and exits 1 when the earliest seat evidence precedes an amendment claiming the
rule was in force. Round 50 has no amendment (`git log -- .ufo/waves/round-50/preregistration.json` → one commit), so it is
the clean passing case; round 28's A1 ordering (first score 08:35:54Z before amendment 08:38:16Z) is the failing fixture.

**3.5 Proposal 7 — true-but-unadmitted knowledge** (`considerthese/2026-10-23.md:33`). What one round needs:
`tools/unadmitted-census.py` joining SKILL registry rows (each cites its round and tool), `registry/claim-outcome-ledger.tsv`
and `corpus/lessons/round-N-verifier-spotcheck.md`, printing `rows=N rejected_rounds=R reproducing=P`. Two rejected rounds
are on record to seed it (`round-40-verifier-spotcheck.md` "rejected, honest stop"; round 45's pending closure), and round 49
supplies an admitted control. Prerequisite: the two ledgers must be re-run first (row 9 is idle since round 45).

**3.6 Proposal 11 — "prepared, not dispatched" ledger** (`considerthese/2026-10-24.md:31`). What one round needs:
`registry/prepared-waves.tsv` with one row per wave (`wave`, `spec_commit`, `max_lanes`, `ready_at`, `dispatched_at`,
`settled_commit`, `rounds_waited`), filled from `W:w1/spec.json`, `w1.ready`, `w1.ready.dispatched` and `w1-results.json`,
plus a `--check` that flags a wave whose `w1.ready` is older than one round with no `w1.ready.dispatched`, and a wave whose
`spec.json` `maxLanes` exceeds the policy ceiling (66 here). Round 50 adds the second datapoint and the first durability
hazard: round 49's pair is tracked, round 50's is untracked (`git status --porcelain`), so the ledger must read the wave dirs
before integration or lose the row.

## 4. Findings

**F1 — round 50 drops the proposal pointer for the second consecutive round, so the lane's own record of what it mined is
unrecoverable from the repo.** `.ufo/waves/round-50/preregistration.json` has no `frontier` key (keys printed in
`commands.txt` §2), as in round 49, while rounds 46-48 each carry `frontier.considerthese`
(`round-46:150`, `round-47:56`, `round-48:55`). Round 49's table filed this as its F1 and it was not repaired; the round that
would have repaired it is this one. Command: the 5-round key print → `49 False None / 50 False None`. Proposed fix: one key
in the preregistration, `"frontier": {"considerthese": "<day> proposal N (summary) — or: none (reason)"}`, and a
`gate-registry-check.py` leg that fails when a round ≥ 50 prereg lacks it.

**F2 — the lesson-level proposal line has now been missing for two landed rounds, and round 50's lesson seat is not asked to
write one.** `grep -cE "considerthese|proposal" corpus/lessons/round-48.md` → 0 and `…/round-49.md` → 0 (exit 1 each), against
`corpus/lessons/round-47.md:37`, `round-46.md:11`, `round-45.md:21`. Round 50's `T4Lesson` item specifies `## Claims`,
`## Gate` and a `## Mistakes` schema and never mentions proposals (`.ufo/waves/round-50/build_spec.py:174-175`), so a third
round will land without the line. Proposed fix (one sentence added to that item): end `## Claims` with
`considerthese: <day> proposal N → <artifact>` or `considerthese: none (reason)`.

**F3 — three landed instruments went dark or stale in the same round, and the round-49 fix for exactly this was not
implemented.** pin-watch: no seat in the wave (`spec.json` U-names → `['U1Fresh']`), no line in `W:measured/measure.sh`;
seat-yield: no line, and unrunnable at build (exit 2, no `*-results.json`); shortcut-tally: runs, population `40-47`
(`tools/shortcut-tally.py:895`, `W:measured/tally-build.out:2`). Round 49's F7 proposed `registry/per-round-instruments.tsv`
plus a gate leg; `ls registry/` → the file does not exist, and `W:measured/gate-build.out:2-3` still only reports the two
unregistered counters. Consequence: six of the twenty proposals (rows 9, 14, 16, 19, 2, 5) now have an instrument whose
"in continuous use" claim is prose only. Proposed fix: the registry file with `instrument, script, command,
required_since_round`, and one leg in `gate-registry-check.py` failing when a required instrument has no `run` line in the
round's `measure.sh`.

**F4 — the committed build receipts contain a failing `sao` receipt that a later build fix repaired without a re-run, so the
SCORECARD integration must quote the tip re-run or carry a false red.** `W:measured/sao-build.out:2` records
`error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)` with `exit=2`; commit `3d42897b`
("S498 row markdown tick parity so sources-append-only row parser accepts it") repaired the row, and at the tip the same
command prints `added S496 (allowed) / added S497 (allowed) / added S498 (allowed) / no append-only violations`, exit 0
(`commands.txt` §9). The receipts and `measure.sh` were committed one commit later (`3b79eadd`) without re-running `sao`.
Proposed fix: re-run `sao` at the measurement commit and overwrite the receipt, or have `measure.sh` re-run at the commit it
records; a receipt whose `exit=2` is repaired by a later commit is otherwise indistinguishable from a real regression.

**F5 — `hexrun-census` is red at the tip for an id the lane cannot resolve, and neither the receipt nor the ledger says
which.** `W:measured/hexrun-build.out:2-3` → `unknown=1`, exit 1; `--details` names it:
`f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 class=unknown`. It is the round-49 report commit in the **fleet** repo,
cited by the round-49 closure at `corpus/lessons/round-49-verifier-spotcheck.md:21`; `git cat-file -t` on it → `fatal: could
not get object info`, and `grep -c f8cdb853 registry/hexrun-ledger.tsv` → 0, although the ledger already carries a
fleet-repo id with class `upstream` (`registry/hexrun-ledger.tsv:2`, `VeigaPunk/shokunin`, with API evidence). The state
predates round 50 (round 49's receipt: `unknown=2 exit=1`), so this is a standing red the round inherits. Proposed fix: add
the ledger row (class `upstream`, repo `VeigaPunk/shokunin`, evidence = the closure line, verified via one `gh api` request),
and make the receipt print the token (the counter needs `--details` today).

**F6 — no closure has ever ruled this tracker, including the one that admitted the round carrying it.** The round-49
closure is `Verdict: **admitted**` (`corpus/lessons/round-49-verifier-spotcheck.md:11`) and
`grep -cE "considerthese|proposal|tally" corpus/lessons/round-49-verifier-spotcheck.md` → 0. Rows 18-20 therefore can never
leave "no verdict", which is the one thing proposal 2 of 2026-10-26 asks the tracker to calibrate
(`considerthese/2026-10-26.md:31`). The omission is not a search artefact: the same zero holds for the
round-47 and round-48 closures (`grep -cE "proposal|considerthese|tally"
corpus/lessons/round-47-verifier-spotcheck.md` → 0, `…round-48…` → 0), so every closure since
the tracker began has left it unruled. This seat therefore cannot calibrate itself, which is
precisely what proposal 2 of 2026-10-26 asks a tracker to do. Proposed fix: one line in each
closure, `frontier seat: <name>: <verdict on its product>`, for every round that dispatches one;
the round-49 closure does route individual seats (its R2 is "late seat X1Kill",
`corpus/lessons/round-49-verifier-spotcheck.md:104`), so the format is not new work.

**F7 — the round whose claim depends on a specific binary lost the only instrument that reports that binary's pin.**
C1's three replays rest on llama.cpp b11909 (`W:preregistration.json:16`), `registry/engine-pins.tsv:4` pins `b11755 S038`,
`grep -c b11909 registry/engine-pins.tsv` → 0, and round 50 dispatched no `U2Pins` seat and ran no `pin-watch`
(`.ufo/waves/round-50/build_spec.py:82`, `W:measured/measure.sh`). Round 49 flagged the absent pin row (its F8) and its seat
recorded that `pin-watch` "cannot say anything about the dependency the witness replays rest on"
(`.ufo/waves/round-49/w1/out/U2Pins.md:13`); round 50 removed the seat. Proposed fix: a pin row for the replay's own
engine+tag (`llama.cpp b11909`, source = the receipt that records it) and a `U2Pins`-equivalent line in `measure.sh`, so the
`behind` signal is at least attached to the dependency the round uses.

## 5. Not re-reported

The round-50 known integration items were not re-verified beyond what the table needed: the two round-50 counters are
unregistered (`W:measured/gate-build.out:2` `unregistered tools/round50-append-audit-v5-check.py`,
`tools/round50-replay-bind-audit.py`; `registered 44 unregistered 2 defective 0`, exit 1); SCORECARD/LOG/QUALITY/README and
the round-50 lesson are not written yet; S496/S497/S498 `used-by` names `corpus/lessons/round-50.md`, which does not exist at
the snapshot (`corpus/SOURCES.md:251`). This seat ran no counter, started no server, and did not touch the lane: the only
runs were read-only tool invocations inside a `git clone --shared` at `3b79eadd`
(`sources-append-only.py`, `hexrun-census.py`, `shortcut-tally.py`, `seat-yield.py`), all recorded with exit codes in
`commands.txt` §9.

Snapshot limit: the wave is in flight and the lane is changing under this pass (29 seat dirs and 3 reports at read time,
`git status --porcelain` untracked wave-state files), so every "absent" statement above is true at `3b79eadd` and may be
closed by the L1 before the round lands; each is backed by a command in `commands.txt`.
