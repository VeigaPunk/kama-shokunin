# R57Item09ClaimFalsifier — distinct case 30 (independent test)

Assigned case: falsify the frozen round-57 C1 no-op control and its predicate.
This file is the separate evidence artifact; the seat report is
`.ufo/waves/round-57/w1/out/R57Item09ClaimFalsifier.md`, receipts are in
`.ufo/waves/round-57/ClaimFalsifier/09/`.

Axes: calibration (a claimed number re-derives or it does not), operability (the
instrument or control actually reads the target). No shared/source edits; all
target reads are committed bytes at tip `b89bdab2cc114735ec5d331c6c610134258f7864`.

## Runnable

```
$ python3 .ufo/waves/round-57/ClaimFalsifier/09/case30.py
case30 control-is-literal match=True exit=0 stdout='mismatches=0 maxN=46 met=True' receipt_line3='mismatches=0 maxN=46 met=True'
case30 control-target-invariant match=True exit=0 identical=True
case30 frozen-accepts-noop match=True exit=0 tip=5f7e1f5d... | present=1 roster_match=1 kills=1 controls=2 met=True
case30 frozen-accepts-deadcall-noop match=True exit=0 tip=fb1589f2... | present=1 roster_match=1 kills=1 controls=2 met=True
case30 numbers-not-46 match=True canon_round=49 canon_rows=11 maxN=56 head_round=56 lessons=43
case30 summary checks=5 matched=5 met=True
exit=0
```

`case30-run.out` holds that output. The harness ships its own inputs, so it does
not depend on the seat's scratch dir:

- `ClaimFalsifier/09/frozen-prereg-check.py` — tip bytes of
  `tools/round56-prereg-check.py` (the frozen checker under test).
- `ClaimFalsifier/09/fixtures/fixtureA` — isolated git repo (root verified as the
  fixture dir) with the tip's `preregistration.json` and a battery carrying the
  preregistered `ROSTER` literal, `main(): return 0`, executing no entry.
  Commit `5f7e1f5d35f70c7302371b6f443226378221380d`.
- `ClaimFalsifier/09/fixtures/fixtureB` — same, plus three `run(...)` calls under
  `if False:`. Commit `fb1589f2a7f1b8138cc7ed938b69637abd479b16`.

## What each check establishes

| Check | Observation | Falsifies |
|---|---|---|
| `control-is-literal` | the control's stdout equals line 3 of its own receipt and equals one literal | that `noop-c1.out` measures anything |
| `control-target-invariant` | same bytes with `--repo /nonexistent --tip deadbeef` from an empty cwd | that the control depends on the counter |
| `frozen-accepts-noop` | frozen checker: `met=True`, exit 0 on a no-op with the matching literal | the predicate's "rejects a no-op" half at the frozen bytes |
| `frozen-accepts-deadcall-noop` | frozen checker: `met=True`, exit 0 when the only trace of execution is unreachable calls | that roster *declaration* is distinguishable from roster *content* |
| `numbers-not-46` | canonical rows 11 (round 49), `maxN` 56 = SCORECARD head, 43 lessons, stale SCORECARD fact 42 | that 46 is a canonical row count or the current round maximum |

Supporting receipt, independent of the harness: `control-syscall-audit.txt`
(strace `openat,execve`) shows the control opens **0** target surfaces
(`SCORECARD`, `round42-selfdesc`, `round56-prereg`, `preregistration`,
`round56-env-leg`) and 2 opens of itself in 36 trace lines.

## Independent re-derivation of the numbers

```
$ python3 tools/round42-selfdesc-reconcile.py --repo LANE --tip b89bdab2...
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `... glob('corpus/lessons/*verifier-spotcheck.md')` no stdout line == '42' (exit 0)
exit=1
```

(`base-counter-at-tip.out`.) So the frozen base receipt is genuine, `maxN=56`
agrees with the SCORECARD head (`Latest measured round: 56`), the canonical table
is 11 rows, and `46` is the historical round-46 counter value quoted at
`SCORECARD.md:2676` — the exact string the frozen control prints.

## Boundary

The seat context labels this claim C1/calibration (stale canonical row count) and
`controls/freeze-amendment.txt` labels it C1/operability (prereg no-op defect).
This case tests both surfaces and resolves neither ordering. The underlying
no-op false green is real; the frozen control and the `46` target are not.

Report: .ufo/waves/round-57/reports/R57Item09ClaimFalsifier-case30.md
