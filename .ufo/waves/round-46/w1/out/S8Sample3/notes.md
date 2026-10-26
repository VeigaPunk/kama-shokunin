# KQ65 hand-read sample — notes (seat S8Sample3, round 46)

No reader was written or run. `sample.tsv` is a hand-labeled line sample; the only code
executed over the sources copies chosen lines verbatim and re-checked them against
`git show <rev>:<path>` (138/138 byte-equal, 0 mismatches). No claim counter was run.

## Sources (read at the revisions the item names)

- self side: `.ufo/reports/round-<N>/kama.md`, N = 34..45, rev
  `9b676be886e1e2a428fa81321a05a16363ca68ac` (fleet HEAD; the item's `git show HEAD:` command).
- outside side: `corpus/lessons/round-<N>-verifier-spotcheck.md`, N = 34..45, rev
  `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` (lane commit the item names).
- All 12 rounds have a closure spot-check file at that rev, so the rounds 20-23
  `MANIFEST.json` branch of the item was not used (it lies outside 34-45 anyway).
- Exact bytes read are copied under `sources/` with `sources.sha256` (24 files, 450 092 bytes).

## Inclusion rule (applied by hand, one line at a time)

A line is a sample row when it asserts the satisfaction status of a declared claim
(C1..C3) of that round. Concretely:

1. claim-scoped counters: any line giving a counter tally with a `met`/`met=`/`met=True|False`
   token for a claim, at base or at tip;
2. claim verdicts: "Verdict: verified (re-measured)", "Ruling: unprovable", "C1 verifies",
   "Score held at N", "→ met", "NOT met", "I rule the claim verified";
3. claim table rows: the `Before → after` / `Claims` / per-axis tables where the row names the
   claim (or is the axis row for a claim's axis) and states met/score/verdict;
4. multi-claim lines: one line covering two or three claims ("All three claims measure …",
   "Both claims verify", "Separability" rows, admission paragraphs);
5. SHONEN box lines that state a claim outcome by id (round 38 only).

Excluded, and listed with line numbers in `boundary.tsv` (32 entries): control receipts
(do-nothing / junk controls are not the claim), counter selftests, counter-limit sentences,
axis trend verdicts unless the same line states a claim id **and** its status, regression lines
for earlier rounds' instruments, non-claim census/pointer statements, and out-of-population
readings.

## Outcome mapping (the frozen enum has no `unverified`)

- `verified` / `verified by re-measurement` / `verifies` / `→ met` / `met True` → `met`
- `met=False` / `met False` / `NOT met` → `not-met`
- round 40's word `unverified` and closure round 45's `Ruling: the frozen code is the predicate
  … met=False` on a claim whose substance is real → `unprovable`
- one line stating a C1 receipt defect and a C1 substance match → `partial` (c39:33)
- one line stating both a met and an unmet claim → `mixed` (f40:296, c40:105, c45:7)
- 2 row-wide tallies (`registered 12 unregistered 0 defective 0`) are labeled by the predicate's
  own reading, not by a `met` word: base tally → `not-met`, tip tally → `met`.

## Shape of the sample

138 rows: 59 self, 79 outside. Claims: C1 56, C2 55, C3 14, "C1;C2" 9, "C1;C2;C3" 4.
Outcomes: met 103, not-met 25, unprovable 6, mixed 3, partial 1.
Classes: measurement-only 62, table-row 36, outcome-word 23, multi-claim-line 13, other 4.
`qualified-met-not-admitted` and `manifest-field` have **zero** members in 34-45.

Three traps the future reader must survive, quantified here:

- **85 of 138 rows carry no literal `C1`/`C2`/`C3` token.** They are identified only by the
  subsection they sit in (round 36-45 measurement bullets) or by the wrapped fragment.
- **8 rows are physical fragments of a wrapped counter output** (round 36: `met` on one line,
  `False`/`True` on the next; the outcome statement spans two lines).
- **13 multi-claim lines** carry two or three claims and, in 3 cases, disagreeing outcomes.

## Lines I could not label

None left unlabeled. Every candidate line I rejected is recorded in `boundary.tsv` with a reason;
three are genuinely arguable and are flagged there by category rather than silently dropped:

- f37:46 — quality trend that mentions "the C1 counter" and its append-only corrections, but
  asserts an axis move; included or excluded changes the population by one.
- f40:293 — same shape (quality trend), but it states "C1's measurement failure is disclosed,
  not counted as a pass", so it is included as `unprovable`/`other`.
- c39:33 — labels `partial`: it is a C1 evidence-fidelity row (attempt-1 receipt not
  reproducible), while C1's substance is met in the row above it.
