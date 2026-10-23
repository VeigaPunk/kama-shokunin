# ExecPromptTooLong — advice report (C1 candidate signature rows)

Verdict: 2 candidate registry rows confirmed live (scratch frozen-counter run: registered 2, counted 2, all 11 checks true per row); both are HTTP-channel signatures tied to the pinned `server-context.cpp` at 704366d.

## Fault family served
"Prompt exceeds slot context; generation past context with --no-context-shift" (port block 47648-47651).

## Candidate signatures (candidates.json)

| row | id | signature (verbatim) | source file:line | observed trigger → status |
|---|---|---|---|---|
| 1 | TBD-1 | `exceeds the available context size (` | server-context.cpp:3678-3679 (format `"request (%d tokens) exceeds the available context size (%d tokens), try increasing it"`) | POST /completion, args `-c 64`, prompt 4352 tok → 400 |
| 2 | TBD-2 | `is too large to process. increase the physical batch ` | server-context.cpp:3657 (literal `"input (%d tokens) is too large to process. increase the physical batch "`) | POST /embedding, args `-c 64 --embedding`, prompt 4352 tok → 500 |

Both signatures: >= 20 bytes (36 / 53), verbatim in the pinned source bytes (server-context.cpp sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` matches the frozen counter's `SOURCE_SHA256`), absent at base 1560e4d8 (`git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` → exit 1 for both), absent from healthy baseline bodies/logs and from `llama-server --help`/`--version` output, absent from the request bytes, and not substrings of each other.

## Live reproductions (every launch on my port block, one child at a time, `-t 2`, `timeout 90`, SIGTERM + port-closed confirmed)

- Run 1 (47648, default shift, long prompt) → **400**; body: `{"error":{"code":400,"message":"request (4352 tokens) exceeds the available context size (2048 tokens), try increasing it","type":"exceed_context_size_error",...}}` (repro #1).
- Run 1b (47648, `-c 64`, long prompt) → **400**; body: `...exceeds the available context size (256 tokens), try increasing it...` (repro #2, exact final trigger).
- Run 2 (47649, `-c 64 --no-context-shift`, long prompt) → **400**, identical message (same signature; not a distinct row).
- Run 3 (47650, `-c 64 --embedding`, prompt 1017 tok) → **500**; body: `{"error":{"code":500,"message":"input (1017 tokens) is too large to process. increase the physical batch size (current batch size: 64)","type":"server_error"}}` (repro #1).
- Run 4 (47651, `-c 64 --embedding --ubatch-size 2048`, prompt 4352 tok) → **500**; body: `...input (4352 tokens) is too large to process. increase the physical batch size (current batch size: 64)...` (repro #2; `--ubatch-size` does not lift the displayed 64 limit).
- Healthy baseline: `-c 64` short /completion → 200; `-c 64 --no-context-shift` short prompt `n_predict:512` → 200 (stop=limit, truncated).

Raw bodies, status files, server logs, healthy runs, and prompt payload are in `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/`; every command + exit code is in `RUNS.txt`.

## Honest negative finding (second assigned sub-fault)
Generation running past the context with `--no-context-shift` is **not** an HTTP error on b11755: `process_token()` truncates and reports `STOP_TYPE_LIMIT` at server-context.cpp:2026-2034, returning 200. The `"context shift is disabled"` 500 branch (server-context.cpp:3378) is unreachable in the single-request flow (source comment at 3376-3377 says it is redundant; `process_token` stops first). So no countable signature exists for that sub-fault; the second countable row is instead the /embedding oversized-prompt error (cannot-split path, server-context.cpp:3653-3664), which is the other live error this family produces on the fixture.

## Scratch counter check (frozen counter)
Prepared a scratch extract of the frozen tip `a23c0e042114016a909eb15173aa6df74b5b7eb0` (`git archive`) at `/fast/scratch/hyaku/kama-r26/kama-extract` with placeholder SKILL rows (`## Round-26 live error signatures`, rows `| TBD-1 |...|` / `| TBD-2 |...|`), SOURCES rows `S901`/`S902`, and `registry/error-signatures-r26.json`; `--repo` pointed at a scratch full clone (`/fast/scratch/hyaku/kama-r26/kama-clone`, checked out at the frozen tip).

Command:
```
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 \
  .ufo/waves/round-26/count-c1.py \
  --lane /fast/scratch/hyaku/kama-r26/kama-extract \
  --repo /fast/scratch/hyaku/kama-r26/kama-clone \
  --out /fast/scratch/hyaku/kama-r26/ExecPromptTooLong/counter-receipt.json
```
Output: `registered 2 counted 2 target 12 met False not-counted []` (exit 0). Per-row checks all true: `id_unique, a_skill_row, b_long, b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown, e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct`. Observed channels: TBD-1 status 400 (excerpt matches run 1b), TBD-2 status 500 (excerpt matches run 4). Receipt copied to `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/counter-receipt-scratch.json`.

## Sources
Both quotes located in the lane-pinned commit snapshot (sha256 compared to the frozen counter's `SOURCE_SHA256`); access date 2026-10-23.
- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3678 — quote (3678-3679): "request (%d tokens) exceeds the available context size (%d tokens), try increasing it" (12 words).
- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3657 — quote (3657-3658): "input (%d tokens) is too large to process. increase the physical batch size (current batch size: %d)" (20 words).

## Files written
- `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/candidates.json`
- `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/counter-receipt-scratch.json`
- `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/` raw outputs: `resp-body-47648/47649/47650/47651.txt`, `resp-status-47648/47649/47650/47651.txt`, `server-47648/47649/47650/47651.log`, `healthy1/2-body.txt`, `healthy1/2-status.txt`, `healthy-server-47648/47649.log`, `prompt_long.txt`, `req-47648/47649/47650/47651.json`
- this advice report

## Risks / blockers
- TBD-1 trigger reports `n_ctx 256` (per-slot share of the `-c 64` unified KV pool over 4 slots), not 64; that is expected and does not affect the signature.
- TBD-2 is the physical-batch variant of the family (embeddings cannot split; `can_split()` false), not the `"larger than the max context size"` branch (server-context.cpp:3669), which is unreachable when `-c 64` also clamps the physical batch to 64.
- The 500 `"context shift is disabled"` and `"Context size has been exceeded."` paths could not be reproduced as HTTP errors; they are dead in the single-request flow.
- No blockers. No tools installed this session.
