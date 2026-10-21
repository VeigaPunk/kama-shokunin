#!/usr/bin/env bash
# Bounded, offline premise measurements for the OracleFleetHistory case.
# Read-only git plumbing on the synthetic fixtures; no network, no transport.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/OracleFleetHistory/fixtures/out
REL=.ufo/reports/round-1/kama.md
ISO=(--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
     -c log.follow=false -c log.showRoot=true -c log.showSignature=false
     -c log.mailmap=false)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

show() { printf '\n### %s\n' "$*"; }

show "M1 fleet_plain: add-commits for the report path"
git "${ISO[@]}" -C "$ROOT/fleet_plain" log --diff-filter=A --format='%H %at %s' -- "$REL"; echo "rc=$?"

show "M1b fleet_plain: --format=%at list (report_cutoff takes the last entry)"
git "${ISO[@]}" -C "$ROOT/fleet_plain" log --diff-filter=A --format=%at -- "$REL"; echo "rc=$?"

show "M2 fleet_plain: full log of the report path"
git "${ISO[@]}" -C "$ROOT/fleet_plain" log --format='%H %at %s' -- "$REL"; echo "rc=$?"

show "M3 fleet_marked_cfg: promisor config, closure completeness"
git "${ISO[@]}" -C "$ROOT/fleet_marked_cfg" config --get remote.origin.promisor; echo "rc=$?"
git "${ISO[@]}" -C "$ROOT/fleet_marked_cfg" rev-list --objects --missing=print --no-object-names HEAD | grep -c '^?' ; echo "missing-lines-above (0 = complete)"

show "M4 fleet_marked_cfg: same add-commit list as the plain twin"
git "${ISO[@]}" -C "$ROOT/fleet_marked_cfg" log --diff-filter=A --format='%H %at' -- "$REL"; echo "rc=$?"

show "M5 fleet_marked_pack: paired .promisor/.pack markers, closure completeness"
ls -1 "$ROOT/fleet_marked_pack/.git/objects/pack"
git "${ISO[@]}" -C "$ROOT/fleet_marked_pack" config --get remote.origin.promisor; echo "promisor-config-rc=$?"
git "${ISO[@]}" -C "$ROOT/fleet_marked_pack" rev-list --objects --missing=print --no-object-names HEAD | grep -c '^?'; echo "missing-lines-above (0 = complete)"
git "${ISO[@]}" -C "$ROOT/fleet_marked_pack" log --diff-filter=A --format='%H %at' -- "$REL"; echo "rc=$?"

show "M6 fleet_hist_missing: first-add blob deleted (promisor config present)"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" config --get remote.origin.promisor; echo "rc=$?"
echo "-- closure scan (rev-list --objects --missing=print)"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" rev-list --objects --missing=print --no-object-names HEAD | grep '^?'; echo "rc=$?"
echo "-- tip-only scan (ls-tree -r HEAD blobs, cat-file --batch-check)"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" ls-tree -r HEAD | awk '{print $3, $4}'
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" ls-tree -r HEAD | awk '{print $3}' | git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" cat-file --batch-check; echo "rc=$?"
echo "-- HEAD report bytes"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" show "HEAD:$REL"; echo "rc=$?"
echo "-- add-commit list (cutoff source) with the first-add blob absent"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" log --diff-filter=A --format='%H %at' -- "$REL"; echo "rc=$?"
echo "-- cat-file --batch-check on the missing first-add blob"
echo 6d06f68c89213cb1fca438aa91f5b61a39dabc4a | git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" cat-file --batch-check; echo "rc=$?"

show "M7 lane: round-1 commits and their author times"
git "${ISO[@]}" -C "$ROOT/lane" log --format='%H %at %an %s' master

show "M8 fleet_plain vs marked twins: identical report bytes at HEAD"
for r in fleet_plain fleet_marked_cfg fleet_marked_pack; do
  printf '%s ' "$r"; git "${ISO[@]}" -C "$ROOT/$r" rev-parse "HEAD:$REL"
done
printf '%s ' fleet_hist; git "${ISO[@]}" -C "$ROOT/fleet_hist" rev-parse "HEAD:$REL"

show "M9 reading the missing first-add blob with --no-lazy-fetch (must fail, no fetch)"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" show "8b0559d8407ec5bb93f95b1438ff3f885b3bea46:$REL"; echo "rc=$?"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" cat-file blob 6d06f68c89213cb1fca438aa91f5b61a39dabc4a; echo "rc=$?"
echo "-- remote that a lazy fetch would have used (never contacted)"
git "${ISO[@]}" -C "$ROOT/fleet_hist_missing" config --get remote.origin.url

show "M10 skew fleet: add-commit author times (re-add carries the EARLIER time)"
git "${ISO[@]}" -C "$ROOT/fleet_skew" log --diff-filter=A --format='%H %at %s' -- "$REL"; echo "rc=$?"
echo "-- closure scan of the skew marked twin"
git "${ISO[@]}" -C "$ROOT/fleet_skew_marked_cfg" rev-list --objects --missing=print --no-object-names HEAD | grep -c '^?'; echo "missing-lines-above (0 = complete)"

show "M11 lane_skew commits"
git "${ISO[@]}" -C "$ROOT/lane_skew" log --format='%H %at %an %s' master

