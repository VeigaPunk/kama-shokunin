#!/usr/bin/env python3
"""ConnectKengaku (kama round 20): list every committed *receipt*.json at REV and
report whether its /v1/models capture carries the engine's header decode
(data[0].meta), with the body re-hashed against captures.models.body_sha256.
Usage: python3 receipts_meta_scan.py LANE REV"""
import hashlib, json, subprocess, sys

lane, rev = sys.argv[1:3]
names = subprocess.run(["git", "-C", lane, "ls-tree", "-r", "--name-only", rev],
                       check=True, capture_output=True, text=True).stdout.split()
rows = []
for p in sorted(n for n in names if n.rsplit("/", 1)[-1].startswith("receipt") and n.endswith(".json")):
    d = json.loads(subprocess.run(["git", "-C", lane, "show", f"{rev}:{p}"], check=True, capture_output=True).stdout)
    m = (d.get("captures") or {}).get("models") or {}
    body, meta, ok = m.get("body"), None, None
    if isinstance(body, str):
        ok = hashlib.sha256(body.encode()).hexdigest() == m.get("body_sha256")
        meta = json.loads(body)["data"][0].get("meta")
    rows.append({"path": p, "schema": d.get("schema"), "model_sha256_post": d.get("model_sha256_post"),
                 "argv_has_override_kv": "--override-kv" in (d.get("argv") or []),
                 "models_body_sha256_ok": ok, "meta": meta})
for r in rows:
    print(json.dumps(r, sort_keys=True))
live = [r for r in rows if r["schema"]]
print(json.dumps({"receipts": len(rows), "live_receipts": len(live),
                  "live_with_meta_and_sha_ok": sum(1 for r in live if r["meta"] and r["models_body_sha256_ok"]),
                  "distinct_meta": len({json.dumps(r["meta"], sort_keys=True) for r in live}),
                  "distinct_model_sha256_post": len({r["model_sha256_post"] for r in live})}))
