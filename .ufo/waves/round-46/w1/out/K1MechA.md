# K1MechA — round 46, C1 mechanical rows first half (id < S110)

Verdict: **PASS — all 10 mechanical carry-forward rows (S001 S015 S035 S036 S047 S054 S056 S059 S106 S107) are `VALID` under the frozen C1 counter, and the hand read at b11906 finds no text-equal row whose meaning changed; no freshness defect in scope.** One pre-existing nuance (S001 id-default) and one cosmetic note-ref drift (+3 lines in server-context.cpp) recorded as observations, neither a b11906 meaning change.

## 1. Population derivation (ground truth from upstream git, not the assignment shorthand)

All 91 b11889 ledger rows re-derive from the bare clone (`pin_blob`, b11889 `release_blob`, `changed` all match; `derivation.out`): 0 failures.

Blob equality b11889 (d854d98b) vs b11906 (4d71b42f), per row via `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-parse <commit>:<path>`:

- file byte-identical b11889→b11906: **73 rows** (not 71)
- mechanically carryable (identical file AND b11889 verdict `holds`/`unchanged-file`): **70 rows**
- file changed b11889→b11906: **18 rows**: S042 S060 S109 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S133 S138 (all `tools/server/server-context.cpp`) + S479 (`tools/server/server-models.cpp`)
- the frozen 20-need-reading list = those 17 server-context rows + the 3 b11889 `holds-reworded` rows on server.cpp (S037 S043 S108) — server.cpp itself is byte-identical b11889→b11906 (blob b6ebf752 at both), but a `holds-reworded` carry-forward cannot supply the required witnesses mechanically, which is why they need reading.

So the assignment's "71 rows whose file blob is identical" is loose: 73 files are identical; **71 is the junk-c1-carryforward control's valid count = 70 carryable + S479** (whose carried release_lines 2276, 2325-2326 happen to remain text-equal at the same line numbers in the changed server-models.cpp — control receipt `junk-c1-carryforward.c1.out`: `valid=71 unverified=20`, the 20 detail lines exactly the 20-list). My set is the stable reading: **complement of the enumerated 20-list with id < S110 = 10 rows** (the 16 rows < S110 minus S037 S042 S043 S060 S108 S109).

## 2. Carry-forward fragment

Built per `build_controls.py`'s carryforward control: b11889 row kept verbatim, `release` → `b11906`, `release_blob` re-derived from `4d71b42f:<path>`, `changed` re-derived, **`release_lines` kept from b11889** (correct because the file is byte-identical, so the b11889 release ranges are still the b11906 ranges — resetting them to `pin_lines` would break the 7 `holds` rows whose text moved between pin and release), witnesses `-`, verdict and note carried.

Fragment: `.ufo/waves/round-46/w1/out/K1MechA/fragment.tsv` (exact 13-col C1 header, 10 rows: 7 `holds` changed=1, 3 `unchanged-file` changed=0).

## 3. Frozen-counter check

```
python3 .ufo/waves/round-46/tools/check-fragment.py <out>/K1MechA/fragment.tsv /fast/scratch/hyaku/kama-r46/K1MechA/chk
→ VALID S001 holds / VALID S015 unchanged-file / VALID S035 holds / VALID S036 holds /
  VALID S047 holds / VALID S054 holds / VALID S056 holds / VALID S059 unchanged-file /
  VALID S106 unchanged-file / VALID S107 holds   (exit 0; receipt fragment-check.out)
```

## 4. Hand read at b11906 (all 10 rows, 8 files) — is `teaches` still true beyond the text?

b11889→b11906 repo delta (65 files): the only files my rows' teaches depend on that changed are `tools/server/server-context.cpp` (+3 net lines after ~1400, mtmd-capability refactor into `mtmd_helper_get_capabilities`) and additively `src/llama-hparams.h` / `src/llama-model.h` (deepseek41 `engram_pad_id` / `engram_token_map` fields only — nothing fit.cpp or the llama-context ctor reads). All 10 anchor files are byte-identical b11889→b11906.

| id | file | teaches | b11906 beyond-text evidence | result |
|---|---|---|---|---|
| S001 | tools/server/README.md | `/health` load-state 503/200; id defaults to `-m` path unless `--alias`; `/metrics` only with `--metrics` | 503 body server-http.cpp 315-325 (file identical); 200 `res->ok({{"status","ok"}})` server-context.cpp 5618 (get_health 5609); `/metrics` guard 5624-5627 errors without `--metrics`; id default 1601-1611 | still true (see observation O1) |
| S015 | tools/quantize/README.md | two offline phases; `--allow-requantize` warns quality loss | README 12-14, 54 identical; quantize.cpp identical b11889→b11906, option live at 123/127-129 (WARNING "severely reduce quality") and parsed at 449-450 | still true |
| S035 | tools/server/README.md | 503 `Loading model` while loading, 200 `{"status":"ok"}` ready; line-1258 `meta: null` sentence contradicted by S036 in direct mode | 503 ✓ (server-http identical); 200 ✓ (SC 5618); README 1346 meta-null sentence identical; `get_res_model_info` 5489-5519 still always builds a populated `meta` object (no null path) — contradiction stands | still true |
| S036 | tools/server/server-http.cpp | every non-frontend path answers 503 before the API-key check while not ready | gate 309-327 (frontend exemption 310-312), state gate 355 before key check 358, OPTIONS bypass 348-354 — all in the identical file; server.cpp identical (b6ebf752 at b11906, routes unchanged); httplib.cpp unchanged (not in the 65-file delta) | still true |
| S047 | tools/server/server-queue.cpp | first SIGTERM lost between handler install and `start_loop`; later signal exits 1 | queue identical: `terminate()` 132-136, `if (!running)` 141-143, `start_loop` `running=true` 278-280; server.cpp identical: `signal_handler` 29-38 with `exit(1)` at 34, `shutdown_handler → ctx_server.terminate()` 645-649, install 651-653, `start_loop()` 671, `return 0` 684; `server_context::terminate` → `queue_tasks.terminate()` at server-context.cpp 5100-5101 (was 5097-5098, +3 shift, same semantics); a pre-loop terminate is undone by `running=true` at 279 | still true |
| S054 | common/arg.cpp | repeated flag warns + last value wins; unknown flag throws; `--host` clears | arg.cpp identical: throw 837-838/1230-1232, warning 840-845, `out_map[opt]=val` last-wins 1256, host clear 3346, port assign 3362; server.cpp identical (common_params_parse route) | still true |
| S056 | common/arg.cpp | `--port`/`--host` last-wins; `--api-key` appends; `--spec-type` appends without the warning | identical file: `--spec-type` skip 841/1234, api-key `push_back` 3546, spec-type `insert` 4329 | still true |
| S059 | gguf-py/gguf/gguf_reader.py | reference reader = independent real-file oracle; supported subset is an implementation property | reader identical: magic 142-143, byte-order swap 148-152, `READER_SUPPORTED_VERSIONS = [2, GGUF_VERSION]` at 41; constants.py unchanged b11889→b11906 (not in the delta) | still true |
| S106 | common/fit.cpp | unset ctx resolved before measuring; `n_ctx_max = min(n_ctx_train × n_streams, UINT32_MAX)`; auto-only reduction; align 256×n_streams; user-set untouched | fit.cpp identical: 197, 267-268, 270, 272, 393-394, 426-430, 447-455 all as taught; caller chain common.cpp identical (a4b4feae at b11906): fit guard 1260, `common_fit_params` call 1285; hparams delta additive only | still true |
| S107 | src/llama-context.cpp | unset n_ctx → n_ctx_train; pad 256; per-slot division; YaRN re-adjust | file identical b11889→b11906: 225 (`n_ctx == 0 ? hparams.n_ctx_train`), 387-403 (pad/divide/reassign+warn), 419-427 (log-only, no clamp), 4132-4136 (YaRN rewrite) | still true |

**No text-equal row whose meaning changed at b11906. No freshness defect found in scope.**

## Observations (not defects)

- **O1 (S001, pre-existing):** the b11889 note's "id default -m path" is a simplification. b11906 server-context.cpp 1601-1611: id = first `--alias`, else `params_base.model.get_name()` (= hf_repo → docker_repo → path, common/common.h:314-322), else `filename()` of the `-m` path — i.e. the basename, not the full path, and an hf/docker name precedes it. Identical code at the README pin (c0fd7862 1521-1529) and at b11889 (1598-1608), so the teaches' truth value is unchanged at b11906; recording it because the carried note overstates the default.
- **O2 (cosmetic, note-internal line refs):** the carried notes cite server-context.cpp lines that shifted +3 at b11906 (mtmd refactor): S001 get_health 5606-5615→5609-5618, /metrics 5621→5624, id default 1598-1606→1601-1611; S035 get_res_model_info 5486-5512→5489-5515; S047 terminate chain 5097-5098→5100-5101. Semantics unchanged; the counter does not check note line refs. If L1 re-reads these rows for the real ledger it may refresh the numbers.
- **O3 (assignment shorthand):** "71 rows' files are byte-identical" — actual: 73 identical files, 70 mechanically carryable, 71 = control's valid count (incl. S479). The enumerated 20-list is exact and was used as the split.

## Residual risk / verification gaps

- The beyond-text read covers every dependency file that changed b11889→b11906 for my 10 rows (server-context.cpp mtmd hunks touch none of their conditions; hparams/model.h deltas are additive engram fields). Files relied on as unchanged are proven by blob equality, not assumed.
- S037/S043/S108 (holds-reworded on an identical server.cpp) and the 17 changed server-context rows are other seats' 20-list items — not read here.
- Section/newrow/flags legs are out of scope for fragments (check-fragment.py does not score them).

## Receipts (all under `.ufo/waves/round-46/w1/out/K1MechA/`)

- `fragment.tsv` — the 10-row carry-forward fragment (13-col C1 header)
- `fragment-check.out` — frozen-counter output, 10× VALID, exit 0
- `derivation.out` — 91-row blob re-derivation, classification, 0 sanity failures
- `sources_rows_freeze.txt` — the 10 SOURCES.md rows at freeze 5790944 (teaches text)
- `server-context-b11889-b11906.diff` — the only dependency delta (+3 shift, mtmd refactor)
- `ranges/S*.txt` — b11906 anchor-range dumps for all 10 rows

Scratch `/fast/scratch/hyaku/kama-r46/K1MechA` removed after receipts were copied. No tool installs were needed (used system git/python3 only).
