#!/usr/bin/env bash
# R57Item38OutsideDefectAudit fixture driver (scratch only).
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r57/R57Item38OutsideDefectAudit
OUT="$S/out"
mkdir -p "$OUT"

# Receipt: extract the frozen (pre-repair) checker and round-56 battery at the closure tip.
git -C "$LANE" show b89bdab2:tools/round56-prereg-check.py > "$S/old-check.py"
git -C "$LANE" show HEAD:tools/round56-prereg-check.py   > "$S/new-check.py"
git -C "$LANE" show b89bdab2:tools/round56-env-leg-battery.py > "$S/battery-b89.py"
git -C "$LANE" show b89bdab2:.ufo/waves/round-56/preregistration.json > "$S/prereg-b89.json"

# Build a fixture repo with the given battery body. $1=dir $2=battery-file
make_fixture() {
  local d="$1" bat="$2"
  rm -rf "$d"; mkdir -p "$d/.ufo/waves/round-56" "$d/tools"
  cp "$S/prereg-b89.json" "$d/.ufo/waves/round-56/preregistration.json"
  cp "$bat" "$d/tools/round56-env-leg-battery.py"
  (
    git init -q "$d" || exit 9
    cd "$d" || exit 9
    top=$(git rev-parse --show-toplevel)
    [ "$top" = "$d" ] || { echo "TOPLEVEL-MISMATCH $top != $d"; exit 8; }
    git -c user.name=seat -c user.email=seat@example.invalid add -A
    git -c user.name=seat -c user.email=seat@example.invalid commit -q -m fixture
    git rev-parse HEAD
  )
}

# 1) literal-roster no-op: exact ROSTER, main() returns 0, no run() calls.
python3 - "$S/battery-b89.py" "$S/battery-noop.py" <<'PY'
import sys
src = open(sys.argv[1]).read()
cut = src.index("def main():")
open(sys.argv[2], "w").write(src[:cut] + 'def main():\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n')
PY

# 2) unreachable-call fixture: no-op main plus run() calls guarded by `if False`.
python3 - "$S/battery-noop.py" "$S/battery-unreachable.py" <<'PY'
import sys
src = open(sys.argv[1]).read()
cut = src.index("def main():")
extra = ('def main():\n    if False:\n'
         '        run("base-old-counter", None, None, None)\n'
         '        run("round56-counter", None, None, None)\n'
         '        run("m-drop-ldaudit", None, None, None)\n'
         '    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n')
open(sys.argv[2], "w").write(src[:cut] + extra)
PY

{
  echo "== fixture tips"
  TIP_NOOP=$(make_fixture "$S/fix-noop" "$S/battery-noop.py"); echo "noop=$TIP_NOOP"
  TIP_UNREACH=$(make_fixture "$S/fix-unreachable" "$S/battery-unreachable.py"); echo "unreachable=$TIP_UNREACH"

  echo
  echo "== old checker (b89bdab2) vs literal-roster no-op"
  python3 "$S/old-check.py" --repo "$S/fix-noop" --tip "$TIP_NOOP"; echo "exit=$?"
  echo
  echo "== new checker (HEAD) vs literal-roster no-op"
  python3 "$S/new-check.py" --repo "$S/fix-noop" --tip "$TIP_NOOP"; echo "exit=$?"
  echo
  echo "== new checker (HEAD) vs unreachable-call fixture"
  python3 "$S/new-check.py" --repo "$S/fix-unreachable" --tip "$TIP_UNREACH"; echo "exit=$?"
  echo
  echo "== new checker (HEAD) vs genuine lane battery at HEAD"
  python3 "$S/new-check.py" --repo "$LANE" --tip HEAD; echo "exit=$?"
  echo
  echo "== old checker (b89bdab2) vs genuine lane battery at b89bdab2"
  python3 "$S/old-check.py" --repo "$LANE" --tip b89bdab2; echo "exit=$?"
} > "$OUT/precheck.txt" 2>&1
cat "$OUT/precheck.txt"
