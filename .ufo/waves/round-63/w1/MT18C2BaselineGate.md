# MT18C2BaselineGate: baseline gate removed from C2 control credit

Seat: MT18C2BaselineGate (mutation-tester, leaf, calibration). Item: remove the baseline gate in a clone of
`tools/round63-c2-counter.py`, run at a tip whose registry carries one wrong recorded verdict, and check
whether the mutant prints `controls_rejected=12/12` under a failing baseline while the unmutated prints
`0/12`, and whether `met` stays False in both. Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Advisory findings only; no verdict on C2.

## Setup (what was run, and where)

- Scratch: `/fast/scratch/hyaku/kama-r63/w/MT18C2BaselineGate` (deleted before yield). Clone:
  `git clone -q --shared <lane> <scratch>/clone`, toplevel asserted, detached checkout of 03a6a1d8.
- Every seat-made commit lives only in the scratch clone (identity `seat`, never the lane). The lane was
  read-only: `git show`, `git rev-parse`, `git status`, and the counter (which reads blobs and writes only
  to `--work`). No lane file, index, or jj state was written.
- Live items inside the counter (llama-server lifecycle on an unregistered loopback port, ollama
  lifecycle, context-capacity K1 probe) ran as the counter launches them. Foreign operator llama-servers
  were up (`host_busy=1`, the context-capacity row returned `host-not-idle-before-K1`, which is its declared
  alternative).
- Tools installed/updated: none. Interpreter: python3 3.14.8 (host). Git: host git.
- Work dirs were kept distinct per tip (`checkout_tip` reuses an existing `work/tip`, so one work dir per
  tip).

## Commits in the scratch clone (SHAs are not reachable after cleanup; patches are archived)

| label | SHA | content |
|---|---|---|
| clean (03a6a1d8) | 03a6a1d850902a66a13dfad33f89cf3a8b759a09 | lane tip, unchanged |
| T1 | 6e87f70fc99fd67d3c21e817c9e580977bc66565 | planted mismatch only (registry) |
| T2 | a115b83de50b1793d76ddf38e39f249e315d8b70 | T1 + mutant 1 (baseline gate removed from credit) |
| M0 | 8ff6142c97779eba5cba10a82d71cfa5b1835847 | clean registry + mutant 1 (control for T2) |
| T3 | a6b3c78d5981a01681a95c861b68fbec93a0457f | T1 + mutant 1 + mutant 2 (baseline also removed from met) |
| T4 | dbd462f8003c72a6ebd2ffff7ea817f10f909767 | T3 + reconciler forced to 0 (PROBE, not a measurement) |
| T5 | 786b47e5547cd60ab142efb10a7f82ef480f66bf | T1 + unmutated counter + reconciler forced to 0 (PROBE) |

**The planted wrong recorded verdict.** `score()` counts a mismatch when a recorded verdict disagrees with the live outcome (`ok` false) or when the recorded `observed` cell is neither in the pattern nor in the run output. A verdict-column edit cannot reach the first path from the registry alone at this tip: `true`→`false` raises `verdict-value`, and `true`→`host-busy` on a non-declared row raises `hostbusy-not-declared`; both are errors raised before execution, not mismatches. Reaching a verdict mismatch needs a live run that fails, which needs a changed tool; I did not do that. So I used the observed path: row `pin-watch` observed set to `selftest pass=8 fail=1` (live output `selftest pass=9 fail=0`), verdict column left `true`. This is one wrong recorded observation and the only registry-only route to one mismatch.
Registry diff: one line (`out/MT18C2BaselineGate/plant-registry.patch`).

**Mutant 1 (the item).** `tools/round63-c2-counter.py` line 527:
`credited = rejected if baseline else 0` → `credited = rejected  # MUTANT: baseline gate removed`
(`met` keeps its `baseline and` conjunct, as the item asks: only control credit is un-gated).

## Results (counter output, verbatim)

Unmutated lane counter (`<lane>/tools/round63-c2-counter.py`), clean tip 03a6a1d8 (control):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```

Unmutated lane counter, planted tip T1 (the item's "unmutated"):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=1 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False
note: baseline not met - control credit withheld (would be 12/12)
```

Mutant 1 (clone counter run from `<clone>/tools/`), planted tip T2 (the item's "mutated"):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=1 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
note: baseline not met - control credit withheld (would be 12/12)
```

Mutant 1, clean-registry tip M0 (control for the mutant, no planted defect):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
Identical to the unmutated clean run: the mutant changes nothing while the baseline is met.

Answers to the item's two questions:
1. Mutant prints `controls_rejected=12/12` under a failing baseline (`mismatches=1`, `is_met` False); the
   unmutated prints `0/12` on the same tip. Confirmed.
2. `met` is False in both (T1 and T2). The reason is the retained `baseline and` conjunct in `met`, and
   separately `selfdesc_mismatches=8` (`selfdesc == 0` is also a conjunct). The gate removal alone does not
   move `met`. See the mutant-2 probe below for what happens when the conjunct goes too.

## Why this is the round-62 vacuity (and what is and is not the same)

Round 62 (`tools/round62-c2-counter.py`, not amended, retained as the honest-stop record):
- `controls()` counts a control family as rejected when its re-score is "not met" (`if not met: rejected += 1`,
  in `round62-c2-counter.py`'s `controls()`). Nothing requires the failure to be the one the control names.
- `main()` makes `met` include `rejected == total` with no baseline gate (`met = (...)` in `main()`).
- So any failing baseline (any registry that is not met) makes every family "rejected". The credit is
  inherited from the baseline's defect, not from the control's mutation. That is the vacuity.

Round 63 added two defences, and the item's mutant removes the one that matters for this case:
- Named-check requirement (`hit = (not met) and expect[name] in tags`). This stops "any failure counts".
- Baseline gate (`credited = rejected if baseline else 0`). This stops inherited credit. The item removes it.

With the gate gone, the named-check alone is not enough at this fixture, because the planted baseline
mismatch leaks into every re-score:
- `controls()` at T1 (probe, `out/probe-T1.txt`): all 12 families `hit=True`. The `observed` family's
  only tag is `mismatch`, and the probe shows the `mismatch` tag comes from the baseline alone: an
  identity (no-op) registry at T1 scores `mismatches 1`, so an unmutated `observed` control would also be
  credited. Its named check is satisfied by the planted row, not by its own forged cells.
- The other 11 families each produce their own named tag (`covered`, `unbound-cap`, `binding`,
  `verdict-value`, `quote`, `pattern`, `hostbusy-not-declared`, `dup-row`, `canonical rows...`, plus the
  inherited `mismatch`). So the 12/12 is not a false rejection on its face, but it carries no information
  about whether the control set discriminates: credit does not depend on the control's effect.

So the item's mutant is the r62 expression again, not by the same code path: r62 had no named-check and no
gate; r63 mutant 1 keeps the named-check and drops the gate. Under a failing baseline the printed credit is
meaningless. The lane counter (unmutated) is not affected: its gate stops this, which is why it prints 0/12.

## Kill verdicts (recipe rule: KILLED if the pair prints met=False or a named control escapes)

- **Mutant 1 (credit gate removed): KILLED, narrowly.** Under the literal rule the pair prints met=False
  (T1 and T2), so it is "killed". But the kill is carried by `baseline` in `met`, which mutant 1 leaves in
  place. The only observable effect of the defect is the printed `controls_rejected` field (0/12 → 12/12).
  No control family and no `met` test detects it; a reader of `met` alone would see nothing wrong.
- **Mutant 2 (probe: baseline conjunct also removed from `met`).** Printed at T3 (real reconciler, 8):
  `controls_rejected=12/12 ... met=False`. That is false only because `selfdesc_mismatches=8` is still a
  conjunct. Probe T4 forces the reconciler to 0 (the value the L1 will re-derive after measurement; forced
  here, not measured):
  ```
  population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=1 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True
  ```
  `met=True` with `mismatches=1` present: **SURVIVED.** The unmutated counter under the same forced 0 (probe
  T5) prints `... selfdesc_mismatches=0 ... controls_rejected=0/12 errors=0 met=False`, so the unmutated
  counter is still correct; only the mutant survives.

## Coverage finding (a defect of the control set, not of the lane's counter)

No one of the 12 control families targets the top-level `met` formula. Each control mutates a registry or
canonical list and re-scores it; none removes the `baseline` conjunct from `met`, and none plants a
mismatch with `selfdesc` at 0. So mutant 2 survives the control set whenever `selfdesc_mismatches=0` and
the registry carries a mismatch. This is exactly the state the L1 will create when it re-derives the
SCORECARD head after measurement. The current counter is only protected by the `baseline` conjunct, which
has no control family of its own. Mutant 2 is the surviving mutant to report prominently.

Also noted (cosmetic, mutant-only): the `note: baseline not met - control credit withheld` line is printed
from `baseline`, not from `credited`, so under mutant 1 it says credit is withheld while the printed
`controls_rejected` is 12/12. The unmutated counter's note is accurate.

## Receipts (all under out/MT18C2BaselineGate/)

- `clean-unmutated.txt`, `M0-mutant.txt`: clean tip, unmutated and mutant-1 counter lines.
- `T1-unmutated.txt`: unmutated counter at the planted tip.
- `T2-mutant.txt`: mutant 1 at the planted tip (the item's run).
- `T3-mutant2.txt`: mutant 2 at the planted tip, reconciler real (8).
- `T4-probe-mutant2-sd0.txt`: mutant 2 with reconciler forced to 0 (met=True, SURVIVED).
- `T5-probe-unmut-sd0.txt`: unmutated with reconciler forced to 0 (met=False).
- `probe-T1.txt` and `probe.py`: per-family detail at T1, plus the identity (no-op) re-score check.
- `plant-registry.patch`, `mutant1-credit-gate.patch`, `mutant2-probe-met-conjunct.patch`,
  `probe-selfdesc0-T4.patch`, `probe-selfdesc0-unmutated-T5.patch`: the exact diffs.
- `commits.txt`: label to SHA map. `*.err` files: stderr of each run.

## Out-of-scope observations (not acted on)

- The lane's working tree has other seats' uncommitted edits (`PROVINCE.md`, `corpus/SOURCES.md`,
  `corpus/knowledge/completion-request-plane.md`, untracked `.ufo/waves/round-63/source/`, `w1.ready`). Not
  mine; not touched.
- Round 62's `controls()` (no named check, no gate) is the same family of defect as the item's mutant; it
  is retained unamended per the freeze. Nothing to add beyond the explanation above.

## Handoff to the L1 (calibration)

1. Item result: mutant 1 prints `controls_rejected=12/12` under the planted failing baseline; unmutated
   prints `0/12`; `met=False` in both (the `baseline` conjunct and `selfdesc=8` both hold it down).
2. Surviving mutant 2 (baseline conjunct out of `met`) is detected only while `selfdesc_mismatches` is
   nonzero. Once the head is re-derived to 0, a planted mismatch would print `met=True`. Suggest the L1
   add a control family that removes the `baseline` conjunct from `met` and scores a mismatch-planted tip
   with the reconciler at 0 (the reconciler result must be injectable for the control, or the control
   counts only when the failure is `mismatch`), and re-run the sensitivity of that family before the
   measured tip is treated as final. Decision on whether to adopt is the L1's.
3. The `note` line should read from `credited`, not `baseline` (cosmetic).

Tally (the item's one-line output, unmutated lane counter at the planted tip, plus the mutant):
`population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=1 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` (unmutated)
`population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=1 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` (mutant 1)
