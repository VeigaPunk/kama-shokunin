#!/bin/bash
# usage: drive_hold.sh <S> <N>   runs N hold-mode lifecycles sequentially; scratch only
S=$1; N=$2; D=$S/clone
for i in $(seq 1 "$N"); do
  H=$S/hold$i; W=$S/work/hold$i; O=$S/hold$i.json
  rm -rf "$H"; mkdir -p "$H"
  python3 "$D/tools/kama-completion-live.py" --work "$W" --hold-dir "$H" --out "$O" --hold-timeout 120 > "$S/hold$i.stdout" 2>&1 &
  P=$!
  for t in $(seq 1 600); do [ -f "$H/ready.json" ] && break; kill -0 $P 2>/dev/null || break; sleep 0.1; done
  if [ -f "$H/hold.json" ]; then cp "$H/hold.json" "$S/out/hold$i.hold.json"; fi
  if [ -f "$H/ready.json" ]; then cp "$H/ready.json" "$S/out/hold$i.ready.json"; fi
  touch "$H/release"
  wait $P; rc=$?
  echo "hold$i rc=$rc verdict=$(python3 -c "import json;r=json.load(open('$O'));print(r['verdict'], r.get('setup_error'))" 2>&1)"
  if [ -f "$H/hold.json" ]; then echo "  hold.json still present after run $i"; fi
done
