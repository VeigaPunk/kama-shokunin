# Draft: SKILL.md decision rows for round-25 C2 (frontier K05)

Seat: ScribeSkillRows (kama round-25 attempt 2, wave 1, read-only).
Date: 2026-10-22. Status: DRAFT — SKILL.md is a lane production file, written
only by L1; this file proposes exactly what to insert and where.

Format: the four-column decision-table style of the only literal "Decision table"
in SKILL.md (line 125-140, "## Decision table — rules with dated September host
examples" — columns `Symptom | First check | Verdict | Action`). Each row names
the knowledge entry (`corpus/knowledge/context-capacity.md`, the admitted entry
of amendment 2), the registered cell ids it rests on, and quotes the fixture
scope. C2 has not yet observed (receipt absent, count-c2.py exit 2 at base
efe58e96), so the rows carry the preregistered predictions and the source-pinned
line citations; they are to be re-anchored to the committed receipt by L1 after
the claim lands.

Fixture scope (compact quote used in every row): build 11755 / commit
704366d76, model `~/.cache/kama-shokunin/models/stories260K.gguf` (sha256
270cba1b…256d), `n_ctx_train` 2048, no SWA / no rope scaling; CPU-sized KV
cache so `--fit` never binds (CriticC2Sizing section 6; amendment-2 launch rule).

## Proposed insertion line

Insert the block below **after SKILL.md line 672** (`registered endpoints, model
downloads and persistent servers remain operator-owned.`), i.e. as a new block
at current line 673 (blank), immediately **before line 674** (`## Round-21
instrument registry: report landing audit and install links (owner: kama)`).
This places the rows directly after the round-20 section that carries the
"do not divide blindly" rule (S060, line 665-667) and keeps the round sections
contiguous; the existing S060 sentence stays intact and is refined, not
replaced. Fallback if L1 wants maximum adjacency to the S060 sentence: insert
after line 667 (end of the "Offline GGUF declared identity" paragraph), but
that sits under an "Offline" heading that does not describe live serving rows.

## Proposed block

**Round-25 live context-capacity decisions (owner: kama; claim C2, frontier
K05).** These rows refine S060 and supersede the round-20 `nctx-crosscheck.py`
formula for an unset `-c` with a split cache. They rest on the admitted entry
`corpus/knowledge/context-capacity.md` and the registered receipt cells.

| Symptom | First check | Verdict | Action |
|---|---|---|---|
| A llama-server's served context capacity is needed; `/props` reports `n_ctx` | `GET /props`, read `default_generation_settings.n_ctx` and `total_slots`; read `/slots` `n_ctx` and `/v1/models` `meta.n_ctx_train` | `n_ctx` is the per-slot ceiling (`n_ctx_slot()`), not the shared KV pool; `/props` (`server-context.cpp:5236`), `/slots` (`:1437`) and `/v1/models` (`:5186`) all read that same per-slot value, so their agreement is expected, not independent evidence. It is not training context and must not be computed as `ctx / total_slots` (S060) | Read the pool from the `-v` log (row below). Knowledge entry: `corpus/knowledge/context-capacity.md`; cells: K1–K8, X1–X3 (config), pilot rows (pilot.md:14-16). Fixture scope: build 11755/704366d76, stories260K.gguf sha256 270cba1b…256d, n_ctx_train 2048, no SWA/rope scaling; `--fit` never binds |
| `-c` is unset, `-np` is explicit and the cache is split (`--no-kv-unified`) | Launch with `-v`; capture the `llama_context: n_ctx` and `n_ctx_slot` log lines and compare them to `/props` | Fit raises the unset context to `n_ctx_train × n_streams` with `n_streams = n_seq_max` for a split cache before slot division (`common/fit.cpp:195-198,266-273`): X1 (`-np 4 --no-kv-unified`) predicts pool 8192 / per-slot 2048, so the round-20 `nctx-crosscheck.py` 512 row is wrong for this binary; `--fit off` (X3) falls back to `n_ctx_train` 2048, pool 2048 / per-slot 512 | Never derive an unset `-c` from the round-20 formula; record the fit step. Knowledge entry: `corpus/knowledge/context-capacity.md` (supersession note); cells: X1, X2, X3. Fixture scope: as above; fit reduction below 4096 never binds here, so the raise is the only fit effect visible on this fixture |
| Two concurrent requests each need the full per-slot context on a shared unified pool (L1: `-c 0` auto → one 2048 pool across 4 slots) | Send two concurrent `POST /completion` requests, 1000-token prompts, `n_predict 600`, `ignore_eos true`, `cache_prompt false`; record HTTP statuses and the server log | Per-slot `n_ctx` limits one request; with a unified cache the slots share the pool and a full pool fails every running request (`Context size has been exceeded`, `server-context.cpp:4301,4318-4320`); L1 predicts at least one error. Identical `/props`, `/slots`, `/v1/models` as X2 hide a fourfold full-context concurrency difference (K1 vs X2) | Do not promise concurrent full-context service from the HTTP surfaces; verify under load. Knowledge entry: `corpus/knowledge/context-capacity.md` (load guarantee); cells: L1, L2, L3. Fixture scope: as above |
| A claim needs the KV pool size; no HTTP surface exposes it | Launch with `-v` and capture the `llama_context: n_ctx` log line (pool printed only at full verbosity; absent at `-lv 3` — amendment-2 honesty notes) | The pool appears only in the log; the round-25 counter requires a `kv_pool_n_ctx` integer matching a captured `llama_context: n_ctx` line for every cell (count-c2.py:55-57). Without `-v`, a pool-value claim has no observed support | Require `-v` log evidence whenever the pool, not just per-slot `n_ctx`, is claimed; store the matched line. Knowledge entry: `corpus/knowledge/context-capacity.md` (visibility limit); cells: all 14 (K1–K8, X1–X3, L1–L3). Fixture scope: as above |

Scope does not establish: served `n_ctx` on registered consumers or large
models, omitted `-c` versus `-c 0` under memory pressure, other builds or other
engines (CriticC2Sizing section 6 does-not-establish list; amendment-2
learning_artifacts).
