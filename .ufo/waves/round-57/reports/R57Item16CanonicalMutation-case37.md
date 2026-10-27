# Case 37 — canonical row content mutation

**Axes:** calibration (counter falsification), operability (whether content-bound audit is actually executed). Read-only inspection of `tools/capability-repertoire-audit.py`, `SCORECARD.md`, and frozen controls; all mutation fixtures were temporary under `/fast/scratch/hyaku/kama-r57/R57Item16CanonicalMutation` and removed on exit. No tools installed.

## Reproduction and evidence

The current instrument is `python3 tools/capability-repertoire-audit.py --repo <root>` (or its `evaluate(root, None)` function). `evaluate` parses capability-shaped tables, finds the latest numbered canonical marker, compares only the set of canonical row names against the union of names in *all* capability tables, and checks that each canonical evidence cell contains at least one existing relative path. It does not bind the description/evidence identity to an independently expected canonical row. Frozen C2 control already documents no-op success (`controls/freeze.txt`: `noop_C2=met=True exit=0 despite skipping data`).

Case command: inline Python imported `tools/capability-repertoire-audit.py`, extracted canonical row/table using `canonical_line` from the evaluator, created temporary mutated `SCORECARD.md` copies and symlinked the lane's `corpus`, `tools`, `.ufo`, and `registry` for path existence, then called `evaluate(temp_root, None)`. Exact outcomes are in `R57Item16CanonicalMutation-case37.out`.

- Base: `exit=0 listed=11 observed=11 missing=0 unsubstantiated=0 met=true`.
- Delete one canonical row: `exit=1 listed=10 observed=11 missing=1 missing_names=[sources-registry] unsubstantiated=0 met=false`.
- Rename row identity: `exit=1 listed=11 observed=12 missing=1 missing_names=[sources-registry] unsubstantiated=0 met=false`.
- **Description-only canonical-row mutation:** `exit=0 listed=11 observed=11 missing=0 unsubstantiated=0 met=true` — false acceptance.
- **Replace evidence pointer with a different existing path** (`corpus/SOURCES.md` → `tools/capability-repertoire-audit.py`): `exit=0 listed=11 observed=11 missing=0 unsubstantiated=0 met=true` — false acceptance; mere path existence does not establish row evidence.
- Delete entire canonical table: `exit=0 listed=11 observed=11 missing=0 unsubstantiated=0 met=true`; fallback chooses the previous capability table as canonical. This is another counterexample: removing the latest canonical heading/table silently shifts authority rather than failing closed.

Code basis: `tools/capability-repertoire-audit.py:129-138` chooses highest marker then falls back to `caps[-1]` if no table follows it; `:141-149` only accumulates names and checks any path existence; `:151-160` computes met from missing names and unsubstantiated count. The direct content-mutation pass demonstrates that this detector is not actually content-bound.

## Smallest safe correction

Fail closed if the highest-numbered canonical marker has no following capability table (remove the `caps[-1]` fallback). For content binding, compare normalized canonical row content—including row name, description, evidence pointer and first-working round—to an independent immutable expected authority (e.g. frozen hash of the canonical rows, established before measurement). Do not derive the expected digest from the mutable `SCORECARD.md` under test. Add two positive mutation controls: description-only change and swap to a different existing evidence path; both must return nonzero. Keep row deletion/rename controls.

This is a calibration counterexample to content binding and an operability false-green for the audit's claimed behavior; it does not establish any serving/runtime capability or score movement.
