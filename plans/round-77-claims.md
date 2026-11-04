# kama round 77 — frozen claims

Frozen before any seat scored. Base revision `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`
(lane `master`, == `origin/master` at freeze). A rule changed after a seat has scored is not
this claim's rule (kumitate r42): a seat that disagrees reports a disagreement and never edits
this file. The predicate sentence, the counter code and the receipt label are the same sentence
in all three places.

Carry-in: the round-76 non-author closure (`corpus/lessons/round-76-verifier-spotcheck.md`)
routed six defects (§4 D1–D6). D1 (missing coverage-map row), D2 (stale `filtered knowledge
entries 46`), D3 (post-cutoff prose undercount) and D4 (`## Gate` quote discipline) are duties
closed in the lesson/README/QUALITY/SOURCES edits, no claim slot. D5 (a capability row without
a passing demonstration) is closed by the `append-registers` capability entering only with its
green demonstration this round. D6 (a committed draft naming a non-existent receipt path) is
applied to `LOG.md` with the pointer repaired, or discarded: decided in the lesson. The
round-76 plan (`plans/round-76-claims.md` §Frontier) retargets its C1 and C3 misses into this
round's C1 and C2; its C2 extension is this round's C3.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration **7** is the lane's
lowest non-retired assigned score (operability 8), so C3 satisfies the lowest-axis duty. C1
operability and C2 freshness are the two other axes the lane owns; two claims on one axis would
count as one claim, so the three claims name three distinct axes.

The three claims are causally separable: C1 reads the round-75 self-record and the frozen
receipt-scope modules; C2 reads the append-only audit JSON plus the two registers and the
contract; C3 reads the round-76 SCORECARD/LOG self-record sentences. Each exits 0 with the
other two counters absent from the tree.

## C1 — operability: a baseline receipt is bound by header ancestry and reproducibility, and the round-75 population classifies 9 bound

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-77/measured/before/c1-scope.out`): the round-76 counter prints
`RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=6 unbound=2 shifted=3
nonreceipt=0 unclassified=0`, exit 1. The three shifted citations are the round-75
`measured/before/*.out` receipts: each names `rev=dc58e513…` (an ancestor of the commit
`10f37171…` that introduced the file) and its bytes are identical at the introducing commit and
at the tip. They are baseline measurements of the pre-round state, so a delta that postdates
them cannot invalidate them; the delta rule is right for an at-the-tip receipt and wrong for a
baseline.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round77-citation-baseline.py --repo <lane> --round 75` prints one
> `CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
> nonreceipt=0 unclassified=0` line and exits 0 only when the round-75 self-record's citation
> population is classified under the frozen fence scope (a citation inside a CommonMark fenced
> block is quoted history; an unclosed fence is could-not-evaluate) and the frozen record-path
> scope (a delta between a receipt's recorded revision and the tip that touches only
> `PROVINCE.md`, `SKILL.md` or `corpus/**` does not shift that receipt), and under the declared
> baseline-receipt class — a citation whose path lies under a `measured/before/` directory is
> bound when its first five lines name one 40-hex revision that is an ancestor of the commit
> that introduced the receipt file and the file's bytes are identical at that introducing
> commit and at the tip — with the two legacy header-less wave receipts named individually as
> `CITATION_BASELINE_UNBOUND <path> :: <reason>`; it exits 1 naming
> `CITATION_BASELINE_FINDING <shifted|stale|nonreceipt>` for a live non-receipt citation, a
> receipt shifted by a non-self-description delta, a baseline receipt whose recorded revision is
> not an ancestor of its introduction, a baseline receipt whose bytes changed after
> introduction, or a stale receipt, and 2 on could-not-evaluate (a missing self-record, an
> unclosed fence, an empty live population, an unreadable receipt at the tip, CLI misuse).

- Scope rulings declared here, before data: (a) the fence rule and the record-path set are the
  frozen round-76 rules, imported from `tools/round76-receipt-scope.py` rather than copied;
  (b) the baseline class is narrower than "any old revision": the path must sit under
  `measured/before/`, the header revision must be an ancestor of the file's `--diff-filter=A`
  introduction commit, and the file's sha256 must be equal at that introduction and at the tip;
  (c) a baseline receipt that fails either leg stays `shifted` with the failing leg named.
- Counting command: `python3 tools/round77-citation-baseline.py --repo . --round 75`
- Before → after: exit 1 `RECEIPT_SCOPE … bound=6 unbound=2 shifted=3 …` → exit 0
  `CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
  nonreceipt=0 unclassified=0`.
- Kill rule: a counter that reaches `bound=9` by widening the at-the-tip delta rule is caught by
  the frozen arm `shift-tools` (a `tools/`-touching delta still shifts an at-the-tip receipt);
  a counter that binds any old revision is caught by `baseline-nonancestor`; a counter that
  ignores later edits to a baseline receipt is caught by `baseline-edited`; the inherited arms
  `fence-none-live`, `fence-unclosed` and `fence-live-nonreceipt` stay red-capable.
- Control that skips the claimed work: the round-76 counter at the same base prints `bound=6
  shifted=3`, exit 1 (`measured/before/c1-scope.out`); a do-nothing round cannot reach the
  after line because the three baseline receipts' introduction and byte-stability facts are
  re-derived by plain `git log --diff-filter=A` and `git show | sha256sum` commands committed in
  the before receipt.

## C2 — freshness: two accepted-history registers with independent cutoffs, and every base audit event accounted once

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-77/measured/before/c2-append.out`): the round-76 counter prints
`APPEND_EXEMPT events=241 register=53 exempt=47 restored=95 disclosed=5 unaccounted=41
cutoff=10f37171… introductions=2 rotation_safe=1`, exit 1, with 41 `missing valid exempt row`
findings. Its single cutoff (the earliest register introduction) cannot admit any event that
postdates it, so the exempt register can never grow; and the audit's `permitted` carriage and
`only=` region classes are not named at all.

**Predicate (frozen, verbatim):**

> `python3 tools/round77-append-registers.py --repo <lane> --to <40-hex>` prints one
> `APPEND_REGISTERS to=<40-hex> events=<n> accepted=<n> exempt=<n> permitted=<n>
> out_of_region=<n> restored=<n> disclosed=<n> unaccounted=0 accepted_cutoff=<40-hex>
> exempt_cutoff=<40-hex> introductions=<a>/<e> rotation_safe=1` line and exits 0 only when every
> event the append-only audit reports at that revision is accounted for exactly once — by a
> line-bound row of `registry/append-only-accepted.tsv` under that register's own introduction
> cutoff, by a class-bound `exempt-head` row of `registry/append-only-exempt.tsv` under that
> register's own introduction cutoff whose count equals the event's ungraded deleted lines and
> whose section list equals the parents those lines sit in, by the audit's own `permitted`
> carriage class when every deleted line of the event is permitted and none is graded or
> ungraded, by the declared `out_of_region` class when the event's file declares an `only=`
> contract region and every deleted line lies outside every declared region, by restoration
> held at the audit revision, or by a disclosure row — and no register path is re-introduced
> after its first introduction with rows its previous version did not carry; it exits 1 naming
> each `APPEND_REGISTERS_FINDING <unaccounted|wrong-class|wrong-count|duplicate|rotation> …`,
> and 2 on could-not-evaluate (audit failure, missing register, CLI misuse).

- Scope rulings declared here, before data: (a) the cutoff of each register is the earliest
  commit that adds that path (`--diff-filter=A`, topological order), and a row is admissible
  when the event commit it names is an ancestor of the audit revision — the register's growth
  is append-only history, not rotation; (b) rotation means a second introduction of the same
  path whose row set is not a subset of the row set at the version that preceded it — the arm
  `rotation-reintroduced` re-adds a register with one new row and must exit 1; (c)
  `out_of_region` is read from the contract's own `only=` region through
  `append-only-audit.py`'s `file_regions`; an event with any deleted line inside a declared
  region is never out-of-region; (d) `permitted` requires `permitted == deleted` and
  `graded == 0 and ungraded == 0`; an event with one line in any other class falls through to
  the register rules and is `unaccounted` if no row covers it.
- Counting command: `python3 tools/round77-append-registers.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`
- Before → after: exit 1 `APPEND_EXEMPT events=241 … unaccounted=41 …` → exit 0
  `APPEND_REGISTERS to=cc6e1d3c… events=241 accepted=53 exempt=56 permitted=28 out_of_region=4
  restored=95 disclosed=5 unaccounted=0 accepted_cutoff=10f37171… exempt_cutoff=c2aa7fb2…
  introductions=1/1 rotation_safe=1`.
- Kill rule: a counter that reaches `unaccounted=0` by accepting every ungraded event is caught
  by `missing-row` (one event stripped of both rows exits 1) and `wrong-count`; one that
  launders a head edit through `out_of_region` is caught by `inside-region` (a deletion inside
  the declared `## Errata` region stays a finding); one that ignores re-introduction is caught
  by `rotation-reintroduced`; one that reports numbers without running the audit is caught by
  the audit-fixture arms.
- Control that skips the claimed work: a do-nothing round leaves `unaccounted=41` (measured at
  base). Appending 41 rows that copy the audit's own counts without the class/count checks is
  caught by `wrong-class` and `wrong-count`; appending the 9 strict rows while leaving the 28
  `permitted` and 4 `out_of_region` events unnamed leaves `unaccounted=32`.

## C3 — calibration: the round-76 record's own facts re-derive or are superseded by a correction whose value re-derives

Motivating evidence, measured at the base revision before freeze
(`.ufo/waves/round-77/measured/before/c3-facts.out`): no counter grades the round-76 record;
the nearest harness exits 2 (`SELFRECORD_FACTS CouldNotEvaluate: fatal: path
'corpus/lessons/round-76-verifier-spotcheck.md' exists on disk, but not in
'a3fbc629fa18c26ad1192adc5d8e762671dd1d79'`), because it resolves the closure pointer at a
revision that predates the closure. Two facts of the round-76 record are stale: its population
sentence files `filtered knowledge entries 46` where `corpus/knowledge/` at `c2aa7fb2` holds 47
(the round-76 non-author closure's D2), and the `## Axes` calibration row names the round-75
closure while the newest at the base tip is round 76.

**Predicate (frozen, verbatim):**

> `python3 tools/round77-selfrecord-round76.py --repo <lane>` prints one `SELFRECORD_R76
> claims=6 mismatches=0 corrected=2 unbacked=0` line and exits 0 only when each of the six
> declared round-76 self-record facts — the work tip, the gate-selftest tally's backing receipt,
> the capability count against the round-76 canonical table, the filtered knowledge-entry count
> at the revision the record names, the `corpus/SOURCES.md` registry row count at that revision,
> and the `## Axes` calibration row's newest-closure pointer — either re-derives from the blob at
> the revision it names or is superseded by an appended dated correction block that names the
> superseded bytes and states a corrected value which itself re-derives; it exits 1 naming each
> `SELFRECORD_R76_FACT <id> filed=<v> derived=<v>` mismatch and each `SELFRECORD_R76_CORRECTION
> <id> unbacked|wrong-value`, and 2 on could-not-evaluate (a missing self-record, an unreadable
> blob, CLI misuse).

- Fact population is declared, not discovered: the six ids are `work-tip`, `gate-tally`,
  `capability-count`, `knowledge-entries`, `sources-rows`, `closure-pointer`. The record
  revision is the sealed round-76 tip named in the predicate's implementation
  (`cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`); the population facts derive at `c2aa7fb2…`, the
  revision the record itself names.
- A correction is accepted only when it (a) sits after the superseded text in the same file,
  (b) names the superseded locator or filed value, and (c) states the corrected value that the
  counter re-derives. A correction naming a wrong value is `wrong-value`, never `corrected`.
- Counting command: `python3 tools/round77-selfrecord-round76.py --repo .`
- Before → after: exit 2 (`no such counter`; the nearest harness `CouldNotEvaluate`) →
  `SELFRECORD_R76 claims=6 mismatches=0 corrected=2 unbacked=0`, exit 0.
- Kill rule: a counter that prints zeros without reading is caught by the module's cheat arm; a
  counter that accepts any correction text is caught by `correction-wrong-value`; a do-nothing
  round cannot reach the after line because the two base mismatches are re-derived by plain
  `git ls-tree`/`grep` commands committed in the before receipt.
- Control that skips the claimed work: relabelling the two stale sentences without appending a
  value-bound correction leaves `mismatches=2`.

## Frontier and duties (no claim slot)

- `corpus/SOURCES.md`: one row opened live this round, cited by the C1 knowledge entry; the Gate
  block in `corpus/lessons/round-77.md` carries the URL, access date and ≤25-word located quote.
- Census before → after recorded with exit codes; the round-end census must exit 0.
- One mined mistake in `corpus/lessons/round-77.md` `## Mistakes`, the fix shown able to fail.
- Assimilation: `merge/kama/` id-collision guard and quarantine slice re-derived read-only from
  `/home/vgpnk/Projects/shokuknow` (never written); the round reports either one adopted theme
  or `Assimilation: none` with the guard's numbers.
- `considerthese/`: one still-unimplemented proposal mined, or the sweep that found none.
- Round-76 closure duties D1, D2, D3, D4, D6 as listed above; D5 closed by C2's green
  demonstration.
- L0: no round-77 question is filed unless a decision is genuinely operator-owned; open
  questions are routed around, never assumed.

## Freeze discipline

`plans/round-77-claims.md` is the frozen plan (this file). The freeze commit is the commit that
adds it; the counter modules cite the base revision in their receipts. Any later change to a
predicate, a counter's exit map or a kill rule is a new claim for a later round, never an edit
here. Divergences between this plan and the landed bytes are recorded in the lesson's
§Freeze divergences with the reason, and the claim's predicate, counter and target are unchanged.
