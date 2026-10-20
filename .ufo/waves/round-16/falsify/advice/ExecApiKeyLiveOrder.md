VERDICT: confirm — api-key precedence claim (knowledge `llamacpp-loading-lifecycle.md` claim 3, S036 server-http.cpp:347-359): a loading llama-server started with `--api-key` answers unkeyed `GET /v1/models` with 503 `Loading model`, not 401. Observed live on the pinned b11755 build, 5 of 5 launches.

# What was attacked

Claim: "A loading server with `--api-key` therefore answers 503, not 401" — i.e. `middleware_server_state` runs before `middleware_validate_api_key` in the pre-routing handler, so the MODEL_LOADING surface is reachable without a key during the load window.

# Static check

Pinned source `…/.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp:354-358` — the pre-routing handler calls `middleware_server_state` (503 gate, lines 307-328) and only then `middleware_validate_api_key` (401, lines 260-305). Order in source matches the claim exactly.

# Live evidence

Script (scratch, removed per contract): `/tmp/kama-r16-ExecApiKeyLiveOrder/apikey_precedence.py`. Per trial:

- Free port chosen by bind-to-0 (refused set {8080, 34113}); observed ports: 53587, 36955, 36237, 37937, 52877.
- Launch: `env`-equivalent minimal env `{'PATH': $PATH, 'HOME': $HOME}`, argv =
  `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --alias kama-apikey-test --host 127.0.0.1 --port <P> -c 256 -t 1 --no-webui --offline --api-key kama-test-only`
  (model sha256 verified `270cba1b…256d` before trials; `-c/-t` match the harness defaults).
- Tight loop of `GET /v1/models` without Authorization from immediately after `Popen`; every 4th request carried `Bearer kama-test-only` to detect readiness. First keyed 200 ends the trial; post-ready samples of both kinds; SIGTERM to the process group.

Results (5 trials, exit 0 each, all servers rc=0 after SIGTERM):

| trial | total reqs | unkeyed 503 (Loading model) | keyed 503 | unkeyed 401 pre-ready | ready at |
|---|---|---|---|---|---|
| 1 | 516 | 22 | 7 | 0 | 13.0 ms |
| 2 | 408 | 27 | 10 | 3 | 15.6 ms |
| 3 | 592 | 24 | 9 | 3 | 15.6 ms |
| 4 | 552 | 30 | 10 | 2 | 13.8 ms |
| 5 | 592 | 24 | 9 | 3 | 14.0 ms |

- All 503 bodies were byte-exact `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (the probe's MODEL_LOADING envelope), including the keyed 503s — the state gate fires even for correctly-keyed requests.
- First unkeyed 503s landed ~7.5 ms after spawn (immediately after the listener opened; earlier attempts were connection refusals). Every unkeyed 401 observed came strictly after the last 503 and after ready — body `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`. Trial 1 had zero unkeyed 401s before readiness: the loading gate consumed the whole window.
- Post-ready: unkeyed → 401, keyed → 200 (`models[]`/`data[]` with id `kama-apikey-test`), confirming the key actually gates a ready server — the 503s were not a no-op key configuration.
- Ready detection at 13–16 ms wall time after spawn (load window ~8 ms per the server log); ~22–30 unkeyed 503s per trial means the claim was sampled ~140 times, not once.

Teardown confirmed: `pgrep -x llama-server` exit 1; `ss -tln | grep -E '8080|34113'` empty (exit 1). No lane files touched.

# Limitations / inferences

- Single-requester loop on one loopback host; ordering across concurrent connections is not stressed. [INFERENCE]: with a listening server and any concurrency, the 503 gate still precedes the key check per request since both run in the same synchronous pre-routing handler.
- Window is ~8 ms; a slower poller could still see only 401s — that is a sampling limitation, not a verdict error (probe never misgrades 503 as UNAUTHORIZED; a missed window yields UNAUTHORIZED_SERVICE, which remains truthful).
- One consequence for the probe [INFERENCE]: against an api-keyed llama.cpp that is still loading, `kama-probe.sh` would now grade MODEL_LOADING instead of UNAUTHORIZED_SERVICE. That is the documented intent of the precedence order (state gate first), but it means MODEL_LOADING can fire on endpoints a key protects once ready — drift either way (exit 2), never a false MODEL_OK.

# Installs

None. No tools installed or updated; python3 + pinned binary only.

# Files

- Report only; scratch `/tmp/kama-r16-ExecApiKeyLiveOrder/` removed after capture (results preserved inline above and re-derivable by re-running the named argv/poll procedure).
