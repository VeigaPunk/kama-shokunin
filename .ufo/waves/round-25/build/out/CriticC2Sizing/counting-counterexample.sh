#!/usr/bin/env bash
# Runs the registered C2 counting command and a bound alternative against synthetic receipts.
# Synthetic trees live under the scratch dir; the lane is never written.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r25/CriticC2Sizing/receipts
REG=$(python3 -c "import json;print([c for c in json.load(open('$LANE/.ufo/waves/round-25/preregistration.json'))['claims'] if c['id']=='C2'][0]['command'])")
BOUND='import json;p=[c for c in json.load(open(".ufo/waves/round-25/preregistration.json"))["claims"] if c["id"]=="C2"][0]["cells"];d=json.load(open(".ufo/waves/round-25/final/context-capacity-receipt.json"));r=d["cells"];I=lambda v:type(v) is int;ok=[x for x in r if I(x.get("props_n_ctx")) and I(x.get("props_total_slots")) and isinstance(x.get("slots_n_ctx"),list) and len(x["slots_n_ctx"])==x["props_total_slots"] and all(map(I,x["slots_n_ctx"])) and I(x.get("models_n_ctx_train")) and "n_ctx_slot = " in str(x.get("log_line",""))];print("bound",[(c["id"],c["args"]) for c in p]==[(x.get("id"),x.get("args")) for x in r],"server",d.get("server_version"),"model_sha256",d.get("model_sha256"),"cells",len(r),"observed",len(ok))'

mk() { mkdir -p "$S/$1/.ufo/waves/round-25" "$S/$1/.ufo/waves/round-25/final"; cp "$LANE/.ufo/waves/round-25/preregistration.json" "$S/$1/.ufo/waves/round-25/"; }

mk failed-starts
python3 - "$S/failed-starts" <<'EOF'
import json, sys
cells = [{"id": f"K{i}", "observed": "server exited before /props answered"} for i in range(1, 9)]
json.dump({"cells": cells}, open(sys.argv[1] + "/.ufo/waves/round-25/final/context-capacity-receipt.json", "w"))
EOF

mk nine-cells
python3 - "$S/nine-cells" <<'EOF'
import json, sys
cells = [{"id": "K1", "observed": True}] * 2 + [{"id": f"K{i}", "observed": True} for i in range(2, 8)] + [{"id": "K8", "observed": False}]
json.dump({"cells": cells}, open(sys.argv[1] + "/.ufo/waves/round-25/final/context-capacity-receipt.json", "w"))
EOF

mk shaped
python3 - "$S/shaped" "$LANE" <<'EOF'
import json, sys
pre = [c for c in json.load(open(sys.argv[2] + "/.ufo/waves/round-25/preregistration.json"))["claims"] if c["id"] == "C2"][0]["cells"]
cells = [{"id": c["id"], "args": c["args"], "observed": True, "props_n_ctx": 2048, "props_total_slots": 1,
          "slots_n_ctx": [2048], "models_n_ctx_train": 2048,
          "log_line": "load_model: initializing, n_slots = 1, n_ctx_slot = 2048, kv_unified = 'false'"} for c in pre]
json.dump({"server_version": "build 11755, commit 704366d76", "model_sha256": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d", "cells": cells},
          open(sys.argv[1] + "/.ufo/waves/round-25/final/context-capacity-receipt.json", "w"))
EOF

for t in failed-starts nine-cells shaped; do
  echo "== $t registered"; (cd "$S/$t" && sh -c "$REG"); echo "exit $?"
  echo "== $t bound";      (cd "$S/$t" && python3 -c "$BOUND"); echo "exit $?"
done
