Verdict: no sibling SOURCES.md overlaps kama's llama.cpp rows; kengaku alone holds committed 34113 bytes that kama's K05 entry should cite (not duplicate), refine (shared-pool concurrency), and exempt from any X1 supersession.

# ConnectorSiblingOverlap — round 25 attempt 2, C2 and frontier K05 (sibling overlap scan)

Seat: fresh attempt-2 identity. Read only across the 20 sibling lanes. No llama-server started, no endpoint contacted, no sibling written, no tool installed or upgraded.

## Evidence

Search commands (all exit 0):

- Per-lane file count, pattern `llama\.cpp|llama-server|kv[ -]cache|--fit\b|n_ctx|--parallel|n_parallel|ctx-size|kv_unified|kv-unified|n_seq_max`, whole lane trees excluding .git and .jj: kagi 13216 and kengaku 959 files (almost all under `.ufo/waves`), kotoba 12, mado 7, tsukuroi 6, others 1-2.
- Narrowed to corpus, knowledge, SOURCES.md, SKILL/PROVINCE/LOG/SCORECARD, tools, plans and reports: 125 files, 63 of them raw kengaku `corpus/evidence` captures.
- Every sibling `corpus/SOURCES.md` (20 files), pattern widened to `llama|ollama|vllm|gguf|kv.?cache|context window|context length|inference server|openai-compatible|lm studio`: two hits only, kotoba S021 (skills budget) and kotodama S020 (motif indexing), both unrelated. **No sibling source row overlaps kama.**

Load-bearing sibling observations (re-read this session):

1. `kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`. The 34113 production argv contains `--ctx-size 16384 ... --fit off --kv-unified ... --parallel 2`. No kama file records `--fit off` for 34113 (`rg 'fit off|--fit off' kama-shokunin/corpus SKILL.md PROVINCE.md SCORECARD.md`, no hits).
2. `r10-scout-endpoint.md:67` says "unified KV ⇒ each slot reports the **full** 16384, not 16384/2". Line 74 adds "unified KV (shared across the 2 slots ...), so a 2-slot server does **not** halve per-slots context."
3. `kengaku-shokunin/SKILL.md:494-495` says "`--kv-unified` with `--parallel 2` (each of 2 slots reports the full 16384 ctx; slot draws do not share a halved context)".
4. I re-parsed the committed raw captures with python3 (exit 0). `props.json` gives n_ctx 16384, total_slots 2 and build b1-d7bd3bf. `slots.json` gives n_ctx [16384, 16384]. `models-34113.json` gives meta n_ctx 16384 and n_ctx_train 262144.
5. `kengaku-shokunin/corpus/evidence/round11-fleet/r11-prior-art-prereg.md:193-194` quotes llama.cpp issue #28656: unified KV cache "is the default when `--parallel` is not given".
6. `kengaku-shokunin/SKILL.md:663` says 34113 is a "historical identity — endpoint refuses connections since 2026-10-15".
7. `kagi-shokunin/corpus/knowledge/op-cli-surface.md:91` says "llama.cpp `/health` → `{"status":"ok"}`; a foreign listener 404s or closes." `kagi-shokunin/SKILL.md:43` uses the same rule.

Kama-side lines touched by these overlaps:

- `kama-shokunin/SKILL.md:188-189` says "`[{"id":0,"n_ctx":16384,…},{"id":1,…}]` from `/slots` (matches `--parallel 2`, `--ctx-size 16384`)". The `--kv-unified` premise is missing.
- `kama-shokunin/corpus/knowledge/listener-census.md:270` records that the-tick consumer declares `parallelSlots 2 / contextTokens 16384` against the 34113 server.
- `kama-shokunin/corpus/knowledge/llamacpp-loading-lifecycle.md:9,30-36` shows a loading llama-server answers 503, with `/health` `{"status":"ok"}` only once ready.
- `kama-shokunin/corpus/knowledge/gguf-declared-identity.md:31` says "Do not divide `ctx` by `total_slots` blindly". This agrees with kengaku.
- Kama cites neither #28656 nor #7052. Its only `rg '28656|7052'` hits are byte counts.

Sources opened this round, access date 2026-10-22 (full record in `out/ConnectorSiblingOverlap/sources-opened.tsv`):

- https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp
  - Fetch: HTTP 200, 24572 bytes, sha256 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4.
  - Diff: `cmp` against the round-16 snapshot exited 0 (identical).
  - Line 170: "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true". This agrees with the #28656 wording kengaku quotes.
- https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp
  - Fetch: HTTP 200, 52124 bytes, sha256 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58.
  - Line 197 sets `n_streams` to 1 when `kv_unified`.
  - Line 198: "const bool n_ctx_auto = cparams->n_ctx == 0;".
  - Lines 271-274: the raise to `n_ctx_train * n_streams` happens only inside `if (n_ctx_auto)`.

The full lane → path:line → overlap-kind table (24 rows, including false positives and exclusions) is in `out/ConnectorSiblingOverlap/overlap-table.tsv`. Summary:

| lane | path:line | overlap kind |
|---|---|---|
| kengaku | corpus/evidence/round10-fleet/r10-scout-endpoint.md:33 | same fact; sibling holds the only committed argv bytes (includes `--fit off`) |
| kengaku | r10-scout-endpoint.md:67; props.json, slots.json, models-34113.json:1 | same fact (K3 shape, other build); cite as historical corroboration |
| kengaku | r10-scout-endpoint.md:74; SKILL.md:494-495 | partial statement: per-slot cap right, shared-pool concurrency limit absent; refinement, not contradiction |
| kengaku | corpus/lessons/round-8-aggregator-box3-coldrun.md:20-21 | duplicate of r10; cite r10 |
| kengaku | corpus/evidence/round12-fleet/r12-endpoint-freshness.md:82 | same declared-versus-served gap (n_ctx_train 262144 vs n_ctx 16384) |
| kengaku | corpus/evidence/round11-fleet/r11-prior-art-prereg.md:193-194, :334 | same claim, weaker source (issue text); cite pinned server.cpp:169-173 instead |
| kengaku | SKILL.md:451-458; corpus/knowledge/eval-prior-art-calibration.md:23,72-76 | adjacent (#7052 multi-slot nondeterminism); no conflict with status-graded L cells |
| kengaku | PROVINCE.md:44-47, :136 | ownership boundary: mechanism is kama's |
| kengaku | SKILL.md:663 | freshness caveat: 34113 historical |
| kama (own) | SKILL.md:188-189 | internal statement missing the `--kv-unified` premise |
| kama (own) | corpus/knowledge/listener-census.md:270 | second-order consumer exposure to the full-context concurrency limit |
| kagi | corpus/knowledge/op-cli-surface.md:91; SKILL.md:43 | conflicting health rule (loading server answers 503, misread as foreign) |
| kagi | credential-isolation.md:35, handler-trust-boundary.md:131, lessons/round-3.md:37, LOG.md:26, PROVINCE.md:42 | 8080/34113 drift already cited by kama cross-lane-scope.md |
| kumitate | PROVINCE.md:27 | boundary: serving → kama |
| kotoba | PROVINCE.md:34 | boundary: "kama (model serving) — no overlap observed" |
| kaidoku | EXAMPLE.kama.md:17,32,63 | ownership echo |
| kumitate, kengaku, kotodama, game-dev-3d | kimi-config-plane.md:129; local-model-index.md:19,39; availability.json:162; configline.md:88 | consumer- or catalog-declared context, other engine: exclude |
| audio, chousa, game-dev-3d, kotoba | static-proofs.py:134; research-gate.sh:1591; r95-boundary.md:323; claude-md-surface.md:29 | false positive |
| all 20 | */corpus/SOURCES.md | no source-row overlap |

Attempt-1 `build/out/ConnectorSiblingOverlap/overlap-scan.tsv` is unverified, so I re-checked it. 12 of its locators matched at the stated line. One was wrong: kotoba `PROVINCE.md:33` gave no match, and the boundary text is actually at line 34. Attempt 1 missed the `--fit off` token, the #28656 source-quality row, kama's own `SKILL.md:188-189`, and the kagi health conflict.

## Affected axes

- **Coverage** (C2 learning artifacts): kama's K05 entry `corpus/knowledge/context-capacity.md` gains one production-scale instance per finding without a new probe, and none of them touches a registered consumer.
- **Correctness of the supersession note**: this bounds the round-20 supersession so it does not reach sibling rows.
- **No numeric axis moves.** The C2 count stays the count-c2.py observed value.

## Proposed move (one, bounded)

The ScribeEntryDraft, ScribeSkillRows and ExecR20Supersede outputs should take one "production counterpart" paragraph that cites kengaku's committed bytes instead of restating them. It has three clauses:

1. **Pool versus slot.** Cite `r10-scout-endpoint.md:33,67` and `slots.json` as the production instance of the K3 shape. With `--kv-unified --parallel 2 --ctx-size 16384`, `/slots` and `/props` show 16384 per slot. That is the per-slot cap, not a private allocation. Kengaku's "does not halve" (`SKILL.md:494-495`, `r10:74`) is right about the cap but silent on concurrency: both slots draw on one 16384-cell pool. Kama's L1 result, whatever is observed, is the missing half. Route that half to kengaku as a report-out; no edit.
2. **Supersession scope.** If X1 shows fit raising an unset split context, that cannot reach any kengaku 34113 row, for three independent reasons in the committed argv:
   - `--ctx-size 16384` is explicit, so the fit-raise branch never runs (`fit.cpp:198`, `:271`).
   - `--fit off` is set.
   - `--kv-unified` sets `n_streams` to 1 (`fit.cpp:197`).

   The supersession note should say it applies only to round-20 `nctx-crosscheck.py`.
3. **Fix kama's own row.** `SKILL.md:188-189` gives "matches `--parallel 2`, `--ctx-size 16384`" as the reason. The correction is "matches `--ctx-size 16384` with `--kv-unified` (kengaku r10:33); a split cache would report a smaller per-slot value". The "smaller" part is [INFERENCE] from the source per-slot rule; it was not run at 16384.

For the shared-default claim, cite pinned `server.cpp:169-173` rather than kengaku's issue #28656 quote: the code is first-party and was opened this round.

## Contradictions stated, not smoothed

- **Kengaku "slot draws do not share a halved context" versus the shared pool.** Both are true at once. The per-slot cap is 16384, and the pool is also 16384 in total. This is a refinement only; kengaku already says "shared" at r10:74.
- **Kagi health rule versus kama loading lifecycle.** Kagi's rule classifies a still-loading llama-server, which answers 503, the same as a foreign listener. This is outside C2. It is a report-out candidate for the L1, not part of this move.

## Risks

- The kengaku captures come from build b1-d7bd3bf (a different llama.cpp build) and a different model. Citing them as more than historical corroboration of the rule would overclaim. Every citation must carry "historical, other build".
- The-tick consumer's declared 2 × 16384 against a 16384 unified pool is where the L1 concurrency limit would bite. [INFERENCE] Not observed; never probe 34113. This belongs to ScoutConsumerCtx.
- Citing kengaku paths couples kama's entry to a sibling's tree. Pin by path plus line, as kama `cross-lane-scope.md` already does.

## Verification (for the L1, not run by this seat)

- Run `rg -n -- '--fit off' kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md` from the fleet root. Expect line 33.
- Run `sed -n '197,198p;271,272p' common/fit.cpp` on the pinned fetch. Expect `n_streams` and `n_ctx_auto` at 197-198, and the `if (n_ctx_auto)` guard at 271.
- After landing, `rg -n 'kv-unified' SKILL.md` in the lane should show the premise near the `/slots` row.
- The C2 count stays `python3 .ufo/waves/round-25/count-c2.py`. This move does not change it.

## Files written

- `.ufo/waves/round-25/a2-build/advice/ConnectorSiblingOverlap.md` (this report)
- `.ufo/waves/round-25/a2-build/out/ConnectorSiblingOverlap/overlap-table.tsv`
- `.ufo/waves/round-25/a2-build/out/ConnectorSiblingOverlap/sources-opened.tsv`
- Scratch (not lane files): `/fast/scratch/hyaku/kama-r25a2/ConnectorSiblingOverlap/tools_server_server.cpp`, `/fast/scratch/hyaku/kama-r25a2/ConnectorSiblingOverlap/common_fit.cpp`

Report: .ufo/waves/round-25/a2-build/advice/ConnectorSiblingOverlap.md
