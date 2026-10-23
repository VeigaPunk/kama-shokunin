# SrcReopen5 — re-open rows S188 and S189 (C1 depth falsification)

Scope: verify that corpus/SOURCES.md rows S188 and S189 pin verbatim, ≤25-word
quotes to the llama.cpp 704366d snapshot at
`.ufo/waves/round-31/sources/llama.cpp-704366d/` and that each `used-by` cell
names something that exists. Advisory evidence only; nothing fixed.

```RESULTS
$ grep -n 'S188\|S189' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
200:| S188 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1521 | code | A | top_logprobs alone is refused; it is only read when logprobs is true | L1521 @ 704366d, opened 2026-10-23 | `throw std::invalid_argument("top_logprobs requires logprobs to be set to true");` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
201:| S189 | llama.cpp b11755 server-common.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1530 | code | A | every remaining request key is copied into the task parameters before the schema keeps only what it declares, the path by which undeclared OpenAI-standard keys reach the server and are pruned | L1530 @ 704366d, opened 2026-10-23 | `llama_params[item.key()] = item.value();` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |

$ grep -n '^##' corpus/SOURCES.md | bracketing lines 200-201
exit=0
9:## Registry          <- rows 200-201 sit inside ## Registry
205:## Paths           <- next header after the rows

$ cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/sources/SNAPSHOT.json
exit=0
{ "schema": "kama-source-snapshot/v1",
  "commit": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad",
  "repo": "https://github.com/ggml-org/llama.cpp",
  "fetched": "2026-10-23",
  "files": { "server-common.cpp": { "path": "tools/server/server-common.cpp",
      "sha256": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442",
      "bytes": 75061 }, ... } }

$ sed -n '1521p' $SNAP/server-common.cpp
exit=0
        throw std::invalid_argument("top_logprobs requires logprobs to be set to true");

$ sed -n '1530p' $SNAP/server-common.cpp
exit=0
            llama_params[item.key()] = item.value();

$ sed -n '1515,1535p' $SNAP/server-common.cpp   (context)
exit=0
    if (json_value(body, "logprobs", false)) {
        if (has_tools && stream) {
            throw std::invalid_argument("logprobs is not supported with tools + stream");
        }
        llama_params["n_probs"] = json_value(body, "top_logprobs", 20);
    } else if (body.contains("top_logprobs") && !body.at("top_logprobs").is_null()) {
        throw std::invalid_argument("top_logprobs requires logprobs to be set to true");
    }

    // Copy remaining properties to llama_params
    // This allows user to use llama.cpp-specific params like "mirostat", ... via OAI endpoint.
    // See "launch_slot_with_task()" for a complete list of params supported by llama.cpp
    for (const auto & item : body.items()) {
        // Exception: if "n_predict" is present, we overwrite the value specified earlier by "max_tokens"
        if (!llama_params.contains(item.key()) || item.key() == "n_predict") {
            llama_params[item.key()] = item.value();
        }
    }
    ...

$ sha256sum $SNAP/server-common.cpp
exit=0
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  .../llama.cpp-704366d/server-common.cpp
(matches SNAPSHOT.json pin)

$ substring check: quote S188 in L1521; quote S189 in L1530
exit=0
S188 verbatim-substring: YES
S189 verbatim-substring: YES
S188 words: 9
S189 words: 3

$ grep -nF 'llama_params[item.key()] = item.value();' $SNAP/server-common.cpp
exit=0
1170:            llama_params[item.key()] = item.value();
1530:            llama_params[item.key()] = item.value();   <- pinned line matches; the statement is not unique in the file

$ test -e used-by paths (from lane root)
exit=0
EXISTS corpus/knowledge/chat-adapter-outcomes.md
EXISTS registry/chat-param-outcomes-r31.json
```

Disagreement lines (required format):

- `S188: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md + registry/chat-param-outcomes-r31.json exists yes`
- `S189: quote-verbatim yes; words 3; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md + registry/chat-param-outcomes-r31.json exists yes`

No disagreements found on either row.

FINDING: S188 and S189 both survive falsification — each quote occurs verbatim
on its pinned snapshot line (verified against the sha256-pinned
server-common.cpp at commit 704366d), is well under 25 words, sits inside the
`## Registry` section (line 9; rows at 200-201), and its `used-by` cell names
two repo paths that exist. No defect found on these two rows.

LIMITS: I checked only S188 and S189 of the S180-S191 block; the other ten rows
are unexamined by this seat. For S189 the quoted statement also appears at line
1170 of the same file, so the quote is not unique to the pinned line — the
pinned line is still correct. I verified `used-by` paths exist but did not open
them to confirm they actually cite or use these sources. Verbatim was tested as
a substring match on the pinned line (leading whitespace differs by
indentation, which is expected); the quote text itself matches character-for-
character. Tool installs: none needed (grep/sed/sha256sum only). Advisory
evidence for the L1, not a verdict.

Receipts in this directory: `verbatim-check.txt`, `evidence.txt`,
`table-header.txt`.
