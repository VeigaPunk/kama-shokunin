#!/usr/bin/env bash
# RV01ProbeDiff driver 2: no-python3 path, listeners registration, snapshot ledger.
set -u
SCR=/fast/scratch/hyaku/kama-r88/RV01ProbeDiff
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-88/w1/out/RV01ProbeDiff
PROBE=$SCR/kama-probe-I.sh
STUB=$OUT/stub_router.py
export TMPDIR=$SCR/tmp

# --- start one unloaded stub in the background (normal PATH), publish port
python3 - "$SCR" <<'PY' &
import http.server, json, pathlib, sys, sysconfig
body = json.dumps({"object": "list", "data": [
    {"id": "m1", "object": "model", "owned_by": "llamacpp",
     "status": {"value": "unloaded"}}]}).encode()
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/v1/models":
            out, ct = body, "application/json; charset=utf-8"
        elif p == "/health":
            out, ct = b'{"status":"ok"}', "application/json; charset=utf-8"
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)
    def version_string(self): return "llama.cpp"
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
pathlib.Path(sys.argv[1] + "/stubport").write_text(str(srv.server_address[1]))
srv.serve_forever()
PY
STUB_PID=$!
for _ in $(seq 1 100); do [ -s "$SCR/stubport" ] && break; sleep 0.05; done
PORT=$(cat "$SCR/stubport")
trap 'kill $STUB_PID 2>/dev/null' EXIT
echo "stub port=$PORT pid=$STUB_PID"

echo "--- 1) no-python3: same stub, PATH without python3"
env PATH="$SCR/nopy" bash "$PROBE" check --port "$PORT" --expect m1 --json > "$SCR/nopy.json" 2> "$SCR/nopy.err"
echo "nopy rc=$?"
grep -E '"verdict"|"reason"|"served_model"|"drift"' "$SCR/nopy.json" | head -4
grep -o 'python3 not found[^"]*' "$SCR/nopy.err" | head -1
env PATH="$SCR/nopy" bash "$PROBE" check --port "$PORT" --expect m1 > "$SCR/nopy.table" 2>&1
echo "nopy-table rc=$?"; grep -E 'MODEL_|registry_rows' "$SCR/nopy.table"

echo "--- 2) listeners --port (override), no registry override -> reg expected 'no'"
bash "$PROBE" listeners --port "$PORT" --expect m1 --json > "$SCR/lis.json" 2>/dev/null
echo "listeners rc=$?"
python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
r=d["listeners"][0]
print("verdict",r["verdict"],"reason",r["reason"],"registered",r["registered"],"served",r["served_model"])
print("summary",{k:v for k,v in d["summary"].items() if k in("probed","model_endpoints","model_loading","governed","unregistered")})
print("vocab",d["verdict_vocabulary"])
' "$SCR/lis.json"

echo "--- 3) listeners with scratch registry declaring the port -> reg expected 'yes'"
PIN="$SCR/pin.txt"; REG="$SCR/reg.tsv"; CLEAN="http://127.0.0.1:$PORT/v1"
printf 'http://user:pass@127.0.0.1:%s/v1?api_key=fixture-secret\n' "$PORT" > "$PIN"
printf 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n' > "$REG"
printf 'rv1-router\t%s\tgrep:http://[^ ]+\t%s\tm1\tRV01 scratch fixture\n' "$PIN" "$CLEAN" >> "$REG"
bash "$PROBE" listeners --port "$PORT" --expect m1 --registry "$REG" --json > "$SCR/lis2.json" 2>/dev/null
echo "listeners-reg rc=$?"
python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
r=d["listeners"][0]
print("verdict",r["verdict"],"registered",r["registered"])
print("summary",{k:v for k,v in d["summary"].items() if k in("model_endpoints","governed","unregistered")})
' "$SCR/lis2.json"

echo "--- 4) snapshot ledger: registry mode (snapshot refuses --port)"
HIST="$SCR/hist"; rm -rf "$HIST"
bash "$PROBE" check --registry "$REG" > "$SCR/chk1.out" 2>&1; echo "check rc=$? (expect 2)"
grep -E 'MODEL_|registry_rows' "$SCR/chk1.out"
bash "$PROBE" snapshot --registry "$REG" --history "$HIST" > "$SCR/snap1.out" 2>&1; echo "snap1 rc=$? (expect 2, baseline)"
grep -E 'MODEL_|snapshot=' "$SCR/snap1.out"
bash "$PROBE" snapshot --json --registry "$REG" --history "$HIST" > "$SCR/snap2.out" 2>&1; echo "snap2 rc=$? (expect 2, stable)"
python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
print("summary",d["summary"]); r=d["rows"][0]
print("row verdict",r["verdict"],"reason",r["reason"],"served",r["served_model"],"drift",r["drift"])
' "$SCR/snap2.out"
echo "DELTA.md:"; cat "$HIST/DELTA.md"
echo "latest.tsv:"; cat "$HIST/latest.tsv"
