# ReopenS107 check log (access date 2026-10-22; pin 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad)

Scratch copies (heavy, not in the lane): /fast/scratch/hyaku/kama-r25a2w2/ReopenS107/

## Fresh fetches and hashes

| file (pinned raw URL path) | exit | lines | sha256 | cross-check |
|---|---|---|---|---|
| src/llama-context.cpp | 0 | 4719 | 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 | `sha256sum -c` against the string typed from SOURCES.md:119 -> `llama-context.cpp: OK`, exit 0; grep finds the string once, at SOURCES.md:119 |
| ggml/include/ggml.h | 0 | 3028 | 475beaa7e959be8c383279d9ce9d5191f37426e6b338270cfb12b26a798129d3 | GGML_PAD at ggml.h:267 |
| common/fit.cpp | 0 | 1113 | 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58 | equals S106 raw sha256 (SOURCES.md:118) |
| common/common.cpp | 0 | 2460 | d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 | equals S111 raw sha256 |
| common/common.h | 0 | 1330 | 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9 | equals the value recorded in a2-build/out/ScoutR20Entry/evidence.md:121 |

Release label: `git ls-remote https://github.com/ggml-org/llama.cpp refs/tags/b11755 'refs/tags/b11755^{}'` -> exit 0; output `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755` (lightweight tag, no peeled line).

## llama-context.cpp line evidence (fresh bytes)

- 168: `llama_context::llama_context(`; no column-0 `}` between 168 and 430 (grep `^\}` in 160-430 matched only `};` at 160), so 377-417 sit inside the constructor.
- 219: `    cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`
- 377: `    cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);`
- 379: `    if (cparams.kv_unified) {`; 380: `cparams.n_ctx_seq = cparams.n_ctx;`; 381: `} else {`
- 382: `cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;`; 383: `cparams.n_ctx_seq = GGML_PAD(cparams.n_ctx_seq, 256);`
- 385-386: `if (cparams.n_ctx_seq == 0) { throw ... }`
- 389: `if (cparams.n_ctx != cparams.n_ctx_seq * cparams.n_seq_max) {`; 390: `cparams.n_ctx =  cparams.n_ctx_seq * cparams.n_seq_max;`
- 391: `LLAMA_LOG_WARN("%s: n_ctx is not divisible by n_seq_max - rounding down to %u\n", __func__, cparams.n_ctx);`
- 392: `}`; 393: `}` (closes else)
- 396: `LLAMA_LOG_INFO("%s: n_ctx                 = %u\n", ...)`; 397: n_ctx_seq log
- 409-412: `if (cparams.n_ctx_seq < hparams.n_ctx_train) { LLAMA_LOG_INFO(...) }`
- 414-417: `if (cparams.n_ctx_seq > hparams.n_ctx_train) { LLAMA_LOG_WARN(...) }`
- Every assignment to `cparams.n_ctx` or `n_ctx_seq` in the file (grep `(cparams\.n_ctx|n_ctx_seq)\s*=[^=]`): 219, 377, 380, 382, 383, 390. None clamps.
- `n_ctx_train` reads in the constructor: 219, 225, 409-416 only (other hits are in other functions: 3753-3754, 3820-3821, 3931-3933, 4034).
- 4021: `llama_context * llama_init_from_model(` ; 4110-4114: `try {`, `auto * ctx = new llama_context(*model, params);`, `const auto & cparams = ctx->get_cparams();`, blank (4113), `if (cparams.rope_scaling_type == LLAMA_ROPE_SCALING_TYPE_YARN && ...) {` (4114)
- 4115-4117: two LLAMA_LOG_INFO lines and `model->hparams.n_ctx_train = cparams.n_ctx_orig_yarn / cparams.rope_freq_scale;` (4116); 4118: `}`

## Fit chain at the pin (why line 219 is not reached on a default launch)

- common.h:457 `int32_t n_ctx = 0; // context size, 0 == context the model was trained with`
- common.h:483 `bool fit_params = true;  // whether to fit unset model/context parameters to free device memory`
- common.cpp:1243 `auto cparams = common_context_params_to_llama(params);`; 1714 `cparams.n_ctx = params.n_ctx;`
- common.cpp:1245 `if (params.fit_params) {`; 1270-1276 `common_fit_params(..., &cparams, ...)`
- fit.cpp:192 `uint32_t hp_nct = 0; // hparams.n_ctx_train` (declaration comment; the filling line was not located -> [INFERENCE] that hp_nct is n_ctx_train)
- fit.cpp:197 `n_streams = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);`; 198 `n_ctx_auto = cparams->n_ctx == 0;`
- fit.cpp:205-208: `auto add_extra_memory = [&](dmds_t & dmds) { if (extra == nullptr) { return; }` (the early return is inside this lambda, not the function)
- fit.cpp:267 `n_ctx_max = min(hp_nct * n_streams, UINT32_MAX)`; 270 comment `llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:`; 271-272 `if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;`
- common.cpp:1372 `llama_context * lctx = llama_init_from_model(model, cparams);` (same variable)

Consequence (verified by reading the chain above): default launch (fit on), no `-c`, split cache, n_seq_max = 4 -> constructor receives n_ctx = 2048 x 4 = 8192 (not 0), so line 219 takes the `params.n_ctx` branch. Registry teaches rule applied to X1 would predict pool 2048, 512 per slot; the entry's X1 row records pool 8192, 2048 per slot (raw log not re-run here).

## Arithmetic from the S107 rules (no server started)

- `-c 1000`, 3 split slots: GGML_PAD(1000,256)=1024; 1024/3=341; GGML_PAD(341,256)=512; 512x3=1536 (entry K6 matches).
- X3 (`--fit off`, `-np 4`, no -c): 2048 -> 2048/4=512 -> 512x4=2048 pool, 512 per slot (entry X3 matches).
- ggml.h:267 `#define GGML_PAD(x, n) (((x) + (n) - 1) & ~((n) - 1))`.

## Working tree vs committed tip (fa3b62ae6475d111eb466d79af616aeebb08bbb9)

| file | committed sha256 | working sha256 at read time | S107 mentions |
|---|---|---|---|
| corpus/SOURCES.md | 45810d499dd65f2f5d1a76280c3cf7cd654a387d12ca97931a66e0df06e6a4a7 | same | row line 119 only |
| corpus/lessons/round-25.md | 9d7ec2953b39469b7094ee830c429a5ac7c3a6add72625d77a2e856592476a16 | 3fc874ba6bad4d6a9e9a0d6ebcf4ac2f86b750dcfcca2faa0bc1af90222363bb | Gate row line 23, identical text in both |
| corpus/knowledge/context-capacity.md | 0959b2342c74b23e46634f029d8e296f3ed29f80cdfe710cef43a5526f78b958 | cea0f42211dcaf61c8e1aa6916b23c5cb5dd9484c07263811dda42c918e2694f (239 lines; copy at scratch entry-working-snapshot.md) | committed: lines 1, 54, 81-82, 167-168; working: lines 1, 59, 91-92, 218-219 |

The working entry and lesson changed while this check ran (earlier reads showed entry sha 7b98dc..., lesson 0d17b907...). Verdicts apply to the snapshot named here.

## Other registry-type files

`SKILL.md`, `SCORECARD.md`, `tools/kama-context-capacity.py`, `.ufo/waves/round-25/count-c2.py`, `preregistration.json`, `errata-attempt-2.json`: all exist (test -e exit 0) and contain no literal `S107` (grep).

## Provenance

`.ufo/waves/round-25/a2-build/advice/SrcLlamaContextPad.md` records the same sha256 (2a25e556...), 4719 lines, curl exit 0. `a2-build/out/ScoutR20Entry/evidence.md:119` records `line 380` for the division and `381` for the pad; the pinned bytes have them at 382 and 383 (stale record, not a registry cell).

## Not run

No llama-server started. No commit, push, index write, or jj command. Installed tools: none (curl, git, sha256sum already present).
