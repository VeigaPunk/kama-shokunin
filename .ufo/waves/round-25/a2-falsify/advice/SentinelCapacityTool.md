Verdict: defect found — all five wave-1 risks remain open; teardown now blocks a success result for an unclosed port, but can still launch another cell when host-idle state is unknown.

Static review only. Target: `fa3b62ae6475d111eb466d79af616aeebb08bbb9`. No `llama-server` child was started and no live port was probed. I ran no checks. The reviewed working-tree files match the target commit by SHA-256: `git show fa3b62ae6475d111eb466d79af616aeebb08bbb9:tools/kama-context-capacity.py | sha256sum` and `sha256sum tools/kama-context-capacity.py` each printed `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27`; the corresponding `kama-llamacpp-live.py` commands each printed `8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3` (exit 0).

## Per-risk findings

1. **OPEN — HIGH — Listener ownership.**
   - **Exploit path:** The runner accepts `/props` as ready, then checks that the child owns the listener once. If the child exits or the listener changes after that check, a different local listener can answer the raw captures, later property reads, or load requests and its data can be recorded.
   - **Evidence:** `tools/kama-context-capacity.py:326-343` performs the readiness GET and one `live.verify_live(proc, port, 'ready')` call. Reads then proceed at `:345-374` with no further ownership check. `tools/kama-llamacpp-live.py:719-731` defines the ownership gate, while `:483-503` shows `http_get` itself only makes the loopback request.
   - **Impact:** A receipt can include observations or request outcomes from a non-fixture listener; load traffic can reach that listener.
   - **Smallest remediation:** Check child ownership immediately before and after each response-producing capture/read/request, and reject any false or unknown result.

2. **OPEN — HIGH — Cleanup on all exits.**
   - **Exploit path:** The server is launched in a new session, with no termination handler or parent-death option in this `Popen` call. A wrapper SIGTERM can therefore terminate the wrapper without signaling the child. Also, the interval between `Popen` returning and entry into the cleanup `try/finally` is not protected; interruption during `_teardown` can interrupt its own signal/wait sequence. **[INFERENCE]** Under the default SIGTERM action, the wrapper exits without Python cleanup, while the separate-session child can remain alive.
   - **Evidence:** `tools/kama-context-capacity.py:303-325` launches with `start_new_session=True` and enters the cleanup `try` only after setting `started_utc`; `:375-377` calls teardown only from that `finally`. `_teardown` has no interruption suppression or outer retry at `:556-595`. The outer `BaseException` handler at `:821-837` records an error but has no child handle or cleanup fallback.
   - **Impact:** An orphaned server may retain its listener after the tool exits.
   - **Smallest remediation:** Install termination handling before launch, protect teardown from interruption, and place child kill/reap in an outer guaranteed cleanup path; treat failure to reap as failure.

3. **OPEN — HIGH — Teardown gate / stop before another run.**
   - **Exploit path:** The old false-success path is partly fixed: a cell is not observed unless it has a return code and `port_closed is True`, and exit 0 requires all recorded ports closed. However, the loop does not stop after a cell's teardown fails. `wait_for_host_idle` treats unknown process state as idle, allowing another launch while a prior child may remain.
   - **Evidence:** The improved cell gate is `tools/kama-context-capacity.py:396-407`; exit 0 also requires every cell's `port_closed` at `:817-820`. The per-cell loop continues after `run_cell` at `:788-806`. `live_llama_server_pids` returns `None` on process-query errors at `:218-224`, and `wait_for_host_idle` returns success for either `None` or an empty list at `:241-253`. `ss_listen_lines` does not inspect `proc.returncode` at `:207-215`, so a failed `ss` command with empty stdout can appear to have no listener.
   - **Impact:** A failed teardown cannot produce the intended successful claim result through the normal gate, but it can still be followed by another child, violating one-child-at-a-time cleanup. Unknown process/listener state is also treated as safe.
   - **Smallest remediation:** Stop immediately unless teardown positively proves reaping and closure; distinguish `pgrep`'s no-match result from errors and fail closed on unknown status; check `ss`'s exit status.

4. **OPEN — MEDIUM — Scratch containment.**
   - **Exploit path:** A caller can set `--scratch` or `--out` to arbitrary paths. The deterministic server log is opened with truncating `open(..., 'wb')`; raw response/log files and the receipt are also written without resolved-path containment or no-follow/exclusive creation. A pre-existing symlink at a predictable log/raw filename can redirect writes.
   - **Evidence:** The default scratch is not attempt-specific (`tools/kama-context-capacity.py:58-61`); CLI paths are unrestricted at `:654-666`. `:766-773` creates the chosen scratch and, when `--out` is set, places raw files beside that output. The server log path and truncating open are at `:299-311`; raw files use `write_bytes` at `:420-427` and `:392-394`; receipt output is unrestricted at `:839-843`.
   - **Impact:** Tool writes can escape the authorized scratch/output areas or truncate a file reached through a symlink.
   - **Smallest remediation:** Resolve and enforce approved scratch/output roots, use unique exclusive no-follow files, and constrain `--out` or keep the receipt on stdout.

5. **OPEN — MEDIUM — Caller-selected executable.**
   - **Exploit path:** `--server` accepts any existing file. The tool executes its real path and accepts a version response containing only the substring `build 11755`; the recorded executable hash is not compared with an approved hash. **[INFERENCE]** A substituted executable can print that marker and ignore `--host 127.0.0.1` / `--offline`, including making outbound connections or binding elsewhere.
   - **Evidence:** The override is exposed at `tools/kama-context-capacity.py:654-657`; any file is resolved at `:731-741`; only the version substring is checked at `:745-754`; launch arguments are at `:292-296`. The receipt records the selected hash but does not pin it (`:739-742`), and the counter's binding checks version and model hash rather than server hash (`.ufo/waves/round-25/count-c2.py:135-140`).
   - **Impact:** The stated loopback/offline boundary depends on trusting a caller-selected program; a receipt can identify an unapproved executable while still satisfying the build-marker check.
   - **Smallest remediation:** Remove the executable override for this claim or require the exact approved realpath and digest. Use an OS/network boundary if containment must hold even for an untrusted executable.

Files written: `.ufo/waves/round-25/a2-falsify/advice/SentinelCapacityTool.md`.