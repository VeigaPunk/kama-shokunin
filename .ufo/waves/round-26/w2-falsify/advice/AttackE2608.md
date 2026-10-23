ATTACK E26-08 / S121 (the `--reranking` 501): partial

Seat: KamaR26.AttackE2608 (wave 2 FALSIFY, round 26). Port block 47728-47731; runs on 47728, 47729, 47730, 47731.
Landed tip f4066979 (receipt tree 7e5ff9b5454dd27f0520cb36a3cbc3a995e48162).
Pins re-checked: `sha256sum ~/.local/bin/llama-server` = b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804;
model = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d; `--version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`.
Port block free before the first launch (`ss -ltn | grep -E '4772[89]|4773[01]'` rc=1).
Row under attack: SKILL.md:1091 (section heading SKILL.md:1062); registry entry registry/error-signatures-r26.json:184-213.

The row is a genuine, live, source-pinned, base-absent error from one emitter. One cell (next action, check 4)
overstates what the code requires. No counted status changes.

## (1) Live re-run of the registered trigger: holds

Registry fields (184-213): channel http, args `["-t","2"]`, model `fixture`, `POST /v1/rerank`,
`Content-Type: application/json`, body `{"query": "test", "documents": ["a", "b"]}`. I launched it the way the counter
does (`count-c1.py` base_argv adds `-m <fixture> --host 127.0.0.1 --port P`).

- Run 1, port 47728, `out/AttackE2608/run1.sh 47728 r1`:
  body `{"error":{"code":501,"message":"This server does not support reranking. Start it with \`--reranking\`","type":"not_supported_error"}}`,
  `HTTP_STATUS=501`, curl rc 0, signature lines in startup log 0 (`grep -c` rc=1), server killed, port closed.
- Run 2, port 47729, same command: identical 501 body, curl rc 0, killed, port closed. (Its `run-r2.log` came out 0 bytes —
  the redirect lost the child's startup lines at SIGTERM. The HTTP body is the evidence for that run; run 3 covers the log.)
- Run 3, port 47730, same flags with a full log (`out/AttackE2608/run3-noflag.log`, 990 bytes): `listening on http://127.0.0.1:47730`,
  no reranking line, POST → identical 501, `PORT_47730_CLOSED`.

The 501 matches `ERROR_TYPE_NOT_SUPPORTED → code = 501` (server-common.cpp:115-117 in the pinned snapshot).
The counter's own E26-08 row (`.ufo/waves/round-26/final/c1-tip-receipt.json`) records all checks true, status 501, and the
same body excerpt; I did not re-run the frozen counter (it belongs to the Rerun seat and the host lock).

## (2) Fault's own text, warning and echo limits (F1/F2/F3): holds

- F1: the text is an `res->error(...)` response, not a log warning. The whole tree at 704366d has exactly one occurrence:
  `grep -rn "does not support reranking" llama.cpp-704366d.../ | wc -l` → 1, `tools/server/server-context.cpp:5803`.
  The startup logs of runs 1 and 3 contain 0 occurrences (`grep -c -F` → 0, rc=1).
- F2: the guard at 5803 runs before `const json body = json::parse(req.body)` at 5807, and the message is a C++ literal;
  no request field can reach it. Control run (`out/AttackE2608/echoctl.sh`, port 47728): body
  `{"query":"This server does not support reranking. Start it with \`--reranking\`","documents":["a"]}` → same 501;
  query string `?msg=This%20server%20does%20not%20support%20reranking.` → same 501; no echo path, log 0 occurrences.
- F3: the registered args name no file (`["-t","2"]`); no template/api-key/model-url argument, so file contents cannot enter.

## (3) Pinned source and the 'meaning (code)' cell: holds (one citation nit)

Fresh fetch (access 2026-10-23):
`curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`
→ sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, equal to the lane snapshot and to
`SOURCE_SHA256["server-context.cpp"]` in the counter. I also pulled the full tree (`codeload.github.com/.../tar.gz/704366d76...`):
its `tools/server/server-context.cpp` has the same sha256, and it is the only file in the tree containing the signature.

Pinned snapshot server-context.cpp:5800-5805:
```
5800    this->post_rerank = [this](const server_http_req & req) {
5801        auto res = create_response();
5802        if (!params.embedding || params.pooling_type != LLAMA_POOLING_TYPE_RANK) {
5803            res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));
5804            return res;
5805        }
```
Row cell: “rerank needs embedding mode and rank pooling; it refuses otherwise (`server-context.cpp:5800-5805`)”. The guard
condition is exactly `!params.embedding || params.pooling_type != LLAMA_POOLING_TYPE_RANK`, the message is at 5803, and the
observation is 501. `--reranking` sets both (`arg.cpp:3525-3530`), and routes are always registered (`server.cpp:300-303`,
one authority: all four rerank routes map to `routes.post_rerank`).

Nit, not a defect: the range starts at the lambda open (5800) and ends at the closing brace (5805); the guard block itself is
5802-5805 (analogous row E26-04 cites 5452-5454, the guard only). If the lane wants uniform ranges, cite `5802-5805`.
No correction is required.

## (4) 'next action' cell: partial — model requirement is overreach

Cell (SKILL.md:1091): “Reranking needs a reranker model launched with `--reranking`; a generation server cannot serve it.”

What the code and the observation support: the route is gated by two launch parameters only
(`!params.embedding || pooling != RANK`, 5802). No model-capability check exists anywhere in the handler.

Counterexample (live, same binary, same fixture model, same request):
- Run 4, port 47731, `out/AttackE2608/run3.sh 47731 rerankflag --reranking` → `HTTP_STATUS=200`,
  body `{"model":".../stories260K.gguf","object":"list","usage":{"prompt_tokens":10,"total_tokens":10},"results":[{"index":1,"relevance_score":1.4062021970748901},{"index":0,"relevance_score":-0.9240114688873291}]}`.
- Run 5, port 47730, `--embeddings --pooling rank` (no `--reranking`) → identical 200 with the same scores.
Both servers were stopped by the harness and logged `cleaning up before exit...`; ports closed; the signature never appeared
in their logs. After the guard the handler parses the body and queues `SERVER_TASK_TYPE_RERANK` tasks (5833-5877) with no
model-capability check, which is why the fixture model returns scores.

So the generation model in the fixture answers `/v1/rerank` with scores once the launch mode is right; obtaining a reranker
model is not what clears the 501, and `--reranking` is not the only flag combination that does. The cell's second clause is
only true under the lane's own sense of “generation server” (server without embedding mode, cf. E26-05); read as
“generation model” it is false. An operator following the cell would look for a different model while relaunching the same
one with the flag already clears the error.

Smallest safe correction (replace the next-action cell):
> Reranking is gated by launch mode only: `--reranking` (embedding mode + rank pooling; `--embeddings --pooling rank` is equivalent) makes this fixture generation model answer 200 with scores. Choose a trained reranker for meaningful scores, not to clear the 501.

If the lane prefers to keep “generation server”, append “(a server without embedding mode)” to that clause. One cell edit
in SKILL.md:1091; no registry, SOURCES, counter or predicate change.

## (5) SOURCES row S121 and the lesson Gate quote: holds

corpus/SOURCES.md:133 (header at :11: id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by):
- source URL `.../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5803`: correct commit, path and
  line (5803 is the `res->error` line in the fresh fetch).
- anchor `server-context.cpp line 5803 @ 704366d...; sha256 dd1de0f2...c2329`: file sha256 matches the fresh fetch and the snapshot.
- scope “at commit 704366d76 only; not other builds” is a correct limitation; teaches repeats the meaning cell.
- status `mined`, opened 2026-10-23, recheck `on-release` (same vocabulary as S001/S121's neighbours), used-by `SKILL.md,
  registry/error-signatures-r26.json`: both name S121 (SKILL.md:1091; registry `source.row` "S121", file "server-context.cpp").
- New at base: `git show 1560e4d8:corpus/SOURCES.md | grep S121` rc=1; the signature is absent from base
  (`git grep -F -q -e '<sig>' 1560e4d8 -- SKILL.md corpus` rc=1); not in `--help`/`--version` (grep rc=1 each).
- `sources-census` at the tip flags S121 only as `W04 duplicate url ... server-context.cpp across scopes` (advisory, census exit=0),
  the same warning carried by every sibling row that cites this file.

corpus/lessons/round-26.md:34 Gate quote: `line 5803: res->error(format_error_response("This server does not support reranking. Start it with \`--reranking\`", ERROR_TYPE_NOT_SUPPORTED));`
— the source line byte for byte (minus leading indentation), under 25 words, URL and access date 2026-10-23 matching the row.
Cosmetic only: the nested backticks around `--reranking` break the Markdown code span in the Gate table; the text itself is right.

## Defects

D1 (partial, check 4) — E26-08 next-action cell asserts a model requirement the code does not have and the live run refutes:
the fixture generation model with `--reranking` (or `--embeddings --pooling rank`) returns HTTP 200 with scores. Correction:
the replacement cell in (4). Scope: SKILL.md:1091 only. Does not affect the counted status (next action is outside the predicate).

Nits, no correction required: the 5800-5805 range vs the guard block 5802-5805 (3); the Gate quote's nested backticks (5).

## Impacted axes

- Depth: one of the 17 counted rows carries an overreaching next action; the count (17 ≥ 12) and every predicate clause are unaffected.
- Calibration: the operator-facing advice for the rerank 501 is slightly wrong about what must change; the fixed text keeps the row useful.
- Not affected: identity/provenance (S121 pins and emitter are correct), adjacency, error-signature coverage.

Judge-facing caveat, not a defect under the frozen predicate: five counted rows are the same mechanism — a launch
flag/parameter left unset → `501 not_supported_error` from a handler-entry guard: E26-01 (5365-5367), E26-02 (5407-5409),
E26-04 (5452-5454), E26-05 (6131-6133), E26-08 (5802-5805). Each has a distinct literal, endpoint, flag and trigger, so clause
(g) passes and the count stands; but the section's 17 rows cover fewer than 17 distinct mechanisms [INFERENCE from the row text].

## Residual risk / verification gaps

- I did not run the frozen counter (RerunC1AtTip's job under the host lock); I read its tip receipt row for E26-08 instead.
- Only b11755/704366d was tested; the row itself limits its scope to that commit, so other builds are out of scope here.
- The single-emitter search covered the full tree tarball at the pinned commit, not other revisions or local rebuilds.

## Process hygiene

One llama-server child at a time on 127.0.0.1:47728-47731, each wrapped in `timeout 120`, `-t 2`, killed after its requests,
and port closure confirmed after every launch. Final `ss -ltn | grep -E ':(47728|47729|47730|47731) '` rc=1 and
`pgrep -af "llama-server.*--port 477(28|29|30|31)"` rc=1. Other llama-server processes on the host (ports 47720, 47734, 47740, ...)
belong to other seats and were not touched. No commits, no jj, no installs or updates.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/AttackE2608.md (this report)
- .ufo/waves/round-26/w2-falsify/out/AttackE2608/{RUNS.txt, run1.sh, run3.sh, run-r1.log, run3-noflag.log,
  run3-rerankflag.log, run3-embrank.log, body-r1.txt, body-r2.txt, body3-noflag.txt, body3-rerankflag.txt, body3-embrank.txt}
- Scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2608/ (the same files plus echoctl.sh, echoctl.log, server-context.fresh.cpp,
  and the extracted llama.cpp-704366d76 tarball).

Report: .ufo/waves/round-26/w2-falsify/advice/AttackE2608.md
