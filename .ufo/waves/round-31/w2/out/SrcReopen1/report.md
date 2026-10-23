# SrcReopen1 — re-open S180 and S181 (falsify)

Scope: rows S180 and S181 in `corpus/SOURCES.md` (claim C1, depth — twelve new SOURCES
rows S180–S191 pinned to llama.cpp 704366d). Falsifier seat: nothing was modified.

```
RESULTS
$ grep -n '^## ' corpus/SOURCES.md | head -40
exit 0
9:## Registry
205:## Paths
212:## Search log
226:## Leads (unopened)
361:## Round-20 source correction — S065
372:## Round-21 falsify corrections — S066–S074 (appended 2026-10-21)
390:## Round-22 bounded source search (2026-10-21)
404:## Round-22 routed correction-row repair
415:## Round-22 residual-source clarification
425:## Round-30 source correction — S174 and S176 (append-only decision record)
440:## Round-31 rows relocated into the registry (repair, 2026-10-23)
→ S180 (line 192) and S181 (line 193) sit inside the Registry table (lines 9–204),
  before the next `##` heading at line 205. Registry-section membership: YES.

$ sed -n '192p' corpus/SOURCES.md   (S180 row, verbatim)
exit 0
| S180 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1360 | code | A | the adapter refuses a request that sends both a JSON schema and a grammar, and the refusal surfaces as a 500 server_error | L1360 @ 704366d, opened 2026-10-23 | `throw std::runtime_error("Cannot use both json_schema and grammar");` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
  URL:     https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1360
  access:  "L1360 @ 704366d, opened 2026-10-23" (access cell) and "2026-10-23" (date cell)
  quote:   `throw std::runtime_error("Cannot use both json_schema and grammar");`
  used-by: corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json

$ sed -n '193p' corpus/SOURCES.md   (S181 row, verbatim)
exit 0
| S181 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1375 | code | A | the adapter validates response_format.type against text/json_object and appends the offending value to the message | L1375 @ 704366d, opened 2026-10-23 | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
  URL:     https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1375
  access:  "L1375 @ 704366d, opened 2026-10-23" (access cell) and "2026-10-23" (date cell)
  quote:   `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);`
  used-by: corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json

$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp; wc -c < same
exit 0
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  server-common.cpp
75061
→ matches SNAPSHOT.json pin for tools/server/server-common.cpp @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad.

$ sed -n '1360p' server-common.cpp          (snapshot dir llama.cpp-704366d/)
exit 0
        throw std::runtime_error("Cannot use both json_schema and grammar");

$ sed -n '1375p' server-common.cpp          (snapshot dir llama.cpp-704366d/)
exit 0
            throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);

$ sed -n '1360p' server-common.cpp | grep -cF 'throw std::runtime_error("Cannot use both json_schema and grammar");'
exit 0
1

$ sed -n '1375p' server-common.cpp | grep -cF 'throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);'
exit 0
1

$ echo 'throw std::runtime_error("Cannot use both json_schema and grammar");' | wc -w
exit 0
7

$ echo 'throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);' | wc -w
exit 0
15

$ for f in corpus/knowledge/chat-adapter-outcomes.md registry/chat-param-outcomes-r31.json; do [ -f "$f" ] && echo "EXISTS $f" || echo "MISSING $f"; done
exit 0
EXISTS corpus/knowledge/chat-adapter-outcomes.md
EXISTS registry/chat-param-outcomes-r31.json
```

FINDING: No disagreements. Both rows falsify-clean on every checked axis.
S180: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes.
S181: quote-verbatim yes; words 15; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes.
(Quote word counts by `wc -w` of the quoted string: S180 = 7, S181 = 15; both ≤ 25.)

LIMITS:
- Only S180 and S181 were opened; S182–S191 were not checked by this seat.
- Verbatim check is substring equality of the quoted text on the pinned line; it does
  not verify that the line is the *only* occurrence in the file or that the quote is
  the most salient content of that line.
- `used-by` files exist; whether those files actually reference S180/S181 or apply
  the taught behavior was not verified.
- The row's teaches claims ("surfaces as a 500 server_error", "appends the offending
  value") were not independently verified against surrounding code context.
- The snapshot tree's SNAPSHOT.json lists only 4 files while 7 are present
  (server-http.cpp, server-models.cpp, utils.hpp unpinned); the pinned file used
  here (server-common.cpp) does match its recorded sha256 and byte count.
- No tools installed or upgraded (coreutils/grep/sed sufficed; pacman paused
  host-wide per directive).

Receipts in this directory: `lines-1360-1375.txt`, `sha256-receipt.txt`, `rows-grep.txt`.
