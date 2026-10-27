# kama — round 26 lesson (2026-10-23)

Claim C1 (depth): a new SKILL.md section, "## Round-26 live error signatures",
of llama-server b11755 error signatures, each reproduced live on the lane
fixture and tied to a pinned source line and a new SOURCES row. Frozen
predicate, controls and amendments A0/A1 (both before any data seat):
`.ufo/waves/round-26/preregistration.json`. Counter:
`.ufo/waves/round-26/count-c1.py`. Repair-first: the round-25 outside
spot-check's routed defects 1-7 (disposition below).

## Gate

Every row below was opened on 2026-10-23 from a fresh fetch at llama.cpp
commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; the fetched bytes equal the
lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/` (sha256 in each
SOURCES row's anchor cell; `fit.cpp`, `llama-kv-cache.cpp` and `README.md` for
S131, S134 and S135 were added to the snapshot after wave-2 seats ReopenS131
and ReopenS134 found them missing, with sha256 equal to the anchor cells; L1 fetch plus wave-1 scribes ScribeSourcesContext,
ScribeSourcesStartup, ScribeSourcesRequest, ScribeSupersedes and every
executor that cited a line). S114-S130 are new `mined` rows used by SKILL.md
and `registry/error-signatures-r26.json`. S131-S135 are KQ31 supersession rows
(teaches starts `supersedes S1NN —`) for S106, S107, S109, S112 and S113: S131,
S133 and S135 are routed by `round-25-verifier-spotcheck.md` defect 3; S132 and
S134 carry the lane-reported S107 and S112 corrections that the spot-check did
not verify; drafted by ScribeSupersedes
(`.ufo/waves/round-26/w1-build/out/ScribeSupersedes/`). Quotes are the source
line, cut to at most 25 words.

| id | URL | access date | located quote (≤25 words) |
|---|---|---|---|
| S114 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5366 | 2026-10-23 | line 5366: `` res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED)); `` |
| S115 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5408 | 2026-10-23 | line 5408: `` res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED)); `` |
| S116 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3084 | 2026-10-23 | line 3084: `throw std::runtime_error("No available space in KV cache or invalid slot save file");` |
| S117 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5453 | 2026-10-23 | line 5453: `` res->error(format_error_response("This server does not support changing global properties. Start it with `--props`", ERROR_TYPE_NOT_SUPPORTED)); `` |
| S118 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6132 | 2026-10-23 | line 6132: `` res->error(format_error_response("This server does not support embeddings. Start it with `--embeddings`", ERROR_TYPE_NOT_SUPPORTED)); `` |
| S119 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6137 | 2026-10-23 | line 6137: `res->error(format_error_response("Pooling type 'none' is not OAI compatible. Please use a different pooling type", ERROR_TYPE_INVALID_REQUEST));` |
| S120 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6151 | 2026-10-23 | line 6151: `res->error(format_error_response("\"input\" or \"content\" must be provided", ERROR_TYPE_INVALID_REQUEST));` |
| S121 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5803 | 2026-10-23 | line 5803: `` res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED)); `` |
| S122 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5476 | 2026-10-23 | line 5476: `res->error(format_error_response(string_format("Infill is not supported by this model: %s", err.c_str()), ERROR_TYPE_NOT_SUPPORTED));` |
| S123 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3657 | 2026-10-23 | line 3657: `"input (%d tokens) is too large to process. increase the physical batch "` |
| S124 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5998 | 2026-10-23 | line 5998: `res->error(format_error_response("Request body must be an array", ERROR_TYPE_INVALID_REQUEST));` |
| S125 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5655 | 2026-10-23 | line 5655: `res->error(format_error_response("The current model does not support audio input.", ERROR_TYPE_NOT_SUPPORTED));` |
| S126 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1272 | 2026-10-23 | line 1272: `throw std::runtime_error("audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj");` |
| S127 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1114 | 2026-10-23 | line 1114: `throw std::invalid_argument("\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string,` |
| S128 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L1021 | 2026-10-23 | line 1021: `GGML_LOG_ERROR("%s: failed to open GGUF file '%s' (%s)\n", __func__, fname, strerror(errno));` |
| S129 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L482 | 2026-10-23 | line 482: `GGML_LOG_ERROR("%s: invalid magic characters: '%c%c%c%c', expected 'GGUF'\n", __func__, c0, c1, c2, c3);` |
| S130 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L2624 | 2026-10-23 | line 2624: `GGML_ASSERT(n_outputs >= 1);` |
| S131 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp#L264 | 2026-10-23 | line 264: `dmds_t dmds_full = common_get_device_memory_data_impl(path_model, mparams, cparams, devs, hp_ngl, hp_nct, hp_nex, log_level);` |
| S132 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L219 | 2026-10-23 | line 219: `params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;` |
| S133 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L1813 | 2026-10-23 | line 1813: `if (!params_base.kv_unified) {` |
| S134 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md#L165 | 2026-10-23 | line 165: “when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N” |
| S135 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp#L301 | 2026-10-23 | line 301: `(%6u cells, %3d layers, %2u/%u seqs)` |

Old-row changes: none. S106, S107, S109, S112 and S113 keep every cell; their
corrections are the new rows S131-S135 (KQ31). No status, recheck or used-by
cell of an existing row changed.

Rejected candidates (observed, not registered; kept here as the discernment
record):

| candidate | reason |
|---|---|
| `This server does not support metrics endpoint...` (server-context.cpp:5304) | held in base-tree wave evidence (`.ufo/waves/round-16/falsify/advice/ScoutMetricsSource.md` and two round-18 advice files); clause (b) checks only SKILL.md and corpus/, so the counter would accept it, but it is not new knowledge (critic CriticAxisFit caveat) |
| `exceeds the available context size (` (server-context.cpp:3678) | held in 13 round-25 wave files |
| `couldn't bind HTTP server socket, hostname` (server-http.cpp:517) | held in `.ufo/waves/round-18/build/advice/ScoutLlamaArgParse.md` |
| `error: invalid argument: ` (arg.cpp:830) | held in round-18 advice files |
| `"authentication_error"` and `invalid_request_error` | error-type labels shared by many faults, not signatures; the 401 envelope is also held in round-16 advice and is kagi's scope |
| ten further per-flag argument messages (`--parallel 0`, `--flash-attn bogus`, `--repeat-penalty 0`, ...) | one validation pattern per flag; they add no decision value beyond one example, and the counter can evaluate at most 19 runnable rows (ReviewerCounterCode F4) |
| `"input" must not be empty`, `Input content cannot be empty`, `"documents" must be a non-empty string array`, `"prompt" must not be empty`, `missing completion id`, `unknown control action`, `This model is not a decision model`, encoding-format and missing-query messages | genuine and live-confirmed by wave-1 seats, held back by the 19-row evaluation limit; two ports kept spare. Candidates for a later round |
| 17 chat-completions request-validation messages (server-common.cpp lines 1302-1521; ExecChatFormat, `.ufo/waves/round-26/w1-build/out/ExecChatFormat/`) | live-confirmed twice each and counted 17 of 17 in the seat's scratch run, but returned after integration; held back by the same 19-row limit. Candidates for a later round |
| router-only model errors (server-models.cpp) | unreachable: the counter always passes `-m`, which forces single-model mode (ExecRouterModels) |

## Mistakes

| Class | Evidence | Captured-by | Fix / demonstrated boundary |
|---|---|---|---|
| false timestamp repeated a third time: the L1 wrote clock guesses into a preregistration | `.ufo/waves/round-26/preregistration.json` at a4a159c3 (`frozen_at_utc` 03:45Z, commit 03:18:51Z) and a12850c5 (A0 03:55Z, commit 03:19:43Z); corrected at f071209a; same class as `round-25.md` §Mistakes row 6 | none mechanical: round 25 named the class but added no check, so it recurred (L1 self-review found it two minutes later) | `tools/prereg-time-check.py` (wave-1 seat ExecPreregTimeCheck): exit 1 when a JSON at a revision holds a UTC time later than that revision's commit time (24 h horizon; `--strict` for any later time). Shown able to fail: exit 1 at a4a159c3 and a12850c5, exit 0 at f071209a and a23c0e04; it also flags the original round-25 preregistration (+76 s) and amendment 1 (+16 s), which `round-25.md` row 6 said amendment 1 had corrected (`.ufo/waves/round-26/w1-build/out/ExecPreregTimeCheck/RUNS.txt`). Limit (wave-2 ReviewerLessonMistakes): it reads only `YYYY-MM-DDTHH:MM[:SS]Z` spellings and passes the same wrong time written with an offset, fractional seconds, a space, lowercase `z`, `UTC` or epoch seconds; no gate runs it yet |
| counter met by a control before data | control seat KamaR26CtlAllFalse scored 12 of 14 with CLI help text printed after an invalid option (`controls/KamaR26CtlAllFalse/REPORT.md`), under the A0 counter | the phase-4 pre-freeze control wave rule; this is the case it exists for | A1 (clause f also excludes `--help`/`--version` text) before any data seat; the same patch scores 0 of 14 under A1 (`controls/A1-rescore/invalid-flag-usage-A1.out`) |
| data dispatched with the shortcut-control slot unfilled; the counter is met by a shortcut found after data | pre-freeze item KamaR26CtlShortcut was refused by the provider (cyber_policy) and KamaR26CtlCounterMutants too; the L1 ran do-nothing, junk, generic and no-reader controls itself but no echo shortcut, and dispatched wave 1. After data, wave-2 critic CriticShortcutRows met the frozen counter from the base tree with no error knowledge: `registered 12 counted 12 target 12 met True` (`.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/`), by hiding a source literal from `e_not_echoed` with a `\u00XX` escape and letting `server-common.cpp:1375` echo it into a 400 (counter limit F2) | the phase-4 rule "score the cheapest shortcut ... and commit that receipt before data"; the L1 treated a refused control item as covered by its own partial controls | C1's frozen counter does not by itself establish the claim; the 17 landed rows rest on the per-row wave-2 attacks (each re-run live; CriticShortcutRows found none of them of a shortcut type). Fix for the next round: the preregistration lists one committed receipt per required control class (do-nothing, junk, all-false, no-reader, shortcut on ids/labels and on echo); a class without a receipt blocks the data wave, and when a control seat dies or is refused the L1 builds that control itself before data. Shown able to fail: this round's preregistration has no shortcut receipt, and the post-data shortcut meets the counter |
| counter weaknesses found after data, so not repairable this round | ReviewerCounterCode (`.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/findings.md`), fourteen findings: F1 warning lines on an unrelated startup failure count; F2 request echo through JSON unicode escapes; F3 echo through argument file contents; F4 more than 19 runnable rows exhaust the 20-port range and the run cannot evaluate; F5 one bad row aborts the whole count; F6 the forbidden-argument list can be bypassed; F7 the server pin covers the 17,864-byte launcher, not `libllama-server-impl.so` where the server code lives (its sha256 is recorded in the SKILL section header, unchanged); F8 results depend on the caller's environment (`LLAMA_ARG_*`, proxies); F9 clause (g) is greedy, so the result depends on registry order; F10-F14 lower severity | the pre-freeze control wave did not cover them: its shortcut and counter-mutant items were refused by the provider (cyber_policy) and three critic seats died on quota | not fixed: a rule changed after data is not the claim's rule. The registered rows avoid F1-F3 (no warning-only startup row; no row whose output echoes a request field; the only path arguments are `-m` to a missing or junk file and `--slot-save-path /tmp`, whose contents never reach the output), stay at 17 rows (F4), and each was re-run by a wave-2 attack seat. Wave-2 attackers also found that five rows are one mechanism (unset flag, 501 at handler entry: E26-01, 02, 04, 05, 08) and that E26-12 and E26-13 share one condition; the frozen predicate counts them separately. A next counter should add a per-row healthy control with the same argv, decoded-request and file-content echo checks, port reuse, a pin on the server library and a cleared environment |
| late-seat writes and an early seat-gate release (round 25) | `round-25-verifier-spotcheck.md:49-78` | the round-25 outside spot-check | this round: 42 paths committed at a4a159c3 (defect 1); each wave's reservation is released only after every seat of that wave returned (defect 7; the release lines are in the round report) |
| false "before" statement in the round's own self-assessment | the first landed SCORECARD round-26 section and LOG entry (7f84cd0e) said SKILL.md held no live b11755 error signature; base SKILL.md:521-523 (`Loading model` 503) and :689 (round-25 `Context size has been exceeded.`) are live b11755 signatures | wave-2 seat ReviewerScorecardLogTruth (the calibration check this round ran on its own sections) | corrected in place before the report, with a note in the SCORECARD row; the falsify wave carries one calibration-check item per round |
| misroot: seat reports first written at the fleet root | wave-2 seats AttackE2616, AttackE2606, ReopenS131 and ReopenS132 wrote their report by a lane-relative path into `/home/vgpnk/Projects/shokunin/.ufo/waves/round-26/` and moved it into the lane themselves (each report says so; ScoutMisroot saw one copy appear and disappear) | the wave-context rule that every `Report:` path is relative to the lane; it was stated and still missed | the L1's misroot sweep before the report (round report §Work performed) finds no remaining copy; next wave contexts should give each seat its absolute report path |

## Routed defects from the round-25 spot-check

1. 42 uncommitted `a2-falsify/` entries (220 added, 2 modified, 1 deleted
   files): committed at a4a159c3 as late round-25 seat outputs (the deleted
   receipt copy stays deleted; it duplicated the committed receipt). One
   1.4 MB log over the 1 MiB new-file limit was skipped by that directory
   commit and committed by name at 7e5ff9b5.
2. KQ36 "landed tip" qualification appended to `QUALITY.md`; erratum appended
   to `round-25.md` (§Mistakes row 2: the SKILL row does not say M17 survives).
3. Supersedes rows S131-S135 (above).
4. `context-capacity.md` errata appended (lines 55-56 and 137).
5. `.ufo/waves/round-25/count-c2.py` now binds every receipt raw sha256 to its
   own file in `final/raw/` (ExecC2RawBinding patch). At the round-26 landed
   tip it still prints `registered 14 observed 14 bound True missing []`; the
   unpatched counter accepted all five receipt mutants of MutationC2Receipts.
   Limit (wave-2 ReviewerLessonMistakes): the binding checks only hashes; the
   cell values are still read from the receipt, so a receipt that changes a
   value (for example K5's pool) but keeps the raw hashes still binds. Open.
6. SCORECARD round-26 section appends the trend correction.
7. Seat-gate reservations: released per wave only after every seat of that
   wave returned (control wave, wave 1 and wave 2; the `released` lines are
   quoted in the round report). A wave-1 seat (ExecRequestParams) returned
   after integration had started; its candidates were not registered.
8. Lowest axis: C1 works depth (7), not calibration (the rejected streak).

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `fd48f9a3b7ca` (round-26: falsify-wave corrections (SKILL row prose and header, lesson Gate and Mistakes incl. post-data shortcut break, SCORECARD/LOG calibration fixes, no depth promotion), snapshot files fit.cpp/llama-kv-cache.cpp/README.md, wave-2 evidence):

`````text
row's anchor cell; L1 fetch plus wave-1 scribes ScribeSourcesContext,
(teaches starts `supersedes S1NN —`) for S106, S107, S109, S112 and S113, routed
by `round-25-verifier-spotcheck.md` defect 3; drafted by ScribeSupersedes
| S114 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5366 | 2026-10-23 | line 5366: `res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));` |
| S115 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5408 | 2026-10-23 | line 5408: `res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));` |
| S117 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5453 | 2026-10-23 | line 5453: `res->error(format_error_response("This server does not support changing global properties. Start it with `--props`", ERROR_TYPE_NOT_SUPPORTED));` |
| S118 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6132 | 2026-10-23 | line 6132: `res->error(format_error_response("This server does not support embeddings. Start it with `--embeddings`", ERROR_TYPE_NOT_SUPPORTED));` |
| S121 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5803 | 2026-10-23 | line 5803: `res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));` |
| S127 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1114 | 2026-10-23 | line 1114: `throw std::invalid_argument("\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings &` |
| S132 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L219 | 2026-10-23 | line 219: `params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx;` |
| nine further per-flag argument messages (`--parallel 0`, `--flash-attn bogus`, `--repeat-penalty 0`, ...) | one validation pattern per flag; they add no decision value beyond one example, and the counter can evaluate at most 19 runnable rows (ReviewerCounterCode F4) |
| false timestamp repeated a third time: the L1 wrote clock guesses into a preregistration | `.ufo/waves/round-26/preregistration.json` at a4a159c3 (`frozen_at_utc` 03:45Z, commit 03:18:51Z) and a12850c5 (A0 03:55Z, commit 03:19:43Z); corrected at f071209a; same class as `round-25.md` §Mistakes row 7 | none mechanical: round 25 named the class but added no check, so it recurred (L1 self-review found it two minutes later) | `tools/prereg-time-check.py` (wave-1 seat ExecPreregTimeCheck): exit 1 when a JSON at a revision holds a UTC time later than that revision's commit time (24 h horizon; `--strict` for any later time). Shown able to fail: exit 1 at a4a159c3 and a12850c5, exit 0 at f071209a and a23c0e04; it also flags the original round-25 preregistration (+76 s) and amendment 1 (+16 s), which `round-25.md` row 7 said amendment 1 had corrected (`.ufo/waves/round-26/w1-build/out/ExecPreregTimeCheck/RUNS.txt`) |
| counter weaknesses found after data, so not repairable this round | ReviewerCounterCode (`.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/findings.md`): F1 warning lines on an unrelated startup failure count; F2 request echo through JSON unicode escapes; F3 echo through argument file contents; F4 more than 19 runnable rows exhaust the 20-port range and the run cannot evaluate | the pre-freeze control wave did not cover them: its shortcut and counter-mutant items were refused by the provider (cyber_policy) and three critic seats died on quota | not fixed: a rule changed after data is not the claim's rule. The registered rows avoid each path (no warning-only startup row, no echoed field, no file argument, 17 rows); wave 2 attacks each row for these paths. A next counter should add a per-row healthy control with the same argv, decoded-request echo checks, file-content echo checks and port reuse |
1. 42 uncommitted `a2-falsify/` paths: committed at a4a159c3 as late
   round-25 seat outputs (the deleted receipt copy stays deleted; it duplicated
   the committed receipt).
7. Seat-gate reservations: released per wave only after the wave settled.
`````
