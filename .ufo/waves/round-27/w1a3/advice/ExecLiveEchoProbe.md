VERDICT: holds — on llama-server b11755 (commit 704366d76) the pinned S137 site returns a 400 whose message holds the JSON-decoded `response_format.type` for every raw spelling tested, including spellings whose bytes never contain the signature, and one fixed message frame covers two distinct request-chosen signatures.

# ExecLiveEchoProbe — live probe of the S137 echo site (X1 evidence)

Seat: `KamaR27A3.ExecLiveEchoProbe` (leaf). Claim served: X1 evidence for
S137 and entry fact 2 of `corpus/knowledge/echo-discriminating-counters.md`.
Port block 47680-47681 used; one server; killed; port confirmed closed.
Tool installs: **none**. No count-c1.py `main()` was run; the frozen counter
was imported function-level only (its `main()` is guarded at
`.ufo/waves/round-27/count-c1.py:744`).

## Verdict basis

A POST to `/v1/chat/completions` with
`{"response_format":{"type": X}}` for an invalid `X` is rejected at
`server-common.cpp:1375` with HTTP 400 and

```
response_format type must be one of "text" or "json_object", but got: <decoded X>
```

Five error requests were sent: signature A (`echo_sig_9f3a`) spelled plain,
first-character `\u00XX`, and fully `\u`-escaped; signature B
(`alt_sig_4b7e`) spelled plain and fully `\u`-escaped. All five returned 400
with the decoded signature in the message. For the three A spellings the
**response bodies are byte-identical** (sha256 `9ea801fb…5a06`); for the two
B spellings likewise (`96398469…7dc3`). Raw request escape spelling is
therefore erased before the message is rendered.

## Provenance (measured, receipt.json `provenance`)

| item | value |
|---|---|
| binary | `/home/vgpnk/.local/opt/llama-b11755/llama-server` |
| binary sha256 | `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` |
| `--version` | `version: 0.7.0-dev (build 11755, commit 704366d76)` / `built with GNU 11.4.0 for Linux x86_64` (exit 0) |
| control `system_fingerprint` | `b11755-704366d76` |
| model | `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` |
| model sha256 | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (1,185,376 B) |
| pinned source | raw fetch of `tools/server/server-common.cpp` @ 704366d76, sha256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` — equals S137's raw hash |
| S137 site | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` at `server-common.cpp:1375`, inside `oaicompat_chat_params_parse` |
| server cmdline | `…/llama-server -m …/stories260K.gguf --host 127.0.0.1 --port 47680 -c 256 -t 2` |
| health | `GET /health` → 200 `{"status":"ok"}` |
| shutdown | SIGTERM; process exited 0; `ss -ltn` and `pgrep -af 'port 47680'` both empty (exit 1) |
| server log | `server-47680.log`, sha256 `019a472c87a84d77feab43eca9f1a55b24bfa087efa89825780cd17fefd76b81` |

## Requests and responses (all raw bytes retained in this directory)

| case | req bytes | req sha256 | status | sig literal in req raw | sig literal in resp raw | decoded sig in message | resp sha256 |
|---|---|---|---|---|---|---|---|
| req1-plain | 103 | `da701328…4b0b` | 400 | yes | yes | yes | `9ea801fb…5a06` |
| req2-firstesc | 108 | `88eb59cb…93c3` | 400 | **no** | yes | yes | `9ea801fb…5a06` |
| req3-fullesc | 168 | `25644d42…6260` | 400 | **no** | yes | yes | `9ea801fb…5a06` |
| req5-altsig-plain | 102 | `500acd73…729f` | 400 | yes | yes | yes | `96398469…7dc3` |
| req6-altsig-full | 162 | `7a423f1b…2820` | 400 | **no** | yes | yes | `96398469…7dc3` |
| req4-control | 60 | `39c0d086…42ae` | **200** | – | – | – | `e05c731e…898d` |

Raw request bodies (exact, no trailing newline):

```
req1 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"response_format":{"type":"echo_sig_9f3a"}}
req2 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"response_format":{"type":"\u0065cho_sig_9f3a"}}
req3 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"response_format":{"type":"\u0065\u0063\u0068\u006f\u005f\u0073\u0069\u0067\u005f\u0039\u0066\u0033\u0061"}}
req5 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"response_format":{"type":"alt_sig_4b7e"}}
req6 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"response_format":{"type":"\u0061\u006c\u0074\u005f\u0073\u0069\u0067\u005f\u0034\u0062\u0037\u0065"}}
req4 {"messages":[{"role":"user","content":"hi"}],"max_tokens":1}
```

Response body for req2 (identical bytes to req1 and req3; 153 B,
`Content-Type: application/json; charset=utf-8`):

```
{"error":{"code":400,"message":"response_format type must be one of \"text\" or \"json_object\", but got: echo_sig_9f3a","type":"invalid_request_error"}}
```

Control returned a real completion (`finish_reason":"length"`, 1 token,
`system_fingerprint":"b11755-704366d76"`), so the 400s are validation
faults on a healthy server, not a dead process.

## Function-level replay through the frozen counter (`replay-function-level.json`)

Imported `count-c1.py` (sha256 `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`,
equal to the frozen pin) and called `occurs` (`:347`), `json_strings`
(`:351`), `request_surfaces` (`:365`); the echo check is `f:in-request` at
`:587` and the frame clause `h:same-message-frame` at `:709`.
Round-26 comparator: `c["e_not_echoed"] = sig not in req_bytes`
(`git show eb09e742:.ufo/waves/round-26/count-c1.py` line 384).

| case | round-26 raw-byte test credits "not echoed" | A3 clause (f) refuses echo | live message holds sig | frame (sig cut, lowercase) |
|---|---|---|---|---|
| req1-plain | no | **yes** | yes | `response_format type must be one of "text" or "json_object", but got: \0` |
| req2-firstesc | **yes (false credit)** | **yes** | yes | same |
| req3-fullesc | **yes (false credit)** | **yes** | yes | same |
| req5-altsig-plain | no | **yes** | yes | same |
| req6-altsig-full | **yes (false credit)** | **yes** | yes | same |

`clause_h_all_frames_equal = true`; frame length 71. Three of the five live
rows would be credited by the raw-byte predicate although the message
contains the signature (two of the three A-spelling rows); the frozen A3
clause (f) refuses all five, and clause (h) collapses all five — two distinct
signatures — onto one frame. This is exactly entry fact 2 ("One frame of this
kind serves any number of 'signatures'") observed live.

## Commands and exit codes (trimmed)

| # | command | exit | evidence |
|---|---|---|---|
| 1 | `~/.local/opt/llama-b11755/llama-server --version` | 0 | `build 11755, commit 704366d76` |
| 2 | `curl -fsS -o server-common.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f…/tools/server/server-common.cpp` | 0 | sha256 `b4f4aae7…d442` = S137 |
| 3 | `sed -n '1355,1385p' server-common.cpp` | 0 | throw at `:1375` (read output line-numbered) |
| 4 | server start (bash service, `ulimit -f 1048576` inside, log redirected) | ready | pid 3140745 on 127.0.0.1:47680 |
| 5 | `GET /health` | 200 | `{"status":"ok"}` |
| 6 | `python3 probe.py` (under `ulimit -f 1048576` + `timeout 300`) | 0 | six POSTs, receipt.json written |
| 7 | `grep -c -F 'echo_sig_9f3a' req*.req` / `req*.resp`; `od -c req2-firstesc.req` | 0 | req2/req3/req6 raw literals 0; all three matching resps 1; `od` shows `\ u 0 0 6 5 …` |
| 8 | `kill -TERM 3140745`; `ss -ltn \| grep ':47680 '`; `pgrep -af 'port 47680'` | — / **1** / **1** | process exit 0; no listener; no matching process (only sibling seats' 47636/47637/47644 remain) |
| 9 | `python3 replay.py` | 0 | replay-function-level.json |
| 10 | `python3 provenance.py` | 0 | receipt provenance merged; `observed_at_utc 2026-10-23T07:11:54Z` |

Counter hash re-measured at probe time: `sha256sum .ufo/waves/round-27/count-c1.py`
→ `49491b80…2765` (matches the frozen value).

## Interpretation

- S137's teaching holds live on this build: the fixed frame is rendered once
  and the **decoded** request value is spliced in. A `\u0065`-escaped spelling
  that appears nowhere in the raw request bytes appears decoded in the 400.
- Entry fact 2 holds live: two distinct signatures and three spellings
  collapse to one frame after cutting the signature; the response body is
  byte-identical across spellings of the same value.
- The round-26 raw-byte echo test is demonstrably insufficient on these
  fixtures (3/5 false credits); the frozen A3 clause (f) refuses all five,
  and clause (h) credits one row for the five.
- [INFERENCE] Response-byte identity follows from parsing the body into JSON
  and rendering `response_type`, as `server-common.cpp:1365-1375` shows;
  the live result is consistent with that code path and does not prove other
  error sites behave the same.
- [INFERENCE] A counter whose echo comparison decodes the request body at any
  depth (as clause (f) does) catches this class; one that compares raw bytes
  or only the request path does not.

## Risks, limits, blockers

- One build and one site: b11755 @ 704366d76, `/v1/chat/completions`
  `response_format.type` only. Other `json_value`-spliced messages and other
  builds are unmeasured here.
- ASCII-only signatures. Non-ASCII escapes (`\uXXXX` beyond ASCII, surrogate
  pairs) and UTF-8-versus-escaped serialisations were not probed; KQ37's rule
  names both serialisations, but this probe does not exercise that half.
- The server log also contains the decoded message with the signature
  (`server-47680.log` lines for every 400), so a counter reading the **log**
  channel sees the echo too. Clause (f) is request-side only; log-channel
  echoes from non-request sources remain a separate class the knowledge doc
  already names.
- No blockers. The probe is a live observation of one build; it is evidence
  for the later non-author reviewer, not the X1 verdict.

## Artifacts (all under `.ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/`)

`receipt.json` (status, sha256 of every request/response body, booleans,
provenance), `replay-function-level.json`, `req1…req6.req`/`.resp`,
`props.json`, `server-47680.log`, `probe.py`, `replay.py`, `provenance.py`,
and `manifest.sha256` (hashes of all 19 files; manifest itself excluded).
Scratch: `/fast/scratch/hyaku/kama-r27c/ExecLiveEchoProbe/`.
