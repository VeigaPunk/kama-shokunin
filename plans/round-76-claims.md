# kama round 76 — frozen claims

Frozen before any seat scored. Base revision `b06cc612711560c53eef3ec21484c6963601262f`
(lane `master`, == `origin/master` at freeze). A rule changed after a seat has scored is not
this claim's rule (kumitate r42): a seat that disagrees reports a disagreement and never edits
this file. The predicate sentence, the counter code and the receipt label are the same sentence
in all three places.

Carry-in: the round-75 non-author closure (`corpus/lessons/round-75-verifier-spotcheck.md`)
admitted round 75 and routed eight defects (§6). Its item 8 — the receipt-binding counter's
citation scope — is C1; items 1 (stale PROVINCE digest), 3 (stale LOG facts) and 4 (no
committed gate-selftest receipt) are the fact population of C2; item 5 (coverage-map row) and
item 6 (QUALITY criteria for the round-75 mistake classes) are required duties closed in the
lesson/README/QUALITY edits, no claim slot; item 2 (C2 after-receipt not a faithful capture) is
re-captured this round and cited; item 7 (round-local Gate reject) is a duty on
`corpus/lessons/round-76.md`. `SCORECARD.md` §Planned (round 76) items 1, 2 and 3 are C1, C2
and C3 in that order, restated below as frozen.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration **7** is the lane's
lowest non-retired assigned score (operability 8), so C2 satisfies the lowest-axis duty. C1
operability and C3 freshness are the two other axes the lane owns; two claims on one axis would
count as one claim, so the three claims name three distinct axes.

The three claims are causally separable: C1 reads the round-75 self-record plus the frozen
receipt-binding modules; C2 reads the round-75 SCORECARD/LOG self-record sentences and the
calibration row; C3 reads the append-only audit JSON and the two registers. Each exits 0 with
the other two counters absent from the tree.

## C1 — operability: the citation population is fence-scoped and record-path-scoped, and the round-75 record is classified instead of ungraded

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-76/measured/before/c1-receipt-claim.out`): the frozen receipt-claim counter
cannot grade its own preceding record at all —
`RECEIPT_CLAIM_V2 CouldNotEvaluate: base tool could not evaluate: RECEIPT_TIP_BINDING_UNREADABLE
cited path is not a receipt file (.py): .ufo/waves/round-75/controls/build-spec.py
(corpus/lessons/round-75.md:125)`, exit 2. The cited bytes sit inside a fenced block the
append-only contract forces the lane to keep (`corpus/lessons/round-75.md` §Superseded bytes and
§Restored paragraph), so the record can never become gradeable under the fence-blind reading.
A dry re-run with fences stripped
(`.ufo/waves/round-76/measured/before/c1-fence-dryrun.out`) shows what remains: `cited=11
bound=6 unbound=2 shifted=3`, i.e. two legacy wave receipts without `# rev=` headers
(`.ufo/waves/round-75/assimilation/summary.out`,
`.ufo/waves/round-75/controls/freeze.txt`) and three before receipts shifted by the self-
description commit `c9ab73d8` (`PROVINCE.md` capability-evidence row).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round76-receipt-scope.py --repo <lane> --round 75` prints one
> `RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
> nonreceipt=0 unclassified=0` line and exits 0 only when the round-75 self-record's citation
> population is classified under the declared fence scope — a citation inside a CommonMark
> fenced block is quoted history, never a citation, and an unclosed fence is
> could-not-evaluate — and under the declared record-path scope — a delta between a receipt's
> recorded revision and the tip that touches only the self-description paths `PROVINCE.md`,
> `SKILL.md` and `corpus/**` does not shift that receipt — with the two legacy header-less wave
> receipts named individually as `RECEIPT_SCOPE_UNBOUND <path> :: <reason>` findings; it exits 1
> naming `RECEIPT_SCOPE_FINDING` for a live non-receipt citation, a receipt shifted by a
> non-self-description delta or a stale receipt, and 2 on could-not-evaluate (a missing
> self-record, an unclosed fence, an empty live population, an unreadable receipt at the tip,
> CLI misuse).

- Scope rulings declared here, before data, and implemented in the counter: (a) the fence rule
  reuses the audit's CommonMark 0.31.2 §4.5 reading (`tools/append-only-audit.py` v5) so the
  lane has one fence definition, not two; (b) the record-path set is the round-72 tool's set
  **plus** `PROVINCE.md`, `SKILL.md`, `corpus/**`, because those paths are the lane's own
  self-description and cannot invalidate a measurement of a runtime or registry surface, while
  a `tools/`, `registry/` or `.ufo/` delta still shifts the receipt (arm `shift-tools`); (c) the
  fenced class is excluded from the population, never from the *check*: a fenced non-receipt is
  counted in `fenced_quoted` and shown, and a live non-receipt is still exit 1.
- Counting command: `python3 tools/round76-receipt-scope.py --repo . --round 75`
- Before → after: exit 2 `…UNREADABLE…(.py)…` → exit 0
  `RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
  nonreceipt=0 unclassified=0`.
- Kill rule: a counter that reaches `unclassified=0` by emptying the population is caught by
  the frozen arm `fence-none-live` (a record whose only receipt citation is fenced exits 2) and
  by `fence-unclosed` (exit 2); a counter that admits a live non-receipt is caught by
  `fence-live-nonreceipt` (exit 1); a counter that accepts any delta is caught by
  `shift-tools` (a `tools/`-touching delta still shifts). All four arms live on the module's
  own selftest and are re-run by the claim's receipt.
- Control that skips the claimed work: the fence-blind frozen base tool plus a
  strip-everything stripping rule. Measured at base: the base exits 2 on the round-75 record
  (`c1-receipt-claim.out`), and a strip-all reading produces an empty population, which the
  declared exit map grades 2, never 0 (`c1-fence-dryrun.out` shows the fence-stripped
  population is 11 citations, not 0). A do-nothing round therefore cannot print the after line.

## C2 — calibration: every declared round-75 self-record fact re-derives or is superseded by a correction whose own value re-derives

Motivating evidence, measured at the base revision before freeze: four self-record facts are
stale and one is unbacked. `.ufo/waves/round-76/measured/before/c2-facts.out` shows
`SCORECARD.md` §Round 75's population sentence filing `PROVINCE.md` sha256 `0e8dc562…`
"(unchanged)" at `rev=c9ab73d8` where the committed blob is `af459acf…`; `LOG.md` §Round 75
filing work tip `b8ed2568…` where the last non-record commit is `c9ab73d8…` and "four mistake
classes" where the lesson carries five; `.ufo/waves/round-76/measured/before/c2-closure.out`
shows `NEWEST_CLOSURE … round=75 row_names=corpus/lessons/round-74-verifier-spotcheck.md
row_current=false`, exit 1; and no committed round-75 file carries the `PRE_REPORT_SELFTEST
pass=18 fail=0` tally the LOG asserts (grep receipt `c2-tally.out`, zero matches).

**Predicate (frozen, verbatim):**

> `python3 tools/round76-selfrecord-facts.py --repo <lane>` prints one `SELFRECORD_FACTS
> claims=8 mismatches=0 corrected=5 unbacked=0` line and exits 0 only when each of the eight
> declared round-75 self-record facts — the `SKILL.md` sha256 and line count, the `PROVINCE.md`
> sha256 and line count, the `corpus/SOURCES.md` registry row count, the filtered
> `corpus/knowledge/*.md` entry count, the LOG work tip, the LOG mistake-class count, the LOG
> gate-selftest tally's backing receipt and the `## Axes` calibration row's newest-closure
> pointer — either re-derives from the blob at the revision it names or is superseded by an
> appended dated correction block that names the superseded bytes and states a corrected value
> which itself re-derives; it exits 1 naming each `SELFRECORD_FACT <id> filed=<v> derived=<v>`
> mismatch and each `SELFRECORD_CORRECTION <id> unbacked|wrong-value` finding, and 2 on
> could-not-evaluate (a missing self-record, an unreadable blob, CLI misuse).

- Fact population is declared, not discovered: the eight ids are `skill-digest`,
  `skill-lines`, `province-digest`, `province-lines`, `sources-rows`, `knowledge-entries`,
  `log-worktip`, `log-mistakes`, `log-tally`, `closure-pointer` — ten checks over eight facts
  (the two digest/line pairs are one fact each; the counter reports `claims=8` = the eight
  named facts, with the digest/line pair graded as one claim carrying two values).
- A correction is accepted only when it (a) sits after the superseded text in the same file,
  (b) names the superseded bytes or their locator, and (c) states the corrected value that the
  counter re-derives from the blob at the named revision. A correction naming a wrong value is
  `wrong-value`, never `corrected`.
- Counting command: `python3 tools/round76-selfrecord-facts.py --repo .`
- Before → after: `SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0` exit 1 (five
  = province-digest, log-worktip, log-mistakes, log-tally, closure-pointer; the tally counts
  both mismatch and unbacked) → `claims=8 mismatches=0 corrected=5 unbacked=0` exit 0.
- Kill rule: a counter that prints zeros without reading is caught by the module's own cheat
  arm; a counter that accepts any correction text is caught by `correction-wrong-value` (a
  correction stating `af459acf…` as `0e8dc562…` stays a mismatch); a do-nothing round cannot
  reach the after line because the five base mismatches are re-derived by the committed before
  receipts independently of the counter.
- Control that skips the claimed work: the five base mismatches themselves, re-derived by plain
  `git show | sha256sum`, `grep -c` and `grep -o` commands committed in the before receipts.
  Relabelling the same stale sentences without appending a value-bound correction leaves
  `mismatches=5`.

## C3 — freshness: every append-only audit event is accounted for exactly once, and the accepted-history cutoff cannot be re-opened by re-introducing a register

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-76/measured/before/c3-audit.out`): the audit reports `events=232 restored=91
unrestored=53 ungraded=83 disclosed=5` — 83 events (341 lines) are the SCORECARD exempt-head
re-derivations the contract declares ungraded, and no committed instrument says so; the
accepted-history register grades only the 53 unrestored events
(`APPEND_ACCEPTED events=53 accepted=53 …`, exit 0) and its cutoff is the single `A` commit it
happens to see, so a delete-and-re-add of the register would re-open it (round-75 SN01's
temporal-cutoff finding, one level up).

**Predicate (frozen, verbatim):**

> `python3 tools/round76-append-exempt.py --repo <lane>` prints one `APPEND_EXEMPT events=232
> register=53 exempt=83 restored=91 disclosed=5 unaccounted=0 cutoff=<40-hex> introductions=1
> rotation_safe=1` line and exits 0 only when every event the append-only audit reports is
> accounted for exactly once — by a line-bound row of `registry/append-only-accepted.tsv`, by a
> class-bound row of `registry/append-only-exempt.tsv` whose `class` is the audit's own
> mechanical exemption class and whose count equals the event's ungraded deleted lines, by
> restoration at the audit revision, or by a disclosure row — and the cutoff is the earliest
> commit adding any accepted-history register, so a later re-introduction of a register cannot
> re-open it; it exits 1 naming each `APPEND_EXEMPT_FINDING
> <unaccounted|wrong-class|wrong-count|duplicate|post-introduction|rotation> …`, and 2 on
> could-not-evaluate (audit run failure, missing register, CLI misuse).

- The exempt class is mechanical, not asserted: a row is accepted only for an event whose audit
  JSON lists `ungraded` lines, whose deleted lines' parent sections are all exempt titles of
  that file's contract row, and whose `graded == 0`; the row's count must equal the event's
  `ungraded` count and its section list must equal the sections the audit names.
- Rotation: `introductions` counts the commits that add either register; the cutoff is the
  **earliest** such commit; every row's commit must be an ancestor of it. A fixture that
  re-adds a register after the cutoff with a row younger than the cutoff must be `rotation`,
  exit 1 (arm `rotation-reintroduced`).
- Counting command: `python3 tools/round76-append-exempt.py --repo .`
- Before → after: audit `events=232 … ungraded=83 …` with the register grading 53 (before
  receipts `c3-audit.out`, `c3-register.out`) → `APPEND_EXEMPT events=232 register=53 exempt=83
  restored=91 disclosed=5 unaccounted=0 … rotation_safe=1` exit 0.
- Kill rule: a counter that accepts every event without a row is caught by the arm
  `missing-row` (one event stripped of both rows exits 1); one that accepts a wrong count by
  `wrong-count`; one that ignores re-introduction by `rotation-reintroduced`; one that reports
  numbers without running the audit by the selftest's audit-fixture arms.
- Control that skips the claimed work: a do-nothing round leaves `unaccounted=83` (measured at
  base). Appending 83 rows that copy the audit's own counts without the class/count checks is
  caught by `wrong-count` and `wrong-class`; the three arms are on the module's selftest.

## Frontier and duties (no claim slot)

- `corpus/SOURCES.md`: one row opened live this round, tier A, `mined`, cited by the C1
  knowledge entry `corpus/knowledge/fenced-quotation-scope.md`; the Gate block in
  `corpus/lessons/round-76.md` carries the URL, access date and ≤25-word located quote.
- Census before → after recorded with exit codes; the round-end census must exit 0.
- One mined mistake in `corpus/lessons/round-76.md` `## Mistakes`, each fix shown able to fail.
- Assimilation: `merge/kama/` id-collision guard and quarantine slice re-derived read-only from
  `/home/vgpnk/Projects/shokuknow` (never written); the round reports either one adopted theme
  or `Assimilation: none` with the guard's numbers.
- `considerthese/`: one still-unimplemented proposal mined, or the sweep that found none.
- Round-75 closure duties: coverage-map row for `knowledge/append-only-accepted-history.md`,
  QUALITY criteria for the round-75 mistake classes with `captured-by: none`, the round-local
  Gate reject, and the faithful re-capture of the C2 survivor run (defect 2).
- L0: no round-76 question is filed unless a decision is genuinely operator-owned; open
  questions are routed around, never assumed.

## Freeze discipline

`plans/round-76-claims.md` is the frozen plan (this file). The freeze commit is the commit that
adds it; the counter modules cite the base revision in their receipts. Any later change to a
predicate, a counter's exit map or a kill rule is a new claim for a later round, never an edit
here. Divergences between this plan and the landed bytes are recorded in the lesson's
§Freeze divergences with the reason, and the claim's predicate, counter and target are
unchanged.
