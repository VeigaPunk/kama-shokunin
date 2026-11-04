# kama round 79 — frozen claims

Lane: kama. Round 79 (attempt 1). Base (lane tip at round start):
`ee53f1a25eab93a8ab55bbb877e49e2e731df535`. Assigned axes (`shokunin.conf` kama row):
operability + calibration. Sealed revision for claim C1 (round 78's tip):
`7a3cd98243b69fcbee0cc9e31878782bd8459320`.

Three claims, three distinct axes; C1 works calibration (7), the lowest assigned
axis, which sits below the saturation line (8/10), so the stagnation nudge is inactive.
This plan is the freeze: the predicates, fact value strings, target lines, controls and
kill rules below are fixed before any seat or counter produces data, and are not
rewritten afterwards. Pre-freeze receipts sit under `.ufo/waves/round-79/measured/before/`
and `.ufo/waves/round-79/measured/control/`.

## C1 — calibration: the round-78 self-record's six declared facts re-derive, or are answered by dated value-bound corrections

PREDICATE (this sentence is the counter's docstring `PREDICATE`, its receipt label and the
claim text — one sentence in three places):

> `python3 tools/round79-selfrecord-round78.py --repo <lane>` prints one `SELFRECORD_R78
> claims=6 mismatches=0 corrected=2 unbacked=0` line and exits 0 only when each of the six
> facts the round-78 self-record declares re-derives from the tree at the sealed revision
> 7a3cd98243b69fcbee0cc9e31878782bd8459320, or is answered by exactly one committed
> correction block at that revision whose stated new value re-derives at the tip; it exits 1
> naming every unanswered fact otherwise.

The six facts, each declared by the record's own bytes at the sealed revision and each
derived from the tree at that same revision (value strings are the receipt labels):

| Fact | Declared by the record | Declared value string | Observed at sealed |
|---|---|---|---|
| F1 lowest assigned axis | "the lowest assigned axis (calibration 7) carries C1" | `lowest-axis=calibration:7` | from the sealed `## Axes` table over the assigned pair |
| F2 population | "sources registry 292 rows …; filtered knowledge entries 51 (two new: …); `SKILL.md` sha256 `a50f6f74…` (1736 lines …); `PROVINCE.md` sha256 `6b8c604f…` (331 lines …)" | `population=sources:292,knowledge:51,skill:a50f6f74/1736,province:6b8c604f/331` | row count, filtered entry count, blob sha prefix and newline count at sealed |
| F3 wave shape | "One v1 wave of 12 seats (3 executor, 3 scribe, 1 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/12 = 33 %)" | `wave=seats:12,executor:3,scribe:3,scout:1,connector:1,reviewer:1,critic:2,mutation-tester:1,attack:4/12` | `.ufo/waves/round-78/w1-spec.json` at sealed |
| F4 wave dead seats | "Three seats returned output (EX01C1Selfrecord, SC02Lesson, SCT01Recon); nine returned empty" | `wave-dead=returned:3(EX01C1Selfrecord,SC02Lesson,SCT01Recon)/empty:9` | `.ufo/waves/round-78/w1-results.json` at sealed |
| F5 tip accounting | "The tip accounting is the round-77 counter, which is green at `rev=22cce544`" | `tip-accounting=rev:22cce544/is-tip:true` | the named revision against the sealed tip: `is-tip:false` (an ancestor) |
| F6 pre-correction run | freeze-divergence item 4: "the pre-correction tip run and the corrected tip run are both in the lesson" | `c1-pre-correction-run=committed` | no blob under `.ufo/waves/round-78/` at sealed carries `mismatches=1`: `absent` |

Pre-freeze measurement (`measured/before/c1-enum.out`): `SELFRECORD_R78_ENUM claims=6
stale=2 corrected=0`, exit 1 — F5 and F6 are the two stale facts, which fixes
`corrected=2` in the target before data. The two corrections are F5 (the record calls
`rev=22cce544` the tip; the sealed tip is `7a3cd982`) and F6 (the pre-correction run is
prose, not a committed receipt — round 78's own routed defect R78V2).

- **Target:** exit 0 with `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0` at
  the round-79 tip.
- **Control that skips the claimed work:** the same counter, same sealed tree, no
  correction blocks at the tip — `SELFRECORD_R78 claims=6 mismatches=2 corrected=0
  unbacked=0`, exit 1 (`measured/before/c1-score-nocorrections.out`, produced pre-freeze).
  A do-nothing round cannot print the target line.
- **Correction grading:** a block is `corrected F<n> old=<value> new=<value> at=<40-hex>
  date=<ISO>`; it answers a fact only when `old` equals that fact's declared value, `at`
  is the sealed revision (40 hex, resolving to it) and `new` re-derives at the tip. Two
  blocks for one fact answer nothing; a 41-character `at` token answers nothing (the
  round-78 `unresolvable-cited-hash` class).
- **Scope ruling:** facts are read from `git show <sealed>:…`, never from the worktree, so
  the round's own record commit cannot refute a fact (the round-78 F2 defect). The
  correction container is `corpus/lessons/round-79.md` §Corrections, appended, never a
  rewrite of the round-78 record.
- **Kill rule:** the claim fails if the frozen line is not printed at the tip, if the
  control reaches the target line, or if any correction's `new` value does not re-derive.

## C2 — operability: the pre-report gate composes the three round-78 instruments as its own arm

PREDICATE:

> `python3 tools/pre-report-gate.py --selftest` prints `PRE_REPORT_SELFTEST pass=26
> fail=0`, and `python3 tools/pre-report-gate.py --repo <lane> --round 79 --tip <rev>`
> prints one `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0` line and exits 0, only
> when the tenth arm `round78-instruments` runs
> `round78-selfrecord-round77.py --selftest`, `round78-append-registers.py --selftest` and
> `round78-live-reconcile.py --selftest`, each exiting 0 with a `*_SELFTEST pass=N fail=0`
> summary, a red, malformed or absent instrument fails the arm closed naming it, and the
> `SKILL.md` pre-report-gate registry row names `round78-instruments` and the new tally in
> the same commit.

- **Before:** the gate has `ARM_ORDER` of 9 arms and prints `PRE_REPORT_SELFTEST pass=22
  fail=0` (`measured/before/c2-gate-arms.out`, `measured/before/c2-gate-selftest.out`); the
  three round-78 instruments are certified only by their own selftests and by claim
  receipts, so a gate run at the tip does not execute them.
- **Target:** `PRE_REPORT_SELFTEST pass=26 fail=0` and `PRE_REPORT round=79 arms=10
  failed=0 uncommitted=0` at the round-79 tip.
- **Control that skips the claimed work:** the base gate (no arm 10) prints `arms=9`, so it
  cannot reach `arms=10`; inside the selftest, a red `round78-*` stub must fail the arm
  naming the instrument and an absent module must fail closed naming `missing <script>`.
  `out-of-population-row` and `uncommitted` stay red-capable (the round-78 register
  selftest keeps its out-of-population arm; selftest case (b) keeps the wave-dir
  cleanliness arm red).
- **Scope ruling:** the arm composes each instrument's `--selftest` only (bounded, ~2 s
  wall); the scored gate is the pre-report gate at the tip, never a second claim counter.
  The arm count is derived from `ARM_ORDER`, not restated independently (KQ123).
- **Kill rule:** the claim fails if the tip prints `arms=9`, if any selftest case passes
  without the arm going red where it must, or if the SKILL row and the module disagree at
  the tip.

## C3 — coverage: the probe reports an unregistered serving listener as its own census class

PREDICATE:

> `python3 tools/round79-unregistered-census.py --repo <lane>` prints one
> `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` line and exits 0
> only when `bash tools/kama-probe.sh listeners` reports the lane-owned llama.cpp fixture,
> serving on an unregistered loopback port, as `registered=no` under a registry that does
> not declare that port and as `registered=yes` under one that does, the summary's
> `unregistered`/`governed` counts move with the class, and a probe without the class is
> `class_missing=1` with exit 1.

- **Before:** `bash tools/kama-probe.sh listeners` has no `registered` column and no
  `governed`/`unregistered` summary keys; the live host's model endpoints are counted as
  `model_endpoints=7` with no registry relation (`measured/before/c3-listeners-base.out`).
  Round 78 recorded one such listener (`127.0.0.1:1234`, four LFM3 ids) as a manual
  observation only.
- **Target:** exit 0 with `unregistered=1 governed=1 class_missing=0`, the named fixture
  port classified both ways by the two scratch registries.
- **Control that skips the claimed work:** the base probe copy (no class column) scored by
  the frozen counter — `class_missing=1`, exit 1
  (`measured/control/c3-base-probe.out`). The negative leg is inside the counter: a
  listener the registry declares must read `registered=yes` and must never be counted
  `unregistered`.
- **Sourced claim:** rests on the round-79 `SOURCES.md` row for llama.cpp's router
  `GET /models` (opened this round; the Gate block carries URL, access date and a located
  ≤25-word quote): the router lists models that are not running and marks each with a
  `status.value`, so a model list is an inventory, not a readiness claim. That is why the
  class names a *serving listener the registry does not govern* and never asserts a loaded
  model or consumer readiness.
- **Scope ruling:** this is a census class, not a verdict: the verdict vocabulary
  (`MODEL_OK` / `MODEL_MISMATCH` / `FOREIGN_SERVICE` / `UNAUTHORIZED_SERVICE` / `DEAD` /
  `NOT_HTTP` / `MODEL_LOADING`) is unchanged, no registry row is admitted (consumer pins
  are operator-owned), and the live-host leg is informational, never a gate. The fixture is
  the lane-owned pinned llama.cpp child on an unregistered loopback port, torn down in the
  run.
- **Kill rule:** the claim fails if the class reads `unregistered` for a registered port, if
  the two registry legs return the same class, or if the class needs a registry row to be
  admitted.

## Round scope and record allow-list

Paths this round may commit: `plans/round-79-claims.md`;
`tools/round79-selfrecord-round78.py`, `tools/round79-unregistered-census.py`,
`tools/pre-report-gate.py`, `tools/kama-probe.sh`; `SCORECARD.md`, `LOG.md`, `SKILL.md`,
`PROVINCE.md`; `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/README.md`,
`corpus/knowledge/*.md`, `corpus/lessons/round-79.md`; `.ufo/waves/round-79/**`;
`registry/*` only when a routed disposition requires a register row. Nothing outside this
list; no sibling lane and no operator-owned file is touched.

## Frontier step (§2b) and round-78 routed defects

- **SOURCES:** one new row for llama.cpp router `GET /models` (URL opened this round,
  pinned commit `39febd2adb947b70da35e95f9351b3bf58ad170a`, the build the live listener
  runs), one admitted `corpus/knowledge/` entry on the census class, one coverage-map row;
  a reject is recorded with its flip (the `llama.cpp` server README already held by S001
  and S526 is not re-rowed for the same surface).
- **Mistake mined:** round 78's "tip" wording — a record that calls an ancestor revision
  "the tip" while claiming a green gate (R78V1), captured by the new F5 fact.
- **Round-78 routed defects (R78V1–R78V7):** V1/V4 by tip-run receipts committed at the
  round-79 tip, V2 by the reproduced pre-correction receipt, V3 by a post-change selftest
  receipt, V5 by a revision-bound C3 receipt under the round-79 measured tree (round-78
  receipts stay history, never rewritten), V6/V7 by dispositions recorded in
  `SCORECARD.md` §Round 79 and the round report. Each disposition names its evidence
  pointer or says why it is not fixed this round.
