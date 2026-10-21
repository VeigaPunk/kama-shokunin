#!/usr/bin/env bash
# Targeted follow-ups for C1ExitReprobe (kama round-21 falsify), read-only on lane/fleet.
# 1) Why does the ambiguous prefix f530ce0 classify as landed-unresolved, not landed-ambiguous?
# 2) Closed stdout (fd 1 closed): why exit 0 with no output?
set -u
LANE=/tmp/kama-r21-C1ExitReprobe/lane
FLEET=/home/vgpnk/Projects/shokunin
AUD=$LANE/tools/report-landing-audit.py
PY=${PY:-/usr/bin/python3}
W=$(mktemp -d /tmp/c1reprobe.XXXXXX)
trap 'rm -rf "$W"' EXIT

AMB=$("$PY" - "$W" <<'PYEOF'
import collections, pathlib, subprocess, sys
W = pathlib.Path(sys.argv[1]); ROOT = W / "amb"; ROOT.mkdir()
subprocess.run(["git", "init", "-q", "-b", "master", str(ROOT)], check=True)
parts = []
for i in range(60000):
    msg = f"c{i}\n".encode()
    parts.append(f"commit refs/heads/master\nmark :{i+1}\ncommitter Amb <a@x> {1700000000+i} +0000\ndata {len(msg)}\n".encode())
    parts.append(msg)
    if i:
        parts.append(f"from :{i}\n".encode())
    parts.append(b"\n")
subprocess.run(["git", "-C", str(ROOT), "fast-import", "--quiet"], input=b"".join(parts), check=True, capture_output=True)
shas = subprocess.run(["git", "-C", str(ROOT), "rev-list", "master"], capture_output=True, text=True, check=True).stdout.split()
by = collections.defaultdict(list)
for s in shas:
    by[s[:7]].append(s)
amb = next(v[0][:7] for v in by.values() if len(v) > 1)
(W / "amb-draft.md").write_text(f"## Landed changes\n- `{amb}` x\n## End\n", encoding="utf-8")
print(amb)
PYEOF
)
echo "== batch-check semantics for the ambiguous prefix $AMB"
printf '%s\n' "$AMB" | git -C "$W/amb" cat-file --batch-check 2>&1; echo "   no_peel_exit=$?"
printf '%s^{commit}\n' "$AMB" | git -C "$W/amb" cat-file --batch-check 2>&1; echo "   peel_exit=$?"
printf '%s^{commit}\n' "$AMB" | git -C "$FLEET" cat-file --batch-check 2>&1; echo "   fleet_peel_exit=$?"

echo "== tool --json on the ambiguous draft (which kind?)"
"$PY" "$AUD" --lane-repo "$W/amb" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/amb-draft.md" --no-errata --json 2>&1 | "$PY" -c 'import json,sys
r=json.load(sys.stdin)["results"][0]
print("   defects:", r["defects"])'; echo "   exit=${PIPESTATUS[0]}"

echo "== tool text output on the ambiguous draft (full stdout)"
"$PY" "$AUD" --lane-repo "$W/amb" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/amb-draft.md" --no-errata; echo "   exit=$?"

echo "== closed stdout: err content and exit"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --json >&- 2>"$W/e8"; echo "   exit=$?"; echo "   stderr_bytes=$(wc -c <"$W/e8")"; cat "$W/e8"

echo "== sys.stdout is None hypothesis (python-level check)"
"$PY" -c 'import os,sys
os.close(1)
try:
    sys.stdout = None if sys.stdout is None else sys.stdout
except Exception as e:
    pass
print("after close: stdout is None ->", sys.stdout is None)' 2>/dev/null; echo "   probe_exit=$?"
echo "done"
