# ExecGatePopulation — round 34, wave 1

## Files changed

- Created `.ufo/waves/round-34/w1/out/ExecGatePopulation/gate-registry-check-widened.py` from `tools/gate-registry-check.py`.
- Created this report at `.ufo/waves/round-34/w1/out/ExecGatePopulation.md`.
- Did not edit `tools/gate-registry-check.py` or any registry file.

## Implementation and behavior

The only source change in the copy is the `COUNTER_RE` population rule. It now matches either `^\.ufo/waves/round-[^/]+/count-[^/]+\.py$` or `^tools/round[0-9]+-[A-Za-z0-9._-]+\.py$`. Registry detection, defect grading, output formatting, and exit-code logic are unchanged from the source.

Exact source diff:

```diff
-COUNTER_RE = re.compile(r"^\.ufo/waves/round-[^/]+/count-[^/]+\.py$")
+COUNTER_RE = re.compile(r"^\.ufo/waves/round-[^/]+/count-[^/]+\.py$|^tools/round[0-9]+-[A-Za-z0-9._-]+\.py$")
```

## Required evidence

### (a) Pinned revision `7c35289da5f4b94e062cd900eb086919e5094003`

Command:

```sh
python3 .ufo/waves/round-34/w1/out/ExecGatePopulation/gate-registry-check-widened.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 7c35289da5f4b94e062cd900eb086919e5094003
```

Output and exit code:

```text
unregistered tools/round33-claim-audit.py
unregistered tools/round33-gate-receipts.py
registered 10 unregistered 2 defective 0
EXIT_CODE=1
```

Both expected round-33 tools are now in the evaluated population and are reported as unregistered.

### (b) Working tree (no `--rev`)

Command:

```sh
python3 .ufo/waves/round-34/w1/out/ExecGatePopulation/gate-registry-check-widened.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
```

Output and exit code:

```text
unregistered tools/round33-claim-audit.py
unregistered tools/round33-gate-receipts.py
registered 10 unregistered 2 defective 0
EXIT_CODE=1
```

### Copy `--selftest`

Command:

```sh
python3 .ufo/waves/round-34/w1/out/ExecGatePopulation/gate-registry-check-widened.py --selftest
```

Output and exit code:

```text
PASS valid-row: exit=0 (want 0) line='registered 1 unregistered 0 defective 0' want-line='registered 1 unregistered 0 defective 0'
PASS thin-row: exit=1 (want 1) line='registered 1 unregistered 0 defective 3' want-line='defective .ufo/waves/round-98/count-selftest.py: thin-row'
PASS empty-exit-map: exit=1 (want 1) line='registered 1 unregistered 0 defective 1' want-line='defective .ufo/waves/round-98/count-selftest.py: empty-exit-map'
PASS missing-path: exit=1 (want 1) line='registered 1 unregistered 0 defective 1' want-line='defective .ufo/waves/round-98/count-selftest.py: missing-path:.ufo/waves/round-999/count-c999.py'
PASS prose-only: exit=1 (want 1) line='registered 0 unregistered 1 defective 0' want-line='unregistered .ufo/waves/round-98/count-selftest.py'
FAIL lane-tip 5c9ef1fe1938: exit=1 line='registered 10 unregistered 2 defective 0'
GATE_SELFTEST pass=5 fail=1
EXIT_CODE=1
```

The five hermetic fixture arms pass. The lane-tip arm fails because the two round-33 tools are still unregistered at the evaluated lane tip; this run does not claim the subsequent `registered 12 unregistered 0 defective 0` state.

## Do-nothing control

The untouched original gate was run at the same pinned revision. It does not include the round-33 tools in its population and therefore does not reach the widened gate's target count of 12 registered instruments.

```text
registered 10 unregistered 0 defective 0
EXIT_CODE=0
```

## Remaining risks and blockers

- The working-tree result is a point-in-time observation; the pinned-revision result is the reproducible baseline.
- The copy's lane-tip selftest remains failing until the separate registry-registration work lands. No registry update was made in this population-only seat.
- No blocker to the assigned population-rule change. No tools were installed, and no service, endpoint, model-quality, or consumer-health claim is made.
