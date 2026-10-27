# R05OtherScript — round 59 C1 receipt

**Axes:** operability (C1); calibration (C2, lowest assigned). This seat exercised only the C1 executable-routing control; it makes no C2 or S517/S518 discernment claim.

## Result

The frozen C1 battery rejects N16 (`N16-decoy-counter-call`) but does **not** establish executable-path binding. At the measured tip, the N16 `run()` first calls `python3 <TEST> --counter ... --expect ...`, then additionally calls `python3 other-script --counter ... --expect ...`. The checker records both calls and requires exactly one call containing `--counter` and `--expect`. Thus this N16 is rejected for the extra call, not because the checker compares the executable path to the leg's declared runner.

In the measured-tip checker, `fake_run` extracts `--counter` and `--expect` and synthesizes the observed result from the counter file; the per-leg predicate checks `len(calls) == 1` and presence of those two flags. It does not compare `argv[0]` (or another executable-path field) to the declared leg. Consequently, a **single-call replacement** with `python3 other-script --counter ... --expect ...` appears capable of satisfying the checker when the counter/expectation result matches. That replacement was not executed; it is a source-grounded inference, not a measured outcome.

## Evidence

Command run (measured tip and frozen counter):

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/R05OtherScript
```

`TMPDIR` was explicitly set to that scratch directory; the scratch directory was removed on command exit. Counter output:

```text
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
...
detail: N16-decoy-counter-call reject exit=1
```

The counter command exited 0. The other displayed aggregate counts were genuine `1/1`, benign `3/3`, no-ops rejected `16/16`, errors `0`.

Measured-tip source confirmation: `tools/round59-battery-outcome-check.py` has argv handling in `fake_run` (lines 59–76), then checks only exactly one call and the two flags (line 191); `tests/round59-battery-variants/N16-decoy-counter-call.py` calls the declared test runner and then the decoy (lines 37–40). LSP was unavailable (`xd://lsp` is not mounted), so this check used the measured-tip source and execution evidence rather than LSP semantic results.

## Verdict / residual risk

N16's frozen negative control is killed, but executable identity is not bound by the checker predicate. A one-call route to `other-script` remains an actionable path-binding gap under the frozen sentence (“routes its argv to `python3 other-script --counter` must not meet”). The exact one-call substitution was not separately run; do not count it as a passed/rejected control. No source, counter, fixture, or fleet files were changed; only this seat receipt was written.
