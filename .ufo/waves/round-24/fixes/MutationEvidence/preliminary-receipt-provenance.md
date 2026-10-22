# Provenance sidecar — the filed preliminary sensitivity receipt

**Annotated file:**
`build/out/MutationOracle/sensitivity-promisor-grid.json`
sha256 `a29cc01dc91e84da38d3aef6c05ae1db041d717f302d953c9dbf4e9034981f82`
(31251 bytes). **The annotated file is not modified by this sidecar.**

## What the receipt says about itself

* `"baseline_mode": true` — it was produced by the runner version that
  still carried the `--baseline` mode, a mode that the L1's static review
  removed from the shipped contract (a pristine candidate that does not
  meet the grid must be could-not-evaluate and must kill nothing).
* `"candidate"` / `"grid"`: the paths of the round-24 candidate auditor and
  the promisor grid as they stood at that moment — the candidate
  `b5a5ce8c579b2754054144d1f54843672f5f37da2ec8eaf0e419a684f338debdca`
  and the grid `d6aa4e74aa1f7dd56167dc8d7e2907642764ea67c8eaf0e419a684f338debdca`
  (the grid with the cross-repo fixture fix; the L1's later path-based
  grader loosening, `5e96fa60…`, was declined and is not what the receipt
  measured).
* `"pristine": "failed rc=1"`, five pristine cells unmet
  (`PG15`, `PG16`, `PG19`, `PG20`, `PG46`), nine mutants killed, one
  survivor (`PM07`), no could-not-evaluate.

## Honest status: unreproducible preliminary, no credit

**The exact producer of this receipt is not recoverable.** The pre-repair
runner (the one with `--baseline`) was never committed: the copy under
`build/out/MutationOracle/` was overwritten by the contract repair, and the
lane integrated the repaired runner (`6e0b9d62…`) in commit `ed1cc3a`. No
byte-exact copy of the producer exists in the repository, so the receipt
cannot be regenerated bit-for-bit from a retained producer.

Consequences, stated plainly:

* the receipt is an **unreproducible preliminary** observation;
* it is **not** a receipt of the shipped contract (its producer had the
  `--baseline` override that the shipped runner removed, and it predates
  the corrected PM08 static gate and the corrected PM11 gate);
* it carries **no credit** for any claim about the candidate;
* the numbers above are quoted **as the receipt's own report**, not as a
  measurement of the current candidate or of the shipped runner.

## What would re-credit the measurement

A fresh run of the shipped runner against a named candidate and grid, with
its receipt filed beside this sidecar:

```
python3 tests/report-audit/promisor-mutants.py \
        --current tools/report-landing-audit.py \
        --grid tests/report-audit/promisor-grid.py --json
```

The main agent owns that run (it is the full sweep, and wave 2 is still
active). Nothing in this sidecar or in
`../MutationEvidence/rationale.md` rewrites, recomputes or re-credits the
filed receipt.
