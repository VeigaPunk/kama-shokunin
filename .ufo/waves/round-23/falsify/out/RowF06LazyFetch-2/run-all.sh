#!/bin/bash
# Rebuild all hand fixtures and capture the observations in run.log.
set +e
OUT=$(cd "$(dirname "$0")" && pwd)
mkdir -p /tmp/f06-hand
cp "$OUT/frozen-audit-4fe9339.py" /tmp/frozen-r23-f06.py
cp "$OUT/detect.py" /tmp/f06-hand/detect.py
: > "$OUT/run.log"
for s in build.sh probe-variants.sh probe2.sh probe3.sh probe4.sh \
         v0-control.sh v1-clean.sh v1-dirty.sh grid-run.sh; do
  echo "===== $s" >> "$OUT/run.log"
  bash "$OUT/$s" >> "$OUT/run.log" 2>&1
  echo "script_exit=$?" >> "$OUT/run.log"
done
cp /tmp/f06-hand/grid-f06.json "$OUT/grid-f06-F06-case.json" 2>/dev/null
exit 0
