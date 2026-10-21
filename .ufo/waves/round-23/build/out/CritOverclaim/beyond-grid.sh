#!/usr/bin/env bash
# Repo-local channels outside the round-23 grid, against frozen and current auditor copies.
# Scratch-only; no network (example.invalid never contacted by these cases).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d "$HERE/run.XXXX")
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mk() { git init -q -b master "$1"; }
cm() { # repo author time subject [file]
  local f=${5:-f}
  echo "$4" >> "$1/$f"
  git -C "$1" add "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$4"
  git -C "$1" rev-parse HEAD
}
base() { # name -> L F LC ; report cites LC only
  L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  LC=$(cm "$L" kama-shokunin 1000 "round-1: work")
  mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/.ufo/reports/round-1/kama.md"
}
publish() { cm "$F" fleet 5000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null; }
run() { # name
  for arm in frozen current; do
    python3 "$HERE/$arm.py" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json \
      >"$T/$1.$arm.out" 2>"$T/$1.$arm.err"
    local rc=$?
    local summ
    summ=$(python3 - "$T/$1.$arm.out" <<'EOF' 2>/dev/null
import json,sys
d=json.load(open(sys.argv[1])); r=d["results"][0]
print([(x["kind"],x["token"][:10]) for x in r["defects"]], "required", r["required"])
EOF
)
    printf '%-22s %-7s exit=%s %s | err=%s\n' "$1" "$arm" "$rc" "${summ:-<no json>}" \
      "$(tail -c 140 "$T/$1.$arm.err" | tr '\n' ' ')"
  done
}
marker() { if [ -e "$1" ]; then echo "   MARKER PRESENT: $(cat "$1" | tr '\n' ' ')"; rm -f "$1"; else echo "   no marker"; fi; }

# control: one round commit, cited -> clean
base control; publish; run control

# S1 log.showSignature + repo gpg.program on a signed-looking round commit
base s1; M=$T/s1/marker
printf '#!/bin/sh\necho "gpg.program ran: $*" >> %s\necho "[GNUPG:] GOODSIG 0 x" >&2\nexit 0\n' "$M" > "$T/s1/fakegpg"
chmod +x "$T/s1/fakegpg"
TREE=$(git -C "$L" rev-parse HEAD^{tree})
OBJ=$(printf 'tree %s\nparent %s\nauthor kama-shokunin <a@x> 1100 +0000\ncommitter kama-shokunin <a@x> 1100 +0000\ngpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n\nround-1: signed\n' "$TREE" "$LC" | git -C "$L" hash-object -t commit -w --stdin)
git -C "$L" update-ref refs/heads/master "$OBJ"
printf -- '- %s\n' "$OBJ" >> "$F/.ufo/reports/round-1/kama.md"; publish
git -C "$L" config log.showSignature true; git -C "$L" config gpg.program "$T/s1/fakegpg"
run s1-showsig; marker "$M"

# S2 .mailmap in lane worktree renames an outsider into the lane author -> report now required to cite it
base s2; X=$(cm "$L" someone 1100 "round-1: outsider")
printf 'kama-shokunin <a@x> someone <a@x>\n' > "$L/.mailmap"
publish; run s2-mailmap-in
# S2b mailmap renames the lane author away -> omitted round commit hidden
base s2b; X=$(cm "$L" kama-shokunin 1100 "round-1: omitted")
printf 'Ghost <a@x> kama-shokunin <a@x>\n' > "$L/.mailmap"
publish; run s2b-mailmap-out
# S2c same via repo-local mailmap.file config pointing at a file outside the worktree
base s2c; X=$(cm "$L" kama-shokunin 1100 "round-1: omitted")
printf 'Ghost <a@x> kama-shokunin <a@x>\n' > "$T/s2c/mm"; git -C "$L" config mailmap.file "$T/s2c/mm"
publish; run s2c-mailmap-file

# S3 .git/shallow hides an omitted older round commit behind a later boundary
base s3; X=$(cm "$L" kama-shokunin 1100 "round-1: omitted"); Y=$(cm "$L" other 1200 "unrelated")
printf -- '- %s\n' "$Y" >/dev/null
echo "$Y" > "$L/.git/shallow"
publish; run s3-shallow

# S4 core.fsmonitor hook command
base s4; M=$T/s4/marker; git -C "$L" config core.fsmonitor "touch $M; false"; git -C "$F" config core.fsmonitor "touch $M; false"
publish; run s4-fsmonitor; marker "$M"

# S5 include.path smuggles log.showSignature/gpg.program (same as S1, via include)
base s5; M=$T/s5/marker
printf '#!/bin/sh\necho "gpg.program ran" >> %s\nexit 0\n' "$M" > "$T/s5/fakegpg"; chmod +x "$T/s5/fakegpg"
TREE=$(git -C "$L" rev-parse HEAD^{tree})
OBJ=$(printf 'tree %s\nparent %s\nauthor kama-shokunin <a@x> 1100 +0000\ncommitter kama-shokunin <a@x> 1100 +0000\ngpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n\nround-1: signed\n' "$TREE" "$LC" | git -C "$L" hash-object -t commit -w --stdin)
git -C "$L" update-ref refs/heads/master "$OBJ"
printf -- '- %s\n' "$OBJ" >> "$F/.ufo/reports/round-1/kama.md"; publish
printf '[log]\n\tshowSignature = true\n[gpg]\n\tprogram = %s\n' "$T/s5/fakegpg" > "$T/s5/inc"
git -C "$L" config include.path "$T/s5/inc"
run s5-include-showsig; marker "$M"

# S6 alternates: fabricated citation resolves from an attacker-chosen object store
base s6; A=$T/s6/attacker; mk "$A"; FAKE=$(cm "$A" x 1 "anything")
printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"; publish
echo "$A/.git/objects" > "$L/.git/objects/info/alternates"
run s6-alternates

echo T=$T
