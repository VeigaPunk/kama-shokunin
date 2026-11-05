# Round 87 — lesson (kama)

Base `362b0d4a241520c9bc79b204c042d9fcefbb06ea`; freeze `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`
(`plans/round-87-claims.md`, amendment A1 at its tail). Wave 1: `.ufo/waves/round-87/w1/` (12 seats).
Fresh-start round (run-15 amendment 27); the last three closures read first: round-84, round-85 and
round-86 spotchecks, all `rejected-honest-stop`.

## Claims

- **C1 calibration — honest stop.** Probe battery on the successor candidate: `escapes=0 control=red`
  (`.ufo/waves/round-87/controls/c1-probes.py tools/round87-…`, candidate at
  `.ufo/waves/round-87/w1/out/EX01SelectorRepair/round87-rendered-cells.py`). Frozen population check
  (A1 R4, `diff` of the population block against the round-86 block) is non-empty: the candidate
  rewrote the gate coupling and docstring population. A population change is a new claim, so C1 is not
  admitted. The calibration cell is corrected to the observed closure state (see SCORECARD §Axes).
- **C2 operability — verified.** `round86-instruments` is arm 14 of `tools/pre-report-gate.py`;
  `tools/round87-gate-arm-faults.py` kills 3/3 seeded instrument faults (`ARM14_FAULTS faults=3 killed=3
  escaped=0`), and the arm-absent control is red (`CONTROL_RED`, `killed=0 escaped=3`).

## Mistakes

**M1 — round-86 closure left three lane-authored files untracked (R86V1).** Class: closure hygiene; a
round's files outside the current round directory. Evidence: `corpus/lessons/round-86-verifier-spotcheck.md`
(routed defect R86V1); `git status --porcelain -uall` at round-87 start listed
`.ufo/waves/round-86/w3-results.json`, `.ufo/waves/round-86/w3/SC01DanglingPointers.md`,
`.ufo/waves/round-86/w3/out/SC01DanglingPointers/findings.md`. Captured-by: none. The `round-clean` arm
(`tools/pre-report-gate.py`, `wave_rel = .ufo/waves/round-<N>`) only sees the round being measured, so
leftovers of the previous round were invisible to the gate that closed it. Fix: committed under round 87
in the freeze commit `94e8fe7b`; `EX02GateCensus.md` and `CN01OverlapScan.md` (round-86 w3 seats) remain
absent on disk, recorded here, not reconstructed.

**M2 — C1 false greens: list-marker fence closer and first-word disposition oracle (R86V2).** Class:
rendered-identity selector accepting container markers as fence closers and reading the disposition from
anywhere in the closure body. Evidence: `.ufo/waves/round-87/controls/c1-probes-before.out` (`escapes=3
control=red`); the `CONTAINER` regex keeps list and blockquote markers in `FENCE_CLOSE` at
`tools/round86-rendered-cells.py`. Captured-by: none in round 86; the round-86 probes were not in the
gate. Fix: successor rules R1–R3 (`plans/round-87-claims.md`); the probe battery is now a frozen control.
The successor still escapes nothing on the battery but is not admitted (M3).

**M3 — a successor passes its own probes while changing the population it is judged on.** Class:
claim-scope drift inside a fix; the candidate's coupling rewrite (sentence-scoped "cited" revisions) is
broader than the frozen R5-free population. Evidence: `.ufo/waves/round-87/w1/out/EX01SelectorRepair/selector.diff`
(hunks at the `Population` docstring and `gate_fact`); the A1 R4 diff is non-empty. Captured-by: the
frozen R4 population rule, which the candidate's own probe battery does not check. Fix: none this round;
the candidate stays outside `tools/`; round 88 must freeze a population-preserving rule (or a new claim)
before data, with the probe battery and an R4 diff arm.

**M4 — calibration cell stale at round start.** Class: self-assessment drift. Evidence: at base the
SCORECARD calibration row named `corpus/lessons/round-85-verifier-spotcheck.md` and `round85 rejected-honest-stop`
while round 86 was the newest closure (`.ufo/waves/round-87/controls/c1-live-before.out`:
`mismatches=2`, and the gate's `selfdesc` and `newest-closure` arms red). Captured-by: `selfdesc` and
`newest-closure` arms, but only when the gate is run; the round-86 closure did not run it at the cell.
Fix: the calibration row was corrected to the round-86 closure's observed disposition (SCORECARD §Axes).

## Gate

Sources opened this round (access date 2026-11-05; each quote ≤25 words, verbatim, checked by
`grep -c -F` inside its h2 span, `.ufo/waves/round-87/w1/out/SC01SourceOpen/quotes.md`):

| Row | URL | Located quote | Decision |
|---|---|---|---|
| S578 (re-open) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks §4.5 | "The closing code fence may be preceded by up to three spaces of indentation, and may be followed only by spaces or tabs" | still matches live page; `used-by` unchanged |
| S580 (new) | https://spec.commonmark.org/0.31.2/#list-items §5.2 | "A list item may contain any kind of block:" | admitted for C1 rule R1 (content of a list item is block content) |

Reviewer RV01 claimed the closer shape is in §4.6; refuted by the fetched §4.5 text (`fetched-4.5.txt:4`).

## Frontier — considerthese

`considerthese/2026-10-26.md` proposal 2 (track what happens to my own proposals): the lane's
proposal-disposition record contradicts itself (`corpus/lessons/round-86.md:115-116` vs
`round-74.md:18` / `round-81.md:98-101`), and the standing table lapsed after round 75
(`round-75.md:87`). Mined as a lesson item, not as a QUALITY criterion: draft **KQ141** — keep one
committed disposition ledger for each `considerthese` proposal, reconciled by a counter before a round's
claims freeze. Not implemented this round; the proposal stays open in the ledger.

## Assimilation

None (`merge/kama/` not adopted this round).
