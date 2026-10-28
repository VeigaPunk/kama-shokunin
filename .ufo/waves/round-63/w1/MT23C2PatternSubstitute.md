# MT23C2PatternSubstitute: attack on the C2 row/manifest binding

Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (freeze amendment 1).
Method: detached clones of the lane in scratch; each variant committed in its clone with the seat identity and scored by the unmutated `tools/round63-c2-counter.py` run from the clone's `tools/` path (`--repo <clone> --tip <commit> --work <per-run dir>`). The lane itself was not written to. Patches and raw stdout/stderr are in `out/MT23C2PatternSubstitute/`.
Tools: none installed or updated. Live tools run by the counter: kama-llamacpp-live, kama-ollama-live, kama-context-capacity (host-busy: foreign llama-server on the operator ports, not touched), and the selftests. Nothing killed, no registered port contacted.

## How verdicts are read
Every run prints `met=False`, including the unmutated baseline at the tip, because `selfdesc_mismatches=8`. The freeze keeps that at 8 on purpose until the L1 re-derives the SCORECARD head. I therefore judge each attack from the other fields. `met*` below means `met` computed with the selfdesc term excluded (covered = population, mismatches = 0, errors = 0, dead = 0, bound = population, controls_rejected = 12/12, sens_selftest = 4/4).

Baseline (unmutated, clone at tip), rc=1:
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
Baseline met* = True.

## The four requested attacks (registry variants, unmutated counter)

All four are KILLED. None survives.

### (a) pattern of one row replaced by `a` (sources-registry, pattern cell only)
Commit 2f8b35ab3b8c.
```
population=12 rows=12 covered=11/12 bound=11 eval_lines=11 sensitive=11/11 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=1 met=False
```
stderr: `error: pattern:sources-registry`; `note: baseline not met - control credit withheld (would be 10/12)`.
- Rejected by the error tag `pattern:` in `score()` (row pattern must equal the manifest pattern). The sources row is skipped before the live scorer, so `bound=11`: the substituted pattern is never used to grade anything.
- The control family whose expected tag is the same, `weak` (pattern cell mutated), is the family that names this check.
- Result: KILLED.

### (b) run template replaced by a different allowed-looking command (sources-registry run cell: `python3 -B %T/tools/...` instead of `python3 %T/tools/...`; same tool, would pass live)
Commit 5b9f88ed1113.
```
population=12 rows=12 covered=11/12 bound=11 eval_lines=11 sensitive=11/11 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=1 met=False
```
stderr: `error: run:sources-registry`; `note: baseline not met - control credit withheld (would be 9/12)`.
- Rejected by the error tag `run:` (exact string equality of the row's run cell against the manifest template). The altered command never executed (`bound=11`).
- No control family names `run`. This check is guarded only by the baseline gate. See counter mutant m1 below.
- Result: KILLED, by a check that no control family covers.

### (c) columns reordered
Two variants, both applied to the whole file (header and all 13 rows):
- c1: `quote` and `binding` swapped (cap stays first). Commit 8ac45a84d667.
```
population=12 rows=0 covered=0/12 bound=0 eval_lines=0 sensitive=0/0 dead=0 host_busy=0 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=1 met=False
```
stderr: `error: header`; `(would be 2/12)`. Every row is rejected because the header is not COLS. Rejected by the `header` error tag (`parse_registry`). KILLED.
- c2: `cap` and `quote` swapped (cap no longer first). Commit abee86a080c2.
  No metric line is printed. rc=1 and an uncaught traceback:
```
  File ".../tools/round63-c2-counter.py", line 397, in controls
    header = [l for l in lines if l.startswith('cap\t')][0]
IndexError: list index out of range
```
  The crash is reached at `main()` line 521, after the baseline has been scored. The counter has no error path for a header whose first column is not `cap`. This is KILLED by an uncaught exception, not by a named tag and not by a parseable receipt. It is a defect in the counter's failure reporting, not a survival.

### (d) tab smuggled into a note (sources note: `...selftest<TAB>is the shipped verifier...`)
Commit f619ebde778e.
```
population=12 rows=11 covered=11/12 bound=11 eval_lines=11 sensitive=11/11 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=1 met=False
```
stderr: `error: cols=9`; `(would be 7/12)`.
- Rejected by the error tag `cols=9` (the row splits into nine cells). The row is dropped silently from the rows count; `covered` drops to 11/12. KILLED.
- A tab in a note cannot yield eight cells: any extra tab is a separator. The only alternative is removing a separator, which shifts a column and is caught by the header, `unbound-cap`, or quote/verdict checks in the same way.

## Extra probes (outside the four, run because the four were killed)

### (e) `observed` cell blanked on all 12 rows, otherwise unchanged. SURVIVED.
Commit 15bd4b5f8668.
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
- Mechanism: `score()` compares `observed` only when non-empty (`if row['observed'] and row['observed'] not in (want_obs or '') and ...`). A blank self-recorded observation is never a mismatch. The `observed` control family forges a non-empty value, so it is caught; blank is not.
- The frozen predicate names the verdict, not `observed`. I am reporting the gap; whether it falsifies a clause of C2 is for the L1.

### (f) recorded verdict of `context-capacity-receipt` flipped from `host-busy` to `true`; live outcome is host-busy here (`host_busy=1`). SURVIVED.
Commit 790fe0479ad1.
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
- Mechanism: `ok = (outcome in declared and (outcome == rec or 'alt' in tpl))` (score lines 320–321). For any row that declares an alternative outcome, the recorded verdict is never compared. A self-assessment of `true` on a row whose observed outcome is `host-busy` is scored as zero mismatches.
- The frozen predicate's disjunction (`equals the recorded verdict or is one of the row's two declared outcomes`) admits this reading, so it is within the letter of the predicate. Under the item's rule (a SURVIVING variant is a falsification of C2) this counts, and it is the most significant finding of this seat. The conditional row's recorded verdict is not falsifiable by this counter.

## Counter mutants (recipe: committed mutated counter, scored from its clone path)

### m1: run-template equality check removed (counter lines 300–302, `CUT`), scored with registry (b). SURVIVED.
Commit 6fe17d36b6c5.
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
- Unmutated counter: (b) is KILLED by `run:`. With the check removed: `errors=0`, `covered=12/12`, `controls_rejected=12/12`. Nothing in the 12 families changes the run cell, and `run_bound()` always executes the manifest template, so the row's run cell becomes decorative. The `run` template binding is guarded only by the one comparison line. This is the strongest finding of the seat: the run binding has no control family.

### m2: pattern equality check removed (counter lines 303–305), scored with registry (a). KILLED.
Commit 715a6c2827cd.
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=11/12 errors=0 met=False
```
stderr: `control-escape: weak {'met': True, 'hit': False, 'tags': []}`.
- The `weak` family (the only family that expects the `pattern` tag) escapes, so the mutant is caught by control credit. The pattern check is guarded; the run check (m1) is not.

## Counter-level observations (code read; only c2 and m1/m2 exercised)
- The `run` equality line has no control family (m1). Suggested direction for the L1: add a `run` family, or derive `run` from the manifest and drop the cell.
- Alt rows ignore the recorded verdict (f). Suggested direction: on alt rows, require `rec == outcome` or report the mismatch, or drop the verdict cell for conditional rows.
- Blank `observed` skips the mismatch check (e). Suggested direction: treat a blank `observed` on a graded row as a mismatch.
- `controls()` IndexError on a header whose first column is not `cap` (c2). Suggested direction: return a `header` error tag instead of crashing so the receipt line is always printed.
- `checkout_tip()` returns an existing `work/tip` without checking it against `--tip` (code read at lines 479–481; not exercised). Reusing a `--work` directory across tips would score a stale tree. Each run here used a fresh work dir.
- The baseline is never `met` at this tip (selfdesc=8), as the freeze intends. The L1 must re-derive the SCORECARD head before any `met=True` line exists.

## Tally
- Requested attacks: 4 of 4 KILLED (a: `pattern:`, b: `run:`, c: `header` and an uncaught IndexError, d: `cols=9`). None survived.
- Extra registry probes: 2 SURVIVED (e blank observed; f alt-row recorded verdict).
- Counter mutants: m1 SURVIVED (run check, no family); m2 KILLED (pattern check, by `weak`).
- Baseline at tip: `covered=12/12 bound=12 mismatches=0 errors=0 controls_rejected=12/12 sens_selftest=4/4`, `met=False` only from `selfdesc_mismatches=8`.

Receipts: `.ufo/waves/round-63/w1/out/MT23C2PatternSubstitute/` (base, a–f, m1–m2 `.out`/`.err`; `mutant-*.patch`; `T-*.txt` commit ids).
