#!/usr/bin/env bash
# Follow-up: fsmonitor configured only after all fixture writes; showSignature override check.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d "$HERE/run2.XXXX")
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mk() { git init -q -b master "$1"; }
cm() {
  local f=${5:-f}
  echo "$4" >> "$1/$f"
  git -C "$1" add "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$4"
  git -C "$1" rev-parse HEAD
}
base() {
  L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  LC=$(cm "$L" kama-shokunin 1000 "round-1: work")
  mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/.ufo/reports/round-1/kama.md"
  cm "$F" fleet 5000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null
}
for arm in frozen current; do
  base "s4-$arm"; M=$T/s4-$arm/marker
  git -C "$L" config core.fsmonitor "touch $M.lane; false"
  git -C "$F" config core.fsmonitor "touch $M.fleet; false"
  python3 "$HERE/$arm.py" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json >/dev/null 2>"$T/s4-$arm.err"
  echo "s4-fsmonitor $arm exit=$? markers: $(ls "$T/s4-$arm" | grep marker | tr '\n' ' ')"
done
# Draft-report path (--report N=PATH) also reads fleet repo via git; same check
base s4d; M=$T/s4d/marker; cp "$F/.ufo/reports/round-1/kama.md" "$T/s4d/draft.md"
git -C "$L" config core.fsmonitor "touch $M.lane; false"; git -C "$F" config core.fsmonitor "touch $M.fleet; false"
python3 "$HERE/current.py" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --report "1=$T/s4d/draft.md" --no-errata --json >/dev/null 2>&1
echo "s4-fsmonitor draft current exit=$? markers: $(ls "$T/s4d" | grep marker | tr '\n' ' ')"

# Does a -c log.showSignature=false override (the smallest candidate) stop gpg.program?
base s1; M=$T/s1/marker
printf '#!/bin/sh\necho ran >> %s\nexit 0\n' "$M" > "$T/s1/fakegpg"; chmod +x "$T/s1/fakegpg"
TREE=$(git -C "$L" rev-parse HEAD^{tree})
OBJ=$(printf 'tree %s\nparent %s\nauthor kama-shokunin <a@x> 1100 +0000\ncommitter kama-shokunin <a@x> 1100 +0000\ngpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n\nround-1: signed\n' "$TREE" "$LC" | git -C "$L" hash-object -t commit -w --stdin)
git -C "$L" update-ref refs/heads/master "$OBJ"
git -C "$L" config log.showSignature true; git -C "$L" config gpg.program "$T/s1/fakegpg"
git -C "$L" --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false \
  log --format=%H master >/dev/null 2>&1
echo "isolation-as-shipped log: marker=$( [ -e "$M" ] && echo PRESENT || echo absent)"; rm -f "$M"
git -C "$L" --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false \
  -c log.showSignature=false log --format=%H master >/dev/null 2>&1
echo "plus -c log.showSignature=false: marker=$( [ -e "$M" ] && echo PRESENT || echo absent)"; rm -f "$M"
git -C "$L" log --format=%H --no-show-signature master >/dev/null 2>&1
echo "--no-show-signature: marker=$( [ -e "$M" ] && echo PRESENT || echo absent)"; rm -f "$M"
echo T=$T
