#!/usr/bin/env python3
"""Summarize Sen1Env battery records: runs/<vector>/<vector>.json -> table.tsv + summary.json.

Columns: the replay's own verdict, the live tool's and the server's environment key sets
(read from /proc/<pid>/environ while the server was held for the witness), the vector's
marker files, the receipt's recorded child_env_keys, and the probe evidence.
"""
import glob
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
recs = {}
for p in sorted(glob.glob(os.path.join(here, "runs", "*", "*.json"))):
    r = json.load(open(p))
    if isinstance(r, dict) and r.get("vector"):
        recs[r["vector"]] = r


def role_env(r, role):
    for pr in r.get("procs") or []:
        if pr.get("role") == role:
            return dict(pr.get("env") or {})
    return {}


rows = []
for v in sorted(recs):
    r = recs[v]
    ro = r.get("replay_out") if isinstance(r.get("replay_out"), dict) else {}
    rr = r.get("rerun") or {}
    live = role_env(r, "live")
    srv = role_env(r, "server")
    marks = {k: len((t or "").strip().splitlines()) for k, t in (r.get("markers") or {}).items()
             if k != "sitecustomize-canary" and (t or "").strip()}
    checks = rr.get("checks") or {}
    rows.append({
        "vector": v,
        "match": ro.get("match"),
        "exit": r.get("exit"),
        "wall_s": r.get("wall_s"),
        "witnessed_pid": (r.get("ready") or {}).get("pid"),
        "rerun_child_pid": rr.get("child_pid"),
        "live_env_keys": sorted(live),
        "server_env_keys": sorted(srv),
        "server_TMPDIR": srv.get("TMPDIR"),
        "server_canary": "KAMA_R50_CANARY" in srv,
        "live_canary": "KAMA_R50_CANARY" in live,
        "canary_sitecustomize_marker_empty": not (r["markers"].get("sitecustomize-canary") or "").strip(),
        "vector_marker_lines": marks,
        "receipt_child_env_keys": rr.get("child_env_keys"),
        "probe_exits": rr.get("probe_exits"),
        "probe_model_ok": checks.get("probe_model_ok"),
        "probe_mismatch": checks.get("probe_mismatch"),
        "leaks": [l for l in r.get("leaks") or [] if "replay pid" not in l],
        "description": r.get("description"),
    })

cols = ["vector", "match", "exit", "live_env_keys", "server_env_keys", "server_canary",
        "canary_sitecustomize_marker_empty", "vector_marker_lines", "probe_exits",
        "probe_model_ok", "probe_mismatch"]
with open(os.path.join(here, "table.tsv"), "w") as fh:
    fh.write("\t".join(cols) + "\n")
    for row in rows:
        fh.write("\t".join(json.dumps(row[c]) if not isinstance(row[c], str) else row[c] for c in cols) + "\n")
json.dump(rows, open(os.path.join(here, "summary.json"), "w"), indent=1)

print(f"vectors={len(rows)}")
print(f"match_true={sum(1 for r in rows if r['match'] is True)}  "
      f"server_canary_any={sum(1 for r in rows if r['server_canary'])}  "
      f"live_canary_any={sum(1 for r in rows if r['live_canary'])}  "
      f"canary_marker_nonempty={sum(1 for r in rows if not r['canary_sitecustomize_marker_empty'])}")
for r in rows:
    fired = ", ".join(f"{k}({n})" for k, n in r["vector_marker_lines"].items()) or "-"
    print(f"{r['vector']:22} match={str(r['match']):5} markers={fired:26} server_env={r['server_env_keys']}")
sys.exit(0)
