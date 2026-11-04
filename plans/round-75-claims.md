# kama round 75 — frozen claims

Frozen before any seat scored. Base revision `dc58e51315e79d36df5fc530c95fbd3aecbf7593`
(lane `master`, == `origin/master` at freeze). A rule changed after a seat has scored is not
this claim's rule (kumitate r42): a seat that disagrees reports a disagreement and never edits
this file. Predicate sentence, counter code and receipt label are the same sentence in all
three places.

Carry-in: the round-74 non-author closure (`corpus/lessons/round-74-verifier-spotcheck.md`)
admitted round 74 and routed seven defects. Its §6 items 1 (coverage-map row), 2 (QUALITY.md
criteria for the round-74 mistakes), 3 (report erratum), 4 (cross-domain-evidence line), 5
(append-only history audit red) and 6 (interpretation debts F1b/F2c, `nc2_two_receipts`,
MT01 seam re-probe, RVW01 exit-map note) are this round's work: items 1, 2, 3, 4, 7 are
required duties of the round (recorded in the lesson and the report, no claim slot), item 5
is C3, item 6 is C1 (F1b/F2c) and C2 (MT01 seam re-probe + the kind/scope arms). Item 7
(closure-pointer re-anchor) is a calibration duty of C1's SCORECARD edit.
`SCORECARD.md` §Planned (round 75) items 1, 2, 3 are C1, C2, C3 in that order.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration 7 is the lane's
lowest non-retired assigned score (operability 8; depth/adjacency tie at 7 but are not
assigned), so C1 satisfies the lowest-axis duty.

C1, C2 and C3 are causally separable: each counter reads its own inputs (SCORECARD fixture
text, the committed C2 module's selftest, the append-only audit's JSON) and exits 0 with the
other two counters absent. C3 touches `registry/append-only-accepted.tsv` and the contract's
`declared_at` column only; C1 and C2 never read either.

## C1 — calibration: the two routed interpretation debts are declared readings with kill arms

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-75/measured/before/c1-mutants.out`): the two readings the round-74 record
discloses as ambiguity are not graded by any committed instrument. Mutating
`tools/round74-selfdesc-canon.py` so that names carried only by tables **older** than the
canonical round join `total` (the "older-demonstrated" reading the lane rejected) leaves its
selftest `pass=11 fail=0`; mutating `tools/round74-receipt-claim-binding.py`'s `REVISION_RE` to
the literal reading (any 40-hex token is a revision mention, including a `recorded at` content
id) leaves its selftest `pass=9 fail=0`. Both mutants are semantically different programs that
ship green — the disclosed reading is prose, not a graded rule.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round75-interpretation-pins.py --repo <lane>` prints one
> `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0` line and exits 0 only when each of
> the lane's two routed interpretation debts is bound to a boundary fixture whose declared
> reading the committed module produces and whose reversed reading a mutated copy of that
> module is caught producing — P1 older-demonstrated: a capability table older than the
> canonical round that carries a name the canon lacks contributes no name to `total` (an older
> table with two extra names leaves `total` at the canonical row count) and the all-tables-union
> mutant scores above it; P2 revision-mention context: a paragraph whose only 40-hex token sits
> in a `recorded at` clause and is not introduced by `rev`/`revision` names no revision (the
> `nc2_recorded_at_hex` paragraph grades clean, exit 0) and the any-hex mutant reports
> `stale-revision` there — it exits 1 naming each `INTERPRETATION_PINS_FINDING <pin>` with the
> declared and observed values and 2 on could-not-evaluate (a module absent, a fixture build
> failure, CLI misuse).

- Fixtures are built by the counter itself in its own scratch (git init under `--work`), the
  way both r74 modules build theirs; nothing is written into the lane.
- P1's fixture is a SCORECARD text: bold canon at round 71 with three rows, plus a round-60
  table carrying those three names and two more. Declared `total=3`; the older-union mutant
  scores `total=5`. The mutant is a source edit applied to a copy of
  `tools/round74-selfdesc-canon.py` inside the counter's work dir, never to the lane file.
- P2's fixture is the round-74 critic's `nc2_recorded_at_hex` record rebuilt from
  `.ufo/waves/round-74/w1/CRT01Claims/attack.md` §F2c: a receipt whose header names `c0` and a
  record paragraph `probe recorded at <c1> naming r.out (content id, not a run revision)`.
  Declared exit `0`; the any-hex mutant exits `1` with `stale-revision`.
- The declared readings are the ones the committed modules already implement (measured: the
  fixtures produce `total=3` and exit `0` at base); the pins make them executable, so a later
  edit that flips either reading is a red receipt, not a silent reinterpretation.
- exit map: `0` clean (`declared=killed=pins`, `escaped=0`), `1` findings, `2`
  could-not-evaluate.
- Counting command: `python3 tools/round75-interpretation-pins.py --repo .`
- Kill rule: each pin's mutant must differ from its declared value; a pin whose mutant equals
  the declared value is `escaped` and fails the counter. The two mutants are the ones measured
  escaping at base (receipt above).
- Control that skips the claimed work: the base modules themselves. Run with the older-union
  and any-hex mutants applied, both selftests stay green (`killed=0 escaped=2`), so a
  do-nothing round cannot reach `declared=2`; a counter that prints the line without running
  the mutants fails P1/P2 because the declared value and the mutant value must differ.
- Wiring: `tools/pre-report-gate.py` arm 8 (`round75-instruments`) composes this module with
  the C2 and C3 modules; the gate verdict becomes
  `PRE_REPORT round=<N> arms=8 failed=<f> uncommitted=<u>`.

## C2 — operability: the two shipped C2 arms are certified by a re-runnable survivor probe, and the two escaping mutants it finds are closed

Motivating evidence, measured at the base revision
(`.ufo/waves/round-75/measured/before/c2-mutants.out`): five defined source mutants of
`tools/round74-receipt-claim-binding.py` were applied to a shared clone and graded by the
committed module's own `--selftest`. Three are killed (`case-hex` — `HEADER_RE_V2` without
`re.I`; `kind-boundary` — a same-line tip claim that does not inherit `stale-claim`;
`paragraph-scope` — per-line instead of per-paragraph grading) and **two escape**
(`conflict-off` — the conflicting-header check in `_header_rev_v2` removed;
`header-window` — `HEADER_WINDOW` narrowed 5→3). The module's docstring declares both
behaviours ("conflicting headers inside the first five lines stay a finding source
(`unbound`), never a crash"), so both escapes are unarmed rules, and MT01's hand-off check 1
(the seam arm must be re-probed when the module is touched) has no committed instrument.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round75-survivor-probe.py --repo <lane>` prints one
> `SURVIVORS2 mutants=5 killed=5 escaped=0` line and exits 0 only when it applies five named
> source mutations to a copy of the committed `tools/round74-receipt-claim-binding.py` in its
> own scratch, runs the pristine module's selftest green and every mutated copy's selftest red,
> and names for each mutant the selftest arm that fails — `case-hex` (the `tip=`/`rev=` header
> parse loses `re.I`), `kind-boundary` (a same-line tip claim no longer inherits `stale-claim`),
> `paragraph-scope` (per-line instead of per-paragraph claim grading), `conflict-off` (the
> conflicting-header check in `_header_rev_v2` is removed) and `header-window` (`HEADER_WINDOW`
> narrowed from 5 to 3) — it exits 1 naming `SURVIVORS2_FINDING <mutant>` with the mutant's
> selftest exit and the arm that stayed green, and 2 on could-not-evaluate (the module absent,
> a clone failure, CLI misuse).

- The module gains the two arms the probe requires: a committed fixture whose receipt carries
  conflicting `rev=` headers inside the five-line window (graded `unbound`, never a crash) and
  a fixture whose header names the revision on the fifth line (a narrower window loses it).
  Both fixtures live in the module's selftest; the probe grades the module, not the fixtures.
- Decision on the round-74 hand-off "does the same-line inherited kind earn its own fixture in
  the kill set": yes, it already has one (`same-line-stale-claim`, r74 arm 6) and the probe
  certifies it as load-bearing (`kind-boundary` killed); no new fixture is added for that
  class. Recorded in the round lesson.
- exit map: `0` clean, `1` findings (a survivor is a finding), `2` could-not-evaluate.
- Counting command: `python3 tools/round75-survivor-probe.py --repo .`
- Kill rule: at base the same probe over the same five mutants reports
  `killed=3 escaped=2`; the claim's target is `escaped=0` with the same five mutants. A
  do-nothing round leaves the two escapes, so the target is unreachable without the module
  arms.
- Control that skips the claimed work: the base module's `--selftest` over the five mutants
  (`killed=3 escaped=2`, receipt above). A probe that prints `killed=5` without running the
  mutants fails the per-mutant red requirement: each mutant's selftest exit is printed and must
  be non-zero.
- Non-goal: the probe grades the two shipped arms; it does not re-open the frozen round-74
  predicate or the F2a/F2b/F2c readings (C1 owns F2c).

## C3 — freshness: the append-only audit's undisclosed deletions are graded as accepted history and every contract declaration binds

Motivating evidence, measured at the base revision
(`.ufo/waves/round-75/measured/before/c3-audit.out`): `python3 tools/append-only-audit.py
--repo .` exits 1 with `commits=575 files=143 events=223 restored=87 unrestored=53 ungraded=78
disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0 ungraded_lines=330
regressed=0 bad_declarations=5`. The tool's own disclosure ledger
(`registry/append-only-disclosures.tsv`, introduced round 51) accepts only commits that
precede its introduction, so the 53 post-ledger events cannot be disclosed there — they are
either restored or graded somewhere that does not weaken that rule. Five of the ten contract
rows point at a `declared_at` line that never binds (`corpus/README.md:761`,
`SKILL.md:578`, `corpus/README.md:1239`).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round75-append-accepted.py --repo <lane>` prints one
> `APPEND_ACCEPTED events=<e> accepted=<a> unaccepted=<u> bad_rows=<r> bad_declarations=<d>`
> line and exits 0 only when the byte-frozen `tools/append-only-audit.py --json` reports zero
> unbound contract declarations and every undisclosed deletion event that audit computes
> carries a committed `registry/append-only-accepted.tsv` row (`commit`, `file`,
> `line_sha256`, `count`, `class`, `note`) whose commit and file match an event, whose line
> hash and count match that event's `undisclosed` entries, and whose class is the mechanical
> class that event computes — the register never changes the audit's `unrestored` count, it
> grades each undisclosed event as accepted history with the commit subject and a one-line
> reason — it exits 1 naming `APPEND_ACCEPTED_FINDING <class> <detail>` and 2 on
> could-not-evaluate (audit unreadable or absent, register absent, CLI misuse).

- The register is generated from the audit's own JSON and `git log -1 --format=%s` per commit;
  no row is hand-typed, so no row can name an event the audit does not compute.
- Byte-exactness: `registry/append-only-contract.tsv`'s five unbound `declared_at` pointers
  are re-pointed at new declaration lines appended to `corpus/README.md`
  (`## Append-only declarations (round 75)`); nothing is edited in place in the corpus.
- The register must not accept a row for a restored event, a row with a wrong line hash, or a
  row whose class differs from the event's mechanical class. Those three rejections are the
  counter's own negative controls, run in its `--selftest`.
- exit map: `0` clean (`unaccepted=0 bad_rows=0 bad_declarations=0`), `1` findings, `2`
  could-not-evaluate.
- Counting command: `python3 tools/round75-append-accepted.py --repo .`
- Kill rule: at base there is no register (`accepted=0 unaccepted=53 bad_declarations=5`). The
  target is `accepted=events unaccepted=0 bad_rows=0 bad_declarations=0` with the register's
  every row hash-bound. A `wc -l` of the register is not a measure: a register with one wrong
  hash fails `bad_rows`.
- Control that skips the claimed work: a 53-line register whose rows carry no hashes, or the
  count-only file, fails the hash binding; the base tree fails with `accepted=0`.
- Non-goal: the audit's `unrestored=53` stays in its summary. This claim grades the events; it
  never erases them, and it never re-stamps a historical receipt (notes cite commit subjects,
  not re-runs).

## Frontier step (rides inside the claim cap; no fourth claim)

- Sourced claim: **C3** rests on a row opened this round for `gitattributes(5)`
  (`https://git-scm.com/docs/gitattributes`): the "Line endings are normalized to LF in the
  index every time the file is checked in" rule grounds the largest accepted-history class in
  the register (the round-65 `S537` LF re-land rewrote every registry row, 639 deletions in
  one commit at `ea33a78f2b0b`). The row is opened live this round (access date, ≤25-word
  located quote, retained bytes) and appended only after the scratch-mirror census gate exits
  0. Knowledge entry: `corpus/knowledge/append-only-accepted-history.md`.
- Mistakes mined into `corpus/lessons/round-75.md` §Mistakes: at least one, from this round or
  an earlier one, with class · evidence pointer · captured-by · fix, the fix shown able to fail.
- Assimilation: no `merge/kama/` entry is adopted this round; the id-collision check and the
  quarantine slice run read-only and are committed under `.ufo/waves/round-75/assimilation/`.
- considerthese: at most one still-unimplemented proposal, mined through the lane's own bar.

## Required duties of the round (no claim slot)

1. Coverage-map row for `corpus/knowledge/host-block-base-revision.md` (round-74 routed
   defect 1) appended as a `## Coverage map — round 74 addition` block, with the remaining
   map-gap count.
2. Three `corpus/QUALITY.md` criteria for the three round-74 mistake classes (routed defect 2),
   each citing `corpus/lessons/round-74.md` §Mistakes.
3. Report erratum: `.ufo/reports/round-74/kama.md:102` says `cited=200 resolved=182`; the
   receipt committed at `8020b2f2` says `cited=202 resolved=184` (routed defect 3).
4. Cross-domain-evidence line in the report (routed defect 4).
5. `SCORECARD.md` calibration row re-anchored to `round-74-verifier-spotcheck.md` (routed
   defect 7).
6. RVW01's C1 exit-map note pinned or retired in the lesson (routed defect 6).

## Freeze control

`controls/freeze.txt` pins `git -C <lane> rev-parse master` (the base line), the sha256 of this
plan, the sha256 of the control script, and the sha256 of the three before-receipts. The
control was run from the base bytes before any seat scored:
`python3 .ufo/waves/round-75/controls/mutation-control.py --lane <lane> --work
/fast/scratch/hyaku/kama-r75/controls`.
