import json
import re
import sys

path = sys.argv[1]
d = json.load(open(path))


def show(label, value, limit=600):
    text = json.dumps(value, ensure_ascii=False)
    print(f"{label}: {text[:limit]}{' ...[cut %d]' % len(text) if len(text) > limit else ''}")


print("== top level ==")
for k in sorted(d.keys()):
    if k == "cells":
        continue
    show(k, d[k])

print()
print("== cells ==", len(d["cells"]))
keys = [
    "args", "observed", "error", "teardown", "port", "started_utc", "stopped_utc",
    "server_sha256", "model_sha256", "models_n_ctx_train", "props_n_ctx", "total_slots",
    "slots_n_ctx", "kv_pool_n_ctx", "kv_pool_candidates", "request_mode",
    "concurrency_delta_s", "requests",
]
for c in d["cells"]:
    print()
    print("---", c.get("id"))
    for k in keys:
        show("  " + k, c.get(k), 400)
    show("  argv", c.get("argv"), 500)
    raw = c.get("raw")
    print(f"  raw: type={type(raw).__name__} " + (f"keys={sorted(raw.keys())}" if isinstance(raw, dict) else f"len={len(raw) if raw is not None else None}"))
    lines = c.get("log_lines") or []
    print(f"  log_lines: {len(lines)}")
    for x in lines:
        if re.search(r"llama_context: n_ctx|n_slots|error|fail|abort|exit|warn|round|kv_unified|slot|exceed|listen|crash|segm", x, re.I):
            print("   LOG: " + x[:220])
