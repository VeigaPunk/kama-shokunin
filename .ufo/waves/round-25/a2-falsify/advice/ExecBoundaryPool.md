Verdict: holds — the C2 arithmetic "two requests overflow the 2048 pool at 1025 tokens each" is confirmed by a sharp boundary: the same pair succeeds at 1024 tokens each (2 x 1024 = 2048, zero slack) and fails at 1025 tokens each (2 x 1025 = 2050). Smallest failing n_predict = 26. No defect found in the claim; one wording refinement is available and is not required.

## What was attacked

Claim text (`corpus/knowledge/context-capacity.md`, "A shared pool limits concurrent requests by its total size"):

> In L1 both slots were released at `n_tokens = 1025` (`final/raw/L1.server.log` lines 1849-1866): 2 x 1025 cells overflow the 2048 pool.

Target (unregistered supporting boundary pair on the L1 config `-c 0`): two concurrent 1000-token prompts with `n_predict` 24 and with `n_predict` 30, `ignore_eos` true, `cache_prompt` false, no streaming. The pair is not in the registered cell list, so it does not change the C2 count; it attacks the arithmetic that the entry and the lesson rest on.

## How it was run

Harness: `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/exec-boundary-pool.py` (written by this seat). Per run: one `llama-server` child, 127.0.0.1 only, port from the assigned range 47440-47459 (a port is used only when `ss -ltn` shows no listener and a bind test succeeds), child SIGTERM'd and reaped, then the port proven closed (`port_refuses_after: true`, and `ss_listen_ports_after: []` for every run) before the next child starts. Launch: `~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port <port> --no-webui --offline -v -c 0`. Server identity: `version: 0.7.0-dev (build 11755, commit 704366d76)`.

Request bodies, both requests: `prompt` = the first 1000 token ids from `/tokenize`, `n_predict` = the tested value, `ignore_eos` true, `cache_prompt` false, `stream` false. Both requests are released from a `threading.Barrier(2)`, so they overlap: measured start gap 0.09-0.21 ms in all 12 runs, `overlap: true` in all 12.

Every run: KV pool 2048 (`llama_context: n_ctx = 2048`), `load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'`, prompt 1000 tokens per request (`slot operator(): ... new prompt, n_ctx_slot = 2048, n_keep = 0, task.n_tokens = 1000`).

## Table

| run | n_predict | port | HTTP statuses | tokens_predicted | release `n_tokens` (slot 0, slot 1) | demand vs pool | outcome |
|---|---|---|---|---|---|---|---|
| np24-r1 | 24 | 47440 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np24-r2 | 24 | 47441 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np24-r3 | 24 | 47442 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np25-r1 | 25 | 47447 | 200, 200 | 25, 25 | 1024, 1024 | 2 x 1024 = 2048 | both pass, exactly full |
| np25-r2 | 25 | 47450 | 200, 200 | 25, 25 | 1024, 1024 | 2 x 1024 = 2048 | both pass, exactly full |
| np26-r1 | 26 | 47448 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np26-r2 | 26 | 47440 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np26-r3 | 26 | 47449 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np27-r1 | 27 | 47446 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r1 | 30 | 47443 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r2 | 30 | 47444 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r3 | 30 | 47445 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |

Failing requests: HTTP 500, `error.type = server_error`, `error.message = "Context size has been exceeded."`, `tokens_predicted` absent. Both requests of the pair fail, not only the newer one — the same shape as L1.

Binary search used 3 of the 6 permitted extra runs (27, 25, 26); the remaining budget was spent on boundary replicates (26 x2, 25 x1).

## Boundary verdict

- **Smallest failing `n_predict` = 26** (3 of 3 runs fail, 3/3 identical: both HTTP 500, both slots released at `n_tokens = 1025`).
- **Largest passing `n_predict` = 25** (2 of 2 runs pass, both HTTP 200, `tokens_predicted` 25, both slots released at `n_tokens = 1024`).
- The boundary is sharp to one cell per request: the pair fits at 2 x 1024 = 2048 (the whole pool, zero slack) and overflows at 2 x 1025 = 2050. Nothing else changes between the two configurations.
- The failure point does not move with `n_predict`: 26, 27 and 30 all release at exactly `n_tokens = 1025`. The cause is therefore the shared pool, not request length — which is what the entry says.
- The limit is the pool total, not a per-slot ceiling: each request reaches only 1025 of its own 2048 per-slot ceiling (`n_ctx_slot = 2048`), and the two requests together exceed only the 2048-cell pool.
- L1's release lines are reproduced exactly: `final/raw/L1.server.log:1852` and `:1866` print `n_tokens = 1025`; my failing runs print the same value (`raw/np26-r1.server.log:1822` and `:1836`).
- The failure path is the same shape as L1 and as S109: the server halves the batch (`failed to find free space in the KV cache, retrying with smaller batch size` down to `n_batch = 1`, `raw/np26-r1.server.log:1730-1810`), then logs `failed to find a memory slot for batch of size 1` (`:1816`) and `decode: Context size has been exceeded. off = 0, n_batch = 1, ret = 1` (`:1818`), then releases both slots (`:1822`, `:1836`).

**The claim holds.** The arithmetic in the corpus entry is exact, not approximate: 1025 tokens per request is the first point at which the pair needs more than the 2048-cell pool, and the neighbouring value 1024 fits exactly.

### One precision point (not a defect, no correction required)

In the failing runs the last successful decode of both slots is at `n_tokens = 1024` (`raw/np26-r1.server.log:1718-1719`), i.e. the cache held 2 x 1024 = 2048 cells, the whole pool; the next 2-token decode batch had no free cell, and the release line prints 1025 because the pending sampled token is counted in `n_past` (`slot prompt_clear: ... clearing prompt with 1025 tokens`, `raw/np26-r1.server.log:1824`). So "2 x 1025 cells overflow the 2048 pool" is right as a demand-versus-capacity statement, and the allocation in fact stopped at 2048 cells. Optional wording improvement for the entry: say that the pair fits exactly at 1024 tokens each and that the 1025th token of each request is the first one the 2048-cell pool cannot hold. The entry's current wording does not claim the 2050 cells were allocated, so nothing in it is wrong.

## Scope of this observation

Two concurrent requests, 1000-token prompts, `-c 0` (2048 unified pool, 4 slots), `ignore_eos` true, `cache_prompt` false, no streaming, build 11755 (commit 704366d76), CPU-only `stories260K.gguf` fixture, unregistered loopback ports 47440-47459. Nothing is claimed about other request counts, other prompt sizes, other pool sizes, other builds, or the registered consumers (no consumer port was probed). The registered C2 cell set is unchanged by this seat; the boundary pair is unregistered supporting evidence.

## Risks and blockers

- None blocking. The fixture model, the pinned build and the assigned port range were all available; every child was reaped and every port closed.
- Other wave-2 seats run their own `llama-server` children at the same time. This seat used only ports 47440-47459, verified free before each launch, and recorded the pool and slot-init lines of every run so the served child is the one measured. A foreign listener on one of these ports would have shown a different `llama_context: n_ctx` or a failed health check; none occurred.
- The measured boundary is a property of this fixture and build. The knowledge entry's scope section already limits transfer to other builds and large models.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/ExecBoundaryPool.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/exec-boundary-pool.py` (harness)
- `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/results-summary.md` (table)
- `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/results-summary.json` (machine-readable rows)
- `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/raw/np24-r1.server.log`, `np24-r2`, `np24-r3`, `np25-r1`, `np25-r2`, `np26-r1`, `np26-r2`, `np26-r3`, `np27-r1`, `np30-r1`, `np30-r2`, `np30-r3` (12 server logs, one per run)
- `.ufo/waves/round-25/a2-falsify/out/ExecBoundaryPool/raw/np24-r1.json` ... `np30-r3.json` (12 run records: statuses, error bodies, request times, release lines, pool, teardown)

No production file was edited. No tool was installed or upgraded (Python 3 standard library only).
