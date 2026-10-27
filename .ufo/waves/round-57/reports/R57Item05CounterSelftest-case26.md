# R57Item05CounterSelftest — distinct case 26

Independent control run for the assigned counter-selftest case. Axes: operability and calibration. Scratch driver ran the frozen base counter and the literal no-op, asserted observed status/output, and was removed after the receipt was copied.

## Exact measured results

The preserved receipt `R57Item05CounterSelftest-case26.out` records:

1. Command: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864`
   - stdout summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`
   - detail says the calibration run has no stdout line equal to `42`.
   - exit 1.
2. Command: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/controls/c1-noop.py`
   - stdout: `mismatches=0 maxN=46 met=True`
   - exit 0.
   - The script only prints that literal. It does not inspect canonical data or execute a check; therefore a control harness must reject its claimed success.
3. Independent execution of the named count command, `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"`, produced `43`, exit 0.

The round-57 freeze amendment controls interpretation: the stale expected count is 42 versus observed 43. `maxN=56` is independently derived from the greatest `## Round N` heading; `46` in the no-op is fabricated output, not the expected value for that field. The no-op is a false-green attack; the base counter is red. This does not establish a shared repair.

## Runnable acceptance rule

A reusable selftest should execute a base-red case and a genuine positive case, then execute the no-op mutant. It must require the no-op to be rejected based on missing observed reads/execution/content binding; never infer validity from `met=True`, `mismatches=0`, or exit 0 alone. For calibration, independently run the named count command and check exact expected stdout `43`; a synthetic or mutated expected value must be rejected. Keep this check separate from `maxN` (56).

No source files were changed; no tools installed.

Report: .ufo/waves/round-57/reports/R57Item05CounterSelftest-case26.md