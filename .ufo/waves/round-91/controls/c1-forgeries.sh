#!/usr/bin/env bash
# Round-91 C1 forgery probes, built from the base probe bytes (pre-freeze).
#   f1-count-cap   : model_matches looks only at the first 1000 served ids (fast by truncation)
#   f2-exact-match : model_matches compares raw ids, no normalize_id fork (fast by dropping the rule)
# Usage: c1-forgeries.sh <lane> <base-rev> <out-dir>
set -euo pipefail
lane=$1 rev=$2 out=$3
mkdir -p "$out"
git -C "$lane" show "$rev:tools/kama-probe.sh" > "$out/base.sh"
sed 's/^  done <<< "\$served"$/  done <<< "$(printf "%s\\n" "$served" | head -n 1000)"/' "$out/base.sh" > "$out/f1-count-cap.sh"
sed -e 's/^    sn=\$(normalize_id "\$s")$/    sn=$s/' -e 's/^  local exp_n; exp_n=\$(normalize_id "\$expected")$/  local exp_n=$expected/' "$out/base.sh" > "$out/f2-exact-match.sh"
for f in f1-count-cap f2-exact-match; do
  if cmp -s "$out/base.sh" "$out/$f.sh"; then echo "forgery $f did not apply" >&2; exit 2; fi
  diff "$out/base.sh" "$out/$f.sh" || true
done
