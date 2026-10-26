# U1DiffCtx: change map of tools/server/server-context.cpp, b11889 -> b11906

Verdict: ONE commit (c6fb3b5be) touches the file between b11889 (d854d98ba, 7070 lines, blob-file sha256 dff696ee...) and b11906 (4d71b42fd, 7073 lines, sha256 61c1afcf...); it makes 6 hunks, net +3 lines, none inside any pinned range of S042 S060 S109 S114-S125 S133 S138. Every cited range of the 17 rows is text-equal at b11906 after a uniform +3 shift; only one b11889 note claim (S125) is stale in wording.

Commands (read-only, bare clone /fast/scratch/hyaku/kama-r46/L1/llama.git; A=d854d98bae59 B=4d71b42fd871):
- `git log --format='%h %cI %s' A..B -- tools/server/server-context.cpp` -> exactly one line: `c6fb3b5be 2026-10-26T12:45:35+01:00 mtmd: add mtmd_helper_get_capabilities (#31183)` (author Xuan-Son Nguyen; `git rev-list --count A..B` = 17).
- `git diff -U0 A B -- tools/server/server-context.cpp | grep '^@@'` -> 6 hunks (below). Raw diffs saved: server-context.diff, server-models.diff, mtmd-helper.diff in this directory.

## Commit c6fb3b5be: what it changes
5 files: mtmd-cli.cpp, mtmd-helper.cpp/.h (new `struct mtmd_helper_cap {chat, vision, audio, video, audio_stream, text_gen, audio_gen, audio_gen_spk_ref}` and `mtmd_helper_get_capabilities(model, mctx)`; `mtmd_helper_model_can_chat` and `mtmd_helper_support_video` kept as DEPRECATED wrappers), server-models.cpp (comment only), server-context.cpp (below). Behavioural equivalence for the server: cap.chat = !audio_gen || chat_template != nullptr (same rule as old can_chat); cap.vision/audio/audio_stream = mtmd_support_*; cap.video = vision only under MTMD_VIDEO (same as old mtmd_helper_support_video); text-only (mctx == nullptr) -> chat true, everything else false (same as old `mctx ? ... : false`). The only semantic nuance: the values are now computed once at load (server-context.cpp 1401, after mctx is created) and cached in `mtmd_cap` instead of recomputed from mctx per call.
Topic classification: capabilities/modalities exposure (/props `modalities`, /v1/models `capabilities`, chat_params allow_image/audio/video). NOT health, loading, metrics, slots (error paths), props handler body, models handler body, router, shutdown. get_meta feeds /props and /v1/models, so the changes are in the *source* of those fields, not in handler bodies.

## Hunks (old = b11889 line numbers, new = b11906)
| # | old | new | net | symbol/context | change |
|---|-----|-----|-----|----------------|--------|
| H1 | 1014 (insert after) | 1015 | +1 | `server_context_impl` members, after `mtmd_context * mctx` | adds `mtmd_helper_cap mtmd_cap = {};` |
| H2 | 1020 | 1021 | 0 | `has_cap_tts()` | body `mctx != nullptr && mtmd_gen_audio_get_info(mctx).type != NONE` -> `mtmd_cap.audio_gen` |
| H3 | 1024 | 1025 | 0 | `has_cap_chat()` | body `mctx == nullptr \|\| mtmd_helper_model_can_chat(ctx_tgt, mctx)` -> `mtmd_cap.chat` |
| H4 | 1399 (insert after, in load_model, after the cache_reuse/mctx warning block, before the `llama_memory_can_shift` ctx_shift check) | 1401-1402 | +2 | load_model | adds blank + `mtmd_cap = mtmd_helper_get_capabilities(model_tgt, mctx);` |
| H5 | 1708-1710 | 1711-1713 | 0 | `chat_params` initialiser | allow_image/audio/video from `mctx ? mtmd_support_vision/audio/helper_support_video(mctx) : false` -> `mtmd_cap.vision/.audio/.video` |
| H6 | 5130 | 5133 | 0 | `server_context::get_meta()` | `has_audio_stream` from `impl->mctx != nullptr && mtmd_support_audio_stream(impl->mctx)` -> `impl->mtmd_cap.audio_stream` |

Cumulative shift for any old line L: L<=1014 +0; 1015..1398 +1; >=1399 +3 (H2,H3,H5,H6 are same-length replacements). Unchanged by this commit and visible in b11906: has_mtmd = `impl->mctx != nullptr` (old 5124 -> new 5127), has_inp_audio = chat_params.allow_audio (new 5129), slot_n_ctx = impl->n_ctx_slot() (old 5132 -> new 5135), pooling_type (old 5133 -> new 5136), /props n_ctx meta.slot_n_ctx (old 5554 -> new 5557), /v1/models n_ctx (old 5504 -> new 5507), transcription guard `!meta->has_mtmd || !meta->chat_params.allow_audio` (old 5972 -> new 5975).

## Row map (ranges are the b11889 `release_lines` of registry/release-recheck-b11889.tsv; `shift` = new b11906 range)
Method: a python script mapped each old range through the six hunks and compared a[old]==b[new] line-for-line; a second pass compared the 704366d76 pin_lines text against the mapped b11906 text. All "equal" results below are exact line equality (S121 pin differs in indentation only, see below).
| row | b11889 range(s) | b11906 range(s) | hunk touches? | text-equal at b11906 | notes |
|-----|-----------------|-----------------|---------------|----------------------|-------|
| S042 | 5171-5174, 5606-5617 | 5174-5177, 5609-5620 | shift only (+3) | yes; pin text also equal | /health get_health body unchanged; /health is not in the capability path |
| S060 | 4954-4963, 5501-5506, 5547-5563 | 4957-4966, 5504-5509, 5550-5566 | shift only (+3) | yes; pin text equal | note cites slot_n_ctx at 5132 -> now 5135 (get_meta hunk H6 is 2 lines above, line itself unchanged); props n_ctx 5554 -> 5557; get_props/get_models 5756-5766/6237-6247 -> +3 |
| S109 | 1887-1912, 3538-3563, 4589-4636 | 1890-1915, 3541-3566, 4592-4639 | shift only (+3) | yes; pin equal | decode/KV-full path untouched |
| S114 | 5684 | 5687 | shift only | yes | get_slots refusal |
| S115 | 5726 | 5729 | shift only | yes | post_slots refusal |
| S116 | 3233 | 3236 | shift only | yes | restore throw |
| S117 | 5771 | 5774 | shift only | yes | post_props refusal |
| S118 | 6733 | 6736 | shift only | yes | embeddings guard |
| S119 | 6738 | 6741 | shift only | yes | note cites llama_pooling_type at 5133 -> now 5136 |
| S120 | 6752 | 6755 | shift only | yes | |
| S121 | 6852 | 6855 | shift only | yes at b11889->b11906; pin line differs from release by leading whitespace only (b11889 already handled: moved into handle_rerank_impl) | a strict pin-vs-b11906 full-line comparison fails by indentation; counter must collapse whitespace as the b11889 holds row did |
| S122 | 5794 | 5797 | shift only | yes | |
| S123 | 3947-3953 | 3950-3956 | shift only | yes | note cites n_ubatch at release 3864 -> now 3867; can_split 494-522 -> 497-525 [INFERENCE: +3 shift, those two cited ranges not individually re-diffed] |
| S124 | 6595-6600 | 6598-6603 | shift only | yes | |
| S125 | 5969-5975 | 5972-5978 | shift only (anchored range untouched) | yes | STALE-WORDING: b11889 note says `chat_params.allow_audio is still mctx ? mtmd_support_audio(mctx) : false (release 1709)`. At b11906 line 1712 is `/* allow_audio */ mtmd_cap.audio,` (H5), computed by mtmd_helper_get_capabilities (cap.audio = mtmd_support_audio(mctx), false when mctx null). Same condition, new spelling; has_mtmd is still `impl->mctx != nullptr` (new 5127). Row still holds; a b11906 note must cite 1712/1401, not the old expression. |
| S133 | 1887-1911, 4593-4625, 4629-4634 | 1890-1914, 4596-4628, 4632-4637 | shift only | yes | |
| S138 | 1887-1912, 4593-4625, 4629-4634 | 1890-1915, 4596-4628, 4632-4637 | shift only | yes | |

Hunks that touch (overlap) a pinned or cited range: none of H1-H6. H6 (old 5130) is above every anchored range; the closest cited lines are S060 slot_n_ctx 5132 and S119 pooling 5133 (both note-level citations 2-3 lines below H6, unchanged lines). H5 (old 1708-1710) is the S125 note citation (old 1709) -> the only note whose quoted code changed.

## Findings (outside the C1 range arithmetic)
1. Brief says S037/S043/S108 sit in server-context.cpp/server-models.cpp; the b11889 TSV puts them in tools/server/server.cpp, and server.cpp is blob b6ebf7523364 at both b11889 and b11906 (`git rev-parse A:tools/server/server.cpp B:...` identical). They are byte-identical files; their b11889 verdicts (holds-reworded) carry to b11906 with release_lines unchanged and no new reading needed.
2. The only other changed file in the population is tools/server/server-models.cpp: S479 (ranges 2329,2378-2379 pin / 2276,2325-2326 at b11889). Its single hunk is old/new 536 (a comment `same rule as mtmd_helper_model_can_chat()` -> `mtmd_helper_get_capabilities()`), net 0 lines, so S479's ranges are unshifted and untouched. S479 is NOT in the brief's list of 20 rows to read but its file is not byte-identical; the real changed-file row set is the 17 server-context.cpp rows + S479 = 18. Whatever the C1 changed-flag says for S479 must be 1; check the census.
3. Other files the commit touches (mtmd-helper.cpp/h, mtmd-cli.cpp) are not in the population paths (`git diff --name-only A B` intersected with the TSV path set returns only server-context.cpp and server-models.cpp).
4. Semantic risk to watch for follow-ups (not a row claim): capabilities are now frozen at load into `mtmd_cap`; load_model teardown at old 1133 (`mctx = nullptr`) does not reset mtmd_cap [INFERENCE from grep: no assignment to mtmd_cap besides 1401]. Not relevant to any population row.
