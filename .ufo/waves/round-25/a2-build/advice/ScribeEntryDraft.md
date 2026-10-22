VERDICT: C2 knowledge-entry draft filed; every claim is source-anchored (pinned llama.cpp lines, fetched fresh) or cell-referenced with a `pending cell <id>` value; no llama-server child started, no port opened, no production file written.

Seat: KamaR25a2.ScribeEntryDraft (scribe, leaf, read-only). Lane branch master tip 1fc41e346853afd98cbd7010af5db4e54dc877f7. Access date for every source: 2026-10-22.

## Behavior

1. Read the binding round-25 files: `preregistration.json`, `preregistration-amendment-1.json`, `preregistration-amendment-2.json`, `count-c2.py`, `pilot.md`, `build/ATTEMPT-1-DISPOSITION.md`, both critic reports (`CriticLearningBar.md`, `CriticC2Sizing.md`), the two knowledge-entry format samples (`gguf-declared-identity.md`, `llamacpp-loading-lifecycle.md`) and `corpus/QUALITY.md` (admission criteria).
2. Fetched the six pinned llama.cpp sources fresh from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/...` into `/fast/scratch/hyaku/kama-r25a2/ScribeEntryDraft/src/` (curl exit 0 each; sha256: `src/llama-context.cpp` 2a25e556…aa5, `common/fit.cpp` 1f83da2a…dd58, `common/common.h` 8bcc5708…a9, `common/arg.cpp` bf4c58c1…d2d, `tools/server/server.cpp` 2143962217…ef4, `tools/server/server-context.cpp` dd1de0f2…2329 — the last equals S060's recorded hash). Read the cited line ranges from the fetched copies (not from the round-16 snapshot).
3. Verified fixture metadata with the lane tool: `python3 tools/gguf-identity.py ~/.cache/kama-shokunin/models/stories260K.gguf --json` (exit 0): architecture `llama`, `llama.context_length` 2048, 5 blocks, 64 embedding dims, GGUF v3, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (sha256sum exit 0). No sliding-window key, no rope-scaling/YaRN key present.
4. Drafted the entry at `.ufo/waves/round-25/a2-build/out/ScribeEntryDraft/context-capacity.md` (12,081 bytes) with the requested structure: pool versus slot; fit raising an unset split context; the full-context concurrency limit of a shared pool (server-context.cpp:4301,4318-4320,4334-4339); what the HTTP surfaces cannot show; a scope block (build 11755, fixture sha256 + architecture, n_ctx_train 2048, no SWA, no rope scaling, fit never binds on this fixture); a does-not-establish block; and a prediction-status table. Predicted values are written as `pending cell <id>`; the L1 fills them from the committed receipt.
5. Wrote this advice report.

## Gates

- No llama-server child started; no port checked or opened; the `ss -ltn` precheck was not needed. No `~/.local/bin/llama-server` invocation.
- Leaf member: no subagent dispatch, no peer messages.
- Wrote only under `.ufo/waves/round-25/a2-build/out/ScribeEntryDraft/` and `a2-build/advice/` (both inside the lane). No production file touched: no SOURCES row, no corpus file, no git/jj command of any kind.
- No tool installed or updated.
- Receipt counting is left to the L1 via `count-c2.py`; a cell counts only with integer `props_n_ctx`, `total_slots`, `models_n_ctx_train`, `kv_pool_n_ctx`, a non-empty integer `slots_n_ctx` list, non-empty `log_lines` including a `llama_context: n_ctx N` line ending in `kv_pool_n_ctx`, and for load cells `request_mode` (`concurrent`/`sequential`) plus at least two requests with integer status, `prompt_tokens 1000`, `n_predict 600` (count-c2.py:43-70).

## Findings

- **Round-20 formula is wrong for X1.** `nctx-crosscheck.py` `predict()` returns per-slot 512 for `-np 4 --no-kv-unified`; the fit source (`common/fit.cpp:195-198,266-273`) raises the unset context to `n_ctx_train * n_streams` = 8192 pool, per-slot 2048. The entry supersedes that row explicitly and names X1 as the control that must disagree with 512. The round-20 docstring excludes only "--fit run lowered n_ctx", not the raise.
- **Three served surfaces report one value.** `/props` `n_ctx` (server-context.cpp:5236), `/slots` `n_ctx` (:1437) and `/v1/models` `meta.n_ctx` (:5186) all read `n_ctx_slot()` (:4829); their agreement is expected, not independent evidence. The pool and cache layout appear in no HTTP field; the pool line `llama_context: n_ctx` needs `-v` (amendment-2 honesty note 11).
- **Shared-pool failure is all-or-most.** `server-context.cpp:4301` + `4318-4320` send `Context size has been exceeded.` to every processing slot; K1 (shared 2048 pool) vs X2 (four private 2048 streams) have identical served surfaces but a fourfold full-context concurrency difference.
- **Flag wording traps:** `--kv-unified-per-slot` sizes the pool even for a split cache (server.cpp:183-184, K7); the "rounding down" warning fires while the pool rises (llama-context.cpp:391, K6: 1000 → 1536).
- **Scope honesty:** fit reduction runs only when projected free memory is below margin (fit.cpp:375-393) and only when `n_ctx_max > n_ctx_min_total` for auto contexts (fit.cpp:393-394); the fixture's ~640 B/token KV estimate is [INFERENCE], so "fit never binds" is a scoped claim for this fixture, not a universal. `-c 0` disables fit reduction (arg.cpp:1646-1648); omitting `-c` differs from `-c 0` under memory pressure — in the does-not-establish block.

## Out-of-scope items

No SOURCES row opened (production file; L1 writes it at admission — the entry header flags the pending rows per KQ31). No attempt-1 output was reused as evidence; attempt-1 receipt rows were not read (amendment-2 blinding respected). No cell was observed; every value in the draft is a preregistered prediction.

## Artifacts

- Draft entry: `.ufo/waves/round-25/a2-build/out/ScribeEntryDraft/context-capacity.md`
- This report: `.ufo/waves/round-25/a2-build/advice/ScribeEntryDraft.md`
- Scratch (heavier): `/fast/scratch/hyaku/kama-r25a2/ScribeEntryDraft/src/*` (six pinned sources), `model-identity.json` (gguf-identity.py output).
