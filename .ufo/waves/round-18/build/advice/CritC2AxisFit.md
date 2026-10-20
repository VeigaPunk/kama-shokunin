VERDICT: confirm — C2 ("killing named detector survivors") is calibration, not operability; the live risk is not the axis label but the counting command's operability-shaped output (fixable by claim-binding, correction below).

Seat: KamaR18.CritC2AxisFit-2 (critic, read-only). State attacked: the C2 claim as declared in the
round-18 build context and `.ufo/waves/round-18/build/spec.json` (items C2CheckPyRobust,
C2FaultControls, C2AppendOnly, C2Provenance, C2Survivors). No C2 artifacts had landed yet; I
attacked the claim structure, the file set and the survivors.py command shape.

## Axes named

- **calibration** (AXES.md:15) — the axis C2 declares and must land.
- **operability** (AXES.md:13) — the axis an outside verifier could read into C2's count.
- **distinct-axes / lowest-axis rules** (AXES.md:31-34) — what collapses if C2 is not calibration.
- **calibration no-harm** — the F7 merge-versus-mislabel boundary for the bookkeeping tools.

## Rules applied

- `AXES.md:15`: calibration is "Self-assessment quality: gaps named honestly, confidence graded,
  overreach caught".
- `AXES.md:13`: operability signal is "A checklist item can be run and produces the stated outcome".
- `AXES.md:32-34`: "two claims on one axis in one round count as one claim" and "At least one claim
  works the lane's lowest-scoring non-retired axis".
- `.ufo/waves/round-17/build/advice/CriticAxisSeparability.md:62-64`: the separating criterion the
  round-17 closure adopted — "whose behaviour does the failing control change? … C1's controls vary
  the lane's **own** instrument … That is self-assessment, i.e. calibration. C2's controls vary the
  **external subject**".
- `../shokunin.conf:52`: kama's live axes are "operability + calibration"; calibration 7 is the
  lowest (operability 8, `corpus/lessons/round-17.md:6-7`).

## Findings

### F1 — C2's whole file set varies the lane's own instruments, never the subject runtime → calibration

The C2 file set is `tests/probe-verdicts/check.py`, `tests/probe-verdicts/fault-controls.py`,
`tools/sources-append-only.py`, `.ufo/waves/round-18/dispatch-provenance.py`, `c2/*`. Each named
survivor class sits inside a lane self-assessment instrument:

- check.py H1/H2/H3/H5/H6/H7 — weakened gradings of the lane's own verdict-grading instrument
  (spec.json C2Survivors family (a), `MutC1Preregistered*.md`).
- fault-controls self-mutants — the detector of the detector (spec family (b),
  `MutFaultControlsSelf.md`).
- sources-append-only `opened`-cell / blank-line mutants — the guard on the lane's own
  append-only record (spec family (c), `MutAppendOnlyGuard.md`).
- dispatch-provenance `refused: 0` — a miscount in the lane's own dispatch ledger (spec family (d);
  `corpus/lessons/round-17.md:88` M4 residual, `round-17-verifier-spotcheck.md:254` "A refused task
  call records `refused: 0`").
- crash faults (nested JSON, 5,000-digit ints, escaped `sleep`) — check.py's documented exit
  behaviour falsified, same shape as round 15's admitted calibration repair
  (`round-15-verifier-spotcheck.md:7`: "Repairing a falsified executable assessment promise is a
  bounded improvement").

Under the adopted criterion, a killed mutant changes what the lane's *own* instruments detect, not
which llama.cpp server or harness behaviours the capability rejects. Contrast C1, whose controls run
fake servers through `kama-llamacpp-live.py` — that is subject behaviour, i.e. operability
(`CriticAxisSeparability.md:64`). C2 therefore lands on the correct axis and satisfies the
lowest-axis obligation, which is live: `SCORECARD.md:696` "last capability entry round 16
(window 1 of 4)" — round 18 is window 2 of 4, no waiver.

### F2 — Round-17 closure accepted the identical class as calibration

- `corpus/lessons/round-17.md:15-30` declares C1 calibration over the same instrument class
  (`check.py` mutants surviving the only detector; `served_model` and route ungraded; malformed
  output crashing it) and was admitted.
- The separation criterion is written down at `corpus/lessons/round-17.md:46-49`: "C1 changes the
  lane's own measuring instrument and corrects a false self-description (calibration); C2 changes
  which server and harness behaviours the capability rejects (operability)".
- Round-16 mutation advice already framed it `.ufo/waves/round-16/falsify/advice/MutateHarness.md:5`:
  "**Calibration / detector sensitivity:** whether the frozen/current totals distinguish lost
  reason, exit, drift, verdict-case, or timeout grading."
- The outside check routed C2's debt in exactly these terms
  (`round-17-verifier-spotcheck.md:249-254`: "R7 — detectors of detectors and provenance …
  `fault-controls.py` survives F0 bypass … `sources-append-only.py` survives dropping the `opened`
  cell … A refused task call records `refused: 0`").

No counter-precedent exists: the round-16 critic's worry was about the *count's framing*, and that
critic itself conceded the fix recasts the count as calibration (F3 below).

### F3 — Residual defect: `survivors.py` reports detection power, which an outside verifier can read as operability [INFERENCE until a verifier rules]

`spec.json` C2Survivors defines the count as killed/survived per mutant and the `refused` count —
detector-power numbers with no reference to a lane statement. This is the exact shape round-17's
critic flagged: "The counting command measures none of these. What it measures is probe behaviour.
That is an operability signal" (quoted inside `CriticAxisSeparability.md:32-34`), whose stated
consequence was "C1 and C2 sit on one axis and count as one claim" and the lowest axis unworked.
The round-17 escape was correction 1: "Recount C1 against documented claims, not just mutants …
documented grading sentence → mutant → detector → before survives / after killed"
(`CriticAxisSeparability.md:99-102`).

**Smallest safe correction (L1, SCORECARD/lesson wording only — no spec or code change):** publish
C2's before→after as a ledger binding each named survivor to the lane statement it defeats, e.g.
`check.py`'s documented exit contract vs crash faults; CORPUS rule 2 / SOURCES immutability vs
`opened`-cell and blank-line mutants; the provenance-ledger `refused` field vs the refused-call
miscount; "8/8 faults detected" vs fault-controls self-mutants. The survivors.py numbers stay the
mechanism; the SCORECARD row cites the sentence→mutant→detector table so the count reads
claim-vs-evidence (calibration), not instrument capability (operability).

### F4 — If C2 were ruled not-calibration, every legal fallback fails; it cannot be salvaged as operability

- *Operability:* C2 then shares C1's axis → `AXES.md:32-33` merges them to one claim, and the
  lowest-axis rule (`AXES.md:33-34`) is unmet because nothing works calibration. Admission fails.
  Re-declaring C1's own calibration would not help — kama's only live axes are operability +
  calibration (`shokunin.conf:52`), so the merged claim cannot move to a third lane axis either.
- *Exploratory:* needs "a named non-author reviewer on record" (`AXES.md:46-48`) and "no counting
  command is required" — C2 ships one (`survivors.py`); the fit is structurally wrong.
- *Capability acquisition:* C2 demonstrates no new `SCORECARD` capability row; survivor-killing is
  not a repertoire entry (`AXES.md:60-64`).
- The only honest operability version of C2 would require its controls to vary the external subject
  (e.g. check.py running against real probe output of a misbehaving server) — a different claim,
  not this file set.

So C2 is calibration or the round's claim structure fails; there is no third reading.

### F5 — Secondary boundary notes (keep out of axis-verdict citations)

- `sources-append-only.py` and `dispatch-provenance.py` inside a *calibration* claim match round-17
  F7: "All three are honesty-of-own-records tools, which is calibration-shaped … merge with C1 under
  `AXES.md:32-33`, which is harmless but earns no credit. Anywhere else they mislabel an axis"
  (`CriticAxisSeparability.md:82-87`). Fine inside C2; never cite them as operability evidence or
  separate credit.
- [INFERENCE] The `controls.py` self-check arms routed to C1 (`MutControlsSelf`) are likewise
  instrument-on-instrument evidence — calibration-shaped inside an operability claim. Round 17 made
  the same fold ("the gate-flip arm 0 accepted" inside C2's operability measurement,
  `corpus/lessons/round-17.md:170`) and it was admitted; keep C1's axis evidence on the
  subject-facing counts (accepted-bad, good-rejected, misclassified, uncontrolled-check) and report
  self-check kills as detector integrity only.

## Impacted axes

calibration (claim landing + no-harm), operability (only via the mislabel path F3/F5), the
lowest-axis and distinct-axes rules (collapse scenario F4).

## Limitations

- C2 artifacts were not built; F1 rests on the declared file set, spec prompts and the named
  survivor advice files, not on landed diffs.
- I ran no survivors.py, gate, controls or mutant grid; started no server; bound no port.
- F3's verifier-merger risk is marked [INFERENCE]: the same risk was named but did not materialise
  in round 17 because correction 1 landed.
- I did not read sibling critics' reports this wave.

## Installs

None.
