# Gate record — llama.cpp tools/server/README.md @ 704366d76

- URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md
  (blob form: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md)
- Access date: 2026-10-22
- Fetch: `curl -fsSL` to /fast/scratch/hyaku/kama-r25a2/SrcServerReadme/README-704366d.md
  (exit 0)
- sha256 (fresh fetch): `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`
- Fresh fetch is byte-identical (`cmp -s` exit 0) to the round-16 pinned snapshot
  `.ufo/waves/round-16/sources/llama.cpp-704366d/README.md` (same sha256) and to the
  sha256 recorded in SOURCES row S035; the file has not changed since round 16.

## Located quotes (each at most 25 words)

1. Line 165 (§Server-specific params, `--kv-unified-per-slot`):
   "when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N"
   (12 words)
2. Line 169 (§Server-specific params, `--kv-unified`):
   "use single unified KV buffer shared across all sequences (default: enabled if number
   of slots is auto)" (17 words)
3. Line 50 (§Common params, `-c, --ctx-size`):
   "size of the prompt context (default: 0, 0 = loaded from model)" (14 words)

## Other anchors read

- Line 177: `--parallel` "number of server slots (default: -1, -1 = auto)".
- Line 927: `/props` default_generation_settings "has the same fields as the
  generation_settings response object from the /completion endpoint".
- Line 928: `/props` `total_slots` "the total number of slots for process requests
  (defined by `--parallel` option)".
- Line 671: /completion generation_settings "including `n_ctx`, `model`".
- Line 683: /completion `truncated`: context size exceeded when `tokens_evaluated` plus
  `tokens predicted` exceeded "the context size (`n_ctx`)".
- Line 983/985: `/slots` "Returns the current slots processing state", per-slot metrics.
- Lines 999, 1064: `/slots` example n_ctx values (65536) — example data only.
- Line 1304: `/v1/models` meta example includes `n_ctx_train` (131072).
