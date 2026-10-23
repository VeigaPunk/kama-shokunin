# SrcReopen6 — re-open S190 and S191 (SOURCES.md @ llama.cpp 704366d pin)

Seat: `KamaR31.SrcReopen6` — falsifier, leaf. Scope: rows S190 and S191 only.
Measured at worktree HEAD `bda324b` ("round-31 attempt 2: C3 freeze …"), one commit
past the dispatch tip `382d11b`; `corpus/SOURCES.md` itself is unchanged between the
two (last touched by `382d11b`) and `git status --porcelain` on it is empty.

```
RESULTS
$ grep -n "^## " corpus/SOURCES.md
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
exit 0

$ sed -n "202p;203p" corpus/SOURCES.md
| S190 | llama.cpp b11755 server-schema.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L47 | code | A | the schema declares max_tokens as an alias of n_predict, so the chat body's max_tokens lands in both stored keys | L47 @ 704366d, opened 2026-10-23 | `->add_alias("max_tokens")` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
| S191 | llama.cpp b11755 server-schema.cpp — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L64 | code | A | the schema declares n as the OpenAI fallback alias of n_cmpl, the multiple-choice count | L64 @ 704366d, opened 2026-10-23 | `->add_alias("n") // alias "n" as fallback (OpenAI completions API)` | mined | 2026-10-23 | on-release | corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json |
exit 0
(rows are at file lines 202–203, inside the ## Registry section that runs lines 9–204)

$ cat .ufo/waves/round-31/sources/SNAPSHOT.json
{
 "schema": "kama-source-snapshot/v1",
 "commit": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad",
 "repo": "https://github.com/ggml-org/llama.cpp",
 "fetched": "2026-10-23",
 "files": {
  "server-common.cpp": {"path": "tools/server/server-common.cpp", "sha256": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442", "bytes": 75061},
  "server-schema.cpp": {"path": "tools/server/server-schema.cpp", "sha256": "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050", "bytes": 29572},
  "server-task.cpp":   {"path": "tools/server/server-task.cpp",   "sha256": "4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495", "bytes": 67241},
  "server-chat.cpp":   {"path": "tools/server/server-chat.cpp",   "sha256": "91f48e09afc5a345033866380e82db1c3ad4d18baf1cec38ffa6cddaf6a6263e", "bytes": 30649}
 }
}
exit 0

$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050  .ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
exit 0
(matches the SNAPSHOT.json pin for tools/server/server-schema.cpp @ 704366d)

$ sed -n "47p" .ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
        ->add_alias("max_tokens")
exit 0

$ sed -n "64p" .ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
        ->add_alias("n") // alias "n" as fallback (OpenAI completions API)
exit 0

$ sed -n "38,70p" .ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
        ->set_desc("Include prompt processing progress events in stream mode"));

    add((new field_num("sse_ping_interval", params.sse_ping_interval))
        ->set_hard_limits(-1, INT32_MAX)
        ->set_desc("Interval in seconds between SSE comment pings emitted while the stream stays silent, -1 disables pings"));

    add((new field_num("n_predict", params.n_predict))
        ->set_hard_limits(-1, INT32_MAX)
        ->add_alias("max_completion_tokens")
        ->add_alias("max_tokens")
        ->set_desc("Set the maximum number of tokens to predict. When 0, no tokens will be generated but the prompt is evaluated into the cache"));

    add((new field_num("n_indent", params.n_indent))
        ->set_hard_limits(0, INT32_MAX)
        ->set_desc("Specify the minimum line indentation for the generated text in number of whitespace characters. Useful for code completion tasks"));

    add((new field_num("n_keep", params.n_keep))
        ->set_hard_limits(-1, INT32_MAX)
        ->set_desc("Specify the number of tokens from the initial prompt to retain when context size is exceeded. Use -1 to retain all tokens from the prompt"));

    add((new field_num("n_discard", params.n_discard))
        ->set_hard_limits(0, INT32_MAX)
        ->set_desc("Number of tokens after n_keep that may be discarded when shifting context (0 = half context)"));

    add((new field_num("n_cmpl", params.n_cmpl))
        ->set_hard_limits(1, params_base.n_parallel)
        ->add_alias("n") // alias "n" as fallback (OpenAI completions API)
        ->set_desc("Number of completions to generate. If the input has multiple prompts, total outputs will be N prompts times n_cmpl"));

    add((new field_num("n_cache_reuse", params.n_cache_reuse))
        ->set_hard_limits(0, INT32_MAX)
        ->set_desc("Min chunk size to attempt reusing from the cache via KV shifting. See --cache-reuse arg"));

exit 0
(L47 alias chains off field_num("n_predict"); L64 alias chains off field_num("n_cmpl")
with hard limit 1..params_base.n_parallel — both match the rows' scope cells)

$ echo '->add_alias("max_tokens")' | wc -w
1
exit 0

$ echo '->add_alias("n") // alias "n" as fallback (OpenAI completions API)' | wc -w
9
exit 0

$ ls -la corpus/knowledge/chat-adapter-outcomes.md registry/chat-param-outcomes-r31.json
-rw-r--r-- 1 vgpnk vgpnk 4367 Oct 23 18:03 corpus/knowledge/chat-adapter-outcomes.md
-rw-r--r-- 1 vgpnk vgpnk 7450 Oct 23 18:03 registry/chat-param-outcomes-r31.json
exit 0

$ grep -n "S19[01]" corpus/knowledge/chat-adapter-outcomes.md registry/chat-param-outcomes-r31.json
corpus/knowledge/chat-adapter-outcomes.md:3:source: S180-S191 (llama.cpp b11755 `tools/server/server-common.cpp` and `server-schema.cpp` @ 704366d76, opened 2026-10-23)
registry/chat-param-outcomes-r31.json:30:    "row": "S190",
registry/chat-param-outcomes-r31.json:325:    "row": "S191",
exit 0
(used-by files exist and cite the rows back — citation check is bonus, spec asked existence only)

$ sed -n "440,447p" corpus/SOURCES.md
## Round-31 rows relocated into the registry (repair, 2026-10-23)

S180–S191 were first appended at end of file, after the last `##` section, so
`scripts/sources-census.sh validate` read them as E12 `row outside Registry section` (12 findings,
exit 1). They now sit in the `## Registry` table above with ids and cells unchanged; this pointer
records the move (append-only: no cell was rewritten). Defect and fix recorded in
`corpus/lessons/round-31.md` §Mistakes row 4.
exit 0

$ git log --oneline -2; git status --porcelain corpus/SOURCES.md; echo clean-if-empty
bda324b round-31 attempt 2: C3 freeze (instrument-registry coverage), C3 before receipt, wave-2 spec/plan/taskCall, round-start census
382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts
clean-if-empty
exit 0
```

FINDING: no disagreement found on either row. Per the required one-line format:
`S190: quote-verbatim yes; words 1; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md,registry/chat-param-outcomes-r31.json exists yes`
`S191: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md,registry/chat-param-outcomes-r31.json exists yes`
Both quotes occur verbatim as substrings of the pinned lines (leading indent is part of the
line, not the quote); both are <= 25 words; both URLs resolve to the SNAPSHOT-pinned file at
the pinned commit (sha256 matches); both rows sit inside `## Registry`; both scope claims
(max_tokens→n_predict, n→n_cmpl) match the enclosing `add((new field_num(...)))` chains.

LIMITS:
- Only lines L47/L64 and their enclosing field blocks were read; no other line of the pinned
  file was checked. The other ten rows S180–S189 are out of scope.
- Verbatim match is a substring check; a quote that coincidentally matches an unrelated
  substring would not be caught. Here the line content and the schema context agree with the
  rows' scope cells, but I did not verify that `max_tokens` actually "lands in both stored
  keys" at request time — that requires reading request-parsing code (server-chat.cpp), which
  the spec did not ask for and this seat did not exercise.
- used-by existence was verified by `ls`; contents of those files were only spot-grepped
  (they cite S190/S191 back) — whether the citations are semantically correct was not judged.
- I did not re-fetch the URL from GitHub; verification is against the local pinned snapshot
  only, matching the counter's own reference tree. Upstream drift since fetch 2026-10-23 is
  not observable from here.
- No verdict is implied: these rows surviving falsification does not admit C1.
- Tooling: no installs or upgrades performed; none needed (coreutils sed/grep/wc, git, sha256sum).
