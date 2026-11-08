#!/usr/bin/env bash
# SN01Bounds: exact reproduction of the candidate probe's errexit abort in `consumers` and
# `listeners` (a C3-candidate regression). Stub answers /v1/models with one unloaded entry and
# /props with either non-JSON (unread) or an explicit models_autoload:false (off).
set -uo pipefail
S=/fast/scratch/hyaku/kama-r99/SN01Bounds
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
W="$S/regress"; rm -rf "$W"; mkdir -p "$W"

cat > "$W/stub.py" <<'PY'
import http.server, json, sys
MODEL_FILE, PROPS_KIND = sys.argv[1], sys.argv[2]
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/v1/models":
            body = json.dumps({"object":"list","data":[{"id":"fixture-model",
                "status":{"value":"unloaded","args":[MODEL_FILE,"-m",MODEL_FILE]}}]}).encode()
            ct = "application/json"
        elif p == "/props":
            if PROPS_KIND == "nonjson":
                body, ct = b"<html>not json</html>", "text/html"
            else:
                body, ct = b'{"role":"router","models_autoload":false}', "application/json"
        else:
            body, ct = b"{}", "application/json"
        self.send_response(200); self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body))); self.end_headers()
        try: self.wfile.write(body)
        except OSError: pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
srv.daemon_threads = True
print(srv.server_address[1], flush=True)
srv.serve_forever()
PY

printf 'GGUF\x03\x00\x00\x00%.0s' $(seq 1 8) > "$W/model.gguf"
CAND="$LANE/.ufo/waves/round-99/candidates/kama-probe.r99.sh"
BASE="$W/probe-base.sh"
( cd "$LANE" && git show 439fdb3d41b55e5b9e6d7c480d17f2c428bae978:tools/kama-probe.sh ) > "$BASE"
printf 'id\tconsumer_path\tresolver\tdeclared_baseurl\texpected\tnotes\n' > "$W/registry.tsv"

for kind in nonjson off; do
  python3 "$W/stub.py" "$W/model.gguf" "$kind" > "$W/port.txt" 2>/dev/null &
  STUB=$!
  for i in $(seq 1 100); do [ -s "$W/port.txt" ] && break; sleep 0.1; done
  PORT=$(cat "$W/port.txt")
  echo "############ /props=$kind stub=127.0.0.1:$PORT"
  for name in BASE CAND; do
    P=$BASE; [ "$name" = CAND ] && P=$CAND
    for sub in check consumers listeners; do
      TMPDIR="$W" bash "$P" "$sub" --port "$PORT" --expect fixture-model --json \
        --registry "$W/registry.tsv" > "$W/o" 2> "$W/e"
      rc=$?
      printf '  %-4s %-9s rc=%s stdout=%sB stderr=%sB  %s\n' "$name" "$sub" "$rc" \
        "$(wc -c < "$W/o")" "$(wc -c < "$W/e")" \
        "$(grep -o '"verdict": *"[^"]*"' "$W/o" | head -1)"
      [ -s "$W/e" ] && sed 's/^/        stderr: /' "$W/e" | head -3
    done
  done
  kill "$STUB" 2>/dev/null; wait "$STUB" 2>/dev/null
done
echo DONE
