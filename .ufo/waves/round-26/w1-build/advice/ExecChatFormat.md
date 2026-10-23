# ExecChatFormat advice (kama round-26 wave-1, claim C1 candidate rows)

Verdict: 17 distinct chat-completions request-validation error signatures reproduced live twice each on the lane fixture and counted 17/17 by the frozen counter in a scratch extract (registered 17 counted 17 target 12 met True).

## What I ran and found

- Blog: llama-server b11755 (build 11755, commit 704366d) at `~/.local/bin/llama-server` sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804; fixture model `stories260K.gguf` sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d. Both match the counter pins.
- Source: `server-common.cpp` at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad. Fresh fetch of `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp` on 2026-10-23 (curl exit 0) sha256 b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442, byte-identical to the lane snapshot and the counter pin (copy kept at `out/ExecChatFormat/raw/server-common-704366d-raw-fetch.cpp`).
- Channel: HTTP, endpoint `/v1/chat/completions` (one same-signature spot-check also on `/apply-template`: 400, identical message). Status 400 for `std::invalid_argument` throws, 500 for `std::runtime_error` throws (both >= 400). Error bodies are JSON `{"error":{"code":...,"message":"...","type":...}}`; each signature appears verbatim in the body.
- Each fault was reproduced twice with independent server launches (pass1 + pass2 matrices) on ports 47652-47655, one child at a time, each launch killed and port-confirmed closed before the next. No listener of mine remains in the block.

## Confirmed candidate rows (17)

All rows: `"channel": "http"`, `"model": "fixture"`, `"occupy_port": false`, `"source": {"file": "server-common.cpp"}`, path `/v1/chat/completions`, method POST, header Content-Type application/json. `args` empty except rows 08/09 (`--no-jinja`). Source line anchors at 704366d76 (access date 2026-10-23); the signature itself is the located quote (<= 25 words) from that line.

| id | signature (verbatim) | source line | args |
|---|---|---|---|
| CHATFMT-01 | `'messages' is required` | server-common.cpp:1386 | |
| CHATFMT-02 | `Expected 'messages' to be an array` | server-common.cpp:1390 | |
| CHATFMT-03 | `All non-assistant messages must contain 'content'` | server-common.cpp:1395 | |
| CHATFMT-04 | `Assistant message must contain either 'content' or 'tool_calls'!` | server-common.cpp:1399 | |
| CHATFMT-05 | `Expected 'content' to be a string or an array` | server-common.cpp:1411 | |
| CHATFMT-06 | `unsupported content[].type` | server-common.cpp:1302 | |
| CHATFMT-07 | `response_format type must be one of ` (constant prefix; observed body continues `"text" or "json_object", but got: xml`) | server-common.cpp:1375 | |
| CHATFMT-08 | `tools param requires --jinja flag` | server-common.cpp:1343 | `--no-jinja` |
| CHATFMT-09 | `tool_choice param requires --jinja flag` | server-common.cpp:1346 | `--no-jinja` |
| CHATFMT-10 | `Cannot use both json_schema and grammar` | server-common.cpp:1360 | |
| CHATFMT-11 | `(expected boolean, got string)` (observed body: `invalid type for "enable_thinking" (expected boolean, got string)`) | server-common.cpp:1473 | |
| CHATFMT-12 | `Cannot have 2 or more assistant messages at the end of the list.` | server-common.cpp:1434 | |
| CHATFMT-13 | `Cannot set both add_generation_prompt and continue_final_message to true.` | server-common.cpp:1440 | |
| CHATFMT-14 | `Cannot continue an assistant message that contains tool calls.` | server-common.cpp:1446 | |
| CHATFMT-15 | `top_logprobs requires logprobs to be set to true` | server-common.cpp:1521 | |
| CHATFMT-16 | `Cannot use custom grammar constraints with tools.` | server-common.cpp:1455 | |
| CHATFMT-17 | `logprobs is not supported with tools + stream` | server-common.cpp:1517 | |

Notes on choices:

- All 17 signatures are >= 20 bytes, occur verbatim in the pinned `server-common.cpp`, absent at base 1560e4d8 (`git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` exit 1 for every one), absent from `llama-server --help`/`--version` output (both exit 0; 0 matches), absent from the healthy baseline requests (`/health`, `/v1/models`, `/props`, `/slots`, `/completion`, `/v1/chat/completions` healthy, `/tokenize`), and never appear in the request bodies (no echo).
- Clause (g) holds within this set: no signature is a substring/superstring of another and every trigger (args + request) differs.
- Rows 07 and 11 use un-quoted substrings because the source literal has backslash-escaped quotes (`\"text\"`, `\"enable_thinking\"`) that decode to plain quotes in the HTTP body; the chosen slice is verbatim in both the source text and the observed body.
- Reproductions and one-off attempts that were dropped because they are NOT citable/valid:
  - `{"messages":[123]}` and `{"role":"user"}` both map to the same fault as CHATFMT-03 (one row kept).
  - object `tool_choice` without jinja is silently defaulted to `auto` by `json_value` (status 200, no error); string `tool_choice: "required"` with `--no-jinja` is the real trigger for CHATFMT-09.
  - `continue_final_message: true` without `add_generation_prompt: false` trips CHATFMT-13; with `add_generation_prompt: false` it trips CHATFMT-14.
  - invalid-role messages (`{"role":"pirate","content":"x"}`) are not rejected by `server-common.cpp` (the role check lives in common chat code not in the pinned file set), so no counted row for roles beyond content-presence faults.
  - `--jinja` default for this fixture is effectively on (tools accepted and a completion returned), hence CHATFMT-08/09 require the `--no-jinja` arg.

## Verification evidence

- `out/ExecChatFormat/candidates.json` — 17 registry entries (id CHATFMT-01..17, source rows S901..S917, file server-common.cpp).
- `out/ExecChatFormat/RUNS.txt` — every command, port, status, and exit code (including the two full repro passes and the hammer run).
- `out/ExecChatFormat/raw/repro/pass1/`, `pass2/` — per-fault `req.json`, `body`, `status`, `server.log`, `args`; plus `APPLY-C-msg-no-content` and J2/O2 runs (raw outputs).
- `out/ExecChatFormat/raw/llama-server-help.txt`, `llama-server-version.txt`, `server-common-704366d-raw-fetch.cpp`, `verify.py` — informational baselines and fresh-fetch bytes.
- `out/ExecChatFormat/counter-receipt.json` — frozen-counter receipt.

## Frozen counter check (scratch)

Ran inside a `git archive a23c0e042114016a909eb15173aa6df74b5b7eb0` extract at `/fast/scratch/hyaku/kama-r26/extract` (lane files untouched), with placeholder SKILL rows for the section `## Round-26 live error signatures`, SOURCES rows S901-S917, and a registry copy, all added in the scratch extract only:

```
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 \
  python3 .ufo/waves/round-26/count-c1.py --lane /fast/scratch/hyaku/kama-r26/extract \
  --out /fast/scratch/hyaku/kama-r26/ExecChatFormat/counter-receipt.json
exit: 0
stdout: registered 17 counted 17 target 12 met True not-counted []
```

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecChatFormat/candidates.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecChatFormat/RUNS.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecChatFormat/counter-receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecChatFormat/raw/...` (repro runs, help/version, verify.py, raw fetch)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/advice/ExecChatFormat.md` (this report)

## Risks / blockers

- The L1 will need to assign final registry ids and SOURCES row numbers (I used placeholder CHATFMT-xx and S901-S917) and land the SKILL.md section + SOURCES rows in the lane; the scratch proved all 17 count under the frozen predicate.
- CHATFMT-07 and CHATFMT-11 are intentionally partial strings (constant parts of format strings whose source literals contain escaped quotes); they are verbatim in both source text and observed channel text.
- No tool installations were performed (no new tool needed); no pacman transactions were attempted.
- Server hygiene: no llama-server process of mine remains (peers' servers on 47605/47625 untouched); ports 47652-47655 are free.
