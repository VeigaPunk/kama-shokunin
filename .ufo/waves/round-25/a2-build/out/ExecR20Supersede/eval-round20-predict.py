#!/usr/bin/env python3
"""Evaluate the round-20 per-slot context formula (nctx-crosscheck.py predict())
against the round-25 amendment-2 source-derived values for the 11 config cells.

Round-20 formula location: .ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py
(lines 38-44). This script imports it unchanged and does not start a server.

Amendment-2 source-derived per-slot n_ctx values (preregistration-amendment-2.json
C2.cells_added / preregistration.json C2.cells):
  K1 2048 | K2 1024 | K3 2048 | K4 1024 | K5 2048 | K6 unknown
  K7 512 | K8 512 | X1 2048 | X2 2048 | X3 512
Load cells L1/L3 reuse K1 args, L2 reuses X2 args.

Output: table cell -> round-20 value -> amendment value -> agree.
Exit 0 always when the module imports and the table prints.
"""
import importlib.util
import os
import sys

ROUND20 = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    *([".."] * 6),
    ".ufo", "waves", "round-20", "build", "out", "SrcServerNctx", "nctx-crosscheck.py",
)
ROUND20 = os.path.normpath(ROUND20)
spec = importlib.util.spec_from_file_location("nctx_crosscheck", ROUND20)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
predict = mod.predict

N_CTX_TRAIN = 2048  # stories260K.gguf meta.n_ctx_train (amendment-2 K1 prediction)

# (id, args, ctx, np, kvu, per_slot, amendment per-slot n_ctx or None)
CELLS = [
    ("K1", "-c 0", 0, -1, False, 0, 2048),
    ("K2", "-c 2048 -np 2 --no-kv-unified", 2048, 2, False, 0, 1024),
    ("K3", "-c 2048 -np 2 --kv-unified", 2048, 2, True, 0, 2048),
    ("K4", "-c 1024 -np 1", 1024, 1, False, 0, 1024),
    ("K5", "-c 4096 -np 1", 4096, 1, False, 0, 2048),
    ("K6", "-c 1000 -np 3 --no-kv-unified", 1000, 3, False, 0, None),
    ("K7", "-np 2 --kv-unified-per-slot 512", 0, 2, False, 512, 512),
    ("K8", "-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512", 4096, 4, True, 512, 512),
    ("X1", "-np 4 --no-kv-unified", 0, 4, False, 0, 2048),
    ("X2", "-c 8192 -np 4 --no-kv-unified", 8192, 4, False, 0, 2048),
    ("X3", "-np 4 --no-kv-unified --fit off", 0, 4, False, 0, 512),
]


def main():
    print(f"round-20 predict() imported from: {ROUND20}")
    print(f"n_ctx_train = {N_CTX_TRAIN} (stories260K.gguf)")
    print("cell\tround-20 per-slot\tsource (pool)\tamendment per-slot\tagree")
    for cid, args, ctx, np, kvu, per_slot, amend in CELLS:
        want, n_parallel, kv_unified = predict(ctx, N_CTX_TRAIN, np, kvu, per_slot)
        pool = mod.pad256(ctx if ctx else N_CTX_TRAIN)
        if amend is None:
            agree = "N/A (amendment: unknown, recorded as observed)"
        else:
            agree = "yes" if want == amend else "NO"
        print(f"{cid}\t{want}\t{pool}\t{amend}\t{agree}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
