#!/usr/bin/env bash
# Scratch-only (KamaR21.C1C2Separability-6): history-level reverts. Each revert is a real commit on top of
# a29bb84 (author kama-shokunin, subject "round-21: ..."), so git history changes, not just the worktree.
set -u
export PYTHONDONTWRITEBYTECODE=1
R=/tmp/kama-r21-C1C2Separability-6
FLEET=/home/vgpnk/Projects/shokunin
O=$R/out3
mkdir -p "$O"
: > "$O/index.txt"
GITID="-c user.name=kama-shokunin -c user.email=kama@shokunin.local"

run() {
  label=$1; dir=$2; shift 2
  (cd "$dir" && exec "$@") >"$O/$label.out" 2>"$O/$label.err"
  rc=$?
  printf '%s rc=%s dir=%s cmd=%s\n' "$label" "$rc" "$(basename "$dir")" "$*" >>"$O/index.txt"
  return 0
}

rm -rf "$R/revC2h" "$R/revC1h"
cp -a "$R/lane" "$R/revC2h" && cp -a "$R/lane" "$R/revC1h"

# committed revert of C2 (file set restored to 7a6bc91 / grid removed)
git -C "$R/revC2h" checkout -q 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d -- tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py
git -C "$R/revC2h" rm -q tests/llamacpp-live/install-links-grid.py
git -C "$R/revC2h" $GITID commit -q -m "round-21: scratch committed revert of C2 (verification only)"
echo "revC2h head=$(git -C "$R/revC2h" log -1 --format='%h %an %s')" >>"$O/index.txt"

# committed revert of C1 (audit and errata removed)
git -C "$R/revC1h" rm -q tools/report-landing-audit.py registry/report-landing-errata.tsv
git -C "$R/revC1h" $GITID commit -q -m "round-21: scratch committed revert of C1 (verification only)"
echo "revC1h head=$(git -C "$R/revC1h" log -1 --format='%h %an %s')" >>"$O/index.txt"

# C1 counting under committed C2 revert (default rounds 10-20 must be unaffected by a round-21 commit)
run revC2h_c1_nolerr   "$R/revC2h" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run revC2h_c1_errata   "$R/revC2h" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run revC2h_c1_selftest "$R/revC2h" python3 tools/report-landing-audit.py --selftest
run revC2h_c1_r21_cite "$R/revC2h" python3 tools/report-landing-audit.py --fleet-repo "$FLEET" --report "21=$R/drafts/draft_cite.md"

# C2 counting under committed C1 revert
run revC1h_c1_nolerr   "$R/revC1h" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"   # negative control
run revC1h_c2_gate     "$R/revC1h" python3 tests/llamacpp-live/check-receipt.py --selftest
run revC1h_c2_grid_current "$R/revC1h" python3 tests/llamacpp-live/install-links-grid.py --arm current
run revC1h_c2_grid_both "$R/revC1h" python3 tests/llamacpp-live/install-links-grid.py
run revC1h_c2_grid_selftest "$R/revC1h" python3 tests/llamacpp-live/install-links-grid.py --selftest

echo DONE >>"$O/index.txt"
