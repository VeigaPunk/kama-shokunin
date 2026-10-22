PASS — freshly opened pinned common/common.cpp supports the conditional common-initialization fit call; a new queued registry row is needed, not runtime execution credit.

## Axes

Source provenance, exact condition coverage, registry compatibility, and honest limits. This seat is SrcCommonInitFit in attempt 2; no attempt-1 output was reused as evidence.

## Commands and observed outcomes

Executed once:

```sh
mkdir -p /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit && curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp -o /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp && sha256sum /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp && wc -l /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp
```

Successful command completion, exit 0. Output:

```text
d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4  /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp
2460 /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp
```

Preserved those fetched bytes without fetching again:

```sh
mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcCommonInitFit && cp /fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcCommonInitFit/common.cpp && printf 'source artifact copy exit=0\n'
```

Exit 0; output: `source artifact copy exit=0`.

The `read` tool opened source lines 1240–1280 and 1410–1425. The `grep` tool searched `corpus/SOURCES.md` with exact pattern `common/common\.cpp` and returned `No matches found`; searching `\bfit\b` also returned `No matches found`. These are tool results, not shell commands with separately reported exit codes. Registry header at `corpus/SOURCES.md:11` establishes the eleven columns. Existing S054/S056 concern common/arg.cpp duplicate-option semantics; S060 concerns server-context.cpp HTTP metadata. Neither covers this file or the initialization fit call. A new scoped row is needed; SOURCES.md was not edited.

## Exact source observations

All source locators below refer to `.ufo/waves/round-25/a2-build/out/SrcCommonInitFit/common.cpp`, freshly downloaded from the pinned raw URL.

- Lines 1240–1243: `common_init_result` constructs model and context parameter objects from the supplied `common_params`.
- Line 1245: the enclosing fit guard is `params.fit_params`.
- Lines 1249–1268: the guarded block prepares speculative draft parameters; MTP selects `LLAMA_CONTEXT_TYPE_MTP`; the extra-model descriptor marks model sharing when there is no separate draft.
- Lines 1270–1276: `common_fit_params` receives the model path, pointers to both parameter objects, tensor split, buffer overrides, target data, and minimum context. The extra-model pointer is supplied only for a draft or MTP. Its log level depends on whether verbosity reaches `LOG_LEVEL_DEBUG`; verbosity is not the fit-enable guard.
- Line 1279: the subsequent `llama_model_load_from_file` receives `mparams`, after the guarded fit block. Neither an unset context nor `model_only` is an additional guard on this visible fit block.
- Lines 1418–1419: `common_init_from_params` constructs `common_init_result(params, model_only)`, connecting the common wrapper to that constructor. Lines 1421–1425 inspect whether its model loaded.

## Draft registry row — eleven columns

ID intentionally remains S1xx; status stays queued and used-by stays empty until L1 actually cites/adopts it. Tier A is scoped to this pinned first-party code, not general runtime behavior.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp common initialization fit call @ 704366d76 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp | code | A | conditional fit invocation in common initialization at this commit; not fit defaults, sizing results, HTTP behavior, or observed server execution | common_init_result lines 1240–1280: fit guard 1245, common_fit_params call 1270–1276, model load 1279; common_init_from_params lines 1418–1425; raw sha256 d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 | The common wrapper constructs common_init_result; when params.fit_params is true, its constructor calls common_fit_params with model/context parameter pointers before loading the model. Draft or MTP enables the extra-model argument; verbosity selects the fit log level. | queued | 2026-10-22 | on-release | — |

## Gate record

- Source URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp
- Actually fetched URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp
- Access date: 2026-10-22.
- Located quote, line 1245: `if (params.fit_params) {` (3 whitespace-delimited words).
- Located quote, line 1270: `common_fit_params(params.model.path.c_str(), &mparams, &cparams,` (3 whitespace-delimited words).
- Located quote, line 1419: `common_init_result_ptr res(new common_init_result(params, model_only));` (4 whitespace-delimited words).
- Total quoted source text: 10 whitespace-delimited words, below the 25-word limit.
- SHA256: `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4`.
- Gate outcome: pinned source freshly opened, required ranges read, row drafted only. This is source evidence, not an observed C2 cell or a completed registry admission.

## Does not establish

- The default value of `fit_params` or how `--fit off` and environment inputs set it; that requires separately opened parameter definitions/parser source.
- The internals or success of fitting, any exact context size, whether an unset split context grows, available device memory, padding, or KV pool versus per-slot sizing.
- The server caller linking its load path to this common wrapper. That link requires separately opened server source; this file establishes the common wrapper-to-constructor connection only.
- HTTP field values, shared-pool concurrency behavior, endpoint health, or any K/X/L cell result.
- That a particular binary executes this path, that fitting changed its parameters, or that a live run succeeded.
- Applicability to another commit, engine, model, hardware configuration, speculative configuration, or registered consumer.

## Touched surfaces, gates not run, and scope

No product, registry, judge, Git index, or jj state was edited. No llama-server child was started; no endpoint or registered consumer was probed. No runtime, build, test, counter, mutation check, or source-snapshot comparison was run. Those remain unverified by this seat. No tool was installed or upgraded. No policy conflict was adjudicated.

Files written:

1. `/fast/scratch/hyaku/kama-r25a2/SrcCommonInitFit/common.cpp` — fresh download scratch copy.
2. `.ufo/waves/round-25/a2-build/out/SrcCommonInitFit/common.cpp` — preserved fresh source artifact.
3. `.ufo/waves/round-25/a2-build/advice/SrcCommonInitFit.md` — this report, draft row, and Gate record.
