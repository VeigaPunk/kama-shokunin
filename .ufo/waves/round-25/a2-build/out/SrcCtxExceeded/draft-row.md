# Draft SOURCES registry row — SrcCtxExceeded (round 25, attempt 2, C2 sourced claim)

Status: queued until the L1 cites it. id deliberately left as the placeholder `S1xx`
(the next free id at draft time is S106; the L1 assigns the final id).

11-column format matches `corpus/SOURCES.md` header (line 11):
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`

Draft row (single table row):

```
| S1xx | llama.cpp server KV-cache-full decode handling @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | how a single-model b11755 server reacts when decoding fails because the KV cache is full: batch-halving retries, then the `Context size has been exceeded` error sent to all processing slots; not the load/fit path, not the HTTP status/body rendering | `decode` lines 4294-4341 (error string 4298-4301; halving 4334-4337; send_error + release + prompt_clear 4318-4327; throw 4330); caller retry/abort 3331-3356; try_clear_idle_slots 1810-1835; raw file sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | On decode failure ret == 1 with n_batch > 1, the server halves n_batch (unless try_clear_idle_slots purges an idle slot) and retries; once n_batch == 1 still fails, every processing slot is sent `Context size has been exceeded.`, its context is cleared (prompt_clear), and update_slots aborts via throw, abort_all_slots and break. | queued | 2026-10-22 | on-release | — |
```

Notes for the L1:
- Existing rows on the same file do NOT cover this scope: S042 (health route body) and S060 (per-slot served context metadata). A new row is needed.
- The row is a draft only; nothing in `corpus/SOURCES.md` was edited.
