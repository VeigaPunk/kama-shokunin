#!/bin/sh
# ScoutLazyFetch repro: promisor lazy fetch vs tools/report-landing-audit.py at base.
# Fixtures live only under /tmp; no audited-repo fixture touches the real lane/fleet.
set -u
B=/tmp/kama-r23-lf/repro
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
BASE_REV=4fe9339f8fc3a4a4a479d9c938a850da12f1124d
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME=A GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=A GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000'
rm -rf "$B"; mkdir -p "$B"
git -C "$LANE" show "$BASE_REV:tools/report-landing-audit.py" > "$B/audit-base.py"
python3 - "$B/audit-base.py" "$B/audit-fix.py" <<'PY'
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = 'proc = subprocess.run(["git", "-C", str(repo), *args], input=stdin,'
new = 'proc = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args], input=stdin,'
assert src.count(old) == 1, src.count(old)
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
PY
# --- fixture repos -----------------------------------------------------------
git init -q --initial-branch=main "$B/origin"
echo one > "$B/origin/f"; git -C "$B/origin" add f; git -C "$B/origin" commit -q -m 'round-1: work'
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin
echo two > "$B/origin/g"; git -C "$B/origin" add g; git -C "$B/origin" commit -q -m 'round-1: more work'
git -C "$B/origin" config uploadpack.allowFilter true
A=$(git -C "$B/origin" rev-list --max-parents=0 HEAD); C=$(git -C "$B/origin" rev-parse HEAD)
BLOB=$(git -C "$B/origin" rev-parse "$A:f")
git init -q --initial-branch=main "$B/evil"; echo evil > "$B/evil/e"
git -C "$B/evil" add e; git -C "$B/evil" commit -q -m 'evil object'
E=$(git -C "$B/evil" rev-parse HEAD)
for N in fleet-clean-origin fleet-evil-origin; do
  git init -q --initial-branch=main "$B/$N"
  mkdir -p "$B/$N/.ufo/reports/round-1"
  git -C "$B/$N" config uploadpack.allowFilter true
done
printf '# r1\n\n## Landed changes\n- `%s` work\n- `%s` more\n\n## Notes\nall good\n' "$A" "$C" > "$B/fleet-clean-origin/.ufo/reports/round-1/kama.md"
printf '# r1\n\n## Landed changes\n- `%s` work\n- `%s` more\n\n## Notes\nReviewed upstream object %s today.\n' "$A" "$C" "$E" > "$B/fleet-evil-origin/.ufo/reports/round-1/kama.md"
for N in fleet-clean-origin fleet-evil-origin; do
  git -C "$B/$N" add .ufo; git -C "$B/$N" commit -q -m 'round-1: kama report'
done
printf '# r1\n\n## Landed changes\n- `%s` work\n- `%s` more\n\n## Notes\nartifact %s reviewed\n' "$A" "$C" "$BLOB" > "$B/draft-blob.md"
printf '# r1\n\n## Landed changes\n- `%s` work\n- `%s` more\n\n## Notes\nall good\n' "$A" "$C" > "$B/draft-clean.md"
R=$(git -C "$B/fleet-clean-origin" rev-parse HEAD:.ufo/reports/round-1/kama.md)
# --- channel markers ---------------------------------------------------------
mk(){ printf '#!/bin/sh\necho "%s $*" >> %s/marker.log\nexit %s\n' "$1" "$B" "$2" > "$B/$3"; chmod +x "$B/$3"; }
mk failmark 127 failmark; mk sshmark 255 sshmark; mk proxymark 127 proxymark; mk credmark 1 credmark
printf '#!/bin/sh\necho "realmark $*" >> %s/marker.log\nexec git-upload-pack "$@"\n' "$B" > "$B/realmark"; chmod +x "$B/realmark"
# --- helpers -----------------------------------------------------------------
run_audit() { label=$1; script=$2; lane=$3; fleet=$4; shift 4
  : > "$B/marker.log"
  if out=$(cd /tmp && timeout 120 python3 "$script" --lane-repo "$lane" --fleet-repo "$fleet" --branch main --rounds 1 --no-errata "$@" 2>&1); then rc=0; else rc=$?; fi
  printf '%-34s rc=%s marker=%-2s | %s\n' "$label" "$rc" "$(grep -c . "$B/marker.log" 2>/dev/null || echo 0)" \
    "$(echo "$out" | grep -E 'UNCORRECTED unresolved|summary|could-not-evaluate' | tr '\n' ' ' | cut -c1-120)"
}
fresh_lane() { rm -rf "$1"; git clone -q --filter=blob:none --no-checkout "file://$B/origin" "$1"; git -C "$1" config remote.origin.url "file://$B/$2"; }
fresh_fleet_p() { rm -rf "$1"; git clone -q --filter=blob:none --no-checkout "file://$B/fleet-clean-origin" "$1"; }
git clone -q "file://$B/origin" "$B/lane-full"
git clone -q "file://$B/fleet-evil-origin" "$B/fleet-full"
echo "A=$A C=$C E=$E BLOB=$BLOB reportblob=$R"
echo "cp-file config-only promisor on a FULL repo:"
git clone -q "file://$B/origin" "$B/lane-fullprom"
git -C "$B/lane-fullprom" config remote.origin.promisor true
git -C "$B/lane-fullprom" config remote.origin.uploadpack "$B/failmark"
printf 'fabricated: '; : > "$B/marker.log"
printf '0123456789abcdef0123456789abcdef01234567\n' | git -C "$B/lane-fullprom" cat-file --batch-check 2>/dev/null; \
  echo "  marker=$(wc -l < "$B/marker.log")"
echo "--- audit matrix ---"
run_audit "S1 base clean draft"        "$B/audit-base.py" "$B/lane-full" "$B/fleet-full" --report 1="$B/draft-clean.md"
run_audit "S1 fix  clean draft"        "$B/audit-fix.py"  "$B/lane-full" "$B/fleet-full" --report 1="$B/draft-clean.md"
run_audit "S2 base evil committed"     "$B/audit-base.py" "$B/lane-full" "$B/fleet-full"
run_audit "S2 fix  evil committed"     "$B/audit-fix.py"  "$B/lane-full" "$B/fleet-full"
fresh_lane "$B/lane-e1" evil; git -C "$B/lane-e1" config remote.origin.uploadpack "$B/realmark"
run_audit "S3 base promisor->evil"     "$B/audit-base.py" "$B/lane-e1" "$B/fleet-full"
fresh_lane "$B/lane-e2" evil; git -C "$B/lane-e2" config remote.origin.uploadpack "$B/realmark"
run_audit "S3 fix  promisor->evil"     "$B/audit-fix.py"  "$B/lane-e2" "$B/fleet-full"
fresh_fleet_p "$B/fleet-pA"; b=$(git -C "$B/fleet-pA" count-objects -v | grep in-pack)
run_audit "S4 base partial fleet"      "$B/audit-base.py" "$B/lane-full" "$B/fleet-pA"
a=$(git -C "$B/fleet-pA" count-objects -v | grep in-pack); echo "   fleet-p in-pack [$b] -> [$a]"
fresh_fleet_p "$B/fleet-pB"
run_audit "S4 fix  partial fleet"      "$B/audit-fix.py"  "$B/lane-full" "$B/fleet-pB"
fresh_fleet_p "$B/fleet-pC"; git -C "$B/fleet-pC" config remote.origin.uploadpack "$B/failmark"
run_audit "S5 base marker-fail"        "$B/audit-base.py" "$B/lane-full" "$B/fleet-pC"
fresh_fleet_p "$B/fleet-pD"; git -C "$B/fleet-pD" config remote.origin.uploadpack "$B/failmark"
run_audit "S5 fix  marker-fail"        "$B/audit-fix.py"  "$B/lane-full" "$B/fleet-pD"
git clone -q "file://$B/fleet-clean-origin" "$B/fleet-fp"
git -C "$B/fleet-fp" config remote.origin.promisor true
git -C "$B/fleet-fp" config remote.origin.url "file://$B/nonexistent"
git -C "$B/fleet-fp" config remote.origin.uploadpack "$B/failmark"
run_audit "S6 base clean+promisor"     "$B/audit-base.py" "$B/lane-full" "$B/fleet-fp"
run_audit "S6 fix  clean+promisor"     "$B/audit-fix.py"  "$B/lane-full" "$B/fleet-fp"
fresh_lane "$B/lane-b1" origin
run_audit "S7 base blob cited"         "$B/audit-base.py" "$B/lane-b1" "$B/fleet-full" --report 1="$B/draft-blob.md"
fresh_lane "$B/lane-b2" origin
run_audit "S7 fix  blob cited"         "$B/audit-fix.py"  "$B/lane-b2" "$B/fleet-full" --report 1="$B/draft-blob.md"
fresh_lane "$B/lane-b3" nonexistent
run_audit "S8 base blob gone"          "$B/audit-base.py" "$B/lane-b3" "$B/fleet-full" --report 1="$B/draft-blob.md"
fresh_lane "$B/lane-b4" nonexistent
run_audit "S8 fix  blob gone"          "$B/audit-fix.py"  "$B/lane-b4" "$B/fleet-full" --report 1="$B/draft-blob.md"
