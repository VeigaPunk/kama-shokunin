# ReopenS113: falsify SOURCES row S113 and its Gate line

**Verdict: defect found (minor, wording only).** The anchor hash, the Gate quote, the cited line numbers, and the entry's use of S113 all hold. Two phrases need a fix. The teaches cell says "per layer" where the code skips some layers. The anchor's "constructor lines 65-98" label is narrower than the constructor, which runs to line 389.

## Inputs and scope

- Row: `corpus/SOURCES.md:125`. Gate line: `corpus/lessons/round-25.md:29`. Gate paragraph: `:13-18`. Entry: `corpus/knowledge/context-capacity.md`.
- Committed tip `fa3b62ae6475d111eb466d79af616aeebb08bbb9`. The S113 row and the Gate line are byte-identical in the committed and working copies. The lesson file as a whole differs (F5).
- Fresh fetch: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp`, accessed 2026-10-22 (10:06:55Z). curl exit 0. 98638 bytes, 2962 lines.
- Blob URL as cited in the row: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp`
- No llama-server was started. No subagent was used. No tool was installed or updated.

## Checks (30 rows in `out/ReopenS113/checks.md`)

**Anchor hash: holds.** `sha256sum` of the fetch is `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`. The anchor cell at `SOURCES.md:125` has the same value (exact match). Two more identities agree: `git hash-object` gives `b7dfadef4638f6221608f48aff0a1f83df281063` (exit 0), and the GitHub contents API at ref 704366d76 gives the same blob sha with size 98638 (exit 0). The seat report committed at fa3b62ae, `a2-build/advice/SrcKvCacheSize.md`, records the same sha (grep count 1).

**Release name: holds.** The GitHub tag API for `refs/tags/b11755` points to commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (exit 0).

**Cited line numbers: hold.** Each was checked in the fetched file:
- `:84` `n_seq_max(n_seq_max), n_stream(unified ? 1 : n_seq_max), ...`
- `:135` `GGML_ASSERT(n_stream == 1 || n_stream == n_seq_max);`
- `:142-145` `v_cells.resize(n_stream);`, then a loop over `n_stream`, and `:144` `v_cells[s].resize(kv_size);`
- `:233-234` K and V `ggml_new_tensor_3d(..., kv_size, n_stream)`. The per-stream view calls are at `:243-244` (loop header `:242`, closing brace `:245`), so the cited 233-244 covers the calls.
- `:92-97` the `if (other)` block: `:93` size_other, `:94` compare, `:95` warning, `:96` `kv_size = size_other;`
- `:301-304` the size log format and its arguments (kv_size, layers, n_seq_max, n_stream)
- `:1221-1225` `get_size()`; `:1231-1233` `get_n_stream()`

**Gate quote: holds.** `round-25.md:29` quotes `size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs), K (%s): %7.2f MiB, V (%s): %7.2f MiB`. This is a verbatim substring of `llama-kv-cache.cpp:301` (python equality: True). It has 18 words, under the 25-word limit. The range "lines 301-304" is correct. The Gate URL equals the row URL.

**Teaches cell, claim by claim:**
- (a) Stream count, `:84`: holds. Notation only (F3).
- (b) Every stream holds kv_size cells, `:144`: holds.
- (c) Tensors are (embd, kv_size, n_stream), so the total is kv_size × n_stream "per layer", `:233-234`: the shape holds. "per layer" overstates (F1).
- (d) The log prints kv_size as "cells" and n_seq_max/n_stream as "%2u/%u seqs", `:301-304`: holds.
- (e) A shared source cache overrides kv_size, `:93-97`: holds in source. No cell exercises it.

**Product rule on live data: holds (committed receipt).** I parsed all 14 cells in `final/context-capacity-receipt.json`. Every size line obeys the stream rule (unified gives n_stream 1; split gives n_stream = n_seq_max), and the pool equals kv_size × n_stream. Example: X1's fit probe is 512 × 4 = 2048, and its serving context is 2048 × 4 = 8192. Receipt line 35 (unified, 2048 cells, K 0.62 MiB) and receipt line 820 (split, 2048 cells, K 2.50 MiB) show that four streams give four times the K bytes. All 14 cells report 5 layers.

**Entry use: holds.**
- `context-capacity.md:65-67` uses S113 for the stream rule and for per-stream cells. It cites lines 84, 144 and 301-304. Each is in the row's teaches, and the receipt matches each.
- The header at `:1` lists S113 with the right file.
- The entry does not use S113 for the n_ctx to kv_size step. That step is carried by S107 (`:52-54`) and by S106 and S111 (`:71-74`). This fits the row's scope exclusion.
- Nothing checks the link by machine. `count-c2.py:137-140` binds only the build and model sha. `tools/kama-context-capacity.py` has no stream or kv_size logic; its "stream" at `:447` is a request field.

**Census and contract shape: hold.**
- `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`: exit 0, "kama ok", 29 W04 lines, none for S113 (`out/ReopenS113/census-validate.tsv`).
- `census`: 113 rows, 94 mined (`census-count.tsv`). `overdue`: S113 appears only as a cadence line (on-release), never as overdue.
- Row shape: 11 inner cells, no stray pipe. Kind `code`, tier A (source code), status mined with a used-by path present, ISO opened date, symbolic recheck. Field rules are in `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:22-41`.

## Findings

**F1 (minor, teaches precision).** `SOURCES.md:125` teaches "total cells = kv_size × n_stream per layer (233-234)". Tensors are created only for layers that pass three skips: `llama-kv-cache.cpp:166-169` (no KV), `:171-174` (filtered), and `:176-191` (shared layers are pushed to `layers` and `continue` before any allocation). Reused layers at `:252-273` get no tensor. The fixture is a plain llama model and all 14 cells report 5 layers, so the claim is true here. The cited lines do not show that qualifier.
- Smallest correction: "...total cells = kv_size × n_stream for each layer that allocates its own K/V tensors (lines 166-191 skip others)."

**F2 (minor, anchor label).** `SOURCES.md:125` anchor says "constructor lines 65-98 (shared-source override 92-97)". The constructor starts at `:65` and closes at `:389`, the first column-0 `}` after `:65`. The next function starts at `:391`. Lines 65-98 cover the header, the member initializers, and the shared-source block. Nothing is false, but the label reads as if the constructor ends at 98.
- Smallest correction: "constructor header and shared-source override, lines 65-98 (override 92-97)."

**F3 (cosmetic).** The teaches cell writes `n_stream = unified ? 1 : n_seq_max` for the member initializer `n_stream(unified ? 1 : n_seq_max)` at `:84`. The meaning is the same. Optional: quote the initializer form.

**F4 (residual, corpus-wide, not blocking for S113).** The contract, `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:34-35`, says teaches is "one grounded learner benefit". Lines 45-48 ask for one quote of at most 25 words that grounds teaches. S113's teaches carries five claims (lines 84, 144, 233-234, 301-304, 93-97). The Gate quotes only line 301. The other four rest on the anchor line numbers and the sha256. This check read those lines and confirmed them. The corpus has the same pattern: teaches cells for S106 (66 words, 3 clauses), S107 (70 words, 4 clauses) and S112 (170 words, 8 clauses). This is a decision for the lesson owner, not a fault in S113 alone.

**F5 (not S113; for the integration owner).** In the working copy, `corpus/lessons/round-25.md` differs from fa3b62ae at working lines 51 (a new "misroot" row) and 53 (the "false timestamp" row, extended). Neither touches the S113 Gate line or the Gate paragraph. Commit or drop these before landing.

## Smallest corrections and the governance limit

- F1 and F2 cannot be fixed in place now. The row is committed at fa3b62ae, and contract rule 2 (`SOURCES-CONTRACT-v1.md:49-51`) allows in-place change only to status, recheck and used-by. The house routes are an appended correction note (pattern: `corpus/SOURCES.md:292-306`) or a row whose teaches opens "supersedes S113 —" (pattern: `corpus/SOURCES.md:324-333`). [INFERENCE: if the lead treats this row as still open for this round, an in-place edit before landing would be allowed. That call belongs to the lead.]
- No edit to `context-capacity.md` is needed. The entry does not use the per-layer product or the constructor range.
- No edit to the S113 Gate line is needed.

## Residual risk and verification gaps

- The shared-source override (`:92-97`) is not exercised. No registered cell uses a draft or shared-source cache. Source only.
- The skip branches (`:166-191` and `:252-273`) are not exercised. Source only.
- The receipt is a committed, dated sample. I did not start a server, so the live check is the committed receipt, not a new run.
- The log prefix `llama_kv_cache:` is not a literal in the source. It comes from the function name, since line 301 prints `%s`. Receipt line 35 shows the same prefix. [INFERENCE on the compiler's `__func__` value; the receipt confirms the output.]
- Census: I ran validate, census and overdue myself, read-only. The RerunCensus outputs in `a2-falsify/out/RerunCensus/` agree.

## Files I wrote

- `.ufo/waves/round-25/a2-falsify/advice/ReopenS113.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/checks.md` (per-check table, C1-C30)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/fetch-and-hash.txt` (commands, exit codes, hashes)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/receipt-cross-check.txt` (14-cell product check)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/committed-vs-working.txt` (sha comparison, lesson diff summary)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/census-validate.tsv` (validate output, exit 0)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/census-count.tsv` (census output, exit 0)
- `.ufo/waves/round-25/a2-falsify/out/ReopenS113/census-validate.err` (empty)

Heavy scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReopenS113/` (`llama-kv-cache.cpp` fetch, `api-contents-kv.json`, `api-tag-b11755.json`, `round-25.committed.md`, `round-25.diff.txt`).

Tools installed or updated: none.
