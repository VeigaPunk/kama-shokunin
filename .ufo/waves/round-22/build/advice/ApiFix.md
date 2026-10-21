# ApiFix — round 22

## Owned change
- ` .ufo/waves/round-22/build/sandboxes/ApiFix/tools/kama-llamacpp-live.py` (sandbox only): `install_tree()` now raises `SetupError` with exact `.code == 'install-tree-unpinnable'` and a deterministic operation/member/`strerror` detail chained from the original `OSError`, on listdir, lstat, and regular-file read errors. No partial map or digest is returned. Symlink/nonregular skipping and the successful map/digest calculation are unchanged.
- The existing `SetupError(code)` behavior is retained; optional detail is included in its rendered text and, when present, in the receipt's `setup_error`, preserving the `install-tree-unpinnable:` receipt prefix. Existing install-links error codes (including `not-hashed`) are unchanged.
- Updated the producer docstring and `_install_identity_selftest()` with a successful-map-and-digest control plus isolated listdir, lstat, and read fault injections that require typed refusal, operation/member detail, chained `OSError`, and one reached injection.

## Evidence and limits
- Inspected the sandbox producer's `SetupError`, `install_tree`, `install_links`, main receipt handler, and install-identity selftest before editing. Also inspected the Matrix oracle's exact `.code` comparison and the existing end-to-end `setup_error.startswith('install-tree-unpinnable:')` expectation; this informed separate error code and receipt detail handling.
- The edit tool reported the resulting sandbox spans under `tools/kama-llamacpp-live.py` (snapshot `4249`).
- No tests, builds, linters, formatters, or smoke runs were run, as required during this wave. No tools were installed. No LSP route was available in the provided tool set; symbol locations were found with repository search and source reads.
- Parent message after the resumed turn reported that L1 had integrated the canonical producer change and Matrix in the lane checkout. This seat made no lane-checkout edits and did not inspect or reconcile against that later integration. The sandbox draft is not an instruction to integrate a duplicate.
- Parent reported the original turn terminal-failed on capacity; this report records only the resumed seat's sandbox change. No peer was woken after that notice.

## Blockers / risk
- None for the scoped sandbox implementation. Integration and official post-integration verification remain with L1; no verification result is claimed here.
