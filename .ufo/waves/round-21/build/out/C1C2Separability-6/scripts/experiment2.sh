#!/usr/bin/env bash
# Scratch-only cross-checks (KamaR21.C1C2Separability-6): fault injection per claim, frontier revert,
# and a within-C2 negative control. Counting commands only; no live producer launch.
set -u
export PYTHONDONTWRITEBYTECODE=1
R=/tmp/kama-r21-C1C2Separability-6
FLEET=/home/vgpnk/Projects/shokunin
O=$R/out2
mkdir -p "$O"
: > "$O/index.txt"

run() {
  label=$1; dir=$2; shift 2
  (cd "$dir" && exec "$@") >"$O/$label.out" 2>"$O/$label.err"
  rc=$?
  printf '%s rc=%s dir=%s cmd=%s\n' "$label" "$rc" "$(basename "$dir")" "$*" >>"$O/index.txt"
  return 0
}

# within-C2 negative control: grid present, producer reverted to 7a6bc91 (no install_links)
rm -rf "$R/revC2b" && cp -a "$R/revC2" "$R/revC2b" && cp "$R/lane/tests/llamacpp-live/install-links-grid.py" "$R/revC2b/tests/llamacpp-live/"

# FAULT in C1 only (errata row for 33a67778 removed): C1 must fail, C2 must be unchanged
run faultC1_c1_errata      "$R/faultC1" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run faultC1_c1_nolerr      "$R/faultC1" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run faultC1_c1_selftest    "$R/faultC1" python3 tools/report-landing-audit.py --selftest
run faultC1_c2_gate        "$R/faultC1" python3 tests/llamacpp-live/check-receipt.py --selftest
run faultC1_c2_grid_current "$R/faultC1" python3 tests/llamacpp-live/install-links-grid.py --arm current
run faultC1_c2_grid_selftest "$R/faultC1" python3 tests/llamacpp-live/install-links-grid.py --selftest

# FAULT in C2 only (producer install_links never records a symlink): C2 must fail, C1 must be unchanged
run faultC2_c2_grid_current "$R/faultC2" python3 tests/llamacpp-live/install-links-grid.py --arm current
run faultC2_c2_gate        "$R/faultC2" python3 tests/llamacpp-live/check-receipt.py --selftest
run faultC2_c1_nolerr      "$R/faultC2" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run faultC2_c1_errata      "$R/faultC2" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run faultC2_c1_selftest    "$R/faultC2" python3 tools/report-landing-audit.py --selftest

# FRONTIER revert (the two .ufo/waves/round-21/sources files, owned by neither claim): both claims unchanged
run revF_c1_nolerr         "$R/revF" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run revF_c1_errata         "$R/revF" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run revF_c1_selftest       "$R/revF" python3 tools/report-landing-audit.py --selftest
run revF_c2_gate           "$R/revF" python3 tests/llamacpp-live/check-receipt.py --selftest
run revF_c2_grid_current   "$R/revF" python3 tests/llamacpp-live/install-links-grid.py --arm current
run revF_c2_grid_selftest  "$R/revF" python3 tests/llamacpp-live/install-links-grid.py --selftest

# within-C2 negative control: grid + producer mismatch must NOT pass
run revC2b_c2_grid_current "$R/revC2b" python3 tests/llamacpp-live/install-links-grid.py --arm current

echo DONE >>"$O/index.txt"
