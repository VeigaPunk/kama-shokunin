Source claim supported at the pinned commit; a new scoped row is needed, but remains queued until L1 cites it. No runtime behavior was exercised.

## Axes

Source provenance, precise claim scope, registry compatibility, and non-interference with serving and lane production files.

## Observed command and provenance

Working directory: `/home/vgpnk/Projects/shokunin`.

Exact command executed:

```sh
mkdir -p /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots && curl -fsSL -o /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp && sha256sum /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp && wc -l /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp; echo "exit=$?"
```

Observed output:

```text
2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4  /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp
591 /fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp
exit=0
```

The final echo printed the successful fetch/hash/count chain's exit code. This was a fresh fetch in attempt 2, not reuse of an attempt-1 output. The full-source SHA-256 is `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`.

## Behavior established by source

Locations below refer to that freshly fetched `server.cpp`:

- Lines 159 and 169–174: inside `if (!is_router_server)`, a negative `params.n_parallel` causes assignment of `params.n_parallel = 4` and `params.kv_unified = true`. This branch sets unified KV to true rather than merely consulting its current value.
- Lines 177–181: the comment describes sizing from `--kv-unified-per-slot` unless context was pinned with `-c`, including `-c 0`; the actual predicate requires `params.kv_unified_per_slot > 0`, `params.n_ctx == 0`, and `(uint32_t) params.fit_params_min_ctx != UINT32_MAX`.
- Lines 183–186: when that predicate holds, `params.n_ctx = params.n_parallel * params.kv_unified_per_slot`, with a corresponding KV-pool-sizing log message.
- The sizing block follows the closing brace at line 175: unlike the preceding auto-slot branch, this displayed block is not itself enclosed by `if (!is_router_server)`. Its predicate does not explicitly test `params.kv_unified`.

## Existing registry coverage

Specialized search executed twice with pattern `tools/server/server\.cpp` against `kama-shokunin/corpus/SOURCES.md`; both searches returned S037 at line 49 and S043 at line 55. These are tool searches, not shell commands; no process exit code was supplied by the search tool. Complete rows were then opened with `read` selector `:49,55:raw`.

- `corpus/SOURCES.md:49`, S037: same file and commit, but scope is when `is_ready` is set in single-model versus router mode; anchors are lines 440–462 and 493–515.
- `corpus/SOURCES.md:55`, S043: same file and commit, but scope is signal/shutdown behavior; anchors are lines 26–38, 507–590 and a supporting queue-file anchor.
- A supplementary search for `auto|kv.unified.per.slot|KV pool|n_parallel` did not identify an existing row with this auto-slot/KV-pool scope. Matches elsewhere were unrelated text such as Automake or automatically generated references.

Decision: a new scoped row is needed. File identity and the matching SHA-256 do not extend either existing row's registered scope. `SOURCES.md` was not edited.

## Draft registry row

Exact column order is from `corpus/SOURCES.md:11`: id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by. The row below has 11 columns, leaves the id as requested, and claims no L1 citation yet.

| S1xx | llama.cpp auto slots and KV-pool sizing @ 704366d76 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | code | A | startup parameter assignments for automatic slot count, unified KV, and per-slot-driven KV-pool sizing at commit 704366d76; not measured served capacity | lines 159–186: non-router auto branch 169–174; sizing predicate 179–181 and assignment 183–186; raw SHA-256 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 | In non-router mode, negative n_parallel becomes 4 and sets kv_unified true. With kv_unified_per_slot > 0, n_ctx == 0 and the fit minimum-context sentinel not UINT32_MAX, startup assigns n_ctx = n_parallel * kv_unified_per_slot. | queued | 2026-10-22 | on-release | — |

Status remains `queued` until the L1 actually cites this scope. No source row was opened by a registry edit in this seat.

## Gate record

- Source URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp
- Freshly fetched raw URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp
- Access date: 2026-10-22.
- Located quote, lines 172–173: `params.n_parallel = 4; params.kv_unified = true;`
- Located quote, line 184: `params.n_ctx = params.n_parallel * params.kv_unified_per_slot;`
- The two quoted snippets total 11 whitespace-separated words, below 25 words even when counted together. The first quote joins the two consecutive source lines with one space; the second is a single complete source line.
- Scope gate: supports the startup assignments and their displayed guards only. This report is source-opening evidence, not C2 live-cell evidence or admission by the canonical judge.

## Does not establish

- How CLI parsing represents an omitted context versus explicit `-c 0`; the displayed comment states intent, but parser/sentinel assignment is outside this read.
- Later fitting, padding, allocation, training-context caps, or the final effective KV pool or per-slot context.
- Endpoint response values, independence of HTTP surfaces, model residency, or registered-consumer health.
- Full-context concurrency capacity, request success or failure, throughput, or model quality.
- A universal four-slot default for router mode or explicitly nonnegative slot counts.
- That the per-slot setting enables unified KV: its displayed sizing predicate has no such test or assignment.
- Runtime identity of the installed binary, any of the 14 registered C2 observations, receipt binding, or the C2 target count. All runtime checks are unrun and unverified by this seat.

## Gates, touched surfaces, and limits

Required preregistration, both amendments, the counter, pilot, attempt-1 disposition, godspeed skill and agent rules were read. No attempt-1 execution evidence was reused. No builds, tests, counter runs, mutation checks, or live probes were performed. No llama-server child was started, so this seat owned no serving port and required no child teardown. No tools were installed or updated. No product code, registry row, Git index, jj state, consumer, operator configuration, or judgment was changed. No conflicts found within this source slice.

Files written:

1. `/fast/scratch/hyaku/kama-r25a2/SrcServerAutoSlots/server.cpp` — fresh source bytes, using the assignment's allowed heavy-scratch root; outside the lane production tree.
2. `.ufo/waves/round-25/a2-build/advice/SrcServerAutoSlots.md` — this report, draft registry row, and Gate record.

No files were written under `.ufo/waves/round-25/a2-build/out/SrcServerAutoSlots/`. The report contains the complete requested deliverable; the raw source is retained at the scratch path above. L1 integration and final citation/admission are outside this seat's scope.
