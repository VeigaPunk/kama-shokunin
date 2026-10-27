# R57Item29ClaimFalsifier — distinct case 50 evidence

Separate evidence file for the assigned case 50: independently falsify the frozen C1 no-op control and
its predicate. Self-contained; every number here was produced by commands in this file, not copied
from another seat. Main report: `.ufo/waves/round-57/w1/out/R57Item29ClaimFalsifier.md`.

Scope: scratch only. Lane read via `git show`; fixture git repo created and committed only under
`/fast/scratch/hyaku/kama-r57/R57Item29ClaimFalsifier/` with `git rev-parse --show-toplevel` asserted
before each mutation. No lane/shared write, no commit, no tool install.

## Case statement under test

C1 predicate (frozen, `controls/freeze-amendment.txt`): "the measured checker rejects a no-op that
declares the matching roster but executes none, while the genuine battery roster remains accepted."
Frozen defect receipt: `.ufo/waves/round-56/measured/c2-noop-control.out` (a battery with the roster
literal and `main(): return 0` reached `met=True`, exit 0).

## Independent construction

Fixture repo (`fixture/`) carries exactly two committed files:
`.ufo/waves/round-56/preregistration.json` (genuine, blob at `b89bdab2`, sha256
`fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68`) and
`tools/round56-env-leg-battery.py` (the variant under test). Checkers are copied out of the lane:

```
$ git -C <lane> show b89bdab2...:tools/round56-prereg-check.py | sha256sum
c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853      # frozen, matches round-56 digest
$ git -C <lane> show 7b74e2f2...:tools/round56-prereg-check.py | sha256sum
dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced      # round-57 repair, unchanged at tip 8640e34c
```

Invocation per cell:

```
$ python3 checkers/repair-check.py --repo fixture --tip <variant_tip> --out receipts/<variant>.repair.out
$ python3 checkers/frozen-check.py --repo fixture --tip <variant_tip> --out receipts/<variant>.frozen.out
```

## Decisive cell — execution-free no-op that declares the roster

Variant `v3_dead_calls` (byte-identical copy at `measured/r57item29/variants/v3_dead_calls.py`):

```python
ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def run(label, counter, expected, out):
    return True


def main():
    if False:
        run("base-old-counter", None, "missed", None)
        run("round56-counter", None, "detected", None)
        run("m-drop-ldaudit", None, "missed", None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Running this file executes zero roster entries (`if False:`), performs no `LD_AUDIT` probe, and calls
no counter. The repair checker's result:

```
$ python3 checkers/repair-check.py --repo fixture --tip 187f97f78550bc37be17e36aaa06a34fbc7b1ab2 \
      --out receipts/v3_dead_calls.repair.out
tip=187f97f78550bc37be17e36aaa06a34fbc7b1ab2
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Rerun in the same harness produced the same two lines (`report.json` → `determinism.v3_dead_calls`).
The frozen checker gives the same green (`receipts/v3_dead_calls.frozen.out`), which is expected: it
never inspects call sites at all.

Two independent confirmations that execution is not what the counter sees:

- `v6_crash_before_calls`: `main()` raises `RuntimeError` *before* the three `run()` calls; the battery
  cannot execute — repair `met=True`, exit 0.
- `v7_outside_main`: the three `run()` calls sit in a module-level `if False:`; `main` returns 0 —
  repair `met=True`, exit 0. This also contradicts the lesson's wording that binding is "to calls in
  the battery's `main`": the check is `ast.walk(tree)` over the whole module
  (`tools/round56-prereg-check.py:61-76` at `7b74e2f2`).

## Controls (the case must be able to fail)

| control | expected | observed |
|---|---|---|
| the exact round-56 no-op (`v1_roster_only`: roster + `main(): return 0`) | repair rejects | `met=False`, exit 1 |
| roster with two of three labels declared (`v4_roster_plus_kill_call`) | repair rejects | `met=False`, exit 1 |
| genuine round-56 battery | repair accepts | `met=True`, exit 0 |
| frozen checker on `v1` (the defect itself) | accepts | `met=True`, exit 0 |
| behaviour-preserving keyword rewrite of the genuine battery (`v5_keyword_identical`) | should be accepted | repair **rejects**: `met=False`, exit 1 |

## Case-50 verdict

- The frozen defect reproduces independently: the frozen checker greens a roster-literal no-op
  (`v1`: `met=True`, exit 0) exactly as the round-56 receipt claims.
- The frozen C1 predicate is **falsified** against the measured repair: `v3`, `v6`, `v7` each declare
  the matching roster and execute none of it, and each returns `met=True`, exit 0.
- The repair is a partial fix with a second, opposite defect: a genuine battery refactored to keyword
  labels is rejected (`v5`).
- Smallest remediation is advisory: the check must observe execution (per-label receipt/exit from a
  run of the battery) or the predicate and the lesson's "cannot satisfy the counter" language must be
  restated as a declaration-only check. No shared file was edited by this seat.

Report: .ufo/waves/round-57/reports/R57Item29ClaimFalsifier-case50.md
