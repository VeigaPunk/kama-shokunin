set -u
B=/tmp/kama-r23-lf
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
A=$(git -C "$B/origin" rev-list --max-parents=0 HEAD)
BLOB=$(git -C "$B/origin" rev-parse "$A:f")
run_audit() { label=$1; script=$2; lane=$3; fleet=$4; shift 4
  : > "$B/marker.log"
  if out=$(cd /tmp && timeout 120 python3 "$script" --lane-repo "$lane" --fleet-repo "$fleet" --branch main --rounds 1 --no-errata "$@" 2>&1); then rc=0; else rc=$?; fi
  printf '%-32s rc=%s marker=%-2s | %s\n' "$label" "$rc" "$(grep -c . "$B/marker.log" 2>/dev/null || echo 0)" "$(echo "$out" | grep -E 'UNCORRECTED unresolved|summary|could-not-evaluate' | tr '\n' ' ' | cut -c1-130)"
}
fresh_lane() { rm -rf "$1"; git clone -q --filter=blob:none --no-checkout "file://$B/origin" "$1"; git -C "$1" config remote.origin.url "file://$B/$2"; }
fresh_fleet_p() { rm -rf "$1"; git clone -q --filter=blob:none --no-checkout "file://$B/fleet-clean-origin" "$1"; }
R=$(git -C "$B/fleet-clean-origin" rev-parse HEAD:.ufo/reports/round-1/kama.md)
echo "clean report blob=$R ; blob-of-f=$BLOB"
echo "--- S3 false clean (fresh clone each run; successful uploadpack marker) ---"
fresh_lane "$B/lane-e1" evil; git -C "$B/lane-e1" config remote.origin.uploadpack "$B/upmark-real"
run_audit "S3 base promisor->evil" "$B/audit-base.py" "$B/lane-e1" "$B/fleet-full"
echo "    evil commit now local? $(GIT_NO_LAZY_FETCH=1 git -C "$B/lane-e1" cat-file -e "$(git -C "$B/evil" rev-parse HEAD)" && echo YES || echo NO)"
fresh_lane "$B/lane-e2" evil; git -C "$B/lane-e2" config remote.origin.uploadpack "$B/upmark-real"
run_audit "S3 fix  promisor->evil" "$B/audit-fix.py" "$B/lane-e2" "$B/fleet-full"
echo "--- S4 partial fleet, report blob really missing ---"
fresh_fleet_p "$B/fleet-pA"
echo "    blob local? $(GIT_NO_LAZY_FETCH=1 git -C "$B/fleet-pA" cat-file -e "$R" && echo YES || echo NO)"
b=$(git -C "$B/fleet-pA" count-objects -v | grep in-pack)
run_audit "S4 base partial fleet" "$B/audit-base.py" "$B/lane-full" "$B/fleet-pA"
a=$(git -C "$B/fleet-pA" count-objects -v | grep in-pack)
echo "    in-pack before[$b] after[$a] ; blob now local? $(GIT_NO_LAZY_FETCH=1 git -C "$B/fleet-pA" cat-file -e "$R" && echo YES || echo NO)"
fresh_fleet_p "$B/fleet-pB"
run_audit "S4 fix  partial fleet" "$B/audit-fix.py" "$B/lane-full" "$B/fleet-pB"
echo "    blob still absent? $(GIT_NO_LAZY_FETCH=1 git -C "$B/fleet-pB" cat-file -e "$R" && echo NO || echo YES)"
echo "--- S5 genuine partial fleet + failing uploadpack marker (clean committed report) ---"
fresh_fleet_p "$B/fleet-pC"; git -C "$B/fleet-pC" config remote.origin.uploadpack "$B/upmark-ps"
run_audit "S5 base marker-fail" "$B/audit-base.py" "$B/lane-full" "$B/fleet-pC"
sed -n '1p' "$B/marker.log" | cut -c1-120
fresh_fleet_p "$B/fleet-pD"; git -C "$B/fleet-pD" config remote.origin.uploadpack "$B/upmark-ps"
run_audit "S5 fix  marker-fail" "$B/audit-fix.py" "$B/lane-full" "$B/fleet-pD"
echo "--- S7 blob-object citation, promised and reachable (fresh clone each) ---"
fresh_lane "$B/lane-b1" origin
run_audit "S7 base blob cited" "$B/audit-base.py" "$B/lane-b1" "$B/fleet-full" --report 1="$B/draft-blob.md"
fresh_lane "$B/lane-b2" origin
run_audit "S7 fix  blob cited" "$B/audit-fix.py" "$B/lane-b2" "$B/fleet-full" --report 1="$B/draft-blob.md"
echo "--- S8 blob-object citation, promisor unreachable ---"
fresh_lane "$B/lane-b3" nonexistent
run_audit "S8 base blob gone" "$B/audit-base.py" "$B/lane-b3" "$B/fleet-full" --report 1="$B/draft-blob.md"
fresh_lane "$B/lane-b4" nonexistent
run_audit "S8 fix  blob gone" "$B/audit-fix.py" "$B/lane-b4" "$B/fleet-full" --report 1="$B/draft-blob.md"
echo "--- promisor config only, full repo, no filter key ---"
rm -rf "$B/lane-fp"; git clone -q "file://$B/origin" "$B/lane-fp"
git -C "$B/lane-fp" config remote.origin.promisor true
git -C "$B/lane-fp" config remote.origin.uploadpack "$B/upmark-ps"
run_audit "S9 base full+promisor" "$B/audit-base.py" "$B/lane-fp" "$B/fleet-full"
rm -rf "$B/lane-fp2"; git clone -q "file://$B/origin" "$B/lane-fp2"
git -C "$B/lane-fp2" config remote.origin.promisor true
git -C "$B/lane-fp2" config remote.origin.uploadpack "$B/upmark-ps"
run_audit "S9 fix  full+promisor" "$B/audit-fix.py" "$B/lane-fp2" "$B/fleet-full"
