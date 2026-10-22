#!/bin/bash
# Mirror discrimination for the fleet-only-tag consumer: the SAME tag with
# its TARGET blob removed from the fleet store must become a refusal
# (unknown, exit 2) per the oracle-supplement-2 rule, while with the
# target present it is a proved mismatch (landed-unresolved, exit 1).
set +e
S=/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03
export TMPDIR="$S/tmp"
W="$S/fix-mirror"
rm -rf "$W"; cp -a "$S/fix" "$W"
TARGET=a6714745b7826cf987108278ecac7d8c380a71ba
p="$W/fleet/.git/objects/${TARGET:0:2}/${TARGET:2}"
echo "target object path: $p"
ls -l "$p" 2>&1
mv "$p" "$p.removed"
echo "-- presence after removal (expect failure) --"
git --no-replace-objects --no-lazy-fetch -C "$W/fleet" cat-file -t "$TARGET" 2>&1
echo "-- tag still present? --"
git --no-replace-objects --no-lazy-fetch -C "$W/fleet" cat-file -t a41c20ec9d249f5de4f163d6a0914d0bd49fe59c 2>&1
echo "-- after tool on the mirror --"
python3 "$S/clone/tools/report-landing-audit.py" --lane-repo "$W/lane" --fleet-repo "$W/fleet" \
  --branch master --rounds 1 --report "1=$W/draft.md" --no-errata --json \
  > "$S/out/mirror-after.json" 2> "$S/out/mirror-after.stderr"
echo "MIRROR_AFTER_EXIT=$?"
echo "-- stderr --"; cat "$S/out/mirror-after.stderr"
echo "-- stdout head --"; head -c 300 "$S/out/mirror-after.json"
exit 0
