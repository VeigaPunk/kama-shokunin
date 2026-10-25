# kama round 42 lesson

author: kama L1
date: 2026-10-25
base: 0b606b03bf0b2a87b791aa537f6c72c941624cf0
freeze: 0bfd47abdda1f5ac21a0834654122644fc23e861

## Claims

C1 calibration 7 → 7 — the SCORECARD head and the files that describe the lane (README, PROVINCE) are the lane's standing self-description. Round 41 reconciled only the `## Axes` table; seat R41A10 itemised what the tree contradicts around it. `tools/round42-selfdesc-reconcile.py` reads `mismatches=40 met=False` at base `0b606b03` (`.ufo/waves/round-42/controls/base.c1.out`).

C2 operability 8 → 8, capability acquisition `digest-ledger` — mines `considerthese/2026-10-25.md` proposal 1 ("Recompute every digest and S-id that a new lesson or row cites"). `tools/digest-ledger.py` finds every full SHA-256 the lane's documents cite and classifies it against the blobs reachable from a revision and `registry/digest-ledger.tsv`. At base the documents cite 94 distinct digests and 10 are unexplained: 9 unknown and 1 `wrong_unflagged` (the round-38 S472 digest, first eight characters equal to the real one). The claim also repairs the routed round-41 counter-hygiene defect (R41A10-10): both round-41 counters leaked a ~253 MB export per run.

C3 coverage 9 → 9, assimilation from the staged `merge/kama` package — the engine-side half of K05 (declared versus served context capacity): `corpus/knowledge/context-capacity-engine-sides.md`, sourced on S478 and S479, both opened 2026-10-25. This is the round's sourced claim.

## Gate

New registry rows (CORPUS.md rule 1), each opened 2026-10-25 by the kama L1 (fetch time 2026-10-25T21:06:04Z, `.ufo/waves/round-42/c3/fetch-time.txt`):

- **S478** — https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py, accessed 2026-10-25 (curl, 111612 bytes, SHA-256 `af4164bca819f1cdc416077522a7019936fd38a523a482283eb91b08dae0e57a`, copy `.ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py`). Located quote, line 1627: "num_blocks = available_memory // bytes_per_block" (6 words). Also read, not quoted: line 2308 `return int(max_concurrency * max_model_len), max_concurrency` and the log literal at line 2328. Admit: grounds the vLLM half of the entry.
- **S479** — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp, accessed 2026-10-25 (curl, 117111 bytes, SHA-256 `9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a`, copy `.ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp`; the digest equals the one the campaign recorded, which proves nothing about this lane and was re-measured here). Located quote, line 2378: "if (meta.n_ctx_train > 0) {" (6 words), followed on line 2379 by `model_info["context_length"] = meta.n_ctx_train;`; handler `get_router_models` at line 2329; `grep -o max_model_len <copy> | wc -l` → 0. Admit: grounds the llama.cpp half of the entry, scoped to the router listing handler.

No existing row's `status`, `recheck` or `used-by` changed in this round.

### Assimilation set (staged `merge/kama`, theme context-capacity) — admit and reject for the closure's spot-check

Theme chosen: `context-capacity` (four staged amendments: round 5, round 7, round 8, round 11). It matches the lane's K05 frontier (`corpus/README.md` §Frontier) and PROVINCE "served-model-id reconciliation" and "liveness/readiness probe conventions" ground. Source repo read-only: nothing was written into `/home/vgpnk/Projects/shokuknow` and no campaign tool was run.

| staged entry | decision | reason | flip condition |
|---|---|---|---|
| `context-capacity-amendment-2026-10-23-r5.md` (S378) | **admit**, re-grounded and merged into one entry | the vLLM source is real and uncovered (`grep -rn kv_cache_size_tokens corpus SKILL.md` empty at base); the staged prose simplified the token figure and was corrected from the file (derived from `max_model_len`, not read off the block count) | — |
| `context-capacity-amendment-2026-10-24-r7.md` (S394) | **admit**, re-grounded and merged into the same entry | the `context_length` literal exists at line 2379; the staged prose called the handler an "OAI-compat card" and corrected a round-6 amendment this lane never held; the entry scopes it to `get_router_models` and does not mention the unheld round-6 text | — |
| `context-capacity-amendment-2026-10-24-r8.md` (S401, S405) | **reject** this round | S401 is llama-cpp-python settings, an engine outside the two this entry reads, and no frozen claim consumes it; one theme and one entry this round | adopt when a claim-bound round opens the llama-cpp-python settings surface; then re-open S401 and S405 |
| `context-capacity-amendment-2026-10-24-r11.md` (S424) | **reject** this round | S424 is an own-work receipt path in another repository's lane tree (`lanes/kama/round11/evidence/…`); the receipt is not in this lane or in the package bytes this round read, so its located quote cannot be re-found | adopt when the receipt bytes are in the lane or the package and the quote is located |

Id collision check (scratch, committed): `.ufo/waves/round-42/assimilation/{reg-ids,staged-ids,collisions}`. Lane registry ids 218, staged ids 142, collisions 9 (S330, S333, S334, S335, S346, S347, S352, S353, S363), none of them adopted. Guard proof: a scratch registry with an indented `  | S378 |` row gives collision S378 with the 0–3-space pattern and nothing with the column-zero-only pattern (`assimilation/guard/`). Renumber map, by document: staged S378 (vLLM kv_cache_utils.py @ v0.32.0) → S478; staged S394 (llama.cpp server-models.cpp @ 704366d7) → S479. Transformation: the two rows were rewritten to the 11-column fleet schema with no `|` in any cell, recheck `on-release`, status `mined`, `used-by` listing exactly the entry and this lesson; the staged `recheck` prose (`90d — re-run …`) and `verified-at` text are not carried. Mirror validation before the append (`assimilation/validate-census.out`): `sources-census.sh validate --file <mirror>/corpus/SOURCES.md` exit 0, 93 W04 and 0 E.

Quarantine slice (`assimilation/quarantine-slice`, 7 data rows, derived from the register): S200, S202, S206, S210, S211, S224, S230, all `payload-absent`. Each already carries a hand-check verdict in the round-35 and round-36 lessons and in seat R41F01 (`.ufo/waves/round-41/w1/out/R41F01.md`); no quarantined row is appended and none is a source of this round's entry.

## considerthese

`considerthese/2026-10-25.md` proposal 1 ("Recompute every digest and S-id that a new lesson or row cites") is mined into C2. The reflection is a pointer, not evidence: this round opened what it names — the S472 digest (right prefix, wrong body) at `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md`, and the round-36 misattributed ids. C2 covers digests only; the cross-check of S-ids named in lesson prose against the rows they name is left open (frontier). Proposals 3 and 4 remain unimplemented; proposal 2 landed in round 41.
