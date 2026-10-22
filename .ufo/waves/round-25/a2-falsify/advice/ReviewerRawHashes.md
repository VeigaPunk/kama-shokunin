# ReviewerRawHashes: C2 receipt integrity (round 25, attempt 2, wave 2, falsify)

Verdict: holds. The committed receipt at fa3b62ae matches all 70 raw files it names and re-derives cell for cell (384 checks, 0 mismatches). Three findings (F1 to F3) concern the registered verification path and the provenance record, not the stored bytes.

## 1. Scope and method

- Subject: `.ufo/waves/round-25/final/context-capacity-receipt.json` at fa3b62ae (git blob 516f4600, 413,554 bytes, sha256 78c51385) and the 70 files under `.ufo/waves/round-25/final/raw/` (14 cells, 5 files each).
- Committed bytes were read with `git show fa3b62ae:<path>`. Working-copy bytes were compared against them. Nothing outside the two allowed output locations was written.
- Re-derivation script: `out/ReviewerRawHashes/check_receipt_raw.py`. Run from that directory: `python3 check_receipt_raw.py`, exit 0, output `committed receipt: checks=384 mismatches=0`.
- No llama-server child was started by this seat. One check run after all analysis: `ss -ltn` listed no socket on 47400 to 47419, 8080 or 34113 (exit 0). `pgrep -a llama-server` found no matching process (non-zero exit; the command printed `none`).
- Installs or upgrades: none. Subagents: none. Network use: `curl` fetched six pinned llama.cpp source files to scratch (exit 0 each).

## 2. Mismatch list

Empty. The file `out/ReviewerRawHashes/mismatches.txt` reads: `committed receipt at fa3b62ae...: 0 mismatches over 384 checks`.

- Raw sha256: 70 of 70 match the receipt's `raw` map (`raw-sha-table.tsv`). The working copies match the committed bytes for all 70. The set of files on disk equals the set the receipt names.
- Cell values: props n_ctx, total_slots, the slots n_ctx list, models n_ctx_train, the log's n_ctx_train line, the last `llama_context: n_ctx` line and the startup slot line match the raw bodies in all 14 cells.
- Embedded fields: `log_lines` equals the tool's log filter applied to the raw server.log exactly (14 of 14). `kv_pool_candidates` equals every pool line exactly (14 of 14). `argv` equals the launch command built from `args` and the port (14 of 14).
- Load outcomes: all six request records agree with the server log (section 4).

## 3. Re-derivation table

Source: `out/ReviewerRawHashes/rederivation-table.tsv`. "receipt = raw" means the receipt field equals the value read from the raw file.

| cell | args | props n_ctx (receipt = raw) | total_slots | slots n_ctx (receipt = raw) | n_ctx_train (receipt = models = log) | last pool line (receipt = raw log) | startup slot line (n_slots, n_ctx_slot, kv_unified) |
|---|---|---|---|---|---|---|---|
| K1 | -c 0 | 2048 | 4 | 2048 x4 | 2048 | 2048 | 4, 2048, true |
| K2 | -c 2048 -np 2 --no-kv-unified | 1024 | 2 | 1024 x2 | 2048 | 2048 | 2, 1024, false |
| K3 | -c 2048 -np 2 --kv-unified | 2048 | 2 | 2048 x2 | 2048 | 2048 | 2, 2048, true |
| K4 | -c 1024 -np 1 | 1024 | 1 | 1024 | 2048 | 1024 | 1, 1024, false |
| K5 | -c 4096 -np 1 | 2048 | 1 | 2048 | 2048 | 4096 | 1, 2048, false |
| K6 | -c 1000 -np 3 --no-kv-unified | 512 | 3 | 512 x3 | 2048 | 1536 | 3, 512, false |
| K7 | -np 2 --kv-unified-per-slot 512 | 512 | 2 | 512 x2 | 2048 | 1024 | 2, 512, false |
| K8 | -c 4096 -np 4 --kv-unified --kv-unified-per-slot 512 | 512 | 4 | 512 x4 | 2048 | 4096 | 4, 512, true |
| X1 | -np 4 --no-kv-unified | 2048 | 4 | 2048 x4 | 2048 | 8192 | 4, 2048, false |
| X2 | -c 8192 -np 4 --no-kv-unified | 2048 | 4 | 2048 x4 | 2048 | 8192 | 4, 2048, false |
| X3 | -np 4 --no-kv-unified --fit off | 512 | 4 | 512 x4 | 2048 | 2048 | 4, 512, false |
| L1 | -c 0 | 2048 | 4 | 2048 x4 | 2048 | 2048 | 4, 2048, true |
| L2 | -c 8192 -np 4 --no-kv-unified | 2048 | 4 | 2048 x4 | 2048 | 8192 | 4, 2048, false |
| L3 | -c 0 | 2048 | 4 | 2048 x4 | 2048 | 2048 | 4, 2048, true |

The log lines behind the non-trivial pool values match their stated causes:

- K5: `K5.server.log:1083` `the slot context (4096) exceeds the training context of the model (2048) - capping`.
- K6: `K6.server.log:282` `n_ctx is not divisible by n_seq_max - rounding down to 1536`.
- K7: `K7.server.log:9` `sizing KV pool to n_parallel * kv_unified_per_slot = 2 * 512 = 1024`.
- K8: `K8.server.log:1083` `capping per-slot context (4096) to --kv-unified-per-slot (512)`.
- X1: `X1.server.log:547` `context size unset and KV cache not unified -> using 8192 for 4 sequences`. The first pool line, 2048 at `X1.server.log:283` with `n_ctx_seq = 512`, is a fit probe. The serving pool is 8192 (lines 812 and 1344, `n_ctx_seq = 2048`).

## 4. Load-cell outcomes from the server log

Source: `out/ReviewerRawHashes/l-outcome-table.tsv`. Log lines are 1-based line numbers in `raw/<cell>.server.log`.

| cell | request | log task | receipt status | receipt error | tokens | log task start to release (s) | log evidence | first decode n_tokens | n_gen | log overlap |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 0 | 2 | 500 | Context size has been exceeded. (server_error) | none | 0.502342 to 0.524972 | `send_error: task id = 2` at line 1849; release line 1852 | 1000 | none | True |
| L1 | 1 | 3 | 500 | same text | none | 0.502373 to 0.525056 | `send_error: task id = 3` at line 1863; release line 1866 | 1000 | none | True |
| L2 | 0 | 2 | 200 | none | 600 | 0.503639 to 0.676927 | no send_error; `n_gen = 600, n_remaining = 0` at line 12668 | 1000 | 600 | True |
| L2 | 1 | 3 | 200 | none | 600 | 0.503663 to 0.676952 | no send_error; line 12679 | 1000 | 600 | True |
| L3 | 0 | 2 | 200 | none | 600 | 0.502735 to 0.627049 | no send_error; line 11442 | 1000 | 600 | False |
| L3 | 1 | 603 | 200 | none | 600 | 0.628104 to 0.758413 | no send_error; line 21696 | 1000 | 600 | False |

Notes on L1: lines 1748 and 1749 show both tasks at `n_tokens = 1024` in a 2048-token pool. Line 1848 is the `decode: Context size has been exceeded.` error that starts the failure. Lines 1849 and 1863 are `send_error` for tasks 2 and 3. The receipt records what the server log shows: both requests failed. The prediction in amendment 2 said at least one would fail; both did. This is an observed outcome recorded as the registration requires, not a claim value.

Notes on L2 and L3: the 200 status is not written in any artifact. See F2.

Concurrency is supported by the log independently of the receipt. In L1 and L2 the two tasks decode in the same time window. In L3 task 603 starts after task 2 releases.

## 5. Checks that held

- Provenance: the final/ tree is byte-identical at 5c95c8f and fa3b62ae, except that fa3b62ae adds four c1/ files. `git diff --stat 5c95c8f fa3b62ae -- .ufo/waves/round-25/final/` lists only those four (exit 0). Receipt blob 516f4600 is the same at both commits.
- Time order: amendment 4 (commit 46fb04b, committer 06:42:31 -03, which is 09:42:31Z) precedes the run (started 2026-10-22T09:42:42.438Z). The run precedes commit 5c95c8f (06:42:57 -03, which is 09:42:57Z).
- Earlier receipt: the committed counter on the 5ea4fc4 receipt (blob 3909806f) prints `registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']`, exit 0. This matches amendment 4's statement that the earlier receipt scores 11 of 14.
- Counter on the committed receipt: `git show fa3b62ae:.ufo/waves/round-25/count-c2.py | python3 - .ufo/waves/round-25/final/context-capacity-receipt.json`, exit 0, prints `registered 14 observed 14 bound True missing []`.
- Binding on disk: model sha256 270cba1b... and size 1,185,376 match the receipt. The llama-server binary at `/home/vgpnk/.local/opt/llama-b11755/llama-server` has sha256 b6a31a8e..., matching the receipt. Tool sha256 589841cd... matches the receipt, the committed bytes and the working copy.
- Build identity: each server log has the line `build 11755 (704366d76)`.
- Ports: all 14 ports lie in 47400 to 47419, are unique, and avoid 8080 and 34113. The registry's three consumers use 8080 and 34113 only (`registry/endpoint-consumers.tsv` rows 35 to 37). Teardown: each child returned 0, and each log contains the clean-exit line `cleaning up before exit`.
- Cell windows are sequential, and each cell's last log timestamp falls just before its recorded wall time. K1 to X3: last log 0.5006 to 0.5021 s, wall 0.503 to 0.504 s. L1: 0.526 vs 0.529 s. L2: 0.678 vs 0.680 s. L3: 0.759 vs 0.761 s.
- Server log: no `POST` line appears in any of the 14 logs. `send_error` appears twice in L1 and zero times elsewhere. No `truncated = 1` line appears in L1, L2 or L3.

## 6. Findings

F1 (medium; verification path, not the receipt). The registered counter never reads the raw directory, never hashes a file, and never checks the receipt's `raw` map. `count-c2.py` line 118 reads only the receipt. The `bound` check (lines 136 to 140) compares two strings already in the receipt against constants. It does not hash the model or binary files on disk.

Evidence: five synthetic negatives were built in scratch from the committed receipt (`out/ReviewerRawHashes/synthetic-negatives.tsv`). The committed counter accepted all five with `registered 14 observed 14 bound True missing []`, exit 0. The re-derivation flagged each one:

- M1: K1 props_n_ctx changed from 2048 to 2047. One mismatch.
- M2: both L1 requests changed from 500 to 200, error text kept. Two mismatches.
- M3: K5 pool changed from 4096 to 2048 in the embedded log and pool fields, kept self-consistent. Three mismatches.
- M4: K2 raw_props hash replaced in the receipt map only. One mismatch.
- M5: K2 props.body bytes changed in memory (n_ctx 1024 to 1025), receipt unchanged. Two mismatches.

The committed bytes are not affected. The gap is that the registered command would accept an edited receipt.

Smallest correction (for the L1 integrator to apply; not applied here):
1. In `count-c2.py`, recompute sha256 of each file named in each cell's `raw` map and compare. Re-derive props n_ctx, total_slots, slots list, n_ctx_train, the last pool line and the startup slot line from those bodies. The existing pool-line rule is the model for this.
2. For load cells, require: status 500 with the send_error text exactly when server.log has `send_error: task id = <task>` for that request; status 200 with 600 generated tokens otherwise.

F2 (low; evidence gap). HTTP status codes for load requests are not stored anywhere. The tool parses completion bodies and discards them (`tools/kama-context-capacity.py:514-553`). `_capture_raw` (lines 420 to 427) writes only four GET bodies. The server log has no HTTP status line.

- L1's 500 is traced to pinned source. `format_error_response` maps `ERROR_TYPE_SERVER` to `server_error` with code 500 (server-common.cpp:107-109). `send_error` defaults to that type (server-context.cpp:2170, 2179). Its error result converts with `format_error_response(err_msg, err_type)` (server-task.cpp:1505). The HTTP status is copied from the `code` field on the exception path (server.cpp:83). The branch that carries a queued error result to the response was not fetched; the comment at server-http.cpp:212 says `res->error()` handles it. [INFERENCE] for that last step.
- L2 and L3's 200 is [INFERENCE]. The tool records `tokens_predicted` only on a 200 response (tool:541-542). The log shows 600 generated tokens and no send_error.

Smallest correction: write each completion response body under `raw/` and include its sha256 in the cell's raw map.

F3 (low; provenance). `receipt['host_idle']` is overwritten on every cell (tool:790-793). The receipt keeps only the L3 record: `{"cell": "L3", "ok": true, "other_pids_seen": [], "waited_s": 0.024}`. Host-idle evidence for the other 13 cells is missing. One child at a time is still supported by the sequential cell windows (checked) and by the empty listener and process lists (checked now). Smallest correction: store host_idle inside each cell record.

F4 (info). `log_lines` keeps only lines matching `n_ctx|kv_unified|n_seq|capping|rounding|KV pool|llama_kv_cache: size` (tool:94-96). The filter drops send_error and "Context size" lines. L1's embedded log has zero send_error lines; the raw log has two. A reader of the receipt alone cannot see the L1 failure. The raw server.log, which is hashed, shows it.

F5 (info). Request `prompt_tokens` (1000) and `n_predict` (600) are tool constants (tool:526-527), not measured values. The log confirms both: first decode n_tokens is 1000, and n_gen reaches 600 (lines 12668, 12679, 11442, 21696).

F6 (info). Parsed props, slots and models come from a second GET made after the raw capture (tool:346-349 against 420-427). All 14 cells agree, so no harm. The re-derivation in this report reads the raw bodies directly.

F7 (info). `L2.server.log:12685` has two log records glued together: `No parser definition detected ... sending result for task id = 3`. This is an output interleaving artifact. It does not affect any value and is kept verbatim.

## 7. Residual risk and verification gaps

- The HTTP status codes for L2 and L3 cannot be re-derived from any stored artifact (F2). Their 200 status is inferred.
- The step from the queued error result to the HTTP response was not fetched (F2).
- The llama-server build was not run to print its version. Running `--version` starts a llama-server process, which this seat was forbidden to do. Build identity rests on the build line in each log and on the binary's sha256.
- This check verifies stored bytes and their internal consistency. It does not reproduce the runs.
- The counter's "observed" flags are computed by the tool. This report did not recompute the flags themselves. It re-derived each value they depend on from the raw bytes, and all agree.

Sources (llama.cpp commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, fetched 2026-10-22 from https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/<file>; sha256 values in `out/ReviewerRawHashes/pinned-source-sha256.txt`):

- server-common.cpp:107-109: `type_str = "server_error";` and `code = 500;`
- server-context.cpp:2170: `const enum error_type type = ERROR_TYPE_SERVER`
- server-context.cpp:4301: `err = "Context size has been exceeded.";`
- server-context.cpp:4320: `send_error(slot, err);`
- server-task.cpp:1505: `json res = format_error_response(err_msg, err_type);`
- server.cpp:83: `res->status = json_value(error_data, "code", 500);`
- server-http.cpp:212: `// for other error codes, we skip processing here because it's already done by res->error()`

## 8. Files written

- `.ufo/waves/round-25/a2-falsify/advice/ReviewerRawHashes.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/check_receipt_raw.py`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/raw-sha-table.tsv` (70 rows)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/rederivation-table.tsv` (14 rows)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/l-outcome-table.tsv` (6 rows)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/mismatches.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/synthetic-negatives.tsv` (5 rows)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerRawHashes/pinned-source-sha256.txt`

Scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReviewerRawHashes/` holds `receipt-5ea4fc4.json`, `receipt-tip.json`, `mutants/M1.json` to `M5.json`, and `src/` (six fetched llama.cpp files).
