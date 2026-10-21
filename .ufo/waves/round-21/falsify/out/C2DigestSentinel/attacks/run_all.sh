#!/bin/sh
# Re-runs every C2DigestSentinel experiment in dependency order, one log per
# script, and records each exit code. Expects the attacked-commit clone at
# /tmp/kama-r21-C2DigestSentinel/lane and the live receipt copy under work/.
W=/tmp/kama-r21-C2DigestSentinel
A=$W/attacks
R=$W/results
mkdir -p "$R"
cd "$A" || exit 2
: > "$R/exits.txt"
for s in a_producer_names b_loader c_gate d_producer_main e_extra f_hwcaps g_extra; do
  timeout 900 python3 "$s.py" > "$R/$s.txt" 2>&1
  rc=$?
  echo "$s.py exit=$rc" >> "$R/exits.txt"
done
echo "gate selftest exit=$(cd $W/lane && timeout 600 python3 tests/llamacpp-live/check-receipt.py --selftest > $R/gate-selftest.txt 2>&1; echo $?)" >> "$R/exits.txt"
echo "producer install_links/install_tree on real tree (read-only) exit=$(timeout 120 python3 -c "
import common as C
t,ts=C.P.install_tree(C.REAL_SERVER); l,ls,p=C.P.install_links(C.REAL_SERVER)
print('members',len(t),'install_tree_sha256',ts); print('links',len(l),'install_links_sha256',ls,'problems',p)
" > $R/real-tree-readonly.txt 2>&1; echo $?)" >> "$R/exits.txt"
cat "$R/exits.txt"
