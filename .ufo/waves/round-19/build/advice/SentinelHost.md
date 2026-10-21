VERDICT: partial - no package/service/boot action or leaked llama-server, but recorded runs opened real loopback listeners and unrelated long-lived host listeners remain.

Axes: host mutation; listener lifetime.

Severity: LOW for the lane-owned lifecycle (no persistent llama-server observed); MEDIUM if the fake-only listener bound applies literally to L1’s live measurements.

Exploit path: `.ufo/waves/round-18/runs/run.py:61-64` launches three actual `llama-server` child runs through the live producer. A same-host process could connect while each run is ready; this is not an ephemeral fake. It is short-lived, not externally bound, and the recorded teardown closes it.

Evidence: No package/service/boot invocation appears in the changed runner, gate, grid, producer or task prompts. The existing `runs/commands.json` records `live-1..3` exit 0; each corresponding receipt records child ownership, SIGTERM sent, no SIGKILL, returncode 0 and `port_refuses=true` (loopback ports 40999/36277/43877). Current `pgrep -a -x llama-server` found no process (pgrep exit 1; logger exit 0). `ss -ltnp` at 2026-10-21T03:34:10-03:00 still showed long-running loopback listeners owned by `omp` and agent shims; `ps` showed their start times >3h and >17h. The same snapshot showed an unowned `127.0.0.1:40443` and a short-lived Python listener. These host listeners are not attributable to the lane [INFERENCE]; no service/process action was taken. Receipts and exact command output are in `/tmp/kama-r19-SentinelHost/out/audit-receipt.md` and sibling `.txt` files.

Impact: No evidence of a leaked lane server or network-facing model listener. However, the strict host-wide “only ephemeral fakes/no persistent listeners” condition is not met by the observed host state; the listener snapshot cannot be represented as clean.

Smallest remediation: If fake-only is binding for L1 runs, do not rerun the `live-*` segment without an explicit scope exception. Keep host infrastructure untouched; the owning runtime must classify its persistent listeners or provide a scoped exclusion.