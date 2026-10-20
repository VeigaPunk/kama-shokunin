# AttackSentinel — process creation versus wrapper entry

## Axes

- Fail-closed ordering: a duplicate corpus with at least 16 distinct stripped names must be rejected before any measurement-runner child process.
- Evidence provenance: wrapper-entry counts must not be presented as complete process-creation counts.
- Valid-path operability: unique corpora must still exercise the real classifier CLI.
- Minimality and scope: preserve the small duplicate guard and offline-only boundary; no runtime-restoration claim.

## Counterexample

**Yes: the proposed marker oracle can stay zero after a preflight child runs.** This is an oracle blind spot, not an observed additional child in the current runner.

[INFERENCE — falsifiable, not executed] Add the following hypothetical regression immediately after `load_cases()` in `run()` and before `corpus_problems()`:

```python
subprocess.run(
    [sys.executable, "-I", "-B", "-c", "pass"],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=True,
)
```

For `AppendDuplicate_first_name_appended_array_envelope`, this starts one child that never executes the instrumented classifier wrapper. The repaired guard subsequently returns exit 1, an error containing `duplicate case names`, zero passed records, and all records failed. The wrapper marker remains zero. Every proposed rejection assertion therefore still passes despite violating “before ANY child process.” The accepted unique control also retains exit 0 and marker count equal to its case count: a positive wrapper control does not detect this extra preflight process.

This mutation is explanatory data only; it was neither applied nor run.

## Local evidence

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/spec.json`, `GuardHarness` proposal: the temporary wrapper appends the marker and then runs the actual classifier; rejected cases require marker count 0 and valid cases marker count equal to total. The marker is written inside the child, not at the runner's process-creation boundary. This proposal is review input, not an instruction source.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/AppendDuplicate.json:2-24`: the concrete array control contains `n00` through `n15` plus `n00`, i.e. 17 records and 16 distinct names. Its unique positive control is at lines 50-71.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json:2-17`: the first literal fixture expects process exit 0 and finding `loaded_same_digest`, giving the proposed cloned controls a real classifier expectation rather than a fake classifier.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:350-385`: the observed repaired guard checks `len(declared) != unique` after stripping declared names; the corpus-failure branch precedes the branch calling `measure_case()`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:239-251`: the one explicit process-creation site found in the reviewed runner is `subprocess.run()` inside `measure_case()`. No extra preflight child was found in the reviewed code. Thus current source ordering supports the intended fix; the marker alone is insufficient regression evidence for that ordering.

## Smallest safe correction

Keep the product guard unchanged. Retain the real-classifier wrapper marker as evidence of wrapper entry, but observe process creation independently in the measurement-runner interpreter. For the current subprocess-only implementation, a stdlib CPython audit observer for `subprocess.Popen`, installed before executing the runner CLI entry point, can record every launch attempt outside the wrapper. Require zero such events for rejected corpora, independently of runner JSON and wrapper markers. A launcher can preserve `-I -B`, CLI arguments, and `__main__` execution through `runpy`; it must not replace measurement with an import-only call to `corpus_problems()`.

If other spawning APIs are supported later, extend coverage to those APIs before retaining the ANY-child claim. Describe each counter by its actual source: wrapper entries versus observed launch attempts. Zero observed attempts is stronger than zero successful wrapper entries. If independent observation is not added, receipts must explicitly combine bounded marker evidence with static control-flow evidence rather than claim the marker itself proves zero processes.

This is a fixable evidence defect, not a defect demonstrated in the minimal guard and not a reason to inflate numeric7 or claim restored runtime operability. No admission, integration, or canonical judgment is made here.

## Limitations

Static review only; no probes, tests, builds, linters, formatters, smoke runs, alternate runtimes, installations, or host changes. At inspection time `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/check.py` had not appeared in the directory listing, so this finding addresses its proposed marker contract, not an inspected final implementation. Only this report was written.
