# K14FrozenTarget — claim/freeze comparison

Axes: operability (C1) and calibration (C2; assigned 7, lowest). Scope: falsification of frozen claims, not admission.

## C1 — operability, 8 → 8

**Frozen target (freeze.txt §§4–8):** at C1 measured tip `aca8d0067ea25627c5015c2193c843965148bc8e`, each named run/mutant leg's own `--expect` must map to that leg's actual `ld_audit` field/value and declared exit, with only that predicate determining pass/fail; mutant assertion must specifically check missed against detected and exit 1. Require genuine 3/3, negative controls rejected, zero evaluation errors. Kill on any genuine leg rejected, outcome-unbound control accepted, evaluation error, or omitted enumerated control.

**Measured evidence conflicts with that target:** the committed `c1-candidate.out` is for tip `494c165759a644a56ec81bb51a7837b028817d89`, not the frozen/measured tip. It reports `genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False`; genuine and all benign rewrites reject. Thus it cannot establish the frozen predicate and directly fails its acceptance requirements. Do not substitute the subsequent `c1-oldchecker-final.out`: it is measured at the intended `aca8…` tip, but says `genuine=1/1 benign=3/3 noop_rejected=13/16 errors=0 met=False`; N12-ignore-leg-result, N14-ignore-mutant-result, and N16-decoy-counter-call are accepted (exit 0), which independently violates the frozen kill rule. The old checker is a negative comparator, not evidence that the candidate meets.

Frozen checker/counter are not do-nothing controls: frozen C1 counter code enumerates genuine+benign and 16 no-op variants, and its `met` condition requires each run pass. The measured candidate's reported 16/16 rejection alone is insufficient because it rejects genuine/benign and its recorded tip is wrong. The exact expected C1 counter command is not present as an exercised receipt here; do not mark it passed. Existing receipt labels/control populations match the freeze's target, but that does not cure the wrong-tip result or the failed acceptance evidence.

## C2 — calibration, 7 → 7

**Frozen target (freeze.txt §§11–15):** at measured tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35`, remove literal outside-closure count and pinned fleet revision from the calibration row; derive lane spotcheck count from committed lane tree and closure verdict from named fleet ref; pointer/token/count and including round must agree with highest numbered lane spotcheck/current matching fleet closure. Frozen counter must fail base, pass measured tip while binding exact lane tip and resolved fleet revision, and reject each field-changing control while preserving real S517/S518 admit/reject records. Missing external verdict or inability to evaluate kills claim; freeze expressly forbids narrowing for unavailable r58 evidence.

**Measured evidence:** `c2-base.out` identifies base tip `8f7f58cd161f2b7dfa1709450c3ae79599c12833`, fleet `c071f0dea9d00d944690534ff8461653eb94df66`, `rows=44 mismatches=3 met=False` (literal count, pinned revision, count command). Its `.exit` is `1`. `c2-after-current-head.out` identifies measured lane tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` and current fleet HEAD `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`, reports `maxN=57 manifest=rejected-honest-stop`, `rows=44 mismatches=0 met=True`; `.exit` is `0`. This supports base-fail/current-tip pass for the clauses actually counted, with resolved revision printed.

However this receipt does **not** establish the full frozen predicate: no evidence in these measured outputs demonstrates isolated rejection of each field mutation or that genuine S517 and S518 admit/reject records were retained/validated. The freeze explicitly says external S517/S518 check is not recorded, and no r58 closure exists (latest recorded closure r57); accordingly current r57 `rejected-honest-stop` is the verdict actually present, not evidence of r58 or S517/S518 discernment. Treat no external discernment progress as claimed. Counter's aggregate `mismatches=0` is not itself proof of the omitted control matrix or external records.

## Post-freeze / scope finding

The freeze states frozen-before-results and fixes both predicates, counters, kill rules and fixtures. Available control receipts show C1 candidate output at the wrong commit and old-checker comparator at intended commit; the latter's 3 accepted no-ops falsify its own target. C2 base/current receipts align with frozen base/measured inputs and do not show a do-nothing pass, but demonstrate only aggregate row checks and current extant closure, not the expressly required per-field controls and external records. No evidence here shows that the frozen target itself was changed; no post-freeze edit is inferred from these outputs. Do not narrow either target or treat a passing aggregate as satisfying the unmet clauses.

## Exact evidence / commands

Read-only evidence inspected (no counter rerun or fixture mutation):
- `cat` equivalent via file reads: `.../controls/freeze.txt` §§4–15.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --stat --oneline --no-renames aca8d0067ea25627c5015c2193c843965148bc8e` → `round-59: score counterfactual leg failures`, one checker file, 9 insertions/5 deletions.
- Same `git show --stat` for `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` → checker plus C1 control receipts, 50 insertions/3 deletions.
- Read `controls/c1-candidate.out` (tip `494c165…`, met false) and `controls/c1-oldchecker-final.out` (tip `aca8…`, 13/16 no-ops rejected, met false).
- Read `controls/c2-base.out` + `.exit` (met false, exit 1), and `controls/c2-after-current-head.out` + `.exit` (met true, exit 0).
- Read committed `tools/round59-c1-counter.py`, `tools/round59-c2-counter.py`, and `tools/round59-battery-outcome-check.py` to compare measured checker/counter semantics with freeze. No command was run in this seat; no unrun check is represented as passed.

Smallest safe correction: preserve the freeze unchanged; obtain an exact frozen C1 counter receipt at the specified tip, and complete/record the C2 frozen field-mutant and S517/S518 evidence before claiming the full C2 predicate. On the evidence at hand, C1 fails and C2 is only partially evidenced; no score/admission decision is made by this seat.
