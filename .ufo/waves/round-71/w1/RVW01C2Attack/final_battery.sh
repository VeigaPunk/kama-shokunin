#!/usr/bin/env bash
# Final attack battery against the current census-waiver-boundary bytes.
set -u
S=/fast/scratch/hyaku/kama-r71/RVW01C2Attack
L=/home/vgpnk/Projects/shokunin/kama-shokunin
cd "$L" || exit 9

echo "== tool sha256 before: $(sha256sum tools/census-waiver-boundary.py | cut -d' ' -f1)"
echo "== census sha256: $(sha256sum tools/round65-host-census.py | cut -d' ' -f1)"

echo "=== A. landed census direct (which member fails on current lane state?) ==="
python3 tools/round65-host-census.py >"$S/final-landed-census.out" 2>&1
echo "landed_exit=$?"
grep -E "^(FAIL|refused|HOST_CENSUS|CENSUS_NOT_EVALUATED)" "$S/final-landed-census.out"

echo "=== B. canonical ==="
python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py >"$S/final-canonical.out" 2>&1
echo "canonical_exit=$?"
grep -E "BOUNDARY" "$S/final-canonical.out"

for v in H3-second-call-silent H4-phantom-not-evaluated; do
  echo "=== C. off-label --census $v ==="
  python3 tools/census-waiver-boundary.py --census "$S/shims/$v.py" >"$S/final-offlabel-$v.out" 2>&1
  echo "offlabel_exit=$?"
  grep -E "BOUNDARY_CASE [0-9]|^BOUNDARY " "$S/final-offlabel-$v.out" | cut -c1-260
  echo "=== D. on-label demo --shims ($v in s5t slot) ==="
  python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py --shims "$S/demo-$v-shims" >"$S/final-demo-$v.out" 2>&1
  echo "demo_exit=$?"
  grep -E "BOUNDARY" "$S/final-demo-$v.out" | cut -c1-300
done

echo "== tool sha256 after: $(sha256sum tools/census-waiver-boundary.py | cut -d' ' -f1)"
