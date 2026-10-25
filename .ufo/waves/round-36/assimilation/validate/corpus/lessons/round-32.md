# kama — round 32 lesson (2026-10-24, attempt 1)

## Claims

- **C1 (calibration).** Repaired claim-row-evidence counter `.ufo/waves/round-32/count-c2r.py`
  (frozen at `9afaf0e9`, sha256 `ef298b63…c92e`): round-qualified `(round, row, class)` key with a
  uniqueness precondition, repairing the frozen round-31 non-injective key. Base
  `18464d0866afd5c4b471c8478d72b079d82d1fa8`: `valid_corrections 10 unresolved 3 met False`
  (identical to the frozen counter's counts). Landed tip: `valid_corrections 13 false_corrections 0
  unresolved 0 met True` via three round-qualified corrections `CR31:11:C1:p1`,
  `CR31:12:C1:p1`, `CR31:13:C1:p1`. Kill rule receipts: one collapsed `CR31:C1 collapsed:p1`
  correction flips the FROZEN counter to `met True` (`valid 11 unresolved 0`) while the repaired
  counter reads it false with `unresolved 3` (`c1/controls/KeyCollapse/`); two corrections sharing
  `(11, C1, p1)` are both false (`c1/controls/DupKey/`).
- **C2 (operability).** `tools/gate-registry-check.py` v2: a tracked counter is registered only
  inside a five-column registry-table row, and the row is graded (`thin-row`, `empty-entry`,
  `empty-exit-map`, `missing-path:PATH`). Do-nothing v1 gate: exit 0 on every defective fixture
  and on the prose-only base tree. v2 at the landed tip: exit 0 `registered 10 unregistered 0
  defective 0`; fixtures exit 1 named; mutation arms flip exactly their fixture (thin-row
  entanglement disclosed). The repair exposed two prose-registered counters (round-17, round-26),
  registered by SKILL's round-32 block.

## Gate

One new row opened this round: **S193** — Gate registry check v2 (own work) —
`tools/gate-registry-check.py`, opened 2026-10-24 at `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`.
Located quote (docstring, "Contract" section, line 22): "`A path is registered iff it occurs in
a cell of a row of such a table.`" (16 words.) Tier A scoped to the gate's population and
row-meaning semantics; `used-by` cites this lesson and `SKILL.md`; C2's SCORECARD evidence row
cites this Gate. Zero cells changed old→new on S180-S192; zero rejections; census 192 → 193,
validate exit 0 (`.ufo/waves/round-32/census-end.out`).

## Mistakes

| # | class | evidence | captured-by | fix (shown able to fail) |
|---|---|---|---|---|
| 1 | reference-drift: the round-31 attempt-3 SCORECARD table and filed report cite `w2/out/RefRepair/`; the receipt is at `.ufo/waves/round-31/controls/RefRepair/receipt.txt` | `grep -n "w2/out/RefRepair" SCORECARD.md` → line 1723 (attempt-3 table); the same drift is in the filed fleet report (fleet-owned, corrected here by append per KQ26) | none — no round-32 command resolved last round's new receipts against their cited pointers before filing | appended record in SCORECARD §Round 32 names the correct path; the wave item `RevPointerSweep` under `.ufo/waves/round-32/w1/` generalizes it: every receipt/pointer cited by a round's SCORECARD/LOG/lesson rows must resolve at the landed tip, with the sweep command pasted |
| 2 | number-drift: the round-31 report says wave 2 returned 44 reports; the committed tree holds 43 seat-output dirs and one seat (`ConnInstrumentDup`) has no output at all | `find .ufo/waves/round-31/w2/out -maxdepth 1 -type d \| wc -l` → 44 including `out` itself (43 seats); `grep -rli instrumentdup .ufo/waves/round-31/w2/out` prints nothing | none — the report counted planned seats as returned reports; the wave had no committed post-dispatch registry to check against (ScribeWaveRecord itself flagged the absent registry) | SCORECARD §Round 32 records 44 planned / 43 dirs / 1 unverifiable, and the w1 wave carries `ScribeWaveRecord`-class items: a wave's returned-seat count must come from a committed registry or directory census command, never from the plan |
| 3 | prose-only registration survived the round-28 occurrence gate for four rounds: `.ufo/waves/round-17/count-verdicts.py` and `.ufo/waves/round-26/count-c1.py` were named in SKILL prose, not in any registry row, and the gate read them registered | `grep -nF <path> SKILL.md` → line 582 / line 1073, both prose paragraphs; the v2 gate on the base tree prints `unregistered` for both (`c2/before-base.out`) | the round-28 gate's own boundary note said "occurrence check, not a table-row check" — the class was disclosed and left open | the v2 gate's `prose-only` selftest arm fails (exit 1) on a prose-only fixture and passes only when the row exists; both counters are registered by real rows in SKILL's round-32 registry block |

## Repairs (routed by the round-31 closure; not claims)

- Defect 5 (RefRepair pointer drift): mistake 1 above.
- Defect 6 (w2 seat count): mistake 2 above.
- Defects 1 (C1 eligibility), 2 (KQ42 probe gating), 4 (pin bytes): wave items under
  `.ufo/waves/round-32/w1/` (32 seats, policy v1, validator exit 0, not dispatched — the host
  mapping gives this seat no dispatch tool; the orchestrator dispatches prepared waves between
  rounds). Not claimed this round.

## Wave findings that shaped the verdicts

- This round ran without a dispatch tool (accepted host mapping): no L2 seats were spawned; the
  build and falsification work above was executed by the L1 directly, and the 32-seat falsify wave
  is prepared, validated and left for the orchestrator. Claims were sized so the L1 can freeze,
  control, measure and land them alone: both predicates name exact output lines and exit codes.
- The thin-row control is entangled with `empty-entry`/`empty-exit-map` (a one-cell row empties
  both); the mutation arm removes the `thin-row` check alone and the fixture still fails on the
  other two — disclosed in `c2/mutations/MutNoThin-vs-CtlThin.out` rather than hidden.
- `count-c2r`'s corr-round fallback (id without a round digit, unique problem row) exists only for
  reading hand-written prose; the three committed corrections carry explicit rounds, and the
  collapse control shows the fallback refuses the ambiguous case (three problem rounds → None).

## Limits

- Both claims are instrument repairs: they make the lane's self-measurement expressive and its
  registry meaningful; they do not re-earn the round-31 depth claim (eligibility counter not yet
  built) and do not grade any instrument's correctness.
- The v2 gate grades rows in the five-column registry tables only; a counter named in a differently
  shaped table or list is read unregistered (conservative; no such case exists at the tip).
- `missing-path` checks repo-relative cited paths at the evaluated revision; it does not validate
  digests, exit-map truth, or that the named command still runs (KQ20-style fail-capability is the
  instrument's own self-test duty).
- Receipts in `.ufo/waves/round-32/c2r/` and `c2/gate-tip.out` measure the data tip
  `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279` and are committed with the final receipts; the
  report-time untracked gate (mistake 5 of round 31) passes at zero before the report lands.
