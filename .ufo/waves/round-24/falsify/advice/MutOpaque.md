# MutOpaque — pinned Opaque mutation experiment

**Falsified, narrowly: PM11's claimed only-named-graded-rows attribution.** PM10 is cleanly killed on its registered opaque rows. The stock runner also labels PM11 killed, but explicitly emits `attributed=false` and unexpected `PG46`; that does not earn an isolated-mutation credit under this assignment. This is a mutation-experiment finding, not a failure of the pristine production auditor or an integration judgment.

## Axes and scope

Axes: behavioral sensitivity; specificity of kill attribution; immutable-oracle/no-harm fidelity; exact-byte restoration and production isolation.

Read preregistration, amendment 1, preinspection snapshot, supplement 2, and `/home/vgpnk/.omp/agent/RULES.md`. Cloned with `--no-hardlinks --no-checkout` into `/fast/scratch/hyaku/kama-r24/falsify/MutOpaque`, then checked out detached `2e254a1763a9c08aa07fc53081287f506c447d84` **in scratch only**. The observed `git rev-parse HEAD` was exactly that revision. No production source, expected manifest, index, fleet, sibling, services, routing, real object stores, or operator configuration was edited. Authorized writes are this report and its own evidence directory.

The first invocation of the stock mutation runner was inventory-only:

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOpaque GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_NO_REPLACE_OBJECTS=1 python3 tests/report-audit/promisor-mutants.py --list
```

CWD was `/fast/scratch/hyaku/kama-r24/falsify/MutOpaque`; exit 0. It resolved these exact registered IDs before selection:

- `PM10-ignore-opaque-nonleaf-missing`; expected-row prefixes `PG33, PG34, PG46, PG47`.
- `PM11-any-hole-refusal`; expected-row prefixes `PG22, PG25, PG33, PG34, PG35, PG36, PG37, PG41, PG42, PG44, PG45, PG47, PG48` — notably **not PG46**.

Only these two mutants were executed. The two independent commands ran concurrently, with distinct per-process TMPDIRs inside this lane's scratch. Each used the same 16 selected cells of the pinned current grid: every assigned expected-row prefix plus the wrong-type twins PG38/39. This is not a full-suite or all-11 run, nor a claim to have remeasured all fixed47 cells.

## Exact bounded commands

The retained `opaque-probe.py` loads the unchanged stock runner with `runpy`, delegates its `main` with the literal CLI arguments below, and observes its unchanged `run_grid` function. It saves the returned actual grid documents, restores each stock-created temporary mutant file to the original bytes in `finally`, invokes that same detector on the restored file, and returns the original mutant result unchanged to the stock classifier. No detector, grader, fixture, expectation, or mutation definition was rewritten. `probe-state.json` retains the complete argv; each `*-grid.json` retains the complete stock grid subprocess command and returned document.

Both commands below used CWD `/fast/scratch/hyaku/kama-r24/falsify/MutOpaque` and an outer 1200-second deadline; each individual grid pass had a 300-second deadline.

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOpaque/probe-tmp/PM10 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_NO_REPLACE_OBJECTS=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOpaque/opaque-probe.py --arm current --current /fast/scratch/hyaku/kama-r24/falsify/MutOpaque/tools/report-landing-audit.py --grid /fast/scratch/hyaku/kama-r24/falsify/MutOpaque/tests/report-audit/promisor-grid.py --grid-timeout 300 --only PM10-ignore-opaque-nonleaf-missing --case PG22-unknown-citation-incomplete-promisor --case PG25-unknown-citation-plain --case PG33-missing-cited-blob-promisor --case PG34-missing-cited-blob-plain --case PG35-unused-missing-blob-promisor --case PG36-unused-missing-blob-plain --case PG37-unused-missing-blob-with-fabricated-citation-plain --case PG38-wrong-type-citation-plain --case PG39-wrong-type-citation-promisor --case PG41-unused-missing-blob-fabricated-in-notes-promisor --case PG42-unused-missing-blob-fabricated-in-notes-plain --case PG44-missing-unused-tree-promisor --case PG45-missing-unused-tree-plain --case PG46-opaque-tree-hides-cited-blob --case PG47-opaque-tree-with-unresolved-fabricated-token --case PG48-opaque-unused-tree-no-unresolved-token --json

env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutOpaque/probe-tmp/PM11 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_NO_REPLACE_OBJECTS=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOpaque/opaque-probe.py --arm current --current /fast/scratch/hyaku/kama-r24/falsify/MutOpaque/tools/report-landing-audit.py --grid /fast/scratch/hyaku/kama-r24/falsify/MutOpaque/tests/report-audit/promisor-grid.py --grid-timeout 300 --only PM11-any-hole-refusal --case PG22-unknown-citation-incomplete-promisor --case PG25-unknown-citation-plain --case PG33-missing-cited-blob-promisor --case PG34-missing-cited-blob-plain --case PG35-unused-missing-blob-promisor --case PG36-unused-missing-blob-plain --case PG37-unused-missing-blob-with-fabricated-citation-plain --case PG38-wrong-type-citation-plain --case PG39-wrong-type-citation-promisor --case PG41-unused-missing-blob-fabricated-in-notes-promisor --case PG42-unused-missing-blob-fabricated-in-notes-plain --case PG44-missing-unused-tree-promisor --case PG45-missing-unused-tree-plain --case PG46-opaque-tree-hides-cited-blob --case PG47-opaque-tree-with-unresolved-fabricated-token --case PG48-opaque-unused-tree-no-unresolved-token --json
```

Actual command exits: **0 and 0**, approximately 5.11 and 5.09 seconds respectively. These are the stock runner's evaluated-inventory exits, not auditor clean verdicts.

## Mutants, detector, and actual outputs

Both registered insertions matched the sole `if __name__ == "__main__":` anchor exactly once, selected alternative 0, and compiled successfully. The specimens actually observed by the detector had the exact hashes of the stock transform. The small behavior-bearing changes are:

- PM10 replaces `opaque_hole(stores)` with a function returning `(None, None)`. Expected detector: opaque missing nonleaf plus an unresolved citation must remain content-derived CNE2; silently accepting absence must violate PG46/47, while actual known wrong type stays failed1.
- PM11 wraps `RepoStore.missing()` and raises on any nonempty `missing` or `opaque` set, with a count-only diagnostic. Expected detector: unrelated holes must not convert justified failed1 or clean0 into refusal; attribution must remain within the registered prefixes.

| Mutant | Pristine grid | Mutated grid | Restored grid | Stock runner output | Scoped verdict |
|---|---:|---:|---:|---|---|
| PM10 | 0; 16 graded, 0 violations | 1; PG46, PG47 | 0; 16 graded, 0 violations | `status=killed`, `killed=1`, `attributed=true`, `unexpected_rows=[]` | **Killed, correctly attributed** |
| PM11 | 0; 16 graded, 0 violations | 1; eight violations below | 0; 16 graded, 0 violations | `status=killed`, `killed=1`, `attributed=false`, `unexpected_rows=[PG46-opaque-tree-hides-cited-blob]` | **Detector-killed, but no isolated only-named-rows credit** |

No grid process exited 2; no timeout, harness leak, traceback, or object acquisition occurred. Expected auditor-level CNE2 cells are not confused with a grid/harness-level could-not-evaluate. All six passes returned usable documents; both stock runner documents had `could_not_evaluate=[]` and `surviving=[]`.

### Exact finding/token pairs

Token abbreviations in the following table expand to these literal observed values:

- `fake = 0123456789abcdef0123456789abcdef01234567`
- `blob = 56d7b323865c731da81e0225cf109d66f0480919`
- `hidden = 2f62e7ff9e9e4c2e972dab0989d414e027012348`
- `subtree = 2a675c1af91c97c51f5101d6cff10bb797458ab6`

Pristine and restored results agreed on every listed exit and defect pair in both experiments:

| Cells | Pristine and restored | PM10 | PM11 |
|---|---|---|---|
| PG22, PG37 | exit1; `(landed-unresolved,fake)`, `(unresolved-full-hash,fake)` | unchanged; met | exit2, no verdict/defect pairs; **unmet** |
| PG25 | exit1; `(landed-unresolved,fake)`, `(unresolved-full-hash,fake)` | unchanged; met | unchanged; met |
| PG33, PG34 | exit2; content-derived refusal naming `blob`; no verdict | unchanged; met | exit2, count-only refusal, no `blob`; **unmet** |
| PG35, PG36 | exit0; `[]` | unchanged; met | unchanged; met |
| PG38, PG39 | exit1; `(landed-unresolved,blob)` | unchanged; met | unchanged; met |
| PG41, PG42 | exit1; `(unresolved-full-hash,fake)` | unchanged; met | exit2, no verdict/defect pairs; **unmet** |
| PG44, PG45, PG48 | exit0; `[]` | unchanged; met | unchanged; met |
| PG46 | exit2; refusal naming `hidden` and `subtree`; no verdict | **exit1; `(unresolved-full-hash,hidden)`; unmet** | exit2; count-only refusal; **unmet, unregistered attribution** |
| PG47 | exit2; refusal naming `fake` and `subtree`; no verdict | **exit1; `(unresolved-full-hash,fake)`; unmet** | exit2; count-only refusal; **unmet** |

PM11's exact violated set was `PG22, PG33, PG34, PG37, PG41, PG42, PG46, PG47`. Its stderr on PG46 was:

```text
could-not-evaluate: /fast/scratch/hyaku/kama-r24/falsify/MutOpaque/probe-tmp/PM11/promisor-grid-jv6_s3d2/current/013/lane: unknown: unavailable required object: 2 hole(s) in the store
```

This is still auditor exit2 but names neither allowed PG46 object. The immutable `names_any_of` check therefore correctly rejects it. PG33/34 and PG47 likewise lose their required object names. The grader was **not** weakened to accept a path. PG22/37/41/42 independently expose actual over-refusal, not merely diagnostic loss.

### Twin mismatches and attribution

The stock `violated_rows` implementation at `tests/report-audit/promisor-mutants.py:530-547` uses graded kind and includes either `met is False` **or** `twin_equal is False`. That is the same function used by the probe, not a replacement classifier.

Actual `twin_mismatch=[]` in all passes. Pristine/restored each compared 10 row endpoints, representing five document-bearing twin pairs. The missing-cited-blob pair has null rather than false document equality because both arms refuse without a verdict. PM11 also makes PG22/37 and PG41/42 equality null by refusing both. Thus this probe observes correct preservation on the document-bearing twins and no false/null conflation; it does **not** claim to have behaviorally forced the twin-mismatch branch. Separate mutation-runner selftests were not run by this lane.

## Scoped experiment defects and minimal corrections (not applied)

1. **Attribution is informational, not a credit gate.** At `promisor-mutants.py:786-798`, `killed = bool(bad)` is assigned before computing `attributed`/`unexpected_rows`. At lines 801-820, a row with `status="killed"` contributes to the killed count and exit0 regardless of `attributed=false`. The actual PM11 output demonstrates that path. This falsifies the assignment's only-named-graded-rows requirement, not the underlying production audit rule.

   Minimal correction: after computing `failed` and the registered-prefix comparison, compute `unexpected` once. If it is nonempty, retain the observed failed rows/details but emit `status="could-not-evaluate"`, `killed=false`, `attributed=false`, and a reason naming the unexpected rows, then skip the ordinary killed/survived entry. The existing aggregate CNE mapping will return exit2 and grant no kill. Apply this gate to the same combined graded failures, including twin mismatches. **Do not change the expected manifest or relax `names_any_of`.** This correction was neither edited nor tested here.

2. **PM11 does not actually install an unconditional any-hole gate.** Observed PG35/36/44/45/48 all stay clean0 under PM11. Static call tracing explains why: `RepoStore.missing()` is lazy; its only callers in the candidate are `unknown_citation` and `opaque_hole` (`tools/report-landing-audit.py:697-714`). `refuse_unknown` skips found/ambiguous/wrongtype before those calls (429-442), and the errata path calls them only for an absent token (570-577). PM11 patches only `missing()` (`promisor-mutants.py:230-247`), so it cannot force an unrelated-hole refusal when every token resolves. It covers an unresolved-token over-refusal, not the advertised full unconditional-precondition surface.

   The minimal semantic correction to the **mutant**, if that separate inventory is revised prospectively, is to trigger its patched missing check eagerly after the original `RepoStore.__init__`, and to include the actual missing OID(s) in its refusal so unchanged required-object cells retain their strong diagnostics. An eager version also needs its registered expected-row attribution reviewed against the fixed grid; merely appending PG46 to the existing list would mask diagnostic contamination and still would not make the current lazy mutant unconditional. No such revised mutant was authored or executed; no contract change is proposed.

## Exact restoration and immutable hashes

All hashes are SHA-256. For each temporary specimen the observer captured the mutated hash before and after the mutant detector, restored the original **exact byte string**, captured equality `true`, and ran the same selected detector on the restored bytes before the stock runner removed its temporary directory. The original scratch candidate was never overwritten and remained exact-byte unchanged. Receipts are in each `probe-state.json` and each grid document's observed `auditor_sha256`.

| Input | Before / pristine | Mutated | After restoration |
|---|---|---|---|
| Auditor, PM10 specimen | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `c01371b1aedfd8b485d3e85aa5779dc8a7d97073ad2750261f6b40861ed1d92e` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| Auditor, PM11 specimen | same pristine hash | `047a715ad09d39ce83eb710720f5cf0d630961d69203febea01869b8a52a7fed` | same pristine hash |
| Grid source | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | unchanged | unchanged |
| Expected manifest | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | unchanged | unchanged |
| Mutation runner | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | unchanged | unchanged |

Pinned population fingerprint returned by the grid: `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`. The production expected-manifest read also yielded the same `d86b7bea...` hash. Evidence observer source: `048eeef9a22b3181d8005878773d28fea36f844a54b72e526890c2ceccf0168d`.

Oracle receipts read without modification:

- preregistration: `6dde0d72343c9b8e64ec6e3ae4c9b382dfa3daaf9d0f6afd3f274cfac30e844c`
- amendment 1: `930b087a218f880a55c4507b7f11309eae130e2b5dd2111e27d5653b39c8f82f`
- preinspection snapshot: `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e`
- supplement 2: `4600a8c3951d26b68ee2562d5967cecfe9b00d66443ac10e6d371956e5d34368`

## Observed versus inferred; limits

Observed: inventory IDs, detached base, unique/compiling insertions, actual specimen hashes, all six grid outputs, exact defect/token pairs, original-byte restoration, zero leaks/timeouts/acquisitions, PM11's `attributed=false` with `killed=1`/exit0, and unchanged manifest/source hashes. Source-derived explanation: lazy-only PM11 coverage and the missing attribution gate. Proposed corrections are unimplemented and unverified, not claims of a repaired result.

The initial metadata-based unknown-citation expectation remains **withdrawn / not achieved**. It is not relabelled passed: both pristine/restored documents separately retain original-view failures PG22, PG34, PG41 while grading the amended local-object policy. The fixed47 manifest was not rewritten.

No PM07 or other unassigned mutant ran; no claim about their equivalence/survival is made. PM08 was never executed. No transport, network, execution payload, old execution-bearing vulnerability probe, full suite, or alternate runtime was invoked. Git isolation flags were not mutated. The inherited Git >=2.45 prerequisite remains L0-open; local `git version 2.56.0` and `Python 3.14.8` do not close the fleet prerequisite. No tools were installed or updated. No serving capability, higher numeric score, global source census, or broader closure is claimed.

## Files written

All permanent artifacts are absolute under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/`:

- `advice/MutOpaque.md` — this first append-only scoped report.
- `out/MutOpaque/opaque-probe.py` — retained reproducible observer, not production code.
- `out/MutOpaque/observed-runner-results.json` — actual printed runner-summary fields, clearly labelled as a transcription.
- `out/MutOpaque/PM10/pristine-grid.json`
- `out/MutOpaque/PM10/mutated-grid.json`
- `out/MutOpaque/PM10/restored-grid.json`
- `out/MutOpaque/PM10/probe-state.json`
- `out/MutOpaque/PM11/pristine-grid.json`
- `out/MutOpaque/PM11/mutated-grid.json`
- `out/MutOpaque/PM11/restored-grid.json`
- `out/MutOpaque/PM11/probe-state.json`

The isolated clone and per-process empty temp parents remain at `/fast/scratch/hyaku/kama-r24/falsify/MutOpaque`; the stock runner/grid cleaned their disposable specimen/fixture directories. No new production-source edits require integration from this lane.

Report: .ufo/waves/round-24/falsify/advice/MutOpaque.md
