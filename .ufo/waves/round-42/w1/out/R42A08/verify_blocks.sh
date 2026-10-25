#!/bin/bash
# R42A08 — C1 history-intact review: moved head blocks verbatim + rest unchanged
S=/fast/scratch/kama-r42/seats/R42A08
B=$S/base_scorecard.md   # 0b606b03bf0b2a87b791aa537f6c72c941624cf0
T=$S/tip_scorecard.md    # 3d9bd8d72366e281fab291874524130428ee423d

# Bodies between heading anchors, headings excluded via next, trailing blanks included.
awk '/^\*\*Current authority \(actual round 5/{f=1;next} /^## Axes/{f=0} f' "$B" > "$S/b_banner"
awk '/^\*\*Current authority \(actual round 5/{f=1;next} /^### Planned \(round-5 text\)/{f=0} f' "$T" > "$S/t_banner"

awk '/^## Planned$/{f=1;next} /^## Retired$/{f=0} f' "$B" > "$S/b_planned"
awk '/^### Planned \(round-5 text\)/{f=1;next} /^### Retired \(round-3 text\)/{f=0} f' "$T" > "$S/t_planned"

awk '/^## Retired$/{f=1;next} /^## Move log$/{f=0} f' "$B" > "$S/b_retired"
awk '/^### Retired \(round-3 text\)/{f=1;next} /^### Capabilities \(round-10 head table\)/{f=0} f' "$T" > "$S/t_retired"

awk '/^## Capabilities$/{f=1;next} /^## Saturation$/{f=0} f' "$B" > "$S/b_caps"
awk '/^### Capabilities \(round-10 head table\)/{f=1;next} /^### Saturation \(round-10 text\)/{f=0} f' "$T" > "$S/t_caps"

awk '/^## Saturation$/{f=1;next} /^## Round 6/{f=0} f' "$B" > "$S/b_sat"
awk '/^### Saturation \(round-10 text\)/{f=1;next} /^## Round 6/{f=0} f' "$T" > "$S/t_sat"

echo "=== per-block byte-for-byte (cmp) ==="
for blk in banner planned retired caps sat; do
  bl=$(wc -l < "$S/b_$blk"); tl=$(wc -l < "$S/t_$blk")
  if cmp -s "$S/b_$blk" "$S/t_$blk"; then
    echo "VERBATIM $blk  base=$bl lines tip=$tl lines  md5=$(md5sum "$S/b_$blk" | cut -c1-12)"
  else
    echo "DIFF     $blk  base=$bl lines tip=$tl lines"
    diff "$S/b_$blk" "$S/t_$blk" | head -25
  fi
done

echo
echo "=== whole body below the head: base 147-2207 vs tip 184-2244 ==="
if cmp -s <(sed -n '147,2207p' "$B") <(sed -n '184,2244p' "$T"); then
  echo "TAIL_IDENTICAL ($(sed -n '147,2207p' "$B" | wc -l) lines, md5 $(md5sum < <(sed -n '147,2207p' "$B") | cut -c1-12))"
else
  echo "TAIL_DIFF:"
  diff <(sed -n '147,2207p' "$B") <(sed -n '184,2244p' "$T") | head -40
fi

echo
echo "=== diff hunk inventory (base..tip) ==="
grep '^@@' "$S/base_to_tip.diff"
echo "deleted lines: $(grep -c '^-[^-]' "$S/base_to_tip.diff")   added lines: $(grep -c '^+[^+]' "$S/base_to_tip.diff")"

echo
echo "=== tip lines 2242-2274 (context tail + appended Round 42 section) ==="
sed -n '2242,2245p' "$T"
echo "..."
grep -n '^## Round 42' "$T"
