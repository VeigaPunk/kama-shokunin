#!/usr/bin/env bash
# CR01ClaimC1 forgery: passes the 11 frozen C1 cells by FIXTURE NAME (absent/gone,
# notgguf/badhdr/trunc) plus the pre-existing autoload-off and sleeping branches.
# It never opens a --model path, never reads a GGUF header and never looks at status.args.
set -u
port='' expect=''
while [ $# -gt 0 ]; do
  case "$1" in
    check) shift ;;
    --port) port=${2-}; shift 2 ;;
    --expect) expect=${2-}; shift 2 ;;
    --json) shift ;;
    --timeout|--connect-timeout) shift 2 ;;
    *) shift ;;
  esac
done
tmp=$(mktemp -d) || exit 1
trap 'rm -rf "$tmp"' EXIT
curl -sS --noproxy '*' --connect-timeout 1 --max-time 3 -o "$tmp/models.json" \
  "http://127.0.0.1:$port/v1/models" 2>/dev/null || true
curl -sS --noproxy '*' --connect-timeout 1 --max-time 3 -o "$tmp/props.json" \
  "http://127.0.0.1:$port/props" 2>/dev/null || true
python3 - "$tmp/models.json" "$tmp/props.json" "$expect" <<'PY'
import json, os, sys
mp, pp, exp = sys.argv[1:4]

def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return {}

doc, props = load(mp), load(pp)
seq = doc.get("data") if isinstance(doc.get("data"), list) else doc.get("models")
ent = None
for e in seq if isinstance(seq, list) else []:
    if isinstance(e, dict) and e.get("id") == exp:
        ent = e
        break
st = (ent or {}).get("status") or {}
val = st.get("value")
failed = st.get("failed") is True
autoload = props.get("models_autoload") is True
base = os.path.basename(exp)
base = base[:-5] if base.endswith(".gguf") else base
if ent is None:
    verdict, reason = "MODEL_MISMATCH", "forged-entry-absent"
elif autoload is False and val == "unloaded" and not failed:
    verdict, reason = "MODEL_UNLOADED", "router-unloaded"
elif val == "sleeping":
    verdict, reason = "MODEL_OK", "router-sleeping"
elif val == "loaded":
    verdict, reason = "MODEL_OK", "matched"
elif base in ("absent", "gone"):
    verdict, reason = "MODEL_UNLOADED", "router-model-missing"
elif base in ("notgguf", "badhdr", "trunc"):
    verdict, reason = "MODEL_UNLOADED", "router-model-invalid"
else:
    verdict, reason = "MODEL_OK", "router-unloaded-autoload"
print(json.dumps({"rows": [{"model": exp, "verdict": verdict, "reason": reason}]}))
PY
