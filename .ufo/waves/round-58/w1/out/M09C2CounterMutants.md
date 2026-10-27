# M09C2CounterMutants — C2 counter mutation probe (round 58, kama w1)

Attacks: frozen C2 counter `tools/round58-c2-counter.py` and its control set.
Bytes probed: freeze dcd69473 blob 99798397bd7de0477b07a89ec675ee97994a8814 (content sha256 61ef1f565706db459b55e3224a0fbedcacf944a080b0a2c31c22ce3b3fcaaeee).
Kill rule under test: "any nonzero counter at the measured tip -> C2 not met"; controls = base row, claim-deleted row, verdict-flip-only row.

## Method
One shared clone `/fast/scratch/hyaku/kama-r58/M09C2CounterMutants/clone` (read-only use). 4 mutants, each a single-point edit
(full diffs: `out/M09C2CounterMutants/mutants/*.diff`): drop `stale`, drop `verdict`, drop `including`, swap manifest key
`r["lane_round"]` -> `r["round"]`. 4 SCORECARD fixture commits (parent = measured tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a,
toplevel asserted, fixture-local identity), each edit confined to the `## Axes` calibration row:
ctl-del 0464038aebe34de7489223eca14df105be7786d3 (claim deleted), stale 369f6ae63cac94ad590aca719f1f8894f62ea429
(claim round 56, token correct for 56), verdict 8ff7b0becdde824868855df129ea4edb94d1471f (claim 57, token `admitted`),
including b8434449250ab4a8c92291f6c646493ae4e62bef (`including round 56`). Matrix: 5 counters x 5 repos, all with
`--manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e --fleet-repo /home/vgpnk/Projects/shokunin`, TMPDIR=scratch.
Template: `TMPDIR=$S python3 $S/<counter>.py --repo <repo> --tip <rev> --manifest-rev 941acf7... --fleet-repo /home/vgpnk/Projects/shokunin`.

## Baseline (conclusive)
pristine @ e4891d8a: `r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`, exit 0. Matches frozen C2 sentence.

## Matrix (exit | r42 missing stale verdict including mismatches met)
- pristine:  genuine 0|0 0 0 0 0 0 True; ctl-del 1|0 1 0 0 0 1 False; stale 1|0 0 1 0 0 1 False; verdict 1|0 0 0 1 0 1 False; including 1|0 0 0 0 1 1 False
- m-drop-stale: genuine 0 True; ctl-del 1 False; **stale 0 True**; verdict 1 False; including 1 False
- m-drop-verdict: genuine 0 True; ctl-del 1 False; stale 1 False; **verdict 0 True**; including 1 False
- m-drop-including: genuine 0 True; ctl-del 1 False; stale 1 False; verdict 1 False; **including 0 True**
- m-key-round: identical to pristine on all 5 repos (see equivalence proof)

Verdicts: **all 4 mutants SURVIVE the frozen C2 control set.**
- m-drop-stale, m-drop-including: pass the measured tip and every frozen control-row shape (claim-deleted, verdict-flip shape = my stale fixture) — no frozen control isolates staleness or the `including round N` repeat.
- m-drop-verdict: passes the measured tip; the frozen verdict-flip receipt (claim N=56, token correct for 56, stale=1) still fails under it — via `stale=1`, i.e. rejected for the wrong reason; the control never isolates a wrong token against the CURRENT round. Only my extra fixture (claim 57 + `admitted`) exposes it, and no such row is in the frozen control set.
- m-key-round: survives trivially — equivalent mutant.
Root cause: the kill rule only ever evaluates counters at the measured tip, where no defect exists, so weakening a defect detector is invisible; controls are scored by the pristine counter, not by mutants. This is a coverage LIMIT of the control set, not a defect in the frozen sentence; no predicate change is proposed.

## Equivalent-mutant proof (m-key-round)
At MANIFEST rev 941acf7: 48 kama closure rows, every row has round == lane_round; `{lane_round: verdict}` and `{round: verdict}` are
identical dicts, and for non-kama rounds both maps miss. So the swap is indistinguishable for EVERY possible SCORECARD row —
confirmed by the identical 5/5 matrix column. LIMIT: the ledger never exercises lane_round != round, so key-field confusion is
untestable in principle against this rev.

## Control-fixture disclosure
Frozen fixture tips from the committed receipts (5e5562db..., 85e51e6f...) are not in the lane object store (`git cat-file -t`:
bad object). Control-row SHAPES were rebuilt at the measured tip from the receipt text; the committed `.out` receipts at
cb1ef10 remain the ground truth for what the frozen controls showed.

## Restoration evidence
- Mutants live only as separate scratch copies; nothing mutated in place.
- Pristine copy sha256 61ef1f56... identical before first run and after all 25 runs.
- Lane worktree `tools/round58-c2-counter.py` sha256 61ef1f56... = frozen content sha256, unchanged by this seat; no lane-tree writes outside `out/M09C2CounterMutants/`.
- Scratch root and all fixtures/tempdirs removed after receipts were copied out (27 receipt files).

## Receipts
`out/M09C2CounterMutants/receipts/` — 25 matrix runs `<counter>__<repo>.out` + `matrix-summary.txt`;
`out/M09C2CounterMutants/mutants/` — pristine + 4 mutant sources and `.diff`s.

Report: .ufo/waves/round-58/w1/out/M09C2CounterMutants.md
