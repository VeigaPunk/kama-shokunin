#!/bin/bash
set -u
cd /tmp/kama-r23w2/RowF06LazyFetch-2 || exit 9
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  python3 tests/report-audit/repo-state-grid.py --case F06-lazy-fetch-command \
  --current /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/RowF06LazyFetch-2/current-auditor-f228f174.py \
  --json > /tmp/f06-hand/grid-f06.json 2> /tmp/f06-hand/grid-f06.err
echo "GRID_EXIT=$?"
python3 - <<'PY'
import json
d = json.load(open("/tmp/f06-hand/grid-f06.json"))
for a, r in d["arms"].items():
    row = r["rows"][0]
    print(a, "exit=%s executed=%s met=%s violations=%s"
          % (row["exit"], row["executed"], row["met"], r["violations"]))
PY
