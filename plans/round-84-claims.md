# round-84 claims (kama) — frozen plan

Base revision `aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0` (the round-83 non-author closure tip; `jj-lane.sh
state` prints `branch=master local=aca4f33a… remote=aca4f33a… ahead=0 behind=0`). Sealed revision C2 grades
`ae4323171596126a9265f7f6c8af4164d499ba09` (the round-83 lane tip the round-83 report cites). Three claims,
three distinct axes, each measured on its own receipt. Frozen before any seat scored; every control is built
and committed before its data run. Freeze date 2026-11-04.

Axis assignment (`../shokunin.conf`, read at the base): **operability + calibration**. Lowest axis at the
base: calibration 7 (depth 7, adjacency 7 unassigned-shared; operability 8) — C2 works calibration, so the
lowest-axis obligation binds; the saturation line is 8/10 with N=4, calibration sits below the line, so the
stagnation nudge is inactive. C1 and C3 move the operability and freshness surfaces the round actually
changes. No axis score move is claimed; claims are instrument-and-record moves graded by their counters.

Routed-defect basis (round-83 non-author closure, `corpus/lessons/round-83-verifier-spotcheck.md`): R83V1
(stale live SCORECARD cells), R83V2 (three round-83 instruments unregistered; arm 13 uncomposed), R83V3 (C1
population instability + wrong-deletion-round note escape), R83V4 (register-row-introduction wording),
R83V5 (coverage-table rows for the round-83 entries), R83V6 (closure pointer). R83V4/V5 are frontier-step
work below, not claims.

## C1 — operability: the late register's note binds to the event commit's own subject round, the round-83 stale rows rotate out disclosed, and the round gate runs thirteen green arms

**Predicate (one sentence, frozen):** `python3 tools/pre-report-gate.py --repo . --round 84 --tip master`
prints `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0` and exits 0, and on the same tree
`python3 tools/round81-append-debt.py --repo . --round 84` prints `bad_rows=0 unaccepted=0` exit 0 while
`python3 tools/round81-append-debt.py --repo . --round 84 --late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv`
prints exactly one `APPEND_DEBT_FINDING note-wrong-deletion-round` line and exits 1.

- **Target values:** `arms=13`, `failed=0`, `uncommitted=0`, exit 0 (counter A); `bad_rows=0`,
  `unaccepted=0`, exit 0 on the real register; `bad_rows=1` with class `note-wrong-deletion-round`, exit 1,
  on the mis-noted fixture (counter B legs).
- **Work:** (a) `tools/round81-append-debt.py` `grade()` gains the subject-round binding
  `tools/round82-late-delta.py` already enforces: a late row's note deletion round must equal the round the
  event commit's own subject declares (`^round-([0-9]+):`); mismatch class `note-wrong-deletion-round`;
  an unresolvable subject leaves the row's grade unchanged (no invented refusal). Two new selftest arms
  (`note-subject-mismatch`, `note-subject-unresolvable`) join the suite. (b) The ten round-83 late rows
  (register lines 105–114, event `0d7c7c3e` `SCORECARD.md`) rotate disclosed into
  `registry/append-only-late-r83-restored.tsv` and out of `registry/append-only-late.tsv`: their event is
  fully restored at the base, so the audit population no longer holds it and the rows are ungradeable
  history (round-83 mistake, R83V3); the round lesson records old→new and a disclosure row lands in
  `registry/append-only-disclosures.tsv`. (c) One new late row accepts the round-83 event the audit holds
  (`96e28374…` `SCORECARD.md`, 1 undisclosed line) with note `round-84 accepts round-83 "<commit subject>";
  …` — the first row the new binding grades live. (d) `tools/pre-report-gate.py` composes arm 13
  `round83-instruments` from the round-83 pair's selftests (`round83-pending-falls.py` →
  `PENDING_FALLS_SELFTEST`, `round83-pin-rechecks.py` → `PIN_RECHECK_SELFTEST`) with the arms 10–12
  own-summary rule, fail-closed on a red, malformed or absent instrument; the gate docstring and selftest
  fixtures move to `arms=13`.
- **Registration (R83V2):** SKILL.md gains registry rows for `round83-pending-falls.py`,
  `round83-selfrecord-round82.py`, `round83-pin-rechecks.py` (kind, entry command, exit map, selftest,
  pinned values, write scope, owner kama) and for the round-84 instruments this round lands.
- **Red-before (able to fail):** at the freeze tree, counter B against the committed fixture under the
  pre-fix tool prints `bad_rows=0` — the mis-noted row (`round-81 accepts round-78` over a round-79
  event) produces **no finding at all** and is accepted; the run's only finding is the unrelated
  `count-short` for the not-yet-accepted round-83 event (`unaccepted=1`, exit 1); receipt
  `.ufo/waves/round-84/measured/before/red-debt-fixture.out` (pre-fix). After the fix the same command
  prints exactly one `note-wrong-deletion-round` finding (receipt `measured/after/…`). [Freeze
  amendment 1, before any seat scored: the bullet first predicted `exit 0`; the actual pre-fix exit is
  1 via that unrelated `unaccepted=1`. The binding predicate sentence above is unchanged.]
- **Do-nothing control (committed before data):** `.ufo/waves/round-84/measured/before/ctl-gate.out` —
  the gate at the freeze tree prints `arms=12` (arm 13 absent), `failed>=2` (debt `bad_rows=10`; the
  closure-pointer arm), exit 1: no-work cannot reach `arms=13 failed=0`.
- **Kill rule:** any failed arm, any unaccepted/bad/out-of-population row, `uncommitted>0`, or counter B
  exiting 0 post-fix fails the claim. An honest miss is reported, never re-targeted.
- **Mutation guard:** deleting or weakening the new binding check must turn the `note-subject-mismatch`
  selftest arm red (mutation-tester seat verifies; survivors reported).

## C2 — calibration (lowest assigned axis): the round-83 record's declared facts re-derive at the sealed revision or are answered by dated value-bound corrections

**Predicate (one sentence, frozen):** `python3 tools/round84-selfrecord-round83.py --repo .` prints
`SELFRECORD_R83 claims=8 mismatches=0 corrected=6 unbacked=0`, exits 0, and `--selftest` prints
`SELFRECORD_R83_SELFTEST pass=N fail=0` with N≥10, exit 0.

**Fact table (population frozen at freeze; witnesses committed before data):** declared values read at the
sealed revision `ae4323171596126a9265f7f6c8af4164d499ba09`; receipt witnesses read at the graded tip; each
stale fact answered by exactly one dated correction block (`corrected F<n> old=<token> new=<token>
at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=<path>`) in
`corpus/lessons/round-84.md`, whose fix path carries the whole new token in tip bytes outside
`LOG-CORRECTION` lines and `#### round-<N> correction` blocks (the round-83 rule, reused verbatim).

| Fact | Container at sealed | Declared | Witness (committed bytes) | Disposition |
|---|---|---|---|---|
| F1 | `SCORECARD.md` head authority paragraph + `## Axes` operability row | `late=23` (and `exit 0`) | `.ufo/waves/round-83/measured/final/c1-legA.out`: `late=22 … bad_rows=10`, exit 1 | corrected → `r83c1-late=22` |
| F2 | same authority paragraph | `accepted=8 … falls=yes`, exit 0 | `.ufo/waves/round-83/measured/final/c1-pending.out`: `window=7 accepted=7 … falls=no`, exit 1 | corrected → `r83c1-window=7`, `r83c1-falls=no` |
| F3 | same authority paragraph | `population=123 carried=103 new=20 bad=0`, exit 0 | `.ufo/waves/round-83/measured/final/c1-delta.out`: `population=113 carried=103 new=10 bad=10`, exit 1 | corrected → `r83c1-delta=113/103/10` |
| F4 | `SCORECARD.md` §Round 82 C2 row (sealed line 4971) | `new=0` | `.ufo/waves/round-82/measured/before/c2-late-delta-base.out`: `new=15` | corrected → `r82c2-new=15` (the carried fourth stale cell, R83V3) |
| F5 | `## Axes` freshness row | selftest `pass=11` | `.ufo/waves/round-83/measured/final/c3-selftest.out`: `PIN_RECHECK_SELFTEST pass=14 fail=0` | corrected → `r83c3-selftest=14` |
| F6 | authority paragraph | `SELFRECORD_R82 claims=6 mismatches=0 corrected=3 unbacked=0`, exit 0 | `.ufo/waves/round-83/measured/final/c2.out`, exit 0 | holds (direction test) |
| F7 | authority paragraph + freshness row | `PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0`, exit 0 | `.ufo/waves/round-83/measured/final/c3.out`, exit 0 | holds (direction test) |
| F8 | `## Axes` calibration row | `latest outside closure corpus/lessons/round-82-verifier-spotcheck.md` | the round-83 non-author closure `corpus/lessons/round-83-verifier-spotcheck.md` (committed `aca4f33a`, dated 2026-11-04) is newest; `python3 tools/round69-newest-closure-counter.py --repo . --rev aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 --since-round 63` resolves it | corrected → `r83-closure=round-83-verifier-spotcheck.md` (R83V6; the live row is re-anchored in place — head sections are re-derived) |

- Live-cell repairs ride the same corrections: the head authority paragraph and the three axis rows
  (`## Axes`, re-derived in place by the round-42 contract) carry the final values; the dated §Round 84
  section carries the correction tokens; no dated section is edited in place.
- **Red-before:** the new counter run at the tree that holds the instrument but not the corrections prints
  `mismatches=6 corrected=0 unbacked=6`, exit 1; receipt `.ufo/waves/round-84/measured/before/red-selfrecord.out`.
- **Do-nothing control (committed before data):** `.ufo/waves/round-84/measured/before/ctl-selfrecord.out` —
  at the freeze tree the counter does not exist (`exit 2`): no-work cannot print the target line.
- **Kill rule:** `mismatches>0`, `unbacked>0`, a corrected hold, an unknown fact, exit != 0 — claim fails;
  the population stays 8 facts; widening after data rewrites the claim and is refused.

## C3 — freshness: the pin-recheck register grades every relation row including the formerly ungraded one, against documents opened this round

**Predicate (one sentence, frozen):** `python3 tools/round83-pin-rechecks.py --repo . --register
registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv` prints
`PIN_RECHECK rows=5 graded=5 ungraded=0 bad=0` and exits 0, with the held verdict mix (`holds/reworded/
moved/drifted`) whatever the committed bytes derive, each recheck row's anchor extracts naming documents
opened this round in `corpus/lessons/round-84.md` `## Gate`.

- **Target values:** `rows=5`, `graded=5`, `ungraded=0`, `bad=0`, exit 0. Before:
  `rows=5 graded=4 holds=4 … ungraded=1 bad=0` (exit 0) — relation 3 (`llama.cpp` `b7200`, cross-lane
  kengaku role) is ungraded because the lane holds no document at that ref.
- **Work:** open this round, by `curl -sS`, the documents the register cites: the llama.cpp server README at
  `b7200` (resolving the era-correct path; recorded with its URL, sha256, and located quote), and fresh
  reads of the three newest-side documents (`b12111` README, sglang `v0.5.23` native API, vllm `v0.33.0`
  prefix-caching) to confirm byte-identity or drift. New `corpus/anchors/` extracts carry the exact header
  format (`# url=<…> sha256=<64hex> ref=<ref> lines=<a>-<b>`). Relation 3's recheck row grades honestly
  from the b7200 bytes (the four-value verdict the bytes derive); if the document proves absent at every
  era-correct path, the row stays `ungraded` and the claim lands `missed` — never laundered. The SGLang
  `/ready` and `/ping` routes (v0.5.23 read, lines 111–112) enter `corpus/knowledge/runtime-health-surface-matrix.md`
  as an appended dated section; other engines' documents stay frontier.
- **Sourced-claim duty:** the claim cites the `S###` rows opened this round (b7200 document and the fresh
  reads); rows enter `corpus/SOURCES.md` per contract v1 with Gate quotes.
- **Do-nothing control (committed before data):** `.ufo/waves/round-84/measured/before/ctl-pinrecheck.out` —
  the register at the freeze tree prints `ungraded=1`: no-work cannot reach `graded=5 ungraded=0`.
- **Kill rule:** `bad>0` (a declared verdict contradicting bytes), `ungraded>0` (relation 3 unresolved),
  any extract whose worktree bytes differ from HEAD, or an anchor header failing its own sha256 — claim
  fails; a `moved/drifted/reworded` verdict on relations 1/2/4/5 does NOT fail the claim (honest drift is
  the freshness signal), only inconsistency does.

## Axis and verdict rules

Verdicts: `improved | harmed | unchanged | unprovable-but-better` per claim, reported honestly; a trade
anywhere is not an improvement. No axis score changes are claimed; SCORECARD score rows stay 8/8/7/9/7/7
unless the closure rules otherwise. Trend verdicts name evidence: expansion (new opened rows + the matrix
addition), quality (instruments registered, gate arm 13, stale cells corrected), discernment (the round-83
closure's routed defects answered with re-derivable counters). An unrun check has not passed.

## Frontier step (not a claim)

- Census before: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0
  (`kama ok`, W01/W04 warnings only) at 2026-11-04, registry 311 rows. Census after runs at round end and
  must exit 0.
- `corpus/lessons/round-84.md` carries `## Gate` (every new S-row: URL, access date, ≤25-word located
  quote), `## Corrections` (F1–F8 blocks), `## Mistakes` (≥1 mined mistake: class · evidence · captured-by
  · fix — the round-83 interim-values-in-live-cells mistake, class `number-drift`/`survivor`, captured-by
  KQ27, fixed by C2's corrections and the new KQ row binding current-evidence cells to the terminal
  receipt revision), and the assimilation line.
- R83V4: an appended correction paragraph in `corpus/knowledge/register-row-introduction.md` naming the
  last-modification (not first-introduction) reading; R83V5: real coverage-table rows for the round-83
  entries, appended without shifting filed anchors.
- SOURCES append block is built in scratch and census-gated
  (`scripts/sources-census.sh validate --file`) before any registry append.
- Assimilation: `merge/kama/` package and `considerthese/` are read this round; a theme is adopted only if
  it rides an already-frozen claim as ordinary curation; otherwise the report says `Assimilation: none`.

## Shape

ONE v1 wave (`w1`, band 8–16 per `ufo-wave-policy.json` `dispatch.swarm`) of 12 seats — 4 executor,
1 scribe, 1 scout, 1 connector, 1 reviewer, 1 critic, 1 mutation-tester, 1 labrat (attack share 4/12 ≥
25%, connector ≤2) — dispatched through the inline spawn handoff after this plan, the fixture and the
control receipts are committed. The L1 holds the planner seat (the validator admits no planner role).
Residual work integrates seat outputs; any residual verification call stays ≤4 seats and is named in the
report. WAVE-DONE precedes the report.
