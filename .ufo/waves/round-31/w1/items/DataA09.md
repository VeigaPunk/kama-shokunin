/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item K31-09 — live measurement and row draft: `messages`
Claim served: C1 (depth, predicate `counted >= 12`).

Measure the pinned llama-server b11755 (`~/.local/opt/llama-b11755/llama-server`,
sha256 b6a31a8e…d804, LD_LIBRARY_PATH=~/.local/opt/llama-b11755) with model
`~/.cache/kama-shokunin/models/stories260K.gguf` (sha256 270cba1b…256d), default argv
`-m <model> --host 127.0.0.1 --port <port>` on a free port 47900-47999.

Protocol: POST /v1/chat/completions with the base body
`{"messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}`, then the same body updated
with `'messages': [{"role": "user", "content": 42}]` (plus any `also` keys the hint names), then GET /slots and pick
the slot with the largest `id_task`. Record: HTTP status, the exact response/error body, the newest
slot's `params` before and after, and `usage.prompt_tokens`.

Hint to verify or refute (never assume it): reject: content must be a string or an array

Produce `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/DataA09/row.json` with exactly:
{"id": "K31-09", "param": "messages", "sent": [{"role": "user", "content": 42}], "outcome": {...},
 "source": {"row": "S<assigned below>", "file": "server-common.cpp", "line": 1411, "contains": "<verbatim substring of that line>"},
 "also": {...} only when the row needs extra body keys,
 "observed": {"status": <int>, "slot_delta": {...}, "response_excerpt": "<first 300 chars>",
   "prompt_tokens": <int>, "server_log_tail": "<last 5 lines>"}}
The `outcome` object must be one of the counter's four kinds and must match what you measured:
reject -> {"kind":"reject","status":<int>,"type":"<error.type>","message":"<error.message verbatim>"};
slot -> {"kind":"slot","set":{"<key>":<value>}}; ignored -> {"kind":"ignored"};
response -> {"kind":"response","check":"n_choices|has_logprobs|sse|sse_usage","value":<json>}.

Also write the SKILL table cell text this row must carry, using the counter's RENDER rule verbatim
(docstring of count-c1.py): `render.txt` with one line = the `outcome` cell (e.g.
`200, n_probs = 20`, `reject 400 invalid_request_error: <message>`, `200, no slot-parameter or
response change`, `200, n_choices = 2`), and `meaning.txt` with a client consequence sentence of at
least eight words (what a caller must do or must not assume).

To prove your row counts before you finish, make your own scratch clone
(`git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/r31w1-DataA09 && cd /tmp/r31w1-DataA09 && git checkout -q 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`),
add your row to `registry/chat-param-outcomes-r31.json` (create it with the build pins and base_body
from the frozen pilot `.ufo/waves/round-31/before/pilot-c1.json` and `preregistration.json`), add the
SKILL section + table and an S### row to your clone's SKILL.md/corpus/SOURCES.md, then run
`/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo . --tip <clone commit> --out out.json`
and iterate until the summary shows your row counted (or report exactly why it cannot be).
Report the counter summary line and your row's `reasons` entry.
