#!/usr/bin/env bash
# R57Item03CounterRepair — isolated scratch prototype of the stale maxN repair.
# Read-only against the lane repo: the counters use git cat-file / archive / ls-tree.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
S=${S:-/fast/scratch/hyaku/kama-r57/R57Item03CounterRepair}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
BASE=b89bdab2cc114735ec5d331c6c610134258f7864
TIP=8640e34cad02adcd247ba0862da63f6fb2aab0df
BASE_COUNTER="$LANE/tools/round42-selfdesc-reconcile.py"
BUILD_COUNTER="$HERE/prototype/build/round42-selfdesc-reconcile.py"
export TMPDIR="$S/tmp"
mkdir -p "$TMPDIR" "$S/out"
trap 'rm -rf "$S/fixtures" "$TMPDIR"' EXIT

run() { # run <label> <counter> <repo> <tip>
  local label=$1 counter=$2 repo=$3 tip=$4
  {
    echo "label=$label"
    echo "counter=$counter"
    echo "counter_sha256=$(sha256sum "$counter" | cut -d' ' -f1)"
    echo "repo=$repo"
    echo "tip_arg=$tip"
    echo "\$ python3 $counter --repo $repo --tip $tip"
  } > "$S/out/$label.out"
  python3 "$counter" --repo "$repo" --tip "$tip" >> "$S/out/$label.out" 2>&1
  echo "exit=$?" >> "$S/out/$label.out"
}

# ---- real-repo receipts -----------------------------------------------------
run base-counter-at-base "$BASE_COUNTER" "$LANE" "$BASE"
run build-counter-at-base "$BUILD_COUNTER" "$LANE" "$BASE"
run base-counter-at-tip "$BASE_COUNTER" "$LANE" "$TIP"
run build-counter-at-tip "$BUILD_COUNTER" "$LANE" "$TIP"

# ---- fixtures ---------------------------------------------------------------
mkfixture() { # mkfixture <dir> <extra-text-file>
  local d=$1 extra=$2
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$LANE" show "$BASE:SCORECARD.md" > "$d/SCORECARD.md"
  cat "$extra" >> "$d/SCORECARD.md"
  git -C "$d" add SCORECARD.md
  git -C "$d" -c user.name=kama-seat -c user.email=seat@example.invalid \
      commit -q -m "fixture: SCORECARD with $(basename "$extra")"
  top=$(git -C "$d" rev-parse --show-toplevel)
  [ "$top" = "$d" ] || { echo "fixture toplevel mismatch: $top != $d" >&2; exit 9; }
  echo "fixture_toplevel=$top" >> "$S/out/fixture-toplevels.out"
}

mkdir -p "$S/fixtures"
cat > "$S/fixtures/stale-fence.txt" <<'EOF'

`````

Deleted by `deadbeef` (fixture: restored historical block carrying a stale heading):

`````text
## Round 99 — stale restored heading (fixture, never measured)
`````
EOF
cat > "$S/fixtures/stale-comment.txt" <<'EOF'

<!--
## Round 98 — hidden stale heading (fixture, never measured)
-->
EOF
cat > "$S/fixtures/live-stale.txt" <<'EOF'

## Round 99 — live unmeasured heading (fixture positive control)
EOF

: > "$S/out/fixture-toplevels.out"
for name in stale-fence stale-comment live-stale; do
  mkfixture "$S/fixtures/$name" "$S/fixtures/$name.txt"
done

for name in stale-fence stale-comment live-stale; do
  run "base-counter-fixture-$name" "$BASE_COUNTER" "$S/fixtures/$name" HEAD
  run "build-counter-fixture-$name" "$BUILD_COUNTER" "$S/fixtures/$name" HEAD
done

# ---- no-op receipts ---------------------------------------------------------
{
  echo 'label=noop-frozen-c1'
  echo "\$ python3 $LANE/.ufo/waves/round-57/controls/c1-noop.py"
  python3 "$LANE/.ufo/waves/round-57/controls/c1-noop.py"
  echo "exit=$?"
} > "$S/out/noop-frozen-c1.out"

cat > "$S/prototype/build/noop-build.py" <<'EOF'
#!/usr/bin/env python3
# Do-nothing "build" control: reads no SCORECARD bytes and derives nothing.
print("r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 "
      "readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True")
EOF
{
  echo 'label=noop-build-summary'
  echo "\$ python3 $HERE/prototype/build/noop-build.py"
  python3 "$HERE/prototype/build/noop-build.py"
  echo "exit=$?"
} > "$S/out/noop-build.out"

# naive gate: shipped alongside this script.
{
  echo 'label=naive-gate-noop (a summary-only verifier accepts a no-op)'
  bash "$HERE/prototype/build/naive-gate.sh" python3 "$HERE/prototype/build/noop-build.py"
  echo "exit=$?"
} > "$S/out/naive-gate-noop.out"

# ---- independent fence-aware derivation -------------------------------------
python3 "$HERE/prototype/build/maxn-cases.py" > "$S/out/maxn-cases.out" 2>&1
echo "exit=$?" >> "$S/out/maxn-cases.out"

python3 - "$LANE/SCORECARD.md" "$BASE" > "$S/out/independent-maxn.out" 2>&1 <<'PY'
import re, subprocess, sys
path, rev = sys.argv[1], sys.argv[2]
text = subprocess.run(["git", "-C", "/home/vgpnk/Projects/shokunin/kama-shokunin",
                       "show", f"{rev}:SCORECARD.md"], capture_output=True, text=True,
                      check=True).stdout
live, fence, comment = [], None, False
for l in text.split("\n"):
    if comment:
        if "-->" in l: comment = False
        continue
    if fence is None:
        s = l.lstrip()
        if s.startswith("<!--"):
            if "-->" not in s[4:]: comment = True
            continue
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", l)
        if m:
            fence = (m.group(1)[0], len(m.group(1))); continue
        live.append(l)
    else:
        m = re.match(r"^ {0,3}(`{3,}|~{3,})\s*$", l)
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1]:
            fence = None
rs = [int(m.group(1)) for l in live for m in [re.match(r"^## Round (\d+)", l)] if m]
allrs = [int(m.group(1)) for l in text.split("\n") for m in [re.match(r"^## Round (\d+)", l)] if m]
print(f"commit={rev}")
print(f"raw_round_headings_max={max(allrs)}")
print(f"live_round_headings_max={max(rs)}")
print(f"live_rounds={rs}")
PY
echo "exit=$?" >> "$S/out/independent-maxn.out"

ls -l "$S/out"
