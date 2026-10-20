# CriticC2ServiceBoundary — C2 vs KQ5 and the PROVINCE write boundary

Seat: critic (read-only). Host sample time `2026-10-20T13:26:28Z` (`date -u`).
Target: C2 design as given in `.ufo/waves/round-16/build/spec.json` item `LiveHarness`.
`tools/kama-llamacpp-live.py` did not exist when I ran (glob: "Skipped missing paths"), so this reviews the design only, not code.
Axes: operability (whether C2 can be admitted) and calibration (whether the fixture verdicts depend on uncontrolled inputs).

## Verdict

Conditional admit. An ephemeral llama-server owned by the lane is not an "enabled service" in the KQ5 sense if every condition in §3 holds. The lane's own record treats "enabling" as restoring a model service for its consumers, alongside repointing and timers:
- `corpus/lessons/round-5.md:48-49`: "Restoring/enabling a model service, repointing external consumers, installing a timer … operator-owned and not authorized."
- `corpus/QUALITY.md:13` (KQ5): "requires enabling services, repointing consumers, installing timers, copying config/environment/session/journal bodies".

A process that serves no registered port, has no unit, and cannot outlive its harness fits neither phrase. Precedent says it is the same class as a fixture the lane already ships:
- `tools/test-snapshot.sh:64`: `server = http.server.HTTPServer(("127.0.0.1", 0), Handler)`.
- `SKILL.md:303` registers that harness with write scope "Removed temporary work directory only".

The design as specified has four counterexamples that can turn the fixture into a de facto service or an out-of-scope probe. Each has a small fix.

## 1. Counterexamples (strongest first)

### CE1 — An orphan outlives the harness and becomes a standing, unsupervised listener (fixable defect)
- The spec launches the server with `start_new_session=True` and tears it down with "try/finally, signal handlers" (spec.json `LiveHarness`). SIGKILL cannot be caught. If L1's runner times out with SIGKILL, or the OOM killer takes the harness, `finally` never runs. The child is in its own session, so terminal hangup does not reach it either. It keeps serving on loopback with no owner. [INFERENCE from POSIX semantics; not reproduced, because I am barred from running the harness.]
- That is exactly the "not a standing service" property the province note relies on: `drafts/province-note.md:40` says "It is **not a standing service.** Its lifetime is one harness run; teardown is required on every exit path."
- Impacted axes: operability (KQ5 admissibility), safety boundary.
- Smallest fix: in `preexec_fn`, call `ctypes.CDLL(None).prctl(1, 9)`, i.e. `PR_SET_PDEATHSIG` with `SIGKILL`. It is stdlib and Linux-only. Keep `start_new_session` for `killpg`. Separately, L1 records an independent post-run check that the harness does not author: `pgrep -c -x llama-server` and `ss -ltnH 'sport = :P'`. The receipt's own teardown fields are self-report.

### CE2 — The free-port handoff can serve or probe a port the lane does not own (fixable defect)
- Port 34113 is a registered port, and it lies inside the kernel's ephemeral range, so `bind(127.0.0.1:0)` can return it:
  - `/proc/sys/net/ipv4/ip_local_port_range` → `32768	60999`.
  - `registry/endpoint-consumers.tsv:36-37` pin `http://127.0.0.1:34113`.
- The spec's refusal rule ("refuse and retry if it is 8080, 34113 or any port number appearing in …endpoint-consumers.tsv") is therefore load-bearing, not cosmetic.
- If llama-server ever served 34113, the live consumers `ufo-fsd-thetick` and `ufo-fsd-local-helper` would reach a toy model. That is service enabling in substance → KQ5 reject.
- Time-of-check/time-of-use (TOCTOU) gap: the probe socket is closed before llama-server binds P. Another process can take P in between. The tight `/health` + `/v1/models` loop then sends GETs to a listener the lane does not own. The round-1 safety lesson reserves that for L0:
  - `corpus/lessons/round-1-safety.md:88-89`: "May non-model services be probed? L0 must approve any endpoint outside the declared local model registry."
  - KQ10 (`corpus/QUALITY.md:32`) rejects out-of-scope probe evidence.
- Smallest fix:
  1. Before the first HTTP request, poll `ss -ltnpH 'sport = :P'` until the listener's `pid=` equals the child PID. If the child exits first → setup error, exit 2.
  2. Store `listener_owner_verified: true` in the receipt.
  3. Re-check `P ∉ registered set` after launch, using the port actually bound.
  4. Re-derive the registered set from the TSV on every run; no hardcoded list.
  - The pre-bind period stays observable through connect-refused transitions only.

### CE3 — Inherited `LLAMA_*` environment changes writes, auth and verdicts (fixable; calibration defect)
- In b11755, environment variables fill any option that argv does not override:
  - [README L309](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L309): "If both command line argument and environment variable are both set for the same param, the argument will take precedence over env var."
- The spec's argv sets only `-m --alias --host --port -c -t --no-webui`. Any of these ambient variables would therefore take effect:

  | Variable | Effect | Source |
  |---|---|---|
  | `LLAMA_ARG_LOG_FILE` | Writes a log file. Breaks the write scope. | [L107](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L107) "Log to file (env: LLAMA_ARG_LOG_FILE)" |
  | `LLAMA_ARG_SLOT_SAVE_PATH` | Writes slot KV cache. Breaks the write scope. | [L228](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L228) |
  | `LLAMA_ARG_ENDPOINT_METRICS` | Flips the `metrics_not_enabled` check. | [L225](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L225) |
  | `LLAMA_API_KEY` | Probe sees `UNAUTHORIZED_SERVICE`, so `probe_model_ok` fails for reasons outside the fixture. | [L215](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L215) "(env: LLAMA_API_KEY)" |
  | `LLAMA_ARG_REUSE_PORT` | Allows the bind to share a socket. | [L195](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L195) |
  | `LLAMA_ARG_MODELS_DIR` / `LLAMA_ARG_HF_REPO` | Router or network-download modes. | [L230](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L230), [L103](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L103) |

- Impacted axes: calibration (the fixture result depends on ambient environment, an uncontrolled variable) and the write boundary.
- Smallest fix: launch with an explicit allowlist environment, e.g. `{"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": <home>}`.
  - The receipt records only the allowlist key names, never values. This also avoids KQ5's "copying … environment … bodies".
  - Optionally add `--log-disable` to argv. Not required, because stdout goes to a temp file that is deleted.

### CE4 — The persistent `~/.local/bin/llama-server` symlink could enable a server through a consumer (checked; not triggered for registered consumers)
- `ls -l ~/.local/bin/llama-server` → `-> /home/vgpnk/.local/opt/llama-b11755/llama-server`, mtime `Oct 20 10:17`. It persists after teardown.
- If a registered consumer started `llama-server` from PATH when its endpoint is dead, the install itself would be service enabling.
- Bounded grep for `llama-server|spawn|execFile|child_process` over the two registered consumer files found no matches. I confirmed both files exist first:
  - `$UFO_SRC/scripts/local-helper.mjs` (360 lines)
  - `config/the-tick.machine.json` (56 lines)
  - `$UFO_SRC` = `/home/vgpnk/Projects/ufo-fsd-alpha`.
- Not evaluated: the third consumer, `~/.local/bin/omp`. I did not read the host binary body, following the round-10 precedent "the host binary body is not read in this round (KQ8, KQ5)" (`.ufo/round-10/audit/stale-anchors.tsv:51`). Per KQ8 this stays undecided, not negative.
- The report must list the symlink, `~/.local/opt/llama-b11755` and `~/.cache/kama-shokunin/models/` as persistent host installs, not as ephemeral fixture state.

## 2. Boundary reading

- Write boundary: `PROVINCE.md:45-46`: "kama never writes to `~/.config`, `~/.omp`, or systemd units." The C2 install paths (`~/.local/opt`, `~/.local/bin`, `~/.cache/kama-shokunin`) are outside that set. The operator tooling directive authorizes installs into `~/.local/bin`. Compliant, provided the installs are recorded.
- Owns-row tension: `PROVINCE.md:10` scopes the owned surface as "read-only service inspection of local serving ports" and says kama "never claims an installed server". Launching is not read-only inspection.
  - Smallest safe framing: a lane test fixture under the existing probe-conventions surface `PROVINCE.md:13` ("liveness/readiness probe conventions | `/health`, `/props`, `/slots`"), added as an appended note.
  - Do not add a new Owns-table row. Adding one is a province change; `PROVINCE.md:29` reserves "province contraction is an L0 decision". [INFERENCE: expansion warrants the same L0 routing.]
  - Must not appear anywhere: wording that kama now "has an installed server/runtime".
- Existing rules that stay binding:
  - `SKILL.md:130`: "A deleted unit is not an installed runtime; do not enable or recreate it."
  - `SKILL.md:219`: "Do not recreate, start, or enable a unit."
  - `corpus/lessons/round-1-safety.md:37-39`: an implementation invoking "`systemctl`, `docker`, `sudo`, or writes an operator-owned path … must be rejected".
- Current host state (snapshot, not proof of absence): at `2026-10-20T13:26:28Z`, `pgrep -c -x llama-server` → `0` and `ss -ltnH 'sport = :8080 or sport = :34113' | wc -l` → `0`. So nothing was left running from the L1 smoke (10:17 -03 = 13:17Z), and no registered port is served.
- Probe matrix mode is isolated from the registry:
  - `tools/kama-probe.sh:743-746`: with `--port`, only the `cli-override` row is classified.
  - `:290`: `curl -sS --noproxy '*'`. Proxy environment cannot redirect the probe.

## 3. Admission conditions (all required; any failure → judge rejects C2)

1. No unit, timer, `systemctl`, `docker` or `sudo` anywhere in the harness. No write to `~/.config`, `~/.omp` or systemd paths.
2. The bound port is not in the registered set. The set is re-derived from `registry/endpoint-consumers.tsv` on every run, and checked against the actually bound port after launch (CE2).
3. The listener on P is verified as owned by the child PID before any HTTP request (CE2).
4. The child cannot outlive the harness, whatever kills the harness (PDEATHSIG, CE1). L1's independent post-run `pgrep`/`ss` check shows no survivor and P closed.
5. Allowlisted environment; only key names recorded (CE3).
6. `--host 127.0.0.1` explicitly in argv. The README default is also 127.0.0.1 ([L193](https://github.com/ggml-org/llama.cpp/blob/b11755/tools/server/README.md#L193)), but explicit argv overrides `LLAMA_ARG_HOST`.
7. Receipt holds nonsecret shape evidence only: filtered `/props`, `/slots` count, argv, no env values and no headers beyond Server/Content-Type. This matches `round-1-safety.md:22-25`.

## 4. What the report must say

- "Ephemeral lane-owned fixture on unregistered loopback port P, lifetime one harness run." Not "service", "restored" or "installed server" (`PROVINCE.md:10`).
- Registered rows: state their verdict only with a fresh `bash tools/kama-probe.sh check` command, time and exit (KQ1, `QUALITY.md:9`). Otherwise write "not sampled this round".
- The receipt must not be offered as registered-consumer health or endpoint restoration. KQ4 (`QUALITY.md:12`) rejects "endpoint restoration is claimed from a documentation measurement".
- Separate teardown evidence: harness self-report versus L1's independent post-run check.
- If `loading_observed` is false, say that MODEL_LOADING was not live-observed this run. The C1 verdict then rests on the stub matrix plus the L1 smoke observation, not on the receipt (KQ13 separation: a ready `/v1/models` id is not a readiness guarantee).
- Installs: llama.cpp b11755 official release into `~/.local/opt/llama-b11755` plus the `~/.local/bin/llama-server` symlink, and the stories260K GGUF into `~/.cache/kama-shokunin/models/`. Give channel, version and reason for each, and label all of them persistent.
- `omp` PATH-spawn behaviour not evaluated (CE4).
- Operator handoff (KQ5): no consumer was repointed, and serving the registered ports remains operator-owned.

## Distinguishing fixable from reject

- Fixable before measurement: CE1, CE2 (ownership check), CE3.
- Reject if observed: any registered port served; any unit, timer or service-manager call; any write to an operator-owned path; a survivor after the run; any report phrasing that equates the fixture with consumer health or restoration.

## Limitations

- Design review only; the harness file had not landed. I ran no harness, gate or probe.
- Commands run, all read-only:
  - `cat ip_local_port_range`
  - `pgrep -c -x llama-server`
  - a bounded `ss -ltnH` on 8080/34113
  - `test -f`/`wc -l` on the two consumer files, plus `ls -l` on the symlink
  - one bounded grep over those two files
  - `curl` of the b11755 README to `/tmp/kama-crit-readme.md`. This is a scratch file outside the lane; it is nonsecret and can be deleted.
- `omp` binary not inspected.
- CE1 orphan behaviour is inferred from POSIX semantics, not reproduced.

## Installs

None.
