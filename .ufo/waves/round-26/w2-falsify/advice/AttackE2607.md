ATTACK E26-07 / S120 (`\"input\" or \"content\" must be provided`): holds

Seat: KamaR26.AttackE2607 (wave 2 FALSIFY, round 26). Port block 47724-47727; only 47724 used.
Pins checked: `sha256sum ~/.local/bin/llama-server` = b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804;
model = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d; `llama-server --version` →
`version: 0.7.0-dev (build 11755, commit 704366d76)`. Port block free before start (`ss -ltn | grep -E ':4772[4-7] '` rc=1).

## (1) Live re-run of the registered trigger: holds

Registry entry (registry/error-signatures-r26.json:156-182): channel http, args
`--embeddings --pooling mean -t 2`, model fixture, `POST /v1/embeddings` body `{"model": "stories260K"}`.
I ran it as the counter does (adding `-m <fixture> --host 127.0.0.1 --port 47724`), with the same body bytes the counter sends
(`json.dumps` → `{"model": "stories260K"}`, `Content-Type: application/json`). Script: `out/AttackE2607/run.sh`.

- Run 1 (`run.sh trig1 47724 --embeddings --pooling mean -t 2`): `HTTP/1.1 400 Bad Request`, body
  `{"error":{"code":400,"message":"\"input\" or \"content\" must be provided","type":"invalid_request_error"}}`, curl rc 0, server_exit=0 (after my kill), port_closed 47724.
- Run 2 (same command): identical status and body, Content-Length 107, curl rc 0, port_closed 47724.

The 400 matches `ERROR_TYPE_INVALID_REQUEST` → `code = 400` (server-common.cpp:95-97 in the pinned snapshot).

## (2) Fault's own text, not a warning (F1) and not echoed from the request (F2/F3): holds

- Channel is http response body, so F1 (a warning line on an unrelated startup failure) cannot apply. The response body holds
  only this one error object. The server log of both runs (`trig1.server.log`, `trig2.server.log`) has only startup warnings
  (`embeddings enabled with n_batch (2048) > n_ubatch (512)`, `embeddings required but some input tokens were not marked as outputs`);
  the signature does not appear there.
- Request bytes are `{"model": "stories260K"}`: no `input`, no `content`, no backslash, no unicode escape, no query string,
  no custom header, and no argument file (`args` has no `@file` or file-valued flag). F2/F3 cannot apply.
- The text is not echoed even when the client puts it elsewhere: `POST /v1/embeddings?input=x` with the same body gives the same
  107-byte body (query string ignored; `ctrl.out`).
- Single emitter: `rg -n -F '\"input\" or \"content\" must be provided' tools common` in the fresh fetch → only
  `tools/server/server-context.cpp:6151` (rc 0). Same result in the 13 pinned snapshot files.
- Guard isolation controls (`ctrl.out`, `nopool.out`, server `--embeddings --pooling mean -t 2` unless noted):
  - `{"model":"stories260K","input":"hello"}` → 200 OpenAI list; `{"model":"stories260K","content":"hello"}` → 200 native array shape.
  - `{}`, `[]`, `{"inputs":"hello"}`, `{"prompt":"hello"}`, `POST /embedding {}`, `POST /embeddings {...}` → 400 with the signature.
  - `{"input": null}` → 400 with a different error (`"prompt" elements must be a string, ...`): the guard tests key presence (`body.count("input")`), not value.
  - Empty body → 400 `[json.exception.parse_error.101] ...` (the earlier `json::parse` at 6141, not this guard).
  - Without `--pooling mean` (`--embeddings -t 2`): `/v1/embeddings` → 400 `Pooling type 'none' is not OAI compatible...` (E26-06's guard at 6136 runs first);
    `/embedding` → 400 with the E26-07 signature. So `--pooling mean` is needed on the OpenAI route, as the row's trigger says.

## (3) Pinned source and the 'meaning (code)' cell: holds

Fresh fetch in `/fast/scratch/hyaku/kama-r26w2/AttackE2607/llama` (`git fetch --depth 1 --filter=blob:none origin 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`,
`git rev-parse FETCH_HEAD` → 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; accessed 2026-10-23).
`sha256sum tools/server/server-context.cpp` → dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329, equal to the lane
snapshot and to count-c1.py `SOURCE_SHA256["server-context.cpp"]`.

server-context.cpp:6145-6152 (fresh fetch):
```
    if (body.count("input") != 0) {
        prompt = body.at("input");
    } else if (body.contains("content")) {
        res_type = TASK_RESPONSE_TYPE_NONE; // "content" field is not OAI compatible
        prompt = body.at("content");
    } else {
        res->error(format_error_response("\"input\" or \"content\" must be provided", ERROR_TYPE_INVALID_REQUEST));
        return res;
```
Row cell (SKILL.md:1090): "the handler accepts `input` (OpenAI) or `content` (native) and refuses when both are absent
(`server-context.cpp:6145-6152`)". The range covers exactly the if / else-if / else and the `return`. `content` switches the
response to the native shape (comment at 6148; seen live as a 200 array). Status 400 matches the observation. Callers: 5793
(`/embedding`, NONE) and 5797 (`/v1/embeddings`, OAI_EMBD) both reach this handler.

## (4) 'next action' cell: holds

"Client bug: the request body lacks the text field. Fix the client to send `input`." Supported: the guard only fires when the
body has no top-level `input`/`content` key. `input` works on both routes (checked first), and on `/v1/embeddings` it is the only key
that keeps the OpenAI response shape (`content` returned the native array). The 400 means the server is up and in embedding
mode, so the action rightly does not suggest relaunching. Live cases `{"prompt":...}`, `{"inputs":...}` and a top-level `[]`
all hit this guard, which fits "lacks the text field".

Nit, not a defect (optional): a client that sends a batch as a top-level JSON array (`[]` → same 400) also lacks the field. The cell
could add "(e.g. `prompt`, `inputs`, or a top-level array instead of `{"input": [...]}`)". No correction is required.

## (5) SOURCES row S120 and lesson Gate quote: holds

corpus/SOURCES.md:132 (header at :11: id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by):
- source URL `.../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6151`: correct commit, path, and line (6151 = the `res->error` line).
- anchor `server-context.cpp line 6151 @ 704366d...; sha256 dd1de0f2...c2329`: matches the fresh fetch.
- teaches: same claim as the SKILL.md meaning cell, with range 6145-6152; checked in (3). Scope limited to commit 704366d76.
- used-by `SKILL.md, registry/error-signatures-r26.json`: both name S120 (SKILL.md:1090; registry `source.row` "S120", file `server-context.cpp`).
corpus/lessons/round-26.md:33 Gate quote: `line 6151: res->error(format_error_response("\"input\" or \"content\" must be provided", ERROR_TYPE_INVALID_REQUEST));`.
That is the source line byte for byte and under 25 words. URL and access date (2026-10-23) match.

The section preamble (SKILL.md:1068-1069) says `\"` in http-body signatures is the JSON escape the server sends, byte for byte as in the C++ literal.
So a reader will not mistake the backslashes for a decoded message.

## Defects

None found in scope. No correction is required.

## Residual risk / verification gaps

- I did not run the frozen counter. Per the contract it runs only in a scratch `git archive` extract under the host lock, and that is the RerunC1AtTip seat's job.
  E26-07's predicate clauses (b), (f) and (g) (base absence, healthy baseline, one fault per row) were not re-derived here; I rely on
  `.ufo/waves/round-26/final/c1-tip.out` (`registered 17 counted 17 target 12 met True not-counted []`).
- The fresh fetch checked out only `tools/server` and `common`. The single-emitter search covers those trees, not the whole repo [INFERENCE: no other component builds into llama-server's HTTP error path for this route].

## Process hygiene

One llama-server child at a time on 127.0.0.1:47724, each wrapped in `timeout 120`, `-t 2`, killed after its requests, and
`port_closed 47724` was confirmed after each of the 4 launches. Final `pgrep -af llama-server | rg '4772[4-7]'` rc=1 and
`ss -ltn | rg ':4772[4-7] '` rc=1. The other llama-server processes I saw (ports 47734, 47740) belong to other seats.
No installs or updates.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/AttackE2607.md (this report)
- .ufo/waves/round-26/w2-falsify/out/AttackE2607/{run.sh, trig1.out, trig2.out, ctrl.out, nopool.out, trig1.server.log, trig2.server.log}
- Scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2607/ (same files plus *.reqs, ctrl/nopool server logs, and the `llama/` fresh-fetch clone)
