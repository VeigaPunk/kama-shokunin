ATTACK E26-10: partial

Target: SKILL.md:1093 row E26-10 / registry `error-signatures-r26.json` signatures[9] / SOURCES S123 / lesson round-26.md:36, at landed tip f4066979096e3452ae731c0e09e50155c6d8258a.
Seat: KamaR26.AttackE2610. Port block 47736-47739 (checked free first: `ss -ltn | grep -E '4773[6-9]'` -> no lines, exit 1). No tools installed or updated. All servers `-t 2`, wrapped in `timeout`, one child at a time, all killed with ports re-checked closed.

Pins re-verified before any claim:
- `sha256sum ~/.local/bin/llama-server` -> `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (matches fixture pin).
- `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` -> `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches).
- `llama-server --version` -> `version: 0.7.0-dev (build 11755, commit 704366d76)`, exit 0.
- Fresh fetch `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` (curl, exit 0, 6320 lines) -> sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, byte-equal to the lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp` and to the S123 anchor cell.
- Fresh `server-http.cpp` -> `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` (matches the counter's expected pin). Fresh `server-common.cpp`, `llama-context.cpp` also fetched at 704366d.

## (1) Live replay of the registered trigger — HOLDS

Registry entry: channel `http`, args `-c 64 --embedding -t 2`, model `fixture`, `occupy_port: false`, `POST /embedding` body `{"content": "<6750-char 'The quick brown fox...' string>"}` (1350 words). Replayed with a script (`/fast/scratch/hyaku/kama-r26w2/AttackE2610/replay.py`) that builds argv exactly as the counter does (`llama-server -m <model> --host 127.0.0.1 --port P` + args) and sends `json.dumps(body)` with `Content-Type: application/json`.

Run 1 (port 47736), `timeout 240 python3 replay.py 47736 run1`, shell exit 0:
```
ARGV: .../llama-server -m .../stories260K.gguf --host 127.0.0.1 --port 47736 -c 64 --embedding -t 2
READY: True rc: None
REQUEST_BYTES: 6765 sha256: 536254e85d2968dc1415636de146b8f0e1e7a75494d9ce4dc7460948f225cea7
STATUS: 500
BODY: {"error":{"code":500,"message":"input (4352 tokens) is too large to process. increase the physical batch size (current batch size: 64)","type":"server_error"}}
SIG_IN_BODY: True
SIG_IN_REQUEST_BYTES: False
PORT_CLOSED: True
SIG_IN_LOG: True
```
Run 2 (port 47737), exit 0: identical status `500`, byte-identical body, same request sha256, `SIG_IN_BODY: True`, `PORT_CLOSED: True`.
So: the row's "4352-token `content` -> 500" is exactly reproduced, twice, on the pinned binary/model. The token count 4352 is stable and matches the row text.

## (2) Is it the fault's own error? — HOLDS (no F1/F2/F3)

- Source of the text: `server-context.cpp:3657` inside `send_error(slot, string_format(...), ERROR_TYPE_SERVER)` at 3655-3660. The signature is a substring of that message only; `grep -c 'is too large to process' server-context.cpp` -> 1 occurrence.
- It reaches the HTTP body as `error.message` and the log as `E srv send_error: task id = 0, error: ...` at `0.00.252.454`, i.e. after `listening on http://127.0.0.1:47736` and only in response to the request. An `awk` scan of `run1.log` up to the `listening` line found no occurrence: it is not a startup warning on an unrelated failure (F1 clear).
- `SIG_IN_REQUEST_BYTES: False` on the raw JSON (F2 clear: nothing in the 6765 request bytes, no unicode-escape path). Request `headers` is `{}`, there is no query string, and args are only CLI flags (`-c 64 --embedding -t 2`) with no argument-file contents (F3 clear).
- `llama-server --help` (exit 0, 60469 bytes) and `--version` (exit 0, 90 bytes): `grep -c 'is too large to process'` -> 0 in both (clause-f family clear).
- At base `git grep -F -q -e 'is too large to process. increase the physical batch ' 1560e4d8 -- SKILL.md corpus` -> exit 1 (clause b clear).
- Registry overlap: no other of the 17 signatures is a substring/superstring of this one (script check over all 17 ids) (clause g family clear).

## (3) Pinned source line and `meaning (code)` cell — PARTIAL (guard and status right; citation and one generalisation wrong)

Guard, from the fresh fetch, exact numbering:
```
3653:                        if (!slot.can_split()) {
3654:                            if (slot.task->n_tokens() > n_ubatch) {
3655-3659:                      send_error(slot, string_format("input (%d tokens) is too large to process. increase the physical batch "
3657-3658:                        "size (current batch size: %d)", slot.task->n_tokens(), n_ubatch),
3660:                                          ERROR_TYPE_SERVER);
3661-3662:                      slot.release(); return;
```
`n_ubatch` is `int32_t n_ubatch = llama_n_ubatch(ctx_tgt);` (server-context.cpp:3574), i.e. the context's effective ubatch, not the CLI value. Status: `ERROR_TYPE_SERVER` maps to code 500 and type `server_error` at `server-common.cpp:107-110`; the adjacent `ERROR_TYPE_EXCEED_CONTEXT_SIZE` maps to 400 (`server-common.cpp:123-125`). Observed 500, so "Status 500, not 400" is correct and code-backed.

Defect 3a (evidence scope). The row cites `server-context.cpp:3652-3658`. Line 3652 is blank, and the cited range stops at 3658 — it excludes `ERROR_TYPE_SERVER` at 3660, which is the only reason the status is 500 rather than 400. The "500, not 400" sentence is therefore asserted outside its own citation. Smallest correction: cite `server-context.cpp:3653-3660` (guard 3653-3654, message 3657-3658, type 3660) in both the SKILL cell and the S123 `teaches` cell.
Defect 3b (generalisation). "embedding inputs cannot be split across batches" is categorical but the code is conditional: `can_split()` (server-context.cpp:447-474) returns true for pooling `LAST` (463-465) and for causal RANK poolings (467-469); it returns false for embeddings only in the remaining cases. On this fixture it returned false (observed), consistent with a non-LAST pooling, but the cell would mislead a reader whose embedding model is pooling-LAST. Smallest correction: "embedding inputs with pooling other than LAST cannot be split across batches (`can_split()`, server-context.cpp:447-474, false at 474)".

## (4) `next action` cell — BREAKS on this fixture

Cell: "Raise `-ub`/`-b` to cover the longest input, or chunk the input on the client. Do not read the 500 as a crashed server."

Three live variants, same request, ports inside my block:
- A, `-c 64 --embedding -t 2 -ub 4096` (port 47738, `timeout 240`, exit 0): status still **500**, body **unchanged**, `"current batch size: 64"`. Raising `-ub` alone on the row's own `-c 64` invocation changes nothing.
- B, `-c 8192 -b 8192 -ub 8192` (port 47739, exit 0): status **400**, `{"error":{"code":400,"message":"input (4352 tokens) is larger than the max context size (2048 tokens). skipping",...}}`, `SIG_IN_BODY: False`. It falls through to the next guard with a different signature.
- C, `-c 8192 -np 1 -b 8192 -ub 8192` (port 47736, exit 0): status **400**, same 2048-token context-size message; log `n_slots = 1, n_ctx_slot = 2048`.
- D, `-c 18432 -b 18432 -ub 18432` (port 47737, exit 0): status **400**, same 2048-token message; log `n_slots = 4, n_ctx_slot = 2048` and `the slot context (18432) exceeds the training context of the model (2048) - capping`.

Code: causal attention clamps the batch to the context (`llama-context.cpp:332-334`: `cparams.n_batch = min(n_ctx, params.n_batch); cparams.n_ubatch = min(cparams.n_batch, n_ubatch or n_batch)`), and the server's slot context is capped at the model's trained context (`server-context.cpp:4655-4662`, `return std::min(res, llama_model_n_ctx_train(model_tgt))`). With `stories260K` (n_ctx_train 2048) a 4352-token input cannot fit any slot or any batch, so the `-ub`/`-b` branch of the advice is unreachable on this fixture; only chunking (or a model whose trained context covers the input) works. The claim is also incomplete even in the general case: `-ub`/`-b` are clamped to `-c`, so a reader must raise `-c` as well.
The third sentence is correct: `HEALTH_AFTER: 200` after every 500/400 in runs A-D — the process does not crash.
Smallest correction: "Chunk the input on the client. On this fixture the slot context is capped at the model's trained context of 2048 tokens (`n_ctx_slot()`, server-context.cpp:4655-4662), so a 4352-token input cannot fit; on a model whose context covers the input, raise `-c` together with `-ub`/`-b`, because causal attention clamps both to `n_ctx` (llama-context.cpp:332-334). Do not read the 500 as a crashed server."

## (5) SOURCES S123 and the lesson Gate quote — HOLDS (with the 3a/3b wording carried over)

S123 cells checked one by one (corpus/SOURCES.md:135): id `S123`; source `llama.cpp server-context.cpp @ 704366d (b11755)` with URL `...#L3657` (fresh-fetch line 3657 is the message line, verified); kind `code`; tier `A` (matches code rows S042/S109/S126); scope "the E26-10 error emitted at server-context.cpp line 3657 and its guard, at commit 704366d76 only; not other builds" (accurate); anchor "server-context.cpp line 3657 @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; sha256 dd1de0f2...c2329" (fresh fetch equal); teaches (mirrors the row, so it inherits defects 3a/3b in its line-range and categorical wording); status `mined`, opened `2026-10-23` (matches access date), recheck `on-release`, used-by `SKILL.md, registry/error-signatures-r26.json` (both true).
Row is new: `git show 1560e4d8:corpus/SOURCES.md | grep -c '^| S123 |'` -> 0; S114-S130 likewise 0 at base.
Lesson Gate quote (corpus/lessons/round-26.md:36): URL, access date 2026-10-23 and the quote `line 3657: "input (%d tokens) is too large to process. increase the physical batch "` — byte-verbatim against line 3657, 11 words (<=25 per the Gate's rule), and the Gate's claim that fetched bytes equal the lane snapshot is true (sha256 above).

## Traceability observation (not a defect for E26-10)

The tip receipt `.ufo/waves/round-26/final/c1-tip.out` records `tree=7e5ff9b5...`; the landed commit f4066979 has tree `6e6fb5f5...`. `git log --all` shows 7e5ff9b5 is the tree of commit f2a981ee. `git diff --stat 7e5ff9b5 f4066979 -- SKILL.md corpus/SOURCES.md registry/error-signatures-r26.json corpus/lessons/round-26.md` -> empty (exit 0); the whole diff is `.ufo/waves/round-26/**`, `LOG.md`. The counted C1 artifacts are byte-identical at the landed tip, so the counted E26-10 row is the landed row. The receipt's tree label is stale relative to the tip, nothing more.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2610.md` (this report)
- `/fast/scratch/hyaku/kama-r26w2/AttackE2610/`: `replay.py`, `variant.py`, `props.py`, `replay logs run1.log run2.log A.log B.log C.log D.log props.log`, `help.txt`, `ver.txt`, and fresh fetches `server-context.cpp`, `server-http.cpp`, `server-common.cpp`, `llama-context.cpp`.

Cleanup: every server child was killed via process group with `teardown` and its port re-probed closed (`PORT_CLOSED: True` in every run); `ss -ltn | grep -E '4773[6-9]'` -> no lines (exit 1); the only `llama-server` left on the host is `--port 47562` and `--port 47719`, both outside my block and not mine. No lane file, git/jj state, fleet repo, operator config, `~/.local/bin`, `~/.local/opt` or `~/.cache/kama-shokunin` was modified.
