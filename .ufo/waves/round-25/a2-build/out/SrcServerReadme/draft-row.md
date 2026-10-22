# Draft SOURCES registry row — S1xx (status queued)

Scope: C2 (learning claim, frontier K05: declared versus served context capacity) is a
sourced claim. This row covers the llama.cpp server README at commit 704366d76 for the
props/slots/option-doc sections only. It is a DRAFT: id left as S1xx, status `queued`
until the L1 cites it. Do not edit SOURCES.md from this seat.

## Row (exact 11-column format of corpus/SOURCES.md)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp server README @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md | docs | A | what the server README at commit 704366d76 promises n_ctx means: the `-c`/`--ctx-size`, `--kv-unified`, `--parallel`, `--kv-unified-per-slot` option docs and the `/props`, `/slots` sections; not runtime behaviour, not the loading lifecycle (S035/S036/S037), not the implementation (S060) | §Common params line 50 (`-c, --ctx-size`); §Server-specific params lines 165 (`--kv-unified-per-slot`), 169 (`--kv-unified`), 177 (`--parallel`); §GET `/props` lines 839-934 (default_generation_settings bullet 927, total_slots bullet 928); §GET `/slots` lines 983-1126 (n_ctx example values at 999 and 1064); §GET `/v1/models` line 1304 (meta.n_ctx_train); §POST `/completion` generation_settings bullet 671 and truncated bullet 683; raw file sha256 714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37 | The only pool-sizing promise in the README is `--kv-unified-per-slot`: when set without `-c`/`--ctx-size`, the shared KV pool is sized to n_parallel*N. Otherwise n_ctx appears only as fields: `-c` is "size of the prompt context (default: 0, 0 = loaded from model)"; `--kv-unified` is "single unified KV buffer shared across all sequences (default: enabled if number of slots is auto)"; `--parallel` is "number of server slots (default: -1, -1 = auto)"; `/props` default_generation_settings "has the same fields as the generation_settings response object from the /completion endpoint" (which includes n_ctx); `/props` total_slots is "defined by --parallel"; `/slots` returns per-slot state including n_ctx (example values only); `/v1/models` meta.n_ctx_train is the training context; /completion truncated defines n_ctx as the context size exceeded when tokens_evaluated plus tokens_predicted exceed it. The README does not define n_ctx in /props or /slots as per-slot or pool-level, does not state how an unset (0) context divides across slots, does not state the served n_ctx for any -c/-np/kv-unified combination, and never mentions the KV pool size in any HTTP surface. | queued | 2026-10-22 | on-release | corpus/knowledge/context-capacity.md |

## Why a new row is needed

- S035 exists on this exact file and commit but its scope is only `/health` load-state docs
  (lines 479-490) and `/v1/models` line 1258; it explicitly says it is "not `/v1/models`
  loading behaviour" and covers neither /props, /slots, nor the option docs. It does not
  cover this claim.
- S060 is the code row (server-context.cpp) establishing what /props actually reports
  (capped per-slot n_ctx) — that is implementation, not the README's promise. The C2
  receipt records both the docs promise and the observed values, so the two rows are
  complementary, not duplicates.
- No other row in SOURCES.md (grep of `server/README`, `/props`, `/slots`, `kv-unified`,
  `n_ctx`, `ctx-size`) covers the props/slots/option-doc sections of this file.
