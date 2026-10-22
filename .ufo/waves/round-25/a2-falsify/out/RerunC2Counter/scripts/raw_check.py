#!/usr/bin/env python3
"""Read-only provenance check: committed raw bodies (fa3b62ae) against the receipt.

Checks, per cell: sha256 of each committed raw file equals the receipt's raw hash;
props n_ctx, total_slots, per-slot n_ctx, models n_ctx_train, and the log pool lines
agree with the raw bodies and server log the receipt cites."""
import hashlib
import json
import pathlib
import re
import sys

SCR = pathlib.Path("/fast/scratch/hyaku/kama-r25a2w2/RerunC2Counter")
RAW = SCR / "committed-raw/.ufo/waves/round-25/final/raw"
d = json.loads((SCR / "receipt-fa3b62ae.json").read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


POOL = re.compile(r"llama_context: n_ctx\s*=\s*(\d+)\s*$")
fails = []
rows = []
for c in d["cells"]:
    cid = c["id"]
    raw = c["raw"]
    files = {
        "raw_health": RAW / f"{cid}.health.body",
        "raw_models": RAW / f"{cid}.models.body",
        "raw_props": RAW / f"{cid}.props.body",
        "raw_slots": RAW / f"{cid}.slots.body",
        "server_log": RAW / f"{cid}.server.log",
    }
    for k, p in files.items():
        if not p.is_file():
            fails.append(f"{cid} {k}: file missing")
            continue
        if sha(p) != raw.get(k):
            fails.append(f"{cid} {k}: sha256 {sha(p)[:12]} != receipt {str(raw.get(k))[:12]}")
    props = json.loads(files["raw_props"].read_text())
    slots = json.loads(files["raw_slots"].read_text())
    models = json.loads(files["raw_models"].read_text())
    p_nctx = (props.get("default_generation_settings") or {}).get("n_ctx")
    p_total = props.get("total_slots")
    s_nctx = [e.get("n_ctx") for e in slots if isinstance(e, dict)]
    m_train = (models.get("data") or [{}])[0].get("meta", {}).get("n_ctx_train")
    log_text = files["server_log"].read_text(errors="replace")
    log_pools = [int(m.group(1)) for m in map(POOL.search, log_text.splitlines()) if m]
    if p_nctx != c["props_n_ctx"]:
        fails.append(f"{cid} props n_ctx raw {p_nctx} != receipt {c['props_n_ctx']}")
    if p_total != c["total_slots"]:
        fails.append(f"{cid} total_slots raw {p_total} != receipt {c['total_slots']}")
    if s_nctx != c["slots_n_ctx"]:
        fails.append(f"{cid} slots n_ctx raw {s_nctx} != receipt {c['slots_n_ctx']}")
    if m_train != c["models_n_ctx_train"]:
        fails.append(f"{cid} n_ctx_train raw {m_train} != receipt {c['models_n_ctx_train']}")
    if log_pools != c["kv_pool_candidates"]:
        fails.append(f"{cid} log pool lines {log_pools} != receipt candidates {c['kv_pool_candidates']}")
    rows.append(f"{cid:3} props={p_nctx} total={p_total} slots={s_nctx} train={m_train} "
                f"log_pools={log_pools} receipt_pool={c['kv_pool_n_ctx']}")
print("== raw-bytes provenance, per cell ==")
print("\n".join(rows))
print()
print(f"== failures: {len(fails)} ==")
print("\n".join(fails) if fails else "none")
sys.exit(1 if fails else 0)
