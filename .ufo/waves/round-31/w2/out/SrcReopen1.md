# SrcReopen1 — re-open S180 and S181 (falsify, claim C1)

Scope: rows S180 and S181 in `corpus/SOURCES.md`. Falsifier seat; nothing modified.
Full receipts: `.ufo/waves/round-31/w2/out/SrcReopen1/report.md` (+ raw logs in the
same directory).

## Row data (verbatim from the `## Registry` table)

S180 (SOURCES.md line 192):
- URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1360
- access: "L1360 @ 704366d, opened 2026-10-23"; date cell `2026-10-23`
- quote: `` `throw std::runtime_error("Cannot use both json_schema and grammar");` ``
- used-by: `corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json`

S181 (SOURCES.md line 193):
- URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1375
- access: "L1375 @ 704366d, opened 2026-10-23"; date cell `2026-10-23`
- quote: `` `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` ``
- used-by: `corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json`

## Resolution against the pinned snapshot

`.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp`
sha256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`, 75061 bytes —
matches `SNAPSHOT.json` pin for `tools/server/server-common.cpp` @ 704366d.

- `sed -n '1360p'` → `        throw std::runtime_error("Cannot use both json_schema and grammar");`
- `sed -n '1375p'` → `            throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);`

## Verdicts (one line each)

`S180: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes`

`S181: quote-verbatim yes; words 15; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes`

Both rows sit inside the `## Registry` section (table lines 9–204; rows at 192–193,
before the next `##` at line 205). Both quotes occur verbatim on their pinned lines;
word counts 7 and 15 (≤ 25). Both `used-by` targets exist at lane tip.

## What this does NOT show

- Only S180/S181 opened; S182–S191 unchecked.
- `used-by` files exist but were not verified to reference S180/S181 or apply the
  taught behavior.
- The teaches claims (500 server_error surfacing; offending value appended) not
  verified against surrounding code context.
- SNAPSHOT.json pins only 4 of the 7 snapshot files; the file used here is pinned
  and hash-matched.
- No tools installed/upgraded.
