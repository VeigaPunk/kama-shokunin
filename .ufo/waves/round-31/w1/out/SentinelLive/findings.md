# SentinelLive — C1 live-protocol audit

## Decision

**NO-GO for live seats using the frozen counter without an explicit local-host risk acceptance.** The assigned port window is currently clear, but the counter can leave a spawned server on constructor/readiness failure or seat crash, does not verify the serving socket belongs to its child, and does not prove the `/slots` payload is free of prompt content. The process census also found an already-running llama-server on 47777; do not attribute, signal, or stop it as a wave process.

## Findings

### Medium — failed startup or seat crash can orphan the live server

**Exploit/failure path:** `Server.__init__` starts the absolute command in a new session, then calls `_wait_ready()` before returning. In `main`, `server = Server()` is before the `try/finally` that calls `server.close()`. If readiness times out after 90 seconds, or `/props` JSON/model-path validation raises while the child remains alive, construction fails without calling `close()`. A counter crash/kill likewise skips `finally`; the child is in a new session. `close()` sends SIGTERM and waits 15 seconds, then only tries to kill the direct child; it does not wait/reap after kill, terminate a process group, or fail if the port is still bound after its 10-second poll.

**Evidence:** `count-c1.py:163-175,177-194,206-219,389-390,578-579`. `Popen(..., start_new_session=True)` and the constructor/finally ordering are explicit. `count-c1.py:206-219` contains the incomplete teardown and silent post-poll return.

**Impact:** A startup error or hard seat failure can leave a local server/model process consuming resources and keeping its port; the endpoint remains reachable on loopback. A later run only notices a responding listener opportunistically while selecting ports, not as an owned stale process.

**Smallest remediation:** Put child creation/readiness under an exception-safe owner/context manager; on every exit terminate and reap the process group, then make a still-bound port a hard failure. Ensure the owner is established before readiness can raise.

### Medium — port selection and readiness do not establish server identity

**Exploit/failure path:** `port_free()` is a TCP connect probe, not a reservation. `pick_port()` releases the probe socket before `Popen`, so another local listener can win the port. The readiness test accepts any HTTP 200 `/health`; `/props` checks only that `model_path` resolves to the same `MODEL` path. It does not prove the responding socket belongs to `self.proc`. A competing listener claiming that model path could therefore supply the measured responses if it wins the race and remains available. Port selection samples 64 random entries from `range(47900, 47999)`, which excludes 47999 despite the stated 47900–47999 range.

**Evidence:** `count-c1.py:131-142,177-194`; requests use fixed loopback `HOST` at `145-153`. `/props` path comparison is against the same `MODEL` constant used to launch.

**Impact:** Live outcomes can be attributed to a process other than the process the counter launched; port availability can be falsely reported or a run can refuse despite a free port among the unsampled ports.

**Smallest remediation:** Reserve the port through child startup (or use an inherited bound socket) and bind readiness to child identity, not just endpoint health and model path. Include the last allowed port if the documented range is intentional.

### Medium — HOME can redirect the binary/model; digest checks are not independent pins

**Exploit path:** `SERVER`, `IMPL`, and `MODEL` are built from `Path.home()` (`count-c1.py:82-85`). `clean_env()` removes Python and loader override variables but preserves `HOME`; it sets `LD_LIBRARY_PATH` to the derived server directory (`156-160`). Thus a caller-supplied HOME relocates all three paths and the server's library search directory. The counter hashes the files at those paths and compares them with `registry.build.{server,library,model}_sha256` loaded from the measured tip (`317-327`); the registry supplies the expected digests. `/props` compares the reported path with the same HOME-derived model path (`191-194`).

**Boundary:** No lane field is used as the executable/model *path*, and argv is an absolute-path list passed to `Popen` (no shell interpretation). Lane data supplies digest expectations and requests, not shell fragments. But the path is environment-dependent, and the content expectation is registry-controlled rather than an independent frozen digest. This does not establish a fixed server/model identity against a hostile HOME or changed registry.

**Impact:** A seat environment can select different binary, library, and model files; matching self-declared hashes and `/props` path do not prove they are the intended b11755/model artifacts.

**Smallest remediation:** Resolve paths from an explicit trusted home/root independent of ambient HOME, and compare against digests frozen outside the data registry. Keep the argv-list construction.

### Open sensitivity boundary — `/slots` payload is not proven secret-free

**Evidence:** `Server.slots()` decodes and returns the entire `GET /slots` JSON (`count-c1.py:196-204`); the caller uses the newest slot's `id_task` and `params` for its checks (`394-397,509-536`). The receipt stores selected status/fields and does not serialize the full slots object (`488-520,571,585-590`). In the pinned snapshot, `server_task_result_slots::to_json()` returns opaque `slots_data` (`server-task.cpp:1513-1517`); the four-file pin does not include the route/producer that constructs this object. Another pinned task result includes a `prompt` field (`server-task.cpp:332-350`), but that does **not** prove `/slots` includes it.

**Impact:** It is not supportable to assert that `/slots` reveals no sensitive values. If the response includes prompts or other task state, any local process able to reach the unauthenticated loopback service could read them; the counter itself keeps the full object only in memory and does not put it in its receipt.

**Smallest remediation:** Pin and inspect the actual `/slots` producer/route and enumerate its returned fields; retain the current receipt minimization and treat the response as sensitive until that source is available. Do not claim a clean no-sensitive-data result from the four-file snapshot.

## Live process and port check

- `ss -ltnp | grep -E '479[0-9][0-9]'` → no matching output (exit 1): no listener observed in the wave port window.
- `pgrep -af llama-server` → `35550 /home/vgpnk/.local/opt/llama-b11755/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47777` (exit 0): an existing process is outside the wave port window; its ownership/purpose is unknown and it was not touched.
- **NO-GO as stated above**; the empty port-window result is not evidence that no llama-server is running. Do not trust the endpoint identity or `/slots` confidentiality based on these checks. No server was started by this audit.