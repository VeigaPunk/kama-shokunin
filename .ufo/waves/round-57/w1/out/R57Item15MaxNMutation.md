# R57Item15MaxNMutation — maxN target mutation and no-op escape

Seat: `R57Item15MaxNMutation` (round57/MaxNMutation/15), leaf seat. Axes: calibration + operability. Distinct case: 36.

## Finding

The frozen `46` is not the round-42 counter's expected maxN. `tools/round42-selfdesc-reconcile.py` defines `maxN` as the greatest `## Round (\\d+)` heading in `SCORECARD.md`, and derives it from the committed tree. At post-repair tip `7b74e2f2515a6f598918488fa5144658ff29925f`, the counter reports `maxN=56`, `mismatches=0`, `met=True`, exit 0. The frozen no-op receipt instead declares `maxN=46` while reading neither the canonical table nor self-description (`controls/noop-c2.out`: `canonical_table_reads=0`, `self_description_reads=0`, `mismatches=0 maxN=46 met=True`, exit 0). Thus the 46 constant is not supported by the counter's maxN definition.

Case 36 renamed the nine `## Round N` headings for N=47,48,49,50,51,52,53,55,56 to `## Archived entry N` in an isolated fixture based on the post-repair tip; this changes the derived maxN from 56 to 46 without editing the head banner or planned section. The real counter detects this inconsistent target mutation: `maxN=46`, `mismatches=2`, `met=False`, exit 1 (banner and planned checks). The no-op replay produced the same `mismatches=0 maxN=46 met=True`, exit 0 before and after the mutation. It escapes the mutation; it does not detect it.

## Evidence and exact runs

All fixture mutations were in `/fast/scratch/hyaku/kama-r57/R57Item15MaxNMutation/fixture`; its `git rev-parse --show-toplevel` was asserted equal to that fixture path before checkout/commit. No lane source, refs, or index were changed. The isolated mutation commit was `b1a79db2389b6ddb134890dad943980c8b3ce853`.

Counter baseline:

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo <fixture> --tip 7b74e2f2515a6f598918488fa5144658ff29925f
 tip=7b74e2f2515a6f598918488fa5144658ff29925f
 r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True
exit=0
```

Counter after case-36 mutation:

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo <fixture> --tip b1a79db2389b6ddb134890dad943980c8b3ce853
 tip=b1a79db2389b6ddb134890dad943980c8b3ce853
 r41=0 banner=1 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=46 met=False
 detail: banner: head lacks 'Latest measured round: 46'
 detail: planned: section does not name '### Planned (round 47)'
exit=1
```

Frozen no-op reproduction, using the previously read `controls/c1-noop.py` behavior (`print("mismatches=0 maxN=46 met=True")`):

```text
$ python3 c1-noop-replay.py  # baseline and mutated fixture
mismatches=0 maxN=46 met=True
exit=0
```

Both no-op outputs are byte-identical (`cmp` exit 0). The replay script and four receipts are in `w1/out/R57Item15MaxNMutation/`. The historical frozen receipt `measured/noop-c1.out` now records a different checker (`round56-prereg-check.py`) rejecting its no-op battery fixture (`met=False`, exit 1); that C1 check is roster-call-site validation, not evidence about maxN. The old `controls/c1-noop.py` file disappeared from the live working tree during concurrent wave work, so this report labels its executed form a replay of the exact source content observed earlier, not a fresh run of a currently present lane file. `controls/noop-c2.out` remains the recorded no-op evidence for maxN/self-description non-reads.

## Scope and gaps

- This independently tests case 36; it does not assess canonical capability-row content binding (assigned to a different seat).
- No LSP device is mounted in the available tool inventory (`xd://lsp` returned “No such tool”); definition evidence was read directly from the counter implementation. No callers are changed.
- No tools were installed or updated.

Report: .ufo/waves/round-57/w1/out/R57Item15MaxNMutation.md
Case-36 evidence: .ufo/waves/round-57/reports/R57Item15MaxNMutation-case36.md
