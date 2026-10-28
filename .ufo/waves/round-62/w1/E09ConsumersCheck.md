# E09ConsumersCheck — registered-consumer isolation of the completion request-plane tool

Seat: executor (advisory leaf), axis **operability**, round 62 wave 1.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, tip `65d7cad0fce90e34de37527cde22e97b63b118bf`
(`git rev-parse master` == `git rev-parse HEAD`). Read-only work; no lane file was written by me, no
git/jj mutation was run, no commit. Scratch root `/fast/scratch/hyaku/kama-r62/w/E09ConsumersCheck`
(created, used, deleted before yield; every receipt copied below first).

Scope: does `tools/kama-completion-live.py` (the C1 request-plane instrument) ever contact a
registered consumer endpoint? Three required steps: read the consumer registry and list its ports,
run the tool once and check `receipt.port`, grep the tool for code paths that could reach a
registered port.

## 1. Registered ports (registry bytes, not prose)

`registry/endpoint-consumers.tsv` has exactly **3** data rows (header skipped, `#` comments ignored):

| line | id | declared_baseurl | port |
|---|---|---|---|
| 35 | `omp-llama-cpp-default` | `http://127.0.0.1:8080` | **8080** |
| 36 | `ufo-fsd-thetick` | `http://127.0.0.1:34113/v1/chat/completions` | **34113** |
| 37 | `ufo-fsd-local-helper` | `http://127.0.0.1:34113` | **34113** |

Registered port set = **{8080, 34113}** (two distinct ports; evidence
`out/E09ConsumersCheck/registered-ports.tsv`, and `ss -ltn` at run time showed no listener on either
port — both rows are currently DEAD, matching the registry notes; that is context, not my claim).
No other `registry/*.tsv` names a `127.0.0.1:<port>` endpoint (`grep -rn "127\.0\.0\.1:[0-9]\+"
registry/ --include=*.tsv` outside the consumer registry returns nothing).

## 2. Live run: chosen port is not a registered port

One plain run (no `--hold-dir`: the hold window needs an outside observer and would have graded
`hold_released` false), under `strace -f -e trace=connect` so the claim is measured, not inferred:

```
TMPDIR=<scratch> strace -f -e trace=connect -o strace-connect.txt \
  python3 tools/kama-completion-live.py --work <scratch>/work \
          --out <scratch>/receipt.json --nonce 3d19352c0db8c28767bd5333106b842a
exit=0
```

* `receipt.schema` = `kama-completion-live/v1`, `receipt.verdict` = `REQUEST_OK`, exit 0.
* **`receipt.port` = 33569** — not in `{8080, 34113}`; it is in the kernel ephemeral band
  (32768–60999), which by construction excludes 8080.
* 16/16 checks evaluated, 0 failed (incl. `listener_owned`, `teardown_clean` rc=0,
  `teardown_port_closed` true; `teardown.waited_ms`=3).
* `receipt.argv` = `[..., --alias kama-completion-probe, --port 33569, --host 127.0.0.1, -c 512, -t 1]`
  — the child binds loopback only.
* Pinned fixtures verified by the tool itself: model sha256 `270cba1b…bd256d`, server sha256
  `b6a31a8e…cd804` (`/home/vgpnk/.local/opt/llama-b11755/llama-server`), both equal to the tool's
  defaults — so the launch path under test is the frozen one.

**Connect-syscall census (whole process tree: harness + llama-server child), 8 `connect()` calls:**
all 8 to `127.0.0.1:33569`; **0** to 8080; **0** to 34113; **no** AF_UNIX/AF_INET6/other-family
connect. The llama-server child itself issued 0 outbound connects (it only accepts). After teardown,
`ss -ltn` shows no listener on 33569/8080/34113. Evidence:
`out/E09ConsumersCheck/strace-connect.txt`, `strace-summary.txt`.

## 3. Static code-path audit: no path reaches a registered port

Port selection is delegated to `tools/kama-llamacpp-live.py` (imported at
`tools/kama-completion-live.py:59-64`), and every socket sink is port-parameterised:

* `kama-completion-live.py:85` `url = f'http://127.0.0.1:{port}{path}'` (local `http_post`);
  `kama-llamacpp-live.py:917` the same shape in `http_get`. There is no other URL construction,
  no host/port from argv/env/registry, no redirect following for the graded captures.
* Call sites: `http_get(port,…)` at `:143,280,286,294`; `http_post(port,…)` at `:309,356,376`.
  All take the single chosen `port` (`:210 receipt['port'] = port`).
* `refused_ports()` (`kama-llamacpp-live.py:517-542`): starts from
  `HARD_REFUSED_PORTS = {8080, 34113}` (`:110`) **and** parses the registry TSV for
  `a.b.c.d:port`, `localhost:port`, `--port N`, `port=N`, `host:N` tokens with a 1–65535 range
  check (bare digit runs like `Qwen3-Coder-30B` are explicitly not ports). An unreadable registry
  raises `SetupError('registry-unreadable:…')` — the tool cannot silently run with an empty refusal
  set.
* `pick_port(refused, requested)` (`:546-579`): explicit `--port` raises
  `port-refused-registered:<n>` for a refused port; the default path binds `127.0.0.1:0`, takes the
  offered ephemeral port, **releases** it, and retries up to 64 times, returning only a port
  `not in refused`; it never passes `0` through to llama-server.
* `--server` cannot smuggle in a foreign client: `server_digest`/`model_digest` are graded against
  the pinned sha256s **before** port selection/launch, so a non-pinned binary exits
  `SETUP_ERROR`/2 without being executed.
* Child environment is allowlisted to `PATH HOME LANG LC_ALL LD_LIBRARY_PATH
  LLAMA_ARG_THREADS XDG_CACHE_HOME` (`kama-completion-live.py:230-232`) — the `llama-server` child
  cannot inherit a proxy/base-URL variable.
* `prepare_witness_dir` / `hold_for_witness` / `port_owned_by` / `_listen_inodes` are filesystem and
  `/proc/net/tcp{,6}` reads only — no sockets are opened toward any endpoint.

Derivation evidence (`out/E09ConsumersCheck/derivation.txt`), from the tool's own dependency:

```
registry_rows=3
registered_ports=[8080, 34113]
HARD_REFUSED_PORTS=[8080, 34113]
refused_ports()=[8080, 34113]
registered_ports_missing_from_refused=[]
fixture_row_45555_in_refused=True          # a registry row naming a non-hardcoded port IS honoured
missing_registry=refused:SetupError        # fail-closed, never an empty refusal set
explicit_8080=refused:port-refused-registered:8080
explicit_34113=refused:port-refused-registered:34113
all_ephemeral_refused=refused:no-free-unregistered-port   # the refusal filter is really consulted
pick_port_200_draws_range=32807..46745 in_refused=[]
```

## 4. Residual risk found (does not violate the consumer-isolation property)

Asymmetry between the two HTTP helpers: the dependency's `http_get` uses a proxy-less opener
(`_OPENER = build_opener(ProxyHandler({}))`, `kama-llamacpp-live.py:979`), but the local
`http_post` (`kama-completion-live.py:101`) uses bare `urllib.request.urlopen`, whose default
handler chain reads `http_proxy`/`HTTP_PROXY` from the harness environment. Measured with a
recorder listener on an unregistered ephemeral port and `http_proxy` pointed at it:

* health/models/props (via `_OPENER`) went **direct** to the chosen port and answered 200;
* the `/v1/completions` POSTs were routed **to the proxy** — the recorder captured
  `POST http://127.0.0.1:45143/v1/completions HTTP/1.1 ... User-Agent: Python-urllib/3.14`
  (2 connections; the envelope then failed 502 and the determinism probe was skipped), verdict
  `FAIL`. Evidence `out/E09ConsumersCheck/receipt-proxy.json`, `proxy-connections.log`,
  `proxy-probe-port.txt`.

Consequences, stated precisely: the request URI still names the chosen unregistered port, so **no
registered consumer is contacted** even on this path; but with a proxy variable set the graded POST
leaves the loopback plane and the run fails spuriously. In the host environment used for the real
run there is no `*_proxy` variable (`env | grep -i proxy` is empty), so the C1 receipt is unaffected.
A one-line `_OPENER`-style proxy-less opener in `http_post` would remove the asymmetry; out of scope
for this seat (no lane source edits).

## 5. Verdict of this seat

Consumer isolation holds on the frozen tip, by three independent lines of evidence (registry-derived
refusal set, live connect-syscall census under strace, static sink audit). This is a finding for the
L1, **not** a verdict on C1/C2.

Recommended follow-ups for the planner (not done here, not my write scope):
1. proxy-less opener for `http_post` (removes the §4 asymmetry);
2. optionally assert in the receipt that `port` is in the ephemeral band and `not in
   refused_ports()` recomputed at verdict time — today `refused` is used but not echoed into the
   receipt, so a verifier re-derives it from the registry bytes only.

## Tools installed / upgraded

None. `strace`, `ss`, `python3`, `llama-server` (b11755) already present; pacman untouched (host-wide
pause respected).

## Blockers

None.

Tally: registered_ports=2 registered_port_list=8080,34113 tool_port=33569 tool_port_registered=False connects_total=8 connects_to_registered=0 off_loopback_connects=0 all_checks=16/16 met=True
