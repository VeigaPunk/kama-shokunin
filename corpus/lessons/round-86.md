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


## Append-only provenance erratum (R84V5)

The round-84 frozen plan (`plans/round-84-claims.md`) cites a red control at
`measured/before/red-selfrecord.out`; no such path exists. The retained red demonstration is
`.ufo/waves/round-84/measured/after/c2-red.out` (the same counter run with `--no-corrections` at
`3e93febb0f40955b08dc80367e8ef658eaccdfd6`). The frozen plan's bytes are not rewritten; this erratum
is the correction of record. The round-84 C2 numeric predicate stays verified as filed.

## Open, not repaired

- R84V1 (a frozen auxiliary disclosure instruction missed) stays an honest miss: no event-loss
  disclosure is manufactured for a source event that was `ungraded`, not restored.
- The round-69 date-ordering exit 2 on undated historical closures (M2) is routed, not fixed.
- C3 proves documentary origin at fetch time; it does not prove that the row's *verdict* word
  (`holds`/`moved`/`drifted`) is the right one for a semantic change — that stays the declarer's
  judgment, and the counter only re-derives byte equality.
