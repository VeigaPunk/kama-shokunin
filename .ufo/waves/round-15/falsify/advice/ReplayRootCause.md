# ReplayRootCause — minimum-only corpus guard

## Axes

- **Original guard behavior:** did the pre-R1 runner reject duplicates independently of the 16-unique-name floor?
- **Causal distinction:** do observations prove duplicate rejection before children, rather than a missing/unlaunchable classifier?
- **Positive-path preservation:** does a valid unique corpus still reach and pass real classifier measurement?

## Reconstructed contract and original failure

The runner documents that a corpus with fewer than 16 unique case names **or any duplicate** must fail before a child is spawned (`.ufo/waves/round-14/measure.py:13-14, 66-77`). The frozen original is tied by `.ufo/waves/round-15/frozen/manifest.json` to source commit `6e348e28943849aceb08d6954dee92be48ce9ba8` and SHA-256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`.

In that frozen source (`.ufo/waves/round-15/frozen/measure-before.py:350-362`), `corpus_problems` collects only nonblank string names after `strip()`, computes `unique = len(set(declared))`, and adds a problem only when `unique < MINIMUM_UNIQUE_CASES` (16). It does not compare the declared-name count with the unique count. Therefore the exact missed case is **17 declared rows, 16 distinct stripped names**: the old test is `16 < 16`, false, so no corpus problem is produced. A smaller duplicate case with only 15 distinct names is rejected by the minimum floor, but cannot establish that duplicates themselves are detected.

The old `run()` path (`measure-before.py:365-395`) sends nonempty corpus problems to unmeasured records; otherwise, when `tool_present`, it loops over every fixture and calls `measure_case` (`:375-383`). `measure_case` stages each fixture and calls `subprocess.run` (`:211-251`). Thus, with a present tool, the 17-row/16-unique counterexample bypasses the corpus gate and attempts per-row child measurement. This is a source/control-flow reconstruction, not an execution observation.

The committed boundary fixture supplies that counterexample literally: `tests/ollama-corpus-guard/ValidBoundaries.json:112-133` has `vd00` through `vd15` followed by a second `vd00` (17 rows, 16 distinct), expected rejected. The matrix loader independently checks at least 16 distinct stripped names and requires a rejected case to contain a duplicate (`check.py:192-210`), avoiding the minimum-floor confound.

## How the positive baseline separates unsupported-tool output from the bug

A failing exit or zero classifier invocations alone is ambiguous. The runner explicitly emits `unsupported` and exits 1 when the classifier tool is absent (`measure.py:34-40, 372-393`); the historical `capability_absent` receipt in `.ufo/waves/round-14/acceptance.json` records this exact state: `tool_present: false`, `passed: 0`, `failed: 51`, null `observed_exit`, `observed_finding: "unsupported"`, and `tool absent` reasons. That is not evidence of duplicate rejection.

The same receipt's `final_corpus` record is the positive baseline: the tool was present with a recorded SHA-256, the corpus had 51 unique names, and all 51 fixtures passed; the first fixture records child exit 0 and the expected classifier finding/schema. This establishes historical valid-corpus measurement, but—because that corpus is all unique—does not test the duplicate guard.

The committed corpus-guard harness makes the distinction explicit. It clones a fixture with `expected_exit == 0` (`check.py:229-254`), wraps the real classifier so each child writes a marker and then runs the classifier (`:289-309`), and audits process-creation events while executing the real runner (`:257-286`). For a rejected duplicate corpus, grading requires exit/verdict 1, an error containing `duplicate case names`, `tool_present is true`, null observed child exits for all rows, zero classifier markers, and zero runner process events/Popen events (`:528-575`). For a valid corpus it requires all rows pass and both classifier markers and `subprocess.Popen` events equal the row count (`:576-604`). A missing tool therefore cannot masquerade as the target bug, while the positive control demonstrates that child measurement is actually operable. The exact-16-unique positive controls are in `ValidBoundaries.json:2-23` and `:64-86`.

## Current divergence and confidence

Current `.ufo/waves/round-14/measure.py:350-364` now adds `len(declared) != unique` as a `duplicate case names` corpus problem before preserving the existing minimum check; `run()` still routes corpus problems through the pre-child branch (`:374-385`). This closes the static source gap while preserving the 16-name floor. No behavioral conclusion about the repair or matrix is claimed here; the falsification wave did not run checks.

**Confidence: high** that the frozen implementation had the minimum-only defect and that the 17-row/16-distinct control exposes it when the tool is present. Confidence is static: no runner, harness, classifier, test, or build was executed. The mounted tool inventory has no `lsp` device (`xd://lsp` returned “No such tool”), so this evidence uses direct source and committed-artifact reads, not semantic LSP references. No tools were installed or updated.
