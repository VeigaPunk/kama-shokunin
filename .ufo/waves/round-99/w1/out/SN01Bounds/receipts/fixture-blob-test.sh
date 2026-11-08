#!/usr/bin/env bash
# SN01Bounds: can the C1 grader be made to run a caller-chosen committed blob?
# Fixture repo only (never the lane). Benign blob: prints a marker and exits 3.
set -uo pipefail
S=/fast/scratch/hyaku/kama-r99/SN01Bounds
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
F="$S/fixture-work"; rm -rf "$F"; mkdir -p "$F"
D=$(mktemp -d "$S/fixture.XXXXXX")
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q
TOP=$(git -C "$D" rev-parse --show-toplevel); echo "toplevel=$TOP"
[ "$TOP" = "$D" ] || { echo "ABORT: toplevel mismatch"; exit 9; }
mkdir -p "$D/tools"

# a committed blob that carries the frozen anchor line, then prints a marker
cat > "$D/tools/counter.py" <<'PY'
#!/usr/bin/env python3
CELLS = [
    ("W14-900k-nd1", ["x"], "MODEL_OK", "router-unloaded-autoload"),
]
print("MARKER: caller-chosen committed blob executed")
raise SystemExit(3)
PY
git -C "$D" -c user.email=s@n -c user.name=sn add tools/counter.py
git -C "$D" -c user.email=s@n -c user.name=sn commit -qm fixture
git -C "$D" log --oneline -1
echo "--- blob content:"; cat "$D/tools/counter.py"
echo "--- anchor line count: $(grep -c '^("W14-900k-nd1",' "$D/tools/counter.py")"

python3 "$LANE/tools/round99-control-population.py" --repo "$D" --rev HEAD \
  --counter tools/counter.py --work "$F" > "$F/out" 2> "$F/err"
echo "grader rc=$?"
echo "--- stdout:"; cat "$F/out"
echo "--- stderr:"; cat "$F/err"
