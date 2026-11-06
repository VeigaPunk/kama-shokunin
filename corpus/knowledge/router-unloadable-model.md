source: S583 (llama.cpp `tools/server/server-models.cpp` @ 6c01da6278ab6c69ed67d9124806b50d2b299ba7 = release b12177, lines 1641, 1956, 1962, 2121-2125, 2269-2273), S584 (`ggml/src/gguf.cpp` @ same commit, gguf_init_from_file_impl header checks), S585 (`gguf-py/gguf/constants.py` @ same commit, `GGML_QUANT_SIZES`); own-work receipts `.ufo/waves/round-89/controls/c1-base.out`, `.ufo/waves/round-89/measured/c1.out`, `.ufo/waves/round-89/measured/router-signatures.jsonl`. Prior art held before round 89: S581/`router-mode-readiness.md` (status vocabulary, `failed: true` after a failed load), SKILL rows E26-15/E26-16 (single-model startup log for a missing or non-GGUF `-m` file, S129), `gguf-declared-identity.md` (a header reader is not loader validation).
verified-at: 2026-11-06 — lane-owned b12177 router children (binary sha256 `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`) and the pinned b11755 build (L1 pre-freeze recon, same behaviour); the header rule checked against 36 GGUF files on this host (all graded loadable) and the operator router 127.0.0.1:1234 (GET only).
recheck: on-release — `python3 tools/round89-unloadable-cells.py --repo . --rev master --work <scratch>` must print `cells=11 mismatches=0`; re-capture `python3 tools/round89-router-signatures.py --out <f> --work <scratch>` and re-run `python3 tools/round89-signature-rows.py --repo . --rev master` after moving the pinned build; re-diff `GGML_QUANT_SIZES` against the probe's `QSIZES` table.

# llama.cpp router: a listed model whose file cannot load

## What was already held (not new in round 89)

The lane knew that a router's model list is an inventory, not readiness (S553, S581), that a failed load
leaves the entry `unloaded` with `failed: true` (S581 status list), that a single-model server started on a
missing or non-GGUF `-m` file exits 1 with `failed to open GGUF file` / `invalid magic characters` in its log
(SKILL E26-15/E26-16), and that decoding a GGUF header proves nothing about loading (`gguf-declared-identity.md`).

## What round 89 adds

1. **Before any load is attempted, an unloadable model looks exactly like a loadable one.** A router started
   with `--models-dir` or `--models-preset` lists every source entry as `"status":{"value":"unloaded"}` without
   opening the file; a missing preset path, a plain-text `.gguf`, a header with garbage counts, a half-length
   file and a file deleted after start are all listed identically (`controls/c1-base.out`, b12177; same on
   b11755 in pre-freeze recon). The round-88 probe graded every one `MODEL_OK router-unloaded-autoload`.
2. **The first real request fails, not the listing.** On an autoload router the completion answers
   `500 {"error":{"code":500,"message":"model name=<id> failed to load","type":"server_error"}}` (S583:1641:
   the waiter sees the spawned instance come back down failed); afterwards the entry reads `unloaded` +
   `failed: true` + `exit_code: 1`. Without autoload the same entry answers `400 model is not loaded`
   (S583:1962), indistinguishable from a healthy unloaded model.
3. **The router hands out the model path.** b11755 and b12177 both put the child's full argv in
   `status.args`, including `--model <path>`, so a prober on the same host can check the file without touching
   the router. The operator's router lists absolute paths; a router started with a relative `--models-dir`
   lists relative paths, which resolve against the router's cwd, not the prober's.
4. **The loader's header checks are decidable from the header alone** (S584): magic `GGUF`; version not 1, not
   above 3, low 16 bits not zero (byte-swapped); `general.alignment` a power of two (u32); at most 4 dims;
   ne[0] a multiple of the type's block size; each tensor's offset equal to the running sum of padded sizes;
   then the llama model loader requires every tensor's bytes inside the file. Tensor byte size = elements /
   block size × bytes per block (S585). The format spec (S586, rejected as the authority here) is not what the
   loader enforces: it asks for version 3 and padding between tensors, while the loader also loads version 2 and
   requires exact contiguity.

## Decision rule (kama-probe, round 89)

| Matching entry, autoload router, `status.args[0]` a local file | Verdict / reason |
|---|---|
| absolute model/mmproj/draft path absent | `MODEL_UNLOADED` / `router-model-missing` |
| path not a regular file, or a header check above fails | `MODEL_UNLOADED` / `router-model-invalid` |
| relative path, unreadable file, unknown tensor type, parse budget exceeded | unchanged: `MODEL_OK` / `router-unloaded-autoload` |
| any other matching entry loadable | it wins (unchanged precedence) |

Measured (`measured/c1.out`, M `4f9eacf7`): 11 live cells, oracle = the router's answer to a real completion;
base 5 mismatches (U1–U5 false green), M 0, positive cells 0 at both.

## Limits

- A file with an intact header and corrupt tensor bytes, a missing second shard of a split model, an
  out-of-memory load, or a file readable by the router's user but not the prober's still grades
  `MODEL_OK router-unloaded-autoload`: only a load can tell, and the probe never loads.
- A router whose `status.args[0]` exists on this host by coincidence (a remote router behind a tunnel with the
  same binary path) would have its paths checked against this host's filesystem.
- The tensor-type table is b12177's; a newer type is "unknown" (no verdict change), never a false red.
- `sleeping` entries are not checked: their file was loadable when they were loaded.
