VERDICT: confirm - added absent and malformed install-tree digest mutations to the copied receipt-gate selftest.

Axis: operability (selftest rejection coverage); calibration is unchanged. The copied `tests/llamacpp-live/check-receipt.py` adds `tree-sha-absent-expect` (`install_tree_sha256=None`) and `tree-sha-malformed-expect` (`install_tree_sha256="not-a-digest"`); both include `--expect-install-tree-sha256 <base_tree>` and expect exit 1. Mutation entries: `/tmp/kama-r19-TreeAbsentCase/out/mutation-entries.json`.

Receipt: `/tmp/kama-r19-TreeAbsentCase/out/receipt.md` records executed copy and output-directory creation commands (exit 0, empty output). Gate selftest was not executed; parent owns post-integration gates. [INFERENCE] Both mutations should be rejected by the existing validator's digest validation and tree-pin requirement; no runtime result is claimed.
