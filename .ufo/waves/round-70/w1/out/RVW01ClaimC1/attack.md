# RVW01ClaimC1 — C1 attack (advisory, not admission)

Axes: operability + calibration; judged axis calibration, frozen score 7, saturation threshold 8, nudge inactive. Source of assignment: controls/freeze.txt. All measured source bytes came from `git show 6035e952c2521999e192d6f236331f265ac98392:<path>`; no index/working-tree source was executed. No tracked lane files changed.

## Findings by severity

### High: five closure-only arms do not protect the other fact families

At base `tools/round42-selfdesc-reconcile.py:235-259`, the five arms plant only closure pointer / including-round changes. The evaluator at lines 389-390 aggregates ten fact counters plus closure_ptr. A scratch-only one-line mutation, immediately before aggregation,

```python
    c = dict.fromkeys(c, 0)
```

erases all non-closure counters while leaving the real closure checker intact. Its selftest nevertheless prints:

```text
SELFDESC_SELFTEST newest=69 planted_stale=57 ok:closure_ptr=1,mismatches=0 stale_ptr:closure_ptr=0,mismatches=1 stale_both:closure_ptr=0,mismatches=1 stale_incl:closure_ptr=0,mismatches=1 no_ptr:closure_ptr=0,mismatches=1 pass=5 fail=0
```

Exit 0. On the untouched base record the same mutant still fails the counter (`closure_ptr=0 mismatches=1 maxN=69 met=False`, exit 1). Thus this is demonstrated selftest blindness, NOT a demonstrated acceptance of the full frozen target. Every planted variant retains the exact required +1 delta despite erasure of nine actual non-closure mismatches.

`tools/round65-host-census.py:36-107` still has 22 members, including the reconciler at lines 59-62; that member runs the selftest. The mutation changes no registry entry. Therefore registration count 22 plus these five arms are insufficient to enforce the prose prohibition on weakened fact checks. They do catch missing registration and closure-delta breakage; they do not prove all checks remain operative. Full census execution was not performed by this seat.

### High: base standing record and run facts are red, as frozen

The unmodified committed counter reproduces exactly:

```text
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False
```

Exit 1. Breakdown (full exact detail lines in evidence.txt):

| Family | Count | Observed failed fact |
|---|---:|---|
| r41 | 1 | `python3 tools/gate-registry-check.py --selftest` does not emit exact `GATE_SELFTEST pass=7 fail=0`; exit 1 |
| r41 | 1 | `python3 tools/round69-newest-closure-counter.py --since-round 63` does not emit exact `NEWEST_CLOSURE … row_current=true`; exit 2 |
| banner | 1 | lacks `Latest measured round: 69` |
| planned | 1 | lacks section reference `### Planned (round 70)` |
| retired | 1 | lacks `15 capabilities` |
| province | 1 | lacks `tools/round67-worktree-landing-check.py` |
| province | 1 | lacks `tools/round68-receipt-pointer-audit.py` |
| province | 1 | lacks `registry/receipt-pointer-resolutions.tsv` |
| province | 1 | lacks `tools/round69-newest-closure-counter.py` |
| closure_ptr | 1 | pointer names round 68, newest tree closure is round 69 |

All other family counters are zero. Closure prints a boolean: `closure_ptr=0` contributes ONE mismatch, explaining why the displayed failing counters sum to nine while mismatches=10.

The canonical imported run path is `tools/round41-scorecard-reconcile.py:131-140,183-195`: it exports `git archive <tip>` into a temporary directory, extracts it, and executes recorded commands with that export as cwd. It is committed tree data, not the live lane. A plain archive does not carry Git repository metadata. The landing repair must restore actual execution of Git-dependent facts, not delete their run assertions. This seat observed the two failing run results above; it did not implement or test a proposed harness repair.

## Base selftest: exactly the ok arm fails

```text
SELFDESC_SELFTEST newest=69 planted_stale=57 ok:closure_ptr=1,mismatches=9 stale_ptr:closure_ptr=0,mismatches=10 stale_both:closure_ptr=0,mismatches=10 stale_incl:closure_ptr=0,mismatches=10 no_ptr:closure_ptr=0,mismatches=10 pass=4 fail=1
```

Exit 1. `ok` repairs only the pointer and including-round text in its scratch fixture; nine other mismatches remain. The assertion `ok_cp == 1 and ok_m == 0` fails because ok_m=9. Each of the four negative arms correctly has cp=0 and exactly ok_m+1=10; those four assertions pass. This is not five failed arms, and the +1-delta mechanism is not itself broken at base.

## Cheapest fake green, scored against the frozen requirements

Scratch-only mutation of evaluator line 389:

```diff
-    mism = sum(c.values()) + (0 if cp else 1)
+    mism = 0
```

No record or run harness repair. It produces:

```text
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=0 maxN=69 met=True
```

Exit 0, with all ten failure details still printed. It fools a consumer checking only `mismatches=0`/exit 0. It does NOT satisfy the full frozen target: closure_ptr remains 0, maxN remains 69, and its selftest is `pass=1 fail=4`, exit 1 (all five mismatch values become zero). The original fixed committed counter, independently scored on the identical untouched base tree, stays at mismatches=10 / exit 1. Mutant execution must not be represented as execution of frozen original bytes.

## What closure must observe

1. At the actual measured landing SHA, re-run committed counter bytes and its selftest; retain exact `tip=...`, complete family line, details, exit codes. Require closure_ptr=1, mismatches=0, maxN=70, met=True AND pass=5 fail=0; an isolated green token is insufficient.
2. Review the landed diff against the frozen evaluator to establish that no check or aggregation was removed/weakened. A content pin may protect a separately frozen oracle, but legitimate harness repair means blanket byte equality of every tool is not the whole criterion.
3. Add/run planted violations for non-closure families, scored by an independent expected result. At minimum the counter-erasure mutant above must be rejected by a control that expects the original nonzero family values on a known bad fixture. The existing five arms cannot establish that. On a fully reconciled positive tree, simply disabling an already-zero check need not change output; plant a violation first, then disable its check and compare.
4. Keep census membership=22 with this arm registered, but do not treat the census population as independent C1 proof. This seat measured AST membership, not a real census green line.

No production patch is recommended by this attack leaf. L1 must land genuine standing-record and run-harness repairs, then retain independent mutation/closure evidence. Reproduction and exact outputs are adjacent in reproduce.py and evidence.txt.

## Residual risk / verification gaps

No landing diff or landing tip was reviewed; no admission/verdict is issued. LSP device was unavailable (`xd://lsp`: No such tool); file/line inspection is textual, not semantic-reference proof. No runtime endpoint, resume path, rerouting, or saturation gain was exercised or claimed. No tools were installed. Scratch was deleted by an EXIT trap after the final evidence run.
