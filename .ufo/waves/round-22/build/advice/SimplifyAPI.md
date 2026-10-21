# SimplifyAPI — C1 fail-closed identity

## Axes and recommendation
- Correctness: incomplete enumeration/stat/member reads must not produce a usable identity.
- Compatibility: preserve `(tree, combined)` success return, byte-for-byte digest construction, and intentional symlink/nonregular exclusion.
- Simplicity/maintainability: reuse `SetupError`; add neither an error subtype nor a third return field nor an error-collection API.
- Operability: use stable `install-tree-unpinnable` token; leave separate link-policy diagnostics intact.

Smallest recommended change: replace each of the three `install_tree` OSError fallback bodies with `raise SetupError('install-tree-unpinnable') from exc`, binding the exception in the existing handlers. This keeps current control flow and all successful identity computation unchanged. A single enclosing OSError handler would also work but unnecessarily reindents the function. No helper abstraction is justified by three identical, local raises.

## Source evidence (read-only)
Observed `tools/kama-llamacpp-live.py`:
- Lines 171–176: `sha256_file` opens and reads the member inside the call; its OSError reaches the existing member handler.
- Lines 178–202: listdir failure returns `(tree, None)`; lstat failure and member-hash failure continue. These are the three failure-escape paths to remove. Only the `not stat.S_ISREG` skip remains intentional.
- Lines 200–202: success digest is SHA-256 over sorted `name sha\n` records. Leave this expression and successful return untouched, including valid empty-directory behavior.
- Lines 1414–1419 and 1602–1603: producer already consumes the two-item tuple and catches `SetupError`, storing `.code`. No new producer adapter is required.
- Lines 213–262: `install_links` independently owns symlink text, target restrictions, special-file policy, loader-searched directory rejection and unpinned-directory reporting. Do not combine it with `install_tree` or delete its `not-hashed` check: separate scans can observe changed membership, and callers may explicitly supply a partial map.
- Lines 1135–1162: existing selftest compares exact regular-member map and asserts that symlink retargeting does not change regular-tree identity. Lines 1188–1190 explicitly exercise the supplied-partial-map `not-hashed` check.
- Literal search of tools and tests/llamacpp-live identifies direct external test callers in `install-links-grid.py:177–181` and `unpinnable-e2e.py:72–75`, and a colon-required setup token predicate at `unpinnable-e2e.py:91–94`. CallerRepair owns adaptations; consumers must accept the bare token without treating unrelated prefixes as equivalent.

## Deletion candidates / stop boundary
Remove only the three silent failure fallbacks, replacing them with explicit refusal. Do not delete any public function, tuple field, link-policy check, historical provenance, or successful hashing operation. The next apparent simplification—removing `install_links` or its partial-map guard—would harm preserved policy or race coverage.

The `xd://lsp` device is unavailable (tool discovery returned “No such tool”). Reference information above is literal grep/read evidence, not semantic no-caller proof. No API deletion is proposed on that basis.

## Evidence limits and handoff
No builds, tests, linters, formatters, smoke runs, service launches or verification commands were run. Successful-behavior preservation is a source-level conclusion, not a measured green result. L1 should run the existing install-link grid and producer identity selftest plus the new frozen/current I/O fault-injection grid after integration; the existing permission-dependent selftest alone cannot establish all fault cases. No endpoint-health/authentication claim is made.

No production files were written; no scratch code was necessary for this read-only assessment. No shared-tree byte-identity verification was run under the build-wave prohibition, so this report does not claim a measured whole-tree equality result. No tools were installed or updated. Recommendation sent to ApiFix.

Owned/written path only: `.ufo/waves/round-22/build/advice/SimplifyAPI.md` (append-only after this write).

Report: .ufo/waves/round-22/build/advice/SimplifyAPI.md
