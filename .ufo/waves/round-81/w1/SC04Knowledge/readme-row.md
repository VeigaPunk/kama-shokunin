## Coverage map — round 81 addition

| Entry | Covers | Round |
|---|---|---|
| `corpus/knowledge/late-acceptance-rule.md` | Round-81 late-acceptance rule over the frozen append-only audit population: events are keyed `(commit, file)` with `undisclosed` lines keyed `line_sha256`/`count`/`class`, and the two audit ledgers (`append-only-accepted.tsv`, `append-only-disclosures.tsv`) are bounded by their own introduction commits — so the round-75 register's pre-introduction cutoff makes every later event permanently unacceptable (round 51: a round must not bless its own damage); a row in `registry/append-only-late.tsv` accepts one only from a later round (`round-<N> accepts round-<M>`, `N > M`), with the register's introducing commit a strict descendant of the event commit and an exact hash/count/class binding; `pending` is the graded round's own visible debt, repaid by the next round, and no row ever restores bytes or moves the audit's `unrestored` count | 81 |
