FINDING: bind loopback yes (counter `HOST` and recorded launch argv); foreign port touched no in the checked measurement records (none observed); teardown proven yes (DataA04 records server exit 0 and post-stop connection refused).

Severity: Medium local-only process-ownership/cleanup caveat; no off-host bind is evidenced.

Evidence: `.ufo/waves/round-31/count-c1.py:82` fixes `HOST = "127.0.0.1"`; lines 171-174 pass that host in argv to `Popen`. The counter selects 47900-47998 after a loopback connect probe (131-142). Wave-1 receipts record 47900, 47901, 47908, 47956, 47980, and 47999, all with explicit loopback argv where reproduced. The scoped live-record search found no measurement launch using 8080 or 34113. DataA04 states: `Port 47901: server process exit 0; post-stop connect_ex returned 111 (connection refused; no listener).` DataA01/A02 and CriticIgnoredClass also record post-stop port-free evidence. CriticClaimSize reports no listeners before/after three counter runs.

Exploit path / impact: `port_free()` does not reserve the port, and readiness plus `/props` does not identify the listener as the counter's child. A local process racing the check could supply measurement responses. Also, `Server()` is constructed before the surrounding `try/finally`, so readiness failure can bypass cleanup. This is a local-only integrity/resource risk; no foreign-port use or off-host service exposure is evidenced.

LIMITS: “Foreign port touched no” is an observation from inspected receipts, not a proof against a race. DataA13 omits PID and free-before/exit/free-after fields; RevCounterFair's manual 47980 note says “exact pinned argv” without reproducing the host argument. A separate prior SentinelLive census saw an unrelated process on 47777 and says it was not touched. This seat ran no server, counter, or external network check. Teardown is proven in at least one receipt, not for every historical run.

Smallest remediation: retain loopback; verify the serving socket belongs to the spawned PID (or reserve/inherit the socket), make startup exception-safe, and fail if the child is not reaped or the port remains bound. Detailed results and raw receipts: `.ufo/waves/round-31/w2/out/SentinelBind/report.md` and `.ufo/waves/round-31/w2/out/SentinelBind/raw/`.

Report: .ufo/waves/round-31/w2/out/SentinelBind.md