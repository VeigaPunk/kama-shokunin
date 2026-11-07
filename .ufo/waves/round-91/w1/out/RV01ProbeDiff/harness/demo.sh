#!/usr/bin/env bash
# Demo 1: no SIGPIPE (141) anywhere in the new model_matches pipeline under pipefail.
# Demo 2: awk-absent degradation: base grades correctly, M fails closed (MODEL_MISMATCH).
set -u
S=$(cd "$(dirname "$0")" && pwd)
source "$S/lib/libM.sh"
python3 - "$S/served-big.txt" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_text("\n".join(["id%06d" % i for i in range(200000)] + ["id000002"]))
PY
served=$(cat "$S/served-big.txt")
set -o pipefail
rc=0
model_matches "$served" "id000002" || rc=$?
printf 'SIGPIPE_DEMO rc=%s (141 would be SIGPIPE)\n' "$rc"
rc=0
model_matches "$served" "absent-id" || rc=$?
printf 'SIGPIPE_DEMO_MISS rc=%s\n' "$rc"
unset pipefail; set +o pipefail

# Demo 2: PATH without awk
NP=$S/nopath; mkdir -p "$NP"
for b in python3 curl mktemp grep sed tr paste wc head tail cat sort uniq od basename dirname sha256sum sleep env uname id getent mktemp rm cp chmod ln mkdir rmdir; do
  p=$(command -v "$b" 2>/dev/null) && ln -sf "$p" "$NP/$b"
done
cat > "$S/stub.py" <<'PY'
import http.server, json, threading
body = json.dumps({"object": "list", "data": [{"id": "good"}]}).encode()
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
print(srv.server_address[1], flush=True)
srv.serve_forever()
PY
python3 "$S/stub.py" > "$S/port.txt" &
STUB=$!
sleep 0.6
PORT=$(cat "$S/port.txt")
for v in B M; do
  out=$(PATH="$NP" TMPDIR="$S" bash "$S/revs/probe-$v.sh" check --port "$PORT" --expect good --json --timeout 5 --connect-timeout 2 2>/dev/null \
    | python3 -c 'import json,sys; r=json.load(sys.stdin)["rows"][0]; print(r["verdict"], r["reason"])')
  rc=$?
  printf 'NOPATH %s exit=%s -> %s\n' "$v" "$rc" "$out"
done
kill "$STUB" 2>/dev/null
wait "$STUB" 2>/dev/null
exit 0
