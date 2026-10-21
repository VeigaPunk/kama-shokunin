#!/bin/sh
# Markers and the 401 server used to prove which repo-local config channels run
# during a promisor lazy fetch. Set B to a scratch dir under /tmp.
set -u
B=${B:?set B to a scratch dir}
mk(){ printf '#!/bin/sh\necho "%s $*" >> %s/marker.log\nexit %s\n' "$1" "$B" "$2" > "$B/$3"; chmod +x "$B/$3"; }
mk failmark 127 failmark     # remote.<name>.uploadpack -> fails the fetch
mk sshmark  255 sshmark      # core.sshCommand -> logs then fails
mk proxymark 127 proxymark   # core.gitProxy -> logs then fails
mk credmark 1 credmark       # credential.helper=!<script> -> logs on HTTP 401
printf '#!/bin/sh\necho "realmark $*" >> %s/marker.log\nexec git-upload-pack "$@"\n' "$B" > "$B/realmark"
chmod +x "$B/realmark"       # succeeds, so lazy fetch can actually resolve an object
printf '#!/bin/sh\necho "extmark $*" >> %s/marker.log\nexit 1\n' "$B" > "$B/extmark"; chmod +x "$B/extmark"
cat > "$B/srv401.py" <<'PY'
import http.server
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(401); self.send_header("WWW-Authenticate", 'Basic realm="x"'); self.end_headers()
    def log_message(self, *a): open("/tmp/kama-r23-lf/srv401.log", "a").write(self.path + "\n")
http.server.HTTPServer(("127.0.0.1", 38471), H).serve_forever()
PY
echo "markers ready in $B; run: python3 $B/srv401.py &"
