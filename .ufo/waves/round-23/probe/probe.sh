#!/usr/bin/env bash
# Probe report-landing-audit.py against repo-local state faults (scratch only).
set -u
AUDIT=${AUDIT:?}
T=$(mktemp -d /tmp/kama-r23-probe/run.XXXX)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mk() { # dir
  git init -q -b master "$1"
}
cm() { # repo author time subject [file]
  local f=${5:-f}
  echo "$4" >> "$1/$f"
  git -C "$1" add "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$4"
  git -C "$1" rev-parse HEAD
}
base() { # name -> sets L F LC
  L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  LC=$(cm "$L" kama-shokunin 1000 "round-1: work")
  mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/.ufo/reports/round-1/kama.md"
  cm "$F" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null
}
run() { # name
  python3 "$AUDIT" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json >"$T/$1.out" 2>"$T/$1.err"
  local rc=$?
  printf '%s exit=%s stderr_tail=%s\n' "$1" "$rc" "$(tail -c 160 "$T/$1.err" | tr '\n' ' ')"
  python3 - "$T/$1.out" <<'EOF' 2>/dev/null
import json,sys
d=json.load(open(sys.argv[1])); r=d["results"][0]
print("   defects", [(x["kind"],x["token"][:12]) for x in r["defects"]], "required", r["required"], "cutoff", r["cutoff"])
EOF
}
# control
base control; run control
# F1 logOutputEncoding latin-1 + non-ASCII subject in lane
base f1; cm "$L" someone 1100 "note café" >/dev/null; git -C "$L" config i18n.logOutputEncoding ISO-8859-1; run f1-logenc
# F2 invalid UTF-8 bytes in committed report
base f2; printf '\xff\xfe bad\n' >> "$F/.ufo/reports/round-1/kama.md"; cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md >/dev/null; run f2-report-bytes
# F3 replace ref hides an omitted round commit
base f3; X=$(cm "$L" kama-shokunin 1200 "round-1: more"); Y=$(git -C "$L" commit-tree -p "$LC" -m "unrelated" "$X^{tree}"); git -C "$L" replace "$X" "$Y"; run f3-replace-omit
# F4 replace ref makes fabricated full hash resolve? (replace an object id that does not exist)
base f4; FAKE=1234567890abcdef1234567890abcdef12345678; printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"; cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md >/dev/null; git -C "$L" update-ref "refs/replace/$FAKE" "$LC"; run f4-replace-fake
# F5 promisor lazy fetch executes repo-configured ssh command
base f5; M=$T/f5/marker; git -C "$L" config extensions.partialClone origin; git -C "$L" config remote.origin.url ssh://example.invalid/x.git; git -C "$L" config remote.origin.promisor true; git -C "$L" config core.sshCommand "touch $M; false"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd; printf -- '- also %s\n' "$FAKE2" >> "$F/.ufo/reports/round-1/kama.md"; cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md >/dev/null
run f5-lazyfetch; [ -e "$M" ] && echo "   MARKER CREATED (command executed)" || echo "   no marker"
# F6 log.follow in fleet changes cutoff (report renamed into place)
base f6; git -C "$F" config log.follow true; mkdir -p "$F/old"; git -C "$F" mv .ufo/reports/round-1/kama.md old/k.md; cm "$F" fleet 2200 "mv" old/k.md >/dev/null 2>&1; git -C "$F" commit -q -m mv 2>/dev/null; git -C "$F" mv old/k.md .ufo/reports/round-1/kama.md; GIT_AUTHOR_DATE="@3000 +0000" GIT_COMMITTER_DATE="@3000 +0000" git -C "$F" -c user.name=fleet -c user.email=a@x commit -q -m back; run f6-follow
echo T=$T
