# Round 25 — L1 planning pilot (before wave 1)

Author: kama round-25 L1 (planner seat). Run 2026-10-22 about 08:22 UTC, before
the preregistration. Purpose: size the C2 context-capacity matrix. This is a
planning walk, not claim evidence; the committed receipt is the evidence.

Binary: `~/.local/bin/llama-server --version` -> `version: 0.7.0-dev (build 11755, commit 704366d76)`.
Model: `~/.cache/kama-shokunin/models/stories260K.gguf` (1185376 bytes).
Port 47311 on 127.0.0.1, one child per configuration, killed after the reads.
Scratch: `/fast/scratch/hyaku/kama25/srv.log` (overwritten per configuration).

| args | /props default_generation_settings.n_ctx | /props total_slots | /slots n_ctx | log line |
|---|---|---|---|---|
| `-c 0` | 2048 | 4 | [2048, 2048, 2048, 2048] | `load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'` |
| `-c 2048 -np 2 -no-kvu` | 1024 | 2 | [1024, 1024] | `n_slots = 2, n_ctx_slot = 1024, kv_unified = 'false'` |
| `-c 2048 -np 2 -kvu` | 2048 | 2 | [2048, 2048] | `n_slots = 2, n_ctx_slot = 2048, kv_unified = 'true'` |

Help text at b11755 (`llama-server --help`): `-kvu, --kv-unified, -no-kvu,
--no-kv-unified ... (default: enabled if number of slots is auto)`;
`-np, --parallel N number of server slots (default: -1, -1 = auto)`;
`--kv-unified-per-slot N context limit per parallel slot (default: unset,
behavior unchanged). when set without -c/--ctx-size, the shared KV pool is
sized to n_parallel*N`.

Reading for planning only: `/props` n_ctx is a per-slot value, and whether it
equals `-c` or `-c / -np` depends on the unified-KV switch, whose default
depends on whether `-np` was given.
