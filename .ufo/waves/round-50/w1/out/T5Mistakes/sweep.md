# Round 50 — T5Mistakes: mistake-mining sweep, closures 45–49 vs lesson `## Mistakes` rows

Seat T5Mistakes (scribe, calibration), leaf. Read-only against lane `kama-shokunin`, snapshot
`3b79eadd` in a `git clone --shared` at `/fast/scratch/hyaku/kama-r50/T5Mistakes/lane`
(the round is still in flight; HEAD at read time `3b79eadd`, build `97c864be`).
No counter, no lane write, no git/jj mutation.

**Verdict.** The five closures route 30 items; expanding r46-D3 and r48-R5 into their named
sub-items gives **32 ledger lines**. **19 carry a lesson `## Mistakes` row or a QUALITY criterion**;
**13 do not**, and of those 6 have a committed non-row carrier (3 `corpus/README.md` frontier
dispositions, 2 prereg `limits`, 1 policy disclosure), 4 are in flight (`r49-R1…R4`, closed by the
build, rows due in the round-50 lesson) and **3 have no committed carrier at all** (r46-D3's two
sub-gaps, r46-D4's rule, r47-D2). I propose **6 rows, all new**; two findings contradict both prior
sweeps (round-48 F1/F5 and round-49 F1/F5/F8/F9 over-reported "dropped" because their greps were
scoped to `corpus/lessons/` and missed `corpus/README.md`).

Axes: calibration (row capture and verdict precision), operability (the three closed-by-commit items).

---

## 1. Method

```
grep -n '^|' corpus/lessons/round-4[5-9].md            # Mistakes tables: r45 27-31, r46 35-42, r47 45-50, r48 28-32, r49 34-38
grep -nE '^\s*(-|[0-9]+\.)\s*\**\**[DR][0-9]' corpus/lessons/round-4[5-9]-verifier-spotcheck.md
                                                        # routed items: r45 146-150, r46 137-142, r47 97-105, r48 110-121, r49 103-108
grep -n 'KQ7[0-9]' corpus/QUALITY.md                   # criteria KQ70-KQ79 (QUALITY.md:397-424)
grep -rn '<id>' corpus/ registry/                      # carrier search, full corpus scope
python3 .ufo/waves/round-50/w1/out/T5Mistakes/checks.py --repo <clone> --rev 3b79eadd
```

**Scope correction that drives the verdict.** Both prior sweeps searched `corpus/lessons/` and
`registry/` only (round-48 `sweep.md` "Method"; round-49 `sweep.md` line 5 queries). The lane also
carries dispositions in `corpus/README.md` §`Frontier disposition — round NN`, which is where the
"carried" items actually live:

```
grep -rn 'floating-series' corpus/lessons/ registry/   -> 2 hits (closures/lesson quote only)
grep -rn 'floating-series' corpus/                     -> 5 hits, incl. corpus/README.md:719
grep -n  'S013\|S022\|S002' corpus/README.md           -> 1068-1069, 1233-1234
grep -n  'Round-45 D1' corpus/README.md                -> 755
grep -n  'prerelease\|sub-20' corpus/README.md         -> 1202, 1229 (round-49 frontier)
```

## 2. Routing ledger — every routed item, closures 45 → 49

Capture key: **ROW** = a `## Mistakes` row; **KQ** = a QUALITY criterion; **LIMIT** = prereg
`limits`; **README** = committed `corpus/README.md` frontier disposition; **CLOSURE** = named only
by a later outside closure; **NONE** = no committed carrier outside the closure that routed it.

| Closure item | What it routed | Captured by | Capture |
|---|---|---|---|
| r45-D1 (`round-45-verifier-spotcheck.md:146`) | claim-outcome reader re-freeze; KQ65 sample must be scored pre-data | `corpus/README.md:755` ("the deferred item stays open"); deferred at `round-46.md:12` | README — **no ROW** |
| r45-D2 (`:147`) | apply KQ64 at the round-46 freeze + receipt | `round-45.md:27` row 1, KQ64; `.ufo/waves/round-50/freeze/prereg-time-check.out` → `RESULT pass … exit=0` | ROW |
| r45-D3 (`:148`) | model locator for the sha256 | `round-46.md:35` row 1, KQ66 | ROW |
| r45-#4 (`:149`) | carried frontier S013/S022/floating-series/S002–S004/llama.cpp; sufficiency | sufficiency → `round-47.md:45` row 1; frontier → `README.md:719`, `:1068-1069`, `:1233-1234` | ROW (sufficiency) / README (frontier) |
| r45-#5 (`:150`) | driver stall N-D, salvage N-A, L0 | N-D → `round-46.md:36` row 2; N-A, L0 operator | ROW (N-D) |
| r46-D1 (`round-46-verifier-spotcheck.md:137`) | `---`-line blind spot | `round-46.md:40` row 6, KQ70 | ROW |
| r46-D2 (`:138`) | restoration measure drift | `round-47.md:46` row 2, KQ70 | ROW |
| r46-D3 (`:139`) | C1 sufficiency, **plus two named sub-gaps** (reworded witnesses auto-pickable; V1Code F1–F4) | family → `round-47.md:45` row 1; sub-gaps: no row, no KQ (`grep -rn 'V1Code' corpus/lessons/` → only round-44/46 + the closure) | ROW (family) / **NONE** (sub-gaps) |
| r46-D4 (`:140`) | hexrun red gate, unknown=21, "close or ledger" | fixed at r47 (22 ledger rows); frontier → `README.md:887`, `:1070`, `:1234` | **NONE** for the rule "unknowns close as ledger rows" |
| r46-D5 (`:141`) | dead `teardown.log_path` | `round-47.md:47` row 3, KQ69 | ROW |
| r46-D6 (`:142`) | N3Fleet adjacency | operator | operator |
| r47-D1 (`round-47-verifier-spotcheck.md:97`) | C2 counter trusted its own evidence | `round-48.md:30` row 3, KQ74 | ROW |
| r47-D2 (`:98`) | replay every receipt, not receipt-1 | implemented r48 (`replayed=3/3`); KQ75 covers the projection, not the count | **NONE** |
| r47-D3 (`:99`) | record-time provenance | KQ74 | KQ |
| r47-D4 (`:100`) | comparison depth | KQ75 | KQ |
| r47-D5 (`:101`) | C1 counter gaps, surviving mutants | KQ70/KQ72 + disclosed survivors | KQ / disclosed |
| r47-D6 (`:102`) | model URL on `main` → pinned | KQ74 pinned clause, S492 | KQ |
| r47-D7 (`:103`) | prerelease cliff | `README.md:1040-1042`, `:1229`; round-50 seat prose (spec item T7Readme) | README — **no ROW** |
| r47-D8 (`:104`) | sources guard grades nothing since r45 | class → `round-47.md:49` row 5 ("Not fixed this round"); repair landed `c4b2175d`, cited by `round-48-verifier-spotcheck.md:42,60` only | ROW (class) / **CLOSURE** (repair) |
| r47-D9 (`:105`) | receipt-tip precision | `round-48.md:29` row 2 | ROW |
| r48-R1 (`round-48-verifier-spotcheck.md:110`) | unbounded archive member read | `round-49.md:37` row 4 | ROW |
| r48-R2 (`:111`) | report filed before its tip | `round-49.md:34` row 1, KQ79 | ROW |
| r48-R3 (`:112`) | census paraphrased | `round-49.md:35` row 2, KQ79 | ROW |
| r48-R4 (`:113`) | prompt route map (operator) + role share | share → `round-49.md:36` row 3; doc correction operator | ROW (share) |
| r48-R5 witness (`:114`) | replay never witnesses execution | KQ76 | KQ |
| r48-R5 record-time fetch (`:116`) | record time never fetches URLs | `README.md:1216` ("archive-origin binding … or an explicit statement") | README — **no ROW** |
| r48-R5 mutants (`:117`) | surviving mutants | SCORECARD disclosure; no kill-threshold policy by design | disclosed |
| r48-R5 exemption/binding (`:118`) | content-blind exemption, substring binding | KQ77, KQ78 | KQ |
| r48-R5 sub-20 (`:119`) | sub-20 deletions unwatched | `README.md:1202`; round-50 prereg `limits[4]` ("the sub-20 threshold is unchanged") | LIMIT |
| r49-R1 (`round-49-verifier-spotcheck.md:103`) | pid↔`child_pid` join, env canaries, model binding | round-50 C1 claim (`preregistration.json` claims[C1].statement) + build `97c864be` | in flight — **no ROW yet** |
| r49-R2 (`:104`) | killed counter leaves replay/tool/server up | round-50 C1 teardown leg | in flight |
| r49-R3 (`:105`) | C2 origin/fence/CRLF gaps, counter shares the rule | round-50 C2 v5 claim | in flight |
| r49-R4 (`:106`) | surviving mutants → routed to round 50 | round-50 spec items M1Ctr/M2Live/M3Tool/M4Ctr (≥20 mutants each); **no prereg `routed` entry** | in flight |
| r49-R5 (`:107`) | sub-20, prerelease cliff, b11906 population | sub-20 → prereg `limits`; prerelease + b11906 → seat prose (spec T7Readme) + `README.md:1229,1233` | LIMIT/README |
| r49-R6 (`:108`) | prompt route map | operator | operator |

Counted (32 ledger lines: 30 closure items, r46-D3 and r48-R5 split into sub-items): **19** carry a
ROW or KQ; of the 13 that do not, **6** have a committed non-row carrier (README ×3, prereg `limits`
×2, policy disclosure ×1), **4** are in flight (r49-R1…R4) and **3** have no committed carrier
(r46-D3's sub-gaps, r46-D4's rule, r47-D2); the r47-D8 *repair* is closure-only while its class has
a row. Operator lines (r45-#5 N-A/L0, r46-D6, r48-R4, r49-R6) are excluded from both counts.

## 3. Prior-sweep verdicts re-checked

| Prior verdict | Claim | Re-check at `3b79eadd` | Flip? |
|---|---|---|---|
| r48 F1 = r49 F1 | r45-D1 "dropped … `grep -n 'r45-D1' -R corpus/lessons/ .ufo/waves/round-49/` → 0 matches" | `corpus/README.md:755` records it and says it "stays open"; `round-46.md:12` records the deferral | **flips** ("dropped" → carried) |
| r48 F5 = r49 F5 | carried frontier "appears nowhere after the r45 closure" | `README.md:719` (floating-series), `:1068-1069` and `:1233-1234` (S013, S022, S002–S004) | **flips** |
| r49 F8 | r47-D7 "absent from round-49 planning" | true of the prereg/lesson; `README.md:1229` is the round-49 disposition | **partial flip** |
| r49 F9 | r47-D8 parser "unfixed … never integrated" | `git log -- tools/sources-append-only.py` → `c4b2175d … sources guard repair`; measured exit 0 today (§4 F4) | **flips** |
| r49 F11e / F11b | sub-20, record-time fetch "open, disclosed without a row" | `README.md:1202`, `:1216` carry both | **partial flip** |
| r48 F4 | `base-unresolved.tsv` has no producer | still true: `grep -rn base-unresolved corpus/` → only the closures/sweeps | stands (outside my 45–49 window) |
| r48 F2/F6 | r44-D2, r44-D3 | outside my window; unchanged | — |

Root cause, one line: a sweep's negative is only as wide as its grep path; `corpus/README.md` is
inside the append-only corpus and outside `corpus/lessons/`.

## 4. Findings

Each row is ready to paste into a lesson `## Mistakes` table (class | evidence | captured-by | fix).

### F1 — NEW: `label-drift` — the round-50 lesson brief attributes closure items to the wrong round

- Evidence. `.ufo/waves/round-50/spec.json` item `T4Lesson`: "(1) round-49 closure R2/R3 (report
  placeholders and census paraphrase; the checker …/round-49/w1/out/S9Mistakes/report-precheck.py
  exists); (2) round-49 closure R4-style source-count mistake …". Those three descriptions belong to
  **round-48** closure items: `round-48-verifier-spotcheck.md:111` (R2 report placeholders),
  `:112` (R3 census paraphrase), `:113` (R4 route-map/source count) — and the round-49 lesson already
  recorded them as such (`round-49.md:34` "round-48 closure R2", `:35` "round-48 closure R3", `:36`
  "round-48 closure R4"). Round-49 closure R2 is the teardown defect, R3 the C2 definition gaps, R4
  the mutation survivors (`round-49-verifier-spotcheck.md:104-106`).
- Consequence, two ways. As written, the scribe either re-writes rows the round-49 lesson already has
  (duplicate rows under a wrong id) or writes rows for teardown/C2-definitions using
  report-placeholder evidence. And nothing in the brief asks for a row on **r49-R1**, the pid/env/model
  binding defect the round's own C1 claim closes — the third consecutive round in which the biggest
  defect of the previous round would be captured by no one (the class round-48 row 4 already names).
- Captured by: the outside closure only (nothing in the lane reads a brief against a closure).
- Proposed row: **`label-drift`** — "A closure citation carries its round prefix and its descriptor
  matches the item: `round-49 closure R2` names the teardown defect, `round-48 closure R2` the report
  placeholders. Every lane item of the previous round's closure is named in the lesson-scribe brief
  or in a seat output."
- Fix shown able to fail: `python3 .ufo/waves/round-50/w1/out/T5Mistakes/checks.py --repo <clone>
  --rev 3b79eadd` → `== check A label-resolution: FAIL (2 finding(s))`, exit 1, printing the two
  T4Lesson citations against the items' true text; the same run passes `T1Log` ("round-49 closure
  R1, R2, R3" with seats K1Cheat/K1Design/R0Controls/X1Kill/K2Origin/K2Cheat/V2Ctr — all seven are
  those items' seats), so the check is not blanket-failing (`checks.out`).
- Hand-read instance the checker does not catch (it predates the citation): spec item `X12Zip` —
  "Record-time archive bounds (round-49 closure R1, carried)" — the archive bounds are **round-48**
  closure R1 (`round-48-verifier-spotcheck.md:110`); round-49 closure R1 is the pid join.

### F2 — NEW: `fix-without-mechanism` — the round-48 row-4 fix exists in round 48 only

- Evidence. `round-48.md:31` fixed "routed items dropped without capture" with "the round-48
  preregistration carries a `routed` block naming r47-D1…D9 … the sweep's comparison of closure D-ids
  against that block flags any id it lacks". Keys of `.ufo/waves/round-49/preregistration.json`:
  `lane, round, attempt, author, frozen_at_utc, base, authority, separability, claims, controls,
  limits` — no `routed`. Round-50: same key set, no `routed`/`carried` (verified by `json.load`).
  So the mechanism the row's fix names has been absent for two rounds, and the row's own check cannot
  run there.
- Captured by: seat T5Mistakes (this sweep); the round-49 sweep noted round 49 only (its note 1).
- Proposed row: **`fix-without-mechanism`** — "A Mistakes row whose fix is a document convention (a
  prereg `routed`/`carried` block) is only as durable as its checker: the row names the committed
  check, and the check runs at the next freeze. A convention with no checker disappears in two rounds."
- Fix shown able to fail: check B in `checks.py` → `round-48: has_routed=True (8 lane items)`,
  `round-49: False (3)`, `round-50: False (5)`, `== check B routed-block: FAIL (2 finding(s))`, exit 1
  (`checks.out`). Pass case is round 48 itself.

### F3 — NEW: `sweep-not-consumed` — a wave's own sweep verdict has no consumer

- Evidence. `.ufo/waves/round-49/w1/out/N5Mistakes/sweep.md` carries 12 findings; `git grep -l
  N5Mistakes 3b79eadd -- corpus registry` returns nothing for round 49 (only the round-48 sweep is
  cited, at `round-48.md:31`). The round-49 lesson rows 1–5 cite closures, not the sweep; the round-49
  prereg has no `routed`; the round-50 prereg has none either. The frontier step-3 output is
  therefore advisory: nothing in the lane is obliged to read it, and the round-50 wave re-does the
  same sweep (spec items `N4Mistakes2`, this seat).
- Captured by: seat T5Mistakes.
- Proposed row: **`sweep-not-consumed`** — "A wave's frontier-sweep verdict is cited by a committed
  `corpus/` or `registry/` file in the round that receives it, with a disposition per finding
  (row, KQ, limit, operator, or a stated drop), the way round-48's sweep is cited at `round-48.md:31`."
- Fix shown able to fail: check C in `checks.py` → `round-48: cited=True`, `round-49: cited=False`,
  `== check C sweep-consumed: FAIL (1 finding(s))`, exit 1 (`checks.out`).

### F4 — NEW: `sweep-verdict-stale` — an integration-time fix read as unfixed, because the sweep was a build-time snapshot

- Evidence. Round-49 sweep F9 (`sweep.md:99`): "`sources-append-only.py` … exits 2 on every revision
  since round 45 … a patch was proposed in wave evidence but never integrated". Measured today:
  the pre-repair tool (extracted from `git show c4b2175d^:tools/sources-append-only.py`, 619 lines)
  on the round-45 lesson's own failing pair prints `error: 052cb1e9:corpus/SOURCES.md:514: row-like
  line outside the parsed registry table; refusing to drop it` and `exit=2`
  (`sources-guard-pre-repair.out`); the tool at the tip on the same pair prints
  `added S484 (allowed) / added S485 (allowed) / no append-only violations`, `exit=0`, and
  `--selftest` → `45/45 selftest cases passed`, `exit=0` (`sources-guard.out`). The repair is the
  round-48 integration commit `c4b2175d` ("sources guard repair"), cited by
  `round-48-verifier-spotcheck.md:42` and `:60` and by no lesson row — `round-47.md:49` still reads
  "Not fixed this round".
- Captured by: seat T5Mistakes; no lane check re-reads a sweep's failing command at integration.
- Proposed row: **`sweep-verdict-stale`** — "A sweep runs at the build and is stale at the measured
  commit: every 'unfixed/red' verdict names the revision it measured, and the round re-runs that
  command at the measured commit, committing both exit codes."
- Fix shown able to fail: the command pair above (`exit=2` at `c4b2175d^`, `exit=0` at `3b79eadd`)
  is the row's whole evidence; a checker that re-runs each red verdict's command and compares exits
  would have flagged F9.

### F5 — NEW: `scoped-grep-false-negative` — "dropped" verdicts that a wider grep flips

- Evidence. Table §3. Round-48 F1 / round-49 F1: r45-D1 "never a row, absent from all later routing"
  — `corpus/README.md:755` carries it. Round-48 F5 / round-49 F5: carried frontier "appears nowhere
  after the r45 closure" — `README.md:719`, `:1068-1069`, `:1233-1234`. Both sweeps searched
  `corpus/lessons/` + `registry/`; the disposition medium is `corpus/README.md`.
- Captured by: seat T5Mistakes (second-order: the sweep that finds it is also a sweep).
- Proposed row: **`scoped-grep-false-negative`** — "A 'never captured' verdict in a sweep records the
  grep path it used and searches the whole append-only surface (`corpus/`, `registry/`, `SCORECARD.md`,
  `LOG.md`, `SKILL.md`); `corpus/README.md` §Frontier disposition is a capture medium."
- Fix shown able to fail: `grep -rn 'floating-series' corpus/lessons/ registry/ | wc -l` → `2`;
  `grep -rn 'floating-series' corpus/` → 5 hits with `corpus/README.md:719` among them;
  `grep -n 'Round-45 D1' corpus/README.md` → `755`. The narrow query is exactly the one both sweeps
  published.

### F6 — NEW: `closed-without-capture` — three items closed by a commit, recorded nowhere a later round reads

- Evidence. (a) **r46-D4** hexrun red gate: closed at r47 with 22 ledger rows; the *rule* ("unknowns
  close as ledger rows carrying committed evidence") is in no row or KQ (`grep -n 'hexrun'
  corpus/QUALITY.md` → only KQ55, which predates and does not require per-row evidence). (b) **r47-D2**
  replay-all-receipts: implemented r48 (`replayed=3/3`); KQ75 covers the compared projection, not the
  receipt count; no row. (c) **r47-D8** sources guard repair: commit `c4b2175d`, cited only by the
  round-48 outside closure; `grep -rn 'c4b2175d' corpus/lessons/round-4[7-9].md` → 0.
- Captured by: seats N5Mistakes (rounds 48/49) for (a) and (b); this seat measured (c).
- Proposed row: **`closed-without-capture`** — "An item closed by a commit is cited by a lesson row in
  the round that receives it, with the closing commit hash; a repair named only by an outside closure
  leaves the next round's frontier reading a defect that is already fixed (F4)."
- Fix shown able to fail: `grep -rn 'c4b2175d' corpus/lessons/round-4[7-9].md` → no output (exit 1),
  while `git log --oneline -1 c4b2175d -- tools/sources-append-only.py` → the repair commit.

## 5. Items I checked and deliberately did **not** propose rows for

| Item | Why not |
|---|---|
| r45-D1 (claim-outcome re-freeze) | no row, but a live carrier exists (`README.md:755`) and no re-claim has been made since round 45; the row proposed by the round-48/49 sweeps assumes a loss that is not there. Propose it if and only if a reader is frozen on the ledger — then F1 of the round-49 sweep applies as written. |
| r45-#4 / r47-D7 / r48-R5 sub-20, record-time fetch / r49-R5 | README frontier + prereg `limits` are committed dispositions; a row would restate a limit the lane already declares. The real defect is the missing cross-round check, which is F2/F3, not the carry. |
| r48-R5 surviving mutants / r49-R4 | disclosed by policy (round-20 criteria exclude a universal mutation score); round 50 is running four mutation seats against the frozen counters. No row by design; the round-50 report should carry kill/survive counts per counter. |
| r49-R1/R2/R3 | in flight: closed by build `97c864be`, rows due in the round-50 lesson. **F1 is the warning that the brief does not ask for R1 and mislabels R2/R3.** |
| r45-#5 N-A salvage, r46-D6, r48-R4 doc correction, r49-R6 | operator/driver-owned; never lane rows, correctly. |
| Known integration items (counters unregistered, lesson/SCORECARD/LOG entries pending, S496–S498 `used-by` → `round-50.md`) | stated as in flight by the seat brief; not re-reported. |

## 6. Evidence files (this directory)

| File | What it shows |
|---|---|
| `checks.py` | the four fail-capable checks (A label-resolution, B routed-block, C sweep-consumed, D carried-limits) |
| `checks.out` | exit 1; A: 2 findings (T4Lesson), B: round-48 pass / 49-50 fail, C: round-48 pass / 49 fail, D: prerelease+b11906 absent from the round-50 `limits` |
| `sources-guard.out` | repaired guard: historic pair `exit=0` (`added S484/S485`), `--selftest` `45/45`, round-50 window `exit=0` (`added S496/S497/S498`) |
| `sources-guard-pre-repair.out` | pre-repair guard at `c4b2175d^`: `error: 052cb1e9:corpus/SOURCES.md:514 … refusing to drop it`, `exit=2` |

Checks A–D were run against the clone's `3b79eadd`; the two guard runs are read-only `git show`
extraction plus the lane tool, no working-tree write.
