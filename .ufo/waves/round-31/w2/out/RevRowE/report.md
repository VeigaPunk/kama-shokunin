```RESULTS
$ /usr/bin/git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowE/clone
exit 0
verbatim tail:
Cloning into '/tmp/kama-r31w2/RevRowE/clone'...
done.

$ /usr/bin/git -C /tmp/kama-r31w2/RevRowE/clone checkout --detach 382d11b2107d335705875da1a4d889b074bd6fa6
exit 0
verbatim tail:
HEAD is now at 382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts

$ /usr/bin/sha256sum /tmp/kama-r31w2/RevRowE/clone/.ufo/waves/round-31/count-c1.py /home/vgpnk/.local/opt/llama-b11755/llama-server /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
exit 0
verbatim tail:
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /tmp/kama-r31w2/RevRowE/clone/.ufo/waves/round-31/count-c1.py
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  /home/vgpnk/.local/opt/llama-b11755/llama-server
e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed  /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf

$ /usr/bin/env TMPDIR=/tmp/kama-r31w2/RevRowE /usr/bin/python3 /tmp/kama-r31w2/RevRowE/clone/.ufo/waves/round-31/count-c1.py --lane /tmp/kama-r31w2/RevRowE/clone --repo /tmp/kama-r31w2/RevRowE/clone --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE/full-live.json
exit 0
verbatim tail:
registered 18 counted 17 target 12 met True not-counted ['K31-10']

$ /usr/bin/env TMPDIR=/tmp/kama-r31w2/RevRowE /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE/probe.py
exit 0
verbatim tail:
{"content_type": "application/json; charset=utf-8", "label": "base", "n_choices": 1, "slot_task": 0, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "application/json; charset=utf-8", "label": "K31-13", "n_choices": 1, "slot_task": 3, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "application/json; charset=utf-8", "label": "K31-14", "n_choices": 1, "slot_task": 6, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "application/json; charset=utf-8", "label": "K31-15", "n_choices": 1, "slot_task": 9, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "application/json; charset=utf-8", "label": "K31-16", "n_choices": 2, "slot_task": 13, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "text/event-stream", "label": "K31-17", "n_choices": null, "slot_task": 16, "sse": true, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "text/event-stream", "label": "K31-18", "n_choices": null, "slot_task": 19, "sse": true, "status": 200, "usage_frames": 1, "user_in_slot_params": false}
{"content_type": "application/json; charset=utf-8", "label": "include-usage-without-stream", "n_choices": 1, "slot_task": 22, "sse": false, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"content_type": "text/event-stream", "label": "stream-with-usage-false", "n_choices": null, "slot_task": 25, "sse": true, "status": 200, "usage_frames": 0, "user_in_slot_params": false}
{"label": "K31-13", "messages_equal_base": false, "normalized_equal_base": true, "slot_delta_keys_exact": []}
{"label": "K31-14", "messages_equal_base": false, "normalized_equal_base": true, "slot_delta_keys_exact": []}
{"label": "K31-15", "messages_equal_base": false, "normalized_equal_base": true, "slot_delta_keys_exact": []}

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE/compare-cells.py
exit 0
verbatim tail:
K31-13 | committed-cell==rendered yes | 200 | overclaim none
K31-14 | committed-cell==rendered yes | 200 | overclaim none
K31-15 | committed-cell==rendered yes | 200 | overclaim none
K31-16 | committed-cell==rendered yes | 200 | overclaim none
K31-17 | committed-cell==rendered yes | 200 | overclaim none
K31-18 | committed-cell==rendered yes | 200 | overclaim none

$ /usr/bin/env TMPDIR=/tmp/kama-r31w2/RevRowE /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowE/tools-context-probe.py
exit 0
verbatim tail:
{"error": null, "label": "grammar-alone", "n_choices": 1, "status": 200}
{"error": {"code": 400, "message": "Cannot use custom grammar constraints with tools.", "type": "invalid_request_error"}, "label": "same-grammar-with-K31-15-tools", "n_choices": 0, "status": 400}
```

FINDING: All six outcome cells match manual rendering byte for byte and reproduce live. Their meaning cells do not overclaim at the stated fixture scope; the broader inference that `ignored` means no response/semantic effect is falsified.

LIMITS: One full frozen-counter run, one raw six-row probe with two streaming controls, and one paired tools/grammar control on b11755/stories260K/default argv. This does not establish sampler use, tool execution, tool concurrency, real-time delivery timing, whole-response equality, other builds, or C1 improvement/admission. The raw probes reuse the unmodified counter's server lifecycle/HTTP/slot helpers, not its renderer or outcome judgment. No canonical judge or other orchestration runtime was invoked. No tools were installed or updated. All writes are inside this seat directory or its single `/tmp` scratch root; the requested flat `w2/out/RevRowE.md` alias was not created because it is outside the developer-authorized seat write directory.

## Axes

- **Depth:** distinguish reproduced endpoint observations from unmeasured session/sampler behavior.
- **Calibration:** keep the meaning and outcome interpretation within the observable projection.
- **Operability:** fresh pinned clone, recorded commands/raw evidence, own-server lifecycle only.

## Required row lines

```text
K31-13 | committed-cell==rendered yes | 200 | overclaim none
K31-14 | committed-cell==rendered yes | 200 | overclaim none
K31-15 | committed-cell==rendered yes | 200 | overclaim none
K31-16 | committed-cell==rendered yes | 200 | overclaim none
K31-17 | committed-cell==rendered yes | 200 | overclaim none
K31-18 | committed-cell==rendered yes | 200 | overclaim none
```

These `overclaim` results concern the actual **meaning** cells, not a blanket endorsement of the registry kind `ignored` or its outcome wording.

## Manual derivation, independent of counted status

The frozen file's RENDER rules are actually at docstring lines **50–54**; lines 40–46 are discrimination rules. I read each registry row and the committed SKILL rows at lines 1259–1264 from the fresh checkout of `382d11b2107d335705875da1a4d889b074bd6fa6`.

- K31-13, K31-14, K31-15: `kind=ignored` chooses the fixed literal `200, no slot-parameter or response change`.
- K31-16: `kind=response`, `check=n_choices`, JSON integer `2` yields `200, n_choices = 2`.
- K31-17: `kind=response`, `check=sse`, JSON boolean `true` yields `200, sse = true`.
- K31-18: `kind=response`, `check=sse_usage`, JSON boolean `true` yields `200, sse_usage = true`.

`compare-cells.py` contains those hand-derived literals; it never imports/calls the renderer. It strips only Markdown cell boundary padding as the frozen parser does, then compares UTF-8 bytes. `row-review.json` retains each registry row, committed outcome, manually rendered outcome, meaning, comparison, and live block. `scoped-live.json` extracts the six live blocks directly from the unmodified full receipt `full-live.json`.

## Meaning-cell attacks

| id | Evidence beyond the counter's count | Boundary of the meaning claim |
|---|---|---|
| K31-13 | Raw probe: HTTP 200, no `user` key in newest slot params, exact empty slot delta, normalized response equal to base. | “This request produced no stored user field” is directly supported; it does not promise that no other subsystem consumed `user`. |
| K31-14 | Raw probe: HTTP 200, exact empty slot delta and normalized equality; request has no tools. Pinned `server-common.cpp:1426` nevertheless reads `parallel_tool_calls` into chat-template inputs. | Its explicit no-tools/no-concurrency-inference qualifier is necessary and sufficient; no tool-concurrency behavior was measured. |
| K31-15 | Raw probe: HTTP 200, exact empty slot delta, normalized equality, assistant text rather than a tool call. Paired context control below proves `tools` is consumed elsewhere. | “Do not assume advertised tools run; inspect returned messages” is cautious advice, not a claim that tools are universally ignored. A one-token, `hi` request cannot establish tool-call capability or incapability. |
| K31-16 | Full receipt has `live={"status":200,"observed":2}`; raw independent probe has two choices. | Exactly supports “This b11755 request returned two choices”; no quality/build-generalization claim. |
| K31-17 | Full receipt has `live={"status":200,"observed":true}`; raw body has JSON `data:` frames and `data: [DONE]`, with `text/event-stream`. | Supports parsing the observed frame/termination contract, not token delivery latency or uninterrupted network streaming. |
| K31-18 | Full receipt has `live={"status":200,"observed":true}`; raw stream has one usage frame. Same `include_usage:true` without `stream:true` returns ordinary JSON and zero SSE frames; `stream:true, include_usage:false` returns SSE without a usage frame. | The additional controls support the explicit-streaming advice on this fixture; the positive counter row alone would not prove necessity. |

The three ignored live blocks contain HTTP 200 and identical normalized fields: one choice, no logprobs, 42 prompt tokens, top keys `choices/created/id/model/object/system_fingerprint/timings/usage`, choice keys `finish_reason/index/message`, and usage keys `completion_tokens/prompt_tokens/prompt_tokens_details/total_tokens`. They do **not** retain raw slot params or full response messages; those are saved separately in `probe-raw.json`.

## Strongest counterexample and smallest safe correction

**Counterexample:** Keep the same base request plus `grammar: 'root ::= "a"'`. With no tools, it returns HTTP 200. Add only the exact K31-15 tools value: it returns HTTP 400 with `{code:400,message:"Cannot use custom grammar constraints with tools.",type:"invalid_request_error"}`. Thus the K31-15 parameter is not semantically ignored by the adapter in general, even though the frozen row's bounded slot/normalized-response check reproduces. This agrees with the pinned adapter's tools parse at `server-common.cpp:1336–1347,1421` and tools/grammar constraint at `1453–1455`. Raw pair: `tools-context-raw.json`; process log: `tools-context-server.log`.

**Additional projection counterexample:** Base assistant content was `A`, while K31-13 returned `H`, K31-14 returned a quotation mark, and K31-15 returned `W`; all three still had equal normalized responses and empty exact slot deltas. These unseeded samples do **not** establish that the parameters caused those content differences. They do directly establish that “normalized response equal” is not “whole response equal,” even apart from volatile ids/timings. See the raw `*-body.txt` files and `probe-raw.json`; the normalizer at frozen counter lines 233–247 omits message content, finish-reason values, and usage values other than prompt tokens.

**Impacted axes:** depth and calibration if the frozen `ignored` label or “no … response change” string is promoted to a semantic no-effect claim. No regression in the scoped meaning cells was found. This evidence does not repair the separate C1 shortcut/admission defect.

**Smallest safe correction:** Preserve the frozen counter and committed measurement. In presentation, explicitly qualify K31-13–15 as “no slot-parameter or normalized-response change in this sample,” never “parameter ignored in general.” Route a literal-render/label correction to a separately frozen future instrument if desired; do not change this round's measurement rule after scoring. This is a fixable precision defect, not evidence authorizing admission or an axis tradeoff to conceal. Judgment remains with the canonical Rust judge.

## Evidence inventory

- `commands.json` and `clone.log`, `checkout.log`, `pins.log`, `counter-full-live.log`, `probe.log`, `compare-cells.log`, `tools-context-probe.log`: exact commands, exits, and raw output.
- `full-live.json`: complete unmodified frozen-counter receipt, covering all registry rows in one full live run.
- `scoped-live.json`, `row-review.json`: extracted six-row evidence and independent byte comparisons.
- `probe.py`, `probe-raw.json`, `probe-server.log`, `base-body.txt`, `K31-13-body.txt` through `K31-18-body.txt`, `include-usage-without-stream-body.txt`, `stream-with-usage-false-body.txt`: reproducible raw six-row/stream-control evidence.
- `tools-context-probe.py`, `tools-context-raw.json`, `tools-context-server.log`: minimal tools-consumption counterexample.
- `compare-cells.py`: manually rendered expected literals and byte comparison, with no use of the renderer under review.
