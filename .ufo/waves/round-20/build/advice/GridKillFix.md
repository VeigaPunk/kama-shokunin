VERDICT: confirm - grid rejects only observed gate verdicts and treats evaluation errors as exit 2

Axes: calibration (errors are not verdicts) and operability (grid exit semantics).

## Change
- Scratch base: `37bd4c5bd456a2f8a54d3312c28495c321715856`; `git show 37bd4c5bd456a2f8a54d3312c28495c321715856:tests/llamacpp-live/install-tree-grid.py > /tmp/kama-r20-GridKillFix/base-install-tree-grid.py && sha256sum /tmp/kama-r20-GridKillFix/base-install-tree-grid.py /tmp/kama-r20-GridKillFix/lane/tests/llamacpp-live/install-tree-grid.py` -> exit 0; frozen grid SHA-256 `6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05`.
- Patched only `tests/llamacpp-live/install-tree-grid.py` in `/tmp/kama-r20-GridKillFix/lane`; the lane source was not edited.
- `rejected` now requires gate exit 1, stdout beginning exactly `INVALID `, and no traceback marker in stdout/stderr. Exit 0 with `VALID ` is `accepted`; silent/mismatched exits, other codes, signals, tracebacks, launch failures and timeouts are `error`.
- Gate stderr is retained as a 200-character excerpt; when it contains `Traceback (most recent call last):`, the excerpt starts at that marker. Any member error or non-VALID baseline returns 2. A grid-level unexpected exception also returns 2.
- Selftest covers genuine VALID/INVALID, crash (uncaught raise), silent exit 1, signal, unknown exit 7, stderr-only INVALID, INVALID followed by traceback in stderr, traceback text in stdout, timeout, absent member, and invalid baseline.

## Exit-map note
- Observed historical absent-member behavior is preserved: absent row -> exit 1. The base selftest explicitly expected exit 1 (`install-tree-grid.py:190-191` at the frozen revision). I notified L1 that its planned registry map says absent -> 2; this is a mismatch, not silently changed here.
- Gate grammar basis: `tests/llamacpp-live/check-receipt.py:2233-2236` at the frozen revision prints `INVALID ...` and returns 1 for validation problems.

## Executed evidence
- `python3 tests/llamacpp-live/install-tree-grid.py --selftest` in scratch -> exit 0; output: `selftest: genuine verdicts, absent/bad input, crash, silent exit 1, signal, unknown exit, post-INVALID tracebacks, stderr-only INVALID and timeout passed`.
- `python3 /tmp/kama-r20-GridKillFix/capture_grid_transcripts.py` -> exit 0. Retained child transcripts show frozen grid crash gate: baseline VALID, 3/3 rejected, grid exit 0; fixed grid: baseline VALID, rejected 0/3, errors 3, grid exit 2; fixed selftest exit 0.
- `python3 /tmp/kama-r20-GridKillFix/capture_unicode_transcript.py` -> exit 0; its child grid exited 2 for a gate that printed `INVALID synthetic` then raised `UnicodeEncodeError`. The row is `error`, with the bounded traceback excerpt retained.
- Patch generation `diff -u --label a/tests/llamacpp-live/install-tree-grid.py --label b/tests/llamacpp-live/install-tree-grid.py /tmp/kama-r20-GridKillFix/base-install-tree-grid.py /tmp/kama-r20-GridKillFix/lane/tests/llamacpp-live/install-tree-grid.py > /tmp/kama-r20-GridKillFix/grid.patch` -> exit 1 (expected differences), 12,553 bytes.
- `cmp -s /tmp/kama-r20-GridKillFix/lane/tests/llamacpp-live/install-tree-grid.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GridKillFix/install-tree-grid.py` -> exit 0; `cmp -s /tmp/kama-r20-GridKillFix/grid.patch /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/GridKillFix/grid.patch` -> exit 0.

## Deliverables / retained evidence
- `.ufo/waves/round-20/build/out/GridKillFix/grid.patch` — SHA-256 `09141504c80c484ceb66b9b852f78413af8d13d69b7dfc66a74b2aae1d472afe`.
- `.ufo/waves/round-20/build/out/GridKillFix/install-tree-grid.py` — full patched file, SHA-256 `083c50b8e8953e100ef9203fa00cd543df5651d09db187957a845e78a42adb16`.
- Transcripts: `transcripts/red-before-base-grid-crash-gate.txt`, `transcripts/green-after-fixed-grid-crash-gate.txt`, `transcripts/green-after-fixed-grid-selftest.txt`, `transcripts/post-INVALID-UnicodeEncodeError.txt`.
- No tools were installed or updated. No live server was launched.

[INFERENCE] The additive JSON `errors` count and `baseline=ERROR` label were not checked against downstream JSON schema consumers; L1 owns integration and the official post-integration gate. No known implementation blocker.
