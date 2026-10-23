ATTACK E26-13 (SKILL.md:1096, registry E26-13, SOURCES S126, lesson Gate S126): holds

One low-severity citation gap (finding L1 below). No check broke.

Tree read: landed tip f4066979096e3452ae731c0e09e50155c6d8258a, extracted with `git archive` to
/fast/scratch/hyaku/kama-r26w2/AttackE2613/tip. `cmp` shows the tip copies of SKILL.md,
registry/error-signatures-r26.json, corpus/SOURCES.md, corpus/lessons/round-26.md and
count-c1.py are identical to the lane working copy. Counter sha256 at tip:
6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588 (matches the pin).
Base 1560e4d8 extracted the same way to .../AttackE2613/base.

Pins re-checked:
- `sha256sum $(readlink -f ~/.local/bin/llama-server)` gives b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 (/home/vgpnk/.local/opt/llama-b11755/llama-server)
- `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` gives 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
- `llama-server --version` prints `version: 0.7.0-dev (build 11755, commit 704366d76)`

## (1) Live re-run of the registered trigger: holds

Before the runs, `ss -ltn | rg ':4774[89]|:4775[01]'` exited 1 (no listener on 47748-47751).
The runner `/fast/scratch/hyaku/kama-r26w2/AttackE2613/run_e2613.py` reads the tip registry entry
and copies count-c1.py `run_trigger`/`http`: the argv is
`llama-server -m <fixture> --host 127.0.0.1 --port P -t 2`, the request uses the same
`json.dumps(body)` encoding, and the Content-Type header is added the same way.

| run | port | command exit | ready | status | body |
|---|---|---|---|---|---|
| 1 | 47748 | 0 | yes (0.25 s) | 500 | `{"error":{"code":500,"message":"audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj","type":"server_error"}}` |
| 2 | 47749 | 0 | yes (0.26 s) | 500 | identical bytes |

The body sha256 in both runs is 95c4ed164f836bc1b6b4f62372585348a0c77288909461edbb4f29df3301433a.
That is byte-identical to `observed.channel_sha256` for E26-13 in
`.ufo/waves/round-26/final/c1-tip-receipt.json:340`. The sha256 of the sent request bytes is
7b169b3667b9852e516aac1d6ddb39a4c1255f13cad9f80eb1d9f28610a57be2. Teardown: both servers ended
with exit 0 after SIGTERM to the process group, `port_closed: true`, and a final `ss` over
47748-47751 exited 1 (no listener). `pgrep -af llama-server` afterwards lists only sibling seats'
servers on ports 47719, 47734 and 47740. None of them are mine.

## (2) Own error text, not F1, F2 or F3: holds

- F1 (a warning line on an unrelated startup failure) does not apply. The channel is http. The
  signature comes from the status-500 response body, which is `format_error_response(e.what(), ERROR_TYPE_SERVER)`
  (server.cpp:70-73 and 82-84; server-common.cpp:107-109). The server log has one
  `W srv operator(): got exception: {...}` line per faulting request. That line is the server
  logging its own error envelope (server.cpp:85). It is a consequence of the fault and not an
  unrelated path, and the counter does not read the log for http rows.
- F2 (echo of the request): for the registered request, the signature is absent from the raw
  sent bytes and from every key and string after a JSON decode. The fragments `audio input` and
  `mmproj` are also absent from every decoded string. The path and headers do not contain it
  either (run1.json and run2.json fields `sig_in_sent_raw`, `sig_in_sent_decoded`,
  `frag_*_in_sent_decoded`, `sig_in_path` and `sig_in_headers` are all false). The body is pure
  ASCII, so no unicode-escape route exists.
- F3 (echo from an argument file): the only extra arguments are `-t 2`. No file argument is
  passed.
- Constant-text probes in run 2, all on the same server. Each status below was observed:
  - an `input_audio` part with no `input_audio` object gives 500 with the same signature;
  - garbage data `zzzz` with format mp3 gives 500 with the same signature;
  - a text part followed by an audio part gives 500 with the same signature;
  - `POST /chat/completions` (no `/v1`) gives 500 with the same signature;
  - an `image_url` part gives 500 with the sibling text `image input is not supported - ...`.

  So the text is fixed by the type guard and does not depend on request data. It fires before
  `handle_media` decodes anything (server-common.cpp:1271-1279).
- Novelty: in the base tree the signature occurs only in raw upstream snapshots
  (`.ufo/waves/round-16/sources/llama.cpp-704366d/server-common.cpp:1272`, and audio-guard code in
  `.ufo/waves/round-21/falsify/out/C2LiveReceiptVerify/fixtures/upstream-704366d76/`). No base
  advice, knowledge or SKILL text describes this fault: the search
  `rg -uu -i 'input_audio|allow_audio|audio input|mmproj' base -g '!**/sources/**'` finds only
  mmproj loading code and help text. Clause (b) scans only SKILL.md and corpus/, so there is no
  predicate issue. The row also passes the lesson's own "held in base-tree wave evidence"
  rejection standard.

## (3) Pinned source and "meaning (code)" cell: holds, with L1

Fresh fetch: `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp`
exited 0 and has sha256 b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442.
`cmp` against the lane snapshot exits 0. Fresh server-context.cpp
(dd1de0f2...2329), server-http.cpp (24ede172...5fdb) and server.cpp (21439622...aef4) also equal
their snapshots. Access date: 2026-10-23.

- server-common.cpp:1270 is `} else if (type == "input_audio") {`, :1271 is
  `if (!opt.allow_audio) {`, :1272 is the throw, and :1273 is `}`. The cited range 1270-1273 is
  exact.
- The guard condition: `allow_audio` is `mctx ? mtmd_support_audio (mctx) : false`
  (server-context.cpp:1632). The fixture has no `--mmproj`, so `mctx` is null and audio is not
  allowed. "throws when audio is not allowed" is correct.
- "chat message parsing": the call chain is `post_chat_completions` (server-context.cpp:5564-5571),
  then `oaicompat_chat_params_parse`, then `oaicompat_content_load_media` (server-common.cpp:1414).
  Both `/chat/completions` and `/v1/chat/completions` are routed through `ex_wrapper`
  (server.cpp:288-289). This matches the observation.
- "the exception surfaces as status 500" is true. Observed 500 twice. The code path:
  `std::runtime_error` is not `invalid_argument` or `common_json_error`, so it is caught as
  `std::exception` and mapped to `ERROR_TYPE_SERVER` (server.cpp:70-73), and
  `format_error_response` maps that to code 500 and type `server_error` (server-common.cpp:107-109).
  See L1.

L1 (low): the 500 mechanism is not cited. Neither the SKILL cell nor S126 cites the lines that
make this throw a 500. The cited lines 1270-1273 only show that it throws. The section framing
says status codes were "observed on this build only" (the lines after SKILL.md:1062), so the
claim is grounded by observation, not by code. `rg 'ex_wrapper|server\.cpp:[0-9]'` over SOURCES.md
and SKILL.md has no match.
Smallest correction: in SKILL.md:1096 and the S126 teaches cell, change
"the exception surfaces as status 500" to
"`ex_wrapper` maps the `std::runtime_error` to `ERROR_TYPE_SERVER`, status 500
(`server.cpp:70-73`, `server-common.cpp:107-109`)".
Both files are pinned in the snapshot dir, so no new SOURCES row is needed for the citation.

## (4) "next action" cell: holds

- "A client-side capability mismatch reported as a server error." This is supported. The cause
  is request content against the `allow_audio` capability, while the type is `server_error`
  because only `invalid_argument` maps to 400 (server.cpp:62-65 vs 70-73).
- "Do not treat this 500 as an outage." Supported by code: the throw happens during request
  parsing, before any task is queued. It is now also supported live (run 2 on the same server):
  `GET /health` returned 200 `{"status":"ok"}` right after the fault, a plain chat completion
  with the same argv returned 200, and `/health` returned 200 again at the end. The wave-1 seat
  also recorded health 200 (`w1-build/out/ExecLoraAudio/RUNS.txt:26-27`).
- "remove audio parts or route to an audio-capable model." Supported by the guard: any
  `input_audio` part triggers it, and only an mtmd context with audio support clears it.
- No overreach found. An optional precision, not a defect: "audio-capable" means a server
  launched with an audio-supporting `--mmproj`. A vision-only mmproj still fails, because
  `mtmd_support_audio` is checked separately from vision (server-context.cpp:1631-1632).

## (5) SOURCES S126 and lesson Gate quote: holds

- The URL `.../blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1272`
  returned HTTP 200 (`curl -w '%{http_code}'`), and #L1272 is the throw line.
- The anchor cell, `server-common.cpp line 1272 @ 704366d76f87...; sha256 b4f4aae7...d442`,
  equals the fresh-fetch sha256 and the counter's `SOURCE_SHA256["server-common.cpp"]`.
- The row has 11 cells. kind=code, tier=A, status=mined, opened=2026-10-23,
  recheck=on-release, and used-by=`SKILL.md, registry/error-signatures-r26.json` all match the
  sibling rows S124, S125 and S127.
- The scope cell says the row covers line 1272 and its guard at 704366d76 only. That is
  accurate. The teaches cell has the same gap as L1 and the same correction.
- The lesson Gate (corpus/lessons/round-26.md:39) has the same URL and access date 2026-10-23.
  Its quote, after the leading indentation is stripped, is byte-identical to source line 1272
  (shell `[ "$Q" = "$SRC" ]` printed QUOTE_EXACT). It is 19 words, within the 25-word limit.

## Residual risk and verification gaps

- I did not run the frozen counter. This seat's job was the trigger on my own port block, and
  the counter uses 47560-47579. The receipt's E26-13 body hash is reproduced byte for byte
  instead.
- I did not run a positive control with an audio-capable mmproj, because the lane has no such
  model. The claim that an audio-capable model clears the guard rests on code (server-context.cpp:1632).
- [INFERENCE] The same signature is reachable through the other `oaicompat_chat_params_parse`
  callers (server-context.cpp:5632, 5668, 5690, 5715 and 6273) and through
  `tokenize_oai_content_array` (server-common.cpp:1313). I did not exercise them. This does not
  affect the row, whose trigger is pinned.

## Installs

None.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/AttackE2613.md (this report)
- .ufo/waves/round-26/w2-falsify/out/AttackE2613/run1.json, run1.server.log
- .ufo/waves/round-26/w2-falsify/out/AttackE2613/run2.json, run2.server.log
- scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2613/{run_e2613.py, server-common.cpp.fresh,
  server-context.cpp.fresh, server-http.cpp.fresh, tip/, base/}
