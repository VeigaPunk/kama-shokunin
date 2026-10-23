# Source and predicate gate

## Verdict

Source bytes and line evidence pass for the four requested files. Ten row drafts have source literals at least 20 bytes and are absent from the archived base `SKILL.md`/`corpus` search. No live trigger, healthy baseline, help/version, request-echo, or counter result was run; those C1 gates remain unverified.

## Fresh fetch and byte pins

Fetched from `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/<file>` on 2026-10-23. Command used for the four required files:

```sh
mkdir -p /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest && commit=704366d76f8748cf9ad3df62a464bfcc8d1ae6ad && for f in server-common.cpp server-task.cpp server-http.cpp server-models.cpp; do curl --fail --location --silent --show-error "https://raw.githubusercontent.com/ggml-org/llama.cpp/$commit/tools/server/$f" --output "/fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/$f" || exit; done && sha256sum /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/*.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-common.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-task.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-http.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-models.cpp
```

Observed `sha256sum` output; each fresh file and lane snapshot pair is identical:

```text
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/server-common.cpp
24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb  /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/server-http.cpp
9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a  /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/server-models.cpp
4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495  /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/server-task.cpp
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-common.cpp
4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-task.cpp
24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-http.cpp
9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-models.cpp
```

The output contained the four expected pairwise matches. The Bash tool did not print a process exit code. The hashes equal the frozen map at `.ufo/waves/round-26/count-c1.py:66–72` for `server-common.cpp`, `server-http.cpp`, `server-models.cpp`, and `server-task.cpp`.

I also fetched fresh `server.cpp` only to resolve router-mode reachability. Its SHA-256 was `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` both in scratch and the lane snapshot. The fresh copy has the router predicate at lines 151–154 and registers `/models` only inside `if (is_router_server)` at lines 231–276. `count-c1.py:225–226` always supplies `-m <model>`, so the model-name HTTP errors in `server-models.cpp` are not candidates for the frozen single-model run.

## Gate quotes for drafted rows

Each quote is from the fresh file opened on 2026-10-23, contains at most 25 whitespace-delimited words, and is pinned at the exact full commit URL.

| Draft row | URL with line anchor | Located quote |
|---|---|---|
| S140 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp#L295 | `authentication_error` |
| S141 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1143 | `"prompt" is required` |
| S142 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1114 | `"prompt" elements must be a string, a list of tokens, a JSON object` |
| S143 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1129 | `"prompt" must not be empty` |
| S144 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1155 | `Only no echo is supported` |
| S145 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1100 | `Multimodal data provided, but model does not support multimodal requests.` |
| S146 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1395 | `All non-assistant messages must contain 'content'` |
| S147 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1390 | `Expected 'messages' to be an array` |
| S148 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1259 | `image input is not supported - hint: if this is unexpected` |
| S149 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1411 | `Expected 'content' to be a string or an array` |

## `grep -n` line proof

To follow the tool policy, the line-number proof below came from the specialized `functions.grep` search on the freshly fetched files (its output is line-numbered; no shell `grep` was run). The matching source lines were:

```text
server-http.cpp:295: {"type", "authentication_error"},
server-common.cpp:1100: throw std::runtime_error("Multimodal data provided, but model does not support multimodal requests.");
server-common.cpp:1114: throw std::invalid_argument("\\"prompt\\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.");
server-common.cpp:1129: throw std::invalid_argument("\\"prompt\\" must not be empty");
server-common.cpp:1143: throw std::runtime_error("\\"prompt\\" is required");
server-common.cpp:1155: throw std::runtime_error("Only no echo is supported");
server-common.cpp:1259: throw std::runtime_error("image input is not supported - hint: if this is unexpected, you may need to provide the mmproj");
server-common.cpp:1390: throw std::invalid_argument("Expected 'messages' to be an array");
server-common.cpp:1395: throw std::invalid_argument("All non-assistant messages must contain 'content'");
server-common.cpp:1411: throw std::invalid_argument("Expected 'content' to be a string or an array");
```

The planned strings are 20, 20, 132, 26, 25, 73, 49, 34, 94, and 45 UTF-8 bytes respectively for S140–S149; all meet `MIN_BYTES = 20` at `.ufo/waves/round-26/count-c1.py:52`.

## Base absence sweep

Extracted the frozen base only into scratch:

```sh
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 1560e4d83f42b04f40336357de6f9637eafa0f4b SKILL.md corpus | tar -x -C /fast/scratch/hyaku/kama-r26/ScribeSourcesRequest/base && printf 'archive_exit=0\n'
```

Observed output: `archive_exit=0`.

The required `functions.grep` sweep searched the extracted `SKILL.md` and `corpus/` for these row needles; each returned exactly `No matches found`:

```text
authentication_error
"prompt" is required
prompt.*elements must be a string
prompt.*must not be empty
Only no echo is supported
Multimodal data provided, but model does not support multimodal requests
All non-assistant messages must contain
Expected 'messages' to be an array
image input is not supported
Expected 'content' to be a string or an array
```

The search tool does not expose a shell exit status. The archived tree contains only the base paths requested by clause (b); this is an absence search, not a live execution result.

## Unverified C1 gates

No server was launched and no registered trigger was sent. Consequently none of these are claimed: HTTP status/body reproduction, startup capture, request-echo absence, healthy-baseline absence, `--help`/`--version` absence under A1, pairwise trigger distinction against earlier counted rows, insertion of the new rows into the measured `corpus/SOURCES.md`, or a frozen counter result. The source pin and source-literal checks above are only the source portion of C1.
