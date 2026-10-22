# MutOverRefusal — PARTIAL: sensitivity holds; expected-row attribution falsified

## Scope and axes

Assigned mutants only: `PM01-blanket-metadata-refusal` and `PM02-blanket-unknown-refusal`, resolved from the pinned runner's `--list` before any selection. Axes: (1) genuine detector sensitivity, (2) unique/compiling mutation application, (3) immutable-oracle and named-row attribution, (4) isolation and byte-exact restoration. No additional mutants, selftests, full repository suites, execution payloads, or network probes were run. PM08 was neither selected nor executed. PM07 was not probed; no survival/equivalence claim is made about it.

**Result:** pristine and restored current-arm grids both passed all 47 graded rows. Both assigned mutants were killed by identifiable graded-row violations, with no harness CNE, leak, timeout, traceback, or acquired fixture objects. However, **both native results have `attributed: false`**: PM01 violates three rows outside its registered `expect_rows`; PM02 violates one. Therefore sensitivity is demonstrated, but an assertion that every violation is confined to the inventory's anticipated rows is falsified. The native exit 0 means the selected inventory was evaluated, not that attribution passed.

## Exact revision, isolation, and commands

Source repository: `/home/vgpnk/Projects/shokunin/kama-shokunin` (production source read-only).
Scratch: `/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal`.
Observed detached HEAD: `2e254a1763a9c08aa07fc53081287f506c447d84`.

Executed initialization, exit 0:

```sh
mkdir -p /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal git -C /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal -c core.hooksPath=/dev/null checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84 && TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal git -C /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal rev-parse HEAD
```

Executed in scratch before selection, exit 0:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal python3 tests/report-audit/promisor-mutants.py --list
```

The output registered the two IDs above exactly; it also explicitly labelled PM08 `execution: static-only`.

Executed bounded probe, exit 0:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOverRefusal/run-probe.py
```

The evidence-only driver loaded the unchanged native runner through `runpy`, wrapped `run_grid` only to retain its returned document/exit/stderr and actual auditor hashes, and called native `main` with this exact argument vector:

```text
--arm current --only PM01-blanket-metadata-refusal --only PM02-blanket-unknown-refusal --grid-timeout 600 --json
```

No `--case` narrowing was used. The native runner performed pristine, PM01, and PM02 grids; the driver performed the required post-restoration grid using the same unchanged detector. Each grid's actual argv, cwd, timeout, elapsed time, and input/output hashes are retained in its `.command.json`. Actual detector command shape:

```text
/usr/bin/python3 /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal/tests/report-audit/promisor-grid.py --arm current --current <actual-auditor-path> --json
```

| Phase | Actual auditor relative to scratch | Grid exit | Graded rows | Violated rows | Elapsed seconds |
|---|---|---:|---:|---:|---:|
| Pristine | `tools/report-landing-audit.py` | 0 | 47 | 0 | 5.104 |
| PM01 | `promisor-mutants-hc54pvi8/PM01-blanket-metadata-refusal.py` | 1 | 47 | 30 | 5.067 |
| PM02 | `promisor-mutants-hc54pvi8/PM02-blanket-unknown-refusal.py` | 1 | 47 | 13 | 4.974 |
| Restored | `tools/report-landing-audit.py` | 0 | 47 | 0 | 5.014 |

Native output: `pristine: passed`, `mutants: 2`, `evaluated: 2`, `killed: 2`, `surviving: []`, `could_not_evaluate: []`; native stderr was empty. Each phase's `harness_fault` was null. All phases had zero timeouts, leaks, and tracebacks. Mutant rows acquired no lane/fleet objects.

## Mutation application and expected detector

Both mutations used the unique `if __name__ == "__main__":` insertion point in the scratch auditor, leaving all ordinary source bytes intact and adding one behavior-bearing wrapper. Native mutant files were independent temporary copies under the assigned scratch root, not production or sibling files.

- **PM01:** alternative 0 regex matched 0 times; fallback alternative 1 insertion matched exactly once and compiled. It wraps the Git helper with refusal on promisor config or paired promisor pack metadata. Expected detector: complete marked clean/failed histories must not become metadata-derived exit 2; required-object refusals must retain content-derived diagnostics.
- **PM02:** alternative 0 insertion matched exactly once and compiled. It wraps `lookup`, raising on any state except `found`, `ambiguous`, or `wrongtype`. Expected detector: ordinary locally absent citations retain their substantive findings/authorized errata treatment; genuine unavailable content must retain an unavailable-object reason rather than a blanket unknown message.

| Bytes | SHA-256 |
|---|---|
| Pristine / restored auditor | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| Actual PM01 auditor, before and after its detector | `1a187e60e9bcf8839defc7bbdab7dc7fca56e6b036b7c23da05e8a0bdffab415` |
| Actual PM02 auditor, before and after its detector | `affd0942d487839213cd1f50de43ccca9ad3420d5b3f86b552e1147f3266b443` |

These actual-run hashes match the hashes independently computed from native `apply_mutation` during selected-pattern inspection.

## Actual findings and token pairs

The per-phase grid JSON retains every named row, actual exit, expected exit, observed finding/token pairs, normalized verdict document, and stderr tail. Here are the distinguishing observations, not inferred successful behavior:

- **PM01 clean witnesses:** PG01–PG06 changed from exit 0/no findings to exit 2/no verdict. PG01 stderr was `could-not-evaluate: /fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal/promisor-grid-w59h9ccr/current/000/lane: partial clone (remote.origin.promisor)`; PG03 used `partial clone (promisor pack)`.
- **PM01 omitted-history witnesses:** PG09/PG11/PG12 pristine exit 1 had `(landed-omitted, 1acb5ebb06054bf52d84ffdacd8727b95287f34b)`. PM01 changed these to metadata-derived exit 2/no findings.
- **PM02 ordinary missing-token witnesses:** PG22/PG23/PG24/PG25/PG37 pristine exit 1 had both `(landed-unresolved, 0123456789abcdef0123456789abcdef01234567)` and `(unresolved-full-hash, 0123456789abcdef0123456789abcdef01234567)`. PM02 exit 2 emitted `could-not-evaluate: 0123456789abcdef0123456789abcdef01234567: unknown: absence is uncertain (blanket refusal)` with no verdict.
- **PM02 unrelated-hole notes witnesses:** PG41/PG42 pristine exit 1 had only `(unresolved-full-hash, 0123456789abcdef0123456789abcdef01234567)`; PM02 produced that same blanket exit-2 diagnostic.
- **PM02 errata witnesses:** PG29/PG30 pristine exit **0**, status `clean`, had raw `(unresolved-full-hash, 58866b563cd900dd894ef21bc863486bcb35b56c)` corrected by errata row 1, and zero uncorrected findings. PM02 instead emitted exit 2 with that exact spliced token and the blanket-unknown message. This is not an ordinary failed baseline verdict: the inventory's PM02 prose incorrectly describes an errata-corrected witness as an ordinary failed finding.
- **PM02 same-exit diagnostic witnesses:** PG33/PG34 remained exit 2 but replaced the required unavailability reason with blanket unknown for `56d7b323865c731da81e0225cf109d66f0480919`. PG46 did the same for hidden blob `2f62e7ff9e9e4c2e972dab0989d414e027012348`. PG47 did the same for the fabricated token. Their pristine diagnostics named unavailable content (PG46/47 additionally named missing tree/commit `2a675c1af91c97c51f5101d6cff10bb797458ab6`). These are legitimate graded diagnostic violations, not harness CNE.
- **Wrong-type control:** PG38/PG39 pristine exit 1 had `(landed-unresolved, 56d7b323865c731da81e0225cf109d66f0480919)` and no unresolved-full-hash finding. PM02 did not violate these rows. PM01 violated the marked PG39 through blanket metadata refusal.

All native failed rows are explicitly named manifest rows with kind `policy` or `control`. Native complete failed sets, using unambiguous manifest cell IDs:

```text
PM01: PG01 PG02 PG03 PG04 PG05 PG06 PG09 PG11 PG12 PG13 PG15 PG17 PG19 PG21 PG22 PG23 PG24 PG26 PG28 PG30 PG31 PG33 PG35 PG39 PG41 PG43 PG44 PG46 PG47 PG48
PM02: PG22 PG23 PG24 PG25 PG29 PG30 PG33 PG34 PG37 PG41 PG42 PG46 PG47
```

## Falsified inventory attribution; no oracle relaxation

Observed native `unexpected_rows`:

```text
PM01: PG15-missing-lane-tree-promisor
      PG19-missing-fleet-tree-promisor
      PG46-opaque-tree-hides-cited-blob
PM02: PG46-opaque-tree-hides-cited-blob
```

These rows keep exit 2 but fail the stronger content-derived diagnostic contract; PM01 supplies forbidden metadata refusal, while PM02's PG46 supplies blanket uncertainty instead of the registered unavailable reason. Thus all kills have real graded witnesses, but not all witnesses were anticipated in each mutant's allowed inventory list. The runner reports this honestly as `attributed: false` yet still credits `killed: true` and exits 0 (`promisor-mutants.py:786-819`). Native exit 0 must not be presented as proof of strict expected-row attribution.

Minimal prospective bookkeeping correction, **not applied or retroactively graded here**: add `PG15`, `PG19`, `PG46` to PM01's expected-row list and `PG46` to PM02's list; change PM02's errata prose to “clean after authorized correction, retaining the raw corrected finding.” These are mutation-inventory/prose corrections, not changes to the immutable grid expectations. If strict expected-row attribution is a required gate rather than an informational field, the gate must also inspect `attributed`; current native exit status alone does not enforce it.

## Twin mismatch and inconclusive-credit boundary

Static source evidence: `violated_rows` includes graded `met == false` **or** `twin_equal == false` (`promisor-mutants.py:530-547`). A failed pristine grid aborts with exit 2; grid exit 2, leak, timeout, nonapplicable mutation, or noncompiling mutation receive no kill (`:703-716`, `:750-785`; harness checks `:509-527`). No such fault occurred in this experiment.

Behaviorally, pristine/restored had 32 row-level comparable twin results and zero mismatches. PM01 had no comparable verdict documents after its refusals; PM02 had 23 comparable rows and zero mismatches. This probe therefore did **not** dynamically exercise the twin-mismatch-only or CNE/leak/timeout rejection branches. Those branch claims are static observations here, not extra executed selftests. A row's incorrect auditor exit 2 is distinguishable from a grid/harness exit 2: both mutant grids exited 1 with concrete graded violations, so neither kill is credited from an inconclusive harness run.

## Oracle and restoration evidence

Before and after all four phases, exact hashes were unchanged:

| Input | SHA-256 |
|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |

Every grid reports population size 47 and population hash `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`. The expected manifest stayed immutable; the strong `names_any_of` grader was used without path-based relaxation. The native runner removed both mutant files; `probe-result.json` records `mutation_files_removed: true`. The original scratch auditor was never overwritten, remained byte-equal to the saved pristine bytes, and passed the same detector again after mutant removal (`before_equals_after: true`, restored exit 0).

The original unknown-from-metadata expectation remains withdrawn/not achieved. Both pristine and restored documents separately retain original-view failures PG22, PG23, PG24, PG28, PG30, PG34, and PG41. The 47 live-policy passes do not relabel these as original-expectation successes.

## Files written, environment, and limits

New report only at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/MutOverRefusal.md`; no production implementation, manifest, index, routing, configuration, fleet, or sibling source was edited.

Evidence directory: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOverRefusal/` contains:

- `run-probe.py` (capture driver; no detector-source modification).
- `selected-patterns.json`, `hashes-before.json`, `hashes-after.json`, `probe-result.json`.
- `native.stdout.json`, `native.stderr.txt`.
- For each phase `pristine`, `PM01-blanket-metadata-refusal`, `PM02-blanket-unknown-refusal`, and `restored`: `.grid.json`, `.command.json`, and `.stderr.txt`.

Observed tools: Git 2.56.0 and Python 3.14.8. No tools installed or updated; no pacman transaction or service/system/config mutation. All subprocess temporary roots were inside the assigned scratch through inherited explicit TMPDIR. Standard offline file-clone fixtures in the unchanged grid were used; no manual object hydration, transport payload, repository-program payload, or PM08 execution occurred.

Unverified by this assigned probe: Git 2.45 execution/prerequisite closure, dynamically injected harness-CNE/leak/timeout/twin-only cases, other nine mutants, remote-universe existence/abbreviation uniqueness, overall source-census verification, broader security closure, and serving capability. No numeric score increase or integration is claimed.

Report: .ufo/waves/round-24/falsify/advice/MutOverRefusal.md
