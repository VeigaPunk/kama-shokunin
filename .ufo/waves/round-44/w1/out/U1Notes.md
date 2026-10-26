# U1Notes - round 44 C1 reconnaissance (b11755 704366d76 -> b11889 d854d98ba)

Verdict: no held population row is made false by upstream code; one lane statement outside the population is (SKILL.md:1213-1216, dry_sequence_breakers), every server.cpp line anchor moved (f3269ef96), and the draft's S047 `holds` carries wrong release lines.

Deliverable: `.ufo/waves/round-44/w1/out/U1Notes/changes.md` (22-commit table with files, behaviour change, registry rows; flags F1-F5; line maps for S037/S043/S047/S108; unchanged-file list).

## Evidence
- `git -C /fast/scratch/hyaku/kama-r44/shared/llama.cpp log --oneline 704366d76..d854d98ba -- <assignment paths>`: 22 commits; whole range 134 commits (`log --oneline | wc -l` = 134).
- `git diff --stat` over the cited files: common/arg.cpp 50, common.cpp 95, llama-context.cpp 24, llama-kv-cache.cpp 11, tools/server 26 files (+2592/-753). fit.cpp, gguf.cpp, gguf_reader.py, quantize/README.md: no diff.
- Region-by-region `diff` of pin vs release slices (offsets from the draft ledger's release_lines) were identical for: decode retry path 4294-4341, try_clear_idle_slots 1810-1835, decode caller 3331-3356, slot_n_ctx 4654-4663, get_meta 5183-5188, props 5229-5245, get_health 5288-5299, ok() 4868-4871, get_models (sleep cache), slots/props/lora/infill/transcription/restore/embedding handlers (S114-S125), llama-context ctor/YaRN/n_outputs regions, kv-cache ctor/tensor/log/size regions, server-http.cpp gate, server-queue.cpp 1-449.
- server.cpp: read both files in full around the run flow; ordering (listener -> load_model -> is_ready -> signal install -> start_loop -> return 0) is identical, only moved into server_run_instance/server_run_router.
- Not run: nothing was launched or built; no live re-check of the S140-S173 clamp/reject teaches; ws upgrade gating not examined.

## Defects / flags (details and line maps in changes.md)
1. F1 `SKILL.md:1213-1216`: "dry_sequence_breakers ... no bounds message and no stored transform" is false at b11889 (63412d873: dedupe stored, >64 distinct entries -> `Error: dry_sequence_breakers must contain at most 64 distinct entries`). Proposed fix: scope the sentence to b11755 or add the b11889 behaviour.
2. F5 `.ufo/waves/round-44/c1/draft-ledger.tsv` row S047: path server-queue.cpp only; release_lines `530-535`, `576-578` are server-queue.cpp lines, not the server.cpp anchors (install 529-534 -> 324-325 called at 651; start_loop 575-576 -> 671; return 0 590 -> 684). Verdict holds, release_lines/note wrong. S043 has the same two-file shape (TODO in the draft). Reproduce: `cut -f1,2,8,9,10 draft-ledger.tsv | grep -P '^S047'`.
3. TODO rows by hand: S037 holds (431-523, 573-685), S043 holds, S108 holds (114-167), S015 and S059 unchanged-file (blob equal), S001 holds (/health 479-490 identical, /v1/models 1258 -> 1346).
4. F3 lane SKILL/knowledge citations of server.cpp lines are b11755-scoped and no longer resolve at b11889 (behaviour identical).
5. F2 lessons/round-26.md:69 rerank message candidates drifted (a5d22276b).

Tooling installed: none.

Written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U1Notes/changes.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U1Notes.md
