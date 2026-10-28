# M16C2AttackNotobs — notobs-family falsification probe on the C2 counter (round 62, kama)

Seat: mutation-tester, wave r62/w1. Axis under attack: calibration (C2).
Instruments: `tools/round62-c2-counter.py` (sha256 `15d11f1c…`, byte-identical snapshot in receipts) and `registry/capability-claims-r62.tsv` (sha256 `6f8365c7…`), both at master `65d7cad0fce90e34de37527cde22e97b63b118bf` (spec-time tip). All mutation happened in scratch fixtures; lane bytes untouched (see Restoration).

## Method

- Fixture repo per variant, built from `git archive master` of the lane (tree byte-identical; registry fixture sha256 equals the lane blob's), committed with my seat identity inside the fixture only. Every counter run read REG/SCORECARD from the fixture tip, so verdicts are pinned to the frozen bytes even though lane master moved to `307466ca` mid-session.
- Two layers, same scoring code:
  1. **Stub layer** — the real `score()` and the real `controls()` mutant construction (module imported from the hash-verified snapshot), with only the executor stubbed green/sensitive. Valid because notobs rows never execute and the bound rows are byte-identical to pristine, whose live behavior the e2e baseline measures.
  2. **Live end-to-end** — the lane counter itself, sequential, on each fixture.
- Four mutants (hashes in `out/M16C2AttackNotobs/mutant-hashes.txt`):
  - **V1 `9dd015bb…`** every bound row's binding → `notobs` (the control-family-8 transform, at top level).
  - **V2 `f08be41a…`** the 6 caps sources-registry…instrument-agreement → `notobs`, no duplicates.
  - **V3 `850ac951…`** pristine 12 bound rows + 6 appended `notobs` rows for those same caps (dup-coverage).
  - **V4 `da0263d8…`** pristine 12 bound rows + 12 appended `notobs` rows (all-notobs + dup-coverage).

## Baseline (pristine) — FAILED, which reframes everything

Live e2e, rc=1, empty stderr:

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=8 canonical=62 controls_rejected=8/8 errors=0 met=False
```

Eight of twelve bound runs returned verdict≠recorded under concurrent wave load (all 12 patterns emitted, none dead — `mismatches=8` with `sensitive=12/12`), so the pristine predicate did not hold in my environment. Per my role: a baseline failure is inconclusive, not a killed mutant — live verdicts below are marked accordingly.

The stub layer explains *why 8/8 controls and `mismatches=0` cannot coexist*: with every run green, pristine scores `controls_rejected=7/8` and **control family `free` escapes** — its mutant registry keeps all 12 green bound rows; the appended free-command row is rejected into `err_list` only (`binding:sources-registry:free`), and the family-met check looks only at covered/mismatches/errors/dead/bound, all clean: `family free: met=True covered=12 mismatches=0 errors=0 dead=0`. Since top-level `met` requires `rejected == total`, **`met=True` is unreachable for any registry and any environment: a fully green registry rejects only 7/8; any red row forces `mismatches>0`.** The frozen C2 instrument is unsatisfiable as committed. (The only live run that shows `8/8` is one whose bound rows are already failing — controls reject the counter's own green baseline.)

## Variant verdicts (live e2e with the real counter; stub layer where marked)

**V1 all-notobs — REJECTED (deterministic; no execution involved).**
```
population=12 rows=12 covered=0/12 bound=0 eval_lines=0 sensitive=0/0 dead=0 mismatches=0 canonical=62 controls_rejected=8/8 errors=0 met=False   [rc=1]
```
Coverage never counts a notobs row; `covered=0/12` decides regardless of environment. Note the printed line says `errors=0` while stderr carries `notobs:<cap>` for all 12 rows — the printed `errors=` counts only structural parse errors (`parse_registry`), never row-level semantic errors.

**V2 some-notobs — REJECTED (deterministic at the coverage layer).**
```
population=12 rows=12 covered=6/12 bound=6 eval_lines=6 sensitive=6/6 dead=0 mismatches=6 canonical=62 controls_rejected=8/8 errors=0 met=False   [rc=1]
```
`covered=6/12 < 12` decides independent of the 6 bound rows' verdicts (coverage is verdict-independent in `score()`); the 6 `mismatches` are the environment-red rows shared with pristine.

**V3 some-notobs + dup bound rows — REJECTED as run, but the rejection is NOT attributable to the notobs rows (live inconclusive per failed baseline; scoring layer decisive).**
```
population=12 rows=18 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=8 canonical=62 controls_rejected=8/8 errors=0 met=False   [rc=1]
```
Coverage counting: 18 rows, 6 of them `notobs`, and **every met-relevant quantity is identical to pristine** — covered=12/12, bound=12, printed `errors=0` (the 6 notobs errors live only in `err_list`/stderr). The live `mismatches=8` is the same environment-red set pristine shows; the stub layer (all-green executor) scores V3 `covered=12/12 bound=12 mismatches=0 errors=0 dead=0 sensitive=12/12`, rejected only by the `free`-family escape at 7/8 — the identical defect pristine has. Had the instrument's `free` family been sound, V3 would print **met=True with 6 notobs rows in the registry**: an ACCEPTED falsification. Under the frozen counter it is formally REJECTED; the notobs family contributes nothing to that rejection.

**V4 all-notobs + dup bound rows — same verdict profile as V3.**
```
population=12 rows=24 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=8 canonical=62 controls_rejected=8/8 errors=0 met=False   [rc=1]
```
Stub layer: all met-relevant quantities green with 12 `notobs` rows present; `controls_rejected=7/8` via the shared `free` escape; 8/8 live rejection again masks via environment-red rows.

## Findings

1. **FALSIFIED (instrument defect): the C2 counter cannot ever report met=True.** `met` requires `controls_rejected=8/8` and `mismatches=0`; family `free` escapes exactly when the bound rows are all green (its injected row is demoted to `err_list`, which no met condition reads), so 8/8 implies some row is red, which implies `mismatches>0`. Empirical: pristine stub `controls_rejected=7/8` with `family free: met=True`; pristine live `met=False` with `mismatches=8`. Consistent with the lane's recorded "final C2 miss" at `10173704`.
2. **FALSIFIED (signal defect): notobs rows are invisible to the counter's printed scoring line.** `errors=` counts only `parse_registry` structural failures; 12 semantically invalid rows (V1) still print `errors=0`. A consumer of the one-line output cannot see that the registry is saturated with notobs rows.
3. **The notobs control does not generalize (coverage-counting hole).** Family 8 only pins the extreme "every bound row notobs". Any registry that keeps one valid bound row per cap tolerates arbitrary extra notobs rows: V3/V4 match pristine on covered/bound/mismatches/errors/dead. The honest rejection of V3/V4 under the frozen counter comes from finding 1, not from notobs handling.
4. Adjacent observation (outside notobs core, one line): `run_bound`'s sensitivity check is vacuous for red runs — `sensitive = not (pattern in mut and rc==0 and not dead)` makes every `rc!=0` run automatically "sensitive", hence `sensitive=12/12` alongside `mismatches=8`.

No variant achieved met=True under the frozen counter, so no variant is formally ACCEPTED; the falsification delivered is findings 1–3 against the instrument, grounded in the pristine baseline failure plus the execution-independent stub-layer proof.

## Restoration & provenance

- Lane `tools/round62-c2-counter.py` sha256 `15d11f1c…` and `registry/capability-claims-r62.tsv` sha256 `6f8365c7…` identical before/after (`out/M16C2AttackNotobs/{before,after}-hashes.txt`). I never mutated, committed, or staged lane bytes; fixtures and counter executions lived entirely under my scratch root.
- `SCORECARD.md` worktree bytes changed during my session (`49f330b8…` → `f28bfe41…`) and master advanced to `307466ca` — done by others (L1/integrator commits visible in log); my probes are pinned to the spec-time fixture tree of `65d7cad0`, so none of my outputs depend on those changes. The 8 pre-existing dirty worktree entries at session start were not mine.
- Bounds: no pacman transactions (no installs needed), no fleet-repo or sibling-lane contact, no registered consumer ports contacted, no processes killed; all live work went through the four blessed lane tools at the counter's chosen unregistered loopback ports, sequentially. Scratch root `/fast/scratch/hyaku/kama-r62/w/M16C2AttackNotobs` deleted after receipts were copied to `out/M16C2AttackNotobs/`.

Receipts (full copies): `driver.py`, `driver-stub.out`, `reg-*.tsv` ×4, `e2e-*.{out,err,rc}` ×5, `c2-counter-snapshot.py`, hash files — all under `.ufo/waves/round-62/w1/out/M16C2AttackNotobs/`.

Report: .ufo/waves/round-62/w1/M16C2AttackNotobs.md

Tally (decisive line, V3 — 6 notobs rows, dup coverage, live): population=12 rows=18 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=8 canonical=62 controls_rejected=8/8 errors=0 met=False
