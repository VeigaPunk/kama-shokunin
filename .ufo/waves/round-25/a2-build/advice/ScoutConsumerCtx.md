# ScoutConsumerCtx — C2 scope: what the fixture result means for the three registered consumers

**Verdict:** the pool-versus-slot finding changes the reading of exactly one registered row's
declared numbers (`ufo-fsd-thetick`: 16384 is a pool, 8192 is the per-slot ceiling), adds one
concrete capacity failure mode to the `omp-llama-cpp-default` row, and leaves
`ufo-fsd-local-helper` unchanged; no row's verdict vocabulary needs to change, but a `MODEL_OK`
must not be read as a capacity statement.

Read-only seat. No endpoint contacted, no `llama-server` child started, no probe run, no file
outside my own output directory and this report written. Every statement below is labelled as
committed-file evidence, a dated host-file read, or wave build output that is **not committed** at
the lane tip `1fc41e346853afd98cbd7010af5db4e54dc877f7`.

## The findings in the form I use them

I opened the raw artifacts directly; I did not re-run any cell. The load-cell status rows
and the six props/log excerpts below are bytes on disk, not peer prose.

| Finding | Direct artifact I opened | Content |
|---|---|---|
| F1 HTTP shows per-slot, not the pool | `.ufo/waves/round-25/a2-build/out/ExecRawReplicate/K5/props.json` and `K5/server.log:283-284,295,1084` | `/props` `n_ctx` 2048 and `total_slots` 1, while `llama_context: n_ctx = 4096`, `n_ctx_seq = 4096`, `n_ctx_slot = 2048`, and the warning `n_ctx_seq (4096) > n_ctx_train (2048)` |
| F2 identical HTTP surfaces, 4x pool difference | `ExecRawReplicate/K1/props.json` vs `X1/props.json`; `K1/server.log:284,1082`; `X1/server.log:812-813,1344-1345,1610` | both report `n_ctx` 2048 and `total_slots` 4; K1 pool 2048 unified, X1 pool 8192 split |
| F3 full-context concurrency is a pool event | `ExecLoadReplicate/l-cells-receipt.json` | L1 (`-c 0`, shared 2048 pool) concurrent: six records, all status 500; L2 (8192 split) concurrent: six records, all 200; L3 (shared pool, sequential): six records, all 200 |

Provenance: these are attempt-2 build outputs in the working tree (`git` has no committed copy at
the tip). Their prose reports are `advice/ExecRawReplicate.md` and `advice/ExecLoadReplicate.md`.
The pool/slot source model is `out/ScribeEntryDraft/context-capacity.md` (lines 13-48, 77-100); the
committed planning walk is `pilot.md:12-16`. All of it is a dated fixture sample, not live service
state.

## Registry rows and what they declare

`registry/endpoint-consumers.tsv:13` fixes six columns: id, consumer_path, resolver,
declared_baseurl, expected_model_id, notes. **No column can carry a context size or a slot count**,
so any declared topology is only visible inside the consumer file, never in the registry itself.

`tools/kama-probe.sh` reads only `/v1/models` and `/health`: a byte-level search for
`props|slots|n_ctx|total_slots|context` over the whole script returns no matches (exit 1), and
`tools/kama-probe.sh:5-7` states the single question it answers. **No current verdict carries
capacity information.**

## Table per consumer row

| Row (`registry/endpoint-consumers.tsv`) | Declared context size | Declared slots | Launch flags in committed files | Does the finding change how kama reads this row? |
|---|---|---|---|---|
| `omp-llama-cpp-default` (:35), `~/.local/bin/omp`, expects `-` | none in the provider object; a capacity number is imported at runtime from `/v1/models` `meta.n_ctx` or `/props` | none | none (consumer, not a server); model id is not checked (expected `-`) | **Yes, one dimension.** The number omp imports is the per-slot ceiling, not the pool. Safe as a single-request budget; wrong as an aggregate capacity reading. Its output cap is set equal to that same number, so a long generation can consume a whole slot. |
| `ufo-fsd-thetick` (:36), `$UFO_SRC/config/the-tick.machine.json`, bare model id | `contextTokensPerRunner` 8192 (:6) and `contextTokens` 16384 (:18), equality enforced (:216-217) | `parallelSlots` 2 (:17); runners count must equal it (:220-221) | target server documented as `--port 34113`, ctx 16384, parallelism 2, `--alias`, `--cors-origins http://127.0.0.1:8080`, `--no-webui`, `--no-agent`, `--model` (`corpus/knowledge/drift-timeline.md:14`; live unit **absent**) | **Yes, and most.** The declaration is a pool statement (16384 = 2 x 8192). It is consistent with the documented values under the default split launch, and two of its numbers are HTTP-checkable (`total_slots` 2, `/props` 8192); the pool itself is not checkable. |
| `ufo-fsd-local-helper` (:37), `$UFO_SRC/scripts/local-helper.mjs`, bare model id | none | none | none (client) | **No change to the row.** It declares no topology. The finding only supplies the error class a capacity failure would take (`backend_http_error`, HTTP 500), which that consumer cannot tell apart from other non-2xx failures. |

## Row detail

### omp-llama-cpp-default

Declared, host binary read this session (`~/.local/bin/omp`, sha256
`85d9daf3a05fc76e8cd425ae1904eb576af8d21cc85fcf4690742626e07ccfa4`, embedded-JS newline offsets):

- Provider object newlines 1174143-1174149: `provider: "llama.cpp"`, `api: "openai-responses"`,
  `baseUrl: Bun.env.LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"`, `discovery: { type:
  "llama.cpp" }`, `optional: !Bun.env.LLAMA_CPP_BASE_URL`. No context size, no slot count.
- Capacity import: `vY` at 1123091-1100 returns
  `default_generation_settings.n_ctx`, falling back to top-level `n_ctx` (the `/props` shape);
  `SY` at 1123101-1109 maps `/v1/models` `meta.n_ctx` to `runtimeContextWindow` and
  `meta.n_ctx_train` to `trainingContextWindow`; the `/props` value feeds
  `configuredContextWindow` at 1123137 and a direct `contextWindow: vY(I)` at 1123329; selection
  at 1123368 is
  `runtimeContextWindow ?? configuredContextWindow ?? Y?.contextWindow ?? trainingContextWindow ?? 128000`
  (constants `ure = 128000` at 907533, `pre = 32768` at 907534).
- Output cap: `maxTokens: iL(pe, Y?.maxTokens)` at 1123380 with
  `iL(u,p) = p === "contextWindow" ? u : Math.min(u, p ?? jK)` at 1123062-3064.

Reading change. Every capacity number omp can see is F1's per-slot value. For one request that is
the correct ceiling, so the import is not wrong; but F2 (K1 and X1 are indistinguishable on `/props`
and `/slots`) means omp cannot tell how many of its own requests can run at full context. F3 shows
that on a shared pool the failure is not a queue: both in-flight requests get HTTP 500, so a caller
that reads `/props` once and dispatches two long requests will lose both. Second, because `pe` is
the per-slot number and the default branch clamps `maxTokens` to 32768, a slot of 8192 yields a
8192-token output budget equal to the whole slot: prompt plus generation can exceed the slot even
with no concurrency. [INFERENCE: static reading of the binary block above; I did not run omp.]

What kama should not do: add a capacity check to this row that treats `/props n_ctx` (or
`/v1/models meta.n_ctx`) as the KV pool. Those two fields are the same function's output
(`n_ctx_slot`); the pool appears only in the server log at `-v`
(`out/ScribeEntryDraft/context-capacity.md:112`).

### ufo-fsd-thetick

Declared (`config/the-tick.machine.json`, tracked and clean at ufo-fsd-alpha HEAD
`093edb979559443bca65245fbdd94ac3621446fb`, sha256 `c0f35a29...9e87f5`, read in full):

- `:6` `"contextTokensPerRunner": 8192`
- `:16` `"endpoint": "http://127.0.0.1:34113/v1/chat/completions"`
- `:17` `"parallelSlots": 2`
- `:18` `"contextTokens": 16384`
- Validator `scripts/the-tick-config.mjs:216-217` requires `contextTokens === parallelSlots *
  contextTokensPerRunner`; `:220-221` requires the runners array length to equal `parallelSlots`.
  So 16384 = 2 x 8192, and the two runner sockets in the file satisfy it.
- The consumer's provenance identity is `endpoint`, `parallelSlots`, `contextTokensPerRunner`
  (`scripts/the-tick-ping.mjs:121`; producer `scripts/the-tick-config.mjs:449-458`). The pool
  value `contextTokens` is deliberately **not** in the identity tuple.
- No request-level cap: a search over `scripts/the-tick-*.mjs` and the config for
  `max_tokens|maxTokens|n_predict|num_predict|maxOutputTokens|num_ctx|n_ctx` returns nothing
  (exit 1), and a search for `/props|n_ctx|num_ctx` over the whole ufo-fsd-alpha tree returns no
  matches. The consumer never measures capacity and never enforces its own declared per-runner value.

Launch flags. The 34113 unit is gone from the host (`test -e` -> absent, both
`qwen-coder.service` and the `ctx32k-q4` variant). The only committed record is prose at
`corpus/knowledge/drift-timeline.md:14`: `--port 34113`, ctx 16384, parallelism 2, `--alias`,
`--cors-origins http://127.0.0.1:8080`, `--no-webui`, `--no-agent`, explicit `--model`. That
record does not spell out `--kv-unified`, so the cache layout of the deployed launch is **not**
established by committed evidence.

Reading change. Apply F1/F2 to the declaration as written:

- `contextTokens` 16384 is a **pool** number, and `contextTokensPerRunner` 8192 is the per-slot
  ceiling it implies when the cache is split (16384 / 2, and the 256-token per-sequence padding
  granularity does not bite here). The committed doc conflates them: `corpus/knowledge/consumer-registry.md:41`
  says "`parallelSlots`/`contextTokens` at `:17-18`" and `:106` says "(2 slots / 16384 ctx)".
  Under this build that reading is wrong; the per-runner context is 8192.
- The documented launch (ctx 16384, parallelism 2, no `--kv-unified` recorded; the record gives
  values, not the flag spellings) yields per-slot 8192,
  which agrees with the declaration. If the same `-c 16384` ran with `--kv-unified`, the served
  per-slot value would be 16384, double the declared per-runner budget. If it ran with `-np`
  unset, the auto branch would give 4 slots ([INFERENCE: auto-slot branch observed at K1 with
  `-c 0`; the branch keys on `n_parallel`, not on the context value, per the wave's source seat
  `advice/SrcServerAutoSlots.md`]).
- All three launch shapes are distinguishable from HTTP alone, using only consumer-declared
  numbers: `total_slots` must be 2 and `/props default_generation_settings.n_ctx` (or every
  `/slots` `n_ctx`) must be 8192. The model-id check the registry runs today cannot see either.
- The residual gap is the pool. A launch of `-c 32768 -np 2 --kv-unified --kv-unified-per-slot
  8192` would serve per-slot 8192 with a 32768 pool, i.e. exactly the declared HTTP numbers with
  double the declared pool (the K8 shape, where a unified pool larger than slots x per-slot leaves
  cells unused). Only the `-v` log line separates that from the declared split launch.
- Concurrency. Because the declaration has pool equal to slots x per-slot, the K1/L1 trap (four
  slots advertising 2048 on one 2048 pool) cannot be described by these numbers: the declared
  topology implies two full-context requests can coexist, and F3's L2 shows that shape succeeding.
  The declaration therefore carries a real concurrency guarantee, but only if the pool is really
  16384, which is the quantity HTTP cannot show.
- Capacity failure of an over-budget request lands at the server, not in this consumer: with no
  request-level cap, a prompt above 8192 tokens per request would produce the F3-style HTTP 500,
  and the consumer has no code that maps that error to a topology complaint.

### ufo-fsd-local-helper

Declared (`scripts/local-helper.mjs`, sha256 `07801abc...deb6b`, read):

- `:8` `DEFAULT_URL = "http://127.0.0.1:34113"`, `:9` bare model id.
- `:10` `MAX_INPUT_BYTES = 12 * 1024` (enforced at `:128`), `:11` `MAX_N_PREDICT = 512`, `:12`
  `DEFAULT_N_PREDICT = 256`.
- Payload `:223-231`: `model`, `messages`, `temperature: 0`, `seed: 0`, `max_tokens: nPredict`,
  `stream: false`, optional `response_format`.
- No context size and no slot count anywhere; the only `context` hits (`:175`, `:337`) are the
  dedupe input array.

Reading change. None for topology: the file makes no capacity claim, so there is nothing to
reconcile. The one consequence is error attribution: `:238-239` maps any non-2xx to
`backend_http_error`, and F3's capacity failure is HTTP 500, so at that consumer's boundary a
slot overflow is indistinguishable from an authentication or routing failure. Its request bound is
about 12 KiB of input plus at most 512 generated tokens, which fits inside the-tick's declared 8192
per-runner ceiling with margin [INFERENCE: no tokenizer was run, so the token count of 12 KiB of
text is not measured].

## Consequences for kama (advice only; the L1 owns edits)

1. Keep the three verdicts as they are; they answer model identity and liveness. No finding here
   makes a `MODEL_OK` wrong.
2. If a capacity check is ever added, it must be per consumer and be fed from the consumer's own
   declaration. For `ufo-fsd-thetick` that is exactly two comparisons (`total_slots`, per-slot
   `n_ctx`), not a pool comparison. The registry TSV has no column for it today.
3. Do not let `/props n_ctx` enter any lane document as "context capacity" without the words
   "per slot". The committed wording at `corpus/knowledge/consumer-registry.md:41` and `:106`
   ("2 slots / 16384 ctx") is the seed of that misreading and is worth a correction when the
   context-capacity entry lands.

## Does not establish

- Any live state of the three consumers. The committed samples are
  `registry/history/20261014T124232Z.json`, `registry/history/20261014T124525Z.json` and
  `registry/history/latest.tsv` (all 2026-10-14, all three rows `DEAD` / `connection-refused`);
  `registry/history/DELTA.md` records the last transitions as `MODEL_OK -> DEAD` for both
  ufo-fsd rows and `FOREIGN_SERVICE -> DEAD` for the omp row at `2026-10-14T12:42:32Z`.
- The deployed 34113 launch's full argv, or its cache layout; the unit is absent and the committed
  record is prose.
- The 30B model's `n_ctx_train`, so the per-slot cap at 8192 for that model is not checked here.
- omp's effective baseURL (`file_match=inherited`; the binary default is not the effective value)
  and whether its llama.cpp provider is selected in the running configuration.
- Any runtime behaviour of omp or the-tick: the omp reading is a static binary reading, and the
  the-tick reading is config plus validator.
- The C2 claim value itself: I read raw cell artifacts, I did not re-run cells and did not run
  `count-c2.py`.

## Files written

- `.ufo/waves/round-25/a2-build/out/ScoutConsumerCtx/evidence.txt` (raw commands, outputs, hashes)
- `.ufo/waves/round-25/a2-build/advice/ScoutConsumerCtx.md` (this report)

No tools installed or updated. No llama-server child started; no port used. No lane production
file, registry row, Git index, jj state, operator config or consumer file was modified.
