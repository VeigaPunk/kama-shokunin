ATTACK E26-05 (SKILL.md:1088, registry/error-signatures-r26.json:106-130, SOURCES S118, lesson Gate S118): holds

Seat KamaR26.AttackE2605, 2026-10-23. Lane tip `git rev-parse HEAD` = f4066979096e3452ae731c0e09e50155c6d8258a.
Port block 47716-47719 (free before the runs: `ss -ltn | rg ':4771[6-9]'` exit 1). Frozen counter not run (not needed: my bodies hash byte-identical to the landed receipt).

Pins re-checked (`sha256sum`, exit 0):
- `~/.local/bin/llama-server` (symlink to `~/.local/opt/llama-b11755/llama-server`) b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804
- `~/.cache/kama-shokunin/models/stories260K.gguf` 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
- `.ufo/waves/round-26/count-c1.py` 6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588 (equals the frozen value)

## Verdict per check

| check | verdict |
|---|---|
| (1) live re-run, twice | holds |
| (2) the fault's own text, not F1, F2 or F3 | holds |
| (3) meaning (code) cell against a fresh fetch | holds |
| (4) next action cell | holds, with one low-severity gap (D1) |
| (5) SOURCES S118 and the lesson Gate quote | cells hold; the Gate quote has a rendering defect (D2, low) |

## (1) Live re-run — holds

Harness `out/AttackE2605/run.sh`. It does the same thing as `count-c1.py` `base_argv` + `run_trigger` + `http`: `llama-server -m <fixture> --host 127.0.0.1 --port P -t 2` (registry args `["-t","2"]`, model `fixture`, `occupy_port` false). It waits for `/health` 200, then sends `POST` with `Content-Type: application/json` and body `{"model": "stories260K", "input": "hello"}` (the bytes `json.dumps` produces for the registry body).

- run1, port 47716: health=200. `POST /v1/embeddings` status=501, body
  `{"error":{"code":501,"message":"This server does not support embeddings. Start it with `--embeddings`","type":"not_supported_error"}}`.
  The server exited 0 on SIGTERM and port 47716 closed.
- run2, port 47717: the same status (501) and byte-identical body. The server exited 0 and port 47717 closed.
- sha256 of both `/v1/embeddings` bodies is 168b1bb696c89efa3807113eae390c8dca4eaa6a89c11fc288b5a9324a45e915. That equals `channel_sha256` for E26-05 in `.ufo/waves/round-26/final/c1-tip-receipt.json`, where every check is true and `counted: true`.
- In the same runs, `POST /embedding` and `POST /embeddings` return the same 501 body (same sha). `POST /v1/embedding` (a route that does not exist) returns 404 `File Not Found`.

## (2) The fault's own error text, not F1, F2 or F3 — holds

- F1 (an unrelated startup line): the channel is the HTTP body, not the log. `grep -c 'does not support embeddings'` gives 0 for run1-server.log, run2-server.log and ctl-server.log. The startup logs (11 lines each) contain no warn or error line.
- F2 and F3 (echo): the registered request is `{"model":"stories260K","input":"hello"}`. It has no headers, no query string and no file argument, and no field contains any part of the signature, so there is nothing to echo, decoded or not.
- Healthy control with the same request (ctl, port 47718, `-t 2 --embeddings --pooling mean`): `/v1/embeddings`, `/embedding` and `/embeddings` all return 200 with embedding vectors, and the signature is absent. So the text appears only when the guard fires.
- Body-independence test (run3, port 47719, no `--embeddings`): a malformed body `not json{` returned 501 with the same signature, and so did an empty body without a Content-Type header. The text does not depend on request content. `/completion` on the same server returned 200 (`" upon a time,"`).
- The literal appears exactly once in the pinned source set: `grep -rn 'does not support embeddings'` over `.ufo/waves/round-26/sources/llama.cpp-704366d/` finds only `server-context.cpp:6132`. No other code path emits it.

## (3) The meaning (code) cell against a fresh fetch — holds

Fresh fetch: `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/{tools/server/server-context.cpp,tools/server/server-common.cpp,tools/server/server.cpp,common/arg.cpp}`, rc=0 for each. The sha256 of every file equals the lane snapshot:
- server-context.cpp dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329
- server-common.cpp b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442
- server.cpp 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4
- arg.cpp bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d

The cell reads: "the embeddings handler refuses before parsing when `params.embedding` is false (`server-context.cpp:6131-6133`)". Against the fetched code:
- Lines 6131-6133 are `if (!params.embedding) {`, `res->error(format_error_response("This server does not support embeddings. Start it with `--embeddings`", ERROR_TYPE_NOT_SUPPORTED));` and `return res;`. The line numbers are exact.
- "Before parsing" is correct: `json::parse(req.body)` comes later, at line 6141, after the pooling check at 6136-6139. The live malformed-body test in (2) confirms it.
- "The embeddings handler" is `handle_embeddings_impl` (line 6129). All three routes reach it: `server.cpp:297-299` maps `/embedding`, `/embeddings` and `/v1/embeddings`, and `server-context.cpp:5792-5798` defines `post_embeddings` and `post_embeddings_oai`.
- The 501 status claim (in the trigger cell): `server-common.cpp:115-117` maps `ERROR_TYPE_NOT_SUPPORTED` to `not_supported_error` with code 501, which matches the observed status and type.
- `params.embedding` is set to true by `--embedding`/`--embeddings` (also env `LLAMA_ARG_EMBEDDINGS`; `arg.cpp:3518-3522`), by `--rerank`/`--reranking` (`arg.cpp:3525-3529`) and by `--embd-gemma-default` (`arg.cpp:4637`). Without any of these the guard fires, which is what the trigger cell "no `--embeddings`" says.

## (4) The next action cell — holds; one gap

The cell reads: "This server is a generation server. Point embedding consumers at a server launched with `--embeddings` (ideally an embedding model)."
- "Generation server": the guard means embedding mode is off, and run3 shows `/completion` answering 200 on the same server. Supported.
- "Separate server, ideally an embedding model": supported by the flag's help text at `arg.cpp:3519`, "restrict to only support embedding use case; use only with dedicated embedding models". So the cell is right not to say "add `--embeddings` to this server". [INFERENCE] On this build the restriction is not enforced for the fixture: ctl2 (`--embeddings --pooling mean`) still served `/completion` with 200. That does not contradict the advice.

D1 (low; the advice is incomplete, not wrong): if you follow the cell literally on the fixture, it leads straight into E26-06. ctl3 (port 47719, `-t 2 --embeddings`, default pooling) answered `POST /v1/embeddings` with 400 `Pooling type 'none' is not OAI compatible. Please use a different pooling type`. The row's own trigger route is `/v1/embeddings`. SKILL.md:1108-1109 also records a SIGSEGV with `--embeddings` and no pooling override. "Ideally an embedding model" covers real embedding models, which carry pooling metadata, but the row does not warn about pooling.
Smallest correction (SKILL.md:1088, next action cell): change "launched with `--embeddings` (ideally an embedding model)" to "launched with `--embeddings` (ideally an embedding model; on a model whose pooling is `none`, also pass `--pooling mean`, see E26-06)".

## (5) SOURCES S118 and the lesson Gate quote — cells hold; one rendering defect

`corpus/SOURCES.md:130`, cells in header order (`corpus/SOURCES.md:11`):
- source/URL `.../blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6132`: the commit is full, the path is correct, and `#L6132` is the signature line. Holds.
- kind `code`, tier `A`: holds.
- scope "the E26-05 error emitted at server-context.cpp line 6132 and its guard, at commit 704366d76 only; not other builds": holds.
- anchor `sha256 dd1de0f2...c2329`: equals the fresh fetch and the snapshot. Holds.
- teaches: the same sentence as the SKILL meaning cell, verified in (3). Holds.
- status `mined`, opened 2026-10-23, recheck `on-release`, used-by "SKILL.md, registry/error-signatures-r26.json": consistent with the lesson Gate, which says S114-S130 are new `mined` rows. Holds.
- `.ufo/waves/round-26/final/census-validate.out:34` flags S118 with W04 "duplicate url ... across scopes". That is a lane-wide warning (49 W04 lines, including S060, S109, S114-S125 and S133 on the same file); the file ends `ok`, exit=0. It is not specific to S118 and not a defect of this row.

Lesson Gate, `corpus/lessons/round-26.md:31`: the URL equals the SOURCES URL, the access date is 2026-10-23, and the raw quote bytes equal source line 6132 with leading whitespace dropped (11 whitespace-separated tokens, within 25 words). The raw bytes hold.

D2 (low; rendering): the quote is wrapped in single backticks, and the source text contains backticks, so the code span closes early. `cmark` (`/usr/bin/cmark`) renders it as
`<code>res-&gt;error(format_error_response(&quot;This server does not support embeddings. Start it with </code>--embeddings<code>&quot;, ERROR_TYPE_NOT_SUPPORTED));</code>`.
The rendered quote loses the two backticks around `--embeddings`, so it is not verbatim when rendered. The SKILL.md:1088 cell uses double-backtick delimiters and renders correctly (`markdown-it` output: `<code>This server does not support embeddings. Start it with `--embeddings`</code>`).
Smallest correction (round-26.md:31): delimit with double backticks and padding spaces, i.e. ``` line 6132: `` res->error(format_error_response("This server does not support embeddings. Start it with `--embeddings`", ERROR_TYPE_NOT_SUPPORTED)); `` ```. [INFERENCE] The same pattern affects the S114 (line 27), S115 (28), S117 (30) and S121 (34) Gate quotes; I did not render those.

## Residual risk and verification gaps

- Observed on build b11755 and the fixture only, as the SKILL section already states.
- My stop helper failed in the second batch (`kill: invalid usage`, an empty pid argument), so run3, ctl2 and ctl3 ran one at a time on port 47719 and were stopped by explicit `kill -TERM <pid>` (1474781 via `pkill -f`, then 1606921, then 1665632). At most one of my children ran at a time. The script's own log (job completed, 108.57 s wall time) shows `server exit=0` and `port 47719 closed` after each of run3, ctl2 and ctl3, and ends `pgrep=1`. Final state: `pgrep -af 'llama-server.*--port 4771[6-9]'` exit 1, `ss -ltn | grep ':4771[6-9]'` exit 1, and `pgrep -af llama-server` exit 1 (no llama-server on the host).
- The ctl server (port 47718) exited 1 with "Received second interrupt, terminating immediately." after one SIGTERM sent through `timeout`. [INFERENCE] This is an artifact of my harness's signal path, not part of the row.
- run3 files include curl's ` status=501` suffix (`-w` piped through `tee`), so their sha256 (af52b61c...) differs from the run1/run2 bodies. The message bytes are the same.

## Installs

None persistent. `uvx --from markdown-it-py` (markdown-it-py 4.2.0, uv channel, ephemeral cache environment) was used once to render the SKILL cell. `cmark` was already installed.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2605.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/AttackE2605/`: `run.sh`; run1 and run2 `-_v1_embeddings.out`, `-_embedding.out`, `-_embeddings.out`, `-_v1_embedding.out` and `-server.log`; ctl `-_v1_embeddings.out`, `-_embedding.out`, `-_embeddings.out`, `-_v1_embedding.out` and `-server.log`; `run3-malformed.out`, `run3-empty.out`, `run3-server.log`; `ctl2-completion.out`, `ctl2-server.log`; `ctl3-v1.out`, `ctl3-server.log`
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2605/` (the same files plus `fetch/` with the four fetched sources and `skillcell.md`)
