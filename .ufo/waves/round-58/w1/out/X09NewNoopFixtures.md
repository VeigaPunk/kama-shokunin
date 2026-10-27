# X09NewNoopFixtures — six seat-authored no-op batteries vs the round-58 C1 checker

Basis: freeze `dcd69473dd7e33b316e2ba238a48e5119a6cd809`, measured tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`,
checker blob sha256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`. Lane tree untouched; all writes are
under `.ufo/waves/round-58/w1/out/X09NewNoopFixtures/` plus scratch `/fast/scratch/hyaku/kama-r58/X09NewNoopFixtures`.

Baseline reproduction (frozen counter, exit 0): `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`
(`receipts-baseline-counter.out`). The 11 enumerated variants still behave as frozen; nothing below changes that.

## Method
Six variants derived by single-anchor edits from the freeze genuine battery (`make-new-noops.py`, every anchor asserted
unique), ROSTER literal intact, `run` / `assert_mutant_breaks_detection` names and the `--counter` argv preserved.
Each scored exactly as `tools/round58-c1-counter.py` scores: one throwaway fixture per candidate in scratch holding
preregistration + the three side files from the tip and the candidate at `tools/round56-env-leg-battery.py`
(`git init -q`, toplevel verified equal to the fixture, throwaway identity), then
`python3 <checker> --repo <fixture> --tip HEAD` (0=accept, 1=reject). Driver: `run-new-noops.py` (`receipts-new-noops.json`).

## Verdicts (checker at the measured tip)
| variant | checker | real `main()` rc | verification actually lost |
|---|---|---|---|
| X12-verdict-discarded | accept | 0 | `run` returns True after writing the receipt, before any field/exit comparison; returns True on a failing leg where genuine returns False |
| X13-legs-copied-positive | accept | 0 | base-control and kill legs run the positive control (`base-c1=detected`, `m-drop-ldaudit=detected`): two of three roster receipts are copies |
| X14-mutant-assert-unmutated | accept | 1 | the mutant is built but the positive-target assert runs the unmutated counter; target receipt `ld_audit=detected`, i.e. SURVIVED |
| X15-exit-hardcoded | accept | 0 | `return 0` replaces `0 if all(results) else 1`: rc 0 with every leg failing |
| X16-comparator-always-true | accept | 1 | `exact_field_match` returns True; the battery's own `comparator-selftest` prints `accepted=True -> fail` and it still passes |
| X18-receipt-forged | accept | 0 | receipts synthesised from `expected` without reading the counter's stdout; receipt bytes and exit identical to genuine |
| X17-subprocess-rebound (negative control) | **reject** | n/a | rebinding `subprocess.run` starves the harness recorder: `legs=0/3`, `counter=[0,0,0,0]` |

So 6/6 seat no-ops are accepted; the one variant that breaks the invocation shape is rejected.

## Sharpest evidence (`receipts-harness-frames.out`)
`--harness` frames for X12, X13, X14, X15, X16, X18 are **identical to genuine**:
`labels=['base-old-counter','round56-counter','m-drop-ldaudit',None] sub=[1,1,1,1] counter=[1,1,1,1] error=None`.
The recorded rows are `fn/label/sub/counter` only — no returncode, no assertion outcome, no receipt bytes — so an
always-passing, an always-failing (X14, rc 1), a hardcoded-exit (X15) and a forged-receipt (X18) battery are
indistinguishable to the predicate. X17 differs (`counter=[0,0,0,0]`) and is the only rejection.

## Limit statement (for the L1; not C1 credit, no predicate change proposed)
C1-r58 is call-shape-only: a battery passes if each roster label reaches a `run` frame that issues one `--counter`
subprocess, plus one mutant-assert invocation with one subprocess. The 11 enumerated variants remove the *shape*
(dead code, guards, rebound `run`, uninvoked `main`, empty loop). The six above keep the shape and remove the
*meaning* — verdict discarded, legs rerouted, kill leg unmutated, exit hardcoded, comparator vacuous, receipts forged.
Because the harness answers every invocation with the same canned `ld_audit=detected / rc 0`, outcome-sensitive
assertions cannot be observed at all; only a counter that returns *varying* bytes per invocation, plus receipt-content
and exit-code checks of the battery itself, would separate these. That is a round-59 predicate question, not a
round-58 defect.

## Artifacts (all under `.ufo/waves/round-58/w1/out/X09NewNoopFixtures/`)
`genuine.py` (freeze blob), `round58-battery-exec-check.py` (tip blob), `variants/X12..X18.py` (7 files),
`make-new-noops.py`, `run-new-noops.py`, `probe-semantics.py`, `probe-main-shape.py`, `probe-real-main.py`,
`receipts-baseline-counter.{out,console}`, `receipts-new-noops.json`, `receipts-semantic-probe.out`,
`receipts-main-shape.out`, `receipts-real-main.out`, `receipts-harness-frames.out`.

## Risks
- Probing imports X17, which rebinds the shared `subprocess.run` at import; every probe snapshots and restores it, so
  X17's probe rows show harness-free behaviour. X17's verdict is the driver's child-process measurement, not the probe.
- Fixtures were committed only inside scratch with a throwaway identity, after asserting the fixture toplevel; scratch
  was removed after receipts were copied out. No git/jj mutation ran in the lane or fleet root. No tool was installed
  (pacman untouched).
