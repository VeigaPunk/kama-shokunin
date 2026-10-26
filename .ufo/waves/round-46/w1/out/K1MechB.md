# K1MechB — C1 mechanical rows, second half (id ≥ S110)

**Verdict: PASS with one claim-prose defect — the 60 carry-forward rows for the mechanical population with id ≥ S110 are all `VALID` under the frozen C1 counter (exit 0); 13 rows re-read at b11906 across all 9 files, every `teaches` still true beyond the text; S126 named as the row whose identical blob hides an upstream truth-source change (mtmd capability caching), S112/S134 monitored, S113/S135/S132 checked-clear. Separately: the frozen gloss "71 rows' files are byte-identical b11889→b11906" is false — S479 (`tools/server/server-models.cpp`) changed by one comment line; the counter result and the 20-row reading list are nevertheless correct as frozen.**

## 1. Fragment built and scored

Population = the 91 registry rows of `registry/release-recheck-b11889.tsv`; rows with id ≥ S110: 75. Blob identity computed with `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-parse --verify -q <rev>:<path>` at b11889 = `d854d98b…` and b11906 = `4d71b42f…`:

- byte-identical with id ≥ S110: **60 rows** (my set) — S110–S113, S126–S132, S134–S135, S137, S140–S173, S180–S191;
- changed with id ≥ S110: 15 rows — S114–S125, S133, S138 (server-context.cpp, another seat) **plus S479 (server-models.cpp)** — see finding §4.

Carry-forward rows built exactly per `.ufo/waves/round-46/controls/build_controls.py` control 1: b11889 row kept (path, pin_commit, pin_blob, pin_lines, release_lines, verdict, note), `release=b11906`, `release_blob` re-derived, `changed = 0 if release_blob==pin_blob else 1`, `witness_pin=witness_new="-"`. Verdict composition: 57 `holds`, 3 `unchanged-file` (S128, S129, S131). No verdict/changed mismatches.

`python3 .ufo/waves/round-46/tools/check-fragment.py <out>/fragment.tsv <scratch>/chk` → **60 × `VALID`, exit 0** (receipt: `K1MechB/check-fragment.out`; identical result re-run from the out-dir copy).

## 2. Reading pass — 13 rows, all 9 files, `teaches` still true at b11906 beyond the text

Anchored text equality is machine-proven by the counter (§1); the following is the beyond-the-text check (hinges cited at b11906; raw excerpts in `K1MechB/evidence-ranges.txt`):

| row | file | beyond-text verdict |
|---|---|---|
| S110 | common/arg.cpp | TRUE — `-c 0` sets the fit-reduction sentinel `fit_params_min_ctx = UINT32_MAX` (1654-1657, comment "disable context reduction"); `--kv-unified-per-slot` promise (1661-1663); fit / fit-min have separate handlers (2889-2902, 2942-2948); consumers common.cpp/fit.cpp are themselves identical blobs. |
| S111 | common/common.cpp | TRUE — `common_init_result` ctor guards on `params.fit_params` (1260) and calls `common_fit_params` (1285-1291) with the draft/MTP extra (1273-1290) before `llama_model_load_from_file` (1294); fit.cpp identical. |
| S112 | tools/server/README.md | TRUE as scoped (a claim about the README's promises; blob identical) — option rows verified at 50, 165, 169, 177; `/props` bullets 1015-1016; the promised `/props` fields still exist in code (server-context.cpp:1711-1713, 5128-5133). Cross-file note: see §3. |
| S134 | tools/server/README.md | TRUE — `llamacpp:n_tokens_max` = "High watermark of the context size observed" (README 1237) matches code `metrics.n_tokens_max = std::max(...)` (server-context.cpp:5008), a context watermark, not a KV-pool metric; `/completion` 671/683 and `n_ctx_train` example 1393 unchanged; metrics code untouched by the 17 commits. |
| S113 | src/llama-kv-cache.cpp | TRUE — per-stream `v_cells[s].resize(kv_size)` (142-145), K/V 3-D tensors `(n_embd, kv_size, n_stream)` (233-234), size log prints kv_size as cells and n_seq_max/n_stream (301-304); caller (llama-context.cpp ctor) identical; hparams change additive only (§3). |
| S135 | src/llama-kv-cache.cpp | TRUE — same hinges; `get_size()` returns one stream's cells (1222-1226), so the size log's product framing claim holds. |
| S126 | tools/server/server-common.cpp | TRUE as a conditional — `if (!opt.allow_audio) throw "audio input is not supported…"` (1288-1289) — **but its upstream truth source moved across files; named row, see §3.** |
| S137 | tools/server/server-common.cpp | TRUE — fixed frame + request-chosen `response_format.type` echoed (1381-1393); fully request-derived, no cross-file dependency. |
| S180 | tools/server/server-common.cpp | TRUE — `throw "Cannot use both json_schema and grammar"` (1375-1379); self-contained. |
| S128 | ggml/src/gguf.cpp | TRUE (`unchanged-file`, pin blob = b11906 blob) — open failure logs path + `strerror(errno)` (1017-1022); gguf.h untouched by the 17 commits. |
| S130 | src/llama-context.cpp | TRUE — negative `-c` passes parsing (arg.cpp `-c` handler 1652-1658 has no lower bound) and graph reservation hits `GGML_ASSERT(n_outputs >= 1)` (2642). |
| S132 | src/llama-context.cpp | TRUE — `n_ctx == 0 → hparams.n_ctx_train` (225); pad/divide/round-down (387-403); n_ctx_seq comparison logs (419-427); `n_ctx_train` loading (llama-model.cpp) untouched. |
| S140 | tools/server/server-schema.cpp | TRUE — `field_num("sse_ping_interval").set_hard_limits(-1, INT32_MAX)` (42-43); the 400 rejection runs through the identical validator in server-common.cpp. |

## 3. Identical blob hiding a cross-file behaviour change — named rows

The 17 commits b11889→b11906 touch 65 files; the only server-side C++ changes are `tools/server/server-context.cpp` (mtmd capability refactor), `tools/server/server-models.cpp` (1 comment line) and `tools/mtmd/mtmd-helper.{h,cpp}` (new `mtmd_helper_get_capabilities`, old helpers deprecated — `K1MechB/server-diff-b11889-b11906.patch`).

- **Named: S126** (and by extension the sibling audio rows outside my half). At b11889 `allow_audio`/`can_chat` were computed per context (`mtmd_support_audio(mctx)`, `mtmd_helper_model_can_chat(ctx_tgt, mctx)`); at b11906 server-context.cpp caches `mtmd_helper_get_capabilities(model_tgt, mctx)` once at init (server-context.cpp:1401) and fills the aggregate `/* allow_audio */ mtmd_cap.audio` (1712) and `can_chat()` = `mtmd_cap.chat` (1025). The identical bytes of server-common.cpp hide that WHICH requests see `allow_audio == false` now depends on the new capabilities API (note the argument change: context → model). The taught conditional ("throws when audio is not allowed") still holds on this diff; the guard's truth source is the named hidden change.
- **Monitored: S112, S134** — the `/props` capability fields they document are now filled from the cached `mtmd_cap` (server-context.cpp:1711-1713) instead of live mtmd queries; field set unchanged, so the README-promise claims hold, but the values' computation moved files.
- **Checked-clear: S113, S135, S132** — `src/llama-hparams.h` changed, but only additively (`engram_pad_id` for deepseek41 Engram); no taught relation (n_ctx_train, n_seq_max, kv_size, n_stream) touched. S110/S111/S128/S130/S137/S140/S180 have no changed dependent surface in the 65-file diff.

## 4. Finding (defect in the frozen claim prose, machine result unaffected)

**Severity: medium (claim-prose accuracy); C1 counter unaffected.**

- Claim: "71 rows' files are byte-identical between b11889 and b11906; 20 rows need reading: S037 … S138."
- Fact: **S479** (`tools/server/server-models.cpp`, pin 704366d76) is in the mechanically-valid set but its file is **not** byte-identical: blob `e1e006f1…` at b11889 vs `57514013…` at b11906 — a 1-line comment change at line 536 (`// same rule as mtmd_helper_model_can_chat()` → `// same rule as mtmd_helper_get_capabilities()`). True split: 73 byte-identical / 18 changed (the 20-list = 17 changed + S037/S043/S108, which are byte-identical prior-`holds-reworded` rows that fail the witness rule on mechanical carry — per the frozen control `controls/junk-c1-carryforward.c1.out`: `pop=91 rows=91 valid=71 unverified=20 met=False`, listing exactly the 20 ids; S479 validated because its anchored ranges pin 2329,2378-2379 → release 2276,2325-2326 are text-equal at b11906 — verified directly).
- Show it: `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-parse d854d98b…:tools/server/server-models.cpp 4d71b42f…:tools/server/server-models.cpp` → two different blobs; `git -C … diff d854d98b… 4d71b42f… -- tools/server/server-models.cpp` → 1 insertion, 1 deletion (comment only).
- Impact: none on the frozen counter (`holds` requires range text-equality, which S479 satisfies) and none on the 20-row reading list (which the frozen control derives correctly); the defect is the "byte-identical" gloss, which misdescribes S479 and would mislead a reader into treating it as a zero-diff file.
- Proposed fix: wherever the split is described in prose, replace "71 rows' files are byte-identical" with "71 rows validate mechanically on carry-forward; 70 are byte-identical, S479's file changed by one comment line outside its anchored ranges (blobs e1e006f1… → 57514013…, ranges text-equal)". Optionally re-note S479's ledger row at integration time ("comment-only change at line 536, mtmd helper rename; anchored ranges untouched").

## 5. Residual risk and verification gaps

- I scored only my 60 rows (fragment checker scores per-row legs; section/newrow legs not scored here, per its docstring).
- S126's beyond-text truth is asserted from the diff + new API source reading (mtmd-helper.cpp:1027-1053), not from a live b11906 run; a behavioural A/B of the two capability computations was not in scope.
- The 47 unread mechanical rows (60 − 13) rely on the counter's text-equality plus the 65-file diff showing no dependent-surface change; I read the full changed-file list, not every diff hunk outside server/ + mtmd + hparams.

## 6. Commands and exit codes

- `python3 classify.py` → fragment built (exit 0).
- `python3 …/check-fragment.py fragment.tsv $S/chk` → 60 `VALID`, exit 0 (twice: scratch copy and out-dir copy).
- `git -C llama.git rev-parse/diff/log d854d98b… 4d71b42f…` → blob identities, 65-file name-status, 17-commit log (exit 0).
- No tools installed (operator 2026-10-19 authorization unused); no pacman; no lane/fleet mutations; fixture commits only inside the checker's own throwaway clone.

Scratch `/fast/scratch/hyaku/kama-r46/K1MechB` removed after copying receipts.

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/fragment.tsv
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/check-fragment.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/evidence-ranges.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/claims.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/mine-ids.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1MechB/server-diff-b11889-b11906.patch
