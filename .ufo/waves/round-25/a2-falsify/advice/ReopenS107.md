Verdict: defect found. The sha256, the release label, the Gate quote and every cited line range in the S107 anchor hold. The teaches cell states the line 219 rule as a general server rule, but on a default launch fit sets `n_ctx` before that line runs. The entry's YaRN range is off by one.

## Scope and snapshot

- Target: `corpus/SOURCES.md` row S107 (line 119), `corpus/lessons/round-25.md` Gate row S107 (line 23), and every S107 use in `corpus/knowledge/context-capacity.md`.
- Read-only. No llama-server started. No commit, push, index write, or jj command. Installed tools: none. Only read-only git: `git show` (3 files) and `git ls-remote`.
- The lane's working entry and lesson changed while I checked. Final-read snapshot of the working entry: sha256 `cea0f42211dcaf61c8e1aa6916b23c5cb5dd9484c07263811dda42c918e2694f`, 239 lines. Committed (fa3b62ae) entry: `0959b2342c74b23e46634f029d8e296f3ed29f80cdfe710cef43a5526f78b958`. Working lesson: `3fc874ba6bad4d6a9e9a0d6ebcf4ac2f86b750dcfcca2faa0bc1af90222363bb`; committed: `9d7ec2953b39469b7094ee830c429a5ac7c3a6add72625d77a2e856592476a16`. `SOURCES.md` is `45810d499dd65f2f5d1a76280c3cf7cd654a387d12ca97931a66e0df06e6a4a7` in both trees. The S107 Gate row text is the same in both lesson versions.
- Line numbers below are the working snapshot unless marked (committed).

## Fetch and provenance

- URL (pinned to 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, access date 2026-10-22): `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp`. `curl -fsSL` exit 0. 4719 lines. sha256 `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`.
- `sha256sum -c` against the string copied from SOURCES.md:119 gives `llama-context.cpp: OK`, exit 0.
- `git ls-remote https://github.com/ggml-org/llama.cpp refs/tags/b11755 'refs/tags/b11755^{}'` exit 0 gives `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad  refs/tags/b11755`. Lightweight tag, so the release label holds.
- Wave-1 seat `a2-build/advice/SrcLlamaContextPad.md` records the same sha256 and 4719 lines.

## Per-check verdicts

| # | Check | Verdict | Evidence (`llama-context.cpp` unless marked) |
|---|---|---|---|
| 1 | Fresh fetch of the pinned file | holds | curl exit 0; 4719 lines |
| 2 | Anchor sha256 equals fetched bytes | holds | `sha256sum -c` OK, exit 0; SOURCES.md:119 holds the same string |
| 3 | Release `b11755` is commit 704366d76 | holds | `git ls-remote` exit 0 |
| 4 | Anchor "GGML_PAD to 256 at 377" | holds | :377 `cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);` |
| 5 | Anchor "per-sequence division 380-383" | holds | :380 unified assign; :382 `n_ctx / n_seq_max`; :383 pad |
| 6 | Anchor "non-divisible reassign and warning 389-392" | holds | :389 `if`; :390 reassign; :391 `LLAMA_LOG_WARN`; :392 `}` |
| 7 | Anchor "n_ctx_seq vs n_ctx_train logs 409-417" | holds | :409-412 INFO block; :414-417 WARN block |
| 8 | Anchor "unset n_ctx default line 219" | holds as a line pointer; wording is F1 | :219 `... == 0 ? hparams.n_ctx_train : params.n_ctx;` |
| 9 | Anchor "llama_init_from_model lines 4114-4118 (YaRN)" | holds | :4114 `if`; :4115-4117 logs and assignment; :4118 `}`; function starts :4021 |
| 10 | Anchor "llama_context ctor lines 377-393" | holds | ctor starts :168; no column-0 `}` in 168-430 |
| 11 | Gate quote, line 391, at most 25 words | holds | :391 contains `n_ctx is not divisible by n_seq_max - rounding down to %u` (11 words); lesson row 23 identical in both trees |
| 12 | Teaches "padded up to a multiple of 256" | holds | :377, :383; ggml.h:267 `#define GGML_PAD(x, n) (((x) + (n) - 1) & ~((n) - 1))` |
| 13 | Teaches "split: per-slot n_ctx_seq is n_ctx / n_seq_max padded to 256" | holds | :381-383 |
| 14 | Teaches "reassigned to n_ctx_seq * n_seq_max, 'rounding down' log when they differ" | holds | :389-391 |
| 15 | Teaches "per-slot values below or above n_ctx_train only log, never clamp" | holds in this file | :409-417 log only; every assignment to `cparams.n_ctx` / `n_ctx_seq` in the file is at :219, :377, :380, :382, :383, :390 |
| 16 | Teaches "custom YaRN rewrites model n_ctx_train to n_ctx_orig_yarn / rope_freq_scale" | holds | :4116 `model->hparams.n_ctx_train = cparams.n_ctx_orig_yarn / cparams.rope_freq_scale;` |
| 17 | Teaches "An unset n_ctx resolves to n_ctx_train (line 219)" as a general rule | FAILS | F1 |
| 18 | Entry "reset to per-sequence times slots (S107, lines 377-392)" | holds | 377 pad; 379-393 split branch; 390 reset |
| 19 | Entry "unset context falls back to the training context and is split (S107, line 219)" | partly holds | fallback holds under fit off (219; `n_ctx` 0 from common.h:457 via common.cpp:1714); "is split" is at :381-393, not 219; F3 |
| 20 | Entry "re-adjusted at load (YaRN; S107 4113-4117)" | FAILS on range | content right, range wrong; F2 |
| 21 | Entry K6 arithmetic derived from S107 | holds | GGML_PAD(1000,256)=1024; 1024/3=341 -> 512; 512x3=1536 |
| 22 | Entry fit section, S106/S111 cites | holds for the lines checked | fit.cpp:197-198, 266-272; common.cpp:1245-1276, 1372 |
| 23 | Other registry uses of S107 | none found | only SOURCES.md:119, the entry and round-25.md:23; `SKILL.md`, `SCORECARD.md`, `tools/kama-context-capacity.py`, `count-c2.py`, `preregistration.json`, `errata-attempt-2.json` contain no literal `S107` |
| 24 | Gate provenance | holds | `a2-build/advice/SrcLlamaContextPad.md` records the same sha256 and line count |

## Findings, most severe first

### F1 (medium): the teaches cell states line 219 as a server rule, and fit overrides it on default launches

- Registry: SOURCES.md:119, teaches cell: "An unset n_ctx resolves to n_ctx_train (line 219), then ...". The anchor cell has "unset n_ctx default line 219". The row's scope cell (same line) says "how llama-server ... derives padded per-slot context" and "not common/fit.cpp behavior".
- Line 219 only maps `llama_context_params.n_ctx == 0` to `n_ctx_train`. On a default launch the context is not 0 when the constructor runs:
  - `common/common.h:457` `int32_t n_ctx = 0; // context size, 0 == context the model was trained with`
  - `common/common.h:483` `bool fit_params = true;  // whether to fit unset model/context parameters to free device memory`
  - `common/common.cpp:1714` `cparams.n_ctx = params.n_ctx;`; `:1243` creates `cparams`; `:1245` `if (params.fit_params) {`; `:1270` `common_fit_params(..., &cparams, ...)`; `:1372` `llama_init_from_model(model, cparams);`
  - `common/fit.cpp:197` `n_streams = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);`; `:198` `n_ctx_auto = cparams->n_ctx == 0;`; `:267` `n_ctx_max = min(hp_nct * n_streams, UINT32_MAX)`; `:270` comment "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:"; `:271-272` `if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;`
  - The `return` at `fit.cpp:207` is inside the lambda `add_extra_memory` (`fit.cpp:205`), so it does not end fit early.
- Effect: for `-np 4 --no-kv-unified` with no `-c` (X1), the constructor receives 8192. The teaches rule gives pool 2048 and 512 per slot, which is the round-20 value that the entry corrects. The entry's X1 row records pool 8192 and 2048 per slot (receipt raw log, not re-run here).
- The entry is already right: its fit section (working lines 75-84) says the zero case and fit-on order, and X3 says "With fit off". Only the registry row is wrong.
- Smallest correction:
  - SOURCES.md:119 teaches: replace "An unset n_ctx resolves to n_ctx_train (line 219)," with "An n_ctx of 0 in llama_context_params resolves to n_ctx_train (line 219); common fit, outside this row, sets n_ctx before this line on a default launch (S106 fit.cpp 267-272),".
  - SOURCES.md:119 anchor: "unset n_ctx default line 219" becomes "n_ctx == 0 default line 219".

### F2 (low): the entry's YaRN range is off by one

- context-capacity.md:218-219 (working; committed :167-168): "(YaRN; S107 / 4113-4117)".
- Correct range is 4114-4118. Line 4113 is blank, :4114 is the `if`, :4118 is the closing brace. The registry row (S107 anchor, 4114-4118) is right.
- Smallest correction: "S107 4114-4118".

### F3 (low): the X3 sentence cites line 219 for "is split"

- context-capacity.md:90-92 (working; committed :81-82): "With fit off the unset context falls back to the training context and is split (S107, line 219)."
- Line 219 supports the fallback only. The split is `llama-context.cpp:381-393` (the `else` branch). The fallback also depends on `common/common.h:457` (default 0), which no registry row covers.
- Smallest correction: "falls back to the training context (S107, line 219) and is split (S107, lines 381-393)". Either add a registry row for `common/common.h:457` or mark the "unset = 0" link [INFERENCE].

### F4 (low): "never clamp" is true of this file, but a row-only reader will overread it

- SOURCES.md:119 teaches: "per-slot values below or above n_ctx_train only log, never clamp". Verified for `llama-context.cpp` (check 15).
- The entry attributes the served per-slot cap to S060 ("capped by --kv-unified-per-slot and by the training context (S060)"). S060 is not checked here.
- Smallest correction: "this constructor only logs n_ctx_seq against n_ctx_train and never clamps it; the served per-slot cap is outside this file (S060)".

### F5 (note, no registry effect): stale line numbers in a wave-1 scout record

- `a2-build/out/ScoutR20Entry/evidence.md:119` gives "line 380" for the division and "381" for the pad. The same bytes (sha256 2a25e556...) have them at 382 and 383. Registry cells are right; this record is stale.

### Note (no action): YaRN field is written elsewhere too

- `llama-context.cpp:3753` writes `model->hparams.n_ctx_train` in the optimizer-init path. The teaches does not say "only", so nothing is wrong. Add "only" only if a later edit wants it.

## How the entry uses S107 (summary)

| use | working / committed lines | verdict |
|---|---|---|
| file header lists S107 | 1 / 1 | holds |
| per-slot reset, "(S107, lines 377-392)" | 59 / 54 | holds |
| X3 "falls back ... and is split (S107, line 219)" | 90-92 / 81-82 | partly (F3) |
| YaRN "S107 4113-4117" | 218-219 / 167-168 | range wrong (F2) |
| K6 arithmetic from S107 377-392 | 60-62 / 55-57 | holds |
| K5 warning text `n_ctx_seq (4096) > n_ctx_train (2048)` | not cited by line | holds (:414-416) |
| fit section cites S106/S111 | 75-84 | holds for lines checked; S108 "sizes the context before fit runs" not checked |

## Sources

All at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, accessed 2026-10-22, via `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`:
- `src/llama-context.cpp` line 219: `params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`
- `src/llama-context.cpp` line 391 (Gate): "n_ctx is not divisible by n_seq_max - rounding down to %u" (11 words)
- `common/fit.cpp` line 270: "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:" (18 words)
- `common/fit.cpp` line 272: `cparams->n_ctx = n_ctx_max;`
- `common/common.h` line 483: "whether to fit unset model/context parameters to free device memory" (10 words)
- `common/common.cpp` line 1372: `llama_context * lctx = llama_init_from_model(model, cparams);`
- `ggml/include/ggml.h` line 267: `#define GGML_PAD(x, n) (((x) + (n) - 1) & ~((n) - 1))`

Fetch sha256 (full values): llama-context.cpp `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`; ggml.h `475beaa7e959be8c383279d9ce9d5191f37426e6b338270cfb12b26a798129d3`; fit.cpp `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`; common.cpp `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4`; common.h `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9`. Same values in `out/ReopenS107/checks.md`.

## Residual risk and verification gaps

- The working entry and lesson moved during this review. The lane integrator should re-pin the S107 line numbers after the final edit.
- Not checked: S060 (served per-slot cap), S108 (`sizes the context before fit runs`, server.cpp 179-186), S110 (`-c 0` sentinel, arg.cpp 1646-1649), and every receipt value (X1 8192/2048, K5, K7). No server was started, per the lane bounds, so the observed values are unverified here.
- `hp_nct` equals `n_ctx_train`: read from the declaration comment at fit.cpp:192. The line that fills it was not located. [INFERENCE]
- The row cites the github.com blob URL. I fetched the raw URL at the same commit. Same commit, same bytes is standard git behavior. [INFERENCE] The sha256 agreement with the wave-1 fetch supports it.
- The default `n_ctx = 0` at common.h:457 is not in any registry row (F3).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReopenS107.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReopenS107/checks.md` (command outputs, hashes, line evidence)
- Scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReopenS107/` (pinned fetches of llama-context.cpp, ggml.h, common/fit.cpp, common/common.cpp, common/common.h; `committed_corpus_*.md` copies from `git show`; `entry-working-snapshot.md`)

Tools installed: none. Servers started: none. Exit codes: curl 0 (5 fetches), `sha256sum -c` 0, `git ls-remote` 0, `git show` 0 (3), `test -e` 0 (7).
