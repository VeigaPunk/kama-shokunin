#!/usr/bin/env bash
# Separability grid: each fault x each fix variant (scratch only).
set -u
AUDIT=/tmp/kama-r23/CritSeparability/tools/report-landing-audit.py
W=/tmp/kama-r23/CritSeparability-work
T=$(mktemp -d $W/run.XXXX)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@x GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@x
mk() { git init -q -b master "$1"; }
cm() { # repo author time subject [file]
  local f=${5:-f}
  printf '%s\n' "$4" >> "$1/$f"
  git -C "$1" add "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$4"
  git -C "$1" rev-parse HEAD
}
report() { # fleet lines...
  local F=$1; shift
  mkdir -p "$F/.ufo/reports/round-1"
  printf '%s\n' "$@" > "$F/.ufo/reports/round-1/kama.md"
}
base() { # dir -> L F LC
  L=$1/lane; F=$1/fleet; mk "$L"; mk "$F"
  LC=$(cm "$L" kama-shokunin 1000 "round-1: work")
  report "$F" "## Landed changes" "" "- $LC"
  cm "$F" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null
}
FAKE=1234567890abcdef1234567890abcdef12345678
setup() { # fault dir
  local d=$2; mkdir -p "$d"; M=$d/marker
  case $1 in
  control) base "$d" ;;
  f1-logenc) base "$d"; cm "$L" someone 1100 "note café" >/dev/null
     git -C "$L" config i18n.logOutputEncoding ISO-8859-1 ;;
  f2-reportbytes) base "$d"; printf '\xff\xfe bad\n' >> "$F/.ufo/reports/round-1/kama.md"
     cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null ;;
  f3-replace-omit) base "$d"; X=$(cm "$L" kama-shokunin 1200 "round-1: more")
     Y=$(git -C "$L" commit-tree -p "$LC" -m unrelated "$X^{tree}"); git -C "$L" replace "$X" "$Y" ;;
  f4-replace-fake) base "$d"; printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"
     cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null
     git -C "$L" update-ref "refs/replace/$FAKE" "$LC" ;;
  f4b-replace-report) base "$d"; printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"
     H=$(cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md)
     P=$(git -C "$F" rev-parse "$H^"); R=$(git -C "$F" commit-tree -p "$P" -m edit "$P^{tree}")
     git -C "$F" replace "$H" "$R" ;;
  f5-lazy-exec) base "$d"
     git -C "$L" config extensions.partialClone origin; git -C "$L" config remote.origin.url ssh://example.invalid/x.git
     git -C "$L" config remote.origin.promisor true; git -C "$L" config core.sshCommand "touch $M; false"
     printf -- '- also %s\n' abcdefabcdefabcdefabcdefabcdefabcdefabcd >> "$F/.ufo/reports/round-1/kama.md"
     cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null ;;
  f5b-lazy-supplies) base "$d"; O=$d/origin; git clone -q --bare "$L" "$O"
     git -C "$O" config uploadpack.allowFilter true; git -C "$O" config uploadpack.allowAnySHA1InWant true
     # object exists only on the promisor remote
     S=$(git -C "$O" commit-tree -m outside "$(git -C "$O" rev-parse "master^{tree}")"); git -C "$O" update-ref refs/heads/outside "$S"
     git -C "$L" config extensions.partialClone origin; git -C "$L" config remote.origin.url "file://$O"
     git -C "$L" config remote.origin.promisor true
     printf -- '- also %s\n' "$S" >> "$F/.ufo/reports/round-1/kama.md"
     cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null ;;
  g1-grafts) base "$d"; X=$(cm "$L" kama-shokunin 1200 "round-1: more"); Z=$(cm "$L" other 1300 "later")
     mkdir -p "$L/.git/info"; printf '%s %s\n' "$Z" "$LC" > "$L/.git/info/grafts" ;;
  g2-shallow) base "$d"; X=$(cm "$L" kama-shokunin 1200 "round-1: more"); Z=$(cm "$L" other 1300 "later")
     printf '%s\n' "$Z" > "$L/.git/shallow"
     report "$F" "## Landed changes" "" "- $Z"; cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null ;;
  g3-legit-partial) O=$d/origin; mk "$O"
     LC0=$(cm "$O" kama-shokunin 1000 "round-1: work")
     mkdir -p "$O/corpus"
     printf '## Registry\n| S001 | https://ex.invalid/a/%s | a | b | c | d | e | f | g | h | i |\n' "$FAKE" > "$O/corpus/SOURCES.md"
     LC=$(cm "$O" kama-shokunin 1001 "round-1: sources" corpus/SOURCES.md)
     git -C "$O" config uploadpack.allowFilter true; git -C "$O" config uploadpack.allowAnySHA1InWant true
     L=$d/lane; git clone -q --filter=blob:none --no-checkout "file://$O" "$L"
     F=$d/fleet; mk "$F"
     report "$F" "src https://ex.invalid/a/$FAKE" "## Landed changes" "" "- $LC0" "- $LC"
     cm "$F" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null ;;
  g4-showsig-exec) base "$d"
     printf '#!/bin/sh\ntouch %s\nexit 1\n' "$M" > "$d/fakegpg"; chmod +x "$d/fakegpg"
     raw=$(git -C "$L" cat-file commit HEAD)
     S=$(printf '%s\n' "$raw" | awk 'NR==1{print; next} /^committer /{print; print "gpgsig -----BEGIN PGP SIGNATURE-----"; print " x"; print " -----END PGP SIGNATURE-----"; next} {print}' | git -C "$L" hash-object -t commit -w --stdin)
     git -C "$L" update-ref refs/heads/master "$S"
     report "$F" "## Landed changes" "" "- $S"; cm "$F" fleet 2100 edit .ufo/reports/round-1/kama.md >/dev/null
     git -C "$L" config log.showSignature true; git -C "$L" config gpg.program "$d/fakegpg" ;;
  g5-foreign-latin1) base "$d"
     T5=$(git -C "$L" rev-parse "HEAD^{tree}")
     S=$(printf 'tree %s\nparent %s\nauthor someone <a@x> 1100 +0000\ncommitter someone <a@x> 1100 +0000\n\nnote caf\xe9\n' "$T5" "$LC" | git -C "$L" hash-object -t commit -w --stdin)
     git -C "$L" update-ref refs/heads/master "$S" ;;
  esac
}
FAULTS="control f1-logenc f2-reportbytes f3-replace-omit f4-replace-fake f4b-replace-report f5-lazy-exec f5b-lazy-supplies g1-grafts g2-shallow g3-legit-partial g4-showsig-exec g5-foreign-latin1"
VARIANTS="none D E DE R L RL DERL DERLF"
printf '%-20s' fault; for v in $VARIANTS; do printf '%-16s' "$v"; done; echo
for f in $FAULTS; do
  printf '%-20s' "$f"
  for v in $VARIANTS; do
    d=$T/$f.$v; setup "$f" "$d" >/dev/null 2>&1
    KAMA_VARIANT=${v/none/} python3 "$AUDIT" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json >"$d.out" 2>"$d.err"
    rc=$?
    st=$(python3 -c 'import json,sys
try:
  d=json.load(open(sys.argv[1])); r=d["results"][0]
  print(d["summary"]["status"][0]+":"+",".join(x["kind"].split("-")[-1][:4] for x in r["defects"]))
except Exception: print("-")' "$d.out")
    tb=""; grep -q Traceback "$d.err" && tb="TB"
    mk_=""; [ -e "$d/marker" ] && mk_="X"
    printf '%-16s' "$rc$tb$mk_/$st"
  done; echo
done
echo T=$T
