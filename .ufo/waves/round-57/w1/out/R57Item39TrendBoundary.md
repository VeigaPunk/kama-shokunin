# R57Item39TrendBoundary — trend evidence boundaries (expansion / quality / discernment)

Seat: sentinel, item `round57/TrendBoundary/39`, distinct case 60. Judged axes: calibration,
operability. **No verdict authority**: nothing below is a round verdict, an admission, an
axis score, or a recommendation to ship.

- Measured tip: `8a7f19760242bbe523fa2d7d1b22528b587633c1` (`git rev-parse HEAD`), no modified
  tracked files. The lane advanced five times during this seat (`8640e34c` → `16efcf5e` →
  `77e7f5ee` → `3d2d5d4d` → `8a7f1976`); every observable in the case-60 probe is identical
  at each re-check, only the `tip=` line differs. `corpus/SOURCES.md` and
  `corpus/lessons/round-57.md` both changed under this seat during the wave; the text quoted
  below is the current text at `3d2d5d4d`+.
- Tooling: `/home/vgpnk/.omp/agent/RULES.md` read first. No tool needed installing or
  updating, so nothing was installed and pacman was not touched (paused). No commits, no
  shared-file edits; the only writes are this report and the five files in this seat's
  out-dir (listed at the end).
- Basis: `LEARNING.md:33-35` (one observable per trend), `LEARNING.md:42` ("A subagent the
  lane dispatched is still the lane"), `corpus/QUALITY.md:376` (KQ61),
  `SCORECARD.md:18` (calibration row and ledger scope), `SCORECARD.md:3149` (§Round 57).

## S515 re-open (required this round)

- URL: `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`,
  opened 2026-10-27 by this seat (`curl -sS -L`, HTTP 200, 830605 bytes).
- SHA-256 of the fetched page: `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`.
  Identical to the round-56 committed copy (`.ufo/waves/round-56/sources/git-docs-git-config.html`)
  and to the round-57 wave copy (`.ufo/waves/round-57/sources/git-config-live-2026-10-27.html`).
  The source is byte-unchanged between rounds 56 and 57.
- Location: `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`, first paragraph
  under those headings; anchor `git-config.txt-GITCONFIGCOUNT` present; revision marker shown
  by the page is `git-config last updated in 2.56.0` (selector dates 2.56.0 to 2026-09-28).
- Located quote, **18 words** (count re-derived from the fetched copy):
  “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be
  added to the process's runtime configuration”.
  Same quote and word count as `corpus/lessons/round-56.md:18` and `corpus/SOURCES.md:268`.
- Scope the page itself supplies: pairs are zero-indexed; a missing key or value is an error;
  empty `GIT_CONFIG_COUNT` equals zero; the pairs override config files but are overridden by
  an explicit `git -c`.
- Registry relation: `corpus/SOURCES.md:264` (S511) has the same URL and the same 18-word
  quote. S515 is a correction row for the omitted revision marker, so the re-open corroborates
  an existing row and adds no new ground.
- Full receipt: `.ufo/waves/round-57/w1/out/R57Item39TrendBoundary/s515-live-extract.md`.

## Expansion — observable exists, no round-57 act can move it

`LEARNING.md:33` requires net new admitted `knowledge/` entries on ground the coverage map did
not hold (each `source:` citing a mined row), or a capability admitted to `SCORECARD.md`.
Measured at the tip: **36** knowledge entries; last knowledge-file *addition* `0e6ff7a2`
(2026-10-25); canonical capability list **11 rows** (round 49) and the head `## Capabilities`
mirror **11 rows**; `SCORECARD.md:3158` states "no capability added" for round 57.

Round 57's claim set is C1/C2 (counter repair), S516 (an own-work call-site row) and the S515
re-open (an existing row). None is a knowledge entry or a capability row, and KQ61
(`QUALITY.md:376`) is explicit: “expansion `improved` cites the admitted entry or capability
row, never a new source row or wave evidence.”

Two measurement traps this boundary exposes:

1. The round-42 counter's capability leg compares the head mirror's *name set* to the
   canonical list. It catches a rename or a dropped row; it cannot distinguish "a capability
   was demonstrated" from "a row exists".
2. `maxN` in the counter's summary is `max()` over `^## Round (\d+)` headings
   (`tools/round42-selfdesc-reconcile.py:168`), **not** a capability-row count. At this tip
   there are 58 such headings, max 57; rounds 24 and 54 have no heading and rounds 29, 30, 31,
   32 and 40 appear more than once. Whatever a repaired `maxN` prints, it is evidence about
   round section headings only.

Boundary: expansion cannot move this round by its own observable. The only admissible
expansion pointer at filing is an entry or capability row that exists at filing.

## Quality — the observable is entry re-verification; a tool repair is not one

`LEARNING.md:34`: improved when “a weaker entry is superseded by a stronger one, or stale
entries re-verify, with no admitted entry failing its re-check”. Measured: 36/36 entries carry
`verified-at:` and `recheck:`; **0** entries carry a 2026-10-27 verification; **0** entries
name a round-50..57 verification; the single 2026-10-26 timestamp in a `verified-at` line is a
round-43 fetch inside a 2026-10-25 entry (`runtime-health-surface-processes.md:2`).
`llamacpp-loading-lifecycle.md` was modified in rounds 47, 48 and 49 while its `verified-at`
lines still read 2026-10-20, 2026-10-21 and round-22 — modification is not re-verification.

Text tension to report, not resolve: `LEARNING.md:86-88` maps the quality trend to the depth,
freshness and operability *axes*, while `LEARNING.md:34` defines the trend's observable as
entry re-verification. Round 56's outside closure credited `quality — improved` to a tooling
fix (`corpus/lessons/round-56-verifier-spotcheck.md:38`: `LD_AUDIT` detection plus the
exact-field negative control). Under `:34`'s observable that is an operability axis move with
no entry re-verified. Round 57's C1 is the same class of act, so the same ambiguity applies to
any round-57 quality verdict. Both readings are shipped text; a seat without verdict authority
reports where they disagree.

Limit: `verified-at` is free text; the measurement above counts what the text states and
cannot prove an entry was actually re-opened.

## Discernment — no outside sample at seat time; the last disagreement is now recorded

`LEARNING.md:35` plus `:42`: improved when the outside spot-check agrees on admits **and**
rejects, or a disagreement becomes a lesson that adds a grounded `QUALITY.md` criterion. A
dispatched subagent is still the lane.

Measured: **43** `*verifier-spotcheck.md` closures; the latest is round 56, which agrees with
S512 and S514 and **disagrees with the S513 reject** (`.ufo/.../round-56-verifier-spotcheck.md:30`
holds the S513 row, `:39` carries the verdict “discernment — harmed”). `corpus/QUALITY.md` has
98 `KQ` rows and **0** cite round 56.

Round-57 state at this tip:

- `corpus/lessons/round-57.md:25` now records the disagreement as a `discernment-disagreement`
  Mistakes row with the fix “Not fixed in this counter-focused round … re-open S513 before any
  later reuse of its gate decision” (added in `3d2d5d4d`).
- `corpus/lessons/round-57.md:16` states no independent verifier is available before filing;
  `SCORECARD.md:3163` (planned round 58, item 2) defers “an independent outside admit/reject
  spot-check” to round 58.
- No round-57 outside closure exists at this tip.

Boundary: the lesson leg of `:35`'s improved condition now exists; the grounded `QUALITY.md`
criterion leg does not (0 rows cite round 56), and no outside closure exists to agree or
disagree. So neither `improved` nor "left unlearned" is reachable from the shipped text alone
at this tip — the round's own verdict is the L1's and the closure's to state.

## Instrument boundary (applies to all three trends)

There is exactly one tool in the lane that parses trend verdicts
(`tools/round44-verdict-ledger-audit.py`; the other six files that match "expansion" use the
word in unrelated senses — append-only contract expansion, path expansion, brace expansion). Its own docstring and constants fix its reach:

- `ROUNDS = range(10, 44)` (`:68`), `TRENDS = ("expansion", "quality", "discernment")` (`:69`);
- population is 68 fixed paths — `.ufo/reports/round-<N>/kama.md` and
  `corpus/lessons/round-<N>-verifier-spotcheck.md` for N in 10..43;
- evidence rule is line tokenisation (a trend word, then a verdict word); no knowledge entry
  and no `verified-at` is ever opened;
- `met = 204 valid rows and table exact and summary exact and axes cite` (`:46`).

Run at the tip: `rows=204 valid=204 missing=0 bad=0 agree=69 overclaim=2 underclaim=16 other=0
absent=15 table_missing=0 table_extra=0 summary=1 axes=1 met=True`, exit 0.

`registry/verdict-ledger.tsv` holds 204 rows covering rounds 10–43 only. Rounds 44–56 (13
rounds, each with an outside closure file) have **no** ledger row: KQ61's “each closed round's
pair is ledgered” implies 47 rounds × 3 trends × 2 sides = 282 rows, so **78 rows are
missing**. `met=True` and that non-conformance coexist because the instrument's round range is
frozen. The instrument's green is a statement about rounds 10–43, not about the current round.

See the separate evidence file for the do-nothing test of this boundary.

## Advisory admit/reject spot-check (advisory only — `LEARNING.md:42`)

This seat is lane-dispatched, so its sample carries **zero** discernment weight. Recorded for
the L1/closure to use or discard.

| Decision | Re-opened | Measured | Advisory |
|---|---|---|---|
| S515 ADMIT (round 56, correction row) | live 2026-10-27, digest matches round-56 copy | Quote present, 18 words, §GIT_CONFIG_COUNT, revision 2.56.0; same URL and quote as S511; page says `git -c` overrides the injected pairs | agree for the narrow runtime-injection claim; do not widen it to "environment always wins" |
| S516 ADMIT (round 57, own-work) | `git show b89bdab2:tools/round56-env-leg-battery.py` | The quoted line `results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))` is line **70**, inside the stated `main()` lines 69–83; the region also holds two more named calls and the mutant assertion | agree: the row's claim (a fixed named call-site inventory) is in the bytes |
| S513 REJECT (round 56) | live 2026-10-27, digest `d9b7737e…` identical to the round-56 copy | `ld.so(8)` contains “secure-execution” **12×** and “dynamic string token” **6×**; `rtld-audit(7)` contains **0** and **0** | the reject ground (“overlaps … for the only fact C1 needs”) is true for C1's fact, but the recorded flip names those topics as future triggers although the source already holds them — the exact round-56 disagreement. Advise keeping the decision for C1 scope while narrowing the ground to claim scope, and leaving the disagreement where the round-57 lesson now records it |

## Round-56 outside defects — lesson-addressed status at this tip

| # | Defect (from `round-56-verifier-spotcheck.md`) | Status | Evidence |
|---|---|---|---|
| 1 | MISSION axis authority vs prompt/config/SCORECARD | open, disclosed | `SCORECARD.md:6` still repeats the open L0 question; no round-57 lesson row |
| 2 | Calibration gate must bind executed battery entries; a roster-literal no-op must fail | addressed in tree and lesson | `tools/round56-prereg-check.py:49-63` binds `ROSTER` to AST `run(...)`/`assert_mutant_breaks_detection(...)` call sites and makes `met` require `executed`; `corpus/lessons/round-57.md:26` records it; acceptance is C1's (another seat). Observability limit: the printed line carries no `executed=` field, so a red result shows only `met=False` |
| 3 | Revisit the S513 rejection rationale / learn the disagreement | lesson row added at `3d2d5d4d`; QUALITY criterion absent | `corpus/lessons/round-57.md:25`; `grep -c round-56 corpus/QUALITY.md` = 0 |
| 4 | Inherited append-only audit exit 1 and invalid `declared_at` bindings; route for repair | not addressed in round 57 | no append-only audit row or re-run in `corpus/lessons/round-57.md` or §Round 57; round 56's exit-1 receipt is the last word. Not re-run by this seat |

## Distinct case 60

Separate evidence file:
`.ufo/waves/round-57/w1/out/R57Item39TrendBoundary/case60-evidence.md`, with the replayable
probe (`case60_trend_binding.py`), the fabricated fixture and three tip receipts
(`case60.out`, `case60-at-77e7f5ee.out`, `case60-at-8a7f1976.out`).

Test: does any lane instrument fail a lesson that claims all three trends improved with zero
evidence? Result: **`FIXTURE_SURVIVES_ALL_LANE_INSTRUMENTS`** — the frozen parser tokenises the
claims but its population (68 fixed paths, rounds 10–43) excludes a round-57 lesson; no other
tool parses trend verdicts; the instrument's `met=True` depends on ledger/document text only.
That is an evidence limit, not a judgment about what round 57's verdicts should be.

## Writes (this seat only)

- `.ufo/waves/round-57/w1/out/R57Item39TrendBoundary.md` (this report)
- `.ufo/waves/round-57/w1/out/R57Item39TrendBoundary/{s515-live-extract.md,
  case60-evidence.md, case60.out, case60-at-77e7f5ee.out, case60-at-8a7f1976.out,
  case60_trend_binding.py, fabricated-round-57-trend-claim.md}`

No tracked file was modified (`git status --porcelain` shows no modified tracked path at the
measured tip). Scratch `/fast/scratch/hyaku/kama-r57/R57Item39TrendBoundary/` is removed after
the receipts above were copied.

Report: .ufo/waves/round-57/w1/out/R57Item39TrendBoundary.md
