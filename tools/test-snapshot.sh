#!/usr/bin/env bash
# Hermetic behavioral checks for `kama-probe.sh snapshot`.
set -euo pipefail
umask 077

SELF_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROBE=${KAMA_PROBE:-$SELF_DIR/kama-probe.sh}
[ -f "$PROBE" ] || { printf 'FAIL probe missing: %s\n' "$PROBE" >&2; exit 1; }
for dep in curl flock python3 ss; do
  command -v "$dep" >/dev/null 2>&1 || { printf 'FAIL missing dependency: %s\n' "$dep" >&2; exit 1; }
done

WORK=$(mktemp -d "${TMPDIR:-/tmp}/kama-snapshot-test.XXXXXX")
FIXTURE_PID=''
PASS=0
FAIL=0
cleanup() {
  if [ -n "$FIXTURE_PID" ]; then
    kill "$FIXTURE_PID" 2>/dev/null || true
    wait "$FIXTURE_PID" 2>/dev/null || true
  fi
  rm -rf -- "$WORK"
}
trap cleanup EXIT INT TERM
ok() { PASS=$((PASS+1)); printf 'PASS %s\n' "$*"; }
bad() { FAIL=$((FAIL+1)); printf 'FAIL %s\n' "$*" >&2; }
assert_file() { [ -f "$1" ] && ok "$2" || bad "$2 (missing $1)"; }
assert_contains() {
  if grep -qE -- "$2" "$1"; then ok "$3"; else bad "$3 (pattern $2 absent)"; fi
}
run_probe() {
  local out=$1
  shift
  set +e
  bash "$PROBE" "$@" >"$out" 2>&1
  RC=$?
  set -e
}

cat > "$WORK/server.py" <<'PY'
import http.server, json, pathlib, sys
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/v1/models":
            body = json.dumps({"data": [{"id": "/tmp/private/fixture-model.gguf"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
    def log_message(self, *_):
        pass
server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
pathlib.Path(sys.argv[1]).write_text(str(server.server_port))
server.serve_forever()
PY

python3 "$WORK/server.py" "$WORK/port" &
FIXTURE_PID=$!
for _ in $(seq 1 100); do
  [ -s "$WORK/port" ] && break
  sleep 0.02
done
[ -s "$WORK/port" ] || { bad "fixture published a port"; exit 1; }
PORT=$(cat "$WORK/port")
PIN="$WORK/pin.txt"
REG="$WORK/registry.tsv"
CLEAN_URL="http://127.0.0.1:$PORT/v1"
printf 'http://user:pass@127.0.0.1:%s/v1?api_key=fixture-secret\n' "$PORT" > "$PIN"
write_registry() {
  local id=$1
  printf 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n' > "$REG"
  printf '%s\t%s\tgrep:http://[^ ]+\t%s\tfixture-model\tSENSITIVE-NOTE\n' \
    "$id" "$PIN" "$CLEAN_URL" >> "$REG"
}
write_registry fixture-a
HIST="$WORK/history"

# Baseline: healthy fixture, exact model match, clean gate.
run_probe "$WORK/check.out" check --registry "$REG"
[ "$RC" -eq 0 ] && ok "check fixture is MODEL_OK/exit 0" || bad "check fixture exit $RC (expected 0)"
run_probe "$WORK/snap1.out" snapshot --json --registry "$REG" --history "$HIST"
[ "$RC" -eq 0 ] && ok "snapshot exit mirrors clean check" || bad "snapshot baseline exit $RC"
assert_file "$HIST/latest.tsv" "baseline TSV written"
assert_file "$HIST/DELTA.md" "transition ledger written"
JSONS=("$HIST"/*.json)
[ "${#JSONS[@]}" -eq 1 ] && ok "one dated JSON written" || bad "expected one dated JSON"
python3 - "${JSONS[0]}" "$WORK/snap1.out" <<'PY' && ok "snapshot JSON contract + redaction" || bad "snapshot JSON contract + redaction"
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
doc = json.loads(p.read_text())
stdout_doc = json.loads(pathlib.Path(sys.argv[2]).read_text())
assert stdout_doc == doc
assert doc["schema"] == "kama-probe/v2"
assert doc["subcommand"] == "snapshot"
assert doc["summary"] == {"registry_rows_evaluated": 1, "model_ok": 1, "drift": 0, "transitions": 0, "exit": 0}
assert len(doc["rows"]) == 1
row = doc["rows"][0]
assert row["served_model"] == "fixture-model"
assert set(row) == {"id", "consumer_path", "port", "expected_model_id", "verdict", "reason", "served_model", "file_match", "drift"}
text = p.read_text()
for forbidden in ("user:pass", "api_key", "fixture-secret", "SENSITIVE-NOTE", "/tmp/private", "resolved_from_file", '"evidence"', '"notes"'):
    assert forbidden not in text, forbidden
PY
BASELINE_ROW=$(grep '^fixture-a' "$HIST/latest.tsv")
EXPECTED_ROW=$(printf 'fixture-a\tMODEL_OK\tmatched\tfixture-model\t%s\tyes' "$PORT")
[ "$BASELINE_ROW" = "$EXPECTED_ROW" ] &&
  ok "baseline fields are normalized and complete" ||
  bad "baseline fields differ: $BASELINE_ROW"
assert_contains "$HIST/DELTA.md" 'baseline recorded \(1 rows\)' "first run records baseline, not transitions"

# Same sampled state: neither tracked artifact mutates and transitions=0.
DELTA_HASH=$(sha256sum "$HIST/DELTA.md" | cut -d' ' -f1)
BASELINE_HASH=$(sha256sum "$HIST/latest.tsv" | cut -d' ' -f1)
run_probe "$WORK/snap2.out" snapshot --registry "$REG" --history "$HIST"
[ "$RC" -eq 0 ] && ok "unchanged snapshot stays exit 0" || bad "unchanged snapshot exit $RC"
assert_contains "$WORK/snap2.out" 'transitions=0 exit=0' "unchanged snapshot reports zero transitions"
DELTA_HASH_2=$(sha256sum "$HIST/DELTA.md" | cut -d' ' -f1)
BASELINE_HASH_2=$(sha256sum "$HIST/latest.tsv" | cut -d' ' -f1)
[ "$DELTA_HASH" = "$DELTA_HASH_2" ] && ok "unchanged snapshot leaves DELTA.md byte-stable" || bad "unchanged snapshot changed DELTA.md"
[ "$BASELINE_HASH" = "$BASELINE_HASH_2" ] && ok "unchanged snapshot leaves latest.tsv byte-stable" || bad "unchanged snapshot changed latest.tsv"

# Endpoint disappears: verdict/reason/served-id net changes are persisted.
kill "$FIXTURE_PID"
wait "$FIXTURE_PID" 2>/dev/null || true
FIXTURE_PID=''
run_probe "$WORK/snap3.out" snapshot --registry "$REG" --history "$HIST"
[ "$RC" -eq 2 ] && ok "dead fixture makes snapshot exit 2" || bad "dead fixture snapshot exit $RC"
assert_contains "$HIST/DELTA.md" 'fixture-a verdict MODEL_OK -> DEAD' "MODEL_OK to DEAD transition recorded"
assert_contains "$HIST/DELTA.md" 'fixture-a served_model fixture-model -> -' "served-id transition recorded"

# Stable-key set changes: added and absent rows are both explicit.
write_registry fixture-b
run_probe "$WORK/snap4.out" snapshot --registry "$REG" --history "$HIST"
[ "$RC" -eq 2 ] && ok "row-set change preserves drift exit 2" || bad "row-set snapshot exit $RC"
assert_contains "$HIST/DELTA.md" 'fixture-b row-added' "row-added transition recorded"
assert_contains "$HIST/DELTA.md" 'fixture-a row-absent' "row-absent transition recorded"

# Malformed trust anchor: warning + audit note + successful rebaseline, never phantom absent.
printf 'garbage garbage garbage\n' > "$HIST/latest.tsv"
run_probe "$WORK/snap5.out" snapshot --registry "$REG" --history "$HIST"
[ "$RC" -eq 2 ] && ok "malformed baseline rebaselines without breaking gate" || bad "malformed baseline exit $RC"
assert_contains "$WORK/snap5.out" 'dropping malformed baseline row' "malformed baseline warns"
assert_contains "$HIST/DELTA.md" "baseline-note malformed-row-dropped id='garbage garbage garbage'" "malformed baseline audited"
if grep -q 'garbage garbage garbage row-absent' "$HIST/DELTA.md"; then
  bad "malformed line became phantom row-absent"
else
  ok "malformed line never becomes phantom transition"
fi

# Matrix probes have no registry baseline; symlinked output roots are refused.
run_probe "$WORK/port.out" snapshot --port "$PORT" --history "$WORK/port-history"
[ "$RC" -eq 1 ] && ok "snapshot --port refused with probe-error exit" || bad "snapshot --port exit $RC"
mkdir "$WORK/real-history"
ln -s "$WORK/real-history" "$WORK/link-history"
run_probe "$WORK/link.out" snapshot --registry "$REG" --history "$WORK/link-history"
[ "$RC" -eq 1 ] && ok "symlinked history dir refused" || bad "symlinked history exit $RC"

printf 'RESULT pass=%s fail=%s\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
