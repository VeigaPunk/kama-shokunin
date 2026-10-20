VERDICT: confirm — The frozen C2 before-count reproduces: 6 accepted-bad, K3 inconclusive, and K0 accepted.

Axes attacked: frozen-input identity; per-control and aggregate count fidelity; fake-server cleanup.

## Findings

- No discrepancy in the scoped before-count. The recorded run has `accepted_bad: 6` and `good_ok: true` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json:2,4-18`); K3 is inconclusive (`tool_exit: 2`, `gate_exit: 1`, `attributed: false`) in the same file at lines 58-73; aggregate `gate_flip_bad: 0`, `inconclusive: 1`, `good_ok: true`, and the expected tool/gate SHA-256 values are at lines 176-181. The rerun emitted the same aggregate values and substantive outcomes for k0-k8. K0 remained accepted with tool/gate exit 0; K3 remained inconclusive. K6’s traceback differed only in its generated temporary-directory name.
- Frozen-input identity matched the recorded hashes: tool `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`, gate `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json:177,181`).
- The controls command’s process exit 1 is expected for this baseline, not a rerun mismatch: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:687-696` returns 0 only when accepted-bad, gate-flip-bad, and inconclusive are all zero and the positive control passes; this frozen baseline has 6 and 1, respectively.

## Commands and observed exit codes

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RerunControlsFrozen-clone && git -C /tmp/KamaR17.RerunControlsFrozen-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && echo CLONE_OK` — 0.
- `cd /tmp/KamaR17.RerunControlsFrozen-clone && sha256sum .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py .ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py && wc -l .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py .ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py tests/llamacpp-live/controls.py` — 0; hashes matched the recorded run.
- `cd /tmp/KamaR17.RerunControlsFrozen-clone && PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/controls.py --tool /tmp/KamaR17.RerunControlsFrozen-clone/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py --gate /tmp/KamaR17.RerunControlsFrozen-clone/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py --json > /tmp/rcf-frozen-rerun.json 2> /tmp/rcf-frozen-rerun.err` — controls.py exit 1 (explicitly captured as `EXIT=1`); JSON was 4,436 bytes and stderr was empty. Exit 1 is the expected dirty-baseline signal described above.
- `if test -e /tmp/kama-live-controls-d82lrx9h; then printf 'replay-temp=present\\n'; else printf 'replay-temp=absent\\n'; fi; ps -o pid,ppid,lstart,args -p 3590955,3590947,3590953,3590946,3625771,3620431,3620447; ss -ltnp` — 0; the replay temp directory was absent. `ss` showed loopback listeners from concurrent local activity; I did not attribute or terminate those processes. The harness also runs fake-group cleanup in `finally` and scopes its workspace with `TemporaryDirectory` (`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:660-667`).

## Residual risk and verification gaps

This confirms only the requested frozen C2 before-count; it does not rerun the current tool/gate or independently validate live b11755 runs. Concurrent loopback Python listeners were present in the host-wide `ss` snapshots, so they were left untouched rather than presumed to belong to this replay. No installs.
