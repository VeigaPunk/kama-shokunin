#!/usr/bin/env python3
"""Compare the round-20 nctx-crosscheck formula with a source-complete derivation at llama.cpp 704366d76.

Cells K1-K8 come from .ufo/waves/round-25/preregistration.json; X1-X3 are critic counterexample
settings (not preregistered). Values are computed from pinned source, not served.
Source-complete derivation adds two steps the round-20 formula omits:
  tools/server/server.cpp:179-186   --kv-unified-per-slot with no -c sizes the pool to n_parallel*N
  common/fit.cpp:196-198,266-273    unset or zero -c with split KV resolves the pool to n_ctx_train*n_streams
The memory-driven reduction in common/fit.cpp:393-436 only applies when n_ctx_train > --fit-ctx (4096),
so it never fires for stories260K (n_ctx_train 2048).
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[6]
spec = importlib.util.spec_from_file_location(
    "r20", ROOT / ".ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py")
r20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r20)

TRAIN = 2048
FIT_CTX_MIN = 4096


def pad256(x):
    return (x + 255) & ~255


def source(ctx, n_parallel, kvu, per_slot, ctx_explicit_zero=False):
    if n_parallel < 0:
        n_parallel, kvu = 4, True
    if per_slot > 0 and ctx == 0 and not ctx_explicit_zero:
        ctx = n_parallel * per_slot
    streams = 1 if kvu else n_parallel
    if ctx == 0:
        ctx = TRAIN * streams
        assert TRAIN <= FIT_CTX_MIN
    n_ctx = pad256(ctx)
    if kvu:
        seq = n_ctx
    else:
        seq = pad256(n_ctx // n_parallel)
        n_ctx = seq * n_parallel
    slot = min(seq, per_slot) if per_slot > 0 else seq
    return min(slot, TRAIN), n_ctx, n_parallel, kvu


CELLS = [
    ("K1", "-c 0", 0, -1, False, 0, True),
    ("K2", "-c 2048 -np 2 --no-kv-unified", 2048, 2, False, 0, False),
    ("K3", "-c 2048 -np 2 --kv-unified", 2048, 2, True, 0, False),
    ("K4", "-c 1024 -np 1", 1024, 1, False, 0, False),
    ("K5", "-c 4096 -np 1", 4096, 1, False, 0, False),
    ("K6", "-c 1000 -np 3 --no-kv-unified", 1000, 3, False, 0, False),
    ("K7", "-np 2 --kv-unified-per-slot 512", 0, 2, False, 512, False),
    ("K8", "-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512", 4096, 4, True, 512, False),
    ("X1", "-np 4 --no-kv-unified", 0, 4, False, 0, False),
    ("X2", "-c 8192 -np 4 --no-kv-unified", 8192, 4, False, 0, False),
    ("X3", "-c 2048 (auto slots)", 2048, -1, False, 0, False),
]

print("cell\targs\tr20_slot\tsource_slot\tsource_pool\tslots\tkv_unified\tconcurrent_guarantee_per_slot\tagree")
for cid, args, ctx, np_, kvu, ps, zero in CELLS:
    r20_slot, _, _ = r20.predict(ctx, TRAIN, np_, kvu, ps)
    slot, pool, n_par, uni = source(ctx, np_, kvu, ps, zero)
    guarantee = min(slot, pool // n_par) if uni else slot
    print(f"{cid}\t{args}\t{r20_slot}\t{slot}\t{pool}\t{n_par}\t{str(uni).lower()}\t{guarantee}\t"
          f"{'yes' if r20_slot == slot else 'NO'}")
