#!/usr/bin/env python3
"""Per-slot context predicted by reading llama.cpp 704366d76 source; no server is started.

Lines modelled (pinned commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad):
  common/arg.cpp:1406            server default n_parallel = -1 (auto)
  common/common.h:580            kv_unified default false
  tools/server/server.cpp:169-187 auto slots -> 4 + unified; per-slot pool sizing when -c unset
  src/llama-context.cpp:219      n_ctx 0 -> n_ctx_train
  src/llama-context.cpp:377-392  pad to 256, per-sequence split, re-pad, n_ctx rewrite
  tools/server/server-context.cpp:4655-4663 n_ctx_slot = min(n_ctx_seq, per_slot, n_ctx_train)
The --fit memory adjustment (common/fit.cpp) is not modelled: it cannot bind on this fixture.
"""
N_CTX_TRAIN = 2048


def pad(x, n=256):
    return (x + n - 1) // n * n


def cell(c=None, np=-1, kvu=None, per_slot=0):
    explicit_c0 = c == 0
    n_ctx = 0 if c is None else c
    kv_unified = False if kvu is None else kvu
    if np < 0:
        np, kv_unified = 4, True
    if per_slot > 0 and n_ctx == 0 and not explicit_c0:
        n_ctx = np * per_slot
    n_ctx = n_ctx or N_CTX_TRAIN
    n_ctx = pad(n_ctx)
    if kv_unified:
        seq = n_ctx
    else:
        seq = pad(n_ctx // np)
        n_ctx = seq * np
    slot = min(seq, per_slot) if per_slot > 0 else seq
    slot = min(slot, N_CTX_TRAIN)
    return dict(total_slots=np, kv_unified=kv_unified, kv_pool=n_ctx, n_ctx_seq=seq, slot_n_ctx=slot)


CELLS = {
    "K1 -c 0": cell(c=0),
    "K2 -c 2048 -np 2 --no-kv-unified": cell(c=2048, np=2, kvu=False),
    "K3 -c 2048 -np 2 --kv-unified": cell(c=2048, np=2, kvu=True),
    "K4 -c 1024 -np 1": cell(c=1024, np=1),
    "K5 -c 4096 -np 1": cell(c=4096, np=1),
    "K6 -c 1000 -np 3 --no-kv-unified": cell(c=1000, np=3, kvu=False),
    "K7 -np 2 --kv-unified-per-slot 512": cell(np=2, per_slot=512),
    "K8 -c 4096 -np 4 --kv-unified --kv-unified-per-slot 512": cell(c=4096, np=4, kvu=True, per_slot=512),
}
for k, v in CELLS.items():
    print(f"{k:58s} {v}")
