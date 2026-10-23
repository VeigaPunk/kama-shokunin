ATTACK E26-01 (SKILL.md row + registry entry + S114 + lesson Gate quote): holds

Seat: KamaR26.AttackE2601 (wave 2, FALSIFY). Date: 2026-10-23, about 03:56-04:05Z.
Port block used: 47700-47703 only (checked free with `ss -ltn` before; closed after).
Landed tip: f4066979096e3452ae731c0e09e50155c6d8258a. A `git archive` extract of that tip
(`/fast/scratch/hyaku/kama-r26w2/AttackE2601/tip/`) is byte-identical (`cmp`) to the lane
working copy for SKILL.md, corpus/SOURCES.md, corpus/lessons/round-26.md and
registry/error-signatures-r26.json, so every line number below is the landed tip's.

No defect breaks the row. There are two low-severity findings (L1, L2) and one advisory
improvement (A1). Each has its smallest correction below.

## Pins checked first

- `sha256sum $(readlink -f ~/.local/bin/llama-server)`: `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
  (`/home/vgpnk/.local/opt/llama-b11755/llama-server`). This matches count-c1.py `SERVER_SHA256`.
- Model `~/.cache/kama-shokunin/models/stories260K.gguf`: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. This matches `MODEL_SHA256`.
- `llama-server --version`: `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- Counter `.ufo/waves/round-26/count-c1.py` sha256 `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`. This matches the preregistration.

## (1) Live re-run of the registered trigger: holds

Registry entry (registry/error-signatures-r26.json, id E26-01): channel `http`,
args `["--no-slots","-t","2"]`, model `fixture`, occupy_port false, request
`GET /slots`, headers `{}`, body `""`.

The harness is `out/AttackE2601/run_e2601.py`. It copies the counter's `http()` request
construction byte for byte: urllib, and the empty-string body becomes `data=b""` with
`Content-Type: application/json`. It launches
`timeout 120 llama-server -m <fixture> --host 127.0.0.1 --port P --no-slots -t 2`, waits for
`/health` 200, sends the request, then sends SIGTERM to the process group and confirms the
port is closed.

Command: `timeout 700 python3 run_e2601.py`. Exit status 0. Wall time 1.35 s.

| run | port | status | raw body |
|---|---|---|---|
| trigger-run1 | 47700 | 501 `application/json; charset=utf-8` | `{"error":{"code":501,"message":"This server does not support slots endpoint. Start it with `--slots`","type":"not_supported_error"}}` |
| trigger-run2 | 47701 | 501 `application/json; charset=utf-8` | identical to run 1 |

Controls on the same harness:

| run | extra args | `GET /slots` |
|---|---|---|
| control-default | `-t 2` | 200, a JSON array of 4 slots (`"id":0..3,"n_ctx":2048`) |
| control-slots-on | `--slots -t 2` | 200, same array |

After each run, `port_closed` was True. Afterwards `ss -ltn | rg ':4770[0-3]'` exited 1
(nothing listening) and `pgrep -af 'llama-server.*477(0[0-3])'` exited 1 (no process).

The tip receipt `.ufo/waves/round-26/final/c1-tip-receipt.json` row E26-01 agrees: every
check is true, `status` 501, and the channel excerpt is the same body.

## (2) The signature is the fault's own text (F1, F2, F3): holds

- F1 (a warning, or a line printed by an unrelated path): the channel is the HTTP response
  body, not the log. The signature appeared in none of the 8 server logs
  (`sig_in_log False` in results.json and results-env.json). I grepped the full 704366d
  source tree (codeload tarball, sha256 `c2d31d5f…0749`) with
  `rg -n -F 'does not support slots endpoint' tree`. Exit 0, and the only hit in the
  whole tree is `tools/server/server-context.cpp:5366`. No other code path can emit this
  string.
- F2 (echo of a decoded request field, query string or header): the registered request has
  an empty body, no headers and no query. The response is a C++ string literal passed to
  `format_error_response`; the request does not feed into it. I also probed this live
  (probe-noslots, port 47702, `--no-slots`):
  - `GET /slots?id_slot=0&fail_on_no_slot=1` returned 501 with the identical body.
  - `GET /slots?q=ECHOPROBE_Start_it_with` with header `X-Probe: ECHOPROBE` returned 501
    with the identical body. Neither the probe text nor the header is reflected.
  - `POST /slots/0?action=save` returned 501 with a different literal (`…slots action.
    Start it with `--slot-save-path``, which is E26-02's text). So the E26-01 text is
    specific to `GET /slots`.
  - `GET /health` returned 200 `{"status":"ok"}`.

  The counter's own `req_bytes`/`trig_key` are made from channel, args, model,
  occupy_port and request, and none of them holds the signature. So `e_not_echoed` is a
  real test for this row.
- F3 (argument file contents): the args are `--no-slots -t 2` only. No file argument is
  passed, so there is no file content to echo.
- `--help`/`--version`: the help text for the flag is `expose slots monitoring endpoint
  (default: …)` (arg.cpp:3649). It does not contain the signature, which agrees with
  `f_absent_from_baseline` true in the tip receipt.

## (3) Pinned source line and the "meaning (code)" cell: holds

Fresh fetch at 2026-10-23 03:57:27Z from
`https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`
(curl exit 0 for each file). The sha256 values are in `out/AttackE2601/fresh-fetch-sha256.txt`:

| file | fresh sha256 | lane snapshot sha256 |
|---|---|---|
| tools/server/server-context.cpp | `dd1de0f2…2329` | `dd1de0f2…2329` (same; also equals the tarball copy) |
| common/arg.cpp | `bf4c58c1…822d` | same |
| tools/server/server-common.cpp | `b4f4aae7…d442` | same |
| tools/server/server.cpp | `21439622…aef4` | same |
| tools/server/server-http.cpp | `24ede172…fdb` | same |
| common/common.h | `8bcc5708…40a9` | (not in the snapshot; fetched to check the default) |

Code facts:
- server-context.cpp:5363 `this->get_slots = [this](const server_http_req & req) {`
- :5365 `if (!params.endpoint_slots) {`
- :5366 `res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));`
- :5367 `return res;`
- server-common.cpp:115-117 maps `ERROR_TYPE_NOT_SUPPORTED` to `type_str = "not_supported_error"; code = 501;`
- server-context.cpp:4872-4874 `error()` sets `status = json_value(error_data, "code", 500)`, so the status is 501.
- server.cpp:318 registers `ctx_http.get("/slots", ex_wrapper(routes.get_slots))` unconditionally.
- arg.cpp:3646-3652 defines `{"--slots"}, {"--no-slots"}`, which set `params.endpoint_slots = value`, with env `LLAMA_ARG_ENDPOINT_SLOTS`.
- common.h:686 `bool endpoint_slots = true;` (enabled by default).

SKILL.md:1084 meaning cell: "`get_slots` refuses when `params.endpoint_slots` is false
(`server-context.cpp:5365-5367`); the launch turned slot monitoring off". The function,
the guard, the 5365-5367 line range and the inference are all correct. The default is
true, so a 501 here means the launch explicitly disabled it. The trigger cell's
"`GET /slots` → 501" matches both the code and the live status.

## (4) The "next action" cell: holds (advisory A1)

Cell: "Slot monitoring is off on this server, not a dead server. Re-launch with `--slots`
only if a consumer needs `/slots`; otherwise stop polling it."
- "not a dead server": on the same `--no-slots` process, `/health` returned 200 (probe-noslots).
- "Re-launch with `--slots`": control-slots-on returned 200. `--slots` also wins over the
  environment: with `LLAMA_ARG_ENDPOINT_SLOTS=0` plus `--slots`, `GET /slots` returned 200
  (env-slots0-plus-flag, port 47701).
- "otherwise stop polling it": this is a conservative operator choice and does not
  overreach.

A1 (advisory, not a defect). The cause can also come from the environment. With
`LLAMA_ARG_ENDPOINT_SLOTS=0` and no flag, `GET /slots` returned 501 with the identical body
(env-slots0, port 47700). An operator who searches the argv for `--no-slots` will not find
it. Both env-slots0 and noslots-props also showed `GET /props` → 200 with
`"endpoint_slots":false` (source server-context.cpp:5254). That gives a one-request
confirmation that works on a live server.

Smallest correction (optional): in the SKILL.md:1084 meaning cell, change "the launch
turned slot monitoring off" to "the launch turned slot monitoring off (`--no-slots` or
`LLAMA_ARG_ENDPOINT_SLOTS=0`; `GET /props` shows `"endpoint_slots":false`)".

## (5) SOURCES row S114 and the lesson Gate quote: holds (finding L1)

The S114 row is at corpus/SOURCES.md:126. Its columns follow the header at :11 (`id | source |
kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`):
- URL `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5366`: correct path, full commit and line (`#L5366` is the error line).
- anchor `server-context.cpp line 5366 @ 704366d…; sha256 dd1de0f2…2329`: equals the fresh fetch.
- teaches: the same text as the meaning cell. It is correct per (3).
- kind `code`, tier `A`, status `mined`, opened `2026-10-23`, used-by `SKILL.md, registry/error-signatures-r26.json`: consistent.

The lesson Gate is at corpus/lessons/round-26.md:27. Its URL is identical and its access
date is 2026-10-23. The quote is the exact bytes of line 5366 without its leading
indentation, which is 12 words (25 or fewer).

L1 (low, rendering only). The Gate quote is wrapped in single backticks, but the quoted
code itself contains backticks (`` `--slots` ``). In CommonMark the span closes at the
inner backtick, so the quote renders as two code spans with a bare `--slots` between them.
The raw bytes are faithful; only the rendered form is wrong. SKILL.md:1084 already uses
double backticks correctly. The same pattern appears in the S115, S117, S118 and S121
quotes (lines 28, 30, 31, 34). Smallest correction: wrap those quotes in double backticks
with padding spaces, as SKILL.md does, for example
``` `` res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED)); `` ```.

## Cross-cutting finding L2 (low): the fixture pin does not cover the code that emits E26-01

- `/home/vgpnk/.local/opt/llama-b11755/llama-server` is a 17,864-byte launcher.
  `readelf -d` shows `NEEDED libllama-server-impl.so` and `RUNPATH $ORIGIN`.
  `rg -l -a -F 'slots endpoint' <install dir>` matches only `libllama-server-impl.so`.
  (GCC stores the literal in pieces, so even there `rg -F 'does not support slots
  endpoint'` exits 1. `strings` shows the fragments `…not support slots endpoint. Start it
  with `--sl…`.)
- count-c1.py pins only `SERVER_SHA256` (the launcher) and `MODEL_SHA256`. SKILL.md:1071-1072
  says the counter "relaunches every trigger against the sha256-pinned binary". That is true
  of the launcher, but the code that emits E26-01 (and every server-side row) lives in an
  unpinned library.
- Observed now: `libllama-server-impl.so` sha256 is
  `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`. Its prefix equals
  the digest the lane recorded earlier in corpus/knowledge/llamacpp-loading-lifecycle.md:106
  (`e404b91a81c9ab65…`). So there is no evidence of drift; this is a gap in pin scope, not a
  wrong observation. The control seat KamaR26CtlCounterMutants already raised it as
  `[INFERENCE]` (controls/KamaR26CtlCounterMutants/REPORT.md:809). It is not listed among
  the counter limits F1-F4 in the lesson.
- Smallest correction (the counter is frozen, so do not edit it). In the SKILL.md:1062-1074
  section preamble, add: "The counter pins the 17,864-byte launcher; the server code is in
  `libllama-server-impl.so` (sha256 `e404b91a…59ed` on 2026-10-23), which the counter does
  not hash." Also add it to the round-26 lesson's counter-limits row as F5. A later round's
  counter should hash the `$ORIGIN` library closure, as `--expect-server-impl-sha256` in
  tests/llamacpp-live/check-receipt.py already does.

## Residual risk and verification gaps

- I did not run the frozen counter. Its port range is 47560-47579 (count-c1.py `PORTS`),
  which is outside this seat's block (47700-47703). I relied on the tip receipt
  c1-tip-receipt.json for the counter's own observation of E26-01.
- No check tested a different build. The row says "observed on this build only", which is correct.
- Router mode (server.cpp:264 `routes.get_slots = models_routes->proxy_get`) was not
  exercised. [INFERENCE] There, a 501 would come from a child server's flags, so "the
  launch" means the child's launch.
- There is no LSP server for these C++ sources in this seat. The code relations above
  (guard, status mapping, route) come from `rg` text search and from reading the pinned
  lines, and they are corroborated by live behavior. They are not semantic proof.

## Commands run (all exit 0 unless noted)

- `sha256sum` of the binary, model, counter and snapshot files; `llama-server --version`.
- `curl -sSfL` of 6 raw files at 704366d, and of the codeload tarball; `tar -xzf`.
- `git -C <lane> archive f4066979… <paths> | tar -x -C tip` (read-only extract), then `cmp` of the 4 files: same.
- `timeout 700 python3 run_e2601.py` (5 server runs, ports 47700-47703); `timeout 400 python3 run_env.py` (3 runs, ports 47700-47702).
- `rg -n -F 'does not support slots endpoint' tree` (one hit); `rg -l -a -F` over the install directory; `readelf -d`; `ldd`; `strings`.
- Final `ss -ltn | rg ':4770[0-3]'` exited 1; `pgrep -af 'llama-server.*477(0[0-3])'` exited 1.

Installs or updates: none.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2601.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/AttackE2601/run_e2601.py`, `run_env.py`, `results.json`, `results-env.json`, `fresh-fetch-sha256.txt`
- `.ufo/waves/round-26/w2-falsify/out/AttackE2601/logs/{trigger-run1,trigger-run2,probe-noslots,control-default,control-slots-on,env-slots0,env-slots0-plus-flag,noslots-props}.log`
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2601/` (fresh-*.cpp/h, tarball and tree, tip extract, logs)
