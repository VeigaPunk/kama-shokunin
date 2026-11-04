# SC02 — round-80 QUALITY criterion (KQ132)

Filing: append this section to `corpus/QUALITY.md` after the round-79 mistake-3 section
(`KQ131`). Section heading, preamble, header row and the one data row are reproduced in the
existing shape; the header row is not re-filed as content.

## Criterion added — round 80 (2026-11-04; no outside review yet)

KQ131 stays in force. This row carries the round-80 mined mistake — round 79 filed its C2
claim as `verified` in the SCORECARD banner, the claim table and the LOG while its own cited
receipt printed `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` — into one admission
check: a self-record fact is stated only in the form the receipt prints it, and a claim whose
own cited receipt disagrees is unverified regardless of intent.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ132 | A self-record fact is stated only in the form its receipt prints it: the recorded value is the receipt's own printed token, and a claim whose own cited receipt disagrees is written as the receipt has it, never softened by the record's intent. Check: at the round-80 tip `python3 tools/round80-selfrecord-round79.py --repo .` prints `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0` and exits 0, every stale fact it names is answered by exactly one committed `corrected F<n> old=<value> new=<value> at=<40-hex> date=<ISO>` block whose `new` re-derives at the tip, and the same counter with `--enumerate` prints the stale facts by name before the corrections land (`claims=6 stale=3 corrected=0`, exit 1). | A verdict, banner, claim-table cell or LOG line is written from intent rather than from the cited receipt; a fact's value string is paraphrased instead of copied from the printed token; a red receipt is compensated by prose elsewhere in the record; a correction's `new` value is prose rather than a re-derivable token; or a `verified` word stands in a record whose own cited receipt prints `failed=1`. Limit: the graded population is the facts the record itself declares, so an undeclared fact is unverified ground, never credited as verified work. | `corpus/lessons/round-80.md` §Gate and §Corrections (routed defects R79V1, the SCORECARD verdict overstatement at F4, and R79V1b/R79V2, the F5 before-tally and F6 LOG line); `plans/round-80-claims.md` §C1 F4–F6; the round-79 C2 row, banner and LOG entry asserting `verified` over `.ufo/waves/round-79/measured/after/c2-gate.out`, which prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0`. |

## Grounding run observed by this seat

Read-only, at the lane tip `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` with
`corpus/lessons/round-80.md` absent (corrections not yet landed), from
`/fast/scratch/hyaku/kama-r80/SC02Sources`:

- `python3 .../tools/round80-selfrecord-round79.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin`
  printed `SELFRECORD_R79 claims=6 mismatches=3 corrected=0 unbacked=0` and exited 1, with
  `FACT F4 … status=stale`, `FACT F5 … status=stale`, `FACT F6 … status=stale`.
- The same command with `--enumerate` printed `SELFRECORD_R79_ENUM claims=6 stale=3 corrected=0`
  and exited 1.
- The same command with `--no-corrections` printed the same `mismatches=3` line and exited 1.

The criterion's Check line is therefore written against the counter's documented target, not
against a green run: this seat did **not** observe `corrected=3`. Receipt:
`c1-counter.out` beside this file.
