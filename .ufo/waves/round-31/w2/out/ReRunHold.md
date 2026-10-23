# ReRunHold — scoped findings (advisory evidence for the L1)

Claim served: the round-30 hold — this round's additions must not break the round-30
self-assessment census (preregistration.json `hold_check`).

## What was run

Fresh `git clone` of the lane repo at `/tmp/kama-r31w2/ReRunHold/clone`, checked out at the
dispatch tip `382d11b2107d335705875da1a4d889b074bd6fa6`. Counter hash verified:

- `sha256sum .ufo/waves/round-30/count-c1.py` →
  `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` — byte-equal to the
  preregistration `hold_check` pin.

Counter run (cwd = clone root), exit 0, stderr empty, one stdout line verbatim:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True tip 382d11b2107d
```

Full receipt: `.ufo/waves/round-31/w2/out/ReRunHold/hold.json` (met True, unresolved 0,
false_corrections [], oracle_unbound 0, by_class C62 H13 N2 P12 Q44 T8).

## Comparison vs committed receipt `.ufo/waves/round-31/c1/hold-r30.out`

Not byte-identical. One field differs: `tip` — committed `0e6f8ed6891c` (round-31 base),
this run `382d11b2107d` (landing tip). All count fields are identical: statements 141,
extracted 69, oracle 72, bound 72, unbound 0, mismatched_at_base 13, append_only True,
valid_corrections 13, false_corrections 0, unresolved 0, met True.

## Finding

The round-30 hold still passes at the round-31 landing tip: `met True`, `unresolved 0`,
exit 0. Round-31's appended corrections section and other additions did not break the
round-30 census — append_only holds and the 13 base mismatches remain validly corrected.

## Limits

- Re-derives only the frozen counter's bounded check; not evidence about population
  completeness or the truth of the underlying statements.
- append_only is a SCORECARD.md byte-prefix test; in-place edits elsewhere are invisible.
- Comparison was against the `.out` wrapper's summary line; the base-run JSON receipt was
  not committed for a full JSON diff.
- No tooling installed or changed.

Raw receipts/logs: `.ufo/waves/round-31/w2/out/ReRunHold/` (`report.md`, `hold.json`,
`run.stdout`, `run.stderr`).

Report: .ufo/waves/round-31/w2/out/ReRunHold/report.md
