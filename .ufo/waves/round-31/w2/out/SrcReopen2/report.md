# SrcReopen2 — re-open SOURCES.md rows S182 and S183 (round-31 wave-2 falsifier)

Seat: `KamaR31.SrcReopen2` (reviewer, leaf). Scope: rows **S182** and **S183** of
`corpus/SOURCES.md` against the pinned snapshot
`.ufo/waves/round-31/sources/llama.cpp-704366d/` (commit
`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, `SNAPSHOT.json` pins). Nothing fixed;
falsification only. No tools installed (coreutils + grep sufficed; pacman paused
host-wide, nothing needed).

## RESULTS

```
$ grep -n '^## ' corpus/SOURCES.md        # row placement check
9:## Registry            <- rows live here (table header L11)
205:## Paths             <- next section; S182/S183 at L194-195 are inside Registry
exit 0

$ sed -n '194,195p' corpus/SOURCES.md     # the two rows, verbatim
| S182 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1390 | code | A | the chat body's messages field must be a JSON array; any other type is refused before inference | L1390 @ 704366d, opened 2026-10-23 | `throw std::invalid_argument("Expected 'messages' to be an array");` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
| S183 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1395 | code | A | every non-assistant message must carry content; a user message without it is refused | L1395 @ 704366d, opened 2026-10-23 | `throw std::invalid_argument("All non-assistant messages must contain 'content'");` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
exit 0

$ sed -n '1390p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
        throw std::invalid_argument("Expected 'messages' to be an array");
exit 0

$ sed -n '1395p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
            throw std::invalid_argument("All non-assistant messages must contain 'content'");
exit 0

$ sed -n '1390p' server-common.cpp | grep -cF 'throw std::invalid_argument("Expected '"'"'messages'"'"' to be an array");'
1          # verbatim quote occurs on the pinned line (exit 0)

$ sed -n '1395p' server-common.cpp | grep -cF 'throw std::invalid_argument("All non-assistant messages must contain '"'"'content'"'"'");'
1          # verbatim quote occurs on the pinned line (exit 0)

$ printf '%s' '<S182 quote>' | wc -w ; printf '%s' '<S183 quote>' | wc -w
7
7          # both <= 25 words

$ sed -n '1385,1400p' server-common.cpp    # context: throws are real guards
    if (!body.contains("messages")) { throw ... "'messages' is required" }
    json & messages = body.at("messages");
    if (!messages.is_array()) {              # <- L1390 throw inside this guard
        throw std::invalid_argument("Expected 'messages' to be an array");
    }
    for (auto & msg : messages) {
        ... if (role != "assistant" && !msg.contains("content")) {
            throw std::invalid_argument("All non-assistant messages must contain 'content'");   # L1395
exit 0

$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442
  == SNAPSHOT.json pin for tools/server/server-common.cpp (match)
exit 0

$ ls -la corpus/knowledge/chat-adapter-outcomes.md registry/chat-param-outcomes-r31.json
-rw-r--r-- 1 vgpnk vgpnk 4367 Oct 23 18:03 corpus/knowledge/chat-adapter-outcomes.md
-rw-r--r-- 1 vgpnk vgpnk 7450 Oct 23 18:03 registry/chat-param-outcomes-r31.json
exit 0   # both used-by targets exist

$ grep -n 'S182\|S183' registry/chat-param-outcomes-r31.json SKILL.md corpus/knowledge/chat-adapter-outcomes.md
registry/chat-param-outcomes-r31.json:119:    "row": "S182"   (K31-06, contains "Expected 'messages' to be an array", line 1390)
registry/chat-param-outcomes-r31.json:140:    "row": "S183"   (K31-07, contains "All non-assistant messages must contain 'content'", line 1395)
SKILL.md:1252:  K31-06 row ending "| S182 |"
SKILL.md:1253:  K31-07 row ending "| S183 |"
corpus/knowledge/chat-adapter-outcomes.md: no literal 'S182'/'S183'; cites the range
  'source: S180-S191' and the same lines as 'server-common.cpp:1390' / ':1395'
exit 0
```

Raw receipts saved beside this report:
`receipt-line-checks.txt` (sed lines, verbatim greps, word counts, context),
`receipt-cells-and-usedby.txt` (row cells, used-by targets, sha256 vs pin).

Note on the URL→file resolution: the row URL points at
`tools/server/server-common.cpp#L1390`; the snapshot tree flattens files to
basenames under `llama.cpp-704366d/` and `SNAPSHOT.json` maps
`server-common.cpp → tools/server/server-common.cpp`. First attempt at
`llama.cpp-704366d/tools/server/server-common.cpp` failed `No such file`
(exit 2, expected — receipt in `/tmp/kama-r31w2/SrcReopen2/`); resolution via
the SNAPSHOT.json mapping is the correct read and it succeeded.

## FINDING:

`S182: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md+registry/chat-param-outcomes-r31.json exists yes`
`S183: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md+registry/chat-param-outcomes-r31.json exists yes`

No disagreement found on either row: both rows sit inside `## Registry`,
both quotes occur verbatim on the exact pinned lines of the sha256-matching
snapshot file (b4f4aae7…d442 == SNAPSHOT.json), each quote is 7 words (≤25),
and every `used-by` target exists and names the rows (registry keys
`"row": "S182"/"S183"`; SKILL.md K31-06/K31-07; the knowledge file cites the
S180-S191 range plus `:1390`/`:1395`).

## LIMITS:

- Checks only S182 and S183; the other ten rows (S180-S191 minus these) are
  out of scope for this seat.
- Verbatim = the quoted text appears on the pinned line; it does not prove
  the quote is the *only* place that string occurs in the file, nor that
  llama-server b11755 (the live fixture) contains the same line — the snapshot
  pins commit 704366d, and I did not diff the fixture build's source.
- Line match is against the flattened snapshot copy authenticated by
  SNAPSHOT.json sha256, not against a fresh fetch of the raw URL; the URL
  itself was not re-fetched (falsification is against the pin the counter uses).
- `used-by` existence = the two named paths exist and cite the row/range; I did
  not verify that every statement in those files supported by S182/S183 is
  true, nor that the registry's live `outcome` measurements (400 rejects)
  actually occurred — those are other seats' items.
- `words` counted as whitespace-separated tokens (7 each); any reasonable
  counting convention stays ≤25.
