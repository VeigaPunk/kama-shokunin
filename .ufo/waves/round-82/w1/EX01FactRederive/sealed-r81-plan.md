# round-81 claims (kama) — frozen plan

Base revision `e7d2fd729cf8204c89c32534303bc9f2a97fcee4` (round-80 non-author closure tip). Sealed
revision C1 grades `a2af1af59faf6cf66fe854559293c4e4b441aff3` (the round-80 record tip — the revision
the round-80 report cites). Two claims, two distinct axes, each measured on its own receipt. Frozen
before any seat scored; a control is built and committed per claim before data.

Axis assignment (`../shokunin.conf`, read at the base): **operability + calibration**. Lowest assigned
axis at the base: calibration 7 (operability 8) — C1 works it.

## C1 — calibration (lowest assigned axis): the round-80 self-record's six declared facts re-derive at the sealed revision or are answered by dated value-bound corrections

Frozen predicate (this block is the counter's `PREDICATE`, the receipt label and the SCORECARD row):

> `python3 tools/round81-selfrecord-round80.py --repo <lane>` prints one `SELFRECORD_R80
> claims=6 mismatches=0 corrected=6 unbacked=0` line and exits 0 only when each of the six facts the
> round-80 self-record declares re-derives from the tree at the sealed revision
> `a2af1af59faf6cf66fe854559293c4e4b441aff3` and matches the same fact re-derived at the tip, or is
> answered by exactly one committed `corrected F<n> old=<value> new=<value> at=<40-hex> date=<ISO>`
> block in `corpus/lessons/round-81.md` `## Corrections` whose `old` is the sealed value, whose `at`
> is the sealed revision, whose `new` equals the fact's tip value, and whose superseded tally is named
> by the appended round-81 correction block in the record file the fact reads; it exits 1 naming every
> unanswered fact otherwise.

The six facts (declared by the round-80 record, observed from the tree at the sealed revision):

| id | record location (sealed) | declared | witness |
|---|---|---|---|
| F1 | `SCORECARD.md` §Round 80 C1 row: `selftest pass=9 fail=0` | `c1-selftest=pass=9` | `.ufo/waves/round-80/measured/after/c1-selftest.out` → `SELFRECORD_R79_SELFTEST pass=11 fail=0` |
| F2 | §Round 80 C3 row: `selftest pass=6 fail=0` | `c3-selftest=pass=6` | `…/measured/after/c3-selftest.out` → `OLLAMA_CENSUS_SELFTEST pass=12 fail=0` |
| F3 | `## Axes` calibration row: `--selftest` → `pass=9 fail=0` | `calibration-row-selftest=pass=9` | `…/measured/after/c1-selftest.out` → `pass=11` |
| F4 | `LOG.md` §Round 80 C1 bullet: `selftest pass=9 fail=0` | `log-c1-selftest=pass=9` | `…/measured/after/c1-selftest.out` → `pass=11` |
| F5 | `## Axes` coverage row last-change cell: `score round 10; evidence re-anchored round 79` | `coverage-last-change=round-79` | the same row's evidence cell names round 80 → `coverage-last-change=round-80` |
| F6 | `## Axes` calibration row: "the newest non-author closure is `corpus/lessons/round-79-verifier-spotcheck.md`" | `newest-closure=round-79-verifier-spotcheck.md` | at the tip the newest closure is `corpus/lessons/round-80-verifier-spotcheck.md` |

Six corrections (all six facts are stale at the base; R80V1, R80V6 and the coverage-cell defect are
their routed-defect disposition):

```
corrected F1 old=c1-selftest=pass=9 new=c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
corrected F2 old=c3-selftest=pass=6 new=c3-selftest=pass=12 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
corrected F3 old=calibration-row-selftest=pass=9 new=calibration-row-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
corrected F4 old=log-c1-selftest=pass=9 new=log-c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
corrected F5 old=coverage-last-change=round-79 new=coverage-last-change=round-80 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
corrected F6 old=newest-closure=round-79-verifier-spotcheck.md new=newest-closure=round-80-verifier-spotcheck.md at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04
```

Record fixes the corrections bind (append-only; the filed §Round 80 and LOG bytes are not rewritten):

- `SCORECARD.md` gains an appended `#### round-81 correction` block naming all five superseded
  tallies/cells (C1-selftest 9→11, C3-selftest 6→12, calibration-row 9→11, coverage last-change
  79→80, newest closure 79→80).
- `LOG.md` gains an appended `LOG-CORRECTION round=80 …` entry naming the superseded selftest tallies.
- The head `## Axes` calibration row is re-anchored to the round-80 closure (arm 2 of the gate) and the
  coverage row's last-change cell is corrected in place; both are round-81 in-place record edits and sit
  in the C2 `pending` class.

Counter rules: every fact is read with `git show <rev>:<path>` (never the worktree); a correction block
outside `## Corrections` is not a correction; a correction whose `new` does not re-derive, whose `at` is
not the sealed revision, whose `old` is not the sealed declared value, or whose fact is not named by the
appended record block is `unbacked`.

Target line: `SELFRECORD_R80 claims=6 mismatches=0 corrected=6 unbacked=0`, exit 0.

Controls (committed as receipts before data):
1. **enumeration** `--enumerate` at the base: `SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0`, exit 1.
2. **no-corrections** `--no-corrections` at the tip: `SELFRECORD_R80 claims=6 mismatches=6 corrected=0`,
   exit 1 — the target is unreachable without the six correction blocks.
3. **selftest** with a stale-value correction and a wrong-`at` correction, each red.

## C2 — operability: the append-only acceptance population is graded under a late-acceptance rule, and every pre-round undeclared deletion event is repaid by a committed late row

Frozen predicate:

> `python3 tools/round81-append-debt.py --repo <lane> --round 81` prints one `APPEND_DEBT round=81
> base=<12-hex> events=<e> accepted=<a> late=<l> pending=<p> unaccepted=<u> bad_rows=<r>
> bad_declarations=<d> out_of_population=<o>` line and exits 0 only when every undeclared deletion
> event the frozen `tools/append-only-audit.py --json` reports at the tip whose commit is ancestral to
> the round's declared base is accepted either by a frozen `registry/append-only-accepted.tsv` row
> (the round-75 rule) or by a committed `registry/append-only-late.tsv` row whose introducing commit is
> a strict descendant of the event commit and whose note names the accepting round `N` and the
> deletion round `M` with `N > M`; a row that names an event outside the base population is counted
> on `out_of_population` and changes no bucket; rows introduced by the graded round cannot accept that
> round's own events (`pending`), and a same-round, short-count, wrong-class or non-descendant row is a
> `bad_rows` finding; it exits 1 naming every unaccepted event otherwise.

Target line: `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=<p>
unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0.

- Before (base `e7d2fd72`): `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=0
  pending=0 unaccepted=10 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 1 — the ten
  unaccepted events are the round-79/80 record edits the frozen register's pre-introduction cutoff
  cannot accept (`.ufo/waves/round-81/measured/before/debt-base.out`).
- The late register `registry/append-only-late.tsv` carries exactly the 88 undeclared lines of those
  ten events, generated deterministically from the audit JSON by `tools/round81-late-rows.py`
  (`--check` re-derives every cell and fails on any mismatch); every row's note is
  `round-81 accepts round-<M> …`.
- Gate composition: arm 8 `round75-instruments` swaps its third member `round75-append-accepted.py`
  (structurally unsatisfiable after its register's introduction cutoff — the round-75 predicate requires
  a row committed before the register's own introduction, so no event created after it can ever be
  accepted) for `round81-append-debt.py`, and a new arm 11 `round81-instruments` runs the new module's
  selftest. The frozen round-75 counter and its red receipts stay byte-intact as history.

Controls (committed before data):
1. **base run** of the new counter with an empty late register: `unaccepted=10`, exit 1.
2. **selftest** mutants, each red: a same-round row (`N == M`), a same-commit row (row commit not a
   strict descendant), a short count, a wrong class, an out-of-population row that must change no
   bucket, and a late row whose note names no round.
3. **vacuous-green control**: the new gate arm run at the base revision must be red for the debt (the
   arm's module prints `unaccepted=10`), so the re-point alone cannot buy green.

## Axis and verdict rules

C1 calibration 7 → 7 (the record's six stale facts are repaired value-bound; the score holds because the
instrument class is already held), C2 operability 8 → 8 (a new capability, `append-debt`, enters the
repertoire; the score holds). No axis is claimed to move in score; both moves are measured on their
lines. No axis may be harmed: the round makes no change to depth/coverage/freshness/adjacency claims.

## Frontier step (not a claim)

- `corpus/SOURCES.md`: S558 supersedes S557 with the corrected Ollama URL (R80V2), S559 `git-merge-base`
  and S560 `git-diff-tree` ground C2's ancestry and record-parsing rules, S561 rejects the vLLM v0.33.0
  release notes for this round with its flip (R80V4 warning inventory restated). Gate records URL,
  access date and a ≤25-word located quote per row, including the S557 Gate erratum (R80V3).
- One admitted knowledge entry (`corpus/knowledge/late-acceptance-rule.md`) on the uncovered ground
  "acceptance may come from a later round, never from the same one", citing S559/S560.
- One mined mistake into `corpus/lessons/round-81.md` `## Mistakes` and one `corpus/QUALITY.md`
  criterion.
- `considerthese/2026-10-26.md` proposal 4 (daily pin-gap line) stays pending — named in the report.

## Shape

ONE v1 wave, 14 seats (band 8–16): 3 executor, 3 scribe, 2 scout, 1 connector, 2 reviewer, 2 critic,
1 mutation-tester — attack seats 5/14 = 36 % (≥25 %); at most 2 connector seats (1). No residual call.
