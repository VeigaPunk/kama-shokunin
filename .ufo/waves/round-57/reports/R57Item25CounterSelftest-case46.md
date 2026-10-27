# R57Item25CounterSelftest — distinct case 46

Axis: calibration. This evidence independently exercises the assigned expected-46 case against frozen base `b89bdab2cc114735ec5d331c6c610134258f7864`; it is separate from the no-op evidence file. A scratch-only Python driver ran:

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864
```

Exact stdout:

```text
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))` no stdout line == '42' (exit 0)
```

Observed process exit: `1`. Driver exit: `0`, emitted `case46=PASS mismatch detected and rejected`. Observed `maxN=56`, which is not the required 46; mismatch is nonzero and rejected, so the negative control detects the stale case as intended. This is not a claim that the counter is repaired. The frozen receipt `controls/base-c1.out` independently records the same result. Scratch directory was removed by an exit trap after copying the evidence into this report.

A separate live-HEAD invocation (not the frozen base) emitted `mismatches=0 maxN=56 met=True`, exit 0; target-bound evidence is the frozen-tip run above. No source files or controls were changed; no git/jj mutation, commit, push, install, or verification suite was run.
