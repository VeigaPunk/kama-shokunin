# V02RosterOrigin — 2 controls + 1 kill: origin, and whether the constant is meaningful
Advisory leaf; no dispatch, no install, no lane/claim/counter/variant/SCORECARD change. C1 subject `tools/round58-battery-exec-check.py` @ tip `e4891d8` (sha256 `89ad4e5d…`), provenance r56 freeze `efc6b3ec`; bytes read via `git -C <lane> show <rev>:<path>`.
## Origin: the roster is a 1:1 projection of C1's three target legs
`preregistration.json` `claims.C2.predicate`: "…exactly equals the preregistered name/designation/
expected-outcome roster, **with one kill-designated mutant and two explicitly labeled controls**"; the
battery docstring names the same triple — red baseline, round-56 counter, one-change mutant.
| entry | C1 leg | why it must exist |
|---|---|---|
| `base-old-counter` control/`missed` | before | old must miss, else "detected" says nothing about the change |
| `round56-counter` positive-control/`detected` | after | the claim needs a positive |
| `m-drop-ldaudit` kill/`missed` | kill | C1's kill rule names one mutant; the after-leg must be load-bearing |
**2 = arity of {must-miss, must-detect}; 1 = arity of C1's one frozen mutant.** Both derive from the
claim's before → after → mutation form, but only in prose: the prereg sentence declares them, the
roster literal instantiates them, `met = … and kills == 1 and controls == 2` restates them as bare literals — the code computes and justifies neither.
## Evidence chain
- `tools/round56-prereg-check.py` @ `efc6b3ec` = `c7b0d787…`, already ending with the same literals;
  r57 adds only the syntactic `executed` walk → `dee6f922…`, byte-identical at base `2f53614` and
  freeze `dcd6947` (`git diff 2f53614 e4891d8 -- tools/round56-prereg-check.py | wc -l` → `0`).
- `round58-battery-exec-check.py` @ `e4891d8` keeps that line verbatim; only `executed` becomes
  execution-bound, and its docstring restates the constants rather than deriving them.
- `tests/round58-battery-variants/genuine.py` = `69b77a6a…` = `tools/round56-env-leg-battery.py`
  byte-for-byte, so the accepted object is the real battery, not a paraphrase.
## Both, separably: arity anchor (meaningful) vs cardinality proxy (magic)
Meaningful half: the only clause that survives a coordinated rewrite of both surfaces, because
`match` compares the battery literal to a file read at the same tip — r56 `R11C2Mutation` mutant B
proved it bites and `P7` reproduces that. Magic half: `controls` sums `control` and `positive-control`
into one bucket and ignores expected outcomes, so it cannot tell the bracket it stands for from a
count-conforming degenerate roster. Fixtures: `git -C <fixture> init -q`, toplevel asserted, committed, then `python3 checker-r58.py --repo <fixture> --tip HEAD`.
| probe | roster variant | exit | met |
|---|---|---|
| P0 | genuine battery + genuine prereg (sanity) | 0 | True |
| P1 | positive control expected `detected`→`missed`, both surfaces | 0 | **True** — bracket lost |
| P2 | `positive-control`→`control`, both surfaces | 0 | **True** — role lost |
| P3 | `run()` expected args inverted, literal + prereg untouched | 0 | **True** — legs assert the opposite |
| P4 | positive control deleted, both surfaces | 1 | False |
| P5 | kill re-designated `positive-control`, both surfaces | 1 | False |
| P6 | fourth entry designation `note`, both surfaces | 0 | **True** — size not pinned |
| P7 | kill→control both surfaces (r56 mutant B) | 1 | False |
Verdict: **derived quantities stated as literals** — meaningful provenance, magic implementation
(`==` unchanged through three rounds). The checked property is `len(controls) == 2`, not "controls
bracket the detector".
## What each finding attacks
- P4/P5/P7 attack `kills == 1 and controls == 2` and show it **does** bite where `match` cannot.
- P1/P2/P6 attack the same clause as under-specification: the accept-side analogue of r56
  `c2-noop-control.out` (why `match` alone was insufficient). P2 restates r56 `K05PredicateIdentity`'s
  known limit ("designations within the accepted control class are not killed"); P1/P6 are new.
- **P3 attacks the new checker's execution binding: survivor outside the 11 enumerated variants →
  LIMIT, not C1 credit** (freeze kill rule). It binds the label and a `--counter` invocation, never
  `run()`'s expected argument against `roster[label]["expected"]`, and discards the battery's
  aggregate result, so legs that would all fail in reality still score `met=True` — one level below
  the r56 defect C1-r58 repaired.
- Proposed for a later round: `{expected of control ∪ positive-control} == {"missed","detected"}`,
  `len(kills) == 1`, plus a call-site expected-to-roster binding. Freeze text unchanged.
## Receipts, confidence
`python3 probe.py` exit 0 (P0–P5, `probe.out`); `python3 probe2.py` exit 0 (P6–P7, `probe2.out`);
`sha256sum checker-r58.py` = `89ad4e5d…`; `TMPDIR=/fast/scratch/hyaku/kama-r58/V02RosterOrigin`,
removed after receipts were copied. High confidence on origin (prereg sentence, docstring and roster
agree; the three entries are exactly the three C1 legs) and on the probes (committed blobs at
`e4891d8`). Medium only on the label: keep it as the freeze's arity anchor, and re-derive it if a
later round wants it to certify the bracket rather than the count.
