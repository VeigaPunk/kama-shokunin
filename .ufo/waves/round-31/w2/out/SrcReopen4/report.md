# SrcReopen4 — C1 depth claim, re-open S186/S187 (falsifier)

Seat: SrcReopen4, round 31 wave 2. Reads only; no tracked file edited. Raw command
transcripts: `receipts.log` in this directory; upstream fetched copy kept at
`/tmp/kama-r31w2/SrcReopen4/upstream-server-common.cpp`.

## RESULTS

```text
$ sed -n '1517p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
exit 0
            throw std::invalid_argument("logprobs is not supported with tools + stream");

$ sed -n '1519p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
exit 0
        llama_params["n_probs"] = json_value(body, "top_logprobs", 20);

$ awk 'NR>=1515 && NR<=1522 {printf "%d|%s\n", NR, $0}' .../server-common.cpp
exit 0
1515|    if (json_value(body, "logprobs", false)) {
1516|        if (has_tools && stream) {
1517|            throw std::invalid_argument("logprobs is not supported with tools + stream");
1518|        }
1519|        llama_params["n_probs"] = json_value(body, "top_logprobs", 20);
1520|    } else if (body.contains("top_logprobs") && !body.at("top_logprobs").is_null()) {
1521|        throw std::invalid_argument("top_logprobs requires logprobs to be set to true");
1522|    }

$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
exit 0
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  .../server-common.cpp
$ wc -l .../server-common.cpp
2147 .../server-common.cpp

$ awk 'NR==198 || NR==199 {n=split($0,a,"`"); for(i=2;i<n;i+=2){printf "SOURCES.md:%d span: [%s] words=%d\n", NR, a[i], split(a[i],w," ")}}' corpus/SOURCES.md
exit 0
SOURCES.md:198 span: [throw std::invalid_argument("logprobs is not supported with tools + stream");] words=9
SOURCES.md:199 span: [llama_params["n_probs"] = json_value(body, "top_logprobs", 20);] words=5

$ curl --max-time 20 -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp -o /tmp/kama-r31w2/SrcReopen4/upstream-server-common.cpp; echo "curl-exit=$?"; sha256sum /tmp/kama-r31w2/SrcReopen4/upstream-server-common.cpp; sed -n '1517p;1519p' /tmp/kama-r31w2/SrcReopen4/upstream-server-common.cpp
curl-exit=0
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  /tmp/kama-r31w2/SrcReopen4/upstream-server-common.cpp
            throw std::invalid_argument("logprobs is not supported with tools + stream");
        llama_params["n_probs"] = json_value(body, "top_logprobs", 20);

$ printf '%s\n' 'throw std::invalid_argument("logprobs is not supported with tools + stream");' | sha256sum; sed -n '1517p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp | sed 's/^[[:space:]]*//' | sha256sum
3208e3ad13f91e018047834fda8f83547eda006f8afba31f71b58d280ea25b35  -
3208e3ad13f91e018047834fda8f83547eda006f8afba31f71b58d280ea25b35  -

$ printf '%s\n' 'llama_params["n_probs"] = json_value(body, "top_logprobs", 20);' | sha256sum; sed -n '1519p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp | sed 's/^[[:space:]]*//' | sha256sum
b4bca0d347501e7614ed551c515a26c056cac8821d3809afd6572a40ec0ac63b  -
b4bca0d347501e7614ed551c515a26c056cac8821d3809afd6572a40ec0ac63b  -

$ glob: corpus/knowledge/chat-adapter-outcomes.md -> listing contains file
$ glob: registry/chat-param-outcomes-r31.json -> listing contains file
```

Row facts (SOURCES.md, `## Registry`):
- S186 (line 198): URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1517`; anchor `L1517 @ 704366d, opened 2026-10-23`; quote `` `throw std::invalid_argument("logprobs is not supported with tools + stream");` ``; used-by `corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json`.
- S187 (line 199): URL `...server-common.cpp#L1519`; anchor `L1519 @ 704366d, opened 2026-10-23`; quote `` `llama_params["n_probs"] = json_value(body, "top_logprobs", 20);` ``; same used-by.

Resolution: SNAPSHOT.json maps `server-common.cpp` → upstream path `tools/server/server-common.cpp`, commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, fetched 2026-10-23, pinned sha256 `b4f4aae7…`. Local snapshot sha256 matches the pin; upstream GitHub raw blob at the same commit has the identical sha256 and identical lines 1517/1519 — so the pinned tree is byte-identical to the URL's file, and GitHub line numbering equals local numbering.

Line-match: sed/awk place the S186 quote on line 1517 and the S187 quote on line 1519 exactly. Quote-verbatim: byte-hash of each row quote equals the byte-hash of its line with leading whitespace trimmed (and the raw lines contain the quote plus only indentation). Words: 9 and 5, both ≤ 25.

## FINDING:
Both rows hold; no disagreement found. `S186: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes` and `S187: quote-verbatim yes; words 5; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes`.

## LIMITS:
- This only checks the two rows named by the item; it does not establish the other ten new SOURCES rows (S180-S185, S188-S191) or any C1 counter behavior, and it is not a verdict.
- "Line match" is judged against the local pinned snapshot; the upstream byte-identity cross-check (curl, exit 0) makes a discrepancy with the GitHub blob at 704366d unobserved.
- "Exists yes" means the used-by cells name existing lane files; the run does not check that those files actually consume S186/S187, nor whether the two 2026-10-23 access dates matter beyond their presence.
- Word counts use awk whitespace splitting on the backticked span; the quotes have no embedded whitespace runs beyond single spaces.
- One earlier `read` tool call's line labels were internally shifted by +2 relative to sed/awk/grep for this file; all conclusions rest on sed/awk/grep numbering, not on that read display.
