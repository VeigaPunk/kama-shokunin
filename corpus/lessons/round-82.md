# kama round 82 — the round-81 record is graded, and the late-acceptance rule is repaired to its own wording

Frozen plan `plans/round-82-claims.md` (freeze `bfdd7a70`; base `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`;
sealed revision C1 grades `1b64f66ddea89c57b71165eacd14b0e1d6f24e11`, the round-81 record tip). Two claims,
two distinct axes, each measured on its own receipt.

## Gate

Sources opened this round (2026-11-04) with `curl -sS`, status, bytes and sha256 recorded in the seat
dirs and re-checked by the L1; the quote is located in the file at the line named.

| id | URL | status | bytes | anchor line | ≤25-word located quote | verdict | reason / flip |
|---|---|---|---|---|---|---|---|
| S563 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md` | 200 | 136429 | 482 (`### GET /health` at 480) | "This endpoint is public (no API key check). `/v1/health` also works." | admit | grounds the newest-tag side of a `behind` relation (sha256 `eafc1b53…a137`); the sentence is byte-identical at the lane's pin, so the release gap alone is a trigger, never drift |
| S564 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md` | 200 | 119661 | 481 (`### GET /health` at 479) | "This endpoint is public (no API key check). `/v1/health` also works." | admit | the pinned-ref side of the comparison (sha256 `714c067b…6a37`): the held statement lives at the lane's own pin, so a recheck compares like with like |
| S565 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/README.md` | 200 | 9472 | 1 | "# SGLang: Fast inference for LLMs and multimodal models" | reject | the README names no health, `/v1/models` or served-identity route, so it cannot ground a check of the pinned SGLang document (sha256 `a7654a48…303c`); flip: a docs page at the same tag that names the health route |

The diff between S563 and S564 is 15 hunks: the health section shifts by one line (+1) and the
anchored sentence is unchanged, while the document grows 2402 → 2620 lines (audio/voice surfaces).
A `behind` relation is therefore a recheck trigger whose cheapest honest resolution is the pinned-doc
comparison, and the relation register's `newer` count says nothing about knowledge drift.

## Corrections

The round-81 record's five stale declared facts, each answered by the value its own cited receipt
prints (the filed §Round 81, LOG and SKILL bytes are not rewritten; the superseded values are named in
the appended `#### round-82 correction` block of the file each fact reads).

```
corrected F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F2 old=log81-frontier-rows=301 new=log81-frontier-rows=302 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=skill81-gate-arms=10 new=skill81-gate-arms=11 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F4 old=calib81-newest-closure=round-80-verifier-spotcheck.md new=calib81-newest-closure=round-81-verifier-spotcheck.md at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F5 old=logcorr81-c2-pending=1 new=logcorr81-c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=LOG.md
```

- **F1** `SCORECARD.md` §Round 81 C2 row: the row's `-> exit 0` cell says `pending=1` and its
  parenthetical repeats "1 at the receipt revision"; `.ufo/waves/round-81/measured/after/debt-green.out`
  prints `pending=4` (the receipt was refreshed at `017c34ca` after the hardening). `pending` is the
  round's own post-base events, so the value is a property of the receipt revision, not of the claim.
- **F2** `LOG.md` §Round 81: `Frontier: registry 297 → 301 rows`; the tip registry holds 302
  (`S562` landed in `50c711ec`, after the LOG line was written). The SCORECARD §Round 81 Frontier
  paragraph says 302, so the two records disagreed.
- **F3** `SKILL.md` pre-report-gate row: "(ten arms, …)" and arm 8's third member
  `tools/round75-append-accepted.py`; the round-81 gate receipt prints `arms=11` and arm 8's third
  member is `tools/round81-append-debt.py`. The row's "ten arms" survived the round that moved the
  gate to eleven (R81V4).
- **F4** `SCORECARD.md` `## Axes` calibration row: "the newest non-author closure is
  `corpus/lessons/round-80-verifier-spotcheck.md`"; at the base tip the newest closure is
  `round-81-verifier-spotcheck.md` (committed by the round-81 closure session at `aaf974db`). Tip-bound
  by construction, like round 81's F6.
- **F5** `LOG.md` `LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=1 at=1b96317f`: the correction
  itself repeats the stale target (`pending=1`) the C2 row carries; the receipt prints 4. The
  correction's own value is wrong, so the second-order correction is required.
- **F6 holds, and is not corrected**: the §Round 81 C1 row's `--selftest` tally `pass=13 fail=0` is
  exactly what `.ufo/waves/round-81/measured/after/c1-selftest.out` prints. A counter that only finds
  stale facts would be a rubber stamp; F6 is the direction test.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `register-introduction-conflated` — a rule and its code disagree on which commit introduces a row: the prose says "a row whose introducing commit", the code resolves one `git log --diff-filter=A` commit for the whole register, so a late register can never accept an event created after it first existed — exactly the promise round 81's plan made for round 82 | `.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out` (`bad_rows=15`, all `not-descendant`) at rev `b0064016`; the described promise at `plans/round-81-claims.md` §C2 ("the graded round's own record edits are `pending`, which the NEXT round must accept") | `none` — the round-81 control suite had no post-introduction acceptance case, and its own green run only graded pre-register events | `tools/round81-append-debt.py` now resolves each row's own introducing commit with `git blame <rev> -- registry/append-only-late.tsv` (`blame_rows`), with the register introduction as fallback; three selftest arms (`row-intro-later`, `row-intro-earlier`, `row-intro-unbound`) prove the row-level reading and the first is red under the old resolution (`pass=22 → pass=25`) |

## Freeze divergences (recorded; the filed plan bytes are not rewritten)

1. **The `--late` path is unbound.** `tools/round81-append-debt.py --late FILE` reads a register from
   disk but never resolves an introduction for it, so every row reports `unbound-register`
   (`measured/defects/c2-debt-register-level-before.out` records the 103-row successor-register attempt
   separately). The round therefore uses the default register path; the `--late` limit is named in the
   report and is a candidate for the next round's rule work, not silently repaired.
2. **The successor register is retained but unused.** `registry/append-only-late-r82.tsv` (a byte copy
   of the register at `b0064016`) was built for the file-level binding hypothesis before the row-level
   repair; it is committed evidence of the failed hypothesis and is kept rather than deleted, because a
   deletion of a 104-line registry would book 104 undeclared lines into round 83's acceptance population.
   Neither leg reads it.
3. **The counter repair is disclosed, not hidden.** C2's predicate names the frozen module and the rule
   text it implements; the module's *resolution* of "introducing commit" was repaired to that text after
   the red-before receipt existed. The rule sentences (exact cells, strict descendant, `N > M`, base
   split, `pending`) are unchanged; `measured/defects/c2-debt-register-level-before.out` reproduces at its named rev and
   the new selftest arms are red-capable. Whether that is admissible to a closure is the closure's call;
   the round reports the red-before and the green-after side by side.
4. **`pending` is the round's own post-base events** and rises with each later record commit, as in
   round 81. The graded buckets are the target.
5. **F2 is base-bound, not tip-bound.** The plan's F2 witness cell reads "the tip registry row count
   (302)"; the round's own three admitted rows move the tip count to 305, which would make the round-81
   record's honest end-state value unstatable. The counter therefore reads `corpus/SOURCES.md` at the
   round's declared base revision (`aaf974db`, 302) and the correction stays `new=302`. Both numbers are
   named in the record: 301 (declared) → 302 (base) → 305 (tip). This is the same divergence round 80
   recorded for its own F2 (a population snapshot is a property of the record's revision); the plan's
   witness cell should have said "base count" at freeze, and does not. The selftest arm
   `registry-base-bound` proves the base reading (a tip with 305 rows must not move the witness).

## Hardening notes (wave attack seats, applied before the report)

- **RV01 (C1 counter) escapes, fixed and re-armed.** Three admitting lines were closed: the `fix` token
  test was substring containment (`sc81c2-pending=44` backed `new=…=4`) and now requires the whole token
  with a non-token right boundary; `fix=` could name this lesson itself and now cannot; the corrections
  container matched any `## ` heading containing "Corrections" and now must be exactly `## Corrections`.
  Three selftest arms (`near-token-new`, `fix-self-referential`, `near-corrections-heading`) make each
  red (selftest 19 → 22). Residual, disclosed: witnesses are read at the graded tip by design (a record
  rewritten to match its receipts stops being stale), and F4's closure pointer is sequencing-fragile —
  a round-82 closure landing before grading moves it, exactly as round 81's F6 did.
- **RV02 (C2) escape, fixed.** The note's deletion round was bound only by `N > M`, so a row noted
  `round-82 accepts round-79` for a round-81 event passed both legs; `tools/round82-late-delta.py` now
  compares the note's deletion round with the event commit's own subject round (`subject_rounds`), with
  the `note-wrong-deletion-round` arm red (selftest 12 → 13). The debt leg's `not-descendant` /
  `unbound-register` behaviour and the `--late` limit are unchanged and were confirmed correct.
- **CR01 (critic) receipt defects, fixed.** Two `before`/control receipts carried `tail`'s exit status
  instead of Python's, and the C2 delta `before` receipt was measured at a revision where its tool did
  not yet exist. Both were re-measured: the C1 controls now run the frozen command at the graded tip
  (the sealed facts do not move) and the delta `before` runs the tip instrument against the base tree
  (`# tree=bfdd7a70`), each with a real `EXIT=`. The two in-place SCORECARD edits this round made
  (banner, claim row) are the `pending` events the round reports, not append-only silence.
- **F2 plan-literal reading.** A plan-literal grader reads "the tip registry row count" as 305 and calls
  the correction `new=302` unbacked; the record states both numbers and the base binding is divergence 5.
