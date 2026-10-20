VERDICT: confirm — b11755 silently applies the LAST duplicated `--port`/`--host` (P2 listens; `ss` shows `0.0.0.0:P`), an extra `--api-key` 401s /v1/models, /props and /metrics, and the frozen gate VALIDates 6 of 8 argv-forged receipts; only exact list equality closes it.

# ProbeArgvEffects: what extra or duplicate llama-server flags do on b11755, and why the v3 gate must re-derive argv exactly

Seat `KamaR18.ProbeArgvEffects-2`, round 18 BUILD, experiment seat (scratch only), 2026-10-20 21:06–21:14Z. Lane tip `e75cf680b53484a61709ee1b2787d8dbc6419f74`. Every run used my `/tmp` clone at that commit, never the lane working tree. In the clone, the tool (sha256 `0efd1723…c46ac`) and the gate (sha256 `ad680179…88ac1e`) are byte-identical to the frozen copies; `sha256sum -c frozen/SHA256SUMS` reported all 10 OK. At 21:17Z, `git status` showed uncommitted edits to `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py` and `tests/probe-verdicts/check.py` in the lane. These are presumably L1's integration work [INFERENCE: L1 is the only integrator]. Those edits were not tested here.

## Setup (exact)

- Server: `~/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`, sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`. `/props` reported build_info `b11755-704366d76` in every run.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. This matches the fixture.
- Baseline argv: built by `tools/kama-llamacpp-live.py` main() at lines 1088–1097, using the build_parser defaults at lines 955–960 (alias `kama-live-probe`, ctx 256, threads 1):
  `<realpath> -m <model> --alias kama-live-probe --host 127.0.0.1 --port P -c 256 -t 1 --no-webui --offline`
- Launch discipline matched the tool:
  - Environment: the tool's `CHILD_ENV_KEYS` allowlist (observed keys `HOME LANG PATH`).
  - Process setup: `start_new_session=True` and the tool's `_preexec_pdeathsig`.
  - Ports: from the tool's own `pick_port(refused_ports())`, with refused set `{8080, 34113}`. No registered port was used.
  - One server at a time.
  - Teardown: `killpg` with SIGTERM, except SIGKILL for the host-netns `0.0.0.0` run.
  - The tool module was imported from my `/tmp` clone with `sys.dont_write_bytecode`, never from the lane checkout.
- Placement terms used below:
  - "before tail": extra flags inserted just before `--no-webui --offline`. This still satisfies the frozen gate's tail rule.
  - "end": extra flags appended after `--offline`.

## Answers to the assigned experiments

### (a) Baseline: the tool's exact argv

- `ss -ltnp 'sport = :46219'`: `LISTEN 0 512 127.0.0.1:46219 0.0.0.0:* users:(("llama-server",pid=3128211,fd=3))`
- `/health` 200 `{"status":"ok"}`.
- `/v1/models` 200: data[0] `{"id":"kama-live-probe","aliases":["kama-live-probe"],"owned_by":"llamacpp"}` (from the e0 repeat).
- `/props` 200: model_alias `kama-live-probe`; n_ctx 256 (from e0).
- `/metrics` 501: `` {"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}} ``.
- The tool predicate `port_owned_by` returned `true`.
- The log had no duplicate-flag warning.

### (b) `--api-key kamatest` appended; no key sent

| GET | no key | `Authorization: Bearer kamatest` |
|---|---|---|
| /health | 200 `{"status":"ok"}` | 200 |
| /v1/models | **401** | 200 |
| /props | **401** | 200 |
| /metrics | **401** | 501 (not-enabled body) |

- All three 401 bodies are identical (sha256 `9956a1bd…`): `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`. The server logged `unauthorized: Invalid API Key` once for each.
- The same three 401s appeared with the flag placed before the tail (b′) and with the underscore spelling `--api_key` (e1).
- The source agrees. Only `"/health",` and `"/v1/health",` (plus the UI asset paths) are public: server-http.cpp:251–258, in the pinned round-17 copy whose sha256 `24ede172…` equals the tool's `SERVER_HTTP_SHA`. The 401 body is built at :290–297. On b11755, `/v1/models` is not public.
- I ran `kama-probe.sh check` with the tool's own `run_probe` argv against an `--api-key` server (run f). Both expects (`kama-live-probe` and `kama-not-this-model`) gave exit 2, `UNAUTHORIZED_SERVICE`, reason `http-401`.
- What a genuine run would grade:
  - `probe_model_ok` and `probe_mismatch`: false (observed probe verdicts above).
  - `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`: false. This is code-derived: I applied tool:1181–1206 to the observed bodies.
  - Result: tool exit 1. An extra `--api-key` is therefore loud in a real run; the danger is a forged receipt (G3, G6 below).
- `--api-key kamatest --api-key kamatest2` (b2):
  - The server logged `DEPRECATED: argument '--api-key' specified multiple times, use comma-separated values instead (only last value will be used)`.
  - Yet both keys were accepted: 200 with either key, 401 with none. The cause is arg.cpp:3538 `params.api_keys.push_back(key);`, which never clears the list.
  - So the server's own warning text misdescribes the semantics.

### (c) `--port P2` after `--port P1`: the last value wins

- c, appended at the end: `--port 40627 … --port 34005`. `ss` showed only `127.0.0.1:34005`. `GET :40627/health` → `ConnectionRefusedError: [Errno 111] Connection refused`.
- c′, inserted before the tail: `--port 36157 … --port 39645`. Only `127.0.0.1:39645` listened; 36157 refused connections.
- Both runs logged `DEPRECATED: argument '--port' specified multiple times, use comma-separated values instead (only last value will be used)`.
- On P1 the tool predicates returned `_listen_inodes` → `[]` and `port_owned_by` → `null`. A genuine run polling P1 would therefore never become ready.
- Source: arg.cpp:3354 `params.port = value;`. The parse loop only warns about the duplicate and continues (:832–838).

### (d) `--host 0.0.0.0` after `--host 127.0.0.1`: the last value wins and the server binds the wildcard

**Host netns (the assigned check):** I sent SIGKILL as soon as `ss` had read the socket.

```text
$ ss -ltnp 'sport = :36745'
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512          0.0.0.0:36745      0.0.0.0:*    users:(("llama-server",pid=3154372,fd=3))
```

- The log said `listening on http://0.0.0.0:36745`.
- Timing: the listener was first seen 10.3 ms after spawn. `ss` finished 10.9 ms after detection, and the process group was reaped 14.2 ms after detection.
- `ss -ltnp 'sport = :36745'` afterwards showed only the header.
- No HTTP request was sent to the wildcard listener on the host.

**Isolated netns:** run under `unshare -rn` with only `lo`, so nothing was exposed. Used to observe the full HTTP surface.

- Both placements (before tail and end) bound the wildcard: `0.0.0.0:39729` and `0.0.0.0:44375`.
- Statuses: /health 200, /v1/models 200, /props 200 with alias `kama-live-probe`, /metrics 501. These are the same statuses as the baseline, so no HTTP-level check can see the wildcard bind.
- Only the tool's fail-closed ownership predicate notices it (tool:316–318):
  - The `/proc/net/tcp` row is `00000000:9B31`.
  - `_listen_inodes` → `[]`, so `port_owned_by` → `null`.
  - `verify_live` then returns `port-listener-ownership-unproven` (tool:634–638), which is a setup error in a genuine run.
- Source: arg.cpp:3338 `params.hostnames.clear();`, then :3342 push_back. `--host` also takes a comma-separated list (help text at :3336). [source-only, not run]

### Spelling variants

These were not assigned. They are cheap loopback runs, and they decide what shape the gate rule has to take.

- **e1, `--api_key kamatest`:** the same three 401s. arg.cpp:827 `std::replace(arg.begin(), arg.end(), '_', '-');` rewrites underscores in `--` arguments. A gate rule that looks for the name `--api-key` would miss this spelling.
- **e2, `-c 256 … --ctx-size 512`:**
  - `/props` default_generation_settings.n_ctx was **512**; the e0 baseline was 256.
  - The log had **no DEPRECATED line**, because `seen_args` keys on the literal spelling (arg.cpp:832).
  - Every v2 check is unaffected.
- **e3, `--alias kama-live-probe … -a kama-other`:**
  - `/v1/models` data[0] was `{"id":"kama-live-probe","aliases":["kama-live-probe","kama-other"],"owned_by":"llamacpp"}`; `/props` model_alias was `kama-live-probe`.
  - The log had **no DEPRECATED line**.
  - arg.cpp:3031 `params.model_alias.insert(alias);` accumulates aliases.
  - `models_alias_id` and `props_alias` would both still pass.
- **The duplicate warning never reaches a receipt.** tool:77 `LOG_KEEP = re.compile(r'build|model loaded|listening|loading', re.IGNORECASE)` does not match the DEPRECATED line. This was measured as `False` in all 5 runs that logged it.

## Why the gate must re-derive argv exactly

I ran the frozen gate (sha256 `ad680179…`, from my /tmp clone) on argv-only edits of round-17 `receipt-1.json`. All other fields are the genuine round-17 values. G0, the unmodified copy, was VALID with exit 0.

| forged insert | placement | frozen gate | first-occurrence `argv_flag` reads | what b11755 does with that argv (measured) |
|---|---|---|---|---|
| G1 `--host 0.0.0.0` | before tail | **VALID, exit 0** | `--host` = `127.0.0.1` | binds `0.0.0.0:P` (d) |
| G2 `--port 40090` | before tail | **VALID, exit 0** | `--port` = `40089` | serves the second port; the first refuses (c) |
| G3 `--api-key kamatest` | before tail | **VALID, exit 0** | `--api-key` = `kamatest` (no rule reads it) | 401 on 3 surfaces (b) |
| G6 `--api_key kamatest` | before tail | **VALID, exit 0** | `--api-key` = `null` | 401 on 3 surfaces (e1) |
| G7 `--ctx-size 512` | before tail | **VALID, exit 0** | `-c` = `256` | n_ctx 512 (e2) |
| G8 `-a kama-other` | before tail | **VALID, exit 0** | `--alias` = `kama-live-probe` | extra alias `kama-other` (e3) |
| G4 `--host 0.0.0.0` | end | INVALID, exit 1 | — | rejected only by `argv tail ['--host', '0.0.0.0'] != ['--no-webui', '--offline']` |
| G5 `--api-key kamatest` | end | INVALID, exit 1 | — | rejected only by `argv tail ['--api-key', 'kamatest'] != ['--no-webui', '--offline']` |

How the gate is fooled:

- check-receipt.py:169–176: `argv_flag` returns the value after the **first** occurrence of a flag.
- check-receipt.py:387–421: seven flags are checked through that lookup, plus a positional two-element tail.

How b11755 actually treats the same argv:

- It applies the **last** value for `--port` and `--host` (c, d).
- It **accumulates** values for `--api-key` and `-a/--alias` (b2, e3), against its own warning text.
- It normalises `_` to `-` (e1).
- It has short and long spellings of the same option: `-t/--threads`, `-c/--ctx-size`, `-a/--alias`, `-m/--model` (arg.cpp:1520, 1642, 3025, 3049). Mixed spellings skip the duplicate warning entirely (e2, e3).

So no per-flag rule is safe, whether it reads the first value, the last value, or a count. Two of the six accepted forgeries, G7 and G8, would not be caught even by a genuine run's v2 checks. G1's wildcard bind is caught only by the tool's ownership predicate, never by an HTTP check. Exact list equality against a template built from receipt fields is the only rule that does not depend on a model of llama.cpp's parser.

## Advice for the v3 rule (C1 owns the edit)

1. **Exact list equality.** Require `argv == [server.realpath, '-m', M, '--alias', alias, '--host', '127.0.0.1', '--port', str(port), '-c', str(ctx), '-t', str(threads), '--no-webui', '--offline']`. That is 15 elements, all strings, and no other form is accepted.
2. **M must be re-derivable. Today this produces a measured false failure (e4).**
   - The tool passes `args.model` unresolved (tool:1089 `server_real, '-m', args.model,`), but records `model.path = os.path.realpath(args.model)` (tool:1055).
   - I made a genuine run from `~/.cache/kama-shokunin/models` with `--model stories260K.gguf`. The tool exited 0 with 11/11 checks true, ownership `child`, and graceful teardown.
   - The frozen gate still returned **INVALID, exit 1**: `argv -m 'stories260K.gguf' != model.path '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'`.
   - An exact v3 rule keeps this good-rejection unless the v3 tool launches with the realpath (preferred, because argv then follows from `model.path`) or records the raw argument.
   - Per the contract, the v1/v2 paths stay unchanged.
3. **Optional extra checks; these do not replace exact equality.**
   - `captures.props.fields["default_generation_settings.n_ctx"] == ctx` would flag e2 in a genuine run.
   - `/v1/models data[].aliases == [alias]` would flag e3. The receipt keeps the /v1/models body (tool:665).
4. **Controls for C1Controls.**
   - G1, G2, G3, G6, G7 and G8 (inserted before the tail) are the forgery shapes the frozen gate currently accepts; v3 must reject every one.
   - G4 and G5 are already rejected, but only because of their position.
   - A live `--api-key` control fails six checks at once (`models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`). It therefore cannot serve as a single-target R5 control.

## Limitations

- **Timing noise.** Peer `KamaR18.ProbeZeroLoading-2` announced a host-wide `stress-ng --cpu 32` window from about 21:06Z, lasting about 4 minutes. My host runs (21:06:46–21:09:54Z) overlapped it, so the millisecond timings may be inflated. The outcomes are deterministic argument-parsing results.
- **Derived vs observed `--api-key` outcomes.** The four HTTP-check outcomes are derived from tool code applied to observed bodies, not from a tool run, because the tool hardcodes its argv. The two probe outcomes are observed.
- **Gate runs are advice, not verdicts.** They were scratch runs from my clone on /tmp copies.
- **Not run:**
  - Comma-valued `--host` or `--alias`.
  - The `--port=N` syntax. Source-only: arg.cpp:829–830 would reject it as `invalid argument`.
  - The environment-variable route: `LLAMA_ARG_HOST`, `LLAMA_ARG_PORT`, `LLAMA_API_KEY` (arg.cpp:3349/3356/3542). These are applied before the CLI (:787–810), and the tool's environment allowlist keeps them from reaching the server.

## Sources opened (candidates for S048+; accessed 2026-10-20)

- **arg.cpp at the pinned commit:** https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp — HTTP 200, 224650 B, sha256 `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`.
  - L836: "DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)"
  - L3338: "params.hostnames.clear();"
  - L3354: "params.port = value;"
  - L3538: "params.api_keys.push_back(key);"
  - L3031: "params.model_alias.insert(alias);"
  - L827: "std::replace(arg.begin(), arg.end(), '_', '-');"
- **common.h at the pinned commit:** https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.h — HTTP 200, 57298 B, sha256 `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9`.
  - L652: `std::vector<std::string> hostnames = {"127.0.0.1"};`
  - L669: `std::vector<std::string> api_keys;`
- **tools/server/server-http.cpp at the same commit:** the round-17 pinned copy, sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`.
  - L253–254: `"/health",` `"/v1/health",` (the public set)
  - L290: `res.status = 401;`
  - L294: `{"message", "Invalid API Key"},`

## Commands and exits

Unless noted, each command ran from cwd `/tmp/kama-r18-ProbeArgvEffects`.

| # | command | exit |
|---|---|---|
| 1 | `curl -sS --max-time 30 -o arg.cpp -w '%{http_code} %{size_download}\n' <arg.cpp URL>`, then the same for common.h | 0 (`200 224650`, `200 57298`) |
| 2 | `python3 harness.py host` (a, b, b′, b2, c, c′) | 0 |
| 3 | `unshare -rn sh -c 'ip link set lo up && ip -br addr && exec python3 harness.py netns'` | 0 (`lo UNKNOWN 127.0.0.1/8 ::1/128`) |
| 4 | `python3 harness.py wildcard; ss -ltnp` | 0; 0 |
| 5 | `python3 harness.py extra` (e0–e3) | 0 |
| 6 | `python3 harness.py gate`, run twice (the second run added G6–G8 and overwrote the JSON) | 0 |
| 7 | (cwd `~/.cache/kama-shokunin/models`) `TMPDIR=/tmp/kama-r18-ProbeArgvEffects/tmp python3 <clone>/tools/kama-llamacpp-live.py --model stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --out /tmp/kama-r18-ProbeArgvEffects/runs/e4-relative-model-receipt.json` | 0 (empty stdout/stderr; the tool removed its temp log) |
| 8 | `python3 <clone>/tests/llamacpp-live/check-receipt.py /tmp/kama-r18-ProbeArgvEffects/runs/e4-relative-model-receipt.json` | 1 |
| 9 | `python3 harness.py probe` (f) | 0 |

The harness exits 0 only if every run's teardown left no live process group and no LISTEN row on its ports.

## Teardown, installs, cleanup

- **Per-run teardown.** For every run: the process group was gone (`killpg(pgid, 0)` → ESRCH), there was no LISTEN row on the run's ports, and those ports refused connections. Details are per run in Appendix A.
- **All server pids.** `ps -o pid,args -p <all 15 of my server pids, including the e4 tool's child 3288931>` exited 1, so none is alive.
- **Final listener check.** `ss -ltnp` at 2026-10-20T21:14:23Z exited 0.
  - No socket is owned by any of my pids.
  - The single llama-server row (pid 3556458, 127.0.0.1:46849, started after my last run) belongs to another seat.
  - The only 0.0.0.0 and [::] rows are the `:5355` resolver sockets, which were already present before I started.

```text
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      4096       127.0.0.1:631        0.0.0.0:*   
LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*   
LISTEN 0      512        127.0.0.1:36381      0.0.0.0:*    users:(("omp",pid=3092,fd=98))
LISTEN 0      5          127.0.0.1:52433      0.0.0.0:*    users:(("python3",pid=3556525,fd=3))
LISTEN 0      4096       127.0.0.1:40443      0.0.0.0:*   
LISTEN 0      10         127.0.0.1:39017      0.0.0.0:*    users:(("chromium",pid=2082972,fd=77))
LISTEN 0      4096      172.17.0.1:53         0.0.0.0:*   
LISTEN 0      5          127.0.0.1:8796       0.0.0.0:*    users:(("python3",pid=1511,fd=3))
LISTEN 0      5          127.0.0.1:8795       0.0.0.0:*    users:(("python3",pid=1512,fd=3))
LISTEN 0      512        127.0.0.1:8793       0.0.0.0:*    users:(("python3",pid=1516,fd=3))
LISTEN 0      512        127.0.0.1:8791       0.0.0.0:*    users:(("python3",pid=1515,fd=3))
LISTEN 0      5          127.0.0.1:8790       0.0.0.0:*    users:(("python3",pid=1517,fd=3))
LISTEN 0      5          127.0.0.1:8789       0.0.0.0:*    users:(("python3",pid=1513,fd=3))
LISTEN 0      5          127.0.0.1:8788       0.0.0.0:*    users:(("python",pid=1518,fd=3))
LISTEN 0      256        127.0.0.1:8787       0.0.0.0:*    users:(("python3",pid=1514,fd=3))
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*   
LISTEN 0      512        127.0.0.1:46849      0.0.0.0:*    users:(("llama-server",pid=3556458,fd=3))
LISTEN 0      4096         0.0.0.0:5355       0.0.0.0:*   
LISTEN 0      4096           [::1]:631           [::]:*   
LISTEN 0      4096            [::]:5355          [::]:*   
```

- **Installs:** none.
- **Network:** the two raw.githubusercontent.com GETs listed above.
- **Writes:** no lane file was written except this report.
- **Scratch:** the directory `/tmp/kama-r18-ProbeArgvEffects` and the clone `/tmp/kama-r18-ProbeArgvEffects-clone` were deleted after this report was written.

## Appendix A — raw outputs (verbatim values from the harness stdout JSON; `$MODEL` = /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf)

Phase JSON sha256 (files deleted with the scratch dir): host 156eebe687bf01bf6700e4f0baec9d9883c47c86bac6ef75baf5d388bf56cf84, netns bae3e177ad4424535641dd1b081183c5e0695f16393f154251379b3cc7413214, wildcard ec5369c7bb162cb526da5be4ccc196d03ab7834ef64f2ea3570edcee82a4c2a7, extra 1bbfa780a5557244ee91c41a0862585d42bd1f8e23555c41036bc31e8e26a46e, gate 1018a09fe9179ef26d11100688fb9c6d2811df4f58780f013212a5029b27d36c, probe 544547c54e7532e8e861d10207afe88d86107f426ffb463e4076cd3c900bbc8a.

#### phase `host` (harness stdout JSON, utc 2026-10-20T21:06:47.341Z; server sha256 b6a31a8e9761…, model sha256 270cba1bd510…, refused ports [8080, 34113])

**a-baseline** — tool exact argv — pid 3128211
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 46219 -c 256 -t 1 --no-webui --offline
wait_health: {"46219": {"ready": true, "secs": 0.052}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=593dd9189def…
GET /props -> 200 len=2069 sha256=8456d4d8518a… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :46219'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:46219      0.0.0.0:*    users:(("llama-server",pid=3128211,fd=3))
/proc/net/tcp* LISTEN rows: {"46219": ["tcp 0100007F:B48B inode=201499852"]}
tool _listen_inodes()/port_owned_by(): {"46219":{"_listen_inodes":["201499852"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"46219": []} port_refuses_after={"46219": true}
server log (13 lines, sha256 c039733a06df…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.008.572 I srv  llama_server: model loaded
  | 0.00.008.575 I srv  llama_server: listening on http://127.0.0.1:46219
```

**b-apikey-appended** — argv + ['--api-key','kamatest'] at the very end — pid 3128358
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 43547 -c 256 -t 1 --no-webui --offline --api-key kamatest
wait_health: {"43547": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 401 len=80 sha256=9956a1bd32a7… body={"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}
GET /props -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /metrics -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /health [Bearer kamatest] -> 200 len=15 sha256=a29ee2b15c49… body=(same as GET /health)
GET /v1/models [Bearer kamatest] -> 200 len=678 sha256=8f4db1fd2e03…
GET /props [Bearer kamatest] -> 200 len=2069 sha256=3a9999e227e3… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics [Bearer kamatest] -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :43547'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:43547      0.0.0.0:*    users:(("llama-server",pid=3128358,fd=3))
/proc/net/tcp* LISTEN rows: {"43547": ["tcp 0100007F:AA1B inode=201481458"]}
tool _listen_inodes()/port_owned_by(): {"43547":{"_listen_inodes":["201481458"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"43547": []} port_refuses_after={"43547": true}
server log (15 lines, sha256 92a4c7f36357…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 3):
  | 0.00.008.737 I srv  llama_server: model loaded
  | 0.00.008.740 I srv  llama_server: listening on http://127.0.0.1:43547
```

**b-apikey-before-tail** — --api-key kamatest inserted before --no-webui --offline — pid 3128488
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 38355 -c 256 -t 1 --api-key kamatest --no-webui --offline
wait_health: {"38355": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 401 len=80 sha256=9956a1bd32a7… body={"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}
GET /props -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /metrics -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
$ ss -ltnp 'sport = :38355'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:38355      0.0.0.0:*    users:(("llama-server",pid=3128488,fd=3))
/proc/net/tcp* LISTEN rows: {"38355": ["tcp 0100007F:95D3 inode=201534714"]}
tool _listen_inodes()/port_owned_by(): {"38355":{"_listen_inodes":["201534714"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"38355": []} port_refuses_after={"38355": true}
server log (15 lines, sha256 d793dbdf745a…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 3):
  | 0.00.008.560 I srv  llama_server: model loaded
  | 0.00.008.563 I srv  llama_server: listening on http://127.0.0.1:38355
```

**b-apikey-twice** — --api-key kamatest --api-key kamatest2 (before tail) — pid 3128633
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 43863 -c 256 -t 1 --api-key kamatest --api-key kamatest2 --no-webui --offline
wait_health: {"43863": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 401 len=80 sha256=9956a1bd32a7… body={"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}
GET /props -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /metrics -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /health [Bearer kamatest] -> 200 len=15 sha256=a29ee2b15c49… body=(same as GET /health)
GET /v1/models [Bearer kamatest] -> 200 len=678 sha256=8f4db1fd2e03…
GET /props [Bearer kamatest] -> 200 len=2069 sha256=e07b91626c72… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics [Bearer kamatest] -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
GET /health [Bearer kamatest2] -> 200 len=15 sha256=a29ee2b15c49… body=(same as GET /health)
GET /v1/models [Bearer kamatest2] -> 200 len=678 sha256=8f4db1fd2e03…
GET /props [Bearer kamatest2] -> 200 len=2069 sha256=e07b91626c72… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics [Bearer kamatest2] -> 501 len=136 sha256=b2e1bfe63d86… body=(same as GET /metrics [Bearer kamatest])
$ ss -ltnp 'sport = :43863'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:43863      0.0.0.0:*    users:(("llama-server",pid=3128633,fd=3))
/proc/net/tcp* LISTEN rows: {"43863": ["tcp 0100007F:AB57 inode=201509454"]}
tool _listen_inodes()/port_owned_by(): {"43863":{"_listen_inodes":["201509454"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"43863": []} port_refuses_after={"43863": true}
server log (16 lines, sha256 d419e4aeec1b…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 3):
  | 0.00.000.375 W DEPRECATED: argument '--api-key' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.008.543 I srv  llama_server: model loaded
  | 0.00.008.546 I srv  llama_server: listening on http://127.0.0.1:43863
```

**c-port-dup-appended** — --port 40627 ... then --port 34005 at the very end — pid 3128798
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40627 -c 256 -t 1 --no-webui --offline --port 34005
wait_health: {"40627": {"GET /health": null, "error": "ConnectionRefusedError: [Errno 111] Connection refused"}, "34005": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=8f4db1fd2e03…
GET /props -> 200 len=2069 sha256=8743998b0a83… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :40627 or sport = :34005'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:34005      0.0.0.0:*    users:(("llama-server",pid=3128798,fd=3))
/proc/net/tcp* LISTEN rows: {"40627": [], "34005": ["tcp 0100007F:84D5 inode=201478886"]}
tool _listen_inodes()/port_owned_by(): {"40627":{"_listen_inodes":[],"port_owned_by":null},"34005":{"_listen_inodes":["201478886"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"40627": [], "34005": []} port_refuses_after={"40627": true, "34005": true}
server log (14 lines, sha256 daa75f220e67…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.000.393 W DEPRECATED: argument '--port' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.008.911 I srv  llama_server: model loaded
  | 0.00.008.914 I srv  llama_server: listening on http://127.0.0.1:34005
```

**c-port-dup-before-tail** — --port 36157 ... then --port 39645 before the tail — pid 3128911
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 36157 -c 256 -t 1 --port 39645 --no-webui --offline
wait_health: {"36157": {"GET /health": null, "error": "ConnectionRefusedError: [Errno 111] Connection refused"}, "39645": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=8f4db1fd2e03…
GET /props -> 200 len=2069 sha256=d0c32d6149b2… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :36157 or sport = :39645'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:39645      0.0.0.0:*    users:(("llama-server",pid=3128911,fd=3))
/proc/net/tcp* LISTEN rows: {"36157": [], "39645": ["tcp 0100007F:9ADD inode=201532642"]}
tool _listen_inodes()/port_owned_by(): {"36157":{"_listen_inodes":[],"port_owned_by":null},"39645":{"_listen_inodes":["201532642"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"36157": [], "39645": []} port_refuses_after={"36157": true, "39645": true}
server log (14 lines, sha256 d9a997480a25…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.000.403 W DEPRECATED: argument '--port' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.008.938 I srv  llama_server: model loaded
  | 0.00.008.940 I srv  llama_server: listening on http://127.0.0.1:39645
```

#### phase `netns` (harness stdout JSON, utc 2026-10-20T21:07:01.810Z; server sha256 b6a31a8e9761…, model sha256 270cba1bd510…, refused ports [8080, 34113])

**d-netns-host-dup-before-tail** — [isolated netns] --host 127.0.0.1 ... then --host 0.0.0.0 before the tail — pid 3144322
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 39729 -c 256 -t 1 --host 0.0.0.0 --no-webui --offline
wait_health: {"39729": {"ready": true, "secs": 0.052}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=57ca436e23b5…
GET /props -> 200 len=2069 sha256=ae5973166c76… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :39729'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512          0.0.0.0:39729      0.0.0.0:*    users:(("llama-server",pid=3144322,fd=3))
/proc/net/tcp* LISTEN rows: {"39729": ["tcp 00000000:9B31 inode=201631363"]}
tool _listen_inodes()/port_owned_by(): {"39729":{"_listen_inodes":[],"port_owned_by":null}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"39729": []} port_refuses_after={"39729": true}
server log (14 lines, sha256 e508c4080ec1…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.000.370 W DEPRECATED: argument '--host' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.008.716 I srv  llama_server: model loaded
  | 0.00.008.720 I srv  llama_server: listening on http://0.0.0.0:39729
```

**d-netns-host-dup-appended** — [isolated netns] --host 127.0.0.1 ... then --host 0.0.0.0 at the very end — pid 3144422
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 44375 -c 256 -t 1 --no-webui --offline --host 0.0.0.0
wait_health: {"44375": {"ready": true, "secs": 0.051}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=57ca436e23b5…
GET /props -> 200 len=2069 sha256=81c8f4d0a91c… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76"}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :44375'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512          0.0.0.0:44375      0.0.0.0:*    users:(("llama-server",pid=3144422,fd=3))
/proc/net/tcp* LISTEN rows: {"44375": ["tcp 00000000:AD57 inode=201634028"]}
tool _listen_inodes()/port_owned_by(): {"44375":{"_listen_inodes":[],"port_owned_by":null}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"44375": []} port_refuses_after={"44375": true}
server log (14 lines, sha256 74f9214922d9…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.000.373 W DEPRECATED: argument '--host' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.008.997 I srv  llama_server: model loaded
  | 0.00.009.003 I srv  llama_server: listening on http://0.0.0.0:44375
```

#### phase `wildcard` (harness stdout JSON, utc 2026-10-20T21:07:09.618Z; server sha256 b6a31a8e9761…, model sha256 270cba1bd510…, refused ports [8080, 34113])

**d-host-host-dup-before-tail** — [HOST netns] --host 127.0.0.1 ... then --host 0.0.0.0 before the tail; SIGKILL immediately after ss — pid 3154372
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 36745 -c 256 -t 1 --host 0.0.0.0 --no-webui --offline
listen_rows_at_detect: ['tcp 00000000:8F89 inode=201684295']
$ ss -ltnp 'sport = :36745'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512          0.0.0.0:36745      0.0.0.0:*    users:(("llama-server",pid=3154372,fd=3))
ms_spawn_to_listen_seen: 10.3
ms_listen_seen_to_ss_done: 10.9
ms_listen_seen_to_group_reaped: 14.2
teardown: signals=['SIGKILL'] rc=-9 group_alive_after=False listen_rows_after={"36745": []} port_refuses_after={"36745": true}
$ ss -ltnp 'sport = :36745'   # exit 0 (after SIGKILL)
State Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
server log (13 lines, sha256 81c6dd9a4418…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.000.431 W DEPRECATED: argument '--host' specified multiple times, use comma-separated values instead (only last value will be used)
  | 0.00.009.005 I srv  llama_server: model loaded
  | 0.00.009.008 I srv  llama_server: listening on http://0.0.0.0:36745
```

#### phase `extra` (harness stdout JSON, utc 2026-10-20T21:09:07.331Z; server sha256 b6a31a8e9761…, model sha256 270cba1bd510…, refused ports [8080, 34113])

**e0-baseline-again** — tool exact argv (n_ctx and models_data reference for e2/e3) — pid 3266579
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 46875 -c 256 -t 1 --no-webui --offline
wait_health: {"46875": {"ready": true, "secs": 0.053}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=fbec17d0b264… data=[{"id":"kama-live-probe","aliases":["kama-live-probe"],"owned_by":"llamacpp"}]
GET /props -> 200 len=2069 sha256=af75c658f204… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76","default_generation_settings.n_ctx":256}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :46875'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:46875      0.0.0.0:*    users:(("llama-server",pid=3266579,fd=3))
/proc/net/tcp* LISTEN rows: {"46875": ["tcp 0100007F:B71B inode=202162272"]}
tool _listen_inodes()/port_owned_by(): {"46875":{"_listen_inodes":["202162272"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"46875": []} port_refuses_after={"46875": true}
server log (13 lines, sha256 c007d58bcd14…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.026.592 I srv  llama_server: model loaded
  | 0.00.026.597 I srv  llama_server: listening on http://127.0.0.1:46875
```

**e1-api_key-underscore** — --api_key kamatest (underscore spelling) before tail — pid 3266667
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 34943 -c 256 -t 1 --api_key kamatest --no-webui --offline
wait_health: {"34943": {"ready": true, "secs": 0.052}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 401 len=80 sha256=9956a1bd32a7… body={"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}
GET /props -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
GET /metrics -> 401 len=80 sha256=9956a1bd32a7… body=(same as GET /v1/models)
$ ss -ltnp 'sport = :34943'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:34943      0.0.0.0:*    users:(("llama-server",pid=3266667,fd=3))
/proc/net/tcp* LISTEN rows: {"34943": ["tcp 0100007F:887F inode=202091394"]}
tool _listen_inodes()/port_owned_by(): {"34943":{"_listen_inodes":["202091394"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"34943": []} port_refuses_after={"34943": true}
server log (15 lines, sha256 fba667a5d4e8…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 3):
  | 0.00.031.274 I srv  llama_server: model loaded
  | 0.00.031.282 I srv  llama_server: listening on http://127.0.0.1:34943
```

**e2-ctx-size-long-spelling** — -c 256 ... then --ctx-size 512 before tail — pid 3266766
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 35675 -c 256 -t 1 --ctx-size 512 --no-webui --offline
wait_health: {"35675": {"ready": true, "secs": 0.054}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=678 sha256=55aee4c845f3… data=[{"id":"kama-live-probe","aliases":["kama-live-probe"],"owned_by":"llamacpp"}]
GET /props -> 200 len=2069 sha256=5608e2c8870f… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76","default_generation_settings.n_ctx":512}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :35675'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:35675      0.0.0.0:*    users:(("llama-server",pid=3266766,fd=3))
/proc/net/tcp* LISTEN rows: {"35675": ["tcp 0100007F:8B5B inode=202139263"]}
tool _listen_inodes()/port_owned_by(): {"35675":{"_listen_inodes":["202139263"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"35675": []} port_refuses_after={"35675": true}
server log (13 lines, sha256 bf5277b39409…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.026.145 I srv  llama_server: model loaded
  | 0.00.026.156 I srv  llama_server: listening on http://127.0.0.1:35675
```

**e3-alias-short-spelling** — --alias kama-live-probe ... then -a kama-other before tail — pid 3266896
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 36957 -c 256 -t 1 -a kama-other --no-webui --offline
wait_health: {"36957": {"ready": true, "secs": 0.054}}
GET /health -> 200 len=15 sha256=a29ee2b15c49… body={"status":"ok"}
GET /v1/models -> 200 len=691 sha256=4a6c8175c018… data=[{"id":"kama-live-probe","aliases":["kama-live-probe","kama-other"],"owned_by":"llamacpp"}]
GET /props -> 200 len=2069 sha256=10fa0bd17b2d… props={"model_alias":"kama-live-probe","total_slots":4,"is_sleeping":false,"build_info":"b11755-704366d76","default_generation_settings.n_ctx":256}
GET /metrics -> 501 len=136 sha256=b2e1bfe63d86… body={"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}
$ ss -ltnp 'sport = :36957'   # exit 0, stderr ''
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:36957      0.0.0.0:*    users:(("llama-server",pid=3266896,fd=3))
/proc/net/tcp* LISTEN rows: {"36957": ["tcp 0100007F:905D inode=202139278"]}
tool _listen_inodes()/port_owned_by(): {"36957":{"_listen_inodes":["202139278"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"36957": []} port_refuses_after={"36957": true}
server log (13 lines, sha256 d01ba925914c…; tool LOG_KEEP keeps DEPRECATED line: False; 'unauthorized: Invalid API Key' lines: 0):
  | 0.00.028.957 I srv  llama_server: model loaded
  | 0.00.028.963 I srv  llama_server: listening on http://127.0.0.1:36957
```

#### phase `gate` (frozen gate sha256 ad6801791f2a… run from the /tmp clone on argv-only edits of round-17 receipt-1.json; utc 2026-10-20T21:09:42.186Z)

```text
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G0-unmodified.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --no-webui --offline
  VALID runs/G0-unmodified.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G1-host-0.0.0.0-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --host 0.0.0.0 --no-webui --offline
  VALID runs/G1-host-0.0.0.0-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G2-port-dup-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --port 40090 --no-webui --offline
  VALID runs/G2-port-dup-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G3-api-key-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --api-key kamatest --no-webui --offline
  VALID runs/G3-api-key-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":"kamatest","-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G4-host-0.0.0.0-appended.json   # exit 1, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --no-webui --offline --host 0.0.0.0
  INVALID runs/G4-host-0.0.0.0-appended.json: 1 problem(s)
    - argv tail ['--host', '0.0.0.0'] != ['--no-webui', '--offline']
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G5-api-key-appended.json   # exit 1, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --no-webui --offline --api-key kamatest
  INVALID runs/G5-api-key-appended.json: 1 problem(s)
    - argv tail ['--api-key', 'kamatest'] != ['--no-webui', '--offline']
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":"kamatest","-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G6-api_key-underscore-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --api_key kamatest --no-webui --offline
  VALID runs/G6-api_key-underscore-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G7-ctx-size-long-spelling-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 --ctx-size 512 --no-webui --offline
  VALID runs/G7-ctx-size-long-spelling-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
$ python3 <clone>/tests/llamacpp-live/check-receipt.py runs/G8-alias-short-spelling-before-tail.json   # exit 0, stderr ''
  argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 40089 -c 256 -t 1 -a kama-other --no-webui --offline
  VALID runs/G8-alias-short-spelling-before-tail.json
  gate argv_flag() reads: {"--host":"127.0.0.1","--port":"40089","--api-key":null,"-c":"256","--alias":"kama-live-probe"}
```

#### phase `probe` (harness stdout JSON, utc 2026-10-20T21:12:45.292Z)

**f-probe-vs-apikey** — kama-probe.sh check (tool run_probe) against an --api-key server — pid 3436044
```text
argv[1:]: -m $MODEL --alias kama-live-probe --host 127.0.0.1 --port 43979 -c 256 -t 1 --api-key kamatest --no-webui --offline
wait_health: {"43979": {"ready": true, "secs": 0.051}}
$ bash <clone>/tools/kama-probe.sh check --port 43979 --expect kama-live-probe --json --timeout 2 --connect-timeout 1   # exit 2, stderr_tail None
  rows[0]: verdict=UNAUTHORIZED_SERVICE reason=http-401
$ bash <clone>/tools/kama-probe.sh check --port 43979 --expect kama-not-this-model --json --timeout 2 --connect-timeout 1   # exit 2, stderr_tail None
  rows[0]: verdict=UNAUTHORIZED_SERVICE reason=http-401
$ ss -ltnp 'sport = :43979'   # exit 0
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      512        127.0.0.1:43979      0.0.0.0:*    users:(("llama-server",pid=3436044,fd=3))
tool _listen_inodes()/port_owned_by(): {"43979":{"_listen_inodes":["202558749"],"port_owned_by":true}}
teardown: signals=['SIGTERM'] rc=0 group_alive_after=False listen_rows_after={"43979": []} port_refuses_after={"43979": true}
```

#### e4 — real tool run, relative `--model` (receipt fields)

```text
argv: /home/vgpnk/.local/opt/llama-b11755/llama-server -m stories260K.gguf --alias kama-live-probe --host 127.0.0.1 --port 37393 -c 256 -t 1 --no-webui --offline
model.path: /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
port: 37393  port_listener_ownership: child  setup_error: None  internal_fault: None
checks: health_ready=True, models_alias_id=True, models_owned_by_llamacpp=True, metrics_not_enabled=True, props_alias=True, probe_model_ok=True, probe_mismatch=True, teardown_graceful=True, teardown_port_closed=True, loading_envelope_graded=True, model_unchanged=True
teardown: {"returncode": 0, "sigterm_sent": true, "sigkill_sent": false, "port_refuses": true}
receipt sha256: 6fe4e6faf0c86c67e66f4fdd5e4657cffd955e8f2be48955c2828f029fe07bcc
```

## Appendix B — scratch harness source (`/tmp/kama-r18-ProbeArgvEffects/harness.py`, sha256 6817f42c36996ae38395a23278214413d6097c9ecda3f09d903abb07709ac045, deleted after this report)

<details><summary>harness.py (489 lines)</summary>

```python
#!/usr/bin/env python3
"""Scratch harness for seat ProbeArgvEffects (kama-shokunin round 18).

Runs the installed b11755 llama-server with the exact argv that
tools/kama-llamacpp-live.py main() builds (baseline) and with argv variants,
one server at a time, loopback ports from the tool's own pick_port().
The single host-netns 0.0.0.0 variant is SIGKILLed as soon as `ss` has read
the listener. Netns variants run inside `unshare -rn` (loopback-only netns).
Not a lane file; scratch only under /tmp/kama-r18-ProbeArgvEffects*.
"""
import copy
import hashlib
import http.client
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
SCRATCH = '/tmp/kama-r18-ProbeArgvEffects'
CLONE = '/tmp/kama-r18-ProbeArgvEffects-clone'
RUNS = f'{SCRATCH}/runs'
SERVER = os.path.realpath(os.path.expanduser('~/.local/bin/llama-server'))
MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
ALIAS = 'kama-live-probe'   # tool default --alias
CTX, THREADS = 256, 1       # tool defaults --ctx / --threads
KEY = 'kamatest'

_spec = importlib.util.spec_from_file_location(
    'kl', f'{CLONE}/tools/kama-llamacpp-live.py')
kl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kl)
REFUSED = kl.refused_ports()

LOG_PICK = re.compile(
    r"DEPRECATED|specified multiple times|listening|couldn't|bind|api_key|"
    r"nauthorized|Invalid API|loading model|model loaded|\bhost\b|\bport\b",
    re.IGNORECASE)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tool_argv(port):
    # == kama-llamacpp-live.py main() server_argv (lines 1088-1097 @ e75cf680)
    return [SERVER, '-m', MODEL,
            '--alias', ALIAS,
            '--host', '127.0.0.1',
            '--port', str(port),
            '-c', str(CTX),
            '-t', str(THREADS),
            '--no-webui',
            '--offline']


def appended(argv, extra):
    return argv + extra


def before_tail(argv, extra):
    # keeps argv[-2:] == ['--no-webui', '--offline'] (frozen gate tail rule)
    return argv[:-2] + extra + argv[-2:]


def pick(exclude=()):
    while True:
        p = kl.pick_port(REFUSED)
        if p not in exclude:
            return p


def listen_rows(port):
    rows = []
    for fam, path in (('tcp', '/proc/net/tcp'), ('tcp6', '/proc/net/tcp6')):
        try:
            with open(path, encoding='ascii') as fh:
                next(fh, None)
                for line in fh:
                    p = line.split()
                    if len(p) < 10 or p[3] != '0A':
                        continue
                    a, ph = p[1].rsplit(':', 1)
                    if int(ph, 16) == port:
                        rows.append(f'{fam} {p[1]} inode={p[9]}')
        except OSError:
            pass
    return rows


def ss(port_filter):
    cmd = ['ss', '-ltnp', port_filter]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return {'cmd': ' '.join(cmd[:2]) + f" '{port_filter}'",
            'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}


def get(port, path, auth=None, timeout=10.0):
    headers = {'Authorization': f'Bearer {auth}'} if auth else {}
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
    try:
        c.request('GET', path, headers=headers)
        r = c.getresponse()
        body = r.read(65536)
        return {'status': r.status, 'error': None,
                'content_type': r.getheader('Content-Type'), 'body': body}
    except OSError as exc:
        return {'status': None, 'error': f'{type(exc).__name__}: {exc}',
                'content_type': None, 'body': b''}
    finally:
        c.close()


def render(path, auth, res):
    b = res['body']
    text = b.decode('utf-8', 'replace')
    out = {'GET': path, 'auth': f'Bearer {auth}' if auth else None,
           'status': res['status'], 'error': res['error'],
           'content_type': res['content_type'], 'body_len': len(b),
           'body_sha256': sha(b)}
    if path == '/props' and res['status'] == 200:
        try:
            doc = json.loads(text)
            out['props_fields'] = {k: doc.get(k) for k in (
                'model_alias', 'total_slots', 'is_sleeping', 'build_info')}
            dgs = doc.get('default_generation_settings')
            out['props_fields']['default_generation_settings.n_ctx'] = (
                dgs.get('n_ctx') if isinstance(dgs, dict) else None)
        except ValueError:
            out['body'] = text[:400]
    else:
        out['body'] = text if len(text) <= 500 else text[:500] + '...[cut]'
    if path == '/v1/models' and res['status'] == 200:
        try:
            doc = json.loads(text)
            out['models_data'] = [
                {k: e.get(k) for k in ('id', 'aliases', 'owned_by')}
                for e in doc.get('data', []) if isinstance(e, dict)]
            out['models_models'] = [
                e.get('name') for e in doc.get('models', [])
                if isinstance(e, dict)]
        except (ValueError, AttributeError):
            pass
    return out


def launch(argv, tag):
    env = {k: os.environ[k] for k in kl.CHILD_ENV_KEYS if k in os.environ}
    log_path = f'{RUNS}/{tag}.log'
    log = open(log_path, 'wb')
    kl._FORKED_PPID[0] = os.getpid()
    proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log,
                            stderr=subprocess.STDOUT, env=env,
                            start_new_session=True,
                            preexec_fn=kl._preexec_pdeathsig)
    log.close()
    return proc, log_path, sorted(env)


def wait_health(proc, port, timeout=60.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if proc.poll() is not None:
            return {'ready': False, 'why': f'exited rc={proc.returncode}',
                    'secs': round(time.monotonic() - t0, 3)}
        r = get(port, '/health', timeout=0.5)
        if r['status'] == 200:
            return {'ready': True, 'secs': round(time.monotonic() - t0, 3)}
        time.sleep(0.05)
    return {'ready': False, 'why': 'timeout',
            'secs': round(time.monotonic() - t0, 3)}


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def teardown(proc, ports, kill_now=False):
    pgid = proc.pid  # start_new_session=True -> pgid == pid
    sent = []
    sig = signal.SIGKILL if kill_now else signal.SIGTERM
    try:
        os.killpg(pgid, sig)
        sent.append(sig.name)
    except ProcessLookupError:
        pass
    try:
        rc = proc.wait(timeout=10.0)
    except subprocess.TimeoutExpired:
        os.killpg(pgid, signal.SIGKILL)
        sent.append('SIGKILL')
        rc = proc.wait()
    deadline = time.monotonic() + 5
    while group_alive(pgid) and time.monotonic() < deadline:
        time.sleep(0.02)
    return {'signals': sent, 'returncode': rc,
            'group_alive_after': group_alive(pgid),
            'listen_rows_after': {p: listen_rows(p) for p in ports},
            'port_refuses_after': {p: kl._port_refuses(p) for p in ports}}


def log_summary(log_path):
    with open(log_path, 'rb') as fh:
        data = fh.read()
    lines = data.decode('utf-8', 'replace').splitlines()
    return {'log_lines_total': len(lines), 'log_sha256': sha(data),
            'picked': [ln for ln in lines if LOG_PICK.search(ln)][:40],
            'tool_LOG_KEEP_would_keep_DEPRECATED': any(
                kl.LOG_KEEP.search(ln) for ln in lines
                if 'specified multiple times' in ln)}


def ownership(pid, port):
    return {'_listen_inodes': sorted(kl._listen_inodes(port)),
            'port_owned_by': kl.port_owned_by(pid, port)}


ENDPOINTS = ('/health', '/v1/models', '/props', '/metrics')


def run_http(tag, desc, argv, ports, serve_port, auths=(None,)):
    rec = {'id': tag, 'desc': desc, 'argv': argv, 'ports': ports}
    proc, log_path, env_keys = launch(argv, tag)
    rec['child_env_keys'] = env_keys
    rec['pid'] = proc.pid
    try:
        rec['wait_health'] = {p: None for p in ports}
        rec['wait_health'][serve_port] = wait_health(proc, serve_port)
        for p in ports:
            if p != serve_port:
                r = get(p, '/health', timeout=2.0)
                rec['wait_health'][p] = {'GET /health': r['status'],
                                         'error': r['error']}
        rec['http'] = []
        if rec['wait_health'][serve_port].get('ready'):
            for auth in auths:
                for path in ENDPOINTS:
                    rec['http'].append(render(path, auth,
                                              get(serve_port, path, auth)))
        rec['ss'] = ss(' or '.join(f'sport = :{p}' for p in ports))
        rec['listen_rows'] = {p: listen_rows(p) for p in ports}
        rec['tool_ownership'] = {p: ownership(proc.pid, p) for p in ports}
    finally:
        rec['teardown'] = teardown(proc, ports)
    rec['log'] = log_summary(log_path)
    return rec


def run_host_wildcard(tag, desc, argv, port):
    """0.0.0.0 on the host netns: kill the group the instant ss has read it."""
    rec = {'id': tag, 'desc': desc, 'argv': argv, 'ports': [port]}
    t0 = time.monotonic()
    proc, log_path, env_keys = launch(argv, tag)
    rec['child_env_keys'] = env_keys
    rec['pid'] = proc.pid
    try:
        seen = None
        rows = []
        while time.monotonic() - t0 < 30.0 and proc.poll() is None:
            rows = listen_rows(port)
            if rows:
                seen = time.monotonic()
                break
            time.sleep(0.001)
        rec['listen_rows_at_detect'] = rows if seen else []
        rec['ss'] = ss(f'sport = :{port}') if seen else None
        t_ss = time.monotonic()
        rec['tool_ownership'] = None
    finally:
        rec['teardown'] = teardown(proc, [port], kill_now=True)
    t_end = time.monotonic()
    if seen:
        rec['ms_spawn_to_listen_seen'] = round((seen - t0) * 1000, 1)
        rec['ms_listen_seen_to_ss_done'] = round((t_ss - seen) * 1000, 1)
        rec['ms_listen_seen_to_group_reaped'] = round((t_end - seen) * 1000, 1)
    rec['ss_after'] = ss(f'sport = :{port}')
    rec['log'] = log_summary(log_path)
    return rec


def experiments_host():
    out = []
    p = pick()
    out.append(run_http('a-baseline', 'tool exact argv', tool_argv(p), [p], p))
    p = pick()
    out.append(run_http('b-apikey-appended',
                        "argv + ['--api-key','kamatest'] at the very end",
                        appended(tool_argv(p), ['--api-key', KEY]),
                        [p], p, auths=(None, KEY)))
    p = pick()
    out.append(run_http('b-apikey-before-tail',
                        "--api-key kamatest inserted before --no-webui --offline",
                        before_tail(tool_argv(p), ['--api-key', KEY]),
                        [p], p))
    p = pick()
    out.append(run_http('b-apikey-twice',
                        '--api-key kamatest --api-key kamatest2 (before tail)',
                        before_tail(tool_argv(p), ['--api-key', KEY,
                                                   '--api-key', KEY + '2']),
                        [p], p, auths=(None, KEY, KEY + '2')))
    p1 = pick()
    p2 = pick(exclude=(p1,))
    out.append(run_http('c-port-dup-appended',
                        f'--port {p1} ... then --port {p2} at the very end',
                        appended(tool_argv(p1), ['--port', str(p2)]),
                        [p1, p2], p2))
    p1 = pick()
    p2 = pick(exclude=(p1,))
    out.append(run_http('c-port-dup-before-tail',
                        f'--port {p1} ... then --port {p2} before the tail',
                        before_tail(tool_argv(p1), ['--port', str(p2)]),
                        [p1, p2], p2))
    return out


def experiments_netns():
    out = []
    p = pick()
    out.append(run_http('d-netns-host-dup-before-tail',
                        '[isolated netns] --host 127.0.0.1 ... then --host '
                        '0.0.0.0 before the tail',
                        before_tail(tool_argv(p), ['--host', '0.0.0.0']),
                        [p], p))
    p = pick()
    out.append(run_http('d-netns-host-dup-appended',
                        '[isolated netns] --host 127.0.0.1 ... then --host '
                        '0.0.0.0 at the very end',
                        appended(tool_argv(p), ['--host', '0.0.0.0']),
                        [p], p))
    return out


def experiments_extra():
    """Spelling variants a per-flag/blacklist gate rule would not see."""
    out = []
    p = pick()
    out.append(run_http('e0-baseline-again', 'tool exact argv (n_ctx and '
                        'models_data reference for e2/e3)', tool_argv(p),
                        [p], p))
    p = pick()
    out.append(run_http('e1-api_key-underscore',
                        '--api_key kamatest (underscore spelling) before tail',
                        before_tail(tool_argv(p), ['--api_key', KEY]),
                        [p], p))
    p = pick()
    out.append(run_http('e2-ctx-size-long-spelling',
                        '-c 256 ... then --ctx-size 512 before tail',
                        before_tail(tool_argv(p), ['--ctx-size', '512']),
                        [p], p))
    p = pick()
    out.append(run_http('e3-alias-short-spelling',
                        '--alias kama-live-probe ... then -a kama-other '
                        'before tail',
                        before_tail(tool_argv(p), ['-a', 'kama-other']),
                        [p], p))
    return out


def experiment_probe_apikey():
    """kama-probe.sh verdicts (the tool's own run_probe argv) against a
    server launched with an extra --api-key; no key is sent."""
    p = pick()
    argv = before_tail(tool_argv(p), ['--api-key', KEY])
    rec = {'id': 'f-probe-vs-apikey', 'desc': 'kama-probe.sh check (tool '
           'run_probe) against an --api-key server', 'argv': argv,
           'ports': [p]}
    proc, log_path, env_keys = launch(argv, rec['id'])
    rec['pid'] = proc.pid
    rec['child_env_keys'] = env_keys
    try:
        rec['wait_health'] = {p: wait_health(proc, p)}
        rec['probes'] = []
        if rec['wait_health'][p].get('ready'):
            env = {k: os.environ[k] for k in kl.CHILD_ENV_KEYS
                   if k in os.environ}
            for expect in (ALIAS, kl.MISMATCH_EXPECT):
                pr = kl.run_probe(f'{CLONE}/tools/kama-probe.sh', p, expect,
                                  env)
                row = kl.probe_row(pr) or {}
                rec['probes'].append({
                    'argv': pr.get('argv'), 'exit': pr.get('exit'),
                    'verdict': row.get('verdict'),
                    'reason': row.get('reason'),
                    'stderr_tail': pr.get('stderr_tail')})
        rec['ss'] = ss(f'sport = :{p}')
        rec['tool_ownership'] = {p: ownership(proc.pid, p)}
    finally:
        rec['teardown'] = teardown(proc, [p])
    rec['log'] = log_summary(log_path)
    return [rec]


def experiment_host_wildcard():
    p = pick()
    return [run_host_wildcard(
        'd-host-host-dup-before-tail',
        '[HOST netns] --host 127.0.0.1 ... then --host 0.0.0.0 before the '
        'tail; SIGKILL immediately after ss',
        before_tail(tool_argv(p), ['--host', '0.0.0.0']), p)]


def gate_forgeries():
    gate = f'{CLONE}/tests/llamacpp-live/check-receipt.py'
    gspec = importlib.util.spec_from_file_location('gate', gate)
    gmod = importlib.util.module_from_spec(gspec)
    gspec.loader.exec_module(gmod)
    src = f'{CLONE}/.ufo/waves/round-17/live/receipt-1.json'
    with open(src, encoding='utf-8') as fh:
        base = json.load(fh)
    other = base['port'] + 1
    variants = [
        ('G0-unmodified', None, []),
        ('G1-host-0.0.0.0-before-tail', before_tail, ['--host', '0.0.0.0']),
        ('G2-port-dup-before-tail', before_tail, ['--port', str(other)]),
        ('G3-api-key-before-tail', before_tail, ['--api-key', KEY]),
        ('G4-host-0.0.0.0-appended', appended, ['--host', '0.0.0.0']),
        ('G5-api-key-appended', appended, ['--api-key', KEY]),
        ('G6-api_key-underscore-before-tail', before_tail,
         ['--api_key', KEY]),
        ('G7-ctx-size-long-spelling-before-tail', before_tail,
         ['--ctx-size', '512']),
        ('G8-alias-short-spelling-before-tail', before_tail,
         ['-a', 'kama-other']),
    ]
    out = []
    for name, how, extra in variants:
        r = copy.deepcopy(base)
        if how:
            r['argv'] = how(r['argv'], extra)
        path = f'{RUNS}/{name}.json'
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(r, fh)
        cmd = [sys.executable, gate, path]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        out.append({'id': name, 'argv': r['argv'], 'cmd': ' '.join(cmd),
                    'exit': cp.returncode, 'stdout': cp.stdout,
                    'stderr': cp.stderr,
                    'gate_argv_flag': {f: gmod.argv_flag(r['argv'], f)
                                       for f in ('--host', '--port',
                                                 '--api-key', '-c',
                                                 '--alias')}})
    return out


def main():
    os.makedirs(RUNS, exist_ok=True)
    which = sys.argv[1]
    if which == 'host':
        res = experiments_host()
    elif which == 'netns':
        res = experiments_netns()
    elif which == 'wildcard':
        res = experiment_host_wildcard()
    elif which == 'probe':
        res = experiment_probe_apikey()
    elif which == 'extra':
        res = experiments_extra()
    elif which == 'gate':
        res = gate_forgeries()
    else:
        raise SystemExit(f'unknown phase {which}')
    meta = {'phase': which, 'server_realpath': SERVER,
            'server_sha256': kl.sha256_file(SERVER),
            'model_sha256': kl.sha256_file(MODEL),
            'refused_ports': sorted(REFUSED),
            'tool_sha256': kl.sha256_file(kl.SCRIPT),
            'utc': kl._utc_now()}
    text = json.dumps({'meta': meta, 'runs': res}, indent=1, default=str)
    with open(f'{RUNS}/phase-{which}.json', 'w', encoding='utf-8') as fh:
        fh.write(text)
    print(text)
    bad = [r['id'] for r in res if 'teardown' in r and (
        r['teardown']['group_alive_after']
        or any(r['teardown']['listen_rows_after'].values()))]
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
```

</details>
