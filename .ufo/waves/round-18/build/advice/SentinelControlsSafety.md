VERDICT: partial — frozen controls provide useful IPv4/process isolation patterns, but lack the required mapped-IPv6 and KeyboardInterrupt controls.

Axes reviewed: operability; calibration. Scope: the two named frozen copies, as requested. The expected `build/out/C1Controls` directory was absent when checked, so these are must-keep review criteria, not a certification of the new delivery.

## Must-keep safety properties

1. **High — fake services bind only loopback, including the mapped-IPv6 positive control.**
   - **Exploit path:** a fake binds `0.0.0.0` or `::` while the test expects a local-only harness; the fake then exposes a test listener on non-loopback interfaces. Conversely, a correct fake bound specifically to `::ffff:127.0.0.1` is rejected because the listener detector fails to recognize it.
   - **Evidence:** `frozen/tests_llamacpp-live_controls.py:245-248` — “`HTTPServer(('127.0.0.1', PORT), Handler)`”; `frozen/tools_kama-llamacpp-live.py:311-318` — “A child bound to `0.0.0.0` or `::` still answers loopback connects but is not counted”. The frozen fake has only the IPv4 bind; it does not supply the new AF_INET6 mapped-address case.
   - **Impact:** unintended network exposure is a control-test side effect; rejecting the mapped-loopback server is a false failure and hides listener-ownership defects.
   - **Smallest remediation / L1 check:** each fake’s bind address must be exactly `127.0.0.1` or, for the dedicated positive case, AF_INET6 `::ffff:127.0.0.1`; forbid wildcard binds. In the mapped case, assert the fake really listens on that address and require the harness to accept it as its owned loopback listener. Confirm using the listener address/owner (not just successful loopback HTTP), and keep the fake and any child processes on loopback only.

2. **High — no fake or real service may use a registered/refused port.**
   - **Exploit path:** a control chooses an endpoint-consumer port and temporarily occupies a service another lane expects to own. The frozen staging helper silently substitutes an empty registry when the source registry cannot be copied.
   - **Evidence:** `frozen/tools_kama-llamacpp-live.py:66-69` — “Ports that must never be served”; `frozen/tools_kama-llamacpp-live.py:284-307` — “Default: bind 127.0.0.1:0”; `frozen/tests_llamacpp-live_controls.py:386-391` — “staged empty registry for controls”.
   - **Impact:** disruption or misattribution of a live endpoint, even if the fake is loopback-only.
   - **Smallest remediation / L1 check:** use the real registry contents, fail closed if they are unavailable (do not stage an empty substitute), and verify the selected port is absent from the parsed registry plus 8080 and 34113 before a fake binds. Assert the fake binds only the harness-selected port; run one fake control at a time.

3. **High — cleanup must be process-group scoped, identity-checked, and unconditional.**
   - **Exploit path:** a timeout or injected teardown failure leaves a fake or descendant listening after the control exits; an unguarded group signal can instead hit the controls harness.
   - **Evidence:** `frozen/tools_kama-llamacpp-live.py:1132-1137` — “`start_new_session=True`”; `frozen/tools_kama-llamacpp-live.py:771-802` — “SIGTERM the process group, SIGKILL after TERM_GRACE”; `frozen/tests_llamacpp-live_controls.py:346-370` — “Kill the fake's process GROUP”; `frozen/tests_llamacpp-live_controls.py:520-522` — “`finally: _kill_fake(st['srv'])`”.
   - **Impact:** orphaned listeners/children can outlive tests or interfere with other lane work; a bad kill target can terminate the harness.
   - **Smallest remediation / L1 check:** preserve a separate session/process group for the fake, verify PID identity and that its PGID is the expected fake group leader before `killpg`, then reap/wait. Keep cleanup in `finally` for ordinary, timeout, and exception paths; after cleanup assert the port refuses connections and no fake/group descendants remain. Never signal the controls process group. Confirm the controls run serially and its outer `finally` still performs the cleanup.

4. **Medium — remove each per-run sandbox, even on failure.**
   - **Exploit path:** a failed or interrupted control leaves its staged model, fake script, receipt, or log in a persistent temp directory.
   - **Evidence:** `frozen/tests_llamacpp-live_controls.py:658-667` — “`tempfile.TemporaryDirectory(`” and “belt-and-braces: kill any fake that outlived its run”.
   - **Impact:** leaked artifacts and stale paths/process metadata accumulate; cleanup failure can mask an orphaned fake.
   - **Smallest remediation / L1 check:** keep all per-control files under a `TemporaryDirectory` context; perform process cleanup before leaving it, then assert the root no longer exists after normal, timeout, and injected-fault runs.

5. **High — do not leak inherited environment values to the fake, receipt, or diagnostics.**
   - **Exploit path:** the controls subprocess inherits the caller environment, and a regression forwards credentials/proxy variables to the fake or prints them into captured diagnostics.
   - **Evidence:** `frozen/tests_llamacpp-live_controls.py:497-513` — “`env = dict(os.environ)`”; `frozen/tools_kama-llamacpp-live.py:82-85` — “Child process environment allowlist”; `frozen/tools_kama-llamacpp-live.py:1103-1105` — “`child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in os.environ}`”.
   - **Impact:** secret disclosure through a child process, receipt, or test output.
   - **Smallest remediation / L1 check:** preserve the server-child allowlist. Have the fake report only environment key names or a boolean for a test-only secret sentinel, never values; assert no non-allowlisted sentinel reaches it and no sentinel value appears in receipt/stdout/stderr. Do not dump `os.environ` or include its values in failure messages.

6. **High — inject KeyboardInterrupt only inside an isolated wrapper, and prove exit/cleanup.**
   - **Exploit path:** raising or delivering SIGINT in the controls process interrupts/kills the harness; a KeyboardInterrupt escaping tool teardown can skip receipt handling and leave the fake alive.
   - **Evidence:** `frozen/tests_llamacpp-live_controls.py:252-259` — “run the tool in-process inside a child wrapper so a teardown fault that escapes the tool's own handlers cannot corrupt this controls process”; `frozen/tests_llamacpp-live_controls.py:284-287` — “`except BaseException:`”; `frozen/tests_llamacpp-live_controls.py:319-321` — existing K6 injects `RuntimeError`, not `KeyboardInterrupt`.
   - **Impact:** the harness can be interrupted or child processes can survive the very control meant to exercise fault handling.
   - **Smallest remediation / L1 check:** patch the in-process tool’s teardown to raise `KeyboardInterrupt` in the child wrapper—not by signaling the controls process. Require a receipt and tool exit exactly 2 per the C1 contract, and assert the wrapper catches any escape without propagating it to the parent. In all outcomes run the outer fake process-group cleanup, prove the port is closed and no child remains, and verify the controls process continues to finish/report normally.

7. **Critical — argv-forgery receipts are data for the gate, never launch instructions.**
   - **Exploit path:** a forged `argv` containing `--api-key X` and a non-loopback host is accidentally fed to a real `llama-server` rather than merely submitted to the receipt gate. The tool can resolve a real server from `PATH` if `--server` is omitted.
   - **Evidence:** `frozen/tests_llamacpp-live_controls.py:406-415` — “`'--server', str(st['fake'])`” followed by “`+ list(extra)`”; `frozen/tools_kama-llamacpp-live.py:998-1004` — “`server_arg = args.server or shutil.which('llama-server')`”; `frozen/tools_kama-llamacpp-live.py:1088-1098` — the constructed server argv explicitly includes “`'--host', '127.0.0.1'`”.
   - **Impact:** credential exposure in process arguments and a network-reachable server if a control launches the forged command; potential impact extends beyond the test lane.
   - **Smallest remediation / L1 check:** implement argv-forgery cases as synthetic receipt mutation followed by a gate-only invocation; do not start the lifecycle tool or any server for these cases. Verify the only subprocess is `[sys.executable, gate, forged_receipt]`. For every control that does start the lifecycle tool, assert `--server` resolves to that control’s staged fake, never `shutil.which('llama-server')` or the installed runtime. Keep the forged `--api-key` / non-loopback argv only inside the receipt fixture and verify it is rejected.

## Limitations / installs

- Review was limited to `frozen/tests_llamacpp-live_controls.py` and `frozen/tools_kama-llamacpp-live.py`; the current C1 delivery was not available at `build/out/C1Controls` when inspected.
- No tools installed or updated.