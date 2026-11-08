# DRAFT — corpus/lessons/round-99.md (seat SB01Entry, round 99, lane kama)

Status: DRAFT for the committer (KamaR99). Not applied to any tracked lane file by this seat.
Every number below was re-derived by this seat on 2026-11-08; commands are in `../receipts/`.

The shape required by the seat brief: `## Gate` (three rows), `## Mistakes` (M1, M2, M3), and the
SCORECARD.md/LOG.md correction blocks with 12 reported / 0 dead, the 7 attack / 5 non-attack names, the
pointers `SCORECARD.md:6431` and `LOG.md:4040`, `EX02BudgetControl` vs `SB01-equivalent`, `RV03Intent`,
the census base/tip groups, and the gate's six failed arms.

The frozen counter `tools/round99-record-audit.py` grades exactly these twelve propositions
(`tools/round99-record-audit.py:8-60`); the text below is written so that each check has its named
tokens, and the counter was run against a materialised tree of this text
(receipt `../receipts/c2-tree-graded.out`: `RECORD_AUDIT99 checks=12 mismatches=0 met=True`).

---

# Round 99 — the population the control ran, the records that did not match, and an unread flag that is not "off"

Lane `kama`, round 99, L1 `KamaR99`. Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978` (round 98 closed
`ok`: C1 calibration, C2 operability, C3 depth all verified at `160e22dd`; expansion unchanged,
quality/discernment improved — `corpus/lessons/round-98-verifier-spotcheck.md`). Claims: C1
operability (the budget counter's control mode refuses a population it did not run), C2 calibration
(the lane's round-98 records agree with the committed wave evidence), C3 depth (an unread `/props`
autoload flag reads `router-autoload-unread`, not `router-unloaded`).

## Gate

Every row below was opened this round (2026-11-08) and re-opened independently by seat `SB01Entry`
(receipt `../receipts/s624-s626-reopen.txt`); the digest is of the bytes fetched by `curl` in this
round, recorded in `.ufo/waves/round-99/sources/`.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S624 llama.cpp `tools/server/server-models.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.cpp — 2026-11-08, sha256 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` (111 675 B), HTTP 200 | `{"models_autoload",      params.models_autoload},` (line 2030, inside `get_router_props` lines 2021-2046) | The bare `/props` body the probe reads is built from the server's own `params.models_autoload`; the field is the configured state, not a request echo. |
| S625 llama.cpp `common/common.h` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-08, sha256 `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` (58 830 B), HTTP 200 | `bool models_autoload = true;` (line 705; trailing comment: automatically load models when requested via the router server) | Autoload defaults to true, so an autoload-off router is an explicit `--no-models-autoload` state; an unread answer is never evidence of it. |
| S626 llama.cpp `tools/server/README.md` @ b12177 | **reject** (C, docs lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md — 2026-11-08, sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` (136 429 B), HTTP 200 | `--models-autoload, --no-models-autoload` — for router server, whether to automatically load models (default: enabled) (line 234) | Names the launch flag and its default, not the `/props` JSON field the probe reads; flip: a docs section names `models_autoload` in the props body. |

Registry changes: S624 and S625 admitted (used-by `SKILL.md`, `corpus/knowledge/router-props-autoload.md`),
S626 a rejected row; no existing row's status/recheck/used-by changed. Census before → after: 363 → 366
rows (`A 345→347`, `B 11→11`, `C 7→8`; `mined 325→327`, `queued 8`, `rejected 30→31`), validate exit 0
at round start (`controls/census-start.out`); the round-end receipt (`controls/census-end.out`) is
committed with the measurement commits, and the 366 figure is re-derivable now from
`git show f6e7ccc2:corpus/SOURCES.md` through `scripts/sources-census.sh census`.

Assimilation: none from `merge/kama/` (the package holds no `/props` autoload theme). `considerthese/2026-11-08.md`
proposal 2 (a counter-requires-its-own-claim scan) is mined as a pre-freeze scan over the three new
counters; the receipt is `controls/counter-literal-scan.out` and the shape it flags is disclosed as
C2 limit (c).

## Mistakes

**M1 — the round-98 wave accounting was written from a directory scan, not from `w1-results.json`.**
Class: `sampling`. Evidence: `corpus/lessons/round-98.md` M3 records that `RV03Intent` and
`EX02BudgetControl` settled inside the same wave; `SCORECARD.md:6431` and `LOG.md:4040` still said
"10 reported, 2 dead" and the LOG credited a "SB01-equivalent" seat that does not exist. Carried-by
M3: the wave-dir scan's own record (`corpus/lessons/round-98.md` M3 — "a wave-dir scan that reads
only `out/<Name>/` inferred two live seats were dead") is the receipt that contradicts the
accounting, and it sat outside that lesson's `## Mistakes`; this round carries it inside `## Mistakes`
(as M3 below) so the contradiction and the accounting are read together. Captured-by:
the round-98 non-author spot-check (routed defect 1), not any lane counter — no counter read the wave
accounting against the results file. Fix: the round-99 corrections in `SCORECARD.md` and `LOG.md`
state **12 reported, 0 dead**, the derived **7 attack / 5 non-attack** split naming `EX02BudgetControl`
and `RV03Intent`, re-derived by `tools/round99-record-audit.py` (C2). Shown able to fail: the same
counter prints `mismatches=10` at base (`controls/c2-base.out`) and 0 after the corrections at M2.

**M2 — the round-98 lesson labelled the base census numbers as HEAD.** Class: `labelling`. Evidence:
`corpus/lessons/round-98.md:28` says "tiers measured with the census at HEAD" and quotes the r98
**base** `681c80a4` → 361 rows (A 344, B 11, C 6; mined 324, queued 8, rejected 29); the r98
**tip** `649bb2e9` → 363 rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30). Captured-by: the
round-98 spot-check's row-count cross-check. Fix: this lesson states the two groups with their
revisions, and `tools/round99-record-audit.py` checks 7–8 re-derive both from `git show <rev>:corpus/SOURCES.md`
with the frozen census generator. The r98 lesson bytes are not rewritten (append-only history).

**M3 — the carried round-98 M3 record sat outside that lesson's `## Mistakes` section.** Class:
`sampling`. Evidence: `corpus/lessons/round-98.md` places "M3 — a wave-dir scan that reads only
`out/<Name>/` inferred two live seats were dead" after `## Spot-check`, so a reader scanning `## Mistakes`
missed the record that contradicts the wave accounting. Captured-by: the round-98 spot-check
(routed defect 4). Fix: the record is carried here, inside `## Mistakes` (this row); the r98 file keeps
its bytes.

**M4 — the wave's own falsification record.** Pending the wave settlement; this row is filled from
`w1-results.json` and the attack artifacts before the report (Amendment 59 requires the artifact
column to read every attack seat).

## Record corrections (the SCORECARD and LOG blocks)

The two appended blocks are drafted verbatim in
`.ufo/waves/round-99/w1/out/SB01Entry/drafts/scorecard-log-correction-blocks.md`; they are what
`tools/round99-record-audit.py` checks 1–6 and 9–12 read. Each block states **12 reported, 0 dead**,
names the seven attack and five non-attack seats as derived from `w1-results.json`, names the stale
pointers `SCORECARD.md:6431` and `LOG.md:4040`, resolves the `SB01-equivalent` misattribution to
`EX02BudgetControl`, adds `RV03Intent`, and enumerates the gate's six failed arms (`selfdesc`,
`newest-closure`, `round-scope`, `round-clean`, `round75-instruments`, `round78-instruments`) against
the receipt's `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1`.

## Routed-defect answers

- **Round-98 spot-check defects 1–4 and 6** (stale wave counts, seat accounting, census mislabel, M3
  placement, under-enumerated gate disclosure) — answered by C2's corrections and this lesson; checks 1–11
  of `tools/round99-record-audit.py` grade them.
- **Defect 5** (M2's red-before receipt and the counter-level `n != len(selected)` fix) — answered by C1:
  `controls/c1-before.out` is the round-98 acceptance of the dropped-cell mutation (exit 0) and
  `controls/c1-candidate-mutant.out` is the successor's refusal (exit 1).
- **Defect 7, carried unchanged:** the slow `/props` **verdict** stays fail-closed `MODEL_UNLOADED`
  (C3 changes only the reason vocabulary); `round75-instruments` `bad_rows=19` (L0 r87/r89 still open);
  `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080; the pass-level
  wall-clock wrapper (SC01); the ctime memo shape; the C1 checks 13–14 receipt-needle limit; the frozen
  `--control` count check (now fixed by C1 for the population count). Also carried: the round-90
  `reason-rows` receipt is stale at base (`REASON_ROWS … bound=0 unbound=24 receipt=stale`, exit 1), so
  the reason table C3 edits was already unbound before this round; a re-capture bound to the round-99
  probe is routed to round 100, not claimed here.

---

## SB01Entry notes for the committer (not part of the file body)

1. **The census-start receipt has no exit marker.** `controls/census-start.out` (committed at the
   freeze) ends at the `kama<TAB>ok<TAB>…/corpus/SOURCES.md` line; the round-98 twin
   `.ufo/waves/round-98/controls/census-start.out` ends with an extra `census_exit=0` line. The plan
   cites the r99 receipt as "exit 0, 363 rows", but the receipt carries neither an exit line nor a
   row count (measured: `grep -c rows` = 0 on both the r99 and r98 receipts). The 363 figure is
   re-derivable from the bytes (`git show 439fdb3d:corpus/SOURCES.md` → 363 rows) but not from the
   receipt; either add the `census_exit=0` line to the r99 receipt shape or cite the derivation.
2. **`S627` has a sources receipt but no registry row.** The freeze commit added
   `.ufo/waves/round-99/sources/s627-arg-models-autoload.txt` (llama.cpp `common/arg.cpp` @ b12177,
   sha256 `c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67`, lines 3676-3684, the
   `--models-autoload` / `--no-models-autoload` option pair), but `corpus/SOURCES.md` has no `S627`
   row (`grep -c S627 corpus/SOURCES.md` = 0), so the census at HEAD counts 366 rows and the tier
   split moves only for S624/S625/S626. The file's URL is the same file as the existing S596 row
   (`common/arg.cpp` @ b12177), so it is a re-open of a pinned file, not a new source — either record
   it as a re-open of S596 or drop the file from the wave's sources directory. Left as a finding, not
   a decision: the wave plan says three rows were opened this round (S624 admit, S625 admit, S626
   reject) and does not mention S627.
3. **The census count moved by three, not four.** The lesson's Gate section above says 363 → 366 rows
   (`A 345→347`), which is what the bytes give (measured at the freeze commit: 366 rows, `tier.A` 347,
   `tier.B` 11, `tier.C` 8, mined 327, queued 8, rejected 31). That is consistent with S624 and S625
   admitted (A, mined) plus S626 rejected (C) — three rows. The S624/S625/S626 `used-by` column names
   `SKILL.md`, which does not yet cite S624/S625 anywhere (`grep -n "S624\|S625" SKILL.md` → no hits
   at the freeze commit); the SKILL.md rows the round-99 draft adds are the ones that would make that
   citation true.
