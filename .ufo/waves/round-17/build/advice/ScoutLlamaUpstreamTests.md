VERDICT: refute — upstream server tests assert neither the `/health` ready body nor the server's exit status; only HTTP status codes (and one indirect cleanup side effect).

# Scout: upstream llama.cpp server tests on /health, "Loading model" 503, shutdown/exit

Commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (llama-server b11755). Read-only seat: nothing in the lane was modified; no servers started, no ports bound.

## Method (observed)

- Listed the exact tree at the commit in a scratch shallow fetch (`git fetch --depth 1 origin 704366d76…` into `/tmp/lcpp`) and enumerated `tools/server/tests`: `conftest.py`, `pytest.ini`, `tests.sh`, `README.md`, 6 `fixtures/*.py`, and 28 `unit/*.py` (incl. `utils.py`). Line numbers below are `git show FETCH_HEAD:<path> | nl -ba`.
- Cross-checked the same bytes with `curl https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…/tools/server/tests/…` for `utils.py`, `test_basic.py`, and all 27 other unit files. GitHub contents API was rate-limited (`API rate limit exceeded`), so the tree listing came from the shallow fetch.
- Exhaustive grep over `tools/server/tests` for `/health`, `503`, `Loading model`, `returncode`, `terminate`, `SIGTERM`, `signal`.

## Q1 — /health readiness

**Every `server.start()` waits on `GET /health` status 200, and silently retries anything else (including 503).**
https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/tests/utils.py#L341-L359
- `utils.py:343` `response = self.make_request("GET", "/health", headers={`; `:346-348` `if response.status_code == 200: self.ready = True` / `return  # server is ready`.
- `:349-350` `except Exception as e: pass` — a 503 body is never inspected; non-200 is indistinguishable from a refused connection.
- `:352-353` `if self.process.poll() is not None:` `raise RuntimeError(f"Server process died with return code {self.process.returncode}")` — the only `returncode` read in the harness, and it fires during *startup*, not teardown.

**The explicit ready-body test asserts status only.**
https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/tests/unit/test_basic.py#L15-L19
- `test_basic.py:18-19` `res = server.make_request("GET", "/health")` / `assert res.status_code == 200`. No `body`, no `status == "ok"`, no key set.

**Other /health call sites are equally body-blind.**
- `test_security.py:22-24` `assert res.status_code == 200` / `assert "error" not in res.body` — public-endpoint check, not a ready-body check.
- `test_sleep.py:52-53` `assert res.status_code == 200` — health after idle-sleep; body unused.
- `test_mcp_servers.py:132-133` `assert res.status_code == 200, res.body` — `res.body` only in the failure message.
- Full-tree grep: `/health` appears in exactly `utils.py`, `test_basic.py`, `test_security.py`, `test_sleep.py`, `test_mcp_servers.py`. No fifth consumer, no body assertion anywhere.

## Q2 — the "Loading model" 503

**No upstream test asserts the documented 503 body.** `git grep -n "Loading model" FETCH_HEAD -- tools/server/tests` returns **0** hits.
- Contract exists only server-side: `server-http.cpp:307-325` `if (!is_ready.load())` → `res.status = 503;` `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`. It is a pre-routing middleware, so it also covers `/health`.
- Documented at `tools/server/README.md:485-490`: `Body: {"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` and ready `Body: {"status": "ok" }`.
- Ready body produced at `server-context.cpp:5288-5297` `res->ok({{"status", "ok"}});`, under the comment `// error and loading states are handled by middleware`.

**The only 503 assertion in the suite is on a different route and is skip-gated.**
https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/tests/unit/test_stream.py#L123-L152
- `test_stream.py:128-131` polls `GET /models`, `status = next(m["status"]["value"] …)`, `if status == "loading":` — loading is observed via `/models`, not `/health`.
- `:146-152` `if res.status_code == 503: saw_503 = True` … `assert saw_503, "resume during the load did not answer 503"` — on `/v1/stream?…&from=0`, not `/health`.
- `:137-138` `pytest.skip("load window too short to be observed on this machine")` — the loading-window assertion is self-skipping, so it is not a stable detector.
- Corollary observed: the loading 503 is *exercised* implicitly by every start (503 ⇒ retry loop) but never *asserted*.

## Q3 — shutdown / exit status

**Teardown never inspects how the server died.**
https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/tests/utils.py#L361-L380
- `:369` `self.process.terminate()`; `:371` `self.process.wait(timeout=5)`; `:372-375` `except subprocess.TimeoutExpired:` … `self.process.kill()` … `self.process.wait(timeout=5)`.
- No `returncode` read, no `rc == 0`, no `-SIGTERM` check, no port-closed check. A SIGKILL'd server (`-9`) and a self-exit are equally "passing"; the timeout branch even prints `did not terminate in time, killing` and continues.
- `conftest.py:16-25` `stop_server_after_each_test` only iterates `server_instances` and calls `server.stop()`; no post-yield assertion.
- Grep for `returncode` in `tools/server/tests` yields only `utils.py:353` (startup death) and `test_tools_builtin.py:128,183,268,275` (a builtin shell tool and `docker inspect`, not the server process).

**One indirect exit assertion exists, and it tests a cleanup side effect.**
https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/tests/unit/test_tools_builtin.py#L271-L275
- `:270` `server.stop()`, then `:275` `assert leftover.returncode != 0, f"container {container_id} was not cleaned up after server exit"` — proves the spawned container disappeared, says nothing about the server's own status or signal.

**The shutdown path the harness could grade is real but untested.**
- `server.cpp:29-37` `signal_handler` → `shutdown_handler(signal)`; second interrupt `exit(1)` (`:33-34` `Received second interrupt, terminating immediately.`).
- `server.cpp:519-523` `shutdown_handler = [&](int) { mcp_mgr.shutdown(); ctx_server.terminate(); }`; registered for `SIGTERM` at `server.cpp:534` `sigaction(SIGTERM, &sigint_action, NULL);`.
- MCP shutdown promptness is the closest thing to an exit assertion: `test_mcp_servers.py:657-661` `assert elapsed < 3, f"Server stop took {elapsed:.1f}s, expected < 3s"`; `:706-711` same bound, with the comment `only completes when stop() sends SIGKILL at ~5s`. It grades *stop latency* (a proxy for not needing SIGKILL), never the exit code.

**CI gate is pytest's own exit code.** `.github/workflows/server-sanitize.yml:123` `PYTEST_WORKERS=4 ./tests.sh`; `tests.sh` runs `set -eu` + `pytest … -x`; the spawned `llama-server` status is never propagated.

## Consequences for C2 (inference)

- [INFERENCE] Upstream's `/health` contract is status-code-only in practice: no test would catch a ready body that changed from `{"status":"ok"}` to `{"status":"degraded"}` — the same weakness C2's `health_ready` has. C2's v2 "exact documented ready body" is *stricter than upstream*, so its SOURCES citation must lean on `README.md:488-490` + `server-context.cpp:5288-5297`, not on upstream tests.
- [INFERENCE] Upstream likewise has no exit-status/no-SIGKILL assertion; the nearest analogue is the `< 3s` stop-latency bound (`test_mcp_servers.py:657-661`), which is an acceptable *precedent shape* for C2's `teardown_exited` (bounded wait + no kill fallback) but not a source for "documented graceful exit status".
- [INFERENCE] For C1's `served_model` invariant, the nearest upstream precedent is `test_basic.py:66-72` `test_server_models`: `assert res.body["data"][0]["id"] == server.model_alias` — upstream grades served identity on `/models`, never on `/health`.

## Limitations

- Line numbers verified at the named commit only; the commit is the tip the shallow fetch resolved, so no history/diff claims are made.
- `test_stream.py` loading assertions were read, not executed (read-only seat; no upstream build or model present).
- GitHub REST tree/content API was rate-limited; directory completeness rests on `git ls-tree -r FETCH_HEAD tools/server/tests`, which is authoritative for the fetched commit.

Installs: none.
