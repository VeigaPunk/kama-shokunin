# N4Skill — C1 population → operating-surface map (round 44, wave 1)

**Verdict:** 76 of the 91 C1 population rows are directly anchored by S-id in the lane's operating surface (SKILL.md tables/prose; registry error-signatures-r26.json, request-field-outcomes-r28.json, chat-param-outcomes-r31.json); the other 15 rest only on corpus/knowledge used-by files and have no S-id anchor in those surfaces. Upstream spot-checks at b11889 found **no drifted semantics in any instruction-carrying anchor** verified here; the six draft `TODO` rows resolve to holds/unverified as detailed in §5, and every instruction that would go wrong if its row drifted is listed per row in §4.

Deliverables: `map.tsv` (175 rows: `id surface file:line instruction`) + this report. No tools installed (system python3/git only, read-only upstream; no pacman/uv actions needed).

---

## 1. Method and evidence

All lane file reads are from the working tree at lane commit `77d1bbf` (plus round-44 drafts); upstream reads via `git -C /fast/scratch/hyaku/kama-r44/shared/llama.cpp show/diff/log` (read-only, never fetch/checkout). Commands (all exit 0):

```
python3 - <<'EOF'   # parse draft ledger, verdict distribution
  id count: 91 rows; 81 holds, 4 unchanged-file, 6 TODO (S001 S015 S037 S043 S059 S108)
EOF
grep 'S\d{3}' SKILL.md                       # S-id occurrences in SKILL.md (grep tool)
grep 'S\d{3}|704366d|b11755' registry/        # registry JSONs (required-citations.json: no S-ids)
python3 scan                                   # per-id occurrence map -> map.tsv (175 rows)
git -C <llama.cpp> diff --stat 704366d76..d854d98b -- <12 population files>
       # common/arg.cpp 50, common.cpp 95, llama-context.cpp 24, llama-kv-cache.cpp 11,
       # server/README.md 163, server-common.cpp 150, server-context.cpp 920, server-http.cpp 51,
       # server-models.cpp 296, server-queue.cpp 3, server-schema.cpp 71, server.cpp 773
git -C <llama.cpp> log --oneline 704366d76..d854d98b -- server.cpp server-queue.cpp server-http.cpp arg.cpp server-schema.cpp
       # f3269ef96 "server: refactor server entrypoint (#31113)" explains S037/S043/S108 TODO relocations
python3 hunk-overlap scan    # diff -U0 hunks vs each row's pin_lines (window ±8) -> 5 rows flagged
```

## 2. What rests on the 91 rows (map.tsv highlights)

| Surface | Rows (id count) | Evidence (map.tsv lines) |
|---|---|---|
| SKILL.md §Round-26 live error signatures + registry/error-signatures-r26.json | S114–S130 (17) | map.tsv:30-63; JSON rows E26-01..17 |
| SKILL.md §Round-28 request-field outcomes + registry/request-field-outcomes-r28.json | S140–S173 (34) | map.tsv:71-138; JSON rows F28-01..34 |
| SKILL.md §Round-31 chat-param outcomes + registry/chat-param-outcomes-r31.json | S180–S191 (12) | map.tsv:139-174; JSON rows K31-01..18 |
| SKILL.md §Round-20/25 capacity + decision table (687-690) | S060, S106, S109, S112, S113 (range S106-S113 at :679) | map.tsv:17-29 |
| SKILL.md §Round-17 live-gate receipts (575, 593-594) | S036, S042, S043, S047 | map.tsv:5-12 |
| SKILL.md §Round-18 v3 receipt prose (618, 637) | S054, S056 | map.tsv:13-15 |
| SKILL.md §Round-11 identity prose (367) | S001 | map.tsv:2 |
| SKILL.md §Round-42 C3 counter row (1397) | S479 (also corpus/knowledge/context-capacity-engine-sides.md:1) | map.tsv:175-176 |
| required-citations.json | **none** — zero S-id references (its `id` keys are receipt names: s055-commands, gate-live-1, r18-*) | scan result |
| No S-id anchor in SKILL.md/registry | S015 S035 S037 S059 S107 S108 S110 S111 S131 S132 S133 S134 S135 S137 S138 (15) — rest on corpus/knowledge used-by files: gguf-runtime-compatibility-boundary.md, llamacpp-loading-lifecycle.md, context-capacity.md, served-identity-crosswalk.md | map.tsv:3,4,7,16,22,23,25,26,64-70 |

## 3. Drift-sensitive instructions (which instruction breaks if its row drifts)

Each row below is an *agent-facing instruction* whose correctness is a function of the row's anchored upstream bytes:

| Row(s) | Instruction an agent follows (surface file:line) | If the row drifts at b11889, the instruction becomes wrong because… |
|---|---|---|
| S114–S130 | E26 rows: classify the HTTP/exit signature and re-launch with the named flag (`--slots`, `--slot-save-path`, `--props`, `--embeddings`, `--pooling`, `--reranking`, `--mmproj`, `--ctx-size`, client-side fixes) (SKILL.md:1102-1118) | the diagnosis (501 vs 400 vs 500 vs exit 1) and remediation would target a state the new build no longer has |
| S140–S173 | F28 rows: client-side validation rules (“send -1, not -2”, “0..1 range”, “read generation_settings back”) (SKILL.md:1166-1199) | a changed bound/clamp would make the client contract wrong (e.g. accept a value the server now rejects) |
| S180–S191 | K31 rows: chat-API expectations (messages array, logprobs/top_logprobs pairing, response_format enum, json_schema vs grammar, stream_options) (SKILL.md:1247-1264) | adapter behavior changes would mislead chat clients |
| S036 | “every non-frontend path answers the exact 503 loading envelope before the API-key check” — live-gate `loading_envelope_graded` + `source_binding` (SKILL.md:575,593) | receipt validation would fail on a real b11889 run or, worse, pass against a changed envelope |
| S042 | `/health` 200 body exactly `{"status":"ok"}`; `health_ready` check (SKILL.md:575,594) | compact-JSON body changes would break the exact-body check |
| S043/S047 | teardown: first SIGTERM → rc 0, second signal exits 1; `teardown_graceful`/`teardown_port_closed` (SKILL.md:575,594) | same reasoning |
| S037 | “single-model listener answers before load; router ready before any model” → reachability of the 503 window (used by round-16/17 loading expectations) | if startup order changed, the 503 window could disappear or move, invalidating receipts |
| S054/S056 | exact-launch-argv policy: duplicate flags warn, last wins; `--spec-type` exempt; `--host` clears (SKILL.md:618,637) | a changed parser rule would make the gate's argv equality wrong |
| S060 | “n_ctx is per-slot ceiling, not the KV pool; don't derive pool from it”; never compute `ctx / total_slots` (SKILL.md:669,687) | capacity math would be wrong |
| S106/S109/S112/S113 | capacity decision table: fit-on raises to training context × slots; unified pool 500s; require verbose log for pool (SKILL.md:688-690) | capacity diagnoses would be wrong |
| S001 | served-identity interpretation guidance (README `/health`, id default/meta, `/metrics`) (SKILL.md:367) | interpretation layer would mis-ground |
| S479 | round-42 C3 counter row (S478/S479 present and correctly celled) (SKILL.md:1397) | counter fails even if the knowledge entry is correct (existence check, not truth check) |

## 4. Upstream re-verification spot-checks at b11889 (d854d98b)

All reads via `git show <commit>:<path>`; every literal/order checked is present or relocated identically:

| Row (verdict in draft) | Check | Result |
|---|---|---|
| S036 (holds) | middleware order: `middleware_server_state` before `middleware_validate_api_key`; 503 body `{"message":"Loading model","type":"unavailable_error","code":503}`; frontend exemption | intact (server-http.cpp:308-329,348-360 release) |
| S037 (TODO) | startup order: router `start()`→`is_ready.store(true)` before `load_startup_models` (release :518-535); instance `start()`→`load_model`→`is_ready.store(true)` (release :619-641) | **semantics hold** (refactor moved code into `server_run_instance`; same order and statements) |
| S043/S047 (TODO/holds) | `signal_handler` identical incl. second-signal `exit(1)` (release :29-38); SIGINT/SIGTERM install after load (release :651-653); `shutdown_handler`→`terminate()`→`start_loop()`→`clean_up()`→`return 0` (release :645-684); server-queue.cpp diff touches only `recv_with_timeout` (`deadline`/`wait_until`), not `terminate()`/`start_loop()` | **S043 semantics hold**; S047 unchanged |
| S054/S056 (holds) | unknown flag `throw` (:837-839); dup warn only for non-spec-type with “only last value will be used” (:840-846); `--host` clears (:3346); `--api-key` push_back (:3546,3562) | intact |
| S108 (TODO) | auto-slot sizing block relocated to server.cpp:127-143: `n_parallel=4`, `kv_unified=true`, `n_ctx = n_parallel * kv_unified_per_slot` | **semantics hold** |
| S114–S130 (holds) | all 17 E26 message literals present at release in the same files as pin (server-context.cpp, server-common.cpp, gguf.cpp, llama-context.cpp); E26-07/14 literals split/across-line in both pin and release (absent as single string in both — no change) | intact |
| S140–S173 (holds) | server-schema.cpp diff is additive-only: +2-line include, dry_sequence_breakers dedupe + new max-distinct error, TTS schema block. No F28 bound/message changed | intact |
| S001/S035/S134 (holds/TODO) | README key claims present at release: `/health`, 503 `Loading model`/`unavailable_error`, `{"status":"ok"}`, `--alias`, `--metrics`, `/v1/models`, `meta` | intact |
| S015 (TODO) | tools/quantize/README.md byte-identical pin↔release (12354 = 12354 bytes); requantize warning present | effectively unchanged-file |
| S059 (TODO) | gguf-py/gguf/gguf_reader.py blob identical pin↔release (bf3e0838…) | unchanged |
| S479 (holds) | `model_info["context_length"] = meta.n_ctx_train;` present at release :2326 (pin :2379), guard `if (meta.n_ctx_train > 0)` intact | intact |

## 5. Findings for L1 (ledger finalization)

1. **Six `TODO` rows need a final verdict.** My readings: S037 → holds (startup order preserved), S043 → holds (signal/teardown semantics preserved), S059 → holds/unchanged-file (blob identical), S108 → holds (block relocated verbatim-semantics), S001 and S015 → holds (README claims intact; S015 file byte-identical). The counter's `holds` path requires the cited text re-located verbatim; for S001/S015/S059 (no pin lines in SOURCES) an anchor must be supplied in the row's release_lines for the counter to count them — flagging them as `unverified` otherwise.
2. **required-citations.json does not rest on the C1 population** (0 S-id references). Do not spend re-verification budget there.
3. **New unregistered behavior at b11889** (not covered by any population row, so no map entry): `server-schema.cpp` now de-duplicates `dry_sequence_breakers` and rejects > `LLAMA_DRY_MAX_SEQ_BREAKERS` distinct entries; new `/tts` and realtime-transcription routes. Neither contradicts a held row.
4. **Range-cited rows**: S107/S110/S111/S113 are only covered by the “S106-S113” range mention at SKILL.md:679; their individual S-ids never appear in SKILL.md/registry. If any of them drifts, the capacity table rows 687-690 (S106/S109/S112) are unaffected but the range citation and its knowledge-file targets are.
5. **S479 is double-anchored**: SKILL.md:1397 (round-42 C3 counter) and `corpus/knowledge/context-capacity-engine-sides.md:1`. Its drift would fail the counter's existence leg regardless of upstream truth; it does not drift at b11889.

## 6. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/N4Skill/map.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/N4Skill.md`
