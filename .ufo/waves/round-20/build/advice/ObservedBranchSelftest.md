VERDICT: confirm - The observed-digest mutant is killed and the integrated CLI/selftest coverage passes.

Axes: calibration (observed-digest branch deletion changes from survivor to killed); operability (unusable registry/git/docs are consistently could-not-evaluate).

Integrated the observed-digest selftest with `build/out/CitationExitFix/citation.patch` in the private scratch clone at `37bd4c5bd456a2f8a54d3312c28495c321715856`. Also added fail-closed JSON-row schema validation: a registry row that is not an object raises stable `ValueError("registry rows must be JSON objects")`, which the existing CLI contract maps to exit 2. No production verdict mapping for missing, mismatching, off-ref, or unresolved revisions was changed.

The exact observed-digest test gives the registry and document the same digest that differs from the committed blob, then requires `missing=0, mismatch=1, verified=0`. Earlier isolated red/green evidence remains in `out/CloseKama18.ObservedBranchSelftest-2/transcripts.txt`: the old 15-case selftest passed after deleting the observed-digest branch; the added case failed on that mutant; restoring the branch passed 16 cases.

Integrated final source: `out/CloseKama18.CitationFinal-2/citation-provenance.py`. Final selftest transcript: `out/CloseKama18.CitationFinal-2/selftest-transcript.txt`. The complete source's `--selftest` was run once after integration: `selftest: ok (24 cases)`, exit 0. The dynamic count reports 15 direct `check()` invocations plus 9 CLI subprocess invocations; the non-invocation `DEFAULT_DOCS` assertion is excluded. Cases include malformed registry `[1]` → 2; missing/unusable Git or docs → 2; missing/mismatch/off-ref/unresolvable-revision verdicts → 1.

Baseline source anchor at `37bd4c5bd456a2f8a54d3312c28495c321715856`, `tools/citation-provenance.py:100-101`:
> `elif error is not None or observed != want:`
> `    status = "mismatch"`

Scope: all source edits and the final selftest ran only in the private scratch clone; no lane source was edited. No tools were installed. LSP was unavailable in the mounted tool inventory. No build, lint, formatter, live server or model was run.

Risk: unresolved Git revisions remain reported as mismatch/exit 1, as required for a citation verdict; the selftest now protects that behavior. [INFERENCE] The parent should copy only the integrated final source after reviewing the retained transcript.
