# Case 38 — counter selftest, never-reads instrument

## Mutant and bounded detector

Target examined: `tools/round42-selfdesc-reconcile.py` (pristine SHA-256 `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`). Its CLI has `--repo`, `--tip`, and `--out`; it has no `--selftest` mode. Frozen controls are `.ufo/waves/round-57/controls/{base-c1.out,noop-c1.out,noop-c2.out}`. The no-op literal is `mismatches=0 maxN=46 met=True`, exit 0; `.ufo/waves/round-57/controls/no-canonical/SCORECARD.md` is the named negative fixture.

Proposed mutant M38 is an instrument that skips all target-content reads and emits the summary literal `r41=0 ... mismatches=0 maxN=46 met=True` with exit 0. It was represented by scratch driver `never-reads.py`, accepting the counter CLI fixture names (`--repo`, `--tip`, `--out`) but not inspecting them. The working counter source was kept pristine: the available `edit` operation could not address the absolute scratch copy, and this seat did not modify shared source. Therefore this is a black-box no-op instrument probe, not a byte-level mutation of the counter; see verdict limitation below.

Same behavioral probe: invoke the instrument at frozen `--tip b89bdab2cc114735ec5d331c6c610134258f7864` against the lane repository, then against `controls/no-canonical`; compare summary and exit, and rerun pristine after restoration. This tests whether literal-only acceptance can distinguish reading from non-reading.

## Actual outputs

Pristine command:
`python3 /fast/scratch/hyaku/kama-r57/R57Item17CounterSelftestMutation/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864`

```text
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))` no stdout line == '42' (exit 0)
exit=1
```

Mutant on lane target:
```text
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=46 met=True
exit=0
```

Same mutant on named negative fixture `controls/no-canonical`:
```text
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=46 met=True
exit=0
```

Restored pristine invocation reproduced the exact pristine output above, exit 1. Scratch-copy digest before/after: `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0` both; receipt files are in `receipts/` beside this report.

## Verdict

Baseline detector is valid against the frozen base: its `mismatches=1 maxN=56 met=False`, exit 1 agrees with `controls/base-c1.out`. Against an output-literal-only detector, M38 survives: it emits the frozen no-op expected literal and its result is invariant across the lane and `no-canonical/SCORECARD.md` target. This is a coverage finding: output literal and fixture names alone do not establish target-content reads. A detector must assert a differential result on a changed target (or otherwise observe actual reads).

Mutation-protocol limitation: because only a new scratch driver could be created and the existing absolute scratch script was not editable with the provided editor, no behavior-bearing line in the counter was changed. Thus survival is established for the literal-only acceptance surface, not for an implemented counter selftest; no counter selftest exists in the inspected CLI. Restoration evidence is byte equality of pristine scratch copy and its `restored.py` copy; source tree was never edited.

Installs/updates: none.

Report: .ufo/waves/round-57/w1/out/R57Item17CounterSelftestMutation/case-38-counter-selftest-never-reads.md