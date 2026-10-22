#!/usr/bin/env python3
"""Compare round-20 nctx-crosscheck.py predict() (imported unchanged) with the attempt-2
sibling observations in a2-build/out/ExecRawReplicate/receipt-config-cells.json.
r20_pool is the pool implied by the round-20 model (pad256(ctx or n_ctx_train), split-adjusted);
predict() itself returns only the per-slot value. Read-only; starts no server."""
import importlib.util, json
s = importlib.util.spec_from_file_location("r20", ".ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
obs = {c["id"]: c for c in json.load(open(".ufo/waves/round-25/a2-build/out/ExecRawReplicate/receipt-config-cells.json"))["cells"]}
T = 2048
print("cell args r20_slot obs_slot slot_agree r20_pool obs_pool pool_agree")
for cid, c in obs.items():
    g = m.launch_settings(["x"] + [a for a in c["args"].split() if a not in ("--fit", "off")], [])
    slot, np_, uni = m.predict(g["ctx"], T, g["np"], g["kvu"], g["per_slot"])
    n = m.pad256(g["ctx"] or T)
    pool = n if uni else m.pad256(n // np_) * np_
    print(cid, repr(c["args"]), slot, c["props_n_ctx"], "yes" if slot == c["props_n_ctx"] else "NO",
          pool, c["kv_pool_n_ctx"], "yes" if pool == c["kv_pool_n_ctx"] else "NO")
