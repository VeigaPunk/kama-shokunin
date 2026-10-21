# Round 22 — actual-producer mutation probe

## Result

**Five actual-production mutants killed; zero survived; zero inconclusive.** Every mutant emitted `finding_id=incomplete-install-identity` and exited **1** through the canonical matrix's `--current-source` path. The unmutated positive ran first: **exit 0, `clean`, 32/32 rows passed**. Each of the five restored source copies subsequently produced **exit 0, `clean`, 32/32 passed**.

Axes: mutation fidelity; finite behavioral detection; byte-exact restoration; write containment. This is a bounded detector result, not a promotion/integration judgment or proof beyond the enumerated matrix.

## Source and execution identity

- Trusted lane clone pinned to `971d4549dff78e93327fbebaf1498e1c47db6661` before reading/executing producer or matrix code. Pin receipt: `.ufo/waves/round-22/residual/FinalMutations/commands/02-source-identity.json`.
- Actual producer: `tools/kama-llamacpp-live.py`; SHA-256 **`8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3`**.
- Canonical detector: `tests/llamacpp-live/install-io-grid.py`; SHA-256 **`c10de62fd57f235d151ca13a4951642502ab163534d87742572119ac404706dc`**.
- Matrix population SHA-256: **`5b38422c32c5fb8bdfe1b69ed003f260914c339a2c12abf0f984790f4ca9833d`**. All eleven detector outputs reported this population: 18 I/O-fault rows plus 14 controls.
- Runtime: **Python 3.14.8**, the same interpreter throughout. No installs or updates.
- Detector invocation shape, from the pinned scratch clone:

  ```text
  python tests/llamacpp-live/install-io-grid.py --arm current --current-source <temporary full producer copy> --json
  ```

  Exact interpreter, argv, cwd, environment overrides, UTC start, elapsed time, 60-second bound, exit code, stdout/stderr paths and hashes are retained in each command receipt. `TMPDIR` was confined to this assignment's scratch scope; bytecode writes were disabled.
- Order: one pristine positive first; five independent mutant probes concurrently, each followed by unconditional byte restoration and its own restored-source detector run. **11 detector invocations / 352 row evaluations** total. No `--selftest`, fixture-only substitute, frozen arm, live producer CLI, server, service, network probe or other runtime was invoked.

## Mutation operators and observed outputs

All mutants began as byte-identical full copies of the pinned actual producer. Only `install_tree` was mutated. “Refusal deleted” means deleting that handler's two-line `raise SetupError(...) from exc` body and restoring the fail-open return/skip behavior represented by the canonical matrix's mutation operator; the `except OSError as exc` header and all other code were preserved. The broad-catch mutants changed only the three `install_tree` catch types, leaving their refusal formatting intact.

| Mutant | Smallest behavior change | Fault rows passed | Controls passed | Failed rows | Emitted finding / exit | Verdict |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `list-refusal-deleted` | Original lines 188–189 → `return {}, None` | 15/18 | 14/14 | **3** | `incomplete-install-identity` / **1** | killed |
| `stat-refusal-deleted` | Original lines 195–196 → `continue` | 12/18 | 14/14 | **6** | `incomplete-install-identity` / **1** | killed |
| `read-refusal-deleted` | Original lines 202–203 → `continue` | 9/18 | 14/14 | **9** | `incomplete-install-identity` / **1** | killed |
| `broad-exception` | Original catch lines 187, 194, 201: `OSError` → `Exception` | 18/18 | 11/14 | **3** | `incomplete-install-identity` / **1** | killed |
| `broad-baseexception` | Same three catches: `OSError` → `BaseException` | 18/18 | 8/14 | **6** | `incomplete-install-identity` / **1** | killed |

Total: **27 failed row occurrences across five mutant executions**. Actual failed-row lists exactly matched the predeclared expected lists in `.ufo/waves/round-22/residual/FinalMutations/mutation-plan.json`. All detector stderr streams were empty; no detector timed out or exited 2.

### Failed rows by exact matrix name

- **`list-refusal-deleted` — 3:** `list-permission`, `list-missing`, `list-io`.
- **`stat-refusal-deleted` — 6:** `stat-llama-server-permission`, `stat-llama-server-missing`, `stat-llama-server-io`, `stat-lib.so-permission`, `stat-lib.so-missing`, `stat-lib.so-io`.
- **`read-refusal-deleted` — 9:** `read-llama-server-permission`, `read-llama-server-missing`, `read-llama-server-isdir`, `read-llama-server-io`, `read-lib.so-permission`, `read-lib.so-missing`, `read-lib.so-isdir`, `read-lib.so-io`, `late-read-lib.so`.
- **`broad-exception` — 3:** `listdir-type-error`, `lstat-type-error`, `read-type-error`.
- **`broad-baseexception` — 6:** `listdir-type-error`, `listdir-interrupt`, `lstat-type-error`, `lstat-interrupt`, `read-type-error`, `read-interrupt`.

### Actual finite effects, not fixture assumptions

- List refusal deletion returned an empty tree and null digest in three injected-fault rows instead of refusing. The paired actual `install_links` helper also reported un-hashed members in all three rows.
- Stat refusal deletion returned six partial, non-null digests; read refusal deletion returned nine. The paired actual helper reported the omitted member in all 15 rows. These paired problems do not erase the direct `install_tree` contract violations.
- The late-read mutant reached the intended finite fault after **one chunk / 1,048,576 bytes**, then returned a partial digest; this was not an unopened-file substitute.
- Both broad-catch mutants produced **`AttributeError`, `same_exception=false`** in their failed propagation controls, rather than preserving the injected `TypeError`/`InjectedInterrupt`. They were killed for lost exception type/identity, **not** for extra `SetupError` refusals. This distinction is present in the actual-producer output and must not be replaced with the selftest fixture's behavior.

## Mutant digests and retained patches

Each mutant's before and restored SHA-256 was the common producer digest `8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3`.

| Mutant | Mutated source SHA-256 |
| --- | --- |
| `list-refusal-deleted` | `05dacdfa6ba98077fc96fa8b6e8a3c1c6efac6eef7276afa8aa64be1b4d82ffc` |
| `stat-refusal-deleted` | `ae7f540b8c7f7c431aa79dd852a6c811b86e062682b5138584d2f42d5742aa01` |
| `read-refusal-deleted` | `23e921bc19f31a8076c44f511996d6a116ff0b96f4823a702a8c25a6798287c1` |
| `broad-exception` | `5be4665bccbe619e6bf9d0c57331da14826f8c0caed684df1f179c4117e42de0` |
| `broad-baseexception` | `f7f9b03e3b930abf9634b9db519ec5de03a0d2897060b6ab70701e533b79e858` |

The matching actual matrix outputs independently report each mutated source digest. Exact unified patches are retained at:

- `.ufo/waves/round-22/residual/FinalMutations/patches/list-refusal-deleted.patch`
- `.ufo/waves/round-22/residual/FinalMutations/patches/stat-refusal-deleted.patch`
- `.ufo/waves/round-22/residual/FinalMutations/patches/read-refusal-deleted.patch`
- `.ufo/waves/round-22/residual/FinalMutations/patches/broad-exception.patch`
- `.ufo/waves/round-22/residual/FinalMutations/patches/broad-baseexception.patch`

Patch hashes are in the mutation plan, per-mutant JSON and manifest. Patch-generation `diff` commands exited 1 because differences existed; these are not detector failures.

## Restoration and containment evidence

Restoration ran in each probe's `finally` block. Five `cp` restoration commands exited 0; five post-restore `sha256sum` receipts matched the original full producer digest; five restored-source detector runs exited 0 with `clean`, 18/18 fault rows and 14/14 controls passed. Their complete JSON stdout bytes also matched the pristine positive's SHA-256 **`8706289526dd9c925d2e29a45951057e4f65ef6a2acfa22ad362cc22434e6db8`**.

The pinned clone's canonical matrix and producer digests also matched before/after. Only temporary producer copies were mutated. No lane source, sibling source, production checkout metadata, fleet/config/index/`.jj`, model parameters or routing were changed. Writes were confined to this assignment's evidence scope and this requested report.

After restoration and recording the evidence, the isolated clone, full temporary producer copies and fixture temp directory were removed. Cleanup exited 0; only patches and receipts remain. No scaffolding is left to integrate.

## Machine-readable evidence

All paths below are relative to the lane root:

- Complete result, source hashes, row-level outcomes, restoration and command index: `.ufo/waves/round-22/residual/FinalMutations/manifest.json`.
- Predeclared expectations, patch paths/hashes and before/mutant hashes: `.ufo/waves/round-22/residual/FinalMutations/mutation-plan.json`.
- Pristine positive: `.ufo/waves/round-22/residual/FinalMutations/baseline-summary.json` and `.ufo/waves/round-22/residual/FinalMutations/commands/06-pristine-positive.json`.
- Five per-mutant result documents: `.ufo/waves/round-22/residual/FinalMutations/list-refusal-deleted.json`, `.ufo/waves/round-22/residual/FinalMutations/stat-refusal-deleted.json`, `.ufo/waves/round-22/residual/FinalMutations/read-refusal-deleted.json`, `.ufo/waves/round-22/residual/FinalMutations/broad-exception.json`, `.ufo/waves/round-22/residual/FinalMutations/broad-baseexception.json`.
- Command receipts and unmodified stdout/stderr: `.ufo/waves/round-22/residual/FinalMutations/commands/`. For each mutant, stems `11-mutated-<mutant>`, `12-restore-<mutant>`, `13-restored-hash-<mutant>`, `14-restored-<mutant>` identify the relevant `.json`, `.stdout`, `.stderr` files.
- Canonical before/after source digests: `.ufo/waves/round-22/residual/FinalMutations/commands/05-canonical-digests.json` and `.ufo/waves/round-22/residual/FinalMutations/commands/15-canonical-after-digests.json`.
- Scaffold cleanup: `.ufo/waves/round-22/residual/FinalMutations/commands/16-remove-scratch-scaffolds.json`.

No production fix, contract change, integration, service run or additional test campaign is claimed or performed.
