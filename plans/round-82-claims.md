# round-82 claims (kama) — frozen plan

Base revision `aaf974dbd3b6adb2ef914dc7293cda92b4e05551` (round-81 non-author closure tip). Sealed
revision C1 grades `1b64f66ddea89c57b71165eacd14b0e1d6f24e11` (the round-81 record tip — the revision
the round-81 report cites). Two claims, two distinct axes, each measured on its own receipt. Frozen
before any seat scored; a control is built and committed per claim before data.

Axis assignment (`../shokunin.conf`, read at the base): **operability + calibration**. Lowest assigned
axis at the base: calibration 7 (operability 8) — C1 works it. Saturation line 8/10 with a
four-round stagnation window: calibration sits below the line, so the nudge is inactive and the
lowest-axis obligation binds.

## C1 — calibration (lowest assigned axis): the round-81 self-record's six declared facts re-derive at the sealed revision or are answered by dated value-bound corrections

Frozen predicate (this block is the counter's `PREDICATE`, the receipt label and the SCORECARD row):

> `python3 tools/round82-selfrecord-round81.py --repo <lane>` prints one `SELFRECORD_R81
> claims=6 mismatches=0 corrected=5 unbacked=0` line and exits 0 only when each of the six facts the
> round-81 self-record declares re-derives from the tree at the sealed revision
> `1b64f66ddea89c57b71165eacd14b0e1d6f24e11` and matches the same fact re-derived at the graded tip,
> or is answered by exactly one committed `corrected F<n> old=<token> new=<token> at=<40-hex>
> date=<ISO> fix=<path>` block in `corpus/lessons/round-82.md` `## Corrections` whose `old` is the
> sealed declared token, whose `at` is the sealed revision, whose `new` equals the fact's tip witness
> token, and whose `fix` path's tip bytes contain the literal `new` token; it exits 1 naming every
> unanswered fact otherwise. A fact that holds at the sealed revision needs no correction; a
> correction for a holding or unnamed fact, a duplicated correction, a correction outside
> `## Corrections`, a wrong `at`, a wrong `old`, or a `fix` whose tip bytes lack the token is
> `unbacked` and is also a mismatch.

The six facts (declared by the round-81 record, observed from the tree):

| id | record location (sealed) | declared token | witness |
|---|---|---|---|
| F1 | `SCORECARD.md` §Round 81 C2 row, the `→ exit 0` cell's `pending=` value | `sc81c2-pending=1` | `.ufo/waves/round-81/measured/after/debt-green.out` → `pending=4` |
| F2 | `LOG.md` §Round 81 `Frontier: registry 297 → <n> rows` | `log81-frontier-rows=301` | the tip registry row count (302) |
| F3 | `SKILL.md` pre-report-gate row `(ten arms, …)` | `skill81-gate-arms=10` | `.ufo/waves/round-81/measured/after/gate.out` → `arms=11` |
| F4 | `SCORECARD.md` `## Axes` calibration row "the newest non-author closure is `<file>`" | `calib81-newest-closure=round-80-verifier-spotcheck.md` | the newest `corpus/lessons/round-*-verifier-spotcheck.md` at the graded tip (round 81) |
| F5 | `LOG.md` `LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=<n>` | `logcorr81-c2-pending=1` | the same `debt-green.out` → `pending=4` |
| F6 | `SCORECARD.md` §Round 81 C1 row's `--selftest` tally, `pass=<n> fail=0` | `sc81c1-selftest=13` | `.ufo/waves/round-81/measured/after/c1-selftest.out` → `pass=13` |

F1–F3, F5 and F6 are graded at the sealed revision against the receipt they cite (or the tip registry
count); F4 is tip-bound (the record states it in the present tense and the round-81 closure lands after
the sealed revision — the round-80 F5 and round-81 F6 precedent). Every fact is read with
`git show <rev>:<path>`, never from the worktree: the round's own record commit cannot refute a fact.
The correction container is `corpus/lessons/round-82.md` section `## Corrections`; blocks outside it
are prose, not corrections.

Five corrections (F1–F5 are stale at the base; F6 holds and must not be corrected):

```
corrected F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F2 old=log81-frontier-rows=301 new=log81-frontier-rows=302 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=skill81-gate-arms=10 new=skill81-gate-arms=11 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F4 old=calib81-newest-closure=round-80-verifier-spotcheck.md new=calib81-newest-closure=round-81-verifier-spotcheck.md at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F5 old=logcorr81-c2-pending=1 new=logcorr81-c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=LOG.md
```

Record fixes the corrections bind (append-only; the filed §Round 81, LOG and SKILL bytes are not
rewritten):

- `SCORECARD.md` gains an appended `#### round-82 correction` block carrying each superseded token
  verbatim (`sc81c2-pending=4`, `log81-frontier-rows=302`, `skill81-gate-arms=11`,
  `calib81-newest-closure=round-81-verifier-spotcheck.md`).
- `LOG.md` gains an appended `LOG-CORRECTION round=81 claim=C2 pending=1 -> pending=4` entry carrying
  `logcorr81-c2-pending=4`.
- `SKILL.md`'s pre-report-gate registry row is updated in place to eleven arms, arm 8's third member
  `tools/round81-append-debt.py` and arm 11 `round81-instruments` (the file is not append-only; the
  superseded value is named in the SCORECARD block and graded as F3).
- The head `## Axes` calibration row is re-anchored to the round-81 closure and the round-82 C1
  counter; that in-place record edit sits in the C2 `pending` class.

Target line: `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, exit 0.

Controls (committed as receipts before data):
1. **enumeration** `--enumerate` at the freeze tip: `SELFRECORD_R81_ENUM claims=6 stale=5 corrected=0`,
   exit 1.
2. **no-corrections** `--no-corrections` at the tip: `SELFRECORD_R81 claims=6 mismatches=5 corrected=0`,
   exit 1 — the target is unreachable without the five correction blocks.
3. **selftest** with, each red: a correction outside `## Corrections`, a wrong-`at` correction, a
   wrong-`old` correction, a `fix` whose tip bytes lack the `new` token, a duplicated correction, a
   correction for the holding F6; and green on the honest set.

## C2 — operability: round 81's five pending events are repaid by committed late rows that a delta check re-derives, and the acceptance population closes

Frozen predicate (two legs, one receipt each; both must print and exit 0):

> `python3 tools/round82-late-delta.py --repo <lane> --round 82` prints one `LATE_DELTA round=82
> base=<12-hex> population=<p> carried=<c> new=<n> bad=0` line and exits 0 only when the committed
> `registry/append-only-late.tsv` at the tip carries, for every undeclared deletion line of every
> event ancestral to the round's base that neither frozen register accepts, exactly one row whose five
> data cells equal the frozen generator's (`tools/round81-late-rows.py generate`) output; a row present
> at the base revision keeps its base-revision bytes unchanged (`carried`), a row first introduced by
> this round carries a note naming round 82 as the accepting round with an accepting round greater
> than the deletion round (`new`), and a missing, extra, duplicated, cell-mismatched or mis-noted row
> is a `bad` finding; it exits 1 naming each.
>
> `python3 tools/round81-append-debt.py --repo <lane> --round 82` prints one `APPEND_DEBT round=82
> base=<12-hex> events=<e> accepted=<a> late=<l> pending=<p> unaccepted=<u> bad_rows=<r>
> bad_declarations=<d> out_of_population=<o>` line and exits 0 only under the round-81 predicate
> (byte-frozen module, its own docstring) with the round-82 base and late register.

Target lines:

- `LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0`, exit 0 — 15 rows
  over the five round-81 events (`cf28c470`, `37484391`, `50c711ec`, `93cdfd60`, `017c34ca`; 9+1+3+1+1
  undeclared lines), each noted `round-82 accepts round-81 …`.
- `APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=<p> unaccepted=0
  bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0; `pending` is the round's own post-base
  events and rises with each later record commit by design (the round-81 convention), so the graded
  buckets are the frozen target.

Before (base `aaf974db`, no round-82 rows): `APPEND_DEBT round=82 … events=68 accepted=53 late=10
pending=0 unaccepted=5 …`, exit 1, and `LATE_DELTA … carried=88 new=0 bad=15`, exit 1 — the five
round-81 record-edit events are the ones the round-81 register could not accept (they were created
after its own base).

Controls (committed before data):
1. **base run** of the debt counter with no round-82 rows: `unaccepted=5`, exit 1.
2. **base run** of the delta check: `new=0 bad=15`, exit 1.
3. **selftest** mutants, each red: a missing row, an extra row, a wrong `count`, a wrong `class`, a
   carried row rewritten, a new row whose note names round 81 (not 82), a new row whose accepting
   round does not exceed its deletion round, a duplicated row.
4. **vacuous-green control**: the gate's round-82 instrument arm run at the freeze tip must be red on
   the debt leg (`unaccepted=5`), so wiring the arm alone cannot buy green.

The frozen round-81 generator and round-81 counter stay byte-intact; the delta check imports the
generator's `generate`/`audit`/`frozen_covered` functions rather than re-implementing them.

## Axis and verdict rules

C1 calibration 7 → 7 (five stale facts of the round-81 record repaired value-bound; the score holds
because the instrument class is already held and one fact is proved to hold). C2 operability 8 → 8 (the
`append-debt` capability gains a delta leg; the score holds). No axis is claimed to move in score; both
moves are measured on their lines. No axis may be harmed: the round makes no change to
depth/coverage/freshness/adjacency claims, and every edit to an append-only file is an append.

## Frontier step (not a claim)

- `corpus/SOURCES.md`: the round opens the pinned documents behind the `pin-watch` `behind` relations
  (llama.cpp `tools/server/README.md` at the newest tag; SGLang and vLLM docs at their newest tags)
  and records each opened URL, access date and a ≤25-word located quote in the lesson's `## Gate`.
  A row is written only for a source opened this round; a refused row keeps its reason and flip.
- Freshness ground for the round's knowledge entry: a `behind` relation is a recheck **trigger**, never
  proof that held knowledge is wrong — grading it means re-opening the pinned document at its own ref.
- One mined mistake into `corpus/lessons/round-82.md` `## Mistakes` (class · evidence · captured-by ·
  fix shown able to fail) and one `corpus/QUALITY.md` criterion.
- `considerthese/2026-10-26.md`: at most one still-unimplemented proposal lands as a lesson/QUALITY row;
  the others stay named as pending in the report.
- Assimilation: `corpus/SOURCES.md` first, then `merge/kama/` only if the claims leave room; either the
  round names one adopted theme or says `Assimilation: none` with its reason.

## Shape

ONE v1 wave, 14 seats (band 8–16): 4 executor, 3 scribe, 2 scout, 1 connector, 2 reviewer, 1 critic,
1 mutation-tester — attack seats 4/14 = 29 % (≥25 %); at most 2 connector seats (1). No residual call.
