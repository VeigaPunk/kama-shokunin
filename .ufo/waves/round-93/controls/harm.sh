#!/usr/bin/env bash
# Round-93 harm suite (round-92 suite plus round92-linear-paths.py) (frozen with the plan). Runs against the lane working tree, whose probe must
# equal the probe at <rev>. Usage: harm.sh <lane> <rev> <scratch>
set -uo pipefail
lane=$1 rev=$2 s=$3
cd "$lane" || exit 2
mkdir -p "$s"
wt=$(sha256sum tools/kama-probe.sh | cut -d' ' -f1)
rv=$(git show "$rev:tools/kama-probe.sh" | sha256sum | cut -d' ' -f1)
echo "# harm at $rev (working-tree probe sha256 $wt; rev probe sha256 $rv; equal: $([ "$wt" = "$rv" ] && echo yes || echo NO))"
echo "## tests/probe-verdicts/check.py"; python3 tests/probe-verdicts/check.py 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "## tools/test-snapshot.sh"; bash tools/test-snapshot.sh 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "## tools/round89-unloadable-cells.py"; python3 tools/round89-unloadable-cells.py --repo . --rev "$rev" --work "$s/r89" 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "## tools/round90-hostile-answers.py"; python3 tools/round90-hostile-answers.py --repo . --rev "$rev" --work "$s/r90" 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "## operator router 127.0.0.1:1234 (GET only)"; bash tools/kama-probe.sh check --port 1234 --expect '*' --json 2>&1 | python3 -c 'import json,sys; r=json.load(sys.stdin)["rows"][0]; print(r["verdict"], r["reason"])'; echo "exit=${PIPESTATUS[0]}"
echo "## tools/round91-answer-time.py"; python3 tools/round91-answer-time.py --repo . --rev "$rev" --work "$s/r91" 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
echo "## tools/round92-linear-paths.py"; python3 tools/round92-linear-paths.py --repo . --rev "$rev" --work "$s/r92" 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
