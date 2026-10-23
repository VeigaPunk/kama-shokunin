# ExecRerankOff — wave-1 findings (round 26, C1 data)

Verdict: 3 rerank faults confirmed live on the fixture (each reproduced twice on port block 47624-47627);
1 of 3 generated a countable signature under the frozen C1 predicate (X1/no-flag), and the other two
(X2/missing-query, X3/empty-documents) are blocked by the counter's clause (d) byte-match on quoted message
constants — evidence and exact mechanism below.

## Files written (all inside the lane w1-build output dir, plus scratch)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecRerankOff/candidates.json
  (3 entries, id "TBD", source.row "TBD", source.file basenames; trigger reproductions as in the schema)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecRerankOff/RUNS.txt
  (every command, output, exit code)
- raw outputs under /fast/scratch/hyaku/kama-r26/ExecRerankOff/logs/ (r1/r1b/r2/r2b/r3/r3b bodies + server
  logs, baseline responses, ls-help.txt, ls-version.txt)
- counter run/scratch extract: /fast/scratch/hyaku/kama-r26/ExecRerankOff/ (git archive of frozen
  a23c0e042114016a909eb15173aa6df74b5b7eb0; SKILL rows X1-X3, SOURCES S114-S116, registry added there
  only), receipt counter-receipt.json.

## Fault A — reranking requested without --reranking (binary: 1 candidate)
Command (each run; identical response both times):
```
timeout 90 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47624 -t 2 > r1-off.log 2>&1 &
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:47624/v1/rerank -H 'Content-Type: application/json' -d '{"query":"test","documents":["a","b"]}'
```
Output (run 1 port 47624, run 2 port 47625, identical):
```
{"error":{"code":501,"message":"This server does not support reranking. Start it with `--reranking`","type":"not_supported_error"}}
HTTP_STATUS=501
```
Signature: `This server does not support reranking. Start it with `--reranking`` (67 bytes).
Source: pinned server-context.cpp line 5803 (`res->error(format_error_response("This server does not support
reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));`), file sha256 dd1de0f2...c2329
== SOURCE_SHA256["server-context.cpp"].
Base absence: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -F -q -e '<sig>' 1560e4d8 -- SKILL.md corpus` -> rc=1 (absent).
Healthy baseline/help/version: absent from baseline-all.txt, ls-help.txt, ls-version.txt (grep -F -q rc=1 each).
Request echo: signature not present in request bytes (request body is `{"query":"test","documents":["a","b"]}`).
Frozen counter (scratch, final run): row X1 counted true (all checks true; observed status 501).

## Fault B — --reranking enabled, query missing (binary: 1 candidate)
Command (each run; identical response both times):
```
timeout 90 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47624 --reranking -t 2 > r2-noquery.log 2>&1 &
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:47624/v1/rerank -H 'Content-Type: application/json' -d '{"documents":["a","b"]}'
```
Output (run 1 port 47624, run 2 port 47625, identical):
```
{"error":{"code":400,"message":"\"query\" must be provided","type":"invalid_request_error"}}
HTTP_STATUS=400
```
Message constant: `"query" must be provided` at pinned server-context.cpp:5822.
Base absence: git grep rc=1. Baseline/help/version: absent (rc=1 each).

## Fault C — --reranking enabled, empty documents (binary: 1 candidate)
Command (each run; identical response both times):
```
timeout 90 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47626 --reranking -t 2 > r3-emptydoc.log 2>&1 &
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:47626/v1/rerank -H 'Content-Type: application/json' -d '{"query":"test","documents":[]}'
```
Output (run 1 port 47626, run 2 port 47627, identical):
```
{"error":{"code":400,"message":"\"documents\" must be a non-empty string array","type":"invalid_request_error"}}
HTTP_STATUS=400
```
Message constant: `"documents" must be a non-empty string array` at pinned server-context.cpp:5829.
Base absence: git grep rc=1. Baseline/help/version: absent (rc=1 each).

## Counter result and the clause (d) blocker for B/C
Scratch counter run:
```
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --lane /fast/scratch/hyaku/kama-r26/ExecRerankOff --repo /home/vgpnk/Projects/shokunin/kama-shokunin --out /fast/scratch/hyaku/kama-r26/ExecRerankOff/counter-receipt.json
registered 3 counted 1 target 12 met False not-counted ['X2:d_in_source', 'X3:d_in_source']
rc=0
```
Receipt: X1 counted true; X2/X3 fail only d_in_source (all other checks true), run skipped, counted false.

Mechanism (verified by byte search of the pinned file): the source stores these message constants as C++
string literals with `\"` escapes (`format_error_response("\"query\" must be provided", ...)` at
server-context.cpp:5822), while the HTTP body renders plain `"` (`"query" must be provided`). Clause (d)
requires the registered signature verbatim in pinned-source bytes; clause (e) requires it verbatim in the
registered channel bytes. No >=20-byte fragment of these quoted message constants exists in both byte
streams: `"query" must be provided` is absent from the source bytes; `query\" must be provided` (21 bytes)
exists in source but not in the HTTP body. So candidates B and C cannot satisfy the frozen predicate as
written; X1 (no quotes in the message) counts cleanly. [INFERENCE] none — the byte searches were run and
their outputs recorded in RUNS.txt section 8.

## Notes for the integrator
- candidates.json uses id "TBD" and source.row "TBD" per the schema; the L1 assigns final ids and S###
  rows. The signatures themselves are final; the scratch SOURCES rows S114-S116 (with source file
  "server-context.cpp" and commit 704366d) are placeholders to show the S### row shape and are not part of
  the lane tree.
- The generic prefix `This server does not support` was intentionally not used (A1 note: sibling family
  members/control runs already occupy it; clause (g) collision and help-text clause (f) risk).
- Final child state: no llama-server of mine remains (pgrep -af check), ports 47624-47627 closed.
- Tooling installs: none (no new tools needed; everything used existed on the host).
