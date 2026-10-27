#!/usr/bin/env bash
set -u
S=/fast/scratch/hyaku/kama-r58/R02ProfileHookSemantics
L=/home/vgpnk/Projects/shokunin/kama-shokunin
CHK=$S/checker/tools/round58-battery-exec-check.py
CNT=$S/checker/tools/round58-c1-counter.py
TIP=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a

echo "=== baseline: frozen C1 counter at lane build tip ==="
TMPDIR=$S HYAKU_SCRATCH=/fast/scratch/hyaku python3 "$CNT" --repo "$L" --tip "$TIP" \
  --checker "$CHK" --work "$S/counter-work" --out "$S/receipts/c1-counter-buildtip.out"
echo "counter exit=$?"

mk() {
  local name=$1
  local d=$S/fixtures/$name
  rm -rf "$d"; mkdir -p "$d"
  cp -a "$S/common/." "$d/"
  cp "$S/variants/$name/tools/round56-env-leg-battery.py" "$d/tools/round56-env-leg-battery.py"
  git -C "$d" init -q || return 9
  local top; top=$(git -C "$d" rev-parse --show-toplevel)
  if [ "$(realpath "$top")" != "$(realpath "$d")" ]; then echo "TOPLEVEL MISMATCH $name"; exit 9; fi
  git -C "$d" add -A
  git -C "$d" -c user.name=r02-seat -c user.email=r02-seat@invalid commit -q -m "fixture $name" || return 9
}

case_run() {
  local name=$1
  local d=$S/fixtures/$name
  echo "=== $name ==="
  TMPDIR=$S HYAKU_SCRATCH=/fast/scratch/hyaku python3 "$CHK" --repo "$d" --tip HEAD \
    --work "$S/work-$name" --out "$S/receipts/$name.verdict.out"
  echo "$name checker exit=$?"
  TMPDIR=$S HYAKU_SCRATCH=/fast/scratch/hyaku python3 "$CHK" --repo "$d" --tip HEAD \
    --work "$S/work-$name-h" --harness "$d/tools/round56-env-leg-battery.py" \
    --harness-out "$S/receipts/$name.frames.json"
  echo "$name harness exit=$?"
  python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
for f in d["frames"]: print("  frame fn=%s label=%r sub=%d counter=%d" % (f["fn"], f["label"], f["sub"], f["counter"]))
print("  frames=%d error=%r" % (len(d["frames"]), d["error"]))' "$S/receipts/$name.frames.json"
}

for n in X01-ghost-thread X01-noghost X02-all-threads; do mk "$n" || echo "mk failed $n"; done
for n in X01-ghost-thread X01-noghost X02-all-threads; do case_run "$n"; done
echo "=== driver done ==="
