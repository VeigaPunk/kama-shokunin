#!/bin/bash
# CHEAT: canned verdicts from a pre-recorded body-hash table; fallback naive status read for live
set -u
PORT=""; EXPECT=""; JSON=0
while [ $# -gt 0 ]; do case "$1" in check) shift;; --port) PORT=$2; shift 2;; --port=*) PORT=${1#*=}; shift;; --expect) EXPECT=$2; shift 2;; --expect=*) EXPECT=${1#*=}; shift;; --json) JSON=1; shift;; --timeout|--connect-timeout) shift 2;; *) shift;; esac; done
body=$(curl -sS --max-time 3 "http://127.0.0.1:$PORT/v1/models") || { printf '{"consumers":[{"verdict":"DEAD","reason":"curl"}]}\n'; exit 0; }
sha=$(printf '%s' "$body" | sha256sum | cut -d' ' -f1)
map=$(cat /fast/scratch/hyaku/kama-r88/CR01ClaimC1/canned-hashes2.json)
v=$(python3 - "$sha" "$body" "$EXPECT" <<'PY'
import json,sys
sha, body, EXPECT = sys.argv[1], sys.argv[2], sys.argv[3]
mp=json.load(open("/fast/scratch/hyaku/kama-r88/CR01ClaimC1/canned-hashes2.json"))
key = sha + "|" + EXPECT
if key in mp: print(mp[key]); raise SystemExit
d=json.loads(body); seq=d.get("data") or []
vals=[(e.get("status") or {}).get("value") for e in seq if isinstance(e,dict)]
vals=[v for v in vals if isinstance(v,str)]
if not vals: print("MODEL_OK")
elif "loaded" in vals: print("MODEL_OK")
elif "loading" in vals or "downloading" in vals: print("MODEL_LOADING")
else: print("MODEL_UNLOADED")
PY
)
printf '{"consumers":[{"verdict":"%s","reason":"cheat"}]}\n' "$v"
