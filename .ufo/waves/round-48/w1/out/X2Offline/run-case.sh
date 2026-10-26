#!/bin/sh
# run one replay case: run-case.sh <case-name> [extra replay args...]
set -u
S=/fast/scratch/hyaku/kama-r48/X2Offline
name=$1; shift
d="$S/cases/$name"
rm -rf "$d/work"; mkdir -p "$d/work"
start=$(date +%s.%N)
TMPDIR="$S" python3 "$S/lane/tools/kama-live-replay.py" \
  --receipt "$d/receipt.json" --work "$d/work" --out "$d/out.json" "$@" \
  >"$d/stdout.txt" 2>"$d/stderr.txt"
code=$?
end=$(date +%s.%N)
echo "case=$name exit=$code secs=$(echo "$end $start" | awk '{printf "%.1f", $1-$2}')"
echo "--- stdout"; cat "$d/stdout.txt"
echo "--- stderr (tail 5)"; tail -5 "$d/stderr.txt"
echo "--- out.json: match/refused/mismatches/live_exit"
python3 - "$d/out.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print(json.dumps({k: r.get(k) for k in ("match", "refused", "mismatches", "live_exit", "rerun_receipt")}, ensure_ascii=True))
PY
echo "--- work tree (type size path)"
find "$d/work" -printf '%y %10s %P\n' | sort -k3
echo "--- rerun receipt:"
if [ -f "$d/work/rerun-receipt.json" ]; then
  python3 - "$d/work/rerun-receipt.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print("schema=%s outcome=%s setup_error=%s internal_fault=%s" % (r.get("schema"), r.get("outcome"), r.get("setup_error"), r.get("internal_fault")))
PY
else
  echo "absent"
fi
echo "case=$name end"
