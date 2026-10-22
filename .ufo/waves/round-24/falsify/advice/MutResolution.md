# MutResolution — scoped mutation sensitivity

**Holds for the assigned resolution probes.** Both registered mutants were killed, each only by its named graded rows. This is not an integration/admission judgment or a higher numeric score.

Axes: **calibration** (credit only attributable behavioral violations), **coverage** (second-repository resolution and bare full-hash type handling), and **operability** (unique applicable source match, compiling variants, bounded offline execution, exact-byte restoration).

## Revision, oracle, isolation

- Detached scratch HEAD observed: `2e254a1763a9c08aa07fc53081287f506c447d84`.
- Scratch: `/fast/scratch/hyaku/kama-r24/falsify/MutResolution`.
- Read preregistration, amendment 1, before-inspection snapshot, and supplement 2. The original metadata-implies-unknown expectation remains **withdrawn/not achieved**, never relabelled passed. The amended local-object contract is the graded authority.
- Fixed population: 47 graded cells; population SHA-256 `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`. The additional PG40 observation is open/ungraded and supplies no kill credit.
- Strong `names_any_of` grading was unchanged. No path-based relaxation, manifest edit, production-source edit, sibling edit, transport payload, or repository-program payload was used. No subagents were dispatched.
- Runtime observed: `git version 2.56.0`; `Python 3.14.8`. No installations or updates.

### Source and oracle SHA-256

The following four values were observed both before and after the mutation run, unchanged:

| Path in scratch | Before = after |
|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |

Pinned registration hashes, measured in scratch:

- `preregistration.json`: `6dde0d72343c9b8e64ec6e3ae4c9b382dfa3daaf9d0f6afd3f274cfac30e844c`
- `oracle-amendment-1.json`: `930b087a218f880a55c4507b7f11309eae130e2b5dd2111e27d5653b39c8f82f`
- `oracle-snapshot-before-inspection.json`: `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e`
- `oracle-supplement-2.json`: `4600a8c3951d26b68ee2562d5967cecfe9b00d66443ac10e6d371956e5d34368`

## Commands and actual results

Unless otherwise indicated, cwd was the absolute scratch path above.

### Clone and exact base

Executed from `/home/vgpnk/Projects/shokunin`, exit **0**:

```sh
mkdir -p /fast/scratch/hyaku/kama-r24/falsify && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/falsify/MutResolution && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution git -C /fast/scratch/hyaku/kama-r24/falsify/MutResolution checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84 && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution git -C /fast/scratch/hyaku/kama-r24/falsify/MutResolution rev-parse HEAD
```

Output named the detached target exactly. Bootstrap variance: the clone command used the parent scratch directory as TMPDIR before the named clone existed; the destination and all detector temporaries were inside the named scratch. No external temporary-file census was performed.

### Resolve IDs before selecting

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution python3 tests/report-audit/promisor-mutants.py --list
```

Exit **0**. Exact registered selections were `PM05-ignore-second-repo` (expected PG26/PG27) and `PM09-peel-bare-full-hash-lookup` (expected PG38/PG39). No invented selectors.

### Static anchors

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json
```

Exit **0**. This CLI statically enumerates the inventory, but executes no grid/mutant. For PM05, both fallback alternatives have one match of the same lookup-loop pattern; the runner selects alternative **0**, not both. For PM09, alternative **0** has exactly one literal match. Both selected variants compile.

The smallest applied changes are:

- PM05, auditor line 211: `for store in stores:` → `for store in stores[:1]:` within `lookup`.
- PM09, auditor line 475: `full = lookup(stores, full_tokens)` → `full = lookup(stores, full_tokens, "^{commit}")`.

A separate **static-only**, bytecode-write-disabled reproduction used the pinned runner's `apply_mutation` and `compiles`, exit **0**, empty stderr. Its exact `python3 -c` argument and output are retained in `static-evidence.json`. Reconstructed variant SHA-256:

- PM05: `7d72089f721d7fae723dbe8ee25ce0fce29b869dc9c56439b2734ac3a851b537`
- PM09: `7ae25010bac4705aa987b296d26b5aa91e3647f7e7ae68f9879f782f8d3428bc`

These are deterministic reconstructed variant hashes, **not separately captured hashes of the deleted executed temporary files**.

### Assigned behavioral measurement

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution python3 tests/report-audit/promisor-mutants.py --only PM05-ignore-second-repo --only PM09-peel-bare-full-hash-lookup --arm current --grid-timeout 300 --json
```

Exit **0**, reported wall time **14.67 s**. The runner first ran the pristine current grid, then only these two generated variants against the same unmodified grid. Actual top-level output: `pristine="passed"`, `mutants=2`, `evaluated=2`, `killed=2`, `surviving=[]`, `could_not_evaluate=[]`.

| Mutant | Only violated graded cells | Actual auditor exit | Expected exit | Actual finding kinds | Verdict |
|---|---|---:|---:|---|---|
| PM05 | PG26-cross-repo-found-promisor; PG27-cross-repo-found-plain | 1 each | 0 each | `landed-unresolved`, `unresolved-full-hash` | killed; attributed=true; unexpected_rows=[] |
| PM09 | PG38-wrong-type-citation-plain; PG39-wrong-type-citation-promisor | 1 each | 1 each | `landed-unresolved`, `unresolved-full-hash` rather than only `landed-unresolved` | killed; attributed=true; unexpected_rows=[] |

Both mutant grid subprocesses exited **1**, identifying those graded violations; neither was a whole-grid could-not-evaluate. The four failed-row details show `twin_equal=true`, empty stderr tails, and no acquired lane/fleet objects. PM09 demonstrates sensitivity to an **extra finding**, not merely to exit-code changes.

### Finding/token pairs and observation boundary

The mutation runner preserves failed-row kinds but drops each row's raw `defects` token list. Therefore the kinds and exits above are **directly observed**; the mutant token association below is **[INFERENCE] from the pinned fixture/source**, not a claim of retained raw mutant-token capture:

- PM05, PG26/PG27: `(landed-unresolved, $fleet_commit)` and `(unresolved-full-hash, $fleet_commit)`. The fixture explicitly appends the fleet-only initial commit. Static SHA-1 Git-object construction from its fixed tree, author/email, timestamp 1900, and message derives `$fleet_commit = f723c76c41609df00704d93c29bd44408dcbdd2e`; construction bytes are retained in `static-evidence.json`.
- PM09, PG38/PG39: `(landed-unresolved, $blob)` and the erroneous additional `(unresolved-full-hash, $blob)`, where `$blob = 56d7b323865c731da81e0225cf109d66f0480919`. That blob token and the correct single `(landed-unresolved, token)` pair are **directly observed in the restored grid**.

### Restoration detector

The runner writes variants only under its own `TemporaryDirectory`; it never overwrites the candidate. Thus restoration means the original bytes were continuously retained, not a best-effort inverse patch. After the run, a glob for scratch `promisor-mutants-*` found none, and the four source/manifest hashes above were unchanged.

The same behavioral detector was explicitly rerun on those retained/restored bytes:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution python3 tests/report-audit/promisor-grid.py --arm current --current tools/report-landing-audit.py --json --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutResolution/restored-grid
```

Exit **0**, reported wall time **5.03 s**. Actual result: **47 graded, 0 violations, 0 twin mismatches, 0 timeouts, 0 harness leaks, 0 tracebacks**. Auditor hash and immutable expectation hash match the before values. PG26/27 return clean exit 0 with no defects; PG38/39 return exit 1 with exactly the expected blob `landed-unresolved` pair. The seven original-view failures remain explicitly filed as `withdrawn_original_failures`, not successes of the withdrawn expectation.

Before/after hash command, both exit **0**:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutResolution sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py tests/report-audit/promisor-grid-expectations.json tests/report-audit/promisor-mutants.py
```

## Detector semantics and limits

- Static source inspection: `violated_rows` credits only graded rows with `met is False` **or** `twin_equal is False`; the actual grid contains policy/control graded rows. `run_grid` does not flatten open rows into kill evidence.
- A nonzero pristine run, whole-grid exit 2, leak, timeout, nonapplying mutation, or compilation failure yields no kill. Those rejection branches were inspected, not independently fault-injected in this assignment. No such condition occurred in the observed probes.
- Neither assigned mutant caused a twin mismatch. The twin-mismatch inclusion branch is statically verified, **not dynamically exercised by this pair**.
- PM08 was never behaviorally executed. Its presence in the static anchor inventory is not a kill. No other mutant was behaviorally selected. PM07 survival/equivalence is untested here and no non-equivalence claim is made.
- The executed temporary mutant files and full raw mutant per-case JSON were not retained by the stock runner. Reconstructed hashes and inferred token associations are qualified above; `mutants-output.json` retains the runner's actual exposed result fields.
- No source defect or minimal production correction was established by this scoped experiment. No live-serving capability, arbitrary-repository safety, or global closure is claimed. The inherited Git >=2.45 prerequisite remains open; execution here used Git 2.56.0 only.

## Files written

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/MutResolution.md`
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutResolution/mutants-output.json`
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutResolution/static-evidence.json`
4. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutResolution/restored-grid/population.json`
5. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutResolution/restored-grid/candidate.json`

Report: .ufo/waves/round-24/falsify/advice/MutResolution.md
