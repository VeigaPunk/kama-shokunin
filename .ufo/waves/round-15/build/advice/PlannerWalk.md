# Round 15 PlannerWalk — duplicate-corpus guard

## Axes and boundary

- **Calibration: 7**, lowest assigned axis versus **operability: 8**. This walk concerns only the outside-R1 repair to the offline measurement corpus guard. It supplies no basis to change the numeric score or claim runtime restoration.
- Bounded to the historical runner, its frozen pre-edit source, the R1 verifier note, and the duplicate-corpus fixture descriptions. No source implementation or sibling artifact was edited.

## Reconstructed contract and one-case walk

The legacy promise recorded by the independent verifier is that duplicate corpora fail before children. The verifier's R1 says this was not true for a corpus with at least 16 distinct names: the old `corpus_problems()` enforced only the minimum unique count and did not compare declared-name count with unique-name count (`corpus/lessons/round-14-verifier-spotcheck.md:142`).

Concrete adversarial example: `tests/ollama-corpus-guard/PrependDuplicate.json`'s `PrependDuplicate-array` uses 17 names: `n15`, `n00` through `n14`, then `n15`. The total is 17; after the old runner's `strip()` canonicalization there are exactly 16 distinct names, so the old minimum is met while `n15` repeats. The adjacent padded control also presents `"  n15  "` and `"n15"`, which the runner's stripping makes equal. The test descriptions mark both duplicate cases as rejected.

Walking that data through the **pre-edit** logic in `.ufo/waves/round-15/frozen/measure-before.py`:

1. `load_cases()` accepts either an array or an object containing a `cases` array (`:109-128`).
2. `corpus_problems()` collects each nonblank string name after `strip()`, computes `unique`, and adds a problem only for `unique < MINIMUM_UNIQUE_CASES` (`:350-362`). For the 17-name example, its result is therefore `([], 16)` **[INFERENCE from the frozen source; not executed]**.
3. With no corpus problem and a present child tool, `run()` selects the `elif tool_present` branch and calls `measure_case()` for each case (`:365-385`). For a corpus cloned from the valid source fixture, `measure_case()` passes its required-field check and reaches `subprocess.run()` (`:211-251`). Thus the duplicate corpus reaches the child stage; if all 17 cloned cases stage successfully and the tool is present, the source path attempts 17 child processes **[INFERENCE; no child was started here]**.

Generalization: order does not affect `len(set(declared))`, and the array/object input envelope does not affect this guard. Any corpus whose stripped declared names satisfy `unique >= 16` but `len(declared) > unique` bypasses the old minimum-only check. This includes prepend, middle, distant, adjacent, append, and stripped-whitespace collisions represented in the current fixture inventory. A unique 16-name corpus instead has `len(declared) == unique == 16`, so the old minimum permits it to continue to measurement.

## Last-known-good and current divergence

The last-known-good measured corpus was the fixed round-14 set: the independent verifier recounts 51 cases / 51 unique names and verifies the recorded final run's 51 passed / 0 failed results (`corpus/lessons/round-14-verifier-spotcheck.md:68-82`). That result supports this actual unique corpus only; it does not establish the duplicate-rejection guarantee.

The round-15 source snapshot is anchored by `.ufo/waves/round-15/frozen/manifest.json`, which names `.ufo/waves/round-14/measure.py` and records source commit `6e348e28943849aceb08d6954dee92be48ce9ba8` and SHA-256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` (manifest values read; digest not recomputed). At the later read of `.ufo/waves/round-14/measure.py:350-425`, the source contained the new `len(declared) != unique` duplicate problem before the unchanged `<16` minimum check. Its `run()` still emits unmeasured corpus records when any corpus problem exists and only reaches the child loop in the `elif tool_present` branch. This is the intended structural correction and preserves the 16-distinct-name path by inspection; **no after-edit behavior is verified here**.

## Planner hand-off and limitations

- L1's decisive before/after case is the 17-name `PrependDuplicate-array` above paired with a valid 16-unique control. Confirm duplicate corpora produce corpus rejection before any child invocation, while the valid unique corpus still reaches normal measurement. This report supplies static reconstruction only, not that proof.
- The current `tests/ollama-corpus-guard/` listing contained fixture JSONs but no `check.py`; no test harness or latest round-15 verifier implementation was available in the listing at inspection.
- No CLI, child process, test, build, lint, formatter, or smoke run was invoked. No tool was installed or updated. The `lsp` device is not mounted (`read xd://lsp` reported no such tool); literal search was used only for discovery, not semantic proof.

**Confidence:** high for the old guard's source-level branch behavior and the 17-name count; inferred for actual subprocess count/outcome because no execution occurred; no claim about post-edit runtime behavior.

Report: .ufo/waves/round-15/build/advice/PlannerWalk.md
