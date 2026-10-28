#!/bin/bash
# Idle-outcome fixture for tools/kama-context-capacity.py (round-64 X10EnvIdleProbe).
# The tool decides "host idle" in live_llama_server_pids(), which shells out to
# `pgrep -x llama-server` (subprocess, PATH lookup) and /proc/<pid>/stat.
# This fixture runs a byte-identical COPY of the tool with a fake `pgrep` first on PATH
# (in the fixture's own bin dir, nothing installed anywhere) that reports no process,
# so no foreign server is seen, no foreign server is touched, and the tool's own code
# path runs unmodified. The tool's own K1 child (its own port 47400-47419 range) is a
# real llama-server it starts and tears down itself.
# usage: idle-fixture.sh <repo-or-clone> <scratch-dir>   (repo is only read/symlinked)
set -u
REPO=$(readlink -f "$1"); S=$(readlink -f "$2")
F=$S/fixture; rm -rf "$F"; mkdir -p "$F/tools" "$F/registry" "$F/.ufo/waves/round-25" "$F/bin" "$S/cc"
cp "$REPO/tools/kama-context-capacity.py" "$F/tools/"          # copy, not symlink: SCRIPT resolves inside $F
ln -s "$REPO/tools/kama-llamacpp-live.py" "$F/tools/"
ln -s "$REPO/registry/endpoint-consumers.tsv" "$F/registry/"
ln -s "$REPO/.ufo/waves/round-25/count-c2.py" "$F/.ufo/waves/round-25/"
cmp "$REPO/tools/kama-context-capacity.py" "$F/tools/kama-context-capacity.py" || { echo "copy differs"; exit 3; }
# fake pgrep: empty output, exit 1 (pgrep's "no match" status); records that it was called.
cat > "$F/bin/pgrep" <<'FAKE'
#!/bin/bash
echo "$@" >> "$(dirname "$0")/pgrep-calls.log"
exit 1
FAKE
chmod +x "$F/bin/pgrep"
cd "$S" || exit 3
PATH="$F/bin:$PATH" python3 "$F/tools/kama-context-capacity.py" --only K1 --host-idle-timeout 20 \
  --scratch "$S/cc" --out "$S/idle-cc.json" >"$S/idle.stdout" 2>"$S/idle.stderr"
RC=$?
echo "exit=$RC"
echo "stdout: $(cat "$S/idle.stdout")"
echo "stderr: $(cat "$S/idle.stderr")"
python3 - "$S/idle-cc.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print('host_idle:',json.dumps(d.get('host_idle'),sort_keys=True))
print('error:',d['error'],'exit_code:',d['exit_code'])
print('all_ports_closed_true:', d['summary'].get('all_ports_closed') is True, 'cells:',d['summary']['cells'],'observed:',d['summary']['observed'])
PY
echo "fake-pgrep-calls: $(wc -l < "$F/bin/pgrep-calls.log")"
exit $RC
