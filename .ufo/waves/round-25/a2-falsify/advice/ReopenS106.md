# ReopenS106 — falsification of SOURCES row S106

Verdict: defect found. The row's source identity holds (pinned URL, sha256, git blob, Gate quote, cited line numbers). The teaches cell is wrong in two places (the order of measurement, and the "user-set" rule, which fails for `-c 0`) and incomplete in one (a reduction path that lands directly on the floor). The entry relies on S106 for a default value and a condition it does not contain, and SKILL.md:687 relies on it for a per-slot clause it does not contain. No observed value is contradicted: the X1 capture (`-np 4 --no-kv-unified`, no `-c`) shows pool 8192 and 2048 per slot.

Scope: row S106 at corpus/SOURCES.md:118 and the Gate line at corpus/lessons/round-25.md:22. Lane tip read-only: fa3b62ae6475d111eb466d79af616aeebb08bbb9. Access date 2026-10-22. No llama-server started, no port opened, no commit, no git or jj write. No tool installed or upgraded. Per-check evidence with exit codes: `.ufo/waves/round-25/a2-falsify/out/ReopenS106/checks.md`.

## 1. Identity — holds
- Fresh fetch of the pinned raw URL: HTTP 200, 52,124 bytes, 1,113 lines. sha256 `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`. The row anchor (SOURCES.md:118) carries the same hash; grep finds it once.
- `git hash-object` gives blob `7a03008295089f1d9e1a2c2f9666199ead03da12`. GitHub's contents API at ref 704366d7… returns the same sha. The fetched bytes are the file at that commit.
- The row's blob URL returns HTTP 200; the commit lookup returns HTTP 200. The row URL and the Gate URL (round-25.md:22) are identical.

## 2. Gate quote — holds
- round-25.md:22 quotes: "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:". fit.cpp:270 has the same text (grep -F, one match). 18 words, limit 25. The row anchor quotes the same text.
- The quoted line is a comment. The code contradicts its ordering (section 4a).

## 3. Cited line numbers — hold, one label wrong
- 197: `const uint32_t n_streams = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);` — holds.
- 267-268: n_ctx_max and n_ctx_min_total, each `min(... , UINT32_MAX)` — holds. hp_nct is set at line 144 from `llama_model_n_ctx_train(model)`.
- 270: the quoted comment — holds.
- 272: `cparams->n_ctx = n_ctx_max;` inside `if (n_ctx_auto)` (271) — holds.
- 393-394: `if (n_ctx_auto) {` then `if (n_ctx_max > n_ctx_min_total) {` — holds, but both sit inside `if (global_surplus < 0) {` at line 384.
- 426-430: linear interpolation, `align = 256 * n_streams`, round down, floor at n_ctx_min_total — holds.
- 447-455: labelled "reduction branch". Wrong label. 447-448 (n_ctx_min == UINT32_MAX, no change), 450-451 (default at or below the minimum, no change), 454-455 (user-set, no change) are the no-change arms.

## 4. Teaches cell — defects
(a) "An unset context is resolved before measuring" is contradicted by the lines.
- fit.cpp:261 says step 1 measures "default parameters". fit.cpp:264 measures with cparams as passed, so an unset context (n_ctx 0) is measured first. Line 272 resolves it. Line 276 re-measures only when n_streams > 1 (line 273).
- The X1 raw log has the same order. The first `llama_context` construction (X1.server.log:281) reports n_ctx 2048 (line 283), which is the trained context that llama.cpp uses for n_ctx 0 (common.h:457). The next two constructions (lines 810 and 1342) report 8192 (lines 812 and 1344).
- [INFERENCE] The first construction is the line-264 probe. The log does not label it, but the count fits the code: there are three constructions, and the minimum-context probe at line 415 is gated off because 8192 is not above 16384 (4096 × 4).
- The upstream comment (line 270) says "resolve the context before measuring anything else". The code does not do that. The row should record observed order, not repeat the comment as behaviour.

(b) The reduction description is incomplete. "by linear interpolation rounded down … and floored" misses a path.
- When the target is at or below the projected use at the minimum context (the else of line 424), there is no interpolation. n_ctx was set to n_ctx_min_total at line 414 and stays there. Lines 441-444 only log. So reduction can land directly on the floor.
- The anchor cites none of lines 414, 424, 441-444. The wave-1 seat report (a2-build/advice/SrcFitCpp.md:40-43) has the same gap.

(c) The trigger is incomplete. "only … when n_ctx_max > n_ctx_min_total" is true as a necessary condition, but it omits the memory deficit at line 384, which encloses the whole block.

(d) "a user-set context is never changed here" holds for a nonzero `-c` only.
- The writes to cparams->n_ctx in fit.cpp are at 216 (copy into the extra draft model), 272, 414, 426 and 430. The main-model writes sit inside the auto branch.
- `-c 0` sets n_ctx to 0 (arg.cpp:1644-1645). That equals the unset default (common.h:457). fit.cpp:198 treats it as auto, line 272 raises it, and only the reduction is disabled (arg.cpp:1646-1649 sets fit_params_min_ctx to UINT32_MAX; fit.cpp:447-448 logs "user has requested full context size … -> no change"). So "user-set" must read "nonzero -c".

(e) Wording: "reduction to n_ctx_min_total" calls the floor a reduction target. n_ctx_min_total is the floor (lines 268 and 430).

Confirmed clauses: the n_ctx_max formula (267, with hp_nct from 144), n_streams (197), `cparams->n_ctx = n_ctx_max` (272), align 256 × n_streams (429), floor (430), and the auto-only writes.

## 5. How the entry uses S106 — defects
Entry: corpus/knowledge/context-capacity.md. S106 appears at lines 1, 74, 157 and 166. The row's used-by cell names this entry and the entry's source line names S106, so the link is two-way. Both show recheck on-release.

- Line 157 (medium defect): "its reduction needs a training context above --fit-ctx (4096 by default) or a cache that does not fit in memory (S106, fit.cpp 393-394)". The code needs both conditions: the deficit at line 384 and the gate at 393-394. "or" is wrong. The conclusion "fit never lowers a context here" still holds, because a single failed condition blocks reduction, but the stated rule is false. The deficit condition is line 384, which the citation omits. The 4096 default is at common.h:485 (sha256 8bcc5708…). No registered row cites common/common.h (grep: 0 rows). The mapping of `--fit-ctx` to n_ctx_min is at arg.cpp:2935-2938 and common.cpp:1274. None of those is S106.
- Line 166 (minor): "a floor of --fit-ctx per stream, S106 426-430". The floor is set at lines 268 and 430. The direct-floor path (414, 441-444) also lands on the floor and is not cited.
- Line 74 (minor): "sets the context to the training context times the number of streams". That is the pre-reduction value (line 272). Lines 414, 426 and 430 can lower it. Lines 155-166 qualify this later, but line 74 reads as the outcome. "one per slot" equates n_seq_max with the slot count. S106 does not establish that mapping; the fixture shows n_seq_max 4 and 4 slots (X1.server.log:282 and 1610).
- Lines 76-79 (minor): the log citations match: 283 (n_ctx 2048), 812 and 1344 (n_ctx 8192), 1610 (load_model), and 1612-1618 (slots at 2048). The phrase "the fit probe" is an inference; tag it [INFERENCE] or cite fit.cpp:264.
- SKILL.md:687 (low defect): "each slot gets the full training context (S106; X1: 8192 pool, 2048 per slot)". S106 has no per-slot division. fit.cpp uses n_seq_max only at line 197. The per-slot division is llama-context.cpp:382 (`cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;`, pinned file sha256 2a25e556…), which is S107's clause. That clause should cite S107.

## 6. Census and row shape — hold
- `sources-census.sh validate --root <fleet root> kama`: exit 0, 30 stdout lines (1 ok, 29 W04), stderr empty. S106 is not flagged. The new W04 lines for S108, S109, S110 and S112 match the lesson's note at round-25.md:36-38.
- The row has 12 pipes, the same as the header (11 cells).

## 7. Smallest correction (the L1 decides)
Channel. corpus/README.md:68-70: "Correct still-live source anchors through new cited correction entries; historical corpus samples stay immutable." S106 is already in the lane tip (fa3b62ae). [INFERENCE] I would not rewrite its teaches cell in place. Use an appended cited correction, as S096 and S105 do with "supersedes", and point the entry at it. The round-24 note at .ufo/waves/round-24/fixes/docs-contract.txt:17 says the same thing: an append correction, not a single successor.

Minimal text:
1. First clause becomes: "An unset context (n_ctx 0) is first measured as passed (fit.cpp:264); line 272 resolves it to n_ctx_max, and line 276 re-measures only when n_streams > 1."
2. Reduction clause becomes: "Reduction happens only when the memory target is missed (384) in auto mode with n_ctx_max > n_ctx_min_total (393-394): either linear interpolation rounded down to 256 × n_streams and floored at n_ctx_min_total (424-430), or, when even the minimum context misses the target, n_ctx stays at n_ctx_min_total (414, 441-444)."
3. "a user-set context is never changed here" becomes: "a nonzero -c value is never changed here; -c 0 is treated as unset (fit.cpp:198), raised at 272, and not reduced (arg.cpp:1646-1649; fit.cpp:447-448)."
4. Anchor: add 264, 384, 414, 424, 441-444; relabel 447-455 as "no-change arms".

Entry and SKILL:
- context-capacity.md:157 → "Fit reduces only when the memory target is missed (fit.cpp:384) and the training context is above the floor, --fit-ctx per stream (fit.cpp:268, 393-394). The default --fit-ctx, 4096, is common.h:485; register common/common.h or drop the number."
- context-capacity.md:166 → add "414, 441-444".
- context-capacity.md:77 → tag the probe [INFERENCE] or cite fit.cpp:264.
- SKILL.md:687 → cite S107 llama-context.cpp:382 for the per-slot clause.

The Gate quote stays valid (exact, line 270, 18 words), so no Gate edit is needed. The L1 may add a second located quote at line 264 if the new teaches cell is kept.

## 8. Residual risk and verification gaps
- The identity of X1 log line 281 as the line-264 probe is an ordering inference. The three-construction count fits the code, but no log line names the probe.
- The census checks row shape and cross-references, not teaches content. It passed.
- I did not run tools/sources-append-only.py. The L1 should run it to confirm an appended correction passes.
- The upstream comment at line 270 disagrees with line 264. I cannot tell whether the authors meant "before the measurement that matters". The row should record observed order only.
- I verified only the lines cited here in other rows: S107 (llama-context.cpp:382), S110 (arg.cpp:1646-1649), S111 (common.cpp:1245-1274). Those belong to their own reviewers.
- No live run was done. The X1 log is the existing lane capture.

## Files written
- .ufo/waves/round-25/a2-falsify/advice/ReopenS106.md (this report)
- .ufo/waves/round-25/a2-falsify/out/ReopenS106/checks.md (check log with exit codes)
- .ufo/waves/round-25/a2-falsify/out/ReopenS106/census-validate.out (copy of census stdout)
- Scratch only, /fast/scratch/hyaku/kama-r25a2w2/ReopenS106/: fit.cpp, api-contents-fit.json, arg.cpp, common.cpp, common.h, llama-context.cpp, census-validate.out, census-validate.err
