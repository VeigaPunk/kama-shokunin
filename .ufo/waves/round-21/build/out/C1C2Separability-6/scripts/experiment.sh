#!/usr/bin/env bash
# Scratch-only experiment (KamaR21.C1C2Separability-6). Read-only w.r.t. the lane and fleet:
# every run is a counting command; no llama-server, no producer launch, no model download.
set -u
export PYTHONDONTWRITEBYTECODE=1
R=/tmp/kama-r21-C1C2Separability-6
FLEET=/home/vgpnk/Projects/shokunin
O=$R/out
L=$R/lane
C2=$R/revC2
C1=$R/revC1
D=$R/drafts
rm -rf "$O"; mkdir -p "$O" "$D"
: > "$O/index.txt"

# run LABEL DIR CMD...  -> stdout/stderr to $O/LABEL.{out,err}; rc appended to index.txt
run() {
  label=$1; dir=$2; shift 2
  (cd "$dir" && exec "$@") >"$O/$label.out" 2>"$O/$label.err"
  rc=$?
  printf '%s rc=%s dir=%s cmd=%s\n' "$label" "$rc" "$(basename "$dir")" "$*" >>"$O/index.txt"
  return 0
}

# ---- revert integrity (exit codes of git diff --quiet: 0 = identical)
git -C "$C2" diff --quiet 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d -- tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py; echo "integrity revC2 C2-files-equal-7a6bc91 rc=$?" >>"$O/index.txt"
git -C "$C2" cat-file -e 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d:tests/llamacpp-live/install-links-grid.py 2>/dev/null; echo "integrity revC2 grid-absent-at-7a6bc91 rc=$?" >>"$O/index.txt"
git -C "$C1" diff --quiet a29bb84abbb8b4d328f5970a89e448330a3a42ac -- tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py tests/llamacpp-live/install-links-grid.py; echo "integrity revC1 C2-files-equal-a29bb84 rc=$?" >>"$O/index.txt"
for f in tools/report-landing-audit.py registry/report-landing-errata.tsv; do
  for t in lane revC2; do sha256sum "$R/$t/$f" 2>/dev/null; done
done >"$O/c1-file-sha256.txt"
for f in tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py tests/llamacpp-live/install-links-grid.py; do
  for t in lane revC1; do sha256sum "$R/$t/$f" 2>/dev/null; done
done >"$O/c2-file-sha256.txt"

# ---- drafts for the round-21 mode of the audit (synthetic; scratch only)
printf '%s\n' '# round-21 scratch draft (no commit cited)' '## Work performed' 'none' '## Landed changes' '- `7a6bc91` round-20: log routed verifier tool registrations' >"$D/draft_nocite.md"
printf '%s\n' '# round-21 scratch draft (cites the mixed commit)' '## Work performed' 'none' '## Landed changes' '- `a29bb84` round-21: report landing audit with errata ledger; symlink-aware install-links pin, gate checks and grid' >"$D/draft_cite.md"

# ---- BASELINE: a29bb84 (scratch clone, unmodified)
run base_c1_nolerr      "$L" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run base_c1_errata      "$L" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run base_c1_selftest    "$L" python3 tools/report-landing-audit.py --selftest
run base_c1_default_fleet "$L" python3 tools/report-landing-audit.py
run base_c1_r21_nocite  "$L" python3 tools/report-landing-audit.py --fleet-repo "$FLEET" --report "21=$D/draft_nocite.md"
run base_c1_r21_cite    "$L" python3 tools/report-landing-audit.py --fleet-repo "$FLEET" --report "21=$D/draft_cite.md"
run base_c2_gate        "$L" python3 tests/llamacpp-live/check-receipt.py --selftest
run base_c2_grid_current "$L" python3 tests/llamacpp-live/install-links-grid.py --arm current
run base_c2_grid_frozen "$L" python3 tests/llamacpp-live/install-links-grid.py --arm frozen
run base_c2_grid_both   "$L" python3 tests/llamacpp-live/install-links-grid.py
run base_c2_grid_selftest "$L" python3 tests/llamacpp-live/install-links-grid.py --selftest
run base_installtree_selftest "$L" python3 tests/llamacpp-live/install-tree-grid.py --selftest

# ---- REVERT C2 (tools/kama-llamacpp-live.py, check-receipt.py, install-links-grid.py -> 7a6bc91 / absent)
run revC2_c1_nolerr     "$C2" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"
run revC2_c1_errata     "$C2" python3 tools/report-landing-audit.py --fleet-repo "$FLEET"
run revC2_c1_selftest   "$C2" python3 tools/report-landing-audit.py --selftest
run revC2_c2_grid_current "$C2" python3 tests/llamacpp-live/install-links-grid.py --arm current   # negative control: must fail
run revC2_c2_gate_info  "$C2" python3 tests/llamacpp-live/check-receipt.py --selftest             # informational (old gate)

# ---- REVERT C1 (tools/report-landing-audit.py, registry/report-landing-errata.tsv removed)
run revC1_c1_nolerr     "$C1" python3 tools/report-landing-audit.py --no-errata --fleet-repo "$FLEET"   # negative control: must fail
run revC1_c2_gate       "$C1" python3 tests/llamacpp-live/check-receipt.py --selftest
run revC1_c2_grid_current "$C1" python3 tests/llamacpp-live/install-links-grid.py --arm current
run revC1_c2_grid_frozen "$C1" python3 tests/llamacpp-live/install-links-grid.py --arm frozen
run revC1_c2_grid_both  "$C1" python3 tests/llamacpp-live/install-links-grid.py
run revC1_c2_grid_selftest "$C1" python3 tests/llamacpp-live/install-links-grid.py --selftest
run revC1_installtree_selftest "$C1" python3 tests/llamacpp-live/install-tree-grid.py --selftest

echo DONE >>"$O/index.txt"
