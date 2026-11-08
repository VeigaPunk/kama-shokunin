#!/usr/bin/env bash
# probe-state.sh <probe-file> <body.json> <idx>... -> "<idx>\t<state>" lines + per-index wall time
set -u
probe=$1; body=$2; shift 2
rp=$(python3 - "$probe" <<'PY'
import sys
t = open(sys.argv[1]).read()
s = t.find("ROUTER_PY=$(cat <<'PY'\n") + len("ROUTER_PY=$(cat <<'PY'\n")
e = t.find("\nPY\n)", s)
sys.stdout.write(t[s:e])
PY
)
python3 -c "$rp" "$body" files "$@"
