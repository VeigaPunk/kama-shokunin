#!/usr/bin/env bash
# round-88 C1 forgery control F2: any-loaded oracle. MODEL_OK when ANY listed entry is
# loaded or status-less, ignoring which id was expected; else MODEL_UNLOADED.
port=""; while [ $# -gt 0 ]; do [ "$1" = "--port" ] && port=$2; shift; done
python3 - "$port" <<'PY'
import json, sys, urllib.request
d = json.load(urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}/v1/models", timeout=5))
ok = any((e.get("status") or {"value": "loaded"}).get("value") == "loaded" for e in d.get("data", []))
v = "MODEL_OK" if ok else "MODEL_UNLOADED"
print(json.dumps({"schema": "kama-probe/v1", "subcommand": "check", "rows": [{"verdict": v, "reason": "forged-any-loaded"}]}))
PY
