# Advice report — SrcServerSlotsAuto (kama round 25, C2 source seat)

Verdict: the auto slot count for `-np -1` is **not** in `tools/server/server-context.cpp` — it is decided in `tools/server/server.cpp` lines 169-174 — while `server-context.cpp` lines 1391-1393 are the code that logs `n_slots = ..., n_ctx_slot = ..., kv_unified = ...`; S060's anchors and quote still hold, and no existing SOURCES row covers either site.

## Scope of this seat

Read-only source seat for claim C2 (frontier K05, declared versus served context capacity). I opened upstream llama.cpp sources at the pinned commit, compared them against the lane's own pinned snapshot, and drafted source rows. I ran no server, bound no port, and probed no endpoint.

## Observations

### 1. Files opened (fetched fresh this round)

Command (exit 0):

```
mkdir -p /fast/scratch/hyaku/kama-r25/SrcServerSlotsAuto && cd /fast/scratch/hyaku/kama-r25/SrcServerSlotsAuto
curl -sSL -o server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
sha256sum server-context.cpp
```

Output: `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329  server-context.cpp` (6320 lines).

The installed binary matches the pinned commit:

```
~/.local/bin/llama-server --version
version: 0.7.0-dev (build 11755, commit 704366d76)
```

Also fetched this round, with sha256:

| file | sha256 | lines |
|---|---|---|
| `tools/server/server-context.cpp` | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | 6320 |
| `tools/server/server.cpp` | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | 591 |
| `common/arg.cpp` | `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d` | 4833 |
| `tools/server/server-common.h` | `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b` | — |
| `common/common.h` | `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9` | — |

### 2. Byte cross-check against the lane's own pinned snapshot

Command (exit 0 for each):

```
diff -q server-context.cpp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/server-context.cpp   # diff-exit=0
diff -q server.cpp        .../round-16/sources/llama.cpp-704366d/server.cpp                                                                 # diff-exit=0
diff -q common_arg.cpp    .../round-16/sources/llama.cpp-704366d/arg.cpp                                                                   # diff-exit=0
```

The round-16 lane snapshot and this round's fresh download are byte-identical, so every line number below is confirmed twice (independent fetch plus the lane's stored copy). `server.cpp` sha256 `21439622…` is the same value already recorded by S037/S043/S047.

### 3. The log line (in `server-context.cpp`)

`tools/server/server-context.cpp` lines 1391-1393, inside `server_context::load_model()` (the function opens at line 1116):

```
1391:        // setup slots
1392:        SRV_INF("initializing, n_slots = %d, n_ctx_slot = %d, kv_unified = '%s'\n",
1393:                params_base.n_parallel, n_ctx_slot(), params_base.kv_unified ? "true" : "false");
```

The printed prefix comes from `tools/server/server-common.h` lines 35-36: `SRV_INF` expands to `LOG_INF("srv  %12.*s: " fmt, 12, __func__, ...)`, so the log line reads `srv        load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'`. That matches the prefix shape already recorded in the round-25 pilot table.

Related lines in the same file: the slot loop `for (int i = 0; i < params_base.n_parallel; i++)` at 1396-1398 and 1429-1437 with `slot.n_ctx = n_ctx_slot();` at 1437; the served per-slot value is computed by `n_ctx_slot()` at 4654-4663; `/props` reports `total_slots` from `params.n_parallel` at 5244.

### 4. Where the slot count for `-np -1` is actually decided

`tools/server/server-context.cpp` never decides it: every `n_parallel` use there (lines 1393, 1396, 1429) only consumes the value. The decision is in `tools/server/server.cpp` lines 169-174:

```
159:    if (!is_router_server) {
169:        if (params.n_parallel < 0) {
170:            SRV_TRC("%s", "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true\n");
172:            params.n_parallel = 4;
173:            params.kv_unified = true;
174:        }
175:    }
```

So in single-model mode the auto slot count is fixed at **4** and the unified-KV flag is turned **on**; giving `-np` explicitly leaves `params.kv_unified` at its struct default `false` (`common/common.h` line 580: `bool kv_unified = false;`). That is exactly what the `-kvu/--kv-unified` help text promises (`common/arg.cpp` line 1730: "default: enabled if number of slots is auto"). The auto default itself is set in `common/arg.cpp` line 1406 (`params.n_parallel = -1;  // auto by default`, server example only) and the CLI text at line 2549 says "number of server slots (default: -1, -1 = auto)".

`server.cpp` lines 177-187 also auto-size the KV pool from `--kv-unified-per-slot` when `-c` was not pinned (`params.n_ctx = params.n_parallel * params.kv_unified_per_slot;` at 184), which is the K7-style path.

### 5. S060 reopened — its quote still holds

S060 anchor: "slot_n_ctx lines 4654–4663; model meta 5183–5188; props 5229–5245 at 704366d76; sha256 dd1de0f…". Verified line by line on the reopened file:

- 4654-4663 — comment "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" at 4654, `n_ctx_slot()` at 4655, `return std::min(res, llama_model_n_ctx_train(model_tgt));` at 4662, closing brace at 4663. Holds.
- 5183-5188 — `{"meta", {` at 5183, `n_ctx` at 5186, `n_ctx_train` at 5187, `n_embd` at 5188. Holds.
- 5229-5245 — `get_res_props` at 5229, `default_generation_settings` at 5243, `total_slots` at 5244, `model_alias` at 5245. Holds.
- sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` — matches. Holds.

S060's teaching sentence ("/props reports capped per-slot n_ctx; /v1/models separately reports n_ctx_train. Comparing served n_ctx with declared training context is not an equality test.") is still correct at this commit.

### 6. Does an existing row already cover this? — No

Command (exit 1, i.e. no match):

```
grep -cE "n_slots|kv_unified|total_slots" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
0
```

Other checks: `grep -n "server-context.cpp" corpus/SOURCES.md` returns rows S042 (line 54) and S060 (line 72) plus prose at lines 198, 213, 221; no other row points at this file. No row in the registry mentions `n_slots`, `kv_unified`, `n_parallel` auto, or the load-time slot log. The only rows touching `tools/server/server.cpp` are S037 (start-up order), S043 (signal path) and S047 (signal path), none of which cover the auto slot count.

One overlap to note for the L1: S060's `props 5229–5245` anchor already contains `total_slots` at 5244, so a new row that leans on `/props total_slots` partly re-covers S060's range. The rows proposed below keep their anchors on the log site and on the auto decision, which S060 does not mention.

## Proposed SOURCES rows (ids left for the L1 to number)

### Row A (primary, the file this seat was asked to open)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp server slot initialisation log @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | the slot count, per-slot context and unified-KV flag a single-model llama-server reports when it loads the model at commit 704366d76; not how `-c` is divided across slots, not the auto-slot decision itself (that is `server.cpp`, row B), not router mode | `load_model` start-up log at lines 1391-1393, slot creation loop 1396-1398, `slot.n_ctx = n_ctx_slot()` at 1437, `/props` `total_slots` at 5244; raw file sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | At model load the server prints the served slot count, the served per-slot context and the unified-KV flag in one line, and copies that per-slot context into every slot, so a receipt can check the log against the HTTP surfaces instead of trusting one of them. | queued | 2026-10-22 | on-release | corpus/knowledge/context-capacity.md |

- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
- Access date: 2026-10-22
- Located quote (8 words), `tools/server/server-context.cpp` lines 1392-1393:
  `initializing, n_slots = %d, n_ctx_slot = %d, kv_unified = '%s'`

### Row B (companion, the code that actually decides the auto slot count)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp server auto slot count @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | code | A | how many slots a single-model llama-server uses when `-np/--parallel` is left at -1 (auto) and whether the KV cache is unified, at commit 704366d76; not router mode (the block is skipped when `is_router_server`), not the division of `-c` across slots | lines 169-174 (`if (params.n_parallel < 0)` → `params.n_parallel = 4; params.kv_unified = true;`), KV-pool auto-sizing 177-187; raw file sha256 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 | With the slot count left at auto the server fixes it at 4 and turns the unified KV cache on; naming `-np` explicitly leaves the flag off, so the unified switch follows whether `-np` was given. | queued | 2026-10-22 | on-release | corpus/knowledge/context-capacity.md |

- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp
- Access date: 2026-10-22
- Located quote (12 words), `tools/server/server.cpp` lines 170:
  `n_parallel is set to auto, using n_parallel = 4 and kv_unified = true`

Supporting anchors, if the L1 wants them inside row B's anchor cell: `common/arg.cpp` line 1406 (`params.n_parallel = -1; // auto by default`), line 2549 (help text "number of server slots (default: -1, -1 = auto)"), lines 1727-1734 (`-kvu/--kv-unified` help text "default: enabled if number of slots is auto"), `common/common.h` line 580 (`bool kv_unified = false;`). These are a separate file and may deserve their own row; I have not numbered them.

## What this teaches for K05 (declared versus served context capacity)

- The served side has three distinct numbers, and this source names where each comes from: the slot count (`n_slots` / `params.n_parallel`), the per-slot context (`n_ctx_slot()` = min(sequence context, `--kv-unified-per-slot`, **model training context**), `server-context.cpp` 4654-4663), and the training context itself (`llama_model_n_ctx_train`, line 1351).
- Because `n_ctx_slot()` clamps to the training context at line 4662, a served per-slot `n_ctx` equal to `n_ctx_train` means the **model's training limit** bound, not that the requested `-c` was honoured. A K05 receipt that reports "served n_ctx = 2048" must say which of the three clamps produced it.
- The unified-KV switch changes the arithmetic: with unified KV the `-c` value is one shared pool, without it the context is divided per sequence. This source shows the switch is decided by whether `-np` was given (`server.cpp` 169-174), so "declared `-c`" cannot be read as "per-slot capacity" without also recording `kv_unified`.
- The load-time log line is a free cross-check: it prints slot count, per-slot context and unified flag together, in the same shape the pilot recorded, so a receipt can compare log against `/props total_slots` and `/props default_generation_settings.n_ctx` and detect a mismatch instead of reporting one number.

## What this does not establish

- It does not establish the observed values on this host. Nothing here was run; the pilot's three rows are the lane's own observation, not a reading of this source.
- It does not establish how `-c` is turned into per-sequence context inside the llama context (that decision lives in `common/context.cpp`, not opened here) — so it does not settle preregistered cell K6 (padding and per-sequence division of a non-multiple `-c 1000`).
- It does not establish the training context of `stories260K.gguf`; that comes from the GGUF file, not from this code.
- It does not cover router mode: the auto decision block is inside `if (!is_router_server)` (`server.cpp` 159), so a router server keeps `n_parallel = -1`.
- It does not establish anything about vLLM, SGLang or Ollama, and it does not describe the three registered consumer endpoints, which were not probed.

## Gates and constraints observed

- No server was started; no port was bound, so the round-16 fixture question and the "one child at a time" rule were not exercised. No registered consumer was probed.
- `corpus/SOURCES.md` was read only, never edited. The proposed rows live in this report and in the artifact below; numbering and insertion are the L1's call.
- No git or jj write command was run. No file outside my report path and my `build/out/SrcServerSlotsAuto/` artifact directory was created in the lane repo.
- Tooling: no package was installed or upgraded this round; the work needed only `curl`, `sha256sum`, `grep` and `diff`, all present on the host.

## Findings for the L1 (verbatim, no upgrade)

1. The item asked this seat to find the auto-slot decision in `tools/server/server-context.cpp`. It is not there: `server-context.cpp` consumes `params_base.n_parallel` (lines 1393, 1396, 1429) and prints it (1391-1393). The decision is `tools/server/server.cpp` lines 169-174 (`params.n_parallel = 4; params.kv_unified = true;`), guarded by `if (!is_router_server)` at line 159.
2. S060's anchors (4654-4663, 5183-5188, 5229-5245) and its sha256 still hold at commit 704366d76; no re-anchor is needed for S060.
3. No existing registry row covers the slot count, the unified-KV default, or the load-time `n_slots = ...` log. Two new rows are proposed (A for `server-context.cpp`, B for `server.cpp`); the L1 decides whether to file one row or both.
4. Overlap note: S060's `props 5229–5245` anchor already includes `total_slots` (5244). Rows A and B keep their anchors away from that overlap.

## Files I wrote

- `.ufo/waves/round-25/build/advice/SrcServerSlotsAuto.md` (this report) — relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`.
- `.ufo/waves/round-25/build/out/SrcServerSlotsAuto/source-pins.json` — URLs, sha256 values, access date, located quotes with line numbers, S060 reopen result.
- `.ufo/waves/round-25/build/out/SrcServerSlotsAuto/excerpts.txt` — the located source lines quoted above, for a reviewer who wants to check them without re-fetching.

Scratch (not lane files): `/fast/scratch/hyaku/kama-r25/SrcServerSlotsAuto/` holds the fetched `server-context.cpp`, `server.cpp`, `common_arg.cpp`, `server-common.h` and `common.h`.

## Out of scope for this seat

- Editing `corpus/SOURCES.md` (L1 owns the registry).
- The live llama-server fixture run and the K1-K8 receipt (executor seats).
- Any C1 mutation-instrument work.
