#!/usr/bin/env bash
# F9: C1 counter against the lane clone at the build commit + direct tool run.
set -u
S=/fast/scratch/hyaku/kama-r47/V1Tool
LANE=$S/lane
TIP=3a09a1d93dcc16799cf6c4b48786e6440af134c4
git -C "$LANE" cat-file -t "$TIP" >/dev/null || { echo "tip missing in clone"; exit 1; }
echo "== counter run at $TIP =="
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py \
  --repo "$LANE" --tip "$TIP" --scratch "$S" --out "$S/lane-c1.out"; echo "counter exit=$?"
echo "== tool direct run (contract from tip) =="
python3 "$LANE/tools/append-only-audit.py" --repo "$LANE" --to "$TIP" --json > "$S/lane-tool.json"
echo "tool exit=$?"
python3 - "$S/lane-tool.json" <<'PY'
import json, sys
out = json.load(open(sys.argv[1]))
print("schema:", out["schema"])
print("files:", len(out["files"]), out["files"][:3], "...")
print("commits:", out["commits"], "events:", len(out["events"]))
print("summary:", out["summary"])
for e in out["events"]:
    print(" ", e["commit"][:12], e["file"], "deleted=%d" % e["deleted"],
          "max=%d" % e["restored_max"], e["status"], "best=%s by=%s" %
          ((e["restored_best"] or "-")[:12], (e["restored_by"] or "-")[:12]))
PY
