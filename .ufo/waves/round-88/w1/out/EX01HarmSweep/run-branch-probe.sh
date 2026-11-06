#!/bin/bash
# EX01HarmSweep targeted branch probe: does the round-88 router refinement reach the
# three subcommands that changed (check, snapshot baseline vocabulary, listeners)?
# Hermetic: own loopback stub per cell, own temp dir under TMPDIR, no external endpoint.
# usage: run-branch-probe.sh <rev> <label>
set -u
rev="$1"; label="$2"
S=/fast/scratch/hyaku/kama-r88/EX01HarmSweep
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-88/w1/out/EX01HarmSweep
WT="$S/wt"
mkdir -p "$OUT/$label"
export TMPDIR="$S/tmp-branch-$label"; mkdir -p "$TMPDIR"
cd "$WT" || exit 9
git checkout --detach "$rev" > "$OUT/$label/branch-checkout.out" 2>&1 || exit 9
git rev-parse HEAD > "$OUT/$label/branch-head.txt"

cat > "$S/stub.py" <<'PY'
import http.server, json, pathlib, sys
VALUE = sys.argv[1]          # 'none' = single-model body without any status object
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/v1/models"):
            if VALUE == "none":
                body = {"data": [{"id": "stories260K"}]}
            else:
                body = {"data": [{"id": "stories260K",
                                  "status": {"value": VALUE, "failed": VALUE in ("unloaded", "incomplete")}}]}
            raw = json.dumps(body).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        elif self.path.startswith("/health"):
            raw = b'{"status":"ok"}'
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        else:
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers()
    def log_message(self, *_): pass
srv = http.server.HTTPServer(("127.0.0.1", 0), H)
pathlib.Path(sys.argv[2]).write_text(str(srv.server_port))
srv.serve_forever()
PY

W=$(mktemp -d -p "$TMPDIR" cell.XXXXXX); PID=''
cleanup() { [ -n "$PID" ] && { kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; }; rm -rf -- "$W"; }
trap cleanup EXIT INT TERM

cell() { # $1 cell name, $2 status value
  name="$1"; value="$2"
  : > "$W/port"
  python3 "$S/stub.py" "$value" "$W/port" & PID=$!
  for _ in $(seq 1 200); do [ -s "$W/port" ] && break; sleep 0.02; done
  [ -s "$W/port" ] || { echo "$name STUB-FAILED"; return 1; }
  PORT=$(cat "$W/port")
  REG="$W/registry.tsv"; HIST="$W/history-$name"; rm -rf "$HIST"
  PIN="$W/pin.txt"
  printf 'http://127.0.0.1:%s/v1?api_key=stub-secret\n' "$PORT" > "$PIN"
  printf 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n' > "$REG"
  printf 'probe-row\t%s\tgrep:http://[^ ]+\thttp://127.0.0.1:%s/v1\tstories260K\t-\n' "$PIN" "$PORT" >> "$REG"
  echo "== cell=$name status=$value port=$PORT"
  bash tools/kama-probe.sh check --registry "$REG" --json > "$W/check-$name.json" 2>&1
  echo "check rc=$? verdict=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); r=d["rows"][0]; print(r["verdict"]+"/"+r["reason"])' "$W/check-$name.json" 2>/dev/null || echo UNPARSED)"
  bash tools/kama-probe.sh listeners --port "$PORT" --registry "$REG" --json > "$W/listeners-$name.json" 2>&1
  echo "listeners rc=$? verdict=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); r=d["listeners"][0]; s=d["summary"]; print(r["verdict"]+"/"+r["reason"]+" model_endpoints="+str(s["model_endpoints"])+" registered="+str(r["registered"]))' "$W/listeners-$name.json" 2>/dev/null || echo UNPARSED)"
  bash tools/kama-probe.sh snapshot --registry "$REG" --history "$HIST" > "$W/snap1-$name.out" 2>&1
  echo "snapshot1 rc=$? $(tail -1 "$W/snap1-$name.out")"
  bash tools/kama-probe.sh snapshot --registry "$REG" --history "$HIST" > "$W/snap2-$name.out" 2>&1
  echo "snapshot2 rc=$? $(tail -1 "$W/snap2-$name.out")"
  echo "baseline-row: $(grep '^probe-row' "$HIST/latest.tsv" 2>/dev/null | tr '\t' '|')"
  echo "malformed-warn-1: $(grep -c 'dropping malformed baseline row' "$W/snap1-$name.out")"
  echo "malformed-warn-2: $(grep -c 'dropping malformed baseline row' "$W/snap2-$name.out")"
  echo "delta2: $(grep -c 'probe-row' "$HIST/DELTA.md" 2>/dev/null)"
  cp "$W/check-$name.json" "$OUT/$label/branch-$name-check.json" 2>/dev/null
  cp "$W/listeners-$name.json" "$OUT/$label/branch-$name-listeners.json" 2>/dev/null
  cp "$W/snap1-$name.out" "$W/snap2-$name.out" "$OUT/$label/" 2>/dev/null
  cp "$HIST/latest.tsv" "$OUT/$label/branch-$name-latest.tsv" 2>/dev/null
  cp "$HIST/DELTA.md" "$OUT/$label/branch-$name-DELTA.md" 2>/dev/null
  kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; PID=''
}

cell unloaded  unloaded
cell loading   loading
cell loaded    loaded
cell sleeping  sleeping
cell singleno  none
