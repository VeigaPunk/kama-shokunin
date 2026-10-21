VERDICT: partial - pinned round-20 source already returns 2; CLI regression coverage added.

Axes: calibration (7, assigned lowest) and operability (8). This move addresses the citation instrument's calibration/error classification.

## Findings

- The requested exit-1 defect did not reproduce at `37bd4c5bd456a2f8a54d3312c28495c321715856`. The frozen `tools/citation-provenance.py` already catches unusable git/registry exceptions and returns 2 (`:221-226`); unreadable docs return 2 (`:238-241`); clean/missing/mismatch/off-ref outcomes retain 0/1 classification (`:240-241`). Its docstring says the same at `:19-20`.
- Executed exact CLI probes: unusable `--lane` exit 2; missing `--docs` exit 2 (`docs_unreadable=1`); missing registry exit 2. Commands and complete observed output are retained in `build/out/CitationExitFix/citation-exit-transcripts.txt`.
- Therefore the patch does not alter production classification. It extends the instrument's own `--selftest` with five subprocess CLI cases asserting exit 2 for unusable git, registry, and docs, and exit 1 for missing and mismatching citations. Those CLI checks would have caught the routed regressions, unlike the prior helper-only checks (`:152-197`). Patch: `build/out/CitationExitFix/citation.patch`.

## Red/green evidence

- Red: in the scratch clone only, I temporarily changed both main error returns (caught unusable input and unreadable docs) from 2 to 1. `python3 /tmp/kama-r20-CitationExitFix-2/lane/tools/citation-provenance.py --selftest` reported `SELFTEST FAIL` for unusable-git, unusable-registry, and unreadable-doc; observed selftest exit 1.
- Green: restored those returns to 2 and ran the same command; output `selftest: ok (20 cases)`; observed selftest exit 0. Full transcripts preserve stderr, wrapper exit, and the invoked process exit. The pre-existing helper unreadable-doc case also emits its expected `cannot read` diagnostic during green.

## Scope and limitations

- Scratch checkout command observed exit 0 and exact HEAD `37bd4c5bd456a2f8a54d3312c28495c321715856`. Source edits, including the temporary red mutant, were confined to `/tmp/kama-r20-CitationExitFix-2/lane`; the lane checkout was not edited.
- [INFERENCE] The round-19 exit-1 observations likely came from different source bytes or invocation conditions; retained inputs do not establish which. No claim is made that the production classification changed here.
- LSP was unavailable in the mounted tool inventory; source was inspected with exact file ranges. No tools were installed or updated.
- Checks run: only the requested reproduction commands and `--selftest` red/green probe. No build, lint, formatter, or unrelated tests were run.