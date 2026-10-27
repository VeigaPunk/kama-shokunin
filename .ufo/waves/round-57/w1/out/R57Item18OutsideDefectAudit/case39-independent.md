# R57Item18OutsideDefectAudit — distinct case 39, independent evidence file

Seat: R57Item18OutsideDefectAudit (`round57/OutsideDefectAudit/18`). This file is the required
**separate evidence file** for case 39: the assigned case tested independently, with its own clone,
its own fixtures and its own pass/fail predicate. It does not reuse sibling receipts as evidence.

Case 39 question: **is the round-56 non-author routed defect 2 closed at the tree — i.e. does a
roster-literal/no-op harness now fail the calibration counter, and is SCORECARD/SHONEN disagreement
tested?** Secondarily, does an audit-tool-free re-derivation confirm the routed defect 4 state?

Measured tip for the fixture matrix: `8640e34c` (counter blob `dee6f922…`); independent binding
check tip: `8a7f1976…` (the lane moved; see the main report's tip note).

## Independence

- Clone: `git clone --no-hardlinks <lane> /fast/scratch/hyaku/kama-r57/R57Item18OutsideDefectAudit/clone`;
  the only mutation was inside that clone, and `git -C <clone> rev-parse --show-toplevel` was asserted
  equal to the clone path before every commit. No lane ref, index or worktree byte was written.
- Fixtures built from scratch from the preregistered roster literal, not from any sibling seat's
  fixture. The two counter versions under test are blobs extracted from lane history
  (`b89bdab2:tools/round56-prereg-check.py`, sha256 `c7b0d787…`; `8640e34:…`, sha256 `dee6f922…`),
  preserved as `receipts/prereg-check-{pre,post}-repair.py`.
- Sibling receipt `measured/noop-c1.out` was read before this test ran, but no figure below is taken
  from it; the plain-no-op row is this seat's own run against this seat's own fixture.

## Predicate

Routed defect 2 is **closed** only if both clauses hold:
(a) every matching-roster harness that executes no battery entry returns `met=False` (nonzero exit);
(b) the counter reads SCORECARD and SHONEN and fails on their disagreement.

## Fixture matrix (each fixture keeps the exact preregistered ROSTER literal)

| Fixture | battery content | pre-repair (`c7b0d787…`) | post-repair (`dee6f922…`) |
|---|---|---|---|
| genuine | real battery, three `run(...)` calls in `main()` | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 |
| v1 plain no-op | no call expressions; `main(): return 0` | `met=True` exit 0 | **`met=False` exit 1** |
| v2 dead-function | `run(...)`×2 + `assert_mutant_breaks_detection(...)` inside an uncalled `_never_called()`; `main(): return 0` | `met=True` exit 0 | **`met=True` exit 0** |
| v3 unreachable | the same three calls under `if False:` inside `main()` | `met=True` exit 0 | **`met=True` exit 0** |
| v5 self-assessment deleted | genuine battery; `SCORECARD.md` and `SHONEN.md` deleted from the tip | — | **`met=True` exit 0** |

Exact post-repair output for the two surviving no-ops:

```
$ python3 receipts/prereg-check-post-repair.py --repo <clone> --tip b317fd8cd47e2b8b9a9a7621b4678789ed69beed
tip=b317fd8cd47e2b8b9a9a7621b4678789ed69beed
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
$ python3 receipts/prereg-check-post-repair.py --repo <clone> --tip e08a2eef32069c88b0e77c7bfedbddd1834c505c
tip=e08a2eef32069c88b0e77c7bfedbddd1834c505c
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Runtime proof that v2 executes nothing: `python3 receipts/fixture-v2-dead-function-calls.py` prints
nothing and exits 0 (no receipt directory is created), yet the counter still reports `met=True`.

Cause, read from the counter source: lines 61–71 build `invoked` from `ast.walk(tree)` over the whole
module, so any string-literal call site counts regardless of reachability or execution.

## Verdict for case 39

- Clause (a) is **false**: v1 is killed, but v2 and v3 — both matching-roster harnesses that execute
  no battery entry — return `met=True`, exit 0. The routed requirement "a roster literal/no-op
  harness must fail" holds only for the narrowest no-op shape.
- Clause (b) is **false**: v5 deletes both self-assessment surfaces and the counter is unchanged
  (`met=True`, exit 0); the counter contains no SCORECARD/SHONEN read.
- Therefore routed defect 2 is **not closed**. The plain-no-op kill is a real partial improvement and
  is credited as such; it is not the executed-entry binding the closure asked for.

## Independent corroboration of the routed defect 4 state (different method)

Instead of the append-only audit tool, resolve each `registry/append-only-contract.tsv`
`declared_at <path>:<line>` at tip and test whether that line contains the word `append-only`:

```
$ python3 receipts/case39-binding-check.py   # embedded in this case's run, tip 8a7f1976
SCORECARD.md         corpus/README.md:761   has_append_only=False  "  context-capacity rows' scope already excludes."
corpus/QUALITY.md    corpus/README.md:761   has_append_only=False  "  context-capacity rows' scope already excludes."
corpus/README.md     corpus/README.md:761   has_append_only=False  "  context-capacity rows' scope already excludes."
corpus/lessons/*.md  corpus/README.md:1239  has_append_only=False  "- Carried over unchanged and not re-measured here: the b11906 ledger population at"
lines_without_append_only 4
```

The other six rows resolve to lines that do contain `append-only`. This reproduces the audit's
`bad_declarations=4` set exactly by an independent path, without invoking `tools/append-only-audit.py`.
The lessons declaration actually sits at `corpus/README.md:1245`; the 761 pointer is stale for three
rows. So the routed defect 4 state ("invalid declared_at bindings") is confirmed, not repaired.

## Limits

- Fixtures live only in the scratch clone; their exact bytes and the driver are preserved under
  `receipts/` (`fixture-v1-plain-noop.py`, `fixture-v2-dead-function-calls.py`,
  `fixture-v3-if-false-calls.py`, `fixture-v5-genuine-battery.py`, `drive.py`,
  `prereg-check-pre-repair.py`, `prereg-check-post-repair.py`, `fixture-results.json`).
- This is a behaviour test, not a verdict on admission, scoring or the lane's honesty; the SCORECARD
  §Round 57 disclosure ("checks the call-site inventory in the committed battery AST") is accurate
  about the implementation.
- No tool installation; no shared write; scratch removed after the receipts were copied here.

Report: .ufo/waves/round-57/w1/out/R57Item18OutsideDefectAudit/case39-independent.md
