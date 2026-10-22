# MutStaticNoFetch — partial

**Finding:** PM08 is a uniquely applicable, compiling, behavior-bearing source mutation, but its registered whole-source substring predicate does not distinguish removal of the actual Git argument. The substring remains in documentation/comments. This is a **static-evidence coverage weakness**, not a demonstrated production fetch, behavioral grid failure, or unsound kill attribution. No behavioral kill is credited.

## Axes and scope

- Detection sensitivity: actual `GIT_ISOLATION` argument membership versus incidental source text.
- Safety: PM08 remains static-only; no auditor, grid, transport, repository program, or execution-bearing fixture was run.
- Reproducibility: registered mutation identity, exact source hashes, identical pristine/mutated/restored detector, and exact restoration.
- Oracle integrity: no expected-manifest, grader, or production-source changes.

One assigned mutation only. No nested dispatch, other mutant, full suite, runtime, configuration change, or installation. Godspeed and UFO instructions were read; this leaf report is advisory and invokes no UFO runtime or judge.

## Snapshot and inventory resolution

Scratch: `/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch`.

Observed detached revision: `2e254a1763a9c08aa07fc53081287f506c447d84`.

Exact setup command, exit **0**:

```sh
mkdir -p /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch && env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_NO_LAZY_FETCH=1 GIT_NO_REPLACE_OBJECTS=1 git -c core.hooksPath=/dev/null clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch && env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_NO_LAZY_FETCH=1 GIT_NO_REPLACE_OBJECTS=1 git -C /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch -c core.hooksPath=/dev/null -c advice.detachedHead=false checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
```

All following shell commands used that scratch as cwd. First mutation-runner invocation, exit **0**:

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch PYTHONDONTWRITEBYTECODE=1 python3 tests/report-audit/promisor-mutants.py --list
```

Exact relevant output:

```text
PM08-remove-no-lazy-fetch-gate
  semantic: every git call carries --no-lazy-fetch, so a missing promisor object can never be fetched through the promisor remote (transport, repository programs, signatures); removing the flag reopens that channel
  expects unmet rows: -
  execution: static-only
```

The assignment's inventory nickname was resolved to **`PM08-remove-no-lazy-fetch-gate`**; no guessed CLI selector was used. Neither normal `--only` mode nor `--anchors` was invoked: normal mode starts the pristine grid before selecting mutants, and `--anchors` traverses all eleven mutations (`promisor-mutants.py:646–704`). This probe needed neither.

Exact snapshot/hash/tool-version command, exit **0**:

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch git rev-parse --verify HEAD && env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py tests/report-audit/promisor-grid-expectations.json tests/report-audit/promisor-mutants.py && env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch git --version && env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch python3 --version
```

| Pinned file | SHA-256 |
|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |

Observed tools: Git **2.56.0**, Python **3.14.8**. No tools installed or updated. This host measurement does not close the inherited Git ≥2.45 prerequisite at L0.

## Mutant and bounded detector

The registered PM08 specification (`promisor-mutants.py:397–410`) is literal data parsed with `ast.literal_eval`, not imported or executed. Its alternative match counts on pristine source were **`[1, 0, 1]`**. The first uniquely matching alternative, **0**, deletes exactly:

```python
'"--no-lazy-fetch",\n                 '
```

The sole scratch edit removed that argument from `GIT_ISOLATION`, joining its first two declaration lines. The changed bytes' SHA-256 exactly matched the hash predicted from the registered alternative. Pristine, mutant, and restored source all compiled in memory; no compiled target code was executed.

The identical bounded static detector at `falsify/out/MutStaticNoFetch/pm08-static-probe.py`:

1. Parses the registered PM08 dictionary and confirms `execution="static-only"`, `expect_rows=[]`, and the selected literal replacement.
2. Compiles source only for syntax checking, without executing it.
3. Parses the literal `GIT_ISOLATION` tuple and checks exact `--no-lazy-fetch` membership.
4. Confirms the auditor's `git()` subprocess argument list forwards `*GIT_ISOLATION`.
5. Confirms the registered expressions are exactly `marker in source` / `marker in applied`, and measures that substring predicate independently.
6. Records source, runner, grid, and immutable manifest hashes for every stage.

Expected static-detector exits: **0 / 1 / 0**, and actual observed exits were **0 / 1 / 0**. A static rejection is not a grid kill.

Exact detector commands, each with a 30-second subprocess deadline and the scratch cwd:

```sh
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutStaticNoFetch/pm08-static-probe.py --scratch /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch --stage pristine
# exit 0

env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutStaticNoFetch/pm08-static-probe.py --scratch /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch --stage mutated
# exit 1

env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutStaticNoFetch/pm08-static-probe.py --scratch /fast/scratch/hyaku/kama-r24/falsify/MutStaticNoFetch --stage restored
# exit 0
```

Actual finding/token pairs:

| Stage | Exit | Finding / token | Static gate membership | Registered substring predicate | Source compiles |
|---|---:|---|---|---|---|
| Pristine | 0 | `PM08 / --no-lazy-fetch` present in forwarded isolation tuple | true | true, 4 occurrences | true |
| Mutated | 1 | `PM08 / --no-lazy-fetch` absent from forwarded isolation tuple | false | true, 3 occurrences | true |
| Restored | 0 | `PM08 / --no-lazy-fetch` restored in forwarded isolation tuple | true | true, 4 occurrences | true |

Full actual stdout, stderr, commands, return codes, and hash evidence are retained in `falsify/out/MutStaticNoFetch/static-probe-evidence.json`. All three stderr strings were empty. No timeout, leak, or CNE was converted to a kill.

## Verdict and minimal correction

**Observed:** the exact registered mutation applies at one behavior-bearing point and compiles. The independent AST detector rejects it. The registered substring predicate **survives** the same mutation: documentation/comment mentions at auditor lines 60, 137, and 660 remain after removing the actual argument at line 138. Thus whole-source substring presence cannot substantiate that the Git argument remains present or that the mutation removed it.

**Not claimed:** an official runner `survived` result. Its normal static branch was not invoked because that would first run the grid. The branch's status is `static-only-not-executed`, with `killed=False` (`promisor-mutants.py:731–749`); the before/after expressions themselves were reproduced and confirmed structurally. [INFERENCE] With an independently passing pristine grid, the current branch would report `static_before=True, static_after=True`, despite the argument's removal. Its non-kill bookkeeping is appropriately conservative.

Minimal correction for L1 consideration, **not applied**: at `promisor-mutants.py:738–747`, replace whole-source substring membership with non-executing AST inspection of the literal `GIT_ISOLATION` tuple, require `before=True` and `after=False`, and require the mutated source to compile before accepting the static evidence. An unavailable/ambiguous binding, wrong transition, or compile failure should remain CNE with no kill. Keep PM08 static-only and `killed=False`; do not introduce a transport probe.

No graded row or finding/token was attributed to a behavioral kill: PM08's registered expected-row list is empty, and **behavioral kill credit remains 0**. Twin-mismatch grading, named-row attribution, CNE/leak/timeout runtime mappings, and PM07 equivalence were not exercised; other seats own those scopes.

## Restoration and oracle preservation

| Source state | SHA-256 |
|---|---|
| Before | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| Mutated | `24d2d7bd103243971fbb64d6c8f79228a4d6242732156357e2c125bb75b0caef` |
| Restored | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |

Exact scratch bytes were restored before final measurement. Grid, runner, and expected-manifest hashes remained identical across all three stages. No grader relaxation or oracle rewrite occurred. The original unknown-from-promisor-metadata expectation remains explicitly **withdrawn / not achieved**, not relabelled passed. The amended local-object contract and supplemental opaque-hole cells were not changed or regraded.

Production source, production Git/JJ/index state, sibling scratch copies, fleet, services, routing, operator configuration, and real object stores were not modified. Only the assigned report/output artifacts were written in production's `.ufo` evidence directory; the scratch source was mutated and exactly restored.

## Files written and unverified items

Persistent evidence files:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/MutStaticNoFetch.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutStaticNoFetch/pm08-static-probe.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutStaticNoFetch/static-probe-evidence.json`

Isolated clone retained at the absolute scratch path above; its sole auditor edit is restored. Unverified by design: actual lazy-fetch behavior, transport/execution payloads, a pristine behavioral grid pass, behavioral mutant kill, full-suite results, and global Git-floor closure. No claim is made about any of them.

Report: .ufo/waves/round-24/falsify/advice/MutStaticNoFetch.md
