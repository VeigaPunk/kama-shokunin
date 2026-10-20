# Round 11 measurement mutation designs
Review/access date checked with `date -u` after the local reads: `2026-10-20T02:15:07Z`. Evidence reviewed here is local wave/repository content; no public vendor source was opened in this slice.

## Axes and contract basis

The two C1 axes are provenance-field completeness and original-prefix integrity. The assigned measurement contract says the `provenance` mode reports `legacy_files`, `missing_files`, `missing_fields`, and `prefix_violations`; it exits 1 for missing fields or a changed prefix, 0 when clean, and 2 for invalid input. These are design expectations from the wave specification, not outputs I ran. The baseline manifest lists nine legacy files; `alias-endpoint-normalization.md` has original SHA-256 `a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93`, 7,595 bytes, and all three fields missing. Its observed first line is `# Alias endpoint normalization` (current read, lines 1–3); the digest/size are the baseline manifest's historical values, not a hash of a post-edit file.

Use a disposable scratch copy of the completed tree, leave the working tree untouched, and use the same `provenance` command for clean, mutant, and restored states. The command shape below assumes the planned positional mode and `--root`/`--baseline` options; confirm argv against `measure.py` before parent execution, since that file was not present when I checked. Keep the original scratch file separately and record its pre-mutation SHA-256; do not infer or fabricate a post-edit hash.

## C1 negative controls

1. **Delete exactly one field.** On a scratch copy, remove only the column-zero `recheck:` line from the round-11 supplement in `corpus/knowledge/alias-endpoint-normalization.md`; leave every other byte unchanged. Run:

   `python3 .ufo/waves/round-11/measure.py provenance --root "$scratch" --baseline .ufo/waves/round-11/legacy-baseline.json`

   **Expected, not observed:** exit `1`; finding counters `missing_files=1`, `missing_fields=1`, `prefix_violations=0`, `legacy_files=9`. This specifically kills the mutant by `missing_fields` (and identifies its containing file through `missing_files`); it must not be mistaken for a prefix failure.

2. **Alter one original-prefix byte.** Starting from exact restored bytes (or a fresh scratch copy), replace only the first byte of that same file from `#` to `!`; preserve the appended provenance section. Run the identical detector command.

   **Expected, not observed:** exit `1`; `missing_files=0`, `missing_fields=0`, `prefix_violations=1`, `legacy_files=9`. The concrete finding is `prefix_violations`, rather than a missing-field result.

For each probe, record the target file SHA-256 before mutation and after restoration, then require equality. Restore from the saved pristine copy, rerun the same detector, and expect exit `0` with `missing_files=0`, `missing_fields=0`, `prefix_violations=0`, `legacy_files=9`. Also record the untouched pristine run as exit `0` with those same counters. Do not combine the two defects: separate probes make each finding independently attributable. No mutation or detector run was performed for this advisory assignment, so these outputs and exit codes remain predictions, not evidence of a kill.

## C2 counterexample for semantic review

Use a documented-shape counterexample, not a runtime observation: the hypothetical served state has a non-empty Ollama `GET /api/tags` available-model inventory, but an empty `GET /api/ps` running-model inventory. The identity record should then state `available=present`, `loaded/running=absent`, `alias identity=not established by availability alone`, and `readiness=undetermined`. This is the concrete case `available_without_loaded_model`. It falsifies any crosswalk wording that treats an available tag as proof that its weights are loaded or that the service is ready.

Grounding: `corpus/SOURCES.md` S011 (line 23) scopes `/api/tags` to locally available models and says availability is not proof of loaded state; S012 (line 24) scopes `/api/ps` to models loaded into memory/running. The existing health matrix also separates those routes at `corpus/knowledge/runtime-health-surface-matrix.md:17` and cautions that documentation does not establish a current local runtime at `:22`. Thus this counterexample is a semantic review case, not a measured response or a claim about any live Ollama server. The planned `crosswalk` measurement is existence/provenance evidence only; human review must check that the new entry preserves these distinct meanings and does not turn inventory into readiness.

## Limits

I read the wave specification and the cited local source rows. I did not run tests, mutate files, invoke a runtime, or install tools. The measurement implementation and new crosswalk entry were not yet present at the time of my reads, so exact CLI rendering and the eventual entry wording remain unobserved. No tool install/update was needed.