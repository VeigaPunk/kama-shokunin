/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item SrcOpen2 — source rows S185..S189 (tier A, code) for C1
Claim served: C1 (depth). Every counted row needs a new S### row that names the pinned file, the
line (`L<n>`) and commit 704366d, and whose quote is verbatim from that line (≤25 words).

Scope: the adapter's logprobs/top_logprobs mapping and the remaining-properties copy loop. Pinned snapshots (already fetched, sha256-pinned in SNAPSHOT.json):
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/sources/llama.cpp-704366d/ — files: server-common.cpp.
Open each line with `sed -n '<n>p' <file>` and read its neighbourhood; the upstream URL form is
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/<file>#L<n>
(access date 2026-10-23; do not re-fetch unless you need to prove the pin — if you do, sha256sum and
compare with SNAPSHOT.json and say so).

Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/SrcOpen2/sources.md` with one table row per id in the exact
10-column format of corpus/SOURCES.md:
| S### | <source name — URL> | code | A | <scope, one clause> | L<n> @ 704366d, opened 2026-10-23 | "<verbatim quote ≤25 words>" | mined | 2026-10-23 | on-release | registry/chat-param-outcomes-r31.json |
Every row must be checked by you: the quote must occur verbatim on that line of that file, and the
line number must be right (`grep -n -F '<quote fragment>' file` gives the line). Record the check
command and its output in `checks.txt`. Do not invent a line; a wrong line voids the data row that
cites it.
