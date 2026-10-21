#!/usr/bin/env bash
# Run one auditor over one fixture arm and print a one-line summary.
# Usage: run-arm.sh AUDITOR ROOT ARM
# Prints: exit=<n> kinds=<sorted kinds or -> summary=<compact json or -> stderr=<tail>
set -u
AUDITOR=$1; ROOT=$2; ARM=$3
LANE="$ROOT/$ARM/lane"; FLEET="$ROOT/$ARM/fleet"
OUT=$(mktemp); ERR=$(mktemp)
python3 "$AUDITOR" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 1 \
  --no-errata --json >"$OUT" 2>"$ERR"
rc=$?
kinds=$(python3 - "$OUT" <<'PY'
import json, sys
try:
    doc = json.load(open(sys.argv[1]))
except Exception:
    print("-", end=""); raise SystemExit
k = sorted({d["kind"] for r in doc.get("results", []) for d in r.get("defects", [])})
s = doc.get("summary", {})
print(f"{k} summary(defects={s.get('defects')},uncorrected={s.get('uncorrected')},"
      f"required={s.get('required_commits')},status={s.get('status')})", end="")
PY
)
printf 'exit=%s %s stderr=%s\n' "$rc" "$kinds" "$(tr '\n' ' ' <"$ERR" | tail -c 200)"
rm -f "$OUT" "$ERR"
