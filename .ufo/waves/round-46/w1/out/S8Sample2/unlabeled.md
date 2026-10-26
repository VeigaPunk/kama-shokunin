# S8Sample2 — lines not labelled, and the labelling boundaries

This file is the companion note to `sample.tsv` (148 rows). It records every
place where the hand read had to stop or make a boundary decision, so a future
claim-outcome reader is calibrated on what the sample deliberately does not
contain.

## Labels used

- `claim`: `C1`/`C2`/`C3` (declared numbered claims), `X1` (the round-27
  exploratory claim, declared in `.ufo/waves/round-27/a3/plan.json`), `(entry)`
  (a round-level admission field in `MANIFEST.json` that is not keyed to any
  claim), `(multi)` (one physical line covering two or more claims).
- `outcome`: `met` | `partial` | `unprovable-but-better` | `unprovable` |
  `not-met` | `mixed`.
- `phrasing`: `outcome-word` | `measurement-only` | `multi-claim-line` |
  `qualified-met-not-admitted` | `table-row` | `manifest-field` | `other`.

## Inclusion rule applied by hand

A physical line entered the sample when it names a claim id (or sits in a block
that names one: a `### C1` heading, a per-claim table, a `Claim verdicts`
paragraph) **and** carries an outcome: a verdict word (`met`, `not met`, `miss`,
`unprovable`, `not established`, `does not verify`, `verified`, `NOT ACHIEVED`,
`not admitted`, `partial`, `held`), or a predicate value (`met True`,
`met False`, `valid_corrections N`, `unresolved N`, `complete=n/4`,
`false_at_writing=n`). Claim **declarations** and **targets** without a verdict
word were not included.

## Lines deliberately not labelled

1. **Manifest numeric score/component fields.**
   `fleet:MANIFEST.json:11359-11366` (round 22 `claims.C1.scalar_before`,
   `scalar_after`, and `components.*.{before,after,of}`). Numeric, no outcome
   word; they do not fit the six-value vocabulary.
2. **Manifest axis maps.** `fleet:MANIFEST.json:11347-11353` (round 22) and
   `12037-12043` (round 23) map *axes*, not claims. They are ambiguous between
   "claim outcome" and "axis trend"; I labelled one such line
   (`12038`, round 23 `calibration: improved`) by mapping the claim's declared
   axis, and flag the mapping as a reader decision.
3. **Round 23 has no claim block at all.** Its closure entry
   (`fleet:MANIFEST.json:12025-12065`) has no `claims` key; the only claim-level
   statement is prose inside `notes` (`12065`) and
   `verification.rechecks` (`12061`). Round 22's entry has `claims.C1`.
   A reader cannot read round 23's claim outcome from a claim-keyed field.
4. **Round 22's fleet report has no per-claim verdict section.**
   `fleet:.ufo/reports/round-22/kama.md` states the C1 outcome only inside the
   declaration line 5 ("verified narrow improvement") and the two component rows
   69-70. Whether that is one claim-outcome line or three is a reader decision;
   I included all three.
5. **Continuation lines with a predicate value but no claim id.**
   Examples: `fleet:.ufo/reports/round-26/kama.md:83` (`met True` for the
   shortcut control), `fleet:.ufo/reports/round-28/kama.md:128` (the `met True`
   fragment of the after-receipt whose bullet starts at `:127`),
   `spot:round-26-verifier-spotcheck.md:24` (the `met True` fragment of `:23`),
   `fleet:round-31/kama.md:88-89`, `fleet:round-32/kama.md:90-92`,
   `spot:round-31-verifier-spotcheck.md:30`. I included the ones I could
   attribute to a claim within two lines (`r26:123` is the whole table row;
   `r28:126` carries its own predicate value; `spot-r31:24` names the claim in
   its own line) and excluded the rest. A reader that attributes by block works better here
   than one that keys on the line alone.
6. **One claim, two verdict words on one line.**
   `fleet:.ufo/reports/round-24/kama.md:5` says both "NOT ACHIEVED" and
   "unprovable in full". A single `outcome` field cannot carry both; I recorded
   `unprovable` and keep this line as the canonical hard case.
7. **Axis rows for axes the round declared no claim on.**
   `spot:round-24-verifier-spotcheck.md:140` (`| operability | unprovable |`)
   and `spot:round-30-verifier-spotcheck.md:47-50` ("no depth claim", "no
   coverage claim"). These are axis verdicts / non-claim declarations, not
   outcomes of a declared claim.
8. **Statements that a claim was *not* declared.**
   `fleet:round-26/kama.md:26-27` ("Repair-first items ... are repair work, not
   claims"), `fleet:round-32/kama.md:43` (`Reconciliations ... not claims`).
9. **Trend-verdict bullets keyed only by axis names.** For example
   `fleet:round-22/kama.md:204-212`, `fleet:round-26/kama.md:190-192`,
   `fleet:round-29/kama.md:136-138`, `fleet:round-30/kama.md:106-116`,
   `fleet:round-31/kama.md:113-125`, `fleet:round-32/kama.md:150-159`,
   `fleet:round-33/kama.md:220-222`, and the closure equivalents. Excluded
   unless the bullet also names a claim or says "claim"; e.g.
   `fleet:round-26/kama.md:194` is included because it says "the claim's
   counter".
10. **Single sentences split across physical lines.**
    `fleet:round-23/kama.md:74-76` is one sentence whose three lines carry
    different polarity (verified → not admitted → harm traded). I labelled each
    line (`met`, `met`, `partial`); a reader must join them to get the claim.
11. **Long mixed lines.** `spot:round-31-verifier-spotcheck.md:25` contains
    both `met True` (for a no-op control) and "Claim falsified"; labelled
    `mixed`. `:31` and `:36` mix a receipt with the lane's own "NOT admitted"
    wording; labelled `not-met` and `unprovable` respectively.
12. **Claim declarations with a score.** `fleet:round-33/kama.md:9-10`,
    `fleet:round-32/kama.md:14-20`, `fleet:round-24/kama.md:63` (included only
    because its heading also says "original claim not achieved/unprovable in
    full"). A score (`7 → 7`) is not an outcome.
13. **Control/shortcut lines that meet the predicate.** `fleet:round-26/kama.md:124`
    and `fleet:round-28/kama.md:57` report a control meeting the target. Their
    line-level predicate value is `met True`, but the claim-level reading is
    `unprovable` (a shortcut meets the counter). I labelled them `unprovable`
    and record this as the single largest classification trap in the sample.
14. **Before-state lines.** `fleet:round-28/kama.md:126`,
    `fleet:round-29/kama.md:98`, `fleet:round-30/kama.md:17-18`,
    `fleet:round-32/kama.md:74`, `fleet:round-33/kama.md:83,89`,
    `spot:round-29-verifier-spotcheck.md:28`,
    `spot:round-30-verifier-spotcheck.md:30` print `met False` / `met=False` at
    the base revision. I labelled them `not-met` (revision-relative, not a
    failed claim). A reader that treats every `not-met` as a claim failure will
    over-count failures by 8 rows on this sample alone.

## Coverage of the source population

Rounds 22-33, two sources each (24 source files, 4,181 physical lines, plus
the two `MANIFEST.json` closure entries):
fleet reports at fleet `HEAD` = `9b676be886e1e2a428fa81321a05a16363ca68ac`
and closures at lane
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`; rounds 22-23 have no
`corpus/lessons/round-N-verifier-spotcheck.md` for `N` in {22,23} (verified:
`git show 4a2a4d55...:corpus/lessons/round-22-verifier-spotcheck.md` exits
non-zero), so their closure entry is `fleet:MANIFEST.json` as the item
specifies.

Not in scope, not read for this sample: `corpus/lessons/round-N.md` (the lane's
own lessons), each round's `SCORECARD.md` row, and the fleet `MANIFEST.json`
`verification`/`notes` prose for rounds 24-33. Those carry additional claim
statements; the sample covers only the two sources the item names.
