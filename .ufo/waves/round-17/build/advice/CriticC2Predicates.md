VERDICT: partial — the three C2 predicates hold on b11755's happy path (rc 0 in 24/24 late SIGTERMs, including 2× CPU oversubscription), but each has a vacuity or provenance gap that v2 must close.

Seat: KamaR17.CriticC2Predicates-2 (critic, read-only). Subject: the proposed `kama-llamacpp-live/v2` predicates. `tools/kama-llamacpp-live.py` is still byte-identical to the frozen copy (`cmp` → SAME), so tool line numbers below refer to `.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py`. llama.cpp source: `/tmp/llama.cpp-704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (another seat's checkout, commit 704366d76 = b11755). Axes: operability, calibration.

## Scratch evidence (advice, not a verdict)
I ran `~/.local/opt/llama-b11755/llama-server` directly, not the harness, with the same argv as the tool (`--host 127.0.0.1 --port <bind(:0) odd ephemeral, not 8080/34113/6901> -c 256 --no-webui --offline`). stdout/stderr went to /dev/null and nothing was written to disk. I sent one `killpg(SIGTERM)` per run, 12 runs per cell. "Loaded" means 64 `python3 -c 'while 1: pass'` burners on 32 CPUs.

| SIGTERM timing | idle rc (SIGKILL needed?) | loaded rc | max term→reap |
|---|---|---|---|
| 200 ms after first `/health` 200 ("late", the harness's case) | 0 ×12 (no) | 0 ×12 (no) | 3 ms / 33 ms |
| immediately at first `/health` 200 | 0 ×12 | 0 ×12 | 1 ms / 34 ms |
| at first `/health` 503 (model loading) | **−15 ×12** | **−15 ×12** | 1 ms / 18 ms |
| two back-to-back SIGTERMs, late | 0 ×8 | — | — |

- Every 200 body was exactly `b'{"status":"ok"}'`.
- A 503 was seen in all 24 "at 503" runs, including under load, even though those polls opened a new connection each time.
- After the runs, `ss -ltnp` showed 0 llama listeners and `pgrep` showed 0 burners.

Python repro of the zombie-race defect (see A2), with no ports and no files:

```
cached returncode before teardown: None
killpg on zombie group -> OK (no error)
sigterm_sent True returncode 0
poll() first -> 0 => sigterm_sent would be False
```

## A1 — Requiring returncode 0 after SIGTERM

**It is version-specific, and the window is real.**
- The source has one `return 0;` (server.cpp:590), reached after `start_loop()` returns. `main.cpp:4` passes it through: `return llama_server(argc, argv);`.
- The signal handlers are installed **after** the model loads:
  - server.cpp:507: `if (!ctx_server.load_model(params)) {`
  - server.cpp:533-534: `sigaction(SIGINT, &sigint_action, NULL); sigaction(SIGTERM, &sigint_action, NULL);`
  - A SIGTERM during loading therefore takes the default action, which returns −15. Python docs (https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode): "A negative value -N indicates that the child was terminated by signal N (POSIX only)." Observed 24/24 above.
- `/health` turns 200 **before** the handlers exist. server.cpp:515 is `ctx_http.is_ready.store(true);` and the `sigaction` calls come 18 lines later. So a 200 alone does not prove that SIGTERM will exit gracefully.
- The first observable proof that the handlers are installed is the log line at server.cpp:544: `SRV_INF("listening on %s\n", address.c_str());`. The round-16 receipt kept that line: `llama_server: listening on http://127.0.0.1:37527`.
- **Lost-signal race [INFERENCE, not reproduced in 24 tries].**
  - The handler calls `ctx_server.terminate()` (server.cpp:522), which sets `running = false` (server-queue.cpp:134).
  - But `start_loop` then unconditionally sets `running = true;` (server-queue.cpp:279).
  - So a SIGTERM that lands between server.cpp:534 and :576 is lost. The server keeps running, the harness sends SIGKILL after `TERM_GRACE = 10.0` (tool:63), and the result is rc −9: a false failure on a healthy server.
  - The harness's happy path is not exposed, because captures plus two bash probes take far longer than this window.
- **Load does not make it flaky.** Worst case under load was 34 ms, against a 10 s grace period.
- **Residual false-failure risk [INFERENCE].** The handler takes a non-async-signal-safe `std::unique_lock<std::mutex> lock(mutex_tasks);` (server-queue.cpp:133). The main loop wakes every second (`max_wait_time = std::chrono::seconds(1)`, server-queue.cpp:288) and holds the same mutex briefly. If SIGTERM lands on the main thread inside that critical section, the process self-deadlocks, gets SIGKILLed, and returns rc −9. Probability is tiny, but not zero.
- **Gate fixture conflict.** The selftest baseline in `tests/llamacpp-live/check-receipt.py:945` encodes `"teardown": {"returncode": -15, "sigterm_sent": True,` as a **passing** receipt (and again at :977). That is the opposite of the documented graceful status.
  - It is fine for v1 "validates unchanged".
  - A v2 baseline must not inherit it. If the v2 gate reuses this fixture and relaxes to "rc ∈ {0, −15}" to stay green, the predicate becomes vacuous again.

**Controls that show the predicate can fail** (fake server, deterministic):
- (a) The fake ignores SIGTERM → SIGKILL → rc −9.
- (b) The fake keeps the default disposition → rc −15.
- (c) The fake traps TERM and exits 1 (this mirrors server.cpp:34 `exit(1);`).

Each must FAIL. Separately, a fake that traps TERM and exits 0 must PASS (repro: `trap "exit 0" TERM` → rc 0).

**Smallest safe correction:**
- Grade `teardown_graceful` as `sigterm_sent ∧ ¬sigkill_sent ∧ rc == 0` only when the run reached post-probes and a "listening on" line was seen before SIGTERM.
- Otherwise record it as ungraded with a reason (`signal-before-handler`), never as passed.
- The DOC row cites server.cpp:527-534, :590 and main.cpp:4 @704366d76, plus the Python `returncode` docs.

## A2 — Provenance hole: "harness-initiated" SIGTERM can be false

- `teardown` decides with the cached value, tool:663: `if proc.returncode is None:  # F5: killpg only while child is alive`.
- The Python docs say `None` reflects "the time of the last method call", not the current state.
- If the child exits on its own (rc 0) after the last `verify_live` poll (tool:976) and before teardown:
  - `sigterm_sent` is recorded as True;
  - `killpg` on the zombie's group succeeds;
  - `wait` returns 0.
- The proposed v2 predicate then passes a self-exit as a graceful SIGTERM shutdown (repro above). This is exactly the "self-exit rc 0" misbehaviour C2 says it closes.

**Control:** a function-level control in `controls.py`:
1. Import the tool and Popen `sh -c 'exit 0'` with `start_new_session=True`.
2. Sleep, without polling.
3. Call `teardown()`.
4. Require that the record does **not** claim a harness-initiated SIGTERM.

An end-to-end fake that self-exits "just after the last probe" is timing-dependent and will be a flaky control. Make sure that control asserts only "run not accepted" (exit ≠ 0), not which check fired.

**Smallest safe correction:** replace the cached test with `alive = proc.poll() is None`, record `alive_before_sigterm`, and require it to be true in the teardown predicate. The remaining race is microseconds; document it in the DOC row.

## A3 — health_ready requiring the exact ready body

- Source: server-context.cpp:5297, `res->ok({{"status", "ok"}});`. The comment at :5292 says "this endpoint can be accessed during sleeping", so idle-sleep cannot change the body.
- Observed the byte-exact body `{"status":"ok"}` in 48/48 scratch runs that reached 200, and in round-16 `captures.health` (`"Content-Length": "15"`).
- False-failure risk with a byte-exact compare on the pinned build: none observed. [INFERENCE] Pin the expected body to the `704366d76` row so a future build bump fails loudly rather than silently.

**Controls:** a fake 200 returning `{"status":"degraded"}`, and a fake 200 returning `{"status":"ok","x":1}`. Both must fail.

Minor gap: v2 should grade both the readiness `/health` 200 transition body and `captures.health`. Otherwise a fake can serve "ok" to one poll and something else to the other.

## A4 — loading_envelope_exact "graded when observed" is vacuous by design

- The loading window is real for this build. httplib is listening before `load_model`, and every endpoint returns the envelope until `is_ready`. server-http.cpp:308: `if (!is_ready.load()) {`; :318: `{"message", "Loading model"},`.
- Round-16 observed it (`loading_observed: true`, 37 repeats). My scratch runs observed a 503 in 24/24, including under load.
- On this host the vacuous branch is therefore rare in practice. It is still a free pass by design for any subject that never answers 503 at all. That is acceptable only if the receipt and gate **count** it as ungraded, not as passed.
- **First-503-only hole.** The producer captures only the first 503: tool:479, `if loading_503 is None and result['status'] == 503 and proven:`. A subject whose first 503 is exact and whose later 503s are malformed passes.
  - The evidence to grade them already exists: transition rows are deduplicated by signature, `_sig(row)` = `(status, error, body_sha256)` (tool:383-384), so each distinct malformed body survives as its own row.

**Controls** (deterministic by request count, not by time):
- (a) The fake returns a malformed 503 for the first N `/v1/models` requests, then 200. It must fail.
- (b) The fake returns an exact 503 once, then a malformed 503, then 200. It must fail; it currently passes.
- (c) The fake never returns 503. The check must be recorded as ungraded, and the gate summary must not count it as a pass.

**Smallest safe correction:**
- Grade every `status == 503` transition row (each body must parse to the envelope; check-receipt re-derives it).
- Emit `graded: false` (or omit the check, with the gate keyed on `loading_observed`) when no 503 was seen.
- Report "N graded / M ungraded" so "11/11" can never include a vacuous pass.

## A5 — Port-closed requiring proven child ownership: can the proof be vacuous?

- **"Any inode" ownership is not exclusive.** `port_owned_by` returns True if **any** LISTEN inode on the port is in the child's fd table (tool:285-288: `if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted: return True`).
- **Not exploitable against the real server.** llama-server sets SO_REUSEPORT only under `--reuse-port`: server-http.cpp:220, `if (reuse_port) {`; the default `bool reuse_port = false;` is at common/common.h:631; the tool's argv (tool:860-869) does not pass it. So for real llama-server a co-listener cannot bind.
- **It does matter for fake controls.** A fake that sets SO_REUSEPORT and spawns a co-listener has "proven ownership" while a stranger also serves.
  - Correction: ownership = **every** LISTEN inode on the port belongs to the child. A real run has exactly one inode, so this adds no false-failure risk.
- **Connect-refusal conflates two causes.** teardown proves closure by `socket.create_connection` at tool:686. That cannot tell a subject-leaked listener from a stranger that bound the freed port in the milliseconds after exit.
  - [INFERENCE] Linux `bind(:0)` prefers odd ephemeral ports. The round-16 port 37527 is odd, so another host process doing `bind(:0)` can land on the freed port. Low-probability false failure.
  - Correction: record the child's LISTEN inode set at the post-probes `verify_live`. After teardown, the subject predicate is "those inodes are absent from /proc/net/tcp{,6}". Keep connect-refusal as a secondary observation; "port accepts but our inode is gone" = `port_reused_by_stranger`, which is not a subject failure.
- **Control that shows it can fail:**
  1. The fake forks a `setsid()` grandchild that inherits the listen fd.
  2. The parent traps TERM and exits 0.
  3. The grandchild keeps accepting.
  4. Result: inode still present and connect succeeds → FAIL.
  - `killpg` (tool:666) cannot reach the escaped session.
  - v2 has no "no surviving descendants" predicate, so the controls themselves must kill the grandchild and confirm with `ss -ltnp`. Otherwise the controls leak.
- **No ownership proof, no grade.** When ownership was never proven (a setup error before the first response), port-closed must be `graded: false`, not passed. The gate already requires `port_listener_ownership == "child"` (check-receipt.py:438-440) only as the post-probes snapshot.

## A6 — Receipt-always-written gap (confirms the C2 premise)

- tool:1020-1021 stores `receipt['teardown'] = {'error': f'{type(exc).__name__}: {exc}'}`.
- tool:1026 then indexes `receipt['teardown']['returncode']` → `KeyError`.
- That escapes the outer finally (tool:1042-1045 only resets `exit_code`), so there is no receipt and the process ends with a Python traceback (exit 1, not 2). Exit 1 is the "checks failed" code, so an internal fault is misreported as a subject verdict.
- [INFERENCE, low] `_emit` failures other than OSError/Terminated escape the same way. tool:1054/1065 catch only those two, and `json.dumps(..., allow_nan=False)` (tool:752) can raise ValueError.

**Control:** monkeypatch `teardown` to raise. The run must write a receipt with exit 2.

## Impacted axes
- **Calibration:** A2, A4 and A5 are cases where a pass does not mean what it claims.
- **Operability:** the lost-signal race and the stranger-rebind case in A1/A5 are false-failure risks; A6 hides internal faults.
- Defects to fix (not tradeoffs): A2, A4 first-503-only, A5 "any inode", A6.
- Tradeoffs to document: the lost-signal and mutex-deadlock windows in A1, and the stranger-rebind case in A5. With the inode predicate, stranger-rebind stops being a tradeoff.

## Limitations
- The scratch runs exercised llama-server directly, not the v2 harness, which does not exist yet. 12 runs per cell is a small sample. The lost-signal race and mutex self-deadlock were not reproduced; they rest on source reading.
- The odd/even ephemeral-port preference is from kernel memory, not checked against source.
- I did not run `controls.py`, `mutants.py`, `measure.py`, or any lane gate.

## Installs
None.
