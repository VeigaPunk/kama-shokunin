# MutUnavailable — required-evidence mutation probe

**Partial — all three assigned mutants were behaviorally killed, but the frozen attribution metadata is incomplete.** PM03 reports the additional graded row PG46; parent-authorized PM06 reports additional PG15 and PG19. These are attribution-metadata gaps, **not auditor source bugs**. Nothing in production or the immutable expectation manifest was edited.

## Axes and scope

1. Detector soundness: passing pristine bytes; identifiable, graded row failures; twin mismatches included in the predicate; no harness-CNE, leak or timeout credit.
2. Mutation specificity: the registered, uniquely matching and compiling behavior change, without a substitute mutation.
3. Isolation/restoration: detached pinned scratch, exact original auditor bytes after each experiment, unchanged grid/runner/manifest, no production/index/object-store mutation.

The original assignment was PM03/PM04. The parent extended the still-open assignment to PM06, which was run separately with `--only PM06-swallow-actual-read-error`; PM03/PM04 were not rerun for that extension. No all-11 mutation run, selftest suite, PM07 execution, PM08 execution, transport payload or execution-bearing vulnerability probe was performed. PM08 remained unselected and unexecuted. L1 retains integration/judgment authority.

The original unknown-from-metadata expectation is **withdrawn/not achieved**, never relabelled passed. Measurements below grade only the amended local-object contract and its independent opaque-hole supplement. The seven withdrawn-original rows remain listed by the captured grid outputs.

## Pinned snapshot and tools

- Scratch: `/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable`.
- Source: `/home/vgpnk/Projects/shokunin/kama-shokunin`, cloned using `git clone --no-hardlinks --no-checkout`, then detached checkout **in scratch only**.
- Observed `git rev-parse HEAD`: `2e254a1763a9c08aa07fc53081287f506c447d84` (exit 0).
- Git: `2.56.0`; Python: `3.14.8`. No installs or updates.
- Every behavioral subprocess used `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable`. Grid fixtures and temporary mutant files stayed below that directory. The grid used its existing no-lazy-fetch helpers; I did not manually inspect blobless objects with fetch-capable Git commands.

| Pinned file | SHA-256 before and after all probes |
|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |

Every grid observation retained population size **47**, population hash `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, and the unchanged expectation-manifest hash above. The separate PG40 open row was reported, never used for a kill.

Authoritative preregistration/amendment/snapshot/supplement digests are in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable/oracle-digests.json`.

## Commands and exit evidence

Working directory for all commands was the pinned scratch. The behavioral launch environment was:

```text
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable
PYTHONDONTWRITEBYTECODE=1
GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1
GIT_NO_LAZY_FETCH=1
GIT_NO_REPLACE_OBJECTS=1
GIT_TERMINAL_PROMPT=0
```

1. **Inventory first:** `python3 tests/report-audit/promisor-mutants.py --list` — **exit 0**. Its actual output registered all three exact selectors used here:
   - `PM03-skip-required-object-availability`
   - `PM04-accept-unavailable-referenced-object`
   - `PM06-swallow-actual-read-error`

2. **PM03/PM04 capture:**

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_NO_LAZY_FETCH=1 GIT_NO_REPLACE_OBJECTS=1 GIT_TERMINAL_PROMPT=0 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable/capture-mutants.py
```

**Exit 0; runner output:** `pristine=passed`, `mutants=2`, `killed=2`, `surviving=[]`, `could_not_evaluate=[]`; empty runner stderr. The capture harness calls the pinned runner's `main()` in process with this exact argv (it is not a claim of an additional shell execution):

```text
--current /fast/scratch/hyaku/kama-r24/falsify/MutUnavailable/tools/report-landing-audit.py
--grid /fast/scratch/hyaku/kama-r24/falsify/MutUnavailable/tests/report-audit/promisor-grid.py
--arm current --grid-timeout 600 --json
--only PM03-skip-required-object-availability
--only PM04-accept-unavailable-referenced-object
```

3. **PM03/PM04 restored-byte detector:**

```sh
python3 /fast/scratch/hyaku/kama-r24/falsify/MutUnavailable/tests/report-audit/promisor-grid.py --arm current --current /fast/scratch/hyaku/kama-r24/falsify/MutUnavailable/tools/report-landing-audit.py --json
```

With the same environment, **exit 0**, 47/47 met, no violated graded rows. Actual stdout/stderr and command/byte receipts are `restored.stdout.json`, `restored.stderr.txt`, and `restoration.json` in the absolute artifact directory below.

4. **Parent-authorized PM06 capture:**

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_NO_LAZY_FETCH=1 GIT_NO_REPLACE_OBJECTS=1 GIT_TERMINAL_PROMPT=0 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable/capture-pm06.py
```

**Exit 0; runner output:** `pristine=passed`, `mutants=1`, `killed=1`, `surviving=[]`, `could_not_evaluate=[]`; empty runner stderr. The in-process pinned-runner argv was identical to step 2 except the only selector was `--only PM06-swallow-actual-read-error`. This capture also ran the same pinned grid on original bytes after the mutant: **restored exit 0**, 47/47 met.

The capture wrappers record results returned by the original `run_grid` function. They do not change the auditor, fixtures, manifest, grading predicates, timeout logic or attribution decisions. Exact spawned `/usr/bin/python3 ... promisor-grid.py --arm current --current <auditor> --json` commands are retained in each grid receipt. All three runner executions here are the two bounded selection batches above plus their prescribed restoration detectors, not a generic full-suite run.

## Minimal mutants and detector outcomes

All alternative indices below are zero-based. Each selected pattern matches once, and each resulting mutant compiles.

| Registered mutant | Actual change | Match counts / selected alternative | Mutant SHA-256 |
|---|---|---|---|
| PM03 | `RepoStore.missing`: `self._missing = missing_reachable(self.path, self.root)` → `self._missing = (set(), set())` | `[0, 1]`; alternative 1 | `a31fc4d041ebcb592413c37eb7a471ff61b395fe47eeac080862adbe9b3e63be` |
| PM04 | `unknown_citation`: `for store in stores:` → `for store in ():` | `[1, 1]`; first applicable alternative 0 | `481e5e6c74171e844f05a7a6b57f73852170b5e75100988a508ada28db129220` |
| PM06 | Registered insertion wraps `git`: non-timeout `EvalError` becomes `""`; timeout exceptions remain raised | `[1]`; alternative 0 | `b0e6fb6c22fca5b6bc97b9b96d5d3d7d9cb3ab0df914a6acc8f2f647ddec018c` |

PM04's two fallback patterns each match once; the runner deterministically applies the first one, not both. Exact diffs and compilation/match evidence are retained.

| Detector stage | Grid exit | Met / graded | Named graded violations | Runner mutation verdict |
|---|---:|---:|---|---|
| PM03/PM04 pristine | 0 | 47/47 | none | baseline passed |
| PM03 | 1 | 43/47 | PG33, PG34, PG46, PG47 | killed; `attributed=false` |
| PM04 | 1 | 45/47 | PG33, PG34 | killed; `attributed=true` |
| PM03/PM04 restored | 0 | 47/47 | none | restored detector passed |
| PM06 pristine | 0 | 47/47 | none | baseline passed |
| PM06 | 1 | 37/47 | PG13–PG21 inclusive, PG43 | killed; `attributed=false` |
| PM06 restored | 0 | 47/47 | none | restored detector passed |

**Across every captured graded arm:** zero twin mismatches, tracebacks, timeouts, harness leaks or acquired objects. Recorded PG40 open-row observations likewise had no leaks, timeouts, tracebacks or acquired objects. PG33/PG34 remain equal twins even under the bad verdict, so the live manifest—not twin inequality—is what kills PM03/PM04.

### Exact changed finding/token pairs

Pristine and restored observations for every row below are exit 2 with no verdict document, meeting the live required-evidence expectation.

| Mutant / exact case | Mutated exit | Actual uncorrected finding/token pairs |
|---|---:|---|
| PM03 and PM04: `PG33-missing-cited-blob-promisor` | 1 | `unresolved-full-hash / 56d7b323865c731da81e0225cf109d66f0480919` |
| PM03 and PM04: `PG34-missing-cited-blob-plain` | 1 | `unresolved-full-hash / 56d7b323865c731da81e0225cf109d66f0480919` |
| PM03: `PG46-opaque-tree-hides-cited-blob` | 1 | `unresolved-full-hash / 2f62e7ff9e9e4c2e972dab0989d414e027012348` |
| PM03: `PG47-opaque-tree-with-unresolved-fabricated-token` | 1 | `unresolved-full-hash / 0123456789abcdef0123456789abcdef01234567` |
| PM06: `PG13-missing-lane-blob-promisor`, `PG14-missing-lane-blob-plain` | 0 | none: false clean verdict |
| PM06: `PG15-missing-lane-tree-promisor`, `PG16-missing-lane-tree-plain` | 0 | none: false clean verdict |
| PM06: `PG17-missing-fleet-report-promisor`, `PG18-missing-fleet-report-plain` | 1 | `landed-omitted / 58866b563cd900df310588effe79028efc104c33`; `landed-section-missing / -` |
| PM06: `PG19-missing-fleet-tree-promisor`, `PG20-missing-fleet-tree-plain` | 2 | none: no verdict; `could-not-evaluate: round 1: .ufo/reports/round-1/kama.md has no fleet commit` |
| PM06: `PG21-missing-ancestor-promisor` | 0 | none: false clean verdict |
| PM06: `PG43-fleet-unhydrated-blobless-report-required` | 1 | `landed-omitted / 58866b563cd900df310588effe79028efc104c33`; `landed-section-missing / -` |

For PG33/PG34, the pristine reason names missing object `56d7b323865c731da81e0225cf109d66f0480919`. For PG46/PG47 it names the unresolved citation and opaque missing tree/commit `2a675c1af91c97c51f5101d6cff10bb797458ab6`.

**CNE receives no availability-verdict kill credit:** PM06 PG19/PG20 still refuse with exit 2. Their strong `names_any_of` check fails because the replacement diagnostic does not identify the missing tree; they are two of the runner's ten graded violations, but I do not count them as evidence that PM06 produced an improper clean/failed availability verdict. The other **eight** changed rows independently demonstrate that substantive defect (five false-clean rows and three improper failed-verdict rows). No exit-2 grid run, leak or timeout was used as kill evidence.

### Attribution metadata, not source bugs

- PM03's original frozen `expect_rows` omits **PG46**, so the unchanged runner correctly emits `unexpected_rows=["PG46-opaque-tree-hides-cited-blob"]` and `attributed=false` despite a named, graded semantic kill.
- PM06's original frozen `expect_rows` omits **PG15 and PG19**, yielding those two `unexpected_rows` and `attributed=false`. PG15 is a false-clean row; PG19 is the diagnostic-specificity-only CNE row distinguished above.
- PM04 has no unexpected rows and `attributed=true`.
- Thus “only original attribution-list rows fail” is not supported for PM03/PM06. This does **not** change either the live manifest or the substantive detector outcomes. Preserve the original lists as historical metadata; no expectation/source correction was applied.
- PM03 and PM04 do not have identical observed failure sets: PM03 also disables opaque-hole inventory, while PM04 leaves the independent opaque-hole refusal active. Treat their overlap as measured, not as an equivalence proof.

## Restoration and observed versus inferred

The registered runner writes mutants to new temporary files, never over the candidate. The candidate auditor remained byte-for-byte equal to the initially saved bytes after the first batch, after its restored run, and after PM06 plus its restored run. The runner, grid and immutable manifest hashes also remained exact. All three recorded temporary mutant paths were absent after their runner returned. The final detector used original auditor hash `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` and passed 47/47.

**Observed:** exact base, unique/compiling replacements, runner outputs, per-row exits/pairs, unchanged hashes, missing temporary mutant paths, zero acquisitions/leaks/timeouts, and the restored-byte detector passes. **[INFERENCE] Mechanism:** the minimal replacements and the distinct opaque-hole outcomes explain the reported failure sets; this finite experiment is not proof about every possible repository or mutation.

Static source inspection of `promisor-mutants.py:530-547` confirms that `violated_rows` includes `met is False` **or** `twin_equal is False` for graded rows. `main:703-716` requires a passing pristine grid; `main:764-784` rejects harness faults, grid exit 2, and exit 1 without an identifiable violated row. These fault branches and a deliberately injected twin mismatch were **not dynamically exercised** in this scope. No stronger fault-injection coverage claim is made.

Unverified/out of scope: Git 2.45 minimum-version behavior remains the inherited open L0 prerequisite (this host is Git 2.56.0); no PM07/PM08 or other unassigned mutation behavior; no arbitrary-untrusted-repository guarantee, source-census gate, new serving capability, numeric-score increase, integration, or shipment claim.

## Files written

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/MutUnavailable.md`.

All following evidence files are under the absolute directory `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable/`:

- `anchors-and-before.json`, `assigned-mutations.diff`, `oracle-digests.json`.
- `capture-mutants.py`, `runner-command-and-hashes.json`, `runner.stdout.json`, `runner.stderr.txt`.
- `grid-00-pristine.json`, `grid-01-PM03-skip-required-object-availability.json`, `grid-02-PM04-accept-unavailable-referenced-object.json`.
- `restoration.json`, `restored.stdout.json`, `restored.stderr.txt`, `measurement-summary.json`.
- `capture-pm06.py`, `pm06-anchors-and-before.json`, `assigned-PM06.diff`.
- `pm06-command-and-restoration.json`, `pm06-runner.stdout.json`, `pm06-runner.stderr.txt`.
- `pm06-grid-00-pristine.json`, `pm06-grid-01-PM06-swallow-actual-read-error.json`, `pm06-grid-02-restored.json`.
- `final-measurement-summary.json` (combined scoped outcomes, exact pairs, metadata gaps and CNE exclusions).

No repository implementation, tests, expectations, production history/index, sibling files, fleet, routing, configuration, services, or real object stores were changed. Scratch is retained at its assigned location; probe evidence is retained, not integrated.

Report: .ufo/waves/round-24/falsify/advice/MutUnavailable.md

## Append-only command-accounting clarification

The earlier phrase “All three runner executions” is imprecise: there were **exactly two pinned mutation-runner `main()` calls**, selecting PM03/PM04 together and PM06 separately. There were **seven grid calls** total: shared pristine + PM03 + PM04 + restored, then PM06 pristine + PM06 + restored. The three mutations were each executed once; there was no third mutation-runner batch. The retained command receipts are authoritative.

Report: .ufo/waves/round-24/falsify/advice/MutUnavailable.md
