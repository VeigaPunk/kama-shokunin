# MutRedundantAll — PM07 bounded falsification

**Partial — assigned probe complete; `PM07-full-all-missing-gate` survived. Zero kill credit.** The pinned runner honestly reports survival; this probe does not establish a non-equivalent defect or falsify the amended local-object contract.

## Axes and scope

- Mutation applicability/compilation; named graded-row sensitivity including twin mismatch; isolation/exact-byte restoration; immutable oracle.
- Read the godspeed skill, operator RULES, preregistration, amendment 1, pre-inspection snapshot, and supplement 2 before the measurement.
- Production was read-only except these authorized report/evidence files. Own scratch: `/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll`.
- Detached scratch HEAD observed as `2e254a1763a9c08aa07fc53081287f506c447d84` after `git clone --no-hardlinks --no-checkout` and scratch-only checkout.
- Exactly one registered mutation was evaluated, on the pinned current grid. No other mutant, PM08, full suite, transport/execution payload, runtime, install, service/config mutation, or production source/index/object-store mutation was invoked. The pinned grid uses benign synthetic local fixtures; any local file-clone fixture setup is the unchanged grid's own setup.
- Every measurement subprocess inherited `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll`. Grid fixture roots and the disposable mutant were beneath that scratch.

## Registered mutant and expected detector

First inventory command, exit **0**, from scratch:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll python3 tests/report-audit/promisor-mutants.py --list
```

Observed exact registered ID: `PM07-full-all-missing-gate`; execution `grid`; expected unmet row prefixes `PG31`, `PG32`, `PG35`, `PG36`, `PG44`, `PG45`, `PG48`. The inventory itself explicitly allows redundancy/survival on a candidate whose traversal already starts at every present object.

At `tools/report-landing-audit.py:666`, the registered alternative 0 inserts exactly one behavior-bearing line:

```diff
     roots = present_roots(repo)
+    roots.append("--all")
```

The three registered regex alternatives matched **[1, 0, 0]**; alternative **0** applied; Python `compile` of the actual mutant succeeded. No grid, oracle, grader, expectation, or contract was edited.

Expected detector: the unmodified current `promisor-grid.py`, grading the live amended 47-cell manifest (original 44 unchanged plus 3 supplement cells). `promisor-mutants.py:530-537` recognizes graded `met == false` **or** `twin_equal == false` as a violated row. Its harness/CNE gates (`:509-527`, `:703-716`, `:764-784`) reject pristine failure, grid exit 2, leaks and timeouts rather than crediting a kill. This probe exercised the real PM07 run, not the runner's stub selftest.

## Exact measurement and outputs

The original `promisor-mutants.py` module's `main(argv)` was invoked through the Python tool, with this exact argument vector:

```text
--current /fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/tools/report-landing-audit.py
--grid /fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/tests/report-audit/promisor-grid.py
--arm current --grid-timeout 600 --only PM07-full-all-missing-gate --json
```

This was an in-process call of the original parser/entrypoint, **not a separate shell CLI execution**. An observational pass-through wrapper around its original `run_grid` recorded each real detector result and auditor hash; it returned the original result unchanged. No grading/result logic was substituted. Entrypoint return: **0**; stderr empty; exception none.

Actual detector command for all three phases, working directory `/home/vgpnk/Projects/shokunin`:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll /usr/bin/python /fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/tests/report-audit/promisor-grid.py --arm current --current AUDITOR --json
```

| Phase | Exact `AUDITOR` | Exit | Graded | Violations | Twin mismatches | Seconds |
|---|---|---:|---:|---:|---:|---:|
| Pristine | `/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/tools/report-landing-audit.py` | 0 | 47 | 0 | 0 | 4.437 |
| Mutated | `/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/promisor-mutants-amkbatw3/PM07-full-all-missing-gate.py` | 0 | 47 | 0 | 0 | 4.493 |
| Restored | `/fast/scratch/hyaku/kama-r24/falsify/MutRedundantAll/tools/report-landing-audit.py` | 0 | 47 | 0 | 0 | 4.731 |

Each phase: 20 cell exits 0, 13 exits 1, 14 expected exits 2; 32 rows with a comparable twin; zero tracebacks, timeouts, leaks or acquired objects. Expected cell-level unavailable-evidence exits 2 are not a runner/harness failure and earn no mutation kill by themselves. The same bounded detector was used on pristine, actual mutated, and restored bytes. There were no differing graded-row verdict documents, finding/token pairs, `met`, twin equality, or safety flags across those phases.

Actual runner output fields:

```json
{"pristine":"passed","mutants":1,"evaluated":1,"killed":0,"killed_ids":[],"surviving":["PM07-full-all-missing-gate"],"could_not_evaluate":[]}
```

The PM07 row has `status="survived"`, `grid_exit=0`, `failed_rows=[]`, `failed_row_detail=[]`, `unexpected_rows=[]`. Its `attributed=true` is vacuous over an empty failed-row set, **not** sensitivity evidence.

### Named-row finding/token pairs

All listed cells have **exit 0 / 0 / 0**, findings/tokens **[] / [] / []**, and `met=true` in pristine / mutated / restored:

| Exact graded row | Twin equality in all three phases |
|---|---|
| `PG31-missing-object-unselected-branch-promisor` | true |
| `PG32-missing-object-unselected-branch-plain` | true |
| `PG35-unused-missing-blob-promisor` | true |
| `PG36-unused-missing-blob-plain` | true |
| `PG44-missing-unused-tree-promisor` | true |
| `PG45-missing-unused-tree-plain` | true |
| `PG48-opaque-unused-tree-no-unresolved-token` | no twin registered |

The unchanged **ungraded** PG40 open row was also reported by the pinned detector: exit **1** in all phases, finding/token pairs `landed-unresolved / 0123456789abcdef0123456789abcdef01234567` and `unresolved-full-hash / 0123456789abcdef0123456789abcdef01234567`. It was not used for kill credit. Complete actual graded finding/token pairs are retained in the three phase JSON files.

The original unknown-from-metadata requirement remains **withdrawn/not achieved**, never relabelled passed. All phases retain the seven `withdrawn_original_failures`: PG22, PG23, PG24, PG28, PG30, PG34, PG41. Strong `names_any_of` grading was not relaxed. The manifest remained byte-identical.

## Hashes and exact restoration

| Bytes | SHA-256 before | SHA-256 after restored detector |
|---|---|---|
| Auditor | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | identical |
| Grid | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | identical |
| Expected manifest | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | identical |
| Mutation runner | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | identical |

Actual executed mutant SHA-256: `bfc79441cdbddf824049b56403770c0834a1b14f443011a3d00985353066bc9e`.

Every phase reports the same expected-manifest hash above and population hash `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, population size 47. The original auditor was never overwritten: the pinned runner generated the mutant as a disposable temporary sibling under the assigned scratch and removed it when its context closed. Exact canonical source byte equality was observed, the actual temporary mutant path was observed absent after cleanup, and the restored detector read the original auditor hash. Post-restored hashes of all four tracked files remain unchanged.

## Observed versus inferred; remaining limits

- **Observed:** one uniquely applicable/compiling mutation; pristine passed; mutant survived all 47 graded cells; restored passed; no named graded violation/twin mismatch or harness failure; exact hashes and disposable-mutant cleanup as above. This is a coverage/sensitivity finding: **PM07 contributes zero kills** here.
- **[INFERENCE]:** survival is consistent with `present_roots` (`tools/report-landing-audit.py:635-648`) already enumerating every locally present commit/tree/tag using `cat-file --batch-all-objects`, before the two missing-object walks. It is not proof of global equivalence, and no non-equivalence claim is made.
- No production source bug/minimal correction was established by this bounded probe. Do not reinterpret survival as permission to change the oracle or credit a kill.
- Unverified/out of scope: global equivalence outside this grid, adversarial/broken refs, other mutants, runner negative-control selftests, PM08 runtime behavior, transport/execution scenarios, the full historical suites, final source census, and Git 2.45 compatibility. Installed Git **2.56.0** and Python **3.14.8** were observed; no installation/update occurred. The inherited Git >=2.45 prerequisite remains open at L0. No serving or numeric-score increase is claimed.

## Files written

All small evidence artifacts are under the authorized absolute directory `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutRedundantAll/`:

- `probe-evidence.json`: exact argv, real detector commands/results, hashes, restoration evidence, complete returned documents.
- `measurement-summary.json`: per-phase exit/safety/twin counts, observed row comparisons, focused rows, post-restored hashes.
- `pristine.grid.json`, `mutated.grid.json`, `restored.grid.json`: complete normalized detector JSON documents.
- `pristine.grid.stderr`, `mutated.grid.stderr`, `restored.grid.stderr`: actual stderr, empty.
- `runner.stdout.json`, `runner.stderr`: actual entrypoint output and empty stderr.
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/MutRedundantAll.md`.

Report: .ufo/waves/round-24/falsify/advice/MutRedundantAll.md

Append-only scope clarification: “no runtime” above means no additional OMP/UFO runtime was invoked; the assigned Python detector was necessarily executed. “No service/config mutation” means no real service or operator/production configuration was changed; the unchanged grid necessarily writes configuration inside its disposable synthetic repositories.

Report: .ufo/waves/round-24/falsify/advice/MutRedundantAll.md
