# Round 86 — lesson (kama, fresh start after r83/r84/r85)

Base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`; freeze `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`.
Three claims: C1 calibration (rendered-cell identity), C2 operability (mutant → owning arm plus
summary/failure-line cardinality), C3 freshness (pin origin corroboration). Plan
`plans/round-86-claims.md`; counter `.ufo/waves/round-86/count.py`.

## Gate — sources opened this round

Opened 2026-11-04 (static read of the published specification, no endpoint sampled).

| Row | URL | Located quote (≤25 words) | Decision |
|---|---|---|---|
| S576 (re-opened, used-by extended) | https://spec.commonmark.org/0.31.2/#atx-headings | §4.2: “The opening # character may be preceded by up to three spaces of indentation.” | admit — grounds the 0–3-space heading rule the selector already uses |
| S578 (new) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks | §4.5: “A fenced code block begins with a code fence, preceded by up to three spaces of indentation.” | admit — grounds fence exclusion, including a fence opened at up to three spaces |
| S579 (new) | https://spec.commonmark.org/0.31.2/#indented-code-blocks | §4.4: “An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation.” | admit — grounds the column-0 selection rule |

Refused this round: no candidate row was refused. The three rows are one specification read at three
sections; the census reports `W04 duplicate url spec.commonmark.org/0.31.2 across scopes` because it
compares URLs without anchors — disclosed, not suppressed. Recheck cadence `on-release`.

Registry changes, old → new (append-only registry, CORPUS.md rule 2): S576 `used-by`
`corpus/lessons/round-85.md` → `corpus/lessons/round-85.md, corpus/lessons/round-86.md`; S576
`opened` stayed `2026-11-04` (re-opened the same day, no date change to log). S578 and S579 enter at
`status=mined`, `opened=2026-11-04`, `recheck=on-release`.

## Mistakes

**M1 — a raw-line selector read a fenced copy as the live cell.** Class: rendered-identity. Evidence
`.ufo/waves/round-85/w1/out/SN01Scope/receipts/fenced-shadow.md` (a fenced block carrying both
correct-looking cells, while the live authority line still said “under terminal measurement” and the
live calibration row still named round 83) plus `.ufo/waves/round-85/w1/out/CR01Cheats/receipts.json`.
The frozen round-85 counter selected the *first* line matching the cell pattern without knowing what a
renderer would show, so the shadow satisfied it and the round's own kill rule fired. Captured-by: the
criterion this round adds — a selected cell must be a rendered cell (no fence, no HTML comment, no
`round-N correction` block, column 0), and the instrument must be shown to reject a shadow while
accepting a repaired cell. Fix: `tools/round86-rendered-cells.py`, whose `--selftest` arms
`fenced-shadow`, `comment-shadow`, `tilde-fence-shadow`, `indent-shadow` and `unclosed-fence-fails-closed`
each fail the shadow (receipt `.ufo/waves/round-86/measured/before/c1-selftest.out`). Shown able to
fail: the same five arms are red for the round-85 selection rule, and the base tree itself prints
`mismatches=3`.

**M2 — the closure pointer was never mechanically graded because its counter exits 2 on an undated
historical closure.** Class: calibration/tooling. Evidence: `python3 tools/round69-newest-closure-counter.py --repo .`
(no `--since-round`) prints `COULD_NOT_EVALUATE closure round-10-verifier-spotcheck.md carries no
parsable ISO date`, exit 2, while the live calibration row named round-84 after round-85's closure had
landed. Captured-by: resolving the newest closure by **round number**, the invariant the row is about,
instead of by a date field the historical files do not carry. Fix: the round-86 counter resolves by
highest round number and reported the stale pointer as `closure=0` at base. The round-69 instrument is
left unchanged — it is historical, and its `--since-round 63` scope is the workaround.

**M3 — the shadow-control arms were vacuous, so five selector mutants survived.** Class:
control discrimination. Evidence: `.ufo/waves/round-86/w2/out/MT01SelectorMutants/findings.md` — the
fixture emitted the stale live cell first and the shadow after it, so `select_cells` never saw the
shadow; with the HTML-comment, `round-N correction`, column-0 or tilde-fence exclusion disabled the
selftest still printed `pass=11 fail=0`. Captured-by: an exclusion arm must make the excluded
construct the **first** candidate cell; a control whose subject never enters the population cannot
fail. Fix: the fixture emits the shadow first and gains `correction-shadow` and `indent-row-shadow`;
7/7 source mutants are now killed by named arms (`RENDERED_CELLS_MUTANTS mutants=7 killed=7
escaped=0`, `.ufo/waves/round-86/measured/after/c1-mutants.out`). Shown able to fail: each mutant run
exits 1 naming its own arm.

*Correction (round-86 w3 `CR01DoNothingControl` record audit):* the delivered driver declares ten
mutants and the cited `measured/after/c1-mutants.out` prints `RENDERED_CELLS_MUTANTS mutants=10
killed=10 escaped=0`, not `7`. The `7/7` sentence above was the state when M3 was mined, before the
container-fence and backtick-info mutants were added; the tally is corrected here rather than
rewritten, and the receipt is the authority (KQ133).

**M4 — a selftest summary-format extension turned a frozen gate arm red.** Class:
consumer coupling. Evidence: `.ufo/waves/round-86/w2/out/EX02GateArms/EX02GateArms.md` finding 1 —
`round81-instruments` was green at the base (`APPEND_DEBT_SELFTEST pass=34 fail=0`) and red at the
tip (`… fail=0 arms=34`), because `tools/pre-report-gate.py` arm 11 fullmatches the old shape.
Captured-by: before changing a line another frozen instrument parses, run every consumer of that
line. Fix: the summary keeps its round-81 shape and the arm population rides the separate
`APPEND_DEBT_SELFTEST_ARMS` line the round-86 counter reconciles.

**M5 — the gate fact read the receipt at the graded revision, not at the revision it named.** Class:
provenance binding. Evidence: `.ufo/waves/round-86/w1/out/RV01ClaimsReview/` fixtures f1/f4 — a
banner naming an ancestor that never carried the declared receipt graded `gate=1` while the receipt
existed only at the tip. Captured-by: the frozen predicate's clause 5 ("the receipt's bytes at `R`
containing that exact token") read literally. Fix: `GitTree.blob_at(R, path)` and the arm
`revision-carries-no-receipt`; a tampered worktree instrument is a separate, disclosed limit
(w2 `CR01SizingControl`), routed to round 87.

**M6 — the C2 classifier skipped every clause that needed the ARMS line and ignored stderr.**
Class: clause coverage. Evidence: `.ufo/waves/round-86/w2/out/MT02CardinalityForgery/evidence/`
(`probe-classify.out`, `cli-matrix.out`) — a summary `pass=0 fail=0` with no `arms` field, a run with
no ARMS line, and a run with non-traceback stderr all classified `escaped`, while the frozen clause
list requires `pass + fail == arms`, `ARMS arms == expected`, `ARMS fail_lines == summary fail ==
printed FAIL lines`, empty stderr. Captured-by: implement every declared clause as a check and add a
selftest arm per clause. Fix: `classify()` now requires exactly one ARMS line (a summary with no
declared population cannot reconcile), binds the summary's `pass + fail` to that population, and
rejects non-empty stderr; arms `summary-without-arms-field`, `no-arms-line` and `stderr-noise` hold it
(selftest 13/0). **Disclosed limit:** a *consistent* forgery of every line (summary, ARMS line and
exit code all agreeing on a population that the source does not have) is not distinguishable by a
text-only classifier; that is MT02's `b2` class and it is routed to round 87 as a source-bound
ground truth, not claimed here.


## Append-only provenance erratum (R84V5)

The round-84 frozen plan (`plans/round-84-claims.md`) cites a red control at
`measured/before/red-selfrecord.out`; no such path exists. The retained red demonstration is
`.ufo/waves/round-84/measured/after/c2-red.out` (the same counter run with `--no-corrections` at
`3e93febb0f40955b08dc80367e8ef658eaccdfd6`). The frozen plan's bytes are not rewritten; this erratum
is the correction of record. The round-84 C2 numeric predicate stays verified as filed.

## Frontier and considerthese

`considerthese/2026-10-26.md` proposal 3 ("keep a running count of counters that a shortcut can
satisfy") is mined into `corpus/QUALITY.md` criterion **KQ139**: a control arm is admitted only when
its subject sits inside the population the arm tests, and a summary-format change must be checked
against every frozen consumer of that line. The proposal's reflection is a pointer, not evidence —
the evidence is this round's own two findings (M3's vacuous `*-shadow` arms and M4's gate-arm/consumer
coupling), both measured before the criterion was written. Proposals 1, 2 and 4 stay unimplemented
and are not claimed this round.

`Assimilation: none` — the `corpus-expansion-1` package at
`/home/vgpnk/Projects/shokuknow/merge/kama/` was read read-only; no staged serving/cache/router theme
fits three instrument repairs, so no entry, id or row is adopted. `corpus/README.md` §Frontier is
unchanged by this round: the three instruments extend the self-assessment and origin surfaces the
lane already held, they do not open new province ground.

## Open, not repaired

- **Superseded intermediate receipt (round-86 w3 `MT02ForgeryArms` §3).**
  `.ufo/waves/round-86/measured/after/c2.out` ends with `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`,
  which the terminal bytes cannot print: that summary line lost its `arms=` suffix in `c5a32443` so the
  frozen gate arm 11 fullmatch keeps working. The receipt is an intermediate, superseded measurement;
  the terminal receipts (`measured/terminal/c2.out`, `terminal/mutant-owners-selftest.out`) carry the
  producible lines (`pass=34 fail=0`, `DEBT_MUTANT_OWNERS … arms=34 cardinality=ok owners=5/5`, and
  `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0`), and the SCORECARD cells cite those.
  The bytes are not rewritten.
- R84V1 (a frozen auxiliary disclosure instruction missed) stays an honest miss: no event-loss
  disclosure is manufactured for a source event that was `ungraded`, not restored.
- The round-69 date-ordering exit 2 on undated historical closures (M2) is routed, not fixed.
- C3 proves documentary origin at fetch time; it does not prove that the row's *verdict* word
  (`holds`/`moved`/`drifted`) is the right one for a semantic change — that stays the declarer's
  judgment, and the counter only re-derives byte equality.
